from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("padre/", views.padre_dashboard, name="padre_dashboard"),
    path("padre/estudiante/<int:pk>/curriculum/", views.padre_estudiante_curriculum, name="padre_curriculum"),
    path(
        "padre/estudiante/<int:pk>/exportar-asistencias/",
        views.padre_exportar_asistencias,
        name="padre_exportar_asistencias",
    ),
    path("registro-padre/<str:token>/", views.registro_padre, name="registro_padre"),
    path("padre/vincular/<str:token>/", views.vincular_otro_hijo, name="vincular_hijo"),
    path(
        "estudiante/<int:pk>/invitacion-padre/",
        views.crear_invitacion_estudiante,
        name="crear_invitacion",
    ),
    path("privacidad/", views.privacidad_resumen, name="privacidad"),
]
