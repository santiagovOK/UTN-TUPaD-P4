from typing import Any, Dict, List, Optional
from sqlmodel import Session, select
from app.models.producto import Producto
from .schemas import ProductoCreate, ProductoUpdate


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


def obtener_producto_por_id(session: Session, id: int) -> Producto:
    """Obtiene un producto por su clave primaria.

    Lanza ValueError("Producto no encontrado") si no existe.
    """
    producto = session.get(Producto, id)
    if not producto:
        raise ValueError("Producto no encontrado")
    return producto


def listar_productos(
    session: Session, skip: int = 0, limit: int = 10
) -> List[Producto]:
    """Retorna una lista paginada de productos persistidos."""
    statement = select(Producto).offset(skip).limit(limit)
    return list(session.exec(statement).all())


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


def eliminar_producto(session: Session, id: int) -> Producto:
    """Aplica borrado lógico desactivando el producto (activo = False).

    Lanza ValueError("Producto no encontrado") si no existe.
    """
    producto = obtener_producto_por_id(session, id)
    producto.activo = False

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


def obtener_estado_stock(session: Session, id: int) -> Dict[str, Any]:
    """Calcula y retorna el estado de stock y alerta de reposición.

    Lanza ValueError("Producto no encontrado") si el ID no existe.
    Resguarda posibles valores nulos en stock o stock_minimo.
    """
    producto = obtener_producto_por_id(session, id)

    stock = producto.stock if producto.stock is not None else 0
    stock_minimo = producto.stock_minimo if producto.stock_minimo is not None else 0
    alerta_stock = stock < stock_minimo

    return {
        "stock": stock,
        "bajo_stock_minimo": alerta_stock,
        "activo": bool(producto.activo),
    }
