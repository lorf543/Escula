from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("tareas", "0003_tarea_grupos"),
        ("core", "0007_grupo_tarea_temporal"),
    ]

    operations = [
        migrations.DeleteModel(
            name="TareaGrupo",
        ),
    ]
