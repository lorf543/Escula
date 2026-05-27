"""Normalización de cédula electoral dominicana (solo dígitos para comparar)."""


def normalizar_cedula(valor: str) -> str:
    if not valor:
        return ""
    return "".join(c for c in str(valor).strip() if c.isdigit())


def cedula_valida_formato(valor: str) -> bool:
    """Once dígitos (cédula nueva RD)."""
    n = normalizar_cedula(valor)
    return len(n) == 11


def estudiantes_por_cedula_normalizada(norm: str):
    """Todos los estudiantes cuya cédula normalizada coincide (asignación automática al padre)."""
    from core.models import Estudiante

    if not norm:
        return Estudiante.objects.none()
    ids = []
    for e in Estudiante.objects.only("id", "cedula").iterator():
        if normalizar_cedula(e.cedula) == norm:
            ids.append(e.pk)
    return Estudiante.objects.filter(pk__in=ids)
