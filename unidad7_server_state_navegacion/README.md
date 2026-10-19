# Trabajo Práctico - Unidad 7 (FastAPI - React - Server State con TanStack Query y Enrutamiento)

Siguiendo las [consignas del Trabajo Práctico](docs/consigna.md) y el diagrama [UML Food Store](docs/UML_FOOD_STORE.svg), el presente trabajo aborda el desarrollo de una solución Full Stack integrando una Single Page Application (SPA) reactiva en **React 19 + TypeScript + TanStack Query + React Router** con un backend modular en **FastAPI + SQLModel / PostgreSQL**.

El sistema implementa:
1. **Frontend (React + TanStack Query + React Router):**
   - CRUD de **Categorías** y **Productos** mediante `useQuery` y `useMutation`, con invalidación de caché (`queryClient.invalidateQueries`) luego de las operaciones de escritura; la edición de categorías usa `PUT /categorias/{id}` (`HU-03`).
   - Navegación declarativa (**CategoriasPage** en `/` y `/categorias`, **ProductsPage** en `/productos` y **ProductDetailPage** en `/productos/:id`) con React Router (`BrowserRouter`, `Routes`, `Route`, `NavLink`).
   - `ProductsPage.tsx` incorpora `ProductoModal.tsx` para alta y edición de productos con selección obligatoria de categorías (`categoria_ids`, `RN-19`), baja con confirmación e invalidación de caché en TanStack Query.
   - Detalle del producto con información de Categorías e Ingredientes, incluyendo la unidad de medida y cantidad de cada ingrediente.
   - Desacoplamiento estricto de `App.tsx`: define rutas y renderiza el `Navbar`, sin lógica de negocio, estado de datos ni llamadas a APIs.
   - Tipado estático de Categorías, Productos, Ingredientes y unidades de medida en contratos TypeScript.
2. **Backend (FastAPI + SQLModel):**
   - Arquitectura en capas Models-Schemas-Service-Router para el clúster `UnidadMedida`, `Ingrediente`, `Categoria`, `Producto`, `ProductoCategoria` y `ProductoIngrediente`.
   - `UnidadMedida` es un catálogo inmutable de solo lectura que se inicializa vía `app/seed.py` con las 7 unidades oficiales; `Ingrediente` dispone de CRUD con borrado lógico.
   - Las relaciones N:M se gestionan exclusivamente al crear (`POST /productos/`) o actualizar (`PUT /productos/{id}`) un producto (`RN-11`, `RN-12`, `RN-19`..`RN-22`).
   - Consultas relacionales inversas: `GET /productos/{id}/categorias`, `GET /productos/{id}/ingredientes` y `GET /categorias/{id}/productos` (`HU-07`); diagnóstico con `GET /health/` y `GET /health/db`.
   - Paginación con `offset` y `limit` y respuesta estandarizada `{ "total": int, "items": list }` donde corresponde.
   - Configuración de CORS para el frontend (`http://localhost:5173` y `http://127.0.0.1:5173`); documentación interactiva disponible en Swagger UI.

Resolución paso a paso y seguimiento Kanban de este trabajo en: [docs/resolucion_tp7.md](docs/resolucion_tp7.md).

> **Nota sobre discrepancia entre Consignas y Diagrama UML:**  
> En el diagrama provisto por la cátedra ([docs/UML_FOOD_STORE.svg](docs/UML_FOOD_STORE.svg)), el clúster *Catálogo de Productos* incluye únicamente las entidades `Categoria`, `Producto` y `ProductoCategoria`; no modela `Ingrediente`, `UnidadMedida` ni `ProductoIngrediente`. Sin embargo, en la especificación formal del Trabajo Práctico ([docs/consigna.md](docs/consigna.md)) se exige explícitamente el catálogo inmutable de `UnidadMedida` (solo lectura con 7 unidades en `seed.py`), el CRUD con baja lógica de `Ingrediente` y la asociación N:M `ProductoIngrediente` (`HU-06`, `HU-07`, `RN-20`, `RN-21`). Por ende, para garantizar estricta concordancia con la consigna, dichas entidades y relaciones fueron modeladas e implementadas en el backend y reflejadas en los contratos del frontend. Para un análisis detallado, consultar la sección 1.1 de [docs/resolucion_tp7.md](docs/resolucion_tp7.md).

> **Nota sobre Modalidad de Entrega y Repositorio Unificado:**  
> Según las pautas de cátedra de la Unidad 7, el proyecto se entrega dividido en dos archivos comprimidos independientes:
> - **Proyecto Frontend:** Comprimido en `Varela_Santiago_TPI_unidad7_frontend.zip` (eliminando estrictamente la carpeta `node_modules/` antes de comprimir).
> - **Proyecto Backend:** Comprimido en `Varela_Santiago_TPI_unidad7_backend.zip` (eliminando entornos virtuales `.venv/` y cachés temporales).
>
> No obstante, el proyecto completo puede clonarse y ejecutarse íntegramente (incluyendo la orquestación concurrente con `pnpm dev`) a partir del repositorio en GitHub:  
> **[https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)**

---

## ✨ Estudiante

- **Nombre:** Varela, Santiago Octavio
- **Email institucional:** santiago.varela@tupad.utn.edu.ar
- **Repositorio Programación IV:** [https://github.com/santiagovOK/UTN-TUPaD-P4](https://github.com/santiagovOK/UTN-TUPaD-P4)
- **Directorio Unidad 7:** [https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion)

---

## Inicialización Rápida

### 1. Backend (Python + FastAPI)

Desde la carpeta del backend (`unidad7_backend/`):

```bash
cd unidad7_backend

# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
source .venv/bin/activate       # En Linux/macOS
# .venv\Scripts\activate        # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (por defecto SQLite local dev.db)
cp .env.example .env

cd ..
```

### 2. Frontend y Raíz (Node + pnpm)

Desde la raíz del proyecto (`unidad7_server_state_navegacion/`):

```bash
# Instalar dependencias del orquestador raíz
pnpm install

# Instalar dependencias de la app React
cd unidad7_frontend && pnpm install && cd ..
```

---

## Modos de Ejecución

El proyecto puede ejecutarse de manera unificada en una sola terminal (mediante `concurrently`) o en terminales independientes por cada capa:

### Opción A — Ejecución Unificada (Recomendada)

Desde la raíz del proyecto, levantar simultáneamente Frontend y Backend con un solo comando:

```bash
pnpm dev
# o bien: pnpm run dev:all
```

- **Frontend:** [http://localhost:5173](http://localhost:5173)
- **Backend API:** [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)

Para detener ambos servidores y liberar los puertos:
```bash
pnpm stop
# o bien: pnpm run dev:stop
```

---

### Opción B — Ejecución Individual por Capa

#### 1. Frontend Único (`unidad7_frontend/`)
Para desarrollar o maquetar exclusivamente en el cliente React:
```bash
# Desde la raíz:
pnpm run dev:front

# O desde unidad7_frontend/:
cd unidad7_frontend
pnpm dev
```
👉 Acceso: **http://localhost:5173**  
*(Más detalles en [unidad7_frontend/README.md](unidad7_frontend/README.md))*

#### 2. Backend Único (`unidad7_backend/`)
Para ejecutar o depurar exclusivamente los endpoints de FastAPI:
```bash
# Desde la raíz:
pnpm run dev:back

# O desde unidad7_backend/ (con el .venv activo):
cd unidad7_backend
fastapi dev app/main.py
```
👉 Acceso: **http://localhost:8000** | Documentación interactiva: **http://localhost:8000/docs**  
*(Más detalles en [unidad7_backend/README.md](unidad7_backend/README.md))*

---

## Tabla de Scripts Disponibles (`package.json` raíz)

| Comando | Descripción | Entorno / Destino |
| :--- | :--- | :--- |
| **`pnpm dev`** (o `pnpm dev:all`) | **Fullstack unificado:** Inicia Frontend y Backend simultáneamente en una sola terminal con prefijos de colores (`concurrently`). | Ambos puertos (5173 y 8000) |
| **`pnpm dev:front`** | Inicia únicamente el servidor de desarrollo de Vite para el Frontend. | `http://localhost:5173` |
| **`pnpm dev:back`** | Inicia únicamente el servidor Uvicorn / FastAPI para el Backend. | `http://localhost:8000` |
| **`pnpm stop`** (o `pnpm dev:stop`) | **Detención de procesos:** Mata los procesos activos en los puertos `5173` y `8000` liberando los puertos. | Consola |
| **`pnpm build:front`** | Compila y valida tipos TypeScript del frontend (`tsc -b && vite build`). | `unidad7_frontend/dist/` |
| **`pnpm test:back`** | Ejecuta la suite de pruebas unitarias y de integración de Python con `pytest`. | Consola |

---

## Configuración de Base de Datos (PostgreSQL / SQLite Fallback)

El backend utiliza **SQLModel / SQLAlchemy**, lo que permite alternar transparentemente entre PostgreSQL y SQLite según el contenido de `DATABASE_URL` en `unidad7_backend/.env`:

1. **PostgreSQL (Producción / Entrega):**
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp7_server_state
   ```

2. **SQLite Local (Desarrollo y pruebas sin PostgreSQL instalado):**
   ```env
   # Base de datos persistente en archivo local:
   DATABASE_URL=sqlite:///./dev.db

   # Base de datos en memoria (volátil):
   DATABASE_URL=sqlite:///:memory:
   ```

> **Nota sobre pruebas automatizadas (`pytest`):**  
> La suite de tests automatizados (`tests/test_productos_http.py`) utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** con `StaticPool` de manera aislada por prueba. Por lo tanto, `pytest` siempre ejecuta y valida los tests sin requerir PostgreSQL activo.

---

## Pruebas y Validación

1. **Swagger UI:** Con el backend en ejecución, acceder a [http://localhost:8000/docs](http://localhost:8000/docs) para probar interactivamente las operaciones CRUD completas de Categorías, Productos y su relación N:N.
2. **Pruebas Automatizadas de Backend (`pytest`):**
   ```bash
   pnpm test:back
   ```
   (Ejecuta los tests unitarios y de integración con SQLite en memoria).
3. **Validación de Tipos Frontend (`tsc`):**
   ```bash
   pnpm build:front
   ```
   (Verifica que no existan discrepancias de tipos TypeScript ni errores de compilación).
4. **Pruebas de API REST Client (`.http`):**  
   El archivo `unidad7_backend/productos.http` permite ejecutar solicitudes HTTP directamente desde el editor para validar los endpoints de `Producto` y `ProductoCategoria` sin requerir interfaz de usuario, cumpliendo con la consigna.

---

## 📁 Estructura General del Proyecto

```text
unidad7_server_state_navegacion/
├── docs/                           # Documentación oficial y planificación
│   ├── consigna.md                 # Requisitos del Trabajo Práctico 7
│   ├── UML_FOOD_STORE.svg          # Diagrama UML de clases del dominio
│   ├── guidelines/                 # Guías de referencia arquitectónica
│   │   ├── unidad7_guia_maestra.md # Server State (TanStack Query) y Routing (React Router)
│   │   └── howto_uml.md            # Reglas de mapeo UML a SQLModel/TypeScript
│   └── resolucion_tp7.md           # Tablero Kanban y registro de ejecución paso a paso
├── package.json                    # Orquestador de scripts concurrentes (dev:all, stop, etc.)
├── .gitignore                      # Exclusiones de Git (node_modules, .venv, *.db, dist)
├── README.md                       # Documentación global del proyecto
│
├── unidad7_backend/                # Capa Backend: FastAPI + SQLModel
│   ├── requirements.txt            # Dependencias Python
│   ├── pytest.ini                  # Configuración de pytest
│   ├── .env.example                # Plantilla de variables de entorno
│   ├── productos.http              # Archivo unificado de pruebas REST Client
│   ├── README.md                   # Documentación específica del backend
│   ├── app/
│   │   ├── main.py                 # Instancia de FastAPI, CORS y routers
│   │   ├── database.py             # Engine de base de datos y sesiones SQLModel
│   │   ├── models/                 # Modelos persistentes: categoria.py, producto.py, ingrediente.py, unidad_medida.py
│   │   ├── seed.py                 # Datos iniciales de ingredientes y unidades de medida
│   │   └── modules/                # Módulos de dominio: categoria, producto, ingrediente, unidad_medida
│   └── tests/                      # Suite de tests automatizada de extremo a extremo
│       ├── __init__.py
│       └── test_productos_http.py  # Suite integral con base SQLite en memoria aislada (StaticPool)
│
└── unidad7_frontend/               # Capa Frontend: React 19 + TypeScript + TanStack Query + React Router
    ├── package.json                # Dependencias de React, TanStack Query y React Router
    ├── tsconfig.json               # Configuración de TypeScript
    ├── vite.config.ts              # Configuración del bundler Vite con Tailwind CSS v4
    ├── README.md                   # Documentación específica del frontend
    ├── index.html                  # HTML base
    └── src/
        ├── main.tsx                # Entrada: montaje de QueryClientProvider y BrowserRouter
        ├── App.tsx                 # Enrutador principal: define <Routes> y <Navbar>, sin lógica de datos
        ├── index.css               # Estilos globales y Tailwind CSS v4
        ├── types/                  # Contratos TypeScript: categoría, producto, ingrediente y unidad de medida
        ├── services/               # Clientes HTTP y servicios CRUD (categorias, productos, ingredientes, unidades)
        ├── pages/                  # Vistas por ruta: CategoriasPage, ProductsPage, ProductDetailPage
        └── components/             # Componentes presentacionales
            ├── Navbar.tsx          # Barra de navegación con NavLink a Categorías y Productos
            ├── CategoriaCard.tsx   # Fila tabular: id, nombre, descripción y acciones
            ├── CategoriaList.tsx   # Contenedor tabular con cabeceras y renderizado de filas
            ├── CategoriaModal.tsx  # Modal interactivo para alta y edición de categorías
            └── ProductoModal.tsx   # Modal para alta y edición de productos e ingredientes asociados
```
