"""Módulo core para abstracciones de persistencia y transacciones.

[TP8 - Ejercicio 1.c: Patrón Repository y Unit of Work]
"""

from app.core.repository import BaseRepository
from app.core.unit_of_work import UnitOfWorkBase

__all__ = ["BaseRepository", "UnitOfWorkBase"]
