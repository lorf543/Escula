from django import forms
from django.contrib.auth import get_user_model

from .models import SolicitudNuevoEnlace
from .utils import cedula_valida_formato, normalizar_cedula

User = get_user_model()


class RegistroPadreForm(forms.Form):
    """No ModelForm: crea User + Padre en la vista tras validar cédula."""

    email = forms.EmailField(
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={"class": "form-control bg-dark text-light border-secondary"}),
    )
    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control bg-dark text-light border-secondary"}),
    )
    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control bg-dark text-light border-secondary"}),
    )
    cedula = forms.CharField(
        label="Cédula electoral del estudiante",
        max_length=32,
        widget=forms.TextInput(
            attrs={
                "class": "form-control bg-dark text-light border-secondary",
                "placeholder": "Ej. 00123456789 o 001-1234567-8",
            }
        ),
    )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este correo ya está registrado. Inicie sesión y use «Vincular otro hijo» "
                "con un nuevo enlace, o solicite ayuda al colegio."
            )
        return email

    def clean(self):
        data = super().clean()
        p1, p2 = data.get("password1"), data.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Las contraseñas no coinciden.")
        return data

    def clean_cedula(self):
        raw = self.cleaned_data.get("cedula", "")
        if not cedula_valida_formato(raw):
            raise forms.ValidationError(
                "Indique una cédula de 11 dígitos (cédula electoral dominicana)."
            )
        return raw


class VincularHijoForm(forms.Form):
    cedula = forms.CharField(
        label="Cédula electoral del estudiante del enlace",
        max_length=32,
        widget=forms.TextInput(attrs={"class": "form-control bg-dark text-light border-secondary"}),
    )

    def clean_cedula(self):
        raw = self.cleaned_data.get("cedula", "")
        if not cedula_valida_formato(raw):
            raise forms.ValidationError("Indique una cédula de 11 dígitos.")
        return raw


class SolicitudNuevoEnlaceForm(forms.ModelForm):
    class Meta:
        model = SolicitudNuevoEnlace
        fields = ["cedula_estudiante", "nombre_solicitante", "telefono", "nota"]
        widgets = {
            "cedula_estudiante": forms.TextInput(
                attrs={"class": "form-control bg-dark text-light border-secondary"}
            ),
            "nombre_solicitante": forms.TextInput(
                attrs={"class": "form-control bg-dark text-light border-secondary"}
            ),
            "telefono": forms.TextInput(attrs={"class": "form-control bg-dark text-light border-secondary"}),
            "nota": forms.Textarea(
                attrs={"class": "form-control bg-dark text-light border-secondary", "rows": 3}
            ),
        }

    def clean_cedula_estudiante(self):
        v = self.cleaned_data.get("cedula_estudiante", "")
        n = normalizar_cedula(v)
        if len(n) < 3:
            raise forms.ValidationError("Indique una cédula válida.")
        return v
