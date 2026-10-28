"""Capa de enrutamiento HTTP para la entidad Ingrediente.

[TP8 - Ampliación Opcional: Patrón Repository y Unit of Work en Ingredientes]
[HU-05: Catálogo de Ingredientes - Rutas REST y códigos de estado HTTP]
[RN-10: Unicidad de nombre de ingrediente insensible a mayúsculas]
[RN-11: Restricción de baja con productos activos asociados]
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from .schemas import (
    IngredienteCreate,
    IngredientePaginatedResponse,
    IngredienteRead,
    IngredienteUpdate,
)
from .services import (
    IngredienteConflictError,
    IngredienteService,
    IngredienteUnidadNotFoundError,
)
from .unit_of_work import IngredienteUnitOfWork

router = APIRouter(prefix="/ingredientes", tags=["Ingredientes"])


def get_ingrediente_service() -> IngredienteService:
    """Proveedor de dependencias para el servicio de dominio de Ingredientes con Unit of Work."""
    return IngredienteService(uow=IngredienteUnitOfWork())


@router.post(
    "/",
    response_model=IngredienteRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo ingrediente en el catálogo",
)
def create_ingrediente(
    data: IngredienteCreate,
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Crea un ingrediente validando unidad de medida (404) y unicidad de nombre (409)."""
    try:
        return service.crear(data)
    except IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except IngredienteConflictError as exc:
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
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Retorna la lista de ingredientes paginados con conteo total de coincidencias."""
    total, items = service.listar(
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
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Obtiene un ingrediente activo por su ID primario o 404 si no existe o está inactivo."""
    ingrediente = service.obtener(ingrediente_id)
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
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Actualiza los datos de un ingrediente activo."""
    try:
        ingrediente = service.actualizar(ingrediente_id, data)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return ingrediente
    except IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except IngredienteConflictError as exc:
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
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Actualiza parcialmente un ingrediente activo."""
    try:
        ingrediente = service.actualizar(ingrediente_id, data)
        if not ingrediente:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return ingrediente
    except IngredienteUnidadNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete(
    "/{ingrediente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar ingrediente (baja lógica)",
)
def delete_ingrediente(
    ingrediente_id: int = Path(..., gt=0, description="Identificador único del ingrediente"),
    service: IngredienteService = Depends(get_ingrediente_service),
):
    """Da de baja lógicamente un ingrediente verificando que no tenga productos asociados."""
    try:
        ok = service.eliminar(ingrediente_id)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ingrediente no encontrado",
            )
        return None
    except IngredienteConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
