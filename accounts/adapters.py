from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse

from .roles import tiene_capacidad_escuela, usuario_en_modo_padre


class EscuelaAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        user = request.user
        if usuario_en_modo_padre(user):
            return reverse("accounts:padre_dashboard")
        if tiene_capacidad_escuela(user):
            return reverse("core:dashboard")
        return reverse("account_login")
