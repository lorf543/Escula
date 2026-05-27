import django_filters
from django import forms

from core.models import GRADO_CHOICES, Materia

from .models import EstadoTareaEval, Tarea, TareaEvaluacion

SELECT_ATTRS = {"class": "form-select bg-dark text-light border-secondary"}


class TareaFilter(django_filters.FilterSet):
    grado = django_filters.ChoiceFilter(
        field_name="grados__grado",
        choices=GRADO_CHOICES,
        label="Curso",
        empty_label="Todos los cursos",
        widget=forms.Select(attrs=SELECT_ATTRS),
    )
    materia = django_filters.ModelChoiceFilter(
        queryset=Materia.objects.order_by("nombre"),
        label="Materia",
        empty_label="Todas las materias",
        widget=forms.Select(attrs=SELECT_ATTRS),
    )

    class Meta:
        model = Tarea
        fields = ["grado", "materia"]


class TareaEvaluacionFilter(django_filters.FilterSet):
    estado = django_filters.ChoiceFilter(
        choices=EstadoTareaEval.choices,
        empty_label="Todos",
        widget=forms.Select(attrs=SELECT_ATTRS),
    )

    class Meta:
        model = TareaEvaluacion
        fields = ["estado"]
