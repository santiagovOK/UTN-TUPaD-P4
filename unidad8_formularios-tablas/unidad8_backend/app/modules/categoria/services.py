"""Capa de servicio para la entidad Categoria.

[Catálogo heredado del TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos - CATEGORIA]
"""

from typing import List, Optional, Tuple, Union

from sqlalchemy.orm import selectinload
from sqlmodel import Session, func, select

from app.models.categoria import Categoria
from app.models.producto import Producto, ProductoCategoria, _utc_now
from .schemas import CategoriaCreate, CategoriaUpdate


class CategoriaConflictError(ValueError):
    """Excepción de dominio lanzada cuando el nombre de categoría ya existe."""


# [Catálogo heredado del TP7 - Alta de categoría con control de duplicados y reactivación tras baja lógica]
# [Diagrama UML - CATEGORIA.nombre VARCHAR(100) UNIQUE]
def create_categoria(session: Session, data: CategoriaCreate) -> Categoria:
    """Crea una categoría verificando unicidad insensible a mayúsculas/minúsculas.

    Si existe una categoría dada de baja lógica con el mismo nombre, la reactiva
    limpiando deleted_at y actualizando sus atributos para evitar colisiones UNIQUE.
    """
    colision = session.exec(
        select(Categoria).where(func.lower(Categoria.nombre) == data.nombre.lower())
    ).first()

    if colision:
        if colision.deleted_at is None:
            raise CategoriaConflictError(f"Ya existe una categoría con el nombre '{data.nombre}'.")
        # Reactivación transparente tras baja lógica
        now = _utc_now()
        colision.nombre = data.nombre
        colision.descripcion = data.descripcion or ""
        colision.deleted_at = None
        colision.updated_at = now
        session.add(colision)
        session.commit()
        session.refresh(colision)
        return colision

    categoria = Categoria.model_validate(data)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


# [Catálogo heredado del TP7 - Listado paginado con orden estricto de 4 pasos]
# [Diagrama UML - Colección de CATEGORIA activas]
def get_categorias(
    session: Session,
    offset: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    nombre: Optional[str] = None,
    incluir_inactivos: bool = False,
) -> Tuple[int, List[Categoria]]:
    """Retorna el total de coincidencias y los registros activos paginados.

    Sigue el orden estricto de 4 pasos:
    1. Consulta base filtrando registros activos (deleted_at IS NULL).
    2. Filtro dinámico condicional por nombre.
    3. Conteo atómico en motor SQL sobre la consulta ya filtrada (subquery).
    4. Extracción de ventana paginada ordenada por ID.
    """
    # 1. Consulta base (registros activos salvo que incluir_inactivos sea True)
    query = select(Categoria)
    if not incluir_inactivos:
        query = query.where(Categoria.deleted_at.is_(None))

    # 2. Filtro dinámico condicional por nombre (o search) insensible a mayúsculas
    filtro_nombre = nombre if nombre is not None else search
    if filtro_nombre and filtro_nombre.strip():
        query = query.where(Categoria.nombre.ilike(f"%{filtro_nombre.strip()}%"))
    # 3. Conteo atómico en el motor SQL sobre la consulta ya filtrada
    count_query = select(func.count()).select_from(query.subquery())
    total: int = session.exec(count_query).one()

    # 4. Extracción de ventana paginada ordenada de manera determinista
    items = session.exec(query.order_by(Categoria.id).offset(offset).limit(limit)).all()
    return total, list(items)


# [Catálogo heredado del TP7 - Detalle de categoría activa por ID]
# [Diagrama UML - CATEGORIA.id PK]
def get_categoria(session: Session, categoria_id: int) -> Optional[Categoria]:
    """Obtiene una categoría por ID solo si no fue dada de baja lógica."""
    categoria = session.get(Categoria, categoria_id)
    if not categoria or categoria.deleted_at is not None:
        return None
    return categoria


# [Catálogo heredado del TP7 - Actualización parcial o total con exclude_unset y control de unicidad]
# [Diagrama UML - Modificación de atributos de CATEGORIA]
def update_categoria(
    session: Session,
    categoria_id: int,
    data: Union[CategoriaUpdate, CategoriaCreate],
) -> Optional[Categoria]:
    """Actualiza una categoría existente verificando colisión de nombres."""
    categoria = get_categoria(session, categoria_id)
    if not categoria:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "nombre" in update_data and update_data["nombre"] is not None:
        nuevo_nombre = update_data["nombre"]
        colision = session.exec(
            select(Categoria).where(
                func.lower(Categoria.nombre) == nuevo_nombre.lower(),
                Categoria.id != categoria_id,
            )
        ).first()
        if colision:
            raise CategoriaConflictError(f"Ya existe una categoría con el nombre '{nuevo_nombre}'.")

    if "descripcion" in update_data and update_data["descripcion"] is None:
        update_data["descripcion"] = ""

    for key, value in update_data.items():
        setattr(categoria, key, value)

    categoria.updated_at = _utc_now()
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


# [Catálogo heredado del TP7 - Baja lógica de categoría preservando auditoría y validando productos asociados]
# [Diagrama UML - CATEGORIA.deleted_at TIMESTAMP]
def soft_delete_categoria(session: Session, categoria_id: int) -> Optional[Categoria]:
    """Marca la categoría con baja lógica asignando deleted_at tras validar que no tenga productos asociados."""
    categoria = get_categoria(session, categoria_id)
    if not categoria:
        return None

    # Validación de productos asociados activos (catálogo heredado del TP7)
    productos_asociados = session.exec(
        select(func.count())
        .select_from(ProductoCategoria)
        .join(Producto, Producto.id == ProductoCategoria.producto_id)
        .where(
            ProductoCategoria.categoria_id == categoria_id,
            Producto.deleted_at.is_(None),
        )
    ).one()
    if productos_asociados > 0:
        raise CategoriaConflictError(
            "No se puede eliminar la categoría porque tiene productos asociados."
        )

    now = _utc_now()
    categoria.deleted_at = now
    categoria.updated_at = now
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


# [Catálogo heredado del TP7 - Baja lógica de categoría (no se borra de la base de datos)]
# [Diagrama UML - Ciclo de vida de CATEGORIA]
def delete_categoria(session: Session, categoria_id: int) -> bool:
    """Da de baja lógicamente una categoría tras validar que no tenga productos activos asociados."""
    categoria = session.get(Categoria, categoria_id)
    if not categoria or categoria.deleted_at is not None:
        return False

    # Validación de productos asociados activos (catálogo heredado del TP7)
    productos_asociados = session.exec(
        select(func.count())
        .select_from(ProductoCategoria)
        .join(Producto, Producto.id == ProductoCategoria.producto_id)
        .where(
            ProductoCategoria.categoria_id == categoria_id,
            Producto.deleted_at.is_(None),
        )
    ).one()
    if productos_asociados > 0:
        raise CategoriaConflictError(
            "No se puede eliminar la categoría porque tiene productos asociados."
        )

    now = _utc_now()
    categoria.deleted_at = now
    categoria.updated_at = now
    session.add(categoria)
    session.commit()
    return True


# [Catálogo heredado del TP7 - Consulta de productos asociados a una categoría]
# [Diagrama UML - Clúster Catálogo de Productos - CATEGORIA -> PRODUCTO]
def get_productos_by_categoria_id(
    session: Session,
    categoria_id: int,
) -> Optional[List[Producto]]:
    """Retorna la lista de productos activos asociados a una categoría activa o None si no existe."""
    categoria = get_categoria(session, categoria_id)
    if not categoria:
        return None

    query = (
        select(Producto)
        .join(ProductoCategoria, Producto.id == ProductoCategoria.producto_id)
        .where(
            ProductoCategoria.categoria_id == categoria_id,
            Producto.deleted_at.is_(None),
        )
        .options(selectinload(Producto.categorias.and_(Categoria.deleted_at.is_(None))))
        .order_by(Producto.id)
    )
    productos = session.exec(query).all()
    return list(productos)


# Alias de compatibilidad arquitectónica
crear = create_categoria
obtener_todas = get_categorias
obtener_por_id = get_categoria
actualizar = update_categoria
actualizar_total = update_categoria
eliminar = delete_categoria
desactivar = soft_delete_categoria
obtener_productos_por_categoria = get_productos_by_categoria_id
