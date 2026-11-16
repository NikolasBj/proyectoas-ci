"""Componente mínimo del Proyecto A+S: cálculo del avance de la Ruta A+S."""

from ruta_as_core.avance import (
    ESTADOS_COMPLETADOS,
    Actividad,
    ResultadoAvance,
    calcular_avance,
    calcular_avance_seccion,
    esta_completada,
)

__all__ = [
    "ESTADOS_COMPLETADOS",
    "Actividad",
    "ResultadoAvance",
    "calcular_avance",
    "calcular_avance_seccion",
    "esta_completada",
]
__version__ = "1.0.0"
