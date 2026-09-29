# Guía de Estudio — Unidad 5

> **Tecnicatura Universitaria en Programación a Distancia**
> Temas: FastAPI · SQLModel · PostgreSQL · Arquitectura por Capas · React · TypeScript · Vite · Tailwind CSS 4

---

## Índice

1. [El Stack Moderno: FastAPI + React](#1-el-stack-moderno-fastapi--react)
2. [Backend: SQLModel y Pydantic](#2-backend-sqlmodel-y-pydantic)
3. [Backend: Conexión a PostgreSQL](#3-backend-conexión-a-postgresql)
4. [Backend: Arquitectura por Capas](#4-backend-arquitectura-por-capas)
5. [Backend: CRUD Persistente y Transacciones](#5-backend-crud-persistente-y-transacciones)
6. [Frontend: Configuración con Vite y PNPM](#6-frontend-configuración-con-vite-y-pnpm)
7. [Frontend: React — Componentización y Virtual DOM](#7-frontend-react--componentización-y-virtual-dom)
8. [Frontend: Props, Flujo de Datos y Renderizado de Listas](#8-frontend-props-flujo-de-datos-y-renderizado-de-listas)
9. [Estilos: Tailwind CSS 4](#9-estilos-tailwind-css-4)
10. [Errores Comunes y Buenas Prácticas](#10-errores-comunes-y-buenas-prácticas)

---

## 1. El Stack Moderno: FastAPI + React

### ¿Por qué este stack?

Una aplicación web moderna tiene dos partes bien diferenciadas:

| Capa | Tecnología | Responsabilidad |
|------|-----------|----------------|
| **Backend** | FastAPI + SQLModel + PostgreSQL | API REST, persistencia, lógica de negocio |
| **Frontend** | React + TypeScript + Vite | Interfaz de usuario reactiva y tipada |
| **Estilos** | Tailwind CSS 4 | Diseño utility-first, sin archivos CSS extra |

### El flujo completo de datos

```
[Navegador / Cliente]
        ↓ HTTP Request (JSON)
[FastAPI — Router]
        ↓ Valida con Pydantic (Schema de entrada)
[Service — Lógica de Negocio]
        ↓ Transforma en modelo de tabla (SQLModel)
[Session → Engine → PostgreSQL]
        ↓ commit() — escritura real en disco
[Service]
        ↓ refresh() — objeto actualizado con ID generado
[FastAPI — Router]
        ↓ filtra con response_model (Schema de salida)
[Navegador / Cliente]
```

Todo cambio de dato sigue este camino unidireccional:
**Request → Validación → Service (Transacción) → Response Model**

Saltarse cualquier etapa no es un atajo: es una falla de seguridad o de integridad.

---

## 2. Backend: SQLModel y Pydantic

### El problema que resuelve SQLModel

Antes de SQLModel existía **duplicación de código**: había que mantener dos clases para lo mismo.

```python
# ❌ Enfoque antiguo — dos clases para el mismo concepto
class UserSchema(BaseModel):      # Pydantic: valida JSON
    name: str
    email: str

class User(Base):                 # SQLAlchemy ORM: representa la tabla
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
```

Cualquier cambio (añadir un campo `telefono`) implica modificar ambas clases. El riesgo de que queden desincronizadas es alto.

### La solución: SQLModel como puente

SQLModel actúa como puente entre Pydantic y SQLAlchemy:

| Capa | Herramienta | Responsabilidad |
|------|-------------|-----------------|
| Validación de JSON | **Pydantic** | Valida tipos en tiempo de ejecución |
| ORM + persistencia | **SQLModel** | Mapea clases a tablas SQL, gestiona sesiones |

**Una única clase puede cumplir ambos roles** gracias al atributo `table=True`.

### Ejemplo Pydantic puro (validación)

```python
from pydantic import BaseModel
from typing import Optional, List

class User(BaseModel):
    name: str
    age: int
    email: Optional[str] = None
    tags: List[str] = []

# Pydantic valida los tipos, aplica defaults y construye un objeto tipado
input_data = {"name": "Ana", "age": 30, "email": "ana@mail.com", "tags": ["admin"]}
user = User(**input_data)

print(user)              # objeto validado
print(user.model_dump()) # diccionario limpio, listo para JSON
```

**Resultado:** parseo automático con validación de tipos; si `age` no es un `int`, Pydantic lo rechaza en tiempo de ejecución.

### Patrón de herencia con SQLModel

```python
from typing import Optional
from sqlmodel import SQLModel, Field

# 1. Base común con los campos compartidos (sin tabla, sin ID)
class UserBase(SQLModel):
    name: str
    age: int
    email: str

# 2. DTO de creación — lo que envía el cliente (sin ID)
class UserCreate(UserBase):
    pass

# 3. Modelo persistente — con ID opcional (será generado por la BD)
class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
```

| Clase | Rol | ¿Tabla en BD? |
|-------|-----|---------------|
| `UserBase` | Campos compartidos (base DRY) | No |
| `UserCreate` | DTO de entrada (POST) | No |
| `User` | Entidad persistida | **Sí** (`table=True`) |

### Comparativa: antes vs. después

| Criterio | Antes (duplicado) | Con SQLModel |
|----------|-------------------|--------------|
| Líneas de código | ~40 líneas | ~15 líneas |
| Riesgo de desincronización | Alto | Eliminado |
| Fuente de verdad | Dos clases | **Una sola clase** |
| Compatibilidad | — | Total con SQLAlchemy |

### Tres principios de SQLModel

1. **Una única fuente de verdad** — una clase sirve para validación, ORM y tabla al mismo tiempo.
2. **Cero conversiones manuales** — Pydantic valida; SQLModel gestiona el ORM.
3. **Compatibilidad total** con el ecosistema Python moderno / SQLAlchemy.

---

## 3. Backend: Conexión a PostgreSQL

### Las tres piezas de la conexión

Para conectar FastAPI + SQLModel a una base de datos se necesitan tres componentes:

| Pieza | Qué es |
|-------|--------|
| **PostgreSQL** | La base de datos donde viven los datos |
| **Engine** | Traduce Python → SQL; gestiona el pool de conexiones |
| **Sesión** | Unidad de trabajo donde ocurren las transacciones |

### El Engine (`database.py`)

El engine se crea **una sola vez** al iniciar la aplicación. Gestiona el pool para no abrir una conexión nueva en cada query.

```python
from sqlmodel import create_engine, SQLModel, Session
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://user:password@localhost:5432/database_name"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,  # muestra cada query SQL en consola (solo en desarrollo)
)
```

- `postgresql+psycopg` indica el dialecto y el driver.
- `echo=True` registra cada query SQL. Indispensable en desarrollo para detectar problemas de rendimiento (ej: errores *N+1*).
- **Nunca hardcodear credenciales** — usar variables de entorno.

### Creación de tablas

```python
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
```

SQLModel inspecciona todos los modelos con `table=True`, genera el DDL (`CREATE TABLE ...`) y lo ejecuta contra PostgreSQL.

Esta función se llama desde el evento `startup` de FastAPI:

```python
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()   # Las tablas existen antes del primer request
```

### La Sesión

La sesión **no es un helper simple**: es una unidad de trabajo que agrupa operaciones en una transacción:

```
Abrir sesión → operar (add/exec) → commit o rollback → cerrar
```

> **Clave:** mientras no se ejecute `commit()`, los cambios **no son permanentes** en disco.

**Patrón estándar: una sesión por cada request**

```python
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session

def get_session():
    with Session(engine) as session:
        yield session           # se inyecta en cada endpoint
        # al terminar: cierra la sesión y devuelve la conexión al pool

# Alias tipado para inyección de dependencias
SessionDep = Annotated[Session, Depends(get_session)]
```

- `Session(engine)` crea una sesión vinculada al engine.
- El `with` usa el context manager de SQLModel → cierre automático sin fugas.
- `yield` inyecta la sesión en la request sin compartirla entre requests.

**Ventajas:**
- Cada request tiene su propia transacción aislada.
- No se comparte estado entre usuarios.
- La sesión se cierra correctamente aunque ocurra una excepción.

### Organización de archivos

```
proyecto/
├── database.py   # Engine + URL + creación de tablas + generador de sesión
├── models.py     # Modelos (tablas) sin lógica de negocio
└── main.py       # Endpoints, eventos startup, registro de routers
```

---

## 4. Backend: Arquitectura por Capas

### Principio fundamental

La lógica de negocio **nunca va en los endpoints**. Cada capa tiene una única responsabilidad:

```
Cliente → Router → Service → Models/Schemas → Session → PostgreSQL
```

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| **Database** | `database.py` | Engine, URL, sesiones, creación de tablas |
| **Models** | `app/models/` | Definición de tablas (`table=True`), sin lógica |
| **Schemas** | `app/schemas/` | DTOs: validación de entrada y modelos de respuesta |
| **Service** | `app/services/` | Lógica de negocio; dueño del ciclo de la transacción |
| **Router** | `app/routers/` | Endpoints HTTP; delega al service; convierte errores a HTTP |

### Estructura del proyecto

```
nombre-proyecto/
├── main.py
├── database.py
└── app/
    ├── routers/   → maneja Requests y Responses HTTP
    ├── schemas/   → validación (entrada) y response models (salida)
    ├── models/    → estructura de la base de datos
    └── services/  → lógica de negocio y control de transacciones
```

### Schemas / DTOs

Los schemas son los contratos de entrada y salida de la API. **Nunca se conectan a la base de datos.**

```python
# app/schemas/hero.py
from typing import Optional
from sqlmodel import SQLModel

# Base con los campos comunes
class HeroBase(SQLModel):
    name: str
    secret_name: str
    age: Optional[int] = None

# DTO de creación — lo que envía el cliente (sin ID)
class HeroCreate(HeroBase):
    pass

# Modelo de respuesta — lo que recibe el cliente (con ID)
class HeroResponse(HeroBase):
    id: int

# Actualización parcial — todos los campos opcionales (PATCH)
class HeroUpdate(SQLModel):
    name: Optional[str] = None
    secret_name: Optional[str] = None
    age: Optional[int] = None
```

| Clase | Uso | Comentario |
|-------|-----|------------|
| `HeroBase` | Base DRY | Campos compartidos entre create y read |
| `HeroCreate` | Entrada POST | Sin ID (lo genera la BD) |
| `HeroResponse` | Respuesta GET/PATCH | Con ID visible al cliente |
| `HeroUpdate` | Entrada PATCH | Todos opcionales para updates parciales |

### Modelos de tabla

```python
# app/models/hero.py
from typing import Optional
from sqlmodel import SQLModel, Field

class Hero(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    secret_name: str
    age: Optional[int] = None
```

- `table=True` registra la clase como tabla en los metadatos de SQLModel.
- `Field(..., primary_key=True)` define la clave primaria; `default=None` indica que la BD la asigna.

### Separación Models / Schemas: ¿por qué?

Exponer el modelo de tabla directamente al cliente es un error arquitectónico y de seguridad por tres razones:

1. **Seguridad:** no todos los campos deben exponerse (ej: `secret_name`, contraseñas, tokens).
2. **Control:** el cliente no debe poder modificar campos críticos como IDs.
3. **Evolución:** la API puede cambiar sin alterar la estructura interna de la BD.

---

## 5. Backend: CRUD Persistente y Transacciones

### El flujo de cuatro etapas (obligatorio)

```
Request → Validación → Service (Commit/Rollback) → Response Model
```

| Etapa | Qué ocurre |
|-------|-----------|
| **Request** | El cliente envía una petición HTTP con datos en el body (JSON) |
| **Validación** | Pydantic filtra tipos, rechaza datos inválidos (error 400) |
| **Commit** | La transacción se confirma en disco; si falla → Rollback |
| **Response Model** | Filtra la salida: oculta datos sensibles, formatea la respuesta |

### La capa Service: dueña de la transacción

El service recibe la sesión y los datos ya validados. Es responsable de controlar el ciclo de vida completo de la transacción.

#### CREATE

```python
# app/services/hero_service.py
from sqlmodel import Session
from app.models.hero import Hero
from app.schemas.hero import HeroCreate

def create_hero(session: Session, data: HeroCreate) -> Hero:
    # 1. Transformar el DTO en modelo de tabla
    hero = Hero.model_validate(data)

    # 2. Agregar a la sesión (en memoria, aún no en disco)
    session.add(hero)

    # 3. Confirmar la transacción (escritura real en PostgreSQL)
    session.commit()

    # 4. Refrescar para obtener valores generados por la BD (ej: ID)
    session.refresh(hero)

    return hero
```

> `model_validate()` transforma el DTO validado por Pydantic al modelo de tabla. Es la transición de "datos de entrada" a "entidad persistible".

#### READ (por ID)

```python
def get_hero_by_id(session: Session, hero_id: int) -> Hero:
    # session.get genera internamente: SELECT ... WHERE id = ? LIMIT 1
    hero = session.get(Hero, hero_id)

    if not hero:
        raise ValueError("Hero not found")  # error lógico, no HTTP

    return hero
```

- El service lanza `ValueError` cuando no encuentra el recurso.
- El **router** convierte ese `ValueError` en una respuesta HTTP 404.

#### READ (listado)

```python
from sqlmodel import select

def list_heroes(session: Session) -> list[Hero]:
    statement = select(Hero)          # SELECT * FROM hero
    result = session.exec(statement)  # ejecuta contra PostgreSQL
    return result.all()               # convierte filas en objetos Hero
```

#### UPDATE (parcial — PATCH)

```python
def update_hero(session: Session, hero_id: int, data: HeroUpdate) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise ValueError("Hero not found")

    # Solo los campos que el cliente envió
    update_data = data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(hero, field, value)   # asignación dinámica — reutilizable

    session.add(hero)
    session.commit()
    session.refresh(hero)

    return hero
```

- `model_dump(exclude_unset=True)` genera un diccionario **solo con los campos enviados** en el request. Ideal para PATCH parcial.
- `setattr(hero, field, value)` asigna cada campo dinámicamente sin hardcodear nombres de campos.

#### DELETE

```python
def delete_hero(session: Session, hero_id: int) -> None:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise ValueError("Hero not found")

    session.delete(hero)   # borrado físico (hard delete)
    session.commit()
```

### El Router: delega y convierte errores

```python
# app/routers/hero_router.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from database import get_session
from app.schemas.hero import HeroCreate, HeroResponse, HeroUpdate
from app.services.hero_service import (
    create_hero, get_hero_by_id, list_heroes, update_hero, delete_hero
)

router = APIRouter(prefix="/heroes", tags=["heroes"])

@router.post("/", response_model=HeroResponse)
def create(hero: HeroCreate, session: Session = Depends(get_session)):
    return create_hero(session, hero)

@router.get("/{hero_id}", response_model=HeroResponse)
def get_by_id(hero_id: int, session: Session = Depends(get_session)):
    try:
        return get_hero_by_id(session, hero_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/", response_model=list[HeroResponse])
def list_all(session: Session = Depends(get_session)):
    return list_heroes(session)

@router.patch("/{hero_id}", response_model=HeroResponse)
def update(hero_id: int, hero: HeroUpdate, session: Session = Depends(get_session)):
    try:
        return update_hero(session, hero_id, hero)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{hero_id}", status_code=204)
def delete(hero_id: int, session: Session = Depends(get_session)):
    try:
        delete_hero(session, hero_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

**Reglas del router:**
- El router **solo** maneja el protocolo HTTP: recibe request, devuelve response.
- Toda la lógica y el manejo de transacciones están en el service.
- Los errores lógicos del service (`ValueError`) se traducen a errores HTTP aquí.

### Transacciones: Commit y Rollback

| Operación | Cuándo | Efecto |
|-----------|--------|--------|
| `session.add(obj)` | Después de crear/modificar | Agrega el objeto a la sesión (en memoria) |
| `session.commit()` | Al confirmar | Escribe en disco de forma permanente |
| `session.rollback()` | Al detectar error | Deshace todos los cambios de la transacción |
| `session.refresh(obj)` | Después del commit | Sincroniza el objeto con los datos generados por la BD (ej: ID) |
| `session.delete(obj)` | Antes del commit en DELETE | Marca el objeto para eliminación |

**Atomicidad:** o todos los cambios se guardan correctamente, o ninguno se guarda. Esto evita datos corruptos.

### Ejemplo completo: creación de un producto

**Paso 1 — Schemas (entrada y salida)**

```python
# Esquema de Entrada (Validación)
class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    stock: int

# Esquema de Salida (Response Model) — no expone el stock
class ProductoResponse(BaseModel):
    id: int
    nombre: str
    precio: float
```

**Paso 2 — Modelo de tabla**

```python
class Producto(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    precio: float
    stock: int
```

**Paso 3 — Service (lógica + transacción)**

```python
def crear_producto(session: Session, data: ProductoCreate) -> Producto:
    nuevo_producto = Producto(**data.model_dump())
    session.add(nuevo_producto)
    session.commit()
    session.refresh(nuevo_producto)
    return nuevo_producto
```

**Paso 4 — Router (endpoint)**

```python
@app.post("/productos/", response_model=ProductoResponse)
def endpoint_crear_producto(producto: ProductoCreate, db: Session = Depends(get_session)):
    producto_creado = crear_producto(db, producto)
    return producto_creado
```

---

## 6. Extensiones del CRUD — Reglas de Negocio Avanzadas

Más allá del CRUD básico, el proyecto implementa cinco reglas de negocio adicionales que garantizan integridad, rendimiento y trazabilidad. Todas están en `services.py`; los errores se mapean en el router mediante `_handle_domain_error`.

### 6.1. Control de duplicados (unicidad por nombre)

La regla *"el nombre es único en la tabla"* (RN-04, HU-02) se valida contra PostgreSQL antes de cualquier escritura. El check ocurre dentro de la transacción actual del servicio — mismo `session`, mismo commit — sin riesgo de que el registro sea inserto inmediatamente:

```python
# creación — validar contra todo el conjunto existente
existente = session.exec(
    select(Producto).where(Producto.nombre == data.nombre)
).first()
if existente:
    raise ValueError("Producto duplicado")
```

En la actualización parcial, solo se permite cambiar el nombre por uno registrado como único (no bloquea cambiar `Nombre A` por `Nombre B`):

```python
nuevo_nombre = update_dict.get("nombre")
if nuevo_nombre and nuevo_nombre != producto.nombre:
    duplicado = session.exec(
        select(Producto).where(
            Producto.nombre == nuevo_nombre, Producto.id != id
        )
    ).first()
    if duplicado:
        raise ValueError("Producto duplicado")
```

- La consulta usa `select(...).where(...)` sin `LIMIT`; PostgreSQL decide cuántas filas leer (el primer resultado es suficiente; ejecución eficiente gracias al índice de nombre en la tabla).
- En el router, cada endpoint (`POST /`, `GET /{id}`, `PUT /{id}`) captura `ValueError` y delega a `_handle_domain_error`, que traduce *"duplicado"* al código HTTP **409 Conflict** (HU-02).

### 6.2. Paginación del listado

El listado se entrega en fragmentos controlados para evitar cargar todo el catálogo en memoria y reducir tiempo de respuesta por request:

```python
def listar_productos(session: Session, skip: int = 0, limit: int = 10) -> List[Producto]:
    statement = select(Producto).offset(skip).limit(limit)
    return list(session.exec(statement).all())
```

El router acota los parámetros con `Query(..., ge=0, le=50)` → máximo 50 registros por página. El endpoint: `GET /productos/?skip=0&limit=10`.

### 6.3. Cálculo de stock con resguardo contra nulos

El atributo `stock` y `stock_minimo` pueden ser `None` en la base de datos. La función `obtener_estado_stock` primero los expande a valores seguros (cero si es nulo), luego compara sin riesgo de excepción:

```python
stock = producto.stock if producto.stock is not None else 0
stock_minimo = producto.stock_minimo if producto.stock_minimo is not None else 0
alerta_stock = stock < stock_minimo
```

Retorna un diccionario con tres campos (`stock`, `bajo_stock_minimo`, `activo`) — sin errores de tipo. Sin este resguardo, una llamada directa como `producto.stock < producto.stock_minimo` lanzaría `AttributeError`.

### 6.4. Borrado lógico (desactivación)

En lugar del borrado físico (`DELETE FROM ...`), la operación marca el registro como inactivo (`activo = False`). La fila queda intacta en la base de datos para trazabilidad histórica y auditoría, devolviendo el mismo objeto persistente:

```python
def eliminar_producto(session: Session, id: int) -> Producto:
    producto = obtener_producto_por_id(session, id)
    producto.activo = False
    session.add(producto)
    session.commit()
    session.refresh(producto)
    return producto  # se retorna el objeto desactivado (no None)
```

Ventajas sobre borrado físico:
- Los registros quedan visibles en consultas sin filtro de `activo` (historial, auditoría).
- Las vistas/lots que filtran por `WHERE activo = True` dejan de mostrarlos automáticamente.
- Sin riesgo de pérdida accidental: la fila sigue en la BD, solo "borrada" lógicamente.

### 6.5. Mapeo centralizado de errores

En lugar de traducir `ValueError` a código HTTP en cada endpoint individualmente, se usa un helper central `_handle_domain_error`:

```python
def _handle_domain_error(e: ValueError) -> None:
    msg = str(e)
    if "no encontrado" in msg.lower():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=msg)
    if "duplicado" en msg.lower():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=msg)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
```

Todos los endpoints que pueden lanzar `ValueError` capturan la excepción y delegan al mapeador: `GET /{id}`, `PUT /{id}`, `DELETE /{id}`. Este patrón unifica tres códigos de estado HTTP en un solo lugar y es explícitamente requerido por HU-02 ("Conflictos de negocio como nombre duplicado devuelven 409") y RN-04 (existencia del producto).

---

## 7. Frontend: Configuración con Vite y PNPM

### Herramientas del stack frontend

| Herramienta | Propósito |
|-------------|-----------|
| **Vite** | Dev server local rápido con HMR; build optimizado para producción |
| **PNPM** | Gestor de paquetes más seguro y eficiente que npm (repositorio local, no ejecuta scripts extra) |
| **React** | Biblioteca declarativa para construir interfaces con componentes reutilizables |
| **TypeScript** | Tipado estático sobre JavaScript → errores detectados antes de ejecutar |

### Crear un proyecto

```bash
# Prerrequisitos
node -v         # verificar Node.js
pnpm -v         # verificar PNPM

# Instalar PNPM si no está disponible
npm install -g pnpm

# Crear proyecto con Vite
pnpm create vite mi-primera-app
cd mi-primera-app
pnpm dev        # inicia el dev server → localhost:5173
```

Al crear el proyecto, Vite pregunta:
- **Framework:** React ✅
- **Variante:** TypeScript ✅ (no JavaScript vanilla)

### Estructura del proyecto

```
mi-primera-app/
├── index.html              # HTML entry point → <div id="root"></div>
├── public/                 # archivos estáticos
├── src/
│   ├── main.tsx            # punto de entrada de React
│   ├── App.tsx             # componente principal
│   ├── App.css             # estilos del App
│   └── index.css           # estilos globales
├── vite.config.ts          # configuración del build tool
├── tsconfig.json           # referencia a tsconfig.node.json + tsconfig.app.json
├── tsconfig.node.json      # compila vite.config.ts
├── tsconfig.app.json       # compila la app TSX
└── package.json            # scripts y dependencias
```

- `tsconfig.json` **no compila** por sí solo; referencia dos configs distintos.
- `tsconfig.node.json` → compila el entorno de Vite (target ES2023, bundler resolution).
- `tsconfig.app.json` → compila la app React con soporte TSX.

### Punto de entrada: `index.html` + `main.tsx`

```html
<!-- index.html -->
<body>
  <div id="root"></div>   <!-- React inyecta toda la UI aquí -->
  <script type="module" src="/src/main.tsx"></script>
</body>
```

```typescript
// src/main.tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'       // estilos globales — sin esto, la app no renderiza nada
import { App } from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
```

- `createRoot()` inyecta React DOM dentro del `<div id="root">`.
- `StrictMode` activa advertencias adicionales en desarrollo.
- Si se omite `import './index.css'`, la aplicación no renderiza nada.

### Scripts disponibles

| Comando | Qué hace |
|---------|----------|
| `pnpm dev` | Arranca Vite dev server con HMR (localhost:5173) |
| `pnpm build` | Compila TS → JS y bundlea para producción (`tsc -b` + `vite build`) |
| `pnpm lint` | Verifica reglas ESLint con TypeScript |
| `pnpm preview` | Simula el entorno de producción localmente |

### `package.json` — dependencias clave

```json
{
  "type": "module",
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^5.1.1",
    "typescript": "~5.9.3",
    "typescript-eslint": "^8.48.0",
    "vite": "^7.3.1"
  }
}
```

- `@vitejs/plugin-react` permite compilar TSX en tiempo real (HMR / Fast Refresh).
- `"type": "module"` porque Vite usa ES modules en todos los archivos.

---

## 7. Frontend: React — Componentización y Virtual DOM

### ¿Qué es React?

React es una librería declarativa creada por Meta (2013) para construir interfaces de usuario con **componentes reutilizables**.

> **Declarativa:** describís *cómo querés que se vea* la UI, no *cómo actualizarla paso a paso*. React se encarga de los cambios.

### Componentes funcionales

Un componente es una función que retorna JSX (fragmentos de interfaz de usuario):

```typescript
function Banner() {
  return <header>La plataforma que impulsa tu negocio</header>;
}
```

Características:
- **Reutilizables:** el mismo componente se usa en distintas partes de la página.
- **Encapsulados:** cada componente tiene su propia lógica y responsabilidad.
- **Tipados:** con TypeScript, las props se validan en tiempo de compilación.

### Virtual DOM

El Virtual DOM es una copia ligera del DOM real almacenada en memoria. React la compara con cada cambio para actualizar **solo lo necesario**:

```
DOM real (en el navegador)
      ↑
Virtual DOM (copia en memoria)
      ↑
React compara diferencias → re-renderiza solo lo que cambió
```

Si solo cambió el texto de un botón, React actualiza únicamente ese nodo, no toda la página.

### Evolución de versiones

| Versión | Año | Características clave |
|---------|-----|-----------------------|
| **React 16** | 2017 | Manejo de errores, portals, fragments |
| **React 16.8** | 2019 | Functional components, **Hooks** (`useState`, `useEffect`) |
| **React 18** | 2022 | Concurrent mode, mejoras de rendimiento |
| **React 19** | 2024 | Nuevos `use` hooks, soporte mejorado para server components |

### Hooks: el poder de los componentes funcionales

Los Hooks son funciones de React que permiten acceder a estado y ciclo de vida desde componentes funcionales:

```typescript
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      {count}
    </button>
  );
}
```

### Componentización atómica: el principio de diseño

En lugar de un archivo HTML de 500 líneas, la interfaz se divide en componentes pequeños:

```
LandingPage
├── Navbar
├── Banner
├── Features
│   ├── FeatureCard (×6)
├── ContactForm
└── Footer
```

**Beneficios:**

| Beneficio | Ejemplo |
|-----------|---------|
| **Reutilización** | El mismo `Button` en diez lugares distintos |
| **Mantenibilidad** | Error en el formulario → solo buscás en `ContactForm.tsx` |
| **Separación de preocupaciones** | Cada componente tiene su lógica y estilos propios |

**Código no componentizado vs componentizado:**

```typescript
// ❌ LandingPageBad.tsx — ~210 líneas, todo junto
const LandingPageBad = () => {
  return (
    <div>
      <header>Launchly</header>
      <main>
        <section id="banner"><h1>Hola mundo</h1></section>
        <section id="features">
          <div>Rendimiento</div>
          <div>Seguridad</div>
          {/* ... más divs repetidos ... */}
        </section>
      </main>
    </div>
  );
};

// ✅ LandingPage.tsx — ~20 líneas, componentizado
import Navbar from "../../components/Navbar/Navbar";
import Banner from "../../components/Banner/Banner";
import Features from "../../components/Features/Features";
import ContactForm from "../../components/ContactForm/ContactForm";
import Footer from "../../components/Footer/Footer";

const LandingPage = () => {
  return (
    <>
      <Navbar />
      <main>
        <Banner />
        <Features />
        <ContactForm />
      </main>
      <Footer />
    </>
  );
};
```

### CSS Modules vs CSS normal

Con CSS Modules cada archivo genera un hash único para sus clases, evitando colisiones de nombres:

```typescript
// ✅ Con CSS Modules — clase aislada al componente
import styles from './Navbar.module.css';

const Navbar = () => (
  <header className={styles.navbar}>
    {/* ... */}
  </header>
);

// ❌ Con CSS normal — React puede alterar el nombre de la clase
<element className="my-component">  {/* ¡puede no coincidir! */}
```

### Reglas JSX importantes

- Los componentes deben comenzar con **PascalCase** (`Navbar`, `FeatureCard`).
- En JSX se usa `className` en lugar de `class` (reservada en JS).
- Usar `htmlFor` en lugar de `for` en los `<label>`.
- Todo el JSX retornado debe tener **un único elemento raíz** (o usar un Fragment `<>...</>`).

---

## 8. Frontend: Props, Flujo de Datos y Renderizado de Listas

### El flujo unidireccional de datos

En React, los datos fluyen **de arriba hacia abajo** (de padre a hijo):

```
                    [Padre]
                    ↓  ↓  ↓
                [Hijo A] [Hijo B] [Hijo C]
                    (props)

Eventos suben: hijo → padre (onClick, onChange)
Datos bajan:  padre → hijo (props)
```

| Dirección | Qué viaja | Ejemplo |
|-----------|-----------|---------|
| **Padre → Hijo** | Props | `name`, `visible`, `count` |
| **Hijo → Padre** | Eventos | `onClick`, `onChange` |

### Props tipadas con TypeScript

**Siempre** definir el tipo de las props. Nunca usar `props: any`.

```typescript
// Definición del contrato del componente
type SaludoProps = {
  nombre: string
}

// El componente desestructura y TypeScript verifica la existencia
export const Saludo = ({ nombre }: SaludoProps) => {
  return <h2>Hola, {nombre}</h2>
}

// Uso en el padre
<Saludo nombre="Luciano" />
<Saludo nombre="Pedro" />
```

Si se omite la prop `nombre`, TypeScript avisa en tiempo de compilación: *"falta nombre"*.

**Ejemplo con múltiples props:**

```typescript
type CardProps = {
  titulo: string       // obligatorio
  descripcion: string  // obligatorio
}

export const Card = ({ titulo, descripcion }: CardProps) => {
  return (
    <div>
      <h3>{titulo}</h3>
      <p>{descripcion}</p>
    </div>
  )
}
```

### Renderizado de listas con `.map()`

Cuando hay elementos similares en cantidad variable, **no** se escriben manualmente. Se usa `.map()` para transformar un array de datos en elementos JSX:

```typescript
const services = [
  { id: 1, name: "Diseño Web" },
  { id: 2, name: "SEO" },
  { id: 3, name: "Marketing" }
];

// Dentro del componente:
{services.map((service) => (
  <ServiceCard key={service.id} name={service.name} />
))}
```

**La prop `key` es obligatoria.** React la necesita para identificar qué elementos cambiaron, se añadieron o se eliminaron. Sin `key`, React re-renderiza toda la lista en cada cambio, lo cual es ineficiente.

- `key` debe ser **único** entre los elementos hermanos.
- Usar un ID estable del dato, nunca el índice del array (puede causar bugs).

### Patrón padre/hijo con `.map()`: Features + FeatureCard

```typescript
// Features.tsx — componente PADRE
interface Feature {
  icon: string;
  title: string;
  description: string;
}

const features: Feature[] = [
  { icon: '⚡', title: 'Rendimiento', description: 'Velocidad máxima.' },
  { icon: '🔒', title: 'Seguridad',   description: 'Protección total.' },
  { icon: '📊', title: 'Analíticas',  description: 'Datos en tiempo real.' },
];

const Features = () => (
  <section id="features">
    <div className="grid">
      {features.map((feature) => (
        <FeatureCard
          key={feature.title}
          icon={feature.icon}
          title={feature.title}
          description={feature.description}
        />
      ))}
    </div>
  </section>
);
```

```typescript
// FeatureCard.tsx — componente HIJO
interface FeatureCardProps {
  icon: string;
  title: string;
  description: string;
}

const FeatureCard = ({ icon, title, description }: FeatureCardProps) => (
  <div>
    <div>{icon}</div>
    <h3>{title}</h3>
    <p>{description}</p>
  </div>
);
```

### Navegación con `.map()` en la Navbar

```typescript
const links = [
  { label: 'Inicio',          href: '#banner' },
  { label: 'Características', href: '#features' },
  { label: 'Contacto',        href: '#contact' },
];

const Navbar = () => (
  <header>
    <nav>
      {links.map((link) => (
        <a key={link.href} href={link.href}>
          {link.label}
        </a>
      ))}
    </nav>
  </header>
);
```

### Año dinámico sin hardcodear

```typescript
const Footer = () => {
  const year = new Date().getFullYear();   // se actualiza automáticamente
  return <footer>© {year} Launchly. Todos los derechos reservados.</footer>;
};
```

### Regla práctica para decidir cuándo usar `.map()`

> Si estás copiando y pegando el mismo bloque de JSX más de dos veces con datos distintos, necesitás un array y `.map()`.

---

## 9. Estilos: Tailwind CSS 4

### ¿Qué es Tailwind CSS?

Tailwind CSS es un framework **utility-first**: en lugar de escribir un archivo CSS con reglas para cada componente, se aplican **clases atómicas** directamente en el HTML.

```css
/* ❌ Sin Tailwind — archivo CSS separado */
.card {
  background-color: #ffffff;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

```jsx
{/* ✅ Con Tailwind — clases atómicas en el HTML */}
<div className="bg-white rounded-lg shadow">
  <h2>Card contenido</h2>
</div>
```

No se inventan nombres, no se cambia el archivo CSS; el componente es completamente autónomo.

| Característica | Descripción |
|----------------|-------------|
| **Utility first** | Clases de bajo nivel aplicadas directamente al HTML |
| **Sin CSS custom** | El estilo vive en el `className`; no hay archivos CSS extra |
| **Responsive integrado** | Sin media queries manuales para cada breakpoint |
| **Integración con React** | Compila sin problemas con Vite |
| **Diseño consistente** | Una única fuente de verdad para todos los estilos |

### Instalación con Vite

```bash
# Crear proyecto
npm create vite@latest mi-proyecto -- --template react
cd mi-proyecto

# Instalar Tailwind CSS 4 + plugin de Vite
npm install css @tailwindcss/vite
```

**Configurar `vite.config.ts`:**

```typescript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
});
```

**Configurar `src/index.css`:**

```css
@import "tailwindcss";
```

Con esta única línea, Tailwind está activo en el proyecto.

### Sistema de espaciado: múltiplos de 4px

Tailwind usa valores en múltiplos de 4 píxeles. Cada unidad equivale a `4px × el número`:

| Valor | Píxeles |
|-------|---------|
| `1`   | 4px     |
| `2`   | 8px     |
| `4`   | 16px    |
| `6`   | 24px    |
| `8`   | 32px    |
| `16`  | 64px    |

### Padding y Margin

| Clase | Aplicación |
|-------|------------|
| `p-4` | Todos los lados (16px) |
| `px-4` | Izquierda + derecha |
| `py-4` | Arriba + abajo |
| `pt-4` | Solo superior |
| `pb-4` | Solo inferior |
| `pl-4` | Solo izquierda |
| `pr-4` | Solo derecha |
| `m-4` | Margin todos los lados |
| `mx-auto` | Centrado horizontal |

```jsx
<div className="p-10">      {/* 40px de padding en todos los lados */}
<div className="px-6 py-4"> {/* 24px horizontal, 16px vertical */}
```

### Gap (Flexbox y Grid)

```jsx
<div className="flex flex-col gap-8">  {/* 32px entre ítems */}
<div className="grid gap-4">           {/* 16px en ambos ejes */}
<div className="grid gap-x-4">        {/* 16px solo horizontal */}
```

### Tipografía

**Tamaño de fuente:**

```jsx
<p className="text-xs">    {/* notas auxiliares, metadata */}
<p className="text-sm">    {/* texto secundario */}
<p className="text-base">  {/* texto principal */}
<p className="text-lg">    {/* destacado leve */}
<p className="text-xl">    {/* subtítulos */}
<p className="text-2xl">   {/* títulos de sección */}
<p className="text-3xl">   {/* encabezados importantes */}
<p className="text-4xl">   {/* hero / título principal */}
```

**Peso de la fuente:**

```jsx
<p className="font-normal">    {/* 400 — texto estándar */}
<p className="font-medium">   {/* 500 — texto destacado leve */}
<p className="font-semibold"> {/* 600 — subtítulos importantes */}
<p className="font-bold">     {/* 700 — encabezados */}
<p className="font-extrabold">{/* 800 — títulos principales */}
```

**Alto de línea:**

```jsx
<p className="leading-none">    {/* 1    — titulares compactos */}
<p className="leading-tight">   {/* 1.25 — encabezados */}
<p className="leading-normal">  {/* 1.5  — texto estándar */}
<p className="leading-relaxed"> {/* 1.625 — lectura cómoda */}
<p className="leading-loose">   {/* 2    — texto muy espaciado */}
```

**Espaciado de letra:**

```jsx
<p className="tracking-tight">   {/* compacto, títulos */}
<p className="tracking-normal">  {/* común, texto regular */}
<p className="tracking-wide">    {/* separadas, subtítulos */}
<p className="tracking-widest">  {/* mayúsculas/etiquetas */}
```

### Colores

Tailwind incluye una paleta con escala de tonalidades del **50 al 950** (muy claro a muy oscuro):

| Tonalidad | Uso típico |
|-----------|------------|
| `blue-100` | Fondo muy claro |
| `blue-300` | Bordes, hover suave |
| `blue-500` | Color principal / acciones |
| `blue-700` | Hover en botones, elementos oscuros |
| `blue-900` | Texto oscuro sobre fondo claro |

**Prefijos de aplicación:**

```jsx
<div className="bg-blue-500">     {/* fondo */}
<p className="text-blue-700">     {/* texto */}
<div className="border-blue-300"> {/* borde */}
<input className="focus:ring-blue-500"> {/* focus ring */}
<input className="placeholder-blue-400"> {/* placeholder */}
```

**Semántica de colores:**

| Color | Uso |
|-------|-----|
| **Grises** | Textos y fondos neutros |
| **Azules/Índigos** | Acciones principales, botones |
| **Verdes** | Éxitos, confirmaciones |
| **Rojos** | Errores, peligro |
| **Amarillos** | Advertencias |

### Layouts: Flexbox

```jsx
{/* Activar Flexbox */}
<div className="flex">

{/* Dirección */}
<div className="flex flex-row">  {/* fila horizontal (default) */}
<div className="flex flex-col">  {/* columna vertical */}

{/* Alinear en el eje principal */}
<div className="justify-start">    {/* alineado a izquierda */}
<div className="justify-center">   {/* centrado */}
<div className="justify-between">  {/* extremos */}
<div className="justify-end">      {/* alineado a derecha */}

{/* Alinear en el eje cruzado */}
<div className="items-center">  {/* centrado verticalmente */}
<div className="items-start">   {/* alineado arriba */}

{/* Wrap */}
<div className="flex flex-wrap">  {/* múltiples filas si no caben */}
```

**Ejemplo real:**

```jsx
<div className="flex items-center justify-between gap-4 p-6">
  <div>Logo</div>
  <nav className="flex gap-4">
    <a href="#">Inicio</a>
    <a href="#">Servicios</a>
  </nav>
</div>
```

### Layouts: CSS Grid

```jsx
{/* Activar Grid con columnas */}
<div className="grid grid-cols-3 gap-4">  {/* 3 columnas, 16px separación */}
<div className="grid grid-cols-2 gap-4">  {/* 2 columnas */}

{/* Ocupar múltiples columnas */}
<div className="col-span-2">  {/* ocupa 2 columnas del grid */}
```

**Ejemplo real:**

```jsx
<div className="grid grid-cols-3 gap-6">
  {features.map((f) => (
    <FeatureCard key={f.title} {...f} />
  ))}
</div>
```

---

## 10. Errores Comunes y Buenas Prácticas

### Backend — Errores a evitar

| ❌ Error | ✅ Práctica correcta |
|---------|---------------------|
| Recibir un JSON genérico sin validar | Siempre usar schemas de entrada (Pydantic/SQLModel) |
| Hacer `session.commit()` en el router | El commit va **solo** en el service |
| Devolver el modelo de tabla completo al cliente | Usar `response_model` con el schema de salida |
| Confundir modelo de BD con schema de validación | Son responsabilidades distintas; separarlos |
| Hardcodear credenciales de BD | Usar variables de entorno |
| Lógica de negocio en el endpoint | La lógica va en el service |

### Frontend — Errores a evitar

| ❌ Error | ✅ Práctica correcta |
|---------|---------------------|
| Usar `props: any` | Tipar siempre con interfaces o tipos explícitos |
| Repetir el mismo JSX N veces | Usar un array + `.map()` |
| Olvidar la prop `key` en `.map()` | Siempre añadir `key` único (no índice) |
| Todo el código en un solo componente | Componentizar en piezas atómicas |
| Usar CSS con clases que colisionan | Usar CSS Modules o Tailwind CSS |
| Nombres de componentes en camelCase | Usar **PascalCase** (`FeatureCard`, no `featureCard`) |

### Resumen de responsabilidades por capa

```
Router       → recibe HTTP, delega al service, convierte errores a HTTP
Service      → lógica de negocio, dueño del ciclo de transacción
Schema/DTO   → valida entrada, filtra salida
Model        → define tabla en la BD, sin lógica de negocio
Database     → engine, sesión, creación de tablas
```

### Checklist antes de hacer un commit al repositorio

**Backend:**
- [ ] ¿Los schemas de entrada y salida están separados?
- [ ] ¿El `commit()` está en el service, no en el router?
- [ ] ¿El `response_model` oculta los campos sensibles?
- [ ] ¿Las credenciales de BD se leen desde variables de entorno?
- [ ] ¿Todos los endpoints retornan el tipo correcto?

**Frontend:**
- [ ] ¿Todas las props están tipadas con interfaces?
- [ ] ¿Todos los elementos de `.map()` tienen `key`?
- [ ] ¿Los componentes comienzan con PascalCase?
- [ ] ¿Los estilos usan CSS Modules o Tailwind CSS?
- [ ] ¿No hay listas de JSX repetido sin `.map()`?

---

## Referencia Rápida de Comandos

### Backend

```bash
# Arrancar el servidor FastAPI
uvicorn main:app --reload

# Instalar dependencias
pip install "fastapi[standard]" sqlmodel psycopg2-binary
```

### Frontend

```bash
# Crear proyecto con Vite + React + TypeScript
pnpm create vite mi-app
cd mi-app
pnpm install

# Añadir Tailwind CSS 4
pnpm add tailwindcss @tailwindcss/vite

# Desarrollo
pnpm dev

# Build para producción
pnpm build
```

### Pruebas de la API (HTTP)

```http
### Crear héroe
POST http://localhost:8000/heroes
Content-Type: application/json

{"name": "Batman", "secret_name": "Bruce Wayne", "age": 35}

### Listar todos
GET http://localhost:8000/heroes

### Obtener por ID
GET http://localhost:8000/heroes/1

### Actualización parcial
PATCH http://localhost:8000/heroes/1
Content-Type: application/json

{"age": 40}

### Eliminar
DELETE http://localhost:8000/heroes/1
```
