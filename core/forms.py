from django import forms
from .models import Estudiante, Profesor, Materia, Observacion, Asistencia, Participacion


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
        fields = ["materia", "tipo", "contenido"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "tipo": forms.Select(attrs=SELECT_ATTRS),
            "contenido": forms.Textarea(attrs={**TEXTAREA_ATTRS, "rows": 4}),
        }

    def __init__(self, *args, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs
        self.fields["materia"].required = False
        self.fields["materia"].empty_label = "-- General (sin materia) --"


class ParticipacionForm(forms.ModelForm):
    class Meta:
        model = Participacion
        fields = ["materia", "tipo", "descripcion"]
        widgets = {
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "tipo": forms.Select(attrs=SELECT_ATTRS),
            "descripcion": forms.TextInput(attrs={**FORM_ATTRS, "placeholder": "Motivo (opcional)"}),
        }

    def __init__(self, *args, materias_qs=None, **kwargs):
        super().__init__(*args, **kwargs)
        if materias_qs is not None:
            self.fields["materia"].queryset = materias_qs


class AsistenciaForm(forms.Form):
    fecha = forms.DateField(widget=forms.DateInput(attrs={**FORM_ATTRS, "type": "date"}))
    grado = forms.ChoiceField(
        choices=[("", "Todos los grados")] + Estudiante._meta.get_field("grado").choices,
        required=False,
        widget=forms.Select(attrs=SELECT_ATTRS),
    )
