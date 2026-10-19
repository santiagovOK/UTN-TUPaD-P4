"""Módulo de ingredientes (catálogo oficial TP7)."""

from . import routers, services
from .routers import router
from .schemas import (
    IngredienteBase,
    IngredienteCreate,
    IngredientePaginatedResponse,
    IngredienteRead,
    IngredienteUpdate,
)
from .services import IngredienteConflictError, IngredienteUnidadNotFoundError

service = services

__all__ = [
    "IngredienteBase",
    "IngredienteCreate",
    "IngredienteRead",
    "IngredienteUpdate",
    "IngredientePaginatedResponse",
    "IngredienteConflictError",
    "IngredienteUnidadNotFoundError",
    "router",
    "routers",
    "services",
    "service",
]
