"""Unit of Work base para control transaccional y ciclo de vida de sesiones.

[TP8 - Ejercicio 1.c: Patrón Repository y Unit of Work]
[HU-07: Gestión de Pedidos - Atomicidad transaccional]
[RN-15, RN-16: Aislamiento y consistencia transaccional]
"""

from typing import Callable, Optional, Self

from sqlmodel import Session


def _default_session_factory() -> Session:
    """Crea una sesión SQLModel utilizando dinámicamente el motor configurado en app.database."""
    from app import database

    return Session(database.engine)


class UnitOfWorkBase:
    """Administrador de contexto transaccional para operaciones con repositorios.

    Garantiza que una unidad de trabajo posea una única sesión, ejecute rollback
    ante excepciones no controladas y cierre la sesión en finally.
    """

    def __init__(
        self,
        session_factory: Optional[Callable[[], Session]] = None,
    ) -> None:
        self.session_factory: Callable[[], Session] = (
            session_factory if session_factory is not None else _default_session_factory
        )
        self.session: Optional[Session] = None

    def _init_repositories(self, session: Session) -> None:
        """Inicializa los repositorios concretos vinculándolos a la sesión activa."""
        raise NotImplementedError

    def __enter__(self) -> Self:
        self.session = self.session_factory()
        try:
            self._init_repositories(self.session)
        except BaseException:
            self.session.close()
            self.session = None
            raise
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.session is None:
            return
        try:
            if exc_type is not None:
                self.session.rollback()
            else:
                try:
                    self.session.commit()
                except BaseException:
                    self.session.rollback()
                    raise
        finally:
            self.session.close()
            self.session = None

    def commit(self) -> None:
        """Confirma manualmente la transacción activa si fuera necesario."""
        if self.session is None:
            raise RuntimeError("No hay una sesión activa en el Unit of Work.")
        self.session.commit()

    def rollback(self) -> None:
        """Revierte manualmente la transacción activa si fuera necesario."""
        if self.session is None:
            raise RuntimeError("No hay una sesión activa en el Unit of Work.")
        self.session.rollback()
