from django.db import migrations, models
import django.db.models.deletion


def migrar_tarea_desde_tareagrupo(apps, schema_editor):
    GrupoEstudiantes = apps.get_model("core", "GrupoEstudiantes")
    TareaGrupo = apps.get_model("tareas", "TareaGrupo")
    for tg in TareaGrupo.objects.select_related("grupo", "tarea").all():
        grupo = tg.grupo
        grupo.tarea_id = tg.tarea_id
        grupo.save(update_fields=["tarea_id"])
    GrupoEstudiantes.objects.filter(tarea__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_grupos_estudiantes"),
        ("tareas", "0003_tarea_grupos"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupoestudiantes",
            name="tarea",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grupos",
                to="tareas.tarea",
            ),
        ),
        migrations.RunPython(migrar_tarea_desde_tareagrupo, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="grupoestudiantes",
            name="anio_escolar",
        ),
        migrations.RemoveField(
            model_name="grupoestudiantes",
            name="persistente",
        ),
        migrations.AlterField(
            model_name="grupoestudiantes",
            name="tarea",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="grupos",
                to="tareas.tarea",
            ),
        ),
    ]
