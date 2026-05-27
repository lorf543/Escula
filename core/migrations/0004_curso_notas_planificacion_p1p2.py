# Generated manually for Curso, NotaCurso, Planificacion, EvaluacionP1, RegistroProgresoP2

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_observacion_visible_padre"),
    ]

    operations = [
        migrations.CreateModel(
            name="Curso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "grado",
                    models.CharField(
                        choices=[
                            ("1RO", "1ro Secundaria"),
                            ("2DO", "2do Secundaria"),
                            ("3RO", "3ro Secundaria"),
                            ("4TO", "4to Secundaria"),
                            ("5TO", "5to Secundaria"),
                            ("6TO", "6to Secundaria"),
                        ],
                        max_length=10,
                    ),
                ),
                ("seccion", models.CharField(default="A", max_length=5, verbose_name="sección")),
                (
                    "anio_escolar",
                    models.CharField(
                        help_text="Formato dominicano, ej.: 2025-2026 (inicio en agosto).",
                        max_length=9,
                        verbose_name="año escolar",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "verbose_name": "curso",
                "verbose_name_plural": "cursos",
                "ordering": ["anio_escolar", "grado", "seccion"],
                "unique_together": {("grado", "seccion", "anio_escolar")},
            },
        ),
        migrations.CreateModel(
            name="EvaluacionP1",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField()),
                ("contenido_texto", models.TextField(blank=True, default="", verbose_name="descripción / hallazgos")),
                (
                    "imagen",
                    models.ImageField(
                        blank=True,
                        help_text="Opcional: foto de instrumento, rúbrica o evidencia.",
                        null=True,
                        upload_to="evaluaciones/p1/%Y/",
                        verbose_name="imagen adjunta",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="evaluaciones_p1",
                        to="core.profesor",
                    ),
                ),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluaciones_p1",
                        to="core.curso",
                    ),
                ),
                (
                    "materia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluaciones_p1",
                        to="core.materia",
                    ),
                ),
            ],
            options={
                "verbose_name": "evaluación P1 (diagnóstica)",
                "verbose_name_plural": "evaluaciones P1 (diagnósticas)",
                "ordering": ["-fecha"],
                "unique_together": {("curso", "materia")},
            },
        ),
        migrations.CreateModel(
            name="NotaCurso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(verbose_name="fecha")),
                ("contenido", models.TextField(verbose_name="observación general")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notas_curso",
                        to="core.profesor",
                    ),
                ),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notas",
                        to="core.curso",
                    ),
                ),
                (
                    "estudiantes",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Opcional: estudiantes sobre los que se comenta en esta nota.",
                        related_name="menciones_nota_curso",
                        to="core.estudiante",
                        verbose_name="estudiantes mencionados",
                    ),
                ),
                (
                    "materia",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="notas_curso",
                        to="core.materia",
                    ),
                ),
            ],
            options={
                "verbose_name": "nota de curso",
                "verbose_name_plural": "notas de curso",
                "ordering": ["-fecha", "-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Planificacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "tipo",
                    models.CharField(
                        choices=[("DIARIA", "Planificación diaria"), ("GENERAL", "Planificación general / unidad")],
                        default="DIARIA",
                        max_length=10,
                    ),
                ),
                (
                    "fecha",
                    models.DateField(
                        help_text="Fecha de la clase (diaria) o inicio de la unidad/período (general)."
                    ),
                ),
                ("titulo", models.CharField(blank=True, default="", max_length=200)),
                (
                    "contenido",
                    models.TextField(
                        help_text="Contenido enriquecido (HTML): actividades, competencias, indicadores MINERD."
                    ),
                ),
                ("competencias_fundamentales", models.TextField(blank=True, default="", verbose_name="competencias fundamentales")),
                ("indicadores_logro", models.TextField(blank=True, default="", verbose_name="indicadores de logro")),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="planificaciones",
                        to="core.profesor",
                    ),
                ),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="planificaciones",
                        to="core.curso",
                    ),
                ),
                (
                    "materia",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="planificaciones",
                        to="core.materia",
                    ),
                ),
            ],
            options={
                "verbose_name": "planificación",
                "verbose_name_plural": "planificaciones",
                "ordering": ["-fecha", "-updated_at"],
            },
        ),
        migrations.CreateModel(
            name="RegistroProgresoP2",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField()),
                (
                    "contenido",
                    models.TextField(
                        help_text="Avances, ajustes didácticos o evidencias de progreso respecto al P1."
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="registros_p2",
                        to="core.profesor",
                    ),
                ),
                (
                    "evaluacion_p1",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="registros_p2",
                        to="core.evaluacionp1",
                    ),
                ),
            ],
            options={
                "verbose_name": "registro P2 (progreso)",
                "verbose_name_plural": "registros P2 (progreso)",
                "ordering": ["-fecha", "-created_at"],
            },
        ),
    ]
