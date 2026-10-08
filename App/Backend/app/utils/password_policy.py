"""
Politica de contrasenas reutilizable (IAH-001, c-63a).

Responsabilidad:
    Valida la fortaleza de una contrasena nueva o cambiada contra una politica
    configurable: longitud minima, lista local de claves comunes, rechazo de
    claves derivables del username y rechazo de reutilizacion reciente.

Decisiones (design.md D2, OQ-1=A):
    - Sin dependencias nuevas (se descarto zxcvbn y el corpus HaveIBeenPwned
      porque requieren red y rompen el subconjunto offline).
    - Sin composicion artificial obligatoria ni rotacion forzada (NIST 800-63B):
      se aceptan passphrases largas.
    - El modulo es reutilizable y se cablea al UNICO punto de provisionamiento
      existente (`auth_service.get_password_hash`). El endpoint de alta/cambio
      de usuario y el historial PERSISTIDO de contrasenas se difieren a c-63b.

Limitacion declarada (OQ-1=A):
    El escenario "reutilizacion reciente" esta cubierto por el validador
    recibiendo `history_hashes`, pero NO existe todavia un almacen persistido
    de historial de hashes en esta fase. El llamador que provee el historial
    (endpoint de alta/cambio) es follow-up de c-63b.

Rechazo:
    `validate_password` lanza `PasswordPolicyViolation`, que transporta un
    codigo estable y se puede traducir al sobre de error estandar via
    `build_policy_envelope` / el manejador HTTP registrado en
    `core/error_handlers.py`.
"""

from __future__ import annotations

from collections.abc import Callable, Collection, Sequence

from app.core.exceptions import AppBaseException

# ── Codigos estables de violacion ─────────────────────────────────────────────

PASSWORD_TOO_SHORT = "PASSWORD_TOO_SHORT"
PASSWORD_TOO_COMMON = "PASSWORD_TOO_COMMON"
PASSWORD_DERIVED_FROM_USERNAME = "PASSWORD_DERIVED_FROM_USERNAME"
PASSWORD_REUSED = "PASSWORD_REUSED"

# Longitud minima por defecto (configurable via settings.password_min_length).
DEFAULT_MIN_LENGTH = 12

# Lista local de claves comunes. NO se consulta una fuente externa: el corpus
# es local y determinista para no romper el subconjunto offline de la suite.
DEFAULT_COMMON_PASSWORDS: frozenset[str] = frozenset(
    {
        "password",
        "password1",
        "password123",
        "password1234",
        "123456",
        "1234567",
        "12345678",
        "123456789",
        "1234567890",
        "12345678910",
        "qwertyuiop",
        "qwerty123",
        "administrator",
        "contrasena",
        "contraseña",
        "admin123",
        "admin1234",
        "administrador",
        "letmein123",
        "welcome123",
        "iloveyou123",
        "monkey123",
        "dragon123",
        "football123",
        "sunshine123",
        "princess123",
        "mesa1234",
        "mesadeayuda",
        "cambiar-clave",
        "colocolo123",
    }
)


class PasswordPolicyViolation(AppBaseException):
    """La contrasena no cumple la politica.

    Transporta un `code` estable (uno de los `PASSWORD_*`) ademas del mensaje y
    los detalles opcionales. Se traduce al sobre de error estandar.
    """

    def __init__(
        self, code: str, message: str, details: dict | None = None
    ) -> None:
        super().__init__(message, details)
        self.code = code


def build_policy_envelope(violation: PasswordPolicyViolation) -> dict:
    """Construye el sobre de error estandar a partir de una violacion."""
    body: dict = {
        "error": {"code": violation.code, "message": violation.message}
    }
    if violation.details:
        body["error"]["details"] = violation.details
    return body


def _normalize(value: str) -> str:
    """Normaliza para comparaciones: minusculas y solo alfanumerico."""
    return "".join(ch for ch in value.lower() if ch.isalnum())


def _default_verify_hash(plain: str, hashed: str) -> bool:
    """Verificacion bcrypt por defecto para el chequeo de reutilizacion."""
    import bcrypt

    try:
        return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def _is_derivable_from_username(password: str, username: str) -> bool:
    """True si la clave es igual, contiene o es una variacion trivial del username."""
    norm_user = _normalize(username)
    norm_pass = _normalize(password)
    if not norm_user or not norm_pass:
        return False
    if norm_pass == norm_user:
        return True
    # Contencion en cualquier sentido, evitando usernames demasiado cortos que
    # producirian falsos positivos sobre passphrases legitimas.
    if len(norm_user) >= 3 and norm_user in norm_pass:
        return True
    if len(norm_pass) >= 3 and norm_pass in norm_user:
        return True
    return False


def validate_password(
    password: str,
    *,
    username: str | None = None,
    history_hashes: Sequence[str] = (),
    min_length: int = DEFAULT_MIN_LENGTH,
    common_passwords: Collection[str] | None = None,
    verify_hash: Callable[[str, str], bool] | None = None,
) -> None:
    """Valida `password` contra la politica; lanza `PasswordPolicyViolation`.

    Args:
        password: Clave en texto plano a validar.
        username: Username de la cuenta; habilita el rechazo de claves
            derivables. Si es None o vacio, ese chequeo se omite.
        history_hashes: Hashes de contrasenas previas; habilita el rechazo de
            reutilizacion reciente. Vacio = sin historial (fase c-63a).
        min_length: Longitud minima configurable.
        common_passwords: Lista de claves comunes; por defecto la local.
        verify_hash: Funcion de verificacion (para tests o bcrypt alternativo).

    Raises:
        PasswordPolicyViolation: Si la clave incumple cualquier regla.
    """
    if len(password) < min_length:
        raise PasswordPolicyViolation(
            PASSWORD_TOO_SHORT,
            f"La contrasena debe tener al menos {min_length} caracteres.",
            {"min_length": min_length, "actual_length": len(password)},
        )

    commons = (
        DEFAULT_COMMON_PASSWORDS if common_passwords is None else common_passwords
    )
    if password.lower() in {c.lower() for c in commons}:
        raise PasswordPolicyViolation(
            PASSWORD_TOO_COMMON,
            "La contrasena es demasiado comun.",
            {"reason": "common_password"},
        )

    if username and _is_derivable_from_username(password, username):
        raise PasswordPolicyViolation(
            PASSWORD_DERIVED_FROM_USERNAME,
            "La contrasena no debe derivarse del nombre de usuario.",
            {"reason": "derived_from_username"},
        )

    if history_hashes:
        checker = verify_hash or _default_verify_hash
        for previous_hash in history_hashes:
            if previous_hash and checker(password, previous_hash):
                raise PasswordPolicyViolation(
                    PASSWORD_REUSED,
                    "No se puede reutilizar una contrasena reciente.",
                    {"reason": "reused_recent_password"},
                )


__all__ = [
    "PasswordPolicyViolation",
    "build_policy_envelope",
    "validate_password",
    "DEFAULT_COMMON_PASSWORDS",
    "DEFAULT_MIN_LENGTH",
    "PASSWORD_TOO_SHORT",
    "PASSWORD_TOO_COMMON",
    "PASSWORD_DERIVED_FROM_USERNAME",
    "PASSWORD_REUSED",
]