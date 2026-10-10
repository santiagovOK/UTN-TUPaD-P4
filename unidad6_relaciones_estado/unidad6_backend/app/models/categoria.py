"""
Modelo de datos para la entidad Categoria.

[Consigna TP6 - Parte A, inciso b]: Definir los models y schemas: Categoria (id, nombre, descripcion).
[Consigna TP6 - Rúbrica Backend]: Persistencia de Categoría en Base de Datos relacional mediante SQLModel.
Define la tabla 'categoria' en SQLModel y su relación muchos a muchos (N:N)
con Producto a través de la tabla intermedia ProductoCategoria.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from .producto import ProductoCategoria

if TYPE_CHECKING:
    from .producto import Producto


# [Consigna TP6 - Parte A, inciso b & Rúbrica CRUD Categorías Backend]:
# Entidad Categoria mapeada a tabla SQLModel con persistencia en DB relacional (PostgreSQL / SQLite).
class Categoria(SQLModel, table=True):
    """Entidad Categoria persistida en la base de datos relacional."""

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = Field(default=None)
    activo: bool = Field(default=True)

    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
    )
