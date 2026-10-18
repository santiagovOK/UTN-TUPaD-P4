# Trabajo Práctico - Unidad 7 (FastAPI - React - Server State con TanStack Query y Enrutamiento)

Siguiendo las [consignas del Trabajo Práctico](/docs/consigna.md), el diagrama [UML Food Store](/docs/UML_FOOD_STORE.svg) y la [Guía Maestra de la Unidad 7](/docs/guidelines/unidad7_guia_maestra.md), el presente trabajo aborda el desarrollo de una solución Full Stack integrando una Single Page Application (SPA) reactiva en **React 19 + TypeScript + TanStack Query + React Router** con un backend modular en **FastAPI + SQLModel / PostgreSQL**.

El sistema implementa:
1. **Frontend (React + TanStack Query + React Router):**
   - CRUD completo de **Categorías** consumiendo la API de FastAPI mediante **TanStack Query** (`useQuery`, `useMutation`), con invalidación automática de la caché (`queryClient.invalidateQueries`) tras cada operación de alta, edición y baja.
   - Navegación declarativa por páginas separadas (**CategoriasPage** en `/` y `/categorias`, **ProductsPage** en `/productos` y **ProductDetailPage** en `/productos/:id`) utilizando **React Router** (`BrowserRouter`, `Routes`, `Route`, `NavLink`).
   - Formulario de alta y edición dentro de un modal accesible y flotante con backdrop (`CategoriaModal.tsx`), controlado con estado booleano mediante `useState` a nivel de página.
   - **Desacoplamiento estricto de `App.tsx`:** No contiene lógica de negocio, estado de datos ni llamadas a APIs; su única responsabilidad es definir la tabla de rutas y renderizar el `Navbar`.
   - Estilizado profesional con **Tailwind CSS v4** y tipado estático riguroso en TypeScript (`Categoria`, `Producto` y props en el 100% de los componentes `.tsx`).
2. **Backend (FastAPI + SQLModel):**
   - Arquitectura en capas **Models-Schemas-Service-Router** para el catálogo de productos (`Categoria`, `Producto` y la tabla intermedia `ProductoCategoria`).
   - Paginación eficiente con `offset` y `limit` validados declarativamente mediante `fastapi.Query` y respuesta estandarizada `{ "total": int, "items": list }`.
   - Configuración de **CORS** para permitir peticiones desde el origen del frontend (`http://localhost:5173` y `http://127.0.0.1:5173`).
   - Demostración de los endpoints de `Producto` y `ProductoCategoria` mediante suite unificada de **REST Client (`productos.http`)** y Swagger UI.

Resolución paso a paso y seguimiento Kanban de este trabajo en: [docs/resolucion_tp7.md](/docs/resolucion_tp7.md).

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
│   │   ├── models/                 # Modelos persistentes (categoria.py, producto.py)
│   │   └── modules/                # Módulos por dominio de negocio (categoria, producto)
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
│       ├── types/                  # Interfaces TypeScript (categoria.ts, producto.ts, index.ts)
│       ├── services/               # Clientes y funciones HTTP puras (categorias.service.ts, productos.service.ts, api.ts)
│       ├── pages/                  # Vistas por ruta (CategoriasPage.tsx, ProductsPage.tsx, ProductDetailPage.tsx)
        └── components/             # Componentes presentacionales puros
            ├── Navbar.tsx          # Barra de navegación con NavLink a Categorías y Productos
            ├── CategoriaCard.tsx   # Fila tabular: id, nombre, descripción y acciones
            ├── CategoriaList.tsx   # Contenedor tabular con cabeceras y renderizado de filas
            └── CategoriaModal.tsx  # Modal interactivo con backdrop para alta y edición
```
