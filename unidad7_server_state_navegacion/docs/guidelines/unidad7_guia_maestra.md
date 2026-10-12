# Guía Maestra: Optimización de Endpoints en Backend (FastAPI / SQLModel), Server State (TanStack Query) y Enrutamiento Profesional (React Router + TypeScript)

---

## Introducción y Fundamentos de Arquitectura Full Stack

El desarrollo de aplicaciones Full Stack modernas y escalables se fundamenta en el desacoplamiento estricto entre dos subsistemas con responsabilidades bien delimitadas:

1. **El Backend como Proveedor de Datos REST Escalable (FastAPI + SQLModel):** Encargado de resguardar la integridad referencial, validar contratos de entrada en la frontera HTTP, filtrar y paginar grandes volúmenes de registros directamente en el motor relacional y exponer respuestas estandarizadas con metadatos de navegación.
2. **El Frontend como Single Page Application Reactiva (React + TypeScript + TanStack Query + React Router):** Encargado de presentar vistas dinámicas sin recargas de documento, sincronizar el estado remoto (*Server State*) mediante políticas declarativas de caché e invalidación automática, y reflejar el estado de navegación en la URL con tipado estático de extremo a extremo.

### Los Tres Problemas Arquitectónicos que Resuelve la Unidad 7

```
+-----------------------------------------------------------------------------------+
|                        ARQUITECTURA FULL STACK UNIDAD 7                           |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ FRONTEND: SPA React + TypeScript ]                                             |
|  ┌─────────────────────────────────────────────────────────────────────────────┐  |
|  │ 1. React Router (BrowserRouter / Routes / Route / useNavigate / useParams)  │  |
|  │    -> Transición de vistas sin recarga HTML; URL como contrato de estado.   │  |
|  ├─────────────────────────────────────────────────────────────────────────────┤  |
|  │ 2. TanStack Query (useQuery / useMutation / QueryClient.invalidateQueries)  │  |
|  │    -> Caché en memoria, deduplicación, estados de carga/error y refetch     │  |
|  │       automático tras mutaciones sin manipular arrays locales manualmente.  │  |
|  ├─────────────────────────────────────────────────────────────────────────────┤  |
|  │ 3. React Local State (useState)                                             │  |
|  │    -> Exclusivo para Client State: apertura de modales, inputs de forms,    │  |
|  │       filtros de búsqueda y página actual.                                  │  |
|  └──────────────────────────────────────┬──────────────────────────────────────┘  |
|                                         │ HTTP / JSON (CORS Habilitado)           |
|                                         ▼                                         |
|  [ BACKEND: FastAPI + SQLModel ]                                                  |
|  ┌─────────────────────────────────────────────────────────────────────────────┐  |
|  │ 1. Router Layer (Validación declarativa con Query: ge, le, status_code)     │  |
|  │    -> Intercepta parámetros inválidos con HTTP 422 antes del servicio.      │  |
|  ├─────────────────────────────────────────────────────────────────────────────┤  |
|  │ 2. Service Layer (Filtros dinámicos + Subquery COUNT + OFFSET/LIMIT)        │  |
|  │    -> Ejecuta exactamente dos consultas SQL acotadas (total + página).      │  |
|  ├─────────────────────────────────────────────────────────────────────────────┤  |
|  │ 3. Schema Layer (DTOs: Create, Read, Update y PaginatedResponse)            │  |
|  │    -> Contrato estandarizado: { "total": int, "items": List[ReadSchema] }   │  |
|  └─────────────────────────────────────────────────────────────────────────────┘  |
+-----------------------------------------------------------------------------------+
```

1. **Sobrecarga de Base de Datos y Ausencia de Metadatos en APIs Tradicionales:** Un endpoint que ejecuta `SELECT * FROM tabla` sin cotas degrada linealmente ($O(N)$) en memoria RAM, ancho de banda y tiempo de serialización, además de privar al cliente de saber cuántos registros existen en total para construir controles de paginación.
2. **Complejidad, Duplicación y Desincronización del Server State con `useEffect` + `useState`:** Gestionar peticiones HTTP manualmente obliga a repetir banderas (`loading`, `error`, `data`) en cada componente, carece de caché entre montajes, dispara solicitudes duplicadas y deja la interfaz desactualizada tras operaciones `POST`, `PATCH` o `DELETE`.
3. **Navegación Rígida y Monolitos en `App.tsx`:** Concentrar llamadas a APIs y vistas condicionales dentro de `App.tsx` impide compartir enlaces profundos (*deep links* como `/productos/42`), rompe el historial del navegador y acopla el layout global con la lógica de negocio de cada pantalla.

Esta guía desarrolla de forma exhaustiva la teoría, el diseño arquitectónico y la implementación práctica de referencia para dominar estos cuatro ejes tanto en el trabajo práctico de la unidad (**Food Store**: `Categoria`, `Producto`, `ProductoCategoria`) como en cualquier sistema empresarial en producción.

---

# Parte 1: Backend — Optimización de Endpoints con FastAPI y SQLModel

---

## 1. Problemas de un Endpoint de Listado Básico

En las etapas iniciales de un proyecto es habitual encontrar endpoints de listado ingenuos como el siguiente:

```python
# ❌ ANTIPATRÓN: Endpoint ingenuo sin cotas ni metadatos
@router.get("/weapons", response_model=List[WeaponRead])
def list_weapons_naive(session: Session = Depends(get_session)):
    return session.exec(select(Weapon)).all()
```

Aunque funcional con decenas de filas en entorno local, este diseño colapsa en producción por tres motivos estructurales:

### 1.1. Degradación de Rendimiento y Complejidad $O(N)$ en Memoria
Cuando una tabla acumula decenas de miles o millones de filas, invocar `.all()` sin restricciones obliga a:
* Transferir la totalidad de las tuplas desde el motor relacional a través del socket de red.
* Instanciar $N$ objetos Python en memoria RAM del proceso worker de Uvicorn/Gunicorn.
* Serializar $N$ diccionarios Pydantic a una cadena JSON masiva, bloqueando el bucle de eventos y saturando el ancho de banda del cliente.

### 1.2. Respuestas Planas sin Metadatos para el Frontend
Si el servidor responde únicamente con un arreglo JSON plano:

```json
[
  { "id": 1, "name": "Excalibur", "description": "Espada legendaria" },
  { "id": 2, "name": "Mjolnir", "description": "Martillo de trueno" }
]
```

El frontend carece de información crítica para renderizar una interfaz de navegación completa:
* **Desconoce el universo total de datos (`total`):** No puede mostrar *"Mostrando 1–10 de 1.250 resultados"*.
* **No puede calcular el número total de páginas:** Resulta imposible determinar si el botón *"Siguiente"* debe deshabilitarse o cuántos botones numéricos de página deben dibujarse.

### 1.3. Vulnerabilidad ante Parámetros Descontrolados (DoS Involuntario)
Incluso si se agregan parámetros `limit` y `offset` sin validación declarativa, un cliente malintencionado o un bug en el frontend puede emitir peticiones destructivas:
* `GET /weapons?limit=1000000` $\rightarrow$ Fuerza un volcado completo de base de datos que agota la memoria del contenedor (*Out Of Memory*).
* `GET /weapons?offset=-200` $\rightarrow$ Provoca una excepción de motor SQL (`OFFSET must not be negative`) que deriva en un `500 Internal Server Error` no controlado.

---

## 2. Paginación de Resultados (`offset` y `limit`)

La paginación divide un conjunto potencialmente infinito de registros en subconjuntos acotados denominados **páginas**.

### 2.1. Semántica Relacional de `LIMIT` y `OFFSET`
En SQL estándar y SQLModel, el recorte de ventana se gobierna mediante dos cláusulas:

| Parámetro | Cláusula SQL | Significado Técnico | Fórmula Habitual desde `page` (base 1) |
| :--- | :--- | :--- | :--- |
| **`limit`** | `LIMIT <n>` | Cantidad máxima de filas que el motor devolverá en la respuesta actual (tamaño de página). | `limit = pageSize` (ej. `10`) |
| **`offset`** | `OFFSET <m>` | Cantidad de filas iniciales que el motor debe descartar antes de comenzar a recolectar las filas del `limit`. | `offset = (page - 1) * limit` |

Por ejemplo, para visualizar la **página 3** mostrando **10 elementos por página**:
$$\text{offset} = (3 - 1) \times 10 = 20, \quad \text{limit} = 10$$

```sql
SELECT id, name, description
FROM weapon
LIMIT 10 OFFSET 20;
```
El motor salta los primeros 20 registros (páginas 1 y 2) y retorna exclusivamente los registros 21 al 30.

### 2.2. La Doble Consulta en SQLModel: Conteo Atómico vs. Recorte de Página

Para entregar tanto los ítems de la página actual como el total general de registros que cumplen los criterios de búsqueda, la capa de servicio debe ejecutar **dos consultas SQL complementarias**:

1. **Consulta de Conteo (`COUNT(*)` en Motor SQL):** Calcula el número exacto de coincidencias mediante `select(func.count()).select_from(query.subquery())`.
2. **Consulta de Datos Paginada (`OFFSET` + `LIMIT`):** Recupera únicamente las entidades correspondientes al segmento solicitado mediante `query.offset(offset).limit(limit)`.

> **Regla de Oro de Rendimiento:** Jamás calcules el total haciendo `total = len(session.exec(query).all())`. Hacerlo trae todas las filas de la base de datos a la memoria de Python solo para contarlas en la aplicación, anulando por completo el beneficio de la paginación. El conteo siempre debe delegarse al motor SQL mediante `func.count()`.

```python
from sqlmodel import Session, select, func
from app.modules.weapon.models import Weapon

# 1. Consulta base (con sus filtros ya aplicados)
query = select(Weapon)

# 2. Conteo atómico en el motor de base de datos (devuelve un único entero)
count_query = select(func.count()).select_from(query.subquery())
total: int = session.exec(count_query).one()

# 3. Extracción exclusiva de la ventana de datos solicitada
items = session.exec(query.offset(offset).limit(limit)).all()
```

---

## 3. Filtros Dinámicos

En aplicaciones reales, los usuarios necesitan refinar listados según múltiples criterios opcionales (búsqueda por texto parcial en el nombre, filtrado por clave foránea, disponibilidad, rango de precios). Crear un endpoint distinto por cada combinación (`GET /weapons/by-name`, `GET /weapons/by-hero`) es un antipatrón que multiplica rutas redundantes.

### 3.1. Construcción Incremental del Objeto Query
SQLModel y SQLAlchemy implementan el patrón **Query Builder Inmutable**: una sentencia `select(Model)` es un objeto estructurado al que se le pueden encadenar cláusulas `.where(...)` de forma condicional antes de ser ejecutado por la sesión.

```python
from typing import Optional, Tuple, List
from sqlmodel import Session, select, func
from app.modules.weapon.models import Weapon

def get_weapons(
    session: Session,
    offset: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
) -> Tuple[int, List[Weapon]]:
    # Paso 1: Consulta base sin restricciones
    query = select(Weapon)

    # Paso 2: Aplicación condicional de filtros dinámicos
    if name:
        # .ilike() ejecuta búsqueda insensible a mayúsculas/minúsculas (ILIKE '%texto%')
        query = query.where(Weapon.name.ilike(f"%{name}%"))

    # Paso 3: El conteo se calcula SOBRE la consulta ya filtrada
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Paso 4: La paginación se aplica SOBRE la misma consulta filtrada
    results = session.exec(query.offset(offset).limit(limit)).all()

    return total, list(results)
```

### 3.2. Simetría Obligatoria entre Conteo y Datos
Observa el orden de las operaciones en el código anterior:
1. Primero se construye `query` y se le añaden **todos** los `.where(...)` condicionales.
2. Luego se deriva `count_query` a partir de `query.subquery()`.
3. Finalmente se aplica `.offset(offset).limit(limit)` a `query`.

Si calculáramos `count_query` **antes** de aplicar el filtro `if name:`, el backend devolvería el total de toda la tabla (ej. `total: 500`) pero solo 3 ítems filtrados por `"espada"`, provocando que el frontend renderice 50 páginas vacías.

---

## 4. Validación Declarativa de Parámetros con `Query`

FastAPI permite declarar reglas de validación numérica y de cadenas directamente en la firma del endpoint utilizando `fastapi.Query`.

```python
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

@router.get("/", response_model=WeaponPaginatedResponse)
def list_weapons(
    offset: int = Query(0, ge=0, description="Registros a omitir (no negativo)"),
    limit: int = Query(10, ge=1, le=100, description="Tamaño máximo de página (1 a 100)"),
    name: Optional[str] = Query(None, min_length=1, max_length=100, description="Filtro parcial por nombre"),
    session: Session = Depends(get_session),
):
    total, items = service.get_weapons(
        session=session,
        offset=offset,
        limit=limit,
        name=name,
    )
    return {"total": total, "items": items}
```

### 4.1. Operadores de Restricción en `Query`

| Restricción | Significado Matemático | Caso de Uso Típico |
| :--- | :--- | :--- |
| **`ge=0`** | *Greater than or equal* ($\ge 0$) | Impedir valores negativos en `offset` o filtros de precio mínimo. |
| **`gt=0`** | *Greater than* ($> 0$) | Garantizar identificadores positivos o límites mayores a cero. |
| **`le=100`** | *Less than or equal* ($\le 100$) | Establecer un techo infranqueable al `limit` para proteger la base de datos. |
| **`lt=value`** | *Less than* ($< \text{valor}$) | Cotas superiores abiertas. |
| **`min_length` / `max_length`** | Longitud de `str` | Prevenir búsquedas vacías `""` o payloads gigantes en query strings. |

### 4.2. Intercepción Automática con `422 Unprocessable Entity`
Cuando un cliente envía `GET /weapons?limit=500` o `GET /weapons?offset=-5`:
1. FastAPI intercepta la petición en la capa de validación **antes** de abrir una sesión de base de datos o invocar a `service.get_weapons()`.
2. Responde inmediatamente con el código de estado estándar **`422 Unprocessable Entity`** y un cuerpo JSON detallado indicando qué parámetro violó qué restricción.
3. El servicio permanece limpio, enfocado 100% en la lógica de negocio sin bloques `if limit < 1 or limit > 100: raise HTTPException(...)`.

---

## 5. Respuestas Estandarizadas y Modelo Paginado

Para que el contrato entre el backend y cualquier cliente (React, aplicación móvil o consumidor externo) sea predecible, los endpoints de colección deben envolver sus resultados en un **DTO de Respuesta Paginada**.

### 5.1. Definición del Schema `PaginatedResponse`
En `schemas.py`, definimos un modelo contenedor que hereda de `SQLModel`:

```python
from typing import List, Generic, TypeVar
from sqlmodel import SQLModel

# Variante específica por módulo (estándar en proyectos SQLModel)
class WeaponPaginatedResponse(SQLModel):
    total: int
    items: List[WeaponRead]

# Variante genérica reutilizable para múltiples módulos
T = TypeVar("T")

class PaginatedResponse(SQLModel, Generic[T]):
    total: int
    items: List[T]
```

### 5.2. Estructura JSON y Fórmulas de Navegación en el Cliente
Al declarar `response_model=WeaponPaginatedResponse`, FastAPI valida y serializa la salida con la siguiente forma canónica:

```json
{
  "total": 47,
  "items": [
    { "id": 1, "name": "Espada Larga", "description": "Acero forjado" },
    { "id": 2, "name": "Arco Compuesto", "description": "Largo alcance" }
  ]
}
```

Con `total`, `limit` y `offset` (o `page`), el frontend calcula de forma determinista todo el estado de la barra de paginación:
* **Total de páginas:** $\text{totalPages} = \lceil \text{total} / \text{limit} \rceil =$ `Math.ceil(total / limit)`
* **Página actual (base 1):** $\text{currentPage} = \lfloor \text{offset} / \text{limit} \rfloor + 1 =$ `Math.floor(offset / limit) + 1`
* **Existe página siguiente (`hasNextPage`):** `offset + limit < total`
* **Existe página anterior (`hasPrevPage`):** `offset > 0`

---

## 6. Arquitectura Modular Backend y Configuración de CORS

### 6.1. Responsabilidad de Cada Capa (`models` $\rightarrow$ `schemas` $\rightarrow$ `service` $\rightarrow$ `router`)

| Archivo | Responsabilidad Única | Qué NO debe contener |
| :--- | :--- | :--- |
| **`models.py`** | Definición de tablas físicas (`table=True`), claves primarias (`primary_key=True`), claves foráneas (`foreign_key`) y relaciones ORM (`Relationship`). | Reglas de validación de query params ni lógica HTTP. |
| **`schemas.py`** | Contratos de entrada/salida (DTOs sin `table=True`): `Base`, `Create`, `Read`, `Update` y `PaginatedResponse`. | Consultas a la base de datos o sesiones. |
| **`service.py`** | Lógica de negocio pura y acceso a datos mediante `Session`: construcción de queries dinámicas, `func.count()`, `offset()`, `limit()`, `commit()` y `refresh()`. | Objetos `HTTPException`, `Query` o detalles del protocolo HTTP. |
| **`router.py`** | Exposición de rutas HTTP (`APIRouter`), validación declarativa (`Query`, `Depends`), traducción de `None`/`False` del servicio a `HTTPException(404/409)` y retorno del schema. | Consultas SQL directas (`select(...)`, `session.add(...)`). |

### 6.2. Configuración Mandatoria de CORS en `app/main.py`
Cuando el frontend en React (ejecutándose por defecto en `http://localhost:5173` con Vite) realiza una petición `fetch` hacia el backend FastAPI (`http://localhost:8000`), el navegador aplica la política de seguridad **Same-Origin Policy** y bloquea la lectura de la respuesta a menos que el servidor emita las cabeceras **CORS** (*Cross-Origin Resource Sharing*) correspondientes.

Además, en peticiones `POST`, `PUT`, `PATCH` o `DELETE` con cabecera `Content-Type: application/json`, el navegador dispara previamente una petición automática **`OPTIONS` (Preflight Request)** para verificar permisos.

```python
# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from app.core.database import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield

app = FastAPI(title="Food Store API", version="1.0.0", lifespan=lifespan)

# Configuración obligatoria de CORS para permitir la comunicación con el Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],   # Permite GET, POST, PUT, PATCH, DELETE, OPTIONS
    allow_headers=["*"],   # Permite Content-Type, Authorization, etc.
)
```

---

# Parte 2: Frontend — Server State y Mutaciones con TanStack Query

---

## 1. El Paradigma del Estado en el Frontend: Client State vs. Server State

Uno de los mayores saltos de calidad en la ingeniería de software frontend consiste en separar el estado local de la interfaz (**Client State**) del estado remoto que pertenece al backend (**Server State**).

### 1.1. Por Qué `useEffect` + `fetch` + `useState` No Escala
En React tradicional, cada componente que necesita datos del servidor suele implementar este patrón manual:

```tsx
// ❌ ANTIPATRÓN TRADICIONAL: Manejo manual repetitivo y frágil
const [products, setProducts] = useState<Product[]>([]);
const [isLoading, setIsLoading] = useState<boolean>(true);
const [isError, setIsError] = useState<boolean>(false);

useEffect(() => {
  setIsLoading(true);
  fetch("http://localhost:8000/productos")
    .then((res) => {
      if (!res.ok) throw new Error("Error HTTP");
      return res.json();
    })
    .then((data) => setProducts(data.items))
    .catch(() => setIsError(true))
    .finally(() => setIsLoading(false));
}, []);
```

Este enfoque presenta **cuatro deficiencias graves** a medida que la aplicación crece:
1. **Boilerplate repetitivo:** Cada vista debe declarar y coordinar manualmente tres estados (`data`, `isLoading`, `isError`) más un `AbortController` para evitar condiciones de carrera.
2. **Ausencia total de caché entre vistas:** Cuando el usuario navega de `/productos` a `/categorias` y regresa a `/productos`, el componente se desmonta y vuelve a montar, disparando una nueva petición HTTP y mostrando una pantalla de carga innecesaria.
3. **Peticiones duplicadas concurrentes:** Si el `Navbar`, un `Sidebar` y la página principal necesitan la lista de categorías al mismo tiempo, se emiten 3 llamadas HTTP idénticas en paralelo.
4. **Desincronización tras mutaciones:** Al crear, editar o eliminar un registro, el desarrollador debe recordar actualizar manualmente el array local con `.filter()` o `.map()`, o forzar un recargado manual propenso a errores.

### 1.2. Matriz Comparativa: Client State vs. Server State

| Dimensión | Client State (Estado del Cliente) | Server State (Estado del Servidor) |
| :--- | :--- | :--- |
| **Definición** | Estado efímero, síncrono y exclusivo de la interfaz de usuario en el navegador. | Datos persistentes almacenados en bases de datos remotas y expuestos vía APIs REST/GraphQL. |
| **Ubicación y Propiedad** | Reside 100% en la memoria de la pestaña actual; el componente o la app tienen control absoluto. | Reside en el servidor; el frontend solo posee una **instantánea en caché** que puede quedar obsoleta. |
| **Latencia y Naturaleza** | Síncrono e instantáneo (cero latencia de red, no puede fallar por red). | Asíncrono; sujeto a latencia, fallos de red, códigos HTTP 4xx/5xx y modificaciones de otros usuarios. |
| **Ejemplos en un Proyecto** | Modal abierto/cerrado (`isModalOpen`), valores de inputs de un formulario, pestaña activa, texto del buscador, página actual (`page`). | Listado de categorías, catálogo paginado de productos, detalle de un producto específico, perfil del usuario autenticado. |
| **Herramienta Ideal** | `useState`, `useReducer`, Context API, Zustand. | **TanStack Query (React Query)**, SWR, RTK Query. |

### 1.3. El Antipatrón de Oro: Copiar Server State dentro de `useState`
> **Regla Inquebrantable:** Jamás copies los datos devueltos por `useQuery` dentro de un `useState` local (`useEffect(() => setLocalItems(data), [data])`) para mostrar una lista o tabla.

Si copias `data` a un `useState`, rompes la reactividad de TanStack Query: cuando una mutación invalide la caché y traiga datos frescos en segundo plano, el componente seguirá renderizando la copia vieja atrapada en el `useState` local. La única excepción válida para copiar datos remotos a un `useState` es **pre-llenar los campos de un formulario de edición** cuando el usuario abre un modal para editar un ítem específico.

---

## 2. Configuración del Entorno TanStack Query

### 2.1. Instalación
En proyectos React con TypeScript gestionados con `pnpm` (o `npm`):

```bash
pnpm add @tanstack/react-query
```

### 2.2. Instanciación de `QueryClient` y `QueryClientProvider` en `main.tsx`
El `QueryClient` es el motor central que administra el almacén de caché en memoria, los temporizadores de recolección de basura y las suscripciones de todos los componentes. Debe instanciarse **fuera** del árbol de renderizado (a nivel de módulo en `main.tsx`) y proveerse mediante `<QueryClientProvider>`:

```tsx
// src/main.tsx
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import App from "./App.tsx";
import "./index.css";

// 1. Instancia global del cliente de caché con políticas por defecto
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutos de datos considerados "frescos"
      gcTime: 1000 * 60 * 10,   // 10 minutos antes de purgar entradas inactivas de RAM
      retry: 1,                 // Reintentar 1 vez automática ante fallos de red
      refetchOnWindowFocus: false, // Opcional: evita refetch cada vez que se cambia de ventana
    },
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    {/* 2. Proveedor de TanStack Query envolviendo toda la aplicación */}
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>
);
```

---

## 3. Lectura Declarativa de Datos con `useQuery`

El hook `useQuery` gestiona el ciclo de vida completo de una operación de **lectura (`GET`)**.

### 3.1. Anatomía de `useQuery`: `queryKey` y `queryFn`

```tsx
const {
  data,
  isLoading,
  isPending,
  isError,
  error,
  isFetching,
  refetch,
} = useQuery<Categoria[]>({
  queryKey: ["categorias"],
  queryFn: getCategorias,
});
```

#### 1. `queryKey` (Identificador Único y Jerárquico de Caché)
Es un **arreglo serializable** que actúa como la clave primaria de la entrada en el almacén de caché de TanStack Query:
* **Claves simples (Colecciones completas):** `["categorias"]`
* **Claves jerárquicas por entidad e ID:** `["producto", id]` (ej. `["producto", 42]`)
* **Claves parametrizadas (Paginación y Filtros):** `["productos", { offset, limit, search }]`

> **Principio Reactivo de las `queryKey`:** Siempre que una `queryFn` dependa de una variable (como `id`, `page`, `limit` o `search`), **esa variable debe formar parte del arreglo `queryKey`**. Cuando el usuario cambia de página o escribe en el buscador, el cambio en el `queryKey` hace que TanStack Query dispare automáticamente el fetch para esa nueva combinación y guarde cada página en su propia ranura de caché.

#### 2. `queryFn` (Función Asíncrona de Obtención de Datos)
Es cualquier función que devuelva una **Promesa (`Promise<T>`)** que resuelva con los datos o sea rechazada con un `Error`.

> **Regla Crítica con `fetch` Nativo:** La API `fetch` del navegador **NO rechaza la promesa** cuando el servidor responde con errores HTTP como `404 Not Found`, `422 Unprocessable Entity` o `500 Internal Server Error`; solo rechaza ante cortes físicos de red. Por lo tanto, es **obligatorio** verificar `if (!res.ok) throw new Error(...)` dentro de la capa de servicio. Si olvidas lanzar el error, `useQuery` creerá que la petición fue exitosa (`isSuccess: true`) y guardará el JSON del error de FastAPI dentro de `data`.

```ts
// src/services/categorias.service.ts
import type { Categoria } from "../types/categoria";

const API_URL = "http://localhost:8000";

export const getCategorias = async (): Promise<Categoria[]> => {
  const res = await fetch(`${API_URL}/categorias/`);

  // Verificación innegociable para activar isError en TanStack Query
  if (!res.ok) {
    throw new Error(`Error ${res.status}: No se pudieron obtener las categorías`);
  }

  return res.json();
};
```

### 3.2. Estados de Retorno de `useQuery`

| Propiedad | Tipo | Significado Técnico y Uso en la Interfaz |
| :--- | :--- | :--- |
| **`data`** | `TData \| undefined` | Datos resueltos por la última ejecución exitosa de `queryFn` (o recuperados instantáneamente de la caché). |
| **`isLoading` / `isPending`** | `boolean` | `true` cuando no existen datos previos en caché y la petición inicial está en vuelo. Se usa para renderizar *skeletons* o el mensaje `"Cargando..."`. |
| **`isError`** | `boolean` | `true` si la `queryFn` lanzó una excepción tras agotar los reintentos configurados. |
| **`error`** | `Error \| null` | Objeto de error capturado (`error.message`), útil para mostrar alertas detalladas al usuario. |
| **`isFetching`** | `boolean` | `true` siempre que haya una petición HTTP en vuelo, **incluyendo** actualizaciones silenciosas en segundo plano cuando `data` ya está en pantalla. |
| **`refetch`** | `() => Promise` | Función para forzar manualmente una recarga (ej. en un botón *"Reintentar"* dentro de la vista de error). |

### 3.3. Ciclo de Vida de la Caché: `staleTime` vs. `gcTime` (`cacheTime`)

Comprender la diferencia entre estos dos temporizadores es fundamental para dominar TanStack Query:

```
[ Petición Exitosa ]
         │
         ▼
┌─────────────────────────────────────────┐
│ ESTADO: FRESH (Fresco)                  │ ◄── Dura mientras transcurre `staleTime` (ej. 5 min).
│ - Si otro componente pide la misma      │     Por defecto en TanStack Query: staleTime = 0 ms.
│   queryKey, se lee de RAM SIN hacer     │
│   ningún fetch de red.                  │
└───────────────────┬─────────────────────┘
                    │ (Expira staleTime o se llama a invalidateQueries)
                    ▼
┌─────────────────────────────────────────┐
│ ESTADO: STALE (Viejo / Desactualizado)  │
│ - El dato SIGUE en caché y se muestra   │
│   al instante al montar el componente,  │
│   pero TanStack Query lanza un refetch  │
│   silencioso en segundo plano.          │
└───────────────────┬─────────────────────┘
                    │ (Se desmontan todos los componentes que usan esta queryKey)
                    ▼
┌─────────────────────────────────────────┐
│ ESTADO: INACTIVE (Inactivo en RAM)      │ ◄── Corre el reloj de `gcTime` / `cacheTime` (por defecto 5 min).
│ - Si el usuario vuelve a la vista antes │     Si nadie usa la query antes de que expire `gcTime`,
│   de que termine gcTime, ve el dato al  │     el Garbage Collector la elimina de la memoria RAM.
│   instante.                             │
└─────────────────────────────────────────┘
```

| Parámetro | Nombre en v4 / Videos | Nombre en v5 | Propósito |
| :--- | :--- | :--- | :--- |
| **`staleTime`** | `staleTime` | `staleTime` | Tiempo durante el cual un dato en caché se considera **fresco y válido**. Mientras está fresco, montar el componente lee de caché sin emitir tráfico de red. |
| **`gcTime`** | `cacheTime` | `gcTime` | Tiempo que una entrada **inactiva** (sin ningún componente montado leyéndola) permanece almacenada en memoria antes de ser eliminada por el recolector de basura. |

---

## 4. Modificación de Datos en el Servidor con `useMutation`

Mientras que `useQuery` es **declarativo y automático** (se ejecuta al montar el componente para peticiones `GET`), el hook `useMutation` es **imperativo y bajo demanda**: está diseñado para operaciones que alteran el estado del servidor (**`POST`**, **`PUT`**, **`PATCH`**, **`DELETE`**) y solo se dispara cuando el usuario realiza una acción explícita (enviar un formulario, confirmar una eliminación).

### 4.1. Estructura Completa de `useMutation`

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createCategoria } from "../services/categorias.service";
import type { CategoriaCreate } from "../types/categoria";

const queryClient = useQueryClient();

const createMutation = useMutation({
  // 1. Función asíncrona que recibe el payload (variables) y ejecuta el POST/PATCH/DELETE
  mutationFn: (nuevaCategoria: CategoriaCreate) => createCategoria(nuevaCategoria),

  // 2. Callback ejecutado únicamente si el servidor responde con éxito (200/201/204)
  onSuccess: (dataCreada) => {
    // Paso crítico: Invalidar la caché para refrescar la lista automáticamente
    queryClient.invalidateQueries({ queryKey: ["categorias"] });
    // Limpiar el formulario y cerrar el modal local
    setNombre("");
    setDescripcion("");
    setIsModalOpen(false);
  },

  // 3. Callback ejecutado si mutationFn lanza un Error
  onError: (error: Error) => {
    console.error("Fallo al crear la categoría:", error.message);
  },
});
```

### 4.2. Ejecución de la Mutación en Eventos de UI
Para disparar la operación desde un manejador `onSubmit` o `onClick`, se invoca `createMutation.mutate(payload)`:

```tsx
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
  e.preventDefault();
  createMutation.mutate({
    nombre: nombre.trim(),
    descripcion: descripcion.trim(),
  });
};
```

### 4.3. Estados Reactivos de una Mutación (`isPending`, `isSuccess`, `isError`)
`useMutation` expone banderas booleanas para brindar retroalimentación visual inmediata y evitar envíos duplicados (doble clic en el botón *"Guardar"*):

| Estado | Significado | Aplicación Práctica en Componentes React |
| :--- | :--- | :--- |
| **`isPending`** | La petición HTTP (`POST`/`PATCH`/`DELETE`) está en curso esperando respuesta del backend. | Deshabilitar el botón de envío (`disabled={mutation.isPending}`) y cambiar su texto a `"Guardando..."` o mostrar un spinner. |
| **`isSuccess`** | El servidor procesó el cambio y devolvió un código `2xx`. | Mostrar un banner verde de confirmación o cerrar automáticamente el modal de edición. |
| **`isError`** | La petición falló (validación `422`, conflicto `409` o caída de red). | Mostrar un mensaje de alerta rojo con `mutation.error.message` dentro del modal sin perder los datos que el usuario había escrito. |

---

## 5. Invalidación de Queries y el Flujo de Sincronización en 5 Pasos

### 5.1. El Problema de la Caché Obsoleta tras Mutar
Supongamos que el componente `CategoriasPage` cargó la lista de categorías mediante `useQuery({ queryKey: ["categorias"], ... })`. Luego, el usuario abre el modal y crea una nueva categoría `"Bebidas"` mediante `useMutation`.
* El backend inserta `"Bebidas"` en la base de datos y responde `201 Created`.
* Sin embargo, **la lista en pantalla no muestra `"Bebidas"`** si no le avisamos a TanStack Query que su caché `"categorias"` quedó desactualizada.

### 5.2. El Flujo Canónico de 5 Pasos con `queryClient.invalidateQueries`
La solución estándar en TanStack Query nunca consiste en hacer `setCategorias([...categorias, nueva])` a mano, sino en **invalidar la clave de caché** dentro del callback `onSuccess`:

```
┌──────────────────────────────────────────────────────────────────────────────┐
│           FLUJO DE SINCRONIZACIÓN AUTOMÁTICA EN 5 PASOS                      │
└──────────────────────────────────────────────────────────────────────────────┘

  1. Acción del Usuario      El usuario envía el formulario o pulsa "Eliminar"
            │                y dispara `mutation.mutate(payload)`.
            ▼
  2. Ejecución HTTP          Se ejecuta `mutationFn` enviando `POST`, `PATCH`
            │                o `DELETE` hacia la API FastAPI.
            ▼
  3. Confirmación Backend    El backend persiste el cambio en SQLModel y
            │                responde `200 OK`, `201 Created` o `204 No Content`.
            ▼
  4. Invalidación de Caché   Se dispara `onSuccess` y ejecuta:
            │                `queryClient.invalidateQueries({ queryKey: ["categorias"] })`
            │                marcando la caché como obsoleta (STALE).
            ▼
  5. Refetch y Re-render     TanStack Query detecta que `["categorias"]` está
                             montada en pantalla, vuelve a ejecutar `getCategorias()`
                             en segundo plano y actualiza la tabla automáticamente.
```

> **Compatibilidad de Sintaxis (v4 vs. v5):**
> * En **TanStack Query v5** (actual LTS), `invalidateQueries` recibe un objeto:
>   `queryClient.invalidateQueries({ queryKey: ["categorias"] })`
> * En versiones anteriores (v4 / algunos ejemplos de diapositivas), se pasaba el arreglo directamente: `queryClient.invalidateQueries(["categorias"])`. Utiliza siempre la sintaxis de objeto `{ queryKey: [...] }` en proyectos actuales con `@tanstack/react-query` v5.

---

# Parte 3: Frontend — Enrutamiento Profesional con React Router y TypeScript

---

## 1. Fundamentos de Single Page Application (SPA) y Enrutamiento Cliente

En la arquitectura web multipágina clásica (MPA), hacer clic en un enlace provoca que el navegador descargue un documento HTML completamente nuevo desde el servidor, destruyendo todo el estado en memoria de JavaScript.

Por el contrario, una **Single Page Application (SPA)** construida con React descarga un único `index.html` inicial. A partir de ese instante, **React Router** intercepta los cambios de URL utilizando la **History API** nativa del navegador (`window.history.pushState`) y decide dinámicamente qué componente de página montar o desmontar en el árbol virtual.

### Sinergia Arquitectónica entre React Router y TanStack Query
Dado que cambiar de ruta en React Router **no recarga la pestaña del navegador**, la instancia de `QueryClient` en memoria permanece intacta durante toda la sesión del usuario:
* Cuando el usuario navega de `/categorias` a `/productos` y luego vuelve a `/categorias`, TanStack Query entrega las categorías desde la memoria RAM en **0 milisegundos**, logrando transiciones instantáneas.

---

## 2. Arquitectura de `BrowserRouter`, `Routes`, `Route` y Desacoplamiento de `App.tsx`

### 2.1. La Regla de Responsabilidad Única en `App.tsx`
> **Principio Arquitectónico Clave:** `App.tsx` **jamás** debe contener lógica de negocio, llamadas `fetch`, estados de formularios ni hooks `useQuery`/`useMutation`. Su única responsabilidad es renderizar la estructura de navegación global (como el `<Navbar />`) y declarar el mapa de rutas (`<Routes>` y `<Route>`).

```tsx
// src/App.tsx
import { Routes, Route, Navigate } from "react-router-dom";
import { Navbar } from "./components/Navbar";
import { CategoriasPage } from "./pages/CategoriasPage";
import { ProductsPage } from "./pages/ProductsPage";
import { ProductDetailPage } from "./pages/ProductDetailPage";

export function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* Layout persistente: visible en todas las pantallas */}
      <Navbar />

      {/* Contenedor dinámico de vistas según la URL actual */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<Navigate to="/categorias" replace />} />
          <Route path="/categorias" element={<CategoriasPage />} />
          <Route path="/productos" element={<ProductsPage />} />
          <Route path="/productos/:id" element={<ProductDetailPage />} />
          <Route
            path="*"
            element={
              <div className="text-center py-16">
                <h2 className="text-2xl font-bold text-slate-700">404 — Página no encontrada</h2>
              </div>
            }
          />
        </Routes>
      </main>
    </div>
  );
}

export default App;
```

### 2.2. Los Tres Componentes Estructurales de `react-router-dom`

| Componente | Ubicación Típica | Función Principal |
| :--- | :--- | :--- |
| **`<BrowserRouter>`** | `src/main.tsx` | Conecta la aplicación con la History API del navegador y provee el contexto de enrutamiento a todos los componentes hijos (`Link`, `NavLink`, `useNavigate`, `useParams`). |
| **`<Routes>`** | `src/App.tsx` | Evalúa todas sus etiquetas `<Route>` hijas frente a la URL actual y renderiza exclusivamente aquella cuyo `path` tenga la coincidencia más específica. |
| **`<Route>`** | Dentro de `<Routes>` | Asocia un patrón de URL (`path="/productos"`) con el elemento JSX que debe montarse (`element={<ProductsPage />}`). |

---

## 3. Rutas Estáticas vs. Rutas Dinámicas

### 3.1. Rutas Estáticas
Poseen un segmento de URL fijo e invariable. Siempre montan el mismo componente de vista general:
* `/categorias` $\rightarrow$ `<CategoriasPage />`
* `/productos` $\rightarrow$ `<ProductsPage />`

### 3.2. Rutas Dinámicas con Parámetros de Segmento (`:param`)
Utilizan el prefijo de dos puntos (`:id`, `:slug`, `:categoriaId`) para declarar un comodín variable en la definición de la ruta:

```tsx
<Route path="/productos/:id" element={<ProductDetailPage />} />
```

De este modo, un único componente (`ProductDetailPage`) sirve para infinitas URLs (`/productos/1`, `/productos/10`, `/productos/42`), cambiando únicamente el valor del parámetro capturado.

---

## 4. Navegación Programática (`useNavigate`) y Lectura de Parámetros (`useParams`)

### 4.1. Navegación Declarativa (`Link` / `NavLink`) vs. Programática (`useNavigate`)
* **En barras de navegación o menús (`Navbar.tsx`):** Se utiliza `<Link to="/categorias">` o `<NavLink to="/categorias">` (que permite aplicar estilos activos automáticamente cuando la ruta coincide). **Nunca se utiliza `<a href="...">`**, ya que `<a href>` fuerza una recarga completa del navegador y destruye la SPA.
* **En respuesta a lógica de código, eventos o finalización de mutaciones:** Se utiliza el hook **`useNavigate()`**.

```tsx
import { useNavigate } from "react-router-dom";

export const ProductCard = ({ id, nombre }: { id: number; nombre: string }) => {
  const navigate = useNavigate();

  const handleVerDetalle = () => {
    // Navegación programática construyendo la ruta dinámica con template literals
    navigate(`/productos/${id}`);
  };

  return (
    <div className="p-4 bg-white rounded-xl shadow">
      <h3 className="font-bold">{nombre}</h3>
      <button
        type="button"
        onClick={handleVerDetalle}
        className="mt-2 text-sm text-indigo-600 hover:underline"
      >
        Ver detalle →
      </button>
    </div>
  );
};
```

> **Tip de Navegación Inversa:** Llamar a `navigate(-1)` equivale exactamente a presionar el botón *"Atrás"* del navegador, regresando a la vista previa en la pila del historial.

### 4.2. Extracción Tipada de Parámetros con `useParams` y Sinergia con `useQuery`
En el componente de destino de una ruta dinámica (`/productos/:id`), el hook `useParams` extrae los segmentos variables de la URL.

> **Advertencia de Tipado en TypeScript:** Todos los parámetros extraídos de una URL mediante `useParams()` son **siempre de tipo `string | undefined`** (por ejemplo, `"42"`). Si tu servicio backend espera un `number`, debes convertirlo explícitamente con `Number(id)` y validar con ` !Number.isNaN(numericId)`.

```tsx
// Patrón profesional combinado: useParams + useNavigate + useQuery
import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getProductoById } from "../services/productos.service";

export const ProductDetailPage = () => {
  // 1. Extraemos el parámetro :id desde la URL
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const numericId = Number(id);

  // 2. Ejecutamos useQuery incluyendo numericId en la queryKey
  const { data: producto, isLoading, isError } = useQuery({
    queryKey: ["producto", numericId],
    queryFn: () => getProductoById(numericId),
    // Solo dispara la petición si el ID es un número válido mayor a 0
    enabled: Boolean(id) && !Number.isNaN(numericId) && numericId > 0,
  });

  if (isLoading) return <p className="p-6 text-slate-500">Cargando detalle del producto...</p>;
  if (isError || !producto) return <p className="p-6 text-red-600">Producto no encontrado.</p>;

  return (
    <section className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
      <button
        type="button"
        onClick={() => navigate("/productos")}
        className="text-sm text-indigo-600 hover:underline mb-4 inline-block"
      >
        ← Volver al listado de productos
      </button>
      <h1 className="text-2xl font-bold">{producto.nombre}</h1>
      <p className="text-slate-600 mt-2">{producto.descripcion}</p>
      <p className="text-xl font-semibold text-emerald-600 mt-4">
        ${Number(producto.precio_base).toFixed(2)}
      </p>
    </section>
  );
};
```

---

# Parte 4: Integración Práctica Full Stack — Arquitectura y Código de Referencia (Dominio Food Store)

A continuación se presenta la arquitectura de carpetas y la implementación de referencia de extremo a extremo para el dominio **Food Store** (`Categoria`, `Producto` y la tabla intermedia `ProductoCategoria`), integrando todos los conceptos de la unidad y cumpliendo estrictamente los lineamientos arquitectónicos de producción y del trabajo práctico.

---

## 1. Estructura de Archivos del Proyecto Full Stack

```
proyecto-fullstack-foodstore/
│
├── backend/                                 # API REST con FastAPI + SQLModel
│   ├── requirements.txt
│   └── app/
│       ├── main.py                          # Lifespan, CORSMiddleware e inclusión de routers
│       ├── core/
│       │   └── database.py                  # Engine SQLite/PostgreSQL y dependencia get_session
│       └── modules/
│           ├── categoria/
│           │   ├── models.py                # Tabla Categoria
│           │   ├── schemas.py               # CategoriaCreate, Read, Update, PaginatedResponse
│           │   ├── service.py               # CRUD + búsqueda dinámica + conteo y paginación
│           │   └── router.py                # Endpoints /categorias con validación Query
│           └── producto/
│               ├── models.py                # Tablas Producto y ProductoCategoria (Link N:M)
│               ├── schemas.py               # ProductoCreate, Read, Update, PaginatedResponse, Link
│               ├── service.py               # CRUD Producto + asignación/desvinculación de categorías
│               └── router.py                # Endpoints /productos y /producto-categorias
│
└── frontend/                                # SPA con React + TypeScript + Vite + Tailwind CSS
    ├── package.json
    └── src/
        ├── main.tsx                         # QueryClientProvider + BrowserRouter
        ├── App.tsx                          # Solo Navbar + Routes (sin lógica de negocio)
        ├── types/
        │   ├── categoria.ts                 # Interfaces Categoria, CategoriaCreate, etc.
        │   └── producto.ts                  # Interfaces Producto, PaginatedResponse<T>
        ├── services/
        │   ├── categorias.service.ts        # Funciones fetch tipadas para Categorías
        │   └── productos.service.ts         # Funciones fetch tipadas para Productos
        ├── components/
        │   ├── Navbar.tsx                   # Barra de navegación superior con NavLink
        │   └── CategoriaModal.tsx           # Modal controlado por useState para Alta y Edición
        └── pages/
            ├── CategoriasPage.tsx           # CRUD completo con useQuery + useMutation + invalidateQueries
            └── ProductsPage.tsx             # Catálogo con filtros, paginación y vista de productos
```

---

## 2. Implementación de Referencia del Backend (FastAPI + SQLModel)

### 2.1. Configuración de Base de Datos (`app/core/database.py`)

```python
# backend/app/core/database.py
from typing import Generator
from sqlmodel import Session, create_engine

DATABASE_URL = "sqlite:///./food_store.db"

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
```

### 2.2. Modelos Relacionales: `Categoria`, `Producto` y `ProductoCategoria`

Siguiendo el diseño UML de **Food Store**, `Producto` y `Categoria` mantienen una relación **Muchos a Muchos (N:M)** articulada mediante la tabla intermedia `ProductoCategoria` (`producto_categoria`), la cual posee clave primaria compuesta (`producto_id`, `categoria_id`) y el atributo de metadato `es_principal`.

```python
# backend/app/modules/producto/models.py
from datetime import datetime, timezone
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.categoria.models import Categoria


class ProductoCategoria(SQLModel, table=True):
    """Tabla intermedia N:M entre Producto y Categoria."""
    __tablename__ = "producto_categoria"

    producto_id: int = Field(foreign_key="producto.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categoria.id", primary_key=True)
    es_principal: bool = Field(default=False, nullable=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class Producto(SQLModel, table=True):
    __tablename__ = "producto"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=150, nullable=False, index=True)
    descripcion: Optional[str] = Field(default=None)
    precio_base: float = Field(ge=0, nullable=False)
    disponible: bool = Field(default=True, nullable=False)

    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
    )
```

```python
# backend/app/modules/categoria/models.py
from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel
from app.modules.producto.models import ProductoCategoria

if TYPE_CHECKING:
    from app.modules.producto.models import Producto


class Categoria(SQLModel, table=True):
    __tablename__ = "categoria"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(max_length=100, unique=True, nullable=False, index=True)
    descripcion: str = Field(default="", nullable=False)

    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
    )
```

### 2.3. Schemas DTO y Respuestas Paginadas (`schemas.py`)

```python
# backend/app/modules/categoria/schemas.py
from typing import List, Optional
from sqlmodel import SQLModel


class CategoriaBase(SQLModel):
    nombre: str
    descripcion: str = ""


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaRead(CategoriaBase):
    id: int


class CategoriaUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None


class CategoriaPaginatedResponse(SQLModel):
    total: int
    items: List[CategoriaRead]
```

```python
# backend/app/modules/producto/schemas.py
from typing import List, Optional
from sqlmodel import Field, SQLModel
from app.modules.categoria.schemas import CategoriaRead


class ProductoBase(SQLModel):
    nombre: str
    descripcion: Optional[str] = None
    precio_base: float = Field(ge=0)
    disponible: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoRead(ProductoBase):
    id: int
    categorias: List[CategoriaRead] = []


class ProductoUpdate(SQLModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    precio_base: Optional[float] = Field(default=None, ge=0)
    disponible: Optional[bool] = None


class ProductoPaginatedResponse(SQLModel):
    total: int
    items: List[ProductoRead]


class ProductoCategoriaAssign(SQLModel):
    producto_id: int
    categoria_id: int
    es_principal: bool = False


class ProductoCategoriaRead(SQLModel):
    producto_id: int
    categoria_id: int
    es_principal: bool
```

### 2.4. Capa de Servicio con Paginación y Filtros Dinámicos (`service.py`)

```python
# backend/app/modules/categoria/service.py
from typing import List, Optional, Tuple
from sqlmodel import Session, select, func
from app.modules.categoria.models import Categoria
from app.modules.categoria.schemas import CategoriaCreate, CategoriaUpdate


def create_categoria(session: Session, data: CategoriaCreate) -> Categoria:
    categoria = Categoria.model_validate(data)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def get_categorias(
    session: Session,
    offset: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
) -> Tuple[int, List[Categoria]]:
    # 1. Consulta base
    query = select(Categoria)

    # 2. Filtro dinámico insensible a mayúsculas/minúsculas
    if search:
        query = query.where(Categoria.nombre.ilike(f"%{search}%"))

    # 3. Conteo total sobre la consulta filtrada
    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # 4. Paginación con offset y limit
    items = session.exec(query.offset(offset).limit(limit)).all()
    return total, list(items)


def get_categoria(session: Session, categoria_id: int) -> Optional[Categoria]:
    return session.get(Categoria, categoria_id)


def update_categoria(
    session: Session, categoria_id: int, data: CategoriaUpdate
) -> Optional[Categoria]:
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        return None

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(categoria, key, value)

    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def delete_categoria(session: Session, categoria_id: int) -> bool:
    categoria = session.get(Categoria, categoria_id)
    if not categoria:
        return False

    session.delete(categoria)
    session.commit()
    return True
```

```python
# backend/app/modules/producto/service.py
from typing import List, Optional, Tuple
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select, func
from app.modules.producto.models import Producto, ProductoCategoria
from app.modules.producto.schemas import (
    ProductoCreate,
    ProductoUpdate,
    ProductoCategoriaAssign,
)
from app.modules.categoria.models import Categoria


def create_producto(session: Session, data: ProductoCreate) -> Producto:
    producto = Producto.model_validate(data)
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto


def get_productos(
    session: Session,
    offset: int = 0,
    limit: int = 20,
    nombre: Optional[str] = None,
    disponible: Optional[bool] = None,
) -> Tuple[int, List[Producto]]:
    query = select(Producto)

    if nombre:
        query = query.where(Producto.nombre.ilike(f"%{nombre}%"))
    if disponible is not None:
        query = query.where(Producto.disponible == disponible)

    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()

    # Eager loading de categorías con selectinload para evitar N+1 queries
    paginated_query = (
        query.options(selectinload(Producto.categorias))
        .offset(offset)
        .limit(limit)
    )
    items = session.exec(paginated_query).all()
    return total, list(items)


def get_producto(session: Session, producto_id: int) -> Optional[Producto]:
    statement = (
        select(Producto)
        .where(Producto.id == producto_id)
        .options(selectinload(Producto.categorias))
    )
    return session.exec(statement).first()


def update_producto(
    session: Session, producto_id: int, data: ProductoUpdate
) -> Optional[Producto]:
    producto = session.get(Producto, producto_id)
    if not producto:
        return None

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(producto, key, value)

    session.add(producto)
    session.commit()
    session.refresh(producto)
    return get_producto(session, producto_id)


def delete_producto(session: Session, producto_id: int) -> bool:
    producto = session.get(Producto, producto_id)
    if not producto:
        return False
    session.delete(producto)
    session.commit()
    return True


def assign_categoria_to_producto(
    session: Session, data: ProductoCategoriaAssign
) -> Optional[ProductoCategoria]:
    producto = session.get(Producto, data.producto_id)
    categoria = session.get(Categoria, data.categoria_id)
    if not producto or not categoria:
        return None

    existing = session.get(
        ProductoCategoria, (data.producto_id, data.categoria_id)
    )
    if existing:
        existing.es_principal = data.es_principal
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    link = ProductoCategoria(
        producto_id=data.producto_id,
        categoria_id=data.categoria_id,
        es_principal=data.es_principal,
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return link


def remove_categoria_from_producto(
    session: Session, producto_id: int, categoria_id: int
) -> bool:
    link = session.get(ProductoCategoria, (producto_id, categoria_id))
    if not link:
        return False
    session.delete(link)
    session.commit()
    return True
```

### 2.5. Capa de Routers con Validación Declarativa (`router.py`)

```python
# backend/app/modules/categoria/router.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.modules.categoria import service
from app.modules.categoria.schemas import (
    CategoriaCreate,
    CategoriaPaginatedResponse,
    CategoriaRead,
    CategoriaUpdate,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])


@router.post("/", response_model=CategoriaRead, status_code=201)
def create_categoria(
    data: CategoriaCreate, session: Session = Depends(get_session)
):
    return service.create_categoria(session, data)


@router.get("/", response_model=CategoriaPaginatedResponse)
def list_categorias(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    session: Session = Depends(get_session),
):
    total, items = service.get_categorias(
        session=session, offset=offset, limit=limit, search=search
    )
    return {"total": total, "items": items}


@router.get("/{categoria_id}", response_model=CategoriaRead)
def get_categoria(categoria_id: int, session: Session = Depends(get_session)):
    categoria = service.get_categoria(session, categoria_id)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.patch("/{categoria_id}", response_model=CategoriaRead)
def update_categoria(
    categoria_id: int,
    data: CategoriaUpdate,
    session: Session = Depends(get_session),
):
    categoria = service.update_categoria(session, categoria_id, data)
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    return categoria


@router.delete("/{categoria_id}", status_code=204)
def delete_categoria(categoria_id: int, session: Session = Depends(get_session)):
    if not service.delete_categoria(session, categoria_id):
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
```

```python
# backend/app/modules/producto/router.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session
from app.core.database import get_session
from app.modules.producto import service
from app.modules.producto.schemas import (
    ProductoCategoriaAssign,
    ProductoCategoriaRead,
    ProductoCreate,
    ProductoPaginatedResponse,
    ProductoRead,
    ProductoUpdate,
)

router = APIRouter(prefix="/productos", tags=["Productos"])


@router.post("/", response_model=ProductoRead, status_code=201)
def create_producto(
    data: ProductoCreate, session: Session = Depends(get_session)
):
    return service.create_producto(session, data)


@router.get("/", response_model=ProductoPaginatedResponse)
def list_productos(
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    nombre: Optional[str] = Query(None),
    disponible: Optional[bool] = Query(None),
    session: Session = Depends(get_session),
):
    total, items = service.get_productos(
        session=session,
        offset=offset,
        limit=limit,
        nombre=nombre,
        disponible=disponible,
    )
    return {"total": total, "items": items}


@router.get("/{producto_id}", response_model=ProductoRead)
def get_producto(producto_id: int, session: Session = Depends(get_session)):
    producto = service.get_producto(session, producto_id)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.patch("/{producto_id}", response_model=ProductoRead)
def update_producto(
    producto_id: int,
    data: ProductoUpdate,
    session: Session = Depends(get_session),
):
    producto = service.update_producto(session, producto_id, data)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto


@router.delete("/{producto_id}", status_code=204)
def delete_producto(producto_id: int, session: Session = Depends(get_session)):
    if not service.delete_producto(session, producto_id):
        raise HTTPException(status_code=404, detail="Producto no encontrado")


@router.post(
    "/categorias/asignar",
    response_model=ProductoCategoriaRead,
    status_code=201,
    tags=["Producto-Categoría"],
)
def assign_categoria(
    data: ProductoCategoriaAssign, session: Session = Depends(get_session)
):
    link = service.assign_categoria_to_producto(session, data)
    if not link:
        raise HTTPException(
            status_code=404, detail="Producto o Categoría inexistente"
        )
    return link


@router.delete(
    "/{producto_id}/categorias/{categoria_id}",
    status_code=204,
    tags=["Producto-Categoría"],
)
def unassign_categoria(
    producto_id: int,
    categoria_id: int,
    session: Session = Depends(get_session),
):
    if not service.remove_categoria_from_producto(
        session, producto_id, categoria_id
    ):
        raise HTTPException(
            status_code=404, detail="Vínculo Producto-Categoría no encontrado"
        )
```

---

## 3. Implementación de Referencia del Frontend (React + TypeScript + TanStack Query + Tailwind CSS)

### 3.1. Definición Estricta de Interfaces TypeScript (`src/types/`)

```ts
// frontend/src/types/categoria.ts
export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string;
}

export interface CategoriaCreate {
  nombre: string;
  descripcion: string;
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

```ts
// frontend/src/types/producto.ts
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

### 3.2. Capa de Servicios HTTP (`src/services/categorias.service.ts`)

```ts
// frontend/src/services/categorias.service.ts
import type {
  Categoria,
  CategoriaCreate,
  CategoriaUpdate,
  PaginatedResponse,
} from "../types/categoria";

const API_BASE_URL = "http://localhost:8000/categorias";

export const getCategorias = async (
  offset = 0,
  limit = 50,
  search?: string
): Promise<PaginatedResponse<Categoria>> => {
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });
  if (search && search.trim() !== "") {
    params.append("search", search.trim());
  }

  const res = await fetch(`${API_BASE_URL}/?${params.toString()}`);
  if (!res.ok) {
    throw new Error("Error al cargar el listado de categorías");
  }
  return res.json();
};

export const createCategoria = async (
  payload: CategoriaCreate
): Promise<Categoria> => {
  const res = await fetch(`${API_BASE_URL}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("No se pudo crear la categoría");
  }
  return res.json();
};

export const updateCategoria = async ({
  id,
  data,
}: {
  id: number;
  data: CategoriaUpdate;
}): Promise<Categoria> => {
  const res = await fetch(`${API_BASE_URL}/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) {
    throw new Error("No se pudo actualizar la categoría");
  }
  return res.json();
};

export const deleteCategoria = async (id: number): Promise<void> => {
  const res = await fetch(`${API_BASE_URL}/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error("No se pudo eliminar la categoría");
  }
};
```

### 3.3. Componente de Navegación (`src/components/Navbar.tsx`)

```tsx
// frontend/src/components/Navbar.tsx
import { NavLink } from "react-router-dom";

export const Navbar = () => {
  const getLinkClasses = ({ isActive }: { isActive: boolean }) =>
    `px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
      isActive
        ? "bg-indigo-600 text-white shadow-sm"
        : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
    }`;

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <span className="text-xl font-bold tracking-tight text-indigo-600">
          🍔 FoodStore Admin
        </span>
        <nav className="flex items-center gap-2">
          <NavLink to="/categorias" className={getLinkClasses}>
            Categorías
          </NavLink>
          <NavLink to="/productos" className={getLinkClasses}>
            Productos
          </NavLink>
        </nav>
      </div>
    </header>
  );
};
```

### 3.4. Modal Controlado de Alta y Edición (`src/components/CategoriaModal.tsx`)

Este componente demuestra el uso correcto de **Client State (`useState`)** para controlar el formulario de alta/edición, manteniendo todas sus `props` rigurosamente tipadas con TypeScript:

```tsx
// frontend/src/components/CategoriaModal.tsx
import { useState, useEffect } from "react";
import type { Categoria, CategoriaCreate } from "../types/categoria";

interface CategoriaModalProps {
  isOpen: boolean;
  initialData: Categoria | null;
  isSubmitting: boolean;
  errorMessage: string | null;
  onClose: () => void;
  onSubmit: (values: CategoriaCreate) => void;
}

export const CategoriaModal = ({
  isOpen,
  initialData,
  isSubmitting,
  errorMessage,
  onClose,
  onSubmit,
}: CategoriaModalProps) => {
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");

  // Sincroniza los campos cuando se abre el modal para editar o para crear
  useEffect(() => {
    if (initialData) {
      setNombre(initialData.nombre);
      setDescripcion(initialData.descripcion);
    } else {
      setNombre("");
      setDescripcion("");
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    onSubmit({
      nombre: nombre.trim(),
      descripcion: descripcion.trim(),
    });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/50 backdrop-blur-xs p-4">
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-md p-6 border border-slate-100">
        <h2 className="text-xl font-bold text-slate-800 mb-4">
          {initialData ? "Editar Categoría" : "Nueva Categoría"}
        </h2>

        {errorMessage && (
          <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-red-700 text-sm">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label
              htmlFor="nombre"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Nombre de la categoría
            </label>
            <input
              id="nombre"
              type="text"
              required
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
              placeholder="Ej. Hamburguesas"
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div>
            <label
              htmlFor="descripcion"
              className="block text-sm font-medium text-slate-700 mb-1"
            >
              Descripción
            </label>
            <textarea
              id="descripcion"
              rows={3}
              required
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
              placeholder="Descripción breve de la categoría..."
              className="w-full rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
            />
          </div>

          <div className="flex justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-100"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-4 py-2 rounded-lg text-sm font-medium bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {isSubmitting ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
```

### 3.5. Página Completa de Categorías con CRUD Reactivo (`src/pages/CategoriasPage.tsx`)

Esta página integra **`useState`** (control booleano del modal y categoría en edición) con **`useQuery`**, **`useMutation`** e **`invalidateQueries`**:

```tsx
// frontend/src/pages/CategoriasPage.tsx
import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  getCategorias,
  createCategoria,
  updateCategoria,
  deleteCategoria,
} from "../services/categorias.service";
import type { Categoria, CategoriaCreate } from "../types/categoria";
import { CategoriaModal } from "../components/CategoriaModal";

export const CategoriasPage = () => {
  const queryClient = useQueryClient();

  // Client State: Apertura del modal, ítem seleccionado para editar y filtro de búsqueda
  const [isModalOpen, setIsModalOpen] = useState<boolean>(false);
  const [editingCategoria, setEditingCategoria] = useState<Categoria | null>(null);
  const [search, setSearch] = useState<string>("");

  // Server State (Lectura): useQuery con clave compuesta por el término de búsqueda
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["categorias", { search }],
    queryFn: () => getCategorias(0, 50, search),
  });

  // Mutación 1: Crear Categoría
  const createMutation = useMutation({
    mutationFn: (nuevo: CategoriaCreate) => createCategoria(nuevo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categorias"] });
      handleCloseModal();
    },
  });

  // Mutación 2: Editar Categoría
  const updateMutation = useMutation({
    mutationFn: ({ id, values }: { id: number; values: CategoriaCreate }) =>
      updateCategoria({ id, data: values }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categorias"] });
      handleCloseModal();
    },
  });

  // Mutación 3: Eliminar Categoría
  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteCategoria(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["categorias"] });
    },
  });

  const handleOpenCreate = () => {
    setEditingCategoria(null);
    createMutation.reset();
    updateMutation.reset();
    setIsModalOpen(true);
  };

  const handleOpenEdit = (categoria: Categoria) => {
    setEditingCategoria(categoria);
    createMutation.reset();
    updateMutation.reset();
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setEditingCategoria(null);
  };

  const handleModalSubmit = (values: CategoriaCreate) => {
    if (editingCategoria) {
      updateMutation.mutate({ id: editingCategoria.id, values });
    } else {
      createMutation.mutate(values);
    }
  };

  const activeError =
    createMutation.error?.message || updateMutation.error?.message || null;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            Gestión de Categorías
          </h1>
          <p className="text-sm text-slate-500">
            Total registradas: {data?.total ?? 0}
          </p>
        </div>

        <div className="flex items-center gap-3">
          <input
            type="search"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Buscar por nombre..."
            className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
          />
          <button
            type="button"
            onClick={handleOpenCreate}
            className="px-4 py-2 rounded-lg bg-indigo-600 text-white text-sm font-medium hover:bg-indigo-700 shadow-xs"
          >
            + Nueva Categoría
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="p-8 text-center text-slate-500 bg-white rounded-2xl border border-slate-200">
          Cargando categorías desde el servidor...
        </div>
      )}

      {isError && (
        <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
          {(error as Error)?.message || "Error al conectar con el backend"}
        </div>
      )}

      {!isLoading && !isError && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {data?.items.map((cat) => (
            <article
              key={cat.id}
              className="bg-white rounded-2xl p-5 shadow-xs border border-slate-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between">
                  <h2 className="font-semibold text-lg text-slate-800">
                    {cat.nombre}
                  </h2>
                  <span className="text-xs font-mono text-slate-400">
                    #{cat.id}
                  </span>
                </div>
                <p className="text-sm text-slate-600 mt-2">{cat.descripcion}</p>
              </div>

              <div className="flex items-center justify-end gap-2 mt-5 pt-3 border-t border-slate-100">
                <button
                  type="button"
                  onClick={() => handleOpenEdit(cat)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-indigo-600 hover:bg-indigo-50"
                >
                  Editar
                </button>
                <button
                  type="button"
                  disabled={deleteMutation.isPending}
                  onClick={() => deleteMutation.mutate(cat.id)}
                  className="px-3 py-1.5 rounded-lg text-xs font-medium text-red-600 hover:bg-red-50 disabled:opacity-50"
                >
                  Eliminar
                </button>
              </div>
            </article>
          ))}
        </div>
      )}

      <CategoriaModal
        isOpen={isModalOpen}
        initialData={editingCategoria}
        isSubmitting={createMutation.isPending || updateMutation.isPending}
        errorMessage={activeError}
        onClose={handleCloseModal}
        onSubmit={handleModalSubmit}
      />
    </div>
  );
};
```

### 3.6. Servicio y Página Paginada de Productos (`src/services/productos.service.ts` y `src/pages/ProductsPage.tsx`)

Para cerrar el circuito de integración con la Parte 1 (paginación con `offset`/`limit`) y la Parte 3 (`useNavigate` hacia `/productos/:id`), se presenta el servicio y la página de productos con controles de paginación calculados sobre `data.total`:

```ts
// frontend/src/services/productos.service.ts
import type { PaginatedResponse } from "../types/categoria";
import type { Producto } from "../types/producto";

const API_BASE_URL = "http://localhost:8000/productos";

export const getProductos = async (
  offset = 0,
  limit = 6,
  nombre?: string
): Promise<PaginatedResponse<Producto>> => {
  const params = new URLSearchParams({
    offset: String(offset),
    limit: String(limit),
  });
  if (nombre && nombre.trim() !== "") {
    params.append("nombre", nombre.trim());
  }

  const res = await fetch(`${API_BASE_URL}/?${params.toString()}`);
  if (!res.ok) {
    throw new Error("Error al cargar el catálogo de productos");
  }
  return res.json();
};

export const getProductoById = async (id: number): Promise<Producto> => {
  const res = await fetch(`${API_BASE_URL}/${id}`);
  if (!res.ok) {
    throw new Error(`Producto #${id} no encontrado`);
  }
  return res.json();
};
```

```tsx
// frontend/src/pages/ProductsPage.tsx
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { getProductos } from "../services/productos.service";

const PAGE_SIZE = 6;

export const ProductsPage = () => {
  const navigate = useNavigate();
  const [page, setPage] = useState<number>(1);
  const [nombre, setNombre] = useState<string>("");

  const offset = (page - 1) * PAGE_SIZE;

  const { data, isLoading, isError } = useQuery({
    queryKey: ["productos", { offset, limit: PAGE_SIZE, nombre }],
    queryFn: () => getProductos(offset, PAGE_SIZE, nombre),
  });

  const total = data?.total ?? 0;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Catálogo de Productos</h1>
          <p className="text-sm text-slate-500">
            Mostrando {data?.items.length ?? 0} de {total} productos
          </p>
        </div>

        <input
          type="search"
          value={nombre}
          onChange={(e) => {
            setNombre(e.target.value);
            setPage(1); // Reiniciar a la página 1 al cambiar el filtro
          }}
          placeholder="Filtrar productos por nombre..."
          className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none"
        />
      </div>

      {isLoading && <p className="text-slate-500">Cargando catálogo...</p>}
      {isError && <p className="text-red-600">Error al obtener los productos.</p>}

      {!isLoading && !isError && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data?.items.map((prod) => (
              <article
                key={prod.id}
                className="bg-white rounded-2xl p-5 shadow-xs border border-slate-200 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between">
                    <h2 className="font-semibold text-slate-800">{prod.nombre}</h2>
                    <span className="text-sm font-bold text-emerald-600">
                      ${Number(prod.precio_base).toFixed(2)}
                    </span>
                  </div>
                  <p className="text-sm text-slate-500 mt-1">
                    {prod.descripcion || "Sin descripción"}
                  </p>
                  <div className="flex flex-wrap gap-1.5 mt-3">
                    {prod.categorias.map((c) => (
                      <span
                        key={c.id}
                        className="px-2 py-0.5 text-xs rounded-full bg-indigo-50 text-indigo-700 font-medium"
                      >
                        {c.nombre}
                      </span>
                    ))}
                  </div>
                </div>

                <button
                  type="button"
                  onClick={() => navigate(`/productos/${prod.id}`)}
                  className="mt-4 text-xs font-semibold text-indigo-600 hover:underline self-end"
                >
                  Ver detalle →
                </button>
              </article>
            ))}
          </div>

          {/* Controles de paginación basados en el total estandarizado */}
          <div className="flex items-center justify-between pt-4 border-t border-slate-200">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((p) => Math.max(1, p - 1))}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-sm disabled:opacity-40"
            >
              ← Anterior
            </button>
            <span className="text-sm text-slate-600">
              Página <strong>{page}</strong> de <strong>{totalPages}</strong>
            </span>
            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((p) => p + 1)}
              className="px-3 py-1.5 rounded-lg border border-slate-300 text-sm disabled:opacity-40"
            >
              Siguiente →
            </button>
          </div>
        </>
      )}
    </div>
  );
};
```

---

## 4. Catálogo de Buenas Prácticas y Antipatrones Full Stack

| # | Antipatrón Frecuente (Qué Evitar) | Por Qué Falla en Producción | Patrón Profesional (Qué Hacer) |
| :--- | :--- | :--- | :--- |
| **1** | **Calcular el total con `len(session.exec(query).all())` en el backend.** | Descarga toda la tabla desde el motor SQL a la memoria RAM de Python en cada petición, destruyendo el propósito del `offset` y `limit`. | Ejecutar una consulta independiente `select(func.count()).select_from(query.subquery())` para que el motor SQL retorne un único entero escalar. |
| **2** | **Omitir `if (!res.ok) throw new Error(...)` al usar `fetch` con TanStack Query.** | `fetch` no lanza excepciones ante códigos `404`, `422` o `500`. Sin el `throw`, `useQuery` y `useMutation` entran en `isSuccess` con el cuerpo del error. | Verificar siempre `if (!res.ok)` en la capa `services/` y lanzar un `new Error(...)` antes de retornar `res.json()`. |
| **3** | **Copiar el resultado `data` de `useQuery` dentro de un `useState` local para renderizar una lista.** | Duplica la fuente de verdad y desconecta la vista de las actualizaciones en segundo plano tras `invalidateQueries`. | Renderizar directamente `data?.items.map(...)` proveniente de `useQuery`. Usar `useState` únicamente para estado de UI (modales, inputs, filtros). |
| **4** | **Olvidar incluir variables de filtro o paginación dentro del `queryKey`.** | Si haces `queryKey: ["productos"]` pero tu `queryFn` usa `page` y `search`, cambiar de página no disparará un nuevo fetch porque la clave no cambió. | Incluir todas las dependencias de la consulta en la clave: `queryKey: ["productos", { offset, limit, search }]`. |
| **5** | **Colocar llamadas a APIs, estados de formularios o lógica de negocio dentro de `App.tsx`.** | Convierte `App.tsx` en un monolito difícil de mantener y acopla todas las pantallas en un solo archivo. | Mantener `App.tsx` exclusivamente como declarador de `<Navbar />` y `<Routes>`, delegando cada vista a su componente en `src/pages/`. |
| **6** | **Usar etiquetas `<a href="/ruta">` para navegar internamente o asumir que `useParams()` devuelve números.** | `<a href>` recarga todo el navegador borrando la caché de TanStack Query; `useParams()` siempre devuelve `string \| undefined`. | Navegar con `<Link>`, `<NavLink>` o `useNavigate()`, y convertir explícitamente los parámetros con `Number(id)`. |

---

## 5. Tabla Resumen Comparativa y Checklist de Implementación

### 5.1. Matriz de Conceptos Críticos: Backend vs. Frontend

| Dimensión Arquitectónica | Backend (FastAPI + SQLModel) | Frontend (React + TanStack Query + React Router) |
| :--- | :--- | :--- |
| **Control de Volumen de Datos** | Cláusulas `.offset(offset).limit(limit)` y conteo con `func.count()`. | Parámetros `offset`/`limit` en el `queryKey` y cálculo de `Math.ceil(total / limit)`. |
| **Filtrado de Información** | Construcción dinámica condicional (`if search: query = query.where(...)`). | Estado local `search` con `useState` sincronizado en el `queryKey`. |
| **Validación y Tipado** | `fastapi.Query(ge=0, le=100)` + Schemas Pydantic (`Create`, `Read`, `Update`). | Interfaces TypeScript en `src/types/` + props tipados en todos los `.tsx`. |
| **Operaciones de Lectura** | Endpoints `GET /recurso` devolviendo `{ total, items }` (`PaginatedResponse`). | Hook declarativo `useQuery({ queryKey, queryFn })` con caché `staleTime` / `gcTime`. |
| **Operaciones de Escritura** | Endpoints `POST` (`201`), `PATCH` (`200`) y `DELETE` (`204`). | Hook imperativo `useMutation({ mutationFn, onSuccess, onError })`. |
| **Sincronización de Estado** | `session.add()`, `session.commit()`, `session.refresh()` en la capa `service.py`. | `queryClient.invalidateQueries({ queryKey })` en el `onSuccess` de la mutación. |
| **Comunicación y Navegación** | `CORSMiddleware` habilitando el origen `http://localhost:5173`. | `BrowserRouter`, `Routes`, `Route`, `useNavigate()` y `useParams()`. |

### 5.2. Checklist Paso a Paso para Implementar Cualquier Módulo Full Stack

1. **Backend — Modelos y Schemas (`models.py` y `schemas.py`):**
   - [ ] Definir las entidades SQLModel con `table=True`, sus claves foráneas y `link_model` si hay relación N:M.
   - [ ] Crear los schemas `Base`, `Create`, `Read`, `Update` y `PaginatedResponse` (`total: int`, `items: List[Read]`).
2. **Backend — Servicio y Router (`service.py`, `router.py`, `main.py`):**
   - [ ] Implementar listado con consulta base `select(Model)`, filtros dinámicos `.ilike()`, conteo `func.count()` sobre `.subquery()` y recorte `.offset().limit()`.
   - [ ] Validar `offset: int = Query(0, ge=0)` y `limit: int = Query(10, ge=1, le=100)` en el router.
   - [ ] Configurar `CORSMiddleware` en `app/main.py` e importar todos los modelos antes de `SQLModel.metadata.create_all(engine)`.
3. **Frontend — Tipos y Servicios (`src/types/` y `src/services/`):**
   - [ ] Declarar las interfaces TypeScript (`Categoria`, `Producto`, `PaginatedResponse<T>`) reflejando exactamente los schemas `Read` y `Create` del backend.
   - [ ] Implementar las funciones asíncronas con `fetch`, incluyendo siempre `if (!res.ok) throw new Error(...)`.
4. **Frontend — Estado del Servidor y Mutaciones (`src/pages/` y `src/components/`):**
   - [ ] Configurar `QueryClientProvider` y `BrowserRouter` en `src/main.tsx`.
   - [ ] Consumir listados con `useQuery` manejando explícitamente los estados `isLoading` e `isError`.
   - [ ] Controlar el modal de alta/edición con `useState<boolean>(false)` y ejecutar las altas, bajas y modificaciones mediante `useMutation`, invocando `queryClient.invalidateQueries` en `onSuccess`.
5. **Frontend — Enrutamiento y Limpieza (`src/App.tsx`):**
   - [ ] Verificar que `App.tsx` solo renderice el `<Navbar />` y el bloque `<Routes>` sin lógica de negocio.
   - [ ] Comprobar que no existan errores de compilación de TypeScript (`tsc -b`) y que todas las vistas apliquen estilos consistentes con Tailwind CSS.
