"""
Endpoint HTTP de autenticacion.

Responsabilidad:
    Define la ruta POST /api/v1/auth/login que recibe credenciales,
    las valida contra la base de datos, y retorna un token JWT firmado.

    Esta capa es responsable exclusivamente de:
        - Recibir y deserializar el payload HTTP.
        - Delegar la logica de autenticacion al auth_service.
        - Serializar y retornar la respuesta HTTP con el token.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import authenticate_user, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# Alias de tipo para inyeccion de sesion via FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def _error_body(code: str, message: str) -> dict:
    """Construye el cuerpo JSON estandar de respuesta de error."""
    return {"error": {"code": code, "message": message}}


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesion y obtener token JWT",
)
async def login(payload: LoginRequest, session: SessionDep):
    """
    Autentica al usuario con username y password, retornando un token JWT.

    El token debe enviarse en el header Authorization de requests subsiguientes:
        Authorization: Bearer <access_token>

    El token expira segun la configuracion JWT_EXPIRE_MINUTES (24 horas por defecto).

    Args:
        payload: Credenciales de inicio de sesion (username + password).

    Returns:
        TokenResponse con access_token y token_type "bearer" (HTTP 200).

    Raises:
        JSONResponse 401: Si las credenciales son invalidas.
    """
    user = await authenticate_user(session, payload.username, payload.password)

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body("INVALID_CREDENTIALS", "Incorrect username or password"),
        )

    settings = get_settings()
    access_token = create_access_token(
        data={"sub": user.username},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=settings.jwt_expire_minutes,
    )

    return TokenResponse(access_token=access_token, token_type="bearer")
