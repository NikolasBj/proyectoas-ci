"""
Cálculo del porcentaje de avance de la Ruta A+S de una sección (RF-RUT-03).

Fórmula: (actividades obligatorias completadas / total de obligatorias) * 100.
Las actividades opcionales cuentan en el total de actividades, pero no en el porcentaje.

El módulo ofrece dos puntos de entrada:
- ``calcular_avance``: función pura que recibe una lista de ``Actividad``.
- ``calcular_avance_seccion``: misma lógica que el servicio
  ``ruta_as.services.ruta_docente`` del backend Django; recibe un objeto con la
  interfaz del ORM (``seccion.actividades.all()``, ``.filter()``, ``.count()``).
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass

# Estados que se consideran terminados para el cálculo de avance.
ESTADOS_COMPLETADOS: tuple[str, ...] = ("Completada", "Finalizado", "Finalizada")


@dataclass(frozen=True)
class Actividad:
    """Actividad A+S de una sección."""

    nombre: str
    obligatoria: bool
    estado: str | None = None


@dataclass(frozen=True)
class ResultadoAvance:
    """Métricas de avance de una sección."""

    seccion_id: int
    total_actividades: int
    total_obligatorias: int
    completadas_obligatorias: int
    avance_porcentaje: float

    def to_dict(self) -> dict:
        return asdict(self)


def esta_completada(estado: str | None) -> bool:
    """Indica si el estado de una actividad cuenta como completado."""
    return estado in ESTADOS_COMPLETADOS


def _porcentaje(completadas: int, total: int) -> float:
    if total == 0:
        return 0.0
    return round((completadas / total) * 100, 2)


def calcular_avance(seccion_id: int, actividades: Iterable[Actividad]) -> ResultadoAvance:
    """Calcula el avance de una sección a partir de sus actividades."""
    lista = list(actividades)
    obligatorias = [a for a in lista if a.obligatoria]
    completadas = sum(1 for a in obligatorias if esta_completada(a.estado))
    return ResultadoAvance(
        seccion_id=seccion_id,
        total_actividades=len(lista),
        total_obligatorias=len(obligatorias),
        completadas_obligatorias=completadas,
        avance_porcentaje=_porcentaje(completadas, len(obligatorias)),
    )


def calcular_avance_seccion(seccion) -> dict:
    """
    Versión equivalente al servicio del backend (consultas estilo Django ORM).

    ``seccion`` debe exponer ``id`` y ``actividades.all()``, que devuelve un
    conjunto con ``count()`` y ``filter(...)``.
    """
    actividades_seccion = seccion.actividades.all()
    total_actividades = actividades_seccion.count()

    obligatorias = actividades_seccion.filter(obligatoria=True)
    total_obligatorias = obligatorias.count()

    if total_obligatorias == 0:
        return ResultadoAvance(seccion.id, total_actividades, 0, 0, 0.0).to_dict()

    completadas = obligatorias.filter(estado__nombre__in=ESTADOS_COMPLETADOS).count()

    return ResultadoAvance(
        seccion_id=seccion.id,
        total_actividades=total_actividades,
        total_obligatorias=total_obligatorias,
        completadas_obligatorias=completadas,
        avance_porcentaje=_porcentaje(completadas, total_obligatorias),
    ).to_dict()
