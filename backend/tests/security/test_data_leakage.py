import pytest
from rest_framework import status
from django.urls import reverse
from ruta_as.models import Noticia, RepresentanteSocio, SocioComunitario, TipoOrganizacion


@pytest.mark.security
@pytest.mark.django_db
class TestInvisibilidadDatosSensibles:
    """
    Pruebas de seguridad contra Fuga de Información Sensible (OWASP API3: Broken Object Property Level Authorization).
    Asegura que los endpoints públicos y abiertos no expongan atributos confidenciales
    (PII como RUT, teléfonos, correos privados de representantes o direcciones exactas).
    """

    @pytest.fixture(autouse=True)
    def setup_datos_sensibles(self, db):
        self.socio = SocioComunitario.objects.create(
            nombre="Hogar de Adultos Mayores San Alberto",
            tipo_organizacion=TipoOrganizacion.objects.get_or_create(nombre="Fundación")[0],
            rut="76.999.888-5",
            email="contacto.privado@hogarsanalberto.cl",
            telefono="+56987654321",
            direccion="Calle Confidencial 1234, Of. 501",
            sitio_web="https://hogarsanalberto.cl",
            redes_sociales="@hogar_san_alberto",
            descripcion="Organización comunitaria dedicada al cuidado integral de adultos mayores.",
            activo=True,
            provisional=False,
        )
        RepresentanteSocio.objects.create(
            socio=self.socio,
            nombre="Marta Fernández",
            cargo="Directora Ejecutiva",
            email="marta.fernandez@hogarsanalberto.cl",
            telefono="+56999887766",
            principal=True,
        )

        self.noticia = Noticia.objects.create(
            titulo="Inicio de Actividades A+S 2026",
            resumen="Nuevos proyectos colaborativos inician este semestre.",
            enlace_original="https://uautonoma.cl/noticias/as-2026",
            categoria="Actualidad A+S",
        )

    def test_listado_publico_socios_no_expone_datos_sensibles(self, api_client):
        """
        El endpoint público GET /api/socios/ debe entregar información institucional
        pero NUNCA datos personales ni de contacto privado de los representantes.
        """
        url = reverse("socios-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        payload = response.data
        resultados = payload["results"] if isinstance(payload, dict) and "results" in payload else payload

        assert len(resultados) >= 1
        socio_data = next((item for item in resultados if item["id"] == self.socio.id), None)
        assert socio_data is not None

        # Campos que SÍ deben estar presentes en el listado público
        assert "nombre" in socio_data
        assert "tipo_organizacion" in socio_data
        assert "sitio_web" in socio_data
        assert "redes_sociales" in socio_data

        # Campos prohibidos en el endpoint público (PII / Datos Sensibles)
        campos_sensibles_prohibidos = [
            "rut",
            "email",
            "telefono",
            "representante_nombre",
            "representante_cargo",
            "representante_email",
            "representante_telefono",
            "direccion",
        ]

        for campo in campos_sensibles_prohibidos:
            assert campo not in socio_data, (
                f"Vulnerabilidad de fuga de datos: El campo confidencial '{campo}' "
                f"está expuesto en el endpoint público {url}"
            )

    def test_listado_noticias_no_expone_claves_internas_ni_usuarios(self, api_client):
        """
        El endpoint público GET /api/noticias/ debe exponer únicamente campos públicos.
        """
        url = reverse("api_noticias_list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK

        payload = response.data
        items = payload["results"] if isinstance(payload, dict) and "results" in payload else payload
        assert len(items) >= 1

        noticia_data = items[0]
        assert "titulo" in noticia_data
        assert "enlace_original" in noticia_data

        campos_inseguros = ["autor_id", "password", "token", "secret", "user"]
        for campo in campos_inseguros:
            assert campo not in noticia_data, f"El campo '{campo}' no debe exponerse públicamente."
