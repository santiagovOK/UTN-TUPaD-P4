from typing import List, Optional
from .schemas import CategoriaCreate, CategoriaRead

# Simulamos algunos registros iniciales
db_categorias: List[CategoriaRead] = [
    CategoriaRead(id=1, nombre="Muebles de Oficina", descripcion="Muebles y escritorios de trabajo", activo=True),
    CategoriaRead(id=2, nombre="Electrónica", descripcion="Dispositivos y gadgets electrónicos", activo=True),
]
id_counter = 3


def crear(data: CategoriaCreate) -> CategoriaRead:
    global id_counter
    nueva = CategoriaRead(id=id_counter, **data.model_dump())
    db_categorias.append(nueva)
    id_counter += 1
    return nueva


def obtener_todas(skip: int = 0, limit: int = 10) -> List[CategoriaRead]:
    return db_categorias[skip : skip + limit]


def obtener_por_id(id: int) -> Optional[CategoriaRead]:
    return next((c for c in db_categorias if c.id == id), None)

def actualizar_total(id: int, data: CategoriaCreate) -> Optional[CategoriaRead]:
    for index, c in enumerate(db_categorias):
        if c.id == id:
            actualizada = CategoriaRead(id=id, **data.model_dump())
            db_categorias[index] = actualizada
            return actualizada
    return None


def desactivar(id: int) -> Optional[CategoriaRead]:
    for index, c in enumerate(db_categorias):
        if c.id == id:
            actualizada = c.model_copy(update={"activo": False})
            db_categorias[index] = actualizada
            return actualizada
    return None

def eliminar(id: int) -> bool:
    for index, c in enumerate(db_categorias):
        if c.id == id:
            del db_categorias[index]
            return True
    return False
