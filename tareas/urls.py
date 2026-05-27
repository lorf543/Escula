from django.urls import path

from . import views

app_name = "tareas"

urlpatterns = [
    path("", views.tarea_list, name="tarea_list"),
    path("miembros-partial/", views.grupo_miembros_partial, name="grupo_miembros_partial"),
    path("nueva/", views.tarea_create, name="tarea_create"),
    path("<int:pk>/", views.tarea_detail, name="tarea_detail"),
    path("<int:pk>/editar/", views.tarea_update, name="tarea_update"),
    path("<int:pk>/eliminar/", views.tarea_delete, name="tarea_delete"),
    path("<int:pk>/evaluar/", views.tarea_evaluar, name="tarea_evaluar"),
]
