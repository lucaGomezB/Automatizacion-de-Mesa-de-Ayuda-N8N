"""
Tests de integracion para autenticacion JWT.

Responsabilidad:
    Verifica el flujo completo de autenticacion: login exitoso, credenciales
    invalidas, proteccion de rutas, y acceso publico a health endpoints.

    Utiliza un fixture auth_client SIN el bypass de autenticacion que tiene
    el fixture client del conftest. Esto permite probar el comportamiento
    real del middleware JWT.

Estrategia de aislamiento:
    seed_user usa el engine directamente (como seed_catalogs) para que el
    cliente ASGI (que abre su propia sesion) pueda consultar el usuario.
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt as jose_jwt
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.database import get_db_session
from app.core.security import create_access_token, get_password_hash
from app.main import create_app
from app.models.user import User


@pytest_asyncio.fixture
async def seed_user(engine):
    """
    Crea un usuario admin en la base de datos de test.

    Usa el engine directamente con commit explicito (como seed_catalogs),
    porque el cliente ASGI abre su propia sesion por request.

    Yields:
        dict con username, password_plain y el objeto User.
    """
    password_plain = "admin123"
    hashed = get_password_hash(password_plain)

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = User(
            username="admin",
            hashed_password=hashed,
            is_active=True,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    yield {
        "username": "admin",
        "password": password_plain,
        "user": user,
    }

    # Teardown: eliminar el usuario creado
    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def auth_client(engine):
    """
    Cliente HTTP asincrono SIN bypass de autenticacion.

    A diferencia del fixture 'client' del conftest (que tiene un override
    de get_current_user para que los tests heredados sigan funcionando),
    este fixture no tiene ese override. Las rutas protegidas requieren
    un token JWT valido.

    Usa follow_redirects=True para seguir los redirects de trailing slash
    que FastAPI emite (ej. /incidentes → /incidentes/).
    """
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
        base_url="http://test",
        follow_redirects=True,
    ) as ac:
        yield ac


# ── Tests: POST /api/v1/auth/login ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_success_returns_token(auth_client: AsyncClient, seed_user):
    """
    Login con credenciales validas debe retornar 200 con access_token y token_type.
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": seed_user["username"], "password": seed_user["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 0


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(auth_client: AsyncClient, seed_user):
    """
    Login con password incorrecta debe retornar 401.
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": seed_user["username"], "password": "wrongpassword"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "error" in body
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_nonexistent_user_returns_401(auth_client: AsyncClient, seed_user):
    """
    Login con usuario inexistente debe retornar 401.
    No debe revelar si el usuario existe o no (mismo codigo de error).
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent", "password": "admin123"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_missing_fields_returns_422(auth_client: AsyncClient):
    """
    Login sin username ni password debe retornar 422 (validacion de Pydantic).
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={},
    )
    assert response.status_code == 422


# ── Tests: Rutas protegidas (sin bypass de auth) ──────────────────────────────

@pytest.mark.asyncio
async def test_incidentes_without_token_returns_401(
    auth_client: AsyncClient, seed_catalogs
):
    """
    GET /api/v1/incidentes sin token debe retornar 401.
    """
    response = await auth_client.get("/api/v1/incidentes")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_incidentes_with_valid_token_returns_200(
    auth_client: AsyncClient, seed_user, seed_catalogs
):
    """
    GET /api/v1/incidentes con token valido debe retornar 200.
    """
    from app.config.settings import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": seed_user["username"]},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=settings.jwt_expire_minutes,
    )
    response = await auth_client.get(
        "/api/v1/incidentes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_incidentes_with_invalid_token_returns_401(
    auth_client: AsyncClient, seed_catalogs
):
    """
    GET /api/v1/incidentes con token invalido (malformado) debe retornar 401.
    """
    response = await auth_client.get(
        "/api/v1/incidentes",
        headers={"Authorization": "Bearer invalid.token.here"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_incidentes_with_expired_token_returns_401(
    auth_client: AsyncClient, seed_user, seed_catalogs
):
    """
    GET /api/v1/incidentes con token expirado debe retornar 401.
    """
    from app.config.settings import get_settings

    settings = get_settings()
    # Crear token con expiracion negativa (ya expiro)
    token = create_access_token(
        data={"sub": seed_user["username"]},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=-1,
    )
    response = await auth_client.get(
        "/api/v1/incidentes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


# ── C-30 BE 6.4: el JWT debe exigir el claim `exp` ─────────────────────────────

@pytest.mark.asyncio
async def test_incidentes_with_token_without_exp_returns_401(
    auth_client: AsyncClient, seed_user, seed_catalogs
):
    """
    Un token correctamente firmado pero SIN claim `exp` debe rechazarse con 401.

    Antes del fix el backend lo aceptaba (200): create_access_token omitia `exp`
    y get_current_user decodificaba sin exigirlo. El rechazo usa el envelope de
    error estandar (UNAUTHORIZED) y no expone `detail` en la raiz.
    """
    from app.config.settings import get_settings

    settings = get_settings()
    token = jose_jwt.encode(
        {"sub": seed_user["username"]},
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    response = await auth_client.get(
        "/api/v1/incidentes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401
    body = response.json()
    assert "detail" not in body
    assert body["error"]["code"] == "UNAUTHORIZED"


def test_create_access_token_defaults_to_configured_expiry():
    """
    create_access_token sin `expires_delta` debe emitir un token con claim `exp`
    derivado de settings.jwt_expire_minutes (no puede emitir tokens sin expiracion).
    """
    from app.config.settings import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": "admin"},
        secret=settings.jwt_secret_key,  # gitleaks:allow
        algorithm=settings.jwt_algorithm,
    )
    payload = jose_jwt.decode(
        token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
    )
    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected = datetime.now(timezone.utc) + timedelta(
        minutes=settings.jwt_expire_minutes
    )
    assert abs((exp - expected).total_seconds()) < 60


@pytest.mark.asyncio
async def test_incidentes_with_default_exp_token_returns_200(
    auth_client: AsyncClient, seed_user, seed_catalogs
):
    """
    Regresion: un token emitido con la expiracion configurada por defecto
    (sin `expires_delta` explicito) sigue autenticando con 200.
    """
    from app.config.settings import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": seed_user["username"]},
        secret=settings.jwt_secret_key,  # gitleaks:allow
        algorithm=settings.jwt_algorithm,
    )
    response = await auth_client.get(
        "/api/v1/incidentes",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_clasificaciones_without_token_returns_401(
    auth_client: AsyncClient, seed_catalogs
):
    """
    GET /api/v1/clasificaciones/revision-pendiente sin token debe retornar 401.
    """
    response = await auth_client.get("/api/v1/clasificaciones/revision-pendiente")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_clasificaciones_with_valid_token_returns_200(
    auth_client: AsyncClient, seed_user, seed_catalogs
):
    """
    GET /api/v1/clasificaciones/revision-pendiente con token valido debe retornar 200.
    """
    from app.config.settings import get_settings

    settings = get_settings()
    token = create_access_token(
        data={"sub": seed_user["username"]},
        secret=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        expires_delta=settings.jwt_expire_minutes,
    )
    response = await auth_client.get(
        "/api/v1/clasificaciones/revision-pendiente",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200


# ── Tests: Rutas publicas (health) ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_remains_public(auth_client: AsyncClient):
    """
    GET /health debe seguir siendo accesible sin autenticacion.
    """
    response = await auth_client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


@pytest.mark.asyncio
async def test_health_db_remains_public(auth_client: AsyncClient):
    """
    GET /health/db debe seguir siendo accesible sin autenticacion.
    """
    response = await auth_client.get("/health/db")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


# ── Test: Triangulacion — credenciales parciales ──────────────────────────────

@pytest.mark.asyncio
async def test_login_only_username_returns_422(auth_client: AsyncClient):
    """
    Login con solo username (sin password) debe retornar 422.
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "admin"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_only_password_returns_422(auth_client: AsyncClient):
    """
    Login con solo password (sin username) debe retornar 422.
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"password": "admin123"},
    )
    assert response.status_code == 422


# ── ERR-001: envelope de error uniforme en 422 y 401 (C-30 BE B5) ─────────────

@pytest.mark.asyncio
async def test_validation_error_uses_error_envelope(auth_client: AsyncClient):
    """
    Un error de validacion de request devuelve 422 con el envelope
    `error.code`/`error.message`/`error.details` y sin `detail` en la raiz.
    """
    response = await auth_client.post(
        "/api/v1/auth/login",
        json={"username": "admin"},  # falta password
    )

    assert response.status_code == 422
    body = response.json()
    assert "detail" not in body
    assert "error" in body
    assert body["error"]["code"] == "VALIDATION_ERROR"
    assert body["error"]["message"]
    assert "details" in body["error"]


@pytest.mark.asyncio
async def test_unauthenticated_error_uses_error_envelope(auth_client: AsyncClient):
    """
    Una peticion sin token devuelve 401 con el envelope (sin `detail` en la
    raiz) y preserva el header `WWW-Authenticate: Bearer`.
    """
    response = await auth_client.get("/api/v1/incidentes/")

    assert response.status_code == 401
    body = response.json()
    assert "detail" not in body
    assert "error" in body
    assert body["error"]["code"] == "UNAUTHORIZED"
    assert body["error"]["message"]
    assert response.headers.get("www-authenticate") == "Bearer"
