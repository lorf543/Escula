from django.contrib import admin

from core.models import GrupoEstudiantes

from .models import Tarea, TareaEvaluacion, TareaGrado, TareaGrupoEvaluacion


class TareaGradoInline(admin.TabularInline):
    model = TareaGrado
    extra = 1


class GrupoTareaInline(admin.TabularInline):
    model = GrupoEstudiantes
    extra = 0
    fields = ("nombre", "creado_por", "created_at")
    readonly_fields = ("created_at",)


@admin.register(Tarea)
class TareaAdmin(admin.ModelAdmin):
    list_display = ("titulo", "materia", "fecha_entrega", "tipo_asignacion", "creada_por", "creado_en")
    list_filter = ("tipo_asignacion", "modalidad", "materia")
    inlines = [TareaGradoInline, GrupoTareaInline]


@admin.register(TareaGrupoEvaluacion)
class TareaGrupoEvaluacionAdmin(admin.ModelAdmin):
    list_display = ("tarea", "grupo", "actualizado_en")


@admin.register(TareaEvaluacion)
class TareaEvaluacionAdmin(admin.ModelAdmin):
    list_display = ("tarea", "estudiante", "estado", "tardio", "actualizado_en")
    list_filter = ("estado", "tardio")
