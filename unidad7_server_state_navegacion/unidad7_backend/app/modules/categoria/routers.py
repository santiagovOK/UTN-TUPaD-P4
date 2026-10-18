"""Capa de enrutamiento HTTP para la entidad Categoria.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos - CATEGORIA]
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.database import get_session
from . import services
from .schemas import (
    CategoriaCreate,
    CategoriaPaginatedResponse,
    CategoriaRead,
    CategoriaUpdate,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])


# [Consigna TP7 - Endpoint POST /categorias/ con control de conflicto 409]
# [Diagrama UML - Creación de CATEGORIA]
@router.post(
    "/",
    response_model=CategoriaRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear categoría",
)
def create_categoria(
    data: CategoriaCreate,
    session: Session = Depends(get_session),
):
    """Crea una nueva categoría en el catálogo.

    Retorna 409 Conflict si el nombre ya existe activo. Si el nombre correspondía
    a una categoría con baja lógica, es reactivada automáticamente.
    """
    try:
        return services.create_categoria(session, data)
    except services.CategoriaConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# [Consigna TP7 - Endpoint GET /categorias/ paginado con conteo atómico y filtros]
# [Diagrama UML - Consulta paginada de CATEGORIA]
@router.get(
    "/",
    response_model=CategoriaPaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar categorías paginadas",
)
def list_categorias(
    offset: int = Query(0, ge=0, description="Cantidad de registros a omitir (no negativo)"),
    limit: int = Query(50, ge=1, le=100, description="Cantidad máxima de registros a retornar (1 a 100)"),
    search: Optional[str] = Query(None, max_length=100, description="Filtro de búsqueda parcial por nombre"),
    session: Session = Depends(get_session),
):
    """Retorna la lista de categorías activas con paginación y búsqueda dinámica."""
    total, items = services.get_categorias(
        session=session,
        offset=offset,
        limit=limit,
        search=search,
    )
    return {"total": total, "items": items}


# [Consigna TP7 - Endpoint GET /categorias/{categoria_id} por ID con control 404]
# [Diagrama UML - Detalle de CATEGORIA]
@router.get(
    "/{categoria_id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener categoría por ID",
)
def get_categoria(
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    session: Session = Depends(get_session),
):
    """Obtiene una categoría activa por su identificador primario."""
    categoria = services.get_categoria(session, categoria_id)
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


# [Consigna TP7 - Endpoint PUT /categorias/{categoria_id} con actualización completa/parcial]
# [Diagrama UML - Modificación de CATEGORIA]
@router.put(
    "/{categoria_id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar categoría (PUT)",
)
def update_categoria_put(
    data: CategoriaUpdate,
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    session: Session = Depends(get_session),
):
    """Actualiza los datos de una categoría activa."""
    try:
        categoria = services.update_categoria(session, categoria_id, data)
    except services.CategoriaConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


# [Consigna TP7 - Endpoint PATCH /categorias/{categoria_id} con actualización parcial exclude_unset]
# [Diagrama UML - Modificación parcial de CATEGORIA]
@router.patch(
    "/{categoria_id}",
    response_model=CategoriaRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente categoría (PATCH)",
)
def update_categoria_patch(
    data: CategoriaUpdate,
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    session: Session = Depends(get_session),
):
    """Actualiza parcialmente los datos de una categoría activa."""
    try:
        categoria = services.update_categoria(session, categoria_id, data)
    except services.CategoriaConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return categoria


# [Consigna TP7 - Endpoint DELETE /categorias/{categoria_id} con baja lógica por defecto o física]
# [Diagrama UML - Eliminación o baja de CATEGORIA]
@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar categoría",
)
def delete_categoria(
    categoria_id: int = Path(..., gt=0, description="Identificador único de la categoría"),
    hard: bool = Query(False, description="Si es True realiza borrado físico; por defecto aplica borrado lógico"),
    session: Session = Depends(get_session),
):
    """Elimina una categoría mediante baja lógica (por defecto) o física (?hard=true)."""
    deleted = services.delete_categoria(session, categoria_id, hard_delete=hard)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoría no encontrada",
        )
    return None
