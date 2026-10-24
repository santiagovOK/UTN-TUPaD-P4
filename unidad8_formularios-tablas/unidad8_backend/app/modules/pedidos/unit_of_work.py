"""Unit of Work concreto para el agregado Pedidos.

[TP8 - Ejercicio 1.c: Patrón Repository y Unit of Work]
[HU-07: Gestión de Pedidos - Orquestación transaccional]
[RN-15, RN-16: Aislamiento y consistencia transaccional]
"""

from sqlmodel import Session

from app.core.unit_of_work import UnitOfWorkBase
from app.modules.pedidos.repository import (
    DetallePedidoRepository,
    PedidoRepository,
    ProductoRepository,
)


class PedidoUnitOfWork(UnitOfWorkBase):
    """Unit of Work del agregado Pedidos.

    Administra una sesión exclusiva y expone los repositorios de Pedidos,
    Detalles y Productos vinculados a dicha sesión.
    """

    pedidos: PedidoRepository
    detalles: DetallePedidoRepository
    productos: ProductoRepository

    def _init_repositories(self, session: Session) -> None:
        self.pedidos = PedidoRepository(session)
        self.detalles = DetallePedidoRepository(session)
        self.productos = ProductoRepository(session)
