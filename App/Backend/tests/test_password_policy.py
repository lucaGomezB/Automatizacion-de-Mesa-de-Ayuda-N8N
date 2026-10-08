"""Tests de la politica de contrasenas (IAH-001).

Cubren el validador puro (`validate_password`), el cableado al punto de
provisionamiento (`get_password_hash`) y el sobre de error estandar.

OQ-1 = A (design.md): el endpoint de alta/cambio y el historial persistido de
hashes se difieren a c-63b. El "reuso reciente" queda cubierto por el validador
recibiendo una lista de hashes, pero SIN historial persistido todavia.
"""

import bcrypt
import pytest

from app.config.settings import get_settings
from app.services.auth_service import get_password_hash, verify_password
from app.utils.password_policy import (
    PASSWORD_DERIVED_FROM_USERNAME,
    PASSWORD_REUSED,
    PASSWORD_TOO_COMMON,
    PASSWORD_TOO_SHORT,
    PasswordPolicyViolation,
    build_policy_envelope,
    validate_password,
)

PASSPHRASE = "correct horse battery staple"


# ── IAH-001: validacion pura ──────────────────────────────────────────────────


def test_short_password_is_rejected():
    """Una clave por debajo de la longitud minima se rechaza con codigo propio."""
    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password("short11char", min_length=12)
    assert exc.value.code == PASSWORD_TOO_SHORT
    assert exc.value.message


def test_exact_minimum_length_is_accepted():
    """Triangulacion del borde: exactamente 12 caracteres no comunes se acepta."""
    validate_password("abcdefghijkl", min_length=12)


def test_passphrase_with_spaces_is_accepted():
    """NIST 800-63B: se aceptan passphrases largas con espacios."""
    validate_password(PASSPHRASE)


def test_common_password_is_rejected():
    """Una clave de la lista local de comunes se rechaza."""
    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password("administrator")
    assert exc.value.code == PASSWORD_TOO_COMMON


def test_password_containing_username_is_rejected():
    """Una clave que contiene el username es derivable y se rechaza."""
    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password("admin12345678", username="admin")
    assert exc.value.code == PASSWORD_DERIVED_FROM_USERNAME


def test_password_trivial_variation_of_username_is_rejected():
    """Una variacion trivial (normalizada) del username se rechaza."""
    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password("Admin.2024!!", username="admin2024")
    assert exc.value.code == PASSWORD_DERIVED_FROM_USERNAME


def test_unrelated_username_does_not_reject_passphrase():
    """Triangulacion: un username no relacionado no afecta una passphrase valida."""
    validate_password(PASSPHRASE, username="jperez")


def test_reused_password_is_rejected():
    """Una clave que coincide con un hash del historial se rechaza."""
    history_hash = bcrypt.hashpw(
        PASSPHRASE.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")

    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password(PASSPHRASE, history_hashes=[history_hash])
    assert exc.value.code == PASSWORD_REUSED


def test_different_password_not_in_history_is_accepted():
    """Triangulacion: una clave distinta a los hashes del historial se acepta."""
    other_hash = bcrypt.hashpw(b"otra-clave-larga-123", bcrypt.gensalt()).decode(
        "utf-8"
    )
    validate_password(PASSPHRASE, history_hashes=[other_hash])


# ── Sobre de error estandar ───────────────────────────────────────────────────


def test_policy_violation_builds_standard_error_envelope():
    """El rechazo se traduce al sobre estandar {error:{code,message,details?}}."""
    with pytest.raises(PasswordPolicyViolation) as exc:
        validate_password("admin12345678", username="admin")
    envelope = build_policy_envelope(exc.value)
    assert set(envelope) == {"error"}
    assert envelope["error"]["code"] == PASSWORD_DERIVED_FROM_USERNAME
    assert envelope["error"]["message"]


# ── Cableado al punto de provisionamiento (OQ-1=A) ───────────────────────────


def test_get_password_hash_enforces_policy_by_default():
    """El unico punto de provisionamiento aplica la politica por defecto."""
    with pytest.raises(PasswordPolicyViolation):
        get_password_hash("admin123", username="admin")


def test_get_password_hash_accepts_compliant_password_and_verifies():
    """Una clave valida se hashea y verifica con bcrypt (no se guarda en claro)."""
    hashed = get_password_hash(PASSPHRASE, username="jperez")
    assert hashed != PASSPHRASE
    assert verify_password(PASSPHRASE, hashed)
    assert not verify_password("otra-clave-distinta", hashed)


def test_get_password_hash_can_grandfather_dev_credentials():
    """Las credenciales sembradas de desarrollo se grandfather explicitamente."""
    hashed = get_password_hash("admin123", enforce_policy=False)
    assert verify_password("admin123", hashed)


def test_get_password_hash_uses_settings_min_length():
    """Los parametros de policy se leen de settings (defaults no invalidan dev)."""
    settings = get_settings()
    assert settings.password_min_length >= 12
    with pytest.raises(PasswordPolicyViolation):
        get_password_hash("oncechars11", username="x")