from django import forms
from django.forms import BaseFormSet, formset_factory

from core.curso_utils import anio_escolar_actual
from core.grupo_utils import (
    estudiantes_elegibles_para_cursos,
    sincronizar_cursos_grupo,
    sincronizar_miembros_grupo,
    validar_miembros_en_cursos,
)
from core.models import Curso, Estudiante, GRADO_CHOICES, GrupoEstudiantes, Materia, Profesor

from .models import (
    Tarea,
    TareaEvaluacion,
    TareaGrado,
    ModalidadTarea,
    EstadoTareaEval,
    TipoAsignacionTarea,
)
from .rubricas import choices_puntaje, derivar_estado, escala_max
from .signals import sincronizar_evaluaciones_tarea

SELECT_ATTRS = {"class": "form-select bg-dark text-light border-secondary"}
CHECK_ATTRS = {"class": "form-check-input"}
FORM_ATTRS = {"class": "form-control bg-dark text-light border-secondary"}


class GrupoTareaForm(forms.Form):
    """Formulario inline para un grupo temporal de una tarea."""

    grupo_id = forms.IntegerField(required=False, widget=forms.HiddenInput)
    nombre = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={**FORM_ATTRS, "placeholder": "Nombre del grupo"}),
    )
    cursos = forms.ModelMultipleChoiceField(
        label="Cursos",
        queryset=Curso.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
    )
    miembros = forms.ModelMultipleChoiceField(
        label="Integrantes",
        queryset=Estudiante.objects.none(),
        widget=forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
        required=False,
    )
    DELETE = forms.BooleanField(required=False, widget=forms.HiddenInput)

    def __init__(self, *args, anio=None, prefix=None, **kwargs):
        super().__init__(*args, prefix=prefix, **kwargs)
        if anio is None:
            anio = anio_escolar_actual()
        self.anio = anio
        self.fields["cursos"].queryset = Curso.objects.filter(anio_escolar=anio).order_by(
            "grado", "seccion"
        )
        curso_ids = []
        if self.data and prefix:
            curso_ids = self.data.getlist(f"{prefix}-cursos")
        elif self.initial.get("cursos"):
            raw = self.initial["cursos"]
            curso_ids = [c.pk if hasattr(c, "pk") else int(c) for c in raw]
        if self.initial.get("cursos"):
            self.fields["cursos"].initial = self.initial["cursos"]
        if self.initial.get("miembros"):
            self.fields["miembros"].initial = self.initial["miembros"]
        if curso_ids:
            self.fields["miembros"].queryset = estudiantes_elegibles_para_cursos(curso_ids)
        else:
            self.fields["miembros"].queryset = Estudiante.objects.none()

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("DELETE"):
            return cleaned
        cursos = cleaned.get("cursos")
        miembros = cleaned.get("miembros") or []
        nombre = (cleaned.get("nombre") or "").strip()
        if not nombre and not cursos and not miembros:
            cleaned["DELETE"] = True
            return cleaned
        if not nombre:
            raise forms.ValidationError("Indique el nombre del grupo.")
        if not cursos:
            raise forms.ValidationError("Seleccione al menos un curso.")
        curso_ids = [c.pk for c in cursos]
        errores = validar_miembros_en_cursos([m.pk for m in miembros], curso_ids)
        if errores:
            raise forms.ValidationError(errores)
        if not miembros:
            raise forms.ValidationError("Seleccione al menos un integrante.")
        cleaned["_curso_ids"] = curso_ids
        cleaned["_miembro_ids"] = [m.pk for m in miembros]
        return cleaned


class BaseGrupoTareaFormSet(BaseFormSet):
    def __init__(self, *args, anio=None, tarea=None, **kwargs):
        self.anio = anio or anio_escolar_actual()
        self.tarea = tarea
        super().__init__(*args, **kwargs)

    def _construct_form(self, i, **kwargs):
        kwargs["anio"] = self.anio
        return super()._construct_form(i, **kwargs)

    def clean(self):
        super().clean()
        activos = [
            f for f in self.forms
            if f.cleaned_data and not f.cleaned_data.get("DELETE")
            and (f.cleaned_data.get("nombre") or "").strip()
        ]
        if not activos:
            raise forms.ValidationError("Defina al menos un grupo con integrantes.")
        return self.cleaned_data

    def save(self, tarea, creado_por=None):
        ids_presentes = set()
        for form in self.forms:
            if not form.is_valid() or not form.cleaned_data:
                continue
            if form.cleaned_data.get("DELETE"):
                gid = form.cleaned_data.get("grupo_id")
                if gid:
                    GrupoEstudiantes.objects.filter(pk=gid, tarea=tarea).delete()
                continue
            nombre = form.cleaned_data.get("nombre", "").strip()
            if not nombre:
                continue
            gid = form.cleaned_data.get("grupo_id")
            if gid:
                grupo = GrupoEstudiantes.objects.get(pk=gid, tarea=tarea)
                grupo.nombre = nombre
                grupo.save(update_fields=["nombre"])
            else:
                grupo = GrupoEstudiantes.objects.create(
                    tarea=tarea,
                    nombre=nombre,
                    creado_por=creado_por,
                )
            ids_presentes.add(grupo.pk)
            sincronizar_cursos_grupo(grupo, form.cleaned_data["_curso_ids"])
            sincronizar_miembros_grupo(grupo, form.cleaned_data["_miembro_ids"])
        GrupoEstudiantes.objects.filter(tarea=tarea).exclude(pk__in=ids_presentes).delete()
        sincronizar_evaluaciones_tarea(tarea)


def build_grupo_formset(data=None, tarea=None, prefix="grupos"):
    initial = initial_grupos_para_tarea(tarea) if tarea and tarea.pk else []
    extra = 0 if initial else 1
    FormSetClass = formset_factory(
        GrupoTareaForm,
        formset=BaseGrupoTareaFormSet,
        extra=extra,
        can_delete=True,
    )
    kwargs = {"prefix": prefix, "form_kwargs": {"anio": anio_escolar_actual()}}
    if data is not None:
        return FormSetClass(data, **kwargs)
    if initial:
        return FormSetClass(initial=initial, **kwargs)
    return FormSetClass(**kwargs)


def initial_grupos_para_tarea(tarea):
    iniciales = []
    for grupo in tarea.grupos.prefetch_related("grupo_cursos", "miembros").order_by("nombre"):
        iniciales.append(
            {
                "grupo_id": grupo.pk,
                "nombre": grupo.nombre,
                "cursos": list(grupo.grupo_cursos.values_list("curso_id", flat=True)),
                "miembros": list(grupo.miembros.values_list("estudiante_id", flat=True)),
            }
        )
    return iniciales


class TareaForm(forms.ModelForm):
    grados_asignados = forms.MultipleChoiceField(
        label="Cursos (grado)",
        choices=GRADO_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs=CHECK_ATTRS),
    )

    class Meta:
        model = Tarea
        fields = [
            "titulo",
            "descripcion",
            "materia",
            "modalidad",
            "tipo_asignacion",
            "fecha_entrega",
        ]
        widgets = {
            "titulo": forms.TextInput(attrs=FORM_ATTRS),
            "descripcion": forms.Textarea(attrs={**FORM_ATTRS, "rows": 6}),
            "materia": forms.Select(attrs=SELECT_ATTRS),
            "modalidad": forms.Select(attrs=SELECT_ATTRS),
            "tipo_asignacion": forms.RadioSelect(attrs=CHECK_ATTRS),
            "fecha_entrega": forms.DateInput(
                attrs={**FORM_ATTRS, "type": "date"},
                format="%Y-%m-%d",
            ),
        }

    def __init__(self, *args, staff_mode=False, materias_qs=None, creada_por=None, **kwargs):
        self.staff_mode = staff_mode
        self._creada_por = creada_por
        super().__init__(*args, **kwargs)
        qs = materias_qs if materias_qs is not None else Materia.objects.order_by("nombre")
        self.fields["materia"].queryset = qs
        self.fields["materia"].required = True
        self.fields["materia"].empty_label = "— Seleccione materia —"
        if staff_mode:
            self.fields["creada_por"] = forms.ModelChoiceField(
                label="Profesor responsable",
                queryset=Profesor.objects.order_by("apellido", "nombre"),
                widget=forms.Select(attrs=SELECT_ATTRS),
            )
            if self.instance.pk and self.instance.creada_por_id:
                self.fields["creada_por"].initial = self.instance.creada_por
        if self.instance.pk:
            self.fields["grados_asignados"].initial = list(
                self.instance.grados.values_list("grado", flat=True)
            )

    def clean(self):
        cleaned = super().clean()
        materia = cleaned.get("materia")
        if not materia:
            return cleaned
        profesor = cleaned.get("creada_por") if self.staff_mode else self._creada_por
        if not profesor and self.instance.pk:
            profesor = self.instance.creada_por
        if profesor and not profesor.materias.filter(pk=materia.pk).exists():
            raise forms.ValidationError(
                {"materia": "La materia debe estar asignada al profesor responsable."}
            )
        return cleaned

    def _sync_grados(self, tarea):
        TareaGrado.objects.filter(tarea=tarea).delete()
        for g in self.cleaned_data.get("grados_asignados", []):
            TareaGrado.objects.create(tarea=tarea, grado=g)

    def save(self, commit=True, creada_por=None, grupo_formset=None):
        tarea = super().save(commit=False)
        if self.staff_mode and "creada_por" in self.cleaned_data:
            tarea.creada_por = self.cleaned_data["creada_por"]
        elif creada_por is not None:
            tarea.creada_por = creada_por
        profesor = tarea.creada_por
        if commit:
            tarea.save()
            if tarea.tipo_asignacion == TipoAsignacionTarea.GRADOS:
                GrupoEstudiantes.objects.filter(tarea=tarea).delete()
                self._sync_grados(tarea)
                sincronizar_evaluaciones_tarea(tarea)
            elif grupo_formset is not None:
                TareaGrado.objects.filter(tarea=tarea).delete()
                grupo_formset.save(tarea, creado_por=profesor)
        return tarea


class TareaEvaluacionForm(forms.ModelForm):
    puntaje = forms.ChoiceField(
        required=False,
        choices=[],
        label="Puntaje (rúbrica)",
        widget=forms.Select(attrs={**SELECT_ATTRS, "class": SELECT_ATTRS["class"] + " puntaje-select"}),
    )
    no_realizado = forms.BooleanField(
        required=False,
        label="No realizó",
        widget=forms.CheckboxInput(attrs={"class": "form-check-input no-realizado-check"}),
    )

    class Meta:
        model = TareaEvaluacion
        fields = ["tardio", "puntaje", "comentario_maestro"]
        widgets = {
            "tardio": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "comentario_maestro": forms.Textarea(
                attrs={"class": "form-control bg-dark text-light border-secondary", "rows": 2}
            ),
        }

    def __init__(self, *args, modalidad=ModalidadTarea.ESCRITA, **kwargs):
        self.modalidad = modalidad
        super().__init__(*args, **kwargs)
        self.fields["puntaje"].choices = choices_puntaje(modalidad)
        max_p = escala_max(modalidad)
        self.fields["puntaje"].help_text = f"Escala 1–{max_p}. El estado se asigna automáticamente."
        if self.instance.pk:
            if self.instance.puntaje is not None:
                self.fields["puntaje"].initial = str(self.instance.puntaje)
            if self.instance.estado == EstadoTareaEval.NO_REALIZADO:
                self.fields["no_realizado"].initial = True

    def clean_puntaje(self):
        raw = self.cleaned_data.get("puntaje")
        if raw in (None, ""):
            return None
        puntaje = int(raw)
        max_p = escala_max(self.modalidad)
        if puntaje < 1 or puntaje > max_p:
            raise forms.ValidationError(f"El puntaje debe estar entre 1 y {max_p}.")
        return puntaje

    def clean(self):
        cleaned = super().clean()
        no_realizado = cleaned.get("no_realizado")
        puntaje = cleaned.get("puntaje")
        if no_realizado and puntaje is not None:
            raise forms.ValidationError(
                "No puede asignar puntaje si marcó «No realizó la tarea»."
            )
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        no_realizado = self.cleaned_data.get("no_realizado")
        puntaje = self.cleaned_data.get("puntaje")
        if no_realizado:
            obj.estado = EstadoTareaEval.NO_REALIZADO
            obj.puntaje = None
        elif puntaje is None:
            obj.estado = EstadoTareaEval.PENDIENTE
            obj.puntaje = None
        else:
            obj.puntaje = puntaje
            obj.estado = derivar_estado(self.modalidad, puntaje)
        if commit:
            obj.save()
        return obj
