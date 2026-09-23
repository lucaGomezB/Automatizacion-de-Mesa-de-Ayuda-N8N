"""
Tests del servicio de resolucion de contactos (c-54, seccion 5).

Describen el contrato de enganche con c-53 (RES-005): `resolver_por_telefono`,
`resolver_por_email` y `resolver_por_usuario` devuelven un `ResultadoResolucion`
que distingue encontrado / no encontrado / ambiguo, sin lanzar excepcion ante
datos ausentes, sin enviar notificaciones y sin PII en los logs.
"""

from unittest.mock import AsyncMock, patch

import pytest
from structlog.testing import capture_logs

from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User
from app.services.contact_resolution_service import (
    ContactResolutionService,
    EstadoResolucion,
)


async def _seed(session) -> Empleado:
    sector = Sector(nombre="Sistemas", descripcion="d")
    session.add(sector)
    await session.flush()
    empleado = Empleado(
        legajo="R-1",
        nombre="Resoluble",
        email="resoluble@example.test",
        telefono="+5491100001000",
        sector_id=sector.id,
        rol=RolEmpleado.usuario_final,
    )
    session.add(empleado)
    await session.flush()
    return empleado


def _svc(session) -> ContactResolutionService:
    return ContactResolutionService(session)


# ── Telefono ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resolver_por_telefono_encontrado(db_session):
    """Un telefono activo resuelve al empleado."""
    await _seed(db_session)

    resultado = await _svc(db_session).resolver_por_telefono("+5491100001000")

    assert resultado.estado == EstadoResolucion.ENCONTRADO
    assert resultado.encontrado is True
    assert resultado.empleado is not None
    assert resultado.empleado.legajo == "R-1"
    assert resultado.canal == "telefono"


@pytest.mark.asyncio
async def test_resolver_por_telefono_normaliza_antes_de_buscar(db_session):
    """Acepta formato local/separadores y normaliza a E.164."""
    await _seed(db_session)

    resultado = await _svc(db_session).resolver_por_telefono("+54 9 11 0000-1000")

    assert resultado.estado == EstadoResolucion.ENCONTRADO


@pytest.mark.asyncio
async def test_telefono_desconocido_no_es_fatal(db_session):
    """Un telefono ausente devuelve no encontrado sin excepcion."""
    resultado = await _svc(db_session).resolver_por_telefono("+5491199999999")

    assert resultado.estado == EstadoResolucion.NO_ENCONTRADO
    assert resultado.empleado is None


@pytest.mark.asyncio
async def test_telefono_malformado_no_es_fatal(db_session):
    """Un telefono malformado no propaga error de normalizacion."""
    resultado = await _svc(db_session).resolver_por_telefono("abc")

    assert resultado.estado == EstadoResolucion.NO_ENCONTRADO


@pytest.mark.asyncio
async def test_telefono_ambiguo_no_concluyente(db_session):
    """Un telefono compartido por varios activos es ambiguo (no elige)."""
    sector = Sector(nombre="Sistemas", descripcion="d")
    db_session.add(sector)
    await db_session.flush()
    for i in range(2):
        db_session.add(
            Empleado(
                legajo=f"AMB-{i}",
                nombre=f"N {i}",
                email=f"amb{i}@example.test",
                telefono="+5491100002000",
                sector_id=sector.id,
                rol=RolEmpleado.usuario_final,
            )
        )
    await db_session.flush()

    resultado = await _svc(db_session).resolver_por_telefono("+5491100002000")

    assert resultado.estado == EstadoResolucion.AMBIGUO
    assert resultado.empleado is None


# ── Email ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resolver_por_email_encontrado_y_normalizado(db_session):
    """Un email con mayusculas resuelve por igualdad tras normalizar."""
    await _seed(db_session)

    resultado = await _svc(db_session).resolver_por_email("  RESOLUBLE@Example.TEST ")

    assert resultado.estado == EstadoResolucion.ENCONTRADO
    assert resultado.empleado.legajo == "R-1"
    assert resultado.canal == "email"


@pytest.mark.asyncio
async def test_email_desconocido_y_malformado_no_son_fatales(db_session):
    """Email ausente o malformado devuelve no encontrado."""
    svc = _svc(db_session)
    assert (await svc.resolver_por_email("nadie@example.test")).estado == (
        EstadoResolucion.NO_ENCONTRADO
    )
    assert (await svc.resolver_por_email("no-es-email")).estado == (
        EstadoResolucion.NO_ENCONTRADO
    )


# ── Usuario autenticado ───────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resolver_por_usuario_vinculado(db_session):
    """Una cuenta vinculada resuelve al empleado."""
    user = User(username="u-res", hashed_password="x", is_active=True)
    db_session.add(user)
    await db_session.flush()
    empleado = await _seed(db_session)
    empleado.user_id = user.id
    await db_session.flush()

    resultado = await _svc(db_session).resolver_por_usuario(user.id)

    assert resultado.estado == EstadoResolucion.ENCONTRADO
    assert resultado.canal == "usuario"


@pytest.mark.asyncio
async def test_usuario_sin_empleado_no_es_fatal(db_session):
    """Una cuenta sin empleado vinculado no impide el flujo web."""
    resultado = await _svc(db_session).resolver_por_usuario(123456)

    assert resultado.estado == EstadoResolucion.NO_ENCONTRADO


@pytest.mark.asyncio
async def test_empleado_inactivo_no_resuelve(db_session):
    """Un empleado inactivo no resuelve por ningun canal."""
    empleado = await _seed(db_session)
    empleado.activo = False
    await db_session.flush()

    svc = _svc(db_session)
    assert (await svc.resolver_por_telefono("+5491100001000")).estado == (
        EstadoResolucion.NO_ENCONTRADO
    )
    assert (await svc.resolver_por_email("resoluble@example.test")).estado == (
        EstadoResolucion.NO_ENCONTRADO
    )


# ── Contrato / trazabilidad / no-notificacion ─────────────────────────────────


@pytest.mark.asyncio
async def test_directorio_vacio_devuelve_no_encontrado_sin_excepcion(db_session):
    """Con directorio vacio, el contrato degrada a no encontrado (RES-005)."""
    resultado = await _svc(db_session).resolver_por_telefono("+5491100009999")

    assert resultado.estado == EstadoResolucion.NO_ENCONTRADO
    assert resultado.empleado is None


@pytest.mark.asyncio
async def test_resolucion_no_envia_notificaciones(db_session):
    """La resolucion no dispara ninguna notificacion (SMS/correo/N8N)."""
    await _seed(db_session)

    with patch(
        "app.utils.n8n_webhook.notify_n8n", new_callable=AsyncMock
    ) as notify:
        await _svc(db_session).resolver_por_telefono("+5491100001000")

    notify.assert_not_called()


@pytest.mark.asyncio
async def test_trazabilidad_sin_pii(db_session):
    """El log estructurado indica canal y resultado, sin contacto en claro."""
    await _seed(db_session)

    with capture_logs() as logs:
        await _svc(db_session).resolver_por_telefono("+5491100001000")

    eventos = [e for e in logs if e.get("event") == "resolucion_contacto"]
    assert eventos, "Debe registrarse la trazabilidad de la resolucion"
    assert eventos[-1].get("canal") == "telefono"
    assert eventos[-1].get("resultado") == "encontrado"

    serializado = repr(logs)
    assert "+5491100001000" not in serializado
    assert "resoluble@example.test" not in serializado
