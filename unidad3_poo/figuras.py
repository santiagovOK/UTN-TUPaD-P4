# Parte 5 - creación de `figuras.py` en función de la resolución de las partes 1 a 4.

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Protocol

from assets.libreria_externa import PlanoCAD # Se importa libreria_externa, pero no se modifica


class Exportable(Protocol):
    """Contrato estructural para duck typing."""
    def exportar(self) -> str: ...


@dataclass(frozen=True)
class Etiqueta:
    texto: str


class Lado:
    def __init__(self, longitud: float, etiqueta: Etiqueta | None = None):
        self.longitud = longitud  # Pasa por el @property.setter para validación
        # Asociación: 0..1 Etiqueta. El lado conoce la etiqueta, pero no la construye.
        self._etiqueta = etiqueta

    @property
    def longitud(self) -> float:
        return self._longitud

    @longitud.setter
    def longitud(self, valor: float) -> None:
        if valor <= 0:
            raise ValueError("La longitud debe ser positiva")
        self._longitud = valor

    @property
    def etiqueta(self) -> Etiqueta | None:
        return self._etiqueta

@dataclass
class Figura:
    nombre: str
    color: str
    _construida: bool = field(init=False, default=True)

    def area(self) -> float:
        return 0.0

class Poligono(Figura, ABC):
    cantidad_creados: int = 0 # El catálogo mutable global fue reemplazado por un contador inmutable (Trampa "A" resuelta)

    def __init__(self, nombre: str, color: str, lados: list[Lado] | None = None, observaciones: list[str] | None = None):
        super().__init__(nombre, color)
        self._lados = list(lados) if lados else []
        self._observaciones = list(observaciones) if observaciones else []
        Poligono.cantidad_creados += 1

    @classmethod
    def desde_medidas(cls, nombre: str, color: str, *medidas: float) -> "Poligono":
        """Constructor alternativo heredado por las subclases."""
        return cls(nombre, color, [Lado(m) for m in medidas])

    @abstractmethod
    def lados_esperados(self) -> int:
        """Cada subclase concreta refina la cantidad exacta."""
        pass
    
    @property
    def lados(self) -> tuple[Lado, ...]:
        # Copia defensiva en el getter
        return tuple(self._lados)

    @property
    def estructura_valida(self) -> bool:
        """La validación real ocurre delegando al método abstracto."""
        esperados = self.lados_esperados()
        if esperados == -1:
            return len(self._lados) >= 3
        return len(self._lados) == esperados

    def perimetro(self) -> float:
        return sum(l.longitud for l in self._lados)

    def exportar(self) -> str:
        """Implementación requerida para satisfacer estructuralmente a Exportable."""
        return f"Exportando polígono {self.nombre} ({self.lados_esperados()} lados)"

    def agregar_observacion(self, texto: str) -> None:
        self._observaciones.append(texto)


class Triangulo(Poligono):
    def lados_esperados(self) -> int:
        return 3

    def area(self) -> float:
        if not self.estructura_valida or len(self.lados) != 3:
            return 0.0
        # Fórmula de Herón
        a, b, c = (l.longitud for l in self.lados)
        s = self.perimetro() / 2
        radicando = s * (s - a) * (s - b) * (s - c)
        return math.sqrt(radicando) if radicando > 0 else 0.0


class Cuadrado(Poligono):
    def lados_esperados(self) -> int:
        return 4

    def area(self) -> float:
        if not self.estructura_valida or len(self.lados) != 4:
            return 0.0
        return self.lados[0].longitud ** 2


class Pentagono(Poligono):
    def lados_esperados(self) -> int:
        return 5


class Hexagono(Poligono):
    def lados_esperados(self) -> int:
        return 6


class Taller:
    def __init__(self):
        # Agregación: 0..* Polígonos. El Taller no los crea.
        self._poligonos: list[Poligono] = []

    def recibir(self, poligono: Poligono) -> None:
        self._poligonos.append(poligono)

    def restaurar(self, poligono: Poligono) -> None:
        # Lógica para restaurar el polígono (stub)
        pass

    def inventario(self) -> tuple[Poligono, ...]:
        # Copia defensiva exigida por la multiplicidad *
        return tuple(self._poligonos)


def exportar_todo(items: list[Exportable]) -> list[str]:
    """Itera sobre cualquier objeto que cumpla el contrato estructural."""
    return [item.exportar() for item in items]
