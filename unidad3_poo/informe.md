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
| 3 | **Herencia para tipo común** | N/A | Herencia → Duck typing | **No existe en el código (pese a la consigna):** La herencia de Triángulo/Cuadrado está justificada por dominio. *Nota: El comentario teórico haría referencia a este javismo aplicando a la clase `PoligonoRegular`, pero en realidad esa clase no existe en este archivo.* |
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
   - Eliminar el atributo de clase estático `catalogo = []`, ya que muta el estado global de forma indeseada **(Resuelve Trampa A)**.
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

### 5. Pregunta Obligatoria: Diferenciación de relaciones en código

Si la sintaxis de guardar la referencia es idéntica en los tres casos (`self._atributo = valor`), la diferencia conceptual entre composición, agregación y asociación se ve más claramente en dónde se inyecta el objeto y cómo se gestiona su ciclo de vida:

1. **Composición (Polígono — Lado)**: Existe una dependencia de vida fuerte; si el todo desaparece, las partes también.
   * **Línea que lo delata**: La exigencia de recibir los lados en el constructor para nacer y, sobre todo, la **copia defensiva** al asignarlos (`self._lados = list(lados)`). Al hacer esa copia, el Polígono se apropia de la lista y garantiza que nadie desde afuera pueda alterar sus lados de forma subrepticia, sellando el ciclo de vida compartido. Además, en la instanciación típica (por ejemplo, `Triangulo("...", [Lado(3)])`), los lados se crean anónimamente y no existen fuera del polígono.

2. **Agregación (Taller — Polígono)**: Las partes existen de manera independiente y sobreviven si el contenedor es destruido. 
   * **Línea que lo delata**: El hecho de que la lista nace vacía en el `__init__` (`self._poligonos = []`) y los polígonos se inyectan en un momento posterior de la vida del objeto a través del método `def recibir(self, poligono: Poligono)`.

3. **Asociación (Lado — Etiqueta)**: Es una relación de conocimiento estructural sin dependencia obligatoria. Un objeto conoce opcionalmente a otro.
   * **Línea que lo delata**: La multiplicidad evidenciada en la firma del constructor `def __init__(self, longitud: float, etiqueta: Etiqueta | None = None)`. La posibilidad de ser explícitamente `None` delata que el lado no necesita a la etiqueta para existir.