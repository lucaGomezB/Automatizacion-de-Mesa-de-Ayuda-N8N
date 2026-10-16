"""
Schemas Pydantic para el flujo de autenticacion JWT.

Responsabilidad:
    Define los contratos de datos de entrada y salida para los endpoints de
    login, refresco y logout. LoginRequest recibe las credenciales; TokenResponse
    devuelve el access token y su expiracion. El refresco NO viaja en el cuerpo
    (c-91, IAH-014): se entrega y se lee desde una cookie HttpOnly, por lo que
    los schemas de cuerpo para /refresh y /logout ya no existen.
"""

from typing import Literal

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """
    Payload de inicio de sesion.

    Aceptado por POST /api/v1/auth/login. Ambos campos son requeridos.
    """

    username: str = Field(..., min_length=1, description="Nombre de usuario")
    password: str = Field(..., min_length=1, description="Password en texto plano")


class TokenResponse(BaseModel):
    """
    Respuesta exitosa de autenticacion (access token).

    El refresh token NO se expone en el cuerpo (c-91, IAH-014): viaja en una
    cookie HttpOnly seteada por el servidor.
    """

    access_token: str = Field(..., description="Token JWT firmado")
    token_type: str = Field(default="bearer", description="Tipo de token (bearer)")
    expires_in: int | None = Field(
        default=None, description="Segundos hasta la expiracion del access token"
    )


class LogoutResponse(BaseModel):
    """Confirmacion de logout (idempotente)."""

    message: str = Field(..., description="Mensaje de confirmacion")


# ── MFA / login en dos pasos (c-63b, IAH-007) ────────────────────────────────


class LoginResponse(BaseModel):
    """Respuesta del login (un paso, o reto de segundo factor; c-63b).

    En el flujo de un paso conserva `access_token`/`token_type` (y agrega
    `expires_in`); el refresh viaja en cookie (IAH-014), NO en el cuerpo. En el
    reto MFA, `mfa_required` es verdadero, se entrega `mfa_ticket` y NO se emite
    access token NI `token_type` (los campos nulos se omiten en la serializacion).
    """

    access_token: str | None = Field(
        default=None, description="Token JWT firmado (ausente en el reto MFA)"
    )
    token_type: str | None = Field(
        default=None,
        description="Tipo de token (bearer); ausente en el reto MFA",
    )
    expires_in: int | None = Field(
        default=None, description="Segundos hasta la expiracion del access token"
    )
    mfa_required: bool = Field(
        default=False, description="True si se requiere el segundo factor"
    )
    mfa_ticket: str | None = Field(
        default=None, description="Ticket corto para POST /auth/mfa/verify"
    )


class MfaVerifyRequest(BaseModel):
    """Payload de POST /auth/mfa/verify: el ticket y el segundo factor."""

    mfa_ticket: str = Field(..., min_length=1, description="Ticket de segundo factor")
    code: str | None = Field(
        default=None, description="Codigo TOTP de 6 digitos"
    )
    recovery_code: str | None = Field(
        default=None, description="Codigo de recuperacion de un solo uso"
    )


class MfaEnrollResponse(BaseModel):
    """Respuesta del enrollment: valores mostrados UNA sola vez."""

    otpauth_uri: str = Field(..., description="URI otpauth:// para la app autenticadora")
    secret: str = Field(..., description="Secreto TOTP (base32)")
    recovery_codes: list[str] = Field(
        ..., description="Codigos de recuperacion de un solo uso"
    )


# ── Identidad y alcance de la sesion (c-81, IAH-012) ─────────────────────────


class AlcanceResponse(BaseModel):
    """Alcance de incidentes de la sesion (c-81, IAH-012).

    Contiene SOLO el modo vigente del modelo c-82. NO expone `sector_id`,
    `ver_todos` ni conceptos del RBAC anterior (los modos SECTOR y REVISION no
    existen).
    """

    modo: Literal["PROPIO", "GLOBAL", "VACIO"] = Field(
        ..., description="Modo de alcance de incidentes derivado del rol"
    )


class IdentidadActualResponse(BaseModel):
    """Identidad efectiva de la sesion y su alcance derivado (c-81, IAH-012).

    Aditivo y de solo lectura. `rol` es el rol del empleado activo vinculado
    (o nulo si no hay empleado). El alcance se recomputa por request desde el
    directorio.
    """

    username: str = Field(..., description="Nombre de usuario autenticado")
    rol: str | None = Field(
        default=None, description="Rol del empleado vinculado (nulo si no hay)"
    )
    alcance: AlcanceResponse = Field(
        ..., description="Alcance de incidentes derivado (modo PROPIO/GLOBAL/VACIO)"
    )