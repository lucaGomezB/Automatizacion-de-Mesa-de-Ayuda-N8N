"""
Endpoints HTTP de autenticacion (c-63a).

Responsabilidad:
    Define las rutas POST /api/v1/auth/login, /refresh y /logout. La capa HTTP
    recibe/deserializa el payload, delega la logica al auth_service y serializa
    la respuesta. No contiene logica de dominio.

Contrato aditivo (D6):
    El login conserva `access_token` y `token_type` y agrega `refresh_token` y
    `expires_in`. El access es de vida corta (15 min por defecto); el refresh
    rota en cada uso y se persiste hasheado.

Ventana residual (IAH-004):
    El logout revoca el refresh; el access ya emitido sigue valido hasta su TTL.
    La revocacion administrativa (`token_version`) es la unica que invalida
    access tokens de inmediato.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.core.exceptions import AccountLockedError
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    TokenResponse,
)
from app.services.auth_service import (
    LockoutSettings,
    authenticate_user,
    create_access_token,
    issue_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

# Alias de tipo para inyeccion de sesion via FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


def _error_body(code: str, message: str) -> dict:
    """Construye el cuerpo JSON estandar de respuesta de error."""
    return {"error": {"code": code, "message": message}}


def _build_token_response(user, refresh_value: str) -> TokenResponse:
    """Emite el access token (con `ver`) y arma la respuesta aditiva del login."""
    settings = get_settings()
    access_token = create_access_token(
        data={"sub": user.username, "ver": int(user.token_version or 0)},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia a settings, no un valor)
        algorithm=settings.jwt_algorithm,
        expires_delta=settings.jwt_access_expire_minutes,
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_value,
        expires_in=settings.jwt_access_expire_minutes * 60,
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Iniciar sesion y obtener el par de tokens",
)
async def login(payload: LoginRequest, session: SessionDep):
    """
    Autentica al usuario con username y password.

    Devuelve un access token JWT de vida corta y un refresh token opaco
    rotativo. El access debe enviarse en `Authorization: Bearer <access_token>`.

    Args:
        payload: Credenciales de inicio de sesion (username + password).

    Returns:
        TokenResponse con access_token, token_type, refresh_token y expires_in.

    Raises:
        JSONResponse 401 INVALID_CREDENTIALS: credenciales invalidas.
        JSONResponse 401 ACCOUNT_LOCKED: cuenta bloqueada por intentos fallidos.
    """
    settings = get_settings()
    try:
        user = await authenticate_user(
            session,
            payload.username,
            payload.password,
            lockout=LockoutSettings.from_settings(settings),
        )
    except AccountLockedError:
        # Se captura en la capa HTTP para que la sesion COMMITEE el estado de
        # bloqueo recien registrado (un raise dejaria el rollback del Unit of Work).
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "ACCOUNT_LOCKED",
                "Cuenta bloqueada temporalmente por intentos fallidos.",
            ),
        )

    if user is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "INVALID_CREDENTIALS", "Incorrect username or password"
            ),
        )

    _token, refresh_value = await issue_refresh_token(
        session, user_id=user.id, settings=settings
    )
    return _build_token_response(user, refresh_value)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Rotar el par de tokens con un refresh token valido",
)
async def refresh(payload: RefreshRequest, session: SessionDep):
    """
    Rota un refresh token valido: invalida el anterior y emite un par nuevo.

    Args:
        payload: Refresh token opaco presentado por el cliente.

    Returns:
        TokenResponse con el nuevo par de tokens.

    Raises:
        JSONResponse 401 INVALID_REFRESH_TOKEN: token inexistente, ya rotado,
            revocado o expirado (incluye la reutilizacion de un token rotado).
    """
    settings = get_settings()
    result = await rotate_refresh_token(
        session, provided_value=payload.refresh_token, settings=settings
    )
    if result is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "INVALID_REFRESH_TOKEN", "Refresh token invalido o revocado"
            ),
        )

    user, new_refresh_value = result
    return _build_token_response(user, new_refresh_value)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Revocar el refresh token (logout)",
)
async def logout(payload: LogoutRequest, session: SessionDep):
    """
    Revoca el refresh token del usuario (idempotente).

    El access ya emitido conserva validez hasta su TTL (ventana residual
    declarada, IAH-004). Un refresh revocado no puede volver a refrescar.

    Args:
        payload: Refresh token a revocar.

    Returns:
        LogoutResponse con un mensaje de confirmacion (HTTP 200).
    """
    await revoke_refresh_token(session, provided_value=payload.refresh_token)
    return LogoutResponse(message="Sesion cerrada")