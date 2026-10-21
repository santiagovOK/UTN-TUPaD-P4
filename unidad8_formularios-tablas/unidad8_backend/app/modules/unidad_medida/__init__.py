"""Módulo de unidades de medida (extensión de catálogo heredada del TP7)."""

from . import routers, services
from .routers import router
from .schemas import UnidadMedidaListResponse, UnidadMedidaRead

service = services

__all__ = [
    "UnidadMedidaRead",
    "UnidadMedidaListResponse",
    "router",
    "routers",
    "services",
    "service",
]
