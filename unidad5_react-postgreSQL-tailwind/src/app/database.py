import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
ENV_FILE_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH)

# Obtener URL de conexión estrictamente desde el entorno (evita credenciales hardcodeadas)
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "Error crítico: La variable de entorno DATABASE_URL no está configurada.\n"
    )
# Engine que traduce Python - SQL y gestiona el pool de conexiones
engine = create_engine(
    DATABASE_URL,
    echo=True,  # registra cada query SQL en consola (solo desarrollo)
)


def create_db_and_tables():
    """Crea las tablas desde los metadatos SQLModel existentes."""
    SQLModel.metadata.bind = engine
    SQLModel.metadata.create_all(engine)


def get_session():
    """Generador de sesiones con context manager — una sesión por request."""
    with Session(engine) as session:
        yield session
