"""Punto de entrada principal de la aplicación FastAPI — Food Store API.

[Consigna TP7 - Arquitectura Backend Models-Schemas-Service-Router]
[RN-05 - CORS Habilitado: Comunicación con frontend React / Vite]
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session

from app.database import create_db_and_tables, engine
from app.modules.categoria.routers import router as categoria_router
from app.modules.ingrediente.routers import router as ingrediente_router
from app.modules.producto.routers import router as producto_router
from app.modules.unidad_medida.routers import router as unidad_medida_router
from app.seed import seed_unidades_medida

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Ciclo de vida de la aplicación.

    Garantiza la materialización inicial de las tablas en la base de datos
    (CATEGORIA, PRODUCTO y la tabla asociativa PRODUCTO_CATEGORIA)
    al iniciar el servidor antes de recibir peticiones.
    """
    create_db_and_tables()
    with Session(engine) as session:
        seed_unidades_medida(session)
    yield


app = FastAPI(
    title="Food Store API — Unidad 7",
    description=(
        "API REST modular optimizada para el catálogo de alimentos (Categorías, "
        "Productos y relación asociativa N:N) con persistencia SQLModel, "
        "paginación, filtros dinámicos y soporte CORS para frontend React."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# [RN-05 - CORS Habilitado]: Orígenes permitidos del frontend React / Vite
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montaje de routers modulares
app.include_router(categoria_router)
app.include_router(producto_router)
app.include_router(unidad_medida_router)
app.include_router(ingrediente_router)


@app.get("/", tags=["Health"], summary="Comprobación de salud de la API")
def health_check() -> dict:
    """Endpoint raíz para comprobación de estado y conectividad básica."""
    return {
        "status": "healthy",
        "service": "Food Store API",
        "version": "1.0.0",
        "unit": "Unidad 7 — Integración Frontend-Backend y Estado del Servidor",
    }
