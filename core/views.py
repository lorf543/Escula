from datetime import date, timedelta
import calendar

from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import (
    AsistenciaForm,
    EstudianteForm,
    MateriaForm,
    ObservacionForm,
    ParticipacionForm,
    ProfesorForm,
)
from .models import (
    Asistencia, Estudiante, Materia, Observacion, Participacion, Profesor, GRADO_CHOICES,
)


# ── Dashboard ──────────────────────────────────────────────────────────


def dashboard(request):
    ctx = {
        "total_estudiantes": Estudiante.objects.count(),
        "total_profesores": Profesor.objects.count(),
        "total_materias": Materia.objects.count(),
        "total_observaciones": Observacion.objects.count(),
        "ultimas_observaciones": Observacion.objects.select_related("estudiante")[:5],
        "estudiantes_por_grado": (
            Estudiante.objects.values("grado")
            .annotate(total=Count("id"))
            .order_by("grado")
        ),
    }
    return render(request, "core/dashboard.html", ctx)


# ── Materias CRUD ──────────────────────────────────────────────────────


def materia_list(request):
    q = request.GET.get("q", "")
    materias = Materia.objects.all()
    if q:
        materias = materias.filter(
            Q(nombre__icontains=q) | Q(codigo__icontains=q)
        )
    if request.htmx:
        return render(request, "core/materias/table.html", {"materias": materias, "q": q})
    return render(request, "core/materias/list.html", {"materias": materias, "q": q})


def materia_create(request):
    form = MateriaForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "materiaChanged"})
    return render(request, "core/materias/form.html", {"form": form, "title": "Nueva Materia"})


def materia_update(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    form = MateriaForm(request.POST or None, instance=materia)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "materiaChanged"})
    return render(request, "core/materias/form.html", {"form": form, "title": "Editar Materia"})


def materia_delete(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == "POST":
        materia.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "materiaChanged"})
    return render(request, "core/materias/delete.html", {"object": materia})


# ── Profesores CRUD ────────────────────────────────────────────────────


def profesor_list(request):
    q = request.GET.get("q", "")
    profesores = Profesor.objects.prefetch_related("materias").all()
    if q:
        profesores = profesores.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(cedula__icontains=q)
        )
    if request.htmx:
        return render(request, "core/profesores/table.html", {"profesores": profesores, "q": q})
    return render(request, "core/profesores/list.html", {"profesores": profesores, "q": q})


def profesor_create(request):
    form = ProfesorForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "profesorChanged"})
    return render(request, "core/profesores/form.html", {"form": form, "title": "Nuevo Profesor"})


def profesor_update(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    form = ProfesorForm(request.POST or None, instance=profesor)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "profesorChanged"})
    return render(request, "core/profesores/form.html", {"form": form, "title": "Editar Profesor"})


def profesor_detail(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    return render(request, "core/profesores/detail.html", {"profesor": profesor})


def profesor_delete(request, pk):
    profesor = get_object_or_404(Profesor, pk=pk)
    if request.method == "POST":
        profesor.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "profesorChanged"})
    return render(request, "core/profesores/delete.html", {"object": profesor})


# ── Estudiantes CRUD ───────────────────────────────────────────────────


def estudiante_list(request):
    q = request.GET.get("q", "")
    grado = request.GET.get("grado", "")
    estudiantes = Estudiante.objects.prefetch_related("profesores").all()
    if q:
        estudiantes = estudiantes.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(cedula__icontains=q)
        )
    if grado:
        estudiantes = estudiantes.filter(grado=grado)
    ctx = {"estudiantes": estudiantes, "q": q, "grado": grado}
    if request.htmx:
        return render(request, "core/estudiantes/table.html", ctx)
    return render(request, "core/estudiantes/list.html", ctx)


def estudiante_create(request):
    form = EstudianteForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "estudianteChanged"})
    return render(
        request, "core/estudiantes/form.html", {"form": form, "title": "Nuevo Estudiante"}
    )


def estudiante_update(request, pk):
    est = get_object_or_404(Estudiante, pk=pk)
    form = EstudianteForm(request.POST or None, instance=est)
    if request.method == "POST" and form.is_valid():
        form.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "estudianteChanged"})
    return render(
        request, "core/estudiantes/form.html", {"form": form, "title": "Editar Estudiante"}
    )


def _get_materias_estudiante(est):
    """Get all materias available to a student through their assigned professors."""
    return Materia.objects.filter(profesores__in=est.profesores.all()).distinct()


def estudiante_detail(request, pk):
    est = get_object_or_404(Estudiante, pk=pk)
    observaciones = est.observaciones.select_related("materia").all()
    participaciones = est.participaciones.select_related("materia").all()
    total_asist = est.asistencias.count()
    presentes = est.asistencias.filter(estado="P").count()
    pct = round(presentes / total_asist * 100, 1) if total_asist else 0

    materias = _get_materias_estudiante(est)
    puntos_por_materia = []
    for m in materias:
        positivos = participaciones.filter(materia=m, tipo="POSITIVO").count()
        negativos = participaciones.filter(materia=m, tipo="NEGATIVO").count()
        puntos_por_materia.append({
            "materia": m,
            "positivos": positivos,
            "negativos": negativos,
            "balance": positivos - negativos,
        })

    total_pos = participaciones.filter(tipo="POSITIVO").count()
    total_neg = participaciones.filter(tipo="NEGATIVO").count()

    ctx = {
        "estudiante": est,
        "observaciones": observaciones,
        "participaciones": participaciones,
        "total_asistencias": total_asist,
        "presentes": presentes,
        "pct_asistencia": pct,
        "puntos_por_materia": puntos_por_materia,
        "total_positivos": total_pos,
        "total_negativos": total_neg,
        "balance_total": total_pos - total_neg,
    }
    return render(request, "core/estudiantes/detail.html", ctx)


def estudiante_delete(request, pk):
    est = get_object_or_404(Estudiante, pk=pk)
    if request.method == "POST":
        est.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "estudianteChanged"})
    return render(request, "core/estudiantes/delete.html", {"object": est})


# ── Observaciones ──────────────────────────────────────────────────────


def observacion_create(request, estudiante_pk):
    est = get_object_or_404(Estudiante, pk=estudiante_pk)
    materias = _get_materias_estudiante(est)
    form = ObservacionForm(request.POST or None, materias_qs=materias)
    if request.method == "POST" and form.is_valid():
        obs = form.save(commit=False)
        obs.estudiante = est
        obs.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "observacionChanged"})
    return render(
        request,
        "core/observaciones/form.html",
        {"form": form, "estudiante": est, "title": "Nueva Observación"},
    )


def observacion_delete(request, pk):
    obs = get_object_or_404(Observacion, pk=pk)
    if request.method == "POST":
        obs.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "observacionChanged"})
    return render(request, "core/observaciones/delete.html", {"object": obs})


def observacion_list_partial(request, estudiante_pk):
    est = get_object_or_404(Estudiante, pk=estudiante_pk)
    observaciones = est.observaciones.select_related("materia").all()
    return render(
        request,
        "core/observaciones/list_partial.html",
        {"observaciones": observaciones, "estudiante": est},
    )


# ── Participación ─────────────────────────────────────────────────────


def participacion_create(request, estudiante_pk):
    est = get_object_or_404(Estudiante, pk=estudiante_pk)
    materias = _get_materias_estudiante(est)
    form = ParticipacionForm(request.POST or None, materias_qs=materias)
    if request.method == "POST" and form.is_valid():
        part = form.save(commit=False)
        part.estudiante = est
        part.save()
        return HttpResponse(status=204, headers={"HX-Trigger": "participacionChanged"})
    return render(
        request,
        "core/participaciones/form.html",
        {"form": form, "estudiante": est, "title": "Nuevo Punto"},
    )


def participacion_delete(request, pk):
    part = get_object_or_404(Participacion, pk=pk)
    if request.method == "POST":
        part.delete()
        return HttpResponse(status=204, headers={"HX-Trigger": "participacionChanged"})
    return render(request, "core/participaciones/delete.html", {"object": part})


def participacion_list_partial(request, estudiante_pk):
    est = get_object_or_404(Estudiante, pk=estudiante_pk)
    participaciones = est.participaciones.select_related("materia").all()

    materias = _get_materias_estudiante(est)
    puntos_por_materia = []
    for m in materias:
        positivos = participaciones.filter(materia=m, tipo="POSITIVO").count()
        negativos = participaciones.filter(materia=m, tipo="NEGATIVO").count()
        puntos_por_materia.append({
            "materia": m,
            "positivos": positivos,
            "negativos": negativos,
            "balance": positivos - negativos,
        })

    return render(
        request,
        "core/participaciones/list_partial.html",
        {
            "participaciones": participaciones,
            "estudiante": est,
            "puntos_por_materia": puntos_por_materia,
        },
    )


# ── Asistencia ─────────────────────────────────────────────────────────


def asistencia_view(request):
    hoy = date.today()
    fecha_str = request.GET.get("fecha")
    grado = request.GET.get("grado", "")

    try:
        fecha = date.fromisoformat(fecha_str) if fecha_str else hoy
    except ValueError:
        fecha = hoy

    if not grado:
        ctx = {
            "fecha": fecha,
            "grado": grado,
            "grados": GRADO_CHOICES,
            "registros": [],
            "sin_grado": True,
        }
        return render(request, "core/asistencia/list.html", ctx)

    estudiantes = Estudiante.objects.filter(grado=grado).order_by("apellido", "nombre")

    registros = []
    for est in estudiantes:
        asist, _ = Asistencia.objects.get_or_create(
            estudiante=est, fecha=fecha, defaults={"estado": "P"}
        )
        registros.append({"estudiante": est, "asistencia": asist})

    total = len(registros)
    presentes = sum(1 for r in registros if r["asistencia"].estado == "P")
    ausentes = sum(1 for r in registros if r["asistencia"].estado == "A")
    tardanzas = sum(1 for r in registros if r["asistencia"].estado == "T")
    excusas = sum(1 for r in registros if r["asistencia"].estado == "E")

    ctx = {
        "fecha": fecha,
        "grado": grado,
        "grado_display": dict(GRADO_CHOICES).get(grado, grado),
        "registros": registros,
        "grados": GRADO_CHOICES,
        "sin_grado": False,
        "resumen": {
            "total": total,
            "presentes": presentes,
            "ausentes": ausentes,
            "tardanzas": tardanzas,
            "excusas": excusas,
        },
    }

    if request.htmx:
        return render(request, "core/asistencia/table.html", ctx)
    return render(request, "core/asistencia/list.html", ctx)


@require_POST
def asistencia_toggle(request, pk):
    asist = get_object_or_404(Asistencia, pk=pk)
    estados = ["P", "A", "T", "E"]
    idx = estados.index(asist.estado) if asist.estado in estados else 0
    asist.estado = estados[(idx + 1) % len(estados)]
    asist.save()
    return render(request, "core/asistencia/badge.html", {"asistencia": asist})


def asistencia_historial(request):
    grado = request.GET.get("grado", "")
    mes_str = request.GET.get("mes", "")
    anio_str = request.GET.get("anio", "")

    hoy = date.today()
    try:
        mes = int(mes_str) if mes_str else hoy.month
        anio = int(anio_str) if anio_str else hoy.year
    except ValueError:
        mes, anio = hoy.month, hoy.year

    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]

    if not grado:
        ctx = {
            "grado": grado,
            "grados": GRADO_CHOICES,
            "mes": mes,
            "anio": anio,
            "meses": meses,
            "sin_grado": True,
        }
        return render(request, "core/asistencia/historial.html", ctx)

    _, last_day = calendar.monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, last_day)

    dias_lectivos = []
    d = fecha_inicio
    while d <= fecha_fin:
        if d.weekday() < 5:  # Lun-Vie
            dias_lectivos.append(d)
        d += timedelta(days=1)

    estudiantes = Estudiante.objects.filter(grado=grado).order_by("apellido", "nombre")

    asistencias_qs = Asistencia.objects.filter(
        estudiante__grado=grado,
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
    ).select_related("estudiante")

    asist_map = {}
    for a in asistencias_qs:
        asist_map[(a.estudiante_id, a.fecha)] = a.estado

    filas = []
    for est in estudiantes:
        estados = []
        p_count = a_count = t_count = e_count = 0
        for dia in dias_lectivos:
            estado = asist_map.get((est.id, dia), "")
            estados.append(estado)
            if estado == "P":
                p_count += 1
            elif estado == "A":
                a_count += 1
            elif estado == "T":
                t_count += 1
            elif estado == "E":
                e_count += 1
        total_reg = p_count + a_count + t_count + e_count
        pct = round(p_count / total_reg * 100, 1) if total_reg else 0
        filas.append({
            "estudiante": est,
            "estados": estados,
            "presentes": p_count,
            "ausentes": a_count,
            "tardanzas": t_count,
            "excusas": e_count,
            "pct": pct,
        })

    ctx = {
        "grado": grado,
        "grado_display": dict(GRADO_CHOICES).get(grado, grado),
        "grados": GRADO_CHOICES,
        "mes": mes,
        "anio": anio,
        "meses": meses,
        "mes_display": dict(meses).get(mes, ""),
        "dias_lectivos": dias_lectivos,
        "filas": filas,
        "sin_grado": False,
        "total_estudiantes": len(filas),
    }

    if request.htmx:
        return render(request, "core/asistencia/historial_table.html", ctx)
    return render(request, "core/asistencia/historial.html", ctx)


def asistencia_exportar(request):
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

    grado = request.GET.get("grado", "")
    mes_str = request.GET.get("mes", "")
    anio_str = request.GET.get("anio", "")

    hoy = date.today()
    try:
        mes = int(mes_str) if mes_str else hoy.month
        anio = int(anio_str) if anio_str else hoy.year
    except ValueError:
        mes, anio = hoy.month, hoy.year

    meses_nombres = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre",
    }

    _, last_day = calendar.monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, last_day)

    dias_lectivos = []
    d = fecha_inicio
    while d <= fecha_fin:
        if d.weekday() < 5:
            dias_lectivos.append(d)
        d += timedelta(days=1)

    if grado:
        estudiantes = Estudiante.objects.filter(grado=grado).order_by("apellido", "nombre")
        grados_export = [(grado, dict(GRADO_CHOICES).get(grado, grado), estudiantes)]
    else:
        grados_export = []
        for g_val, g_label in GRADO_CHOICES:
            ests = Estudiante.objects.filter(grado=g_val).order_by("apellido", "nombre")
            if ests.exists():
                grados_export.append((g_val, g_label, ests))

    asist_qs = Asistencia.objects.filter(
        fecha__gte=fecha_inicio, fecha__lte=fecha_fin,
    ).select_related("estudiante")
    if grado:
        asist_qs = asist_qs.filter(estudiante__grado=grado)

    asist_map = {}
    for a in asist_qs:
        asist_map[(a.estudiante_id, a.fecha)] = a.get_estado_display()

    wb = openpyxl.Workbook()
    wb.remove(wb.active)

    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="2F5496", end_color="2F5496", fill_type="solid")
    center = Alignment(horizontal="center", vertical="center")
    thin = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin"),
    )
    estado_fills = {
        "Presente": PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid"),
        "Ausente": PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid"),
        "Tardanza": PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid"),
        "Excusa": PatternFill(start_color="B4C6E7", end_color="B4C6E7", fill_type="solid"),
    }
    estado_fonts = {
        "Presente": Font(color="006100", size=10),
        "Ausente": Font(color="9C0006", size=10),
        "Tardanza": Font(color="9C6500", size=10),
        "Excusa": Font(color="003366", size=10),
    }

    for g_val, g_label, estudiantes in grados_export:
        ws = wb.create_sheet(title=g_label[:31])

        ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=3 + len(dias_lectivos))
        title = ws.cell(
            row=1, column=1,
            value=f"Asistencia - {g_label} - {meses_nombres[mes]} {anio}",
        )
        title.font = Font(bold=True, size=14, color="2F5496")
        title.alignment = center

        headers = ["#", "Apellido", "Nombre"]
        for dia in dias_lectivos:
            headers.append(dia.strftime("%d"))
        headers += ["P", "A", "T", "E", "%"]

        for col_idx, h in enumerate(headers, 1):
            cell = ws.cell(row=3, column=col_idx, value=h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center
            cell.border = thin

        for i, est in enumerate(estudiantes):
            row = 4 + i
            ws.cell(row=row, column=1, value=i + 1).border = thin
            ws.cell(row=row, column=1).alignment = center
            ws.cell(row=row, column=2, value=est.apellido).border = thin
            ws.cell(row=row, column=3, value=est.nombre).border = thin

            p = a = t = e = 0
            for j, dia in enumerate(dias_lectivos):
                col = 4 + j
                estado_str = asist_map.get((est.id, dia), "")
                cell = ws.cell(row=row, column=col, value=estado_str[:1] if estado_str else "")
                cell.alignment = center
                cell.border = thin
                if estado_str in estado_fills:
                    cell.fill = estado_fills[estado_str]
                    cell.font = estado_fonts[estado_str]
                if estado_str == "Presente":
                    p += 1
                elif estado_str == "Ausente":
                    a += 1
                elif estado_str == "Tardanza":
                    t += 1
                elif estado_str == "Excusa":
                    e += 1

            summary_col = 4 + len(dias_lectivos)
            for offset, val in enumerate([p, a, t, e]):
                cell = ws.cell(row=row, column=summary_col + offset, value=val)
                cell.alignment = center
                cell.border = thin

            total_reg = p + a + t + e
            pct = round(p / total_reg * 100, 1) if total_reg else 0
            pct_cell = ws.cell(row=row, column=summary_col + 4, value=pct / 100)
            pct_cell.number_format = "0.0%"
            pct_cell.alignment = center
            pct_cell.border = thin

        ws.column_dimensions["A"].width = 5
        ws.column_dimensions["B"].width = 22
        ws.column_dimensions["C"].width = 20

    mes_nombre = meses_nombres.get(mes, str(mes))
    grado_str = grado if grado else "Todos"
    filename = f"Asistencia_{grado_str}_{mes_nombre}_{anio}.xlsx"

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
