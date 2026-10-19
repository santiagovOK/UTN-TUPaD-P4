"""DTOs de unidades de medida según la consigna TP7 y el UML del catálogo.

[Consigna TP7 - Catálogo base oficial de unidades de medida]
[Diagrama UML - Clúster Catálogo de Productos - UNIDAD_MEDIDA]
"""

from typing import List

from sqlmodel import Field, SQLModel


class UnidadMedidaRead(SQLModel):
    """DTO de salida para unidad de medida."""

    id: int
    nombre: str
    simbolo: str
    tipo: str


class UnidadMedidaListResponse(SQLModel):
    """Respuesta para el listado completo de unidades de medida."""

    total: int = Field(ge=0, description="Total de unidades de medida en el catálogo")
    items: List[UnidadMedidaRead] = Field(
        default_factory=list, description="Listado de unidades de medida"
    )
