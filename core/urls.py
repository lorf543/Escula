from django.urls import path
from . import curso_views, views

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
    path("estudiantes/<int:pk>/curriculum/", views.estudiante_curriculum, name="estudiante_curriculum"),
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
    path("asistencia/guardar/", views.asistencia_guardar, name="asistencia_guardar"),
    path("asistencia/historial/", views.asistencia_historial, name="asistencia_historial"),
    path("asistencia/exportar/", views.asistencia_exportar, name="asistencia_exportar"),
    # Cursos — notas, planificación, P1/P2 (RD)
    path("cursos/", curso_views.curso_list, name="curso_list"),
    path("cursos/crear/", curso_views.curso_create, name="curso_create"),
    path("cursos/<int:pk>/", curso_views.curso_detail, name="curso_detail"),
    path("cursos/<int:pk>/curriculum/", curso_views.curso_curriculum, name="curso_curriculum"),
    path("cursos/<int:curso_pk>/notas/crear/", curso_views.nota_curso_create, name="nota_curso_create"),
    path("notas-curso/<int:pk>/eliminar/", curso_views.nota_curso_delete, name="nota_curso_delete"),
    path(
        "cursos/<int:curso_pk>/planificacion/crear/",
        curso_views.planificacion_create,
        name="planificacion_create",
    ),
    path("planificacion/<int:pk>/editar/", curso_views.planificacion_update, name="planificacion_update"),
    path("planificacion/<int:pk>/eliminar/", curso_views.planificacion_delete, name="planificacion_delete"),
    path(
        "cursos/<int:curso_pk>/p1/crear/",
        curso_views.evaluacion_p1_create,
        name="evaluacion_p1_create",
    ),
    path("evaluacion-p1/<int:pk>/editar/", curso_views.evaluacion_p1_update, name="evaluacion_p1_update"),
    path("evaluacion-p1/<int:pk>/eliminar/", curso_views.evaluacion_p1_delete, name="evaluacion_p1_delete"),
    path("evaluacion-p1/<int:p1_pk>/p2/crear/", curso_views.registro_p2_create, name="registro_p2_create"),
    path("registro-p2/<int:pk>/editar/", curso_views.registro_p2_update, name="registro_p2_update"),
    path("registro-p2/<int:pk>/eliminar/", curso_views.registro_p2_delete, name="registro_p2_delete"),
]
