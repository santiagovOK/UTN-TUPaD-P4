# Resolución y Plan de Ejecución — Trabajo Práctico 5

> **Materia:** Programación IV (Tecnicatura Universitaria en Programación a Distancia - UTN)  
> **Tema:** Migración a PostgreSQL con SQLModel (FastAPI) y Maquetado Frontend con React + TypeScript + Tailwind CSS  
> **Estrategia:** Descomposición "Bottom-Up" (de menor a mayor dependencia) que estoy comenzando a implementar en mis proyectos para mejor organización, orientada a tablero Kanban privado. Cada tarea referencia explícitamente las Historias de Usuario (HU) y Reglas de Negocio (RN) correspondientes a las [consignas](/docs/consignas.md). En ese sentido, las consignas más vinculadas al frontend pasan a la fase 3, pese a que sea uno de los ejes centrales de este trabajo.

---

## 1. Matriz de Trazabilidad Rápida

| ID | Tipo | Descripción Sintética | Fase Asignada |
| :--- | :---: | :--- | :---: |
| **HU-01** | HU | Migrar backend de memoria a PostgreSQL con SQLModel | Fase 1 |
| **HU-02** | HU | Validar datos con Pydantic y reglas de negocio en Service | Fase 2 |
| **HU-03** | HU | Documentar API interactiva con Swagger UI (/docs) | Fase 2 |
| **HU-04** | HU | Crear pantalla de productos con React, TypeScript y Tailwind | Fase 3 / Fase 4 |
| **HU-05** | HU | Aplicar estilos utilitarios con Tailwind CSS (Responsive) | Fase 3 / Fase 4 |
| **HU-06** | HU | Estructurar proyecto con componentes funcionales puros (sin hooks) | Fase 4 |
| **RN-01** | RN | Modelos SQLModel en archivos separados con tipos estrictos | Fase 1 |
| **RN-02** | RN | Nombre obligatorio (`min_length=1`, sin espacios vacíos, error 422) | Fase 2 |
| **RN-03** | RN | Precio mayor o igual a 0 (`ge=0`, error 422) | Fase 2 |
| **RN-04** | RN | No operar sobre IDs inexistentes (404 Not Found) | Fase 2 |
| **RN-05** | RN | Operaciones de escritura persisten en PostgreSQL vía sesión | Fase 1 / Fase 2 |
| **RN-06** | RN | Datos migrados mantienen la misma estructura y validación de u1/u4 | Fase 1 |
| **RN-07** | RN | Interface `Producto` en TS refleja el modelo del backend | Fase 4 |
| **RN-08** | RN | Props tipadas en `.tsx` con TypeScript (prohibido `any`) | Fase 4 |
| **RN-09** | RN | Componentes funcionales puros (sin `useState`, `useEffect`, etc.) | Fase 4 |
| **RN-10** | RN | Estructura de carpetas frontend con `components/` y `types/` | Fase 3 |
| **RN-11** | RN | Archivos de prueba demostrando cada endpoint del CRUD | Fase 2 |
| **RN-12** | RN | `pnpm install` + `pnpm dev` ejecuta sin errores al descomprimir | Fase 3 |
| **RN-13** | RN | `requirements.txt` con fastapi, uvicorn, sqlmodel, psycopg/sqlalchemy | Fase 1 |

---

## 2. Desglose de Tareas "Bottom-Up" para Tablero Kanban

```
[ Fase 1: Base de Datos & Modelos ] (Cero dependencias de negocio)
                ↓
[ Fase 2: Lógica de Servicio, API REST & Pruebas Backend ]
                ↓
[ Fase 3: Infraestructura & Setup Frontend ] (Cero dependencias de UI)
                ↓
[ Fase 4: Componentes Puros, Tipado TS & Pruebas Frontend ]
```

---

### FASE 1: Infraestructura Backend, Modelado de Datos y Persistencia Base
> **Criterio de Dependencia:** Nivel 0 (Base). No depende de ningún endpoint ni interfaz; define la base de datos relacional y las entidades.

> **Nota de Diseño Técnico y Alcance (Alembic vs. DDL de SQLModel):**  
> Si bien la tabla introductoria de conceptos en las consignas menciona a *Alembic* a título informativo, se optó por una **rúbrica estricta** alineada a los requerimientos evaluables (`HU-01`, `RN-13`, `Modalidad de Entrega`), prescindiendo de Alembic por las siguientes razones:
> 1. **Contradicción en las consignas:** La regla de dependencias explícita **`RN-13`** exige taxativamente: *"El proyecto backend debe incluir requirements.txt con fastapi, uvicorn, sqlmodel y sqlalchemy"*, excluyendo a Alembic de la lista requerida. A su vez, la sección de entrega no solicita artefactos de migración (`alembic.ini` / `alembic/versions/`).
> 2. **Ausencia en el desarrollo pedagógico:** En el marco teórico y las clases de la cátedra no se enseñó la configuración ni el flujo de uso de Alembic (inicialización de entorno, mapeo de metadatos de SQLModel, generación ni aplicación de revisiones DDL).
> 3. **Estrategia idiomática de SQLModel:** Se utiliza `SQLModel.metadata.create_all(engine)` invocado en la función `create_db_and_tables()` durante el arranque de la aplicación. Esta alternativa nativa cumple cabalmente con la persistencia en PostgreSQL (`HU-01`, `RN-05`), permitiendo al evaluador clonar el proyecto, indicar su `DATABASE_URL` y levantarlo de forma inmediata sin comandos manuales de migración previos.

#### Tarea 1.1: Entorno y dependencias del Backend
- **Acción:** Configurar el entorno virtual (`python -m venv .venv`) y el archivo `requirements.txt` con las librerías necesarias: `fastapi`, `uvicorn`, `sqlmodel`, `sqlalchemy`, y driver PostgreSQL (`psycopg2-binary`). Luego instalar desde dentro del venv con `pip install -r requirements.txt`.
- **Estado:** Completada — `.venv` creado y dependencias instaladas exitosamente (Python 3.13, verificación `pip list`; `pip check` sin errores).

> **Verificación realizada (dentro de `.venv`, después `pip install -r requirements.txt`):**
> - Todas las dependencias de `requirements.txt` instaladas correctamente: fastapi, uvicorn, sqlmodel, sqlalchemy, psycopg2-binary, pydantic, python-dotenv, pytest, httpx.
> - **Compatibilidad:** `pip check` sin errores (conflictos resueltos).

- **Historias de Usuario asociadas:** `HU-01`
- **Reglas de Negocio asociadas:** `RN-13`
- **Criterio de Aceptación / Verificación:** El entorno virtual se instala limpiamente sin conflictos de dependencias.

#### Tarea 1.2: Configuración de conexión y ciclo de vida de BD (`database.py`) — Completada
- **Acción:** Crear `src/app/database.py` con el engine, variable `DATABASE_URL` desde entorno, `create_db_and_tables()` y `get_session()`; integrar en `main.py` mediante evento `@app.on_event("startup")`.

> **Archivo creado: `src/app/database.py`:**
> ```python
> import os
> from sqlalchemy import create_engine
> from sqlmodel import SQLModel, Session
> 
> DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/tp5_react")
> engine = create_engine(DATABASE_URL, echo=True)
> 
> 
> def create_db_and_tables():
>     SQLModel.metadata.bind = engine
>     SQLModel.metadata.create_all(engine)
> 
> 
> def get_session():
>     with Session(engine) as session:
>         yield session
> ```
> - **Integración en `main.py`:** evento `@app.on_event("startup")` que invoca `create_db_and_tables()` dentro de un bloque `try/except` (fallback local, no quebrar el arranque sin BD).

> Verificación:
> - `database.py` creado con engine `postgresql+psycopg`, URL desde variable de entorno sin hardcodear credenciales. 
> - `create_db_and_tables()` llamada en evento `startup` de FastAPI para crear las tablas antes del primer request.
> - `get_session()` implementado con context manager (`with Session(engine) as session: yield session`).
> - `main.py` importado y modificado correctamente, sintaxis válida (py_compile).

- **Historias de Usuario asociadas:** `HU-01`
- **Reglas de Negocio asociadas:** `RN-05`
- **Criterio de Aceptación / Verificación:** Conexión exitosa contra PostgreSQL. No hay credenciales críticas hardcodeadas.

#### Tarea 1.3: Definición del Modelo de Tabla y Schemas Base (`models/producto.py`, `schemas/producto.py`) — Completada
- **Acción:** Definir la jerarquía SQLModel/Pydantic separando entidad persistible de esquemas DTO:
  - `ProductoBase(SQLModel)`: Campos comunes (nombre, descripcion, precio, categoria, stock, stock_minimo, activo).
  - `Producto(ProductoBase, table=True)`: Modelo de tabla con `id: Optional[int] = Field(default=None, primary_key=True)`.
  - `ProductoCreate(ProductoBase)`: Schema de entrada para creación (sin ID), hereda directamente de `ProductoBase` sin duplicar campos.
  - `ProductoResponse(ProductoBase)`: Schema de salida garantizando que el ID esté presente (`id: int`).
  - `ProductoUpdate(SQLModel)`: Schema para actualización con campos opcionales.
  - `ProductoStockResponse(SQLModel)`: Schema para respuesta de consulta de inventario.
- **Estado:** Completada — Modelos SQLModel y Schemas DTO refactorizados e implementados siguiendo el patrón de herencia estricto (DRY) de la Guía Maestra de la Unidad 5.

> **Implementación y Verificación realizada:**
> - **Herencia DRY:** `ProductoCreate` y `ProductoResponse` heredan de `ProductoBase(SQLModel)`; `Producto` hereda de `ProductoBase` con `table=True` (sintaxis corregida sin `primary_key` como kwarg de clase).
> - **Validaciones declarativas:** `ProductoCreate` rechaza nombres vacíos (`min_length=1`) y precios negativos (`ge=0`), lanzando `ValidationError` (HTTP 422).
> - **Registro DDL en `database.py`:** Se aseguró la importación de `Producto` dentro de `create_db_and_tables()` garantizando que `SQLModel.metadata.create_all(engine)` genere la tabla `producto` en PostgreSQL.
> - **Sintaxis DDL generada y verificada:** Tabla `producto` con columnas y `PRIMARY KEY (id)` validada exitosamente.

- **Historias de Usuario asociadas:** `HU-01`
- **Reglas de Negocio asociadas:** `RN-01`, `RN-06`
- **Criterio de Aceptación / Verificación:** Las tablas se crean correctamente en PostgreSQL mediante `SQLModel.metadata.create_all(engine)` respetando la estructura heredada del gestor en memoria original. ✅ Cumplido.
---

### FASE 2: Lógica de Negocio, Endpoints REST y Pruebas Backend
> **Criterio de Dependencia:** Depende de Fase 1. Implementa las validaciones de negocio en la capa Service y expone las rutas HTTP en el Router.

#### Tarea 2.1: Validaciones de Schema con Pydantic
- **Acción:** Añadir restricciones declarativas con `Field` en `ProductoBase` y `ProductoCreate`:
  - `nombre`: obligatorio, `min_length=1`, sin cadenas vacías o solo espacios en blanco.
  - `precio`: `ge=0` (mayor o igual a cero).
- **Historias de Usuario asociadas:** `HU-02`
- **Reglas de Negocio asociadas:** `RN-02`, `RN-03`
- **Criterio de Aceptación / Verificación:** Envíos con nombre vacío o precio negativo devuelven HTTP 422 con el detalle estructurado.

#### Tarea 2.2: Implementación de la Capa Service (`services/producto_service.py`)
- **Acción:** Implementar operaciones CRUD transaccionales controladas por la sesión de SQLModel:
  - `crear_producto`: `session.add`, `session.commit`, `session.refresh`. Control de duplicados si aplica (409 Conflict).
  - `obtener_producto_por_id`: Retorna la entidad o lanza excepción de dominio / `ValueError` si no existe.
  - `listar_productos`: `session.exec(select(Producto)).all()`.
  - `actualizar_producto`: Actualiza atributos dinámicamente con `exclude_unset=True`, `session.commit`. Lanza excepción si el ID no existe.
  - `eliminar_producto`: Borrado físico (`session.delete`) o lógico según corresponda, con validación de existencia previa.
- **Historias de Usuario asociadas:** `HU-01`, `HU-02`
- **Reglas de Negocio asociadas:** `RN-04`, `RN-05`
- **Criterio de Aceptación / Verificación:** Ningún `commit` se ejecuta fuera de la capa Service. Transacciones atómicas comprobadas.

#### Tarea 2.3: Enrutador HTTP y Manejo de Errores (`routers/producto_router.py` y `main.py`)
- **Acción:** Crear endpoints con `APIRouter` inyectando la sesión con `Depends(get_session)`:
  - `POST /productos/` (201 Created, `response_model=ProductoResponse`).
  - `GET /productos/` (200 OK, `response_model=list[ProductoResponse]`).
  - `GET /productos/{id}` (200 OK, captura `ValueError` y lanza `HTTPException(404)`).
  - `PUT /productos/{id}` o `PATCH /productos/{id}` (200 OK, maneja 404 y 422).
  - `DELETE /productos/{id}` (204 No Content, maneja 404).
- **Historias de Usuario asociadas:** `HU-01`, `HU-02`, `HU-03`
- **Reglas de Negocio asociadas:** `RN-04`, `RN-05`
- **Criterio de Aceptación / Verificación:** En `/docs` (Swagger UI) se muestran los endpoints, esquemas correctos y es posible probarlos interactivamente.

#### Tarea 2.4: Pruebas Unitarias del Backend (Pytest + TestClient)
- **Acción:** Configurar suite de pruebas unitarias y de integración con `pytest` y `TestClient`:
  - Pruebas de validación Pydantic (422 en nombres inválidos o precios `< 0`).
  - Pruebas de CRUD completo con base de datos de test / SQLite en memoria o PostgreSQL de test.
  - Pruebas de errores esperados (404 al consultar/modificar ID inexistente).
  - Exportar/actualizar archivo de pruebas manuales (`.json` de Postman o `.http` de REST Client).
- **Historias de Usuario asociadas:** `HU-01`, `HU-02`, `HU-03`
- **Reglas de Negocio asociadas:** `RN-02`, `RN-03`, `RN-04`, `RN-11`
- **Criterio de Aceptación / Verificación:** Todos los tests de `pytest` pasan en verde. Los archivos de prueba HTTP cubren todos los métodos CRUD.

---

### FASE 3: Infraestructura Frontend, Configuración y Estilos Base
> **Criterio de Dependencia:** Nivel 0 dentro del Frontend. Configura el tooling de construcción, empaquetado y diseño sin depender aún de componentes complejos.

#### Tarea 3.1: Inicialización del Proyecto Frontend con Vite y TypeScript
- **Acción:** Inicializar la aplicación utilizando Vite con template `react-ts` y gestor de paquetes `pnpm`. Configurar `package.json`, `tsconfig.json` y scripts de desarrollo/construcción.
- **Historias de Usuario asociadas:** `HU-04`
- **Reglas de Negocio asociadas:** `RN-10`, `RN-12`
- **Criterio de Aceptación / Verificación:** `pnpm dev` levanta el servidor local en `localhost:5173` y `pnpm build` compila sin errores.

#### Tarea 3.2: Configuración de Tailwind CSS
- **Acción:** Instalar y configurar Tailwind CSS según la guía para Vite (`@tailwindcss/vite` e importación `@import "tailwindcss";` en `src/index.css`).
- **Historias de Usuario asociadas:** `HU-05`
- **Reglas de Negocio asociadas:** `RN-12`
- **Criterio de Aceptación / Verificación:** Las clases utilitarias de Tailwind aplican estilos correctamente en el navegador y el bundle no genera errores de CSS.

#### Tarea 3.3: Estructura de Directorios del Frontend
- **Acción:** Crear la estructura de carpetas estándar requerida:
  - `src/types/`
  - `src/components/`
  - `src/tests/` (para pruebas unitarias de frontend)
- **Historias de Usuario asociadas:** `HU-06`
- **Reglas de Negocio asociadas:** `RN-10`
- **Criterio de Aceptación / Verificación:** Árbol de carpetas limpio y alineado a las consignas y la guía maestra.

---

### FASE 4: Modelado de Tipos, Componentes Puros y Pruebas Frontend
> **Criterio de Dependencia:** Depende de Fase 3 y del contrato de datos establecido en Fase 1/2. Construye la UI declarativa y tipada.

#### Tarea 4.1: Definición de Tipos TypeScript (`src/types/producto.ts`)
- **Acción:** Declarar la interface `Producto` reflejando fielmente los atributos del backend:
  ```typescript
  export interface Producto {
    id: number;
    nombre: string;
    descripcion?: string;
    precio: number;
  }
  ```
- **Historias de Usuario asociadas:** `HU-04`
- **Reglas de Negocio asociadas:** `RN-07`, `RN-08`
- **Criterio de Aceptación / Verificación:** Tipos estrictos sin uso de `any`. Compatibilidad exacta con el schema `ProductoResponse` del backend.

#### Tarea 4.2: Creación de Componentes Funcionales Puros (`src/components/`)
- **Acción:** Desarrollar los 5 componentes requeridos como funciones puras (sin `useState`, sin `useEffect`, props estrictamente tipadas):
  1. `Navbar.tsx`: Barra de navegación con branding y diseño responsive.
  2. `ProductoCard.tsx`: Recibe un `producto: Producto` por props y renderiza su tarjeta con Tailwind.
  3. `ProductoList.tsx`: Recibe `productos: Producto[]` y renderiza la grilla/lista mapeando con `.map()` y `key={producto.id}`.
  4. `ProductoForm.tsx`: Maquetado del formulario de alta con labels, inputs y botón de submit (solo estructura/estilos, sin lógica de estado).
  5. `Footer.tsx`: Pie de página informativo con año dinámico y estilos consistentes.
- **Historias de Usuario asociadas:** `HU-04`, `HU-05`, `HU-06`
- **Reglas de Negocio asociadas:** `RN-08`, `RN-09`
- **Criterio de Aceptación / Verificación:** Cero hooks en el código. Todas las props validadas por el compilador de TypeScript.

#### Tarea 4.3: Ensamblado y Maquetado en `App.tsx`
- **Acción:** Integrar los componentes en `App.tsx` suministrando un array de al menos 3 productos hardcodeados que cumplan con la interface `Producto`. Diseñar el layout responsivo (`grid`, `flex`, espaciados coherentes).
- **Historias de Usuario asociadas:** `HU-04`, `HU-05`
- **Reglas de Negocio asociadas:** `RN-08`, `RN-09`, `RN-12`
- **Criterio de Aceptación / Verificación:** La pantalla visualiza el navbar, el formulario maquetado, la grilla con al menos 3 productos y el footer. `pnpm dev` corre sin warnings ni errores de TS.

#### Tarea 4.4: Pruebas Unitarias del Frontend (Vitest + Testing Library)
- **Acción:** Configurar pruebas unitarias con Vitest y React Testing Library para validar el contrato de los componentes:
  - Prueba de renderizado de `ProductoCard` con datos correctos.
  - Prueba de renderizado de lista en `ProductoList` (verificar cantidad de tarjetas según el array provisto).
  - Verificación de ausencia de hooks y cumplimiento de componentes puros.
- **Historias de Usuario asociadas:** `HU-04`, `HU-06`
- **Reglas de Negocio asociadas:** `RN-08`, `RN-09`
- **Criterio de Aceptación / Verificación:** Suite `pnpm test` ejecuta y pasa todos los tests unitarios de componentes.

---

## 3. Checklist de Entrega y Empaquetado Final
- [ ] Backend: Dependencias registradas en `requirements.txt` (`RN-13`).
- [ ] Backend: Archivos `.json` de Postman o `.http` de REST Client disponibles y probados (`RN-11`).
- [ ] Frontend: `node_modules` y directorios `.venv` eliminados antes de comprimir.
- [ ] Ambos proyectos organizados y comprimidos en un único archivo `.zip`.
- [ ] Verificación post-descompresión: `pnpm install` y `pnpm dev` funcionando inmediatamente sin errores (`RN-12`).
