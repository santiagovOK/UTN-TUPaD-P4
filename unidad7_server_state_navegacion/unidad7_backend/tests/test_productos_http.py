"""Pruebas integrales de la suite REST Client del backend."""

import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app


@pytest.fixture(name="client")
def client_fixture():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def _http_file() -> Path:
    path = Path("productos.http")
    return path if path.exists() else Path("unidad7_backend/productos.http")


def _execute_http_file(client: TestClient) -> int:
    content = _http_file().read_text(encoding="utf-8")
    variables = {m.group(1): m.group(2) for line in content.splitlines()
                 if (m := re.match(r"^@(\w+)\s*=\s*(.+)$", line.strip()))}
    blocks = re.split(r"\n###\s+", content)
    count = 0
    for block in blocks:
        lines = block.splitlines()
        request_index = next((i for i, line in enumerate(lines)
                              if re.match(r"^(GET|POST|PUT|PATCH|DELETE)\s+", line)), None)
        if request_index is None:
            continue
        request = lines[request_index]
        for key, value in variables.items():
            request = request.replace(f"{{{{{key}}}}}", value)
        method, raw_url = request.split()[:2]
        url = re.sub(r"^https?://[^/]+", "", raw_url)
        headers, body_lines, in_body = {}, [], False
        for line in lines[request_index + 1:]:
            if in_body:
                body_lines.append(line)
            elif not line.strip():
                in_body = True
            elif ":" in line:
                key, value = line.split(":", 1)
                headers[key.strip()] = value.strip()
        body = "\n".join(body_lines).strip()
        response = client.request(method, url, headers=headers, json=json.loads(body) if body else None)
        count += 1
        assert response.status_code in {200, 201, 204, 404, 409, 422}, (
            f"{method} {url}: {response.status_code} {response.text}"
        )
    return count


def test_suite_productos_http_completa(client: TestClient):
    assert _execute_http_file(client) >= 40


def test_archivo_productos_http_validez_sintactica():
    content = _http_file().read_text(encoding="utf-8")
    assert "@baseUrl" in content and "@contentType" in content
    for marker in (
        "SECCIÓN 0:", "SECCIÓN 1: CRUD Y BÚSQUEDA PAGINADA DE CATEGORÍAS",
        "SECCIÓN 2: CRUD Y FILTRADO DINÁMICO DE PRODUCTOS",
        "SECCIÓN 3: CONSULTAS RELACIONALES INVERSAS N:M",
        "SECCIÓN 4: ERRORES SEMÁNTICOS",
    ):
        assert marker in content
    assert len(re.findall(r"^(GET|POST|PUT|PATCH|DELETE)\s+", content, re.MULTILINE)) >= 40


def test_archivo_productos_http_ejecucion_dinamica(client: TestClient):
    assert _execute_http_file(client) >= 40
