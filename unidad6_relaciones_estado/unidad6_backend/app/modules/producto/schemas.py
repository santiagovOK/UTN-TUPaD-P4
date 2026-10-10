"""
Schemas DTO Pydantic / SQLModel para la entidad Producto y relación con Categorías.

[Consigna TP6 - Parte A, inciso b]: Definir los models y schemas:
  - Producto (id: int, nombre: str, descripcion: str, precio_base: str, imagen_url: list[], disponible: bool)
[Consigna TP6 - Rúbrica Backend]: Esquemas Pydantic para validación y serialización de datos.
"""

from typing import List, Optional
from sqlmodel import SQLModel, Field
from pydantic import field_validator
from app.models.producto import ProductoBase
from app.modules.categoria.schemas import CategoriaRead
from .validators import validate_producto_nombres


# =============================================================================
# DTO de Entrada - Creación
# =============================================================================
# [Consigna TP6 - Parte A, inciso b]: Schema de creación validando nombre, descripcion, precio_base, imagen_url, disponible.
class ProductoCreate(ProductoBase):
    """Schema de entrada para creación de producto (sin ID).

    Hereda los campos y restricciones declarativas de ProductoBase (TP6):
    nombre, descripcion, precio_base, imagen_url, disponible.
    """

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        """Aplica validate_producto_nombres desde el módulo dedicado."""
        return validate_producto_nombres(value)


# =============================================================================
# DTOs de Salida - Lectura y Consulta de Relación N:N
# =============================================================================
# [Consigna TP6 - Parte A, inciso b & Rúbrica Backend]: Schema de lectura garantizando la presencia de id.
class ProductoRead(ProductoBase):
    """Schema de salida garantizando que el ID esté presente."""

    id: int


# [Consigna TP6 - Parte A, inciso d & Conclusiones Esperadas]:
# Schema de salida con lista anidada de categorías asociadas (relación muchos a muchos).
class ProductoReadConCategorias(ProductoRead):
    """Schema de salida de Producto que incluye la lista anidada de categorías asociadas (relación N:N)."""

    categorias: List[CategoriaRead] = []


# =============================================================================
# DTO de Actualización
# =============================================================================
# [Consigna TP6 - Rúbrica Backend]: Schema para actualización parcial o total de campos del producto.
class ProductoUpdate(SQLModel):
    """Schema para actualización parcial o total de atributos de Producto."""
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[str] = Field(default=None, min_length=1)
    imagen_url: Optional[List[str]] = None
    disponible: Optional[bool] = None

    @field_validator("nombre")
    @classmethod
    def validar_nombre_opcional(cls, value: Optional[str]) -> Optional[str]:
        """Aplica validación de nombre cuando se provee explícitamente."""
        if value is not None:
            return validate_producto_nombres(value)
        return value
