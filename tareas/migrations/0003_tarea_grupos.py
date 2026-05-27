from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_grupos_estudiantes"),
        ("tareas", "0002_tarea_modalidad_tareaevaluacion_puntaje"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="tarea",
            name="tipo_asignacion",
            field=models.CharField(
                choices=[("GRADOS", "Por curso (grado)"), ("GRUPOS", "Por grupos")],
                default="GRADOS",
                max_length=10,
            ),
        ),
        migrations.CreateModel(
            name="TareaGrupo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "grupo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tareas_asignadas",
                        to="core.grupoestudiantes",
                    ),
                ),
                (
                    "tarea",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grupos_asignados",
                        to="tareas.tarea",
                    ),
                ),
            ],
            options={
                "verbose_name": "grupo asignado",
                "verbose_name_plural": "grupos asignados",
                "unique_together": {("tarea", "grupo")},
            },
        ),
        migrations.CreateModel(
            name="TareaGrupoEvaluacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "observacion_general",
                    models.TextField(blank=True, default="", verbose_name="observación general del grupo"),
                ),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                (
                    "actualizado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="evaluaciones_grupo_tarea_editadas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "grupo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluaciones_tarea",
                        to="core.grupoestudiantes",
                    ),
                ),
                (
                    "tarea",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evaluaciones_grupo",
                        to="tareas.tarea",
                    ),
                ),
            ],
            options={
                "verbose_name": "evaluación de grupo",
                "verbose_name_plural": "evaluaciones de grupo",
                "unique_together": {("tarea", "grupo")},
            },
        ),
    ]
