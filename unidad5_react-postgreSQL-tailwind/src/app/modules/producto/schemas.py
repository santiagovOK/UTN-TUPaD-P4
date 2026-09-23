from typing import Optional
from sqlmodel import SQLModel, Field
from app.models.producto import ProductoBase


# ============================
# DTO de Entrada - Creación
# ============================
class ProductoCreate(ProductoBase):
    """Schema de entrada para creación de producto (sin ID).

    Hereda todos los campos y restricciones declarativas de ProductoBase:
    nombre obligatorio (min_length=1), precio >= 0, etc.
    """
    pass


# ============================
# DTO de Salida - Response
# ============================
class ProductoResponse(ProductoBase):
    """Schema de salida garantizando que el ID esté presente.

    Contrato de respuesta para todos los endpoints de lectura.
    Refleja fielmente la entidad SQLModel Producto del backend.
    """
    id: int


# ============================
# DTO de Actualización (ahora con SQLModel - Unidad 5)
# ============================
class ProductoUpdate(SQLModel):
    """Schema para actualización con campos opcionales.

    Permite actualizar parcial o totalmente los atributos del producto.
    Los validadores de negocio (nombre no vacío, precio >= 0) se aplican
    solo cuando se proporcionan valores explícitos.
    """
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio: Optional[float] = Field(default=None, ge=0)
    categoria: Optional[str] = None
    stock: Optional[int] = Field(default=None, ge=0)
    stock_minimo: Optional[int] = Field(default=None, ge=0)
    activo: Optional[bool] = None


# ============================
# Respuesta de Consulta Stock
# ============================
class ProductoStockResponse(SQLModel):
    """Schema para respuesta de consulta de stock.

    Entrega el estado actual del inventario junto con la bandera de alerta.
    """
    stock: int
    bajo_stock_minimo: bool
    activo: bool


# ============================
# Compatibilidad con routers/services existentes (Fase 2)
# ============================
ProductoRead = ProductoResponse
