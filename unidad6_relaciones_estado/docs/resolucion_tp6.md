# Resolución y Plan de Ejecución — Trabajo Práctico 6

> **Materia:** Programación IV (Tecnicatura Universitaria en Programación a Distancia - UTN)  
> **Tema:** Relaciones en Backend (FastAPI - SQLModel / PostgreSQL) y Gestión de Estado en Frontend (React 19 - TypeScript - Hooks)  
> **Estrategia:** Descomposición "Bottom-Up" (de menor a mayor dependencia) orientada a tablero Kanban. Cada tarea referencia explícitamente las Historias de Usuario (HU) y Reglas de Negocio (RN) correspondientes a las consignas del trabajo práctico. Las tareas se organizan en fases secuenciales donde cada nivel provee la base necesaria para el siguiente.

---

## 1. Matriz de Trazabilidad Rápida

| ID | Tipo | Descripción Sintética | Fase Asignada |
| :--- | :---: | :--- | :---: |
| **HU-01** | HU | Listado reactivo de categorías en la interfaz (React + Tailwind CSS). | Fase 1 (UI) / Fase 2 (Fetch) |
| **HU-02** | HU | Creación y edición interactiva de categorías mediante modal reactivo (`CategoriaModal.tsx`) controlado con `useState`. | Fase 1 (UI) / Fase 2 (Fetch) |
| **HU-03** | HU | Eliminación de categorías desde las tarjetas de catálogo (`CategoriaCard.tsx`) con confirmación y sincronización de estado. | Fase 2 (Fetch) |
| **RN-01** | RN | Modelado y endpoints REST de `Producto` y relación muchos a muchos (`Producto_Categoria`) testeados con archivo REST Client (`.http`) sin requerir interfaz gráfica. | Fase 3 (Backend) |
| **RN-02** | RN | Uso estricto de `fetch` nativo y hooks estándar (`useState`, `useEffect`) centralizados en `App.tsx`. Componentes hijos funcionales puros sin hooks propios. | Fase 2 (Frontend) |
| **RN-03** | RN | Configuración y habilitación de CORS en FastAPI para permitir solicitudes Cross-Origin desde el origen del frontend (`http://localhost:5173`). | Fase 1 (Infraestructura) |
| **RN-04** | RN | Tipado estático riguroso en TypeScript (`Categoria`, `Producto`) y validación de esquemas en backend con Pydantic / SQLModel sin discrepancias de contrato. | Fase 1 / Fase 3 |
| **RN-05** | RN | Estructura modular de proyecto y empaquetado de entrega en archivos `.zip` independientes excluyendo directorios de dependencias (`node_modules/`, `.venv/`, `dist/`). | Fase 1 / Fase 4 |

---

## 2. Desglose de Tareas "Bottom-Up" para Tablero Kanban

```text
[ Fase 1: Infraestructura Base, UI Estática, Endpoints de Categoría & Documentación ] (COMPLETADA)
                                        ↓
[ Fase 2: Integración Frontend — Estado Reactivo & Fetch API ] (PENDIENTE)
                                        ↓
[ Fase 3: Backend — Modelos y Endpoints de Producto & Relaciones ] (PENDIENTE)
                                        ↓
[ Fase 4: Pruebas Integradas, Empaquetado y Entrega Final ] (PENDIENTE)
```

---

### FASE 1: Infraestructura Base, UI Estática, Endpoints de Categoría y Documentación
> **Estado:** **COMPLETADA**  
> **Criterio de Dependencia:** Nivel 0 (Base). No depende de capas superiores; establece la estructura del repositorio, el tipado de datos base, la configuración de desarrollo concurrente, los endpoints en memoria de categorías y los componentes presentacionales estáticos importados y adaptados de la Unidad 5.

> **Nota de Diseño Técnico:**  
> Se adoptó un enfoque de migración limpia desde la base de la Unidad 5: se purgó el acoplamiento a productos en el frontend para enfocar la interfaz exclusivamente en el CRUD de Categorías (conforme a las consignas del TP6), y se modularizó el backend en dominios independientes (`categoria` y `producto`). La configuración de `concurrently` en la raíz (`package.json`) permite coordinar el desarrollo fullstack con un único comando unificado (`pnpm dev`), a la vez que se preserva la capacidad de ejecutar y depurar cada capa de forma aislada.

#### Tarea 1.1: Configuración de la estructura del monorepo, dependencias y scripts de orquestación concurrente
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
- **Acción:** Importar y adaptar el módulo `categoria` en `unidad6_backend/app/modules/categoria/` con esquemas Pydantic (`CategoriaCreate`, `CategoriaRead`), servicio de datos y router REST (`GET /categorias/`, `POST /categorias/`, `GET /categorias/{id}`, `PUT /categorias/{id}`, `DELETE /categorias/{id}`). Habilitar middleware CORS para `http://localhost:5173`.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Contratos de datos (`schemas.py`):** Modelos `CategoriaBase`, `CategoriaCreate` y `CategoriaRead` con campos obligatorios (`id`, `nombre`) y opcionales (`descripcion`, `activo`), adaptando el esquema para compatibilidad plena con el frontend de React.
> - **CORS Middleware (`app/main.py`):** Configurado para admitir peticiones desde `http://localhost:5173` y `http://127.0.0.1:5173` con todos los métodos HTTP (`GET`, `POST`, `PUT`, `DELETE`, `OPTIONS`).
> - **Enrutador (`routers.py`):** Prefijo `/categorias` registrado en la instancia principal de FastAPI con códigos de estado HTTP semánticos (200, 201, 204, 404).

- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-03, RN-04.
- **Criterio de Aceptación / Verificación:** Endpoints visibles y operativos en Swagger UI (`/docs`), respondiendo correctamente a llamadas locales con cabeceras CORS habilitadas.

#### Tarea 1.3: Tipado TypeScript y maquetado de componentes estáticos de Categoría en Frontend (Tailwind CSS v4)
- **Acción:** Definir la interface `Categoria` en `src/types/categoria.ts` y maquetar componentes funcionales puros en `src/components/`: `Navbar.tsx`, `CategoriaCard.tsx`, `CategoriaList.tsx`, `CategoriaModal.tsx`, `Footer.tsx`. Ensamblar en `App.tsx` con datos mockeados.
- **Estado:** **Completada**

> **Implementación y Verificación realizada:**
> - **Modelado de Tipos (`categoria.ts`):** Interface estricta `Categoria` tipando `id: number`, `nombre: string`, `descripcion?: string`, `activo?: boolean`.
> - **Componentes Funcionales Puros:** Cada componente recibe datos y callbacks mediante `props` fuertemente tipados con TypeScript. Sin estado interno ni hooks impuros.
> - **Estilizado Tailwind CSS v4:** Maquetación responsiva con Tailwind CSS v4, badges semánticos de estado (activo/inactivo), accesibilidad para teclado (Skip Link, focus visible, ARIA labels).
> - **Verificación:** Ejecución de `pnpm build` (`tsc -b && vite build`) completada con 0 errores de tipado o compilación.

- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-02, RN-04.
- **Criterio de Aceptación / Verificación:** La aplicación compila limpiamente y renderiza la lista de tarjetas y el modal estático sin dependencias de estado mutable.

#### Tarea 1.4: Documentación integral del proyecto y guías de ejecución
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

### FASE 2: Integración Frontend — Estado Reactivo & Fetch API
> **Estado:** **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 1. Depende de la UI estática y los endpoints de Categoría de la Fase 1. Conecta la capa visual con la API REST utilizando hooks estándar (`useState`, `useEffect`) y `fetch` nativo exclusivamente en `App.tsx`.

#### Tarea 2.1: Implementación de estado centralizado en `App.tsx` (`useState`)
- **Acción:** Declarar y estructurar las variables de estado en `src/App.tsx`:
  - `categorias: Categoria[]` (colección reactiva de categorías).
  - `isModalOpen: boolean` (control de visibilidad del modal de creación/edición).
  - `categoriaEnEdicion: Categoria | null` (almacena la categoría seleccionada para edición o `null` para alta).
  - `loading: boolean` (estado de carga para retroalimentación visual).
  - `error: string | null` (registro de errores de red o servidor).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-01, HU-02.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** El estado se gestiona de forma inmutable en el componente contenedor raíz y se distribuye a los componentes hijos mediante props. Los componentes hijos permanecen como funciones puras sin hooks propios.

#### Tarea 2.2: Sincronización de datos iniciales con `useEffect` y `fetch` nativo (`GET /categorias`)
- **Acción:** Implementar un efecto secundario en `App.tsx` mediante `useEffect` con array de dependencias vacío `[]` para realizar una petición asíncrona mediante `fetch` nativo hacia `http://localhost:8000/categorias/` al montar el componente, actualizando el estado `categorias`.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-01.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** Al acceder a la aplicación en el navegador, se realiza la llamada HTTP GET y las categorías devueltas por el backend se pintan automáticamente en la grilla de `CategoriaList`.

#### Tarea 2.3: Implementación de funciones CRUD de mutación con `fetch` nativo (`POST`, `PUT`, `DELETE`)
- **Acción:** Desarrollar en `App.tsx` los controladores de eventos asíncronos y transferirlos como callbacks a los componentes hijos:
  - `handleCreate(categoriaData)`: Petición `POST http://localhost:8000/categorias/` con payload JSON. Agrega el nuevo elemento al estado inmutable `categorias` y cierra el modal.
  - `handleUpdate(id, categoriaData)`: Petición `PUT http://localhost:8000/categorias/{id}`. Actualiza la categoría en el estado inmutable `categorias` y cierra el modal.
  - `handleDelete(id)`: Confirmación interactiva al usuario y posterior petición `DELETE http://localhost:8000/categorias/{id}`. Filtra y remueve la categoría del estado inmutable.
  - `handleOpenCreateModal()`: Setea `categoriaEnEdicion` en `null` y abre el modal.
  - `handleOpenEditModal(categoria)`: Setea la categoría seleccionada en `categoriaEnEdicion` y abre el modal con los campos precargados.
  - `handleCloseModal()`: Cierra el modal y resetea `categoriaEnEdicion`.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** Operaciones completas de alta, modificación y eliminación ejecutables de extremo a extremo desde el navegador sin recargar la página web, persistiendo los cambios en el backend.

#### Tarea 2.4: Manejo de feedback de usuario, estados de carga y errores de red
- **Acción:** Incorporar en la interfaz indicadores visuales durante las peticiones en curso (spinner de carga, deshabilitación de botones de acción para prevenir dobles submits), mensajes de alerta ante errores de conexión o respuestas HTTP 4xx/5xx, y mensajes informativos cuando no existan categorías cargadas (*empty state*).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-02.
- **Criterio de Aceptación / Verificación:** El usuario recibe retroalimentación visual clara e inmediata sobre el éxito o fracaso de cada operación sin estados inconsistentes.

---

### FASE 3: Backend — Modelos y Endpoints de Producto & Relaciones
> **Estado:** **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 2. Implementa la lógica de backend requerida para el catálogo de productos y su relación N:N con categorías, sin requerir interfaz gráfica de usuario (conforme a RN-01).

#### Tarea 3.1: Modelado y Schemas relacionales para `Producto` y tabla intermedia `Producto_Categoria` (SQLModel / Pydantic)
- **Acción:** Definir en `unidad6_backend/app/models/` y `unidad6_backend/app/modules/producto/schemas.py`:
  - Tabla intermedia `ProductoCategoria` (o `Producto_Categoria`) con clave primaria compuesta (`producto_id`, `categoria_id`) y claves foráneas con restricción de eliminación en cascada.
  - Modelo persistente `Producto` con los campos exigidos por la consigna: `id: int`, `nombre: str`, `descripcion: str`, `precio_base: str`, `imagen_url: list[str]`, `disponible: bool`.
  - Esquemas DTO de Pydantic: `ProductoBase`, `ProductoCreate`, `ProductoRead`, `ProductoUpdate` y esquemas de asociación.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01, RN-04.
- **Criterio de Aceptación / Verificación:** Tablas relacionales creadas y vinculadas con `Relationship` y `link_model` en SQLModel, sin ciclos de importación ni violaciones de integridad referencial.

#### Tarea 3.2: Servicios y validaciones de negocio para Productos y vinculación con Categorías
- **Acción:** Implementar en `services.py` y `validators.py` del módulo `producto`:
  - Operaciones CRUD completas para la entidad `Producto`.
  - Funciones para asociar y desasociar categorías a un producto específico.
  - Validaciones de existencia previa de producto y categoría antes de persistir vínculos en la tabla intermedia.
  - Consultas optimizadas con Eager Loading (`selectinload`) para evitar el problema $N+1$.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** Cobertura de pruebas unitarias con `pytest` validando la persistencia y recuperación de productos con sus categorías asociadas.

#### Tarea 3.3: Exposición de endpoints REST en `unidad6_backend/app/modules/producto/routers.py`
- **Acción:** Registrar las rutas REST en el enrutador de productos:
  - `POST /productos/`: Creación de producto.
  - `GET /productos/`: Listado paginado de productos.
  - `GET /productos/{id}`: Detalle de producto con sus categorías vinculadas.
  - `PUT /productos/{id}`: Modificación de producto.
  - `DELETE /productos/{id}`: Eliminación física o lógica de producto.
  - `POST /productos/{id}/categorias/{categoria_id}`: Asociación de categoría a producto.
  - `DELETE /productos/{id}/categorias/{categoria_id}`: Desvinculación de categoría de producto.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** Endpoints accesibles vía Swagger UI (`/docs`) y testeables con respuestas HTTP semánticas (200, 201, 204, 404, 409).

#### Tarea 3.4: Elaboración de archivo de pruebas REST Client (`productos.http` y `categorias.http`)
- **Acción:** Crear los archivos de solicitudes HTTP ejecutables para VS Code REST Client / JetBrains HTTP Client que demuestren el funcionamiento integral de la API sin requerir frontend:
  - Peticiones ordenadas para crear categorías.
  - Creación de productos con diferentes atributos.
  - Asociación de productos a múltiples categorías (relación N:N).
  - Consulta de producto verificando categorías anidadas en la respuesta JSON.
  - Actualización y eliminación de asociaciones y registros.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A (Backend / REST Client).
- **Reglas de Negocio asociadas:** RN-01.
- **Criterio de Aceptación / Verificación:** El archivo `.http` se entrega junto al proyecto y ejecuta con 100% de éxito contra el servidor local.

---

### FASE 4: Pruebas Integradas, Empaquetado y Entrega Final
> **Estado:** **PENDIENTE**  
> **Criterio de Dependencia:** Nivel 3. Depende de la finalización de las Fases 1, 2 y 3. Consolida la solución completa, ejecuta validaciones finales de extremo a extremo y genera los paquetes comprimidos para entrega.

#### Tarea 4.1: Validación de flujo integral de extremo a extremo (E2E Smoke Test)
- **Acción:** Iniciar el entorno fullstack unificado (`pnpm dev`) y verificar el ciclo de vida completo:
  1. Acceder a `http://localhost:5173` y verificar la carga inicial de categorías.
  2. Abrir el modal de alta, registrar una nueva categoría y verificar su aparición inmediata en la grilla y en el backend.
  3. Editar la categoría creada mediante el modal, guardarla y comprobar la actualización reactiva.
  4. Eliminar la categoría y verificar su remoción de la pantalla y del backend.
  5. Ejecutar la secuencia de pruebas del archivo `.http` de productos y relaciones, verificando la integridad de base de datos.
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** HU-01, HU-02, HU-03.
- **Reglas de Negocio asociadas:** RN-01, RN-02, RN-03.
- **Criterio de Aceptación / Verificación:** Flujo fluido sin errores en la consola del navegador, sin excepciones no controladas en el servidor y con consistencia total de datos.

#### Tarea 4.2: Chequeo estricto de tipos y ejecución de suites de pruebas
- **Acción:** Ejecutar las verificaciones estáticas y dinámicas de calidad de código:
  - Frontend: `pnpm build:front` (validación de compilación TypeScript y empaquetado de producción con Vite).
  - Backend: `pnpm test:back` (ejecución de suite de pruebas unitarias e integración con `pytest`).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A.
- **Reglas de Negocio asociadas:** RN-04.
- **Criterio de Aceptación / Verificación:** 0 errores de compilación de TypeScript y 100% de tests de Python pasando exitosamente.

#### Tarea 4.3: Limpieza de directorios y empaquetado para entrega según pautas de cátedra
- **Acción:** Purgar directorios de dependencias, entornos virtuales y artefactos temporales (`node_modules/`, `.venv/`, `dist/`, `__pycache__/`, `.pytest_cache/`, `*.db`). Generar los archivos comprimidos independientes para Frontend y Backend según lo solicitado en la sección "Modalidad de Entrega" de las consignas:
  - Proyecto Frontend comprimido en `.zip` (sin `node_modules`).
  - Proyecto Backend comprimido en `.zip` (sin `.venv` ni `__pycache__`).
- **Estado:** Pendiente
- **Historias de Usuario asociadas:** N/A.
- **Reglas de Negocio asociadas:** RN-05.
- **Criterio de Aceptación / Verificación:** Archivos `.zip` generados con la estructura limpia, permitiendo una instalación y ejecución en frío (*clean clone/unzip*) sin fallos.

---

## 3. Checklist de Entrega y Empaquetado Final

- [ ] **Entorno y dependencias:** Declarados rigurosamente en `unidad6_backend/requirements.txt`, `unidad6_frontend/package.json` y `package.json` raíz.
- [ ] **Frontend reactivo:** CRUD de categorías operativo de extremo a extremo mediante `fetch` nativo y hooks (`useState`, `useEffect`) centralizados en `App.tsx`.
- [ ] **Modal funcional:** Formulario de alta/edición dentro de `CategoriaModal.tsx` controlado por estado booleano de visibilidad.
- [ ] **Backend modular:** Endpoints de Categorías, Productos y relación `Producto_Categoria` implementados con FastAPI y SQLModel.
- [ ] **Demostración REST Client:** Archivo `.http` disponible en el backend para ejecutar y evidenciar las operaciones de Producto y su relación N:N.
- [ ] **CORS habilitado:** Middleware en FastAPI configurado para permitir peticiones desde `http://localhost:5173`.
- [ ] **Tipado TypeScript:** Interfaces `Categoria` y `Producto` estrictamente tipadas. Props tipados en todos los componentes funcionales (`.tsx`).
- [ ] **Compilación limpia:** `pnpm build:front` finaliza con código de salida 0 y sin errores de TypeScript en consola.
- [ ] **Pruebas de backend:** Suite de `pytest` aprobada al 100% con motor de prueba SQLite aislado.
- [ ] **Limpieza de artefactos:** Carpetas `node_modules/`, `.venv/`, `__pycache__/`, `dist/` y bases de datos locales excluidas antes de empaquetar.
- [ ] **Archivos comprimidos:** Generados en formato `.zip` independientes para Frontend y Backend conforme a las pautas de entrega de la cátedra.
- [ ] **Verificación post-descompresión:** Instalación y ejecución en frío (*clean install*) validada sin fallos.
