from typing import Optional
from pydantic import BaseModel, Field


class ProveedorBase(BaseModel):
    codigo: str = Field(..., min_length=1, description="Codigo unico del proveedor")
    razon_social: str = Field(..., min_length=3, description="Razon social del proveedor")
    cuit: str = Field(..., min_length=11, max_length=15, description="Numero de CUIT")
    email: str = Field(default="", description="Correo electronico de contacto")
    telefono: str = Field(default="", description="Telefono de contacto")
    activo: bool = Field(default=True, description="Estado logico del proveedor")


class ProveedorCreate(ProveedorBase):
    pass


class ProveedorUpdate(BaseModel):
    codigo: Optional[str] = Field(default=None, min_length=1, description="Codigo unico del proveedor")
    razon_social: Optional[str] = Field(default=None, min_length=3, description="Razon social del proveedor")
    cuit: Optional[str] = Field(default=None, min_length=11, max_length=15, description="Numero de CUIT")
    email: Optional[str] = Field(default=None, description="Correo electronico de contacto")
    telefono: Optional[str] = Field(default=None, description="Telefono de contacto")
    activo: Optional[bool] = Field(default=None, description="Estado logico del proveedor")


class ProveedorRead(ProveedorBase):
    id: int = Field(..., description="Identificador unico autoincremental generado por el backend")
