"""Rol activo: padre/tutor vs escuela (staff o profesor vinculado).

`UserProfile.role` define el modo cuando el usuario tiene fila `Padre` y además puede
acceder a la escuela; sin eso, quedaría «atrapado» en portal familiar solo por existir `Padre`.
"""

from __future__ import annotations

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect

from .models import UserProfile, UserRole


def _related_exists(user, attr: str) -> bool:
    try:
        getattr(user, attr)
        return True
    except ObjectDoesNotExist:
        return False


def tiene_perfil_padre(user) -> bool:
    if not user.is_authenticated:
        return False
    return _related_exists(user, "padre_profile")


def tiene_capacidad_escuela(user) -> bool:
    """Personal con acceso a gestión escolar (admin o profesor vinculado)."""
    if not user.is_authenticated:
        return False
    if user.is_staff:
        return True
    return _related_exists(user, "profesor_perfil")


def usuario_en_modo_padre(user) -> bool:
    """
    True si la UI y el middleware deben tratar al usuario como padre/tutor.

    Requiere `Padre`. El rol en `UserProfile` manda; si no hay perfil, solo modo padre
    cuando no hay capacidad escuela (cuentas solo familiares).
    """
    if not tiene_perfil_padre(user):
        return False
    try:
        return user.profile.role == UserRole.PADRE
    except UserProfile.DoesNotExist:
        return not tiene_capacidad_escuela(user)


def respuesta_si_no_modo_padre(request):
    """
    Si el usuario no está en modo padre, devuelve HttpResponseRedirect o None.
    Quien tenga escuela pero rol profesor recibe aviso para cambiar rol en admin.
    """
    if usuario_en_modo_padre(request.user):
        return None
    if tiene_capacidad_escuela(request.user):
        messages.info(
            request,
            "El portal familiar no está activo: su cuenta está en modo escuela. "
            "Para ver «Mis hijos», en Administración asigne el rol «Padre / Tutor» a su perfil de usuario.",
        )
        return redirect("core:dashboard")
    messages.error(request, "Esta sección es solo para padres o tutores.")
    return redirect("account_login")
