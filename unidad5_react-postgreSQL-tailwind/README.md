# Trabajo Práctico - Unidad 5 (FastAPI - Pydantic)

Siguiendo las [consignas](/docs/consignas.md), la realización de este trabajo parte de lo realizado en la [unidad anterior](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad4_FastApi). Allí dice "unidad 1", pero según lo que se solicita deduzco que es un error y hay que basarse en el práctico de la unidad 4

Resolución paso a paso de este trabajo en: [resolucion_tp5.md](/docs/resolucion_tp5.md).

---

## ✨ Estudiante

- Nombre: Varela, Santiago Octavio
- Email institucional: santiago.varela@tupad.utn.edu.ar

Repositorio donde podrán encontrar mis trabajos de Programación IV: https://github.com/santiagovOK/UTN-TUPaD-P4

---

## Inicialización

### Crear entorno virtual (.venv)

En directorio raíz del proyecto:

```bash
python -m venv .venv
```

### Activar entorno

Con el entorno virtual ya creado, activarlo:

```bash
source .venv/bin/activate
```

### Instalar dependencias

Con el entorno virtual activado, instalar los paquetes declarados en `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Configuración de Base de Datos (PostgreSQL / SQLite como Fallback)

El backend utiliza **SQLModel / SQLAlchemy**, lo que permite interactuar indistintamente con PostgreSQL o SQLite mediante la variable de entorno `DATABASE_URL`.

Cree un archivo `.env` en la raíz del proyecto (basado en `.env.example`):

1. **PostgreSQL (Entorno de producción / entrega):**
   ```env
   DATABASE_URL=postgresql+psycopg2://usuario:password@localhost:5432/tp5_react
   ```

2. **SQLite como Fallback Local (Pruebas y desarrollo sin PostgreSQL):**
   Si no se dispone de una instancia de PostgreSQL activa, se puede utilizar SQLite sin alterar el código de la aplicación:
   ```env
   # Base de datos en archivo local (persistente, inspeccionable con DBeaver):
   DATABASE_URL=sqlite:///./dev.db

   # Base de datos en memoria (volátil, reinicia con el servidor):
   DATABASE_URL=sqlite:///:memory:
   ```

   **Inspección visual en DBeaver:**
   Para abrir la base de datos local en DBeaver, crear una conexión de tipo **SQLite** e ingresar en el campo de conexión/URL JDBC:
   ```text
   jdbc:sqlite:/path/proyecto/dev.db
   ```
   *(O adaptar con la ruta absoluta correspondiente a la ubicación del proyecto).*

> **Nota sobre pruebas automatizadas (`pytest`):**  
> La suite de tests automatizados (`tests/conftest.py`) ya utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** con `StaticPool` de manera aislada por prueba. Por lo tanto, `pytest` siempre ejecuta y valida los 43 tests  sin necesidad de tener PostgreSQL u otro servicio externo en ejecución.

### Inicialización y Scripts del Frontend (Vite + React + TypeScript)

En la raíz del proyecto, instalar las dependencias de Node:

```bash
pnpm install
```

#### Scripts de Ejecución Disponibles (`package.json`)

| Comando | Descripción | Entorno / URL |
| :--- | :--- | :--- |
| **`pnpm dev`** | **Frontend único (`RN-12`):** Levanta el servidor Vite para maquetado estático con componentes funcionales puros. | `http://localhost:5173` |
| **`pnpm dev:back`** | **Backend único:** Levanta la API FastAPI con Uvicorn en modo `--reload` utilizando el entorno virtual. | `http://localhost:8000` (`/docs`) |
| **`pnpm dev:all`** | **Fullstack unificado:** Levanta **Frontend y Backend simultáneamente** en una única terminal mediante `concurrently`. | Ambos servidores |
| **`pnpm dev:stop`** (o `pnpm stop`) | **Detención unificada:** Mata los procesos activos en los puertos `5173` y `8000`, liberando Frontend y Backend. | Consola |
| **`pnpm build`** | Verificación de tipos (`tsc -b`) y empaquetado de producción con Vite. | Directorio `dist/` |
| **`pnpm preview`** | Servidor local para previsualizar el bundle de producción compilado. | Localhost |
| **`pnpm test`** | Ejecución de la suite de pruebas unitarias del frontend con Vitest y React Testing Library. | Consola |
| **`pnpm test:watch`** | Modo observador interactivo (watch) para pruebas unitarias con Vitest. | Consola interactiva |

---

### Documentación Interactiva, Validación y Pruebas (Backend y Frontend)

1. **Swagger UI:** Con el backend en ejecución, acceder a [http://localhost:8000/docs](http://localhost:8000/docs) para probar interactivamente las operaciones CRUD completas del catálogo de productos y verificar los esquemas OpenAPI y respuestas (200, 201, 204, 404, 409, 422).
2. **ReDoc:** Disponible en [http://localhost:8000/redoc](http://localhost:8000/redoc).
3. **Pruebas Automatizadas del Backend (`pytest`):**  
   Ejecutar en la terminal con el entorno virtual activo:
   ```bash
   pytest -v
   ```
   (Ejecuta los 43 casos de prueba con SQLite en memoria aislado).
4. **Pruebas Unitarias del Frontend (`vitest` + `React Testing Library`):**  
   Ejecutar en la raíz del proyecto con Node:
   ```bash
   pnpm test
   ```
   (Ejecuta los 9 casos de prueba unitarios validando los componentes funcionales puros `ProductoCard` y `ProductoList`, verificando renderizado condicional, formateo de moneda con `Intl`, badges de estado y stock, estados vacíos con `role="status"` y estructura semántica de listas sin hooks ni efectos colaterales).
5. **Pruebas Manuales del Backend (REST Client y Postman):**  
   - **REST Client (VS Code):** Peticiones listas en [`src/tests/test_api.http`](src/tests/test_api.http) y [`src/tests/proveedores.http`](src/tests/proveedores.http).
   - **Colección Postman v2.1:** Exportada y lista para importar en [`src/tests/postman_collection.json`](src/tests/postman_collection.json).

---

## 📁 Estructura del Proyecto

```text
unidad5_react-postgreSQL-tailwind/
├── docs/                         # Documentación de consignas, resolución y sync
│   ├── consignas.md              # Requerimientos oficiales del trabajo práctico
│   ├── resolucion_tp5.md         # Registro paso a paso y justificación técnica
│   └── sync_kanban.js            # Script de sincronización con tablero Kanban
├── src/
│   ├── app/                      # Backend: FastAPI + SQLModel + PostgreSQL
│   │   ├── main.py               # Instancia de aplicación FastAPI y evento de startup
│   │   ├── database.py           # Engine de BD, create_db_and_tables() y sesiones
│   │   ├── models/               # Modelos de base de datos persistibles (SQLModel)
│   │   │   ├── producto.py
│   │   │   ├── categoria.py
│   │   │   └── proveedor.py
│   │   └── modules/              # Arquitectura modular por dominio (Router, Service, Schemas)
│   │       ├── producto/         # Endpoints, reglas de negocio y DTOs de Producto
│   │       ├── categoria/        # Endpoints, reglas de negocio y DTOs de Categoría
│   │       └── proveedor/        # Endpoints, reglas de negocio y DTOs de Proveedor
│   ├── components/               # Frontend: Componentes funcionales puros (RN-09, RN-10)
│   │   ├── Navbar.tsx            # Barra de navegación accesible con branding
│   │   ├── ProductoCard.tsx      # Tarjeta atómica de producto con badges y formateo Intl
│   │   ├── ProductoList.tsx      # Grilla y contenedor de lista accesible de productos
│   │   ├── ProductoForm.tsx      # Maquetado accesible de formulario de alta (sin hooks)
│   │   └── Footer.tsx            # Pie de página institucional con año dinámico
│   ├── types/                    # Frontend: Definición de interfaces TypeScript (RN-07, RN-10)
│   │   └── producto.ts           # Interface Producto alineada al schema del backend
│   ├── tests/                    # Pruebas del frontend y requests HTTP
│   │   ├── setup.ts              # Configuración global de Vitest y Jest-DOM
│   │   ├── ProductoCard.test.tsx # Pruebas unitarias de tarjeta de producto
│   │   ├── ProductoList.test.tsx # Pruebas unitarias de listado y estado vacío
│   │   ├── test_api.http         # Peticiones REST Client para Productos y Categorías
│   │   ├── proveedores.http      # Peticiones REST Client para Proveedores
│   │   └── postman_collection.json # Colección Postman para importar y probar
│   ├── App.tsx                   # Ensamblado principal de la aplicación y mock tipado
│   ├── main.tsx                  # Punto de entrada de React 19
│   └── index.css                 # Estilos globales con Tailwind CSS v4
├── tests/                        # Backend: Suite automatizada de pruebas (pytest)
│   ├── conftest.py               # Fixture con SQLite en memoria y StaticPool aislado
│   ├── test_fase1_database_and_models.py
│   ├── test_fase2_tarea2_1_validators.py
│   └── test_fase2_tarea2_2_services.py
├── .env.example                  # Plantilla de configuración de base de datos
├── package.json                  # Dependencias y scripts de Node / React
├── requirements.txt              # Dependencias del backend Python (RN-13)
├── tsconfig.json                 # Configuración raíz de TypeScript
├── vite.config.ts                # Configuración de Vite, Tailwind y Vitest
└── README.md                     # Guía de inicialización, ejecución y arquitectura
```