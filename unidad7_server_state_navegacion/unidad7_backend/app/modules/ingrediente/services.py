"""Capa de servicio para la entidad Ingrediente.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[Diagrama UML - Clúster Catálogo de Productos - INGREDIENTE]
"""

from typing import List, Optional, Tuple, Union

from sqlmodel import Session, func, select

from app.models.ingrediente import Ingrediente
from app.models.producto import Producto, ProductoIngrediente, _utc_now
from app.models.unidad_medida import UnidadMedida
from app.seed import seed_unidades_medida
from .schemas import IngredienteCreate, IngredienteUpdate


class IngredienteConflictError(ValueError):
    """Excepción de dominio cuando el nombre de ingrediente colisiona o tiene productos asociados."""


class IngredienteUnidadNotFoundError(LookupError):
    """Excepción de dominio cuando la unidad de medida no existe."""


def _ensure_unidades(session: Session) -> None:
    """Asegura que las unidades de medida existan si la base está vacía."""
    total = session.exec(select(func.count()).select_from(UnidadMedida)).one()
    if total == 0:
        seed_unidades_medida(session)


def create_ingrediente(session: Session, data: IngredienteCreate) -> Ingrediente:
    """Crea un ingrediente validando unidad de medida y unicidad."""
    _ensure_unidades(session)

    # Validar existencia de unidad de medida
    unidad = session.get(UnidadMedida, data.unidad_medida_id)
    if not unidad:
        raise IngredienteUnidadNotFoundError(
            f"La unidad de medida con id {data.unidad_medida_id} no existe."
        )

    # Validar colisión de nombre insensible a mayúsculas
    colision = session.exec(
        select(Ingrediente).where(func.lower(Ingrediente.nombre) == data.nombre.lower())
    ).first()

    if colision:
        if colision.deleted_at is None:
            raise IngredienteConflictError(
                f"Ya existe un ingrediente con el nombre '{data.nombre}'."
            )
        # Reactivación tras baja lógica
        now = _utc_now()
        colision.nombre = data.nombre
        colision.descripcion = data.descripcion or ""
        colision.unidad_medida_id = data.unidad_medida_id
        colision.activo = data.activo
        colision.deleted_at = None
        colision.updated_at = now
        session.add(colision)
        session.commit()
        session.refresh(colision)
        return colision

    ingrediente = Ingrediente.model_validate(data)
    session.add(ingrediente)
    session.commit()
    session.refresh(ingrediente)
    return ingrediente


def get_ingredientes(
    session: Session,
    offset: int = 0,
    limit: int = 10,
    nombre: Optional[str] = None,
    search: Optional[str] = None,
    incluir_inactivos: bool = False,
) -> Tuple[int, List[Ingrediente]]:
    """Retorna total de registros y la lista paginada de ingredientes."""
    query = select(Ingrediente)

    if not incluir_inactivos:
        query = query.where(Ingrediente.deleted_at.is_(None))

    filtro_nombre = nombre if nombre is not None else search
    if filtro_nombre and filtro_nombre.strip():
        query = query.where(Ingrediente.nombre.ilike(f"%{filtro_nombre.strip()}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total: int = session.exec(count_query).one()

    items = session.exec(query.order_by(Ingrediente.id).offset(offset).limit(limit)).all()
    return total, list(items)


def get_ingrediente(session: Session, ingrediente_id: int) -> Optional[Ingrediente]:
    """Obtiene un ingrediente activo por su identificador primario."""
    ingrediente = session.get(Ingrediente, ingrediente_id)
    if not ingrediente or ingrediente.deleted_at is not None:
        return None
    return ingrediente


def update_ingrediente(
    session: Session,
    ingrediente_id: int,
    data: Union[IngredienteUpdate, IngredienteCreate],
) -> Optional[Ingrediente]:
    """Actualiza los datos de un ingrediente activo."""
    ingrediente = get_ingrediente(session, ingrediente_id)
    if not ingrediente:
        return None

    update_data = data.model_dump(exclude_unset=True)

    if "unidad_medida_id" in update_data and update_data["unidad_medida_id"] is not None:
        _ensure_unidades(session)
        unidad = session.get(UnidadMedida, update_data["unidad_medida_id"])
        if not unidad:
            raise IngredienteUnidadNotFoundError(
                f"La unidad de medida con id {update_data['unidad_medida_id']} no existe."
            )

    if "nombre" in update_data and update_data["nombre"] is not None:
        nuevo_nombre = update_data["nombre"]
        colision = session.exec(
            select(Ingrediente).where(
                func.lower(Ingrediente.nombre) == nuevo_nombre.lower(),
                Ingrediente.id != ingrediente_id,
            )
        ).first()
        if colision:
            raise IngredienteConflictError(
                f"Ya existe un ingrediente con el nombre '{nuevo_nombre}'."
            )

    if "descripcion" in update_data and update_data["descripcion"] is None:
        update_data["descripcion"] = ""

    for key, value in update_data.items():
        setattr(ingrediente, key, value)

    ingrediente.updated_at = _utc_now()
    session.add(ingrediente)
    session.commit()
    session.refresh(ingrediente)
    return ingrediente


def delete_ingrediente(session: Session, ingrediente_id: int) -> bool:
    """Da de baja lógicamente un ingrediente validando que no tenga productos activos asociados."""
    ingrediente = session.get(Ingrediente, ingrediente_id)
    if not ingrediente or ingrediente.deleted_at is not None:
        return False

    # Verificar si tiene productos activos asociados
    productos_asociados = session.exec(
        select(func.count())
        .select_from(ProductoIngrediente)
        .join(Producto, Producto.id == ProductoIngrediente.producto_id)
        .where(
            ProductoIngrediente.ingrediente_id == ingrediente_id,
            Producto.deleted_at.is_(None),
        )
    ).one()

    if productos_asociados > 0:
        raise IngredienteConflictError(
            "No se puede eliminar el ingrediente porque tiene productos asociados."
        )

    now = _utc_now()
    ingrediente.deleted_at = now
    ingrediente.updated_at = now
    ingrediente.activo = False
    session.add(ingrediente)
    session.commit()
    return True


# Alias arquitectónicos
crear = create_ingrediente
obtener_todos = get_ingredientes
obtener_por_id = get_ingrediente
actualizar = update_ingrediente
eliminar = delete_ingrediente
