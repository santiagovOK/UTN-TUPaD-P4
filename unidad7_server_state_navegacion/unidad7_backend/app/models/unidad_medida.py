"""Modelo de unidades de medida del catálogo para TP7.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos]
"""

from typing import Optional
from sqlmodel import Field, SQLModel


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidad_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=50, unique=True, nullable=False, index=True)
    simbolo: str = Field(min_length=1, max_length=10, nullable=False)
    tipo: str = Field(min_length=1, max_length=30, nullable=False)
