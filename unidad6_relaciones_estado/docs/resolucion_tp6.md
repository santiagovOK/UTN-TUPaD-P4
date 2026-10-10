# Resolución y Plan de Ejecución — Trabajo Práctico 6

> **Materia:** Programación IV (Tecnicatura Universitaria en Programación a Distancia - UTN)  
> **Tema:** Relaciones en Backend (FastAPI - SQLModel / PostgreSQL) y Gestión de Estado en Frontend (React 19 - TypeScript - Hooks)  
> **Estrategia:** Descomposición "Bottom-Up" (de menor a mayor dependencia) orientada a tablero Kanban. Cada tarea referencia explícitamente las Historias de Usuario (HU) y Reglas de Negocio (RN) correspondientes a las consignas del trabajo práctico. Las tareas se organizan en fases secuenciales donde cada nivel provee la base necesaria para el siguiente.

---

## 1. Matriz de Trazabilidad Rápida

| ID | Tipo | Descripción Sintética | Fase Asignada |
| :--- | :---: | :--- | :---: |
| **HU-01** | HU | Listado reactivo de categorías en estructura tabular (`NÚMERO`, `NOMBRE`, `DESCRIPCIÓN`, `ACCIONES`) según mockup (`docs/mockup/mockup.md`). | Fase 1 (UI) / Fase 2 (Fetch) |
| **HU-02** | HU | Creación y edición interactiva de categorías mediante modal flotante superpuesto (`CategoriaModal.tsx` con backdrop) controlado con `useState`. | Fase 1 (UI) / Fase 2 (Fetch) |
| **HU-03** | HU | Eliminación de categorías desde la columna de acciones de cada fila (`CategoriaCard.tsx`) con confirmación y sincronización de estado. | Fase 2 (Fetch) |
| **RN-01** | RN | Modelado y endpoints REST de `Producto` y relación muchos a muchos (`Producto_Categoria`) testeados con archivo REST Client (`.http`) sin requerir interfaz gráfica. | Fase 3 (Backend) |
| **RN-02** | RN | Uso estricto de `fetch` nativo y hooks estándar (`useState`, `useEffect`) centralizados en `App.tsx`. Componentes hijos funcionales puros sin hooks propios. | Fase 2 (Frontend) |
| **RN-03** | RN | Configuración y habilitación de CORS en FastAPI para permitir solicitudes Cross-Origin desde el origen del frontend (`http://localhost:5173`). | Fase 1 (Infraestructura) |
| **RN-04** | RN | Tipado estático riguroso en TypeScript (`Categoria`, `Producto`) y validación de esquemas en backend con Pydantic / SQLModel sin discrepancias de contrato. | Fase 1 / Fase 3 |
| **RN-05** | RN | Estructura modular de proyecto y empaquetado de entrega en archivos `.zip` independientes excluyendo directorios de dependencias (`node_modules/`, `.venv/`, `dist/`). | Fase 1 / Fase 4 |

---

## 2. Desglose de Tareas "Bottom-Up" para Tablero Kanban

```text
[ Fase 1: Infraestructura Base, UI Estática, Endpoints de Categoría & Documentación ] (REDISEÑO UI MOCKUP)
                                        ↓
[ Fase 2: Integración Frontend — Estado Reactivo & Fetch API ] (REDISEÑO UI MOCKUP)
                                        ↓
[ Fase 3: Backend — Modelos y Endpoints de Producto & Relaciones ] (EN PROGRESO)
                                        ↓
[ Fase 4: Pruebas Integradas, Empaquetado y Entrega Final ] (PENDIENTE)
```

### 2.1. Tablero Kanban de Estado de Tareas

| ID Tarea | Tarea | Fase | Estado | Componentes / Módulos Afectados |
| :---: | :--- | :---: | :---: | :--- |
| **1.1** | Configuración de monorepo y scripts concurrentes | Fase 1 | ✅ **Done** | `package.json`, `pnpm-workspace.yaml` |
| **1.2** | Endpoints base y schemas de Categoría (FastAPI + CORS) | Fase 1 | ✅ **Done** | `app/modules/categoria/`, `app/main.py` |
| **1.3** | Tipado TypeScript y maquetado de componentes según Mockup (`docs/mockup/mockup.md`) | Fase 1 | ✅ **Done** | `src/types/`, `src/components/`, `src/App.tsx` |
| **1.4** | Documentación integral y guías de ejecución | Fase 1 | ✅ **Done** | `README.md`, `unidad6_*/README.md` |
| **2.1** | Implementación de estado centralizado (`useState`) | Fase 2 | ✅ **Done** | `src/App.tsx` |
| **2.2** | Sincronización inicial con `useEffect` y `fetch` (`AbortController`) | Fase 2 | ✅ **Done** | `src/App.tsx` |
| **2.3** | Funciones CRUD de mutación con `fetch` (`POST`, `PUT`, `DELETE`) | Fase 2 | ✅ **Done** | `src/App.tsx`, `CategoriaModal`, `CategoriaList` |
| **2.4** | Adaptación de layout principal, modal flotante y feedback visual (`loading`/`error`) | Fase 2 | ✅ **Done** | `src/App.tsx`, `CategoriaModal`, `CategoriaList` |
| **3.1** | Migración de persistencia de Categoría a SQLModel y Base de Datos | Fase 3 | ✅ **Done** | `app/models/categoria.py`, `app/modules/categoria/`, `tests/test_categoria.py` |
| **3.2** | Modelado SQLModel de `Producto` (esquema TP6) y tabla intermedia `Producto_Categoria` | Fase 3 | 📋 **Backlog** | `app/models/producto.py`, `app/database.py` |
| **3.3** | Schemas DTO, validadores y servicios de Producto y vinculación N:N | Fase 3 | 📋 **Backlog** | `app/modules/producto/schemas.py`, `services.py` |
| **3.4** | Exposición de endpoints REST en `app/modules/producto/routers.py` | Fase 3 | 📋 **Backlog** | `app/modules/producto/routers.py` |
| **3.5** | Archivo de pruebas REST Client (`productos.http`, `categorias.http`) | Fase 3 | 📋 **Backlog** | `productos.http`, `categorias.http` |
| **4.1** | Validación E2E Smoke Test integral | Fase 4 | 📋 **Backlog** | Fullstack (`:5173` y `:8000`) |
| **4.2** | Verificación estática TypeScript y suite pytest por dominio | Fase 4 | 📋 **Backlog** | `tests/test_categoria.py`, `tests/test_producto.py`, CI |
| **4.3** | Purgado y empaquetado final `.zip` | Fase 4 | 📋 **Backlog** | Artefactos de entrega |

---

### FASE 1: Infraestructura Base, UI Estática, Endpoints de Categoría y Documentación
> **Estado:** **COMPLETADA**
> **Criterio de Dependencia:** Nivel 0 (Base). No depende de capas superiores; establece la estructura del repositorio, el tipado de datos base, la configuración de desarrollo concurrente, los endpoints base de categorías y los componentes presentacionales puros alineados visualmente con `docs/mockup/mockup.md`.

> **Nota de Diseño Técnico:**  
> En una primera iteración se reciclaron los componentes de la Unidad 5 (layout de dos columnas con formulario lateral inline y grilla de tarjetas). Tras relevar las pantallas oficiales de referencia en `docs/mockup/mockup.md` (`img/ejemplo1.png` y `img/ejemplo2.png`), se refinan las tareas de frontend para adoptar el **diseño tabular limpio de columna única centrada** con cabecera de acción (`"+ Añadir Categoría"`) y **ventana modal flotante superpuesta con backdrop** (`Editar Categoría` / `Añadir Categoría`), manteniendo estrictamente los nombres de archivos y contratos exigidos por `docs/consignas.md` (`Navbar.tsx`, `CategoriaList.tsx`, `CategoriaCard.tsx`, `CategoriaModal.tsx`).

#### Tarea 1.1: Configuración de la estructura del monorepo, dependencias y scripts de orquestación concurrente
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso a** (*"Crear y activar un entorno virtual Python, crea archivo de dependencias e instalar las dependencias"*) y la **Parte B - inciso a** (*"Inicializar el proyecto: pnpm create vite... pnpm install"*) de `docs/consignas.md`.
- **Acción:** Configurar `package.json` en la raíz con `concurrently` y scripts unificados (`dev`, `dev:all`, `dev:front`, `dev:back`, `stop`), actualizar manifiesto de frontend (`unidad6_frontend/package.json`) y asegurar las dependencias de backend (`unidad6_backend/requirements.txt`).
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Orquestación raíz:** Se creó el archivo `package.json` raíz integrando `concurrently` (`^9.1.2`) y `kill-port` (`^2.0.1`), permitiendo levantar frontend y backend simultáneamente en la misma consola con salida diferenciada por color.
> - **Aislamiento por capa:** Scripts dedicados `dev:front` y `dev:back` para desarrollo independiente.
> - **Verificación:** Ejecución exitosa de `pnpm install` en la raíz (generando `pnpm-lock.yaml`) y comprobación de comando `stop` para liberar los puertos 5173 y 8000.

- **Historias de Usuario asociadas:** N/A (Infraestructura).
- **Reglas de Negocio asociadas:** RN-03, RN-05.
- **Criterio de Aceptación / Verificación:** Ambas capas pueden inicializarse conjuntamente mediante `pnpm dev` o individualmente sin conflictos de puertos ni rutas relativas rotas.

#### Tarea 1.2: Endpoints base y schemas de Categoría en Backend (FastAPI + CORS)
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso b** (*"Definir los models y schemas: Categoria (id: int, nombre: str, descripcion: str)"*) e **inciso c** (*"Implementar los endpoints de Categorías en ./categoria/router.py, deberá de habilitar los CORS para poder consumir su API desde el Front-End: allow_origins=['http://localhost:5173']"*) de `docs/consignas.md`.
- **Acción:** Importar y adaptar el módulo `categoria` en `unidad6_backend/app/modules/categoria/` con esquemas Pydantic (`CategoriaCreate`, `CategoriaRead`), servicio de datos y router REST (`GET /categorias/`, `POST /categorias/`, `GET /categorias/{id}`, `PUT /categorias/{id}`, `DELETE /categorias/{id}`). Habilitar middleware CORS para `http://localhost:5173`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Contratos de datos (`schemas.py`):** Modelos `CategoriaBase`, `CategoriaCreate` y `CategoriaRead` con campos obligatorios (`id`, `nombre`) y opcionales (`descripcion`, `activo`), adaptando el esquema para compatibilidad plena con el frontend de React.
> - **CORS Middleware (`app/main.py`):** Configurado para admitir peticiones desde `http://localhost:5173` y `http://127.0.0.1:5173` con todos los métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`).
> - **Enrutador (`routers.py`):** Prefijo `/categorias` registrado en la instancia principal de FastAPI con códigos de estado HTTP semánticos (200, 201, 204, 404).

- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-03, RN-04.
- **Criterio de Aceptación / Verificación:** Endpoints visibles y operativos en Swagger UI (`/docs`), respondiendo correctamente a llamadas locales con cabeceras CORS habilitadas.

#### Tarea 1.3: Tipado TypeScript y maquetado de componentes de Categoría en Frontend según Mockup (Tailwind CSS v4)
- **Alineación con la Consigna:** Resuelve la **Parte B - incisos b, c y d** de `docs/consignas.md` (*"Instalar y configurar Tailwind CSS"*, *"Definir el tipo en src/types/categoria.ts"* y *"Crear los componentes en src/components/ (.tsx): Navbar, CategoriaCard, CategoriaList, CategoriaModal"*) siguiendo la especificación visual de `docs/mockup/mockup.md` (`ejemplo1.png` y `ejemplo2.png`).
- **Acción:** Definir la interface `Categoria` en `src/types/categoria.ts` y maquetar los componentes funcionales puros en `src/components/` replicando el diseño del mockup:
  - `Navbar.tsx`: Barra superior minimalista con el nombre de la aplicación, armonizada con la paleta neutra/azul (`slate`/`blue`) del mockup.
  - `CategoriaList.tsx`: Contenedor principal en tarjeta blanca con bordes redondeados y sombra suave (`bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden`). Renderiza la tabla con fila de encabezado en mayúsculas (`bg-slate-50 text-xs font-semibold uppercase tracking-wider text-slate-500`) compuesta por las 4 columnas del mockup: `NÚMERO`, `NOMBRE`, `DESCRIPCIÓN` y `ACCIONES` (alineada a la derecha), iterando la colección `Categoria[]` en el cuerpo de la tabla.
  - `CategoriaCard.tsx`: Componente funcional puro que representa cada fila (`<tr>`) del listado tabular de categorías. Recibe `categoria: Categoria`, `onEdit` y `onDelete` por props tipados; muestra el `id` en la columna `NÚMERO`, `nombre` en `NOMBRE`, `descripcion` en `DESCRIPCIÓN`, y en la columna `ACCIONES` incluye los botones `"Editar"` (en tono azul interactivo `text-blue-600 hover:text-blue-800 font-medium`, idéntico a `ejemplo1.png`) y `"Eliminar"` (en tono rojo/rosa `text-rose-600 hover:text-rose-800 font-medium`, cumpliendo la consigna Parte B inciso d: *"Incluye botones Editar y Eliminar"*).
  - `CategoriaModal.tsx`: Ventana modal flotante real centrada en el viewport sobre un overlay semitransparente oscuro (`fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4`), conforme a `ejemplo2.png`:
    - Contenedor del diálogo: `bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8`.
    - Cabecera: Título dinámico `"Editar Categoría"` (en modo edición) o `"Añadir Categoría"` (en modo alta) con tipografía `text-xl font-bold text-slate-900`.
    - Controles de formulario: Campo `"Nombre de la categoría"` (`<input type="text">` con borde y anillo de foco azul `focus:ring-2 focus:ring-blue-500 focus:border-blue-500 rounded-lg`) y campo `"Descripción"` (`<input type="text">` con `border-slate-300 rounded-lg`).
    - Botonera inferior alineada a la derecha (`flex justify-end gap-3 pt-4`): Botón secundario `"Cancelar"` (`bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium px-4 py-2 rounded-lg`) y botón primario `"Guardar"` (`bg-blue-600 hover:bg-blue-700 text-white font-medium px-5 py-2 rounded-lg`).
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Estructura de Componentes:** Definición estricta de `Categoria` (`id`, `nombre`, `descripcion`, `activo`) en `src/types/categoria.ts`.
> - **Alineación con Mockup:** Reemplazado el maquetado previo por la composición tabular limpia de `docs/mockup/mockup.md` (`NÚMERO`, `NOMBRE`, `DESCRIPCIÓN`, `ACCIONES` en `CategoriaList.tsx`, filas `<tr>` en `CategoriaCard.tsx` con acciones `Editar`/`Eliminar`, y diálogo modal flotante con backdrop en `CategoriaModal.tsx`).
> - **Verificación:** Compilación TypeScript limpia (`pnpm build:front`) y validación visual 1:1 en navegador con capturas contra `img/ejemplo1.png` y `img/ejemplo2.png`.
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-02, RN-04.
- **Criterio de Aceptación / Verificación:** La aplicación compila sin errores de TypeScript (`pnpm build:front`) y presenta exactamente la tabla de categorías y el modal superpuesto descritos en `docs/mockup/mockup.md`.
#### Tarea 1.4: Documentación integral del proyecto y guías de ejecución
- **Alineación con la Consigna:** Resuelve la sección **"Estructura esperada del proyecto"** (diseño en capas limpio para FastAPI y React) y el **"Marco Teórico"** de `docs/consignas.md`, asegurando reproducibilidad y trazabilidad técnica.
- **Acción:** Redactar la documentación técnica detallada en `unidad6_frontend/README.md`, `unidad6_backend/README.md`, `README.md` en la raíz del proyecto y formalizar el presente documento `docs/resolucion_tp6.md`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **README Raíz:** Guía unificada (estilo TP5) que cubre inicialización fullstack, scripts disponibles, configuración de bases de datos (PostgreSQL / SQLite), tabla de comandos y árbol de directorios.
> - **READMEs Específicos:** Documentación detallada por capa (`unidad6_frontend/README.md` y `unidad6_backend/README.md`) con comandos de ejecución individual (`pnpm dev`, `fastapi dev app/main.py`), arquitectura de componentes y documentación interactiva (`/docs`).
> - **Trazabilidad:** Tablero Kanban estructurado con matriz de trazabilidad y criterios de aceptación verificables.

- **Historias de Usuario asociadas:** N/A (Documentación).
- **Reglas de Negocio asociadas:** RN-05.
- **Criterio de Aceptación / Verificación:** Documentación comprensible, precisa y verificada en el repositorio.

---

### FASE 2: Integración Frontend — Estado Reactivo, Layout Principal & Fetch API
> **Estado:** **COMPLETADA**
> **Criterio de Dependencia:** Nivel 1. Depende de los componentes de la Fase 1 y los endpoints de Categoría. Conecta la tabla y el modal flotante con la API REST utilizando hooks estándar (`useState`, `useEffect`) y `fetch` nativo exclusivamente en `App.tsx`.

#### Tarea 2.1: Implementación de estado centralizado (`useState`) y cabecera de sección en `App.tsx`
- **Alineación con la Consigna:** Resuelve la **Parte B - inciso e** de `docs/consignas.md` (*"useState para la lista de categorías, el estado del modal (abierto/cerrado) y la categoría seleccionada para edición"*) y estructura el encabezado principal de `ejemplo1.png` (`docs/mockup/mockup.md`).
- **Acción:** Declarar y estructurar las variables de estado y disparadores de interfaz en `src/App.tsx`:
  - `categorias: Categoria[]` (colección reactiva de categorías renderizada en la tabla).
  - `isModalOpen: boolean` (controla el montaje del overlay flotante `CategoriaModal`).
  - `categoriaEnEdicion: Categoria | null` (almacena la categoría seleccionada al pulsar `"Editar"` en una fila, o `null` al pulsar `"+ Añadir Categoría"`).
  - `loading: boolean` y `error: string | null` (estados de carga y error de red).
  - Disposición del encabezado superior de sección en `App.tsx` (según `ejemplo1.png`): Título `"Categorías"` a la izquierda y botón azul `"+ Añadir Categoría"` a la derecha vinculado a `handleOpenCreateModal`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Estado Reactivo Centralizado:** Declarados los 5 estados en `App.tsx` manteniendo los componentes hijos como funciones puras.
> - **Control de Modal Flotante:** Handlers `handleOpenCreateModal` (abre modal vacío), `handleOpenEditModal(categoria)` (abre modal precargado con la fila seleccionada) y `handleCloseModal` (cierra el modal al pulsar `"Cancelar"`).

- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** Al hacer clic en `"+ Añadir Categoría"` o en `"Editar"` dentro de cualquier fila de la tabla, se abre el modal superpuesto sobre el backdrop oscuro con el título y los valores correspondientes.

#### Tarea 2.2: Sincronización de datos iniciales con `useEffect` y `fetch` nativo (`GET /categorias`)
- **Alineación con la Consigna:** Resuelve la **Parte B - inciso e** de `docs/consignas.md`: *"useEffect para cargar las categorías al montar el componente (GET /categorias)"*.
- **Acción:** Implementar en `App.tsx` el efecto secundario mediante `useEffect` para consultar asíncronamente `GET http://localhost:8000/categorias/` al montar el componente y volcar los registros en la tabla de `CategoriaList`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Fetching Desacoplado:** Función `fetchCategorias` envuelta en `useCallback` consumiendo `http://localhost:8000/categorias/`.
> - **Limpieza y Cancelación (`AbortController`):** Integración de `AbortController` y `signal` para cancelar peticiones pendientes ante desmontaje o doble invocación de React StrictMode.

- **Historias de Usuario asociadas:** HU-01.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** Al cargar la vista principal, se ejecuta `GET /categorias/` y las filas se renderizan en la tabla con sus columnas `NÚMERO`, `NOMBRE`, `DESCRIPCIÓN` y `ACCIONES`.

#### Tarea 2.3: Implementación de funciones CRUD de mutación con `fetch` nativo (`POST`, `PUT`, `DELETE`)
- **Alineación con la Consigna:** Resuelve la **Parte B - inciso e** de `docs/consignas.md`: *"Funciones handleCreate, handleUpdate, handleDelete que usen fetch nativo hacia el backend"* y *"Pasar las funciones y el estado como props a los componentes hijos"*.
- **Acción:** Desarrollar en `App.tsx` los controladores asíncronos y transferirlos por props a `CategoriaList` y `CategoriaModal`:
  - `handleSubmit(e)`: Manejador para creación (`POST http://localhost:8000/categorias/`) y edición (`PUT http://localhost:8000/categorias/{id}`) al enviar el formulario del modal flotante (`"Guardar"`). Actualiza inmutablemente `categorias` (`.map()` en edición, `[...prev, nueva]` en alta) y cierra el diálogo modal (`handleCloseModal()`).
  - `handleDelete(id)`: Confirmación con `window.confirm` al pulsar `"Eliminar"` en una fila de la tabla y petición `DELETE http://localhost:8000/categorias/{id}`, filtrando la categoría eliminada mediante `.filter()`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Creación y Edición Unificada:** `handleSubmit` toma los valores de `nombre` y `descripcion` del formulario del modal, ejecuta `POST` o `PUT` según `categoriaEnEdicion` y sincroniza la tabla en memoria.
> - **Eliminación Segura:** `handleDelete` emite `DELETE` con código 204 y actualiza las filas de la tabla sin recargar la página.

- **Historias de Usuario asociadas:** HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** El alta y la edición desde el modal superpuesto y la eliminación desde la columna `ACCIONES` impactan en la base de datos y actualizan la tabla instantáneamente.

#### Tarea 2.4: Adaptación de layout de columna única, superposición modal y estados de carga/error
- **Alineación con la Consigna:** Complementa la **Parte B - incisos d y e** de `docs/consignas.md` y materializa la composición visual de `docs/mockup/mockup.md` (`ejemplo1.png` y `ejemplo2.png`).
- **Acción:** Reestructurar el contenedor principal en `App.tsx` eliminando la división lateral de 3 columnas (heredada de la Unidad 5) en favor de un contenedor centrado (`max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8`):
  - Disponer el encabezado superior (`"Categorías"` + botón `"+ Añadir Categoría"`) directamente sobre la tarjeta tabular de `CategoriaList`.
  - Renderizar `CategoriaModal` fuera del flujo de columnas como capa modal superpuesta (`fixed inset-0`), de modo que la tabla permanezca visible detrás del backdrop oscurecido tal como en `ejemplo2.png`.
  - Mantener indicadores de carga (`loading`), alerta de error (`[role="alert"]`) y deshabilitación del botón `"Guardar"` (`isSubmitting`) durante peticiones en vuelo.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Layout Unificado:** Reestructuración de `App.tsx` a columna única centrada (`max-w-5xl mx-auto w-full`), ubicando la cabecera con el título `"Categorías"` y el botón `"+ Añadir Categoría"` sobre la tarjeta tabular.
> - **Modal Flotante Superpuesto:** `CategoriaModal` renderizado fuera del flujo de columnas con backdrop oscuro semitransparente (`fixed inset-0 z-50 bg-black/40`), manteniendo la tabla en segundo plano al editar o crear.
> - **Feedback Visual y Robustez:** Indicadores de carga (`loading`), alerta de error (`[role="alert"]`) con reintento, y prevención de doble submit con `isSubmitting` en el botón `"Guardar"`.
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** Al abrir el modal de creación o edición, la tabla de categorías permanece en segundo plano bajo el overlay semitransparente oscuro exactamente como en `img/ejemplo2.png`.
---

### FASE 3: Backend — Modelos y Endpoints de Producto & Relaciones
> **Estado:** **EN PROGRESO**  
> **Criterio de Dependencia:** Nivel 2. Implementa la lógica de backend requerida para el catálogo de productos y su relación N:N con categorías, sin requerir interfaz gráfica de usuario (conforme a RN-01).

#### Tarea 3.1: Migración de persistencia de Categoría a SQLModel y Base de Datos Relacional (Prerrequisito N:N)
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso b** (*"Definir los models y schemas: Categoria (id: int, nombre: str, descripcion: str)"*) y el criterio de rúbrica *"CRUD Categorías – Backend: Endpoints FastAPI... con Pydantic y persistencia en lista/DB"*, proveyendo la tabla relacional requerida para la clave foránea de `Producto_Categoria`.
- **Acción:** Para posibilitar la integridad referencial y las claves foráneas de la tabla intermedia `Producto_Categoria`, migrar la entidad `Categoria` de la lista en memoria actual (`db_categorias`) a la base de datos relacional:
  - Crear la entidad persistente `Categoria` en `unidad6_backend/app/models/categoria.py` con `SQLModel, table=True` (`id: Optional[int]`, `nombre: str`, `descripcion: Optional[str]`, `activo: bool = True`) y el vínculo bidireccional `productos: list["Producto"] = Relationship(back_populates="categorias", link_model=ProductoCategoria)`.
  - Refactorizar `unidad6_backend/app/modules/categoria/services.py` sustituyendo la manipulación en memoria por operaciones contra `Session` (`db.exec(select(Categoria))`, `db.add()`, `db.commit()`, `db.refresh()`).
  - Inyectar la dependencia de sesión `db: Session = Depends(get_session)` en los endpoints de `app/modules/categoria/routers.py`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Entidad Persistente (`app/models/categoria.py`):** Creado el modelo `Categoria(SQLModel, table=True)` con `id` (PK autoincremental), `nombre`, `descripcion`, `activo` y relación bidireccional `productos` vinculada mediante `ProductoCategoria` (`app/models/producto.py`) y registrada en `create_db_and_tables()` (`app/database.py`).
> - **Servicios SQLModel (`app/modules/categoria/services.py`):** Eliminada la lista en memoria `db_categorias` e `id_counter`; implementadas operaciones transaccionales contra `Session` (`select(Categoria)`, `db.get()`, `db.add()`, `db.delete()`, `db.commit()`, `db.refresh()`).
> - **Inyección de Sesión (`app/modules/categoria/routers.py`):** Inyectada la dependencia `db: Session = Depends(get_session)` en los 6 endpoints del router de categorías, preservando el contrato `CategoriaRead` (`from_attributes=True`).
> - **Pruebas Automatizadas por Dominio (`tests/test_categoria.py`):** Suite completa de 15 pruebas automatizadas organizadas por dominio: metadatos DDL (`categoria` y tabla intermedia `productocategoria`), servicios transaccionales con `session` (creación, listado con paginación, búsqueda por ID, actualización total, borrado lógico y físico) y endpoints HTTP con `client` (`TestClient`) sobre base de datos SQLite en memoria aislada (`conftest.py`).
> - **Verificación:** 15 tests pasando exitosamente en `test_categoria.py` y persistencia real verificada contra servidor local.
- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-01, RN-04.
- **Criterio de Aceptación / Verificación:** Las categorías se persisten y consultan directamente desde la base de datos (PostgreSQL / SQLite) manteniendo 100% el contrato JSON consumido por el frontend React.

#### Tarea 3.2: Modelado SQLModel para `Producto` y tabla intermedia `Producto_Categoria` (Alineación con TP6)
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso b** de `docs/consignas.md`: *"Definir los models y schemas: Producto (id: int, nombre: str, descripcion: str, precio_base: str, imagen_url: list[], disponible: bool) y Producto_Categoria (producto_id: int, categoria_id: int)"* y la sección *"Conclusiones Esperadas"* referida al modelado de entidades y relaciones.
- **Acción:** Definir en `unidad6_backend/app/models/producto.py`:
  - Tabla intermedia `ProductoCategoria` (o `Producto_Categoria`) heredando de `SQLModel, table=True` con clave primaria compuesta (`producto_id: int = Field(foreign_key="producto.id", primary_key=True)`, `categoria_id: int = Field(foreign_key="categoria.id", primary_key=True)`).
  - Modelo persistente `Producto` adaptado a los campos exactos exigidos por la consigna del TP6: `id: Optional[int] = Field(default=None, primary_key=True)`, `nombre: str`, `descripcion: str`, `precio_base: str`, `imagen_url: list[str] = Field(default_factory=list, sa_column=Column(JSON))`, `disponible: bool = True`.
  - Configurar `categorias: list["Categoria"] = Relationship(back_populates="productos", link_model=ProductoCategoria)` para navegación directa de relaciones muchos a muchos.
- **Estado:** Pendiente / Backlog
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01, RN-04.
- **Criterio de Aceptación / Verificación:** Tablas relacionales creadas y vinculadas correctamente en `create_db_and_tables()` de SQLModel, sin ciclos de importación ni violaciones de claves foráneas.

#### Tarea 3.3: Schemas DTO, validaciones y servicios de negocio para Productos y vinculación N:N
- **Alineación con la Consigna:** Resuelve la **Parte A - incisos b y d** y la sección **"Conclusiones Esperadas"** de `docs/consignas.md`: validación estricta de datos con esquemas Pydantic y lógica de servicios para garantizar integridad referencial y prevenir duplicados en la asociación N:N entre `Producto` y `Categoria`.
- **Acción:** Implementar en `unidad6_backend/app/modules/producto/schemas.py`, `services.py` y `validators.py`:
  - Esquemas DTO de Pydantic: `ProductoBase`, `ProductoCreate`, `ProductoUpdate`, `ProductoRead` y `ProductoReadConCategorias` (incluyendo la lista anidada `categorias: list[CategoriaRead] = []`).
  - Servicios CRUD completos para la entidad `Producto`.
  - Funciones de servicio para asociar (`asociar_categoria`) y desasociar (`desasociar_categoria`) categorías a un producto específico.
  - Validaciones de existencia previa de producto y categoría antes de persistir vínculos en la tabla intermedia, arrojando excepciones HTTP semánticas (404 si no existe, 409 si ya está asociada).
  - Consultas optimizadas con Eager Loading (`selectinload(Producto.categorias)`) para prevenir el problema $N+1$.
- **Estado:** Pendiente / Backlog
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** Servicios testeables que persisten productos y administran vínculos N:N con integridad referencial garantizada.

#### Tarea 3.4: Exposición de endpoints REST en `unidad6_backend/app/modules/producto/routers.py`
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso d** de `docs/consignas.md`: *"Implementar también los endpoints de Producto. Estos no necesitan conectarse al frontend — serán demostrados con REST Client"* y endpoints para gestionar la asociación N:N.
- **Acción:** Registrar las rutas REST en el enrutador de productos:
  - `POST /productos/`: Creación de producto (status 201).
  - `GET /productos/`: Listado paginado de productos (status 200).
  - `GET /productos/{id}`: Detalle de producto con sus categorías vinculadas (status 200, schema `ProductoReadConCategorias`).
  - `PUT /productos/{id}`: Modificación de producto (status 200).
  - `DELETE /productos/{id}`: Eliminación física o lógica de producto (status 204).
  - `POST /productos/{id}/categorias/{categoria_id}`: Asociación de categoría a producto (status 200 o 201).
  - `DELETE /productos/{id}/categorias/{categoria_id}`: Desvinculación de categoría de producto (status 204).
- **Estado:** Pendiente / Backlog
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** Endpoints accesibles vía Swagger UI (`/docs`) y testeables con respuestas HTTP semánticas (200, 201, 204, 404, 409).

#### Tarea 3.5: Elaboración de archivo de pruebas REST Client (`productos.http` y `categorias.http`)
- **Alineación con la Consigna:** Resuelve la **Parte A - inciso d** (*"El archivo .http debera ser entregado junto al proyecto"*), la sección **"Conclusiones Esperadas"** (*"Backend REST documentado: Endpoints de Producto y ProductoCategoria funcionando y demostrados en el archivo .http"*) y la **Rúbrica de Evaluación** (*"CRUD Productos y relación – REST Client (15 pts)"*) de `docs/consignas.md`.
- **Acción:** Crear los archivos de solicitudes HTTP ejecutables para VS Code REST Client / JetBrains HTTP Client en `unidad6_backend/` que demuestren el funcionamiento integral de la API sin requerir frontend:
  - Peticiones ordenadas para crear categorías.
  - Creación de productos con diferentes atributos (`precio_base: str`, lista `imagen_url`, `disponible: bool`).
  - Asociación de productos a múltiples categorías (relación N:N).
  - Consulta de producto verificando categorías anidadas en la respuesta JSON.
  - Actualización y eliminación de asociaciones y registros.
  - Verificación de casos de error (404 para entidades inexistentes, 409 para duplicados).
- **Estado:** Pendiente / Backlog
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** El archivo `.http` se entrega junto al proyecto y ejecuta con 100% de éxito contra el servidor local demostrando el CRUD de Productos y la relación muchos a muchos.

---

### FASE 4: Pruebas Integradas, Empaquetado y Entrega Final
> **Estado:** **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 3. Depende de la finalización de las Fases 1, 2 y 3. Consolida la solución completa, ejecuta validaciones finales de extremo a extremo y genera los paquetes comprimidos para entrega.

#### Tarea 4.1: Validación de flujo integral de extremo a extremo (E2E Smoke Test)
- **Alineación con la Consigna:** Resuelve el **"OBJETIVO GENERAL"**, la sección **"Conclusiones Esperadas"** (*"Integración Full Stack: El frontend React consume la API FastAPI mediante fetch nativo. El CRUD de Categorías funciona de extremo a extremo"*) y el criterio de Rúbrica *"CRUD Categorías – Frontend (30 pts)"* de `docs/consignas.md`.
- **Acción:** Iniciar el entorno fullstack unificado (`pnpm dev`) y verificar el ciclo de vida completo:
  1. Acceder a `http://localhost:5173` y verificar la carga inicial de categorías en la tabla (`NÚMERO`, `NOMBRE`, `DESCRIPCIÓN`, `ACCIONES`) conforme a `img/ejemplo1.png`.
  2. Pulsar `"+ Añadir Categoría"`, registrar una nueva categoría en el modal flotante y verificar su aparición inmediata en la tabla y en el backend.
  3. Pulsar `"Editar"` en una fila, modificar los campos en el modal superpuesto (`img/ejemplo2.png`), guardar y comprobar la actualización reactiva.
  4. Pulsar `"Eliminar"` en la fila creada y verificar su remoción de la tabla y de la base de datos.
  5. Ejecutar la secuencia de pruebas del archivo `.http` de productos y relaciones, verificando la integridad de base de datos.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-03.
- **Criterio de Aceptación / Verificación:** Flujo fluido sin errores en la consola del navegador, sin excepciones no controladas en el servidor y con consistencia total de datos.

#### Tarea 4.2: Chequeo estricto de tipos y ejecución de suites de pruebas
- **Alineación con la Consigna:** Resuelve la **Parte B - inciso f** (*"Verificar que el proyecto corre sin errores TypeScript: pnpm dev"*), el criterio de Rúbrica *"Tipado TypeScript (10 pts)"* y *"Estructura y buenas prácticas: Sin errores de TS en consola (10 pts)"* de `docs/consignas.md`.
- **Acción:** Ejecutar las verificaciones estáticas y dinámicas de calidad de código:
  - Frontend: `pnpm build:front` (validación de compilación TypeScript y empaquetado de producción con Vite).
  - Backend: `pnpm test:back` (`pytest` ejecutando la suite organizada por **dominio**: `tests/test_categoria.py` y `tests/test_producto.py` mediante *Sociable Tests* con motor SQLite en memoria aislado).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A.
- **Reglas de Negocio asociadas:** RN-04.
- **Criterio de Aceptación / Verificación:** 0 errores de compilación de TypeScript y 100% de tests de Python pasando exitosamente (actualmente 58 tests automatizados por dominio).

#### Tarea 4.3: Limpieza de directorios y empaquetado para entrega según pautas de cátedra
- **Alineación con la Consigna:** Resuelve la sección **"Modalidad de Entrega"** de `docs/consignas.md`: *"Eliminar la carpeta node_modules antes de comprimir"*, *"Proyecto Frontend comprimido en un archivo .zip"* y *"Proyecto Backend comprimido en un archivo .zip"*.
- **Acción:** Purgar directorios de dependencias, entornos virtuales y artefactos temporales (`node_modules/`, `.venv/`, `dist/`, `__pycache__/`, `.pytest_cache/`, `*.db`). Generar los archivos comprimidos independientes para Frontend y Backend según lo solicitado en la sección "Modalidad de Entrega" de las consignas:
  - Proyecto Frontend comprimido en `.zip` (sin `node_modules`).
  - Proyecto Backend comprimido en `.zip` (sin `.venv` ni `__pycache__`).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A.
- **Reglas de Negocio asociadas:** RN-05.
- **Criterio de Aceptación / Verificación:** Archivos `.zip` generados con la estructura limpia, permitiendo una instalación y ejecución en frío (*clean clone/unzip*) sin fallos.

---

## 3. Checklist de Entrega y Empaquetado Final

- [x] **Entorno y dependencias:** Declarados rigurosamente en `unidad6_backend/requirements.txt`, `unidad6_frontend/package.json` y `package.json` raíz.
- [x] **Frontend reactivo:** CRUD de categorías operativo de extremo a extremo mediante `fetch` nativo y hooks (`useState`, `useEffect`) centralizados en `App.tsx`.
- [x] **Modal funcional:** Formulario de alta/edición dentro de `CategoriaModal.tsx` controlado por estado booleano de visibilidad y backdrop flotante.
- [ ] **Backend modular:** Endpoints de Categorías, Productos y relación `Producto_Categoria` implementados con FastAPI y SQLModel.
- [ ] **Demostración REST Client:** Archivo `.http` disponible en el backend para ejecutar y evidenciar las operaciones de Producto y su relación N:N.
- [x] **CORS habilitado:** Middleware en FastAPI configurado para permitir peticiones desde `http://localhost:5173`.
- [x] **Tipado TypeScript:** Interfaces `Categoria` y `Producto` estrictamente tipadas. Props tipados en todos los componentes funcionales (`.tsx`).
- [x] **Compilación limpia:** `pnpm build:front` finaliza con código de salida 0 y sin errores de TypeScript en consola.
- [x] **Pruebas de backend:** Suite de `pytest` organizada por dominio (`test_categoria.py` y `test_producto.py`) aprobada al 100% (58 tests) con motor de prueba SQLite aislado en memoria.
- [ ] **Archivos comprimidos:** Generados en formato `.zip` independientes para Frontend y Backend conforme a las pautas de entrega de la cátedra.
- [ ] **Verificación post-descompresión:** Instalación y ejecución en frío (*clean install*) validada sin fallos.
