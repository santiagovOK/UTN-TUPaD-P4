"""Repositorios concretos del agregado Pedidos y lectura de catálogo.

[TP8 - Ejercicio 1.c: Patrón Repository y Unit of Work]
[HU-07: Gestión de Pedidos - Persistencia del agregado y lectura de productos]
[RN-09, RN-13, RN-15: Filtrado de borrado lógico y aislamiento transaccional]
"""

from typing import List, Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.core.repository import BaseRepository
from app.models.producto import Producto
from app.modules.pedidos.models import DetallePedido, Pedido, _utc_now


class PedidoRepository(BaseRepository[Pedido]):
    """Repositorio para la entidad raíz Pedido."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Pedido)

    def get_by_id(
        self, pedido_id: int, incluir_eliminados: bool = False
    ) -> Optional[Pedido]:
        """Obtiene un pedido por ID con sus detalles cargados.

        Por omisión excluye pedidos con borrado lógico (RN-13).
        """
        statement = (
            select(Pedido)
            .options(selectinload(Pedido.detalles))
            .where(Pedido.id == pedido_id)
        )
        if not incluir_eliminados:
            statement = statement.where(Pedido.deleted_at.is_(None))
        return self.session.exec(statement).first()

    def get_all(
        self,
        offset: int = 0,
        limit: Optional[int] = None,
        incluir_eliminados: bool = False,
    ) -> List[Pedido]:
        """Retorna todos los pedidos con sus detalles, ordenados por ID."""
        statement = select(Pedido).options(selectinload(Pedido.detalles))
        if not incluir_eliminados:
            statement = statement.where(Pedido.deleted_at.is_(None))
        statement = statement.order_by(Pedido.id).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())

    def get_active(
        self, offset: int = 0, limit: Optional[int] = None
    ) -> List[Pedido]:
        """Alias explícito para listar pedidos activos (sin borrado lógico)."""
        return self.get_all(offset=offset, limit=limit, incluir_eliminados=False)

    def soft_delete(self, pedido: Pedido) -> Pedido:
        """Aplica borrado lógico asignando deleted_at y emitiendo flush sin commit."""
        pedido.deleted_at = _utc_now()
        self.session.add(pedido)
        self.session.flush()
        self.session.refresh(pedido)
        return pedido


class DetallePedidoRepository(BaseRepository[DetallePedido]):
    """Repositorio para la entidad asociativa DetallePedido."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, DetallePedido)

    def create(self, entity: DetallePedido) -> DetallePedido:
        """Inserta un detalle, realiza flush/refresh y expira la relación del pedido padre.

        La expiración selectiva de 'detalles' en el pedido padre permite que
        PedidoRead.model_validate(pedido) refleje los ítems agregados dentro de
        la misma transacción sin alterar atributos pendientes (ej. total).
        """
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        pedido = self.session.get(Pedido, entity.pedido_id)
        if pedido is not None:
            self.session.expire(pedido, ["detalles"])
        return entity

    def get_by_ids(
        self, pedido_id: int, producto_id: int
    ) -> Optional[DetallePedido]:
        """Obtiene un detalle por su clave primaria compuesta (pedido_id, producto_id)."""
        return self.session.get(DetallePedido, (pedido_id, producto_id))

    def get_by_pedido_id(self, pedido_id: int) -> List[DetallePedido]:
        """Retorna los detalles de un pedido ordenados por producto_id."""
        statement = (
            select(DetallePedido)
            .where(DetallePedido.pedido_id == pedido_id)
            .order_by(DetallePedido.producto_id)
        )
        return list(self.session.exec(statement).all())


class ProductoRepository(BaseRepository[Producto]):
    """Repositorio de lectura para consultar productos dentro de la sesión transaccional."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Producto)

    def get_by_id(
        self, producto_id: int, incluir_eliminados: bool = False
    ) -> Optional[Producto]:
        """Consulta un producto por ID dentro de la sesión del Unit of Work.

        Por omisión retorna None si el producto fue dado de baja lógica (RN-09).
        """
        producto = self.session.get(Producto, producto_id)
        if producto is None:
            return None
        if not incluir_eliminados and producto.deleted_at is not None:
            return None
        return producto
