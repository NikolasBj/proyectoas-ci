"""
Uso: python -m ruta_as_core <archivo.json>

El archivo describe una sección:
{"seccion_id": 1, "actividades": [{"nombre": "...", "obligatoria": true, "estado": "Completada"}]}
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from ruta_as_core.avance import Actividad, calcular_avance


def main(argv: list[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        print("Uso: python -m ruta_as_core <archivo.json>", file=sys.stderr)
        return 2
    try:
        datos = json.loads(Path(args[0]).read_text(encoding="utf-8"))
        actividades = [
            Actividad(
                nombre=a["nombre"],
                obligatoria=bool(a["obligatoria"]),
                estado=a.get("estado"),
            )
            for a in datos["actividades"]
        ]
        resultado = calcular_avance(int(datos["seccion_id"]), actividades)
    except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"Error: archivo de sección inválido ({error})", file=sys.stderr)
        return 1
    print(json.dumps(resultado.to_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
