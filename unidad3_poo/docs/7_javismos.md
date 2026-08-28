# 8 Checklist de desintoxicación (del PDF pasado en [guia.md](guia.md))

*Los 7 java-ismos a buscar en tu código Python*

Usalo como checklist de code review - tuya y de tus estudiantes. Si venís de Java, estos siete reflejos son los que producen «Java escrito en Python»: código que funciona, pasa los tests, y le grita al lector de dónde viene.

No están en orden de gravedad sino de frecuencia. El primero es, de lejos, el más común.

| # | Pregunta / Reflejo | Solución idiomatica |
|---|---|---|
| **1** | ¿Escribí `get_x()` / `set_x()`? | $\rightarrow$ Atributo público, o `@property` si hay lógica |
| **2** | ¿Puse `__doble_guion` creyendo que es `private`? | $\rightarrow$ `_simple` es la convención |
| **3** | ¿Heredé de una clase base solo para tener un tipo común? | $\rightarrow$ Duck typing o `Protocol` |
| **4** | ¿Definí una interfaz vacía para hacer `implements`? | $\rightarrow$ `Protocol` |
| **5** | ¿Escribí `__init__` que solo asigna campos? | $\rightarrow$ `@dataclass` |
| **6** | ¿Traduje un stream con `for` + `append` + acumulador? | $\rightarrow$ Comprehension |
| **7** | ¿Confío en que los type hints me protegen? | $\rightarrow$ Corré mypy, o no te protegen |