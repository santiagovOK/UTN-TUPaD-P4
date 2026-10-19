"""DTOs de productos y su asociación con categorías para TP7.

[Consigna TP7 - Contratos de entrada/salida, validación y paginación]
[Diagrama UML - PRODUCTO y entidad asociativa PRODUCTO_CATEGORIA]
"""

from typing import List, Optional, Union

from pydantic import field_validator
from sqlmodel import Field, SQLModel

from app.modules.categoria.schemas import CategoriaRead
from app.modules.ingrediente.schemas import IngredienteRead
from app.modules.producto.validators import validate_producto_nombres


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


class ProductoIngredienteInput(SQLModel):
    ingrediente_id: int = Field(gt=0, description="ID del ingrediente a asociar")
    cantidad: float = Field(default=1.0, gt=0, description="Cantidad requerida del ingrediente (> 0)")
    es_opcional: bool = Field(default=False, description="Indica si el ingrediente es opcional")


class ProductoCreate(ProductoBase):
    categoria_ids: List[int] = Field(
        min_length=1,
        description="Lista obligatoria de al menos un ID de categoría existente (RN-19)",
    )
    ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = Field(
        default=None,
        description="Ingredientes asociados como IDs o especificaciones detalladas (RN-20)",
    )


class ProductoRead(ProductoBase):
    id: int
    categorias: List[CategoriaRead] = Field(
        default_factory=list, description="Categorías activas asociadas al producto"
    )
    ingredientes: List[IngredienteRead] = Field(
        default_factory=list, description="Ingredientes activos asociados al producto"
    )


ProductoReadConCategorias = ProductoRead


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=150)
    descripcion: Optional[str] = Field(default=None)
    precio_base: Optional[float] = Field(default=None, ge=0)
    imagenes_url: Optional[List[str]] = Field(default=None)
    disponible: Optional[bool] = Field(default=None)
    categoria_ids: Optional[List[int]] = Field(
        default=None,
        min_length=1,
        description="Si se envía, reemplaza todas las categorías asociadas (RN-12)",
    )
    ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = Field(
        default=None,
        description="Si se envía, reemplaza todos los ingredientes asociados (RN-21)",
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        return validate_producto_nombres(value) if value is not None else None


class ProductoPaginatedResponse(SQLModel):
    total: int = Field(ge=0, description="Total de productos que coinciden con los filtros")
    items: List[ProductoRead] = Field(default_factory=list, description="Lista de productos de la página actual")

