# Resolución y Plan de Ejecución — Trabajo Práctico 7

> **Materia:** Programación IV (Tecnicatura Universitaria en Programación a Distancia - UTN)  
> **Tema:** Server State (TanStack Query) y Navegación (React Router + TypeScript) en Frontend; Optimización de Endpoints y Relaciones en Backend (FastAPI + SQLModel / PostgreSQL).  
> **Estrategia:** Descomposición combinada **"Bottom-Up"** (orden cronológico de hojas a raíz en el grafo de dependencias) + **"Walking Skeleton"** (esqueleto mínimo compilable en verde desde la Fase 1), orientada a tablero Kanban. Cada tarea referencia explícitamente las Historias de Usuario (HU), Reglas de Negocio (RN) y los lineamientos de `docs/consigna.md`, `docs/guidelines/unidad7_guia_maestra.md`, `docs/guidelines/javaismos_guia.md` y `docs/UML_FOOD_STORE.svg`.

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
  2. `Producto` (CRUD en Backend y schemas DTO; catálogo paginado con filtro en `ProductsPage` y vista de detalle en `ProductDetailPage` en Frontend).
  3. `ProductoCategoria` (tabla intermedia N:N con campo `es_principal` y endpoints en Backend).
* **Entidades Excluidas (Fuera de Alcance de la Consigna):**
  * Dominio **Identidad & Acceso**: `Usuario`, `Rol`, `UsuarioRol`, `DireccionEntrega`.
  * Dominio **Ventas & Transacciones**: `FormaPago`, `EstadoPedido`, `Pedido`, `DetallePedido`, `HistorialEstadoPedido`.
  * Dominio **Inventario / Stock**: Excluido de `Producto` por principio de responsabilidad única (anotación explícita del UML: *"stock excluido: dominio INVENTARIO (SRP)"*).

### 1.4. Invariantes Arquitectónicos y Prevención de Antipatrones (Guías Maestras)
1. **Simetría y Conteo Atómico en SQL (`unidad7_guia_maestra.md` §1.2–1.3):**
   * Prohibido calcular el total en memoria Python mediante `len(session.exec(query).all())`.
   * El servicio construye primero la consulta base `query = select(Model)`, encadena **todos** los filtros dinámicos (`.where(...)`), deriva el conteo con `select(func.count()).select_from(query.subquery())` y recién al final aplica `.offset(offset).limit(limit)`.
2. **Separación Estricta de Capas y Python Idiomático (`unidad7_guia_maestra.md` §1.6, `javaismos_guia.md`):**
   * `models`: solo definición relacional (`table=True`, `Field`, `Relationship`).
   * `schemas`: contratos DTO (`Base`, `Create`, `Read`, `Update`, `PaginatedResponse`) y validadores de dominio, sin lógica de sesión.
   * `services`: lógica de negocio pura y consultas SQLModel; retorna entidades, tuplas `(total, items)` o `None`/`bool`, sin importar `HTTPException` ni `fastapi.Query`.
   * `routers`: validación declarativa de parámetros HTTP (`Query(ge=..., le=...)`), inyección de sesión (`Depends(get_session)`) y traducción a códigos de estado semánticos (`200`, `201`, `204`, `404`, `409`, `422`).
   * Cero *java-ismos*: acceso directo a atributos y validación declarativa con Pydantic/SQLModel sin getters/setters triviales.
3. **Contrato de Error en `fetch` para TanStack Query (`unidad7_guia_maestra.md` §2.3):**
   * Dado que `fetch` nativo no rechaza promesas ante respuestas HTTP `4xx`/`5xx`, toda función en `src/services/` debe verificar explícitamente `if (!res.ok) throw new Error(...)` (extrayendo `detail` del JSON de FastAPI cuando esté disponible) para activar correctamente `isError` en `useQuery` y `useMutation`.
4. **Frontera Client State vs. Server State (`unidad7_guia_maestra.md` §2.1, §2.5):**
   * Prohibido copiar `data` de `useQuery` dentro de un `useState` local para renderizar tablas o grillas.
   * `useState` se reserva exclusivamente para **Client State**: control booleano del modal (`isModalOpen`), ítem seleccionado para edición (`editingCategoria`), inputs de formulario, término de búsqueda (`search`/`nombre`) y página actual (`page`).
   * En TanStack Query v5, la invalidación utiliza siempre la firma de objeto: `queryClient.invalidateQueries({ queryKey: ["categorias"] })`, y toda variable de filtro o paginación que afecte a `queryFn` se incluye en `queryKey`.
5. **Enrutamiento SPA Puro y Tipado de Parámetros (`unidad7_guia_maestra.md` §3.2–3.4):**
   * `App.tsx` carece por completo de estado y llamadas HTTP; únicamente renderiza `<Navbar />` y el bloque `<Routes>`.
   * Prohibido el uso de `<a href="...">` para rutas internas; se emplea `<NavLink>`, `<Link>` o `useNavigate()`.
   * En rutas dinámicas (`/productos/:id`), los parámetros extraídos con `useParams()` (`string | undefined`) se convierten explícitamente con `Number(id)` y se validan con `!Number.isNaN(numericId)` antes de habilitar la consulta (`enabled`).
6. **Trazabilidad Explícita en Código (`[Consigna TP7]` + `[Diagrama UML]`):**
   * Cada archivo, módulo y componente implementado a lo largo de todas las fases del proyecto debe incluir comentarios explícitos en su cabecera y bloques críticos especificando:
     - `[Consigna TP7 - ...]`: El inciso, requerimiento funcional o regla de `docs/consigna.md` que satisface.
     - `[Diagrama UML - ...]`: La entidad, atributo, clave (PK/FK), relación relacional (1:N, N:N) o principio de diseño (ej. SRP) de `docs/UML_FOOD_STORE.svg` al que corresponde.
   * Queda estrictamente prohibido mantener referencias obsoletas o residuales a `TP6` o `unidad6_backend` en los módulos de producción de la Unidad 7.
7. **Estrategia Combinada Bottom-Up + Walking Skeleton con Montaje Progresivo (Feedback Visual Continuo):**
   * **Orden Bottom-Up (Grafo Acíclico de Dependencias):** Ningún archivo se crea antes que los módulos hoja que importa (`src/types/categoria.ts` precede a los componentes presentacionales de `src/components/`, y el esqueleto `src/App.tsx` precede al consumidor raíz `src/main.tsx`).
   * **Alcance Walking Skeleton y Montaje Progresivo en `App.tsx`:** Al cierre de la Fase 1 el proyecto cuenta con un esqueleto funcional de extremo a extremo que compila en verde (`tsc -b --noEmit` = `0 errores`). Dado que en una SPA React el único punto de entrada visual al ejecutar el servidor de desarrollo (`pnpm dev`) es `App.tsx`, el *Walking Skeleton* **no permanece inerte ni congela la visualización hasta el final de la Fase 3**: a medida que cada vista o barra de navegación se completa en orden *Bottom-Up* (comenzando por `CategoriasPage` y `CategoriaModal` en la Tarea 3.3, siguiendo con `Navbar` en la 3.4 y las vistas de productos en la 3.5), **se monta de inmediato en `App.tsx`** para garantizar inspección visual en tiempo real (HMR), validación de estilos Tailwind y prueba interactiva antes de avanzar al siguiente eslabón.
---
## 2. Matriz de Trazabilidad Rápida

| ID | Tipo | Descripción Sintética | Fase Asignada |
| :--- | :---: | :--- | :---: |
| **HU-01** | HU | Listado reactivo de categorías consumiendo la API mediante `useQuery` de TanStack Query, con estados de carga (`isLoading`), error (`isError`), búsqueda (`search` en `queryKey`) y renderizado tabular con total de registros. | Fase 3 |
| **HU-02** | HU | Formulario de alta y edición de categorías dentro de modal flotante (`CategoriaModal.tsx`), controlado con `useState` booleano en la página, ejecutando mutaciones con `useMutation` (`isPending`, manejo de `error`) e invalidando la caché (`invalidateQueries`). | Fase 3 |
| **HU-03** | HU | Eliminación de categorías desde la tabla mediante `useMutation` con confirmación previa, deshabilitación durante `isPending` y refetch automático de la caché. | Fase 3 |
| **HU-04** | HU | Navegación SPA sin recarga entre `CategoriasPage` (`/` y `/categorias`), `ProductsPage` (`/productos`) y `ProductDetailPage` (`/productos/:id`) utilizando React Router (`BrowserRouter`, `Routes`, `Route`, `NavLink`, `useNavigate`, `useParams`). | Fase 3 |
| **HU-05** | HU | Visualización del catálogo de productos en `ProductsPage.tsx` y su detalle en `ProductDetailPage.tsx` mediante `useQuery`, con filtro por nombre, controles de paginación (`offset`/`limit` sobre `total`), tarjetas con badges de categorías asociadas e indicador de disponibilidad. | Fase 3 |
| **RN-01** | RN | **Desacoplamiento de `App.tsx`:** `App.tsx` no debe contener lógica de negocio, estado de datos ni llamadas a APIs; su rol exclusivo es definir las rutas de navegación y renderizar el `Navbar`. | Fase 3 |
| **RN-02** | RN | **Gestión de Server State:** Prohibido el uso de `useEffect` + `useState` para sincronización de datos remotos o copiar `data` de `useQuery` a estado local; la comunicación con la API se delega a TanStack Query y a la capa `services/` (con verificación obligatoria `if (!res.ok) throw new Error(...)`). | Fase 3 |
| **RN-03** | RN | **Backend REST Robusto y Paginado:** Endpoints de `Categoria`, `Producto` y `ProductoCategoria` bajo arquitectura Models-Schemas-Service-Router, con validación declarativa `fastapi.Query(ge=..., le=...)`, filtros dinámicos, conteo SQL atómico (`func.count()`) y respuesta estructurada `{ total, items }`. | Fase 2 |
| **RN-04** | RN | **Soporte Dual PUT / PATCH:** Los routers de actualización admiten tanto `PUT` como `PATCH` con `exclude_unset=True` para actualizaciones totales o parciales sin excepciones de contrato. | Fase 2 |
| **RN-05** | RN | **CORS Habilitado:** Middleware en FastAPI configurado para admitir solicitudes (incluyendo preflight `OPTIONS`) desde el origen del frontend (`http://localhost:5173` y `http://127.0.0.1:5173`). | Fase 1 / Fase 2 |
| **RN-06** | RN | **Demostración REST Client:** Endpoints de `Producto` y `ProductoCategoria` verificados y demostrados de forma autosuficiente mediante archivo `productos.http`. | Fase 2 / Fase 4 |
| **RN-07** | RN | **Tipado Estricto TypeScript:** Interfaces `Categoria`, `Producto` y `PaginatedResponse<T>` definidas formalmente en `src/types/`. Props tipados en el 100% de los componentes `.tsx` sin errores en `tsc -b`. | Fase 1 / Fase 3 |
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
| **1.1** | Migración de archivos base y contratos hoja (`src/types/categoria.ts`) desde Unidad 6 | Fase 1 | ✅ **Done** | `requirements.txt`, `pytest.ini`, `app/database.py`, `validators.py`, `src/types/categoria.ts`, componentes `.tsx` base, `tsconfig*.json`, `index.css` |
| **1.2** | Configuración de orquestación raíz y dependencias de frontend (`package.json`) | Fase 1 | ✅ **Done** | `package.json`, `unidad7_frontend/package.json` (`@tanstack/react-query`, `react-router-dom`) |
| **1.3** | Configuración de *Walking Skeleton* (`App.tsx` mínimo) y proveedores raíz en `main.tsx` (`QueryClientProvider`, `BrowserRouter`) | Fase 1 | ✅ **Done** | `unidad7_frontend/src/App.tsx`, `unidad7_frontend/src/main.tsx` |
| **2.1** | Adaptación de modelos SQLModel según UML (Auditoría, `deleted_at`, `precio_base`, `imagenes_url`, `es_principal`) | Fase 2 | ✅ **Done** | `app/models/categoria.py`, `app/models/producto.py` |
| **2.2** | Schemas DTO, validaciones declarativas y respuestas paginadas (`{ total, items }`) | Fase 2 | ✅ **Done** | `unidad7_backend/app/modules/categoria/schemas.py`, `unidad7_backend/app/modules/producto/schemas.py`, módulos `__init__.py` |
| **2.3** | Capa de servicio y router de Categorías (CRUD, soft delete, `Query(ge, le)`, `func.count()`, PUT/PATCH) | Fase 2 | ✅ **Done** | `app/modules/categoria/services.py`, `routers.py` |
| **2.4** | Capa de servicio y router de Productos y relación N:N (`selectinload`, `ProductoCategoriaAssign`) | Fase 2 | ✅ **Done** | `app/modules/producto/services.py`, `routers.py` |
| **2.5** | Middleware CORS, instancia de aplicación y configuración de entorno | Fase 2 | ✅ **Done** | `app/main.py`, `.env.example` |
| **2.6** | Suite integral de solicitudes HTTP (`productos.http`) para REST Client | Fase 2 | ✅ **Done** | `unidad7_backend/productos.http` |
| **3.1** | Consolidación de contratos de datos TypeScript del catálogo (`Producto`, `ProductoCreate`, `index.ts`) | Fase 3 | ✅ **Done** | `src/types/categoria.ts`, `producto.ts`, `index.ts` |
| **3.2** | Creación de capa de servicios HTTP con control de `!res.ok` (`categorias.service.ts`, `productos.service.ts`) | Fase 3 | ✅ **Done** | `src/services/categorias.service.ts`, `productos.service.ts`, `api.ts` |
| **3.3** | Integración de TanStack Query para Categorías (`useQuery`, `useMutation`, `invalidateQueries`, adaptación de `CategoriaModal` y montaje inicial en `App.tsx`) | Fase 3 | ✅ **Done** | `src/pages/CategoriasPage.tsx`, `src/components/CategoriaModal.tsx`, `src/App.tsx` |
| **3.4** | Adaptación de `Navbar.tsx` con enlaces activos de React Router (`NavLink`) e incorporación al layout de `App.tsx` | Fase 3 | ⏳ **Pendiente** | `src/components/Navbar.tsx`, `src/App.tsx` |
| **3.5** | Implementación de vistas de catálogo `ProductsPage.tsx` (paginada) y `ProductDetailPage.tsx` (`:id`) | Fase 3 | ⏳ **Pendiente** | `src/pages/ProductsPage.tsx`, `src/pages/ProductDetailPage.tsx` |
| **3.6** | Cierre del *Walking Skeleton* en `App.tsx` con el enrutador completo (`Navbar` + `Routes` de Categorías y Productos, sin lógica de negocio) | Fase 3 | ⏳ **Pendiente** | `src/App.tsx` |
| **4.1** | Smoke Test E2E de integración Full Stack (CRUD Categorías, catálogo paginado y navegación reactiva) | Fase 4 | ⏳ **Pendiente** | Navegador / Consola / Servidores concurrentes |
| **4.2** | Demostración REST Client de Producto y ProductoCategoria | Fase 4 | ⏳ **Pendiente** | `productos.http` |
| **4.3** | Verificación estática TypeScript (`tsc`) y ejecución de tests backend (`pytest`) | Fase 4 | ⏳ **Pendiente** | `tsc -b`, `pytest` |
| **4.4** | Limpieza de artefactos y empaquetado final en dos archivos `.zip` para entrega | Fase 4 | ⏳ **Pendiente** | Scripts de purgado y compresión `.zip` |

---

### FASE 1: Infraestructura Base, Dependencias y Archivos Semilla
> **Estado:** ✅ **COMPLETADA**  
> **Criterio de Dependencia:** Nivel 0 (Base). Establece los paquetes y la estructura de directorios requerida tanto en frontend como en backend.

#### Tarea 1.1: Migración de archivos base y contratos hoja (`src/types/categoria.ts`)
- **Acción:** Copiar archivos de infraestructura e inicialización que no requieren alteración estructural y proveer el contrato hoja en orden *Bottom-Up*:
  - Backend: `requirements.txt`, `pytest.ini`, `app/database.py`, `app/modules/producto/validators.py` y archivos `__init__.py`.
  - Frontend (Base Hoja): `src/types/categoria.ts` (`Categoria`, `CategoriaCreate`, `CategoriaUpdate`, `PaginatedResponse<T>`) para satisfacer las importaciones de los componentes presentacionales desde el primer momento.
  - Frontend (Configuración y Presentación): `index.html`, `tsconfig.json`, `tsconfig.app.json`, `tsconfig.node.json`, `pnpm-workspace.yaml`, `src/index.css` y los componentes `CategoriaCard.tsx`, `CategoriaList.tsx`, `CategoriaModal.tsx`.
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
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-02, RN-07.

#### Tarea 1.3: Configuración de *Walking Skeleton* (`App.tsx`) y proveedores raíz en `main.tsx`
- **Acción:** Construir el esqueleto mínimo compilable en orden *Bottom-Up* (primero el módulo consumido `App.tsx` y luego la raíz `main.tsx`):
  - Crear `unidad7_frontend/src/App.tsx` (*Walking Skeleton*): contenedor esquelético libre de lógica de negocio con `<Routes>` inicial para garantizar compilación limpia (`tsc -b --noEmit` = `0 errores`) desde el cierre de la Fase 1, sirviendo como arnés de montaje progresivo en la Fase 3 a medida que se construyen las vistas.
  - Crear `unidad7_frontend/src/main.tsx` envolviendo `<App />` en:
    - `<QueryClientProvider client={queryClient}>` instanciado a nivel de módulo (fuera del árbol de renderizado) con políticas explícitas de ciclo de vida de caché (TanStack Query v5):
      ```typescript
      const queryClient = new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 1000 * 60 * 5, // 5 minutos de datos considerados "frescos" (FRESH)
            gcTime: 1000 * 60 * 10,   // 10 minutos en memoria antes de recolección de basura (INACTIVE)
            retry: 1,                 // 1 reintento automático ante fallos transitorios
            refetchOnWindowFocus: false, // evita refetches accidentales al cambiar de ventana
          },
        },
      });
      ```
    - `<BrowserRouter>` para conectar la aplicación con la History API del navegador.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-01, HU-04.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-07.
---

### FASE 2: Backend — Modelos UML, Servicios y Endpoints Optimizados
> **Estado:** ✅ **COMPLETADA**
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
- **Estado:** ✅ **Done**
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
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-03.

#### Tarea 2.3: Capa de servicio y router de Categorías
- **Acción:**
  - `app/modules/categoria/services.py`:
    - Creación con validación de nombre duplicado (retornando conflicto semántico `409` en el router si ya existe).
    - Listado con orden estricto de operaciones:
      1. Consulta base filtrando registros activos (`Categoria.deleted_at.is_(None)`).
      2. Filtro dinámico condicional (`search: Optional[str]` sobre `Categoria.nombre.ilike(f"%{search}%")`).
      3. Conteo atómico en motor SQL **sobre la consulta ya filtrada**: `select(func.count()).select_from(query.subquery())`.
      4. Extracción de ventana paginada: `query.offset(offset).limit(limit)`.
    - Actualización parcial/total soportando `model_dump(exclude_unset=True)` y refrescando `updated_at`.
    - Borrado lógico (`deleted_at = datetime.now(timezone.utc)`) o físico según parámetro.
  - `app/modules/categoria/routers.py`:
    - `POST /categorias/` (Status `201 Created`).
    - `GET /categorias/` con validación declarativa `offset: int = Query(0, ge=0)`, `limit: int = Query(50, ge=1, le=100)` y `search: Optional[str] = Query(None, max_length=100)`. Retorna `CategoriaPaginatedResponse`.
    - `GET /categorias/{id}` (Detalle `200 OK` o `404 Not Found`).
    - `PUT /categorias/{id}` y `PATCH /categorias/{id}` (Actualización total o parcial).
    - `DELETE /categorias/{id}` (Status `204 No Content`).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-03, RN-04.

#### Tarea 2.4: Capa de servicio y router de Productos y relación N:N
- **Acción:**
  - `app/modules/producto/services.py` y `routers.py`:
    - CRUD completo de productos con filtros dinámicos (`nombre: Optional[str]`, `disponible: Optional[bool]`, `categoria_id: Optional[int]`), conteo simétrico (`func.count()` sobre subquery filtrada), paginación (`offset`, `limit`) y carga ansiosa (*Eager Loading*) con `selectinload(Producto.categorias)` para prevenir el problema de consultas $N+1$ y `DetachedInstanceError`.
    - `POST /productos/` (Status `201 Created`).
    - `GET /productos/` con parámetros validados mediante `Query(ge=0)` / `Query(ge=1, le=100)` y retorno `ProductoPaginatedResponse`.
    - `GET /productos/{id}` (Detalle con categorías anidadas o `404 Not Found`).
    - `PUT /productos/{id}` y `PATCH /productos/{id}`.
    - `DELETE /productos/{id}` (Status `204 No Content`).
    - **Gestión de la relación N:N (`ProductoCategoria`):**
      - `POST /productos/categorias/asignar` (Status `201 Created`, recibe `ProductoCategoriaAssign`, crea o actualiza el vínculo con `es_principal`).
      - `POST /productos/{id}/categorias/{categoria_id}` (alias de conveniencia RESTful para compatibilidad con pruebas previas).
      - `DELETE /productos/{producto_id}/categorias/{categoria_id}` (desvincula la categoría con `204 No Content` o `404 Not Found` si el vínculo no existe).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-05.
- **Reglas de Negocio asociadas:** RN-03, RN-06.

#### Tarea 2.5: Middleware CORS, instancia de aplicación y configuración de entorno
- **Acción:**
  - En `app/main.py`: Configurar `CORSMiddleware` para `http://localhost:5173` y `http://127.0.0.1:5173`, registrar routers y actualizar título/descripción a Unidad 7.
  - En `.env.example`: Configurar variables para base de datos de Unidad 7 (`tp7_server_state` o SQLite dev).
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-05.

#### Tarea 2.6: Suite de pruebas REST Client (`productos.http`)
- **Acción:**
  - Adaptar el archivo `unidad7_backend/productos.http` estructurado en bloques ejecutables:
    1. CRUD y búsqueda paginada de Categorías (`POST`, `GET /?search=...`, `PATCH`, `DELETE`).
    2. CRUD y búsqueda de Productos con filtros (`GET /?nombre=...&disponible=true`).
    3. Asignación N:N mediante `POST /productos/categorias/asignar` (verificando `es_principal: true/false`).
    4. Desasignación de relación mediante `DELETE /productos/{id}/categorias/{cat_id}`.
    5. Validación de errores semánticos (`404`, `409`, `422`).
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-06.

---

### FASE 3: Frontend — Capa de Servicios, Server State y Navegación
> **Estado:** 🔄 **EN PROGRESO**  
> **Criterio de Dependencia:** Nivel 2. Conecta la interfaz de usuario con la API REST mediante TanStack Query y desacopla la navegación mediante React Router.

#### Tarea 3.1: Consolidación de contratos de datos TypeScript del catálogo
- **Acción:**
  - Verificar `src/types/categoria.ts` (creado como nodo hoja en Tarea 1.1) y completar el árbol de tipos del catálogo:
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
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-07.

#### Tarea 3.2: Implementación de la capa de servicios HTTP (`src/services/`)
- **Acción:**
  - Crear `src/services/api.ts`: Constante `API_BASE_URL` (configurable vía `import.meta.env.VITE_API_URL || "http://localhost:8000"`) y helper de manejo de respuestas que garantice `if (!res.ok) throw new Error(...)` extrayendo el mensaje `detail` del backend.
  - Crear `src/services/categorias.service.ts` (con re-exportación o alias compatible si se importa como `categoriaService.ts`):
    - `getCategorias(offset = 0, limit = 50, search?: string)`: Construye `URLSearchParams`, verifica `!res.ok` y retorna `Promise<PaginatedResponse<Categoria>>`.
    - `createCategoria(payload: CategoriaCreate)`: `POST /categorias/`.
    - `updateCategoria({ id, data }: { id: number; data: CategoriaUpdate })`: `PATCH /categorias/{id}` (compatible con `PUT`).
    - `deleteCategoria(id: number)`: `DELETE /categorias/{id}`.
  - Crear `src/services/productos.service.ts`:
    - `getProductos(offset = 0, limit = 6, nombre?: string, disponible?: boolean)`: Retorna `Promise<PaginatedResponse<Producto>>`.
    - `getProductoById(id: number)`: `GET /productos/{id}` (retorna `Promise<Producto>`).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03, HU-05.
- **Reglas de Negocio asociadas:** RN-02.

#### Tarea 3.3: Integración de TanStack Query para Categorías, refinamiento de `CategoriaModal.tsx` y montaje visual en `App.tsx`
- **Acción:**
  - Refinar `src/components/CategoriaModal.tsx` para soportar estado controlado de los campos (`nombre`, `descripcion`) sincronizado al abrir para crear o editar, recibir `errorMessage?: string | null` para mostrar errores de validación/conflicto (`409`/`422`) dentro del modal sin perder lo escrito, y deshabilitar botones mientras `isSubmitting` sea `true`.
  - Implementar `src/pages/CategoriasPage.tsx`:
    - **Client State (`useState`):**
      - `isModalOpen: boolean` (control booleano de apertura del modal).
      - `editingCategoria: Categoria | null` (categoría seleccionada para edición).
      - `search: string` (término de búsqueda dinámico incluido en `queryKey`).
    - **Lectura declarativa con `useQuery` (RN-02):**
      ```typescript
      const { data, isLoading, isError, error, refetch } = useQuery({
        queryKey: ["categorias", { search }],
        queryFn: () => getCategorias(0, 50, search),
      });
      ```
      Renderiza directamente `data?.items ?? []` en `CategoriaList` sin copiar el listado en un `useState` local, mostrando contador `Total registradas: {data?.total ?? 0}`, estados de carga (`isLoading`) y alerta de error (`isError`) con reintento.
    - **Escritura imperativa con `useMutation` y flujo de sincronización en 5 pasos:**
      - `createMutation`: Invoca `createCategoria`, y en `onSuccess` ejecuta `queryClient.invalidateQueries({ queryKey: ["categorias"] })` y cierra el modal.
      - `updateMutation`: Invoca `updateCategoria`, y en `onSuccess` invalida `["categorias"]` y cierra el modal.
      - `deleteMutation`: Invoca `deleteCategoria`, y en `onSuccess` invalida `["categorias"]`.
  - **Montaje progresivo en `src/App.tsx` (Feedback Visual Inmediato):**
    - Conectar las rutas iniciales `/` y `/categorias` hacia `<CategoriasPage />` dentro del `<Routes>` de `App.tsx` (manteniendo un fallback para rutas aún no implementadas). Esto permite levantar `pnpm dev` de inmediato y verificar visualmente en el navegador la tabla, los estilos de `CategoriaModal` y el ciclo CRUD sin trabajar a ciegas.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-07.

#### Tarea 3.4: Adaptación de `Navbar.tsx` con React Router y montaje en `App.tsx`
- **Acción:**
  - Crear/adaptar `src/components/Navbar.tsx` reemplazando hipervínculos `<a href="#">` por `<NavLink>` de `react-router-dom`.
  - Aplicar función de clases activas:
    ```tsx
    const getLinkClasses = ({ isActive }: { isActive: boolean }) =>
      `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
        isActive
          ? "bg-indigo-600 text-white shadow-sm"
          : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
      }`;
    ```
  - Enlaces de navegación hacia **Categorías** (`/categorias`) y **Productos** (`/productos`).
  - Actualizar branding a *"Food Store Admin"* y badge a *"TP7"*.
  - Incorporar `<Navbar />` en la cabecera del layout de `src/App.tsx` para verificar visualmente la barra de navegación y el resaltado de ruta activa en el navegador.
- **Estado:** ⏳ **Pendiente**
- **Historias de Usuario asociadas:** HU-04.
- **Reglas de Negocio asociadas:** RN-01.

#### Tarea 3.5: Implementación de vistas de catálogo `ProductsPage.tsx` y `ProductDetailPage.tsx`
- **Acción:**
  - `src/pages/ProductsPage.tsx`:
    - **Client State (`useState`):** `page: number` (página actual base 1) y `nombre: string` (filtro de búsqueda que reinicia `setPage(1)` al cambiar).
    - **Server State (`useQuery`):** Calcula `offset = (page - 1) * PAGE_SIZE` y ejecuta `useQuery({ queryKey: ["productos", { offset, limit: PAGE_SIZE, nombre }], queryFn: () => getProductos(offset, PAGE_SIZE, nombre) })`.
    - Renderiza grilla de tarjetas de productos con nombre, descripción, precio formateado (`$precio`), badges de categorías asociadas, indicador de disponibilidad, botón *"Ver detalle →"* con navegación programática (`navigate(\`/productos/\${prod.id}\`)`) y barra de paginación calculada sobre `data?.total` (`totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))`).
  - `src/pages/ProductDetailPage.tsx`:
    - Extrae `:id` con `useParams<{ id: string }>()`, convierte a número (`const numericId = Number(id)`) y ejecuta `useQuery({ queryKey: ["producto", numericId], queryFn: () => getProductoById(numericId), enabled: Boolean(id) && !Number.isNaN(numericId) && numericId > 0 })`.
    - Muestra ficha completa del producto con sus categorías e incluye botón *"← Volver al listado de productos"* mediante `useNavigate()`.
- **Estado:** ⏳ **Pendiente**
- **Historias de Usuario asociadas:** HU-04, HU-05.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-07.

#### Tarea 3.6: Cierre del *Walking Skeleton* en `App.tsx` al enrutador definitivo (Sin lógica de negocio)
- **Acción:**
  - Completar la tabla declarativa de rutas (`<Routes>`) en `App.tsx` conectando las páginas `ProductsPage` y `ProductDetailPage` construidas en la Tarea 3.5 junto a `Navbar` y `CategoriasPage` ya montadas:
    ```tsx
    export function App() {
      return (
        <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900">
          <Navbar />
          <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <Routes>
              <Route path="/" element={<CategoriasPage />} />
              <Route path="/categorias" element={<CategoriasPage />} />
              <Route path="/productos" element={<ProductsPage />} />
              <Route path="/productos/:id" element={<ProductDetailPage />} />
            </Routes>
          </main>
        </div>
      );
    }
    ```
  - **Cero lógica de negocio**, cero `useState` de datos y cero llamadas `fetch` o `useQuery` en `App.tsx`.
- **Estado:** ⏳ **Pendiente**
- **Historias de Usuario asociadas:** HU-04.
- **Reglas de Negocio asociadas:** RN-01.
---

### FASE 4: Pruebas Integradas E2E, Verificación Estática y Empaquetado
> **Estado:** ⏳ **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 3. Consolida la entrega completa y asegura el cumplimiento de la rúbrica de evaluación.

#### Tarea 4.1: Smoke Test E2E de integración Full Stack
- **Acción:** Levantar el entorno con `pnpm dev` y comprobar de extremo a extremo:
  1. Navegación fluida entre `/categorias`, `/productos` y `/productos/:id` sin recarga de página mediante `NavLink` y `useNavigate`, verificando la persistencia en caché de TanStack Query entre cambios de vista.
  2. Carga inicial de categorías en la tabla vía `useQuery` con indicador de carga y filtro de búsqueda en tiempo real.
  3. Creación de una nueva categoría desde `CategoriaModal` y verificación del refresco instantáneo tras `invalidateQueries`.
  4. Edición de categoría existente y actualización reactiva en la tabla.
  5. Eliminación de categoría y remoción inmediata de la tabla tras la invalidación de la caché.
  6. Visualización paginada y filtrada de productos en `ProductsPage` con sus badges de categorías asociadas y acceso al detalle en `ProductDetailPage`.
- **Estado:** ⏳ **Pendiente**
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03, HU-04, HU-05.
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
- [ ] **Server State con TanStack Query:** El consumo de la API utiliza `useQuery` y `useMutation`, con invalidación de caché (`queryClient.invalidateQueries({ queryKey: ["categorias"] })`), verificación `if (!res.ok) throw new Error(...)` en `services/` y sin copiar `data` a `useState`.
- [ ] **Modal Reactivo:** El formulario de alta y edición se presenta dentro de `CategoriaModal.tsx` controlado con `useState` booleano en `CategoriasPage.tsx`.
- [ ] **Navegación con React Router:** Separación en páginas independientes (`CategoriasPage`, `ProductsPage` y `ProductDetailPage`) navegables mediante `NavLink` y `useNavigate` sin recarga de documento.
- [ ] **Catálogo de Productos en Frontend:** `ProductsPage.tsx` muestra la grilla paginada y filtrable de productos con sus categorías asociadas, disponibilidad y navegación a `/productos/:id`.
- [ ] **Tipado Estricto TypeScript:** Interfaces `Categoria`, `Producto` y `PaginatedResponse<T>` definidas formalmente; props tipados en todos los componentes `.tsx`; 0 errores en compilación de TypeScript (`tsc -b`).
- [ ] **Backend Modular FastAPI:** Arquitectura Models-Schemas-Service-Router con Pydantic y SQLModel, libre de `HTTPException` en la capa de servicio y sin *java-ismos*.
- [ ] **Paginación y Filtros Dinámicos:** Endpoints de colección con validación declarativa `fastapi.Query(ge=0, le=100)`, conteo atómico `func.count()` sobre subquery filtrada y respuesta estructurada `{ total, items }`.
- [ ] **Endpoints de Producto y ProductoCategoria:** Endpoints construidos con `selectinload` (prevención de $N+1$), funcionales y demostrados mediante archivo `productos.http` (incluyendo asignación con `es_principal`).
- [ ] **CORS Habilitado:** Configurado en FastAPI para permitir peticiones desde el origen del frontend (`http://localhost:5173` y `http://127.0.0.1:5173`).
- [ ] **Estilizado Tailwind CSS:** Clases aplicadas coherentemente y sin errores visuales.
- [ ] **Archivos de Entrega:** Dos archivos `.zip` independientes (`frontend` y `backend`) excluyendo `node_modules` y `.venv`.
