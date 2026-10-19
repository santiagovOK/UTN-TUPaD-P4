"""DTOs de ingredientes según la consigna TP7 y el UML del catálogo.

[Consigna TP7 - Contratos de entrada/salida, validación y paginación de ingredientes]
[Diagrama UML - Clúster Catálogo de Productos - INGREDIENTE]
"""

from typing import List, Optional

from pydantic import field_validator
from sqlmodel import Field, SQLModel


def _validate_ingrediente_nombre(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El nombre del ingrediente no puede estar vacío o contener solo espacios.")
    return value


# [Consigna TP7 - Datos comunes validados de ingrediente]
class IngredienteBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=100, description="Nombre único del ingrediente")
    descripcion: Optional[str] = Field(default="", description="Descripción opcional del ingrediente")
    unidad_medida_id: int = Field(gt=0, description="ID de la unidad de medida asociada")
    activo: bool = Field(default=True, description="Indica si el ingrediente está activo")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        return _validate_ingrediente_nombre(value)

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalizar_descripcion(cls, value):
        return "" if value is None else value


# [Consigna TP7 - DTO para creación de ingredientes]
class IngredienteCreate(IngredienteBase):
    pass


# [Consigna TP7 - DTO de lectura de ingrediente]
class IngredienteRead(IngredienteBase):
    id: int


# [Consigna TP7 - DTO de actualización parcial/total de ingrediente]
class IngredienteUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None)
    unidad_medida_id: Optional[int] = Field(default=None, gt=0)
    activo: Optional[bool] = Field(default=None)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        return _validate_ingrediente_nombre(value) if value is not None else None

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalizar_descripcion(cls, value):
        return "" if value is None else value


# [Consigna TP7 - Respuesta paginada {total, items}]
class IngredientePaginatedResponse(SQLModel):
    total: int = Field(ge=0, description="Total de ingredientes que coinciden con la consulta")
    items: List[IngredienteRead] = Field(
        default_factory=list, description="Lista de ingredientes de la página actual"
    )
