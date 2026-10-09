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

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.core.exceptions import AccountLockedError
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    MfaEnrollResponse,
    MfaVerifyRequest,
    RefreshRequest,
    TokenResponse,
)
from app.services import mfa_service
from app.services.auth_service import (
    LockoutSettings,
    authenticate_user,
    create_access_token,
    create_mfa_ticket,
    decode_mfa_ticket,
    issue_refresh_token,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.services.privilege_service import user_is_privileged

router = APIRouter(prefix="/auth", tags=["Auth"])

# Alias de tipo para inyeccion de sesion via FastAPI Depends
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]


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
        key_id=settings.jwt_key_id,
    )
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        refresh_token=refresh_value,
        expires_in=settings.jwt_access_expire_minutes * 60,
    )


def _build_login_response(user, refresh_value: str) -> LoginResponse:
    """Arma la respuesta aditiva del login en el flujo de un paso (c-63b)."""
    token = _build_token_response(user, refresh_value)  # gitleaks:allow (referencia/fixture, no un valor real)
    return LoginResponse(
        access_token=token.access_token,
        token_type=token.token_type,
        refresh_token=token.refresh_token,
        expires_in=token.expires_in,
        mfa_required=False,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    response_model_exclude_none=True,
    summary="Iniciar sesion (un paso, o reto de segundo factor)",
)
async def login(payload: LoginRequest, session: SessionDep):
    """
    Autentica al usuario con username y password.

    Devuelve un access token JWT de vida corta y un refresh token opaco
    rotativo. Si la cuenta es privilegiada, tiene MFA activo y la bandera
    `mfa_required_for_privileged` esta encendida, devuelve un estado "segundo
    factor requerido" con un ticket corto y SIN emitir token (IAH-007).

    Args:
        payload: Credenciales de inicio de sesion (username + password).

    Returns:
        LoginResponse con access_token/token_type (y refresh_token/expires_in) en
        el flujo de un paso, o con mfa_required/mfa_ticket en el reto MFA.

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

    # Reto de segundo factor (IAH-007): SOLO privilegiada + MFA activo + bandera.
    if (
        settings.mfa_required_for_privileged
        and user.totp_enabled
        and await user_is_privileged(session, user)
    ):
        ticket = create_mfa_ticket(user, settings)
        return LoginResponse(mfa_required=True, mfa_ticket=ticket)

    _token, refresh_value = await issue_refresh_token(
        session, user_id=user.id, settings=settings
    )
    return _build_login_response(user, refresh_value)



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


# ── MFA: enrollment y verificacion del segundo factor (c-63b, IAH-006/007) ────


@router.post(
    "/mfa/enroll",
    response_model=MfaEnrollResponse,
    summary="Iniciar el enrollment del segundo factor TOTP",
)
async def mfa_enroll(session: SessionDep, current_user: CurrentUserDep):
    """
    Inicia/confirma el enrollment de MFA para la cuenta autenticada.

    Devuelve el URI `otpauth://`, el secreto y los codigos de recuperacion. El
    secreto se persiste CIFRADO at-rest y los codigos como hashes bcrypt; el
    material en claro se muestra UNA sola vez.

    Autorizacion (S6): restringido a cuentas PRIVILEGIADAS. El gating NO
    reintroduce el chicken-and-egg: una cuenta privilegiada SIN MFA activo
    (`totp_enabled=False`) inicia sesion en un solo paso, obtiene un access token
    y llega a este endpoint. El reto de segundo factor solo aparece cuando el MFA
    YA esta activo; si esa cuenta pierde el dispositivo Y los codigos, aplica el
    reset administrativo documentado (OQ-B2), no el enrollment.

    Returns:
        MfaEnrollResponse con otpauth_uri, secret y recovery_codes.

    Raises:
        HTTPException 403: si la cuenta autenticada no es privilegiada.
    """
    settings = get_settings()
    if not await user_is_privileged(session, current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere una cuenta privilegiada para el enrollment de MFA.",
        )
    enrollment = await mfa_service.start_enrollment(session, current_user, settings)
    return MfaEnrollResponse(
        otpauth_uri=enrollment.otpauth_uri,
        secret=enrollment.secret,
        recovery_codes=enrollment.recovery_codes,
    )


@router.post(
    "/mfa/verify",
    response_model=TokenResponse,
    summary="Completar el login con el segundo factor",
)
async def mfa_verify(payload: MfaVerifyRequest, session: SessionDep):
    """
    Completa el login validando el segundo factor (TOTP o recuperacion).

    Presenta el ticket corto emitido por `/auth/login` junto con un codigo TOTP
    valido o un codigo de recuperacion no consumido; emite el par de tokens con
    los campos actuales del contrato.

    Raises:
        JSONResponse 401 INVALID_MFA_TICKET: ticket ausente, vencido o invalido.
        JSONResponse 401 INVALID_MFA_CODE: segundo factor invalido.
    """
    settings = get_settings()

    username = decode_mfa_ticket(payload.mfa_ticket, settings)
    if username is None:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "INVALID_MFA_TICKET", "Ticket de segundo factor invalido o expirado"
            ),
        )

    user = await UserRepository(session).get_by_username(username)
    if user is None or not user.is_active:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "INVALID_MFA_TICKET", "Ticket de segundo factor invalido o expirado"
            ),
        )

    verified = await mfa_service.verify_second_factor(
        session,
        user,
        code=payload.code,
        recovery_code=payload.recovery_code,
        settings=settings,
    )
    if not verified:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content=_error_body(
                "INVALID_MFA_CODE", "Segundo factor invalido o expirado"
            ),
        )

    _token, refresh_value = await issue_refresh_token(
        session, user_id=user.id, settings=settings
    )
    return _build_token_response(user, refresh_value)