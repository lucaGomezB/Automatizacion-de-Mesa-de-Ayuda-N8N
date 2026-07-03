"""
Schemas Pydantic para el flujo de autenticacion JWT.

Responsabilidad:
    Define los contratos de datos de entrada y salida para el endpoint
    de login. LoginRequest recibe las credenciales, TokenResponse
    devuelve el JWT generado.
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

    Contiene el token JWT firmado y el tipo de token (siempre "bearer").
    """

    access_token: str = Field(..., description="Token JWT firmado")
    token_type: str = Field(default="bearer", description="Tipo de token (bearer)")
