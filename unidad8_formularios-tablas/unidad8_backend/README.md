# Backend — API Food Store (FastAPI + SQLModel — Unidad 8)

Backend modular para el Trabajo Práctico de la **Unidad 8** de **Programación IV (TUPaD - UTN)**. Construido con **FastAPI** y **SQLModel** (SQLAlchemy + Pydantic), preparado para persistencia en **PostgreSQL** y **SQLite**.

---

## 📋 Alcance y Estado del Backend en la Unidad 8

El backend combina la arquitectura probada del catálogo de alimentos con la planificación de un nuevo subsistema transaccional:

1. **Catálogo de Alimentos (Implementado y Preservado):**  
   Módulos para `categoria`, `producto`, `ingrediente` y `unidad_medida` (catálogo seed inmutable de 7 unidades oficiales). Paginación `{ total, items }`, filtros dinámicos, baja lógica y validaciones de Pydantic.
2. **Módulo de Pedidos y DetallePedido (Planificado — Épica 2):**  
   Arquitectura formal *Models–Schemas–Repository–Unit of Work–Service–Router* para registrar ventas atómicas, congelar precios históricos de productos y gestionar estados (`PENDIENTE`, `CONFIRMADO`, `ENTREGADO`, `CANCELADO`). **No implementado en esta etapa documental.**

> **Modalidad de Entrega:**  
> Comprimido en **`Varela_Santiago_TPI_unidad8_backend.zip`** (excluyendo estrictamente entornos virtuales `.venv/`, `__pycache__/`, bases locales `.db`, temporales y cualquier carpeta `guidelines/`). Consulte [docs/resolucion_tp8.md](../docs/resolucion_tp8.md) para la estrategia detallada y la política de exclusión de bibliografía en los ZIPs de entrega.  
> Repositorio oficial: [https://github.com/santiagovOK/UTN-TUPaD-P4](https://github.com/santiagovOK/UTN-TUPaD-P4)  
> Antecedente histórico: [Directorio Unidad 7 en GitHub](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)

---

## 🛠️ Tecnologías y Librerías

- **FastAPI:** Framework moderno asíncrono para endpoints REST de alto rendimiento.
- **SQLModel / SQLAlchemy:** Definición declarativa de modelos de base de datos relacionales y queries tipadas.
- **Pydantic:** Validación estricta en esquemas DTO de entrada y serialización de salida.
- **Uvicorn / FastAPI CLI:** Servidor ASGI para desarrollo local con recarga en caliente (`reload`).
- **PostgreSQL / SQLite:** Motores de almacenamiento relacional con claves foráneas e integridad referencial.
- **Pytest + HTTPX:** Suite de pruebas automatizada con base de datos volátil aislada por test.

---

## 🚀 Inicialización y Ejecución Local

### 1. Entorno Virtual y Dependencias

Desde la carpeta `unidad8_backend/`:

```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
source .venv/bin/activate       # Linux / macOS
# .venv\Scripts\activate        # Windows

# Instalar librerías
pip install -r requirements.txt
```

### 2. Configuración de Base de Datos (`.env`)

Copiar el archivo de variables de entorno de ejemplo:

```bash
cp .env.example .env
```

Editar el archivo `.env` para especificar la variable `DATABASE_URL`.  
*Nota técnica: `app/database.py` exige esta variable y lanza un error crítico si no se encuentra configurada (no aplica fallbacks automáticos).*

- **Opción A — PostgreSQL (Entorno principal de desarrollo y persistencia relacional):**
  ```env
  DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp7_server_state
  ```
  *(El nombre de base `tp7_server_state` corresponde a la base de datos preexistente y no altera el funcionamiento del TP8).*
- **Opción B — SQLite en disco (Archivo local `dev.db`):**
  ```env
  DATABASE_URL=sqlite:///./dev.db
  ```
- **Opción C — SQLite en memoria (Volátil / RAM):**
  ```env
  DATABASE_URL=sqlite:///:memory:
  ```

### 3. Iniciar el Servidor de Desarrollo

```bash
fastapi dev app/main.py
# O bien: python -m fastapi dev app/main.py
# O bien: uvicorn app.main:app --reload --port 8000
```

- **Punto de Entrada:** [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Especificación OpenAPI (JSON):** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## 🌐 Catálogo de Endpoints REST

### 1. Diagnóstico y Salud del Servicio (Activo)

| Método | Ruta | Descripción | Código |
|---|---|---|---|
| `GET` | `/` | Comprobación de salud básica con nombre y unidad del servicio. | `200 OK` |
| `GET` | `/health/` | Health check simple para balanceadores o monitoreo. | `200 OK` |
| `GET` | `/health/db` | Comprobación real de conectividad ejecutando `SELECT 1`. | `200 OK` |

### 2. Categorías de Alimentos (Activo)

| Método | Ruta | Descripción | Código |
|---|---|---|---|
| `GET` | `/categorias/` | Listado paginado con búsqueda por nombre y total de coincidencias. | `200 OK` |
| `POST` | `/categorias/` | Alta de categoría con control de duplicados (insensible a mayúsculas). | `201 Created` / `409` |
| `GET` | `/categorias/{id}` | Detalle de categoría activa por ID. | `200 OK` / `404` |
| `PUT` | `/categorias/{id}` | Actualización completa de datos de la categoría. | `200 OK` / `404` / `409` |
| `PATCH`| `/categorias/{id}` | Modificación parcial de atributos. | `200 OK` / `404` / `409` |
| `DELETE`|`/categorias/{id}` | Baja lógica (impide eliminación si tiene productos asociados). | `204 No Content` / `409` |
| `GET` | `/categorias/{id}/productos` | Productos activos asociados a la categoría indicada. | `200 OK` / `404` |

### 3. Productos (Activo)

| Método | Ruta | Descripción | Código |
|---|---|---|---|
| `GET` | `/productos/` | Listado paginado con filtros dinámicos (nombre, disponible, categoría). | `200 OK` |
| `POST` | `/productos/` | Alta de producto con validación de precio >= 0 y categorías obligatorias. | `201 Created` / `404` / `422` |
| `GET` | `/productos/{id}` | Ficha de detalle con categorías e ingredientes asociados. | `200 OK` / `404` |
| `PUT` | `/productos/{id}` | Actualización completa con reemplazo de asociaciones. | `200 OK` / `404` / `422` |
| `PATCH`| `/productos/{id}` | Modificación parcial de campos básicos. | `200 OK` / `404` |
| `DELETE`|`/productos/{id}` | Baja lógica del producto. | `204 No Content` / `404` |
| `GET` | `/productos/{id}/categorias` | Categorías activas asociadas al producto. | `200 OK` / `404` |
| `GET` | `/productos/{id}/ingredientes`| Ingredientes activos asociados al producto. | `200 OK` / `404` |

### 4. Unidades de Medida e Ingredientes (Activo — Extensión Heredada del TP7)

| Método | Ruta | Descripción | Código |
|---|---|---|---|
| `GET` | `/unidades-medida/` | Catálogo de solo lectura con las 7 unidades de medida oficiales. | `200 OK` |
| `GET` | `/unidades-medida/{id}` | Consulta de unidad de medida por identificador. | `200 OK` / `404` |
| `GET` | `/ingredientes/` | Listado paginado de ingredientes con filtro por nombre. | `200 OK` |
| `POST` | `/ingredientes/` | Alta de ingrediente vinculando una unidad de medida existente. | `201 Created` / `404` / `409` |
| `GET` | `/ingredientes/{id}` | Detalle de ingrediente activo por ID. | `200 OK` / `404` |
| `PUT` | `/ingredientes/{id}` | Actualización de nombre, descripción y unidad de medida. | `200 OK` / `404` / `409` |
| `DELETE`|`/ingredientes/{id}` | Baja lógica (impide baja si está vinculado a productos). | `204 No Content` / `409` |

### 5. Pedidos y DetallePedido (⏳ Planificado — Pendiente Épica 2)

| Método | Ruta | Descripción | Estado |
|---|---|---|:---:|
| `GET` | `/pedidos/` | Listado de pedidos activos del sistema. | ⏳ Planificado |
| `GET` | `/pedidos/{id}` | Detalle de pedido con sus ítems y precios unitarios congelados. | ⏳ Planificado |
| `POST` | `/pedidos/` | Creación atómica de pedido y detalles con Unit of Work transaccional. | ⏳ Planificado |
| `PUT` | `/pedidos/{id}` | Actualización de estado (`PENDIENTE`, `CONFIRMADO`, `ENTREGADO`, `CANCELADO`). | ⏳ Planificado |
| `DELETE`|`/pedidos/{id}` | Borrado lógico del pedido (`204 No Content`). | ⏳ Planificado |

---

## 🧪 Pruebas Automatizadas y REST Client

### Pruebas Unitarias e Integración (`pytest`)

Ejecutar la suite de tests desde la raíz del proyecto o desde `unidad8_backend/`:

```bash
# Desde la raíz:
pnpm test:back

# O desde unidad8_backend/ (con .venv activo):
pytest
```

*La suite actual (`tests/test_productos_http.py`) evalúa 60 peticiones sobre una base SQLite en memoria con aislamiento `StaticPool`, validando las reglas de negocio del catálogo sin alterar bases locales.*

### Archivos de Solicitudes REST Client (`.http`)

- `unidad8_backend/productos.http`: Suite integral de solicitudes HTTP para probar el catálogo de alimentos directamente en VS Code o editores compatibles.
- `unidad8_backend/pedidos.http`: Suite de pruebas REST Client para el módulo de Pedidos (**planificada en tarea E2.5**).
