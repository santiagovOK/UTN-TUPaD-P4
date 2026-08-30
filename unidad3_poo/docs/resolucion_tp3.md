# Informe — Trabajo Práctico Integrador (Unidad 3)

## Parte 1 — Diagnóstico de java-ismos

### Preámbulo: El Checklist de los 7 Java-ismos

A partir de la teoría (`docs/7_javismos.md`), el checklist oficial de desintoxicación se compone de los siguientes 7 puntos:
1. ¿Escribí `get_x()` / `set_x()`?
2. ¿Puse `__doble_guion` creyendo que es `private`?
3. ¿Heredé de una clase base solo para tener un tipo común?
4. ¿Definí una interfaz vacía para hacer `implements`?
5. ¿Escribí `__init__` que solo asigna campos?
6. ¿Traduje un stream con `for` + `append` + acumulador?
7. ¿Confío en que los type hints me protegen?

La consigna de la Parte 1 indica que "los siete del checklist están todos acá, más un octavo". Sin embargo, al auditar el archivo `assets/parte1_diagnostico.py`, se evidencia que esto no es estrictamente cierto. A continuación se presentan dos tablas: la **Tabla 1** evalúa los 8 ítems basándose en la checklist teórica (aclarando con honestidad cuáles no existen realmente en el código de partida) y la **Tabla 2** agrupa los errores reales encontrados que quedaron fuera de esa checklist.

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

### Tabla 2: Errores reales fuera del checklist (Trampas del manual)

Dado que varios ítems del checklist no estaban presentes, aquí se documentan los otros errores explícitamente marcados por el profesor en el código, los cuales pertenecen a capítulos teóricos distintos ("Trampas que Java no te enseñó a ver").

| # | Error detectado (Trampa / Traducción) | Dónde (clase.método) | Inversión que lo explica | Síntoma observable |
|---|---|---|---|---|
| A | **Atributo de clase mutable** (Falso static) | `Poligono` (`catalogo=[]`) | Declaración → Runtime | Compartir la lista entre todas las instancias de la clase; mutar en una afecta a todo el ecosistema en silencio. |
| B | **Argumento por defecto mutable** | `Poligono.__init__` | Declaración → Runtime | Instanciar distintos polígonos sin pasar `lados` hace que todos compartan idéntica lista en memoria. |
| C | **Olvido de llamada a constructor base** | `Poligono.__init__` | Compilador → Acuerdo | El atributo `_construida` del padre jamás se inicializa, ya que Python no inyecta implícitamente `super().__init__()`. |
| D | **Alias sin copia defensiva** (Exposición) | `Poligono.__init__` y `.getLados` | Compilador → Acuerdo | Modificar la lista externa devuelta por el getter altera el estado interno del objeto directamente. |

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

Este script prueba que al menos dos de los java-ismos puros de la **Tabla 1** (`getters/setters` y `type hints engañosos`) causan síntomas graves o permiten corromper el estado del programa.

```python
from assets.parte1_diagnostico import Poligono, Lado

def demo_getter_setter_bypass():
    print("--- Demostrando Javismo #1: Getters/Setters (Bypass de validación) ---")
    # Al depender de un setter estilo Java para validar, es común que el __init__ 
    # asigne directamente a la variable "privada" (_longitud), evadiendo la regla.
    l_invalido = Lado(-10)
    print(f"Lado instanciado con longitud: {l_invalido.getLongitud()}")
    print("El lado se creó con longitud negativa. La validación fue evadida.\n")

def demo_type_hint_enganioso():
    print("--- Demostrando Javismo #7: Type hints engañosos ---")
    p = Poligono("P", "verde")
    resultado = p.area()
    
    print(f"El método area() indica en su firma que devuelve un 'int'.")
    print(f"Valor real devuelto: '{resultado}' (Tipo real: {type(resultado).__name__})")
    print("Intentando sumar 10 al área confiando ciegamente en el type hint...")
    
    try:
        total = resultado + 10
    except TypeError as e:
        print("Atrapado TypeError en runtime:", e)

if __name__ == "__main__":
    demo_getter_setter_bypass()
    demo_type_hint_enganioso()
```

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

Creación de clases nuevas, que luego van a ir en `figuras.py`

### 1. Clase Taller (Agregación)

La clase `Taller` modela una relación de **agregación** con `Poligono` (representada por el rombo vacío `o--` en el diagrama UML). Esta relación se evidencia en que el Taller no controla el ciclo de vida de los polígonos ni los instancia en su interior; por el contrario, los recibe ya construidos desde el exterior a través del método `recibir(poligono)`.

**Código propuesto:**
```python
class Taller:
    def __init__(self):
        # Agregación: 0..* Polígonos. El Taller no los crea.
        self._poligonos: list[Poligono] = []

    def recibir(self, poligono: Poligono) -> None:
        self._poligonos.append(poligono)

    def restaurar(self, poligono: Poligono) -> None:
        # Lógica para restaurar el polígono
        pass

    def inventario(self) -> tuple[Poligono, ...]:
        # Copia defensiva exigida por la multiplicidad *
        return tuple(self._poligonos)
```

### 2. Clase Etiqueta (Asociación)

La clase `Etiqueta` se implementa como un objeto de datos inmutable utilizando el decorador `@dataclass(frozen=True)`. Esta es la solución idiomática ideal en Python para clases cuyo único propósito es albergar datos sin comportamiento adicional, resolviendo de forma limpia el Javismo #5.

A su vez, modela una relación de **asociación** opcional `0..1` con la clase `Lado`. La asociación se distingue porque ambas entidades tienen ciclos de vida independientes (borrar el Lado no necesariamente destruye la Etiqueta, y la Etiqueta se construye por separado). En el código, esto se evidencia al inyectar opcionalmente una instancia de `Etiqueta` en el constructor del `Lado`.

**Código propuesto:**
```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Etiqueta:
    texto: str

# --- Actualización en Lado para reflejar la Asociación ---

class Lado:
    def __init__(self, longitud: float, etiqueta: Etiqueta | None = None):
        self.longitud = longitud  # Pasa por el @property.setter para validación
        
        # Asociación: 0..1 Etiqueta. El lado conoce la etiqueta, pero no la construye.
        self._etiqueta = etiqueta
        
    @property
    def etiqueta(self) -> Etiqueta | None:
        return self._etiqueta
```

### 3. Implementación en constructores y copias defensivas

Tal como se pide en el ítem 3 y en la regla de copias defensivas, las decisiones de diseño ya se dejaron implementadas explícitamente en los bloques de código de los ítems 1 y 2 de arriba:
- La **agregación** del Taller (multiplicidad `0..*`) quedó plasmada en su `__init__`.
- La **asociación** del Lado con la Etiqueta (multiplicidad `0..1`) quedó expuesta explícitamente en la inyección opcional del `__init__` de `Lado` (`Etiqueta | None`).

### 4. Copias defensivas

- Las **copias defensivas** se evidencian en los métodos expuestos hacia el cliente que retornan multiplicidades, obligándolos a devolver copias o tuplas (`tuple(self._poligonos)`).

### 5. Pregunta Obligatoria: Diferenciación de relaciones en código

Si la sintaxis de guardar la referencia es idéntica en los tres casos (`self._atributo = valor`), la diferencia conceptual entre composición, agregación y asociación se ve más claramente en dónde se inyecta el objeto y cómo se gestiona su ciclo de vida:

1. **Composición (Polígono — Lado)**: Existe una dependencia de vida fuerte; si el todo desaparece, las partes también.
   * **Línea que lo delata**: La exigencia de recibir los lados en el constructor para nacer y, sobre todo, la **copia defensiva** al asignarlos (`self._lados = list(lados)`). Al hacer esa copia, el Polígono se apropia de la lista y garantiza que nadie desde afuera pueda alterar sus lados de forma subrepticia, sellando el ciclo de vida compartido. Además, en la instanciación típica (por ejemplo, `Triangulo("...", [Lado(3)])`), los lados se crean anónimamente y no existen fuera del polígono.

2. **Agregación (Taller — Polígono)**: Las partes existen de manera independiente y sobreviven si el contenedor es destruido. 
   * **Línea que lo delata**: El hecho de que la lista nace vacía en el `__init__` (`self._poligonos = []`) y los polígonos se inyectan en un momento posterior de la vida del objeto a través del método `def recibir(self, poligono: Poligono)`.

3. **Asociación (Lado — Etiqueta)**: Es una relación de conocimiento estructural sin dependencia obligatoria. Un objeto conoce opcionalmente a otro.
   * **Línea que lo delata**: La multiplicidad evidenciada en la firma del constructor `def __init__(self, longitud: float, etiqueta: Etiqueta | None = None)`. La posibilidad de ser explícitamente `None` delata que el lado no necesita a la etiqueta para existir.


## Parte 3 - Herencia justificada por dominio

### 1. Clase Polígono (Clase Abstracta)

Para justificar la herencia por dominio y lograr que una instancia incompleta explote al construir (falla temprana), la clase `Poligono` debe heredar de `ABC` y marcar `lados_esperados` como `@abstractmethod`. Esto formaliza el contrato de que todo polígono debe indicar su cantidad de lados esperados sin proveer una implementación por defecto.

Esto también irá luego en `figuras.py`

**Código propuesto:**
```python
from abc import ABC, abstractmethod

class Poligono(Figura, ABC):
    def __init__(self, nombre: str, color: str, lados: list[Lado] | None = None, observaciones: list[str] | None = None):
        super().__init__(nombre, color)
        self._lados = list(lados) if lados else []
        self._observaciones = list(observaciones) if observaciones else []

    @abstractmethod
    def lados_esperados(self) -> int:
        """Cada subclase concreta refina la cantidad exacta."""
        pass
    
```

### 2. Subclases concretas: Pentágono, Hexágono, Triángulo y Cuadrado

Al transformar `Poligono` en un ABC, las subclases se ven forzadas por contrato a implementar `lados_esperados()`. Se agregan `Pentagono` y `Hexagono`, y se refactorizan `Triangulo` y `Cuadrado` para eliminar el java-ismo de sobrecarga falsa.

La validación estructural se puede delegar al padre (`Poligono`) mediante una propiedad que aprovecha el polimorfismo llamando a `self.lados_esperados()`, asegurando que la lista de lados cumpla la restricción del dominio. Además, centralizamos un constructor alternativo `desde_medidas` con `@classmethod` en la clase base. Al usar `cls`, las subclases lo heredan de forma transparente y devuelven el tipo correcto (ej. un `Triangulo`), evitando duplicar la lógica de inicialización o hacer la falsa sobrecarga vista en Java.

**Código propuesto:**
```python
class Poligono(Figura, ABC):
    def __init__(self, nombre: str, color: str, lados: list[Lado] | None = None, observaciones: list[str] | None = None):
        super().__init__(nombre, color)
        self._lados = list(lados) if lados else []
        self._observaciones = list(observaciones) if observaciones else []

    @classmethod
    def desde_medidas(cls, nombre: str, color: str, *medidas: float) -> "Poligono":
        """Constructor alternativo heredado por las subclases (por ejemplo, Triangulo.desde_medidas(...))."""
        return cls(nombre, color, [Lado(m) for m in medidas])

    @abstractmethod
    def lados_esperados(self) -> int:
        """Cada subclase concreta refina la cantidad exacta."""
        pass
    
    @property
    def estructura_valida(self) -> bool:
        """La validación real ocurre delegando al método abstracto."""
        esperados = self.lados_esperados()
        if esperados == -1:
            return len(self._lados) >= 3
        return len(self._lados) == esperados


# Una vez definida la clase abstracta, lo único que varía es lados_esperados para cada figura.

class Triangulo(Poligono):
    def lados_esperados(self) -> int:
        return 3

class Cuadrado(Poligono):
    def lados_esperados(self) -> int:
        return 4

class Pentagono(Poligono):
    def lados_esperados(self) -> int:
        return 5

class Hexagono(Poligono):
    def lados_esperados(self) -> int:
        return 6

```
### 3 y 4. Decisión sobre PoligonoRegular - Jerarquías

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

## Parte 4 — ABC vs. Protocol

### 1. Implementación del contrato Exportable (Protocol)

Para asegurar que tanto nuestras clases de dominio (`Poligono`) como las de una librería externa inmodificable (`PlanoCAD`) puedan ser tratadas bajo un mismo tipo sin forzarlas a heredar de una clase base común, utilizamos un **Contrato Estructural** mediante `typing.Protocol`. 

Esto formaliza el *Duck Typing*: si un objeto tiene el método `exportar() -> str`, es `Exportable`, sin importar quién es su clase padre ni si conoce este contrato.

### 2. Función exportar_todo

Aprovechando el protocolo definido, escribimos una función que recibe una lista tipada con `Exportable`. Gracias al tipado estructural, esta función acepta sin problemas tanto instancias de nuestras clases (por ejemplo, `Triangulo`) como de clases externas (`PlanoCAD`), procesándolas exitosamente en *runtime* (polimorfismo / duck typing).

**Código propuesto:**
```python
def exportar_todo(items: list[Exportable]) -> list[str]:
    """Itera sobre cualquier objeto que cumpla el contrato estructural."""
    return [item.exportar() for item in items]
```

### 3. Por qué una ABC no serviría para PlanoCAD

Si `Exportable` hubiese sido definida como una clase abstracta (`abc.ABC`), el contrato exigiría **tipado nominal** (herencia explícita: `class PlanoCAD(Exportable):`). 

Dado que `PlanoCAD` proviene de una librería de terceros (`libreria_externa.py`) cuyo código fuente no podemos ni debemos modificar, nos sería imposible forzar esa herencia. Pesea a que`PlanoCAD` ya implementa el método `exportar() -> str`, un analizador estático lo rechazaría por no ser "hijo" directo de la ABC. 

Al usar `Protocol`, confiamos en el **tipado estructural**: si el objeto sabe exportar, nos sirve, sin importar quiénes sean sus ancestros.

### 4. Actualización de Poligono para cumplir el contrato

Para que `Poligono` cumpla el contrato, simplemente debe implementar el método `exportar() -> str`. Dado que `Exportable` es un `Protocol`, **no** modificamos la declaración de la clase para que herede de él (no hacemos `class Poligono(Figura, ABC, Exportable):`). Al añadir el método con la firma correcta, la clase ya cumple el contrato automáticamente.

**Código propuesto (fragmento a agregar en Poligono):**
```python
    def exportar(self) -> str:
        """Implementación requerida para satisfacer estructuralmente a Exportable. `exportar` es un método propio de Polígono"""
        return f"Exportando polígono {self._nombre} ({self.nro_lados} lados)"
```

### 5. Pregunta que cierra la unidad

**La elección entre ABC y Protocol la decide siempre el dominio.**

El lenguaje (Python) simplemente nos ofrece ambas herramientas libres de las reglas del compilador, para que elijamos según lo que nos dice el modelo (el UML):

* **Elegimos `ABC`** cuando el dominio afirma un **"es-un"** absoluto y hay **implementación compartida**. Usamos `ABC` para `Poligono` porque en el dominio real todo polígono *es una* figura geométrica con un núcleo de datos compartido (nombre, color).
* **Elegimos `Protocol`** cuando el dominio afirma un **"puede-hacer"** o **"actúa-como"**. Usamos Protocol para `Exportable` porque define una capacidad transversal compartida por objetos que no son familiares directos (un `Poligono` propio y un `PlanoCAD` externo).

En Java elegíamos forzados por lo que el compilador necesitaba para armar una lista. En Python, la sintaxis se relaja para que la elección dependa de la verdadera naturaleza (el diseño) del objeto.

#### Respecto a la advertencia

Las Partes 3 y 4 piden tomar la misma decisión desde dos caminos distintos, mientras que la unidad se cierra cuando ambas se justifican con el mismo criterio. Hasta aquí se demostró que en la Parte 3 borramos `PoligonoRegular` porque su herencia era una trampa sintáctica del compilador Java y conservamos `Figura -> Poligono` porque el dominio lo exigía. Aquí es lo mismo, **la decide el dominio.**


