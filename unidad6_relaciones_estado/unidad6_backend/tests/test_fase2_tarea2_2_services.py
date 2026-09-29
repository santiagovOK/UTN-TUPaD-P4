"""
Pruebas de la Fase 2: Tarea 2.2 - Capa Service transaccional y Enrutador HTTP.

Cubre:
- Operaciones CRUD en services.py con SQLModel Session y control de transacciones (add, commit, refresh).
- Validación de regla de negocio de duplicados (ValueError -> HTTP 409 Conflict).
- Control de existencia de producto (ValueError -> HTTP 404 Not Found).
- Borrado lógico (activo = False) vía DELETE /productos/{id} con HTTP 204 No Content.
- Consulta de estado de inventario y alertas de stock mínimo.
- Paginación y actualización parcial/total.
"""

import pytest
from sqlmodel import Session, select
from fastapi.testclient import TestClient

from app.models.producto import Producto
from app.modules.producto.schemas import ProductoCreate, ProductoUpdate
from app.modules.producto import services


# =====================================================================
# 1. Pruebas Unitarias de la Capa Service (services.py)
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

    # Verificar que realmente se persistió en la BD
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

    # Persiste en base de datos con activo = False
    en_bd = session.get(Producto, creado.id)
    assert en_bd is not None
    assert en_bd.activo is False


def test_service_eliminar_producto_not_found_raises(session: Session):
    """Verifica que eliminar un ID inexistente lance ValueError."""
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.eliminar_producto(session, 9999)


def test_service_obtener_estado_stock_thresholds_and_null_safe(session: Session):
    """Verifica cálculo de bajo_stock_minimo y resguardo ante campos opcionales nulos."""
    # Caso 1: stock bajo
    p_bajo = services.crear_producto(
        session,
        ProductoCreate(nombre="RAM 8GB", precio=40.0, stock=2, stock_minimo=5),
    )
    estado_bajo = services.obtener_estado_stock(session, p_bajo.id)
    assert estado_bajo["stock"] == 2
    assert estado_bajo["bajo_stock_minimo"] is True
    assert estado_bajo["activo"] is True

    # Caso 2: stock suficiente
    p_ok = services.crear_producto(
        session,
        ProductoCreate(nombre="RAM 16GB", precio=75.0, stock=10, stock_minimo=5),
    )
    estado_ok = services.obtener_estado_stock(session, p_ok.id)
    assert estado_ok["bajo_stock_minimo"] is False

    # Caso 3: stock y stock_minimo nulos
    p_null = services.crear_producto(
        session,
        ProductoCreate(nombre="Licencia Software", precio=199.0, stock=None, stock_minimo=None),
    )
    estado_null = services.obtener_estado_stock(session, p_null.id)
    assert estado_null["stock"] == 0
    assert estado_null["bajo_stock_minimo"] is False

    # Caso 4: inexistente
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.obtener_estado_stock(session, 9999)


# =====================================================================
# 2. Pruebas de Integración de Endpoints HTTP (routers.py)
# =====================================================================

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

    # Confirmar que sigue accesible vía GET con activo = False (borrado lógico)
    res_get = client.get(f"/productos/{prod_id}")
    assert res_get.status_code == 200
    assert res_get.json()["activo"] is False

    # Eliminar ID inexistente retorna 404
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
