import json
from pathlib import Path

import pytest

from ruta_as_core.__main__ import main

EJEMPLO = Path(__file__).resolve().parent.parent / "examples" / "seccion_ejemplo.json"


@pytest.mark.unit
def test_cli_calcula_ejemplo(capsys):
    assert main([str(EJEMPLO)]) == 0
    salida = json.loads(capsys.readouterr().out)
    assert salida["seccion_id"] == 55
    assert salida["total_actividades"] == 5
    assert salida["avance_porcentaje"] == 50.0


@pytest.mark.unit
def test_cli_sin_argumentos(capsys):
    assert main([]) == 2
    assert "Uso" in capsys.readouterr().err


@pytest.mark.unit
def test_cli_archivo_invalido(tmp_path, capsys):
    malo = tmp_path / "malo.json"
    malo.write_text('{"seccion_id": 1}', encoding="utf-8")
    assert main([str(malo)]) == 1
    assert "inválido" in capsys.readouterr().err


@pytest.mark.unit
def test_cli_archivo_inexistente(tmp_path, capsys):
    assert main([str(tmp_path / "no_existe.json")]) == 1
