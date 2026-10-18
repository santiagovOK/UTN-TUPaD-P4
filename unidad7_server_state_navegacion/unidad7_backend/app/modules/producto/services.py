"""Capa de servicio para la entidad Producto y la relación asociativa N:N ProductoCategoria.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - PRODUCTO y tabla asociativa PRODUCTO_CATEGORIA]
"""

from typing import List, Optional, Tuple, Union

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.models.categoria import Categoria
from app.models.producto import Producto, ProductoCategoria, _utc_now
from .schemas import ProductoCategoriaAssign, ProductoCreate, ProductoUpdate


class ProductoConflictError(ValueError):
    """Excepción de dominio lanzada ante conflictos de unicidad o vínculo duplicado."""


# [Consigna TP7 - Alta de producto con control de duplicados por nombre y reactivación tras baja lógica]
# [Diagrama UML - PRODUCTO.nombre VARCHAR(150)]
def create_producto(session: Session, data: ProductoCreate) -> Producto:
    """Crea un producto verificando unicidad de nombre insensible a mayúsculas/minúsculas.

    Si existe un producto activo con el mismo nombre, lanza ProductoConflictError.
    Si existe un producto en baja lógica (deleted_at is not None), se reactiva actualizando sus datos.
    """
    colision = session.exec(
        select(Producto).where(func.lower(Producto.nombre) == data.nombre.lower())
    ).first()

    if colision:
        if colision.deleted_at is None:
            raise ProductoConflictError(f"Ya existe un producto con el nombre '{data.nombre}'.")

        # Reactivación tras baja lógica
        colision.nombre = data.nombre
        colision.descripcion = data.descripcion
        colision.precio_base = data.precio_base
        colision.imagenes_url = data.imagenes_url
        colision.disponible = data.disponible
        colision.deleted_at = None
        colision.updated_at = _utc_now()
        session.add(colision)
        session.commit()
        producto_reactivado = get_producto(session, colision.id)  # type: ignore[arg-type]
        return producto_reactivado or colision

    producto = Producto.model_validate(data)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    producto_creado = get_producto(session, producto.id)  # type: ignore[arg-type]
    return producto_creado or producto


# [Consigna TP7 - Listado paginado con orden estricto de 4 pasos y eager loading selectinload]
# [Diagrama UML - Colección de PRODUCTO activos y relación N:N con CATEGORIA]
def get_productos(
    session: Session,
    offset: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    disponible: Optional[bool] = None,
    categoria_id: Optional[int] = None,
) -> Tuple[int, List[Producto]]:
    """Retorna el total de coincidencias y los registros activos paginados con sus categorías activas cargadas."""
    # Paso 1: Consulta base filtrando productos activos
    query = select(Producto).where(Producto.deleted_at.is_(None))

    # Paso 2: Filtros dinámicos condicionales
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

    # Paso 3: Conteo atómico en motor SQL sobre la subconsulta filtrada
    count_query = select(func.count()).select_from(query.subquery())
    total: int = session.exec(count_query).one()

    # Paso 4: Extracción de ventana paginada con Eager Loading (selectinload)
    paginated_query = (
        query.options(selectinload(Producto.categorias.and_(Categoria.deleted_at.is_(None))))
        .order_by(Producto.id)
        .offset(offset)
        .limit(limit)
    )
    items = session.exec(paginated_query).all()
    return total, list(items)


# [Consigna TP7 - Detalle de producto activo por ID con carga de categorías activas]
# [Diagrama UML - PRODUCTO.id PK y relación N:N con CATEGORIA]
def get_producto(session: Session, producto_id: int) -> Optional[Producto]:
    """Obtiene un producto activo por ID junto con sus categorías activas asociadas."""
    statement = (
        select(Producto)
        .where(Producto.id == producto_id, Producto.deleted_at.is_(None))
        .options(selectinload(Producto.categorias.and_(Categoria.deleted_at.is_(None))))
    )
    return session.exec(statement).first()


# [Consigna TP7 - Actualización parcial o total con exclude_unset y control de unicidad de nombre]
# [Diagrama UML - Modificación de atributos de PRODUCTO]
def update_producto(
    session: Session,
    producto_id: int,
    data: Union[ProductoUpdate, ProductoCreate],
) -> Optional[Producto]:
    """Actualiza un producto existente verificando colisión de nombres."""
    producto = get_producto(session, producto_id)
    if not producto:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "nombre" in update_data and update_data["nombre"] is not None:
        nuevo_nombre = update_data["nombre"]
        colision = session.exec(
            select(Producto).where(
                Producto.id != producto_id,
                Producto.deleted_at.is_(None),
                func.lower(Producto.nombre) == nuevo_nombre.lower(),
            )
        ).first()
        if colision:
            raise ProductoConflictError(f"Ya existe un producto con el nombre '{nuevo_nombre}'.")

    for key, value in update_data.items():
        setattr(producto, key, value)

    producto.updated_at = _utc_now()
    session.add(producto)
    session.commit()
    return get_producto(session, producto_id)


# [Consigna TP7 - Baja lógica de producto preservando auditoría]
# [Diagrama UML - PRODUCTO.deleted_at TIMESTAMP]
def soft_delete_producto(session: Session, producto_id: int) -> Optional[Producto]:
    """Marca el producto con baja lógica asignando deleted_at y disponible=False."""
    producto = get_producto(session, producto_id)
    if not producto:
        return None

    now = _utc_now()
    producto.deleted_at = now
    producto.updated_at = now
    producto.disponible = False
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


# [Consigna TP7 - Eliminación lógica por defecto o física según parámetro]
# [Diagrama UML - Ciclo de vida de PRODUCTO]
def delete_producto(session: Session, producto_id: int, hard_delete: bool = False) -> bool:
    """Elimina un producto lógica o físicamente. Retorna True si la operación tuvo éxito."""
    producto = session.get(Producto, producto_id)
    if not producto:
        return False

    if not hard_delete and producto.deleted_at is not None:
        return False

    if hard_delete:
        session.delete(producto)
        session.commit()
        return True

    now = _utc_now()
    producto.deleted_at = now
    producto.updated_at = now
    producto.disponible = False
    session.add(producto)
    session.commit()
    return True


# [Consigna TP7 - Asignación o actualización de vínculo N:N ProductoCategoria]
# [Diagrama UML - PRODUCTO_CATEGORIA con es_principal]
def assign_categoria_to_producto(
    session: Session,
    data: ProductoCategoriaAssign,
) -> Optional[ProductoCategoria]:
    """Asigna o actualiza la asociación entre un producto y una categoría activa.

    Si es_principal es True, desmarca cualquier otra categoría principal previa del producto.
    Retorna el objeto ProductoCategoria o None si el producto o la categoría no existen o están inactivos.
    """
    producto = get_producto(session, data.producto_id)
    if not producto:
        return None

    categoria = session.get(Categoria, data.categoria_id)
    if not categoria or categoria.deleted_at is not None:
        return None

    if data.es_principal:
        existing_links = session.exec(
            select(ProductoCategoria).where(
                ProductoCategoria.producto_id == data.producto_id,
                ProductoCategoria.categoria_id != data.categoria_id,
            )
        ).all()
        for link in existing_links:
            if link.es_principal:
                link.es_principal = False
                session.add(link)

    existing = session.get(ProductoCategoria, (data.producto_id, data.categoria_id))
    if existing:
        existing.es_principal = data.es_principal
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    new_link = ProductoCategoria(
        producto_id=data.producto_id,
        categoria_id=data.categoria_id,
        es_principal=data.es_principal,
    )
    session.add(new_link)
    session.commit()
    session.refresh(new_link)
    return new_link


# [Consigna TP7 - Alias RESTful para asociar categoría retornando el Producto actualizado]
# [Diagrama UML - PRODUCTO y relación N:N con CATEGORIA]
def asociar_categoria(
    session: Session,
    producto_id: int,
    categoria_id: int,
    es_principal: bool = False,
) -> Optional[Producto]:
    """Asocia una categoría a un producto y retorna el producto con sus categorías actualizadas."""
    dto = ProductoCategoriaAssign(
        producto_id=producto_id,
        categoria_id=categoria_id,
        es_principal=es_principal,
    )
    link = assign_categoria_to_producto(session, dto)
    if not link:
        return None

    session.expire_all()
    return get_producto(session, producto_id)


# [Consigna TP7 - Desasociación de vínculo N:N ProductoCategoria]
# [Diagrama UML - Eliminación de tupla en PRODUCTO_CATEGORIA]
def remove_categoria_from_producto(
    session: Session,
    producto_id: int,
    categoria_id: int,
) -> bool:
    """Elimina la relación N:N entre un producto y una categoría. Retorna True si existía."""
    link = session.get(ProductoCategoria, (producto_id, categoria_id))
    if not link:
        return False

    session.delete(link)
    session.commit()
    return True


# Alias de compatibilidad arquitectónica
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
asignar_categoria = assign_categoria_to_producto
desasociar_categoria = remove_categoria_from_producto
