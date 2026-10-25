"""Módulo de Pedidos.

[TP8 - Ejercicio 1: Backend de Pedidos y Unit of Work]
[HU-07: Gestión de Pedidos]
"""

from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.repository import (
    DetallePedidoRepository,
    PedidoRepository,
    ProductoRepository,
)
from app.modules.pedidos.schemas import (
    DetallePedidoCreate,
    DetallePedidoRead,
    EstadoPedido,
    PedidoCreate,
    PedidoRead,
    PedidoUpdate,
)
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork
from app.modules.pedidos.service import (
    DetalleInvalidoError,
    PedidoNoEncontrado,
    PedidoService,
    ProductoNoEncontrado,
)
from app.modules.pedidos.router import get_pedido_service, router

__all__ = [
    "Pedido",
    "DetallePedido",
    "EstadoPedido",
    "DetallePedidoCreate",
    "PedidoCreate",
    "PedidoUpdate",
    "DetallePedidoRead",
    "PedidoRead",
    "PedidoRepository",
    "DetallePedidoRepository",
    "ProductoRepository",
    "PedidoUnitOfWork",
    "PedidoService",
    "PedidoNoEncontrado",
    "ProductoNoEncontrado",
    "DetalleInvalidoError",
    "router",
    "get_pedido_service",
]
