"""
Logica de negocio y persistencia en memoria para el modulo Proveedor.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from . import schemas

# Almacenamiento en memoria para proveedores
proveedores_db: List[schemas.ProveedorRead] = []
id_counter: int = 1


def crear_proveedor(data: schemas.ProveedorCreate) -> schemas.ProveedorRead:
    global id_counter
    # RN-02: Validacion de codigo unico
    for p in proveedores_db:
        if p.codigo == data.codigo:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un proveedor con el codigo '{data.codigo}'"
            )

    nuevo_proveedor = schemas.ProveedorRead(id=id_counter, **data.model_dump())
    proveedores_db.append(nuevo_proveedor)
    id_counter += 1
    return nuevo_proveedor


def listar_proveedores(
    skip: int = 0,
    limit: int = 10,
    activo: Optional[bool] = None
) -> List[schemas.ProveedorRead]:
    resultado = proveedores_db
    if activo is not None:
        resultado = [p for p in resultado if p.activo == activo]
    return resultado[skip : skip + limit]


# Alias para mantener consistencia con el patron de categoria y producto
obtener_todos = listar_proveedores

# Alias para mantener consistencia con el patron de categoria y producto
crear = crear_proveedor
