# Informe — Trabajo Práctico Integrador (Unidad 3)

## Parte 1 — Diagnóstico de java-ismos

La consigna de la Parte 1 indica que "los siete del checklist están todos acá, más un octavo". Sin embargo, al auditar el archivo `assets/parte1_diagnostico.py`, se evidencia que esto no es estrictamente cierto. A continuación se presentan dos tablas: la **Tabla 1** evalúa los 8 ítems basándose en la checklist teórica y la **Tabla 2** agrupa los errores encontrados que quedaron fuera de esa checklist.

---

### Tabla 1: Los 8 Java-ismos de la consigna (En base a la Checklist)

| # | Java-ismo (según Checklist) | Dónde (clase.método) | Inversión que lo explica | Síntoma observable / Estado real |
|---|---|---|---|---|
| 1 | **Getters/Setters explícitos** | `Figura` y `Lado` | Declaración → Runtime | **Presente:** Obliga al cliente a usar métodos como `f.getNombre()`. En Python se exponen atributos y se usa `@property` si hay lógica. |
| 2 | **Uso de doble guion bajo (`__`)** | N/A | Declaración → Runtime | **No existe en el código (pese a la consigna):** Todas las clases en el archivo usan correctamente el guion simple de convención (`_nombre`, `_color`). |
| 3 | **Herencia para tipo común** | N/A | Herencia → Duck typing | **No existe en el código (pese a la consigna):** La herencia de Triángulo/Cuadrado está justificada por dominio. *Nota: El comentario teórico haría referencia a este java-ismo aplicando a la clase `PoligonoRegular`, pero en realidad esa clase no existe en este archivo.* |
| 4 | **Interfaz vacía para implements** | N/A | Herencia → Duck typing | **No existe en el código (pese a la consigna):** Ninguna clase del código de partida es una interfaz vacía (se ve recién en la Parte 4). |
| 5 | **`__init__` que solo asigna campos** | `Figura` y `Lado` | Declaración → Runtime | **Presente:** Los constructores de `Figura` y `Lado` solo reciben variables y las guardan en atributos, patrón candidato a `@dataclass`. |
| 6 | **Stream manual con for y acumulador**| `Poligono.perimetro` | Declaración → Runtime | **Presente:** Se traduce un pipeline a mano con un `for` y acumulador. En Python se resuelve con una comprehension o `sum()`. |
| 7 | **Type hints engañosos sin mypy** | `Poligono.area` | Compilador → Acuerdo | **Presente:** Retorna `str` pese a decir `-> int`. El intérprete no explota en runtime sin herramientas externas como Mypy. |
| 8 | **Falsa sobrecarga comprobando tipos** | `Triangulo.__init__` | Herencia → Duck typing | *(El 8vo ítem de diseño fuera de lista)* **Presente:** Emular múltiples constructores con ramas `isinstance` y `len()`. Se resuelve con `*args` o `@classmethod`. |

---

### Tabla 2: Errores fuera del checklist (Trampas del manual)

Dado que varios ítems del checklist no estaban presentes, aquí se documentan los otros errores explícitamente marcados en el código, los cuales pertenecen a capítulos teóricos distintos ("Trampas que Java no te enseñó a ver").

| # | Error detectado (Trampa / Traducción) | Dónde (clase.método) | Inversión que lo explica | Síntoma observable |
|---|---|---|---|---|
| A | **Atributo de clase mutable** (Falso static) | `Poligono` (`catalogo=[]`) | Declaración → Runtime | Compartir la lista entre todas las instancias de la clase; mutar en una afecta a todo el ecosistema en silencio. |
| B | **Argumento por defecto mutable** | `Poligono.__init__` | Declaración → Runtime | Instanciar distintos polígonos sin pasar `lados` hace que todos compartan idéntica lista en memoria. |
| C | **Olvido de llamada a constructor base** | `Poligono.__init__` | Compilador → Acuerdo | El atributo `_construida` del padre jamás se inicializa, ya que Python no inyecta implícitamente `super().__init__()`. |
| D | **Alias sin copia defensiva** (Exposición) | `Poligono.__init__` y `.getLados` | Compilador → Acuerdo | Modificar la lista externa devuelta por el getter altera el estado interno del objeto directamente. |

### Tabla de equivalencias
| Elemento en Java | Cómo quedó en tu código Python | ¿Traducción directa o rediseño? | Por qué |
| --- | --- | --- | --- |
| Visibilidad `private` y `getters`/`setters` preventivos | Guion bajo `_atributo` por convención y `@property` solo si hay lógica | Rediseño | En Python no hay modificadores de acceso estrictos, el encapsulamiento es por convención. Solo se justifica ocultar el acceso (vía `@property`) si hay lógica de validación o cálculo. |
| Interfaz vacía (`implements`) para agrupar tipos | Contrato estructural (`typing.Protocol`) | Rediseño | El compilador de Java obliga a heredar para tener polimorfismo. En Python rige el Duck Typing; con `Protocol` no hace falta heredar, basta con cumplir la firma. |
| Atributos estáticos mutables (ej. `List` global) | Atributos de clase inmutables (ej. un `int` como contador) | Rediseño | Java protege referencias estáticas de otra forma. Un atributo de clase mutable en Python corrompe el estado de todas las instancias en silencio (Trampa A). |
| Colecciones fuertemente tipadas (`List<Poligono>`) | Anotación de tipos `list[Poligono]` verificada por Mypy | Traducción directa | El comportamiento en runtime sigue siendo dinámico. Las comprobaciones de tipos se delegan a una herramienta de análisis estático (Mypy) fuera de la ejecución (Javismo #7). |
| Clases DTO inmutables con variables `final` | `@dataclass(frozen=True)` (Ej. `Etiqueta`) | Rediseño | Python provee decoradores nativos que generan automáticamente el boilerplate (como `__init__` o representaciones) y aseguran la inmutabilidad. |
| Asignación directa de colecciones (`this.l = l`) | Copia defensiva (`self._l = list(l)`) | Rediseño | Al no existir protección absoluta de memoria en objetos referenciados, se debe hacer una copia activa para garantizar el encapsulamiento y un ciclo de vida estricto (Composición). |
---

### 2. Correcciones a realizar (Paso a paso)

1. **`Figura`**:
   - Eliminar los métodos preventivos `getNombre` y `getColor` **(Resuelve Javismo #1)**.
   - Modificar el type hint y el valor de retorno en `area()` para que sea correcto: `-> float: return 0.0` **(Resuelve Javismo #7)**.
   - Dado que el `__init__` actual solo se dedica a recibir y asignar variables, se sugiere aplicar el decorador `@dataclass` para eliminar el boilerplate de inicialización **(Resuelve Javismo #5)**.

2. **`Lado`**:
   - Eliminar `getLongitud` y `setLongitud`, reemplazándolos por un `@property def longitud(self):` para lectura y un `@longitud.setter` para inyectar validación estricta (`valor <= 0`) **(Resuelve Javismo #1)**.
   - Usar `self.longitud = longitud` dentro del propio `__init__` para que la validación pase por el setter al construir el objeto **(Complementa Javismo #1)**.
   - Al requerir inyectar lógica de validación estricta en la asignación, se descarta el uso del decorador `@dataclass` y se privilegia la resolución mediante `@property`. **(Resuelve Javismo #5)**

3. **`Poligono`**:
   - Eliminar el atributo de clase estático `catalogo = []` que mutaba el estado global (almacenando referencias a objetos). Reemplazarlo por un contador entero inmutable `cantidad_creados = 0` que se incremente en el constructor para preservar la métrica sin riesgos **(Resuelve Trampa A)**.
   - Reemplazar los defaults de `__init__` que causan memoria compartida: usar `lados=None, observaciones=None` **(Resuelve Trampa B)**. 
   - Añadir la invocación al padre: `super().__init__(nombre, color)` al inicio del init **(Resuelve Trampa C)**.
   - Aplicar copia defensiva en la asignación interna: `self._lados = list(lados) if lados else []` **(Resuelve Trampa D)**.
   - Corregir `perimetro()`: Reemplazar el bucle manual por la función nativa `return sum(l.longitud for l in self._lados)` **(Resuelve Javismo #6)**.
   - Reemplazar `getLados()` por un `@property def lados(self): return tuple(self._lados)` para exponer el estado sin riesgo de mutación **(Resuelve Javismo #1 y Trampa D)**.
   - Arreglar el tipo de retorno en `area() -> float` **(Resuelve Javismo #7)**.

4. **Constructores (Triángulo / Cuadrado)**:
   - Eliminar por completo las condicionales y los chequeos rígidos de tipos manuales (`isinstance`).
   - Implementar el diseño idiomático para constructores alternativos, usando `*args` o explícitamente `@classmethod` **(Resuelve Javismo #8)**.

### 3. Código propuesto para `demo_sintomas.py`

Este script prueba que al menos dos de los java-ismos puros de la **Tabla 1** (`getters/setters` y `type hints engañosos`) causan síntomas graves, permitiendo corromper el estado del programa. Ver código en [demo_sintomas.py](demo_sintomas.py)

### 4. Antes y Después del Getter/Setter con Lógica (Lado)

Prueba irrefutable de que el cliente no cambia una sola línea de código en sus llamadas al migrar a `@property`.

**Antes (Acento de Java):**
```python
# Lado.__init__
self._longitud = longitud

def getLongitud(self):
    return self._longitud

def setLongitud(self, valor):
    if valor <= 0:
        raise ValueError("...")
    self._longitud = valor

# Cliente
l = Lado(10)
l.setLongitud(5)
print(l.getLongitud())
```

**Después (Python Idiomático):**
```python
@property
def longitud(self):
    return self._longitud

@longitud.setter
def longitud(self, valor):
    if valor <= 0:
        raise ValueError("La longitud debe ser positiva")
    self._longitud = valor

# Cliente (la asignación invoca al método de forma natural)
l = Lado(10)
l.longitud = 5       # Pasa por el setter validando la regla
print(l.longitud)    # Pasa por la property
```

*Nota: Con este enfoque idiomático, incluso dentro del constructor `__init__` se debe usar `self.longitud = longitud` (sin guion bajo) para que la validación garantice que los valores corruptos no entren jamás al objeto.*

---

## Parte 2 — Relaciones estructurales

### Pregunta Obligatoria: Diferenciación de relaciones en código

Si bien la sintaxis de asignación es idéntica (`self._atributo = valor`), la diferencia radica en el ciclo de vida y cómo se inyectan las referencias:
1. **Composición (Polígono—Lado)**: Delatada por la exigencia de inicialización y la **copia defensiva** en el constructor (`self._lados = list(lados)`), que apropia la lista y sella un ciclo de vida compartido.
2. **Agregación (Taller—Polígono)**: Delatada por una colección que nace vacía (`self._poligonos = []`) y métodos posteriores (`def recibir()`) que inyectan los polígonos ya creados externamente.
3. **Asociación (Lado—Etiqueta)**: Delatada por la opcionalidad explícita en la firma del constructor (`etiqueta: Etiqueta | None = None`), evidenciando independencia total.
---

## Parte 3 - Herencia justificada por dominio

### 3 y 4. Decisión obligatoria sobre PoligonoRegular - Jerarquías

En la jerarquía de herencia, nos enfrentamos a dos casos distintos:

1. **La jerarquía que se queda (`Figura` -> `Poligono`)**: Esta herencia se justifica plenamente por el dominio (un polígono "es-una" figura) y, además, comparten implementación real (estado como `_nombre` y `_color`).
2. **La jerarquía que se rediseña (`PoligonoRegular`)**: Según el análisis, esta clase existía en el diseño original de Java con el único propósito de proveer un "tipo común" para poder agrupar objetos regulares (como Cuadrado o Triángulo) dentro de una misma lista fuertemente tipada (`List<PoligonoRegular>`). 

Como hemos visto, en Python esta necesidad impuesta por el compilador no existe. Las listas son heterogéneas y el polimorfismo es libre (Duck Typing). Crear una superclase o clase abstracta vacía solo para agrupar elementos es un java-ismo. 

**¿Con qué se reemplaza?**
Si simplemente necesitamos recorrer una lista y ejecutar métodos, no la reemplazamos con nada (Duck Typing). Sin embargo, si necesitamos establecer un contrato explícito para herramientas de tipado estático (como `mypy`), la forma idiomática de reemplazar esta falsa herencia es utilizando un **Contrato Estructural (`typing.Protocol`)**.

*Ejemplo conceptual de reemplazo:*
```python
from typing import Protocol

class PoligonoRegular(Protocol):
    """Reemplaza a la clase base. No requiere que nadie herede de ella."""
    def apotema(self) -> float: ...
```
De esta manera, cualquier polígono que implemente `apotema()` es considerado un `PoligonoRegular` estructuralmente, liberando al dominio de herencias artificiales.

---

## Parte 4 - ABC vs. Protocol

### Pregunta que cierra la unidad

**La elección entre ABC y Protocol la decide siempre el dominio.**

El lenguaje (Python) simplemente nos ofrece ambas herramientas libres de las reglas del compilador, para que elijamos según lo que nos dice el modelo (el UML):

* **Elegimos `ABC`** cuando el dominio afirma un **"es-un"** absoluto y hay **implementación compartida**. Usamos `ABC` para `Poligono` porque en el dominio real todo polígono *es una* figura geométrica con un núcleo de datos compartido (nombre, color).
* **Elegimos `Protocol`** cuando el dominio afirma un **"puede-hacer"** o **"actúa-como"**. Usamos Protocol para `Exportable` porque define una capacidad transversal compartida por objetos que no son familiares directos (un `Poligono` propio y un `PlanoCAD` externo).

En Java elegíamos forzados por lo que el compilador necesitaba para armar una lista. En Python, la sintaxis se relaja para que la elección dependa de la verdadera naturaleza (el diseño) del objeto.

#### Respecto a la advertencia

Las Partes 3 y 4 piden tomar la misma decisión desde dos caminos distintos, mientras que la unidad se cierra cuando ambas se justifican con el mismo criterio. Hasta aquí se demostró que en la Parte 3 borramos `PoligonoRegular` porque su herencia era una trampa sintáctica del compilador Java y conservamos `Figura -> Poligono` porque el dominio lo exigía. Aquí es lo mismo, **la decide el dominio.**

## Cierre

Al transicionar de Java a Python, **el diseño conceptual del dominio (las relaciones de la vida real) se mantuvo intacto**, pero **la manera de implementarlo cambió** al liberarnos de las exigencias del compilador. 

**Lo que se mantuvo idéntico:**
La diferencia conceptual entre composición, agregación y asociación. Si bien en ambos lenguajes estas relaciones se traducen a la misma sintaxis básica de asignación (`this.x = x` o `self.x = x`), la decisión sobre quién administra el ciclo de vida de los objetos (creación y destrucción) y quién es el dueño exclusivo de las referencias sigue respondiendo puramente al modelo de dominio (UML), no al lenguaje.

**Lo que cambió (Rediseño):**
Todo lo que hacemos en Java es obligado por el compilador o por el tipado fuerte:
1. **La protección de datos:** Pasamos de la coerción sintáctica (`private`) al acuerdo entre programadores (`_`) y el uso de `@property` solo bajo demanda funcional (por ejemplo, al hacer una validación).
2. **Las jerarquías artificiales:** Eliminamos clases abstractas e interfaces vacías que solo servían para agrupar objetos bajo un mismo tipo (como `PoligonoRegular`), adoptando la filosofía de *duck typing* y formalizando con contratos estructurales (`Protocol`).
3. **El estado de las referencias:** Constatamos que las variables de clase y los valores por defecto mutables en constructores requieren rediseños activos (uso de inmutables, `None` defaults y copias defensivas) para evitar compartir memoria de forma no intencionada (Trampas A y B).

En resumen, Python requiere programar para el modelo de dominio y no para satisfacer al compilador. El verdadero salto exige **rediseñar en relación a la dinámica de runtime y la responsabilidad del desarrollador.**