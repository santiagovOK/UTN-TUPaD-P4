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

### 1.4. Decisión de alcance: contratos de ingredientes en el frontend
* **Contexto:** La consigna refinada de TP7 incorpora `Ingrediente`, `UnidadMedida` y `ProductoIngrediente` en el backend, aunque no exige una interfaz frontend para administrar ingredientes ni unidades de medida.
* **Decisión Adoptada:** Se añadieron tipos TypeScript para ingredientes y sus asociaciones con productos, y se muestra en el detalle del producto la lista de ingredientes hidratados por el backend. No se incorporó un CRUD frontend de ingredientes ni una pantalla de unidades de medida dentro de TP7.
* **Fundamento:** Mantener contratos frontend compatibles con el modelo y las respuestas del backend, y dejar preparada esa información para su posible uso en futuros trabajos prácticos que amplíen la interfaz. Esta previsión no implica que esa funcionalidad futura esté requerida ni implementada en TP7.

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
[ Fase 4: Pruebas Integradas E2E y Verificación Estática ]
                               ↓
[ Fase 5: Backend — Catálogo Extendido, Seed, Reglas RN-01..22 & Relaciones N:M (18/10) ]
                               ↓
[ Fase 6: Frontend — Alineación de Servicios, PUT Total & Modal CRUD en ProductsPage (18/10) ]
                               ↓
[ Fase 7: Verificación E2E Full Stack, Documentación Sincronizada & Re-empaquetado (18/10) ]
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
| **3.4** | Adaptación de `Navbar.tsx` con enlaces activos de React Router (`NavLink`) e incorporación al layout de `App.tsx` | Fase 3 | ✅ **Done** | `src/components/Navbar.tsx`, `src/App.tsx` |
| **3.5** | Implementación de vistas de catálogo `ProductsPage.tsx` (paginada) y `ProductDetailPage.tsx` (`:id`) | Fase 3 | ✅ **Done** | `src/pages/ProductsPage.tsx`, `src/pages/ProductDetailPage.tsx` |
| **3.6** | Cierre del *Walking Skeleton* en `App.tsx` con el enrutador completo (`Navbar` + `Routes` de Categorías y Productos, sin lógica de negocio) | Fase 3 | ✅ **Done** | `src/App.tsx` |
| **4.1** | Smoke Test E2E de integración Full Stack (CRUD Categorías, catálogo paginado y navegación reactiva) | Fase 4 | ✅ **Done** | Navegador / Consola / Servidores concurrentes |
| **4.2** | Demostración REST Client de Producto y ProductoCategoria | Fase 4 | ✅ **Done** | `productos.http` |
| **4.3** | Verificación estática TypeScript (`tsc`) y ejecución de tests backend (`pytest`) | Fase 4 | ✅ **Done** | `tsc -b`, `pytest` |
| **5.1** | Modelos SQLModel y Seed de Catálogo (`UnidadMedida`, `Ingrediente`, `ProductoIngrediente`, `seed.py`) | Fase 5 | ✅ **Done** | `app/models/unidad_medida.py`, `app/models/ingrediente.py`, `app/models/producto.py`, `app/seed.py` |
| **5.2** | Módulos completos `unidad_medida` (solo lectura) e `ingrediente` (CRUD con borrado lógico) | Fase 5 | ✅ **Done** | `app/modules/unidad_medida/`, `app/modules/ingrediente/` (schemas, services, routers) |
| **5.3** | Adecuación de `categoria` a nuevas reglas (`RN-05` 409 al borrar con productos, query params estándar, `GET /{id}/productos`) | Fase 5 | ✅ **Done** | `app/modules/categoria/services.py`, `app/modules/categoria/routers.py` |
| **5.4** | Refactorización de `producto` y relaciones N:M (`RN-06`, `RN-11`, `RN-12`, `RN-14`, `RN-19`..`RN-22`, `GET` inversos) | Fase 5 | ✅ **Done** | `app/modules/producto/schemas.py`, `app/modules/producto/services.py`, `app/modules/producto/routers.py` |
| **5.5** | Endpoints de salud (`/health/`, `/health/db`), integración de seed en `lifespan` y actualización de `productos.http` + suite pytest | Fase 5 | ✅ **Done** | `app/main.py`, `unidad7_backend/productos.http`, `tests/test_productos_http.py` |
| **6.1** | Tipado TypeScript extendido y servicios frontend (`PUT /categorias/{id}`, DTOs de ingredientes y productos) | Fase 6 | ✅ **Done** | `src/types/ingrediente.ts`, `src/types/producto.ts`, `src/services/categorias.service.ts`, `src/services/productos.service.ts` |
| **6.2** | Formulario CRUD de Productos (`ProductoModal.tsx`) e integración de mutaciones en `ProductsPage.tsx` | Fase 6 | ✅ **Done** | `src/components/ProductoModal.tsx`, `src/pages/ProductsPage.tsx` |
| **7.1** | Verificación integral de endpoints con `pytest` y ejecución demostrativa de `productos.http` | Fase 7 | ✅ **Done** | Suite backend: 3/3 tests y 60 solicitudes HTTP |
| **7.2** | Compilación estática TypeScript (`tsc -b`) y Smoke Test E2E Full Stack en navegador | Fase 7 | ✅ **Done** | Build frontend y smoke CRUD/navegación completados sobre stack local ya activo |
| **7.3** | Sincronización de documentación (`README.md` raíz, backend y frontend) con las nuevas especificaciones | Fase 7 | ✅ **Done** | `README.md`, `unidad7_backend/README.md`, `unidad7_frontend/README.md` |
| **4.4** | Empaquetado limpio final de los dos entregables `.zip` (tras completar Fase 7) | Cierre | ⏳ **Pendiente** | Purgado de artefactos y compresión final |

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
> **Estado:** ✅ **COMPLETADA**  
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
- **Estado:** ✅ **Done**
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
- **Estado:** ✅ **Done**
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
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-04.
- **Reglas de Negocio asociadas:** RN-01.
---

### FASE 4: Pruebas Integradas E2E y Verificación Estática
> **Estado:** ✅ **COMPLETADA**
> **Criterio de Dependencia:** Nivel 3. Consolida la entrega completa y asegura el cumplimiento de la rúbrica de evaluación.

#### Tarea 4.1: Smoke Test E2E de integración Full Stack
- **Acción:** Levantar el entorno con `pnpm dev` y comprobar de extremo a extremo:
  1. Navegación fluida entre `/categorias`, `/productos` y `/productos/:id` sin recarga de página mediante `NavLink` y `useNavigate`, verificando la persistencia en caché de TanStack Query entre cambios de vista.
  2. Carga inicial de categorías en la tabla vía `useQuery` con indicador de carga y filtro de búsqueda en tiempo real.
  3. Creación de una nueva categoría desde `CategoriaModal` y verificación del refresco instantáneo tras `invalidateQueries`.
  4. Edición de categoría existente y actualización reactiva en la tabla.
  5. Eliminación de categoría y remoción inmediata de la tabla tras la invalidación de la caché.
  6. Visualización paginada y filtrada de productos en `ProductsPage` con sus badges de categorías asociadas y acceso al detalle en `ProductDetailPage`.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03, HU-04, HU-05.
#### Tarea 4.2: Demostración REST Client de Producto y ProductoCategoria
- **Acción:** Ejecutar las peticiones de `productos.http` verificando que los endpoints de Producto y ProductoCategoria responden con códigos HTTP semánticos (200, 201, 204, 404, 409, 422).
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-06.

#### Tarea 4.3: Verificación estática TypeScript y suite pytest
- **Acción:**
  - Compilación limpia de frontend: `pnpm build:front` (`tsc -b && vite build`) sin errores de TypeScript.
  - Ejecución de suite de pruebas backend: `pytest` en `unidad7_backend/` con base de datos en memoria.
- **Estado:** ✅ **Done**
- **Reglas de Negocio asociadas:** RN-07.


---

## Revisión luego de que subieran un nuevo PDF con las consignas refinadas (18/10)

Actualización integral de la consigna (`docs/consigna.md`), refinando el alcance técnico, formalizando una especificación de **7 Historias de Usuario (`HU-01` a `HU-07`)** con criterios de aceptación verificables, **22 Reglas de Negocio (`RN-01` a `RN-22`)** estrictas, dos nuevas entidades en el catálogo (`UnidadMedida` e `Ingrediente`), la gestión de asociaciones N:M consolidada exclusivamente en las operaciones del producto, endpoints de consulta relacional inversa y la incorporación de un formulario modal interactivo para productos en el frontend.

Para absorber estos cambios de forma determinista y sin desestabilizar el código ya desarrollado y testeado en las Fases 1 a 4, se formula a continuación el diagnóstico de divergencias, las decisiones de diseño técnico, la nueva matriz de trazabilidad y el desglose de tareas de convergencia estructurado en las **Fases 5, 6 y 7** bajo la misma metodología *Bottom-Up + Walking Skeleton*.

---

### 1.1. Auditoría de Incongruencias entre la Implementación Previa (Fases 1–4) y la Nueva Consigna (18/10)

| # | Eje de Divergencia | Implementación Previa (Fases 1–4) | Requerimiento Nueva Consigna (`docs/consigna.md` 18/10) | Impacto y Plan de Adaptación |
| :-: | :--- | :--- | :--- | :--- |
| **1** | **Nuevas Entidades de Catálogo (`UnidadMedida`, `Ingrediente`)** | Solo existen los modelos `Categoria`, `Producto` y `ProductoCategoria`. | Se exige la entidad `UnidadMedida` (catálogo de solo lectura poblado vía `seed.py` con 7 unidades exactas), la entidad `Ingrediente` (CRUD con borrado lógico) y la tabla intermedia `ProductoIngrediente`. | Crear modelos, schemas, seed idempotente y routers en backend (Fase 5, Tareas 5.1 y 5.2). |
| **2** | **Gestión de Relaciones N:M (`RN-11`, `RN-12`, `RN-19`..`RN-22`)** | `ProductoCreate` no exigía `categoria_ids` y se disponía de endpoints separados (`POST /productos/categorias/asignar`, `POST /productos/{id}/categorias/{categoria_id}`, `DELETE /...`). | Las relaciones N:M se gestionan **exclusivamente** al crear (`POST /productos/`) o editar (`PUT /productos/{id}`). `categoria_ids` es obligatorio en `POST` (`min_length=1`, `422` si falta o vacío, `404` si algún id no existe). En `PUT`, si se envían `categoria_ids` o `ingredientes`, se reemplazan en su totalidad. Prohibidos endpoints separados (`RN-22`). | Eliminar endpoints mutadores independientes de relación; unificar la gestión en `services.py` y schemas de `producto` (Fase 5, Tarea 5.4). |
| **3** | **Endpoints de Consulta Relacional Inversa (`HU-07`)** | No existían rutas dedicadas para consultar asociaciones inversas de forma desacoplada. | Se exige implementar: `GET /productos/{id}/categorias`, `GET /productos/{id}/ingredientes` y `GET /categorias/{id}/productos` (respondiendo `404 Not Found` si la entidad raíz no existe o fue eliminada). | Incorporar endpoints de solo lectura en los routers de `producto` y `categoria` con carga optimizada (Fase 5, Tareas 5.3 y 5.4). |
| **4** | **Unicidad de Nombre en Producto (`RN-06`)** | `services.py` validaba unicidad de `Producto.nombre` y devolvía `409 Conflict`. | `RN-06` establece textualmente: *"El nombre de un producto es obligatorio (`min_length=1`) y no puede quedar vacío ni contener solo espacios. **No es único: pueden coexistir productos con el mismo nombre.**"* | Remover la comprobación de unicidad en `create_producto` y `update_producto` permitiendo nombres repetidos (Fase 5, Tarea 5.4). |
| **5** | **Integridad Referencial al Eliminar Categoría (`HU-04`, `RN-05`)** | `DELETE /categorias/{id}` ejecutaba el borrado lógico directamente sin validar vínculos con productos. | `RN-05`: *"Una categoría con productos asociados no puede eliminarse hasta desasociar esos productos o eliminarlos"* → Debe responder HTTP `409 Conflict`. | Añadir verificación de productos asociados en `delete_categoria` antes de aplicar la baja lógica (Fase 5, Tarea 5.3). |
| **6** | **Borrado en Cascada de Asociaciones de Producto (`HU-06`, `RN-14`)** | `delete_producto` marcaba `deleted_at` pero conservaba vivas las tuplas en `ProductoCategoria`. | `RN-14`: Al eliminar un producto (borrado lógico), se eliminan en cascada sus asociaciones en `ProductoCategoria` y `ProductoIngrediente` para desvincularlo de categorías e ingredientes. | En `delete_producto`, marcar `deleted_at` y purgar sus filas asociadas en las tablas intermedias dentro de la misma transacción (Fase 5, Tarea 5.4). |
| **7** | **Parámetros Comunes de Colección (`offset`, `limit`, `nombre`, `incluir_inactivos`)** | `GET /categorias/` utilizaba `limit=50` por defecto y parámetro `search`. `GET /productos/` no soportaba `incluir_inactivos`. | Ambos listados deben alinearse al estándar: `offset: int = 0`, `limit: int = 10`, `nombre: Optional[str] = None` (manteniendo `search` como alias retrocompatible en categorías) e `incluir_inactivos: bool = False`. | Actualizar firmas y lógica de filtrado en routers y servicios de `categoria` y `producto` (Fase 5, Tareas 5.3 y 5.4). |
| **8** | **Endpoints de Salud (`/health/` y `/health/db`)** | Solo existía el endpoint raíz de comprobación general `GET /`. | Se exige formalmente `GET /health/` (`200 OK`) y `GET /health/db` (`200 OK` comprobando conectividad real a la base de datos con `SELECT 1`). | Implementar ambos endpoints en `app/main.py` manteniendo `GET /` como alias de compatibilidad (Fase 5, Tarea 5.5). |
| **9** | **Método HTTP en Edición de Categoría en Frontend (`HU-03`)** | `categorias.service.ts` emitía `PATCH /categorias/{id}`. | `HU-03`: *"Al guardar se envía `PUT /categorias/{id}` (reemplazo total), que responde 200 con la categoría actualizada..."*. | Cambiar el método de mutación a `PUT` en `categorias.service.ts` (Fase 6, Tarea 6.1). |
| **10** | **Formulario CRUD de Productos en Frontend (`ProductsPage.tsx`, Inciso `g`)** | `ProductsPage.tsx` solo implementaba el catálogo paginado y filtro de búsqueda de solo lectura. | La consigna exige que `ProductsPage` posea estructura similar a `CategoriasPage`: listado + formulario modal (`ProductoModal.tsx`) para crear/editar con validación y confirmación de baja. | Crear `ProductoModal.tsx` con soporte de `categoria_ids` e integrar mutaciones con TanStack Query en `ProductsPage.tsx` (Fase 6, Tarea 6.2). |

---

### 1.2. Decisiones de Diseño Técnico para las Nuevas Entidades y Contratos

#### 1. Entidad `UnidadMedida` (Catálogo de Solo Lectura — `app/models/unidad_medida.py`)
* **Naturaleza:** Entidad `<<Catalog>>` inmutable en runtime; carece de endpoints de mutación (`POST`, `PUT`, `DELETE`).
* **Estructura relacional:**
  ```python
  class UnidadMedida(SQLModel, table=True):
      __tablename__ = "unidad_medida"

      id: Optional[int] = Field(default=None, primary_key=True)
      nombre: str = Field(max_length=50, unique=True, nullable=False, index=True)
      simbolo: str = Field(max_length=10, nullable=False)
      tipo: str = Field(max_length=30, nullable=False)  # masa, volumen, unidad, area
  ```
* **Poblado Semilla (`app/seed.py`):**
  Función `seed_unidades_medida(session: Session)` invocada durante el evento `lifespan` de FastAPI luego de `create_db_and_tables()`. Inserta de forma idempotente las 7 unidades oficiales definidas por la cátedra:
  1. `kilogramo` (`kg`, `masa`)
  2. `gramo` (`g`, `masa`)
  3. `litro` (`L`, `volumen`)
  4. `mililitro` (`mL`, `volumen`)
  5. `pieza` (`u`, `unidad`)
  6. `docena` (`doc`, `unidad`)
  7. `metro cuadrado` (`m²`, `area`)
* **Contratos DTO y Endpoints:**
  - `GET /unidades-medida/` → Retorna `UnidadMedidaListResponse(total=7, items=[UnidadMedidaRead, ...])`.
  - `GET /unidades-medida/{id}` → Retorna `UnidadMedidaRead` o HTTP `404 Not Found`.

#### 2. Entidad `Ingrediente` (Catálogo Dinámico — `app/models/ingrediente.py`)
* **Naturaleza:** Entidad con auditoría completa y soporte de borrado lógico (`deleted_at`).
* **Estructura relacional:**
  ```python
  class Ingrediente(SQLModel, table=True):
      __tablename__ = "ingrediente"

      id: Optional[int] = Field(default=None, primary_key=True)
      nombre: str = Field(max_length=100, unique=True, nullable=False, index=True)
      descripcion: Optional[str] = Field(default="")
      unidad_medida_id: int = Field(foreign_key="unidad_medida.id", nullable=False)
      activo: bool = Field(default=True, nullable=False)
      created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
      updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
      deleted_at: Optional[datetime] = Field(default=None, nullable=True)
  ```
* **Contratos DTO y Endpoints (`/ingredientes/`):**
  - `GET /ingredientes/?offset=0&limit=10&nombre=...&incluir_inactivos=false` → `IngredientePaginatedResponse`.
  - `POST /ingredientes/` (`201 Created`): Valida existencia de `unidad_medida_id` (`404`) y unicidad insensible a mayúsculas de `nombre` (`409`).
  - `GET /ingredientes/{id}` (`200 OK` o `404`).
  - `PUT /ingredientes/{id}` (`200 OK` reemplazo o `404`/`409`).
  - `DELETE /ingredientes/{id}` (`204 No Content` borrado lógico; rechaza con `409 Conflict` si está asociado a productos activos).

#### 3. Tabla Intermedia `ProductoIngrediente` (`app/models/producto.py`)
* **Naturaleza:** Asociación N:M entre `Producto` e `Ingrediente` con atributos extendidos.
* **Estructura relacional:**
  ```python
  class ProductoIngrediente(SQLModel, table=True):
      __tablename__ = "producto_ingrediente"

      producto_id: int = Field(foreign_key="producto.id", primary_key=True)
      ingrediente_id: int = Field(foreign_key="ingrediente.id", primary_key=True)
      cantidad: float = Field(default=1.0, gt=0, nullable=False)
      es_opcional: bool = Field(default=False, nullable=False)
      created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False)
  ```

#### 4. Contratos DTO de Producto Actualizados (`app/modules/producto/schemas.py`)
* **`ProductoCreate`:**
  ```python
  class ProductoCreate(ProductoBase):
      categoria_ids: List[int] = Field(min_length=1, description="Lista obligatoria de al menos un ID de categoría existente")
      ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = Field(
          default=None,
          description="Lista opcional de ingredientes (IDs enteros o payloads con cantidad y es_opcional)"
      )
  ```
* **`ProductoUpdate`:**
  ```python
  class ProductoUpdate(SQLModel):
      nombre: Optional[str] = None
      descripcion: Optional[str] = None
      precio_base: Optional[float] = Field(default=None, ge=0)
      disponible: Optional[bool] = None
      imagenes_url: Optional[List[str]] = None
      categoria_ids: Optional[List[int]] = Field(default=None, min_length=1)
      ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = None
  ```
* **`ProductoRead`:** Retorna la información completa del producto con sus relaciones hidratadas:
  `id`, `nombre`, `descripcion`, `precio_base`, `disponible`, `imagenes_url`, `categorias: List[CategoriaRead]` e `ingredientes: List[ProductoIngredienteRead]`.

---

### 1.3. Nueva Matriz de Trazabilidad Integral (`HU-01` a `HU-07` y `RN-01` a `RN-22`)

#### Historias de Usuario (HU)
| ID | Denominación y Alcance | Canal de Verificación | Criterios de Aceptación Clave | Fase / Tarea |
| :---: | :--- | :--- | :--- | :---: |
| **HU-01** | Listar categorías | Frontend (React) | Monta `CategoriasPage`, ejecuta `useQuery` con `GET /categorias`, renderiza nombre y descripción, muestra estado vacío o error `{"detail": "..."}`. | Fase 3 / 3.3 (Vigente) |
| **HU-02** | Crear una categoría | Frontend (React) | Modal con formulario vacío, `nombre` obligatorio (`min_length=1`, sin espacios solos), `POST /categorias/` (`201`), conflicto duplicado (`409`), refetch e invalidación sin recarga. | Fase 3 / 3.3 (Vigente) |
| **HU-03** | Editar una categoría | Frontend (React) | Modal con campos precargados, envío de `PUT /categorias/{id}` (reemplazo total, `200`), control de `404` y `409`, actualización reactiva y cierre de modal. | Fase 6 / 6.1 (Adaptación PUT) |
| **HU-04** | Eliminar una categoría | Frontend (React) | Botón eliminar dispara `DELETE /categorias/{id}` (`204`), control de `404` y bloqueo `409` si tiene productos asociados (`RN-05`). Confirmación previa obligatoria. | Fase 5 / 5.3 (RN-05 Backend) |
| **HU-05** | Navegar entre páginas con React Router | Frontend (React) | Enlaces en `Navbar` hacia `/categorias` y `/productos` mediante React Router, sin recarga de navegador. `App.tsx` desacoplado sin lógica de negocio. | Fase 3 / 3.4 y 3.6 (Vigente) |
| **HU-06** | CRUD de Productos desde REST Client | Backend (REST Client) | `GET /productos`, `POST /productos` (`201` con `categoria_ids` obligatorio `min_length=1` e ingredientes opcionales), `PUT /productos/{id}` (`200` con reemplazo de relaciones), `DELETE /productos/{id}` (`204` con cascada de vínculos). Demostrado vía `productos.http`. | Fase 5 / 5.4 y 5.5 |
| **HU-07** | Consultar relación N:M Producto-Categoría y Producto-Ingrediente | Backend (REST Client) | `GET /productos/{id}/categorias`, `GET /productos/{id}/ingredientes`, `GET /categorias/{id}/productos`. Relaciones gestionadas ÚNICAMENTE en `POST`/`PUT` de productos. Error `404` si la entidad base no existe. | Fase 5 / 5.3, 5.4 y 5.5 |

#### Reglas de Negocio (RN)
| ID | Regla de Negocio | Entidad / Código Esperado | Criterio de Verificación | Fase / Tarea |
| :---: | :--- | :--- | :--- | :---: |
| **RN-01** | `Categoria.nombre` obligatorio (`min_length=1`), no vacío ni solo espacios | Categoria / `422 Unprocessable Entity` | Schema `CategoriaCreate` / `CategoriaUpdate` con validador strip y `min_length=1`. | Fase 2 / 2.2 (Vigente) |
| **RN-02** | `Categoria.nombre` único (insensible a mayúsculas/espacios) | Categoria / `409 Conflict` | Comprobación `func.lower(nombre)` en `categoria.services`. | Fase 2 / 2.3 (Vigente) |
| **RN-03** | `Categoria.descripcion` opcional con default `""` | Categoria / `200` o `201` | Schema `descripcion: str = ""` persistido sin error. | Fase 1 y 2 (Vigente) |
| **RN-04** | No actualizar ni eliminar categoría con ID inexistente | Categoria / `404 Not Found` | Verificación en `get_categoria_by_id` en service/router. | Fase 2 / 2.3 (Vigente) |
| **RN-05** | Categoría con productos asociados no puede eliminarse | Categoria / `409 Conflict` | Conteo en `producto_categoria` previo a baja; lanza conflicto si count > 0. | Fase 5 / 5.3 |
| **RN-06** | `Producto.nombre` obligatorio (`min_length=1`). **No es único: se permiten repetidos** | Producto / `422` (si inválido) | Permitir nombres duplicados en `create_producto` y `update_producto`. | Fase 5 / 5.4 |
| **RN-07** | `Producto.precio_base` debe ser $\ge 0$ | Producto / `422 Unprocessable Entity` | Validación Pydantic `Field(ge=0)`. | Fase 2 / 2.2 (Vigente) |
| **RN-08** | `Producto.disponible` booleano con default `True` | Producto / `201 Created` | Valor predeterminado en modelo y schema. | Fase 2 / 2.1 (Vigente) |
| **RN-09** | `Producto.imagenes_url` lista de cadenas (puede ser vacía) | Producto / `422` (si tipo erróneo) | Declaración `List[str] = Field(default_factory=list)`. | Fase 2 / 2.1 (Vigente) |
| **RN-10** | No consultar, actualizar ni eliminar producto con ID inexistente | Producto / `404 Not Found` | Retorno `404` si `get_producto_by_id` es `None`. | Fase 2 / 2.4 (Vigente) |
| **RN-11** | En `POST`/`PUT` producto, todas las categorías en `categoria_ids` deben existir | Relación / `404 Not Found` | Verificación de existencia de cada ID contra la tabla `categoria`. | Fase 5 / 5.4 |
| **RN-12** | En `PUT /productos/{id}`, si se envían `categoria_ids`, se reemplazan TODAS las asociaciones | Relación / `200 OK` (`409` si conflicto de estado) | Eliminación y recreación transaccional de tuplas en `producto_categoria`. | Fase 5 / 5.4 |
| **RN-13** | Cardinalidad N:M entre Producto y Categoría | Relación / `GET` inversos | Verificación con `GET /productos/{id}/categorias` y `GET /categorias/{id}/productos`. | Fase 5 / 5.3 y 5.4 |
| **RN-14** | Al eliminar un producto, borrado en cascada de sus asociaciones N:M | Relación / Consistencia tras `DELETE` | Purgado de filas en `producto_categoria` y `producto_ingrediente` al aplicar soft delete. | Fase 5 / 5.4 |
| **RN-15** | IDs autoincrementales asignados por el backend (solo lectura) | Todas / Autoincrement | Prohibido enviar o mutar PK `id` desde el cliente. | Fase 2 (Vigente) |
| **RN-16** | Persistencia consistente durante la ejecución del servidor | Todas / Runtime | SQLite en disco / PostgreSQL según variable `DATABASE_URL`. | Fase 2 / 2.5 (Vigente) |
| **RN-17** | Operaciones inválidas devuelven error y no mutan el estado | Todas / `404`, `409`, `422` | Transacciones atómicas de sesión en SQLAlchemy/SQLModel. | Fase 2 (Vigente) |
| **RN-18** | Enrutamiento SPA gestionado en el cliente con React Router | Frontend / SPA puro | `BrowserRouter`, `Routes`, `Route`, `NavLink` sin recargas completas. | Fase 3 / 3.4 y 3.6 (Vigente) |
| **RN-19** | En `POST /productos/`, `categoria_ids` es obligatorio con al menos un ID | Producto / `422 Unprocessable Entity` | Pydantic `Field(min_length=1)` sobre `categoria_ids`. | Fase 5 / 5.4 |
| **RN-20** | `ingredientes` es opcional al crear o actualizar producto | Producto / `201` o `200` | Si se omite, el producto se crea o mantiene sin ingredientes asociados. | Fase 5 / 5.4 |
| **RN-21** | En `PUT /productos/{id}`, si se envían `ingredientes`, se reemplazan TODOS los existentes | Producto / `200 OK` | Reemplazo transaccional completo en `producto_ingrediente`. | Fase 5 / 5.4 |
| **RN-22** | No existen endpoints `POST`/`DELETE` específicos para relaciones N:M | Relación / Arquitectura | Gestión exclusiva en `POST /productos/` y `PUT /productos/{id}`. | Fase 5 / 5.4 |

---

### 1.4. Tablero Kanban de Readaptación (Fases 5, 6 y 7)

```text
[ FASE 5: Backend — Catálogo Extendido, Seed, Reglas RN-01..22 & Relaciones N:M ]
                                      ↓
[ FASE 6: Frontend — Alineación de Servicios, PUT Total & Modal CRUD en ProductsPage ]
                                      ↓
[ FASE 7: Verificación E2E Full Stack, Documentación Sincronizada & Re-empaquetado ]
```

| ID Tarea | Tarea | Fase | Estado | Componentes / Módulos Afectados |
| :---: | :--- | :---: | :---: | :--- |
| **5.1** | Modelos SQLModel y Seed de Catálogo (`UnidadMedida`, `Ingrediente`, `ProductoIngrediente`, `seed.py`) | Fase 5 | ✅ **Done** | `app/models/unidad_medida.py`, `app/models/ingrediente.py`, `app/models/producto.py`, `app/seed.py` |
| **5.2** | Módulos completos `unidad_medida` (solo lectura) e `ingrediente` (CRUD con borrado lógico) | Fase 5 | ✅ **Done** | `app/modules/unidad_medida/`, `app/modules/ingrediente/` (schemas, services, routers) |
| **5.3** | Adecuación de `categoria` a nuevas reglas (`RN-05` 409 al borrar con productos, query params estándar, `GET /{id}/productos`) | Fase 5 | ✅ **Done** | `app/modules/categoria/services.py`, `app/modules/categoria/routers.py` |
| **5.4** | Refactorización de `producto` y relaciones N:M (`RN-06`, `RN-11`, `RN-12`, `RN-14`, `RN-19`..`RN-22`, `GET` inversos) | Fase 5 | ✅ **Done** | `app/modules/producto/schemas.py`, `app/modules/producto/services.py`, `app/modules/producto/routers.py` |
| **5.5** | Endpoints de salud (`/health/`, `/health/db`), integración de seed en `lifespan` y actualización de `productos.http` + suite pytest | Fase 5 | ✅ **Done** | `app/main.py`, `unidad7_backend/productos.http`, `tests/test_productos_http.py` |
| **6.1** | Tipado TypeScript extendido y servicios frontend (`PUT /categorias/{id}`, DTOs de ingredientes y productos) | Fase 6 | ✅ **Done** | `src/types/ingrediente.ts`, `src/types/producto.ts`, `src/services/categorias.service.ts`, `src/services/productos.service.ts` |
| **6.2** | Formulario CRUD de Productos (`ProductoModal.tsx`) e integración de mutaciones en `ProductsPage.tsx` | Fase 6 | ✅ **Done** | `src/components/ProductoModal.tsx`, `src/pages/ProductsPage.tsx` |
| **7.1** | Verificación integral de endpoints con `pytest` y ejecución demostrativa de `productos.http` | Fase 7 | ✅ **Done** | Suite backend: 3/3 tests y 60 solicitudes HTTP |
| **7.2** | Compilación estática TypeScript (`tsc -b`) y Smoke Test E2E Full Stack en navegador | Fase 7 | ✅ **Done** | Build frontend y smoke CRUD/navegación completados sobre stack local ya activo |
| **7.3** | Sincronización de documentación (`README.md` raíz, backend y frontend) con las nuevas especificaciones | Fase 7 | ✅ **Done** | `README.md`, `unidad7_backend/README.md`, `unidad7_frontend/README.md` |
| **4.4** | Empaquetado limpio final de los dos entregables `.zip` (tras completar Fase 7) | Cierre | ⏳ **Pendiente** | Purgado de artefactos y compresión final |

---

### FASE 5: Backend — Catálogo Extendido, Seed, Reglas RN-01..22 & Relaciones N:M
> **Estado:** ✅ **COMPLETADA**
> **Criterio de Dependencia:** Nivel 4 (Construye sobre el backend base de la Fase 2 para cumplir al 100% la especificación del 18/10).

#### Tarea 5.1: Modelos SQLModel y Seed de Catálogo
- **Acción:**
  - Crear `app/models/unidad_medida.py`: Definir modelo `UnidadMedida` con `__tablename__ = "unidad_medida"`, campos `id`, `nombre` (único, indexado), `simbolo` y `tipo`.
  - Crear `app/models/ingrediente.py`: Definir modelo `Ingrediente` con `__tablename__ = "ingrediente"`, campos `id`, `nombre` (único), `descripcion`, `unidad_medida_id` (FK a `unidad_medida.id`), `activo`, marcas temporales de auditoría (`created_at`, `updated_at`, `deleted_at`).
  - Actualizar `app/models/producto.py`: Incorporar tabla intermedia `ProductoIngrediente` con clave primaria compuesta `(producto_id, ingrediente_id)`, campos `cantidad: float = Field(default=1.0, gt=0)` y `es_opcional: bool = Field(default=False)`.
  - Crear `app/seed.py`: Función `seed_unidades_medida(session: Session)` idempotente que verifique registros existentes e inserte las 7 unidades oficiales definidas por la cátedra (`kilogramo`, `gramo`, `litro`, `mililitro`, `pieza`, `docena`, `metro cuadrado`).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-06, HU-07.
- **Reglas de Negocio asociadas:** RN-15, RN-16, RN-20.

#### Tarea 5.2: Módulos completos `unidad_medida` e `ingrediente`
- **Acción:**
  - Módulo `app/modules/unidad_medida/`:
    - `schemas.py`: `UnidadMedidaRead(id: int, nombre: str, simbolo: str, tipo: str)` y `UnidadMedidaListResponse(total: int, items: List[UnidadMedidaRead])`.
    - `services.py`: `get_unidades_medida(session)` y `get_unidad_medida_by_id(session, id)`.
    - `routers.py`: `GET /unidades-medida/` y `GET /unidades-medida/{id}` (solo lectura, sin endpoints de escritura).
  - Módulo `app/modules/ingrediente/`:
    - `schemas.py`: `IngredienteBase`, `IngredienteCreate` (con validación de `nombre` y `unidad_medida_id`), `IngredienteUpdate`, `IngredienteRead` e `IngredientePaginatedResponse(total: int, items: List[IngredienteRead])`.
    - `services.py`: CRUD completo con filtrado dinámico (`nombre`, `incluir_inactivos`), conteo atómico SQL, validación de existencia de unidad de medida y chequeo de no duplicidad de nombre. Borrado lógico marcando `deleted_at` y `activo = False`. Bloqueo con excepción de conflicto si el ingrediente está vinculado a productos activos.
    - `routers.py`: `GET /ingredientes/`, `POST /ingredientes/` (`201`), `GET /ingredientes/{id}`, `PUT /ingredientes/{id}` y `DELETE /ingredientes/{id}` (`204`).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-07.
- **Reglas de Negocio asociadas:** RN-15, RN-16, RN-17.

#### Tarea 5.3: Adecuación de `categoria` a nuevas reglas de negocio
- **Acción:**
  - En `app/modules/categoria/routers.py`:
    - Ajustar parámetros de `GET /categorias/`: `offset: int = Query(0, ge=0)`, `limit: int = Query(10, ge=1, le=100)`, `nombre: Optional[str] = Query(None)` (manteniendo `search` como alias retrocompatible opcional) e `incluir_inactivos: bool = Query(False)`.
    - Incorporar endpoint de consulta inversa relacional: `GET /categorias/{id}/productos` (`HU-07`) retornando la lista de productos asociados a la categoría solicitada, o `404 Not Found` si la categoría no existe o está dada de baja.
  - En `app/modules/categoria/services.py`:
    - Modificar `delete_categoria` (`RN-05`): Verificar previamente si existen registros en `producto_categoria` asociados a la categoría; en caso afirmativo, abortar la baja y retornar un indicador de conflicto para que el router emita `409 Conflict`.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-04, HU-07.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-03, RN-04, RN-05.

#### Tarea 5.4: Refactorización de `producto` y relaciones N:M
- **Acción:**
  - En `app/modules/producto/schemas.py`:
    - Actualizar `ProductoCreate` incorporando `categoria_ids: List[int] = Field(min_length=1)` (`RN-19`) e `ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = None` (`RN-20`).
    - Actualizar `ProductoUpdate` incorporando `categoria_ids: Optional[List[int]] = Field(default=None, min_length=1)` e `ingredientes: Optional[List[Union[int, ProductoIngredienteInput]]] = None`.
    - Reflejar en `ProductoRead` la lista de categorías e ingredientes asociados.
  - En `app/modules/producto/services.py`:
    - Remover la restricción de nombre único (`RN-06`): Permitir productos con nombres idénticos.
    - En `create_producto`: Validar que todos los `categoria_ids` existan en la tabla `categoria` (`RN-11`, retornando `404` ante identificadores faltantes); si se enviaron `ingredientes`, validar existencia de cada uno. Crear transaccionalmente el producto y registrar los vínculos en `producto_categoria` y `producto_ingrediente`.
    - En `update_producto`: Si se provee `categoria_ids` (`RN-12`), validar existencia de todos los IDs (`RN-11`) y reemplazar atómicamente todas las relaciones previas en `producto_categoria`. Si se provee `ingredientes` (`RN-21`), reemplazar atómicamente los vínculos en `producto_ingrediente`.
    - En `delete_producto` (`RN-14`): Aplicar borrado lógico en `Producto` (`deleted_at = datetime.now(timezone.utc)`) y eliminar en cascada sus filas en `producto_categoria` y `producto_ingrediente`.
    - Implementar funciones de consulta relacional: `get_categorias_by_producto_id(session, id)` y `get_ingredientes_by_producto_id(session, id)`.
  - En `app/modules/producto/routers.py`:
    - Eliminar los endpoints dedicados `POST /productos/categorias/asignar`, `POST /productos/{id}/categorias/{categoria_id}` y `DELETE /productos/{id}/categorias/{categoria_id}` (`RN-22`).
    - Ajustar parámetros en `GET /productos/`: `offset: int = Query(0, ge=0)`, `limit: int = Query(10, ge=1, le=100)`, `nombre: Optional[str] = None`, `incluir_inactivos: bool = False`.
    - Agregar endpoints de consulta inversa: `GET /productos/{id}/categorias` y `GET /productos/{id}/ingredientes` (`HU-07`).
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-06, HU-07.
- **Reglas de Negocio asociadas:** RN-06, RN-07, RN-08, RN-09, RN-10, RN-11, RN-12, RN-13, RN-14, RN-19, RN-20, RN-21, RN-22.

#### Tarea 5.5: Endpoints de salud, ciclo lifespan y suite de pruebas actualizada
- **Acción:**
  - En `app/main.py`:
    - Implementar los endpoints `GET /health/` (`200 {"status": "ok"}`) y `GET /health/db` (`200 {"status": "ok", "database": "connected"}` ejecutando `session.exec(text("SELECT 1"))`).
    - En el contextmanager `lifespan`: Asegurar la invocación de `seed_unidades_medida(session)` tras `create_db_and_tables()`.
    - Registrar los nuevos routers de `unidad_medida` e `ingrediente`.
  - En `unidad7_backend/productos.http`:
    - Reestructurar el archivo con las secciones oficiales:
      1. Comprobación de salud (`/health/`, `/health/db`).
      2. Catálogo inmutable de Unidades de Medida (`GET /unidades-medida/`, `GET /unidades-medida/1`).
      3. CRUD de Ingredientes (`POST`, `GET`, `PUT`, `DELETE`).
      4. CRUD de Categorías con reglas de conflicto (`POST`, `GET`, `PUT`, `DELETE` con `409` si tiene productos).
      5. CRUD de Productos con relaciones N:M unificadas en `POST` (`categoria_ids` obligatorio) y `PUT` (reemplazo total de categorías e ingredientes).
      6. Consultas relacionales inversas N:M (`GET /productos/{id}/categorias`, `GET /productos/{id}/ingredientes`, `GET /categorias/{id}/productos`).
      7. Comprobación de borrado en cascada de vínculos al eliminar producto (`RN-14`).
  - Actualizar `tests/test_productos_http.py` para asegurar que la suite automatizada cubra todas las nuevas rutas y aserciones.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-06, HU-07.
- **Reglas de Negocio asociadas:** RN-05, RN-06, RN-11..14, RN-19..22.

---

### FASE 6: Frontend — Alineación de Servicios, PUT Total & Modal CRUD en `ProductsPage`
> **Estado:** ✅ **COMPLETADA**  
> **Criterio de Dependencia:** Nivel 5 (Consume los endpoints y esquemas actualizados en la Fase 5).

#### Tarea 6.1: Tipado TypeScript extendido y servicios HTTP
- **Acción:**
  - Crear `src/types/ingrediente.ts`: Tipos `UnidadMedida`, `Ingrediente` e `IngredienteInput`.
  - Actualizar `src/types/producto.ts`: Incorporar `categoria_ids: number[]` e `ingredientes?: ...` en `ProductoCreate` y `ProductoUpdate`, y actualizar `Producto` con su detalle de categorías e ingredientes.
  - En `src/services/categorias.service.ts`:
    - Modificar `updateCategoria`: Enviar método HTTP `PUT` en lugar de `PATCH` hacia `/categorias/{id}` para dar cumplimiento estricto a `HU-03`.
  - En `src/services/productos.service.ts`:
    - Completar el cliente API de productos con las operaciones de mutación requeridas:
      - `createProducto(payload: ProductoCreate)`: `POST /productos/`.
      - `updateProducto({ id, data }: { id: number; data: ProductoUpdate })`: `PUT /productos/{id}`.
      - `deleteProducto(id: number)`: `DELETE /productos/{id}`.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-03, HU-06.
- **Reglas de Negocio asociadas:** RN-01, RN-06, RN-07, RN-19.

#### Tarea 6.2: Formulario CRUD de Productos (`ProductoModal.tsx`) y refinamiento de `ProductsPage.tsx`
- **Acción:**
  - Crear `src/components/ProductoModal.tsx`:
    - Modal flotante con control reactivo de inputs: `nombre`, `descripcion`, `precio_base`, `disponible`, selección de categorías (`categoria_ids` con checkboxes o multiselect validando al menos 1 categoría seleccionada).
    - Soporte dual de modo Alta (*"Nuevo Producto"*) y modo Edición (*"Editar Producto"*).
    - Despliegue de mensajes de error de validación/conflicto dentro del modal (`errorMessage`).
    - Deshabilitación de controles durante el envío (`isSubmitting`).
  - Refinar `src/pages/ProductsPage.tsx`:
    - Incorporar botón *"Nuevo Producto"* en la cabecera.
    - Gestionar estado de modal: `isModalOpen: boolean` y `editingProducto: Producto | null`.
    - Integrar `useMutation` para creación (`createMutation`), edición (`updateMutation`) y baja con confirmación interactiva (`deleteMutation`).
    - Invalidar la caché de productos tras cada mutación exitosa: `queryClient.invalidateQueries({ queryKey: ["productos"] })`.
    - Agregar botones de *Editar* y *Eliminar* en cada tarjeta de producto.
- **Estado:** ✅ **Done**
- **Historias de Usuario asociadas:** HU-05, HU-06.
- **Reglas de Negocio asociadas:** RN-06, RN-07, RN-08, RN-11, RN-12, RN-19.

---

### FASE 7: Verificación E2E Full Stack & Documentación Sincronizada
> **Estado:** ✅ **COMPLETADA**
> **Criterio de Dependencia:** Nivel 6 (Consolida y verifica la totalidad de la aplicación actualizada).

#### Tarea 7.1: Verificación de suite pytest y REST Client `productos.http`
- **Acción:**
  - Ejecutar la suite completa de backend mediante `pytest` asegurando 100% de tests pasando en verde.
  - Probar de punta a punta el archivo `productos.http` verificando el seed de unidades de medida, CRUD de ingredientes, CRUD de categorías con bloqueo `409` por productos asociados, CRUD de productos con validación obligatoria de `categoria_ids` (`422`/`404`), reemplazo en `PUT`, endpoints de consulta inversa N:M y comprobación de salud en `/health/` y `/health/db`.
- **Estado:** ✅ **Done** — pytest: 3/3 tests; las 60 solicitudes de `productos.http` verificadas.
- **Historias de Usuario asociadas:** HU-06, HU-07.
- **Reglas de Negocio asociadas:** RN-01..RN-22.

#### Tarea 7.2: Compilación estática TypeScript y Smoke Test E2E Full Stack
- **Acción:**
  - Ejecutar `pnpm build:front` (`tsc -b && vite build`) comprobando compilación limpia con 0 errores de tipado en componentes, servicios y vistas.
  - Levantar concurrentemente el frontend y backend para comprobar de forma interactiva en navegador:
    1. Navegación fluida por React Router entre `/categorias` y `/productos`.
    2. Ciclo completo de Categorías: creación con modal, edición con `PUT`, eliminación con confirmación.
    3. Ciclo completo de Productos: creación con selección obligatoria de categorías en `ProductoModal`, edición de atributos y asociaciones, baja lógica interactiva y reflejo instantáneo en la grilla paginada.
- **Estado:** ✅ **Done** — build frontend y smoke test de CRUD/navegación completados con un stack localhost que ya estaba activo; los registros temporales se eliminaron al terminar.
- **Historias de Usuario asociadas:** HU-01 a HU-05.

#### Tarea 7.3: Sincronización de archivos de documentación (`README.md`)
- **Acción:**
  - Actualizar `README.md` (raíz), `unidad7_backend/README.md` y `unidad7_frontend/README.md` detallando:
    - El clúster completo de entidades (`UnidadMedida`, `Ingrediente`, `Categoria`, `Producto`, `ProductoCategoria`, `ProductoIngrediente`).
    - La carga semilla automática de unidades de medida (`seed.py`).
    - Los nuevos endpoints disponibles y las reglas de gestión N:M unificadas en `POST`/`PUT`.
    - El modal interactivo de productos en el frontend.
- **Estado:** ✅ **Done**
#### Tarea 4.4: Empaquetado limpio final para entrega según consigna
- **Acción:**
  - Purgar directorios y cachés temporales (`node_modules/`, `.venv/`, `.pytest_cache/`, `dist/`, `__pycache__/`).
  - Generar los dos archivos comprimidos independientes:
    - `Varela_Santiago_TPI_unidad7_frontend.zip`
    - `Varela_Santiago_TPI_unidad7_backend.zip`
- **Estado:** ⏳ **Pendiente**
- **Reglas de Negocio asociadas:** RN-08.


---

## 4. Checklist de Control de Entrega

- [x] **Estructura de Carpetas:** El frontend cuenta con las carpetas `src/components/`, `src/types/`, `src/services/` y `src/pages/`.
- [x] **Arquitectura de `App.tsx`:** `App.tsx` carece totalmente de lógica de negocio o llamadas a API; solo define rutas con React Router y renderiza el `Navbar`.
- [x] **Server State con TanStack Query:** El consumo de la API utiliza `useQuery` y `useMutation`, con invalidación de caché (`queryClient.invalidateQueries({ queryKey: [...] })`), verificación `if (!res.ok) throw new Error(...)` en `services/` y sin copiar `data` a `useState`.
- [x] **Modal Reactivo de Categorías:** El formulario de alta y edición se presenta dentro de `CategoriaModal.tsx` controlado con `useState` booleano en `CategoriasPage.tsx`. Edición envía `PUT /categorias/{id}` (`HU-03`).
- [x] **Modal Reactivo de Productos:** Formulario interactivo en `ProductoModal.tsx` integrado en `ProductsPage.tsx` con soporte de selección obligatoria de categorías (`categoria_ids`, `RN-19`), ingredientes opcionales y baja con confirmación.
- [x] **Navegación con React Router:** Separación en páginas independientes (`CategoriasPage`, `ProductsPage` y `ProductDetailPage`) navegables mediante `NavLink` y `useNavigate` sin recarga de documento.
- [x] **Catálogo Inmutable de Unidades de Medida:** Modelo `UnidadMedida` poblado automáticamente al arrancar la aplicación vía `seed.py` con las 7 unidades oficiales (`RN-15`, `RN-16`), accesible exclusivamente mediante endpoints de lectura `GET /unidades-medida/` y `GET /unidades-medida/{id}`.
- [x] **CRUD de Ingredientes:** Modelo `Ingrediente` con borrado lógico (`deleted_at`), validación de clave foránea a unidad de medida y endpoints completos en `/ingredientes/`.
- [x] **Gestión Unificada de Relaciones N:M:** Relaciones N:M gestionadas exclusivamente a través de `POST /productos/` (`categoria_ids` obligatorio `min_length=1`, `RN-19`) y `PUT /productos/{id}` (reemplazo atómico total de categorías e ingredientes, `RN-12`, `RN-21`), sin endpoints `POST`/`DELETE` separados (`RN-22`).
- [x] **Consultas Relacionales Inversas N:M:** Endpoints `GET /productos/{id}/categorias`, `GET /productos/{id}/ingredientes` y `GET /categorias/{id}/productos` implementados y operativos (`HU-07`).
- [x] **Protección de Integridad en Categoría (`RN-05`):** `DELETE /categorias/{id}` rechaza la eliminación con `409 Conflict` si la categoría tiene productos asociados activos.
- [x] **Flexibilidad en Nombre de Producto (`RN-06`):** `Producto.nombre` no requiere unicidad y permite productos con nombres idénticos.
- [x] **Borrado en Cascada de Asociaciones (`RN-14`):** Al eliminar un producto se purgan automáticamente sus vínculos en `producto_categoria` y `producto_ingrediente`.
- [x] **Endpoints de Salud y Diagnóstico:** `GET /health/` (`200 OK`) y `GET /health/db` (`200 OK` comprobando conectividad real a la base de datos).
- [x] **Tipado Estricto TypeScript:** Interfaces completas en `src/types/` (`Categoria`, `Producto`, `Ingrediente`, `UnidadMedida`); props tipados en todos los componentes `.tsx`; 0 errores en compilación de TypeScript (`tsc -b`).
- [x] **Backend Modular FastAPI:** Arquitectura Models-Schemas-Service-Router con Pydantic y SQLModel, libre de `HTTPException` en la capa de servicio y sin *java-ismos*.
- [x] **Paginación y Filtros Estándar:** Endpoints de colección con validación `fastapi.Query(ge=0, le=100)`, parámetros `offset`, `limit` (default 10), `nombre`, `incluir_inactivos`, conteo atómico `func.count()` y respuesta estructurada `{ total, items }`.
- [x] **CORS Habilitado:** Configurado en FastAPI para permitir peticiones desde el origen del frontend (`http://localhost:5173` y `http://127.0.0.1:5173`).
- [x] **Suite de Pruebas y REST Client:** Archivo `productos.http` actualizado cubriendo todos los endpoints y casos de prueba, y suite `pytest` en verde (3/3 tests; 60 solicitudes verificadas).
- [ ] **Archivos de Entrega:** Dos archivos `.zip` independientes (`frontend` y `backend`) excluyendo estrictamente `node_modules`, `.venv`, cachés y temporales.
