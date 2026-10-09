"""IAH-006: MFA TOTP para cuentas privilegiadas (c-63b, Fase B).

Cubren enrollment (URI otpauth + secreto), verificacion RFC 6238, rechazo de
codigos invalidos/expirados, codigos de recuperacion de un solo uso hasheados,
y el secreto TOTP cifrado at-rest (nunca en claro).
"""

from datetime import datetime, timedelta, timezone

import pyotp
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.models.user import User
from app.services import mfa_service

RECOVERY_COUNT = 3


async def _make_user(session: AsyncSession, username: str) -> User:
    user = User(
        username=username,
        hashed_password="not-a-real-hash",
        is_active=True,
        is_privileged=True,
    )
    session.add(user)
    await session.flush()
    return user


# ── Enrollment ───────────────────────────────────────────────────────────────


async def test_enrollment_returns_otpauth_uri_and_secret(db_session: AsyncSession):
    """Escenario: el enrollment entrega el URI otpauth y el secreto."""
    user = await _make_user(db_session, "enroll_user")

    result = await mfa_service.start_enrollment(
        db_session,
        user,
        get_settings(),
        recovery_code_count=RECOVERY_COUNT,
    )

    assert result.otpauth_uri.startswith("otpauth://totp/")
    assert "secret=" in result.otpauth_uri
    assert result.secret
    assert len(result.recovery_codes) == RECOVERY_COUNT
    assert len(set(result.recovery_codes)) == RECOVERY_COUNT
    assert user.totp_enabled is True
    # El secreto devuelto es el que el ORM descifra desde la columna.
    assert user.totp_secret == result.secret


async def test_enrollment_confirms_with_otpauth_secret(db_session: AsyncSession):
    """Triangulacion: el secreto del URI coincide con el devuelto."""
    user = await _make_user(db_session, "enroll_uri_user")
    result = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )

    parsed = pyotp.parse_uri(result.otpauth_uri)
    assert parsed.secret == result.secret


# ── Verificacion TOTP ────────────────────────────────────────────────────────


async def test_valid_totp_verifies(db_session: AsyncSession):
    """Escenario: un codigo TOTP valido verifica."""
    user = await _make_user(db_session, "totp_valid_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    code = pyotp.TOTP(enrollment.secret).now()

    assert (
        await mfa_service.verify_second_factor(
            db_session, user, code=code, recovery_code=None, settings=get_settings()
        )
        is True
    )


async def test_invalid_totp_is_rejected(db_session: AsyncSession):
    """Escenario: un codigo TOTP incorrecto es rechazado."""
    user = await _make_user(db_session, "totp_invalid_user")
    await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )

    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code="000000",
            recovery_code=None,
            settings=get_settings(),
        )
        is False
    )


async def test_expired_totp_is_rejected(db_session: AsyncSession):
    """Escenario: un codigo fuera de la ventana de tiempo es rechazado."""
    user = await _make_user(db_session, "totp_expired_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    far_past = datetime.now(timezone.utc) - timedelta(minutes=10)
    old_code = pyotp.TOTP(enrollment.secret).at(far_past)

    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code=old_code,
            recovery_code=None,
            settings=get_settings(),
        )
        is False
    )


async def test_totp_within_window_boundary_verifies(db_session: AsyncSession):
    """Triangulacion: un codigo del periodo anterior (dentro de la ventana) verifica."""
    user = await _make_user(db_session, "totp_boundary_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    previous = datetime.now(timezone.utc) - timedelta(seconds=30)
    boundary_code = pyotp.TOTP(enrollment.secret).at(previous)

    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code=boundary_code,
            recovery_code=None,
            settings=get_settings(),
        )
        is True
    )


# ── Codigos de recuperacion ──────────────────────────────────────────────────


async def test_recovery_code_is_single_use(db_session: AsyncSession):
    """Escenario: un codigo de recuperacion valido se consume tras usarse."""
    user = await _make_user(db_session, "recovery_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    code = enrollment.recovery_codes[0]

    first = await mfa_service.verify_second_factor(
        db_session, user, code=None, recovery_code=code, settings=get_settings()
    )
    second = await mfa_service.verify_second_factor(
        db_session, user, code=None, recovery_code=code, settings=get_settings()
    )

    assert first is True
    assert second is False


async def test_recovery_codes_are_hashed(db_session: AsyncSession):
    """El valor persistido de los codigos de recuperacion es un hash bcrypt."""
    import json

    user = await _make_user(db_session, "recovery_hash_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    await db_session.flush()

    raw = (
        await db_session.execute(
            text("SELECT mfa_recovery_codes FROM users WHERE id = :id"),
            {"id": user.id},
        )
    ).scalar_one()
    stored = json.loads(raw)

    assert len(stored) == RECOVERY_COUNT
    for plain, hashed in zip(enrollment.recovery_codes, stored):
        assert hashed != plain
        assert hashed.startswith("$2")


async def test_recovery_code_accepts_normalized_variants(db_session: AsyncSession):
    """Triangulacion: la verificacion tolera guiones y mayusculas/minusculas.

    El codigo se hashea en forma normalizada (sin guiones, mayusculas); el
    usuario puede presentarlo con o sin guiones y en minusculas.
    """
    user = await _make_user(db_session, "recovery_norm_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )

    # Variante 1: sin guiones y en minusculas.
    lower_no_dash = enrollment.recovery_codes[0].replace("-", "").lower()
    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code=None,
            recovery_code=lower_no_dash,
            settings=get_settings(),
        )
        is True
    )

    # Variante 2: forma canonica con guion (otro codigo, el primero ya se consumio).
    canonical = enrollment.recovery_codes[1]
    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code=None,
            recovery_code=canonical,
            settings=get_settings(),
        )
        is True
    )


# ── Secreto cifrado at-rest ──────────────────────────────────────────────────


async def test_totp_secret_is_encrypted_at_rest(db_session: AsyncSession):
    """Escenario: el secreto TOTP no se almacena en claro."""
    user = await _make_user(db_session, "secret_at_rest_user")
    enrollment = await mfa_service.start_enrollment(
        db_session, user, get_settings(), recovery_code_count=RECOVERY_COUNT
    )
    await db_session.flush()

    raw = (
        await db_session.execute(
            text("SELECT totp_secret FROM users WHERE id = :id"), {"id": user.id}
        )
    ).scalar_one()

    assert raw is not None
    assert raw != enrollment.secret
    assert enrollment.secret not in raw


async def test_verify_requires_enabled_mfa(db_session: AsyncSession):
    """Triangulacion: sin enrollment (totp_enabled falso) la verificacion falla."""
    user = await _make_user(db_session, "not_enrolled_user")

    assert (
        await mfa_service.verify_second_factor(
            db_session,
            user,
            code="123456",
            recovery_code=None,
            settings=get_settings(),
        )
        is False
    )
