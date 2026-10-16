"""
Transporte del refresh token en cookie HttpOnly (c-91, IAH-014).

Responsabilidad:
    Centraliza la lectura/escritura/borrado de la cookie de refresh y la
    verificacion de `Origin` que mitiga CSRF sobre los endpoints que derivan
    autoridad de la cookie (`/refresh`, `/logout`).

    Es codigo transversal de la capa HTTP (presentacion). La logica de dominio
    del refresh (rotacion, revocacion, inactividad) vive en `auth_service`.
"""

from fastapi import Request, Response

from app.config.settings import Settings


def _cookie_options(settings: Settings) -> dict:
    """Atributos comunes de la cookie de refresh (HttpOnly + Secure + SameSite)."""
    return {
        "path": settings.auth_refresh_cookie_path,
        "httponly": True,
        "secure": settings.auth_refresh_cookie_secure,
        "samesite": settings.auth_refresh_cookie_samesite,
    }


def set_refresh_cookie(
    response: Response, value: str, settings: Settings, *, max_age_seconds: int
) -> None:
    """Setea/renueva la cookie de refresh con el valor opaco recien emitido."""
    response.set_cookie(
        key=settings.auth_refresh_cookie_name,
        value=value,
        max_age=max_age_seconds,
        **_cookie_options(settings),
    )


def clear_refresh_cookie(response: Response, settings: Settings) -> None:
    """Expira la cookie de refresh (Max-Age=0) en el logout."""
    response.delete_cookie(
        key=settings.auth_refresh_cookie_name,
        **_cookie_options(settings),
    )


def read_refresh_cookie(request: Request, settings: Settings) -> str | None:
    """Devuelve el refresh presentado en la cookie, o None si no existe."""
    return request.cookies.get(settings.auth_refresh_cookie_name)


def origin_is_trusted(origin: str | None, settings: Settings) -> bool:
    """True si el `Origin` es confiable (o ausente).

    Sin cabecera `Origin` no puede haber un CSRF de navegador (los navegadores
    envian `Origin` en peticiones de estado cross-site); se permite para no
    romper clientes no-navegador. Con `Origin` presente, debe figurar en la
    lista exacta `cors_allow_origins`.
    """
    if not origin:
        return True
    return origin in settings.cors_allow_origins
