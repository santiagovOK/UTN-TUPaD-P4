# Parte 5 - `fix_parte1_diagnostico.py` — El dominio Figura / Polígono / Lado, funcionando (corregido).

# Se resolvieron los 8 javismos y trampas correspondientes a la Parte 1.

from dataclasses import dataclass, field


@dataclass
class Figura:
    nombre: str
    color: str
    _construida: bool = field(init=False, default=True)

    def area(self) -> float:
        return 0.0


class Lado:
    def __init__(self, longitud: float):
        self.longitud = longitud  # Pasa por el @property.setter para validación

    @property
    def longitud(self) -> float:
        return self._longitud

    @longitud.setter
    def longitud(self, valor: float):
        if valor <= 0:
            raise ValueError("La longitud debe ser positiva")
        self._longitud = valor


class Poligono(Figura):
    cantidad_creados: int = 0 # El catálogo mutable global fue reemplazado por un contador inmutable (Trampa "A" resuelta)

    def __init__(self, nombre: str, color: str, lados: list[Lado] | None = None, observaciones: list[str] | None = None):
        super().__init__(nombre, color)
        self._lados = list(lados) if lados else []
        self._observaciones = list(observaciones) if observaciones else []
        Poligono.cantidad_creados += 1

    def lados_esperados(self) -> int:
        return 0

    def perimetro(self) -> float:
        return sum(l.longitud for l in self._lados)

    def area(self) -> float:
        return 0.0

    def agregar_observacion(self, texto: str):
        self._observaciones.append(texto)

    @property
    def lados(self) -> tuple[Lado, ...]:
        return tuple(self._lados)


class Triangulo(Poligono):
    def __init__(self, nombre: str, color: str, lados: list[Lado]):
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 3


class Cuadrado(Poligono):
    def __init__(self, nombre: str, color: str, lados: list[Lado]):
        super().__init__(nombre, color, lados)

    def lados_esperados(self) -> int:
        return 4


if __name__ == "__main__":
    activo = True
    if activo:
        t = Triangulo("Triángulo", "rojo", [Lado(3), Lado(4), Lado(5)])
        c = Cuadrado("Cuadrado", "azul", [Lado(2), Lado(2), Lado(2), Lado(2)])
        print(f"Perímetro del triángulo: {t.perimetro()}")
        print(f"Perímetro del cuadrado: {c.perimetro()}")
        t.agregar_observacion("revisar el vértice A")
        # El catálogo mutable global fue reemplazado por un contador inmutable (Trampa "A" resuelta)
        print(f"Figuras creadas en total: {Poligono.cantidad_creados}")
        print(f"Nombre (via atributo): {t.nombre}")
