from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .asistencia_utils import calendario_asistencia_estudiante, dias_lectivos_mes
from .curso_utils import anio_escolar_actual, sincronizar_cursos_desde_estudiantes
from .forms import (
    CursoForm,
    EvaluacionP1Form,
    NotaCursoForm,
    PlanificacionForm,
    RegistroProgresoP2Form,
)
from .models import (
    Asistencia,
    Curso,
    EvaluacionP1,
    Materia,
    NotaCurso,
    Planificacion,
    RegistroProgresoP2,
)
from .participacion_utils import resumen_participacion_estudiantes
from .puntaje_utils import total_bruto_estudiantes_map
from .views import school_access


def _profesor_de_request(request):
    pp = getattr(request.user, "profesor_perfil", None)
    return pp.profesor if pp else None


def _materias_para_usuario(request):
    if request.user.is_staff:
        return Materia.objects.all()
    profesor = _profesor_de_request(request)
    if profesor:
        return profesor.materias.all()
    return Materia.objects.none()


# ── Cursos ─────────────────────────────────────────────────────────────


@school_access
def curso_list(request):
    anio = request.GET.get("anio", anio_escolar_actual())
    if request.method == "POST" and request.POST.get("action") == "sincronizar":
        n = sincronizar_cursos_desde_estudiantes(anio_escolar=anio)
        messages.success(request, f"Se crearon {n} curso(s) nuevo(s) para {anio}.")
        return redirect(f"{request.path}?anio={anio}")

    cursos = Curso.objects.filter(anio_escolar=anio).order_by("grado", "seccion")
    anios = list(
        Curso.objects.values_list("anio_escolar", flat=True)
        .distinct()
        .order_by("-anio_escolar")
    )
    if anio not in anios:
        anios = [anio] + anios

    for curso in cursos:
        curso.total_estudiantes = curso.estudiantes_qs().count()

    return render(
        request,
        "core/cursos/list.html",
        {
            "cursos": cursos,
            "anio": anio,
            "anios": anios,
            "anio_actual": anio_escolar_actual(),
        },
    )


@school_access
def curso_create(request):
    form = CursoForm(
        request.POST or None, initial={"anio_escolar": anio_escolar_actual()}
    )
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoChanged"})
    return render(
        request, "core/cursos/form_curso.html", {"form": form, "title": "Nuevo curso"}
    )


@school_access
def curso_detail(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    tab = request.GET.get("tab", "notas")
    materias = _materias_para_usuario(request)

    notas = (
        curso.notas.select_related("materia", "creado_por")
        .prefetch_related("estudiantes")
        .all()
    )
    planificaciones = curso.planificaciones.select_related(
        "materia", "creado_por"
    ).all()
    evaluaciones_p1 = (
        curso.evaluaciones_p1.select_related("materia", "creado_por")
        .prefetch_related("registros_p2")
        .all()
    )

    tipo_plan = request.GET.get("tipo_plan", "")
    if tipo_plan:
        planificaciones = planificaciones.filter(tipo=tipo_plan)

    return render(
        request,
        "core/cursos/detail.html",
        {
            "curso": curso,
            "tab": tab,
            "notas": notas,
            "planificaciones": planificaciones,
            "evaluaciones_p1": evaluaciones_p1,
            "materias": materias,
            "tipo_plan": tipo_plan,
            "total_estudiantes": curso.estudiantes_qs().count(),
        },
    )


# ── Notas de curso ─────────────────────────────────────────────────────


@school_access
def nota_curso_create(request, curso_pk):
    curso = get_object_or_404(Curso, pk=curso_pk)
    form = NotaCursoForm(
        request.POST or None,
        curso=curso,
        materias_qs=_materias_para_usuario(request),
    )
    if request.method == "POST" and form.is_valid():
        nota = form.save(commit=False)
        nota.curso = curso
        nota.creado_por = _profesor_de_request(request)
        nota.save()
        form.save_m2m()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoNotaChanged"})
    return render(
        request,
        "core/cursos/nota_form.html",
        {"form": form, "curso": curso, "title": "Nueva nota del curso"},
    )


@school_access
def nota_curso_delete(request, pk):
    nota = get_object_or_404(NotaCurso, pk=pk)
    curso_pk = nota.curso_id
    if request.method == "POST":
        nota.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoNotaChanged"})
    return render(
        request,
        "core/cursos/nota_delete.html",
        {"object": nota, "curso_pk": curso_pk},
    )


# ── Planificación ──────────────────────────────────────────────────────


@school_access
def planificacion_create(request, curso_pk):
    curso = get_object_or_404(Curso, pk=curso_pk)
    tipo = request.GET.get("tipo", "DIARIA")
    form = PlanificacionForm(
        request.POST or None,
        materias_qs=_materias_para_usuario(request),
        initial={"tipo": tipo},
    )
    if request.method == "POST" and form.is_valid():
        plan = form.save(commit=False)
        plan.curso = curso
        plan.creado_por = _profesor_de_request(request)
        plan.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoPlanChanged"})
    titulo = "Planificación diaria" if tipo == "DIARIA" else "Planificación general"
    return render(
        request,
        "core/cursos/planificacion_form.html",
        {
            "form": form,
            "curso": curso,
            "title": titulo,
            "rich_field": "id_contenido",
        },
    )


@school_access
def planificacion_update(request, pk):
    plan = get_object_or_404(Planificacion, pk=pk)
    form = PlanificacionForm(
        request.POST or None,
        instance=plan,
        materias_qs=_materias_para_usuario(request),
    )
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.creado_por = obj.creado_por or _profesor_de_request(request)
        obj.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoPlanChanged"})
    return render(
        request,
        "core/cursos/planificacion_form.html",
        {
            "form": form,
            "curso": plan.curso,
            "title": "Editar planificación",
            "rich_field": "id_contenido",
            "initial_html": plan.contenido,
        },
    )


@school_access
def planificacion_delete(request, pk):
    plan = get_object_or_404(Planificacion, pk=pk)
    curso_pk = plan.curso_id
    if request.method == "POST":
        plan.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoPlanChanged"})
    return render(
        request,
        "core/cursos/planificacion_delete.html",
        {"object": plan, "curso_pk": curso_pk},
    )


# ── Evaluación P1 / P2 ─────────────────────────────────────────────────


@school_access
def evaluacion_p1_create(request, curso_pk):
    curso = get_object_or_404(Curso, pk=curso_pk)
    form = EvaluacionP1Form(
        request.POST or None,
        request.FILES or None,
        materias_qs=_materias_para_usuario(request),
        curso=curso,
    )
    if request.method == "POST" and form.is_valid():
        ev = form.save(commit=False)
        ev.curso = curso
        ev.creado_por = _profesor_de_request(request)
        ev.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p1_form.html",
        {"form": form, "curso": curso, "title": "Evaluación diagnóstica P1"},
    )


@school_access
def evaluacion_p1_update(request, pk):
    ev = get_object_or_404(EvaluacionP1, pk=pk)
    form = EvaluacionP1Form(
        request.POST or None,
        request.FILES or None,
        instance=ev,
        materias_qs=_materias_para_usuario(request),
        curso=ev.curso,
    )
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.creado_por = obj.creado_por or _profesor_de_request(request)
        obj.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p1_form.html",
        {
            "form": form,
            "curso": ev.curso,
            "title": "Editar evaluación P1",
            "evaluacion": ev,
        },
    )


@school_access
def evaluacion_p1_delete(request, pk):
    ev = get_object_or_404(EvaluacionP1, pk=pk)
    if request.method == "POST":
        ev.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p1_delete.html",
        {"object": ev, "curso_pk": ev.curso_id},
    )


@school_access
def registro_p2_create(request, p1_pk):
    p1 = get_object_or_404(EvaluacionP1, pk=p1_pk)
    form = RegistroProgresoP2Form(request.POST or None)
    if request.method == "POST" and form.is_valid():
        reg = form.save(commit=False)
        reg.evaluacion_p1 = p1
        reg.creado_por = _profesor_de_request(request)
        reg.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p2_form.html",
        {"form": form, "evaluacion_p1": p1, "title": "Registro de progreso P2"},
    )


@school_access
def registro_p2_update(request, pk):
    reg = get_object_or_404(RegistroProgresoP2, pk=pk)
    form = RegistroProgresoP2Form(request.POST or None, instance=reg)
    if request.method == "POST" and form.is_valid():
        obj = form.save(commit=False)
        obj.creado_por = obj.creado_por or _profesor_de_request(request)
        obj.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p2_form.html",
        {
            "form": form,
            "evaluacion_p1": reg.evaluacion_p1,
            "title": "Editar registro P2",
            "registro": reg,
        },
    )


@school_access
def registro_p2_delete(request, pk):
    reg = get_object_or_404(RegistroProgresoP2, pk=pk)
    if request.method == "POST":
        reg.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "cursoP1Changed"})
    return render(
        request,
        "core/cursos/p2_delete.html",
        {"object": reg, "curso_pk": reg.evaluacion_p1.curso_id},
    )


@school_access
def curso_curriculum(request, pk):
    curso = get_object_or_404(Curso, pk=pk)
    hoy = timezone.localdate()
    try:
        mes = int(request.GET.get("mes", hoy.month))
        anio = int(request.GET.get("anio", hoy.year))
    except ValueError:
        mes, anio = hoy.month, hoy.year

    meses = [
        (1, "Enero"),
        (2, "Febrero"),
        (3, "Marzo"),
        (4, "Abril"),
        (5, "Mayo"),
        (6, "Junio"),
        (7, "Julio"),
        (8, "Agosto"),
        (9, "Septiembre"),
        (10, "Octubre"),
        (11, "Noviembre"),
        (12, "Diciembre"),
    ]

    materia_id = request.GET.get("materia", "")
    materias = _materias_para_usuario(request)
    mid = int(materia_id) if materia_id.isdigit() else None

    estudiantes = list(curso.estudiantes_qs().order_by("apellido", "nombre"))
    eids = [e.pk for e in estudiantes]

    fecha_inicio, fecha_fin, _ = dias_lectivos_mes(mes, anio)
    asistencias = Asistencia.objects.filter(
        estudiante_id__in=eids,
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
    )
    asist_map = {}
    for a in asistencias:
        asist_map.setdefault(a.estudiante_id, []).append(a.estado)

    pts_map = resumen_participacion_estudiantes(eids, materia_id=mid)

    # --- P1/P2 para supervisión pedagógica ---
    evaluaciones_p1 = (
        curso.evaluaciones_p1.select_related("materia", "creado_por")
        .prefetch_related("registros_p2")
        .all()
    )
    if mid:
        evaluaciones_p1 = evaluaciones_p1.filter(materia_id=mid)

    tarea_map = {}
    promedio_normalizado = None
    try:
        from tareas.models import ModalidadTarea, TareaEvaluacion
        from tareas.rubricas import promedio_normalizado as _prom_norm

        promedio_normalizado = _prom_norm

        evals = list(
            TareaEvaluacion.objects.filter(
                estudiante_id__in=eids,
                puntaje__isnull=False,
            ).select_related("tarea")
        )
        tarea_map = {}
        for ev in evals:
            t = tarea_map.setdefault(
                ev.estudiante_id, {"oral": [], "escrita": [], "all": []}
            )
            t["all"].append(ev)
            if ev.tarea.modalidad == ModalidadTarea.ORAL:
                t["oral"].append(ev)
            else:
                t["escrita"].append(ev)
    except Exception:
        tarea_map = {}

    filas = []
    prom_tareas_map = {}
    for eid in eids:
        tm = tarea_map.get(eid, {"all": []})
        prom_tareas_map[eid] = (
            promedio_normalizado(tm["all"])
            if promedio_normalizado and tm.get("all")
            else None
        )
    bruto_map = total_bruto_estudiantes_map(eids, prom_tareas_map, materia_id=mid)

    for est in estudiantes:
        estados = asist_map.get(est.pk, [])
        p = sum(1 for s in estados if s == "P")
        a = sum(1 for s in estados if s == "A")
        total = len([s for s in estados if s])
        pct = round(p / total * 100, 1) if total else 0

        pts = pts_map.get(
            est.pk, {"balance": 0, "positivos": 0, "negativos": 0, "bonos": 0}
        )
        part_total = pts["balance"] + pts.get("bonos", 0)

        bruto = bruto_map.get(
            est.pk, {"total_bruto": 0, "tareas_bruta_10": 0, "bono_manual": 0}
        )
        tm = tarea_map.get(est.pk, {"oral": [], "escrita": [], "all": []})
        prom_oral = (
            promedio_normalizado(tm["oral"])
            if promedio_normalizado and tm.get("oral")
            else None
        )
        prom_esc = (
            promedio_normalizado(tm["escrita"])
            if promedio_normalizado and tm.get("escrita")
            else None
        )
        prom_tareas_pct = (
            promedio_normalizado(tm["all"])
            if promedio_normalizado and tm.get("all")
            else None
        )

        alertas = []
        if total and pct < 75:
            alertas.append("Baja asistencia")
        if pts["balance"] < 0:
            alertas.append("Balance negativo")
        if prom_oral is not None and prom_oral < 60:
            alertas.append("Comprensión baja")
        if prom_esc is not None and prom_esc < 60:
            alertas.append("Cuaderno bajo")
        if bruto["total_bruto"] < 0:
            alertas.append("Bruto bajo")

        filas.append(
            {
                "estudiante": est,
                "asist_p": p,
                "asist_a": a,
                "asist_pct": pct,
                "participacion": part_total,
                "balance": pts["balance"],
                "positivos": pts["positivos"],
                "negativos": pts["negativos"],
                "bonos": pts.get("bonos", 0),
                "cuaderno": prom_esc,
                "comprension": prom_oral,
                "prom_tareas_pct": prom_tareas_pct,
                "tareas_bruta_10": bruto["tareas_bruta_10"],
                "bono_manual": bruto["bono_manual"],
                "total_bruto": bruto["total_bruto"],
                "alertas": alertas,
                "score_orden": (len(alertas), bruto["total_bruto"], pct),
            }
        )

    filas.sort(key=lambda f: (-len(f["alertas"]), f["balance"], f["asist_pct"]))

    notas = (
        curso.notas.select_related("materia", "creado_por")
        .prefetch_related("estudiantes")
        .all()[:10]
    )

    return render(
        request,
        "core/cursos/curriculum.html",
        {
            "curso": curso,
            "mes": mes,
            "anio": anio,
            "meses": meses,
            "materias": materias,
            "materia_id": materia_id,
            "filas": filas,
            "notas": notas,
            "evaluaciones_p1": evaluaciones_p1,
        },
    )
