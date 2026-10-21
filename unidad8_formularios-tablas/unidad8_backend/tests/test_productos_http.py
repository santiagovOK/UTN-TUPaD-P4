"""Pruebas integrales de la suite REST Client del backend.

Base heredada del TP7; identidad y documentación adaptadas al TP8.
"""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

import app.database as database
import app.main as main
from app.database import get_session
from app.main import app


SECTION_HEADERS = (
    "SECCIÓN 0: HEALTH, UNIDADES DE MEDIDA E INGREDIENTES",
    "SECCIÓN 1: CRUD Y BÚSQUEDA PAGINADA DE CATEGORÍAS",
    "SECCIÓN 2: CRUD Y FILTRADO DINÁMICO DE PRODUCTOS CON RELACIONES N:M",
    "SECCIÓN 3: CONSULTAS RELACIONALES INVERSAS N:M",
    "SECCIÓN 4: ERRORES SEMÁNTICOS Y REGLAS DE NEGOCIO (404, 409, 422)",
)
REQUEST_RE = re.compile(r"^(GET|POST|PUT|PATCH|DELETE)\s+(\S+)")
VARIABLE_RE = re.compile(r"^@(\w+)\s*=\s*(.*?)\s*$")


@pytest.fixture(name="client")
def client_fixture(monkeypatch):
    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    monkeypatch.setattr(database, "engine", test_engine)
    monkeypatch.setattr(main, "engine", test_engine)

    def get_session_override():
        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        test_engine.dispose()


def _find_http_file() -> Path:
    tests_dir = Path(__file__).resolve().parent
    candidates = (
        tests_dir.parent / "productos.http",
        Path("productos.http").resolve(),
        Path("unidad8_backend/productos.http").resolve(),
        *Path.cwd().resolve().rglob("productos.http"),
    )
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    searched = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"No se encontró productos.http. Rutas examinadas: {searched}")


def _parse_http_file() -> list[dict]:
    content = _find_http_file().read_text(encoding="utf-8")
    lines = content.splitlines()
    variables: dict[str, str] = {}
    for line in lines:
        match = VARIABLE_RE.match(line.strip())
        if match:
            variables[match.group(1)] = match.group(2)

    def interpolate(value: str) -> str:
        return re.sub(
            r"{{(\w+)}}",
            lambda match: variables.get(match.group(1), match.group(0)),
            value,
        )

    requests: list[dict] = []
    section = ""
    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if line.startswith("###"):
            heading = line[3:].strip()
            if heading.startswith("SECCIÓN"):
                section = heading
            index += 1
            continue
        match = REQUEST_RE.match(line)
        if not match:
            index += 1
            continue

        method, raw_url = match.groups()
        line_number = index + 1
        headers: dict[str, str] = {}
        body_lines: list[str] = []
        index += 1
        in_body = False
        while index < len(lines):
            current = lines[index]
            stripped = current.strip()
            if stripped.startswith("###") or REQUEST_RE.match(stripped):
                break
            if not in_body:
                if not stripped:
                    in_body = True
                elif ":" in current:
                    key, value = current.split(":", 1)
                    headers[key.strip()] = interpolate(value.strip())
            elif stripped:
                body_lines.append(current)
            index += 1

        url = interpolate(raw_url)
        url = re.sub(r"^https?://[^/]+", "", url)
        body_text = "\n".join(body_lines).strip()
        try:
            body = json.loads(body_text) if body_text else None
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON at { _find_http_file() }:{line_number}: {exc}") from exc
        requests.append({
            "line_number": line_number,
            "section": section,
            "method": method,
            "url": url,
            "headers": headers,
            "body_text": body_text,
            "body": body,
        })
    return requests


def test_archivo_productos_http_validez_sintactica():
    path = _find_http_file()
    content = path.read_text(encoding="utf-8")
    assert re.search(r"^@baseUrl\s*=", content, re.MULTILINE)
    assert re.search(r"^@contentType\s*=", content, re.MULTILINE)
    for section in SECTION_HEADERS:
        assert section in content
    requests = _parse_http_file()
    assert len(requests) == 56
    assert all(request["method"] and request["url"] for request in requests)


def test_suite_productos_http_ejecucion_dinamica(client: TestClient):
    requests = _parse_http_file()
    assert len(requests) == 56
    allowed_statuses = {200, 201, 204, 404, 409, 422}
    category_two_delete_statuses: list[int] = []

    for request in requests:
        response = client.request(
            request["method"], request["url"],
            headers=request["headers"], json=request["body"],
        )
        label = f"{request['method']} {request['url']} (línea {request['line_number']})"
        assert response.status_code != 500, f"{label}: {response.text}"
        assert response.status_code in allowed_statuses, (
            f"{label}: {response.status_code} {response.text}"
        )

        if request["url"] == "/health/":
            assert response.status_code == 200
            assert response.json() == {"status": "ok"}
        elif request["url"] == "/health/db":
            assert response.status_code == 200
            assert response.json() == {"status": "ok", "database": "connected"}
        elif request["url"] == "/unidades-medida/":
            assert response.status_code == 200
            assert len(response.json()["items"]) == 7
        if request["method"] == "POST" and request["url"] == "/categorias/" \
                and request["body"].get("nombre") == "Hamburguesas Gourmet":
            assert response.status_code == 409, f"{label}: esperaba 409"
        if request["method"] == "POST" and request["url"] == "/ingredientes/" \
                and request["body"].get("nombre") == "Carne vacuna" \
                and request["body"].get("descripcion") is None:
            assert response.status_code == 409, f"{label}: esperaba 409"
        if request["method"] == "POST" and request["url"] == "/productos/" \
                and request["body"].get("nombre") in {"Sin categoría", "   "}:
            assert response.status_code == 422, f"{label}: esperaba 422"
        if request["method"] == "GET" and request["url"] == "/productos/?limit=0":
            assert response.status_code == 422, f"{label}: esperaba 422"
        if request["method"] == "GET" and request["url"] == "/categorias/0":
            assert response.status_code == 422, f"{label}: esperaba 422"
        if request["method"] == "POST" and request["url"] in {
            "/categorias/", "/ingredientes/", "/productos/"
        } and response.status_code == 201:
            assert response.json().get("id") is not None, f"{label}: falta id"

        if request["method"] == "DELETE" and request["url"] == "/categorias/2":
            category_two_delete_statuses.append(response.status_code)
        if request["method"] == "GET" and "9999" in request["url"]:
            assert response.status_code == 404, f"{label}: esperaba 404"

    assert category_two_delete_statuses == [409, 204]


def test_suite_productos_http_cobertura_secciones(client: TestClient):
    del client  # El fixture también garantiza el entorno aislado para esta prueba.
    requests = _parse_http_file()
    counts = {section: sum(request["section"] == section for request in requests)
              for section in SECTION_HEADERS}
    minimums = (10, 10, 10, 5, 15)
    for section, minimum in zip(SECTION_HEADERS, minimums):
        assert counts[section] >= minimum, f"{section}: {counts[section]} < {minimum}"
