import calendar
from datetime import date, timedelta

from .models import Asistencia


def dias_lectivos_mes(mes, anio):
    _, last_day = calendar.monthrange(anio, mes)
    fecha_inicio = date(anio, mes, 1)
    fecha_fin = date(anio, mes, last_day)
    dias = []
    d = fecha_inicio
    while d <= fecha_fin:
        if d.weekday() < 5:
            dias.append(d)
        d += timedelta(days=1)
    return fecha_inicio, fecha_fin, dias


def calendario_asistencia_estudiante(estudiante, mes, anio):
    fecha_inicio, fecha_fin, dias_lectivos = dias_lectivos_mes(mes, anio)
    asistencias = Asistencia.objects.filter(
        estudiante=estudiante,
        fecha__gte=fecha_inicio,
        fecha__lte=fecha_fin,
    )
    asist_map = {a.fecha: a.estado for a in asistencias}

    estados = []
    p_count = a_count = t_count = e_count = 0
    for dia in dias_lectivos:
        estado = asist_map.get(dia, "")
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

    return {
        "mes": mes,
        "anio": anio,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "dias_lectivos": dias_lectivos,
        "estados": estados,
        "presentes": p_count,
        "ausentes": a_count,
        "tardanzas": t_count,
        "excusas": e_count,
        "pct": pct,
    }
