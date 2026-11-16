import pytest
from django.urls import reverse
from rest_framework import status
from authentication.models import Docente
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
    SeccionDocente,
    NombrePeriodo,
    TipoPeriodo,
    AuditoriaCambio,
)


@pytest.mark.integration
@pytest.mark.django_db(transaction=True)
class TestActualizarEstadoActividadAPI:
    """
    Pruebas de integración para el endpoint PATCH /api/actividades/<pk>/estado/ (RF-RUT-02).
    Valida:
    - Retorno de códigos de estado HTTP correctos.
    - Persistencia real del cambio en PostgreSQL.
    - Creación de registro de auditoría asociado al usuario autenticado (RNF-AUD-01).
    - Rechazo de transacciones inválidas con status 400 Bad Request.
    """

    @pytest.fixture(autouse=True)
    def setup_entorno_academico(self, db, usuario_docente):
        facultad = Facultad.objects.create(nombre="Facultad de Ingeniería y Administración")
        carrera = Carrera.objects.create(nombre="Ingeniería Civil Informática", facultad=facultad)
        asignatura = Asignatura.objects.create(codigo="AS-INF-2026", nombre="Proyecto Integrador A+S")
        tipo, _ = TipoPeriodo.objects.get_or_create(codigo="SEMESTRE", defaults={"nombre": "Semestre"})
        NombrePeriodo.objects.get_or_create(tipo=tipo, numero=1, defaults={"nombre": "Semestre 1"})
        periodo, _ = PeriodoAcademico.obtener_o_crear(2026, tipo, 1, nombre="2026-1")
        sede = Sede.objects.create(nombre="Campus Providencia", codigo="PROV")
        campus = Campus.objects.create(sede=sede, nombre=f"{sede.nombre} Central", activo=True, habilitado_docentes=True)

        self.seccion = Seccion.objects.create(
            asignatura=asignatura,
            carrera=carrera,
            periodo_academico=periodo,
            sede=sede,
            campus=campus,
            numero="101",
        )

        # El docente solo puede modificar actividades de sus propias secciones.
        SeccionDocente.objects.create(seccion=self.seccion, docente=Docente.objects.get(usuario=usuario_docente))

        self.estado_pendiente, _ = EstadoActividad.objects.get_or_create(
            nombre="Pendiente", defaults={"descripcion": "Actividad por iniciar"}
        )
        self.estado_completada, _ = EstadoActividad.objects.get_or_create(
            nombre="Completada", defaults={"descripcion": "Actividad finalizada"}
        )

        self.actividad = ActividadAS.objects.create(
            seccion=self.seccion,
            nombre="Diagnóstico Inicial de la Comunidad",
            estado=self.estado_pendiente,
            obligatoria=True,
        )

    def test_actualizar_estado_exitoso_persiste_en_postgres_y_registra_auditoria(
        self, client_autenticado_docente, usuario_docente
    ):
        """
        Valida que un Docente autenticado actualice el estado a 'Completada',
        se persista en la base de datos y se registre el cambio en AuditoriaCambio.
        """
        url = reverse("actividad_estado_actualizar", kwargs={"pk": self.actividad.pk})
        payload = {"estado": "Completada"}

        response = client_autenticado_docente.patch(url, data=payload, format="json")

        # 1. Validación de respuesta HTTP
        assert response.status_code == status.HTTP_200_OK
        assert response.data["nuevo_estado"] == "Completada"
        assert response.data["actividad_id"] == self.actividad.id

        # 2. Validación de persistencia en PostgreSQL
        self.actividad.refresh_from_db()
        assert self.actividad.estado == self.estado_completada

        # 3. Validación de auditoría generada (RNF-AUD-01)
        auditoria = AuditoriaCambio.objects.filter(
            entidad="ActividadAS",
            entidad_id=self.actividad.id,
            accion="actualizar_estado_actividad",
        ).first()

        assert auditoria is not None
        assert auditoria.autor == usuario_docente
        assert auditoria.detalle["estado_anterior"] == "Pendiente"
        assert auditoria.detalle["estado_nuevo"] == "Completada"

    def test_actualizar_estado_inexistente_retorna_400_y_no_modifica_bd(
        self, client_autenticado_docente
    ):
        """
        Verifica que enviar un estado no tipificado retorne 400 Bad Request
        y no altere el registro en base de datos.
        """
        url = reverse("actividad_estado_actualizar", kwargs={"pk": self.actividad.pk})
        payload = {"estado": "EstadoInventadoNoValido"}

        response = client_autenticado_docente.patch(url, data=payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "no existe" in str(response.data["detail"]).lower()

        # Asegurar no persistencia
        self.actividad.refresh_from_db()
        assert self.actividad.estado == self.estado_pendiente

    def test_actualizar_actividad_inexistente_retorna_404(
        self, client_autenticado_docente
    ):
        """
        Verifica que consultar un id que no existe en BD retorne 404 Not Found.
        """
        url = reverse("actividad_estado_actualizar", kwargs={"pk": 999999})
        response = client_autenticado_docente.patch(url, data={"estado": "Completada"}, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
