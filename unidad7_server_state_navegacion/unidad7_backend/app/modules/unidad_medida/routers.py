"""Capa de enrutamiento HTTP para la entidad UnidadMedida (solo lectura).

[Consigna TP7 - Catálogo base oficial de unidades de medida]
[Diagrama UML - Clúster Catálogo de Productos - UNIDAD_MEDIDA]
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlmodel import Session

from app.database import get_session
from . import services
from .schemas import UnidadMedidaListResponse, UnidadMedidaRead

router = APIRouter(prefix="/unidades-medida", tags=["Unidades de Medida"])


@router.get(
    "/",
    response_model=UnidadMedidaListResponse,
    status_code=status.HTTP_200_OK,
    summary="Listar unidades de medida del catálogo oficial",
)
def list_unidades_medida(
    session: Session = Depends(get_session),
):
    """Retorna todas las unidades de medida predefinidas en el catálogo del sistema."""
    total, items = services.get_unidades_medida(session)
    return {"total": total, "items": items}


@router.get(
    "/{unidad_id}",
    response_model=UnidadMedidaRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener detalle de unidad de medida por ID",
)
def get_unidad_medida(
    unidad_id: int = Path(..., gt=0, description="Identificador único de la unidad de medida"),
    session: Session = Depends(get_session),
):
    """Retorna los datos de una unidad de medida por su ID o 404 si no existe."""
    unidad = services.get_unidad_medida_by_id(session, unidad_id)
    if not unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unidad de medida no encontrada",
        )
    return unidad
