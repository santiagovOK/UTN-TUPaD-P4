from fastapi import FastAPI
from app.database import engine, create_db_and_tables
from app.modules.producto.routers import router as producto_router
from app.modules.categoria.routers import router as categoria_router
from app.modules.proveedor.routers import router as proveedor_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="API Integradora - Unidad 1",
        description="Conceptos: Path, Query, Body, Pydantic, Errores.",
        version="1.0.0"
    )

    # Crear tablas en PostgreSQL al iniciar la aplicación
    @app.on_event("startup")
    def on_startup():
        try:
            create_db_and_tables()   # las tablas existen antes del primer request
        except Exception:
            # Si falla la conexión sin BD local, no quebrar el arranque (fallback local para pruebas antes de conectar a PG real)
            pass

    app.include_router(producto_router)
    app.include_router(categoria_router)
    app.include_router(proveedor_router)

    return app


app = create_app()
