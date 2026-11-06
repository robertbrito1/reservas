from datetime import date, time

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from .models import Reserva


class ReservasTests(TestCase):
    def setUp(self):
        self.hoy = date.today().isoformat()
        self.reserva = Reserva.objects.create(
            nombre="Ana", apellido="López", telefono="600111222",
            fecha=date.today(), hora=time(14, 0), mesa=101, turno="DIA", personas=2,
        )
        self.empleado = User.objects.create_user("empleado", password="clave-segura-123")

    # --- Vista pública ---

    def test_vista_cliente_no_muestra_datos_de_otros_clientes(self):
        respuesta = self.client.get(f"/cliente/?fecha={self.hoy}&turno=DIA")
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotContains(respuesta, "600111222")
        self.assertNotContains(respuesta, "López")

    def test_cliente_puede_reservar_y_vuelve_a_la_vista_publica(self):
        respuesta = self.client.post("/guardar-reserva/", {
            "mesa": "102", "nombre": "Luis", "apellido": "Pérez", "telefono": "600333444",
            "fecha": self.hoy, "hora": "21:00", "turno": "NOCHE", "personas": 2,
        })
        self.assertEqual(Reserva.objects.filter(mesa=102).count(), 1)
        self.assertTrue(respuesta.url.startswith("/cliente/"))

    def test_reserva_de_grupo_crea_una_reserva_por_mesa(self):
        self.client.post("/guardar-reserva/", {
            "mesa": "3,4,5", "nombre": "Grupo", "apellido": "Cena", "telefono": "600",
            "fecha": self.hoy, "hora": "21:00", "turno": "NOCHE", "personas": 6,
        })
        self.assertEqual(Reserva.objects.filter(nombre="Grupo").count(), 3)

    # --- Vistas internas: requieren login ---

    def test_vistas_internas_redirigen_al_login(self):
        for url in ["/", "/terraza/", "/exportar-pdf/"]:
            respuesta = self.client.get(url)
            self.assertEqual(respuesta.status_code, 302, url)
            self.assertIn("/accounts/login/", respuesta.url)

    def test_eliminar_sin_login_no_borra(self):
        self.client.post(f"/eliminar-reserva/{self.reserva.id}/")
        self.assertTrue(Reserva.objects.filter(id=self.reserva.id).exists())

    def test_eliminar_con_get_no_esta_permitido(self):
        self.client.login(username="empleado", password="clave-segura-123")
        respuesta = self.client.get(f"/eliminar-reserva/{self.reserva.id}/")
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Reserva.objects.filter(id=self.reserva.id).exists())

    def test_empleado_puede_ver_editar_y_eliminar(self):
        self.client.login(username="empleado", password="clave-segura-123")

        respuesta = self.client.get(f"/?fecha={self.hoy}&turno=DIA")
        self.assertContains(respuesta, "600111222")

        self.client.post(f"/editar-reserva/{self.reserva.id}/", {
            "nombre": "Ana", "apellido": "López", "telefono": "699999999",
            "personas": 4, "hora": "15:00", "comentarios": "",
        })
        self.reserva.refresh_from_db()
        self.assertEqual(self.reserva.telefono, "699999999")

        self.client.post(f"/eliminar-reserva/{self.reserva.id}/")
        self.assertFalse(Reserva.objects.filter(id=self.reserva.id).exists())

    def test_exportar_pdf(self):
        self.client.login(username="empleado", password="clave-segura-123")
        respuesta = self.client.get(f"/exportar-pdf/?fecha={self.hoy}&turno=DIA")
        self.assertEqual(respuesta["Content-Type"], "application/pdf")
        self.assertTrue(respuesta.content.startswith(b"%PDF"))

    # --- Comandos de gestión ---

    def test_create_admin_sin_contrasena_no_crea_usuario(self):
        call_command("create_admin")
        self.assertFalse(User.objects.filter(username="admin").exists())

    def test_usuario_demo_no_es_administrador(self):
        call_command("create_demo_user")
        demo = User.objects.get(username="demo")
        self.assertFalse(demo.is_staff)
        self.assertFalse(demo.is_superuser)
        self.assertTrue(self.client.login(username="demo", password="demo-reservas"))
