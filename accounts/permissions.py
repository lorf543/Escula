from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


def puede_gestionar_invitacion(user, estudiante) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    prof = getattr(user, "profesor_perfil", None)
    if prof and estudiante in prof.profesor.estudiantes.all():
        return True
    return False


def staff_o_profesor(user) -> bool:
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return hasattr(user, "profesor_perfil")
