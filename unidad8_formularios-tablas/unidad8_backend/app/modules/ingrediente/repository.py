"""Repositorio concreto para la persistencia de Ingredientes y lectura de Unidades de Medida.

[TP8 - Ampliación Opcional: Patrón Repository y Unit of Work en Ingredientes]
[HU-05: Catálogo de Ingredientes - Abstracción de acceso a datos]
[RN-10: Unicidad de nombre de ingrediente insensible a mayúsculas]
[RN-11: Restricción de baja con productos activos asociados]
"""

from typing import List, Optional, Tuple

from sqlmodel import Session, func, select

from app.core.repository import BaseRepository
from app.models.ingrediente import Ingrediente
from app.models.producto import Producto, ProductoIngrediente, _utc_now
from app.models.unidad_medida import UnidadMedida
from app.seed import UNIDADES_MEDIDA_SEED


class IngredienteRepository(BaseRepository[Ingrediente]):
    """Repositorio concreto para la entidad Ingrediente sin confirmación de transacción."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, Ingrediente)

    def get_active_by_id(self, ingrediente_id: int) -> Optional[Ingrediente]:
        """Obtiene un ingrediente activo por su ID."""
        ingrediente = self.session.get(Ingrediente, ingrediente_id)
        if not ingrediente or ingrediente.deleted_at is not None:
            return None
        return ingrediente

    def get_by_nombre_ci(
        self, nombre: str, exclude_id: Optional[int] = None
    ) -> Optional[Ingrediente]:
        """Busca un ingrediente por nombre sin distinción de mayúsculas/minúsculas (RN-10)."""
        statement = select(Ingrediente).where(
            func.lower(Ingrediente.nombre) == nombre.lower()
        )
        if exclude_id is not None:
            statement = statement.where(Ingrediente.id != exclude_id)
        return self.session.exec(statement).first()

    def list_paginated(
        self,
        offset: int = 0,
        limit: int = 10,
        nombre: Optional[str] = None,
        search: Optional[str] = None,
        incluir_inactivos: bool = False,
    ) -> Tuple[int, List[Ingrediente]]:
        """Retorna el total de coincidencias y los registros paginados."""
        query = select(Ingrediente)
        if not incluir_inactivos:
            query = query.where(Ingrediente.deleted_at.is_(None))

        filtro_nombre = nombre if nombre is not None else search
        if filtro_nombre and filtro_nombre.strip():
            query = query.where(
                Ingrediente.nombre.ilike(f"%{filtro_nombre.strip()}%")
            )

        count_query = select(func.count()).select_from(query.subquery())
        total: int = self.session.exec(count_query).one()
        items = self.session.exec(
            query.order_by(Ingrediente.id).offset(offset).limit(limit)
        ).all()
        return total, list(items)

    def count_active_productos(self, ingrediente_id: int) -> int:
        """Cuenta la cantidad de productos activos asociados al ingrediente (RN-11)."""
        statement = (
            select(func.count())
            .select_from(ProductoIngrediente)
            .join(Producto, Producto.id == ProductoIngrediente.producto_id)
            .where(
                ProductoIngrediente.ingrediente_id == ingrediente_id,
                Producto.deleted_at.is_(None),
            )
        )
        return int(self.session.exec(statement).one())

    def soft_delete(self, ingrediente: Ingrediente) -> Ingrediente:
        """Aplica baja lógica actualizando deleted_at, activo y updated_at sin commit."""
        now = _utc_now()
        ingrediente.deleted_at = now
        ingrediente.updated_at = now
        ingrediente.activo = False
        self.session.add(ingrediente)
        self.session.flush()
        return ingrediente


class UnidadMedidaReadRepository(BaseRepository[UnidadMedida]):
    """Repositorio de lectura para verificar unidades de medida dentro de la misma sesión UoW."""

    def __init__(self, session: Session) -> None:
        super().__init__(session, UnidadMedida)

    def ensure_seeded(self) -> None:
        """Puebla de forma transaccional las 7 unidades estándar si la tabla está vacía."""
        total = self.session.exec(
            select(func.count()).select_from(UnidadMedida)
        ).one()
        if total == 0:
            for item in UNIDADES_MEDIDA_SEED:
                self.session.add(
                    UnidadMedida(
                        id=int(item["id"]),
                        nombre=str(item["nombre"]),
                        simbolo=str(item["simbolo"]),
                        tipo=str(item["tipo"]),
                    )
                )
            self.session.flush()
