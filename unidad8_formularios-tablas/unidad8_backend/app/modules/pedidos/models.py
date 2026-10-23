"""Modelos relacionales del agregado Pedidos.

[TP8 - Ejercicio 1.b: Definición de models y schemas de Pedido y DetallePedido]
[HU-07: Gestión de Pedidos - Modelos del agregado y persistencia relacional]
[RN-12, RN-14: Integridad de cabecera y detalle de pedidos]
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


# [TP8 - Ejercicio 1.b: Entidad PEDIDO con auditoría, estado textual y borrado lógico]
# [Diagrama UML - Simplificación de Ventas & Transacciones para Pedido]
class Pedido(SQLModel, table=True):
    __tablename__ = "pedido"

    id: Optional[int] = Field(default=None, primary_key=True)
    fecha: datetime = Field(default_factory=_utc_now, nullable=False)
    estado: str = Field(default="PENDIENTE", nullable=False)
    total: float = Field(default=0.0, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    detalles: List["DetallePedido"] = Relationship(back_populates="pedido")


# [TP8 - Ejercicio 1.b: Entidad asociativa DETALLE_PEDIDO con clave primaria compuesta]
# [Diagrama UML - Clave compuesta (pedido_id, producto_id) y congelamiento de precio_unitario]
class DetallePedido(SQLModel, table=True):
    __tablename__ = "detalle_pedido"

    pedido_id: int = Field(foreign_key="pedido.id", primary_key=True)
    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    cantidad: int = Field(ge=1, nullable=False)
    precio_unitario: float = Field(nullable=False)

    pedido: Optional[Pedido] = Relationship(back_populates="detalles")
