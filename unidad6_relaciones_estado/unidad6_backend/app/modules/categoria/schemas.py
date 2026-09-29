from pydantic import BaseModel, Field
from typing import Optional


class CategoriaBase(BaseModel):
    nombre: str = Field(..., min_length=1, examples=["Electrónica"])
    descripcion: Optional[str] = Field(None, examples=["Dispositivos y accesorios electrónicos"])
    activo: bool = True


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1)
    descripcion: Optional[str] = Field(None)
    activo: Optional[bool] = None


class CategoriaRead(CategoriaBase):
    id: int
