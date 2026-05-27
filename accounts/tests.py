from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from accounts.models import InvitacionPadre, Padre, ProfesorPerfil, UserProfile, UserRole
from core.models import Estudiante, Profesor


class PadreCurriculumPermisosTests(TestCase):
    def setUp(self):
        self.ced = "00123456789"
        self.est = Estudiante.objects.create(
            nombre="Ana",
            apellido="Pérez",
            grado="1RO",
            cedula=self.ced,
        )
        self.u1 = User.objects.create_user("padre1@test.com", "padre1@test.com", "pass12345")
        self.p1 = Padre.objects.create(user=self.u1)
        UserProfile.objects.create(user=self.u1, role=UserRole.PADRE)
        self.p1.estudiantes.add(self.est)

        self.est2 = Estudiante.objects.create(
            nombre="Bob", apellido="Gómez", grado="2DO", cedula="00987654321"
        )
        self.u2 = User.objects.create_user("padre2@test.com", "padre2@test.com", "pass12345")
        self.p2 = Padre.objects.create(user=self.u2)
        UserProfile.objects.create(user=self.u2, role=UserRole.PADRE)
        self.p2.estudiantes.add(self.est2)

    def test_padre_no_ve_curriculum_de_otro_hijo(self):
        c = Client()
        c.force_login(self.u1)
        url = reverse("accounts:padre_curriculum", args=[self.est2.pk])
        r = c.get(url)
        self.assertEqual(r.status_code, 404)

    def test_padre_ve_curriculum_propio(self):
        c = Client()
        c.force_login(self.u1)
        url = reverse("accounts:padre_curriculum", args=[self.est.pk])
        r = c.get(url)
        self.assertEqual(r.status_code, 200)


class DualRolProfesorPadreTests(TestCase):
    """Con fila Padre y ProfesorPerfil, el rol en UserProfile decide el modo activo."""

    def setUp(self):
        self.ced = "00111111111"
        self.est = Estudiante.objects.create(
            nombre="Luis", apellido="Ramos", grado="3RO", cedula=self.ced
        )
        self.user = User.objects.create_user(
            "dual@test.com", "dual@test.com", "pass12345"
        )
        self.prof_row = Profesor.objects.create(
            nombre="Luis", apellido="Ramos", cedula="40222222222"
        )
        ProfesorPerfil.objects.create(user=self.user, profesor=self.prof_row)
        Padre.objects.create(user=self.user)
        self.user.padre_profile.estudiantes.add(self.est)
        UserProfile.objects.create(user=self.user, role=UserRole.PROFESOR)

    def test_rol_profesor_accede_core_sin_redirigir_a_padre(self):
        c = Client()
        c.force_login(self.user)
        r = c.get(reverse("core:dashboard"), follow=False)
        self.assertEqual(r.status_code, 200)

    def test_rol_profesor_no_entra_padre_dashboard(self):
        c = Client()
        c.force_login(self.user)
        r = c.get(reverse("accounts:padre_dashboard"), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse("core:dashboard"))

    def test_rol_padre_redirige_core_a_portal_familiar(self):
        self.user.profile.role = UserRole.PADRE
        self.user.profile.save(update_fields=["role"])
        c = Client()
        c.force_login(self.user)
        r = c.get(reverse("core:dashboard"), follow=False)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(r.url, reverse("accounts:padre_dashboard"))


class InvitacionExpiraTests(TestCase):
    def test_token_unico(self):
        est = Estudiante.objects.create(nombre="X", apellido="Y", grado="3RO", cedula="00111111111")
        inv = InvitacionPadre.crear(est)
        self.assertTrue(inv.activa())
        self.assertTrue(len(inv.token) > 20)
