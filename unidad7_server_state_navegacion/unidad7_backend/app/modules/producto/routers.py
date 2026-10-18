"""Capa de enrutamiento HTTP para la entidad Producto y la relación asociativa N:N ProductoCategoria.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - PRODUCTO y tabla asociativa PRODUCTO_CATEGORIA]
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.database import get_session
from . import services
from .schemas import (
    ProductoCategoriaAssign,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoPaginatedResponse,
    ProductoRead,
    ProductoUpdate,
)

router = APIRouter(prefix="/productos", tags=["Productos"])


# [Consigna TP7 - Endpoint POST /productos/ con control de conflicto 409]
# [Diagrama UML - Creación de PRODUCTO]
@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
)
def create_producto(
    data: ProductoCreate,
    session: Session = Depends(get_session),
):
    """Crea un nuevo producto en el catálogo verificando unicidad de nombre."""
    try:
        return services.create_producto(session, data)
    except services.ProductoConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# [Consigna TP7 - Endpoint GET /productos/ paginado con conteo atómico y filtros]
# [Diagrama UML - Consulta paginada de PRODUCTO con selectinload(Producto.categorias)]
@router.get(
    "/",
    response_model=ProductoPaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar productos con paginación y filtros",
)
def list_productos(
    offset: int = Query(0, ge=0, description="Cantidad de registros a omitir (no negativo)"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima de registros a retornar (1 a 100)"),
    nombre: Optional[str] = Query(None, max_length=150, description="Filtro de búsqueda parcial por nombre"),
    disponible: Optional[bool] = Query(None, description="Filtro por estado de disponibilidad"),
    categoria_id: Optional[int] = Query(None, gt=0, description="Filtro por ID de categoría asociada"),
    session: Session = Depends(get_session),
):
    """Retorna la lista de productos activos con paginación, filtros dinámicos y categorías anidadas."""
    total, items = services.get_productos(
        session=session,
        offset=offset,
        limit=limit,
        nombre=nombre,
        disponible=disponible,
        categoria_id=categoria_id,
    )
    return {"total": total, "items": items}


# [Consigna TP7 - Endpoint POST /productos/categorias/asignar para asignación N:N]
# [Diagrama UML - PRODUCTO_CATEGORIA con es_principal]
@router.post(
    "/categorias/asignar",
    response_model=ProductoCategoriaRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Producto-Categoría"],
    summary="Asignar o actualizar relación producto-categoría",
)
def assign_categoria(
    data: ProductoCategoriaAssign,
    session: Session = Depends(get_session),
):
    """Crea o actualiza el vínculo N:N entre un producto y una categoría activa."""
    link = services.assign_categoria_to_producto(session, data)
    if not link:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto o Categoría inexistente",
        )
    return link


# [Consigna TP7 - Endpoint GET /productos/{producto_id} por ID con control 404]
# [Diagrama UML - Detalle de PRODUCTO con categorías anidadas]
@router.get(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener producto por ID",
)
def get_producto(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    session: Session = Depends(get_session),
):
    """Obtiene un producto activo por su identificador primario con sus categorías anidadas."""
    producto = services.get_producto(session, producto_id)
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return producto


# [Consigna TP7 - Endpoint PUT /productos/{producto_id} con actualización completa o parcial]
# [Diagrama UML - Modificación de PRODUCTO]
@router.put(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar producto de forma completa o parcial",
)
def update_producto_put(
    data: ProductoUpdate,
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    session: Session = Depends(get_session),
):
    """Actualiza los datos de un producto activo verificando unicidad de nombre."""
    try:
        producto = services.update_producto(session, producto_id, data)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return producto
    except services.ProductoConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# [Consigna TP7 - Endpoint PATCH /productos/{producto_id} con actualización parcial]
# [Diagrama UML - Modificación parcial de PRODUCTO]
@router.patch(
    "/{producto_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente un producto",
)
def update_producto_patch(
    data: ProductoUpdate,
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    session: Session = Depends(get_session),
):
    """Actualiza parcialmente los datos de un producto activo verificando unicidad de nombre."""
    try:
        producto = services.update_producto(session, producto_id, data)
        if not producto:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Producto no encontrado",
            )
        return producto
    except services.ProductoConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# [Consigna TP7 - Endpoint DELETE /productos/{producto_id} con baja lógica por defecto o física]
# [Diagrama UML - Eliminación o baja de PRODUCTO]
@router.delete(
    "/{producto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar producto",
)
def delete_producto(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    hard: bool = Query(False, description="Si es True realiza borrado físico; por defecto aplica borrado lógico"),
    session: Session = Depends(get_session),
):
    """Elimina un producto mediante baja lógica (por defecto) o física (?hard=true)."""
    exito = services.delete_producto(session, producto_id, hard_delete=hard)
    if not exito:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto no encontrado",
        )
    return None


# [Consigna TP7 - Endpoint POST /productos/{producto_id}/categorias/{categoria_id} (alias de conveniencia)]
# [Diagrama UML - PRODUCTO y relación N:N con CATEGORIA]
@router.post(
    "/{producto_id}/categorias/{categoria_id}",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    tags=["Producto-Categoría"],
    summary="Asociar categoría a un producto (alias RESTful)",
)
def asociar_categoria_endpoint(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    es_principal: bool = Query(False, description="Indica si la categoría asignada es la principal"),
    session: Session = Depends(get_session),
):
    """Asocia una categoría a un producto y retorna el producto actualizado con sus categorías."""
    producto = services.asociar_categoria(
        session=session,
        producto_id=producto_id,
        categoria_id=categoria_id,
        es_principal=es_principal,
    )
    if not producto:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Producto o Categoría inexistente",
        )
    return producto


# [Consigna TP7 - Endpoint DELETE /productos/{producto_id}/categorias/{categoria_id} para desvincular]
# [Diagrama UML - Eliminación de tupla asociativa PRODUCTO_CATEGORIA]
@router.delete(
    "/{producto_id}/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Producto-Categoría"],
    summary="Desasociar categoría de un producto",
)
def remove_categoria_endpoint(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    session: Session = Depends(get_session),
):
    """Elimina el vínculo N:N entre un producto y una categoría."""
    eliminado = services.remove_categoria_from_producto(
        session=session,
        producto_id=producto_id,
        categoria_id=categoria_id,
    )
    if not eliminado:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vínculo Producto-Categoría no encontrado",
        )
    return None
