from django.contrib import admin
from .models import Materia, Profesor, Estudiante, Observacion, Asistencia, Participacion

admin.site.register(Materia)
admin.site.register(Profesor)
admin.site.register(Estudiante)
admin.site.register(Observacion)
admin.site.register(Asistencia)
admin.site.register(Participacion)
