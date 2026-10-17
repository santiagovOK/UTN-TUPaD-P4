"""Modelos del catálogo de productos para TP7.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos]
"""

from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel


def _utc_now() -> datetime:
    """Retorna la fecha y hora UTC actual para los campos de auditoría."""
    return datetime.now(timezone.utc)


# [Consigna TP7 - Relación N:N enriquecida entre productos y categorías]
# [Diagrama UML - Entidad asociativa PRODUCTO_CATEGORIA]
class ProductoCategoria(SQLModel, table=True):
    __tablename__ = "producto_categoria"

    producto_id: Optional[int] = Field(
        default=None,
        foreign_key="producto.id",
        primary_key=True,
    )
    categoria_id: Optional[int] = Field(
        default=None,
        foreign_key="categoria.id",
        primary_key=True,
    )
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)


# [Consigna TP7 - Datos comunes de productos]
# [Diagrama UML - PRODUCTO excluye stock por SRP; pertenece al dominio INVENTARIO]
class ProductoBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=150, nullable=False, index=True)
    descripcion: Optional[str] = Field(default=None)
    precio_base: float = Field(ge=0, nullable=False)
    imagenes_url: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    disponible: bool = Field(default=True, nullable=False)


# [Consigna TP7 - Entidad PRODUCTO con auditoría y borrado lógico]
# [Diagrama UML - Clúster Catálogo de Productos]
class Producto(ProductoBase, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=_utc_now, nullable=False)
    updated_at: datetime = Field(default_factory=_utc_now, nullable=False)
    deleted_at: Optional[datetime] = Field(default=None, nullable=True)
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )
