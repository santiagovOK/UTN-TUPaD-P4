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
  - **RN-02**: Validacion de unicidad de codigo recorriendo la lista en memoria. Si el codigo ya existe, interrumpe el flujo lanzando `HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mensaje explicativo")`.
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
  - Manejo de excepciones 404 (Seccion 8): Uso de `raise HTTPException` para comunicar al cliente que el recurso solicitado no existe, produciendo una respuesta JSON con estructura de detalle explicativo.
- **Verificacion**: Se ejecuto script de pruebas validando retorno de datos para IDs existentes y generacion de error 404 ante identificadores inexistentes.
### 3.4 Funcion `actualizar_proveedor`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-04 (Actualizar un proveedor)**
- **Reglas de negocio y comportamiento**:
  - **RN-04**: Verifica la existencia del proveedor delegando en `obtener_proveedor_por_id(id)`. Si el ID no existe, se dispara automaticamente la excepcion HTTP 404 Not Found.
  - **RN-02**: En caso de enviarse un nuevo `codigo` diferente al actual, valida que no pertenezca a ningun otro proveedor registrado (`p.id != id`). Si hay colision, interrumpe el flujo con `HTTPException(status_code=status.HTTP_409_CONFLICT, detail="mensaje explicativo")`.
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

## Paso 4: Implementacion de Controladores y Endpoints (`routers.py`)
- **Estado**: Completado
- **Objetivo**: Configurar el enrutador con `prefix="/proveedores"` y definir los endpoints REST con códigos de estado semánticos (`status_code`).
- **Estandar de tipado con `typing.Annotated` (Guia Maestra Unidad 4, Seccion 5)**: Se adopto el patron moderno `Annotated[Tipo, ReglaDeValidacion()] = ValorPorDefecto` para la declaracion de Path y Query Parameters. Esta practica desacopla el tipo base (`int`, `bool`) de los metadatos de transporte y validacion (`Path(gt=0)`, `Query(ge=0, le=50)`), eliminando la necesidad de recurrir al objeto `Ellipsis` como marcador de obligatoriedad y garantizando compatibilidad total con herramientas de analisis estatico.

### 4.1 Endpoint `POST /proveedores/`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-01 (Registrar un proveedor)**
- **Detalle e implementacion**:
  - Decorador `@router.post("/", response_model=schemas.ProveedorRead, status_code=status.HTTP_201_CREATED)`.
  - Recibe el cuerpo de la peticion validado por Pydantic mediante `proveedor: schemas.ProveedorCreate`.
  - Conecta directamente con la capa de servicios invocando `services.crear_proveedor(proveedor)`.
  - Rechaza cuerpos con datos incompletos o invalidos con HTTP 422 Unprocessable Entity (**RN-01, RN-03**).
  - Si el servicio detecta colision de codigo, responde con HTTP 409 Conflict (**RN-02**).
  - Ante exito, responde HTTP 201 Created serializando los datos bajo el contrato `ProveedorRead` (incluyendo su `id`).
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Metodos HTTP con Body y Pydantic (Seccion 4): Deserializacion automatica del payload JSON.
  - Response Model (Seccion 6): Filtro activo de serializacion que garantiza la estructura de salida.
  - Codigos de estado semanticos (Seccion 7): Declaracion explicita de `status.HTTP_201_CREATED` para creacion de recursos.
- **Verificacion**: Se valido la respuesta HTTP 201 Created y estructura del schema, la captura de codigo repetido con 409 Conflict y el rechazo 422 ante violaciones de longitud minima.
 
### 4.2 Endpoint `GET /proveedores/`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-02 (Listar proveedores)**
- **Detalle e implementacion**:
  - Decorador `@router.get("/", response_model=List[schemas.ProveedorRead], status_code=status.HTTP_200_OK)`.
  - Declara parametros de consulta fuertemente tipados utilizando `Annotated`: `skip: Annotated[int, Query(ge=0)] = 0`, `limit: Annotated[int, Query(ge=1, le=50)] = 10` y `activo: Annotated[Optional[bool], Query()] = None`.
  - Valida restricciones numericas en la entrada: cualquier valor de `skip < 0` o `limit` fuera del rango [1, 50] es rechazado automaticamente con HTTP 422 Unprocessable Entity.
  - Conecta con la capa de servicios delegando la ejecucion en `services.listar_proveedores(skip, limit, activo)`.
  - Responde HTTP 200 OK serializando la coleccion bajo el modelo `List[ProveedorRead]`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Parametros de consulta (Seccion 3): Manejo estandar de filtros y paginacion.
  - Validaciones declarativas y metadatos (Seccion 5): Aplicacion de operadores relacionales `ge` y `le` en `Query` para blindar la entrada.
  - Respuestas que retornan listas de modelos (Seccion 6): Tipado estricto con `response_model=List[ProveedorRead]`.
- **Verificacion**: Se valido la respuesta HTTP 200 OK general, la paginacion mediante skip/limit, el filtrado selectivo por estado activo e inactivo, y el rechazo 422 ante limit=0, limit=51 y skip=-1.

### 4.3 Endpoint `GET /proveedores/{id}`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-03 (Consultar un proveedor)**
- **Detalle e implementacion**:
  - Decorador `@router.get("/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK)`.
  - Declara el parametro de ruta validado `id: Annotated[int, Path(gt=0, description="Identificador unico del proveedor")]`.
  - Si el cliente envia un valor no entero o un numero menor o igual a cero (`id <= 0`), FastAPI responde de inmediato con HTTP 422 Unprocessable Entity.
  - Invoca `services.obtener_proveedor_por_id(id)`. Si el ID no existe en memoria, el servicio lanza HTTP 404 Not Found (**RN-04**).
  - Ante coincidencia, responde HTTP 200 OK serializando los datos bajo `ProveedorRead`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Parametros de ruta (Seccion 2): Extraccion automatica del segmento URL, coercion de tipos a entero nativo y validacion de tipos.
  - Validacion numerica en Path (Seccion 5): Restriccion de dominio con `gt=0`.
  - Manejo de recursos inexistentes (Seccion 8): Retorno consistente de 404 Not Found ante entidades que no existen en el catalogo.
- **Verificacion**: Se valido la respuesta HTTP 200 OK para ID valido, el error 404 Not Found ante ID inexistente, y el rechazo 422 ante identificadores no numericos o menores o iguales a cero.

### 4.4 Endpoint `PUT /proveedores/{id}`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-04 (Actualizar un proveedor)**
- **Detalle e implementacion**:
  - Decorador `@router.put("/{id}", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK)`.
  - Combina parametros de ruta y cuerpo: recibe `id: Annotated[int, Path(gt=0)]` y el payload validado `proveedor: schemas.ProveedorUpdate`.
  - Conecta con la capa de servicios invocando `services.actualizar_proveedor(id, proveedor)`.
  - Si el ID no existe, se devuelve HTTP 404 Not Found (**RN-04**).
  - Si el nuevo codigo colisiona con otro registro, se devuelve HTTP 409 Conflict (**RN-02**).
  - Ante exito, responde HTTP 200 OK serializando el resultado bajo el modelo `ProveedorRead`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Combinacion simultanea de Body y Path (Seccion 4): Identificacion del recurso via URL y envio del payload de modificacion en el cuerpo JSON.
  - Codigos de estado (Seccion 7): Retorno de `status.HTTP_200_OK` para actualizaciones procesadas con contenido.
- **Verificacion**: Se valido la respuesta HTTP 200 OK con los datos actualizados, la respuesta 404 Not Found ante ID inexistente, el conflicto 409 Conflict ante duplicidad de codigo y el error 422 ante identificador menor o igual a cero.

### 4.5 Endpoint `PUT /proveedores/{id}/desactivar`
- **Estado**: Completado
- **HU que ataca/resuelve**: **HU-05 (Desactivar un proveedor)**
- **Detalle e implementacion**:
  - Decorador `@router.put("/{id}/desactivar", response_model=schemas.ProveedorRead, status_code=status.HTTP_200_OK)`.
  - Endpoint de accion para borrado logico: recibe `id: Annotated[int, Path(gt=0)]`.
  - Delega en `services.desactivar_proveedor(id)` para cambiar el estado `activo` a `False`.
  - Si el ID no existe, responde HTTP 404 Not Found (**RN-04**).
  - Si el proveedor ya se encuentra inactivo, responde HTTP 409 Conflict (**RN-05**).
  - Ante exito, responde HTTP 200 OK serializando el registro actualizado bajo `ProveedorRead`.
- **Fundamentacion teorica (Guia Maestra Unidad 4)**:
  - Operaciones de accion especifica (Seccion 2): Uso de sub-rutas semanticas (`/desactivar`) para operaciones transaccionales puntuales sobre un recurso.
  - Manejo de conflictos de estado (Seccion 7 y 8): Notificacion transparente con codigo 409 cuando la accion solicitada es incompatible con el estado actual de la entidad.
- **Verificacion**: Se valido la respuesta HTTP 200 OK con `activo=False`, la respuesta 404 Not Found ante ID inexistente, el conflicto 409 Conflict ante re-desactivacion y el error 422 ante identificador invalido.
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
