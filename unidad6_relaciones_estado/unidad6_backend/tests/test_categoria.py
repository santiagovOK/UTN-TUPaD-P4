"""
Pruebas integrales del dominio Categoria y tabla intermedia ProductoCategoria (Tarea 3.1).

Organización por secciones:
1. Metadatos DDL y Modelos SQLModel (Categoria y ProductoCategoria).
2. Servicios Transaccionales (app.modules.categoria.services con SQLModel Session).
3. Endpoints HTTP / Sociable Tests (Integración con FastAPI TestClient).
"""

from sqlmodel import SQLModel, Session
from fastapi.testclient import TestClient

from app.models.categoria import Categoria
from app.models.producto import ProductoCategoria
from app.modules.categoria.schemas import CategoriaCreate, CategoriaRead, CategoriaUpdate
from app.modules.categoria import services


# =====================================================================
# 1. Metadatos DDL y Modelos SQLModel (Categoria y ProductoCategoria)
# =====================================================================

def test_categoria_table_metadata():
    """Verifica que la entidad Categoria esté registrada como tabla en SQLModel.metadata con su PK id."""
    assert Categoria.__tablename__ == "categoria"
    assert "categoria" in SQLModel.metadata.tables, "La tabla 'categoria' debe estar en SQLModel.metadata"
    table = SQLModel.metadata.tables["categoria"]
    assert "id" in table.columns, "La tabla 'categoria' debe contener la columna 'id'"
    assert table.columns["id"].primary_key, "La columna 'id' debe ser Primary Key"
    assert "nombre" in table.columns
    assert "descripcion" in table.columns
    assert "activo" in table.columns


def test_producto_categoria_table_metadata():
    """Verifica que ProductoCategoria tenga claves primarias compuestas y claves foráneas hacia producto.id y categoria.id."""
    assert ProductoCategoria.__tablename__ == "productocategoria"
    assert "productocategoria" in SQLModel.metadata.tables, "La tabla 'productocategoria' debe estar en SQLModel.metadata"
    table = SQLModel.metadata.tables["productocategoria"]

    assert "producto_id" in table.columns
    assert "categoria_id" in table.columns
    assert table.columns["producto_id"].primary_key, "producto_id debe formar parte de la clave primaria compuesta"
    assert table.columns["categoria_id"].primary_key, "categoria_id debe formar parte de la clave primaria compuesta"

    fk_targets = {
        fk.target_fullname
        for col in table.columns.values()
        for fk in col.foreign_keys
    }
    assert "producto.id" in fk_targets, "Debe existir clave foránea hacia 'producto.id'"
    assert "categoria.id" in fk_targets, "Debe existir clave foránea hacia 'categoria.id'"


def test_categoria_model_defaults_and_schemas():
    """Verifica valores por defecto del modelo Categoria y contratos de schemas DTO."""
    cat = Categoria(nombre="Periféricos")
    assert cat.id is None
    assert cat.nombre == "Periféricos"
    assert cat.descripcion is None
    assert cat.activo is True

    dto_create = CategoriaCreate(nombre="Audio", descripcion="Equipos de sonido")
    assert dto_create.nombre == "Audio"
    assert dto_create.activo is True

    dto_update = CategoriaUpdate(descripcion="Nueva descripción")
    assert dto_update.nombre is None
    assert dto_update.descripcion == "Nueva descripción"

    dto_read = CategoriaRead(id=1, nombre="Redes", descripcion="Switches y routers", activo=True)
    assert dto_read.id == 1


# =====================================================================
# 2. Servicios Transaccionales (app.modules.categoria.services)
# =====================================================================

def test_service_crear_categoria_persists_entity(session: Session):
    """Verifica que services.crear persista la categoría en la BD y asigne ID autoincremental."""
    data = CategoriaCreate(
        nombre="Electrónica",
        descripcion="Dispositivos electrónicos de consumo",
        activo=True,
    )
    creada = services.crear(session, data)

    assert creada.id is not None
    assert creada.id > 0
    assert creada.nombre == "Electrónica"
    assert creada.descripcion == "Dispositivos electrónicos de consumo"
    assert creada.activo is True

    en_bd = session.get(Categoria, creada.id)
    assert en_bd is not None
    assert en_bd.nombre == "Electrónica"


def test_service_obtener_todas_pagination(session: Session):
    """Verifica que services.obtener_todas retorne la lista paginada respetando skip y limit."""
    for i in range(5):
        services.crear(
            session,
            CategoriaCreate(nombre=f"Categoría {i}", descripcion=f"Descripción {i}"),
        )

    pagina = services.obtener_todas(session, skip=1, limit=2)
    assert len(pagina) == 2
    assert pagina[0].nombre == "Categoría 1"
    assert pagina[1].nombre == "Categoría 2"


def test_service_obtener_por_id_found_and_not_found(session: Session):
    """Verifica que services.obtener_por_id retorne la entidad existente o None si no existe."""
    creada = services.crear(
        session, CategoriaCreate(nombre="Almacenamiento", descripcion="SSD y HDD")
    )

    encontrada = services.obtener_por_id(session, creada.id)
    assert encontrada is not None
    assert encontrada.id == creada.id
    assert encontrada.nombre == "Almacenamiento"

    inexistente = services.obtener_por_id(session, 9999)
    assert inexistente is None


def test_service_actualizar_total_found_and_not_found(session: Session):
    """Verifica que services.actualizar_total modifique los campos de una categoría existente o retorne None."""
    creada = services.crear(
        session,
        CategoriaCreate(nombre="Monitores", descripcion="Pantallas LED", activo=True),
    )

    nuevos_datos = CategoriaCreate(
        nombre="Monitores Gamer",
        descripcion="Pantallas IPS y OLED de alta tasa de refresco",
        activo=False,
    )
    actualizada = services.actualizar_total(session, creada.id, nuevos_datos)

    assert actualizada is not None
    assert actualizada.id == creada.id
    assert actualizada.nombre == "Monitores Gamer"
    assert actualizada.descripcion == "Pantallas IPS y OLED de alta tasa de refresco"
    assert actualizada.activo is False

    inexistente = services.actualizar_total(session, 9999, nuevos_datos)
    assert inexistente is None


def test_service_desactivar_found_and_not_found(session: Session):
    """Verifica que services.desactivar aplique borrado lógico (activo=False) o retorne None."""
    creada = services.crear(
        session, CategoriaCreate(nombre="Cables", descripcion="Conectividad", activo=True)
    )
    assert creada.activo is True

    desactivada = services.desactivar(session, creada.id)
    assert desactivada is not None
    assert desactivada.activo is False

    en_bd = session.get(Categoria, creada.id)
    assert en_bd is not None
    assert en_bd.activo is False

    inexistente = services.desactivar(session, 9999)
    assert inexistente is None


def test_service_eliminar_found_and_not_found(session: Session):
    """Verifica que services.eliminar borre físicamente la categoría de la BD y retorne booleano."""
    creada = services.crear(
        session, CategoriaCreate(nombre="Temporal", descripcion="Para borrar")
    )
    cat_id = creada.id

    resultado_ok = services.eliminar(session, cat_id)
    assert resultado_ok is True
    assert session.get(Categoria, cat_id) is None

    resultado_inexistente = services.eliminar(session, 9999)
    assert resultado_inexistente is False


# =====================================================================
# 3. Endpoints HTTP / Sociable Tests (client: TestClient)
# =====================================================================

def test_api_alta_categoria_201(client: TestClient):
    """POST /categorias/ crea una categoría en la BD y retorna HTTP 201 Created."""
    payload = {
        "nombre": "Componentes PC",
        "descripcion": "Placas madre, procesadores y memorias",
        "activo": True,
    }
    response = client.post("/categorias/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["nombre"] == "Componentes PC"
    assert body["descripcion"] == "Placas madre, procesadores y memorias"
    assert body["activo"] is True


def test_api_listar_categorias_200_and_pagination(client: TestClient):
    """GET /categorias/ retorna HTTP 200 OK con el listado de categorías paginado."""
    for i in range(3):
        client.post(
            "/categorias/",
            json={"nombre": f"Rubro {i}", "descripcion": f"Detalle {i}"},
        )

    response = client.get("/categorias/?skip=0&limit=2")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) == 2
    assert items[0]["nombre"] == "Rubro 0"
    assert items[1]["nombre"] == "Rubro 1"


def test_api_detalle_categoria_200_and_404(client: TestClient):
    """GET /categorias/{id} retorna HTTP 200 para categoría existente y 404 si no existe."""
    res_post = client.post(
        "/categorias/",
        json={"nombre": "Impresoras", "descripcion": "Láser e inyección de tinta"},
    )
    cat_id = res_post.json()["id"]

    res_get = client.get(f"/categorias/{cat_id}")
    assert res_get.status_code == 200
    assert res_get.json()["nombre"] == "Impresoras"

    res_404 = client.get("/categorias/99999")
    assert res_404.status_code == 404
    assert "Categoría no encontrada" in res_404.json()["detail"]


def test_api_actualizar_categoria_200_and_404(client: TestClient):
    """PUT /categorias/{id} actualiza la categoría con HTTP 200 OK o retorna 404 si no existe."""
    res_post = client.post(
        "/categorias/",
        json={"nombre": "Sillas", "descripcion": "Oficina", "activo": True},
    )
    cat_id = res_post.json()["id"]

    update_payload = {
        "nombre": "Sillas Ergonómicas",
        "descripcion": "Sillas gamer y de oficina",
        "activo": True,
    }
    res_put = client.put(f"/categorias/{cat_id}", json=update_payload)
    assert res_put.status_code == 200
    body = res_put.json()
    assert body["id"] == cat_id
    assert body["nombre"] == "Sillas Ergonómicas"
    assert body["descripcion"] == "Sillas gamer y de oficina"

    res_put_404 = client.put("/categorias/99999", json=update_payload)
    assert res_put_404.status_code == 404
    assert "Categoría no encontrada" in res_put_404.json()["detail"]


def test_api_desactivar_categoria_200_and_404(client: TestClient):
    """PUT /categorias/{id}/desactivar aplica baja lógica con HTTP 200 OK o retorna 404 si no existe."""
    res_post = client.post(
        "/categorias/",
        json={"nombre": "Proyectores", "descripcion": "Video proyectores"},
    )
    cat_id = res_post.json()["id"]

    res_desactivar = client.put(f"/categorias/{cat_id}/desactivar")
    assert res_desactivar.status_code == 200
    assert res_desactivar.json()["activo"] is False

    res_desactivar_404 = client.put("/categorias/99999/desactivar")
    assert res_desactivar_404.status_code == 404
    assert "Categoría no encontrada" in res_desactivar_404.json()["detail"]


def test_api_eliminar_categoria_204_and_404(client: TestClient):
    """DELETE /categorias/{id} elimina físicamente con HTTP 204 No Content o retorna 404 si no existe."""
    res_post = client.post(
        "/categorias/",
        json={"nombre": "Accesorios Obsoletos", "descripcion": "Disquetes"},
    )
    cat_id = res_post.json()["id"]

    res_del = client.delete(f"/categorias/{cat_id}")
    assert res_del.status_code == 204
    assert res_del.text == ""

    res_get_after = client.get(f"/categorias/{cat_id}")
    assert res_get_after.status_code == 404

    res_del_404 = client.delete("/categorias/99999")
    assert res_del_404.status_code == 404
    assert "Categoría no encontrada" in res_del_404.json()["detail"]
