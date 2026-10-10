"""
Pruebas integrales del dominio Producto, relaciones N:N con Categoria e Infraestructura de Base de Datos.

[Consigna TP6 - Parte A, incisos b y d]:
  - Definición de models y schemas: Producto y Producto_Categoria.
  - Endpoints REST de Producto y demostración de relaciones N:N.
[Consigna TP6 - Rúbrica Backend / Pruebas Automatizadas]:
  - Validación con motor SQLite aislado en memoria mediante TestClient y Session SQLModel.
"""

import pytest
from pydantic import ValidationError
from sqlalchemy.engine import Engine
from sqlmodel import SQLModel, Session
from fastapi.testclient import TestClient

from app.database import engine, get_session, DATABASE_URL
from app.models.producto import Producto, ProductoBase
from app.modules.categoria.schemas import CategoriaCreate
from app.modules.categoria import services as categoria_services
from app.modules.producto.validators import validate_producto_nombres
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoRead,
    ProductoReadConCategorias,
)
from app.modules.producto import services


# =====================================================================
# 1. Infraestructura y Modelo
# [Consigna TP6 - Parte A, inciso b & Rúbrica Backend]: Metadatos DDL de Producto y ProductoCategoria
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
    """Verifica que la entidad Producto esté registrada como tabla en SQLModel.metadata con sus columnas TP6."""
    assert Producto.__tablename__ == "producto"
    assert "producto" in SQLModel.metadata.tables, "La tabla 'producto' debe estar en los metadatos DDL"
    table = SQLModel.metadata.tables["producto"]
    assert "id" in table.columns, "La tabla debe contener la columna 'id'"
    assert table.columns["id"].primary_key, "La columna 'id' debe ser Primary Key"
    assert "nombre" in table.columns
    assert "descripcion" in table.columns
    assert "precio_base" in table.columns
    assert "imagen_url" in table.columns
    assert "disponible" in table.columns
    assert "precio" not in table.columns
    assert "stock" not in table.columns


def test_producto_base_fields_and_defaults():
    """Verifica los atributos base del modelo ProductoBase y sus valores por defecto en TP6."""
    base = ProductoBase(
        nombre="Monitor",
        precio_base="250.00",
        descripcion="24 pulgadas",
    )
    assert base.nombre == "Monitor"
    assert base.precio_base == "250.00"
    assert base.descripcion == "24 pulgadas"
    assert base.imagen_url == [], "El valor por defecto de 'imagen_url' debe ser lista vacía"
    assert base.disponible is True, "El valor por defecto de 'disponible' debe ser True"


def test_producto_create_does_not_require_id():
    """Verifica que ProductoCreate sea un DTO de creación sin requerir ID."""
    dto = ProductoCreate(nombre="Teclado", precio_base="50.00", imagen_url=[])
    assert not hasattr(dto, "id") or getattr(dto, "id", None) is None


def test_producto_read_requires_id_and_con_categorias():
    """Verifica que ProductoRead y ProductoReadConCategorias exijan el campo id."""
    resp = ProductoRead(id=1, nombre="Mouse", precio_base="25.00", imagen_url=[])
    assert resp.id == 1
    assert resp.nombre == "Mouse"

    resp_cat = ProductoReadConCategorias(
        id=1, nombre="Mouse", precio_base="25.00", imagen_url=[]
    )
    assert resp_cat.id == 1
    assert resp_cat.categorias == []


# =====================================================================
# 2. Validadores y Schemas Pydantic
# [Consigna TP6 - Parte A, inciso b]: ProductoCreate, ProductoRead, ProductoReadConCategorias, ProductoUpdate
# =====================================================================

def test_validate_producto_nombres_empty_raises():
    """Cadena vacía debe lanzar ValueError."""
    with pytest.raises(ValueError, match="El nombre no puede estar vacío o contener solo espacios"):
        validate_producto_nombres("")


@pytest.mark.parametrize("invalid_spaces", ["   ", "\t", "\n", " \t \n "])
def test_validate_producto_nombres_spaces_raises(invalid_spaces):
    """Cadenas compuestas únicamente por espacios/tabulaciones/saltos deben fallar."""
    with pytest.raises(ValueError, match="El nombre no puede estar vacío o contener solo espacios"):
        validate_producto_nombres(invalid_spaces)


def test_validate_producto_nombres_sanitizes_whitespace():
    """Debe normalizar recortando espacios circundantes y retornar la cadena limpia."""
    assert validate_producto_nombres("  Auriculares Bluetooth  ") == "Auriculares Bluetooth"
    assert validate_producto_nombres("Mouse") == "Mouse"


def test_producto_create_none_nombre_raises_validation_error():
    """nombre=None debe ser rechazado por Pydantic con ValidationError (tipo inválido)."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoCreate(nombre=None, precio_base="10.00", imagen_url=[])
    assert any(err["loc"] == ("nombre",) for err in exc_info.value.errors())


def test_producto_create_spaces_nombre_raises_validation_error():
    """nombre con solo espacios debe lanzar ValidationError con el mensaje de negocio."""
    with pytest.raises(ValidationError) as exc_info:
        ProductoCreate(nombre="   ", precio_base="10.00", imagen_url=[])
    msg = exc_info.value.errors()[0]["msg"]
    assert "El nombre no puede estar vacío o contener solo espacios" in msg


def test_producto_create_sanitizes_nombre():
    """ProductoCreate debe almacenar el nombre sanitizado (sin espacios circundantes)."""
    prod = ProductoCreate(nombre="  Webcam HD  ", precio_base="45.00", imagen_url=[])
    assert prod.nombre == "Webcam HD"


def test_producto_update_none_nombre_is_allowed():
    """En actualización parcial, nombre=None no debe disparar validación de vacío."""
    up = ProductoUpdate(nombre=None, precio_base="30.00")
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


def test_producto_read_does_not_block_existing_data():
    """ProductoRead no debe tener validador de entrada que impida serializar registros existentes."""
    resp = ProductoRead(id=99, nombre="Legacy Item", precio_base="10.00", imagen_url=[])
    assert resp.id == 99
    assert resp.nombre == "Legacy Item"


# =====================================================================
# 3. Servicios Transaccionales y Relación N:N
# [Consigna TP6 - Parte A, incisos b y d & Conclusiones Esperadas]:
# Lógica transaccional de Producto, borrado lógico y asociación N:N con Categoria
# =====================================================================

def test_service_crear_producto_persists_entity(session: Session):
    """Verifica que crear_producto persista la entidad con imagen_url JSON y disponible=True."""
    data = ProductoCreate(
        nombre="Monitor Gamer 144Hz",
        descripcion="Panel IPS 1ms",
        precio_base="320.00",
        imagen_url=["https://example.com/monitor1.jpg", "https://example.com/monitor2.jpg"],
    )
    producto = services.crear_producto(session, data)

    assert producto.id is not None
    assert producto.id > 0
    assert producto.nombre == "Monitor Gamer 144Hz"
    assert producto.precio_base == "320.00"
    assert producto.imagen_url == [
        "https://example.com/monitor1.jpg",
        "https://example.com/monitor2.jpg",
    ]
    assert producto.disponible is True

    db_entity = session.get(Producto, producto.id)
    assert db_entity is not None
    assert db_entity.nombre == "Monitor Gamer 144Hz"
    assert len(db_entity.imagen_url) == 2


def test_service_crear_producto_duplicate_name_raises(session: Session):
    """Verifica que crear_producto rechace nombres duplicados con ValueError."""
    data1 = ProductoCreate(nombre="Mouse Inalámbrico", precio_base="25.00", imagen_url=[])
    services.crear_producto(session, data1)

    data2 = ProductoCreate(nombre="Mouse Inalámbrico", precio_base="30.00", imagen_url=[])
    with pytest.raises(ValueError, match="Producto duplicado"):
        services.crear_producto(session, data2)


def test_service_obtener_producto_por_id_success_and_not_found(session: Session):
    """Verifica consulta por ID y lanzamiento de excepción de dominio cuando no existe."""
    data = ProductoCreate(nombre="Teclado Mecánico", precio_base="80.00", imagen_url=[])
    creado = services.crear_producto(session, data)

    obtenido = services.obtener_producto_por_id(session, creado.id)
    assert obtenido.id == creado.id
    assert obtenido.nombre == "Teclado Mecánico"
    assert obtenido.categorias == []

    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.obtener_producto_por_id(session, 9999)


def test_service_listar_productos_pagination(session: Session):
    """Verifica que listar_productos respete el orden, skip y limit."""
    for i in range(5):
        services.crear_producto(
            session,
            ProductoCreate(nombre=f"Item {i}", precio_base=f"{10 * (i + 1)}.00", imagen_url=[]),
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
            descripcion="Mid Tower",
            precio_base="90.00",
            imagen_url=["https://example.com/case.jpg"],
        ),
    )

    update_dto = ProductoUpdate(precio_base="105.00")
    actualizado = services.actualizar_producto(session, creado.id, update_dto)

    assert actualizado.precio_base == "105.00"
    assert actualizado.nombre == "Gabinete ATX"
    assert actualizado.imagen_url == ["https://example.com/case.jpg"]


def test_service_actualizar_producto_duplicate_name_raises(session: Session):
    """Verifica que actualizar al nombre de otro producto existente lance ValueError."""
    services.crear_producto(session, ProductoCreate(nombre="Disco SSD", precio_base="50.00", imagen_url=[]))
    p2 = services.crear_producto(session, ProductoCreate(nombre="Disco HDD", precio_base="30.00", imagen_url=[]))

    update_conflict = ProductoUpdate(nombre="Disco SSD")
    with pytest.raises(ValueError, match="Producto duplicado"):
        services.actualizar_producto(session, p2.id, update_conflict)


def test_service_actualizar_producto_not_found_raises(session: Session):
    """Verifica que actualizar un ID inexistente lance ValueError."""
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.actualizar_producto(
            session, 9999, ProductoUpdate(precio_base="50.00")
        )


def test_service_eliminar_producto_logical_deletion(session: Session):
    """Verifica que eliminar_producto aplique borrado lógico (disponible=False) en BD."""
    creado = services.crear_producto(
        session, ProductoCreate(nombre="Fuente 600W", precio_base="65.00", imagen_url=[])
    )
    assert creado.disponible is True

    eliminado = services.eliminar_producto(session, creado.id)
    assert eliminado.disponible is False

    en_bd = session.get(Producto, creado.id)
    assert en_bd is not None
    assert en_bd.disponible is False


def test_service_eliminar_producto_not_found_raises(session: Session):
    """Verifica que eliminar un ID inexistente lance ValueError."""
    with pytest.raises(ValueError, match="Producto no encontrado"):
        services.eliminar_producto(session, 9999)


def test_service_asociar_y_desasociar_categoria(session: Session):
    """Verifica la vinculación y desvinculación N:N entre Producto y Categoria en services."""
    prod = services.crear_producto(
        session, ProductoCreate(nombre="Notebook Pro", precio_base="1200.00", imagen_url=[])
    )
    cat1 = categoria_services.crear(
        session, CategoriaCreate(nombre="Computación", descripcion="Equipos portátiles")
    )
    cat2 = categoria_services.crear(
        session, CategoriaCreate(nombre="Ofertas", descripcion="Promociones")
    )

    vinculado = services.asociar_categoria(session, prod.id, cat1.id)
    assert len(vinculado.categorias) == 1
    assert vinculado.categorias[0].nombre == "Computación"

    vinculado2 = services.asociar_categoria(session, prod.id, cat2.id)
    assert len(vinculado2.categorias) == 2

    # Vínculo duplicado debe lanzar ValueError
    with pytest.raises(ValueError, match="duplicado"):
        services.asociar_categoria(session, prod.id, cat1.id)

    # Desasociar primera categoría
    services.desasociar_categoria(session, prod.id, cat1.id)
    actualizado = services.obtener_producto_por_id(session, prod.id)
    assert len(actualizado.categorias) == 1
    assert actualizado.categorias[0].id == cat2.id

    # Desasociar vínculo ya inexistente debe lanzar ValueError
    with pytest.raises(ValueError, match="no encontrada"):
        services.desasociar_categoria(session, prod.id, cat1.id)


# =====================================================================
# 4. Endpoints HTTP / Sociable Tests
# [Consigna TP6 - Parte A, inciso d & Rúbrica Backend]:
# Integración HTTP de endpoints CRUD y gestión de asociaciones N:N (/productos/{id}/categorias/{cat_id})
# =====================================================================

def test_api_create_producto_null_nombre_returns_422(client: TestClient):
    """Garantiza que un nombre nulo devuelva HTTP 422 y NUNCA un crash HTTP 500."""
    response = client.post("/productos/", json={"nombre": None, "precio_base": "100.00"})
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data


def test_api_create_producto_spaces_nombre_returns_422(client: TestClient):
    """Garantiza que un nombre de solo espacios devuelva HTTP 422."""
    response = client.post("/productos/", json={"nombre": "   ", "precio_base": "100.00"})
    assert response.status_code == 422
    assert "El nombre no puede estar vacío o contener solo espacios" in str(response.json())


def test_api_create_producto_sanitizes_nombre_in_response(client: TestClient):
    """Garantiza que un alta válida normalice el nombre y devuelva HTTP 201 Created."""
    response = client.post(
        "/productos/",
        json={"nombre": "  Teclado Mecanico RGB  ", "precio_base": "120.00", "imagen_url": []},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["nombre"] == "Teclado Mecanico RGB"
    assert body["precio_base"] == "120.00"


def test_api_crear_producto_success(client: TestClient):
    """POST /productos/ retorna HTTP 201 Created y esquema ProductoRead."""
    payload = {
        "nombre": "Placa de Video RTX 4060",
        "descripcion": "8GB GDDR6",
        "precio_base": "450.00",
        "imagen_url": ["https://example.com/rtx4060.png"],
        "disponible": True,
    }
    response = client.post("/productos/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["nombre"] == "Placa de Video RTX 4060"
    assert body["precio_base"] == "450.00"
    assert body["imagen_url"] == ["https://example.com/rtx4060.png"]
    assert body["disponible"] is True


def test_api_crear_producto_duplicate_returns_409(client: TestClient):
    """POST /productos/ con nombre duplicado retorna HTTP 409 Conflict."""
    payload = {"nombre": "Auricular USB", "precio_base": "35.00", "imagen_url": []}
    res1 = client.post("/productos/", json=payload)
    assert res1.status_code == 201

    res2 = client.post("/productos/", json=payload)
    assert res2.status_code == 409
    body = res2.json()
    assert "Producto duplicado" in body["detail"]


def test_api_detalle_producto_200_and_404(client: TestClient):
    """GET /productos/{id} retorna 200 con categorias incluidas y 404 para inexistente."""
    res_crear = client.post(
        "/productos/", json={"nombre": "Hub USB-C", "precio_base": "22.00", "imagen_url": []}
    )
    prod_id = res_crear.json()["id"]

    res_get = client.get(f"/productos/{prod_id}")
    assert res_get.status_code == 200
    body = res_get.json()
    assert body["nombre"] == "Hub USB-C"
    assert body["categorias"] == []

    res_404 = client.get("/productos/99999")
    assert res_404.status_code == 404
    assert "Producto no encontrado" in res_404.json()["detail"]


def test_api_listar_productos_pagination(client: TestClient):
    """GET /productos/ retorna 200 y array paginado."""
    for i in range(3):
        client.post(
            "/productos/",
            json={"nombre": f"Accesorio {i}", "precio_base": "15.00", "imagen_url": []},
        )

    res = client.get("/productos/?skip=0&limit=2")
    assert res.status_code == 200
    items = res.json()
    assert isinstance(items, list)
    assert len(items) == 2


def test_api_actualizar_producto_200_and_404(client: TestClient):
    """PUT /productos/{id} actualiza campos parciales y retorna 200, o 404 si no existe."""
    res_crear = client.post(
        "/productos/", json={"nombre": "Micrófono", "precio_base": "60.00", "imagen_url": []}
    )
    prod_id = res_crear.json()["id"]

    res_put = client.put(
        f"/productos/{prod_id}",
        json={"precio_base": "75.00", "descripcion": "Condensador"},
    )
    assert res_put.status_code == 200
    assert res_put.json()["precio_base"] == "75.00"
    assert res_put.json()["descripcion"] == "Condensador"
    assert res_put.json()["nombre"] == "Micrófono"

    res_put_404 = client.put("/productos/99999", json={"precio_base": "10.00"})
    assert res_put_404.status_code == 404


def test_api_actualizar_producto_duplicate_returns_409(client: TestClient):
    """PUT /productos/{id} con nombre colisionante retorna HTTP 409 Conflict."""
    client.post("/productos/", json={"nombre": "Cámara Web A", "precio_base": "50.00", "imagen_url": []})
    res_b = client.post("/productos/", json={"nombre": "Cámara Web B", "precio_base": "55.00", "imagen_url": []})
    id_b = res_b.json()["id"]

    res_put = client.put(f"/productos/{id_b}", json={"nombre": "Cámara Web A"})
    assert res_put.status_code == 409
    assert "Producto duplicado" in res_put.json()["detail"]


def test_api_eliminar_producto_204_and_404(client: TestClient):
    """DELETE /productos/{id} retorna 204 No Content sin cuerpo y marca disponible=False."""
    res_crear = client.post(
        "/productos/", json={"nombre": "Cable DisplayPort", "precio_base": "18.00", "imagen_url": []}
    )
    prod_id = res_crear.json()["id"]

    res_del = client.delete(f"/productos/{prod_id}")
    assert res_del.status_code == 204
    assert res_del.text == ""

    res_get = client.get(f"/productos/{prod_id}")
    assert res_get.status_code == 200
    assert res_get.json()["disponible"] is False

    res_del_404 = client.delete("/productos/99999")
    assert res_del_404.status_code == 404
    assert "Producto no encontrado" in res_del_404.json()["detail"]


def test_api_asociar_y_desasociar_categoria_n_a_n(client: TestClient):
    """Verifica los endpoints POST y DELETE /productos/{id}/categorias/{cat_id} y casos de error 404/409."""
    res_prod = client.post(
        "/productos/",
        json={
            "nombre": "Smartwatch Deportivo",
            "descripcion": "GPS integrado y resistencia al agua",
            "precio_base": "199.99",
            "imagen_url": ["https://example.com/watch.jpg"],
        },
    )
    assert res_prod.status_code == 201
    prod_id = res_prod.json()["id"]

    res_cat1 = client.post(
        "/categorias/",
        json={"nombre": "Wearables", "descripcion": "Relojes y bandas inteligentes"},
    )
    assert res_cat1.status_code == 201
    cat1_id = res_cat1.json()["id"]

    res_cat2 = client.post(
        "/categorias/",
        json={"nombre": "Deportes", "descripcion": "Equipamiento deportivo"},
    )
    assert res_cat2.status_code == 201
    cat2_id = res_cat2.json()["id"]

    # Asociar categoría 1 y categoría 2
    res_assoc1 = client.post(f"/productos/{prod_id}/categorias/{cat1_id}")
    assert res_assoc1.status_code in (200, 201)
    assert len(res_assoc1.json()["categorias"]) == 1
    assert res_assoc1.json()["categorias"][0]["nombre"] == "Wearables"

    res_assoc2 = client.post(f"/productos/{prod_id}/categorias/{cat2_id}")
    assert res_assoc2.status_code in (200, 201)
    assert len(res_assoc2.json()["categorias"]) == 2

    # Asociar categoría ya vinculada -> 409 Conflict
    res_dup = client.post(f"/productos/{prod_id}/categorias/{cat1_id}")
    assert res_dup.status_code == 409

    # Asociar con producto o categoría inexistente -> 404 Not Found
    assert client.post(f"/productos/99999/categorias/{cat1_id}").status_code == 404
    assert client.post(f"/productos/{prod_id}/categorias/99999").status_code == 404

    # Consultar GET /productos/{id} y verificar categorías anidadas
    res_detail = client.get(f"/productos/{prod_id}")
    assert res_detail.status_code == 200
    nombres_cats = {c["nombre"] for c in res_detail.json()["categorias"]}
    assert nombres_cats == {"Wearables", "Deportes"}

    # Desasociar categoría 1 -> 204 No Content
    res_unassoc = client.delete(f"/productos/{prod_id}/categorias/{cat1_id}")
    assert res_unassoc.status_code == 204

    # Verificar que solo queda categoría 2
    res_after = client.get(f"/productos/{prod_id}")
    assert len(res_after.json()["categorias"]) == 1
    assert res_after.json()["categorias"][0]["id"] == cat2_id

    # Desasociar vínculo ya eliminado -> 404 Not Found
    assert client.delete(f"/productos/{prod_id}/categorias/{cat1_id}").status_code == 404
