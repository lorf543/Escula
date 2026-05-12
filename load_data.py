"""
Carga inicial de datos: materias, profesor Eduardo, y todos los estudiantes por curso.
Ejecutar con: python manage.py shell < load_data.py
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escuela.settings")
django.setup()

from core.models import Materia, Profesor, Estudiante

# ── Materias ───────────────────────────────────────────────────────────

ingles, _ = Materia.objects.get_or_create(
    codigo="ING", defaults={"nombre": "Inglés", "descripcion": "Lengua extranjera - Inglés"}
)
sociales, _ = Materia.objects.get_or_create(
    codigo="CCSS",
    defaults={"nombre": "Ciencias Sociales", "descripcion": "Historia, Geografía y Ciencias Sociales"},
)
print(f"Materias: {ingles}, {sociales}")

# ── Profesor ───────────────────────────────────────────────────────────

profesor, created = Profesor.objects.get_or_create(
    nombre="Eduardo Alberto",
    apellido="Sánchez Lebrón",
    defaults={"cedula": "", "telefono": "", "email": ""},
)
profesor.materias.set([ingles, sociales])
print(f"Profesor: {profesor} ({'creado' if created else 'ya existía'})")

# ── Estudiantes ────────────────────────────────────────────────────────

ESTUDIANTES_1RO = [
    ("Luisa Darila", "Abad Montero"),
    ("Isaac", "Agramonte Fabián"),
    ("Emanuela", "Amervil"),
    ("Emanueli", "Amervil"),
    ("Nayeli", "Caraballo"),
    ("Adrianny Esther", "Cedano Feliz"),
    ("Enger Domingo", "Cuevas Mora"),
    ("Yamileth Pamela", "Cuevas Oviedo"),
    ("Samuel", "De Jesús Polonia"),
    ("Luis Manuel", "De La Cruz De León"),
    ("Mebelin Pamela", "De Los Santos Ramírez"),
    ("Darwin Ismael", "Feliz Lorenzo"),
    ("Geisel Sebastián", "Feliz Morrobel"),
    ("Lenec", "Fleurimond"),
    ("Ángel Enmanuel", "Francisco"),
    ("Wellves", "García"),
    ("Eveline", "Geffrard Pérez"),
    ("Leudis Denzel", "Gil Amancio"),
    ("Raúl", "Guzmán Feliz"),
    ("Dencel Ricardo", "Heredia"),
    ("Gabriel Elías", "Lizardo Díaz"),
    ("Claudia Darismel", "Pimentel Rodríguez"),
    ("Walis", "Ramón Encarnación"),
    ("Sheila Mireya", "Rodríguez Cordero"),
    ("Michelle Ángela", "Rodríguez Cordero"),
    ("Juan David", "Sánchez Martínez"),
    ("Kendry Anuel", "Sánchez Martínez"),
    ("Ricardo Isaac", "Sosa Apolinar"),
    ("Franyel Daniel", "Soto Segura"),
]

ESTUDIANTES_2DO = [
    ("Luis David", "Abreu Rincón"),
    ("Wilkin Abrhan", "Beltré Carela"),
    ("Arianna Maciel", "Calzado"),
    ("Laura Alejandra", "Cedeño"),
    ("Sara Inerys", "Comprés Martínez"),
    ("Marielys", "David Díaz"),
    ("Daniel", "De Jesús Polonia"),
    ("Jorge Luis", "De La Cruz Reyes"),
    ("Ana Camila", "De León"),
    ("Yeirell Alejandro", "Hernández"),
    ("Félix Junior", "Martínez Mendoza"),
    ("Reison", "Matos Gómez"),
    ("Camila", "Montero Peralta"),
    ("Fraideli", "Terrero Montero"),
    ("Hanzel Antonio", "Vásquez Pérez"),
    ("María Valentina", "Basilio"),
    ("Ana Yudeilis", "Abreu Soto"),
    ("Wolkenley", "Renacier"),
]

ESTUDIANTES_3RO = [
    ("Ana Yovanna", "Abreu Ricón"),
    ("Jordy Isaac", "Benavides Rosario"),
    ("Andry Michael", "Batista García"),
    ("Jhoneuly Marcelino", "Cordero Pérez"),
    ("Yadelin Shanell", "Roa Cuevas"),
    ("Johanna", "Pérez Pérez"),
]

CURSOS = [
    ("1RO", ESTUDIANTES_1RO),
    ("2DO", ESTUDIANTES_2DO),
    ("3RO", ESTUDIANTES_3RO),
]

total = 0
for grado, lista in CURSOS:
    print(f"\n-- {grado} Secundaria ({len(lista)} estudiantes) --")
    for nombre, apellido in lista:
        est, created = Estudiante.objects.get_or_create(
            nombre=nombre,
            apellido=apellido,
            grado=grado,
            defaults={"seccion": "A"},
        )
        est.profesores.add(profesor)
        status = "+" if created else "="
        print(f"  {status} {est.nombre_completo}")
        total += 1

print(f"\n{'='*50}")
print(f"Total estudiantes procesados: {total}")
print("Profesor asignado a todos los estudiantes")
print(f"Materias asignadas: {profesor.materias.count()}")
print(f"{'='*50}")
