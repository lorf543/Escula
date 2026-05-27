"""Rúbricas holísticas institucionales para tareas orales y escritas."""

from .models import ModalidadTarea

# (valor, etiqueta_corta, descriptor)
RUBRICA_ORAL = [
    (1, "Insuficiente", "No presenta o no logra comunicar el contenido."),
    (2, "En desarrollo", "Se expresa con dificultad; ideas incompletas o poco claras."),
    (3, "Aceptable", "Cumple lo mínimo; mensaje entendible con apoyo."),
    (4, "Bueno", "Buen dominio; expresión clara y organizada."),
    (5, "Excelente", "Dominio sobresaliente; comunicación fluida y segura."),
]

# Valores representativos por banda (escala 1–10)
RUBRICA_ESCRITA = [
    (2, "Insuficiente (1–2)", "No cumple requisitos; errores graves de contenido o forma."),
    (4, "En desarrollo (3–4)", "Idea presente pero organización o redacción débiles."),
    (6, "Aceptable (5–6)", "Cumple lo esperado con errores moderados."),
    (8, "Bueno (7–8)", "Contenido sólido y buena redacción."),
    (10, "Excelente (9–10)", "Trabajo completo, claro y bien fundamentado."),
]

ESCALA_MAX = {
    ModalidadTarea.ORAL: 5,
    ModalidadTarea.ESCRITA: 10,
}


def rubrica_items(modalidad):
    if modalidad == ModalidadTarea.ORAL:
        return RUBRICA_ORAL
    return RUBRICA_ESCRITA


def escala_max(modalidad):
    return ESCALA_MAX.get(modalidad, 10)


def descriptor(modalidad, puntaje):
    if puntaje is None:
        return ""
    items = rubrica_items(modalidad)
    if modalidad == ModalidadTarea.ORAL:
        for val, label, _ in items:
            if val == puntaje:
                return label
        return str(puntaje)
    # Escrita: banda más cercana
    best = min(items, key=lambda x: abs(x[0] - puntaje))
    return best[1]


def normalizar_puntaje(modalidad, puntaje):
    if puntaje is None:
        return None
    max_p = escala_max(modalidad)
    return round(puntaje / max_p * 100)


def choices_puntaje(modalidad):
    items = rubrica_items(modalidad)
    return [
        ("", "— Sin puntaje —"),
        *[
            (str(val), f"{val} — {label}: {desc}")
            for val, label, desc in items
        ],
    ]


def puntaje_display(modalidad, puntaje):
    if puntaje is None:
        return "—"
    max_p = escala_max(modalidad)
    label = descriptor(modalidad, puntaje)
    return f"{puntaje}/{max_p} — {label}"


def promedio_normalizado(evaluaciones):
    """Promedio 0–100 de evaluaciones con puntaje asignado."""
    scores = [e.puntaje_normalizado for e in evaluaciones if e.puntaje is not None]
    if not scores:
        return None
    return round(sum(scores) / len(scores), 1)


def derivar_estado(modalidad, puntaje):
    """Infiera estado cualitativo a partir del puntaje de la rúbrica."""
    from .models import EstadoTareaEval

    if puntaje is None:
        return EstadoTareaEval.PENDIENTE
    if modalidad == ModalidadTarea.ORAL:
        if puntaje <= 2:
            return EstadoTareaEval.NECESITA_MEJORA
        return EstadoTareaEval.COMPLETO
    # Escrita: bandas 2 y 4 = en desarrollo / insuficiente
    if puntaje <= 4:
        return EstadoTareaEval.NECESITA_MEJORA
    return EstadoTareaEval.COMPLETO
