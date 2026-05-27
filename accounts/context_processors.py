from .roles import usuario_en_modo_padre


def modo_padre(request):
    return {
        "en_modo_padre": (
            usuario_en_modo_padre(request.user) if request.user.is_authenticated else False
        ),
    }
