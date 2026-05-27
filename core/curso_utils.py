"""Utilidades para cursos y año escolar (República Dominicana)."""

from django.utils import timezone

from .models import Curso, Estudiante, GRADO_CHOICES


def anio_escolar_actual(fecha=None):
    """
    Año escolar dominicano (agosto–julio).
    Ej.: agosto 2025 → '2025-2026'; marzo 2026 → '2025-2026'.
    """
    if fecha is None:
        fecha = timezone.localdate()
    if fecha.month >= 8:
        return f"{fecha.year}-{fecha.year + 1}"
    return f"{fecha.year - 1}-{fecha.year}"


def sincronizar_cursos_desde_estudiantes(anio_escolar=None):
    """Crea registros Curso para cada combinación grado+sección con estudiantes."""
    if anio_escolar is None:
        anio_escolar = anio_escolar_actual()
    pares = (
        Estudiante.objects.values_list("grado", "seccion")
        .distinct()
        .order_by("grado", "seccion")
    )
    creados = 0
    for grado, seccion in pares:
        _, created = Curso.objects.get_or_create(
            grado=grado,
            seccion=seccion or "A",
            anio_escolar=anio_escolar,
        )
        if created:
            creados += 1
    return creados


def etiqueta_grado(grado):
    return dict(GRADO_CHOICES).get(grado, grado)
