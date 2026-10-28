"""Módulo de ingredientes (catálogo con arquitectura Repository y Unit of Work).

[TP8 - Ampliación Opcional: Patrón Repository y Unit of Work en Ingredientes]
[HU-05: Catálogo de Ingredientes - Abstracción transaccional Models-Schemas-Repository-UoW-Service-Router]
[RN-10: Unicidad de nombre de ingrediente insensible a mayúsculas]
[RN-11: Restricción de baja con productos activos asociados]
"""

from . import repository, routers, services, unit_of_work
from .repository import IngredienteRepository, UnidadMedidaReadRepository
from .routers import get_ingrediente_service, router
from .schemas import (
    IngredienteBase,
    IngredienteCreate,
    IngredientePaginatedResponse,
    IngredienteRead,
    IngredienteUpdate,
)
from .services import (
    IngredienteConflictError,
    IngredienteService,
    IngredienteUnidadNotFoundError,
)
from .unit_of_work import IngredienteUnitOfWork

service = services

__all__ = [
    "IngredienteBase",
    "IngredienteCreate",
    "IngredienteRead",
    "IngredienteUpdate",
    "IngredientePaginatedResponse",
    "IngredienteConflictError",
    "IngredienteUnidadNotFoundError",
    "IngredienteRepository",
    "UnidadMedidaReadRepository",
    "IngredienteUnitOfWork",
    "IngredienteService",
    "get_ingrediente_service",
    "router",
    "routers",
    "services",
    "service",
    "repository",
    "unit_of_work",
]
