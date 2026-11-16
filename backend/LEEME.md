# Archivos para el repositorio Backend-Proyecto-A-S

Copiar estos archivos en la raíz del repo del backend respetando las carpetas:

```
.github/workflows/backend-ci.yml          (nuevo)
tests/integration/test_api_actividades.py  (reemplaza al actual)
tests/integration/test_api_seccion_avance.py (reemplaza al actual)
tests/security/test_data_leakage.py        (reemplaza al actual)
```

## Por qué se modifican las 3 pruebas

Las fixtures se habían quedado atrás respecto de los modelos actuales y fallaban al crear datos:

- `PeriodoAcademico.anio` y `tipo` ahora son llaves foráneas: se usa `PeriodoAcademico.obtener_o_crear()`.
- `Seccion` ahora exige `campus` de la misma sede: se crea un `Campus`.
- `SocioComunitario.tipo_organizacion` es un catálogo y los datos del representante viven en `RepresentanteSocio`.
- Los endpoints de avance y de estado de actividades ahora exigen sesión y que la sección sea del docente:
  las pruebas usan el cliente autenticado y asignan el docente a la sección (`SeccionDocente`).

No se cambió ninguna aserción sobre el comportamiento esperado.

## Resultado verificado

Con PostgreSQL + PostGIS, `pytest tests/` termina con **37 pruebas pasadas, 0 fallidas**
(unitarias, integración y seguridad). `manage.py check` y `makemigrations --check` pasan sin cambios.

## Pipeline (`backend-ci.yml`)

1. Levanta un PostGIS efímero (`postgis/postgis:18-3.6`) con credenciales ficticias.
2. Instala las librerías de GeoDjango y WeasyPrint y las dependencias de `requirements.txt` (Python 3.14).
3. `python manage.py check` y `python manage.py makemigrations --check --dry-run`.
4. `pytest tests/` con reporte JUnit y cobertura (quedan como artifact `reportes-backend`).
5. Construye la imagen Docker y la verifica con `manage.py check`.

No usa secretos ni se conecta a Neon, Supabase ni Render.

> Nota: `ruta_as/test_expedientes.py` (fuera de `tests/`) tiene 34 pruebas desactualizadas: llaman al
> endpoint de expedientes sin sesión y reciben 401. No se incluyen en el pipeline; conviene
> corregirlas (autenticar el cliente) o moverlas a `tests/` cuando estén al día.
