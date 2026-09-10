"""
Lógica de negocio y persistencia en memoria para el módulo Proveedor.
"""
from typing import List, Optional
from fastapi import HTTPException, status
from . import schemas

# Almacenamiento en memoria para proveedores
proveedores_db: List[dict] = []
id_actual: int = 0
