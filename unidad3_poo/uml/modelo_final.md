# Modelo Final - Diagrama de Clases

A continuación se detalla el diagrama de clases final del dominio de figuras geométricas, reflejando las decisiones de diseño aplicadas.

## Explicación de Relaciones Estructurales

1. **Herencia (`<|--`):** 
   - `Figura` es la superclase (ABC) de `Poligono`.
   - `Poligono` es la superclase (ABC) de `Triangulo`, `Cuadrado`, `Pentagono` y `Hexagono`. 
   - Esta relación está estrictamente justificada por el dominio: modela un "es-un" absoluto con comportamiento base compartido.

2. **Composición (`*--`):**
   - Un `Poligono` está compuesto por múltiples lados (`Lado`). 
   - **Multiplicidad:** `1` a `3..*`. 
   - La dependencia de vida es fuerte: el polígono exige los lados para construirse y, mediante copia defensiva, controla su existencia; si se destruye el polígono, sus lados se destruyen con él.

3. **Agregación (`o--`):**
   - El `Taller` agrupa polígonos (`Poligono`).
   - **Multiplicidad:** `1` a `0..*`. 
   - El taller los recibe ya construidos desde el exterior. Sus ciclos de vida son independientes.

4. **Asociación (`-->`):**
   - Un `Lado` puede estar asociado a una `Etiqueta`.
   - **Multiplicidad:** `1` a `0..1`. 
   - Es un conocimiento opcional; el lado no requiere de la etiqueta para nacer.

5. **Cumplimiento de Protocolo Estructural (`..|>`):**
   - La clase vacía artificial `PoligonoRegular` fue eliminada al tratarse de un "java-ismo". La necesidad de agrupar objetos heterogéneos bajo un mismo contrato se resolvió con el protocolo estructural `Exportable`.
   - Tanto `Poligono` como `PlanoCAD` (la clase externa) cumplen el contrato de manera implícita mediante *duck typing*, ya que ambas exponen un método `exportar() -> str`. Ninguna hereda nominalmente de `Exportable`.

## Diagrama UML

```mermaid
classDiagram

class Exportable {
    <<Protocol>>
    +exportar() str
}

class Figura {
    <<dataclass>>
    +nombre str
    +color str
    #_construida bool
    +area()* float
}

class Poligono {
    <<abstract>>
    #_lados list~Lado~
    #_observaciones list~str~
    +cantidad_creados$ int
    +lados_esperados()* int
    +perimetro() float
    +area() float
    +agregar_observacion(texto)
    +lados() tuple~Lado~
    +estructura_valida() bool
    +exportar() str
    +desde_medidas(nombre, color, ...medidas)$ Poligono
}

class Lado {
    #_longitud float
    #_etiqueta Etiqueta
    +longitud() float
    +etiqueta() Etiqueta
}

class Etiqueta {
    <<frozen dataclass>>
    +texto str
}

class Taller {
    #_poligonos list~Poligono~
    +recibir(poligono)
    +restaurar(poligono)
    +inventario() tuple~Poligono~
}

class Triangulo {
    +lados_esperados() int
    +area() float
}

class Cuadrado {
    +lados_esperados() int
    +area() float
}

class Pentagono {
    +lados_esperados() int
}

class Hexagono {
    +lados_esperados() int
}

class PlanoCAD {
    <<librería externa>>
    +identificador str
    +escala str
    +exportar() str
}

Figura <|-- Poligono : herencia
Poligono <|-- Triangulo
Poligono <|-- Cuadrado
Poligono <|-- Pentagono
Poligono <|-- Hexagono

Poligono "1" *-- "3..*" Lado : composición
Lado "1" --> "0..1" Etiqueta : asociación
Taller "1" o-- "0..*" Poligono : agregación

Poligono ..|> Exportable : cumple
PlanoCAD ..|> Exportable : cumple sin saberlo
```