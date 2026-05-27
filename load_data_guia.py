"""
Carga de ejemplo: Guía de Ciencias Sociales (3ro Secundaria).
Ejecutar con: python manage.py shell < load_data_guia.py
"""

import os
from datetime import date, timedelta

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escuela.settings")
django.setup()

from core.models import Curso, EvaluacionP1, Materia, Profesor
from tareas.models import ModalidadTarea, Tarea, TareaGrado, TipoAsignacionTarea

# 1. Obtener/Crear Materia
sociales, _ = Materia.objects.get_or_create(
    codigo="CCSS",
    defaults={
        "nombre": "Ciencias Sociales",
        "descripcion": "Historia, Geografía y Ciencias Sociales",
    },
)

# 2. Obtener Curso 3ro Secundaria (asumiendo que existe uno para 2025-2026)
curso = Curso.objects.filter(grado="3RO", anio_escolar="2025-2026").first()
if not curso:
    curso = Curso.objects.create(grado="3RO", seccion="A", anio_escolar="2025-2026")

# 3. Obtener Profesor
profesor = Profesor.objects.first()

# 4. Crear Evaluación P1 (Justificación del Plan)
p1_content = (
    "JUSTIFICACIÓN PEDAGÓGICA DEL PLAN (Ciencias Sociales - 3ro Secundaria)\n\n"
    "Este plan de 12 horas presenciales (4 semanas) busca:\n"
    "- Garantizar acceso a contenidos esenciales.\n"
    "- Desarrollar competencias históricas sobre la formación de la República.\n"
    "- Ofrecer una base sobre Independencia, Restauración y organización del Estado.\n\n"
    "ENFOQUE: Evaluación formativa y continua, priorizando evidencias reales en el cuaderno."
)

ev_p1, created = EvaluacionP1.objects.get_or_create(
    curso=curso,
    materia=sociales,
    defaults={
        "fecha": date.today(),
        "contenido_texto": p1_content,
        "creado_por": profesor,
    },
)
print(f"P1 {'creado' if created else 'ya existía'} para {curso}")

# 5. Crear las 4 Tareas (Viernes de cada semana)
tareas_data = [
    (
        "Práctica: Resumen de la Independencia",
        "Describir causas, personajes (Duarte, Sánchez y Mella) y fecha.",
    ),
    (
        "Cuadro Comparativo: Independencia vs Restauración",
        "Identificar diferencias y similitudes entre ambos procesos históricos.",
    ),
    (
        "Esquema: Los Poderes del Estado Dominicano",
        "Graficar la división entre Poder Ejecutivo, Legislativo y Judicial.",
    ),
    (
        "Evaluación de Cierre (Prueba Escrita)",
        "Evidencia final sobre los contenidos de la unidad.",
    ),
]

hoy = date.today()
for i, (titulo, desc) in enumerate(tareas_data):
    fecha_entrega = hoy + timedelta(days=(i + 1) * 7)
    tarea, t_created = Tarea.objects.get_or_create(
        titulo=titulo,
        creada_por=profesor,
        defaults={
            "descripcion": desc,
            "modalidad": ModalidadTarea.ESCRITA,
            "tipo_asignacion": TipoAsignacionTarea.GRADOS,
            "fecha_entrega": fecha_entrega,
        },
    )
    if t_created:
        TareaGrado.objects.create(tarea=tarea, grado="3RO")
        print(f"Tarea creada: {titulo}")
    else:
        print(f"Tarea ya existía: {titulo}")

print("\nCarga de guía finalizada con éxito.")
