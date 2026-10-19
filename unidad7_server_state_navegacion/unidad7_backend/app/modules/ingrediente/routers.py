"""Capa de enrutamiento HTTP para la entidad Ingrediente.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos - INGREDIENTE]
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlmodel import Session

from app.database import get_session
from . import services
from .schemas import (
    IngredienteCreate,
    IngredientePaginatedResponse,
    IngredienteRead,
    IngredienteUpdate,
)

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ingrediente en el catálogo",
)
def create_ingrediente(
    data: IngredienteCreate,
    session: Session = Depends(get_session),
):
    """Crea un ingrediente validando unidad de medida (404) y unicidad de nombre (409)."""
    try:
        return services.create_ingrediente(session, data)
    except services.IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except services.IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get(
    "/",
    response_model=IngredientePaginatedResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar ingredientes con paginación y filtros",
)
def list_ingredientes(
    offset: int = Query(0, ge=0, description="Desplazamiento inicial para paginación"),
    limit: int = Query(10, ge=1, le=100, description="Cantidad máxima de registros por página"),
    nombre: Optional[str] = Query(None, max_length=100, description="Filtro parcial por nombre"),
    search: Optional[str] = Query(None, max_length=100, description="Alias retrocompatible por nombre"),
    incluir_inactivos: bool = Query(False, description="Incluir registros dados de baja lógica"),
    session: Session = Depends(get_session),
):
    """Retorna la lista de ingredientes paginados con conteo total de coincidencias."""
    total, items = services.get_ingredientes(
        session=session,
        offset=offset,
        limit=limit,
        nombre=nombre,
        search=search,
        incluir_inactivos=incluir_inactivos,
    )
    return {"total": total, "items": items}


@router.get(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener ingrediente por ID",
)
def get_ingrediente(
    ingrediente_id: int = Path(..., gt=0, description="Identificador único del ingrediente"),
    session: Session = Depends(get_session),
):
    """Obtiene un ingrediente activo por su ID primario o 404 si no existe o está inactivo."""
    ingrediente = services.get_ingrediente(session, ingrediente_id)
    if not ingrediente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ingrediente no encontrado",
        )
    return ingrediente


@router.put(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar ingrediente completo",
)
def update_ingrediente_put(
    ingrediente_id: int = Path(..., gt=0, description="Identificador único del ingrediente"),
    data: IngredienteUpdate = ...,
    session: Session = Depends(get_session),
):
    """Actualiza los datos de un ingrediente activo."""
    try:
        ingrediente = services.update_ingrediente(session, ingrediente_id, data)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return ingrediente
    except services.IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except services.IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch(
    "/{ingrediente_id}",
    response_model=IngredienteRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar parcialmente ingrediente",
)
def update_ingrediente_patch(
    ingrediente_id: int = Path(..., gt=0, description="Identificador único del ingrediente"),
    data: IngredienteUpdate = ...,
    session: Session = Depends(get_session),
):
    """Actualiza parcialmente un ingrediente activo."""
    try:
        ingrediente = services.update_ingrediente(session, ingrediente_id, data)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return ingrediente
    except services.IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except services.IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ingrediente (baja lógica o física)",
)
def delete_ingrediente(
    ingrediente_id: int = Path(..., gt=0, description="Identificador único del ingrediente"),
    hard: bool = Query(False, description="Si es True, realiza borrado físico; si es False, baja lógica"),
    session: Session = Depends(get_session),
):
    """Elimina un ingrediente mediante baja lógica o física verificando que no tenga productos asociados."""
    try:
        ok = services.delete_ingrediente(session, ingrediente_id, hard_delete=hard)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return None
    except services.IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
