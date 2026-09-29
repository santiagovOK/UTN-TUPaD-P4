# Trabajo Práctico - Unidad 6 (FastAPI - React - Relaciones y Gestión de Estado)

Siguiendo las [consignas del Trabajo Práctico](/docs/consignas.md) y la [Guía Maestra de la Unidad 6](/docs/unidad6_guia.md), el presente trabajo aborda el desarrollo de una solución Full Stack integrando un frontend reactivo en **React 19 + TypeScript** con un backend modular en **FastAPI + SQLModel / PostgreSQL**.

El sistema implementa:
1. **Frontend (React + Hooks):** CRUD interactivo de **Categorías** consumiendo la API REST mediante `fetch` nativo, centralización de estado en `App.tsx` (`useState`, `useEffect`) y componentes funcionales puros estilizados con **Tailwind CSS v4**.
2. **Backend (FastAPI + SQLModel):** Modelado relacional y endpoints REST de **Categorías**, **Productos** y la tabla intermedia **Producto_Categoria** (relación N:N), testeados exhaustivamente y demostrables mediante archivos **REST Client (`.http`)** y Swagger UI.

Resolución paso a paso y seguimiento Kanban de este trabajo en: [docs/resolucion_tp6.md](/docs/resolucion_tp6.md).

---

## ✨ Estudiante

- **Nombre:** Varela, Santiago Octavio
- **Email institucional:** santiago.varela@tupad.utn.edu.ar
- **Repositorio Programación IV:** [https://github.com/santiagovOK/UTN-TUPaD-P4](https://github.com/santiagovOK/UTN-TUPaD-P4)

---

## 🚀 Inicialización Rápida

### 1. Backend (Python + FastAPI)

Desde la carpeta del backend (`unidad6_backend/`):

```bash
cd unidad6_backend

# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar entorno virtual
source .venv/bin/activate       # En Linux/macOS
# .venv\Scripts\activate       # En Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno (por defecto SQLite local dev.db)
cp .env.example .env

cd ..
```

### 2. Frontend y Raíz (Node + pnpm)

Desde la raíz del proyecto (`unidad6_relaciones_estado/`):

```bash
# Instalar dependencias del orquestador raíz
pnpm install

# Instalar dependencias de la app React
cd unidad6_frontend && pnpm install && cd ..
```

---

## 🏃 Modos de Ejecución

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

#### 1. Frontend Único (`unidad6_frontend/`)
Para desarrollar o maquetar exclusivamente en el cliente React:
```bash
# Desde la raíz:
pnpm run dev:front

# O desde unidad6_frontend/:
cd unidad6_frontend
pnpm dev
```
👉 Acceso: **http://localhost:5173**  
*(Más detalles en [unidad6_frontend/README.md](unidad6_frontend/README.md))*

#### 2. Backend Único (`unidad6_backend/`)
Para ejecutar o depurar exclusivamente los endpoints de FastAPI:
```bash
# Desde la raíz:
pnpm run dev:back

# O desde unidad6_backend/ (con el .venv activo):
cd unidad6_backend
fastapi dev app/main.py
```
👉 Acceso: **http://localhost:8000** | Documentación interactiva: **http://localhost:8000/docs**  
*(Más detalles en [unidad6_backend/README.md](unidad6_backend/README.md))*

---

## 📜 Tabla de Scripts Disponibles (`package.json` raíz)

| Comando | Descripción | Entorno / Destino |
| :--- | :--- | :--- |
| **`pnpm dev`** (o `pnpm dev:all`) | **Fullstack unificado:** Inicia Frontend y Backend simultáneamente en una sola terminal con prefijos de colores (`concurrently`). | Ambos puertos (5173 y 8000) |
| **`pnpm dev:front`** | Inicia únicamente el servidor de desarrollo de Vite para el Frontend. | `http://localhost:5173` |
| **`pnpm dev:back`** | Inicia únicamente el servidor Uvicorn / FastAPI para el Backend. | `http://localhost:8000` |
| **`pnpm stop`** (o `pnpm dev:stop`) | **Detención de procesos:** Mata los procesos activos en los puertos `5173` y `8000` liberando los puertos. | Consola |
| **`pnpm build:front`** | Compila y valida tipos TypeScript del frontend (`tsc -b && vite build`). | `unidad6_frontend/dist/` |
| **`pnpm test:back`** | Ejecuta la suite de pruebas unitarias y de integración de Python con `pytest`. | Consola |

---

## 🗄️ Configuración de Base de Datos (PostgreSQL / SQLite Fallback)

El backend utiliza **SQLModel / SQLAlchemy**, lo que permite alternar transparentemente entre PostgreSQL y SQLite según el contenido de `DATABASE_URL` en `unidad6_backend/.env`:

1. **PostgreSQL (Producción / Entrega):**
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp6_relaciones
   ```

2. **SQLite Local (Desarrollo y pruebas sin PostgreSQL instalado):**
   ```env
   # Base de datos persistente en archivo local:
   DATABASE_URL=sqlite:///./dev.db

   # Base de datos en memoria (volátil):
   DATABASE_URL=sqlite:///:memory:
   ```

> **Nota sobre pruebas automatizadas (`pytest`):**  
> La suite de tests automatizados (`tests/conftest.py`) utiliza por defecto un motor **SQLite en memoria (`sqlite:///:memory:`)** con `StaticPool` de manera aislada por prueba. Por lo tanto, `pytest` siempre ejecuta y valida los tests sin requerir PostgreSQL activo.

---

## 🧪 Pruebas y Validación

1. **Swagger UI:** Con el backend en ejecución, acceder a [http://localhost:8000/docs](http://localhost:8000/docs) para probar interactivamente las operaciones CRUD completas de Categorías y Productos.
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
   Los archivos `.http` permiten ejecutar solicitudes HTTP directamente desde el editor para validar los endpoints de `Producto` y `Producto_Categoria` sin requerir interfaz de usuario, cumpliendo con la consigna.

---

## 📁 Estructura General del Proyecto

```text
unidad6_relaciones_estado/
├── docs/                           # Documentación oficial y planificación
│   ├── consignas.md                # Requisitos del Trabajo Práctico
│   ├── unidad6_guia.md             # Guía teórica y arquitectónica de relaciones y estado
│   └── resolucion_tp6.md           # Tablero Kanban y registro de ejecución paso a paso
├── package.json                    # Orquestador de scripts concurrentes (dev:all, stop, etc.)
├── pnpm-lock.yaml                  # Lockfile de dependencias del orquestador
├── .gitignore                      # Exclusiones de Git (node_modules, .venv, *.db, dist)
├── README.md                       # Documentación global del proyecto
│
├── unidad6_backend/                # Capa Backend: FastAPI + SQLModel
│   ├── requirements.txt            # Dependencias Python
│   ├── pytest.ini                  # Configuración de pytest
│   ├── .env.example                # Plantilla de variables de entorno
│   ├── README.md                   # Documentación específica del backend
│   ├── app/
│   │   ├── main.py                 # Instancia de FastAPI, CORS y routers
│   │   ├── database.py             # Engine de base de datos y sesiones SQLModel
│   │   ├── models/                 # Modelos de base de datos relacionales
│   │   └── modules/                # Módulos por dominio de negocio
│   │       ├── categoria/          # Endpoints, schemas y servicio de Categorías
│   │       └── producto/           # Endpoints, schemas y servicio de Productos
│   └── tests/                      # Suite de tests con fixtures SQLite aisladas
│
└── unidad6_frontend/               # Capa Frontend: React 19 + TypeScript + Tailwind
    ├── package.json                # Dependencias de React y scripts Vite
    ├── tsconfig.json               # Configuración de TypeScript
    ├── vite.config.ts              # Configuración del bundler Vite
    ├── README.md                   # Documentación específica del frontend
    ├── index.html                  # HTML base
    └── src/
        ├── main.tsx                # Entrada de la aplicación React
        ├── App.tsx                 # Contenedor principal: estado (useState), efectos (useEffect) y fetch
        ├── index.css               # Estilos globales y Tailwind CSS v4
        ├── types/                  # Interfaces TypeScript (categoria.ts, producto.ts)
        └── components/             # Componentes funcionales puros
            ├── Navbar.tsx          # Barra de navegación
            ├── CategoriaCard.tsx   # Tarjeta de categoría con acciones
            ├── CategoriaList.tsx   # Grilla y listado de categorías
            ├── CategoriaModal.tsx  # Modal interactivo de alta/edición
            └── Footer.tsx          # Pie de página institucional
```
