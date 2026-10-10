"""
Servicios de datos para la entidad Producto y la relación muchos a muchos ProductoCategoria.

[Consigna TP6 - Parte A, incisos b y d]:
  - Persistencia de Producto con SQLModel Session (creación, lectura, actualización, borrado lógico).
  - Gestión de la relación N:N con Categoria mediante la tabla intermedia ProductoCategoria.
[Consigna TP6 - Rúbrica Backend / Conclusiones Esperadas]:
  - CRUD Productos y relación N:N garantizando integridad referencial y prevención de duplicados.
"""

from typing import List
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select
from app.models.categoria import Categoria
from app.models.producto import Producto, ProductoCategoria
from .schemas import ProductoCreate, ProductoUpdate


# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: Alta de Producto con persistencia en DB y validación de unicidad

def crear_producto(session: Session, data: ProductoCreate) -> Producto:
    """Crea y persiste un nuevo producto en la base de datos.

    Valida la regla de negocio de unicidad por nombre (RN).
    Lanza ValueError("Producto duplicado") si el nombre ya existe.
    """
    existente = session.exec(
        select(Producto).where(Producto.nombre == data.nombre)
    ).first()
    if existente:
        raise ValueError("Producto duplicado")

    producto = Producto.model_validate(data)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


# [Consigna TP6 - Parte A, inciso d & Conclusiones Esperadas]:
# Consulta de detalle de Producto con "carga ansiosa" (Eager Loading) de categorías vinculadas
def obtener_producto_por_id(session: Session, id: int) -> Producto:
    """Obtiene un producto por su clave primaria incluyendo sus categorías vinculadas (Eager Loading).

    Lanza ValueError("Producto no encontrado") si no existe.
    """
    statement = (
        select(Producto)
        .where(Producto.id == id)
        .options(selectinload(Producto.categorias))
    )
    producto = session.exec(statement).first()
    if not producto:
        raise ValueError("Producto no encontrado")
    return producto


# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: Listado paginado de productos persistidos
def listar_productos(
    session: Session, skip: int = 0, limit: int = 10
) -> List[Producto]:
    """Retorna una lista paginada de productos persistidos con carga ansiosa de categorías."""
    statement = (
        select(Producto)
        .options(selectinload(Producto.categorias))
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())


# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: Modificación parcial o total de producto con control de duplicados
def actualizar_producto(
    session: Session, id: int, data: ProductoUpdate
) -> Producto:
    """Actualiza dinámicamente los campos especificados de un producto.

    Utiliza exclude_unset=True para actualizar solo los campos provistos.
    Si se intenta cambiar el nombre por uno ya existente, lanza ValueError("Producto duplicado").
    Lanza ValueError("Producto no encontrado") si el ID no existe.
    """
    producto = obtener_producto_por_id(session, id)

    update_dict = data.model_dump(exclude_unset=True)
    if not update_dict:
        return producto

    # Si se actualiza el nombre, verificar unicidad contra otros registros
    nuevo_nombre = update_dict.get("nombre")
    if nuevo_nombre and nuevo_nombre != producto.nombre:
        duplicado = session.exec(
            select(Producto).where(
                Producto.nombre == nuevo_nombre, Producto.id != id
            )
        ).first()
        if duplicado:
            raise ValueError("Producto duplicado")

    for key, value in update_dict.items():
        setattr(producto, key, value)

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


# [Consigna TP6 - Parte A, incisos b y d]: Borrado lógico actualizando el estado `disponible = False`
def eliminar_producto(session: Session, id: int) -> Producto:
    """Aplica borrado lógico marcando el producto como no disponible (disponible = False).
    """
    producto = obtener_producto_por_id(session, id)
    producto.disponible = False

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


# [Consigna TP6 - Parte A, incisos b y d & Conclusiones Esperadas]:
# Asociación N:N de Categoria a Producto mediante inserción en la tabla intermedia ProductoCategoria
def asociar_categoria(
    session: Session, producto_id: int, categoria_id: int
) -> Producto:
    """Asocia una categoría existente a un producto existente mediante la tabla intermedia ProductoCategoria.

    Lanza ValueError("Producto no encontrado") o ValueError("Categoría no encontrada") si alguno no existe.
    Lanza ValueError("Vínculo duplicado: la categoría ya está asociada al producto") si la relación ya existe.
    """
    producto = session.get(Producto, producto_id)
    if not producto:
        raise ValueError("Producto no encontrado")

    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise ValueError("Categoría no encontrada")

    vinculo_existente = session.exec(
        select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id,
        )
    ).first()
    if vinculo_existente:
        raise ValueError(
            "Vínculo duplicado: la categoría ya está asociada al producto"
        )

    vinculo = ProductoCategoria(
        producto_id=producto_id, categoria_id=categoria_id
    )
    session.add(vinculo)
    session.commit()
    session.expire(producto, ["categorias"])
    return obtener_producto_por_id(session, producto_id)


# [Consigna TP6 - Parte A, incisos b y d & Conclusiones Esperadas]:
# Desasociación N:N de Categoria y Producto mediante eliminación del registro en ProductoCategoria
def desasociar_categoria(
    session: Session, producto_id: int, categoria_id: int
) -> None:
    """Elimina la asociación entre un producto y una categoría en la tabla intermedia ProductoCategoria.
    Lanza ValueError("Producto no encontrado"), ValueError("Categoría no encontrada")
    o ValueError("Asociación no encontrada") si no existen.
    """
    producto = session.get(Producto, producto_id)
    if not producto:
        raise ValueError("Producto no encontrado")

    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        raise ValueError("Categoría no encontrada")

    vinculo = session.exec(
        select(ProductoCategoria).where(
            ProductoCategoria.producto_id == producto_id,
            ProductoCategoria.categoria_id == categoria_id,
        )
    ).first()
    if not vinculo:
        raise ValueError("Asociación no encontrada")

    session.delete(vinculo)
    session.commit()
    session.expire(producto, ["categorias"])
