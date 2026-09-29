from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_db_and_tables
from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Gestor de Productos - Unidad 6",
        description="Gestor de Productos con SQLModel y PostgreSQL (Arquitectura en capas).",
        version="1.0.0",
    )

    # Configuración de CORS para permitir la comunicación con el frontend (React + Vite)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Crear tablas en PostgreSQL al iniciar la aplicación
    @app.on_event("startup")
    def on_startup():
        try:
            create_db_and_tables()
        except Exception:
            # Fallback seguro para pruebas unitarias sin conexión directa a PostgreSQL
            pass

    app.include_router(producto_router)
    app.include_router(categoria_router)

    return app


app = create_app()
