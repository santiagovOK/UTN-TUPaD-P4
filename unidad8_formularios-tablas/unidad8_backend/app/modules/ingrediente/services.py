"""Capa de servicio para la entidad Ingrediente con patrón Repository y Unit of Work.

[TP8 - Ampliación Opcional: Patrón Repository y Unit of Work en Ingredientes]
[HU-05: Catálogo de Ingredientes - Orquestación de Casos de Uso]
[RN-10: Unicidad de nombre de ingrediente insensible a mayúsculas]
[RN-11: Restricción de baja con productos activos asociados]
"""

from typing import List, Optional, Tuple, Union

from sqlmodel import Session

from app.models.ingrediente import Ingrediente
from app.models.producto import _utc_now
from .repository import IngredienteRepository, UnidadMedidaReadRepository
from .schemas import (
    IngredienteCreate,
    IngredienteRead,
    IngredienteUpdate,
)
from .unit_of_work import IngredienteUnitOfWork


class IngredienteConflictError(ValueError):
    """Excepción de dominio cuando el nombre de ingrediente colisiona o tiene productos asociados."""


class IngredienteUnidadNotFoundError(LookupError):
    """Excepción de dominio cuando la unidad de medida no existe."""


class _ExistingSessionUoW(IngredienteUnitOfWork):
    """Adaptador de UoW cuando un consumidor provee explícitamente una sesión SQLModel activa."""

    def __init__(self, session: Session) -> None:
        super().__init__()
        self._existing_session = session

    def __enter__(self) -> "IngredienteUnitOfWork":
        self.session = self._existing_session
        self._init_repositories(self.session)
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if self.session is None:
            return
        if exc_type is not None:
            self.session.rollback()
        else:
            self.session.commit()
        self.session = None


class IngredienteService:
    """Servicio de dominio para la gestión del catálogo de Ingredientes.

    Orquesta las operaciones transaccionales a través de IngredienteUnitOfWork,
    manteniéndose desacoplado del protocolo de transporte HTTP/FastAPI.
    """

    def __init__(self, uow: Optional[IngredienteUnitOfWork] = None) -> None:
        self.uow = uow if uow is not None else IngredienteUnitOfWork()

    def crear(self, data: IngredienteCreate) -> IngredienteRead:
        """Crea un ingrediente validando unidad de medida y unicidad insensible a mayúsculas."""
        with self.uow as uow:
            uow.unidades.ensure_seeded()
            unidad = uow.unidades.get_by_id(data.unidad_medida_id)
            if not unidad:
                raise IngredienteUnidadNotFoundError(
                    f"La unidad de medida con id {data.unidad_medida_id} no existe."
                )

            colision = uow.ingredientes.get_by_nombre_ci(data.nombre)
            if colision:
                if colision.deleted_at is None:
                    raise IngredienteConflictError(
                        f"Ya existe un ingrediente con el nombre '{data.nombre}'."
                    )
                # Reactivación tras baja lógica conservando ID original
                now = _utc_now()
                colision.nombre = data.nombre
                colision.descripcion = data.descripcion or ""
                colision.unidad_medida_id = data.unidad_medida_id
                colision.activo = data.activo
                colision.deleted_at = None
                colision.updated_at = now
                uow.ingredientes.update(colision)
                return IngredienteRead.model_validate(colision)

            ingrediente = Ingrediente.model_validate(data)
            created = uow.ingredientes.create(ingrediente)
            return IngredienteRead.model_validate(created)

    def listar(
        self,
        offset: int = 0,
        limit: int = 10,
        nombre: Optional[str] = None,
        search: Optional[str] = None,
        incluir_inactivos: bool = False,
    ) -> Tuple[int, List[IngredienteRead]]:
        """Retorna el total de coincidencias y la lista de ingredientes paginados."""
        with self.uow as uow:
            total, items = uow.ingredientes.list_paginated(
                offset=offset,
                limit=limit,
                nombre=nombre,
                search=search,
                incluir_inactivos=incluir_inactivos,
            )
            return total, [IngredienteRead.model_validate(item) for item in items]

    def obtener(self, ingrediente_id: int) -> Optional[IngredienteRead]:
        """Obtiene un ingrediente activo por su ID primario."""
        with self.uow as uow:
            ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
            if not ingrediente:
                return None
            return IngredienteRead.model_validate(ingrediente)

    def actualizar(
        self,
        ingrediente_id: int,
        data: Union[IngredienteUpdate, IngredienteCreate],
    ) -> Optional[IngredienteRead]:
        """Actualiza los datos de un ingrediente activo."""
        with self.uow as uow:
            ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
            if not ingrediente:
                return None

            update_data = data.model_dump(exclude_unset=True)

            if (
                "unidad_medida_id" in update_data
                and update_data["unidad_medida_id"] is not None
            ):
                uow.unidades.ensure_seeded()
                unidad = uow.unidades.get_by_id(update_data["unidad_medida_id"])
                if not unidad:
                    raise IngredienteUnidadNotFoundError(
                        f"La unidad de medida con id {update_data['unidad_medida_id']} no existe."
                    )

            if "nombre" in update_data and update_data["nombre"] is not None:
                nuevo_nombre = update_data["nombre"]
                colision = uow.ingredientes.get_by_nombre_ci(
                    nuevo_nombre, exclude_id=ingrediente_id
                )
                if colision:
                    raise IngredienteConflictError(
                        f"Ya existe un ingrediente con el nombre '{nuevo_nombre}'."
                    )

            if "descripcion" in update_data and update_data["descripcion"] is None:
                update_data["descripcion"] = ""

            for key, value in update_data.items():
                setattr(ingrediente, key, value)

            ingrediente.updated_at = _utc_now()
            updated = uow.ingredientes.update(ingrediente)
            return IngredienteRead.model_validate(updated)

    def eliminar(self, ingrediente_id: int) -> bool:
        """Da de baja lógicamente un ingrediente validando que no tenga productos asociados."""
        with self.uow as uow:
            ingrediente = uow.ingredientes.get_active_by_id(ingrediente_id)
            if not ingrediente:
                return False

            productos_asociados = uow.ingredientes.count_active_productos(
                ingrediente_id
            )
            if productos_asociados > 0:
                raise IngredienteConflictError(
                    "No se puede eliminar el ingrediente porque tiene productos asociados."
                )

            uow.ingredientes.soft_delete(ingrediente)
            return True


# ---------------------------------------------------------------------------
# Funciones de módulo y adaptadores retrocompatibles
# ---------------------------------------------------------------------------


def _build_service(session: Optional[Session] = None) -> IngredienteService:
    if session is not None:
        uow = _ExistingSessionUoW(session)
    else:
        uow = IngredienteUnitOfWork()
    return IngredienteService(uow=uow)


def create_ingrediente(
    session_or_data: Union[Session, IngredienteCreate],
    data: Optional[IngredienteCreate] = None,
) -> IngredienteRead:
    """Crea un ingrediente delegando en IngredienteService."""
    if isinstance(session_or_data, Session):
        session = session_or_data
        actual_data = data
    else:
        session = None
        actual_data = session_or_data

    if actual_data is None:
        raise ValueError("data es requerido para create_ingrediente")
    return _build_service(session).crear(actual_data)


def get_ingredientes(
    session: Optional[Session] = None,
    offset: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    search: Optional[str] = None,
    incluir_inactivos: bool = False,
) -> Tuple[int, List[IngredienteRead]]:
    """Retorna total de registros y la lista paginada de ingredientes."""
    return _build_service(session).listar(
        offset=offset,
        limit=limit,
        nombre=nombre,
        search=search,
        incluir_inactivos=incluir_inactivos,
    )


def get_ingrediente(
    session_or_id: Union[Session, int],
    ingrediente_id: Optional[int] = None,
) -> Optional[IngredienteRead]:
    """Obtiene un ingrediente activo por su identificador primario."""
    if isinstance(session_or_id, Session):
        session = session_or_id
        target_id = ingrediente_id
    else:
        session = None
        target_id = session_or_id

    if target_id is None:
        raise ValueError("ingrediente_id es requerido")
    return _build_service(session).obtener(target_id)


def update_ingrediente(
    session_or_id: Union[Session, int],
    ingrediente_id_or_data: Union[int, IngredienteUpdate, IngredienteCreate],
    data: Optional[Union[IngredienteUpdate, IngredienteCreate]] = None,
) -> Optional[IngredienteRead]:
    """Actualiza los datos de un ingrediente activo."""
    if isinstance(session_or_id, Session):
        session = session_or_id
        target_id = int(ingrediente_id_or_data)
        actual_data = data
    else:
        session = None
        target_id = int(session_or_id)
        actual_data = ingrediente_id_or_data  # type: ignore

    if actual_data is None:
        raise ValueError("data es requerido para update_ingrediente")
    return _build_service(session).actualizar(target_id, actual_data)


def delete_ingrediente(
    session_or_id: Union[Session, int],
    ingrediente_id: Optional[int] = None,
) -> bool:
    """Da de baja lógicamente un ingrediente."""
    if isinstance(session_or_id, Session):
        session = session_or_id
        target_id = ingrediente_id
    else:
        session = None
        target_id = session_or_id

    if target_id is None:
        raise ValueError("ingrediente_id es requerido")
    return _build_service(session).eliminar(target_id)


# Alias arquitectónicos
crear = create_ingrediente
obtener_todos = get_ingredientes
obtener_por_id = get_ingrediente
actualizar = update_ingrediente
eliminar = delete_ingrediente
