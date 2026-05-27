from django import forms
from django.utils import timezone

from .models import (
    Asistencia,
    Curso,
    Estudiante,
    EvaluacionP1,
    Materia,
    NotaCurso,
    Observacion,
    Participacion,
    Planificacion,
    Profesor,
    RegistroProgresoP2,
)


FORM_ATTRS = {"class": "form-control bg-dark text-light border-secondary"}
SELECT_ATTRS = {"class": "form-select bg-dark text-light border-secondary"}
TEXTAREA_ATTRS = {
    "class": "form-control bg-dark text-light border-secondary",
    "rows": 3,
}
CHECK_ATTRS = {"class": "form-check-input"}


class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ["nombre", "codigo", "descripcion"]
        widgets = {
            "nombre": forms.TextInput(attrs=FORM_ATTRS),
            "codigo": forms.TextInput(attrs=FORM_ATTRS),
            "descripcion": forms.Textarea(attrs=TEXTAREA_ATTRS),
        }


class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = ["nombre", "apellido", "cedula", "telefono", "email", "materias"]
        widgets = {
            "nombre": forms.TextInput(attrs=FORM_ATTRS),
            "apellido": forms.TextInput(attrs=FORM_ATTRS),
            "cedula": forms.TextInput(attrs=FORM_ATTRS),
            "telefono": forms.TextInput(attrs=FORM_ATTRS),
            "email": forms.EmailInput(attrs=FORM_ATTRS),
            "materias": forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
        }


class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            "nombre",
            "apellido",
            "cedula",
            "fecha_nacimiento",
            "grado",
            "seccion",
            "profesores",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs=FORM_ATTRS),
            "apellido": forms.TextInput(attrs=FORM_ATTRS),
            "cedula": forms.TextInput(attrs=FORM_ATTRS),
            "fecha_nacimiento": forms.DateInput(
                attrs={**FORM_ATTRS, "type": "date"}, format="%Y-%m-%d"
            ),
            "grado": forms.Select(attrs=SELECT_ATTRS),
            "seccion": forms.TextInput(attrs=FORM_ATTRS),
            "profesores": forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
        }


class ObservacionForm(forms.ModelForm):
    class Meta:
        model = Observacion
        fields = ["materia", "tipo", "contenido", "visible_padre"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "tipo": forms.Select(attrs=SELECT_ATTRS),
            "contenido": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 4}),
            "visible_padre": forms.CheckboxInput(attrs=CHECK_ATTRS),
        }

    def __init__(self, *args, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs
        self.fields["materia"].required = False
        self.fields["materia"].empty_label = "-- General (sin materia) --"


PUNTOS_PARTICIPACION = [(i, str(i)) for i in range(1, 6)]


class ParticipacionForm(forms.ModelForm):
    class Meta:
        model = Participacion
        fields = ["materia", "origen", "tipo", "valor", "descripcion"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "origen": forms.Select(attrs=SELECT_ATTRS),
            "tipo": forms.Select(attrs=SELECT_ATTRS),
            "valor": forms.Select(attrs=SELECT_ATTRS, choices=PUNTOS_PARTICIPACION),
            "descripcion": forms.TextInput(attrs={**FORM_ATTRS, "placeholder": "Motivo (opcional)"}),
        }

    def __init__(self, *args, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs
        self.fields["valor"].label = "Puntos (1–5)"
        self.fields["origen"].label = "Origen del punto"


class AsistenciaForm(forms.Form):
    fecha = forms.DateField(widget=forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}))
    grado = forms.ChoiceField(
        choices=[("", "Todos los grados")] + Estudiante._meta.get_field("grado").choices,
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),
    )


class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ["grado", "seccion", "anio_escolar"]
        widgets = {
            "grado": forms.Select(attrs=SELECT_ATTRS),
            "seccion": forms.TextInput(attrs=FORM_ATTRS),
            "anio_escolar": forms.TextInput(
                attrs={**FORM_ATTRS, "placeholder": "2025-2026"}
            ),
        }


class NotaCursoForm(forms.ModelForm):
    class Meta:
        model = NotaCurso
        fields = ["materia", "fecha", "contenido", "estudiantes"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "fecha": forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}, format="%Y-%m-%d"),
            "contenido": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 5}),
            "estudiantes": forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
        }

    def __init__(self, *args, curso=None, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["materia"].required = False
        self.fields["materia"].empty_label = "-- General del curso --"
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs
        if curso is not None:
            self.fields["estudiantes"].queryset = curso.estudiantes_qs().order_by(
                "apellido", "nombre"
            )
            self.fields["estudiantes"].required = False
        if not self.initial.get("fecha") and not self.data:
            self.initial["fecha"] = timezone.localdate()


class PlanificacionForm(forms.ModelForm):
    class Meta:
        model = Planificacion
        fields = [
            "materia",
            "tipo",
            "fecha",
            "titulo",
            "contenido",
            "competencias_fundamentales",
            "indicadores_logro",
        ]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "tipo": forms.Select(attrs=SELECT_ATTRS),
            "fecha": forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}, format="%Y-%m-%d"),
            "titulo": forms.TextInput(attrs=FORM_ATTRS),
            "contenido": forms.HiddenInput(),
            "competencias_fundamentales": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 2}),
            "indicadores_logro": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 2}),
        }

    def __init__(self, *args, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs
        if not self.initial.get("fecha") and not self.data:
            self.initial["fecha"] = timezone.localdate()


class EvaluacionP1Form(forms.ModelForm):
    class Meta:
        model = EvaluacionP1
        fields = ["materia", "fecha", "contenido_texto", "imagen"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "fecha": forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}, format="%Y-%m-%d"),
            "contenido_texto": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 5}),
            "imagen": forms.ClearableFileInput(
                attrs={"class": "form-control bg-dark text-light border-secondary"}
            ),
        }

    def __init__(self, *args, materias_qs=None, curso=None, **kwargs):
        self.curso = curso
        super().__init__(*args, **kwargs)
        qs = materias_qs if materias_qs is not None else self.fields["materia"].queryset
        if self.instance.pk and self.instance.materia_id:
            qs = qs | Materia.objects.filter(pk=self.instance.materia_id)
        if curso and not self.instance.pk:
            usadas = curso.evaluaciones_p1.values_list("materia_id", flat=True)
            qs = qs.exclude(pk__in=usadas)
        self.fields["materia"].queryset = qs.distinct()
        if self.instance.pk:
            self.fields["materia"].disabled = True
        if not self.initial.get("fecha") and not self.data:
            self.initial["fecha"] = timezone.localdate()

    def clean_materia(self):
        if self.instance.pk:
            return self.instance.materia
        return self.cleaned_data.get("materia")

    def clean(self):
        cleaned = super().clean()
        texto = (cleaned.get("contenido_texto") or "").strip()
        imagen = cleaned.get("imagen")
        if self.instance.pk and self.instance.imagen and not imagen:
            imagen = self.instance.imagen
        if not texto and not imagen:
            raise forms.ValidationError(
                "La evaluación P1 debe incluir texto descriptivo o una imagen adjunta."
            )
        materia = cleaned.get("materia")
        if self.curso and materia and not self.instance.pk:
            if EvaluacionP1.objects.filter(curso=self.curso, materia=materia).exists():
                raise forms.ValidationError(
                    "Ya existe una evaluación P1 para esta materia en el curso."
                )
        return cleaned


class RegistroProgresoP2Form(forms.ModelForm):
    class Meta:
        model = RegistroProgresoP2
        fields = ["fecha", "contenido"]
        widgets = {
            "fecha": forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}, format="%Y-%m-%d"),
            "contenido": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial.get("fecha") and not self.data:
            self.initial["fecha"] = timezone.localdate()
