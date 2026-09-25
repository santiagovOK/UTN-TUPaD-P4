"""
Pruebas de la Fase 2: Tarea 2.1 - Validaciones de Schema con Pydantic.

Cubre:
- Validador dedicado validate_producto_nombres() en validators.py.
- Restricciones declarativas y de negocio en ProductoCreate y ProductoUpdate (RN-02, RN-03).
- Ausencia de validador de entrada en ProductoResponse (diseño idiomático).
- Comportamiento de la API ante payloads inválidos (422 Unprocessable Entity, sin caídas HTTP 500).
"""

import pytest
from pydantic import ValidationError
from fastapi.testclient import TestClient
from app.main import app
from app.modules.producto.validators import validate_producto_nombres
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse,
)


client = TestClient(app)


# =====================================================================
# 1. Pruebas Unitarias del Validador Dedicado (validators.py)
# =====================================================================

def test_validate_producto_nombres_empty_raises():
    """Cadena vacía debe lanzar ValueError."""
    with pytest.raises(ValueError, match="El nombre no puede estar vacío o contener solo espacios"):
        validate_producto_nombres("")


@pytest.mark.parametrize("invalid_spaces", ["   ", "\t", "\n", " \t \n "])
def test_validate_producto_nombres_spaces_raises(invalid_spaces):
    """Cadenas compuestas únicamente por espacios/tabulaciones/saltos deben fallar (RN-02)."""
    with pytest.raises(ValueError, match="El nombre no puede estar vacío o contener solo espacios"):
        validate_producto_nombres(invalid_spaces)


def test_validate_producto_nombres_sanitizes_whitespace():
    """Debe normalizar recortando espacios circundantes y retornar la cadena limpia."""
    assert validate_producto_nombres("  Auriculares Bluetooth  ") == "Auriculares Bluetooth"
    assert validate_producto_nombres("Mouse") == "Mouse"


# =====================================================================
# 2. Pruebas de Schemas Pydantic / DTOs (schemas.py)
# =====================================================================

def test_producto_create_none_nombre_raises_validation_error():
    """nombre=None debe ser rechazado por Pydantic con ValidationError (tipo inválido)."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoCreate(nombre=None, precio=10.0)
    assert any(err["loc"] == ("nombre",) for err in exc_info.value.errors())


def test_producto_create_spaces_nombre_raises_validation_error():
    """nombre con solo espacios debe lanzar ValidationError con el mensaje de negocio."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoCreate(nombre="   ", precio=10.0)
    msg = exc_info.value.errors()[0]["msg"]
    assert "El nombre no puede estar vacío o contener solo espacios" in msg


def test_producto_create_sanitizes_nombre():
    """ProductoCreate debe almacenar el nombre sanitizado (sin espacios circundantes)."""
    prod = ProductoCreate(nombre="  Webcam HD  ", precio=45.0)
    assert prod.nombre == "Webcam HD"


def test_producto_create_negative_precio_raises():
    """Precio menor a 0 debe fallar por restricción declarativa ge=0 (RN-03)."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoCreate(nombre="Cable HDMI", precio=-5.0)
    assert any("greater_than_equal" in err["type"] for err in exc_info.value.errors())


def test_producto_create_zero_precio_allowed():
    """Precio igual a 0.0 debe ser permitido según RN-03 (ge=0)."""
    prod = ProductoCreate(nombre="Producto Gratuito", precio=0.0)
    assert prod.precio == 0.0


def test_producto_update_none_nombre_is_allowed():
    """En actualización parcial, nombre=None no debe disparar validación de vacío."""
    up = ProductoUpdate(nombre=None, precio=30.0)
    assert up.nombre is None


def test_producto_update_spaces_nombre_raises():
    """En actualización, si se suministra un nombre con solo espacios, debe ser rechazado."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoUpdate(nombre="   ")
    assert "El nombre no puede estar vacío o contener solo espacios" in exc_info.value.errors()[0]["msg"]


def test_producto_update_sanitizes_nombre():
    """En actualización, si se suministra un nombre válido con espacios, debe sanitizarse."""
    up = ProductoUpdate(nombre="  Pad Mouse  ")
    assert up.nombre == "Pad Mouse"


def test_producto_response_does_not_block_existing_data():
    """ProductoResponse no debe tener validador de entrada que impida serializar registros existentes."""
    resp = ProductoResponse(id=99, nombre="Legacy Item", precio=10.0)
    assert resp.id == 99
    assert resp.nombre == "Legacy Item"


# =====================================================================
# 3. Pruebas de API REST con TestClient (Endpoints HTTP)
# =====================================================================

def test_api_create_producto_null_nombre_returns_422():
    """Garantiza que un nombre nulo devuelva HTTP 422 y NUNCA un crash HTTP 500."""
    response = client.post("/productos/", json={"nombre": None, "precio": 100.0})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_create_producto_spaces_nombre_returns_422():
    """Garantiza que un nombre de solo espacios devuelva HTTP 422."""
    response = client.post("/productos/", json={"nombre": "   ", "precio": 100.0})
    assert response.status_code == 422
    assert "El nombre no puede estar vacío o contener solo espacios" in str(response.json())


def test_api_create_producto_negative_precio_returns_422():
    """Garantiza que un precio negativo devuelva HTTP 422 (RN-03)."""
    response = client.post("/productos/", json={"nombre": "Parlantes", "precio": -15.0})
    assert response.status_code == 422


def test_api_create_producto_sanitizes_nombre_in_response():
    """Garantiza que un alta válida normalice el nombre y devuelva HTTP 201 Created."""
    response = client.post(
        "/productos/",
        json={"nombre": "  Teclado Mecanico RGB  ", "precio": 120.0},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Teclado Mecanico RGB"
    assert body["precio"] == 120.0
