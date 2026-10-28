"""Unit of Work para la gestión transaccional del catálogo de Ingredientes.

[TP8 - Ampliación Opcional: Patrón Repository y Unit of Work en Ingredientes]
[HU-05: Catálogo de Ingredientes - Control transaccional desacoplado]
[RN-10: Unicidad de nombre de ingrediente insensible a mayúsculas]
[RN-11: Restricción de baja con productos activos asociados]
"""

from sqlmodel import Session

from app.core.unit_of_work import UnitOfWorkBase
from .repository import IngredienteRepository, UnidadMedidaReadRepository


class IngredienteUnitOfWork(UnitOfWorkBase):
    """Unit of Work para la gestión transaccional del módulo de Ingredientes."""

    ingredientes: IngredienteRepository
    unidades: UnidadMedidaReadRepository

    def _init_repositories(self, session: Session) -> None:
        self.ingredientes = IngredienteRepository(session)
        self.unidades = UnidadMedidaReadRepository(session)
