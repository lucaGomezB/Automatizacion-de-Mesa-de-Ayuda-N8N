"""Tests de expiracion, refresco rotativo y revocacion de tokens (IAH-003/004).

Cubren el contrato aditivo del login, la rotacion del refresh, el rechazo de
reutilizacion, la persistencia hasheada, el logout revocatorio, la revocacion
administrativa por `token_version` y la ventana residual declarada.

Desde c-91 (IAH-014) el refresh viaja en una cookie HttpOnly: el cliente usa
base `https://test` para que el jar de httpx acepte y reenvie la cookie `Secure`.
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import create_access_token, get_password_hash
from app.main import create_app
from app.models.user import User
from app.services.auth_service import revoke_all_sessions

PASSWORD = "correct horse battery staple"
COOKIE_NAME = "refresh_token"


@pytest_asyncio.fixture
async def seed_token_user(engine):
    """Siembra un usuario operable con contrasena que cumple la politica."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = User(
            username="tokenuser",
            hashed_password=get_password_hash(PASSWORD, username="tokenuser"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    yield {"username": "tokenuser", "password": PASSWORD, "user": user}

    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def token_client(engine):
    """Cliente ASGI sin bypass de auth (valida el JWT real)."""
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
        transport=ASGITransport(app=app),
        base_url="https://test",
        follow_redirects=True,
    ) as ac:
        yield ac


async def _login_response(client, username="tokenuser", password=PASSWORD):
    response = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response


async def _login(client, username="tokenuser", password=PASSWORD) -> dict:
    return (await _login_response(client, username, password)).json()


# ── IAH-003: contrato aditivo y expiracion ───────────────────────────────────


@pytest.mark.asyncio
async def test_login_contract_is_additive(token_client, seed_token_user):
    """El login conserva access_token/token_type y agrega expires_in; el refresh
    ya NO viaja en el cuerpo sino en la cookie (IAH-014)."""
    response = await _login_response(token_client)
    body = response.json()

    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert "refresh_token" not in body
    assert body["expires_in"] == 30 * 60
    # El refresh se entrega en la cookie HttpOnly.
    assert token_client.cookies.get(COOKIE_NAME)


@pytest.mark.asyncio
async def test_access_ttl_env_override_changes_expires_in(
    token_client, seed_token_user, monkeypatch
):
    """Triangulacion (c-91, D1): un override de entorno cambia `expires_in`."""
    from app.config.settings import get_settings

    monkeypatch.setenv("JWT_ACCESS_EXPIRE_MINUTES", "45")
    get_settings.cache_clear()
    try:
        body = await _login(token_client)
        assert body["expires_in"] == 45 * 60
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_expired_access_token_is_rejected(token_client, seed_token_user):
    """Un access pasado su expiracion devuelve 401."""
    from app.config.settings import get_settings

    settings = get_settings()
    expired = create_access_token(
        data={"sub": seed_token_user["username"]},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia a settings, no un valor)
        algorithm=settings.jwt_algorithm,
        expires_delta=-1,
    )
    response = await token_client.get(
        "/api/v1/incidentes/", headers={"Authorization": f"Bearer {expired}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_rotates_and_invalidates_previous(token_client, seed_token_user):
    """El refresco emite un par nuevo e invalida el refresh usado (por cookie)."""
    await _login(token_client)
    first_cookie = token_client.cookies.get(COOKIE_NAME)
    assert first_cookie

    r1 = await token_client.post("/api/v1/auth/refresh")
    assert r1.status_code == 200
    second = r1.json()
    assert second["access_token"]
    assert second["token_type"] == "bearer"
    assert "refresh_token" not in second
    assert token_client.cookies.get(COOKIE_NAME) != first_cookie

    # El token de refresco anterior ya no puede usarse (fue rotado).
    r2 = await token_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}={first_cookie}"},
    )
    assert r2.status_code == 401
    assert r2.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_refresh_reuse_of_rotated_token_is_rejected(
    token_client, seed_token_user
):
    """Triangulacion: presentar un refresh ya rotado se rechaza con 401."""
    await _login(token_client)
    original = token_client.cookies.get(COOKIE_NAME)

    rotated = await token_client.post("/api/v1/auth/refresh")
    assert rotated.status_code == 200

    reuse = await token_client.post(
        "/api/v1/auth/refresh", headers={"Cookie": f"{COOKIE_NAME}={original}"}
    )
    assert reuse.status_code == 401


@pytest.mark.asyncio
async def test_invalid_refresh_token_is_rejected(token_client, seed_token_user):
    """Sin cookie (o con una inexistente) el refresco devuelve 401."""
    response = await token_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}=no-existe"},
    )
    assert response.status_code == 401


# ── IAH-004: revocacion y ventana residual ───────────────────────────────────


@pytest.mark.asyncio
async def test_logout_revokes_refresh(token_client, seed_token_user):
    """El logout revoca el refresh: ya no puede refrescar la sesion."""
    await _login(token_client)
    previous = token_client.cookies.get(COOKIE_NAME)

    logout = await token_client.post("/api/v1/auth/logout")
    assert logout.status_code == 200

    refresh = await token_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}={previous}"},
    )
    assert refresh.status_code == 401


@pytest.mark.asyncio
async def test_residual_window_access_survives_logout(
    token_client, seed_token_user, seed_catalogs
):
    """La ventana residual: el access ya emitido sigue valido tras el logout."""
    body = await _login(token_client)
    logout = await token_client.post("/api/v1/auth/logout")
    assert logout.status_code == 200

    response = await token_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_token_version_invalidates_previous_access(
    token_client, seed_token_user, engine
):
    """La revocacion administrativa invalida de inmediato los access previos."""
    body = await _login(token_client)
    previous = token_client.cookies.get(COOKIE_NAME)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = await session.get(User, seed_token_user["user"].id)
        await revoke_all_sessions(session, user=user)
        await session.commit()
        assert user.token_version == 1

    old = await token_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert old.status_code == 401

    # El refresh tambien quedo revocado por la revocacion masiva.
    refresh = await token_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}={previous}"},
    )
    assert refresh.status_code == 401


@pytest.mark.asyncio
async def test_new_access_after_admin_revocation_is_accepted(
    token_client, seed_token_user, seed_catalogs, engine
):
    """Triangulacion: tras la revocacion, un login nuevo (nueva version) es valido."""
    await _login(token_client)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = await session.get(User, seed_token_user["user"].id)
        await revoke_all_sessions(session, user=user)
        await session.commit()

    fresh = await _login(token_client)
    response = await token_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {fresh['access_token']}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_malformed_token_version_is_rejected(token_client, seed_token_user):
    """Triangulacion: un claim `ver` no numerico se rechaza con 401 (no 500)."""
    from app.config.settings import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": seed_token_user["username"], "ver": "not-an-int"},
        secret=settings.jwt_secret_key,  # gitleaks:allow (referencia a settings, no un valor)
        algorithm=settings.jwt_algorithm,
    )
    response = await token_client.get(
        "/api/v1/incidentes/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token_is_persisted_hashed(token_client, seed_token_user, engine):
    """El valor en claro del refresh nunca se persiste; solo su hash SHA-256."""
    from sqlalchemy import select

    from app.models.refresh_token import RefreshToken

    await _login(token_client)
    cookie_value = token_client.cookies.get(COOKIE_NAME)
    assert cookie_value

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        stored = (await session.scalars(select(RefreshToken))).all()

    assert len(stored) == 1
    assert stored[0].token_hash != cookie_value
    assert len(stored[0].token_hash) == 64
    assert stored[0].expires_at is not None
