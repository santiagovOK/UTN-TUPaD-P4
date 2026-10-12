import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

# Directorio raíz del módulo backend (unidad6_backend)
BACKEND_DIR = Path(__file__).resolve().parent.parent

# Cargar variables de entorno desde el archivo .env en la raíz de unidad6_backend
ENV_FILE_PATH = BACKEND_DIR / ".env"
if ENV_FILE_PATH.exists():
    load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)
else:
    load_dotenv(override=True)

# Obtener URL de conexión estrictamente desde el entorno (evita credenciales hardcodeadas)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Error crítico: La variable de entorno DATABASE_URL no está configurada.\n"
    )

# Configurar opciones de conexión según motor y modo:
# - Opción 1: PostgreSQL (producción / entrega) -> Pool estándar de SQLAlchemy.
# - Opción 2: SQLite en disco (dev.db) -> check_same_thread=False y ruta anclada a backend.
# - Opción 3: SQLite en memoria (:memory:) -> check_same_thread=False y StaticPool para compartir memoria entre requests.
extra_kwargs = {}

if DATABASE_URL.startswith("sqlite"):
    extra_kwargs["connect_args"] = {"check_same_thread": False}
    if ":memory:" in DATABASE_URL or DATABASE_URL == "sqlite://":
        from sqlalchemy.pool import StaticPool
        extra_kwargs["poolclass"] = StaticPool
    elif DATABASE_URL.startswith("sqlite:///./"):
        db_relative_name = DATABASE_URL[len("sqlite:///./") :]
        resolved_db_path = (BACKEND_DIR / db_relative_name).resolve()
        DATABASE_URL = f"sqlite:///{resolved_db_path}"

# Engine que traduce Python - SQL y gestiona el pool de conexiones
engine = create_engine(
    DATABASE_URL,
    echo=True,  # registra cada query SQL en consola (solo desarrollo)
    **extra_kwargs,
)


# [Consigna TP6 - Parte A, inciso b & Rúbrica Backend / Tarea 3.1]:
# Creación automática de tablas persistentes (categoria, producto, productocategoria) en la base de datos relacional.
def create_db_and_tables():
    """Crea las tablas desde los metadatos SQLModel existentes.

    Importa los modelos para que queden registrados en SQLModel.metadata antes de create_all.
    """
    from app.models.producto import Producto, ProductoCategoria  # noqa: F401
    from app.models.categoria import Categoria  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session():
    """Generador de sesiones con context manager — una sesión por request."""
    with Session(engine) as session:
        yield session
