"""Modelo de ingredientes del catálogo para TP7.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos]
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .producto import ProductoIngrediente, _utc_now

if TYPE_CHECKING:
    from .producto import Producto
    from .unidad_medida import UnidadMedida


class Ingrediente(SQLModel, table=True):
    __tablename__ = "ingrediente"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=100, unique=True, nullable=False, index=True)
    descripcion: str = Field(default="", nullable=False)
    unidad_medida_id: int = Field(foreign_key="unidad_medida.id", nullable=False, index=True)
    activo: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=_utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)

    unidad_medida: Optional["UnidadMedida"] = Relationship()
    productos: List["Producto"] = Relationship(
        back_populates="ingredientes",
        link_model=ProductoIngrediente,
    )
