# Trabajo Práctico — Unidad 8: Formularios y Tablas (FastAPI - React)

> **Materia:** Programación IV (TUPaD - UTN)  
> **Tema:** Formularios tipados con validación y manejo de estado (@tanstack/react-form), Tablas dinámicas con ordenamiento, filtrado y paginación (@tanstack/react-table v8), Persistencia transaccional con Unit of Work en backend y Navegación SPA.  
> **Seguimiento Operativo y Plan de Ejecución:** [docs/resolucion_tp8.md](docs/resolucion_tp8.md)  
> **Consigna Oficial:** [docs/consigna.md](docs/consigna.md) | **Diagrama de Dominio:** [docs/UML_FOOD_STORE.svg](docs/UML_FOOD_STORE.svg)

---

## 🎯 Objetivo de la Unidad 8 y Continuidad con TP7

El presente proyecto representa la continuidad directa del **Trabajo Práctico 7** para dar cumplimiento a los requerimientos de la **Unidad 8**. Sobre la base del catálogo de alimentos y la navegación desacoplada previa, el trabajo se enfoca en dos grandes ejes de ingeniería:

1. **Frontend:** Migración de los formularios de gestión a **TanStack Form** (control unificado, validación estricta y prevención de doble envío), adopción de **TanStack Table v8** para la presentación tabular con ordenamiento y paginación en cliente, e incorporación de la gestión completa para **Ingredientes**.
2. **Backend:** Incorporación del módulo transaccional de **Pedidos y DetallePedido** bajo una arquitectura rigurosa por capas (*Models–Schemas–Repository–Unit of Work–Service–Router*), garantizando operaciones atómicas (todo o nada) y congelamiento histórico de precios unitarios.

### Estado Actual del Repositorio y Diagnóstico de Brechas

| Capa / Módulo | Estado en el Código | Planificación TP8 |
|---|---|---|
| **Identidad del Proyecto** | Renombrado a `unidad8_backend/`, `unidad8_frontend/` y sincronización documental completa. | ✅ Épica 0 completada |
| **Categorías (Frontend)** | CRUD operativo con TanStack Query y modales HTML/useState. | ⏳ Planificado: migración a TanStack Form y Table (Épica 3) |
| **Productos (Frontend)** | CRUD operativo con modales HTML, categorías obligatorias y ficha de detalle. | ⏳ Planificado: migración a TanStack Table y Form (Épica 3) |
| **Ingredientes (Frontend)** | Tipos TypeScript definidos; sin interfaz de gestión. | ⏳ Planificado: creación de servicio, página CRUD, modal y tabla (Épica 4) |
| **Catálogo (Backend)** | Categorías, Productos, Ingredientes y Unidades de Medida con persistencia SQLModel. | ✅ Preservado: arquitectura probada, sin regresión |
| **Pedidos (Backend)** | Inexistente en la base actual. | ⏳ Planificado: modelos, schemas, UoW transaccional, servicio y router REST (Épica 2) |

---

## 📦 Modalidad de Entrega y Repositorio

Conforme a las pautas de evaluación de la cátedra para la Unidad 8, la entrega final se compone de dos archivos comprimidos independientes generados por exclusión:
- **Frontend:** `Varela_Santiago_TPI_unidad8_frontend.zip` (excluyendo estrictamente `node_modules/`, `dist/`, artefactos temporales y cualquier carpeta `guidelines/`).
- **Backend:** `Varela_Santiago_TPI_unidad8_backend.zip` (excluyendo entornos `.venv/`, `__pycache__/`, bases locales `.db`, temporales y cualquier carpeta `guidelines/`).

> **Exclusión de Bibliografía en Entregables:**  
> Conforme a lo establecido en [docs/resolucion_tp8.md](docs/resolucion_tp8.md), la carpeta `docs/guidelines/` se utiliza como bibliografía técnica de trabajo local y no se incluirá en ninguno de los archivos ZIP de entrega.

### Repositorio y Enlaces Locales
- **Repositorio General (Programación IV):** [https://github.com/santiagovOK/UTN-TUPaD-P4](https://github.com/santiagovOK/UTN-TUPaD-P4)
- **Capa Backend (local):** [unidad8_backend/](unidad8_backend/README.md)
- **Capa Frontend (local):** [unidad8_frontend/](unidad8_frontend/README.md)
- **Antecedente Histórico:** [Directorio Unidad 7 en GitHub](https://github.com/santiagovOK/UTN-TUPaD-P4/tree/main/unidad7_server_state_navegacion) *(mantenido solo como referencia de versiones previas)*.

---

## 🚀 Inicialización y Puesta en Marcha

### 1. Backend (Python + FastAPI)

Desde el directorio `unidad8_backend/`:

```bash
cd unidad8_backend

# 1. Crear y activar entorno virtual
python -m venv .venv
source .venv/bin/activate       # En Linux/macOS
# .venv\Scripts\activate        # En Windows

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# IMPORTANTE: Editar .env para definir DATABASE_URL explícitamente (PostgreSQL o SQLite local).
# app/database.py exige esta variable y no aplica fallbacks silenciosos.

cd ..
```

### 2. Frontend y Orquestador Raíz (Node + pnpm)

Desde la raíz del proyecto:

```bash
# Instalar dependencias del orquestador raíz
pnpm install

# Instalar dependencias de la aplicación React
cd unidad8_frontend && pnpm install && cd ..
```

---

## 🖥️ Comandos de Ejecución (`package.json` raíz)

| Comando | Acción | Destino / Puerto |
|---|---|---|
| **`pnpm dev`** *(o `pnpm dev:all`)* | **Fullstack unificado:** Inicia frontend y backend concurrentemente con prefijos en consola. | Puertos `5173` y `8000` |
| **`pnpm dev:front`** | Inicia únicamente el servidor de desarrollo Vite del frontend. | [http://localhost:5173](http://localhost:5173) |
| **`pnpm dev:back`** | Inicia únicamente la API de FastAPI con recarga automática. | [http://localhost:8000](http://localhost:8000) (Docs: `/docs`) |
| **`pnpm build:front`** | Valida tipos TypeScript y compila el bundle de producción frontend. | `unidad8_frontend/dist/` |
| **`pnpm test:back`** | Ejecuta la suite de pruebas automatizadas del backend con `pytest`. | Consola (SQLite en memoria) |
| **`pnpm stop`** *(o `pnpm dev:stop`)* | Mata los procesos que ocupan los puertos `5173` y `8000`. | Consola |

---

## 🗄️ Persistencia y Base de Datos

La conexión de base de datos se rige estrictamente por la variable de entorno `DATABASE_URL` en `unidad8_backend/.env`. El sistema **requiere configuración explícita** y no asume una base por omisión:

1. **PostgreSQL (Desarrollo y entrega relacional):**
   ```env
   DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/tp7_server_state
   ```
   *(El nombre de base `tp7_server_state` es una convención de base de datos preexistente y no afecta el funcionamiento de la Unidad 8).*
2. **SQLite Local (Desarrollo sin motor PostgreSQL instalado):**
   ```env
   DATABASE_URL=sqlite:///./dev.db
   ```
3. **SQLite en Memoria (Testing automatizado):**
   ```env
   DATABASE_URL=sqlite:///:memory:
   ```

> **Aislamiento en Tests:** La suite automatizada (`tests/test_productos_http.py`) intercepta el engine y utiliza de forma transparente `sqlite:///:memory:` con `StaticPool`, permitiendo que `pnpm test:back` corra de manera aislada sin alterar datos existentes.

---

## 📁 Estructura del Proyecto

```text
utn-paradigmas4-tp8-formularios-tablas/
├── docs/                           # Documentación oficial y planificación
│   ├── consigna.md                 # Especificación evaluativa del TP8
│   ├── resolucion_tp8.md           # Plan rector, matrices HU/RN y tablero de épicas
│   ├── UML_FOOD_STORE.svg          # Diagrama UML de clases del dominio
│   └── guidelines/                 # Referencia conceptual local; excluida de ZIP
│       ├── unidad8_guia_maestra.md # Criterio normativo Unidad 8 (UoW, Form, Table)
│       ├── clean_code.md           # Principios Clean Code y refactorización
│       └── javaismos_guia.md       # Buenas prácticas en Python idiomático
├── package.json                    # Orquestador de scripts concurrentes
├── pnpm-lock.yaml                  # Lockfile del orquestador raíz
├── .gitignore                      # Exclusiones de Git
├── README.md                       # Documentación principal de bienvenida
│
├── unidad8_backend/                # Backend modular en FastAPI + SQLModel
│   ├── requirements.txt            # Dependencias Python
│   ├── pytest.ini                  # Configuración de pytest
│   ├── .env.example                # Archivo de ejemplo de variables de entorno
│   ├── productos.http              # Suite REST Client del catálogo
│   ├── README.md                   # Documentación específica del backend
│   ├── app/
│   │   ├── main.py                 # Instancia FastAPI, CORS y montaje de routers
│   │   ├── database.py             # Engine SQLAlchemy, sesiones y metadata
│   │   ├── seed.py                 # Inicialización de catálogo de unidades de medida
│   │   ├── models/                 # Modelos relacionales: categoria, producto, etc.
│   │   └── modules/                # Módulos: categoria, producto, ingrediente, unidad_medida
│   │                               # (Planificado: pedidos con Repository y Unit of Work)
│   └── tests/                      # Suite de pruebas automatizada
│       └── test_productos_http.py  # Tests integrales sobre suite HTTP
│
└── unidad8_frontend/               # Frontend React 19 + TypeScript + Vite
    ├── package.json                # Dependencias (React, TanStack Query, Router, Tailwind)
    ├── vite.config.ts              # Configuración Vite con plugin Tailwind v4
    ├── tsconfig.json               # Configuración de compilador TypeScript
    ├── README.md                   # Documentación específica del frontend
│   ├── index.html                  # Documento HTML principal ("Food Store Admin — TP8")
    └── src/
        ├── main.tsx                # Entrada raíz: QueryClientProvider y BrowserRouter
        ├── App.tsx                 # Enrutador declarativo sin lógica de datos
        ├── index.css               # Importación de Tailwind CSS v4
        ├── types/                  # Contratos TypeScript de las entidades
        ├── services/               # Clientes de API y funciones fetch
        ├── pages/                  # Vistas: CategoriasPage, ProductsPage, ProductDetailPage
        │                           # (Planificado: IngredientesPage)
        └── components/             # Componentes presentacionales y modales
            └── Navbar.tsx          # Barra de navegación con insignia TP8
```
