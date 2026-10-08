"""Tests del bloqueo por intentos fallidos (IAH-002, c-63a).

El bloqueo es por CUENTA, con umbral/ventana/duracion configurables y flag
apagado por defecto. La logica recibe un reloj (`now`) y una configuracion
(`LockoutSettings`) inyectables, por lo que los tests son deterministas y no
dependen de tiempos reales.
"""

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.exceptions import AccountLockedError
from app.core.security import get_password_hash
from app.main import create_app
from app.models.user import User
from app.services.auth_service import (
    LockoutSettings,
    authenticate_user,
    issue_refresh_token,
)

NOW = datetime(2026, 10, 8, 12, 0, 0, tzinfo=timezone.utc)
PASSWORD = "correct horse battery staple"

ENABLED = LockoutSettings(
    enabled=True, threshold=5, duration_minutes=15, window_minutes=15
)


async def _make_user(session, username="operador", password=PASSWORD) -> User:
    user = User(
        username=username,
        hashed_password=get_password_hash(password, username=username),
        is_active=True,
    )
    session.add(user)
    await session.flush()
    return user


# ── Service-level: lockout ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_failed_attempt_below_threshold_returns_none_and_counts(db_session):
    """Un fallo por debajo del umbral devuelve None e incrementa el contador."""
    user = await _make_user(db_session, password=PASSWORD)

    result = await authenticate_user(
        db_session, "operador", "wrong-password", lockout=ENABLED, now=NOW
    )

    assert result is None
    assert user.failed_attempts == 1
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_reaching_threshold_locks_account(db_session):
    """Al alcanzar el umbral la cuenta queda bloqueada con locked_until."""
    await _make_user(db_session, password=PASSWORD)

    for _ in range(ENABLED.threshold - 1):
        assert (
            await authenticate_user(
                db_session, "operador", "wrong", lockout=ENABLED, now=NOW
            )
            is None
        )

    with pytest.raises(AccountLockedError):
        await authenticate_user(
            db_session, "operador", "wrong", lockout=ENABLED, now=NOW
        )

    user = await db_session.get(User, 1)
    assert user.locked_until is not None
    locked_until = user.locked_until
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    expected = NOW + timedelta(minutes=ENABLED.duration_minutes)
    assert locked_until == expected


@pytest.mark.asyncio
async def test_locked_account_rejects_valid_credentials(db_session):
    """Una cuenta bloqueada rechaza credenciales VALIDAS antes de expirar."""
    await _make_user(db_session, password=PASSWORD)

    for _ in range(ENABLED.threshold - 1):
        assert (
            await authenticate_user(
                db_session, "operador", "wrong", lockout=ENABLED, now=NOW
            )
            is None
        )
    with pytest.raises(AccountLockedError):
        await authenticate_user(
            db_session, "operador", "wrong", lockout=ENABLED, now=NOW
        )

    with pytest.raises(AccountLockedError):
        await authenticate_user(
            db_session, "operador", PASSWORD, lockout=ENABLED, now=NOW
        )


@pytest.mark.asyncio
async def test_successful_login_resets_counter(db_session):
    """Un login exitoso resetea el contador de intentos fallidos."""
    await _make_user(db_session, password=PASSWORD)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=NOW
    )

    user = await authenticate_user(
        db_session, "operador", PASSWORD, lockout=ENABLED, now=NOW
    )

    assert user is not None
    assert user.failed_attempts == 0
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_lock_expires_and_valid_login_succeeds(db_session):
    """Transcurrida la duracion, el bloqueo se limpia y el login es exitoso."""
    await _make_user(db_session, password=PASSWORD)
    for _ in range(ENABLED.threshold - 1):
        assert (
            await authenticate_user(
                db_session, "operador", "wrong", lockout=ENABLED, now=NOW
            )
            is None
        )
    with pytest.raises(AccountLockedError):
        await authenticate_user(
            db_session, "operador", "wrong", lockout=ENABLED, now=NOW
        )

    later = NOW + timedelta(minutes=ENABLED.duration_minutes + 1)
    user = await authenticate_user(
        db_session, "operador", PASSWORD, lockout=ENABLED, now=later
    )

    assert user is not None
    assert user.failed_attempts == 0
    assert user.locked_until is None


@pytest.mark.asyncio
async def test_success_clears_window_start(db_session):
    """Triangulacion: el login exitoso limpia el inicio de ventana."""
    user = await _make_user(db_session, password=PASSWORD)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=NOW
    )
    assert user.lockout_window_start is not None

    await authenticate_user(
        db_session, "operador", PASSWORD, lockout=ENABLED, now=NOW
    )
    assert user.failed_attempts == 0
    assert user.lockout_window_start is None


@pytest.mark.asyncio
async def test_window_resets_stale_failures(db_session):
    """Triangulacion: fallos fuera de la ventana no acumulan hacia el bloqueo."""
    await _make_user(db_session, password=PASSWORD)

    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=NOW
    )
    user = await db_session.get(User, 1)
    assert user.failed_attempts == 1
    window_start = user.lockout_window_start
    if window_start.tzinfo is None:
        window_start = window_start.replace(tzinfo=timezone.utc)

    # El segundo intento llega fuera de la ventana dedicada: se reinicia antes
    # de incrementar (vuelve a 1) y la ventana se re-ancla.
    later = window_start + timedelta(minutes=ENABLED.window_minutes + 1)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=later
    )

    user = await db_session.get(User, 1)
    assert user.failed_attempts == 1, (
        "Un fallo viejo fuera de la ventana no debe acumular"
    )
    reanchored = user.lockout_window_start
    if reanchored.tzinfo is None:
        reanchored = reanchored.replace(tzinfo=timezone.utc)
    assert reanchored == later


@pytest.mark.asyncio
async def test_window_uses_dedicated_column_not_updated_at(db_session):
    """W2: la ventana se ancla en `lockout_window_start`, no en `updated_at`.

    Un update ajeno que mueve `updated_at` al pasado no debe reiniciar el
    contador mientras la ventana dedicada siga vigente.
    """
    from sqlalchemy import text

    await _make_user(db_session, password=PASSWORD)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=NOW
    )
    user = await db_session.get(User, 1)
    assert user.failed_attempts == 1

    # Simula un update ajeno (p. ej. is_active) que mueve updated_at al pasado
    # sin tocar lockout_window_start.
    await db_session.execute(
        text("UPDATE users SET updated_at = '2020-01-01 00:00:00' WHERE id = :id"),
        {"id": user.id},
    )
    # Forzar la recarga desde la base para exponer el `updated_at` movido; si la
    # logica dependiera de el, reiniciaria el contador.
    await db_session.refresh(user)
    assert user.updated_at.year == 2020

    # Dentro de la ventana dedicada: debe acumular (2), no reiniciar (1).
    within_window = NOW + timedelta(minutes=1)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=within_window
    )

    user = await db_session.get(User, 1)
    assert user.failed_attempts == 2, (
        "La ventana debe depender de lockout_window_start, no de updated_at"
    )


@pytest.mark.asyncio
async def test_lock_expiry_clears_window_start(db_session):
    """Triangulacion: al expirar el bloqueo tambien se limpia la ventana."""
    await _make_user(db_session, password=PASSWORD)
    for _ in range(ENABLED.threshold - 1):
        assert (
            await authenticate_user(
                db_session, "operador", "wrong", lockout=ENABLED, now=NOW
            )
            is None
        )
    with pytest.raises(AccountLockedError):
        await authenticate_user(
            db_session, "operador", "wrong", lockout=ENABLED, now=NOW
        )

    later = NOW + timedelta(minutes=ENABLED.duration_minutes + 1)
    user = await authenticate_user(
        db_session, "operador", PASSWORD, lockout=ENABLED, now=later
    )
    assert user is not None
    assert user.lockout_window_start is None


# ── W2: row lock (SELECT ... FOR UPDATE) ─────────────────────────────────────


@pytest.mark.asyncio
async def test_get_by_username_for_update_returns_user(db_session):
    """El helper de lock devuelve el usuario (no rompe en SQLite)."""
    from app.repositories.user_repository import UserRepository

    await _make_user(db_session, username="lockuser")
    user = await UserRepository(db_session).get_by_username_for_update("lockuser")
    assert user is not None
    assert user.username == "lockuser"


def test_for_update_compiles_on_postgres_and_is_ignored_on_sqlite():
    """Prueba estructural: el lock se emite en PostgreSQL y SQLite lo ignora."""
    from sqlalchemy import select
    from sqlalchemy.dialects import postgresql, sqlite

    stmt = select(User).where(User.username == "x").with_for_update()
    pg_sql = str(stmt.compile(dialect=postgresql.dialect()))
    assert "FOR UPDATE" in pg_sql

    sqlite_sql = str(stmt.compile(dialect=sqlite.dialect()))
    assert "FOR UPDATE" not in sqlite_sql


@pytest.mark.asyncio
async def test_authenticate_uses_locking_helper_when_lockout_enabled(
    db_session, monkeypatch
):
    """La autenticacion adquiere el lock de fila via el helper FOR UPDATE."""
    from app.repositories.user_repository import UserRepository

    calls = {"n": 0}
    original = UserRepository.get_by_username_for_update

    async def spy(self, username):
        calls["n"] += 1
        return await original(self, username)

    monkeypatch.setattr(UserRepository, "get_by_username_for_update", spy)

    await _make_user(db_session, password=PASSWORD)
    await authenticate_user(
        db_session, "operador", "wrong", lockout=ENABLED, now=NOW
    )
    assert calls["n"] == 1


@pytest.mark.asyncio
async def test_flag_off_preserves_development_flow(db_session):
    """Con el flag apagado no hay bloqueo observable y la credencial valida entra."""
    user = await _make_user(db_session, password=PASSWORD)
    disabled = LockoutSettings(
        enabled=False, threshold=5, duration_minutes=15, window_minutes=15
    )

    for _ in range(10):
        assert (
            await authenticate_user(
                db_session, "operador", "wrong", lockout=disabled, now=NOW
            )
            is None
        )

    assert user.failed_attempts == 0
    assert user.locked_until is None

    assert (
        await authenticate_user(
            db_session, "operador", PASSWORD, lockout=disabled, now=NOW
        )
        is not None
    )


@pytest.mark.asyncio
async def test_unknown_user_never_locks_and_returns_none(db_session):
    """Un usuario inexistente devuelve None (no revela existencia ni bloquea)."""
    assert (
        await authenticate_user(
            db_session, "nadie", "cualquiera", lockout=ENABLED, now=NOW
        )
        is None
    )


# ── Route-level: ACCOUNT_LOCKED observable ───────────────────────────────────


@pytest.fixture
async def locked_client(engine, monkeypatch):
    """Cliente ASGI con lockout habilitado y umbral bajo (2)."""
    from httpx import ASGITransport, AsyncClient

    from app.config.settings import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "account_lockout_enabled", True)
    monkeypatch.setattr(settings, "account_lockout_threshold", 2)
    monkeypatch.setattr(settings, "account_lockout_duration_minutes", 15)
    monkeypatch.setattr(settings, "account_lockout_window_minutes", 15)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        session.add(
            User(
                username="bloqueable",
                hashed_password=get_password_hash(
                    PASSWORD, username="bloqueable"
                ),
                is_active=True,
            )
        )
        await session.commit()

    app = create_app()

    async def override_db():
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db_session] = override_db

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac

    async with factory() as session:
        from sqlalchemy import delete

        await session.execute(delete(User))
        await session.commit()


@pytest.mark.asyncio
async def test_login_returns_account_locked_code_after_threshold(locked_client):
    """El login responde 401 ACCOUNT_LOCKED al superar el umbral, sin emitir token."""
    r1 = await locked_client.post(
        "/api/v1/auth/login",
        json={"username": "bloqueable", "password": "wrong"},
    )
    assert r1.status_code == 401
    assert r1.json()["error"]["code"] == "INVALID_CREDENTIALS"

    r2 = await locked_client.post(
        "/api/v1/auth/login",
        json={"username": "bloqueable", "password": "wrong"},
    )
    assert r2.status_code == 401
    assert r2.json()["error"]["code"] == "ACCOUNT_LOCKED"

    r3 = await locked_client.post(
        "/api/v1/auth/login",
        json={"username": "bloqueable", "password": PASSWORD},
    )
    assert r3.status_code == 401
    assert r3.json()["error"]["code"] == "ACCOUNT_LOCKED"
    assert "access_token" not in r3.json()


@pytest.mark.asyncio
async def test_issue_refresh_token_persists_only_hash(db_session):
    """Triangulacion: el valor emitido no se persiste; solo su hash."""
    from app.config.settings import get_settings

    user = await _make_user(db_session, username="refreshuser")
    settings = get_settings()

    stored, value = await issue_refresh_token(
        db_session, user_id=user.id, settings=settings, now=NOW
    )

    assert stored.token_hash != value
    assert value not in stored.token_hash
    assert len(stored.token_hash) == 64