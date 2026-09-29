import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from fastapi.testclient import TestClient

from app.main import app
from app.database import get_session


@pytest.fixture(name="session")
def session_fixture():
    """Provee una sesión SQLModel aislada en memoria SQLite para pruebas de servicios."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(autouse=True)
def override_get_session():
    """Garantiza aislamiento total para requests HTTP ejecutados via TestClient.

    Cada test recibe un motor SQLite en memoria nuevo, impidiendo colisiones
    por duplicados o efectos colaterales entre pruebas consecutivas.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)

    def get_session_override():
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_session_override
    yield
    app.dependency_overrides.clear()


@pytest.fixture(name="client")
def client_fixture():
    """Provee un TestClient de FastAPI listo para consumir la app con sesión aislada."""
    return TestClient(app)
