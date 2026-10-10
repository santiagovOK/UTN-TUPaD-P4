"""
Pruebas integrales del dominio Producto e Infraestructura de Base de Datos.

Organización por secciones:
1. Infraestructura y Modelo (DATABASE_URL, engine, get_session, metadatos DDL de Producto y DTOs base).
2. Validadores y Schemas Pydantic (validate_producto_nombres, ProductoCreate, ProductoUpdate, ProductoResponse).
3. Servicios Transaccionales (CRUD en services.py con SQLModel Session, control de duplicados, borrado lógico y stock).
4. Endpoints HTTP / Sociable Tests (Integración con FastAPI TestClient).
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session
from fastapi.testclient import TestClient

from app.database import engine, get_session, DATABASE_URL
from app.models.producto import Producto, ProductoBase
from app.modules.producto.validators import validate_producto_nombres
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoResponse,
    ProductoStockResponse,
)
from app.modules.producto import services


# =====================================================================
# 1. Infraestructura y Modelo
# =====================================================================

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


# =====================================================================
# 2. Validadores y Schemas Pydantic
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
# 3. Servicios Transaccionales
# =====================================================================

def test_service_crear_producto_persists_entity(session: Session):
    """Verifica que crear_producto persista la entidad y asigne clave primaria."""
    data = ProductoCreate(
        nombre="Monitor Gamer 144Hz",
        descripcion="Panel IPS 1ms",
        precio=320.0,
        categoria="Monitores",
        stock=15,
        stock_minimo=3,
    )
    producto = services.crear_producto(session, data)

    assert producto.id is not None
    assert producto.id > 0
    assert producto.nombre == "Monitor Gamer 144Hz"
    assert producto.activo is True

    db_entity = session.get(Producto, producto.id)
    assert db_entity is not None
    assert db_entity.nombre == "Monitor Gamer 144Hz"


def test_service_crear_producto_duplicate_name_raises(session: Session):
    """Verifica que crear_producto rechace nombres duplicados con ValueError."""
    data1 = ProductoCreate(nombre="Mouse Inalámbrico", precio=25.0)
    services.crear_producto(session, data1)

    data2 = ProductoCreate(nombre="Mouse Inalámbrico", precio=30.0)
    with pytest.raises(ValueError, match="Producto duplicado"):
        services.crear_producto(session, data2)


def test_service_obtener_producto_por_id_success_and_not_found(session: Session):
    """Verifica consulta por ID y lanzamiento de excepción de dominio cuando no existe."""
    data = ProductoCreate(nombre="Teclado Mecánico", precio=80.0)
    creado = services.crear_producto(session, data)

    obtenido = services.obtener_producto_por_id(session, creado.id)
    assert obtenido.id == creado.id
    assert obtenido.nombre == "Teclado Mecánico"

    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.obtener_producto_por_id(session, 9999)


def test_service_listar_productos_pagination(session: Session):
    """Verifica que listar_productos respete el orden, skip y limit."""
    for i in range(5):
        services.crear_producto(
            session, ProductoCreate(nombre=f"Item {i}", precio=10.0 * (i + 1))
        )

    pagina = services.listar_productos(session, skip=1, limit=2)
    assert len(pagina) == 2
    assert pagina[0].nombre == "Item 1"
    assert pagina[1].nombre == "Item 2"


def test_service_actualizar_producto_partial(session: Session):
    """Verifica actualización parcial excluyendo campos no provistos."""
    creado = services.crear_producto(
        session,
        ProductoCreate(
            nombre="Gabinete ATX",
            precio=90.0,
            stock=10,
            stock_minimo=2,
        ),
    )

    update_dto = ProductoUpdate(precio=105.0)
    actualizado = services.actualizar_producto(session, creado.id, update_dto)

    assert actualizado.precio == 105.0
    assert actualizado.nombre == "Gabinete ATX"
    assert actualizado.stock == 10


def test_service_actualizar_producto_duplicate_name_raises(session: Session):
    """Verifica que actualizar al nombre de otro producto existente lance ValueError."""
    services.crear_producto(session, ProductoCreate(nombre="Disco SSD", precio=50.0))
    p2 = services.crear_producto(session, ProductoCreate(nombre="Disco HDD", precio=30.0))

    update_conflict = ProductoUpdate(nombre="Disco SSD")
    with pytest.raises(ValueError, match="Producto duplicado"):
        services.actualizar_producto(session, p2.id, update_conflict)


def test_service_actualizar_producto_not_found_raises(session: Session):
    """Verifica que actualizar un ID inexistente lance ValueError."""
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.actualizar_producto(
            session, 9999, ProductoUpdate(precio=50.0)
        )


def test_service_eliminar_producto_logical_deletion(session: Session):
    """Verifica que eliminar_producto aplique borrado lógico (activo=False) en BD."""
    creado = services.crear_producto(
        session, ProductoCreate(nombre="Fuente 600W", precio=65.0)
    )
    assert creado.activo is True

    eliminado = services.eliminar_producto(session, creado.id)
    assert eliminado.activo is False

    en_bd = session.get(Producto, creado.id)
    assert en_bd is not None
    assert en_bd.activo is False


def test_service_eliminar_producto_not_found_raises(session: Session):
    """Verifica que eliminar un ID inexistente lance ValueError."""
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.eliminar_producto(session, 9999)


def test_service_obtener_estado_stock_thresholds_and_null_safe(session: Session):
    """Verifica cálculo de bajo_stock_minimo y resguardo ante campos opcionales nulos."""
    p_bajo = services.crear_producto(
        session,
        ProductoCreate(nombre="RAM 8GB", precio=40.0, stock=2, stock_minimo=5),
    )
    estado_bajo = services.obtener_estado_stock(session, p_bajo.id)
    assert estado_bajo["stock"] == 2
    assert estado_bajo["bajo_stock_minimo"] is True
    assert estado_bajo["activo"] is True

    p_ok = services.crear_producto(
        session,
        ProductoCreate(nombre="RAM 16GB", precio=75.0, stock=10, stock_minimo=5),
    )
    estado_ok = services.obtener_estado_stock(session, p_ok.id)
    assert estado_ok["bajo_stock_minimo"] is False

    p_null = services.crear_producto(
        session,
        ProductoCreate(nombre="Licencia Software", precio=199.0, stock=None, stock_minimo=None),
    )
    estado_null = services.obtener_estado_stock(session, p_null.id)
    assert estado_null["stock"] == 0
    assert estado_null["bajo_stock_minimo"] is False

    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.obtener_estado_stock(session, 9999)


# =====================================================================
# 4. Endpoints HTTP / Sociable Tests
# =====================================================================

def test_api_create_producto_null_nombre_returns_422(client: TestClient):
    """Garantiza que un nombre nulo devuelva HTTP 422 y NUNCA un crash HTTP 500."""
    response = client.post("/productos/", json={"nombre": None, "precio": 100.0})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_create_producto_spaces_nombre_returns_422(client: TestClient):
    """Garantiza que un nombre de solo espacios devuelva HTTP 422."""
    response = client.post("/productos/", json={"nombre": "   ", "precio": 100.0})
    assert response.status_code == 422
    assert "El nombre no puede estar vacío o contener solo espacios" in str(response.json())


def test_api_create_producto_negative_precio_returns_422(client: TestClient):
    """Garantiza que un precio negativo devuelva HTTP 422 (RN-03)."""
    response = client.post("/productos/", json={"nombre": "Parlantes", "precio": -15.0})
    assert response.status_code == 422


def test_api_create_producto_sanitizes_nombre_in_response(client: TestClient):
    """Garantiza que un alta válida normalice el nombre y devuelva HTTP 201 Created."""
    response = client.post(
        "/productos/",
        json={"nombre": "  Teclado Mecanico RGB  ", "precio": 120.0},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Teclado Mecanico RGB"
    assert body["precio"] == 120.0


def test_api_crear_producto_success(client: TestClient):
    """POST /productos/ retorna HTTP 201 Created y esquema ProductoResponse."""
    payload = {
        "nombre": "Placa de Video RTX 4060",
        "descripcion": "8GB GDDR6",
        "precio": 450.0,
        "categoria": "Componentes",
        "stock": 5,
        "stock_minimo": 1,
    }
    response = client.post("/productos/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["nombre"] == "Placa de Video RTX 4060"
    assert body["precio"] == 450.0
    assert body["activo"] is True


def test_api_crear_producto_duplicate_returns_409(client: TestClient):
    """POST /productos/ con nombre duplicado retorna HTTP 409 Conflict."""
    payload = {"nombre": "Auricular USB", "precio": 35.0}
    res1 = client.post("/productos/", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/productos/", json=payload)
    assert res2.status_code == 409
    body = res2.json()
    assert "Producto duplicado" in body["detail"]


def test_api_detalle_producto_200_and_404(client: TestClient):
    """GET /productos/{id} retorna 200 para existente y 404 para inexistente."""
    res_crear = client.post("/productos/", json={"nombre": "Hub USB-C", "precio": 22.0})
    prod_id = res_crear.json()["id"]

    res_get = client.get(f"/productos/{prod_id}")
    assert res_get.status_code == 200
    assert res_get.json()["nombre"] == "Hub USB-C"

    res_404 = client.get("/productos/99999")
    assert res_404.status_code == 404
    assert "Producto no encontrado" in res_404.json()["detail"]


def test_api_listar_productos_pagination(client: TestClient):
    """GET /productos/ retorna 200 y array paginado."""
    for i in range(3):
        client.post("/productos/", json={"nombre": f"Accesorio {i}", "precio": 15.0})

    res = client.get("/productos/?skip=0&limit=2")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) == 2


def test_api_actualizar_producto_200_and_404(client: TestClient):
    """PUT /productos/{id} actualiza campos parciales y retorna 200, o 404 si no existe."""
    res_crear = client.post("/productos/", json={"nombre": "Micrófono", "precio": 60.0})
    prod_id = res_crear.json()["id"]

    res_put = client.put(f"/productos/{prod_id}", json={"precio": 75.0, "descripcion": "Condensador"})
    assert res_put.status_code == 200
    assert res_put.json()["precio"] == 75.0
    assert res_put.json()["descripcion"] == "Condensador"
    assert res_put.json()["nombre"] == "Micrófono"

    res_put_404 = client.put("/productos/99999", json={"precio": 10.0})
    assert res_put_404.status_code == 404


def test_api_actualizar_producto_duplicate_returns_409(client: TestClient):
    """PUT /productos/{id} con nombre colisionante retorna HTTP 409 Conflict."""
    client.post("/productos/", json={"nombre": "Cámara Web A", "precio": 50.0})
    res_b = client.post("/productos/", json={"nombre": "Cámara Web B", "precio": 55.0})
    id_b = res_b.json()["id"]

    res_put = client.put(f"/productos/{id_b}", json={"nombre": "Cámara Web A"})
    assert res_put.status_code == 409
    assert "Producto duplicado" in res_put.json()["detail"]


def test_api_eliminar_producto_204_and_404(client: TestClient):
    """DELETE /productos/{id} retorna 204 No Content sin cuerpo y marca activo=False."""
    res_crear = client.post("/productos/", json={"nombre": "Cable DisplayPort", "precio": 18.0})
    prod_id = res_crear.json()["id"]

    res_del = client.delete(f"/productos/{prod_id}")
    assert res_del.status_code == 204
    assert res_del.text == ""

    res_get = client.get(f"/productos/{prod_id}")
    assert res_get.status_code == 200
    assert res_get.json()["activo"] is False

    res_del_404 = client.delete("/productos/99999")
    assert res_del_404.status_code == 404
    assert "Producto no encontrado" in res_del_404.json()["detail"]


def test_api_consultar_stock_200_and_404(client: TestClient):
    """GET /productos/{id}/stock retorna 200 con ProductoStockResponse y 404 si no existe."""
    res_crear = client.post(
        "/productos/",
        json={"nombre": "Router WiFi 6", "precio": 110.0, "stock": 1, "stock_minimo": 4},
    )
    prod_id = res_crear.json()["id"]

    res_stock = client.get(f"/productos/{prod_id}/stock")
    assert res_stock.status_code == 200
    body = res_stock.json()
    assert body["stock"] == 1
    assert body["bajo_stock_minimo"] is True
    assert body["activo"] is True

    res_stock_404 = client.get("/productos/99999/stock")
    assert res_stock_404.status_code == 404
    assert "Producto no encontrado" in res_stock_404.json()["detail"]
