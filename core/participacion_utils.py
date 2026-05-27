from django.db.models import Sum

from .models import Participacion


def _participacion_sin_bono(qs):
    """Participación de clase (excluye bonos manuales del balance +/-)."""
    return qs.exclude(origen="BONO_MANUAL")


def resumen_participacion(queryset):
    """Totales y desglose por materia usando campo valor (1–5)."""
    qs = queryset.select_related("materia")
    qs_clase = _participacion_sin_bono(qs)
    agg_pos = qs_clase.filter(tipo="POSITIVO").aggregate(t=Sum("valor"))["t"] or 0
    agg_neg = qs_clase.filter(tipo="NEGATIVO").aggregate(t=Sum("valor"))["t"] or 0
    agg_bonos = qs.filter(origen="BONO_MANUAL").aggregate(t=Sum("valor"))["t"] or 0

    materia_ids = qs.values_list("materia_id", flat=True).distinct()
    puntos_por_materia = []
    for mid in materia_ids:
        if not mid:
            continue
        mqs = qs.filter(materia_id=mid)
        mqs_clase = _participacion_sin_bono(mqs)
        pos = mqs_clase.filter(tipo="POSITIVO").aggregate(t=Sum("valor"))["t"] or 0
        neg = mqs_clase.filter(tipo="NEGATIVO").aggregate(t=Sum("valor"))["t"] or 0
        bonos = mqs.filter(origen="BONO_MANUAL").aggregate(t=Sum("valor"))["t"] or 0
        if pos or neg or bonos:
            materia = mqs.first().materia
            puntos_por_materia.append(
                {
                    "materia": materia,
                    "positivos": pos,
                    "negativos": neg,
                    "bonos": bonos,
                    "balance": pos - neg,
                }
            )

    puntos_por_materia.sort(key=lambda x: x["materia"].nombre)
    return {
        "total_positivos": agg_pos,
        "total_negativos": agg_neg,
        "total_bonos": agg_bonos,
        "balance_total": agg_pos - agg_neg,
        "puntos_por_materia": puntos_por_materia,
    }


def resumen_participacion_estudiantes(estudiante_ids, materia_id=None):
    """Resumen de participación por estudiante (para curriculum curso)."""
    qs = Participacion.objects.filter(estudiante_id__in=estudiante_ids)
    if materia_id:
        qs = qs.filter(materia_id=materia_id)

    result = {}
    for eid in estudiante_ids:
        eqs = qs.filter(estudiante_id=eid)
        eqs_clase = _participacion_sin_bono(eqs)
        pos = eqs_clase.filter(tipo="POSITIVO").aggregate(t=Sum("valor"))["t"] or 0
        neg = eqs_clase.filter(tipo="NEGATIVO").aggregate(t=Sum("valor"))["t"] or 0
        bonos = eqs.filter(origen="BONO_MANUAL").aggregate(t=Sum("valor"))["t"] or 0
        result[eid] = {"positivos": pos, "negativos": neg, "bonos": bonos, "balance": pos - neg}
    return result
