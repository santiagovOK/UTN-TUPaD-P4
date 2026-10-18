from . import routers, services
from .routers import router
from .schemas import (
    ProductoBase,
    ProductoCategoriaAssign,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoPaginatedResponse,
    ProductoRead,
    ProductoReadConCategorias,
    ProductoUpdate,
)
from .services import ProductoConflictError

# Alias de compatibilidad arquitectónica
service = services

__all__ = [
    "ProductoBase",
    "ProductoCreate",
    "ProductoRead",
    "ProductoReadConCategorias",
    "ProductoUpdate",
    "ProductoPaginatedResponse",
    "ProductoCategoriaAssign",
    "ProductoCategoriaRead",
    "ProductoConflictError",
    "router",
    "routers",
    "services",
    "service",
]
