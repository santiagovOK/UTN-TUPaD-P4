# Resolución de Trabajo Práctico 4 - Módulo Proveedores

Estructura de pasos a seguir para la implementación del módulo `proveedor`, basada en los requerimientos del Trabajo Práctico (`docs/consignas.md`) y las pautas técnicas y conceptuales de la Unidad 4 (`docs/unidad4_guia_maestra.md`).

---

### Nota metodologica sobre el orden de implementacion: Enfoque Bottom-Up vs. Top-Down
Al analizar las consignas originales (Paso 3, incisos a, b y c), se identifica una propuesta de diseño Top-Down (de afuera hacia adentro): primero definir los modelos (schemas), luego exponer los endpoints HTTP (routers) y finalmente desarrollar la persistencia y logica de negocio (services). Se comprende que dicho orden pedagógico busca fijar primero el contrato publico visible en Swagger UI.

Tras investigar conceptualmente las implicancias de ambas metodologias en arquitecturas modulares, se optó conscientemente priorizar un enfoque Bottom-Up (de adentro hacia afuera: schemas -> services -> routers) por las siguientes razones tecnicas:
1. Direccion de dependencias: `services.py` depende exclusivamente de `schemas.py`. En cambio, `routers.py` depende de ambos (`schemas` y `services`). Desarrollar primero los servicios evita escribir controladores que invoquen funciones inexistentes.
2. Verificabilidad unitaria: Permite testear y asegurar las reglas de negocio (RN-01 a RN-05) de forma aislada mediante scripts en Python antes de involucrar el framework de transporte HTTP.
3. Construccion incremental segura: Al llegar a la capa de `routers.py`, cada endpoint se enlaza de inmediato con una funcion operativa y verificada, reduciendo la superficie de errores.

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

## Paso 2: Definicion de Schemas y Validacion de Datos (`schemas.py`)
- **Estado**: Completado
- **Objetivo**: Definir los modelos Pydantic con segregacion de responsabilidades (`ProveedorBase`, `ProveedorCreate`, `ProveedorRead`, `ProveedorUpdate`).
- **Modelos implementados**:
  - `ProveedorBase`: Esquema base con los atributos comunes (`codigo`, `razon_social`, `cuit`, `email`, `telefono`, `activo`).
  - `ProveedorCreate`: Hereda de `ProveedorBase` sin campos adicionales para el payload de creacion.
  - `ProveedorRead`: Hereda de `ProveedorBase` e incorpora el campo `id: int` como contrato de salida.
  - `ProveedorUpdate`: Modelo con todos los campos como `Optional` con valor por defecto `None` para permitir actualizaciones parciales o totales.
- **Validaciones y Reglas aplicadas**:
  - **RN-01**: `codigo` obligatorio con `min_length=1`.
  - **RN-03**: `razon_social` obligatoria con `min_length=3`.
  - `cuit`: Validacion de longitud con `min_length=11` y `max_length=15`.
  - Valores por defecto: `email=""`, `telefono=""`, `activo=True`.
- **HUs que ataca/resuelve**:
  - **HU-01 (Registrar un proveedor)**: Validacion estricta de entrada con `ProveedorCreate` y contrato de salida con `ProveedorRead`.
  - **HU-02 (Listar proveedores)**: Esquema de salida en coleccion (`list[ProveedorRead]`).
  - **HU-03 (Consultar un proveedor)**: Esquema de respuesta `ProveedorRead`.
  - **HU-04 (Actualizar un proveedor)**: Validacion del cuerpo de actualizacion con `ProveedorUpdate` y respuesta con `ProveedorRead`.
  - **HU-05 (Desactivar un proveedor)**: Esquema de respuesta `ProveedorRead` tras la desactivacion.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - **Principio "Fail Fast"**: Los datos malformados se interceptan y rechazan en la frontera de la aplicacion generando respuestas HTTP 422 estandarizadas.
  - **Segregacion de modelos**: Se separa el esquema de entrada del de salida para evitar fugas de datos y asegurar contratos explicitos.
- **Verificacion**: Se ejecuto suite de aserciones en Python validando aceptacion de datos correctos y rechazo con `ValidationError` ante violaciones de longitud minima.
---

## Paso 3: Implementacion de la Capa de Logica de Negocio y Almacenamiento en Memoria (`services.py`)
- **Estado**: Completado
- **Objetivo**: Implementar la lista en memoria `proveedores_db` y las funciones de negocio que aplican las validaciones y lanzan `HTTPException`.

### 3.1 Funcion `crear_proveedor`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-01 (Registrar un proveedor)**
- **Reglas de negocio y comportamiento**:
  - Generacion automatica de identificador autoincremental mediante `id_counter`.
  - **RN-02**: Validacion de unicidad de codigo recorriendo la lista en memoria. Si el codigo ya existe, interrumpe el flujo lanzando `HTTPException(status_code=status.HTTP_409_CONFLICT, detail="...")`.
  - Desempaquetado del modelo de entrada (`data.model_dump()`) combinandolo con el `id` generado para retornar una instancia valida de `ProveedorRead`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Manejo de excepciones de negocio con `raise HTTPException` (Seccion 8) usando constantes semanticas de `fastapi.status` (Seccion 7), garantizando una respuesta JSON estandarizada con `detail`.
- **Verificacion**: Se ejecuto script de pruebas validando creacion exitosa con incremento de ID y captura de error 409 ante intento de duplicacion de codigo.
### 3.2 Funcion `listar_proveedores`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-02 (Listar proveedores)**
- **Reglas de negocio y comportamiento**:
  - Filtrado opcional: Si `activo` es provisto (`True` o `False`), se filtran los elementos correspondientes; si es `None`, se consideran todos los registros.
  - Paginacion por slicing: Se aplican los parametros de desplazamiento (`skip`) y cantidad maxima (`limit`) mediante la expresion `resultado[skip : skip + limit]`.
  - Se provee el alias `obtener_todos = listar_proveedores` para estandarizacion interna.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Filtrado y paginacion con slicing (Seccion 3): Patron estandar en APIs REST para gestionar colecciones de datos en memoria sin sobrecargar la respuesta.
- **Verificacion**: Se ejecuto script de pruebas validando retorno total, paginacion con combinaciones de skip y limit, y filtrado selectivo por estado activo e inactivo.
### 3.3 Funcion `obtener_proveedor_por_id`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-03 (Consultar un proveedor)**
- **Reglas de negocio y comportamiento**:
  - Busqueda lineal por identificador unico (`id`).
  - **RN-04**: Si ningun registro coincide con el `id` solicitado, se interrumpe inmediatamente el flujo lanzando `HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Proveedor con id {id} no encontrado")`.
  - Se declara el alias `obtener_por_id = obtener_proveedor_por_id`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Manejo de excepciones 404 (Seccion 8): Uso de `raise HTTPException` para comunicar al cliente que el recurso solicitado no existe, produciendo una respuesta JSON con estructura `{"detail": "..."}`.
- **Verificacion**: Se ejecuto script de pruebas validando retorno de datos para IDs existentes y generacion de error 404 ante identificadores inexistentes.
### 3.4 Funcion `actualizar_proveedor`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-04 (Actualizar un proveedor)**
- **Reglas de negocio y comportamiento**:
  - **RN-04**: Verifica la existencia del proveedor delegando en `obtener_proveedor_por_id(id)`. Si el ID no existe, se dispara automaticamente la excepcion HTTP 404 Not Found.
  - **RN-02**: En caso de enviarse un nuevo `codigo` diferente al actual, valida que no pertenezca a ningun otro proveedor registrado (`p.id != id`). Si hay colision, interrumpe el flujo con `HTTPException(status_code=status.HTTP_409_CONFLICT, detail="...")`.
  - Fusiona los datos existentes con los campos explícitamente enviados usando `data.model_dump(exclude_unset=True)`.
  - Reemplaza la instancia en la lista en memoria y retorna el `ProveedorRead` actualizado.
  - Se declara el alias `actualizar_total = actualizar_proveedor`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Serializacion y exportacion con `.model_dump(exclude_unset=True)` (Seccion 4): Permite aplicar selectivamente los campos enviados sin sobrescribir con valores nulos los atributos no especificados.
  - Manejo de excepciones 404 y 409 (Seccion 8): Control de integridad referencial y de unicidad antes de modificar el estado.
- **Verificacion**: Se ejecuto script de pruebas validando actualizacion exitosa, preservacion de codigo existente, rechazo 404 ante ID inexistente y rechazo 409 por colisión de codigo.
### 3.5 Funcion `desactivar_proveedor`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-05 (Desactivar un proveedor)**
- **Reglas de negocio y comportamiento**:
  - **RN-04**: Valida la existencia del proveedor invocando `obtener_proveedor_por_id(id)`. Si el ID no existe en memoria, se aborta la operacion con error HTTP 404 Not Found.
  - **RN-05**: Evalua el estado actual del registro. Si `proveedor_actual.activo` ya es `False`, lanza `HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"El proveedor con id {id} ya se encuentra desactivado")`.
  - Borrado logico: Actualiza el atributo `activo = False` preservando la totalidad del historial de datos del proveedor.
  - Reemplaza el elemento en `proveedores_db` y retorna la instancia actualizada.
  - Se declara el alias `desactivar = desactivar_proveedor`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Borrado logico vs. fisico: Se mantiene el registro historico sin destruir la entidad, comunicando el estado de conflicto (409 Conflict, Seccion 7 y 8) cuando una operacion contradice el estado previo del recurso.
- **Verificacion**: Se ejecuto script de pruebas validando desactivacion correcta, rechazo 404 ante ID inexistente y rechazo 409 Conflict ante intento de desactivar un proveedor inactivo.
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
