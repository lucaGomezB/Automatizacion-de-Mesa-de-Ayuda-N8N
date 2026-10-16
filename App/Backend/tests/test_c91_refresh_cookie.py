"""IAH-014 (c-91): transporte del refresh en cookie HttpOnly y CSRF.

Cubren: la cookie seteada por login (atributos HttpOnly/Secure/SameSite) y la
ausencia del refresh en el cuerpo; `/refresh` leyendo SOLO la cookie y rotando la
cookie; `/logout` revocando y limpiando la cookie (Max-Age=0); la deteccion de
reuso en el camino por cookie; la mitigacion CSRF por verificacion de `Origin`;
y la regresion de N8N (solo consume `access_token`).

El cliente usa base `https://test` para que el jar de httpx acepte y reenvie la
cookie `Secure`.
"""

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import get_password_hash
from app.main import create_app
from app.models.user import User

PASSWORD = "correct horse battery staple"
COOKIE_NAME = "refresh_token"
TRUSTED_ORIGIN = "http://localhost:3000"


@pytest_asyncio.fixture
async def seed_cookie_user(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = User(
            username="cookieuser",
            hashed_password=get_password_hash(PASSWORD, username="cookieuser"),
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
    yield {"username": "cookieuser", "password": PASSWORD, "user": user}
    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def cookie_client(engine):
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


async def _login(client, username="cookieuser", password=PASSWORD):
    resp = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return resp


def _set_cookie_header(resp) -> str:
    return "; ".join(resp.headers.get_list("set-cookie")).lower()


# ── 4.1/4.2: login setea cookie y esconde el refresh del cuerpo ──────────────


@pytest.mark.asyncio
async def test_login_sets_refresh_cookie_and_hides_token(cookie_client, seed_cookie_user):
    resp = await _login(cookie_client)
    body = resp.json()

    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert "refresh_token" not in body
    assert body["expires_in"] == 30 * 60

    header = _set_cookie_header(resp)
    assert f"{COOKIE_NAME}=" in header
    assert "httponly" in header
    assert "secure" in header
    assert "samesite=strict" in header
    # La cookie quedo almacenada en el jar (no accesible por JS en un navegador).
    assert cookie_client.cookies.get(COOKIE_NAME)


# ── 4.3/4.4: /refresh lee SOLO la cookie y rota la cookie ────────────────────


@pytest.mark.asyncio
async def test_refresh_reads_cookie_and_rotates_cookie(cookie_client, seed_cookie_user):
    await _login(cookie_client)
    first = cookie_client.cookies.get(COOKIE_NAME)
    assert first

    resp = await cookie_client.post("/api/v1/auth/refresh")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["access_token"]
    assert "refresh_token" not in body

    rotated = cookie_client.cookies.get(COOKIE_NAME)
    assert rotated and rotated != first

    header = _set_cookie_header(resp)
    assert "httponly" in header
    assert "samesite=strict" in header


@pytest.mark.asyncio
async def test_refresh_without_cookie_is_rejected(cookie_client, seed_cookie_user):
    resp = await cookie_client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


# ── 4.5/4.6: /logout revoca y limpia la cookie ───────────────────────────────


@pytest.mark.asyncio
async def test_logout_revokes_and_clears_the_cookie(cookie_client, seed_cookie_user):
    await _login(cookie_client)
    previous = cookie_client.cookies.get(COOKIE_NAME)
    assert previous

    resp = await cookie_client.post("/api/v1/auth/logout")
    assert resp.status_code == 200
    assert "max-age=0" in _set_cookie_header(resp)
    # El jar ya no conserva la cookie.
    assert cookie_client.cookies.get(COOKIE_NAME) is None

    # Y el refresh revocado no puede rehidratar, aunque se reenvie el valor viejo.
    reuse = await cookie_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}={previous}"},
    )
    assert reuse.status_code == 401


# ── 4.7/4.8: reuso de un refresh rotado (camino por cookie) ──────────────────


@pytest.mark.asyncio
async def test_rotated_refresh_reuse_via_cookie_is_rejected(cookie_client, seed_cookie_user):
    await _login(cookie_client)
    original_value = cookie_client.cookies.get(COOKIE_NAME)

    first = await cookie_client.post("/api/v1/auth/refresh")
    assert first.status_code == 200

    reuse = await cookie_client.post(
        "/api/v1/auth/refresh",
        headers={"Cookie": f"{COOKIE_NAME}={original_value}"},
    )
    assert reuse.status_code == 401
    assert reuse.json()["error"]["code"] == "INVALID_REFRESH_TOKEN"


# ── 4.9: CSRF por verificacion de Origin ─────────────────────────────────────


@pytest.mark.asyncio
async def test_untrusted_origin_is_rejected_on_refresh_and_logout(
    cookie_client, seed_cookie_user
):
    await _login(cookie_client)

    refresh = await cookie_client.post(
        "/api/v1/auth/refresh", headers={"Origin": "http://evil.example"}
    )
    assert refresh.status_code == 403
    assert refresh.json()["error"]["code"] == "CSRF_ORIGIN_REJECTED"

    logout = await cookie_client.post(
        "/api/v1/auth/logout", headers={"Origin": "http://evil.example"}
    )
    assert logout.status_code == 403
    assert logout.json()["error"]["code"] == "CSRF_ORIGIN_REJECTED"


@pytest.mark.asyncio
async def test_trusted_origin_is_accepted_on_refresh(cookie_client, seed_cookie_user):
    await _login(cookie_client)
    resp = await cookie_client.post(
        "/api/v1/auth/refresh", headers={"Origin": TRUSTED_ORIGIN}
    )
    assert resp.status_code == 200, resp.text


# ── 4.11: regresion N8N — solo consume access_token ──────────────────────────


@pytest.mark.asyncio
async def test_access_token_still_works_as_bearer_only(
    cookie_client, seed_cookie_user, seed_catalogs
):
    body = (await _login(cookie_client)).json()

    response = await cookie_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 200


# ── 4.10: CORS con credenciales y origenes EXACTOS (config estructural) ───────


def test_cors_allows_credentials_with_exact_origins():
    """El stack CORS permite credenciales con origenes exactos (nunca "*")."""
    from starlette.middleware.cors import CORSMiddleware

    app = create_app()
    cors = [m for m in app.user_middleware if m.cls is CORSMiddleware]
    assert cors, "CORSMiddleware debe estar configurado"
    kwargs = cors[0].kwargs
    assert kwargs["allow_credentials"] is True
    assert "*" not in kwargs["allow_origins"]
    assert "http://localhost:3000" in kwargs["allow_origins"]


def test_origin_is_trusted_helper():
    """Sin Origin no hay CSRF de navegador; con Origin debe estar en la lista."""
    from app.config.settings import get_settings
    from app.core.auth_cookies import origin_is_trusted

    settings = get_settings()
    assert origin_is_trusted(None, settings) is True
    assert origin_is_trusted("http://localhost:3000", settings) is True
    assert origin_is_trusted("http://evil.example", settings) is False


@pytest.mark.asyncio
async def test_cors_response_allows_credentials_for_trusted_origin(cookie_client):
    """La respuesta CORS habilita credenciales para el origen exacto confiable."""
    resp = await cookie_client.get(
        "/health", headers={"Origin": TRUSTED_ORIGIN}
    )
    assert resp.headers.get("access-control-allow-origin") == TRUSTED_ORIGIN
    assert resp.headers.get("access-control-allow-credentials") == "true"
