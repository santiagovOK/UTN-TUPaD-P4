"""
Endpoints REST para el módulo Proveedor.
"""
from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import Annotated, List, Optional
from . import schemas, services

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])


@router.post(
    "/", response_model=schemas.ProveedorRead, status_code=status.HTTP_201_CREATED
)
def alta_proveedor(proveedor: schemas.ProveedorCreate):
    return services.crear_proveedor(proveedor)


@router.get(
    "/", response_model=List[schemas.ProveedorRead], status_code=status.HTTP_200_OK
)
def listar_proveedores(
    skip: Annotated[int, Query(ge=0, description="Cantidad de registros a saltar")] = 0,
    limit: Annotated[int, Query(ge=1, le=50, description="Cantidad maxima a retornar")] = 10,
    activo: Annotated[Optional[bool], Query(description="Filtrar por estado activo")] = None
):
    return services.listar_proveedores(skip=skip, limit=limit, activo=activo)


@router.get(
    "/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK
)
def detalle_proveedor(
    id: Annotated[int, Path(gt=0, description="Identificador unico del proveedor")]
):
    return services.obtener_proveedor_por_id(id)


@router.put(
    "/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK
)
def actualizar_proveedor(
    proveedor: schemas.ProveedorUpdate,
    id: Annotated[int, Path(gt=0, description="Identificador unico del proveedor")]
):
    return services.actualizar_proveedor(id, proveedor)


@router.put(
    "/{id}/desactivar",
    response_model=schemas.ProveedorRead,
    status_code=status.HTTP_200_OK
)
def desactivar_proveedor(
    id: Annotated[int, Path(gt=0, description="Identificador unico del proveedor")]
):
    return services.desactivar_proveedor(id)
