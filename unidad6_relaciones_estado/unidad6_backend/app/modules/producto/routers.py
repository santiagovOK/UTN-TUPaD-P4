from typing import List
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session
from app.database import get_session
from . import schemas, services

router = APIRouter(prefix="/productos", tags=["Productos"])


def _handle_domain_error(e: ValueError) -> None:
    """Mapea excepciones de dominio de la capa Service a códigos de estado HTTP."""
    msg = str(e)
    if "no encontrado" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=msg
        )
    if "duplicado" in msg.lower():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=msg
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=msg
    )


# ---------------------------------------------------------
# ALTA DE PRODUCTO
# Método: POST | Endpoint: /productos | Estado: 201 Created
# ---------------------------------------------------------
@router.post(
    "/",
    response_model=schemas.ProductoResponse,
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
# Método: GET | Endpoint: /productos | Estado: 200 OK
# ---------------------------------------------------------
@router.get(
    "/",
    response_model=List[schemas.ProductoResponse],
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
# Método: GET | Endpoint: /productos/{id} | Estado: 200 OK
# ---------------------------------------------------------
@router.get(
    "/{id}",
    response_model=schemas.ProductoResponse,
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
# Método: PUT | Endpoint: /productos/{id} | Estado: 200 OK
# ---------------------------------------------------------
@router.put(
    "/{id}",
    response_model=schemas.ProductoResponse,
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
# Método: DELETE | Endpoint: /productos/{id} | Estado: 204 No Content
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
# CONSULTAR STOCK (Lógica de Negocio)
# Método: GET | Endpoint: /productos/{id}/stock | Estado: 200 OK
# ---------------------------------------------------------
@router.get(
    "/{id}/stock",
    response_model=schemas.ProductoStockResponse,
    status_code=status.HTTP_200_OK,
)
def consultar_stock(
    id: int = Path(..., gt=0),
    db: Session = Depends(get_session),
):
    try:
        return services.obtener_estado_stock(db, id)
    except ValueError as e:
        _handle_domain_error(e)
