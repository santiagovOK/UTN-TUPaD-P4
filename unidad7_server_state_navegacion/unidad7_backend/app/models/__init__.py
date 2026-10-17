"""Modelos relacionales del catálogo TP7."""

from .categoria import Categoria
from .producto import Producto, ProductoBase, ProductoCategoria

__all__ = ["Categoria", "Producto", "ProductoBase", "ProductoCategoria"]
