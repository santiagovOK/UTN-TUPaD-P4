# Bloque 9 · Teoría – Los 7 java-ismos: por qué cada hábito era correcto en Java

Transcripción del video **"17 – Los 7 java-ismos: por qué cada hábito era correcto en Java – TEORÍA"** (serie Java → Python, ~7 min), organizada por temas. Fuente: subtítulos automáticos en español del video de YouTube.

---

## Introducción: un video distinto, sin contenido nuevo

Hola a todos y bienvenidos a un nuevo video de la serie de programación orientada a objetos. El video de hoy es **distinto a todos los anteriores** y quiero que lo sepan desde el arranque, ya que **este no trae contenido nuevo**. Nada de lo que van a escuchar hoy es información que no hayan visto ya.

Lo que vamos a hacer en realidad es tomar los ocho bloques que recorrimos hasta ahora y convertirlos en una sola herramienta. Esta va a ser bastante compacta de **siete puntos** que van a poder llevarse a cualquier code review que hagan de acá en adelante, ya sea hoy o en 10 años, y utilizarla si se les facilita el proceso.

Antes de mostrarles la lista completa, voy a hacer una aclaración importante para que la lean correctamente. El orden en que van a aparecer los siete puntos no indica cuál es el error más grave, sino que indica pura y exclusivamente **qué tan seguido se lo van a encontrar en código real**. El primer punto de la lista es con una diferencia enorme respecto de los demás, el más frecuente de los siete.

Ahora sí podemos ver la tabla completa, la pieza central de todo el video. Y se las voy a leer de corrido para que tengan el panorama entero antes de que entremos al detalle de cada una.

| # | El java-ismo (el reflejo de Java) | La corrección en Python | Bloque de origen |
|---|---|---|---|
| 1 | Escribir `get x` y `set x` | Atributo público directo, o `property` si hay lógica real | Bloque 3 |
| 2 | Usar doble guion bajo creyendo que reproduce el `private` | Guion simple (`-`), la convención de Python | Bloque 4 |
| 3 | Heredar de una clase base solo para tener un tipo común | Duck typing puro o `Protocol` | Bloque 7 |
| 4 | Escribir una interfaz vacía solo para hacer `implements` | `Protocol` (solo) | Bloque 7 |
| 5 | Un `__init__` que solo asigna campos uno por uno | `@dataclass` | Bloque 8 |
| 6 | Un `stream` traducido a mano con `for`, `pen` y acumulador | `comprehension` | Bloque 5 |
| 7 | Confiar en que los type hints protegen solos sin correr Mypy | Correr Mypy | Bloque 6 |

---

## Punto 1 – `get x` y `set x` sin lógica (el más común)

En el punto uno tenemos **escribir get x y set x**, el cual se corrige con un atributo público directo o con `property` si hay lógica real de por medio.

Esto lo vieron completo en el bloque tres con el ejemplo de polígono y lado. La corrección, como pueden ver acá, es básicamente un `property` para poder leer. Y si el atributo no necesita ninguna validación ni cálculo especial, ni siquiera hace falta el `setter`, entonces el **atributo público directo** nos alcanza.

```python
# Java – getter y setter sin lógica (reflejo de Java)
class Poligono:
    private int lados;
    public int getLados() { return lados; }
    public void setLados(int l) { lados = l; }

# Python – property con lógica, o atributo público si no la hay
class Poligono:
    _lados: int

    @property
    def lados(self) -> int:
        return self._lados

    @lados.setter
    def lados(self, valor: int) -> None:
        if valor < 3:
            raise ValueError("Un polígono necesita al menos 3 lados")
        self._lados = valor
        # ✅ Solo existe setter si hay validación real
```

---

## Punto 2 – El doble guion bajo no es `private`

En el punto dos tenemos **usar doble guion bajo** creyendo que reproduce el `private` de Java, pero este se corrige con un guion simple que es la convención correcta que utiliza Python.

Esto fue del bloque cuatro en donde vimos los tres niveles de visibilidad. La corrección es bastante simple de enunciar: simplemente utilizamos un guion solo, o sea, un guion simple. Esa es la convención que la comunidad de Python entiende y respeta.

El doble guion se va a reservar para el único caso legítimo que vimos en su momento, que sería **evitar colisiones de nombres entre una superclase y una subclase**.

```python
# ❌ Doble guion bajo: activa name mangling, no privacidad
class Poligono:
    def __init__(self):
        self.__lados = 3

# ✅ Guion simple: la convención que Python entiende como interno
class Poligono:
    def __init__(self):
        self._lados = 3

p = Poligono()
p._lados = 5   # ✅ Se puede leer y escribir desde afuera: es una convención, no un bloqueo
```

---

## Puntos 3 y 4 – Las dos caras del duck typing

Tenemos los puntos tres y cuatro, los cuales vamos a agrupar juntos, porque son literalmente **las dos caras de la misma moneda**, la cual sería el duck typing que vimos completo en el bloque 7.

### Punto 3 – Heredar solo para un tipo común

El punto tres es **herencia que solo existía para darle un tipo común al compilador** sin ningún comportamiento real compartido detrás. Eso se resuelve con el duck typing puro.

### Punto 4 – Una interfaz vacía solo para `implements`

El punto cuatro se trata de una interfaz vacía declarada solo para poder escribir `implements` sin que nadie necesite ese contrato de manera explícita. Eso se resuelve con `Protocol`, pero solamente `Protocol`.

Los dos comparten el mismo diagnóstico de fondo, que sería preguntarse si esa estructura estaba ahí **por el dominio o solo por el compilador**.

> **¿El dominio afirma que estos conceptos son lo mismo, o el compilador exige un tipo común para que compile?**

```python
# Punto 3 – El tipo común sobra: se elimina la herencia
# El compilador ya no la necesita para el polimorfismo.

# Punto 4 – Si el contrato debe documentarse explícitamente, Protocol:
from typing import Protocol

class Dibujable(Protocol):
    def dibujar(self) -> None: ...

# Cualquier clase que tenga 'dibujar' cumple el protocolo sin heredar.
```

---

## Punto 5 – Un `__init__` que solo asigna campos

Ahora podemos pasar al punto cinco, que trata de un `init` que no hace nada más que **asignar campos uno por uno** sin ninguna lógica de validación ni cálculo adicional. Ese patrón es candidato directo a un `dataclass`, tal como lo vieron en el bloque 8 con el ejemplo de **producto y medida**. Ahí comparamos las casi 40 líneas que necesitaba Java para una estructura de tres campos contra las tres líneas que necesitaba Python con un `dataclass` para exactamente lo mismo.

```java
// Java – ~40 líneas de boilerplate
public class Producto {
    private String nombre;
    private double precio;
    private int stock;
    public Producto(String nombre, double precio, int stock) {
        this.nombre = nombre; this.precio = precio; this.stock = stock;
    }
    @Override public boolean equals(Object o) { ... }
    @Override public int hashCode() { ... }
    @Override public String toString() { ... }
}
```

```python
# Python – @dataclass, tres líneas
from dataclasses import dataclass

@dataclass(frozen=True)
class Producto:
    nombre: str
    precio: float
    stock: int
```

---

## Punto 6 – Traducir un `stream` a mano con `for`

Ahora pasemos al punto seis, el cual trata de **traducir un stream de Java a mano** con un `for`, una `pen loop` y un acumulador. Todo esto en lugar de usar la herramienta correcta de Python. Todo esto lo vimos en el bloque 5 y la corrección es casi siempre una `comprehension`.

A veces, como el ejemplo de `cont`, ni siquiera hace falta escribir un loop explícito. La estructura de datos correcta de la biblioteca estándar ya resuelve el problema en una sola línea.

```java
// Java – stream (la herramienta correcta en Java)
lista.stream().filter(f -> f.area() > 10).forEach(f -> total += f.area());

# Python – comprehension, una sola línea
total = sum(f.calcular_area() for f in figuras if f.calcular_area() > 10)
```

---

## Punto 7 – Confiar en los type hints sin correr Mypy

Y por último, el punto siete, que trataba sobre **confiar en que los type hints los protegen solos** sin correr Mypy. Todo esto se vio en el bloque seis. Y quiero remarcar algo que ya dijimos en su momento, porque vale la pena repetirlo acá. **Esta es para mí la trampa más peligrosa de las siete** porque es la única que no produce ningún error visible por sí sola.

El programa corre, el intérprete no se queja y todo parece estar en orden. Y sin Mypy corriendo, nunca se van a enterar de que el hint está mintiendo.

```python
# ❌ El type hint no se verifica en tiempo de ejecución
datos: str = 5  # ¡5 es un int, no un str! El programa corre igual

# ✅ Mypy encuentra la mentira en un segundo
# $ mypy archivo.py
# Error: Incompatible types in assignment (expression has type "int", variable has type "str")
```

---

## Cierre: cada java-ismo era correcto en Java, no ignorancia

Y ahora sí podemos cerrar la parte teórica con la idea que para mí sostiene todo este checklist, y en realidad sostiene a toda la serie completa.

Los siete puntos tienen algo en común: **cada uno de ellos era un hábito correcto en Java y ninguno de los siete nace de la ignorancia.** El estudiante que escribe getters en Python no es que no sepa programación orientada a objetos, es que **sabe demasiado bien otra cosa. Y eso es que sabe Java** y sabe escribir el reflejo que Java le exigía durante años.

> Esa es la diferencia real entre **corregir un error** y **desactivar un reflejo** instalado durante mucho tiempo. Lo primero se soluciona explicando una vez, pero lo segundo lleva práctica, repetición y exactamente el tipo de checklist que acabamos de construir juntos.

Ahora sí ya tienen las siete herramientas concretas, cada una con su bloque de origen y su corrección puntual. En el próximo video vamos a cazarlas a las siete juntas, pero en un solo archivo de código real, que sería el ejercicio integrador de toda la serie. Así que muchas gracias por ver el video y nos vemos ahí.

---

## Notas de transcripción

- Transcripción generada a partir de los **subtítulos automáticos en español** del video.
- Se organizaron los contenidos por tema (los siete java-ismos del checklist, su tabla resumen, su bloque de origen y su corrección puntual) y se conservó **todo el contenido hablado**.
- Se corrigieron errores evidentes del dictado automático (por ejemplo, "coto review" → *code review*, "back typing" y "docing" → *duck typing*, "dataglass" → *dataclass*, "Mypie" → *Mypy*, "pen loop" → *for loop*, "el punto si" → *el punto siete*, "8o" → *8*). El orden de la tabla indica **frecuencia de aparición en el código real**, no gravedad.
- Los fragmentos de código son **reconstrucciones ilustrativas** basadas en lo descrito en voz alta por el narrador; no se copian textualmente de la pantalla.
