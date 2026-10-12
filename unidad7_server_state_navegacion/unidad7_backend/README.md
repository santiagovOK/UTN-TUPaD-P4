# Backend — API Food Store (FastAPI + SQLModel)

Backend para el Trabajo Práctico de la **Unidad 7** de **Programación IV (TUPaD - UTN)**. Construido con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), y preparado para persistencia en **PostgreSQL** con fallback transparente a **SQLite**.

Expone una API REST optimizada para el catálogo de alimentos (`categoria`, `producto`, `productocategoria`), con paginación (`offset`, `limit`) y metadatos de conteo, soporte completo de CORS para frontend en `http://localhost:5173`, y documentación interactiva automática en Swagger UI.

> **Nota sobre Modalidad de Entrega y Ejecución Unificada:**  
> Según las pautas de evaluación de la Unidad 7, el backend se entrega como un archivo comprimido independiente:  
> **`Varela_Santiago_TPI_unidad7_backend.zip`** (excluyendo estrictamente el entorno virtual `.venv/`, `__pycache__/`, bases locales `*.db` y cachés temporales).  
>
> Asimismo, el proyecto Full Stack completo puede clonarse y ejecutarse desde el repositorio en GitHub:  
> **[https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)**

---

## 🛠️ Tecnologías y Librerías

- **FastAPI:** Framework web moderno y asíncrono de alto rendimiento para APIs REST en Python.
- **SQLModel / SQLAlchemy:** ORM que unifica modelos de base de datos relacionales y esquemas de validación de datos.
- **Pydantic:** Validación estricta de tipos de datos de entrada y serialización de respuestas mediante DTOs.
- **Uvicorn / FastAPI CLI:** Servidor ASGI para ejecución en desarrollo con recarga en caliente (`reload`).
- **PostgreSQL / SQLite:** Soporte de base de datos relacional con integridad referencial y claves foráneas.
- **Pytest + HTTPX:** Suite de pruebas automatizadas y cliente de pruebas de integración con SQLite en memoria.

---

## 📋 Requisitos Previos

- **Python:** Versión 3.10, 3.11, 3.12 o 3.13+.
- **pip:** Gestor de paquetes de Python.
- Gestor de entornos virtuales (`venv`).

---

## 🚀 Inicialización y Ejecución Individual

### 1. Crear y activar el entorno virtual

Desde el directorio `unidad7_backend/`:

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

- **Opción A — PostgreSQL (Entorno principal de producción y entrega):**
  ```env
  DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp7_server_state
  ```

- **Opción B — SQLite con persistencia en disco (Fallback local / inspección en DBeaver):**
  ```env
  DATABASE_URL=sqlite:///./dev.db
  ```
  *(Genera `dev.db` en el directorio de `unidad7_backend` para inspección visual).*

- **Opción C — SQLite en memoria (Pruebas volátiles en RAM):**
  ```env
  DATABASE_URL=sqlite:///:memory:
  ```
  *(100% en memoria mediante `StaticPool`. No escribe archivos en disco y se reinicia en cada arranque).*

> **Nota sobre pruebas (`pytest`):**  
> La suite de tests automatizada (`tests/conftest.py`) utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** completamente aislado por sesión de test, por lo que las pruebas no requieren ninguna base de datos externa en ejecución.

---

## 💻 Servidor de Desarrollo

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

## 📖 Documentación Interactiva de la API

FastAPI genera automáticamente documentación interactiva basada en OpenAPI:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs) (permite probar cada endpoint en vivo).
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc).

---

## 🧪 Pruebas Automatizadas y Demostración REST Client

### Pruebas Unitarias e Integración (`pytest`)

Ejecutar la suite completa con:

```bash
pytest -v
```

Todas las pruebas se ejecutan contra SQLite en memoria con aislamiento automático por fixture.

### Pruebas con REST Client (`productos.http`)

Para validar los endpoints sin interfaz gráfica (tal como solicita la consigna para los módulos de `Producto` y `ProductoCategoria`), se proporciona el archivo unificado `productos.http` ejecutable con la extensión **REST Client** de VS Code / Cursor o JetBrains HTTP Client. Incluye:
1. Ciclo de vida completo de Categorías (`POST`, `GET` paginado, `GET /{id}`, `PUT`, borrado lógico y borrado físico).
2. Ciclo de vida completo de Productos (`POST`, `GET` paginado, `GET /{id}`, `PUT`, borrado lógico).
3. Relación muchos a muchos (`POST /productos/{id}/categorias/{cat_id}` y `DELETE /productos/{id}/categorias/{cat_id}`).
4. Cobertura de códigos de estado semánticos (`200 OK`, `201 Created`, `204 No Content`, `404 Not Found`, `409 Conflict`, `422 Unprocessable Entity`).

---

## 📁 Estructura del Código Fuente

```text
unidad7_backend/
├── requirements.txt            # Lista de dependencias del backend Python
├── pytest.ini                  # Configuración de pruebas para pytest
├── .env.example                # Plantilla de variables de entorno (PostgreSQL / SQLite)
├── productos.http              # Archivo unificado de pruebas REST Client (CRUD y relación N:N)
├── app/
│   ├── main.py                 # Factoría FastAPI, middleware CORS y montaje de routers
│   ├── database.py             # Configuración del motor de base de datos y sesiones SQLModel
│   ├── models/                 # Modelos de base de datos persistibles (SQLModel table=True)
│   │   ├── categoria.py        # Entidad Categoria (id, nombre UQ, descripcion nullable, auditoría)
│   │   └── producto.py         # Entidad Producto y tabla intermedia ProductoCategoria (con es_principal)
│   └── modules/                # Arquitectura modular por dominio de negocio (Models-Schemas-Service-Router)
│       ├── categoria/          # Módulo de Categorías (consumido por Frontend)
│       │   ├── routers.py      # Endpoints REST (GET, POST, PUT, DELETE) con validación Query
│       │   ├── schemas.py      # DTOs Pydantic (Create, Read, Update, PaginatedResponse)
│       │   └── services.py     # Lógica de persistencia, paginación y conteo atómico SQL
│       └── producto/           # Módulo de Productos (demostrado vía REST Client)
│           ├── routers.py      # Endpoints REST de Producto y relaciones N:N
│           ├── schemas.py      # DTOs Pydantic de Producto y ProductoReadConCategorias
│           ├── services.py     # Lógica de consulta relacional, Eager Loading y servicios N:N
│           └── validators.py   # Validaciones de reglas de negocio
└── tests/                      # Suite de pruebas automatizadas organizada por dominio
    ├── conftest.py             # Fixtures de base de datos aislada en memoria (StaticPool)
    ├── test_categoria.py       # Pruebas de dominio Categoría (DDL, servicios y endpoints)
    └── test_producto.py        # Pruebas de dominio Producto y relación N:N
```
