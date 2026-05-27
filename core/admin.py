from django.contrib import admin
from .models import (
    Asistencia,
    Curso,
    Estudiante,
    EvaluacionP1,
    GrupoCurso,
    GrupoEstudiantes,
    GrupoMiembro,
    Materia,
    NotaCurso,
    Observacion,
    Participacion,
    Planificacion,
    Profesor,
    RegistroProgresoP2,
)


@admin.register(Curso)
class CursoAdmin(admin.ModelAdmin):
    list_display = ("nombre_completo", "grado", "seccion", "anio_escolar")
    list_filter = ("anio_escolar", "grado")


class RegistroP2Inline(admin.TabularInline):
    model = RegistroProgresoP2
    extra = 0


@admin.register(EvaluacionP1)
class EvaluacionP1Admin(admin.ModelAdmin):
    list_display = ("curso", "materia", "fecha")
    inlines = [RegistroP2Inline]


admin.site.register(Materia)
admin.site.register(Profesor)
admin.site.register(Estudiante)
admin.site.register(Observacion)
admin.site.register(Asistencia)
admin.site.register(Participacion)
admin.site.register(NotaCurso)
admin.site.register(Planificacion)


class GrupoCursoInline(admin.TabularInline):
    model = GrupoCurso
    extra = 0


class GrupoMiembroInline(admin.TabularInline):
    model = GrupoMiembro
    extra = 0


@admin.register(GrupoEstudiantes)
class GrupoEstudiantesAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tarea", "creado_por", "created_at")
    list_filter = ("created_at",)
    inlines = [GrupoCursoInline, GrupoMiembroInline]
