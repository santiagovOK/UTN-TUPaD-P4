"""Rutas HTTP para la gestión del catálogo de productos."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.database import get_session
from app.modules.categoria.schemas import CategoriaRead
from app.modules.ingrediente.schemas import IngredienteRead
from . import services
from .schemas import ProductoCreate, ProductoPaginatedResponse, ProductoRead, ProductoUpdate

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post(
    "/",
    response_model=ProductoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo producto",
)
def create_producto(data: ProductoCreate, session: Session = Depends(get_session)):
    try:
        return services.create_producto(session, data)
    except services.ProductoRelationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


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
    incluir_inactivos: bool = Query(False, description="Incluir productos dados de baja lógica"),
    session: Session = Depends(get_session),
):
    total, items = services.get_productos(
        session=session,
        offset=offset,
        limit=limit,
        nombre=nombre,
        disponible=disponible,
        categoria_id=categoria_id,
        incluir_inactivos=incluir_inactivos,
    )
    return {"total": total, "items": items}


@router.get(
    "/{producto_id}/categorias",
    response_model=List[CategoriaRead],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías activas de un producto",
)
def get_categorias_by_producto(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    session: Session = Depends(get_session),
):
    categorias = services.get_categorias_by_producto_id(session, producto_id)
    if categorias is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return categorias


@router.get(
    "/{producto_id}/ingredientes",
    response_model=List[IngredienteRead],
    status_code=status.HTTP_200_OK,
    summary="Listar ingredientes activos de un producto",
)
def get_ingredientes_by_producto(
    producto_id: int = Path(..., gt=0, description="Identificador único del producto"),
    session: Session = Depends(get_session),
):
    ingredientes = services.get_ingredientes_by_producto_id(session, producto_id)
    if ingredientes is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return ingredientes


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
    producto = services.get_producto(session, producto_id)
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


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
    try:
        producto = services.update_producto(session, producto_id, data)
    except services.ProductoRelationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


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
    try:
        producto = services.update_producto(session, producto_id, data)
    except services.ProductoRelationNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if producto is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return producto


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
    if not services.delete_producto(session, producto_id, hard_delete=hard):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Producto no encontrado")
    return None
