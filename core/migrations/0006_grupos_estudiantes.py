from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_participacion_valor"),
    ]

    operations = [
        migrations.CreateModel(
            name="GrupoEstudiantes",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=200)),
                (
                    "anio_escolar",
                    models.CharField(
                        help_text="Formato dominicano, ej.: 2025-2026.",
                        max_length=9,
                        verbose_name="año escolar",
                    ),
                ),
                ("persistente", models.BooleanField(default=True, help_text="Si es falso, el grupo solo existe para una tarea y no aparece en el listado.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="grupos_creados",
                        to="core.profesor",
                    ),
                ),
            ],
            options={
                "verbose_name": "grupo de estudiantes",
                "verbose_name_plural": "grupos de estudiantes",
                "ordering": ["nombre"],
            },
        ),
        migrations.CreateModel(
            name="GrupoCurso",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "curso",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grupo_cursos",
                        to="core.curso",
                    ),
                ),
                (
                    "grupo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grupo_cursos",
                        to="core.grupoestudiantes",
                    ),
                ),
            ],
            options={
                "verbose_name": "curso del grupo",
                "verbose_name_plural": "cursos del grupo",
                "unique_together": {("grupo", "curso")},
            },
        ),
        migrations.CreateModel(
            name="GrupoMiembro",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "curso",
                    models.ForeignKey(
                        blank=True,
                        help_text="Curso de origen al que pertenece el estudiante en este grupo.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="grupo_miembros",
                        to="core.curso",
                    ),
                ),
                (
                    "estudiante",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="grupos_miembro",
                        to="core.estudiante",
                    ),
                ),
                (
                    "grupo",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="miembros",
                        to="core.grupoestudiantes",
                    ),
                ),
            ],
            options={
                "verbose_name": "miembro del grupo",
                "verbose_name_plural": "miembros del grupo",
                "unique_together": {("grupo", "estudiante")},
            },
        ),
    ]
