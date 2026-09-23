"""
Modelo de datos para la entidad Producto.

Este archivo define la jerarquía SQLModel que se persiste en PostgreSQL.
Las tablas se crean mediante SQLModel.metadata.create_all(engine) en database.py.

Campos del modelo: id, nombre, descripcion, precio, categoria, stock, stock_minimo, activo
"""

from sqlmodel import SQLModel, Field
from typing import Optional


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
