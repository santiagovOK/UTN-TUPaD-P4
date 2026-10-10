"""
Enrutador FastAPI para endpoints de Producto y gestión de relación N:N con Categorías.

[Consigna TP6 - Parte A, inciso d]: Implementar los endpoints de Producto demostrables con REST Client.
[Consigna TP6 - Rúbrica Backend / Conclusiones Esperadas]:
  - Endpoints REST para CRUD de Producto (POST, GET, GET/{id}, PUT/{id}, DELETE/{id}).
  - Endpoints para asociar y desasociar categorías (POST/DELETE /{id}/categorias/{categoria_id}).
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session
from app.database import get_session
from . import schemas, services

# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: Router prefijado en /productos
router = APIRouter(prefix="/productos", tags=["Productos"])


def _handle_domain_error(e: ValueError) -> None:
    """Mapea excepciones de dominio de la capa Service a códigos de estado HTTP."""
    msg = str(e)
    msg_lower = msg.lower()
    if "no encontrado" in msg_lower or "no encontrada" in msg_lower:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=msg
        )
    if "duplicado" in msg_lower or "duplicada" in msg_lower:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=msg
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=msg
    )

# ---------------------------------------------------------
# ALTA DE PRODUCTO
# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: POST /productos - Alta de producto con código 201 Created
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=schemas.ProductoRead,
    status_code=status.HTTP_201_CREATED,
)
def alta_producto(
    producto: schemas.ProductoCreate,
    db: Session = Depends(get_session),
):
    try:
        return services.crear_producto(db, producto)
    except ValueError as e:
        _handle_domain_error(e)


# ---------------------------------------------------------
# LISTAR PRODUCTOS
# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: GET /productos - Listado paginado con código 200 OK
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=List[schemas.ProductoReadConCategorias],
    status_code=status.HTTP_200_OK,
)
def listar_productos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_session),
):
    return services.listar_productos(db, skip=skip, limit=limit)


# ---------------------------------------------------------
# DETALLE DE PRODUCTO
# [Consigna TP6 - Parte A, inciso d & Conclusiones Esperadas]:
# GET /productos/{id} - Detalle de producto con categorías asociadas anidadas (código 200 OK)
# ---------------------------------------------------------
@router.get(
    "/{id}",
    response_model=schemas.ProductoReadConCategorias,
    status_code=status.HTTP_200_OK,
)
def detalle_producto(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        return services.obtener_producto_por_id(db, id)
    except ValueError as e:
        _handle_domain_error(e)


# ---------------------------------------------------------
# ACTUALIZACIÓN (Parcial o Total)
# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]: PUT /productos/{id} - Modificación con código 200 OK
# ---------------------------------------------------------
@router.put(
    "/{id}",
    response_model=schemas.ProductoRead,
    status_code=status.HTTP_200_OK,
)
def actualizar_producto(
    producto: schemas.ProductoUpdate,
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        return services.actualizar_producto(db, id, producto)
    except ValueError as e:
        _handle_domain_error(e)


# ---------------------------------------------------------
# BORRADO LÓGICO
# [Consigna TP6 - Parte A, incisos b y d]: DELETE /productos/{id} - Borrado lógico (disponible=False) con código 204 No Content
# ---------------------------------------------------------
@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def eliminar_producto(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        services.eliminar_producto(db, id)
    except ValueError as e:
        _handle_domain_error(e)
    return None


# ---------------------------------------------------------
# ASOCIAR CATEGORÍA A PRODUCTO (Relación N:N)
# [Consigna TP6 - Parte A, incisos b y d & Conclusiones Esperadas]:
# POST /productos/{id}/categorias/{categoria_id} - Asociación N:N con código 201 Created
# ---------------------------------------------------------
@router.post(
    "/{id}/categorias/{categoria_id}",
    response_model=schemas.ProductoReadConCategorias,
    status_code=status.HTTP_201_CREATED,
)
def asociar_categoria_a_producto(
    id: int = Path(..., gt=0),
    categoria_id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        return services.asociar_categoria(db, id, categoria_id)
    except ValueError as e:
        _handle_domain_error(e)


# ---------------------------------------------------------
# DESASOCIAR CATEGORÍA DE PRODUCTO (Relación N:N)
# [Consigna TP6 - Parte A, incisos b y d & Conclusiones Esperadas]:
# DELETE /productos/{id}/categorias/{categoria_id} - Desvinculación N:N con código 204 No Content
# ---------------------------------------------------------
@router.delete(
    "/{id}/categorias/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def desasociar_categoria_de_producto(
    id: int = Path(..., gt=0),
    categoria_id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        services.desasociar_categoria(db, id, categoria_id)
    except ValueError as e:
        _handle_domain_error(e)
    return None
