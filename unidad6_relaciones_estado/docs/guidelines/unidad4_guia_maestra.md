# Guía Maestra de FastAPI y Pydantic en base a los materiales teóricos de la unidad 4 - Programación 4

## Arquitectura, Validación y Construcción de APIs REST Modernas

Documento técnico de referencia consolidado a partir de las Unidades y Actividades 1 a 4. Diseñado como guía práctica y conceptual completa para el diseño y desarrollo de servicios backend con FastAPI y Pydantic.

---

## Tabla de Contenidos

- [Guía Maestra de FastAPI y Pydantic en base a los materiales teóricos de la unidad 4 - Programación 4](#guía-maestra-de-fastapi-y-pydantic-en-base-a-los-materiales-teóricos-de-la-unidad-4---programación-4)
  - [Arquitectura, Validación y Construcción de APIs REST Modernas](#arquitectura-validación-y-construcción-de-apis-rest-modernas)
  - [Tabla de Contenidos](#tabla-de-contenidos)
  - [1. Fundamentos y Arquitectura de FastAPI](#1-fundamentos-y-arquitectura-de-fastapi)
    - [¿Qué es FastAPI y por qué utilizarlo?](#qué-es-fastapi-y-por-qué-utilizarlo)
    - [Los dos pilares: Starlette y Pydantic](#los-dos-pilares-starlette-y-pydantic)
    - [Documentación interactiva automática (OpenAPI, Swagger y ReDoc)](#documentación-interactiva-automática-openapi-swagger-y-redoc)
    - [Estructura base de una aplicación](#estructura-base-de-una-aplicación)
    - [Herramientas de prueba para endpoints](#herramientas-de-prueba-para-endpoints)
  - [2. Parámetros de Ruta (Path Parameters)](#2-parámetros-de-ruta-path-parameters)
    - [Fundamentos: URL, URI y Recursos REST](#fundamentos-url-uri-y-recursos-rest)
    - [Definición y tipado estático de Path Parameters](#definición-y-tipado-estático-de-path-parameters)
    - [Validación automática de tipos y error HTTP 422](#validación-automática-de-tipos-y-error-http-422)
    - [Regla crítica: Orden de evaluación de rutas](#regla-crítica-orden-de-evaluación-de-rutas)
    - [Restricción de valores con Enumeraciones (Enum)](#restricción-de-valores-con-enumeraciones-enum)
    - [Parámetros de ruta que contienen rutas (`:path`)](#parámetros-de-ruta-que-contienen-rutas-path)
  - [3. Parámetros de Consulta (Query Parameters)](#3-parámetros-de-consulta-query-parameters)
    - [Definición y estructura en la URL](#definición-y-estructura-en-la-url)
    - [Parámetros con valores por defecto](#parámetros-con-valores-por-defecto)
    - [Parámetros opcionales y requeridos](#parámetros-opcionales-y-requeridos)
    - [Conversión inteligente de tipos de datos](#conversión-inteligente-de-tipos-de-datos)
    - [Filtrado y paginación con slicing](#filtrado-y-paginación-con-slicing)
    - [Coexistencia de múltiples Path y Query Parameters](#coexistencia-de-múltiples-path-y-query-parameters)
  - [4. Cuerpo de la Petición (Request Body) y Modelado con Pydantic](#4-cuerpo-de-la-petición-request-body-y-modelado-con-pydantic)
    - [El ciclo Request-Response y métodos HTTP con Body](#el-ciclo-request-response-y-métodos-http-con-body)
    - [Definición de esquemas con `pydantic.BaseModel`](#definición-de-esquemas-con-pydanticbasemodel)
    - [Ciclo de procesamiento de una solicitud con Body](#ciclo-de-procesamiento-de-una-solicitud-con-body)
    - [Serialización y exportación con `.model_dump()`](#serialización-y-exportación-con-model_dump)
    - [Desempaquetado de diccionarios para enriquecer datos](#desempaquetado-de-diccionarios-para-enriquecer-datos)
    - [Combinación simultánea de Body, Path y Query](#combinación-simultánea-de-body-path-y-query)
  - [5. Validaciones Avanzadas y Metadatos Declarativos](#5-validaciones-avanzadas-y-metadatos-declarativos)
    - [Uso estándar de `typing.Annotated`](#uso-estándar-de-typingannotated)
    - [Validación de cadenas con `Query`](#validación-de-cadenas-con-query)
    - [Validación numérica en `Path` y `Query`](#validación-numérica-en-path-y-query)
    - [Metadatos para OpenAPI (title, description, deprecated)](#metadatos-para-openapi-title-description-deprecated)
    - [Validación de modelos con `pydantic.Field` y tipos `Literal`](#validación-de-modelos-con-pydanticfield-y-tipos-literal)
    - [Modelos para agrupar parámetros Query complejos](#modelos-para-agrupar-parámetros-query-complejos)
    - [Ventajas arquitectónicas de validar en la entrada](#ventajas-arquitectónicas-de-validar-en-la-entrada)
  - [6. Modelos de Respuesta (Response Model) y Filtrado de Datos](#6-modelos-de-respuesta-response-model-y-filtrado-de-datos)
    - [El contrato de salida y seguridad de datos](#el-contrato-de-salida-y-seguridad-de-datos)
    - [Tipo de retorno vs. parámetro `response_model`](#tipo-de-retorno-vs-parámetro-response_model)
    - [Análisis de los 4 casos de respuesta](#análisis-de-los-4-casos-de-respuesta)
      - [Caso 0: Sin tipo ni `response_model` (Sin control)](#caso-0-sin-tipo-ni-response_model-sin-control)
      - [Caso 1: Con tipo de retorno estándar (Camino feliz)](#caso-1-con-tipo-de-retorno-estándar-camino-feliz)
      - [Caso 2: Con tipo de retorno con datos incompletos (Fallo interno)](#caso-2-con-tipo-de-retorno-con-datos-incompletos-fallo-interno)
      - [Caso 3: Con `response_model` como filtro de seguridad](#caso-3-con-response_model-como-filtro-de-seguridad)
    - [Segregación de modelos con herencia (UserBase, UserCreate, UserPublic)](#segregación-de-modelos-con-herencia-userbase-usercreate-userpublic)
    - [Respuestas que retornan listas de modelos](#respuestas-que-retornan-listas-de-modelos)
  - [7. Códigos de Estado HTTP (Status Codes)](#7-códigos-de-estado-http-status-codes)
    - [Semántica y familias de códigos HTTP](#semántica-y-familias-de-códigos-http)
    - [Declaración de `status_code` en operaciones de ruta](#declaración-de-status_code-en-operaciones-de-ruta)
    - [Uso de constantes con `fastapi.status`](#uso-de-constantes-con-fastapistatus)
  - [8. Manejo de Errores y Excepciones](#8-manejo-de-errores-y-excepciones)
    - [Interrupción de flujo con `HTTPException`](#interrupción-de-flujo-con-httpexception)
    - [Estructura estándar del error JSON](#estructura-estándar-del-error-json)
    - [Inyección de encabezados (Headers) personalizados](#inyección-de-encabezados-headers-personalizados)
    - [Errores de cliente (4xx) vs. errores de servidor (5xx)](#errores-de-cliente-4xx-vs-errores-de-servidor-5xx)
    - [Manejadores de excepciones globales (`@app.exception_handler`)](#manejadores-de-excepciones-globales-appexception_handler)
      - [Captura global de excepciones HTTP y de validación](#captura-global-de-excepciones-http-y-de-validación)
  - [9. Catálogo de Errores Frecuentes y Buenas Prácticas](#9-catálogo-de-errores-frecuentes-y-buenas-prácticas)

---

## 1. Fundamentos y Arquitectura de FastAPI

### ¿Qué es FastAPI y por qué utilizarlo?

FastAPI es un framework web moderno y de alto rendimiento para Python, diseñado para construir APIs RESTful de forma rápida, robusta y con documentación automática interactiva bajo los estándares abiertos OpenAPI y JSON Schema.

Principales ventajas competitivas:
- **Alto rendimiento**: Velocidad comparable a NodeJS y Go gracias a su arquitectura ASGI.
- **Validación automática**: Verificación exhaustiva de tipos en tiempo de ejecución para cada solicitud entrante.
- **Tipado estático intensivo**: Aprovecha los type hints de Python 3.10+ para brindar autocompletado en IDEs y detección temprana de errores.
- **Documentación automática**: Generación sin esfuerzo manual de interfaces Swagger UI y ReDoc.
- **Menos código repetitivo**: Reduce drásticamente el código defensivo y de parseo manual.

### Los dos pilares: Starlette y Pydantic

La arquitectura interna de FastAPI delega responsabilidades críticas a dos librerías especializadas:

```
+-------------------------------------------------------------+
|                           FastAPI                           |
|      (Enrutamiento, Inyección de Dependencias, OpenAPI)     |
+------------------------------+------------------------------+
|          Starlette           |           Pydantic           |
|  - Servidor ASGI             |  - Validación de esquemas    |
|  - Peticiones HTTP           |  - Serialización a JSON      |
|  - WebSockets                |  - Coerción de tipos         |
|  - Background Tasks          |  - Generación JSON Schema    |
+------------------------------+------------------------------+
```

1. **Starlette (Motor Asíncrono)**:
   - Manejo del protocolo ASGI (*Asynchronous Server Gateway Interface*).
   - Enrutamiento de bajo nivel y ciclo de vida de peticiones HTTP.
   - Soporte nativo para WebSockets y streaming.
   - Ejecución de tareas en segundo plano (*Background Tasks*).
   - Eventos y gestores de contexto de ciclo de vida (*Lifespan events*).

2. **Pydantic (Validación y Modelado de Datos)**:
   - Define la estructura y restricciones de los datos utilizando clases estándar de Python.
   - Valida entradas y genera mensajes de error detallados si el formato es inválido.
   - Convierte automáticamente los datos crudos a los tipos de datos nativos correspondientes.
   - Serializa objetos complejos a estructuras compatibles con JSON.

### Documentación interactiva automática (OpenAPI, Swagger y ReDoc)

Al iniciar una aplicación FastAPI, el framework analiza todas las operaciones de ruta y genera de inmediato:
- **Swagger UI** (`/docs`): Interfaz interactiva para explorar endpoints, visualizar parámetros, esquemas esperados y ejecutar solicitudes de prueba en vivo.
- **ReDoc** (`/redoc`): Documentación visual alternativa, altamente legible, organizada jerárquicamente por recursos.
- **Esquema OpenAPI** (`/openapi.json`): Especificación formal completa en formato JSON que describe la totalidad de la API.

### Estructura base de una aplicación

Un archivo mínimo de FastAPI (`main.py`) consta de:

```python
from fastapi import FastAPI

# Instancia central de la aplicación
app = FastAPI(
    title="Mi API de Ejemplo",
    description="Demostración de estructura básica en FastAPI",
    version="1.0.0"
)

# Decorador de operación de ruta HTTP GET
@app.get("/")
async def root():
    # FastAPI serializa automáticamente diccionarios y modelos a JSON
    return {"message": "Hello World"}

@app.get("/ping")
async def ping():
    return {"status": "ok", "timestamp": "2026-09-09"}
```

Ejecución del servidor ASGI en desarrollo:
```bash
uvicorn main:app --reload
```
- `main`: Nombre del archivo Python (`main.py`).
- `app`: Variable que contiene la instancia de `FastAPI()`.
- `--reload`: Reinicia el servidor automáticamente ante cambios en el código.

### Herramientas de prueba para endpoints

1. **Swagger UI**: Disponible en el navegador en `http://127.0.0.1:8000/docs`.
2. **Archivos `.http` (REST Client en VS Code)**:
   Permiten versionar y ejecutar solicitudes HTTP directamente desde el editor:
   ```http
   ### Probar endpoint raíz
   GET http://127.0.0.1:8000/

   ### Probar endpoint de ping
   GET http://127.0.0.1:8000/ping
   ```
3. **cURL**:
   ```bash
   curl -X GET "http://127.0.0.1:8000/ping" -H "accept: application/json"
   ```

---

## 2. Parámetros de Ruta (Path Parameters)

### Fundamentos: URL, URI y Recursos REST

Una URL identifica la ubicación exacta de un recurso en la red. En la arquitectura REST:
- Un **recurso** es cualquier entidad o concepto de negocio expuesto por la API (un usuario, un ítem, un reporte).
- La **representación** es el formato en el que se transfiere el estado de ese recurso (típicamente JSON).
- Los **parámetros de ruta** forman parte de la estructura jerárquica de la URL y se emplean para **identificar unívocamente un recurso específico**.

Estructura de una URL:
```
https://api.tienda.com:8000/items/42?categoria=libros#detalle
\___/   \____________/ \__/ \______/ \_______________/ \_____/
Protocolo    Host      Puerto  Path        Query       Fragmento
```

### Definición y tipado estático de Path Parameters

Los parámetros de ruta se declaran encerrándolos entre llaves `{}` dentro del path del decorador y se reciben como argumentos con anotación de tipo en la función:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

FastAPI realiza automáticamente:
1. **Extracción**: Obtiene el segmento de la URL correspondiente a `{item_id}`.
2. **Conversión de tipo**: El segmento viaja como string (`"42"`), pero FastAPI lo convierte a un entero nativo de Python (`42`).
3. **Paso de argumentos**: Ejecuta la función pasando el valor ya convertido.

### Validación automática de tipos y error HTTP 422

Si un cliente envía un valor que no puede ser convertido al tipo especificado:

```http
GET http://127.0.0.1:8000/items/guitarra
```

FastAPI intercepta la petición antes de ingresar a la función y responde automáticamente con un código **422 Unprocessable Entity**:

```json
{
  "detail": [
    {
      "type": "int_parsing",
      "loc": ["path", "item_id"],
      "msg": "Input should be a valid integer, unable to parse string as an integer",
      "input": "guitarra"
    }
  ]
}
```

Estructura del detalle de error:
- `loc`: Ubicación exacta del fallo (`path`, `query`, `body`).
- `msg`: Descripción clara de la discrepancia.
- `type`: Identificador formal del tipo de error de validación.

### Regla crítica: Orden de evaluación de rutas

FastAPI evalúa las rutas registradas en orden secuencial estricto, de arriba hacia abajo.

```python
# CORRECTO: La ruta estática precede a la ruta parametrizada
@app.get("/users/me")
async def read_user_me():
    return {"user_id": "usuario_actual"}

@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}
```

Si el orden se invierte:
```python
# INCORRECTO: La ruta dinámica absorbe todas las peticiones
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}

@app.get("/users/me")
async def read_user_me():
    # Este endpoint nunca se ejecutará
    return {"user_id": "usuario_actual"}
```
En el caso incorrecto, una petición a `/users/me` coincidirá con `{user_id}` asignándole a la variable el valor `"me"`.

### Restricción de valores con Enumeraciones (Enum)

Cuando un parámetro de ruta solo puede aceptar un conjunto finito de opciones válidas, se utiliza una clase `Enum` estándar de Python que herede de `str` y `Enum`. Heredar de `str` permite que la documentación OpenAPI interprete los valores como cadenas de texto.

```python
from enum import Enum
from fastapi import FastAPI

class ModelName(str, Enum):
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"

app = FastAPI()

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    # Comparación directa con el miembro de la enumeración
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning clásico"}

    # Acceso a su valor en string mediante .value
    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "Reconocimiento de imágenes"}

    return {"model_name": model_name, "message": "Arquitectura residual"}
```

Ventajas:
- **Validación estricta**: Si el cliente envía un valor fuera de la lista, recibe automáticamente un error 422.
- **Swagger interactivo**: La interfaz `/docs` genera un menú desplegable con las opciones permitidas.
- **Seguridad en código**: Evita errores de tipeo al comparar constantes.

### Parámetros de ruta que contienen rutas (`:path`)

Para capturar una ruta completa como parámetro (incluyendo barras inclinadas `/`), se utiliza el convertidor `:path`:

```python
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
```
Una petición a `/files/home/user/documento.txt` asignará `"home/user/documento.txt"` a `file_path`.

---

## 3. Parámetros de Consulta (Query Parameters)

### Definición y estructura en la URL

Los parámetros de consulta son pares clave-valor que se agregan al final de la URL a partir del delimitador `?`, separados entre sí por `&`:
```
http://127.0.0.1:8000/items/?skip=0&limit=10
```

En FastAPI, **cualquier parámetro de la función que no esté declarado en la ruta del endpoint es interpretado automáticamente como un Query Parameter**.

### Parámetros con valores por defecto

Al asignar un valor por defecto en la firma de la función, el parámetro se vuelve opcional para el cliente:

```python
from fastapi import FastAPI

app = FastAPI()

fake_items_db = [{"item_name": f"Item {i}"} for i in range(1, 21)]

@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    # Slicing de la lista según los parámetros de paginación
    return fake_items_db[skip : skip + limit]
```

Comportamiento:
- `GET /items/` -> Aplica `skip=0` y `limit=10`.
- `GET /items/?skip=5&limit=2` -> Devuelve los ítems en el rango del índice 5 al 7.

### Parámetros opcionales y requeridos

1. **Parámetro opcional** (usando sintaxis de unión de tipos en Python 3.10+):
   ```python
   @app.get("/items/{item_id}")
   async def read_item(item_id: str, q: str | None = None):
       if q:
           return {"item_id": item_id, "q": q}
       return {"item_id": item_id}
   ```

2. **Parámetro requerido** (sin valor por defecto):
   ```python
   @app.get("/items/{item_id}")
   async def read_item(item_id: str, needy: str):
       # 'needy' es obligatorio en la query string
       return {"item_id": item_id, "needy": needy}
   ```
   Si se invoca `GET /items/foo` sin `?needy=algo`, FastAPI retornará error 422.

### Conversión inteligente de tipos de datos

FastAPI convierte automáticamente los tipos primitivos declarados en los Query Parameters:
- Números: `int`, `float`.
- Booleanos (`bool`): Interpreta de manera flexible múltiples representaciones textuales.

```python
@app.get("/items/{item_id}")
async def read_item(item_id: str, short: bool = False):
    item = {"item_id": item_id}
    if not short:
        item.update({"description": "Esta es una descripción extendida del ítem."})
    return item
```

Valores interpretados como `True`: `1`, `true`, `True`, `on`, `yes`.
Valores interpretados como `False`: `0`, `false`, `False`, `off`, `no`.

### Filtrado y paginación con slicing

Los Query Parameters son el estándar REST para operaciones de búsqueda, ordenamiento y paginación:

```python
@app.get("/products/")
async def get_products(skip: int = 0, limit: int = 5, categoria: str | None = None):
    # Lógica de filtrado
    resultado = productos_db
    if categoria:
        resultado = [p for p in resultado if p["categoria"] == categoria]
    return resultado[skip : skip + limit]
```

### Coexistencia de múltiples Path y Query Parameters

FastAPI diferencia de forma natural el origen de cada parámetro basándose en su nombre y en si aparece o no en la plantilla de ruta:

```python
@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,          # Path Parameter (definido en la URL)
    item_id: str,          # Path Parameter (definido en la URL)
    q: str | None = None,  # Query Parameter (opcional)
    short: bool = False    # Query Parameter (con valor por defecto)
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item["q"] = q
    if not short:
        item["description"] = "Detalle completo del ítem del usuario"
    return item
```

---

## 4. Cuerpo de la Petición (Request Body) y Modelado con Pydantic

### El ciclo Request-Response y métodos HTTP con Body

El protocolo HTTP sigue un ciclo donde:
1. El cliente envía un mensaje de petición (*Request*).
2. El servidor procesa la información y valida las entradas.
3. El servidor devuelve un mensaje de respuesta (*Response*).

Uso del Request Body por método HTTP:
- `GET`: Obtiene datos. No debe transportar cuerpo según el estándar HTTP.
- `POST`: Crea recursos en el servidor. Utiliza Request Body.
- `PUT`: Reemplaza completamente un recurso existente. Utiliza Request Body.
- `PATCH`: Modifica parcialmente un recurso existente. Utiliza Request Body.
- `DELETE`: Elimina un recurso. Típicamente no requiere cuerpo.

### Definición de esquemas con `pydantic.BaseModel`

Para recibir un Request Body, se define un modelo de datos que herede de `pydantic.BaseModel`:

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
```

FastAPI infiere que un parámetro de tipo `BaseModel` debe ser leído desde el cuerpo de la petición en formato JSON.

### Ciclo de procesamiento de una solicitud con Body

```
[Cliente HTTP] 
      |  (Envía JSON)
      v
[Uvicorn (Servidor ASGI)]
      |
      v
[FastAPI (Enrutamiento)]
      |
      v
[Pydantic (Validación)]  ---> ¿JSON Inválido o tipos incorrectos? ---> Responde 422
      | (JSON Válido)
      v
[Función del Endpoint] (Recibe instancia de Item fuertemente tipada)
      |
      v
[Serialización de Respuesta] ---> Responde JSON con status 200
```

Ejemplo de endpoint `POST`:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### Serialización y exportación con `.model_dump()`

En Pydantic v2, el método estándar para convertir una instancia de modelo a un diccionario nativo de Python es `.model_dump()` (reemplaza al método `.dict()` de Pydantic v1).

```python
item = Item(name="Cafetera", price=120.0)

# Convierte el modelo a un diccionario de Python
data = item.model_dump()
# {'name': 'Cafetera', 'description': None, 'price': 120.0, 'tax': None}

# Opción para excluir campos no seteados explícitamente en la petición
data_sin_defaults = item.model_dump(exclude_unset=True)
# {'name': 'Cafetera', 'price': 120.0}
```

### Desempaquetado de diccionarios para enriquecer datos

El operador de desempaquetado `**` permite combinar datos existentes del modelo con nuevos cálculos o metadatos antes de responder:

```python
@app.post("/items/")
async def create_item(item: Item):
    item_dict = item.model_dump()
    if item.tax is not None:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict
```

### Combinación simultánea de Body, Path y Query

FastAPI identifica el origen de cada parámetro sin ambigüedades siguiendo estas tres reglas:
1. Si el parámetro está en la URL -> **Path Parameter**.
2. Si el parámetro es un tipo primitivo (`int`, `str`, `float`, `bool`) -> **Query Parameter**.
3. Si el parámetro es un modelo de `BaseModel` -> **Request Body**.

```python
@app.put("/items/{item_id}")
async def update_item(
    item_id: int,          # Path Parameter
    item: Item,            # Request Body
    q: str | None = None   # Query Parameter
):
    result = {"item_id": item_id, **item.model_dump()}
    if q:
        result.update({"q": q})
    return result
```

---

## 5. Validaciones Avanzadas y Metadatos Declarativos

### Uso estándar de `typing.Annotated`

En Python moderno y FastAPI, se recomienda el uso de `Annotated` (`from typing import Annotated`) para asociar metadatos y reglas de validación al tipo de dato, manteniendo limpio el tipo base:

```python
# Patrón moderno recomendado:
parametro: Annotated[Tipo, ReglaDeValidacion()] = ValorPorDefecto
```

### Validación de cadenas con `Query`

La clase `Query` permite restringir longitud, patrones mediante expresiones regulares y definir metadatos:

```python
from typing import Annotated
from fastapi import FastAPI, Query

app = FastAPI()

@app.get("/items/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            min_length=3,
            max_length=50,
            pattern="^[a-zA-Z0-9_-]+$",
            title="Término de Búsqueda",
            description="Cadena de texto alfanumérica para filtrar elementos"
        )
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results
```

### Validación numérica en `Path` y `Query`

Para validar parámetros numéricos se utilizan los operadores relacionales:
- `gt`: Mayor que (*greater than*).
- `ge`: Mayor o igual que (*greater than or equal*).
- `lt`: Menor que (*less than*).
- `le`: Menor o igual que (*less than or equal*).

```python
from typing import Annotated
from fastapi import FastAPI, Path, Query

app = FastAPI()

@app.get("/items/{item_id}")
async def read_items(
    item_id: Annotated[int, Path(title="ID del Ítem", ge=1, le=1000)],
    q: Annotated[str | None, Query(alias="item-query")] = None,
    size: Annotated[float, Query(gt=0, lt=10.5)] = 1.0
):
    results = {"item_id": item_id, "size": size}
    if q:
        results.update({"q": q})
    return results
```

### Metadatos para OpenAPI (title, description, deprecated)

FastAPI transfiere los metadatos declarados directamente al esquema OpenAPI y a la interfaz Swagger UI:
- `title`: Título legible para la documentación del campo.
- `description`: Explicación del propósito del parámetro.
- `deprecated=True`: Marca el parámetro visualmente como obsoleto en Swagger UI sin romper compatibilidad.
- `examples`: Lista de ejemplos para facilitar las pruebas en la documentación.

### Validación de modelos con `pydantic.Field` y tipos `Literal`

Dentro de los modelos Pydantic, la función `Field` provee las mismas capacidades de validación que `Query` y `Path`:

```python
from typing import Literal
from pydantic import BaseModel, Field

class FilterParams(BaseModel):
    limit: int = Field(default=10, gt=0, le=100, description="Cantidad máxima de registros")
    offset: int = Field(default=0, ge=0, description="Desplazamiento inicial")
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = Field(default_factory=list)
```

El tipo `Literal` restringe el valor estrictamente a las cadenas especificadas.

### Modelos para agrupar parámetros Query complejos

Para evitar funciones con docenas de argumentos en la firma, se pueden agrupar múltiples Query Parameters en un modelo Pydantic utilizando `Annotated[Modelo, Query()]`:

```python
from typing import Annotated, Literal
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI()

class FilterParams(BaseModel):
    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: Literal["created_at", "updated_at"] = "created_at"
    tags: list[str] = []

@app.get("/items/")
async def read_items(filter_query: Annotated[FilterParams, Query()]):
    return filter_query
```
FastAPI extraerá cada campo del modelo `FilterParams` directamente desde la query string de la URL (`/items/?limit=50&offset=10&order_by=created_at`).

### Ventajas arquitectónicas de validar en la entrada

1. **Principio "Fail Fast"**: Cualquier dato malformado es rechazado en la frontera del sistema antes de alcanzar la lógica de negocio o la base de datos.
2. **Eliminación de código defensivo**: No se requieren bloques repetitivos de `if not isinstance(...)` o `if len(...) < 3` dentro de los servicios.
3. **Consistencia de errores**: Todos los errores de validación presentan la misma estructura JSON estandarizada con código 422.
4. **Documentación viva**: La documentación interactiva refleja automáticamente todas las restricciones definidas en el código.

---

## 6. Modelos de Respuesta (Response Model) y Filtrado de Datos

### El contrato de salida y seguridad de datos

Así como se valida la entrada, una API robusta debe gobernar estrictamente su salida para:
- **Evitar fuga de datos sensibles**: Ocultar campos internos como contraseñas, hashes de seguridad, o banderas administrativas.
- **Garantizar el contrato de la API**: Asegurar que la respuesta cumpla con la estructura prometida al cliente.
- **Filtrar datos sobrantes**: Limpiar atributos extra provenientes de bases de datos antes de responder.

### Tipo de retorno vs. parámetro `response_model`

FastAPI ofrece dos mecanismos complementarios:

1. **Tipo de retorno en la firma (`-> Modelo`)**:
   - Brinda autocompletado y tipado estático en el editor (mypy, Pylance).
   - Genera la documentación OpenAPI de salida.
   - Valida que la función devuelva los campos requeridos.

2. **Parámetro `response_model` en el decorador (`@app.get("/", response_model=Modelo)`)**:
   - Actúa como un **filtro activo de serialización**: elimina automáticamente cualquier campo del diccionario u objeto devuelto que no esté explícitamente declarado en `response_model`.
   - Convierte automáticamente los datos al modelo especificado.

### Análisis de los 4 casos de respuesta

A continuación se analizan los comportamientos posibles según la configuración de salida:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
```

#### Caso 0: Sin tipo ni `response_model` (Sin control)
```python
@app.get("/items/caso0")
async def get_caso0():
    # PELIGRO: Se exponen campos internos no deseados
    return {"name": "Laptop", "price": 999.0, "password_db": "secret123"}
```
Resultado: El cliente recibe `password_db`. No hay filtrado ni validación de salida.

#### Caso 1: Con tipo de retorno estándar (Camino feliz)
```python
@app.get("/items/caso1")
async def get_caso1() -> Item:
    return Item(name="Laptop", price=999.0)
```
Resultado: Salida validada, tipado estricto en IDE y documentación correcta en OpenAPI.

#### Caso 2: Con tipo de retorno con datos incompletos (Fallo interno)
```python
@app.get("/items/caso2")
async def get_caso2() -> Item:
    # Falta el campo requerido 'price'
    return {"name": "Laptop"}  # type: ignore
```
Resultado: FastAPI detecta que la respuesta no cumple con el contrato y lanza un error interno `500 Internal Server Error (ResponseValidationError)`, protegiendo al cliente de recibir datos rotos.

#### Caso 3: Con `response_model` como filtro de seguridad
```python
@app.get("/items/caso3", response_model=Item)
async def get_caso3():
    # Se devuelve un diccionario con campos extra
    return {"name": "Laptop", "price": 999.0, "password_db": "secret123"}
```
Resultado: FastAPI toma el diccionario, lo filtra contra el esquema `Item` y devuelve únicamente `{"name": "Laptop", "price": 999.0}`. El campo `password_db` es descartado de forma segura.

### Segregación de modelos con herencia (UserBase, UserCreate, UserPublic)

El patrón recomendado para gestionar la asimetría entre lo que un usuario envía y lo que debe recibir se basa en herencia de clases:

```python
from fastapi import FastAPI, status
from pydantic import BaseModel, EmailStr

app = FastAPI()

# 1. Base común con atributos compartidos (Principio DRY)
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None

# 2. Modelo de entrada para creación (recibe la contraseña en texto plano)
class UserCreate(UserBase):
    password: str

# 3. Modelo de salida público (no expone la contraseña)
class UserPublic(UserBase):
    pass

# 4. Modelo interno de base de datos (con hash)
class UserInDB(UserBase):
    hashed_password: str

@app.post("/users/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate) -> UserPublic:
    # Simulación de persistencia:
    # fake_hashed_password = hash_func(user.password)
    # user_db = UserInDB(**user.model_dump(), hashed_password=fake_hashed_password)
    
    # Se retorna un objeto con la estructura de UserPublic
    return UserPublic(**user.model_dump())
```

### Respuestas que retornan listas de modelos

Para endpoints que devuelven colecciones de datos, se especifica `response_model=list[Modelo]`:

```python
items_db = [
    {"name": "Mesa", "price": 150.0, "cost": 80.0},
    {"name": "Silla", "price": 45.0, "cost": 20.0}
]

@app.get("/items/", response_model=list[Item])
async def read_all_items():
    # Cada elemento de la lista será filtrado por el esquema Item (omitiendo 'cost')
    return items_db
```

---

## 7. Códigos de Estado HTTP (Status Codes)

### Semántica y familias de códigos HTTP

Los códigos de estado HTTP indican el resultado de la solicitud del cliente mediante enteros de 3 dígitos agrupados en 5 clases:

| Rango | Clase | Significado | Ejemplos Comunes |
| :--- | :--- | :--- | :--- |
| **1xx** | Informativo | Solicitud recibida, continuando proceso | `100 Continue` |
| **2xx** | Éxito | Acción solicitada recibida, entendida y aceptada | `200 OK`, `201 Created`, `204 No Content` |
| **3xx** | Redirección | Se deben tomar acciones adicionales | `301 Moved Permanently`, `304 Not Modified` |
| **4xx** | Error del Cliente | La solicitud contiene sintaxis errónea o no puede cumplirse | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found`, `422 Unprocessable Entity` |
| **5xx** | Error del Servidor | El servidor falló al intentar procesar una solicitud válida | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable` |

### Declaración de `status_code` en operaciones de ruta

Por defecto, FastAPI devuelve `200 OK` en todas las operaciones exitosas. Para operaciones de creación o acciones sin contenido, se debe declarar explícitamente el código adecuado en el decorador:

```python
from fastapi import FastAPI, status

app = FastAPI()

# Creación de recursos: 201 Created
@app.post("/items/", status_code=status.HTTP_201_CREATED)
async def create_item(name: str):
    return {"name": name}

# Eliminación sin cuerpo de retorno: 204 No Content
@app.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(item_id: int):
    # Lógica de eliminación
    return None
```

### Uso de constantes con `fastapi.status`

Es una buena práctica estricta utilizar las constantes provistas por `fastapi.status` en lugar de literales numéricos (*números mágicos*):
- Previene errores de tipeo accidentales (ej. `status_code=2010`).
- Mejora la legibilidad del código.
- Se integra automáticamente en el esquema OpenAPI.

```python
from fastapi import status

# Uso recomendado:
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_204_NO_CONTENT
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
status.HTTP_422_UNPROCESSABLE_ENTITY
status.HTTP_500_INTERNAL_SERVER_ERROR
```

---

## 8. Manejo de Errores y Excepciones

### Interrupción de flujo con `HTTPException`

Para retornar errores controlados al cliente (recurso no encontrado, credenciales inválidas, reglas de negocio infringidas), se debe lanzar una excepción `HTTPException` mediante la sentencia `raise`.

```python
from fastapi import FastAPI, HTTPException, status

app = FastAPI()

items_db = {"foo": "The Foo Wrestlers"}

@app.get("/items/{item_id}")
async def read_item(item_id: str):
    if item_id not in items_db:
        # raise interrumpe la ejecución de inmediato
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ítem no encontrado en el sistema"
        )
    return {"item": items_db[item_id]}
```

Reglas críticas de `HTTPException`:
- **Siempre usar `raise`**: Nunca se debe devolver con `return`. Al lanzar `raise`, Python detiene la ejecución del endpoint de forma inmediata.
- **Formato de `detail`**: Puede recibir una cadena de texto, una lista o un diccionario con información estructurada.

### Estructura estándar del error JSON

Cuando se lanza `HTTPException`, FastAPI intercepta la excepción y produce automáticamente una respuesta JSON consistente:

```json
{
  "detail": "Ítem no encontrado en el sistema"
}
```

Si `detail` es un diccionario:
```python
raise HTTPException(
    status_code=400,
    detail={"error_code": "INVALID_CURRENCY", "message": "Moneda no soportada"}
)
```
La respuesta será:
```json
{
  "detail": {
    "error_code": "INVALID_CURRENCY",
    "message": "Moneda no soportada"
  }
}
```

### Inyección de encabezados (Headers) personalizados

Ciertos flujos de autenticación o especificaciones HTTP requieren adjuntar encabezados en las respuestas de error. `HTTPException` acepta un parámetro opcional `headers`:

```python
@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
            headers={"X-Error-Reason": "ResourceDoesNotExist", "X-Trace-ID": "abc-123"}
        )
    return {"item": items_db[item_id]}
```

### Errores de cliente (4xx) vs. errores de servidor (5xx)

- **Errores 4xx (Responsabilidad del Cliente)**:
  - El cliente envió parámetros incorrectos, datos malformados o no tiene permisos.
  - Se deben gestionar y lanzar deliberadamente con `raise HTTPException(status_code=4xx, detail=...)`.
  - El servidor sigue funcionando correctamente.

- **Errores 5xx (Responsabilidad del Servidor)**:
  - Ocurren ante bugs no capturados en el código, desconexión de bases de datos o fallos de infraestructura.
  - FastAPI los captura a nivel global y responde con `500 Internal Server Error` para no filtrar trazas internas (*stack traces*) al cliente en producción.

### Manejadores de excepciones globales (`@app.exception_handler`)

FastAPI permite registrar manejadores globales para capturar excepciones personalizadas de la aplicación o sobreescribir los errores por defecto del framework:

```python
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# 1. Excepción de dominio personalizada
class RecursoNoDisponibleException(Exception):
    def __init__(self, nombre: str):
        self.nombre = nombre

app = FastAPI()

# 2. Registro del manejador global
@app.exception_handler(RecursoNoDisponibleException)
async def recurso_no_disponible_handler(request: Request, exc: RecursoNoDisponibleException):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"error": "Recurso Inexistente", "detalle": f"El recurso '{exc.nombre}' no está disponible."}
    )

@app.get("/recursos/{nombre}")
async def obtener_recurso(nombre: str):
    if nombre == "prohibido":
        raise RecursoNoDisponibleException(nombre=nombre)
    return {"recurso": nombre}
```

#### Captura global de excepciones HTTP y de validación
Para sobreescribir el comportamiento por defecto de las excepciones HTTP de FastAPI/Starlette o de validación de Pydantic:
```python
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"custom_error": True, "message": exc.detail}
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"mensaje": "Error en la validación de entrada", "errores": exc.errors()}
    )
```
*Nota arquitectónica: Conviene capturar `StarletteHTTPException` en lugar de `HTTPException` de FastAPI para asegurar que también se capturen los errores generados internamente por el enrutador de Starlette (como rutas inexistentes 404 o métodos no permitidos 405).*

---

## 9. Catálogo de Errores Frecuentes y Buenas Prácticas

| Error Común | Causa o Riesgo | Solución Correcta |
| :--- | :--- | :--- |
| **Invertir el orden de rutas fijas y dinámicas** | Definir `@app.get("/items/{id}")` antes de `@app.get("/items/me")`. La ruta dinámica captura todo y la fija nunca se ejecuta. | Declarar siempre primero las rutas específicas y fijas, seguidas por las rutas dinámicas parametrizadas. |
| **Usar `return` en vez de `raise` en `HTTPException`** | `return HTTPException(...)` no interrumpe el flujo y responde un código 200 con la excepción serializada como cuerpo. | Lanzar siempre las excepciones utilizando la palabra clave `raise HTTPException(...)`. |
| **Depender siempre del status 200 por defecto** | Responder `200 OK` tras crear recursos o procesar eliminaciones sin cuerpo. | Declarar explícitamente `status_code=status.HTTP_201_CREATED` o `status.HTTP_204_NO_CONTENT` en el decorador. |
| **Usar números mágicos en status codes** | Escribir `status_code=201` o `status_code=404` propenso a errores tipográficos. | Utilizar las constantes oficiales importadas desde `fastapi.status` (ej. `status.HTTP_201_CREATED`). |
| **Fuga de datos sensibles en respuestas** | Devolver diccionarios u objetos de BD completos que contienen campos como contraseñas, tokens o hashes. | Implementar el patrón de segregación de esquemas (`UserCreate` vs `UserPublic`) y aplicar `response_model=UserPublic`. |
| **Usar `.dict()` en lugar de `.model_dump()`** | `.dict()` es un método deprecado de Pydantic v1 que genera advertencias o errores en versiones modernas. | Utilizar siempre `.model_dump()` o `.model_dump_json()` de Pydantic v2. |
| **Olvidar valores por defecto en Query Parameters opcionales** | Declarar `q: str | None` sin asignar `= None`, convirtiendo el parámetro involuntariamente en requerido. | Asignar siempre el valor por defecto: `q: str | None = None`. |
| **No registrar excepciones HTTP sobre Starlette** | Crear un handler para `fastapi.HTTPException` no intercepta excepciones de bajo nivel generadas por Starlette. | Registrar los manejadores globales sobre `starlette.exceptions.HTTPException`. |
| **Repetir campos en esquemas de Pydantic** | Redefinir `username`, `email`, etc., en múltiples modelos independientes violando el principio DRY. | Diseñar una jerarquía de clases con un modelo base común (`UserBase`) y especializar mediante herencia. |
