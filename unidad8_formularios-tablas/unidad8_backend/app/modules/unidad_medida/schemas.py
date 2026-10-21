"""DTOs de unidades de medida (extensión de catálogo heredada del TP7).

[Catálogo heredado del TP7 - Catálogo base de unidades de medida]
[Extensión heredada del TP7: catálogo inmutable de unidades de medida]
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
