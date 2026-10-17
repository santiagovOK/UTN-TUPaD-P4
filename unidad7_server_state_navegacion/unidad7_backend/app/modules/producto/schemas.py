"""DTOs de productos y su asociación con categorías para TP7.

[Consigna TP7 - Contratos de entrada/salida, validación y paginación]
[Diagrama UML - PRODUCTO y entidad asociativa PRODUCTO_CATEGORIA]
"""

from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.modules.categoria.schemas import CategoriaRead
from app.modules.producto.validators import validate_producto_nombres


# [Consigna TP7 - Datos comunes validados de producto]
# [Diagrama UML - PRODUCTO excluye stock por SRP; imagenes_url es una lista]
class ProductoBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=150, description="Nombre del producto")
    descripcion: Optional[str] = Field(default=None, description="Descripción detallada opcional")
    precio_base: float = Field(ge=0, description="Precio base unitario (>= 0)")
    imagenes_url: List[str] = Field(default_factory=list, description="Lista de URLs de imágenes del producto")
    disponible: bool = Field(default=True, description="Indicador de disponibilidad en el catálogo")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        return validate_producto_nombres(value)


# [Consigna TP7 - DTO para creación de productos]
# [Diagrama UML - Atributos de PRODUCTO]
class ProductoCreate(ProductoBase):
    pass


# [Consigna TP7 - DTO de respuesta de producto con categorías]
# [Diagrama UML - PRODUCTO y relación N:N con CATEGORIA]
class ProductoRead(ProductoBase):
    id: int
    categorias: List[CategoriaRead] = Field(default_factory=list, description="Categorías asociadas al producto")


# Alias explícito para la forma de lectura con categorías; no duplica el DTO.
ProductoReadConCategorias = ProductoRead


# [Consigna TP7 - DTO parcial para actualización de productos]
# [Diagrama UML - Atributos modificables de PRODUCTO, sin campos de auditoría]
class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None)
    precio_base: Optional[float] = Field(default=None, ge=0)
    imagenes_url: Optional[List[str]] = Field(default=None)
    disponible: Optional[bool] = Field(default=None)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        return validate_producto_nombres(value) if value is not None else None


# [Consigna TP7 - Respuesta paginada {total, items}]
# [Diagrama UML - Colección de productos]
class ProductoPaginatedResponse(SQLModel):
    total: int = Field(ge=0, description="Total de productos que coinciden con los filtros")
    items: List[ProductoRead] = Field(default_factory=list, description="Lista de productos de la página actual")


# [Consigna TP7 - DTO de asignación de relación N:N]
# [Diagrama UML - PRODUCTO_CATEGORIA con clave compuesta y es_principal]
class ProductoCategoriaAssign(SQLModel):
    producto_id: int = Field(gt=0, description="ID del producto a vincular")
    categoria_id: int = Field(gt=0, description="ID de la categoría a vincular")
    es_principal: bool = Field(default=False, description="Indica si es la categoría principal del producto")


# [Consigna TP7 - DTO de lectura de relación N:N]
# [Diagrama UML - PRODUCTO_CATEGORIA]
class ProductoCategoriaRead(SQLModel):
    producto_id: int
    categoria_id: int
    es_principal: bool
