# Guía Maestra: Arquitectura de Relaciones en Backend (FastAPI / SQLModel) y Gestión de Estado en Frontend (React)

---

## Introducción y Propósito

El desarrollo de aplicaciones web modernas de alto rendimiento exige una comprensión rigurosa y sin fisuras de dos pilares esenciales:
1. **La persistencia relacional en el backend**, garantizando integridad referencial, modelado normalizado y consultas eficientes sin sobrecarga de base de datos.
2. **La gestión de estado y ciclo de vida en el frontend**, asegurando interfaces reactivas, inmutabilidad de datos y separación limpia entre lógica y presentación.

Esta guía consolida la teoría arquitectónica, patrones de diseño de la industria, ejemplos completos en **Python (FastAPI + SQLModel / SQLAlchemy)** y **TypeScript (React + Hooks)**, así como las buenas prácticas innegociables para construir sistemas escalables y mantenibles a largo plazo.

---

# Parte 1: Backend — Arquitectura de Relaciones con SQLModel y FastAPI

---

## 1. Teoría y Fundamentos de Relaciones en Bases de Datos Relacionales

### 1.1. Relaciones 1:N (Uno a Muchos) y Perspectiva N:1 (Muchos a Uno)

Una relación de uno a muchos (**1:N**) modela una asociación donde un único registro en una tabla principal o "padre" puede estar vinculado con múltiples registros en una tabla secundaria o "hija". Por ejemplo, un equipo (**Team**) posee múltiples héroes (**Hero**).

* **Equivalencia Conceptual 1:N vs. N:1:** Ambas expresiones describen exactamente la misma asociación estructural, pero observada desde extremos opuestos del grafo relacional:
  * Desde el punto de vista del equipo: un `Team` tiene muchos `Heroes` (1:N).
  * Desde el punto de vista del héroe: un `Hero` pertenece a un único `Team` (N:1).

#### La Regla de Oro de la Clave Foránea (Foreign Key)
> **Principio Inquebrantable:** En el modelo relacional, la clave foránea (**FK**) siempre debe residir físicamente en la tabla correspondiente al lado "muchos" (la entidad hija).

Jamás se almacena una lista o colección de identificadores dentro de la tabla del lado "uno", ya que esto violaría la Primera Forma Normal (1FN), destruiría la indexación y haría imposible la integridad referencial a nivel de motor.

#### El Principio de Aislamiento del Padre
El registro padre (lado "uno") jamás almacena referencias de sus entidades hijas a nivel de estructura física de base de datos. La tabla `team` desconoce por completo cuántos registros de `hero` hacen referencia a su clave primaria. Esto garantiza que la entidad padre exista de forma totalmente autónoma e independiente de sus dependientes.

---

### 1.2. Relaciones N:N (Muchos a Muchos)

Una relación de muchos a muchos (**N:N**) ocurre cuando múltiples registros de la Tabla A pueden vincularse con múltiples registros de la Tabla B, y viceversa. Ejemplos canónicos:
* Un héroe pertenece a múltiples equipos (ej. *Spider-Man* forma parte de *Avengers* y de *Fantastic Four*).
* Un equipo está compuesto por múltiples héroes.
* Artículos con múltiples etiquetas (*tags*), y etiquetas aplicadas a miles de artículos.

#### Limitaciones del Modelo Relacional y Riesgo de Redundancia
Ninguna clave foránea simple ubicada en las entidades principales es capaz de capturar una relación N:N:
* Si se colocara `team_id` en `Hero`, un héroe solo podría tener un equipo.
* Si se intentara duplicar la fila del héroe por cada equipo al que pertenece, se incurriría en **redundancia severa de datos**: cualquier cambio en el nombre o poderes del héroe exigiría actualizar múltiples filas, derivando en anomalías de actualización y corrupción de datos.

#### La Solución Canónica: La Tabla Intermedia (Link Table / Junction Table)
La solución estandarizada consiste en descomponer la relación N:N en dos relaciones 1:N mediante una **tabla intermedia** (también denominada tabla de enlace, pivote o puente). Su único propósito es registrar las asociaciones sin duplicar los datos de las entidades de negocio.

* **Nomenclatura Convencional:** Se construye combinando los nombres de las entidades vinculadas (ej. `hero_team_link`).
* **Clave Primaria Compuesta (Composite Primary Key):** Para garantizar que un héroe no sea asignado dos veces al mismo equipo, la tabla intermedia define una clave primaria compuesta integrada por la combinación indivisible de ambas claves foráneas (`hero_id` + `team_id`). A nivel matemático y relacional, esto impide la duplicidad de asociaciones en el motor.

#### Regla de Oro Minimalista vs. Metadatos de la Relación
* **Forma Pura (Minimalista):** Contiene exclusivamente las dos claves foráneas que componen la clave primaria. Todos los datos descriptivos permanecen en las tablas de origen.
* **Extensión Semántica (Metadatos):** Cuando el vínculo mismo posee propiedades intrínsecas que no pertenecen ni al héroe ni al equipo por separado, la tabla intermedia aloja dichos atributos. Ejemplos:
  * `joined_at` (`datetime`): Momento exacto de incorporación al equipo.
  * `role` (`str` o `Enum`): Rol dentro de la asociación (ej. *Líder*, *Miembro activo*, *Reserva*).
  * `status` (`Enum`): Estado de la afiliación (ej. *Activo*, *Suspendido*).

---

### 1.3. Estructura Física (Disco/SQL) vs. Navegación en Memoria (ORM / Python)

Uno de los errores conceptuales más frecuentes es confundir las definiciones físicas de base de datos con las estructuras de conveniencia del ORM.

```
+-----------------------------------------------------------------------+
| BASE DE DATOS (Física en Disco)                                       |
| - Columnas reales, tipos SQL, restricciones.                          |
| - Claves Foráneas: Field(foreign_key="team.id")                        |
| - Genera: team_id INTEGER REFERENCES team(id)                         |
+-----------------------------------------------------------------------+
                                  │
                       Traducción bidireccional (ORM)
                                  ▼
+-----------------------------------------------------------------------+
| MEMORIA PYTHON (Objetos y Grafos)                                     |
| - Navegación entre objetos: Relationship(back_populates="...")        |
| - NO genera columnas nuevas en la base de datos (NO ALTER TABLE).     |
| - Permite la sintaxis: hero.team  o  team.heroes                      |
+-----------------------------------------------------------------------+
```

1. **Estructura Física (Persistencia Real):**
   * Se define mediante `Field(foreign_key="tabla.id")`.
   * Crea una columna real en la tabla SQL con una restricción de integridad referencial (`REFERENCES`).
2. **Navegación en Memoria (`Relationship`):**
   * Es una abstracción exclusiva de Python y SQLAlchemy/SQLModel.
   * **Bajo ninguna circunstancia crea columnas físicas ni ejecuta comandos `ALTER TABLE`.**
   * Facilita recorrer el grafo de objetos cargados en la sesión (`hero.team.name` o `[h.name for h in team.heroes]`).
   * **Sincronización Bidireccional (`back_populates`):** Es de uso obligatorio y simétrico. Permite que, al asignar `hero.team = un_equipo`, el ORM actualice automáticamente la lista en memoria `un_equipo.heroes` para preservar la coherencia.
   * **El parámetro `link_model`:** En relaciones N:N, indica al ORM qué tabla intermedia debe utilizarse para construir automáticamente los `JOIN` subyacentes.

---

### 1.4. Estrategia de Rendimiento: Carga de Datos y el Problema N+1

#### Comportamiento por Defecto: Carga Perezosa (Lazy Loading)
Por defecto, los ORMs (incluyendo SQLModel / SQLAlchemy) aplican **Lazy Loading**. Esto significa que cuando se consulta una entidad (`Hero`), el ORM solo trae sus campos directos. La relación asociada (`hero.team`) no se busca en el motor hasta el momento exacto en que el código accede explícitamente a esa propiedad.

Esto introduce dos riesgos críticos en arquitecturas de APIs:

1. **Riesgo 1: Error de Sesión Desconectada (Detached Instance Error):**
   Si la sesión de base de datos se cierra (por ejemplo, al salir del bloque de dependencias en FastAPI) antes de que la capa de serialización acceda al atributo relacionado, la aplicación arrojará una excepción fatal en tiempo de ejecución (`DetachedInstanceError`).
2. **Riesgo 2: El Problema de Consultas N+1 ($1 + N$ Queries):**
   Si se listan $N$ héroes mediante `SELECT * FROM hero` y luego la aplicación serializa el equipo de cada uno, el ORM disparará:
   * **1 consulta** inicial para recuperar la lista de héroes.
   * **$N$ consultas individuales** adicionales (`SELECT * FROM team WHERE id = ?`), una por cada héroe.
   
   Para $1.000$ registros, el sistema emitirá $1.001$ consultas HTTP/SQL, colapsando el pool de conexiones y degradando la latencia de milisegundos a varios segundos.

#### Resolución Arquitectónica: Carga Anticipada (Eager Loading) con `selectinload`
Para endpoints que devuelven estructuras anidadas, es mandatorio aplicar **Eager Loading** mediante el operador `selectinload` de SQLAlchemy:

* `selectinload` ejecuta una segunda consulta optimizada con la cláusula `WHERE id IN (...)` conteniendo todos los identificadores padres obtenidos en la primera consulta.
* Transforma $1 + N$ consultas en exactamente **2 consultas atómicas y eficientes**, independientemente del volumen de datos, resolviendo el problema de raíz antes de que la sesión finalice.

---

## 2. Ejemplos de Código (SQLModel / FastAPI)

### 2.1. Implementación de Relación 1:N (`Team` y `Hero`)

```python
# app/modules/team/models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class Team(SQLModel, table=True):
    __tablename__ = "team"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    # Navegación hacia las entidades hijas (en memoria)
    heroes: List["Hero"] = Relationship(back_populates="team")


# app/modules/hero/models.py
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

class Hero(SQLModel, table=True):
    __tablename__ = "hero"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str

    # Clave Foránea FÍSICA en la base de datos (lado 'muchos')
    # Genera: team_id INTEGER REFERENCES team(id)
    team_id: Optional[int] = Field(default=None, foreign_key="team.id")

    # Navegación hacia la entidad padre (en memoria)
    team: Optional["Team"] = Relationship(back_populates="heroes")
```

---

### 2.2. Implementación de Relación N:N con Tabla Intermedia (`HeroTeamLink`)

```python
# app/modules/hero/models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, Integer, ForeignKey

# 1. Tabla Intermedia / Link Table
# Debe declararse antes de las entidades principales que la referencian en link_model
class HeroTeamLink(SQLModel, table=True):
    __tablename__ = "hero_team_link"

    # Clave primaria compuesta + FKs con eliminación en cascada
    hero_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("hero.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )
    team_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("team.id", ondelete="CASCADE"),
            primary_key=True,
            nullable=False
        )
    )

# 2. Entidad Hero con relación N:N
class Hero(SQLModel, table=True):
    __tablename__ = "hero"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str

    # Relación N:N vinculada mediante link_model
    teams: List["Team"] = Relationship(
        back_populates="heroes",
        link_model=HeroTeamLink
    )


# app/modules/team/models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from app.modules.hero.models import HeroTeamLink

class Team(SQLModel, table=True):
    __tablename__ = "team"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    # Contraparte simétrica de la relación N:N
    heroes: List["Hero"] = Relationship(
        back_populates="teams",
        link_model=HeroTeamLink
    )
```

---

### 2.3. Consulta Optimizada con Eager Loading (`selectinload`)

```python
# app/modules/hero/service.py
from typing import List, Optional
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload
from app.modules.hero.models import Hero

def get_hero_with_team(session: Session, hero_id: int) -> Optional[Hero]:
    """
    Obtiene un héroe individual cargando anticipadamente su equipo.
    Evita DetachedInstanceError al serializar fuera de la sesión.
    """
    statement = (
        select(Hero)
        .where(Hero.id == hero_id)
        .options(selectinload(Hero.team))
    )
    return session.exec(statement).first()

def list_heroes_with_teams(session: Session, skip: int = 0, limit: int = 50) -> List[Hero]:
    """
    Lista héroes aplicando Eager Loading.
    Resuelve el problema N+1 ejecutando exactamente 2 consultas SQL atómicas:
    1) SELECT hero.* FROM hero LIMIT 50 OFFSET 0;
    2) SELECT team.* FROM team WHERE team.id IN (team_ids_encontrados);
    """
    statement = (
        select(Hero)
        .options(selectinload(Hero.team))
        .offset(skip)
        .limit(limit)
    )
    return list(session.exec(statement).all())
```

---

## 3. Buenas Prácticas de Arquitectura Backend

### 3.1. Separación de Esquemas (Pydantic DTOs vs. Modelos Persistentes)
> **Regla de Seguridad y Diseño:** Jamás se deben exponer directamente los modelos de base de datos (`table=True`) en la capa de transporte (endpoints de FastAPI).

Exponer directamente los modelos de base de datos genera filtración involuntaria de campos sensibles (hashes de contraseñas, flags internos), acopla el contrato público de la API al esquema físico y desencadena fallos de serialización circular con el ORM.

Se debe estructurar una jerarquía limpia de esquemas:
* **`HeroBase`:** Campos compartidos de validación (nombre, identidad secreta).
* **`HeroCreate`:** Payload para inserción (incluye `team_id: Optional[int] = None`).
* **`HeroRead`:** Respuesta básica con identificadores y campos propios, sin relaciones complejas anidadas.
* **`HeroReadFull`:** Extiende `HeroRead` incorporando objetos anidados para vistas detalladas.

---

### 3.2. Mitigación de Dependencias Circulares (Circular Imports)
En sistemas modulares donde el módulo `hero` conoce a `team` y el módulo `team` necesita exponer a `hero`, la importación directa de esquemas completos produce bucles de importación cíclica en Python (`ImportError: cannot import name ... from partially initialized module`).

**Patrón de Solución Arquitectónica:**
Cada módulo define y exporta un esquema reducido (*basic schema*) de la entidad externa, rompiendo la cadena de dependencias:

```python
# app/modules/hero/schemas.py
from typing import Optional
from sqlmodel import SQLModel

# Esquema reducido del Team definido localmente para romper el ciclo
class TeamBasicRead(SQLModel):
    id: int
    name: str

class HeroRead(SQLModel):
    id: int
    name: str
    secret_name: str
    team_id: Optional[int] = None

class HeroReadFull(HeroRead):
    team: Optional[TeamBasicRead] = None


# app/modules/team/schemas.py
from typing import List
from sqlmodel import SQLModel

# Esquema reducido del Hero definido localmente para romper el ciclo
class HeroBasicRead(SQLModel):
    id: int
    name: str

class TeamRead(SQLModel):
    id: int
    name: str
    headquarters: str

class TeamReadFull(TeamRead):
    heroes: List[HeroBasicRead] = []
```

---

### 3.3. Validación en la Capa de Servicio antes de Persistir

El motor de base de datos lanzará un error genérico (`IntegrityError`) si una clave foránea apunta a un registro inexistente. Sin embargo, una arquitectura profesional debe interceptar y responder con códigos semánticos claros:

1. **En operaciones de creación (1:N):**
   Verificar manualmente la existencia previa de la entidad padre. Si no existe, elevar inmediatamente una excepción HTTP controlada (`404 Not Found`).

```python
# app/modules/hero/service.py
from fastapi import HTTPException, status
from sqlmodel import Session
from app.modules.hero.models import Hero
from app.modules.hero.schemas import HeroCreate
from app.modules.team.models import Team

def create_hero(session: Session, hero_data: HeroCreate) -> Hero:
    # 1. Validación preventiva de existencia del padre
    if hero_data.team_id is not None:
        team = session.get(Team, hero_data.team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Team with id {hero_data.team_id} does not exist."
            )

    # 2. Instanciación y persistencia
    db_hero = Hero.model_validate(hero_data)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero
```

2. **En operaciones de asociación N:N:**
   * Validar que ambas entidades existan secuencialmente (404 si alguna no se encuentra).
   * Validar que la asociación no exista con anterioridad; en caso afirmativo, abortar con `409 Conflict` para respetar la integridad y evitar duplicados lógicos.

```python
# app/modules/hero/service.py (Gestión de Asociación N:N)
from sqlmodel import Session, select
from fastapi import HTTPException, status
from app.modules.hero.models import Hero, HeroTeamLink
from app.modules.team.models import Team

def associate_hero_with_team(session: Session, hero_id: int, team_id: int) -> Hero:
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hero not found")

    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Team not found")

    # Chequeo de duplicados en la tabla intermedia
    stmt = select(HeroTeamLink).where(
        HeroTeamLink.hero_id == hero_id,
        HeroTeamLink.team_id == team_id
    )
    if session.exec(stmt).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The hero is already a member of this team."
        )

    link = HeroTeamLink(hero_id=hero_id, team_id=team_id)
    session.add(link)
    session.commit()
    session.refresh(hero)
    return hero
```

---

### 3.4. Integridad Referencial en el Motor e Indexación

* **Restricción de Eliminación en Cascada (`ON DELETE CASCADE`):**
  Al eliminar un héroe o un equipo, las filas asociadas en la tabla intermedia quedarían "huérfanas" (fantasmas) si no se depuran. Configurar `ondelete="CASCADE"` en las columnas foráneas de `HeroTeamLink` delega la limpieza al propio motor SQL de manera atómica, rápida y segura.
* **Estrategia de Indexación Física:**
  Búsquedas en la tabla intermedia o consultas filtradas por `team_id` sin índices obligan al motor a ejecutar lecturas secuenciales exhaustivas (**Full Table Scans**). Marcar `index=True` en claves foráneas o crear índices explícitos sobre las columnas de relación asegura búsquedas logarítmicas $O(\log n)$ a escala.

---

# Parte 2: Frontend — Gestión de Estado y Ciclo de Vida con React Hooks

---

## 1. Teoría y Conceptos Fundamentales de React

### 1.1. El Concepto de Estado en Componentes Funcionales

En React, el **estado** representa cualquier información que varía a lo largo del tiempo dentro de un componente y que determina directamente cómo se renderiza la interfaz.

* **Por qué las variables tradicionales de JavaScript no son suficientes:**
  Si se declara una variable local común (`let count = 0`), modificar su valor (`count++`) no genera ninguna notificación al motor de React. El navegador permanece estático y la pantalla no se actualiza.
* **El Ciclo de Reactividad:**
  React conecta el estado al motor de reconciliación. Cuando el estado muta mediante su función modificadora, React programa y ejecuta un **re-render** del componente funcional, calculando la diferencia (*diffing*) con el Virtual DOM y aplicando las mínimas alteraciones necesarias en el DOM real del navegador.

```
┌─────────────────────────────────┐
│     Interacción del Usuario     │ (click, input, submit)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ Disparo de Evento y setState() │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│      Re-render de React         │ (Se vuelve a ejecutar la función)
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│    Actualización del DOM        │ (Virtual DOM reconciliado)
└─────────────────────────────────┘
```

---

### 1.2. El Hook `useState`

`useState` es la función primitiva que permite declarar una variable de estado en componentes funcionales.

```typescript
const [state, setState] = useState(valorInicial);
```

Retorna una tupla inmutable de dos elementos:
1. El valor actual del estado en el render en curso.
2. La función despachadora que programa una actualización del estado y solicita un re-render.

#### Actualizaciones Basadas en el Estado Previo (Functional Updates)
Cuando el nuevo valor del estado depende directamente del valor anterior (por ejemplo contadores, colecciones acumulativas o flags de inversión), **nunca** debe pasarse el valor directo si este puede desfasarse en operaciones encoladas:

```typescript
// ❌ RIESGOSO: En operaciones asíncronas o múltiples llamadas seguidas puede leer un estado obsoleto
setCount(count + 1);

//  RECOMENDADO: Función updater con callback
setCount((prevCount) => prevCount + 1);
```
El patrón `prev => nuevoValor` garantiza que React proporcione la versión más reciente del estado disponible en la cola interna, previniendo condiciones de carrera (*stale state*).

---

### 1.3. El Hook `useEffect` y los Efectos Secundarios

Un **efecto secundario** (*side effect*) es cualquier operación que interactúa con el mundo exterior o trasciende el cálculo puramente matemático de generar JSX:
* Peticiones HTTP a APIs REST.
* Suscripciones a WebSockets o eventos globales del navegador (`window.addEventListener`).
* Modificación manual del título del documento o timers (`setTimeout`, `setInterval`).

#### Orden de Ejecución en el Ciclo de Vida
React renderiza primero el componente y actualiza el DOM para que la interfaz se muestre de forma inmediata al usuario. **Posteriormente** a que el DOM fue pintado, React ejecuta los efectos declarados en `useEffect`.

#### La Mecánica del Array de Dependencias
El segundo argumento de `useEffect` gobierna cuándo debe ejecutarse la función del efecto:

| Sintaxis | Comportamiento | Caso de Uso |
| :--- | :--- | :--- |
| `useEffect(fn)` (Sin array) | Se ejecuta **después de cada render** del componente. | Sincronizaciones continuas de depuración (usar con extrema cautela). |
| `useEffect(fn, [])` (Array vacío) | Se ejecuta **exactamente una vez** tras el montaje inicial (*mount*). | Inicialización, carga de datos inicial de una API (*fetch on mount*). |
| `useEffect(fn, [a, b])` (Con dependencias) | Se ejecuta tras el montaje y **cada vez que cambie el valor o referencia** de `a` o `b`. | Reaccionar a cambios de IDs, parámetros de búsqueda o filtros. |

#### Función de Limpieza (Cleanup Function)
Si la función pasada a `useEffect` retorna otra función, esta última se convierte en la **cleanup function**:

```typescript
useEffect(() => {
  // Lógica del efecto (suscripción / timer / listener)

  return () => {
    // Lógica de limpieza (cleanup)
  };
}, [dependencia]);
```

**Momentos exactos en que se ejecuta el cleanup:**
1. Justo antes de que el efecto vuelva a ejecutarse debido a un cambio en las dependencias.
2. En el instante en que el componente es retirado de la pantalla (**desmontaje / unmount**).

Su propósito es liberar memoria, cancelar peticiones HTTP en vuelo, detener intervalos y desuscribir escuchas para evitar fugas de memoria (*memory leaks*).

---

### 1.4. Flujo de Datos Unidireccional (Unidirectional Data Flow)

En React la información fluye en un único sentido: **de padres a hijos**.

* **Estado Centralizado en el Padre:** El estado vive en el componente contenedor más alto que lo requiera.
* **Descenso mediante Props:** Los componentes hijos reciben datos exclusivamente como atributos de solo lectura (`props`).
* **Notificación Ascendente vía Callbacks:** Si un hijo necesita modificar el estado del padre, lo hace invocando una función callback transmitida por el padre a través de sus props.
* **Separación de Roles:** Permite contar con componentes "tontos" o de presentación (*dumb components*) altamente reutilizables que solo renderizan lo que reciben, aislados del origen del dato.

---

## 2. Ejemplos de Código (React + TypeScript)

### 2.1. Uso Básico de `useState` con Actualización Funcional

```tsx
import React, { useState } from 'react';

export const Counter: React.FC = () => {
  const [count, setCount] = useState<number>(0);

  const increment = () => {
    // Uso del callback funcional para asegurar consistencia ante llamadas concurrentes
    setCount((prev) => prev + 1);
  };

  const decrement = () => {
    setCount((prev) => Math.max(0, prev - 1));
  };

  const reset = () => {
    setCount(0);
  };

  return (
    <div style={{ padding: '1rem', border: '1px solid #ccc', borderRadius: '8px' }}>
      <h3>Contador: {count}</h3>
      <button onClick={decrement}>-1</button>
      <button onClick={reset} style={{ margin: '0 0.5rem' }}>Reiniciar</button>
      <button onClick={increment}>+1</button>
    </div>
  );
};
```

---

### 2.2. Uso de `useEffect` con Petición Asíncrona y Cleanup (`AbortController`)

```tsx
import React, { useState, useEffect } from 'react';

interface Hero {
  id: number;
  name: str;
  secret_name: str;
}

interface HeroDetailProps {
  heroId: number;
}

export const HeroDetail: React.FC<HeroDetailProps> = ({ heroId }) => {
  const [hero, setHero] = useState<Hero | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // Instanciamos el controlador para cancelar la petición en vuelo si cambian las deps o se desmonta
    const abortController = new AbortController();
    const { signal } = abortController;

    setLoading(true);
    setError(null);

    fetch(`https://api.example.com/heroes/${heroId}`, { signal })
      .then((res) => {
        if (!res.ok) {
          throw new Error(`Error HTTP: ${res.status}`);
        }
        return res.json();
      })
      .then((data: Hero) => {
        setHero(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        // Ignoramos el error si fue causado intencionalmente por la cancelación
        if (err.name === 'AbortError') return;
        setError(err.message);
        setLoading(false);
      });

    // Cleanup Function: cancela la petición pendiente si el usuario cambia heroId rápidamente
    return () => {
      abortController.abort();
    };
  }, [heroId]); // Se re-ejecuta cada vez que cambia el prop heroId

  if (loading) return <p>Cargando información del héroe...</p>;
  if (error) return <p style={{ color: 'red' }}>Error: {error}</p>;
  if (!hero) return <p>No se encontró el héroe.</p>;

  return (
    <div>
      <h2>{hero.name}</h2>
      <p>Identidad secreta: {hero.secret_name}</p>
    </div>
  );
};
```

---

### 2.3. Ejemplo Avanzado: Custom Hook Genérico `useForm` con TypeScript

Este Custom Hook abstrae por completo la gestión de formularios dinámicos, eliminando código duplicado y asegurando type-safety estricto.

```tsx
// src/hooks/useForm.ts
import { useState, useCallback, ChangeEvent } from 'react';

export interface UseFormReturn<T> {
  values: T;
  handleChange: (e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => void;
  resetForm: () => void;
  setValues: React.Dispatch<React.SetStateAction<T>>;
}

/**
 * Custom Hook genérico para la centralización y actualización dinámica de formularios.
 * @template T Estructura del objeto de campos del formulario.
 */
export function useForm<T extends Record<string, any>>(initialValues: T): UseFormReturn<T> {
  const [values, setValues] = useState<T>(initialValues);

  // Función dinámica de actualización basada en el atributo name del input
  const handleChange = useCallback((
    e: ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
  ) => {
    const { name, value, type } = e.target;

    setValues((prev) => {
      // Manejo específico para checkboxes o inputs numéricos si fuera necesario
      const parsedValue = type === 'number' ? (value === '' ? '' : Number(value)) : value;

      return {
        ...prev, // Preservación estricta de inmutabilidad (spread)
        [name]: parsedValue, // Sobrescritura dinámica de la clave
      };
    });
  }, []);

  const resetForm = useCallback(() => {
    setValues(initialValues);
  }, [initialValues]);

  return { values, handleChange, resetForm, setValues };
}
```

#### Consumo del Custom Hook en un Componente de Formulario

```tsx
// src/components/HeroForm.tsx
import React from 'react';
import { useForm } from '../hooks/useForm';

interface HeroFormValues {
  name: string;
  secret_name: string;
  team_id: string;
}

export const HeroForm: React.FC = () => {
  const { values, handleChange, resetForm } = useForm<HeroFormValues>({
    name: '',
    secret_name: '',
    team_id: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('Enviando datos al backend:', values);
    // Llamada a la API de FastAPI con el payload unificado
  };

  return (
    <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '0.8rem', maxWidth: '350px' }}>
      <div>
        <label htmlFor="name">Nombre de Héroe:</label>
        <input
          id="name"
          name="name" // Identificador dinámico
          type="text"
          value={values.name}
          onChange={handleChange}
          required
        />
      </div>

      <div>
        <label htmlFor="secret_name">Identidad Secreta:</label>
        <input
          id="secret_name"
          name="secret_name" // Identificador dinámico coincidente con la clave del estado
          type="text"
          value={values.secret_name}
          onChange={handleChange}
          required
        />
      </div>

      <div>
        <label htmlFor="team_id">ID de Equipo:</label>
        <input
          id="team_id"
          name="team_id"
          type="number"
          value={values.team_id}
          onChange={handleChange}
        />
      </div>

      <div style={{ display: 'flex', gap: '0.5rem' }}>
        <button type="submit">Guardar Héroe</button>
        <button type="button" onClick={resetForm}>Limpiar</button>
      </div>
    </form>
  );
};
```

---

## 3. Buenas Prácticas en Frontend

### 3.1. Inmutabilidad Estricta y el Operador Spread (`...prev`)
> **Regla de Oro en React:** Nunca modifiques directamente un objeto o array en el estado.

```typescript
// ❌ ANTIPATRÓN CATASTRÓFICO: Mutación directa
values.name = "Nuevo Nombre";
setValues(values); // React compara la referencia anterior con la nueva: como son idénticas, NO dispara re-render.

//  PATRÓN CORRECTO: Inmutabilidad con nuevo objeto
setValues((prev) => ({
  ...prev,
  name: "Nuevo Nombre"
}));
```

React utiliza comparaciones superficiales (**Shallow Comparison**) de referencias en memoria para determinar si un estado ha cambiado. Al mutar una propiedad interna directamente, la dirección del objeto en memoria no cambia, por lo que React asume que nada ha mutado y cancela la actualización de la pantalla. El uso del operador spread (`...prev`) crea una nueva referencia, forzando a React a detectar la mutación y renderizar la interfaz.

---

### 3.2. Rigor en las Funciones de Limpieza (`cleanup`) en `useEffect`
Omitir la función de limpieza es una de las causas más frecuentes de bugs silenciosos en producción:
* **Memory Leaks:** Suscripciones a eventos globales que siguen vivas consumiendo memoria tras cerrar pantallas.
* **Errores de actualización en componentes desmontados:** Callbacks asíncronos que intentan ejecutar `setState` en componentes que ya no existen en el árbol visual.
* **Condiciones de Carrera (Race Conditions):** Si el usuario cambia rápidamente de elemento (ej. hace clic en el Héroe 1 y de inmediato en el Héroe 2), dos peticiones de red compiten por llegar. Sin cancelación (`abort()`), la respuesta del Héroe 1 podría llegar después que la del Héroe 2 y sobrescribir erróneamente la interfaz.

---

### 3.3. Separación de Responsabilidades: Componentes de Presentación ("Dumb") vs. Lógica en Hooks
* **Presentational / Dumb Components:**
  * No gestionan peticiones a APIs ni contienen lógica de negocio compleja.
  * Solo reciben datos vía `props` y emiten eventos vía callbacks.
  * Son altamente testeables y predecibles.
* **Custom Hooks / Container Components:**
  * Encapsulan toda la lógica de negocio, ciclo de vida, persistencia y comunicación de red.
  * Exponen una API limpia hacia la vista (`values`, `handleChange`, `loading`, `error`).
  * Permiten reutilizar la misma lógica de formularios o fetches en interfaces móviles, de escritorio o diferentes vistas web.

---

### 3.4. Centralización Dinámica de Formularios mediante el Atributo `name`
En lugar de crear 10 estados independientes y 10 manejadores `onChange` para un formulario de 10 campos:
1. Agrupar todos los valores en un único objeto representativo del DTO/modelo.
2. Asignar a cada control HTML (`<input>`, `<select>`, `<textarea>`) un atributo `name` exactamente idéntico al nombre de la clave en el objeto.
3. Utilizar una única función despachadora computada:
   ```typescript
   setValues(prev => ({ ...prev, [e.target.name]: e.target.value }))
   ```
Esto reduce la superficie de código en más de un 70%, simplifica la serialización directa para enviar al backend (JSON payload) y escala de manera instantánea con solo agregar nuevas etiquetas sin tocar la lógica.

---

## Tabla Resumen Comparativa: Conceptos Críticos

| Dimensión | Backend (SQLModel / FastAPI) | Frontend (React / Hooks) |
| :--- | :--- | :--- |
| **Persistencia vs. Estado** | Tablas físicas SQL en disco (`table=True`). | Estado volátil en memoria del navegador (`useState`). |
| **Navegación / Vinculación** | `Relationship()` en Python con `back_populates`. | Flujo unidireccional por `props` y callbacks hacia el padre. |
| **Relaciones Complejas** | Tablas intermedias N:N (`link_model`) con PK compuesta. | Custom Hooks genéricos (`useForm<T>`) con objetos planos. |
| **Optimización de Lecturas** | Eager loading con `selectinload` para erradicar el problema N+1. | Array de dependencias y `AbortController` en `useEffect`. |
| **Integridad y Limpieza** | `ON DELETE CASCADE` e índices físicos en base de datos. | Cleanup functions al desmontar para evitar memory leaks. |
| **Validación de Datos** | Schemas DTO de Pydantic y chequeo 404/409 en capa de servicio. | TypeScript estricto, inputs controlados e inmutabilidad (`...prev`). |
