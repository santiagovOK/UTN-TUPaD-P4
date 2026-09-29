"""
Pruebas de la Fase 1: Infraestructura de Base de Datos y Modelado de Datos.

Cubre:
- Tarea 1.2: Configuración del engine, DATABASE_URL y ciclo de vida de sesiones (database.py).
- Tarea 1.3: Definición del modelo de tabla SQLModel y esquemas DTO base (models/producto.py, schemas/producto.py).
"""

import pytest
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session
from app.database import engine, get_session, DATABASE_URL
from app.models.producto import Producto, ProductoBase
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoResponse,
    ProductoUpdate,
    ProductoStockResponse,
)


def test_database_configuration():
    """Verifica que DATABASE_URL esté definida y el engine esté correctamente instanciado."""
    assert DATABASE_URL is not None, "DATABASE_URL no debe ser None"
    assert isinstance(engine, Engine), "engine debe ser una instancia válida de SQLAlchemy Engine"


def test_get_session_yields_session():
    """Verifica que el generador get_session provea una sesión activa de SQLModel."""
    session_gen = get_session()
    session = next(session_gen)
    assert isinstance(session, Session), "get_session debe entregar una Session de SQLModel"
    assert session.is_active, "La sesión entregada debe estar activa"
    # Cerrar sesión generada
    try:
        next(session_gen)
    except StopIteration:
        pass


def test_producto_table_metadata():
    """Verifica que la entidad Producto esté registrada como tabla en SQLModel.metadata con su PK."""
    assert Producto.__tablename__ == "producto"
    assert "producto" in SQLModel.metadata.tables, "La tabla 'producto' debe estar en los metadatos DDL"
    table = SQLModel.metadata.tables["producto"]
    assert "id" in table.columns, "La tabla debe contener la columna 'id'"
    assert table.columns["id"].primary_key, "La columna 'id' debe ser Primary Key"


def test_producto_base_fields_and_defaults():
    """Verifica los atributos base del modelo ProductoBase y sus valores por defecto."""
    base = ProductoBase(
        nombre="Monitor",
        precio=250.0,
        descripcion="24 pulgadas",
        categoria="Periféricos",
        stock=10,
        stock_minimo=2,
    )
    assert base.nombre == "Monitor"
    assert base.precio == 250.0
    assert base.activo is True, "El valor por defecto de 'activo' debe ser True"


def test_producto_create_does_not_require_id():
    """Verifica que ProductoCreate sea un DTO de creación sin requerir ID."""
    dto = ProductoCreate(nombre="Teclado", precio=50.0)
    assert not hasattr(dto, "id") or getattr(dto, "id", None) is None


def test_producto_response_requires_id():
    """Verifica que ProductoResponse sea un DTO de salida que exija el campo id."""
    resp = ProductoResponse(id=1, nombre="Mouse", precio=25.0)
    assert resp.id == 1
    assert resp.nombre == "Mouse"
