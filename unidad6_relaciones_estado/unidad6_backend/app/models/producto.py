"""
Modelo de datos para la entidad Producto.

Este archivo define la jerarquía SQLModel que se persiste en PostgreSQL.
Las tablas se crean mediante SQLModel.metadata.create_all(engine) en database.py.

Campos del modelo: id, nombre, descripcion, precio, categoria, stock, stock_minimo, activo
"""

from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

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


class ProductoBase(SQLModel):
    """Campos comunes para la entidad Producto.

    Base hereditaria para los schemas de DTO (entrada/salida).
    No crea tabla por sí sola.
    """

    nombre: str = Field(..., min_length=1)
    descripcion: Optional[str] = None
    precio: float = Field(..., ge=0)
    categoria: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    stock_minimo: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = True


class Producto(ProductoBase, table=True):
    """Entidad principal que se persiste en PostgreSQL.

    Agrega el campo ID como primary key. La tabla 'producto' se crea
    al invocar SQLModel.metadata.create_all(engine) en database.py.
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )
