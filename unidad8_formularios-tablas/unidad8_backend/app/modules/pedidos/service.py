"""Capa de servicio de dominio para el agregado Pedidos.

[TP8 - Ejercicio 1.c: Capa de Servicio y Orquestación Transaccional]
[HU-07: Gestión de Pedidos - Orquestación de Casos de Uso]
[RN-09, RN-12, RN-13, RN-14, RN-15, RN-16: Reglas de negocio e integridad transaccional]
"""

from typing import List, Optional

from app.modules.pedidos.models import DetallePedido, Pedido
from app.modules.pedidos.schemas import (
    EstadoPedido,
    PedidoCreate,
    PedidoRead,
    PedidoUpdate,
)
from app.modules.pedidos.unit_of_work import PedidoUnitOfWork

ESTADOS_PEDIDO_VALIDOS: tuple[EstadoPedido, ...] = (
    "PENDIENTE",
    "CONFIRMADO",
    "ENTREGADO",
    "CANCELADO",
)


class PedidoNoEncontrado(Exception):
    """Excepción lanzada cuando un pedido no existe o fue dado de baja lógica."""

    def __init__(self, pedido_id: int) -> None:
        self.pedido_id = pedido_id
        super().__init__(f"Pedido con ID {pedido_id} no encontrado.")


class ProductoNoEncontrado(Exception):
    """Excepción lanzada cuando un producto solicitado no existe o fue dado de baja lógica."""

    def __init__(self, producto_id: int) -> None:
        self.producto_id = producto_id
        super().__init__(f"Producto con ID {producto_id} no encontrado.")


class DetalleInvalidoError(ValueError):
    """Excepción para violaciones de reglas de negocio en los ítems o estado del pedido."""


class PedidoService:
    """Servicio de dominio para la gestión del agregado Pedido.

    Orquesta las operaciones transaccionales a través de PedidoUnitOfWork,
    manteniéndose desacoplado del protocolo de transporte HTTP/FastAPI.
    """

    def __init__(self, uow: Optional[PedidoUnitOfWork] = None) -> None:
        self.uow = uow if uow is not None else PedidoUnitOfWork()

    def listar(self, offset: int = 0, limit: Optional[int] = None) -> List[PedidoRead]:
        """Obtiene la lista de pedidos activos (sin borrado lógico)."""
        with self.uow as uow:
            pedidos = uow.pedidos.get_active(offset=offset, limit=limit)
            return [PedidoRead.model_validate(p) for p in pedidos]

    def obtener(self, pedido_id: int) -> PedidoRead:
        """Obtiene un pedido activo por su ID junto con sus detalles asociados.

        Lanza PedidoNoEncontrado si no existe o fue dado de baja lógica.
        """
        with self.uow as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado(pedido_id)
            return PedidoRead.model_validate(pedido)

    def crear(self, data: PedidoCreate) -> PedidoRead:
        """Crea un nuevo pedido de manera atómica con congelamiento de precios.

        Valida defensivamente la presencia de detalles, cantidades y unicidad de productos.
        Si algún producto no existe o está eliminado, revierte la transacción completa
        y lanza ProductoNoEncontrado.
        """
        if not data.detalles:
            raise DetalleInvalidoError("El pedido debe contener al menos un detalle.")

        vistos = set()
        for item in data.detalles:
            if item.cantidad < 1:
                raise DetalleInvalidoError(
                    "La cantidad de cada detalle debe ser mayor o igual a 1."
                )
            if item.producto_id in vistos:
                raise DetalleInvalidoError(
                    "No se puede repetir un producto en el pedido."
                )
            vistos.add(item.producto_id)

        with self.uow as uow:
            pedido = uow.pedidos.create(Pedido(estado="PENDIENTE", total=0.0))
            total = 0.0

            for item in data.detalles:
                producto = uow.productos.get_by_id(item.producto_id)
                if producto is None:
                    raise ProductoNoEncontrado(item.producto_id)

                uow.detalles.create(
                    DetallePedido(
                        pedido_id=pedido.id,
                        producto_id=producto.id,
                        cantidad=item.cantidad,
                        precio_unitario=producto.precio_base,
                    )
                )
                total += item.cantidad * producto.precio_base

            pedido.total = round(total, 2)
            uow.pedidos.update(pedido)
            return PedidoRead.model_validate(pedido)

    def actualizar_estado(self, pedido_id: int, data: PedidoUpdate) -> PedidoRead:
        """Actualiza el estado de un pedido activo.

        Lanza DetalleInvalidoError si el estado no es válido según ESTADOS_PEDIDO_VALIDOS,
        o PedidoNoEncontrado si el pedido no existe o está eliminado.
        """
        if data.estado not in ESTADOS_PEDIDO_VALIDOS:
            raise DetalleInvalidoError(f"Estado de pedido inválido: {data.estado}")

        with self.uow as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado(pedido_id)

            pedido.estado = data.estado
            uow.pedidos.update(pedido)
            return PedidoRead.model_validate(pedido)

    def eliminar(self, pedido_id: int) -> None:
        """Aplica baja lógica sobre un pedido activo.

        Lanza PedidoNoEncontrado si el pedido no existe o ya fue dado de baja lógica.
        """
        with self.uow as uow:
            pedido = uow.pedidos.get_by_id(pedido_id)
            if pedido is None:
                raise PedidoNoEncontrado(pedido_id)

            uow.pedidos.soft_delete(pedido)
