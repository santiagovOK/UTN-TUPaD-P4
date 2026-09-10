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

def obtener_proveedor_por_id(id: int) -> schemas.ProveedorRead:
    for p in proveedores_db:
        if p.id == id:
            return p
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Proveedor con id {id} no encontrado"
    )

def actualizar_proveedor(id: int, data: schemas.ProveedorUpdate) -> schemas.ProveedorRead:
    # RN-04: Validacion de existencia (lanza 404 si no existe)
    proveedor_actual = obtener_proveedor_por_id(id)

    # RN-02: Validacion de codigo unico si se desea actualizar
    if data.codigo is not None and data.codigo != proveedor_actual.codigo:
        for p in proveedores_db:
            if p.id != id and p.codigo == data.codigo:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe otro proveedor con el codigo '{data.codigo}'"
                )

    datos_actualizados = proveedor_actual.model_dump()
    datos_actualizados.update(data.model_dump(exclude_unset=True))
    proveedor_nuevo = schemas.ProveedorRead(**datos_actualizados)

    for index, p in enumerate(proveedores_db):
        if p.id == id:
            proveedores_db[index] = proveedor_nuevo
            break

    return proveedor_nuevo

def desactivar_proveedor(id: int) -> schemas.ProveedorRead:
    # RN-04: Validacion de existencia (lanza 404 si no existe)
    proveedor_actual = obtener_proveedor_por_id(id)

    # RN-05: Validacion de no desactivar ya desactivado
    if not proveedor_actual.activo:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"El proveedor con id {id} ya se encuentra desactivado"
        )

    datos = proveedor_actual.model_dump()
    datos["activo"] = False
    proveedor_desactivado = schemas.ProveedorRead(**datos)

    for index, p in enumerate(proveedores_db):
        if p.id == id:
            proveedores_db[index] = proveedor_desactivado
            break

    return proveedor_desactivado


# Alias para mantener consistencia con el patron de categoria y producto
desactivar = desactivar_proveedor


# Aliases para mantener consistencia con el patron de categoria y producto
obtener_por_id = obtener_proveedor_por_id
obtener_todos = listar_proveedores
crear = crear_proveedor
actualizar_total = actualizar_proveedor
