"""Servicios para la gestión transaccional del catálogo de productos."""

from typing import List, Optional, Tuple, Union

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.models.categoria import Categoria
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto, ProductoCategoria, ProductoIngrediente, _utc_now
from .schemas import ProductoCreate, ProductoIngredienteInput, ProductoUpdate


class ProductoConflictError(ValueError):
    """Excepción de dominio para conflictos de producto."""


class ProductoRelationNotFoundError(LookupError):
    """Una categoría o ingrediente referenciado no existe o está inactivo."""


def _validate_and_dedup_categorias(session: Session, categoria_ids: List[int]) -> List[int]:
    ids = list(dict.fromkeys(categoria_ids))
    for categoria_id in ids:
        categoria = session.get(Categoria, categoria_id)
        if categoria is None or categoria.deleted_at is not None:
            raise ProductoRelationNotFoundError(f"La categoría con id {categoria_id} no existe.")
    return ids


def _validate_and_normalize_ingredientes(
    session: Session,
    ingredientes_input: List[Union[int, ProductoIngredienteInput]],
) -> List[ProductoIngredienteInput]:
    normalized: dict[int, ProductoIngredienteInput] = {}
    for item in ingredientes_input:
        detalle = (
            ProductoIngredienteInput(ingrediente_id=item)
            if isinstance(item, int)
            else item
        )
        normalized[detalle.ingrediente_id] = detalle

    for ingrediente_id in normalized:
        ingrediente = session.get(Ingrediente, ingrediente_id)
        if ingrediente is None or ingrediente.deleted_at is not None:
            raise ProductoRelationNotFoundError(f"El ingrediente con id {ingrediente_id} no existe.")
    return list(normalized.values())


def _sync_producto_categorias(session: Session, producto_id: int, categoria_ids: List[int]) -> None:
    links = session.exec(
        select(ProductoCategoria).where(ProductoCategoria.producto_id == producto_id)
    ).all()
    for link in links:
        session.delete(link)
    for index, categoria_id in enumerate(categoria_ids):
        session.add(
            ProductoCategoria(
                producto_id=producto_id,
                categoria_id=categoria_id,
                es_principal=index == 0,
            )
        )


def _sync_producto_ingredientes(
    session: Session,
    producto_id: int,
    items: List[ProductoIngredienteInput],
) -> None:
    links = session.exec(
        select(ProductoIngrediente).where(ProductoIngrediente.producto_id == producto_id)
    ).all()
    for link in links:
        session.delete(link)
    for item in items:
        session.add(
            ProductoIngrediente(
                producto_id=producto_id,
                ingrediente_id=item.ingrediente_id,
                cantidad=item.cantidad,
                es_opcional=item.es_opcional,
            )
        )


def create_producto(session: Session, data: ProductoCreate) -> Producto:
    """Crea un producto y sus relaciones en una sola transacción."""
    cat_ids = _validate_and_dedup_categorias(session, data.categoria_ids)
    ing_items = (
        _validate_and_normalize_ingredientes(session, data.ingredientes)
        if data.ingredientes is not None
        else None
    )
    producto = Producto(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio_base=data.precio_base,
        imagenes_url=data.imagenes_url,
        disponible=data.disponible,
    )
    session.add(producto)
    session.flush()
    assert producto.id is not None
    _sync_producto_categorias(session, producto.id, cat_ids)
    if ing_items is not None:
        _sync_producto_ingredientes(session, producto.id, ing_items)
    session.commit()
    return get_producto(session, producto.id) or producto


def get_productos(
    session: Session,
    offset: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    disponible: Optional[bool] = None,
    categoria_id: Optional[int] = None,
    incluir_inactivos: bool = False,
) -> Tuple[int, List[Producto]]:
    query = select(Producto)
    if not incluir_inactivos:
        query = query.where(Producto.deleted_at.is_(None))
    if nombre is not None and nombre.strip():
        query = query.where(Producto.nombre.ilike(f"%{nombre.strip()}%"))
    if disponible is not None:
        query = query.where(Producto.disponible == disponible)
    if categoria_id is not None:
        query = (
            query.join(ProductoCategoria, ProductoCategoria.producto_id == Producto.id)
            .join(Categoria, Categoria.id == ProductoCategoria.categoria_id)
            .where(
                ProductoCategoria.categoria_id == categoria_id,
                Categoria.deleted_at.is_(None),
            )
            .distinct()
        )
    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    paginated_query = (
        query.options(
            selectinload(Producto.categorias.and_(Categoria.deleted_at.is_(None))),
            selectinload(Producto.ingredientes.and_(Ingrediente.deleted_at.is_(None))),
        )
        .order_by(Producto.id)
        .offset(offset)
        .limit(limit)
    )
    return total, list(session.exec(paginated_query).all())


def get_producto(session: Session, producto_id: int) -> Optional[Producto]:
    statement = (
        select(Producto)
        .where(Producto.id == producto_id, Producto.deleted_at.is_(None))
        .options(
            selectinload(Producto.categorias.and_(Categoria.deleted_at.is_(None))),
            selectinload(Producto.ingredientes.and_(Ingrediente.deleted_at.is_(None))),
        )
    )
    return session.exec(statement).first()


def update_producto(
    session: Session,
    producto_id: int,
    data: Union[ProductoUpdate, ProductoCreate],
) -> Optional[Producto]:
    producto = get_producto(session, producto_id)
    if producto is None:
        return None

    update_data = data.model_dump(exclude_unset=True)
    relations_sent = data.model_fields_set
    raw_cat_ids = update_data.pop("categoria_ids", None)
    raw_ingredientes = update_data.pop("ingredientes", None)

    if "categoria_ids" in relations_sent and raw_cat_ids is not None:
        valid_cat_ids = _validate_and_dedup_categorias(session, raw_cat_ids)
        _sync_producto_categorias(session, producto_id, valid_cat_ids)

    if "ingredientes" in relations_sent:
        ing_items = (
            _validate_and_normalize_ingredientes(session, raw_ingredientes)
            if raw_ingredientes
            else []
        )
        _sync_producto_ingredientes(session, producto_id, ing_items)

    for key, value in update_data.items():
        setattr(producto, key, value)
    producto.updated_at = _utc_now()
    session.add(producto)
    session.commit()
    session.expire_all()
    return get_producto(session, producto_id)


def _purge_producto_relations(session: Session, producto_id: int) -> None:
    for model in (ProductoCategoria, ProductoIngrediente):
        links = session.exec(select(model).where(model.producto_id == producto_id)).all()
        for link in links:
            session.delete(link)


def soft_delete_producto(session: Session, producto_id: int) -> Optional[Producto]:
    producto = get_producto(session, producto_id)
    if producto is None:
        return None
    now = _utc_now()
    _purge_producto_relations(session, producto_id)
    producto.deleted_at = now
    producto.updated_at = now
    producto.disponible = False
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


def delete_producto(session: Session, producto_id: int, hard_delete: bool = False) -> bool:
    producto = session.get(Producto, producto_id)
    if producto is None or (not hard_delete and producto.deleted_at is not None):
        return False
    _purge_producto_relations(session, producto_id)
    if hard_delete:
        session.delete(producto)
    else:
        now = _utc_now()
        producto.deleted_at = now
        producto.updated_at = now
        producto.disponible = False
        session.add(producto)
    session.commit()
    return True


def get_categorias_by_producto_id(session: Session, producto_id: int) -> Optional[List[Categoria]]:
    if get_producto(session, producto_id) is None:
        return None
    return list(
        session.exec(
            select(Categoria)
            .join(ProductoCategoria, ProductoCategoria.categoria_id == Categoria.id)
            .where(
                ProductoCategoria.producto_id == producto_id,
                Categoria.deleted_at.is_(None),
            )
            .order_by(Categoria.id)
        ).all()
    )


def get_ingredientes_by_producto_id(
    session: Session,
    producto_id: int,
) -> Optional[List[Ingrediente]]:
    if get_producto(session, producto_id) is None:
        return None
    return list(
        session.exec(
            select(Ingrediente)
            .join(ProductoIngrediente, ProductoIngrediente.ingrediente_id == Ingrediente.id)
            .where(
                ProductoIngrediente.producto_id == producto_id,
                Ingrediente.deleted_at.is_(None),
            )
            .order_by(Ingrediente.id)
        ).all()
    )


crear = create_producto
crear_producto = create_producto
obtener_todos = get_productos
listar_productos = get_productos
obtener_por_id = get_producto
obtener_producto_por_id = get_producto
actualizar = update_producto
actualizar_producto = update_producto
actualizar_total = update_producto
desactivar = soft_delete_producto
eliminar = delete_producto
eliminar_producto = delete_producto
