from django.urls import path
from . import views

app_name = "core"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    # Materias
    path("materias/", views.materia_list, name="materia_list"),
    path("materias/crear/", views.materia_create, name="materia_create"),
    path("materias/<int:pk>/editar/", views.materia_update, name="materia_update"),
    path("materias/<int:pk>/eliminar/", views.materia_delete, name="materia_delete"),
    # Profesores
    path("profesores/", views.profesor_list, name="profesor_list"),
    path("profesores/crear/", views.profesor_create, name="profesor_create"),
    path("profesores/<int:pk>/", views.profesor_detail, name="profesor_detail"),
    path("profesores/<int:pk>/editar/", views.profesor_update, name="profesor_update"),
    path("profesores/<int:pk>/eliminar/", views.profesor_delete, name="profesor_delete"),
    # Estudiantes
    path("estudiantes/", views.estudiante_list, name="estudiante_list"),
    path("estudiantes/crear/", views.estudiante_create, name="estudiante_create"),
    path("estudiantes/<int:pk>/", views.estudiante_detail, name="estudiante_detail"),
    path("estudiantes/<int:pk>/editar/", views.estudiante_update, name="estudiante_update"),
    path("estudiantes/<int:pk>/eliminar/", views.estudiante_delete, name="estudiante_delete"),
    # Observaciones
    path(
        "estudiantes/<int:estudiante_pk>/observaciones/",
        views.observacion_list_partial,
        name="observacion_list",
    ),
    path(
        "estudiantes/<int:estudiante_pk>/observaciones/crear/",
        views.observacion_create,
        name="observacion_create",
    ),
    path("observaciones/<int:pk>/eliminar/", views.observacion_delete, name="observacion_delete"),
    # Participaciones
    path(
        "estudiantes/<int:estudiante_pk>/participaciones/",
        views.participacion_list_partial,
        name="participacion_list",
    ),
    path(
        "estudiantes/<int:estudiante_pk>/participaciones/crear/",
        views.participacion_create,
        name="participacion_create",
    ),
    path("participaciones/<int:pk>/eliminar/", views.participacion_delete, name="participacion_delete"),
    # Asistencia
    path("asistencia/", views.asistencia_view, name="asistencia"),
    path("asistencia/<int:pk>/toggle/", views.asistencia_toggle, name="asistencia_toggle"),
    path("asistencia/historial/", views.asistencia_historial, name="asistencia_historial"),
    path("asistencia/exportar/", views.asistencia_exportar, name="asistencia_exportar"),
]
