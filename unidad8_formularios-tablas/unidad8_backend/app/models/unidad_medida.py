"""Modelo de unidades de medida del catálogo (extensión heredada del TP7).

[Catálogo heredado del TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Extensión heredada del TP7: catálogo inmutable de unidades de medida]
"""

from typing import Optional
from sqlmodel import Field, SQLModel


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=50, unique=True, nullable=False, index=True)
    simbolo: str = Field(min_length=1, max_length=10, nullable=False)
    tipo: str = Field(min_length=1, max_length=30, nullable=False)
