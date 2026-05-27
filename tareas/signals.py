from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.grupo_utils import estudiante_ids_de_tarea_grupos
from core.models import Estudiante, GrupoEstudiantes, GrupoMiembro

from .models import (
    Tarea,
    TareaEvaluacion,
    TareaGrado,
    TareaGrupoEvaluacion,
    TipoAsignacionTarea,
)


def sincronizar_evaluaciones_tarea(tarea: Tarea):
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        permitidos = estudiante_ids_de_tarea_grupos(tarea)
        if not permitidos:
            TareaEvaluacion.objects.filter(tarea=tarea).delete()
            return
        existentes = set(
            TareaEvaluacion.objects.filter(tarea=tarea).values_list("estudiante_id", flat=True)
        )
        for eid in permitidos:
            if eid not in existentes:
                TareaEvaluacion.objects.create(tarea=tarea, estudiante_id=eid)
        TareaEvaluacion.objects.filter(tarea=tarea).exclude(estudiante_id__in=permitidos).delete()
        return

    grados = set(tarea.grados.values_list("grado", flat=True))
    if not grados:
        TareaEvaluacion.objects.filter(tarea=tarea).delete()
        return
    estudiantes = Estudiante.objects.filter(grado__in=grados)
    existentes = set(
        TareaEvaluacion.objects.filter(tarea=tarea).values_list("estudiante_id", flat=True)
    )
    for est in estudiantes:
        if est.pk not in existentes:
            TareaEvaluacion.objects.create(tarea=tarea, estudiante=est)
    permitidos = estudiantes.values_list("pk", flat=True)
    TareaEvaluacion.objects.filter(tarea=tarea).exclude(estudiante_id__in=permitidos).delete()


def asegurar_evaluaciones_grupo(tarea: Tarea, grupo: GrupoEstudiantes):
    TareaGrupoEvaluacion.objects.get_or_create(tarea=tarea, grupo=grupo)


@receiver(post_save, sender=TareaGrado)
def al_guardar_grado(sender, instance, **kwargs):
    if instance.tarea.tipo_asignacion == TipoAsignacionTarea.GRADOS:
        sincronizar_evaluaciones_tarea(instance.tarea)


@receiver(post_delete, sender=TareaGrado)
def al_borrar_grado(sender, instance, **kwargs):
    tarea = instance.tarea
    if tarea.tipo_asignacion != TipoAsignacionTarea.GRADOS:
        return
    grados = set(tarea.grados.values_list("grado", flat=True))
    if not grados:
        TareaEvaluacion.objects.filter(tarea=tarea).delete()
        return
    permitidos = Estudiante.objects.filter(grado__in=grados).values_list("pk", flat=True)
    TareaEvaluacion.objects.filter(tarea=tarea).exclude(estudiante_id__in=permitidos).delete()
    sincronizar_evaluaciones_tarea(tarea)


@receiver(post_save, sender=GrupoEstudiantes)
def al_guardar_grupo(sender, instance, **kwargs):
    tarea = instance.tarea
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        asegurar_evaluaciones_grupo(tarea, instance)
        sincronizar_evaluaciones_tarea(tarea)


@receiver(post_delete, sender=GrupoEstudiantes)
def al_borrar_grupo(sender, instance, **kwargs):
    tarea = instance.tarea
    TareaGrupoEvaluacion.objects.filter(tarea=tarea, grupo_id=instance.pk).delete()
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        sincronizar_evaluaciones_tarea(tarea)


@receiver(post_save, sender=GrupoMiembro)
def al_guardar_miembro(sender, instance, **kwargs):
    tarea = instance.grupo.tarea
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        sincronizar_evaluaciones_tarea(tarea)


@receiver(post_delete, sender=GrupoMiembro)
def al_borrar_miembro(sender, instance, **kwargs):
    tarea = instance.grupo.tarea
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        sincronizar_evaluaciones_tarea(tarea)
