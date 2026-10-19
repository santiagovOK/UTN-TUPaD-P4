# Backend — API Food Store (FastAPI + SQLModel)

Backend para el Trabajo Práctico de la **Unidad 7** de **Programación IV (TUPaD - UTN)**. Construido con **FastAPI**, **SQLModel** (SQLAlchemy + Pydantic), y preparado para persistencia en **PostgreSQL** con fallback transparente a **SQLite**.

Expone una API REST para las entidades `unidad_medida` (catálogo seed de solo lectura), `ingrediente`, `categoria`, `producto` y las asociaciones `producto_categoria` y `producto_ingrediente`. El seed carga las 7 unidades oficiales al iniciar la aplicación. Ofrece paginación y filtros, baja lógica o física según el endpoint y documentación interactiva en Swagger UI; `/health/` y `/health/db` permiten comprobar la aplicación y la conexión a la base de datos.

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
> La suite de tests automatizada (`tests/test_productos_http.py`) utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** completamente aislado por sesión de test con `StaticPool`, por lo que las pruebas no requieren ninguna base de datos externa en ejecución.
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

## 🔌 Resumen de Endpoints

Todas las rutas se sirven desde `http://localhost:8000`. Las listas paginadas responden con `total` e `items`; por defecto excluyen registros inactivos cuando admiten baja lógica. Los errores de validación de entrada usan `422`; los recursos inexistentes, `404`; y los conflictos de unicidad o reglas de negocio, `409`, según corresponda.

### Categorías

| Método | Ruta | Descripción / semántica |
|---|---|---|
| `POST` | `/categorias/` | Crear categoría (`201`); conflicto de nombre `409`. |
| `GET` | `/categorias/` | Listado paginado con búsqueda y filtros. |
| `GET` | `/categorias/{categoria_id}` | Obtener categoría activa (`404` si no existe o está inactiva). |
| `PUT` / `PATCH` | `/categorias/{categoria_id}` | Actualización completa / parcial de categoría activa. |
| `DELETE` | `/categorias/{categoria_id}` | Baja lógica por defecto; `?hard=true` solicita eliminación física. Valida asociaciones y conflictos de negocio (`409`). |
| `GET` | `/categorias/{categoria_id}/productos` | Productos activos asociados a una categoría. |

### Productos y relación muchos a muchos

| Método | Ruta | Descripción / semántica |
|---|---|---|
| `POST` | `/productos/` | Crear producto (`201`); `categoria_ids` es obligatorio y requiere al menos una categoría (`RN-19`); `ingredientes` es opcional. |
| `GET` | `/productos/` | Listado paginado con filtros. |
| `GET` | `/productos/{producto_id}` | Obtener producto por ID (`404` si no existe o está inactivo). |
| `PUT` | `/productos/{producto_id}` | Actualización completa; reemplaza las asociaciones de categorías e ingredientes cuando se envían. |
| `DELETE` | `/productos/{producto_id}` | Baja lógica con borrado en cascada de asociaciones (`RN-14`). |
| `GET` | `/productos/{producto_id}/categorias` | Categorías relacionadas con el producto. |
| `GET` | `/productos/{producto_id}/ingredientes` | Ingredientes relacionados con el producto. |

### Ingredientes

| Método | Ruta | Descripción / semántica |
|---|---|---|
| `POST` | `/ingredientes/` | Crear ingrediente; unidad inexistente `404`, nombre duplicado `409`, creado `201`. |
| `GET` | `/ingredientes/` | Listado paginado; admite filtro `nombre` (o alias `search`) e `incluir_inactivos`. |
| `GET` | `/ingredientes/{ingrediente_id}` | Obtener ingrediente activo (`404` si no existe o está inactivo). |
| `PUT` | `/ingredientes/{ingrediente_id}` | Actualización completa; conflictos de unicidad `409`. |
| `DELETE` | `/ingredientes/{ingrediente_id}` | Baja lógica o física; `409` si tiene productos asociados. |

### Unidades de medida

| Método | Ruta | Descripción / semántica |
|---|---|---|
| `GET` | `/unidades-medida/` | Listar el catálogo oficial precargado de unidades (`total` e `items`). |
| `GET` | `/unidades-medida/{unidad_id}` | Obtener unidad por ID (`404` si no existe). |

### Salud

| Método | Ruta | Descripción / semántica |
|---|---|---|
| `GET` | `/` | Health check con estado, servicio, versión y unidad académica. |
| `GET` | `/health/` | Comprueba que la aplicación está activa (`{"status":"ok"}`). |
| `GET` | `/health/db` | Ejecuta `SELECT 1` para comprobar conectividad con la base de datos. |

---

## 🧪 Pruebas Automatizadas y Demostración REST Client

### Pruebas Unitarias e Integración (`pytest`)

Ejecutar la suite completa con:

```bash
pytest -v
```

Todas las pruebas se ejecutan contra SQLite en memoria con aislamiento automático por fixture.

### Pruebas con REST Client (`productos.http`)

El archivo `productos.http` puede ejecutarse con **REST Client** de VS Code / Cursor o JetBrains HTTP Client. Organiza las peticiones en cinco secciones:
1. **Health, Unidades de Medida e Ingredientes:** diagnóstico, consulta del catálogo seed de unidades y CRUD de ingredientes.
2. **Categorías:** ciclo CRUD, listado paginado, filtros y bajas.
3. **Productos con Relaciones N:M :** ciclo CRUD; `categoria_ids` obligatorio al crear e ingredientes opcionales; reemplazo total de asociaciones en `PUT`.
4. **Consultas Relacionales Inversas N:M :** productos por categoría y categorías e ingredientes por producto (`HU-07`).
5. **Errores Semánticos 404/409/422:** casos de recursos inexistentes, conflictos de negocio y entradas inválidas.

Las peticiones contemplan códigos semánticos como `200 OK`, `201 Created`, `204 No Content`, `404 Not Found`, `409 Conflict` y `422 Unprocessable Entity`.

---

## 📁 Estructura del Código Fuente

```text
unidad7_backend/
├── requirements.txt            # Lista de dependencias del backend Python
├── pytest.ini                  # Configuración de pruebas para pytest
├── .env.example                # Plantilla de variables de entorno (PostgreSQL / SQLite)
├── productos.http              # Peticiones REST Client (salud, catálogo, relaciones e ingredientes)
├── app/
│   ├── main.py                 # FastAPI, health checks, CORS y montaje de routers
│   ├── database.py             # Configuración del motor de base de datos y sesiones SQLModel
│   ├── seed.py                 # Precarga del catálogo oficial de unidades de medida
│   ├── models/
│   │   ├── categoria.py        # Entidad Categoria
│   │   ├── producto.py         # Entidad Producto y tabla intermedia ProductoCategoria
│   │   ├── ingrediente.py      # Entidad Ingrediente
│   │   └── unidad_medida.py    # Entidad UnidadMedida
│   └── modules/
│       ├── categoria/          # Rutas, esquemas y servicios de categorías
│       ├── producto/           # Rutas, esquemas, servicios y validadores de productos
│       ├── ingrediente/        # Rutas, esquemas y servicios de ingredientes
│       └── unidad_medida/      # Rutas, esquemas y servicios de solo lectura
└── tests/                      # Suite de pruebas automatizadas
    ├── __init__.py
    └── test_productos_http.py  # Suite integral HTTP
```
## 🧪 Pruebas Automatizadas y Demostración REST Client

### Pruebas Unitarias e Integración (`pytest`)

Ejecutar la suite completa con:

```bash
pytest -v
```

Todas las pruebas se ejecutan contra SQLite en memoria con aislamiento automático por fixture.

