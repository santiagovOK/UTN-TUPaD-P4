from . import routers, services
from .routers import router
from .schemas import (
    CategoriaBase,
    CategoriaCreate,
    CategoriaPaginatedResponse,
    CategoriaRead,
    CategoriaUpdate,
)
from .services import CategoriaConflictError

# Alias de compatibilidad arquitectónica
service = services

__all__ = [
    "CategoriaBase",
    "CategoriaCreate",
    "CategoriaRead",
    "CategoriaUpdate",
    "CategoriaPaginatedResponse",
    "CategoriaConflictError",
    "router",
    "routers",
    "services",
    "service",
]
