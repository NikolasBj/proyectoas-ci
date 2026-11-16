"""
Pruebas originales del backend (tests/unit/test_calculo_avance.py) sobre la
versión con interfaz estilo Django ORM.
"""

from unittest.mock import MagicMock

import pytest

from ruta_as_core.avance import ESTADOS_COMPLETADOS, calcular_avance_seccion


@pytest.mark.unit
class TestCalculoAvanceRutaDocente:
    def test_calculo_avance_ignora_actividades_opcionales(self):
        seccion_mock = MagicMock()
        seccion_mock.id = 55

        obligatorias_mock = MagicMock()
        obligatorias_mock.count.return_value = 4
        obligatorias_mock.filter.return_value.count.return_value = 2

        actividades_mock = MagicMock()
        actividades_mock.count.return_value = 7
        actividades_mock.filter.side_effect = lambda obligatoria: (
            obligatorias_mock if obligatoria else MagicMock()
        )
        seccion_mock.actividades.all.return_value = actividades_mock

        resultado = calcular_avance_seccion(seccion_mock)

        assert resultado == {
            "seccion_id": 55,
            "total_actividades": 7,
            "total_obligatorias": 4,
            "completadas_obligatorias": 2,
            "avance_porcentaje": 50.0,
        }
        obligatorias_mock.filter.assert_called_once_with(estado__nombre__in=ESTADOS_COMPLETADOS)

    def test_seccion_sin_actividades_obligatorias_retorna_cero_sin_error(self):
        seccion_mock = MagicMock()
        seccion_mock.id = 56

        actividades_mock = MagicMock()
        actividades_mock.count.return_value = 2
        actividades_mock.filter.return_value.count.return_value = 0
        seccion_mock.actividades.all.return_value = actividades_mock

        resultado = calcular_avance_seccion(seccion_mock)

        assert resultado["seccion_id"] == 56
        assert resultado["total_obligatorias"] == 0
        assert resultado["completadas_obligatorias"] == 0
        assert resultado["avance_porcentaje"] == 0.0

    def test_seccion_con_todas_obligatorias_completadas_retorna_cien(self):
        seccion_mock = MagicMock()
        seccion_mock.id = 57

        obligatorias_mock = MagicMock()
        obligatorias_mock.count.return_value = 5
        obligatorias_mock.filter.return_value.count.return_value = 5

        actividades_mock = MagicMock()
        actividades_mock.count.return_value = 5
        actividades_mock.filter.return_value = obligatorias_mock
        seccion_mock.actividades.all.return_value = actividades_mock

        resultado = calcular_avance_seccion(seccion_mock)

        assert resultado["total_obligatorias"] == 5
        assert resultado["completadas_obligatorias"] == 5
        assert resultado["avance_porcentaje"] == 100.0
