"""IAH-007: login en dos pasos aditivo para cuentas privilegiadas (c-63b).

Cubren el reto MFA sin token, la verificacion que emite el token con los campos
actuales, el rechazo de tickets invalidos/expirados, el rechazo de un ticket en
rutas protegidas, el flujo de un paso para cuentas no privilegiadas, la
compatibilidad dev con la bandera apagada y el enrollment por endpoint.
"""

from datetime import datetime, timedelta, timezone

import pyotp
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from jose import jwt as jose_jwt
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.core.security import get_password_hash
from app.main import create_app
from app.models.user import User
from app.services import mfa_service

COMPLIANT_PASSWORD = "correct horse battery staple"
DEV_PASSWORD = "admin123"


# ── Fixtures ─────────────────────────────────────────────────────────────────


async def _seed(engine, username: str, password: str, *, is_privileged: bool) -> int:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = User(
            username=username,
            hashed_password=get_password_hash(
                password, username=username, enforce_policy=False
            ),
            is_active=True,
            is_privileged=is_privileged,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user.id


async def _enable_mfa(engine, user_id: int) -> str:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = await session.get(User, user_id)
        enrollment = await mfa_service.start_enrollment(
            session, user, get_settings(), recovery_code_count=3
        )
        await session.commit()
        return enrollment.secret


@pytest_asyncio.fixture
async def privileged_user(engine):
    username = "privuser"
    user_id = await _seed(engine, username, COMPLIANT_PASSWORD, is_privileged=True)
    yield {"username": username, "password": COMPLIANT_PASSWORD, "id": user_id}
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def regular_user(engine):
    username = "regularuser"
    user_id = await _seed(engine, username, COMPLIANT_PASSWORD, is_privileged=False)
    yield {"username": username, "password": COMPLIANT_PASSWORD, "id": user_id}
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def dev_admin(engine):
    username = "admin"
    user_id = await _seed(engine, username, DEV_PASSWORD, is_privileged=True)
    yield {"username": username, "password": DEV_PASSWORD, "id": user_id}
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        await session.execute(delete(User))
        await session.commit()


@pytest_asyncio.fixture
async def auth_client(engine):
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


@pytest.fixture
def mfa_flag_on(monkeypatch):
    monkeypatch.setenv("MFA_REQUIRED_FOR_PRIVILEGED", "true")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


async def _login(client, username: str, password: str) -> dict:
    response = await client.post(
        "/api/v1/auth/login", json={"username": username, "password": password}
    )
    assert response.status_code == 200, response.text
    return response.json()


# ── Reto MFA ─────────────────────────────────────────────────────────────────


async def test_challenge_and_verify_flow(
    auth_client, engine, privileged_user, mfa_flag_on
):
    """Escenario: la cuenta privilegiada recibe el reto sin token; verify emite token."""
    secret = await _enable_mfa(engine, privileged_user["id"])

    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )
    assert body["mfa_required"] is True
    assert body["mfa_ticket"]
    assert body.get("access_token") is None
    # El reto NO debe mostrar `token_type` (no hay token que tipar).
    assert "token_type" not in body

    code = pyotp.TOTP(secret).now()
    response = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": body["mfa_ticket"], "code": code},
    )
    assert response.status_code == 200, response.text
    verified = response.json()
    assert verified["access_token"]
    assert verified["token_type"] == "bearer"
    assert verified["refresh_token"]
    assert verified["expires_in"] == 15 * 60


async def test_verify_rejects_invalid_code(
    auth_client, engine, privileged_user, mfa_flag_on
):
    """Escenario: un segundo factor invalido no emite token."""
    await _enable_mfa(engine, privileged_user["id"])
    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )

    response = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": body["mfa_ticket"], "code": "000000"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_MFA_CODE"


async def test_recovery_code_completes_login(
    auth_client, engine, privileged_user, mfa_flag_on
):
    """Triangulacion: un codigo de recuperacion completa el login y se consume."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        user = await session.get(User, privileged_user["id"])
        enrollment = await mfa_service.start_enrollment(
            session, user, get_settings(), recovery_code_count=3
        )
        await session.commit()
        recovery_code = enrollment.recovery_codes[0]

    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )
    response = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": body["mfa_ticket"], "recovery_code": recovery_code},
    )
    assert response.status_code == 200, response.text
    assert response.json()["access_token"]

    # El codigo quedo consumido: un segundo intento falla.
    second = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": body["mfa_ticket"], "recovery_code": recovery_code},
    )
    assert second.status_code == 401


# ── Tickets invalidos / expirados / scope ────────────────────────────────────


async def test_invalid_ticket_is_rejected(auth_client, privileged_user, mfa_flag_on):
    """Escenario: un ticket invalido es rechazado."""
    response = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": "not.a.ticket", "code": "123456"},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "INVALID_MFA_TICKET"


async def test_expired_ticket_is_rejected(
    auth_client, engine, privileged_user, mfa_flag_on
):
    """Escenario: un ticket fuera de vigencia es rechazado."""
    await _enable_mfa(engine, privileged_user["id"])
    settings = get_settings()
    expired = jose_jwt.encode(
        {
            "sub": privileged_user["username"],
            "scope": "mfa",
            "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
        },
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )

    response = await auth_client.post(
        "/api/v1/auth/mfa/verify",
        json={"mfa_ticket": expired, "code": "123456"},
    )
    assert response.status_code == 401


async def test_mfa_ticket_is_rejected_on_protected_route(
    auth_client, engine, privileged_user, mfa_flag_on, seed_catalogs
):
    """Triangulacion: el ticket de scope `mfa` no sirve como access token."""
    await _enable_mfa(engine, privileged_user["id"])
    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )

    response = await auth_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {body['mfa_ticket']}"},
    )
    assert response.status_code == 401


async def test_mfa_ticket_has_no_kid_header(
    auth_client, engine, privileged_user, mfa_flag_on
):
    """Desacople de c-63c: el ticket MFA se firma con el secreto activo, sin `kid`.

    `create_mfa_ticket` NO debe usar el keyring de c-63c: el ticket no lleva el
    header `kid` (se firma/verifica directo con `settings.jwt_secret_key`).
    """
    await _enable_mfa(engine, privileged_user["id"])
    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )

    header = jose_jwt.get_unverified_header(body["mfa_ticket"])
    assert "kid" not in header


# ── Flujo de un paso y compatibilidad ────────────────────────────────────────


async def test_non_privileged_uses_single_step(auth_client, regular_user, mfa_flag_on):
    """Escenario: la cuenta no privilegiada usa el flujo de un paso."""
    body = await _login(
        auth_client, regular_user["username"], regular_user["password"]
    )
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body.get("mfa_required") is not True
    assert not body.get("mfa_ticket")


async def test_privileged_flag_on_without_enrollment_single_step(
    auth_client, privileged_user, mfa_flag_on
):
    """Cuenta privilegiada SIN MFA activo + bandera ON: un paso hasta el enrollment.

    El reto solo aplica a cuentas con `totp_enabled=True` (design D-B7); una
    cuenta privilegiada que aun no enrolo entra en un solo paso.
    """
    body = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body.get("mfa_required") is not True
    assert not body.get("mfa_ticket")


async def test_flag_off_keeps_dev_admin_single_step(
    auth_client, engine, dev_admin, seed_catalogs
):
    """Escenario: con la bandera apagada admin/admin123 entra en un solo paso."""
    await _enable_mfa(engine, dev_admin["id"])

    body = await _login(auth_client, dev_admin["username"], dev_admin["password"])
    assert body["access_token"]
    assert body["token_type"] == "bearer"
    assert body.get("mfa_required") is not True

    response = await auth_client.get(
        "/api/v1/incidentes/",
        headers={"Authorization": f"Bearer {body['access_token']}"},
    )
    assert response.status_code == 200


# ── Enrollment por endpoint ──────────────────────────────────────────────────


async def test_enroll_endpoint_returns_otpauth(auth_client, privileged_user):
    """El enrollment autenticado devuelve URI otpauth, secreto y codigos."""
    login = await _login(
        auth_client, privileged_user["username"], privileged_user["password"]
    )
    response = await auth_client.post(
        "/api/v1/auth/mfa/enroll",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["otpauth_uri"].startswith("otpauth://totp/")
    assert body["secret"]
    assert len(body["recovery_codes"]) == get_settings().mfa_recovery_code_count


async def test_enroll_requires_authentication(auth_client, privileged_user):
    """Sin token, el enrollment responde 401."""
    response = await auth_client.post("/api/v1/auth/mfa/enroll")
    assert response.status_code == 401


async def test_enroll_forbidden_for_non_privileged(auth_client, regular_user):
    """El enrollment se restringe a cuentas privilegiadas (403 si no lo es)."""
    login = await _login(
        auth_client, regular_user["username"], regular_user["password"]
    )
    response = await auth_client.post(
        "/api/v1/auth/mfa/enroll",
        headers={"Authorization": f"Bearer {login['access_token']}"},
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
