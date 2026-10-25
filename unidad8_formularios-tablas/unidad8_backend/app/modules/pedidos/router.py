"""Router REST para la gestión del agregado Pedidos.

[TP8 - Ejercicio 1.c: Router REST y cinco endpoints del agregado]
[HU-07: Gestión de Pedidos - Endpoints HTTP]
[RN-09, RN-12, RN-13, RN-14, RN-15, RN-16: Códigos HTTP semánticos y traducción de excepciones]
"""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.modules.pedidos.schemas import PedidoCreate, PedidoRead, PedidoUpdate
from app.modules.pedidos.service import (
    DetalleInvalidoError,
    PedidoNoEncontrado,
    PedidoService,
    ProductoNoEncontrado,
)
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def get_pedido_service() -> PedidoService:
    """Proveedor de dependencia para PedidoService con PedidoUnitOfWork."""
    return PedidoService(uow=PedidoUnitOfWork())


@router.get(
    "",
    response_model=List[PedidoRead],
    status_code=status.HTTP_200_OK,
    summary="Listar pedidos activos",
)
@router.get(
    "/",
    response_model=List[PedidoRead],
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def listar_pedidos(
    offset: int = Query(0, ge=0, description="Cantidad de registros a omitir"),
    limit: Optional[int] = Query(
        None, ge=1, le=100, description="Cantidad máxima de registros a retornar"
    ),
    service: PedidoService = Depends(get_pedido_service),
) -> List[PedidoRead]:
    """Retorna la lista de pedidos no eliminados con paginación opcional."""
    return service.listar(offset=offset, limit=limit)


@router.get(
    "/{pedido_id}",
    response_model=PedidoRead,
    status_code=status.HTTP_200_OK,
    summary="Obtener pedido por ID con sus detalles",
)
def obtener_pedido(
    pedido_id: int = Path(..., gt=0, description="Identificador único del pedido"),
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoRead:
    """Devuelve un pedido específico con sus detalles asociados.

    Responde 404 si el pedido no existe o fue dado de baja lógica.
    """
    try:
        return service.obtener(pedido_id)
    except PedidoNoEncontrado as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc


@router.post(
    "",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un pedido con sus detalles de forma atómica",
)
@router.post(
    "/",
    response_model=PedidoRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def crear_pedido(
    data: PedidoCreate,
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoRead:
    """Crea un pedido con su lista de detalles de forma transaccional.

    Responde 404 si algún producto no existe o está inactivo.
    Responde 422 si la lista de detalles es inválida (vacía, repetida o cantidad < 1).
    """
    try:
        return service.crear(data)
    except ProductoNoEncontrado as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except DetalleInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.put(
    "/{pedido_id}",
    response_model=PedidoRead,
    status_code=status.HTTP_200_OK,
    summary="Actualizar el estado de un pedido",
)
def actualizar_estado_pedido(
    data: PedidoUpdate,
    pedido_id: int = Path(..., gt=0, description="Identificador único del pedido"),
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoRead:
    """Actualiza el estado de un pedido activo.

    Responde 404 si el pedido no existe o fue dado de baja lógica.
    Responde 422 si el estado no pertenece a los permitidos.
    """
    try:
        return service.actualizar_estado(pedido_id, data)
    except PedidoNoEncontrado as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
    except DetalleInvalidoError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)
        ) from exc


@router.delete(
    "/{pedido_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar lógicamente un pedido",
)
def eliminar_pedido(
    pedido_id: int = Path(..., gt=0, description="Identificador único del pedido"),
    service: PedidoService = Depends(get_pedido_service),
) -> None:
    """Aplica borrado lógico completando deleted_at y responde 204 No Content.

    Responde 404 si el pedido no existe o ya fue dado de baja lógica.
    """
    try:
        service.eliminar(pedido_id)
        return None
    except PedidoNoEncontrado as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)
        ) from exc
