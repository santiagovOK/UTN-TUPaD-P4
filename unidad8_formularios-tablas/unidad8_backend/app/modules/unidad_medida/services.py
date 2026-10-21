"""Capa de servicio para la entidad UnidadMedida (catálogo de solo lectura).

[Catálogo heredado del TP7 - Catálogo base de unidades de medida]
[Extensión heredada del TP7: catálogo inmutable de unidades de medida]
"""

from typing import List, Optional, Tuple

from sqlmodel import Session, func, select

from app.models.unidad_medida import UnidadMedida
from app.seed import seed_unidades_medida


def get_unidades_medida(session: Session) -> Tuple[int, List[UnidadMedida]]:
    """Retorna el total y el listado completo de unidades de medida ordenadas por ID.

    Si la tabla está vacía, garantiza el seed de forma transparente antes de responder.
    """
    total = session.exec(select(func.count()).select_from(UnidadMedida)).one()
    if total == 0:
        seed_unidades_medida(session)
        total = session.exec(select(func.count()).select_from(UnidadMedida)).one()

    items = session.exec(select(UnidadMedida).order_by(UnidadMedida.id)).all()
    return total, list(items)


def get_unidad_medida_by_id(session: Session, unidad_id: int) -> Optional[UnidadMedida]:
    """Obtiene una unidad de medida por su ID primario."""
    total = session.exec(select(func.count()).select_from(UnidadMedida)).one()
    if total == 0:
        seed_unidades_medida(session)

    return session.get(UnidadMedida, unidad_id)


# Alias arquitectónicos
get_unidad_medida = get_unidad_medida_by_id
obtener_todas = get_unidades_medida
obtener_por_id = get_unidad_medida_by_id
