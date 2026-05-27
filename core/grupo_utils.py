"""Utilidades para grupos de estudiantes multi-curso (temporales por tarea)."""

from .models import Curso, Estudiante, GrupoCurso, GrupoMiembro


def estudiantes_elegibles_para_cursos(curso_ids):
    """Unión de rosters de los cursos indicados."""
    if not curso_ids:
        return Estudiante.objects.none()
    cursos = Curso.objects.filter(pk__in=curso_ids)
    estudiante_ids = set()
    for curso in cursos:
        estudiante_ids.update(curso.estudiantes_qs().values_list("pk", flat=True))
    return Estudiante.objects.filter(pk__in=estudiante_ids).order_by("apellido", "nombre")


def curso_origen_para_estudiante(estudiante, curso_ids):
    """Primer curso del grupo cuyo roster incluye al estudiante."""
    for curso in Curso.objects.filter(pk__in=curso_ids).order_by("grado", "seccion"):
        if curso.estudiantes_qs().filter(pk=estudiante.pk).exists():
            return curso
    return None


def validar_miembros_en_cursos(estudiante_ids, curso_ids):
    """Devuelve lista de mensajes de error; vacía si todo es válido."""
    errores = []
    if not curso_ids:
        errores.append("Seleccione al menos un curso.")
        return errores
    elegibles = set(estudiantes_elegibles_para_cursos(curso_ids).values_list("pk", flat=True))
    for eid in estudiante_ids:
        if eid not in elegibles:
            est = Estudiante.objects.filter(pk=eid).first()
            nombre = str(est) if est else f"ID {eid}"
            errores.append(f"{nombre} no pertenece a los cursos seleccionados.")
    return errores


def sincronizar_cursos_grupo(grupo, curso_ids):
    GrupoCurso.objects.filter(grupo=grupo).exclude(curso_id__in=curso_ids).delete()
    existentes = set(
        GrupoCurso.objects.filter(grupo=grupo).values_list("curso_id", flat=True)
    )
    for cid in curso_ids:
        if cid not in existentes:
            GrupoCurso.objects.create(grupo=grupo, curso_id=cid)


def sincronizar_miembros_grupo(grupo, estudiante_ids, curso_ids=None):
    """Actualiza miembros; elimina los que ya no están en la lista."""
    if curso_ids is None:
        curso_ids = list(grupo.grupo_cursos.values_list("curso_id", flat=True))
    estudiante_ids = set(estudiante_ids)
    GrupoMiembro.objects.filter(grupo=grupo).exclude(estudiante_id__in=estudiante_ids).delete()
    existentes = set(
        GrupoMiembro.objects.filter(grupo=grupo).values_list("estudiante_id", flat=True)
    )
    for eid in estudiante_ids:
        if eid in existentes:
            continue
        est = Estudiante.objects.get(pk=eid)
        curso = curso_origen_para_estudiante(est, curso_ids)
        GrupoMiembro.objects.create(grupo=grupo, estudiante=est, curso=curso)


def estudiante_ids_de_grupos(grupo_ids):
    if not grupo_ids:
        return set()
    return set(
        GrupoMiembro.objects.filter(grupo_id__in=grupo_ids).values_list(
            "estudiante_id", flat=True
        )
    )


def estudiante_ids_de_tarea_grupos(tarea):
    grupo_ids = list(tarea.grupos.values_list("pk", flat=True))
    return estudiante_ids_de_grupos(grupo_ids)
