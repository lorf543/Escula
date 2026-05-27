from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render

from accounts.permissions import staff_o_profesor
from core.curso_utils import anio_escolar_actual
from core.grupo_utils import estudiantes_elegibles_para_cursos
from core.models import Materia

from .filters import TareaEvaluacionFilter, TareaFilter
from .forms import (
    TareaEvaluacionForm,
    TareaForm,
    build_grupo_formset,
)
from .rubricas import rubrica_items
from .models import (
    Tarea,
    TareaEvaluacion,
    TareaGrupoEvaluacion,
    TipoAsignacionTarea,
)
from .signals import asegurar_evaluaciones_grupo


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_list(request):
    qs = (
        Tarea.objects.select_related("creada_por", "materia")
        .prefetch_related("grados", "grupos__miembros")
        .order_by("-creado_en")
    )
    if not request.user.is_staff:
        qs = qs.filter(creada_por=request.user.profesor_perfil.profesor)
    f = TareaFilter(request.GET, queryset=qs)
    tareas = list(f.qs.distinct())
    for t in tareas:
        if t.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
            t.grupos_resumen = [
                {"nombre": g.nombre, "total": g.miembros.count()}
                for g in t.grupos.all()
            ]
    return render(request, "tareas/tarea_list.html", {"filter": f, "tareas": tareas})


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def grupo_miembros_partial(request):
    """HTMX: checkboxes de integrantes según cursos (prefijo del formset)."""
    prefix = request.GET.get("prefix") or request.POST.get("prefix") or "grupos-0"
    curso_ids = request.GET.getlist(f"{prefix}-cursos") or request.POST.getlist(f"{prefix}-cursos")
    field_miembros = f"{prefix}-miembros"
    selected = request.GET.getlist(field_miembros) or request.POST.getlist(field_miembros)
    selected = {int(x) for x in selected if str(x).isdigit()}
    qs = estudiantes_elegibles_para_cursos(curso_ids)
    return render(
        request,
        "tareas/_miembros_checkboxes.html",
        {
            "estudiantes": qs,
            "selected": selected,
            "field_prefix": prefix,
        },
    )


def _form_ctx(form, grupo_formset, title, tarea=None):
    return {
        "form": form,
        "grupo_formset": grupo_formset,
        "title": title,
        "tarea": tarea,
        "anio": anio_escolar_actual(),
    }


def _materias_qs_tarea(request, profesor=None):
    if request.user.is_staff:
        if profesor:
            return profesor.materias.order_by("nombre")
        return Materia.objects.order_by("nombre")
    return request.user.profesor_perfil.profesor.materias.order_by("nombre")


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_create(request):
    staff = request.user.is_staff
    creada_por = None if staff else request.user.profesor_perfil.profesor
    form = TareaForm(
        request.POST or None,
        staff_mode=staff,
        materias_qs=_materias_qs_tarea(request, creada_por),
        creada_por=creada_por,
    )
    grupo_formset = build_grupo_formset(
        data=request.POST if request.method == "POST" else None,
    )
    if request.method == "POST" and form.is_valid():
        tipo = form.cleaned_data.get("tipo_asignacion")
        if tipo == TipoAsignacionTarea.GRUPOS and not grupo_formset.is_valid():
            return render(
                request,
                "tareas/tarea_form.html",
                _form_ctx(form, grupo_formset, "Nueva tarea"),
            )
        form.save(
            commit=True,
            creada_por=creada_por,
            grupo_formset=grupo_formset if tipo == TipoAsignacionTarea.GRUPOS else None,
        )
        messages.success(request, "Tarea creada.")
        return redirect("tareas:tarea_detail", pk=form.instance.pk)
    return render(
        request,
        "tareas/tarea_form.html",
        _form_ctx(form, grupo_formset, "Nueva tarea"),
    )


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_update(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not request.user.is_staff and tarea.creada_por_id != request.user.profesor_perfil.profesor_id:
        messages.error(request, "No puede editar tareas de otro profesor.")
        return redirect("tareas:tarea_list")
    staff = request.user.is_staff
    form = TareaForm(
        request.POST or None,
        instance=tarea,
        staff_mode=staff,
        materias_qs=_materias_qs_tarea(request, tarea.creada_por),
        creada_por=tarea.creada_por,
    )
    grupo_formset = build_grupo_formset(
        data=request.POST if request.method == "POST" else None,
        tarea=tarea,
    )
    if request.method == "POST" and form.is_valid():
        tipo = form.cleaned_data.get("tipo_asignacion")
        if tipo == TipoAsignacionTarea.GRUPOS and not grupo_formset.is_valid():
            return render(
                request,
                "tareas/tarea_form.html",
                _form_ctx(form, grupo_formset, "Editar tarea", tarea),
            )
        form.save(
            commit=True,
            creada_por=tarea.creada_por,
            grupo_formset=grupo_formset if tipo == TipoAsignacionTarea.GRUPOS else None,
        )
        messages.success(request, "Cambios guardados.")
        return redirect("tareas:tarea_detail", pk=tarea.pk)
    return render(
        request,
        "tareas/tarea_form.html",
        _form_ctx(form, grupo_formset, "Editar tarea", tarea),
    )


def _bloques_grupo_tarea(tarea):
    bloques = []
    evals_por_est = {
        ev.estudiante_id: ev
        for ev in tarea.evaluaciones.select_related("estudiante")
    }
    evals_grupo = {
        eg.grupo_id: eg
        for eg in tarea.evaluaciones_grupo.select_related("grupo")
    }
    for grupo in tarea.grupos.prefetch_related("miembros__estudiante").order_by("nombre"):
        miembro_ids = list(grupo.miembros.values_list("estudiante_id", flat=True))
        evaluaciones = [
            evals_por_est[eid]
            for eid in sorted(miembro_ids)
            if eid in evals_por_est
        ]
        evaluaciones.sort(key=lambda e: (e.estudiante.apellido, e.estudiante.nombre))
        bloques.append(
            {
                "grupo": grupo,
                "eval_grupo": evals_grupo.get(grupo.pk),
                "evaluaciones": evaluaciones,
            }
        )
    return bloques


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_detail(request, pk):
    tarea = get_object_or_404(
        Tarea.objects.prefetch_related("grados", "grupos"),
        pk=pk,
    )
    if not request.user.is_staff and tarea.creada_por_id != request.user.profesor_perfil.profesor_id:
        messages.error(request, "No autorizado.")
        return redirect("tareas:tarea_list")
    evals = tarea.evaluaciones.select_related("estudiante").order_by("estudiante__apellido")
    f = TareaEvaluacionFilter(request.GET, queryset=evals)
    ctx = {"tarea": tarea, "filter": f}
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        filtrados = set(f.qs.values_list("pk", flat=True))
        bloques = _bloques_grupo_tarea(tarea)
        for bloque in bloques:
            bloque["evaluaciones"] = [
                e for e in bloque["evaluaciones"] if e.pk in filtrados
            ]
        ctx["bloques_grupo"] = bloques
    return render(request, "tareas/tarea_detail.html", ctx)


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_delete(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not request.user.is_staff and tarea.creada_por_id != request.user.profesor_perfil.profesor_id:
        raise Http404()
    if request.method == "POST":
        tarea.delete()
        messages.success(request, "Tarea eliminada.")
        return redirect("tareas:tarea_list")
    return render(request, "tareas/tarea_delete.html", {"tarea": tarea})


@login_required
@user_passes_test(staff_o_profesor, login_url=settings.LOGIN_URL)
def tarea_evaluar(request, pk):
    tarea = get_object_or_404(Tarea, pk=pk)
    if not request.user.is_staff and tarea.creada_por_id != request.user.profesor_perfil.profesor_id:
        messages.error(request, "No autorizado.")
        return redirect("tareas:tarea_list")

    for grupo in tarea.grupos.all():
        asegurar_evaluaciones_grupo(tarea, grupo)

    EvalFormSet = modelformset_factory(
        TareaEvaluacion,
        form=TareaEvaluacionForm,
        extra=0,
    )
    qs = tarea.evaluaciones.select_related("estudiante").order_by("estudiante__apellido")
    if request.method == "POST":
        formset = EvalFormSet(request.POST, queryset=qs, form_kwargs={"modalidad": tarea.modalidad})
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                obj.actualizado_por = request.user
                obj.save()
            if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
                for grupo in tarea.grupos.all():
                    texto = request.POST.get(f"obs_grupo_{grupo.pk}", "")
                    evg, _ = TareaGrupoEvaluacion.objects.get_or_create(
                        tarea=tarea, grupo=grupo
                    )
                    evg.observacion_general = texto
                    evg.actualizado_por = request.user
                    evg.save()
            messages.success(request, "Evaluaciones guardadas.")
            return redirect("tareas:tarea_detail", pk=tarea.pk)
    else:
        formset = EvalFormSet(queryset=qs, form_kwargs={"modalidad": tarea.modalidad})

    ctx = {
        "tarea": tarea,
        "formset": formset,
        "rubrica_items": rubrica_items(tarea.modalidad),
    }
    if tarea.tipo_asignacion == TipoAsignacionTarea.GRUPOS:
        bloques = _bloques_grupo_tarea(tarea)
        forms_by_id = {f.instance.pk: f for f in formset}
        for bloque in bloques:
            bloque["forms"] = [
                forms_by_id[ev.pk]
                for ev in bloque["evaluaciones"]
                if ev.pk in forms_by_id
            ]
        ctx["bloques_grupo"] = bloques
    return render(request, "tareas/tarea_evaluar.html", ctx)
