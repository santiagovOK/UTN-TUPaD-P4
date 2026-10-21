"""DTOs de categorías del catálogo.

[Catálogo heredado del TP7 - Contratos de entrada/salida, validación y paginación]
[Diagrama UML - Entidad CATEGORIA, nombre y descripción]
"""

from typing import List, Optional

from sqlmodel import Field, SQLModel
from pydantic import field_validator


def _validate_categoria_nombre(value: str) -> str:
    value = value.strip()
    if not value:
        raise ValueError("El nombre de la categoría no puede estar vacío o contener solo espacios.")
    return value


# [Catálogo heredado del TP7 - Datos comunes validados de categoría]
# [Diagrama UML - CATEGORIA.nombre VARCHAR(100) y descripcion]
class CategoriaBase(SQLModel):
    nombre: str = Field(min_length=1, max_length=100, description="Nombre único de la categoría")
    descripcion: Optional[str] = Field(default="", description="Descripción opcional de la categoría")

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        return _validate_categoria_nombre(value)

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalizar_descripcion(cls, value):
        return "" if value is None else value


# [Catálogo heredado del TP7 - DTO para creación de categorías]
# [Diagrama UML - Atributos de CATEGORIA]
class CategoriaCreate(CategoriaBase):
    pass


# [Catálogo heredado del TP7 - DTO de respuesta de categoría sin campos internos]
# [Diagrama UML - Identificador de CATEGORIA]
class CategoriaRead(CategoriaBase):
    id: int


# [Catálogo heredado del TP7 - DTO parcial para actualización]
# [Diagrama UML - Atributos modificables de CATEGORIA]
class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(default=None)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value: Optional[str]) -> Optional[str]:
        return _validate_categoria_nombre(value) if value is not None else None

    @field_validator("descripcion", mode="before")
    @classmethod
    def normalizar_descripcion(cls, value):
        return "" if value is None else value


# [Catálogo heredado del TP7 - Respuesta paginada {total, items}]
# [Diagrama UML - Colección de categorías]
class CategoriaPaginatedResponse(SQLModel):
    total: int = Field(ge=0, description="Total de registros que coinciden con la consulta")
    items: List[CategoriaRead] = Field(default_factory=list, description="Lista de categorías de la página actual")
