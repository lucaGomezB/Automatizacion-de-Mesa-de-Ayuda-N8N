"""Servicio del segundo factor TOTP (c-63b, IAH-006).

Responsabilidad:
    Implementa el enrollment y la verificacion del segundo factor basado en TOTP
    (RFC 6238) para las cuentas privilegiadas: generacion del secreto y del URI
    `otpauth://` (via `pyotp`), verificacion de codigos dentro de la ventana de
    tiempo, y codigos de recuperacion de un solo uso almacenados como hashes
    bcrypt.

Cifrado at-rest:
    El secreto TOTP se persiste en `User.totp_secret`, columna declarada con el
    TypeDecorator `EncryptedText` (`utils/encryption.py`): el ORM cifra al
    escribir y descifra al leer, de modo que el valor en la base es ciphertext
    Fernet. Este modulo NUNCA registra el secreto ni los codigos en claro.

Dependencia:
    `pyotp` (pure-Python) calcula TOTP/HOTP. Se ancla en `requirements.txt`;
    es una dependencia de terceros que debe auditarse (supply chain).
"""

import json
import secrets
from dataclasses import dataclass

import bcrypt
import pyotp
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings
from app.core.logging import get_logger
from app.models.user import User

logger = get_logger(__name__)

# Ventana de tolerancia en periodos de 30 s (RFC 6238). 1 = acepta el periodo
# anterior y el siguiente, cubriendo el desfase de reloj del autenticador.
_TOTP_VALID_WINDOW = 1


@dataclass(frozen=True)
class MfaEnrollment:
    """Resultado del enrollment: se muestra UNA sola vez al usuario."""

    secret: str
    otpauth_uri: str
    recovery_codes: list[str]


def generate_secret() -> str:
    """Genera un secreto TOTP base32 (RFC 4648)."""
    return pyotp.random_base32()


def build_otpauth_uri(secret: str, username: str, issuer: str) -> str:
    """Construye el URI `otpauth://totp/...` para la app autenticadora."""
    return pyotp.TOTP(secret).provisioning_uri(name=username, issuer_name=issuer)


def generate_recovery_codes(count: int) -> list[str]:
    """Genera `count` codigos de recuperacion unicos en formato XXXXX-XXXXX."""
    codes: set[str] = set()
    while len(codes) < count:
        raw = secrets.token_hex(5).upper()  # 10 caracteres hexadecimales
        codes.add(f"{raw[:5]}-{raw[5:]}")
    return sorted(codes)


def _hash_recovery_code(code: str) -> str:
    """Hash bcrypt de un codigo de recuperacion (nunca se guarda en claro)."""
    return bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def _normalize_recovery_code(code: str) -> str:
    """Normaliza un codigo presentado: sin guiones y en mayusculas."""
    return code.replace("-", "").replace(" ", "").upper()


def _load_hashes(user: User) -> list[str]:
    """Deserializa la lista de hashes bcrypt almacenada en la cuenta."""
    if not user.mfa_recovery_codes:
        return []
    try:
        parsed = json.loads(user.mfa_recovery_codes)
    except (TypeError, ValueError):
        return []
    return [h for h in parsed if isinstance(h, str)]


async def start_enrollment(
    session: AsyncSession,
    user: User,
    settings: Settings,
    *,
    recovery_code_count: int | None = None,
) -> MfaEnrollment:
    """Inicia/confirma el enrollment de MFA para una cuenta.

    Genera un secreto TOTP nuevo, lo persiste (cifrado at-rest por el
    TypeDecorator), marca `totp_enabled` y genera/almacena los codigos de
    recuperacion hasheados. Devuelve el URI y los codigos en claro UNA sola vez.

    Args:
        recovery_code_count: Override inyectable (tests); por defecto el valor
            de `settings.mfa_recovery_code_count`.
    """
    count = (
        recovery_code_count
        if recovery_code_count is not None
        else settings.mfa_recovery_code_count
    )

    secret = generate_secret()
    plain_codes = generate_recovery_codes(count)
    # Se hashea la forma NORMALIZADA (sin guiones, mayusculas) para que la
    # verificacion sea tolerante al formato con que el usuario copia el codigo.
    hashed = [_hash_recovery_code(_normalize_recovery_code(code)) for code in plain_codes]

    user.totp_secret = secret
    user.totp_enabled = True
    user.mfa_recovery_codes = json.dumps(hashed)
    await session.flush()

    logger.info(
        "mfa_enrollment_started",
        user_id=user.id,
        recovery_codes=len(plain_codes),
    )
    return MfaEnrollment(
        secret=secret,
        otpauth_uri=build_otpauth_uri(secret, user.username, settings.mfa_issuer),
        recovery_codes=plain_codes,
    )


def verify_totp(
    user: User,
    code: str,
    settings: Settings,
    *,
    at=None,
) -> bool:
    """Verifica un codigo TOTP contra el secreto de la cuenta (RFC 6238)."""
    if not user.totp_enabled or not user.totp_secret:
        return False
    if not code:
        return False
    if not code.isdigit():
        return False

    totp = pyotp.TOTP(user.totp_secret)
    return bool(totp.verify(code, for_time=at, valid_window=_TOTP_VALID_WINDOW))


async def consume_recovery_code(
    session: AsyncSession, user: User, code: str
) -> bool:
    """Consume un codigo de recuperacion valido (de un solo uso).

    Compara el codigo normalizado contra los hashes bcrypt almacenados; al
    coincidir, elimina ese hash y persiste la lista restante.
    """
    if not code:
        return False

    normalized = _normalize_recovery_code(code)
    hashes = _load_hashes(user)
    for hashed in hashes:
        if bcrypt.checkpw(normalized.encode("utf-8"), hashed.encode("utf-8")):
            hashes.remove(hashed)
            user.mfa_recovery_codes = json.dumps(hashes)
            await session.flush()
            logger.info("mfa_recovery_code_consumed", user_id=user.id)
            return True
    return False


async def verify_second_factor(
    session: AsyncSession,
    user: User,
    *,
    code: str | None,
    recovery_code: str | None,
    settings: Settings,
    at=None,
) -> bool:
    """Verifica el segundo factor: codigo TOTP o codigo de recuperacion.

    Cualquiera de los dos concede el segundo factor; el codigo de recuperacion
    queda consumido si se usa.
    """
    if user is None or not user.totp_enabled:
        return False

    if code and verify_totp(user, code, settings, at=at):
        return True
    if recovery_code:
        return await consume_recovery_code(session, user, recovery_code)
    return False
