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
    visible_padre = models.BooleanField(
        "visible para padres/tutores",
        default=False,
        help_text="Si está marcado, el contenido podrá verse en el currículum familiar.",
    )
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

ORIGEN_PARTICIPACION = [
    ("PARTICIPACION", "Participación"),
    ("BONO_MANUAL", "Bono manual"),
]


class Participacion(models.Model):
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="participaciones"
    )
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, related_name="participaciones"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_PARTICIPACION)
    valor = models.PositiveSmallIntegerField(
        "puntos",
        default=1,
        help_text="Valor del 1 al 5 según la importancia del registro.",
    )
    origen = models.CharField(
        max_length=20,
        choices=ORIGEN_PARTICIPACION,
        default="PARTICIPACION",
    )
    descripcion = models.CharField(max_length=300, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "participación"
        verbose_name_plural = "participaciones"

    @property
    def puntos_firmados(self):
        return self.valor if self.tipo == "POSITIVO" else -self.valor

    def __str__(self):
        signo = "+" if self.tipo == "POSITIVO" else "-"
        return f"{signo}{self.valor} {self.estudiante} - {self.materia} ({self.fecha:%d/%m/%Y})"


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


# ── Cursos (grado + sección + año escolar RD) ─────────────────────────────


class Curso(models.Model):
    grado = models.CharField(max_length=10, choices=GRADO_CHOICES)
    seccion = models.CharField("sección", max_length=5, default="A")
    anio_escolar = models.CharField(
        "año escolar",
        max_length=9,
        help_text="Formato dominicano, ej.: 2025-2026 (inicio en agosto).",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["anio_escolar", "grado", "seccion"]
        verbose_name = "curso"
        verbose_name_plural = "cursos"
        unique_together = [("grado", "seccion", "anio_escolar")]

    def __str__(self):
        return self.nombre_corto

    @property
    def nombre_corto(self):
        grado = self.get_grado_display()
        return f"{grado} — Sección {self.seccion}"

    @property
    def nombre_completo(self):
        return f"{self.nombre_corto} ({self.anio_escolar})"

    def estudiantes_qs(self):
        return Estudiante.objects.filter(grado=self.grado, seccion=self.seccion)


class GrupoEstudiantes(models.Model):
    """Grupo temporal de estudiantes vinculado a una tarea."""

    tarea = models.ForeignKey(
        "tareas.Tarea",
        on_delete=models.CASCADE,
        related_name="grupos",
    )
    nombre = models.CharField(max_length=200)
    creado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grupos_creados",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "grupo de estudiantes"
        verbose_name_plural = "grupos de estudiantes"

    def __str__(self):
        return self.nombre

    @property
    def total_miembros(self):
        return self.miembros.count()


class GrupoCurso(models.Model):
    grupo = models.ForeignKey(
        GrupoEstudiantes, on_delete=models.CASCADE, related_name="grupo_cursos"
    )
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="grupo_cursos")

    class Meta:
        unique_together = [("grupo", "curso")]
        verbose_name = "curso del grupo"
        verbose_name_plural = "cursos del grupo"

    def __str__(self):
        return f"{self.grupo} — {self.curso}"


class GrupoMiembro(models.Model):
    grupo = models.ForeignKey(
        GrupoEstudiantes, on_delete=models.CASCADE, related_name="miembros"
    )
    estudiante = models.ForeignKey(
        Estudiante, on_delete=models.CASCADE, related_name="grupos_miembro"
    )
    curso = models.ForeignKey(
        Curso,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="grupo_miembros",
        help_text="Curso de origen al que pertenece el estudiante en este grupo.",
    )

    class Meta:
        unique_together = [("grupo", "estudiante")]
        verbose_name = "miembro del grupo"
        verbose_name_plural = "miembros del grupo"

    def __str__(self):
        return f"{self.estudiante} en {self.grupo}"


class NotaCurso(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="notas")
    materia = models.ForeignKey(
        Materia, on_delete=models.SET_NULL, null=True, blank=True, related_name="notas_curso"
    )
    fecha = models.DateField("fecha")
    contenido = models.TextField("observación general")
    estudiantes = models.ManyToManyField(
        Estudiante,
        blank=True,
        related_name="menciones_nota_curso",
        verbose_name="estudiantes mencionados",
        help_text="Opcional: estudiantes sobre los que se comenta en esta nota.",
    )
    creado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notas_curso",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-created_at"]
        verbose_name = "nota de curso"
        verbose_name_plural = "notas de curso"

    def __str__(self):
        return f"{self.curso} — {self.fecha:%d/%m/%Y}"


TIPO_PLANIFICACION = [
    ("DIARIA", "Planificación diaria"),
    ("GENERAL", "Planificación general / unidad"),
]


class Planificacion(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="planificaciones")
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, related_name="planificaciones"
    )
    tipo = models.CharField(max_length=10, choices=TIPO_PLANIFICACION, default="DIARIA")
    fecha = models.DateField(
        help_text="Fecha de la clase (diaria) o inicio de la unidad/período (general).",
    )
    titulo = models.CharField(max_length=200, blank=True, default="")
    contenido = models.TextField(
        help_text="Contenido enriquecido (HTML): actividades, competencias, indicadores MINERD.",
    )
    competencias_fundamentales = models.TextField(
        "competencias fundamentales",
        blank=True,
        default="",
    )
    indicadores_logro = models.TextField("indicadores de logro", blank=True, default="")
    creado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="planificaciones",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-updated_at"]
        verbose_name = "planificación"
        verbose_name_plural = "planificaciones"

    def __str__(self):
        base = self.titulo or self.get_tipo_display()
        return f"{base} — {self.curso} / {self.materia}"


class EvaluacionP1(models.Model):
    """
    Evaluación diagnóstica inicial (P1) por curso y materia.
    Según práctica docente en RD: línea base al inicio del año o unidad.
    """

    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name="evaluaciones_p1")
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name="evaluaciones_p1")
    fecha = models.DateField()
    contenido_texto = models.TextField("descripción / hallazgos", blank=True, default="")
    imagen = models.ImageField(
        "imagen adjunta",
        upload_to="evaluaciones/p1/%Y/",
        blank=True,
        null=True,
        help_text="Opcional: foto de instrumento, rúbrica o evidencia.",
    )
    creado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="evaluaciones_p1",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "evaluación P1 (diagnóstica)"
        verbose_name_plural = "evaluaciones P1 (diagnósticas)"
        unique_together = [("curso", "materia")]

    def __str__(self):
        return f"P1 — {self.curso} / {self.materia}"

    @property
    def tiene_contenido(self):
        return bool(self.contenido_texto.strip()) or bool(self.imagen)


class RegistroProgresoP2(models.Model):
    """Seguimiento de progreso (P2) vinculado a la evaluación inicial P1."""

    evaluacion_p1 = models.ForeignKey(
        EvaluacionP1,
        on_delete=models.CASCADE,
        related_name="registros_p2",
    )
    fecha = models.DateField()
    contenido = models.TextField(
        help_text="Avances, ajustes didácticos o evidencias de progreso respecto al P1.",
    )
    creado_por = models.ForeignKey(
        Profesor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="registros_p2",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-created_at"]
        verbose_name = "registro P2 (progreso)"
        verbose_name_plural = "registros P2 (progreso)"

    def __str__(self):
        return f"P2 — {self.evaluacion_p1} ({self.fecha:%d/%m/%Y})"
