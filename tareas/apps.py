from django.apps import AppConfig


class TareasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tareas"
    verbose_name = "Tareas"

    def ready(self):
        import tareas.signals  # noqa: F401
