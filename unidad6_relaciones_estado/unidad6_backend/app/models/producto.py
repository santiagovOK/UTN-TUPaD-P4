"""
Modelo de datos para la entidad Producto y la relación Producto_Categoria.

[Consigna TP6 - Parte A, inciso b]: Definir los models y schemas:
  - Producto (id: int, nombre: str, descripcion: str, precio_base: str, imagen_url: list[], disponible: bool)
  - Producto_Categoria (producto_id: int, categoria_id: int)
[Consigna TP6 - Rúbrica Backend]: Persistencia de Producto y relación N:N mediante SQLModel y tablas relacionales.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

if TYPE_CHECKING:
    from .categoria import Categoria


# [Consigna TP6 - Parte A, inciso b]: Tabla intermedia Producto_Categoria (producto_id: int, categoria_id: int)
# para materializar la relación muchos a muchos (N:N) entre Producto y Categoria con integridad referencial.
class ProductoCategoria(SQLModel, table=True):
    """Tabla intermedia para la relación muchos a muchos entre Producto y Categoria."""

    producto_id: Optional[int] = Field(
        default=None, foreign_key="producto.id", primary_key=True
    )
    categoria_id: Optional[int] = Field(
        default=None, foreign_key="categoria.id", primary_key=True
    )


# [Consigna TP6 - Parte A, inciso b]: Modelado base de Producto con campos exactos:
# nombre, descripcion, precio_base (str), imagen_url (list JSON) y disponible (bool).
class ProductoBase(SQLModel):
    """Campos comunes para la entidad Producto.

    Base hereditaria para la entidad persistente y los schemas de DTO.
    """
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = Field(default=None)
    precio_base: str = Field(..., min_length=1)
    imagen_url: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    disponible: bool = Field(default=True)


# [Consigna TP6 - Parte A, inciso b & Rúbrica Backend]:
# Entidad persistente Producto con clave primaria autoincremental y relación N:N hacia Categoria.
class Producto(ProductoBase, table=True):
    """Entidad principal persistida en la base de datos relacional."""
    id: Optional[int] = Field(default=None, primary_key=True)
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )
