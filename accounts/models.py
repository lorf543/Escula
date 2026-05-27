import secrets
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import Estudiante, Profesor


class UserRole(models.TextChoices):
    PROFESOR = "PROFESOR", "Profesor"
    PADRE = "PADRE", "Padre / Tutor"
    ESTUDIANTE = "ESTUDIANTE", "Estudiante"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    role = models.CharField(max_length=20, choices=UserRole.choices, default=UserRole.PADRE)

    class Meta:
        verbose_name = "perfil de usuario"
        verbose_name_plural = "perfiles de usuario"

    def __str__(self):
        return f"{self.user} ({self.get_role_display()})"


class Padre(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="padre_profile",
    )
    estudiantes = models.ManyToManyField(
        Estudiante,
        related_name="padres",
        blank=True,
    )

    class Meta:
        verbose_name = "padre / tutor"
        verbose_name_plural = "padres / tutores"

    def __str__(self):
        return f"Padre: {self.user.email or self.user.username}"


class ProfesorPerfil(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profesor_perfil",
    )
    profesor = models.OneToOneField(
        Profesor,
        on_delete=models.CASCADE,
        related_name="usuario",
    )

    class Meta:
        verbose_name = "perfil profesor"
        verbose_name_plural = "perfiles profesor"

    def __str__(self):
        return f"{self.user} ↔ {self.profesor}"


class InvitacionPadre(models.Model):
    """Enlace de registro para padres; expira a las 24 h; un solo uso exitoso."""

    estudiante = models.ForeignKey(
        Estudiante,
        on_delete=models.CASCADE,
        related_name="invitaciones_padre",
    )
    token = models.CharField(max_length=64, unique=True, db_index=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    expira_en = models.DateTimeField()
    usado_en = models.DateTimeField(null=True, blank=True)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="invitaciones_creadas",
    )

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "invitación padre"
        verbose_name_plural = "invitaciones padre"

    def __str__(self):
        return f"Invitación {self.estudiante_id} ({'usada' if self.usado_en else 'activa'})"

    @classmethod
    def crear(cls, estudiante, usuario=None, horas_validez: int = 24):
        token = secrets.token_urlsafe(32)
        now = timezone.now()
        return cls.objects.create(
            estudiante=estudiante,
            token=token,
            expira_en=now + timedelta(hours=horas_validez),
            creado_por=usuario,
        )

    def activa(self) -> bool:
        if self.usado_en:
            return False
        return timezone.now() <= self.expira_en


class SolicitudNuevoEnlace(models.Model):
    """Si el enlace expiró, el padre deja datos para que el colegio genere uno nuevo."""

    cedula_estudiante = models.CharField(max_length=32)
    nombre_solicitante = models.CharField(max_length=200)
    telefono = models.CharField(max_length=40, blank=True, default="")
    nota = models.TextField(blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)
    atendida = models.BooleanField(default=False)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "solicitud de nuevo enlace"
        verbose_name_plural = "solicitudes de nuevo enlace"

    def __str__(self):
        return f"Solicitud {self.cedula_estudiante} — {self.nombre_solicitante}"
