# Resolución de Trabajo Práctico 4 - Módulo Proveedores

Estructura de pasos a seguir para la implementación del módulo `proveedor`, basada en los requerimientos del Trabajo Práctico (`docs/consignas.md`) y las pautas técnicas y conceptuales de la Unidad 4 (`docs/unidad4_guia_maestra.md`).

---

## Paso 1: Estructura base del módulo `proveedor`
- **Estado**: Completado
- **Objetivo**: Crear el paquete y los módulos base respetando la arquitectura modular del proyecto (`categoria/`, `producto/`).
- **Archivos creados**:
  - `u1_ej_8_integrador/app/modules/proveedor/__init__.py`: Inicializador del paquete Python.
  - `u1_ej_8_integrador/app/modules/proveedor/schemas.py`: Módulo base para modelos Pydantic.
  - `u1_ej_8_integrador/app/modules/proveedor/services.py`: Módulo base para la lógica de negocio y almacén en memoria.
  - `u1_ej_8_integrador/app/modules/proveedor/routers.py`: Módulo base para la exposición de endpoints con `APIRouter(prefix="/proveedores", tags=["Proveedores"])`.
- **HUs que ataca/resuelve**: Base estructural requerida para **HU-01, HU-02, HU-03, HU-04 y HU-05**.
- **Fundamentación arquitectónica (Guía Maestra Unidad 4)**:
  - **Separación de responsabilidades**: Se aísla el enrutamiento HTTP (`routers.py`), la validación y contratos de datos (`schemas.py`) y la lógica de dominio/persistencia (`services.py`).
  - **Cohesión y modularidad**: Cada módulo de negocio opera de forma independiente y autocontenida, permitiendo escalar la API sin acoplamientos indeseados.
- **Verificación**: Se verificó la importación exitosa del paquete y submódulos vía Python runtime.
---

## Paso 2: Definición de Schemas y Validación de Datos (`schemas.py`)
- **Objetivo**: Definir los modelos Pydantic con segregación de responsabilidades (`ProveedorBase`, `ProveedorCreate`, `ProveedorRead`, `ProveedorUpdate`).
- **Validaciones**: Tipos de datos, longitudes mínimas/máximas y valores por defecto.
- **HUs que ataca/resuelve**:
  - **HU-01 (Registrar un proveedor)**: Validación estricta del cuerpo de entrada con `ProveedorCreate` (`min_length` para RN-01 y RN-03) y esquema de salida `ProveedorRead`.
  - **HU-02 (Listar proveedores)**: Esquema de salida en colección (`list[ProveedorRead]`).
  - **HU-03 (Consultar un proveedor)**: Esquema de respuesta `ProveedorRead`.
  - **HU-04 (Actualizar un proveedor)**: Validación del cuerpo de actualización con `ProveedorUpdate` y respuesta con `ProveedorRead`.
  - **HU-05 (Desactivar un proveedor)**: Esquema de respuesta `ProveedorRead` tras la desactivación.

---

## Paso 3: Implementación de la Capa de Lógica de Negocio y Almacenamiento en Memoria (`services.py`)
- **Objetivo**: Implementar la lista en memoria `proveedores_db` y las funciones de negocio que aplican las validaciones y lanzan `HTTPException`.

### 3.1 Función `crear_proveedor`
- **HU que ataca/resuelve**: **HU-01 (Registrar un proveedor)**
- **Reglas de negocio**: Generación de ID incremental y validación de unicidad de código (RN-02 -> 409 Conflict).

### 3.2 Función `listar_proveedores`
- **HU que ataca/resuelve**: **HU-02 (Listar proveedores)**
- **Reglas de negocio**: Paginación mediante slicing (`skip`, `limit`) y filtrado opcional por estado (`activo`).

### 3.3 Función `obtener_proveedor_por_id`
- **HU que ataca/resuelve**: **HU-03 (Consultar un proveedor)**
- **Reglas de negocio**: Búsqueda por ID y validación de existencia (RN-04 -> 404 Not Found).

### 3.4 Función `actualizar_proveedor`
- **HU que ataca/resuelve**: **HU-04 (Actualizar un proveedor)**
- **Reglas de negocio**: Validación de existencia del recurso (RN-04 -> 404 Not Found) y verificación de que el nuevo código no colisione con otro proveedor (RN-02 -> 409 Conflict).

### 3.5 Función `desactivar_proveedor`
- **HU que ataca/resuelve**: **HU-05 (Desactivar un proveedor)**
- **Reglas de negocio**: Validación de existencia (RN-04 -> 404 Not Found) y verificación de que no esté previamente desactivado (RN-05 -> 409 Conflict).

---

## Paso 4: Implementación de Controladores y Endpoints (`routers.py`)
- **Objetivo**: Configurar el enrutador con `prefix="/proveedores"` y definir los endpoints REST con códigos de estado semánticos (`status_code`).

### 4.1 Endpoint `POST /proveedores/`
- **HU que ataca/resuelve**: **HU-01 (Registrar un proveedor)**
- **Detalle**: Recibe `ProveedorCreate`, responde `201 Created` con `ProveedorRead`, valida cuerpo (422, RN-01 y RN-03) y conflicto de código (409, RN-02).

### 4.2 Endpoint `GET /proveedores/`
- **HU que ataca/resuelve**: **HU-02 (Listar proveedores)**
- **Detalle**: Recibe parámetros de consulta con validación numérica y opcionales (`skip: ge=0`, `limit: ge=1, le=50`, `activo: bool | None`), responde `200 OK` con `list[ProveedorRead]`.

### 4.3 Endpoint `GET /proveedores/{id}`
- **HU que ataca/resuelve**: **HU-03 (Consultar un proveedor)**
- **Detalle**: Recibe path parameter `id: int`, responde `200 OK` con `ProveedorRead`, maneja error de recurso inexistente (404 Not Found, RN-04).

### 4.4 Endpoint `PUT /proveedores/{id}`
- **HU que ataca/resuelve**: **HU-04 (Actualizar un proveedor)**
- **Detalle**: Recibe `id: int` y cuerpo `ProveedorUpdate`, responde `200 OK` con `ProveedorRead`, controla existencia (404 Not Found, RN-04) y unicidad de código (409 Conflict, RN-02).

### 4.5 Endpoint `PUT /proveedores/{id}/desactivar`
- **HU que ataca/resuelve**: **HU-05 (Desactivar un proveedor)**
- **Detalle**: Endpoint de acción para borrado lógico, responde `200 OK` con `ProveedorRead`, controla existencia (404 Not Found, RN-04) y estado previo (409 Conflict, RN-05).

---

## Paso 5: Registro del Router en la Aplicación (`app/main.py`)
- **Objetivo**: Integrar `proveedor_router` en la instancia central de `FastAPI`.
- **HUs que ataca/resuelve**: Habilita la exposición pública en la API y en Swagger UI para **HU-01, HU-02, HU-03, HU-04 y HU-05**.

---

## Paso 6: Verificación y Pruebas con REST Client (`tests/proveedores.http`)
- **Objetivo**: Diseñar la batería de pruebas HTTP que certifiquen el correcto funcionamiento y los códigos de respuesta exigidos.
- **HUs que ataca/resuelve**:
  - **HU-01**: Pruebas de alta exitosa (201), validación de campos obligatorios/longitud (422) y código duplicado (409).
  - **HU-02**: Pruebas de listado general (200), filtrado por `activo=true`/`activo=false` y paginación con `skip` y `limit`.
  - **HU-03**: Pruebas de consulta por ID existente (200) e inexistente (404).
  - **HU-04**: Pruebas de actualización completa (200), ID inexistente (404) y colisión de código (409).
  - **HU-05**: Pruebas de borrado lógico (200), ID inexistente (404) y rechazo por intento de desactivar proveedor ya inactivo (409).
