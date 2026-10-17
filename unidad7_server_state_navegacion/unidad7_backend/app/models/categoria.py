"""Modelo de categorías del catálogo para TP7.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos]
"""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .producto import ProductoCategoria, _utc_now

if TYPE_CHECKING:
    from .producto import Producto


# [Consigna TP7 - Entidad CATEGORIA con auditoría y borrado lógico]
# [Diagrama UML - Clúster Catálogo de Productos]
class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(min_length=1, max_length=100, unique=True, nullable=False, index=True)
    descripcion: str = Field(default="", nullable=False)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=_utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
    )
