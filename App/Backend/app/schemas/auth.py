"""
Schemas Pydantic para el flujo de autenticacion JWT.

Responsabilidad:
    Define los contratos de datos de entrada y salida para los endpoints de
    login, refresco y logout. LoginRequest recibe las credenciales; TokenResponse
    devuelve el par de tokens de forma ADITIVA respecto del contrato previo
    (c-63a): conserva `access_token` y `token_type` y agrega `refresh_token` y
    `expires_in` opcionales.

    RefreshRequest/LogoutRequest reciben el refresh token opaco.
"""

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
    Respuesta exitosa de autenticacion.

    Contrato aditivo (c-63a): `access_token` y `token_type` se conservan con la
    misma semantica que antes; `refresh_token` y `expires_in` se agregan de
    forma opcional para no romper clientes existentes.
    """

    access_token: str = Field(..., description="Token JWT firmado")
    token_type: str = Field(default="bearer", description="Tipo de token (bearer)")
    refresh_token: str | None = Field(
        default=None, description="Refresh token opaco rotativo"
    )
    expires_in: int | None = Field(
        default=None, description="Segundos hasta la expiracion del access token"
    )


class RefreshRequest(BaseModel):
    """Payload del endpoint de refresco: el refresh token opaco rotativo."""

    refresh_token: str = Field(..., min_length=1, description="Refresh token opaco")


class LogoutRequest(BaseModel):
    """Payload del endpoint de logout: el refresh token a revocar."""

    refresh_token: str = Field(..., min_length=1, description="Refresh token opaco")


class LogoutResponse(BaseModel):
    """Confirmacion de logout (idempotente)."""

    message: str = Field(..., description="Mensaje de confirmacion")


# ── MFA / login en dos pasos (c-63b, IAH-007) ────────────────────────────────


class LoginResponse(BaseModel):
    """Respuesta del login, ADITIVA respecto del contrato previo (c-63b).

    En el flujo de un paso conserva `access_token`/`token_type` (y agrega
    `refresh_token`/`expires_in`). En el reto MFA, `mfa_required` es verdadero,
    se entrega `mfa_ticket` y NO se emite access token NI `token_type` (los
    campos nulos se omiten en la serializacion).
    """

    access_token: str | None = Field(
        default=None, description="Token JWT firmado (ausente en el reto MFA)"
    )
    token_type: str | None = Field(
        default=None,
        description="Tipo de token (bearer); ausente en el reto MFA",
    )
    refresh_token: str | None = Field(
        default=None, description="Refresh token opaco rotativo"
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