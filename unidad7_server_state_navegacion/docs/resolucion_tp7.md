# Resolución y Plan de Ejecución — Trabajo Práctico 7

> **Materia:** Programación IV (Tecnicatura Universitaria en Programación a Distancia - UTN)  
> **Tema:** Server State (TanStack Query) y Navegación (React Router + TypeScript) en Frontend; Optimización de Endpoints y Relaciones en Backend (FastAPI + SQLModel / PostgreSQL).  
> **Estrategia:** Descomposición "Bottom-Up" (de menor a mayor dependencia) orientada a tablero Kanban. Cada tarea referencia explícitamente las Historias de Usuario (HU), Reglas de Negocio (RN) y los lineamientos de `docs/consigna.md`, `docs/guidelines/unidad7_guia_maestra.md` y `docs/UML_FOOD_STORE.svg`.

---

## 1. Decisiones de Diseño Técnico y Alcance

### 1.1. Modelado de `Categoria.descripcion` (Resolución de Ambigüedad en UML)
* **Contexto:** En el diagrama `docs/UML_FOOD_STORE.svg`, la entidad `Categoria` exhibe el campo `descripcion : TEXT {NN, DEFAULT 0}`. Dicha definición presenta una inconsistencia semántica (`DEFAULT 0` en una columna textual, probablemente heredado por copia desde columnas de descuento o costo en tablas de transacciones).
* **Decisión Adoptada (Opción A - Flexible):**
  * `descripcion` se modela como **opcional / nullable** con fallback a cadena vacía (`default=""` o `None`).
  * **Backend (SQLModel / Pydantic):**
    * Modelo: `descripcion: str = Field(default="", nullable=False)`.
    * Schemas: `descripcion: Optional[str] = ""` (admite omitted, `None` o `str`, normalizando a cadena vacía para evitar errores de validación HTTP 422).
  * **Frontend (TypeScript):** `descripcion?: string`.
  * **Fundamento:** Mantiene simetría con las otras entidades del catálogo (`Rol.descripcion` y `Producto.descripcion` son `TEXT`), respeta la flexibilidad de carga en el formulario modal y preserva la compatibilidad con el maquetado de `CategoriaCard.tsx` (que contempla el fallback visual *"Sin descripción"*).

### 1.2. Modelado de la Relación Muchos a Muchos (`ProductoCategoria`) y Metadatos
* **Contexto:** La consigna exige el CRUD completo de `ProductoCategoria` en el backend. El diagrama UML detalla la tabla intermedia con clave primaria compuesta `(producto_id, categoria_id)` y el atributo `es_principal : BOOLEAN {NN, DEFAULT false}` con marca temporal `created_at`.
* **Decisión de Implementación:**
  * **Entidad `ProductoCategoria`:** Definida con `__tablename__ = "producto_categoria"`, clave primaria compuesta en `producto_id` y `categoria_id`, y campo booleano `es_principal: bool = Field(default=False, nullable=False)`.
  * **Contratos REST y Endpoints de Asociación (Alineación con Guía Maestra):**
    * `POST /productos/categorias/asignar`: Endpoint semántico que recibe el DTO `ProductoCategoriaAssign(producto_id: int, categoria_id: int, es_principal: bool = False)`, permitiendo asignar o actualizar el rol principal de una categoría.
    * `DELETE /productos/{producto_id}/categorias/{categoria_id}`: Desvinculación de la relación con código HTTP 204 No Content.
    * `POST /productos/{id}/categorias/{categoria_id}`: Mantenido como alias de conveniencia RESTful para compatibilidad retroactiva con la suite de pruebas del TP6.

### 1.3. Alcance Funcional Delimitado
* **Entidades Incluidas:** Exclusivamente el clúster **Catálogo de Productos**:
  1. `Categoria` (CRUD completo en Frontend con TanStack Query y Backend REST).
  2. `Producto` (CRUD en Backend y schemas DTO; catálogo de consulta en Frontend en `ProductsPage`).
  3. `ProductoCategoria` (tabla intermedia N:N con campo `es_principal` y endpoints en Backend).
* **Entidades Excluidas (Fuera de Alcance de la Consigna):**
  * Dominio **Identidad & Acceso**: `Usuario`, `Rol`, `UsuarioRol`, `DireccionEntrega`.
  * Dominio **Ventas & Transacciones**: `FormaPago`, `EstadoPedido`, `Pedido`, `DetallePedido`, `HistorialEstadoPedido`.
  * Dominio **Inventario / Stock**: Excluido de `Producto` por principio de responsabilidad única (anotación explícita del UML: *"stock excluido: dominio INVENTARIO (SRP)"*).

---

## 2. Matriz de Trazabilidad Rápida

| ID | Tipo | Descripción Sintética | Fase Asignada |
| :--- | :---: | :--- | :---: |
| **HU-01** | HU | Listado reactivo de categorías consumiendo la API mediante `useQuery` de TanStack Query, con estados de carga (`isLoading`), error (`isError`), búsqueda (`search`) y renderizado tabular. | Fase 3 |
| **HU-02** | HU | Formulario de alta y edición de categorías dentro de modal flotante (`CategoriaModal.tsx`), controlado con `useState` booleano en la página, ejecutando mutaciones con `useMutation` e invalidando la caché (`invalidateQueries`). | Fase 3 |
| **HU-03** | HU | Eliminación de categorías desde la tabla mediante `useMutation` con confirmación previa y refetch/actualización automática de la caché. | Fase 3 |
| **HU-04** | HU | Navegación SPA sin recarga entre `CategoriasPage` (`/` y `/categorias`) y `ProductsPage` (`/productos`) utilizando React Router (`BrowserRouter`, `Routes`, `Route`, `NavLink` con estilos activos). | Fase 3 |
| **HU-05** | HU | Visualización del catálogo de productos en `ProductsPage.tsx` mediante `useQuery(["productos"])`, renderizando tarjetas con badges de categorías asociadas e indicador de disponibilidad. | Fase 3 |
| **RN-01** | RN | **Desacoplamiento de `App.tsx`:** `App.tsx` no debe contener lógica de negocio, estado de datos ni llamadas a APIs; su rol exclusivo es definir las rutas de navegación y renderizar el `Navbar`. | Fase 3 |
| **RN-02** | RN | **Gestión de Server State:** Prohibido el uso de `useEffect` + `useState` para sincronización de datos remotos en componentes; la comunicación con la API se delega a TanStack Query y a la capa `services/` (`categorias.service.ts`, `productos.service.ts`). | Fase 3 |
| **RN-03** | RN | **Backend REST Robusto:** Endpoints de `Categoria`, `Producto` y `ProductoCategoria` construidos en FastAPI bajo arquitectura Models-Schemas-Service-Router, con paginación (`offset`/`limit`), filtros dinámicos y respuesta estructurada `{ total, items }`. | Fase 2 |
| **RN-04** | RN | **Soporte Dual PUT / PATCH:** Los routers de actualización admiten tanto `PUT` como `PATCH` con `exclude_unset=True` para actualizaciones totales o parciales sin excepciones de contrato. | Fase 2 |
| **RN-05** | RN | **CORS Habilitado:** Middleware en FastAPI configurado para admitir solicitudes desde el origen del frontend (`http://localhost:5173` y `http://127.0.0.1:5173`). | Fase 1 / Fase 2 |
| **RN-06** | RN | **Demostración REST Client:** Endpoints de `Producto` y `ProductoCategoria` verificados y demostrados de forma autosuficiente mediante archivo `productos.http`. | Fase 2 / Fase 4 |
| **RN-07** | RN | **Tipado Estricto TypeScript:** Interfaces `Categoria` y `Producto` definidas formalmente en `src/types/`. Props tipados en el 100% de los componentes `.tsx` sin errores en `tsc`. | Fase 1 / Fase 3 |
| **RN-08** | RN | **Empaquetado Limpio:** Entrega en dos archivos `.zip` independientes (`frontend` y `backend`), excluyendo `node_modules`, `.venv`, `.git` y cachés temporales. | Fase 4 |

---

## 3. Desglose de Fases y Tablero Kanban

```text
[ Fase 1: Infraestructura Base, Dependencias & Archivos Semilla ]
                               ↓
[ Fase 2: Backend — Modelos UML, Servicios & Endpoints Optimizados ]
                               ↓
[ Fase 3: Frontend — Servicios, TanStack Query, Enrutamiento & Vistas ]
                               ↓
[ Fase 4: Pruebas Integradas E2E, Verificación Estática & Empaquetado ]
```

### 3.1. Tablero Kanban de Estado de Tareas

| ID Tarea | Tarea | Fase | Estado | Componentes / Módulos Afectados |
| :---: | :--- | :---: | :---: | :--- |
| **1.1** | Migración de archivos base sin cambios desde Unidad 6 | Fase 1 | ✅ **Done** | `requirements.txt`, `pytest.ini`, `app/database.py`, `validators.py`, componentes `.tsx` base, `tsconfig*.json`, `index.css` |
| **1.2** | Configuración de orquestación raíz y dependencias de frontend (`package.json`) | Fase 1 | ⏳ **Pendiente** | `package.json`, `unidad7_frontend/package.json` (`@tanstack/react-query`, `react-router-dom`) |
| **1.3** | Configuración de proveedores raíz (`QueryClientProvider`, `BrowserRouter`) con defaults de caché | Fase 1 | ⏳ **Pendiente** | `unidad7_frontend/src/main.tsx` |
| **2.1** | Adaptación de modelos SQLModel según UML (Auditoría, `deleted_at`, `Decimal`, `imagenes_url`) | Fase 2 | ⏳ **Pendiente** | `app/models/categoria.py`, `app/models/producto.py` |
| **2.2** | Schemas DTO, validaciones declarativas y respuestas paginadas (`{ total, items }`) | Fase 2 | ⏳ **Pendiente** | `app/modules/categoria/schemas.py`, `app/modules/producto/schemas.py` |
| **2.3** | Capa de servicio y router de Categorías (CRUD, soft delete, paginación, filtros, PUT/PATCH) | Fase 2 | ⏳ **Pendiente** | `app/modules/categoria/services.py`, `routers.py` |
| **2.4** | Capa de servicio y router de Productos y relación N:N (`ProductoCategoriaAssign`) | Fase 2 | ⏳ **Pendiente** | `app/modules/producto/services.py`, `routers.py` |
| **2.5** | Middleware CORS, instancia de aplicación y configuración de entorno | Fase 2 | ⏳ **Pendiente** | `app/main.py`, `.env.example` |
| **2.6** | Suite integral de solicitudes HTTP (`productos.http`) para REST Client | Fase 2 | ⏳ **Pendiente** | `unidad7_backend/productos.http` |
| **3.1** | Actualización de contratos de datos TypeScript (`Categoria`, `Producto`, `PaginatedResponse`) | Fase 3 | ⏳ **Pendiente** | `src/types/categoria.ts`, `producto.ts`, `index.ts` |
| **3.2** | Creación de capa de servicios HTTP (`categorias.service.ts`, `productos.service.ts`) | Fase 3 | ⏳ **Pendiente** | `src/services/categorias.service.ts`, `productos.service.ts`, `api.ts` |
| **3.3** | Integración de TanStack Query para Categorías (`useQuery`, `useMutation`, `invalidateQueries`) | Fase 3 | ⏳ **Pendiente** | `src/pages/CategoriasPage.tsx` |
| **3.4** | Adaptación de `Navbar.tsx` con enlaces activos de React Router (`NavLink`) | Fase 3 | ⏳ **Pendiente** | `src/components/Navbar.tsx` |
| **3.5** | Implementación de páginas `CategoriasPage.tsx` (modal `useState`) y `ProductsPage.tsx` (catálogo) | Fase 3 | ⏳ **Pendiente** | `src/pages/CategoriasPage.tsx`, `src/pages/ProductsPage.tsx` |
| **3.6** | Refactorización de `App.tsx` (exclusivo para rutas y Navbar, sin lógica de negocio) | Fase 3 | ⏳ **Pendiente** | `src/App.tsx` |
| **4.1** | Smoke Test E2E de integración Full Stack (CRUD Categorías y navegación reactiva) | Fase 4 | ⏳ **Pendiente** | Navegador / Consola / Servidores concurrentes |
| **4.2** | Demostración REST Client de Producto y ProductoCategoria | Fase 4 | ⏳ **Pendiente** | `productos.http` |
| **4.3** | Verificación estática TypeScript (`tsc`) y ejecución de tests backend (`pytest`) | Fase 4 | ⏳ **Pendiente** | `tsc -b`, `pytest` |
| **4.4** | Limpieza de artefactos y empaquetado final en dos archivos `.zip` para entrega | Fase 4 | ⏳ **Pendiente** | Scripts de purgado y compresión `.zip` |

---

### FASE 1: Infraestructura Base, Dependencias y Archivos Semilla
> **Estado:** **EN PROGRESO**  
> **Criterio de Dependencia:** Nivel 0 (Base). Establece los paquetes y la estructura de directorios requerida tanto en frontend como en backend.

#### Tarea 1.1: Migración de archivos base sin cambios desde Unidad 6
- **Acción:** Copiar archivos de infraestructura e inicialización que no requieren alteración estructural:
  - Backend: `requirements.txt`, `pytest.ini`, `app/database.py`, `app/modules/producto/validators.py` y archivos `__init__.py`.
  - Frontend: `index.html`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `pnpm-workspace.yaml`, `src/index.css` y los componentes de presentación `CategoriaCard.tsx`, `CategoriaList.tsx`, `CategoriaModal.tsx`.
- **Estado:** ✅ **Done**

#### Tarea 1.2: Configuración de orquestación raíz y dependencias de frontend
- **Acción:**
  - Configurar `package.json` raíz con scripts concurrentes apuntando a `unidad7_frontend` y `unidad7_backend`.
  - Crear `unidad7_frontend/package.json` incorporando dependencias esenciales:
    - React 19 (`react`, `react-dom`).
    - TanStack Query (`@tanstack/react-query`).
    - React Router (`react-router-dom`).
    - Tailwind CSS v4 (`@tailwindcss/vite`, `tailwindcss`).
  - Crear `unidad7_frontend/vite.config.ts`.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-02, RN-07.

#### Tarea 1.3: Configuración de proveedores raíz en `main.tsx`
- **Acción:** Crear `unidad7_frontend/src/main.tsx` envolviendo la aplicación en:
  - `<QueryClientProvider client={queryClient}>` configurado con opciones de producción:
    ```typescript
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5, // 5 minutos de validez en caché
          refetchOnWindowFocus: false, // evita refetches accidentales al cambiar de foco
          retry: 1,
        },
      },
    });
    ```
  - `<BrowserRouter>` para habilitar el enrutamiento declarativo.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-01, RN-02.

---

### FASE 2: Backend — Modelos UML, Servicios y Endpoints Optimizados
> **Estado:** ⏳ **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 1. Provee la API REST requerida para el catálogo, alineada a `docs/UML_FOOD_STORE.svg` y `docs/guidelines/unidad7_guia_maestra.md`.

#### Tarea 2.1: Adaptación de modelos SQLModel según UML
- **Acción:**
  - `Categoria` (`app/models/categoria.py`):
    - Clave primaria `id: Optional[int] = Field(default=None, primary_key=True)`.
    - `nombre: str = Field(max_length=100, unique=True, nullable=False, index=True)`.
    - `descripcion: str = Field(default="", nullable=False)`.
    - Campos de auditoría: `created_at: datetime`, `updated_at: datetime`, `deleted_at: Optional[datetime] = None`.
    - Relación N:N con `Producto` a través de `ProductoCategoria`.
  - `Producto` (`app/models/producto.py`):
    - `id: Optional[int] = Field(default=None, primary_key=True)`.
    - `nombre: str = Field(max_length=150, nullable=False, index=True)`.
    - `descripcion: Optional[str] = Field(default=None)`.
    - `precio_base: float = Field(ge=0, nullable=False)`.
    - `imagenes_url: list[str] = Field(default_factory=list, sa_column=Column(JSON))` (o compatible).
    - `disponible: bool = Field(default=True, nullable=False)`.
    - Campos de auditoría: `created_at`, `updated_at`, `deleted_at`.
    - Sin campos de stock (excluido por SRP).
  - `ProductoCategoria` (`app/models/producto.py`):
    - Clave compuesta `producto_id` (`foreign_key="producto.id"`) y `categoria_id` (`foreign_key="categoria.id"`).
    - `es_principal: bool = Field(default=False, nullable=False)`.
    - `created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)`.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-03.

#### Tarea 2.2: Schemas DTO, validaciones declarativas y respuestas paginadas
- **Acción:**
  - `app/modules/categoria/schemas.py`:
    - `CategoriaBase(nombre: str, descripcion: Optional[str] = "")`.
    - `CategoriaCreate(CategoriaBase)`.
    - `CategoriaRead(CategoriaBase)` con `id: int`.
    - `CategoriaUpdate(nombre: Optional[str] = None, descripcion: Optional[str] = None)`.
    - `CategoriaPaginatedResponse(total: int, items: List[CategoriaRead])`.
  - `app/modules/producto/schemas.py`:
    - `ProductoBase(nombre: str, descripcion: Optional[str] = None, precio_base: float, disponible: bool = True)`.
    - `ProductoCreate(ProductoBase)`.
    - `ProductoRead(ProductoBase)` con `id: int, categorias: List[CategoriaRead] = []`.
    - `ProductoUpdate(nombre: Optional[str] = None, descripcion: Optional[str] = None, precio_base: Optional[float] = None, disponible: Optional[bool] = None)`.
    - `ProductoPaginatedResponse(total: int, items: List[ProductoRead])`.
    - `ProductoCategoriaAssign(producto_id: int, categoria_id: int, es_principal: bool = False)`.
    - `ProductoCategoriaRead(producto_id: int, categoria_id: int, es_principal: bool)`.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-03.

#### Tarea 2.3: Capa de servicio y router de Categorías
- **Acción:**
  - `app/modules/categoria/services.py`:
    - Creación con validación de nombre duplicado.
    - Listado con filtros dinámicos (`search: Optional[str]` sobre `nombre.ilike()`), paginación (`offset`, `limit`), conteo atómico (`select(func.count()).select_from(...)`) y filtrado de registros activos (`deleted_at.is_(None)`).
    - Actualización soportando `model_dump(exclude_unset=True)`.
    - Borrado lógico (`deleted_at = datetime.now()`) o físico según parámetro.
  - `app/modules/categoria/routers.py`:
    - `POST /categorias/` (Status 201 Created).
    - `GET /categorias/` con `offset = Query(0, ge=0)`, `limit = Query(50, ge=1, le=100)` y `search: Optional[str] = None`. Retorna `CategoriaPaginatedResponse`.
    - `GET /categorias/{id}` (Detalle o 404).
    - `PUT /categorias/{id}` y `PATCH /categorias/{id}` (Actualización de datos).
    - `DELETE /categorias/{id}` (Status 204 No Content).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-03, RN-04.

#### Tarea 2.4: Capa de servicio y router de Productos y relación N:N
- **Acción:**
  - `app/modules/producto/services.py` y `routers.py`:
    - CRUD completo de productos con filtros (`nombre: Optional[str]`, `disponible: Optional[bool]`), paginación (`offset`, `limit`) y carga ansiosa (*Eager Loading*) con `selectinload(Producto.categorias)` para prevenir $N+1$.
    - `POST /productos/` (Status 201 Created).
    - `GET /productos/` con parámetros `Query` y retorno `ProductoPaginatedResponse`.
    - `GET /productos/{id}` (Detalle con categorías anidadas).
    - `PUT /productos/{id}` y `PATCH /productos/{id}`.
    - `DELETE /productos/{id}` (Status 204 No Content).
    - **Gestión de la relación N:N (`ProductoCategoria`):**
      - `POST /productos/categorias/asignar` (recibe `ProductoCategoriaAssign`, actualiza o crea el vínculo con `es_principal`).
      - `POST /productos/{id}/categorias/{categoria_id}` (alias de conveniencia REST).
      - `DELETE /productos/{producto_id}/categorias/{categoria_id}` (desvincula la categoría con 204).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-03, RN-06.

#### Tarea 2.5: Middleware CORS, instancia de aplicación y configuración de entorno
- **Acción:**
  - En `app/main.py`: Configurar `CORSMiddleware` para `http://localhost:5173` y `http://127.0.0.1:5173`, registrar routers y actualizar título/descripción a Unidad 7.
  - En `.env.example`: Configurar variables para base de datos de Unidad 7 (`tp7_server_state` o SQLite dev).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-05.

#### Tarea 2.6: Suite de pruebas REST Client (`productos.http`)
- **Acción:**
  - Adaptar el archivo `unidad7_backend/productos.http` estructurado en bloques ejecutables:
    1. CRUD y búsqueda paginada de Categorías (`POST`, `GET /?search=...`, `PATCH`, `DELETE`).
    2. CRUD y búsqueda de Productos con filtros (`GET /?nombre=...&disponible=true`).
    3. Asignación N:N mediante `POST /productos/categorias/asignar` (verificando `es_principal: true/false`).
    4. Desasignación de relación mediante `DELETE /productos/{id}/categorias/{cat_id}`.
    5. Validación de errores semánticos (`404`, `409`, `422`).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-06.

---

### FASE 3: Frontend — Capa de Servicios, Server State y Navegación
> **Estado:** ⏳ **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 2. Conecta la interfaz de usuario con la API REST mediante TanStack Query y desacopla la navegación mediante React Router.

#### Tarea 3.1: Actualización de contratos de datos TypeScript
- **Acción:**
  - `src/types/categoria.ts`:
    ```typescript
    export interface Categoria {
      id: number;
      nombre: string;
      descripcion?: string;
    }
    export interface CategoriaCreate {
      nombre: string;
      descripcion?: string;
    }
    export interface CategoriaUpdate {
      nombre?: string;
      descripcion?: string;
    }
    export interface PaginatedResponse<T> {
      total: number;
      items: T[];
    }
    ```
  - `src/types/producto.ts`:
    ```typescript
    import type { Categoria } from "./categoria";

    export interface Producto {
      id: number;
      nombre: string;
      descripcion: string | null;
      precio_base: number;
      disponible: boolean;
      categorias: Categoria[];
    }
    export interface ProductoCreate {
      nombre: string;
      descripcion?: string;
      precio_base: number;
      disponible?: boolean;
    }
    ```
  - `src/types/index.ts`: Re-exportación limpia de todas las interfaces.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-07.

#### Tarea 3.2: Implementación de la capa de servicios HTTP (`src/services/`)
- **Acción:**
  - Crear `src/services/api.ts`: Constante `API_BASE_URL = "http://localhost:8000"` y utilidades de fetch con manejo de errores.
  - Crear `src/services/categorias.service.ts`:
    - `getCategorias(offset, limit, search)`: Retorna `Promise<PaginatedResponse<Categoria>>`.
    - `createCategoria(payload: CategoriaCreate)`: `POST /categorias/`.
    - `updateCategoria({ id, data }: { id: number; data: CategoriaUpdate })`: `PATCH /categorias/{id}`.
    - `deleteCategoria(id: number)`: `DELETE /categorias/{id}`.
  - Crear `src/services/productos.service.ts`:
    - `getProductos(offset, limit, nombre, disponible)`: Retorna `Promise<PaginatedResponse<Producto>>`.
    - `getProductoById(id: number)`: `GET /productos/{id}`.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-02.

#### Tarea 3.3: Integración de TanStack Query para Categorías
- **Acción:**
  - En `src/pages/CategoriasPage.tsx`:
    - `useQuery`:
      ```typescript
      const { data, isLoading, isError, error } = useQuery({
        queryKey: ["categorias", { search }],
        queryFn: () => getCategorias(0, 50, search),
      });
      ```
    - Mutaciones (`useMutation`):
      - `createMutation`: Invoca `createCategoria`, y en `onSuccess` ejecuta `queryClient.invalidateQueries({ queryKey: ["categorias"] })` y cierra el modal.
      - `updateMutation`: Invoca `updateCategoria`, y en `onSuccess` invalida caché y cierra el modal.
      - `deleteMutation`: Invoca `deleteCategoria`, y en `onSuccess` invalida caché.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-02.

#### Tarea 3.4: Adaptación de `Navbar.tsx` con React Router
- **Acción:**
  - Reemplazar hipervínculos muertos `<a href="#">` por `<NavLink>` de `react-router-dom`.
  - Aplicar función de clases activas:
    ```tsx
    const getLinkClasses = ({ isActive }: { isActive: boolean }) =>
      `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        isActive
          ? "bg-indigo-600 text-white shadow-sm"
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
      }`;
    ```
  - Enlaces de navegación: **Categorías** (`/` y `/categorias`) y **Productos** (`/productos`).
  - Actualizar branding a *"Food Store Admin"* y badge a *"TP7"*.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-01.

#### Tarea 3.5: Implementación de páginas `CategoriasPage.tsx` y `ProductsPage.tsx`
- **Acción:**
  - `src/pages/CategoriasPage.tsx`:
    - **Client State (`useState`):**
      - `isModalOpen: boolean` (control de apertura del modal).
      - `editingCategoria: Categoria | null` (categoría cargada para edición).
      - `search: string` (término de búsqueda dinámico).
    - **Server State (TanStack Query):** Consume `useQuery` y las mutaciones descriptas en Tarea 3.3.
    - Renderiza la cabecera con botón `"+ Añadir Categoría"`, barra de búsqueda, la tabla `CategoriaList` (alimentada con `data?.items ?? []`) y el modal flotante `CategoriaModal`.
  - `src/pages/ProductsPage.tsx`:
    - Consume `useQuery({ queryKey: ["productos"], queryFn: ... })`.
    - Presenta una grilla de tarjetas de productos mostrando nombre, descripción, precio base formateado (`$precio`), badges de las categorías asociadas e indicador de disponibilidad (`disponible`).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-07.

#### Tarea 3.6: Refactorización de `App.tsx` (Sin lógica de negocio)
- **Acción:**
  - `App.tsx` debe contener **exclusivamente**:
    ```tsx
    export function App() {
      return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans">
          <Navbar />
          <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<CategoriasPage />} />
              <Route path="/categorias" element={<CategoriasPage />} />
              <Route path="/productos" element={<ProductsPage />} />
            </Routes>
          </main>
        </div>
      );
    }
    ```
  - **Cero lógica de negocio**, cero `useState` de datos y cero `fetch` en `App.tsx`.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-01.

---

### FASE 4: Pruebas Integradas E2E, Verificación Estática y Empaquetado
> **Estado:** ⏳ **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 3. Consolida la entrega completa y asegura el cumplimiento de la rúbrica de evaluación.

#### Tarea 4.1: Smoke Test E2E de integración Full Stack
- **Acción:** Levantar el entorno con `pnpm dev` y comprobar de extremo a extremo:
  1. Navegación fluida entre `/categorias` y `/productos` sin recarga de página mediante `NavLink`.
  2. Carga inicial de categorías en la tabla vía TanStack Query con skeleton o estado de carga.
  3. Creación de una nueva categoría desde el modal y verificación del refresco instantáneo sin parpadeo.
  4. Edición de categoría existente y actualización reactiva.
  5. Eliminación de categoría y remoción inmediata de la tabla tras la invalidación de la caché.
  6. Visualización de productos en `ProductsPage` con sus categorías asociadas.
- **Estado:** ⏳ **Pendiente**

#### Tarea 4.2: Demostración REST Client de Producto y ProductoCategoria
- **Acción:** Ejecutar las peticiones de `productos.http` verificando que los endpoints de Producto y ProductoCategoria responden con códigos HTTP semánticos (200, 201, 204, 404, 409, 422).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-06.

#### Tarea 4.3: Verificación estática TypeScript y suite pytest
- **Acción:**
  - Compilación limpia de frontend: `pnpm build:front` (`tsc -b && vite build`) sin errores de TypeScript.
  - Ejecución de suite de pruebas backend: `pytest` en `unidad7_backend/` con base de datos en memoria.
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-07.

#### Tarea 4.4: Empaquetado para entrega según consigna
- **Acción:**
  - Generar los dos archivos comprimidos independientes:
    - `Varela_Santiago_TPI_unidad7_frontend.zip` (eliminando estrictamente `node_modules/`).
    - `Varela_Santiago_TPI_unidad7_backend.zip` (sin `.venv/` ni `__pycache__/`).
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-08.

---

## 4. Checklist de Control de Entrega

- [ ] **Estructura de Carpetas:** El frontend cuenta con las carpetas `src/components/`, `src/types/`, `src/services/` y `src/pages/`.
- [ ] **Arquitectura de `App.tsx`:** `App.tsx` carece totalmente de lógica de negocio o llamadas a API; solo define rutas con React Router y renderiza el `Navbar`.
- [ ] **Server State con TanStack Query:** El consumo de la API de Categorías utiliza `useQuery` y `useMutation`, con invalidación de caché (`queryClient.invalidateQueries`) tras cada operación.
- [ ] **Modal Reactivo:** El formulario de alta y edición se presenta dentro de `CategoriaModal.tsx` controlado con `useState` booleano en `CategoriasPage.tsx`.
- [ ] **Navegación con React Router:** Separación en páginas independientes (`CategoriasPage` y `ProductsPage`) navegables desde la barra de navegación sin recarga.
- [ ] **Catálogo de Productos en Frontend:** `ProductsPage.tsx` muestra la grilla de productos con sus categorías asociadas y disponibilidad.
- [ ] **Tipado Estricto TypeScript:** Interfaces `Categoria` y `Producto` definidas formalmente; props tipados en todos los componentes `.tsx`; 0 errores en compilación de TypeScript (`tsc`).
- [ ] **Backend Modular FastAPI:** Arquitectura Models-Schemas-Service-Router con Pydantic y SQLModel.
- [ ] **Paginación y Filtros Dinámicos:** Endpoints de colección con parámetros `Query` (`offset`, `limit`, `search`/`nombre`) y respuesta estructurada `{ total, items }`.
- [ ] **Endpoints de Producto y ProductoCategoria:** Endpoints construidos, funcionales y demostrados mediante archivo `.http` (incluyendo asignación con `es_principal`).
- [ ] **CORS Habilitado:** Configurado en FastAPI para permitir peticiones desde el origen del frontend (`http://localhost:5173`).
- [ ] **Estilizado Tailwind CSS:** Clases aplicadas coherentemente y sin errores visuales.
- [ ] **Archivos de Entrega:** Dos archivos `.zip` independientes (`frontend` y `backend`) excluyendo `node_modules` y `.venv`.
