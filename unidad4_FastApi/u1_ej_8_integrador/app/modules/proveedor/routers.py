"""
Endpoints REST para el módulo Proveedor.
"""
from fastapi import APIRouter, HTTPException, Path, Query, status
from typing import List, Optional
from . import schemas, services

router = APIRouter(prefix="/proveedores", tags=["Proveedores"])
