"""Keyring JWT con `kid` y ventana de solapamiento (c-63c, IAH-008).

Responsabilidad:
    Resolver las claves vigentes del keyring (clave activa + clave anterior con
    ventana de solapamiento) y verificar tokens JWT de forma ACOTADA: como
    maximo dos intentos por token (una verificacion por clave vigente). La firma
    de tokens nuevos se hace con la clave activa y su `kid` (claim aditivo en el
    header); ver `auth_service.create_access_token(key_id=...)`.

Estrategia de verificacion (design.md D-C1):
    - Token con `kid` de la clave activa -> verifica con la activa.
    - Token con `kid` de la anterior y ventana abierta -> verifica con la anterior.
    - Token legacy SIN `kid` -> prueba activa y luego la anterior abierta.
    - Token con `kid` desconocido -> se rechaza SIN intentar ninguna clave (la
      verificacion nunca es ilimitada ni prueba claves fuera del keyring).

Ventana de solapamiento (design.md D-C2):
    `jwt_previous_key_expires_at` (ISO-8601 UTC) cierra la ventana. Vacio =
    la clave anterior se acepta mientras este configurada. Un valor ilegible NO
    abre una ventana indefinida: se trata como CERRADA (fail-closed, S3) y
    `Settings` lo rechaza en el arranque.
"""

from dataclasses import dataclass
from datetime import datetime, timezone

from jose import JWTError, jwt

from app.config.settings import Settings

# Claim del header donde viaja el identificador de clave.
KID_HEADER = "kid"


@dataclass(frozen=True)
class JwtKey:
    """Par identificador + secreto de una clave del keyring."""

    kid: str | None
    secret: str


def _normalize_str(value: object) -> str:
    """Normaliza a str; cualquier valor no textual (p. ej. un mock) es vacio."""
    if isinstance(value, bytes):
        return value.decode("ascii")
    if isinstance(value, str):
        return value
    return ""


def _parse_instant(raw: str) -> datetime | None:
    """Parsea un instante ISO-8601 a UTC aware; None si el valor es vacio.

    Un valor NO vacio pero ilegible NO se interpreta como "sin vencimiento":
    lanza ValueError (fail-closed, S3) para que el llamador cierre la ventana.
    """
    value = raw.strip()
    if not value:
        return None
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    parsed = datetime.fromisoformat(value)  # ValueError si es ilegible
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def active_key(settings: Settings) -> JwtKey:
    """Clave activa (con la que se firma) y su `kid`."""
    kid = _normalize_str(getattr(settings, "jwt_key_id", "")) or None
    return JwtKey(kid=kid, secret=settings.jwt_secret_key)  # gitleaks:allow (referencia/fixture, no un valor real)


def previous_key(settings: Settings, now: datetime | None = None) -> JwtKey | None:
    """Clave anterior vigente, o None si no esta configurada o la ventana cerro."""
    secret = _normalize_str(getattr(settings, "jwt_previous_secret_key", ""))
    if not secret:
        return None

    expires_raw = _normalize_str(getattr(settings, "jwt_previous_key_expires_at", ""))
    try:
        expires = _parse_instant(expires_raw)
    except ValueError:
        # Fail-closed (S3): una ventana ilegible NO se abre indefinidamente; se
        # trata como CERRADA y la clave anterior no se acepta. `Settings` ya
        # rechaza este valor en el arranque; esto cubre objetos duck-typed.
        return None
    if expires is not None:
        moment = now or datetime.now(timezone.utc)
        if moment >= expires:
            return None

    kid = _normalize_str(getattr(settings, "jwt_previous_key_id", "")) or None
    return JwtKey(kid=kid, secret=secret)


def candidate_keys(
    settings: Settings, token: str, *, now: datetime | None = None
) -> list[JwtKey]:
    """Claves del keyring aplicables al token, acotadas a las claves vigentes.

    Lee el `kid` NO verificado del header para elegir; un `kid` desconocido
    devuelve una lista vacia (el token se rechaza sin intentar ninguna clave).
    """
    header = jwt.get_unverified_header(token)
    kid = header.get(KID_HEADER)

    active = active_key(settings)
    previous = previous_key(settings, now)

    if kid is None:
        keys = [active]
        if previous is not None:
            keys.append(previous)
        return keys

    if kid == active.kid:
        return [active]
    if previous is not None and kid == previous.kid:
        return [previous]
    return []


def decode_token(
    token: str, settings: Settings, *, now: datetime | None = None
) -> dict:
    """Verifica un token con las claves vigentes (a lo sumo dos intentos).

    Args:
        token:    JWT a verificar.
        settings: Configuracion con el keyring.
        now:      Instante inyectable para evaluar la ventana (tests).

    Returns:
        El payload decodificado.

    Raises:
        JWTError: si el token es malformado (header ilegible), ningun `kid`
            corresponde al keyring, o ninguna clave vigente lo verifica.
    """
    last_error: JWTError | None = None
    for key in candidate_keys(settings, token, now=now):
        try:
            return jwt.decode(
                token,
                key.secret,
                algorithms=[settings.jwt_algorithm],
                options={"require_exp": True},
            )
        except JWTError as exc:
            last_error = exc

    if last_error is not None:
        raise last_error
    raise JWTError("Token signature does not match any key in the keyring")


__all__ = [
    "JwtKey",
    "KID_HEADER",
    "active_key",
    "candidate_keys",
    "decode_token",
    "previous_key",
]
