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