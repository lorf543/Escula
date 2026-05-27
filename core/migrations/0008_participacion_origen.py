from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_grupo_tarea_temporal"),
    ]

    operations = [
        migrations.AddField(
            model_name="participacion",
            name="origen",
            field=models.CharField(
                choices=[("PARTICIPACION", "Participación"), ("BONO_MANUAL", "Bono manual")],
                default="PARTICIPACION",
                max_length=20,
            ),
        ),
    ]
