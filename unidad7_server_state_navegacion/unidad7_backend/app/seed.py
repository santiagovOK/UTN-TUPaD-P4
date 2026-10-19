"""Poblado semilla idempotente de catálogo para TP7.

[Consigna TP7 - 18/10: 7 unidades de medida oficiales]
"""

from typing import Dict, List, Union

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.unidad_medida import UnidadMedida

# Las 7 unidades oficiales definidas en docs/consigna.md
UNIDADES_MEDIDA_SEED: List[Dict[str, Union[int, str]]] = [
    {"id": 1, "nombre": "kilogramo", "simbolo": "kg", "tipo": "masa"},
    {"id": 2, "nombre": "gramo", "simbolo": "g", "tipo": "masa"},
    {"id": 3, "nombre": "litro", "simbolo": "L", "tipo": "volumen"},
    {"id": 4, "nombre": "mililitro", "simbolo": "mL", "tipo": "volumen"},
    {"id": 5, "nombre": "pieza", "simbolo": "u", "tipo": "unidad"},
    {"id": 6, "nombre": "docena", "simbolo": "doc", "tipo": "unidad"},
    {"id": 7, "nombre": "metro cuadrado", "simbolo": "m²", "tipo": "area"},
]


def seed_unidades_medida(session: Session) -> List[UnidadMedida]:
    """Inserta o sincroniza las unidades de medida oficiales de forma idempotente.

    Garantiza que el catálogo base contenga las 7 unidades estándar
    requeridas por la especificación de dominio del 18/10.
    """
    for item in UNIDADES_MEDIDA_SEED:
        unidad = session.exec(
            select(UnidadMedida).where(
                (UnidadMedida.id == item["id"])
                | (func.lower(UnidadMedida.nombre) == str(item["nombre"]).lower())
            )
        ).first()

        if unidad is None:
            nueva_unidad = UnidadMedida(
                id=item["id"],
                nombre=str(item["nombre"]),
                simbolo=str(item["simbolo"]),
                tipo=str(item["tipo"]),
            )
            session.add(nueva_unidad)
        else:
            unidad.nombre = str(item["nombre"])
            unidad.simbolo = str(item["simbolo"])
            unidad.tipo = str(item["tipo"])
            session.add(unidad)

    session.commit()

    return list(session.exec(select(UnidadMedida).order_by(UnidadMedida.id)).all())
