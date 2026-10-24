"""Repositorio genérico base para abstracción de persistencia con SQLModel.

[TP8 - Ejercicio 1.c: Patrón Repository y Unit of Work]
[HU-07: Gestión de Pedidos - Abstracción de acceso a datos]
"""

from typing import Any, Generic, List, Optional, Type, TypeVar

from sqlmodel import Session, SQLModel, select

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """Repositorio base con operaciones CRUD desacopladas del control de transacciones.

    Ningún método invoca session.commit() para delegar la atomicidad al Unit of Work.
    """

    def __init__(self, session: Session, model: Type[ModelType]) -> None:
        self.session = session
        self.model = model

    def get_by_id(self, entity_id: Any) -> Optional[ModelType]:
        return self.session.get(self.model, entity_id)

    def get_all(self, offset: int = 0, limit: Optional[int] = None) -> List[ModelType]:
        statement = select(self.model).offset(offset)
        if limit is not None:
            statement = statement.limit(limit)
        return list(self.session.exec(statement).all())

    def create(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def add(self, entity: ModelType) -> ModelType:
        """Alias de create para compatibilidad con interfaces de colección."""
        return self.create(entity)

    def update(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def delete(self, entity: ModelType) -> None:
        self.session.delete(entity)
        self.session.flush()
