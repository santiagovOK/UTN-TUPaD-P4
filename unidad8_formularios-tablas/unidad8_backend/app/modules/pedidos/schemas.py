"""DTOs y esquemas de validación del agregado Pedidos.

[TP8 - Ejercicio 1.b: Definición de models y schemas de Pedido y DetallePedido]
[HU-07: Gestión de Pedidos - Contratos de entrada/salida y reglas de validación]
[RN-12, RN-14: Validación de no repetidos, cantidad >= 1 y estados permitidos]
"""

from datetime import datetime
from typing import Annotated, List, Literal, Optional

from pydantic import Field as PydanticField, field_validator
from sqlmodel import Field, SQLModel

# [TP8 - Ejercicio 1.b: Estados permitidos para Pedido en memoria/validación (texto en persistencia)]
EstadoPedido = Literal["PENDIENTE", "CONFIRMADO", "ENTREGADO", "CANCELADO"]


# [TP8 - Ejercicio 1.b: DTO de entrada para ítem de pedido (producto_id y cantidad entera >= 1)]
class DetallePedidoCreate(SQLModel):
    producto_id: int
    cantidad: Annotated[int, PydanticField(strict=True, ge=1)]


# [TP8 - Ejercicio 1.b / 1.c: DTO de alta con al menos un detalle y rechazo de productos duplicados]
# [RN-12: Validación estricta que previene errores 500 por colisión de clave primaria compuesta]
class PedidoCreate(SQLModel):
    detalles: List[DetallePedidoCreate] = Field(min_length=1)

    @field_validator("detalles")
    @classmethod
    def validar_productos_unicos(
        cls, value: List[DetallePedidoCreate]
    ) -> List[DetallePedidoCreate]:
        vistos = set()
        for item in value:
            if item.producto_id in vistos:
                raise ValueError("No se puede repetir un producto en el pedido.")
            vistos.add(item.producto_id)
        return value


# [TP8 - Ejercicio 1.c: DTO de actualización de estado para PUT /pedidos/{id}]
# [RN-14: Validación de transición de estado permitido (422 ante valores inválidos)]
class PedidoUpdate(SQLModel):
    estado: EstadoPedido


# [TP8 - Ejercicio 1.b: DTO de salida para detalle con precio congelado]
class DetallePedidoRead(SQLModel):
    pedido_id: int
    producto_id: int
    cantidad: int = Field(ge=1)
    precio_unitario: float


# [TP8 - Ejercicio 1.b: DTO de respuesta pública de Pedido (excluye deleted_at)]
class PedidoRead(SQLModel):
    id: int
    fecha: datetime
    estado: EstadoPedido
    total: float
    detalles: List[DetallePedidoRead] = Field(default_factory=list)
