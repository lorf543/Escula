from core.participacion_utils import resumen_participacion, resumen_participacion_estudiantes


def tareas_bruta_10(prom_tareas_pct):
    if prom_tareas_pct is None:
        return 0
    return round(prom_tareas_pct / 10, 1)


def total_bruto_estudiante(participacion_resumen, prom_tareas_pct):
    participacion_bruta = participacion_resumen.get("balance_total", 0)
    bonos = participacion_resumen.get("total_bonos", 0)
    tareas = tareas_bruta_10(prom_tareas_pct)
    return {
        "participacion_bruta": participacion_bruta,
        "bono_manual": bonos,
        "tareas_bruta_10": tareas,
        "total_bruto": round(participacion_bruta + bonos + tareas, 1),
    }


def total_bruto_estudiantes_map(estudiante_ids, prom_tareas_pct_map, materia_id=None):
    part_map = resumen_participacion_estudiantes(estudiante_ids, materia_id=materia_id)
    result = {}
    for eid in estudiante_ids:
        part = part_map.get(eid, {"balance": 0, "bonos": 0, "positivos": 0, "negativos": 0})
        tareas = tareas_bruta_10(prom_tareas_pct_map.get(eid))
        total = round(part["balance"] + part.get("bonos", 0) + tareas, 1)
        result[eid] = {
            "participacion_bruta": part["balance"],
            "bono_manual": part.get("bonos", 0),
            "tareas_bruta_10": tareas,
            "total_bruto": total,
            "positivos": part.get("positivos", 0),
            "negativos": part.get("negativos", 0),
        }
    return result
