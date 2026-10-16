"""IAH-013 (c-91): cierre de sesion por inactividad (refresh DESLIZANTE).

La inactividad se gobierna por la ventana de vigencia del refresh
(`jwt_refresh_expire_minutes`, 7 dias por defecto), RENOVADA en cada rotacion
exitosa. NO se agrega columna de inactividad ni migracion; NO hay tope absoluto
de vida de la sesion. La evaluacion usa un `now` inyectable (sin tiempos reales).

Estos tests operan a nivel de SERVICIO (`issue_refresh_token` /
`rotate_refresh_token`) reutilizando el fixture `db_session` (SQLite), de modo
que no dependen del transporte HTTP de la cookie.
"""

from datetime import datetime, timedelta, timezone

import pytest

from app.config.settings import get_settings
from app.core.security import get_password_hash
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.token_repository import TokenRepository
from app.services.auth_service import (
    _hash_refresh_value,
    issue_refresh_token,
    rotate_refresh_token,
)

T0 = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
IDLE_MINUTES = get_settings().jwt_refresh_expire_minutes


def _aware(value: datetime) -> datetime:
    """Normaliza a UTC aware (SQLite devuelve datetimes naive)."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


async def _make_user(session) -> User:
    user = User(
        username="idleuser",
        hashed_password=get_password_hash(
            "correct horse battery staple", username="idleuser"
        ),
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


# ── RED/GREEN: la actividad dentro de la ventana renueva la vigencia ─────────


@pytest.mark.asyncio
async def test_rotation_within_window_renews_the_idle_window(db_session):
    """Una rotacion dentro de los 7 dias renueva la ventana (sliding)."""
    settings = get_settings()
    user = await _make_user(db_session)
    issued, value = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )
    assert _aware(issued.expires_at) == T0 + timedelta(minutes=IDLE_MINUTES)

    six_days = T0 + timedelta(days=6)
    result = await rotate_refresh_token(
        db_session, provided_value=value, settings=settings, now=six_days
    )
    assert result is not None
    rotated_user, new_value = result
    assert rotated_user.id == user.id
    assert new_value != value

    # La nueva ventana vence 7 dias DESPUES de la rotacion (no de la emision).
    rotated = await TokenRepository(db_session).get_by_hash(
        _hash_refresh_value(new_value)
    )
    assert _aware(rotated.expires_at) == six_days + timedelta(minutes=IDLE_MINUTES)


# ── RED/GREEN: la sesion inactiva de 7 dias se revoca y cierra ───────────────


@pytest.mark.asyncio
async def test_refresh_is_rejected_and_revoked_after_idle_window(db_session):
    """Pasada la ventana sin rotar, el refresh se rechaza y queda revocado."""
    settings = get_settings()
    user = await _make_user(db_session)
    issued, value = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )

    after = T0 + timedelta(minutes=IDLE_MINUTES + 1)
    result = await rotate_refresh_token(
        db_session, provided_value=value, settings=settings, now=after
    )
    assert result is None

    # El token quedo revocado: la sesion esta cerrada.
    await db_session.refresh(issued)
    assert issued.revoked_at is not None


# ── TRIANGULAR: la inactividad es por sesion, no por cuenta ──────────────────


@pytest.mark.asyncio
async def test_idle_is_per_session_not_per_account(db_session):
    """Solo la sesion inactiva se revoca; otra sesion del mismo usuario sigue."""
    settings = get_settings()
    user = await _make_user(db_session)

    # Sesion A: emitida en T0 y NUNCA rotada (inactiva).
    _to_a, value_a = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )
    # Sesion B: emitida en T0 y renovada a los 6 dias (activa).
    _to_b, value_b = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )
    renewed = await rotate_refresh_token(
        db_session,
        provided_value=value_b,
        settings=settings,
        now=T0 + timedelta(days=6),
    )
    assert renewed is not None
    _user_b, value_b2 = renewed

    day8 = T0 + timedelta(days=8)
    # A esta inactiva -> rechazada.
    assert (
        await rotate_refresh_token(
            db_session, provided_value=value_a, settings=settings, now=day8
        )
        is None
    )
    # B sigue viva (renovada hace menos de 7 dias) -> rota.
    assert (
        await rotate_refresh_token(
            db_session, provided_value=value_b2, settings=settings, now=day8
        )
        is not None
    )


# ── TRIANGULAR: la ventana es configurable y vence exactamente ───────────────


@pytest.mark.asyncio
async def test_idle_window_is_configurable_and_expires_exactly(db_session):
    """Con una ventana de 1 min, la revocacion ocurre exactamente al vencer."""
    settings = get_settings().model_copy(update={"jwt_refresh_expire_minutes": 1})
    user = await _make_user(db_session)

    # Justo antes del vencimiento (59 s): sigue valido.
    _to, value = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )
    assert (
        await rotate_refresh_token(
            db_session,
            provided_value=value,
            settings=settings,
            now=T0 + timedelta(seconds=59),
        )
        is not None
    )

    # Exactamente al vencer (1 min): rechazado.
    _to2, value2 = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=T0
    )
    assert (
        await rotate_refresh_token(
            db_session,
            provided_value=value2,
            settings=settings,
            now=T0 + timedelta(minutes=1),
        )
        is None
    )
