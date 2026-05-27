from django.contrib import admin

from .models import InvitacionPadre, Padre, ProfesorPerfil, SolicitudNuevoEnlace, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)


@admin.register(Padre)
class PadreAdmin(admin.ModelAdmin):
    list_display = ("user",)
    filter_horizontal = ("estudiantes",)


@admin.register(ProfesorPerfil)
class ProfesorPerfilAdmin(admin.ModelAdmin):
    list_display = ("user", "profesor")


@admin.register(InvitacionPadre)
class InvitacionPadreAdmin(admin.ModelAdmin):
    list_display = ("estudiante", "creado_en", "expira_en", "usado_en", "creado_por")
    readonly_fields = ("token", "creado_en")


@admin.register(SolicitudNuevoEnlace)
class SolicitudNuevoEnlaceAdmin(admin.ModelAdmin):
    list_display = ("cedula_estudiante", "nombre_solicitante", "telefono", "creado_en", "atendida")
    list_filter = ("atendida",)
