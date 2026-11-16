import pytest

from ruta_as_core.avance import (
    ESTADOS_COMPLETADOS,
    Actividad,
    ResultadoAvance,
    calcular_avance,
    esta_completada,
)


def obligatoria(estado):
    return Actividad(nombre="obligatoria", obligatoria=True, estado=estado)


def opcional(estado):
    return Actividad(nombre="opcional", obligatoria=False, estado=estado)


@pytest.mark.unit
class TestCalcularAvance:
    def test_ignora_actividades_opcionales(self):
        actividades = [
            obligatoria("Completada"),
            obligatoria("Finalizada"),
            obligatoria("En curso"),
            obligatoria(None),
            opcional("Completada"),
            opcional("Completada"),
            opcional("Completada"),
        ]
        r = calcular_avance(55, actividades)
        assert r == ResultadoAvance(55, 7, 4, 2, 50.0)

    def test_sin_actividades(self):
        assert calcular_avance(1, []) == ResultadoAvance(1, 0, 0, 0, 0.0)

    def test_solo_opcionales_retorna_cero_sin_error(self):
        r = calcular_avance(2, [opcional("Completada"), opcional(None)])
        assert r.total_actividades == 2
        assert r.total_obligatorias == 0
        assert r.avance_porcentaje == 0.0

    def test_todas_completadas_retorna_cien(self):
        r = calcular_avance(3, [obligatoria(e) for e in ESTADOS_COMPLETADOS])
        assert r.avance_porcentaje == 100.0

    def test_redondea_a_dos_decimales(self):
        r = calcular_avance(4, [obligatoria("Completada"), obligatoria(None), obligatoria(None)])
        assert r.avance_porcentaje == 33.33

    def test_acepta_generadores(self):
        r = calcular_avance(5, (obligatoria("Completada") for _ in range(2)))
        assert r.total_obligatorias == 2
        assert r.avance_porcentaje == 100.0

    def test_to_dict(self):
        assert calcular_avance(6, [obligatoria("Completada")]).to_dict() == {
            "seccion_id": 6,
            "total_actividades": 1,
            "total_obligatorias": 1,
            "completadas_obligatorias": 1,
            "avance_porcentaje": 100.0,
        }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("estado", "esperado"),
    [
        ("Completada", True),
        ("Finalizado", True),
        ("Finalizada", True),
        ("En curso", False),
        ("Pendiente", False),
        ("completada", False),
        (None, False),
    ],
)
def test_esta_completada(estado, esperado):
    assert esta_completada(estado) is esperado
