from django.db import models
from django.conf import settings

from core.models import Estudiante, GRADO_CHOICES, GrupoEstudiantes, Materia, Profesor


class ModalidadTarea(models.TextChoices):
    ORAL = "ORAL", "Oral"
    ESCRITA = "ESCRITA", "Escrita"


class TipoAsignacionTarea(models.TextChoices):
    GRADOS = "GRADOS", "Por curso (grado)"
    GRUPOS = "GRUPOS", "Por grupos"


class Tarea(models.Model):
    titulo = models.CharField(max_length=200, blank=True, default="")
    descripcion = models.TextField()
    modalidad = models.CharField(
        max_length=10,
        choices=ModalidadTarea.choices,
        default=ModalidadTarea.ESCRITA,
    )
    tipo_asignacion = models.CharField(
        max_length=10,
        choices=TipoAsignacionTarea.choices,
        default=TipoAsignacionTarea.GRADOS,
    )
    fecha_entrega = models.DateField()
    materia = models.ForeignKey(
        Materia,
        on_delete=models.PROTECT,
        related_name="tareas",
        null=True,
        blank=True,
        verbose_name="materia",
    )
    creada_por = models.ForeignKey(
        Profesor,
        on_delete=models.CASCADE,
        related_name="tareas_creadas",
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado_en"]
        verbose_name = "tarea"
        verbose_name_plural = "tareas"

    def __str__(self):
        return self.titulo or f"Tarea #{self.pk}"


class TareaGrado(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="grados")
    grado = models.CharField(max_length=10, choices=GRADO_CHOICES)

    class Meta:
        unique_together = [("tarea", "grado")]
        verbose_name = "grado asignado"
        verbose_name_plural = "grados asignados"


class TareaGrupoEvaluacion(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="evaluaciones_grupo")
    grupo = models.ForeignKey(
        GrupoEstudiantes, on_delete=models.CASCADE, related_name="evaluaciones_tarea"
    )
    observacion_general = models.TextField("observación general del grupo", blank=True, default="")
    actualizado_en = models.DateTimeField(auto_now=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluaciones_grupo_tarea_editadas",
    )

    class Meta:
        unique_together = [("tarea", "grupo")]
        verbose_name = "evaluación de grupo"
        verbose_name_plural = "evaluaciones de grupo"

    def __str__(self):
        return f"{self.grupo} — {self.tarea}"


class EstadoTareaEval(models.TextChoices):
    PENDIENTE = "PENDIENTE", "Pendiente"
    COMPLETO = "COMPLETO", "Completo"
    NECESITA_MEJORA = "NECESITA_MEJORA", "Necesita mejora"
    NO_REALIZADO = "NO_REALIZADO", "No realizado"


class TareaEvaluacion(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE, related_name="evaluaciones")
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE, related_name="evaluaciones_tarea")
    estado = models.CharField(
        max_length=20,
        choices=EstadoTareaEval.choices,
        default=EstadoTareaEval.PENDIENTE,
    )
    tardio = models.BooleanField(default=False)
    puntaje = models.PositiveSmallIntegerField(
        "puntaje",
        null=True,
        blank=True,
        help_text="Oral: 1–5. Escrita: 1–10.",
    )
    comentario_maestro = models.TextField(blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)
    actualizado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluaciones_tarea_editadas",
    )

    class Meta:
        unique_together = [("tarea", "estudiante")]
        ordering = ["estudiante__apellido", "estudiante__nombre"]
        verbose_name = "evaluación de tarea"
        verbose_name_plural = "evaluaciones de tarea"

    def __str__(self):
        return f"{self.estudiante} — {self.tarea}"

    @property
    def puntaje_normalizado(self):
        from .rubricas import normalizar_puntaje

        return normalizar_puntaje(self.tarea.modalidad, self.puntaje)

    @property
    def puntaje_etiqueta(self):
        from .rubricas import puntaje_display

        return puntaje_display(self.tarea.modalidad, self.puntaje)
