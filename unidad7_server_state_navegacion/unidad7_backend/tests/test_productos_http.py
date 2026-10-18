"""Suite de pruebas automatizadas que valida la suite productos.http.

Ejecuta secuencialmente las 5 secciones de peticiones definidas en
unidad7_backend/productos.http utilizando un TestClient de FastAPI
con base de datos SQLite en memoria aislada.
"""

import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    # Motor SQLite en memoria aislado para la suite de pruebas
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_suite_productos_http_completa(client: TestClient):
    """Ejecuta en secuencia exacta cada solicitud documentada en productos.http."""

    # --------------------------------------------------------------------------
    # 0. Health Check
    # --------------------------------------------------------------------------
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

    # --------------------------------------------------------------------------
    # SECCIÓN 1: CRUD Y BÚSQUEDA PAGINADA DE CATEGORÍAS
    # --------------------------------------------------------------------------
    # 1.1 Alta de Categoría 1: Hamburguesas
    res = client.post("/categorias/", json={
        "nombre": "Hamburguesas",
        "descripcion": "Hamburguesas artesanales gourmet con medallón casero"
    })
    assert res.status_code == 201
    cat1 = res.json()
    assert cat1["id"] == 1
    assert cat1["nombre"] == "Hamburguesas"

    # 1.2 Alta de Categoría 2: Bebidas
    res = client.post("/categorias/", json={
        "nombre": "Bebidas",
        "descripcion": "Cervezas artesanales, gaseosas y bebidas refrescantes"
    })
    assert res.status_code == 201
    cat2 = res.json()
    assert cat2["id"] == 2

    # 1.3 Alta de Categoría 3: Postres
    res = client.post("/categorias/", json={
        "nombre": "Postres",
        "descripcion": "Postres artesanales, tortas y helados"
    })
    assert res.status_code == 201
    cat3 = res.json()
    assert cat3["id"] == 3

    # 1.4 Alta de Categoría Temporal 4: Categoría Temporal
    res = client.post("/categorias/", json={
        "nombre": "Categoría Temporal",
        "descripcion": "Categoría para demostración de borrado físico permanente"
    })
    assert res.status_code == 201
    cat4 = res.json()
    assert cat4["id"] == 4

    # 1.5 Listado paginado general
    res = client.get("/categorias/?offset=0&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4

    # 1.6 Búsqueda dinámica parcial por nombre
    res = client.get("/categorias/?search=Ham")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Hamburguesas"

    # 1.7 Consulta de detalle por ID
    res = client.get("/categorias/1")
    assert res.status_code == 200
    assert res.json()["nombre"] == "Hamburguesas"

    # 1.8 Actualización total (PUT)
    res = client.put("/categorias/1", json={
        "nombre": "Hamburguesas Gourmet",
        "descripcion": "Hamburguesas artesanales con panes brioche y carnes maduradas"
    })
    assert res.status_code == 200
    assert res.json()["nombre"] == "Hamburguesas Gourmet"

    # 1.9 Actualización parcial (PATCH) con exclude_unset
    res = client.patch("/categorias/1", json={
        "descripcion": "Selección premium de hamburguesas caseras y combinaciones gourmet"
    })
    assert res.status_code == 200
    assert res.json()["nombre"] == "Hamburguesas Gourmet"
    assert "Selección premium" in res.json()["descripcion"]

    # 1.10 Baja lógica de Categoría 3
    res = client.delete("/categorias/3")
    assert res.status_code == 204

    # 1.11 Verificación de baja lógica: 404
    res = client.get("/categorias/3")
    assert res.status_code == 404

    # 1.12 Borrado físico de Categoría 4
    res = client.delete("/categorias/4?hard=true")
    assert res.status_code == 204

    # 1.13 Verificación de borrado físico: 404
    res = client.get("/categorias/4")
    assert res.status_code == 404

    # --------------------------------------------------------------------------
    # SECCIÓN 2: CRUD Y FILTRADO DINÁMICO DE PRODUCTOS
    # --------------------------------------------------------------------------
    # 2.1 Alta de Producto 1: Hamburguesa Doble Cheddar
    res = client.post("/productos/", json={
        "nombre": "Hamburguesa Doble Cheddar",
        "descripcion": "Doble medallón de carne 120g, queso cheddar fundido y panceta ahumada",
        "precio_base": 12500.0,
        "imagenes_url": [
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd"
        ],
        "disponible": True
    })
    assert res.status_code == 201
    prod1 = res.json()
    assert prod1["id"] == 1
    assert prod1["nombre"] == "Hamburguesa Doble Cheddar"

    # 2.2 Alta de Producto 2: Pinta Cerveza IPA
    res = client.post("/productos/", json={
        "nombre": "Pinta Cerveza IPA",
        "descripcion": "Cerveza artesanal India Pale Ale de 500cc",
        "precio_base": 4500.0,
        "imagenes_url": [
            "https://images.unsplash.com/photo-1535958636474-b021ee887b13"
        ],
        "disponible": True
    })
    assert res.status_code == 201
    prod2 = res.json()
    assert prod2["id"] == 2

    # 2.3 Alta de Producto 3: Cheesecake de Frutos Rojos
    res = client.post("/productos/", json={
        "nombre": "Cheesecake de Frutos Rojos",
        "descripcion": "Clásico pastel de queso",
        "precio_base": 5800.0,
        "imagenes_url": [
            "https://images.unsplash.com/photo-1533134242443-d4fd215305ad"
        ],
        "disponible": True
    })
    assert res.status_code == 201
    prod3 = res.json()
    assert prod3["id"] == 3

    # 2.4 Alta de Producto Temporal 4: Producto Temporal
    res = client.post("/productos/", json={
        "nombre": "Producto Temporal",
        "descripcion": "Producto destinado a demostrar borrado físico permanente",
        "precio_base": 1000.0,
        "imagenes_url": [],
        "disponible": True
    })
    assert res.status_code == 201
    prod4 = res.json()
    assert prod4["id"] == 4

    # 2.5 Listado paginado general de Productos
    res = client.get("/productos/?offset=0&limit=10")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 4
    assert len(data["items"]) == 4

    # 2.6 Filtro dinámico por nombre parcial
    res = client.get("/productos/?nombre=Cheddar")
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    assert data["items"][0]["nombre"] == "Hamburguesa Doble Cheddar"

    # 2.7 Filtro dinámico por disponibilidad
    res = client.get("/productos/?disponible=true")
    assert res.status_code == 200
    assert res.json()["total"] == 4

    # 2.8 Detalle de Producto por ID con categorías anidadas
    res = client.get("/productos/1")
    assert res.status_code == 200
    assert res.json()["nombre"] == "Hamburguesa Doble Cheddar"
    assert res.json()["categorias"] == []

    # 2.9 Actualización total (PUT) de Producto
    res = client.put("/productos/1", json={
        "nombre": "Hamburguesa Doble Cheddar Premium",
        "descripcion": "Doble medallón 150g, triple queso cheddar, panceta crocante y salsa barbacoa",
        "precio_base": 13900.0,
        "imagenes_url": [
            "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
            "https://images.unsplash.com/photo-1586190848861-99aa4a171e90"
        ],
        "disponible": True
    })
    assert res.status_code == 200
    assert res.json()["nombre"] == "Hamburguesa Doble Cheddar Premium"

    # 2.10 Actualización parcial (PATCH) de Producto
    res = client.patch("/productos/1", json={
        "precio_base": 14500.0
    })
    assert res.status_code == 200
    assert res.json()["precio_base"] == 14500.0
    assert res.json()["nombre"] == "Hamburguesa Doble Cheddar Premium"

    # 2.11 Borrado físico de Producto 4
    res = client.delete("/productos/4?hard=true")
    assert res.status_code == 204

    # 2.12 Verificación de borrado físico: 404
    res = client.get("/productos/4")
    assert res.status_code == 404

    # --------------------------------------------------------------------------
    # SECCIÓN 3: GESTIÓN DE LA RELACIÓN MUCHOS A MUCHOS (N:N)
    # --------------------------------------------------------------------------
    # 3.1 Asignar Categoría 1 a Producto 1 como principal
    res = client.post("/productos/categorias/asignar", json={
        "producto_id": 1,
        "categoria_id": 1,
        "es_principal": True
    })
    assert res.status_code == 201
    assert res.json() == {
        "producto_id": 1,
        "categoria_id": 1,
        "es_principal": True
    }

    # 3.2 Asignar Categoría 2 a Producto 1 como secundaria
    res = client.post("/productos/categorias/asignar", json={
        "producto_id": 1,
        "categoria_id": 2,
        "es_principal": False
    })
    assert res.status_code == 201
    assert res.json() == {
        "producto_id": 1,
        "categoria_id": 2,
        "es_principal": False
    }

    # 3.3 Asignar Categoría 2 a Producto 2 mediante alias RESTful
    res = client.post("/productos/2/categorias/2?es_principal=true")
    assert res.status_code == 201
    prod2_updated = res.json()
    assert prod2_updated["id"] == 2
    assert any(c["id"] == 2 for c in prod2_updated["categorias"])

    # 3.4 Verificación de Producto 1 con categorías anidadas
    res = client.get("/productos/1")
    assert res.status_code == 200
    prod1_data = res.json()
    cat_ids = [c["id"] for c in prod1_data["categorias"]]
    assert 1 in cat_ids
    assert 2 in cat_ids
    assert len(cat_ids) == 2

    # 3.5 Filtrar productos pertenecientes a Categoría 1
    res = client.get("/productos/?categoria_id=1")
    assert res.status_code == 200
    assert any(p["id"] == 1 for p in res.json()["items"])

    # 3.6 Filtrar productos pertenecientes a Categoría 2
    res = client.get("/productos/?categoria_id=2")
    assert res.status_code == 200
    cat2_pids = [p["id"] for p in res.json()["items"]]
    assert 1 in cat2_pids
    assert 2 in cat2_pids

    # 3.7 Desasociar Categoría 2 de Producto 1
    res = client.delete("/productos/1/categorias/2")
    assert res.status_code == 204

    # 3.8 Verificación de desvinculación
    res = client.get("/productos/1")
    assert res.status_code == 200
    cat_ids_after = [c["id"] for c in res.json()["categorias"]]
    assert cat_ids_after == [1]

    # --------------------------------------------------------------------------
    # SECCIÓN 4: BAJA LÓGICA DE PRODUCTO (SOFT DELETE)
    # --------------------------------------------------------------------------
    # 4.1 Baja lógica de Producto 3
    res = client.delete("/productos/3")
    assert res.status_code == 204

    # 4.2 Verificación de baja lógica: 404
    res = client.get("/productos/3")
    assert res.status_code == 404

    # 4.3 Verificación de listado: excluido
    res = client.get("/productos/?offset=0&limit=10")
    assert res.status_code == 200
    active_ids = [p["id"] for p in res.json()["items"]]
    assert 3 not in active_ids

    # --------------------------------------------------------------------------
    # SECCIÓN 5: CASOS DE ERROR SEMÁNTICOS Y REGLAS DE NEGOCIO (404, 409, 422)
    # --------------------------------------------------------------------------
    # 5.1 404 Not Found — Consulta de producto inexistente
    res = client.get("/productos/9999")
    assert res.status_code == 404

    # 5.2 404 Not Found — Consulta de categoría inexistente
    res = client.get("/categorias/9999")
    assert res.status_code == 404

    # 5.3 404 Not Found — Asignar vínculo N:N con categoría inexistente
    res = client.post("/productos/categorias/asignar", json={
        "producto_id": 1,
        "categoria_id": 9999,
        "es_principal": False
    })
    assert res.status_code == 404

    # 5.4 404 Not Found — Asignar vínculo N:N con producto inexistente
    res = client.post("/productos/categorias/asignar", json={
        "producto_id": 9999,
        "categoria_id": 1,
        "es_principal": False
    })
    assert res.status_code == 404

    # 5.5 404 Not Found — Desvincular relación N:N inexistente
    res = client.delete("/productos/1/categorias/9999")
    assert res.status_code == 404

    # 5.6 409 Conflict — Nombre de categoría duplicado
    res = client.post("/categorias/", json={
        "nombre": "Hamburguesas Gourmet",
        "descripcion": "Intento de alta duplicada de categoría"
    })
    assert res.status_code == 409

    # 5.7 409 Conflict — Nombre de producto duplicado
    res = client.post("/productos/", json={
        "nombre": "Pinta Cerveza IPA",
        "descripcion": "Intento de alta duplicada de producto",
        "precio_base": 5000.0,
        "imagenes_url": [],
        "disponible": True
    })
    assert res.status_code == 409

    # 5.8 422 Unprocessable Entity — Validación de Producto
    res = client.post("/productos/", json={
        "nombre": "   ",
        "precio_base": -50.0,
        "imagenes_url": [],
        "disponible": True
    })
    assert res.status_code == 422

    # 5.9 422 Unprocessable Entity — Validación de Categoría
    res = client.post("/categorias/", json={
        "nombre": ""
    })
    assert res.status_code == 422

    # 5.10 422 Unprocessable Entity — Limit fuera de rango
    res = client.get("/productos/?limit=0")
    assert res.status_code == 422

    # 5.11 422 Unprocessable Entity — Ruta no positiva
    res = client.get("/categorias/0")
    assert res.status_code == 422


def test_archivo_productos_http_validez_sintactica():
    """Verifica que el archivo productos.http existe, no está vacío y contiene todas las secciones."""
    http_file = Path("productos.http")
    if not http_file.exists():
        http_file = Path("unidad7_backend/productos.http")
    assert http_file.exists(), "El archivo productos.http debe existir en el backend"
    content = http_file.read_text(encoding="utf-8")
    assert "@baseUrl" in content
    assert "@contentType" in content
    assert "SECCIÓN 1: CRUD Y BÚSQUEDA PAGINADA DE CATEGORÍAS" in content
    assert "SECCIÓN 2: CRUD Y FILTRADO DINÁMICO DE PRODUCTOS" in content
    assert "SECCIÓN 3: GESTIÓN DE LA RELACIÓN MUCHOS A MUCHOS" in content
    assert "SECCIÓN 4: BAJA LÓGICA DE PRODUCTO" in content
    assert "SECCIÓN 5: CASOS DE ERROR SEMÁNTICOS" in content


def test_archivo_productos_http_ejecucion_dinamica(client: TestClient):
    """Parsea productos.http y ejecuta cada una de las solicitudes HTTP contra TestClient."""
    import json
    import re

    http_file = Path("productos.http")
    if not http_file.exists():
        http_file = Path("unidad7_backend/productos.http")
    content = http_file.read_text(encoding="utf-8")

    vars_dict = {}
    for line in content.splitlines():
        m = re.match(r"^@(\w+)\s*=\s*(.+)$", line.strip())
        if m:
            vars_dict[m.group(1)] = m.group(2)

    blocks = re.split(r"\n###\s+", content)
    executed_count = 0

    for block in blocks:
        lines = [l.rstrip() for l in block.splitlines()]
        req_idx = None
        for i, line in enumerate(lines):
            if re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+", line):
                req_idx = i
                break

        if req_idx is None:
            continue

        req_line = lines[req_idx]
        for k, v in vars_dict.items():
            req_line = req_line.replace(f"{{{{{k}}}}}", v)

        parts = req_line.split()
        method = parts[0]
        raw_url = parts[1]
        url = re.sub(r"^https?://[^/]+", "", raw_url)

        headers = {}
        body_lines = []
        in_body = False

        for line in lines[req_idx + 1:]:
            if in_body:
                body_lines.append(line)
            elif line.strip() == "":
                in_body = True
            else:
                m = re.match(r"^([^:]+):\s*(.+)$", line)
                if m:
                    hk = m.group(1).strip()
                    hv = m.group(2).strip()
                    for vk, vv in vars_dict.items():
                        hv = hv.replace(f"{{{{{vk}}}}}", vv)
                    headers[hk] = hv

        body_str = "\n".join(body_lines).strip()
        kwargs = {"headers": headers}
        if body_str:
            kwargs["json"] = json.loads(body_str)

        res = client.request(method, url, **kwargs)
        executed_count += 1
        assert res.status_code in [200, 201, 204, 404, 409, 422], (
            f"Fallo en {method} {url}: status {res.status_code}, respuesta {res.text}"
        )

    assert executed_count >= 40, f"Se esperaban al menos 40 solicitudes ejecutadas, pero fueron {executed_count}"
