"""
Servicio de autenticacion de usuarios.

Responsabilidad:
    Implementa la logica de negocio del flujo de login: verificacion de
    credenciales contra el hash bcrypt almacenado, generacion de tokens
    JWT firmados, y resolucion de usuarios desde la base de datos.

    Capa intermedia entre routes/auth.py (HTTP) y el modelo User (ORM).
    No contiene dependencias de FastAPI; es puramente logica de negocio.
"""

import hashlib
import secrets
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.core.exceptions import AccountLockedError
from app.core.logging import get_logger
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.repositories.user_repository import UserRepository
from app.utils.password_policy import validate_password

logger = get_logger(__name__)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifica que una password en texto plano coincida con su hash bcrypt.

    Args:
        plain_password: Password ingresada por el usuario en el login.
        hashed_password: Hash bcrypt almacenado en la base de datos.

    Returns:
        True si la password coincide, False en caso contrario.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(
    password: str,
    username: str | None = None,
    *,
    enforce_policy: bool = True,
    history_hashes: Sequence[str] = (),
    settings: Settings | None = None,
) -> str:
    """
    Genera el hash bcrypt de una password en texto plano.

    Es el UNICO punto de provisionamiento de contrasenas del sistema
    (OQ-1=A): por defecto aplica la politica de contrasenas (IAH-001) antes de
    hashear. Los seeds/scripts de desarrollo pueden grandfather credenciales
    debiles con `enforce_policy=False` (dev-only).

    Args:
        password: Password en texto plano a hashear.
        username: Username de la cuenta; habilita el rechazo de claves
            derivables del nombre de usuario.
        enforce_policy: Si True (default), valida contra la politica.
        history_hashes: Hashes previos para el chequeo de reutilizacion.
        settings: Settings inyectable (tests); por defecto `get_settings()`.

    Returns:
        String con el hash bcrypt.

    Raises:
        PasswordPolicyViolation: Si la password incumple la politica y
            `enforce_policy` es True.
    """
    if enforce_policy:
        effective = settings or get_settings()
        validate_password(
            password,
            username=username,
            history_hashes=history_hashes,
            min_length=effective.password_min_length,
        )
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def create_access_token(
    data: dict,
    secret: str,
    algorithm: str = "HS256",
    expires_delta: int | None = None,
    key_id: str | None = None,
) -> str:
    """
    Crea un token JWT firmado con los datos proporcionados.

    Todo token emitido lleva el claim `exp`: si no se especifica
    `expires_delta`, se usa settings.jwt_access_expire_minutes (vida corta,
    c-63a). Esto evita emitir tokens sin expiracion, que serian validos
    indefinidamente.

    Keyring `kid` (c-63c, IAH-008): cuando se pasa `key_id`, se agrega el `kid`
    de la clave activa como header aditivo del token. Los llamadores de
    produccion pasan `settings.jwt_key_id`; sin `key_id` el token no lleva el
    header (compatibilidad con tokens / tests existentes).

    Args:
        data: Payload a incluir en el token (tipicamente {"sub": username}).
        secret: Clave secreta para firmar el token.
        algorithm: Algoritmo de firma (por defecto HS256).
        expires_delta: Minutos hasta la expiracion. Si es None, se usa
            settings.jwt_access_expire_minutes.
        key_id: Identificador de la clave activa (`kid`) a incluir en el header.

    Returns:
        Token JWT codificado como string.
    """
    if expires_delta is None:
        expires_delta = get_settings().jwt_access_expire_minutes

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    headers = {"kid": key_id} if key_id else None
    encoded_jwt = jwt.encode(
        to_encode, secret, algorithm=algorithm, headers=headers
    )
    return encoded_jwt


# ── Ticket de segundo factor MFA (c-63b, IAH-007) ────────────────────────────

# Scope dedicado del ticket: lo distingue del access token y hace que
# `get_current_user` lo rechace en rutas protegidas.
MFA_TICKET_SCOPE = "mfa"


def create_mfa_ticket(
    user: User,
    settings: Settings,
    *,
    expires_delta_minutes: int | None = None,
) -> str:
    """Emite un ticket corto de segundo factor (JWT de scope `mfa`).

    NO es un access token: no lleva `ver`, no usa el keyring de rotacion JWT
    (c-63c) y `get_current_user` lo rechaza. Solo habilita
    `POST /auth/mfa/verify` por una ventana corta (D-B6).

    Desacople de c-63c (W1): el ticket se firma DIRECTAMENTE con el secreto JWT
    activo (`settings.jwt_secret_key`, HS256), sin `kid`. Durante una rotacion de
    claves, un ticket en vuelo emitido antes del cambio de clave PUEDE fallar la
    verificacion; se acepta por su TTL corto (5 min por defecto). El keyring de
    `kid`/solapamiento es exclusivo del access token (c-63c).
    """
    minutes = (
        expires_delta_minutes
        if expires_delta_minutes is not None
        else settings.mfa_ticket_expire_minutes
    )
    return create_access_token(
        data={"sub": user.username, "scope": MFA_TICKET_SCOPE},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia/fixture, no un valor real)
        algorithm=settings.jwt_algorithm,
        expires_delta=minutes,
    )


def decode_mfa_ticket(token: str, settings: Settings) -> str | None:
    """Valida un ticket de segundo factor y devuelve el username, o None.

    Rechaza tokens vencidos (exige `exp`), malformados o con un scope distinto
    de `mfa`. Verifica DIRECTAMENTE con el secreto JWT activo
    (`settings.jwt_secret_key`, HS256), sin keyring (W1): durante una rotacion de
    claves un ticket en vuelo puede fallar, lo cual es aceptable por su TTL corto.
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"require_exp": True},
        )
    except JWTError:
        return None

    if payload.get("scope") != MFA_TICKET_SCOPE:
        return None

    sub = payload.get("sub")
    return sub if isinstance(sub, str) else None


@dataclass(frozen=True)
class LockoutSettings:
    """Parametros del bloqueo por intentos fallidos (IAH-002).

    Es un value object inmutable e inyectable: los tests no dependen de tiempos
    reales ni de la configuracion global (`get_settings`), sino que pasan una
    instancia con `enabled`, `threshold`, `duration_minutes` y `window_minutes`.
    """

    enabled: bool
    threshold: int
    duration_minutes: int
    window_minutes: int

    @classmethod
    def from_settings(cls, settings: Settings) -> "LockoutSettings":
        return cls(
            enabled=settings.account_lockout_enabled,
            threshold=settings.account_lockout_threshold,
            duration_minutes=settings.account_lockout_duration_minutes,
            window_minutes=settings.account_lockout_window_minutes,
        )


def _ensure_aware(value: datetime) -> datetime:
    """Normaliza un datetime a UTC aware (SQLite devuelve datetimes naive)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def authenticate_user(
    session: AsyncSession,
    username: str,
    password: str,
    *,
    lockout: LockoutSettings | None = None,
    now: datetime | None = None,
) -> User | None:
    """
    Autentica un usuario por username y password, aplicando el bloqueo por
    intentos fallidos (IAH-002).

    Flujo:
        1. Resuelve el usuario y verifica que este activo.
        2. Si el flag esta habilitado y la cuenta esta bloqueada y no expiro,
           lanza `AccountLockedError` (rechaza incluso credenciales validas).
        3. Si el bloqueo expiro, lo limpia.
        4. Verifica la password. En fallo, registra el intento (si el flag esta
           habilitado) y, al alcanzar el umbral, bloquea la cuenta.
        5. En exito, resetea el contador si el flag esta habilitado.

    Args:
        session: Sesion de base de datos activa.
        username: Nombre de usuario a autenticar.
        password: Password en texto plano a verificar.
        lockout: Configuracion del bloqueo; por defecto se deriva de settings.
        now: Instante inyectable (tests); por defecto `datetime.now(UTC)`.

    Returns:
        Instancia de User si las credenciales son validas, None en caso contrario.

    Raises:
        AccountLockedError: Si la cuenta esta bloqueada y el bloqueo no expiro.
    """
    effective_lockout = lockout or LockoutSettings.from_settings(get_settings())
    current = now or _utcnow()

    # W2: se toma el lock de fila (SELECT ... FOR UPDATE) para serializar las
    # lecturas/escrituras concurrentes del contador de intentos fallidos de la
    # cuenta. En SQLite la clausula se ignora (suite offline intacta). El lock
    # se mantiene hasta el commit/rollback del Unit of Work.
    user = await UserRepository(session).get_by_username_for_update(username)

    if user is None:
        return None
    if not user.is_active:
        logger.info("auth_inactive_user", username=username)
        return None

    if effective_lockout.enabled and user.locked_until is not None:
        locked_until = _ensure_aware(user.locked_until)
        if current < locked_until:
            logger.warning("auth_account_locked", username=username, user_id=user.id)
            raise AccountLockedError()
        # El bloqueo expiro: limpiar estado (contador y ventana) antes de continuar.
        user.locked_until = None
        user.failed_attempts = 0
        user.lockout_window_start = None

    if not verify_password(password, user.hashed_password):
        if effective_lockout.enabled:
            await _register_failed_attempt(
                session, user, effective_lockout, current
            )
        return None

    if effective_lockout.enabled and (
        user.failed_attempts or user.locked_until is not None
    ):
        user.failed_attempts = 0
        user.locked_until = None
        user.lockout_window_start = None
        await session.flush()

    logger.info("auth_login_success", username=username, user_id=user.id)
    return user


async def _register_failed_attempt(
    session: AsyncSession,
    user: User,
    lockout: LockoutSettings,
    now: datetime,
) -> None:
    """Incrementa el contador de fallos y bloquea la cuenta al llegar al umbral.

    La ventana se evalua contra la columna DEDICADA `lockout_window_start` (W2),
    que se fija en el primer fallo de la racha y se re-ancla cuando la ventana
    previa expira. No se usa `updated_at`: un update ajeno a la autenticacion no
    debe reiniciar el contador.
    """
    window_start = user.lockout_window_start
    if user.failed_attempts > 0 and window_start is not None:
        if (now - _ensure_aware(window_start)) > timedelta(
            minutes=lockout.window_minutes
        ):
            user.failed_attempts = 0
            user.lockout_window_start = None

    if user.failed_attempts == 0 or user.lockout_window_start is None:
        user.lockout_window_start = now

    user.failed_attempts = (user.failed_attempts or 0) + 1

    if user.failed_attempts >= lockout.threshold:
        user.locked_until = now + timedelta(minutes=lockout.duration_minutes)
        await session.flush()
        logger.warning(
            "auth_account_lockout_triggered",
            username=user.username,
            user_id=user.id,
            threshold=lockout.threshold,
        )
        raise AccountLockedError()

    await session.flush()
    logger.info(
        "auth_failed_attempt",
        username=user.username,
        user_id=user.id,
        failed_attempts=user.failed_attempts,
    )


# ── Refresh tokens rotativos (IAH-003 / IAH-004) ────────────────────────────


def _hash_refresh_value(value: str) -> str:
    """SHA-256 hexadecimal de un refresh token opaco (nunca se guarda en claro)."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def generate_refresh_token_value() -> str:
    """Genera un refresh token opaco de alta entropia."""
    return secrets.token_urlsafe(48)


async def issue_refresh_token(
    session: AsyncSession,
    *,
    user_id: int,
    settings: Settings,
    now: datetime | None = None,
    rotated_from: int | None = None,
) -> tuple[RefreshToken, str]:
    """Emite y persiste (hasheado) un refresh token para el usuario.

    Returns:
        Tupla (fila persistida, valor opaco en claro) — el valor en claro solo
        se devuelve al cliente y nunca se persiste.
    """
    current = now or _utcnow()
    value = generate_refresh_token_value()
    expires_at = current + timedelta(minutes=settings.jwt_refresh_expire_minutes)
    token = await TokenRepository(session).create(
        user_id=user_id,
        token_hash=_hash_refresh_value(value),
        expires_at=expires_at,
        rotated_from=rotated_from,
    )
    return token, value


async def rotate_refresh_token(
    session: AsyncSession,
    *,
    provided_value: str,
    settings: Settings,
    now: datetime | None = None,
) -> tuple[User, str] | None:
    """Rota un refresh token valido: invalida el anterior y emite uno nuevo.

    Returns:
        Tupla (usuario, nuevo valor opaco) si el token es valido; None si el
        token no existe, esta revocado (incluye reutilizacion de uno ya rotado),
        expiro, o el usuario no existe / esta inactivo.
    """
    current = now or _utcnow()
    repo = TokenRepository(session)
    stored = await repo.get_by_hash(_hash_refresh_value(provided_value))

    if stored is None:
        return None
    if stored.revoked_at is not None:
        # Reutilizacion de un token ya rotado o revocado.
        logger.warning("auth_refresh_reuse_detected", token_id=stored.id)
        return None
    if current >= _ensure_aware(stored.expires_at):
        await repo.revoke(stored, now=current)
        return None

    user = await UserRepository(session).get_by_id(stored.user_id)
    if user is None or not user.is_active:
        return None

    await repo.revoke(stored, now=current)
    _new_token, new_value = await issue_refresh_token(
        session,
        user_id=user.id,
        settings=settings,
        now=current,
        rotated_from=stored.id,
    )
    logger.info("auth_refresh_rotated", user_id=user.id, token_id=stored.id)
    return user, new_value


async def revoke_refresh_token(
    session: AsyncSession,
    *,
    provided_value: str,
    now: datetime | None = None,
) -> bool:
    """Revoca (logout) un refresh token. Retorna True si existia y quedo revocado."""
    current = now or _utcnow()
    repo = TokenRepository(session)
    stored = await repo.get_by_hash(_hash_refresh_value(provided_value))
    if stored is None or stored.revoked_at is not None:
        return False
    await repo.revoke(stored, now=current)
    logger.info("auth_logout_revoked", token_id=stored.id, user_id=stored.user_id)
    return True


async def revoke_all_sessions(
    session: AsyncSession,
    *,
    user: User,
    now: datetime | None = None,
) -> int:
    """Revocacion administrativa: incrementa `token_version` y revoca los refresh.

    Invalida de inmediato todos los access tokens emitidos con la version
    anterior (via `get_current_user`) y todos los refresh activos. Retorna la
    cantidad de refresh revocados. Emite un evento estructurado sin datos
    sensibles (IAH-004).
    """
    current = now or _utcnow()
    user.token_version = (user.token_version or 0) + 1
    revoked = await TokenRepository(session).revoke_active_for_user(
        user.id, now=current
    )
    await session.flush()
    logger.warning(
        "auth_admin_revocation",
        user_id=user.id,
        token_version=user.token_version,
        revoked_refresh=revoked,
    )
    return revoked
