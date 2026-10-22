"""
Endpoints HTTP de autenticacion (c-63a).

Responsabilidad:
    Define las rutas POST /api/v1/auth/login, /refresh y /logout. La capa HTTP
    recibe/deserializa el payload, delega la logica al auth_service y serializa
    la respuesta. No contiene logica de dominio.

Contrato de tokens (c-91, IAH-014):
    El login conserva `access_token`, `token_type` y `expires_in` (access de 30
    min por defecto, IAH-003). El REFRESH ya NO viaja en el cuerpo: se entrega en
    una cookie `HttpOnly` + `Secure` + `SameSite` que setean `login`, `mfa/verify`
    y `refresh`, y que `logout` limpia. `/refresh` y `/logout` leen el refresh de
    la cookie y verifican el `Origin` (CSRF).

Ventana residual (IAH-004):
    El logout revoca el refresh; el access ya emitido sigue valido hasta su TTL.
    La revocacion administrativa (`token_version`) es la unica que invalida
    access tokens de inmediato.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.auth_cookies import (
    clear_refresh_cookie,
    origin_is_trusted,
    read_refresh_cookie,
    set_refresh_cookie,
)
from app.core.database import get_db_session
from app.core.exceptions import AccountLockedError
from app.core.security import get_current_user
from app.models.user import User
from app.repositories.empleado_repository import EmpleadoRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import (
    AlcanceResponse,
    IdentidadActualResponse,
    LoginRequest,
    LoginResponse,
    LogoutResponse,
    MfaEnrollResponse,
    MfaVerifyRequest,
    TokenResponse,
)
from app.services import mfa_service
from app.services.incident_visibility import alcance_desde_empleado
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


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    """Respuesta de error con el envelope estandar `{"error": {...}}`."""
    return JSONResponse(status_code=status_code, content=_error_body(code, message))


def _create_access_token_for(user, settings) -> str:
    """Emite el access token del usuario (con `ver` y el `kid` activo)."""
    return create_access_token(
        data={"sub": user.username, "ver": int(user.token_version or 0)},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia a settings, no un valor)
        algorithm=settings.jwt_algorithm,
        expires_delta=settings.jwt_access_expire_minutes,
        key_id=settings.jwt_key_id,
    )


def _token_response_body(user, settings) -> TokenResponse:
    """Cuerpo del contrato de tokens SIN el refresh (viaja en cookie, IAH-014)."""
    return TokenResponse(
        access_token=_create_access_token_for(user, settings),  # gitleaks:allow (resultado de una llamada, no un secreto)
        token_type="bearer",
        expires_in=settings.jwt_access_expire_minutes * 60,
    )


def _refresh_cookie_max_age(settings) -> int:
    """Segundos de vigencia de la cookie de refresh (ventana deslizante)."""
    return settings.jwt_refresh_expire_minutes * 60


@router.post(
    "/login",
    response_model=LoginResponse,
    response_model_exclude_none=True,
    summary="Iniciar sesion (un paso, o reto de segundo factor)",
)
async def login(payload: LoginRequest, session: SessionDep, response: Response):
    """
    Autentica al usuario con username y password.

    Devuelve un access token JWT (30 min por defecto) y entrega el refresh opaco
    en una cookie HttpOnly (IAH-014). Si la cuenta es privilegiada, tiene MFA
    activo y la bandera `mfa_required_for_privileged` esta encendida, devuelve un
    estado "segundo factor requerido" con un ticket corto y SIN emitir token.

    Args:
        payload: Credenciales de inicio de sesion (username + password).
        response: Respuesta inyectada donde se setea la cookie de refresh.

    Returns:
        LoginResponse con access_token/token_type/expires_in en el flujo de un
        paso, o con mfa_required/mfa_ticket en el reto MFA.

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
    set_refresh_cookie(
        response,
        refresh_value,
        settings,
        max_age_seconds=_refresh_cookie_max_age(settings),
    )
    return LoginResponse(
        access_token=_create_access_token_for(user, settings),  # gitleaks:allow (resultado de una llamada, no un secreto)
        token_type="bearer",
        expires_in=settings.jwt_access_expire_minutes * 60,
        mfa_required=False,
    )



@router.post(
    "/refresh",
    response_model=TokenResponse,
    response_model_exclude_none=True,
    summary="Rotar el refresh (por cookie) y emitir un access nuevo",
)
async def refresh(request: Request, session: SessionDep, response: Response):
    """
    Rota el refresh presentado en la cookie HttpOnly y renueva la cookie.

    Lee el refresh SOLO de la cookie (IAH-014). Verifica el `Origin` para mitigar
    CSRF (solo estos endpoints operan sobre la cookie). El cuerpo devuelve un
    access nuevo sin exponer el refresh.

    Returns:
        TokenResponse con el access nuevo (el refresh viaja en la cookie rotada).

    Raises:
        JSONResponse 403 CSRF_ORIGIN_REJECTED: origen no confiable.
        JSONResponse 401 INVALID_REFRESH_TOKEN: sin cookie, o token inexistente,
            ya rotado, revocado o expirado (reutilizacion incluida).
    """
    settings = get_settings()

    if not origin_is_trusted(request.headers.get("origin"), settings):
        return _error_response(
            status.HTTP_403_FORBIDDEN,
            "CSRF_ORIGIN_REJECTED",
            "Origen no confiable para operar sobre la sesion.",
        )

    provided = read_refresh_cookie(request, settings)
    if not provided:
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_REFRESH_TOKEN",
            "Refresh token invalido o revocado",
        )

    result = await rotate_refresh_token(
        session, provided_value=provided, settings=settings
    )
    if result is None:
        return _error_response(
            status.HTTP_401_UNAUTHORIZED,
            "INVALID_REFRESH_TOKEN",
            "Refresh token invalido o revocado",
        )

    user, new_refresh_value = result
    set_refresh_cookie(
        response,
        new_refresh_value,
        settings,
        max_age_seconds=_refresh_cookie_max_age(settings),
    )
    return _token_response_body(user, settings)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    summary="Revocar el refresh (por cookie) y limpiar la cookie (logout)",
)
async def logout(request: Request, session: SessionDep, response: Response):
    """
    Revoca el refresh presentado en la cookie y la limpia (idempotente).

    Verifica el `Origin` (CSRF). El access ya emitido conserva validez hasta su
    TTL (ventana residual declarada, IAH-004). Un refresh revocado no puede
    volver a refrescar.

    Returns:
        LogoutResponse con un mensaje de confirmacion (HTTP 200).

    Raises:
        JSONResponse 403 CSRF_ORIGIN_REJECTED: origen no confiable.
    """
    settings = get_settings()

    if not origin_is_trusted(request.headers.get("origin"), settings):
        return _error_response(
            status.HTTP_403_FORBIDDEN,
            "CSRF_ORIGIN_REJECTED",
            "Origen no confiable para operar sobre la sesion.",
        )

    provided = read_refresh_cookie(request, settings)
    if provided:
        await revoke_refresh_token(session, provided_value=provided)

    clear_refresh_cookie(response, settings)
    return LogoutResponse(message="Sesion cerrada")


# ── Identidad y alcance de la sesion (c-81, IAH-012) ─────────────────────────


@router.get(
    "/me",
    response_model=IdentidadActualResponse,
    summary="Identidad efectiva y alcance de la sesion actual",
)
async def me(
    session: SessionDep, current_user: CurrentUserDep
) -> IdentidadActualResponse:
    """
    Devuelve la identidad efectiva de la sesion y su alcance DERIVADO.

    ADITIVO y de SOLO LECTURA. No modifica el contrato de login/refresh/logout.
    Recomputa el alcance por request reutilizando la derivacion existente
    (`EmpleadoRepository.get_by_user_id` + `alcance_desde_empleado`, que lee el
    registro unico de politica de rol) SIN duplicar el mapeo rol -> alcance. La
    ruta solo orquesta: route -> (repositorio + servicio) -> models.

    Returns:
        IdentidadActualResponse con username, rol (o nulo) y alcance.modo
        (PROPIO | GLOBAL | SECTOR | VACIO).

    Raises:
        HTTPException 401: si la solicitud no esta autenticada.
    """
    empleado = await EmpleadoRepository(session).get_by_user_id(current_user.id)
    alcance = alcance_desde_empleado(empleado)
    # `Empleado.rol` es una columna String: se serializa su valor textual (la
    # normalizacion de enum vive en `politica_de_rol`, ya consumida por el
    # servicio de alcance; la ruta no duplica ese mapeo).
    rol = None
    if empleado is not None:
        rol = getattr(empleado.rol, "value", empleado.rol)
    return IdentidadActualResponse(
        username=current_user.username,
        rol=rol,
        alcance=AlcanceResponse(modo=alcance.modo.value),
    )


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
    response_model_exclude_none=True,
    summary="Completar el login con el segundo factor",
)
async def mfa_verify(
    payload: MfaVerifyRequest, session: SessionDep, response: Response
):
    """
    Completa el login validando el segundo factor (TOTP o recuperacion).

    Presenta el ticket corto emitido por `/auth/login` junto con un codigo TOTP
    valido o un codigo de recuperacion no consumido; emite el access y entrega el
    refresh en la cookie HttpOnly (IAH-014).

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
    set_refresh_cookie(
        response,
        refresh_value,
        settings,
        max_age_seconds=_refresh_cookie_max_age(settings),
    )
    return _token_response_body(user, settings)