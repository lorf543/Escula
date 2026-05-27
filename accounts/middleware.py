"""Redirige a padres/tutores (modo padre) lejos de rutas de gestión escolar (`core`)."""

from .roles import usuario_en_modo_padre


class PadreCoreRedirectMiddleware:
    ALLOWED_PREFIXES = (
        "/accounts/",
        "/cuentas/",
        "/static/",
        "/media/",
        "/admin/",
        "/favicon.ico",
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and usuario_en_modo_padre(request.user):
            path = request.path
            if not any(path.startswith(p) for p in self.ALLOWED_PREFIXES):
                from django.shortcuts import redirect
                from django.urls import reverse

                return redirect(reverse("accounts:padre_dashboard"))
        return self.get_response(request)
