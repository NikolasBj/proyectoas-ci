# Proyecto A+S · Componente mínimo con CI

Repositorio técnico del Proyecto Final de **Arquitectura de Software** (Universidad Autónoma de Chile).
Integrantes: Nicolás Bascuñán, Sofía Díaz y José Moris.

Contiene un **componente funcional mínimo** del sistema Proyecto A+S, sus **pruebas automatizadas**
y un **pipeline de integración continua** en GitHub Actions.

## Componente

`ruta_as_core.avance` calcula el porcentaje de avance de la Ruta A+S de una sección (RF-RUT-03):

> avance = (actividades obligatorias completadas / total de obligatorias) × 100

- Las actividades opcionales cuentan en el total de actividades, pero no en el porcentaje.
- Se consideran completadas las actividades en estado `Completada`, `Finalizado` o `Finalizada`.
- Sin actividades obligatorias el avance es `0.0` (sin división por cero).

Es la misma lógica que `ruta_as.services.ruta_docente.calcular_avance_seccion` del backend Django.
`calcular_avance_seccion` conserva la interfaz del ORM y `calcular_avance` es una versión pura,
sin dependencias externas.

## Estructura

```
src/ruta_as_core/
  avance.py          lógica de negocio (componente mínimo)
  __main__.py        interfaz de línea de comandos
tests/
  test_avance.py             pruebas de la función pura
  test_avance_seccion_orm.py pruebas originales del backend (con mocks del ORM)
  test_cli.py                pruebas de la interfaz de línea de comandos
examples/seccion_ejemplo.json
Dockerfile
.github/workflows/ci.yml
```

## Uso local

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

ruff check .                       # calidad de código
pytest --cov                       # pruebas con cobertura
python -m ruta_as_core examples/seccion_ejemplo.json
```

Con Docker:

```bash
docker build -t ruta-as-core .
docker run --rm ruta-as-core
```

## Pipeline CI (`.github/workflows/ci.yml`)

Se ejecuta en cada push a `main`, en cada pull request y manualmente (*Run workflow*).

| Etapa | Qué hace |
|---|---|
| **Calidad de código** | `ruff check` y `ruff format --check` |
| **Pruebas** | `pytest` en Python 3.12, 3.13 y 3.14, cobertura mínima de 90 %, reporte JUnit |
| **Construcción** | Paquete (wheel y sdist), imagen Docker y prueba de humo de la imagen |

Los reportes (JUnit, cobertura y paquete) quedan como *artifacts* de cada ejecución y el resumen de
pruebas aparece en la pestaña *Summary* del run.
