"""IAH-008: rotacion del secreto JWT con keyring `kid` y ventana de solapamiento.

Cubren la firma con la clave activa + `kid` aditivo, la aceptacion acotada de
tokens firmados con la clave anterior dentro de la ventana, el rechazo tras
cerrarse, la compatibilidad de los tokens legacy sin `kid`, y la cota de
verificacion (a lo sumo las claves vigentes del keyring, nunca ilimitada).

Los tests unitarios construyen `Settings` con `_env_file=None` para no depender
del `.env` real; los de integracion inyectan el instante de la ventana.
"""

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from jose import JWTError, jwt
from pydantic import ValidationError

from app.config.settings import Settings
from app.core import jwt_keyring
from app.core.security import get_current_user
from app.models.user import User
from app.services.auth_service import create_access_token

ACTIVE_SECRET = "active-secret-0123456789abcdef0123456789abcdef"  # gitleaks:allow (referencia/fixture, no un valor real)
PREVIOUS_SECRET = "previous-secret-0123456789abcdef0123456789"  # gitleaks:allow (referencia/fixture, no un valor real)
GHOST_SECRET = "ghost-secret-0123456789abcdef0123456789abcd"  # gitleaks:allow (referencia/fixture, no un valor real)
ACTIVE_KID = "v1"
PREVIOUS_KID = "v0"

# Claves Fernet validas (no contienen datos reales).
FERNET_ACTIVE = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
FERNET_PREVIOUS = "N-Kutrp44LM5v5HP0YZZzj-liZG0hJ4oQY7VhiLJMUM="


def make_settings(**overrides) -> Settings:
    """Construye Settings aislado del `.env` real, con overrides de keyring."""
    base: dict = {
        "_env_file": None,
        "database_url": "postgresql+asyncpg://u:p@localhost:5432/db",
        "gemini_api_key": "test-gemini-key",
        "pseudonymization_encryption_key": FERNET_ACTIVE,
        "jwt_secret_key": ACTIVE_SECRET,
    }
    base.update(overrides)
    return Settings(**base)


def make_ns_settings(**overrides) -> SimpleNamespace:
    """Settings duck-typed (sin validacion pydantic) para probar el keyring."""
    ns = SimpleNamespace(
        jwt_secret_key=ACTIVE_SECRET,
        jwt_algorithm="HS256",
        jwt_key_id=ACTIVE_KID,
        jwt_previous_secret_key="",
        jwt_previous_key_id="",
        jwt_previous_key_expires_at="",
    )
    for key, value in overrides.items():
        setattr(ns, key, value)
    return ns


def _future() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=30)


def sign_with(secret: str, *, kid: str | None, sub: str = "rotuser") -> str:
    """Firma un token de prueba con (o sin) `kid` en el header."""
    headers = {"kid": kid} if kid else None
    return jwt.encode(
        {"sub": sub, "exp": _future()},
        secret,
        algorithm="HS256",
        headers=headers,
    )


# ── Configuracion aditiva (D-C2) ─────────────────────────────────────────────


def test_settings_keyring_defaults_are_retrocompatible():
    """Sin clave anterior el keyring se comporta como el sistema actual."""
    settings = make_settings()

    assert settings.jwt_key_id == "v1"
    assert settings.jwt_previous_secret_key == ""
    assert settings.jwt_previous_key_id == ""
    assert settings.jwt_previous_key_expires_at == ""
    # Sin clave anterior no hay segunda clave vigente.
    assert jwt_keyring.previous_key(settings) is None


# ── Guard de ids del keyring (S1) ────────────────────────────────────────────


def test_settings_rejects_identical_keyring_ids():
    """Con clave anterior, un `kid` anterior igual al activo es config invalida."""
    with pytest.raises(ValidationError):
        make_settings(
            jwt_key_id="v1",
            jwt_previous_secret_key=PREVIOUS_SECRET,
            jwt_previous_key_id="v1",
        )


def test_settings_accepts_distinct_keyring_ids():
    """Triangulacion: con ids distintos la configuracion es valida."""
    settings = make_settings(
        jwt_key_id="v1",
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id="v0",
    )
    assert settings.jwt_previous_key_id == "v0"
    assert jwt_keyring.previous_key(settings) is not None


def test_settings_allows_same_id_without_previous_key():
    """Triangulacion: sin clave anterior el guard no aplica (retrocompatible)."""
    settings = make_settings(jwt_key_id="v1", jwt_previous_key_id="v1")
    assert settings.jwt_previous_secret_key == ""


# ── Validacion estricta de la ventana (S3) ───────────────────────────────────


def test_settings_rejects_malformed_previous_expiry():
    """Un `expires_at` ilegible es config invalida (no abre ventana indefinida)."""
    with pytest.raises(ValidationError):
        make_settings(
            jwt_previous_secret_key=PREVIOUS_SECRET,
            jwt_previous_key_id=PREVIOUS_KID,
            jwt_previous_key_expires_at="not-a-date",
        )


def test_settings_accepts_valid_and_empty_previous_expiry():
    """Triangulacion: un instante ISO valido y el vacio son configuracion valida."""
    valid = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at="2026-11-01T00:00:00+00:00",
    )
    assert valid.jwt_previous_key_expires_at == "2026-11-01T00:00:00+00:00"

    empty = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at="",
    )
    assert empty.jwt_previous_key_expires_at == ""


def test_previous_key_fails_closed_on_malformed_expiry():
    """Fail-closed: un `expires_at` ilegible cierra la ventana (no la abre)."""
    settings = make_ns_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at="not-a-date",
    )

    assert jwt_keyring.previous_key(settings) is None

    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)
    with pytest.raises(JWTError):
        jwt_keyring.decode_token(token, settings)


# ── Firma con la clave activa + kid (escenario IAH-008) ──────────────────────


def test_new_token_uses_active_key_and_carries_kid():
    """La firma nueva usa la clave activa y lleva su `kid` en el header."""
    settings = make_settings()
    token = create_access_token(
        data={"sub": "rotuser"},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia/fixture, no un valor real)
        algorithm=settings.jwt_algorithm,
        key_id=settings.jwt_key_id,
    )

    header = jwt.get_unverified_header(token)
    assert header["kid"] == ACTIVE_KID

    # Verificable con la clave activa.
    payload = jwt_keyring.decode_token(token, settings)
    assert payload["sub"] == "rotuser"


# ── Ventana de solapamiento (D-C1) ───────────────────────────────────────────


def test_token_signed_with_previous_key_is_accepted_within_window():
    """Un token de la clave anterior se acepta mientras la ventana esta abierta."""
    now = datetime.now(timezone.utc)
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at=(now + timedelta(hours=1)).isoformat(),
    )
    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)

    payload = jwt_keyring.decode_token(token, settings, now=now)
    assert payload["sub"] == "rotuser"


def test_token_with_previous_key_is_rejected_after_window():
    """Cerrrada la ventana, un token de la clave anterior se rechaza."""
    now = datetime.now(timezone.utc)
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at=(now - timedelta(seconds=1)).isoformat(),
    )
    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)

    with pytest.raises(JWTError):
        jwt_keyring.decode_token(token, settings, now=now)


# ── Tokens legacy sin kid (transicion) ───────────────────────────────────────


def test_legacy_token_without_kid_is_accepted_via_active_key():
    """Un token legacy sin `kid` se valida con la clave activa."""
    settings = make_settings()
    token = sign_with(ACTIVE_SECRET, kid=None)

    payload = jwt_keyring.decode_token(token, settings)
    assert payload["sub"] == "rotuser"


def test_window_closes_exactly_at_expiry():
    """Triangulacion: en el instante exacto de vencimiento la ventana esta cerrada."""
    expires = datetime.now(timezone.utc)
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at=expires.isoformat(),
    )
    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)

    with pytest.raises(JWTError):
        jwt_keyring.decode_token(token, settings, now=expires)


def test_legacy_token_without_kid_falls_back_to_previous_key():
    """Sin `kid`, la verificacion prueba la activa y luego la anterior abierta."""
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
    )
    token = sign_with(PREVIOUS_SECRET, kid=None)

    payload = jwt_keyring.decode_token(token, settings)
    assert payload["sub"] == "rotuser"


# ── Cota de verificacion (D-C1) ──────────────────────────────────────────────


def test_unknown_kid_is_rejected_without_trying_extra_keys(monkeypatch):
    """Un `kid` fuera del keyring se rechaza sin intentar ninguna clave."""
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
    )
    token = sign_with(GHOST_SECRET, kid="ghost")

    attempts: list[int] = []
    original = jwt.decode

    def counting(*args, **kwargs):
        attempts.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(jwt_keyring.jwt, "decode", counting)
    with pytest.raises(JWTError):
        jwt_keyring.decode_token(token, settings)

    assert attempts == []


def test_verification_is_bounded_to_two_keys(monkeypatch):
    """Sin `kid`, se intentan como maximo las dos claves vigentes del keyring."""
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
    )
    token = sign_with(GHOST_SECRET, kid=None)

    attempts: list[int] = []
    original = jwt.decode

    def counting(*args, **kwargs):
        attempts.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(jwt_keyring.jwt, "decode", counting)
    with pytest.raises(JWTError):
        jwt_keyring.decode_token(token, settings)

    assert len(attempts) == 2


# ── Integracion con get_current_user (respuesta 401) ─────────────────────────


async def test_get_current_user_accepts_previous_key_within_window(
    db_session, monkeypatch
):
    """La dependencia real acepta un access de la clave anterior en la ventana."""
    user = User(username="rotuser", hashed_password="x", is_active=True)
    db_session.add(user)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at=(now + timedelta(hours=1)).isoformat(),
    )
    monkeypatch.setattr("app.core.security.get_settings", lambda: settings)

    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)
    current = await get_current_user(token, db_session)

    assert current.username == "rotuser"


async def test_get_current_user_rejects_previous_key_after_window(
    db_session, monkeypatch
):
    """Cerrada la ventana, la dependencia responde 401 (HTTPException)."""
    user = User(username="rotuser", hashed_password="x", is_active=True)
    db_session.add(user)
    await db_session.flush()

    now = datetime.now(timezone.utc)
    settings = make_settings(
        jwt_previous_secret_key=PREVIOUS_SECRET,
        jwt_previous_key_id=PREVIOUS_KID,
        jwt_previous_key_expires_at=(now - timedelta(seconds=1)).isoformat(),
    )
    monkeypatch.setattr("app.core.security.get_settings", lambda: settings)

    token = sign_with(PREVIOUS_SECRET, kid=PREVIOUS_KID)
    with pytest.raises(HTTPException) as exc:
        await get_current_user(token, db_session)

    assert exc.value.status_code == 401
