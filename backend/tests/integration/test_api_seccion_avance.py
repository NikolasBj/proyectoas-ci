import pytest
from django.urls import reverse
from rest_framework import status
from ruta_as.models import (
    ActividadAS,
    EstadoActividad,
    Seccion,
    Asignatura,
    Carrera,
    Facultad,
    PeriodoAcademico,
    Sede,
    Campus,
    NombrePeriodo,
    TipoPeriodo,
)


@pytest.mark.integration
@pytest.mark.django_db
class TestSeccionAvanceAPI:
    """
    Pruebas de integración para el endpoint GET /api/secciones/<seccion_id>/avance/ (RF-RUT-03).
    Valida:
    - Retorno de códigos 200 OK con cálculo dinámico en PostgreSQL.
    - Serialización exacta del esquema esperado.
    - Exclusión de actividades opcionales en el porcentaje.
    - Retorno 404 Not Found ante secciones inexistentes.
    """

    @pytest.fixture(autouse=True)
    def setup_seccion_con_actividades(self, db):
        facultad = Facultad.objects.create(nombre="Facultad de Ciencias Sociales")
        carrera = Carrera.objects.create(nombre="Trabajo Social", facultad=facultad)
        asignatura = Asignatura.objects.create(codigo="AS-SOC-101", nombre="Taller Social I")
        tipo, _ = TipoPeriodo.objects.get_or_create(codigo="SEMESTRE", defaults={"nombre": "Semestre"})
        NombrePeriodo.objects.get_or_create(tipo=tipo, numero=2, defaults={"nombre": "Semestre 2"})
        periodo, _ = PeriodoAcademico.obtener_o_crear(2026, tipo, 2, nombre="2026-2")
        sede = Sede.objects.create(nombre="Campus San Miguel", codigo="SM")
        campus = Campus.objects.create(sede=sede, nombre=f"{sede.nombre} Central", activo=True, habilitado_docentes=True)

        self.seccion = Seccion.objects.create(
            asignatura=asignatura,
            carrera=carrera,
            periodo_academico=periodo,
            sede=sede,
            campus=campus,
            numero="2",
        )

        self.estado_pendiente, _ = EstadoActividad.objects.get_or_create(nombre="Pendiente")
        self.estado_completada, _ = EstadoActividad.objects.get_or_create(nombre="Completada")

        # 2 Obligatorias: 1 completada, 1 pendiente -> 50%
        ActividadAS.objects.create(
            seccion=self.seccion,
            nombre="Visita a Sede Comunitaria",
            estado=self.estado_completada,
            obligatoria=True,
        )
        ActividadAS.objects.create(
            seccion=self.seccion,
            nombre="Informe de Diagnóstico",
            estado=self.estado_pendiente,
            obligatoria=True,
        )

        # 1 Opcional completada -> no debe alterar el 50%
        ActividadAS.objects.create(
            seccion=self.seccion,
            nombre="Charla Vocacional Comunitaria",
            estado=self.estado_completada,
            obligatoria=False,
        )

    def test_obtener_avance_seccion_calcula_porcentaje_correcto(self, client_autenticado_coordinador):
        """
        Verifica el cálculo de avance: 1 de 2 obligatorias completadas = 50.0%.
        La actividad opcional no altera el porcentaje de avance.
        """
        url = reverse("seccion_avance", kwargs={"seccion_id": self.seccion.id})
        response = client_autenticado_coordinador.get(url)

        assert response.status_code == status.HTTP_200_OK

        payload = response.data
        assert payload["seccion_id"] == self.seccion.id
        assert payload["total_actividades"] == 3
        assert payload["total_obligatorias"] == 2
        assert payload["completadas_obligatorias"] == 1
        assert payload["avance_porcentaje"] == 50.0

    def test_seccion_inexistente_retorna_404(self, client_autenticado_coordinador):
        """Verifica que solicitar una sección inexistente retorne 404 Not Found."""
        url = reverse("seccion_avance", kwargs={"seccion_id": 999999})
        response = client_autenticado_coordinador.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
