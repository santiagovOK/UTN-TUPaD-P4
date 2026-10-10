"""
Servicios de datos para la entidad Categoria.

[Consigna TP6 - Rúbrica Backend]: CRUD Categorías con persistencia en Base de Datos mediante SQLModel Session.
Reemplaza la persistencia en memoria por transacciones atómicas contra la base de datos relacional.
"""
from typing import List, Optional
from sqlmodel import Session, select
from app.models.categoria import Categoria
from .schemas import CategoriaCreate

# [Consigna TP6 - Rúbrica Backend]: Alta de categoría con persistencia en DB (db.add, db.commit, db.refresh)
def crear(db: Session, data: CategoriaCreate) -> Categoria:
    nueva = Categoria.model_validate(data)
    db.add(nueva)
    db.commit()
    db.refresh(nueva)
    return nueva


# [Consigna TP6 - Rúbrica Backend]: Listado de categorías persistidas en DB relacional (select(Categoria))
def obtener_todas(db: Session, skip: int = 0, limit: int = 10) -> List[Categoria]:
    statement = select(Categoria).offset(skip).limit(limit)
    return list(db.exec(statement).all())


# [Consigna TP6 - Rúbrica Backend]: Consulta de categoría por clave primaria en DB (db.get)
def obtener_por_id(db: Session, id: int) -> Optional[Categoria]:
    return db.get(Categoria, id)


# [Consigna TP6 - Rúbrica Backend]: Modificación total de categoría en DB (db.commit)
def actualizar_total(
    db: Session, id: int, data: CategoriaCreate
) -> Optional[Categoria]:
    categoria = db.get(Categoria, id)
    if not categoria:
        return None
    categoria.nombre = data.nombre
    categoria.descripcion = data.descripcion
    categoria.activo = data.activo
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


# [Consigna TP6 - Rúbrica Backend]: Borrado lógico (activo = False) persistido en DB
def desactivar(db: Session, id: int) -> Optional[Categoria]:
    categoria = db.get(Categoria, id)
    if not categoria:
        return None
    categoria.activo = False
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


# [Consigna TP6 - Rúbrica Backend]: Eliminación física de categoría en DB (db.delete, db.commit)
def eliminar(db: Session, id: int) -> bool:
    categoria = db.get(Categoria, id)
    if not categoria:
        return False
    db.delete(categoria)
    db.commit()
    return True
