# Backend — API Gestor de Productos y Categorías (FastAPI + SQLModel)

Backend para el Trabajo Práctico de la **Unidad 6** de **Programación IV (TUPaD - UTN)**. Construido con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), y preparado para persistencia en **PostgreSQL** con fallback transparente a **SQLite**.

Expone una API REST con arquitectura modular por dominio (`categoria`, `producto`), soporte completo de CORS para frontend en `http://localhost:5173`, y documentación interactiva automática en Swagger UI.

---

## Tecnologías y Librerías

- **FastAPI:** Framework web moderno y asíncrono de alto rendimiento para APIs REST en Python.
- **SQLModel / SQLAlchemy:** ORM que unifica modelos de base de datos relacionales y esquemas de validación de datos.
- **Pydantic:** Validación estricta de tipos de datos de entrada y serialización de respuestas.
- **Uvicorn / FastAPI CLI:** Servidor ASGI para ejecución en desarrollo con recarga en caliente (`reload`).
- **PostgreSQL / SQLite:** Soporte de base de datos relacional con integridad referencial.
- **Pytest + HTTPX:** Suite de pruebas automatizadas y cliente de pruebas de integración.

---

## Requisitos Previos

- **Python:** Versión 3.10, 3.11, 3.12 o 3.13+.
- **pip:** Gestor de paquetes de Python.
- Gestor de entornos virtuales (`venv`).

---

## Inicialización y Ejecución Individual

### 1. Crear y activar el entorno virtual

Desde el directorio `unidad6_backend/`:

```bash
# Crear entorno virtual
python -m venv .venv

# Activar en Linux / macOS:
source .venv/bin/activate

# Activar en Windows (PowerShell / CMD):
.venv\Scripts\activate
```

### 2. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos (`.env`)

Copiar el archivo de ejemplo `.env.example` a `.env`:

```bash
cp .env.example .env
```

El backend permite operar indistintamente con PostgreSQL o SQLite mediante la variable `DATABASE_URL`:

- **Opción A — SQLite Local (Recomendado para desarrollo rápido sin servicios externos):**
  ```env
  DATABASE_URL=sqlite:///./dev.db
  ```
  *(O `sqlite:///:memory:` para base de datos volátil en memoria).*

- **Opción B — PostgreSQL:**
  ```env
  DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp6_relaciones
  ```

> **Nota sobre pruebas (`pytest`):**  
> La suite de tests automatizada (`tests/conftest.py`) utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** completamente aislado por sesión de test, por lo que las pruebas no requieren ninguna base de datos externa en ejecución.

---

## Servidor de Desarrollo

Para iniciar el backend en modo desarrollo:

```bash
fastapi dev app/main.py
```

*Alternativas equivalentes:*
```bash
# Mediante el módulo de Python:
python -m fastapi dev app/main.py

# Directamente con Uvicorn:
uvicorn app.main:app --reload --port 8000
```

El servidor quedará disponible en:
👉 **http://localhost:8000**

---

## Documentación Interactiva de la API

FastAPI genera automáticamente documentación interactiva basada en OpenAPI:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (permite probar cada endpoint en vivo).
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 🧪 Pruebas Automatizadas y Manuales

### Pruebas Unitarias e Integración (`pytest`)

Ejecutar la suite completa con:

```bash
pytest -v
```

Todas las pruebas se ejecutan contra SQLite en memoria con rollback y aislamiento automático.

### Pruebas con REST Client (`.http`)

Para validar los endpoints sin interfaz gráfica (tal como solicita la consigna para el módulo de Productos), se proporcionan archivos `.http` ejecutables con la extensión **REST Client** de VS Code / Cursor o herramientas como JetBrains HTTP Client.

---

## 📁 Estructura del Código Fuente

```text
unidad6_backend/
├── requirements.txt            # Lista de dependencias del backend Python
├── pytest.ini                  # Configuración de pruebas para pytest
├── .env.example                # Plantilla de variables de entorno
├── app/
│   ├── main.py                 # Factoría FastAPI, middlewares de CORS y montaje de routers
│   ├── database.py             # Configuración del motor de base de datos y sesiones SQLModel
│   ├── models/                 # Modelos de base de datos persistibles (SQLModel table=True)
│   │   └── producto.py         # Modelos relacionales de persistencia
│   └── modules/                # Arquitectura modular por dominio de negocio
│       ├── categoria/          # Módulo de Categorías (consumido por Frontend)
│       │   ├── routers.py      # Endpoints REST (GET, POST, PUT, DELETE)
│       │   ├── schemas.py      # DTOs y esquemas Pydantic (Create, Read, Update)
│       │   └── services.py     # Lógica de persistencia y reglas de negocio
│       └── producto/           # Módulo de Productos (demostrado vía REST Client)
│           ├── routers.py      # Endpoints REST de Producto y relaciones
│           ├── schemas.py      # DTOs Pydantic de Producto
│           ├── services.py     # Lógica de consulta relacional y persistencia
│           └── validators.py   # Validaciones de reglas de negocio
└── tests/                      # Suite de pruebas automatizadas
    ├── conftest.py             # Fixtures de base de datos aislada en memoria
    ├── test_fase1_database_and_models.py
    ├── test_fase2_tarea2_1_validators.py
    └── test_fase2_tarea2_2_services.py
```
