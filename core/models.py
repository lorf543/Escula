from django.db import models


class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name_plural = "materias"

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Profesor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField("cédula", max_length=20, unique=True, blank=True, default="")
    telefono = models.CharField("teléfono", max_length=20, blank=True)
    email = models.EmailField(blank=True)
    materias = models.ManyToManyField(Materia, related_name="profesores", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["apellido", "nombre"]
        verbose_name_plural = "profesores"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


GRADO_CHOICES = [
    ("1RO", "1ro Secundaria"),
    ("2DO", "2do Secundaria"),
    ("3RO", "3ro Secundaria"),
    ("4TO", "4to Secundaria"),
    ("5TO", "5to Secundaria"),
    ("6TO", "6to Secundaria"),
]


class Estudiante(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cedula = models.CharField("cédula", max_length=20, blank=True, default="")
    fecha_nacimiento = models.DateField("fecha de nacimiento", null=True, blank=True)
    grado = models.CharField(max_length=10, choices=GRADO_CHOICES)
    seccion = models.CharField("sección", max_length=5, blank=True, default="A")
    profesores = models.ManyToManyField(Profesor, related_name="estudiantes", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["grado", "apellido", "nombre"]
        verbose_name_plural = "estudiantes"

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


TIPO_OBSERVACION = [
    ("ACADEMICA", "Académica"),
    ("CONDUCTA", "Conducta"),
    ("PARTICIPACION", "Participación"),
    ("LOGRO", "Logro"),
    ("GENERAL", "General"),
]


class Observacion(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="observaciones"
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.SET_NULL, null=True, blank=True, related_name="observaciones"
    )
    tipo = models.CharField(max_length=20, choices=TIPO_OBSERVACION, default="GENERAL")
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "observación"
        verbose_name_plural = "observaciones"

    def __str__(self):
        return f"{self.estudiante} - {self.tipo} ({self.fecha:%d/%m/%Y})"


TIPO_PARTICIPACION = [
    ("POSITIVO", "Punto Positivo"),
    ("NEGATIVO", "Punto Negativo"),
]


class Participacion(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="participaciones"
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, related_name="participaciones"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_PARTICIPACION)
    descripcion = models.CharField(max_length=300, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "participación"
        verbose_name_plural = "participaciones"

    def __str__(self):
        signo = "+" if self.tipo == "POSITIVO" else "-"
        return f"{signo} {self.estudiante} - {self.materia} ({self.fecha:%d/%m/%Y})"


ESTADO_ASISTENCIA = [
    ("P", "Presente"),
    ("A", "Ausente"),
    ("T", "Tardanza"),
    ("E", "Excusa"),
]


class Asistencia(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="asistencias"
    )
    fecha = models.DateField()
    estado = models.CharField(max_length=1, choices=ESTADO_ASISTENCIA, default="P")
    nota = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-fecha", "estudiante__apellido"]
        unique_together = ["estudiante", "fecha"]
        verbose_name_plural = "asistencias"

    def __str__(self):
        return f"{self.estudiante} - {self.fecha} ({self.get_estado_display()})"
