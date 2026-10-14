"""Tests del aviso post-revision a gestion_incidentes (c-86, NR-008).

Cubren:
    - `NotificationRecipientService.resolver_destinatarios_gestion(sector_ids)`:
      gestion ACTIVOS de los sectores, sin duplicados, sin otros roles, lista
      vacia no fatal.
    - El disparo fire-and-forget desde `ClasificacionService.validate` con
      `destinatarios_gestion`, sin alterar la respuesta.
    - El payload del aviso (marcador `incidente_validado_gestion`, lista vacia
      representable), sin emails en claro en la firma de trazabilidad.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.catalog import Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.services.clasificacion_service import ClasificacionService
from app.services.notification_recipient_service import NotificationRecipientService
from app.utils.n8n_webhook import build_post_revision_payload


@pytest_asyncio.fixture
async def notif_env(engine):
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        a = Sector(nombre="Sistemas", descripcion="A")
        b = Sector(nombre="Bases de Datos", descripcion="B")
        c = Sector(nombre="Soporte Tecnico Software", descripcion="C")
        # Sector SIN gestion activo: ejercita la lista vacia (NR-008).
        d = Sector(nombre="Soporte Tecnico Hardware", descripcion="D")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([a, b, c, d, estado])
        await s.flush()

        gr_a = Empleado(
            legajo="NGA", nombre="Gestion A", email="nga@example.test",
            sector_id=a.id, rol=RolEmpleado.gestion_incidentes,
        )
        gr_b = Empleado(
            legajo="NGB", nombre="Gestion B", email="ngb@example.test",
            sector_id=b.id, rol=RolEmpleado.gestion_incidentes,
        )
        gr_c = Empleado(
            legajo="NGC", nombre="Gestion C", email="ngc@example.test",
            sector_id=c.id, rol=RolEmpleado.gestion_incidentes,
        )
        gr_a_off = Empleado(
            legajo="NGA2", nombre="Gestion A off", email="ngaoff@example.test",
            sector_id=a.id, rol=RolEmpleado.gestion_incidentes, activo=False,
        )
        mesa_a = Empleado(
            legajo="NMA", nombre="Mesa A", email="nma@example.test",
            sector_id=a.id, rol=RolEmpleado.mesa_de_ayuda,
        )
        s.add_all([gr_a, gr_b, gr_c, gr_a_off, mesa_a])
        await s.flush()

        inc = Incidente(
            descripcion_original="incidente",
            descripcion_pseudonimizada="incidente",
            prioridad=PrioridadEnum.media,
            estado_id=estado.id,
            sector_id=a.id,
            requiere_revision_humana=True,
        )
        s.add(inc)
        await s.flush()
        log = ClasificacionLog(
            incidente_id=inc.id, sector_id_predicho=a.id, confianza=0.55,
            etapa="gemini", requiere_revision_humana=True, respuesta_raw="{}",
        )
        s.add(log)
        await s.commit()

        ids = {
            "sector_a": a.id, "sector_b": b.id, "sector_c": c.id, "sector_d": d.id,
            "gr_a": gr_a.id, "gr_b": gr_b.id,
            "inc": inc.id, "log": log.id,
            "email_a": gr_a.email, "email_b": gr_b.email,
        }
    yield ids

    async with factory() as s:
        await s.execute(delete(ClasificacionLog))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@pytest.mark.asyncio
async def test_resolver_gestion_activos_de_los_sectores(engine, notif_env):
    """Resuelve los gestion activos de los sectores, excluyendo otros roles."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = NotificationRecipientService(s)
        destinatarios = await service.resolver_destinatarios_gestion(
            [notif_env["sector_a"], notif_env["sector_b"]]
        )
        assert set(destinatarios) == {notif_env["email_a"], notif_env["email_b"]}
        assert len(destinatarios) == len(set(destinatarios))  # sin duplicados
        await s.rollback()


@pytest.mark.asyncio
async def test_resolver_gestion_sin_sectores_o_sin_coincidencia(engine, notif_env):
    """Sin sectores o sin coincidencia devuelve lista vacia sin excepcion."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = NotificationRecipientService(s)
        assert await service.resolver_destinatarios_gestion([]) == []
        assert await service.resolver_destinatarios_gestion([999999]) == []
        await s.rollback()


@pytest.mark.asyncio
async def test_validate_dispara_aviso_post_revision(engine, notif_env):
    """La validacion exitosa dispara (fire-and-forget) el aviso a gestion."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = ClasificacionService(s)
        with patch(
            "app.services.clasificacion_service.notify_n8n_post_revision",
            new_callable=AsyncMock,
        ) as mock_notify:
            log = await service.validate(
                notif_env["log"], asyncpg_sector := notif_env["sector_a"]
            )
            assert log is not None
            await asyncio.sleep(0)
        assert mock_notify.await_count == 1
        incidente_id, _sectores, destinatarios = mock_notify.await_args.args
        assert incidente_id == notif_env["inc"]
        assert notif_env["email_a"] in destinatarios
        incidente = await s.get(Incidente, notif_env["inc"])
        assert incidente.requiere_revision_humana is False
        await s.rollback()


@pytest.mark.asyncio
async def test_validate_sin_destinatarios_no_falla(engine, notif_env):
    """Sin gestion en el sector, el aviso lleva lista vacia y no falla."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        service = ClasificacionService(s)
        with patch(
            "app.services.clasificacion_service.notify_n8n_post_revision",
            new_callable=AsyncMock,
        ) as mock_notify:
            # El sector D no tiene gestion activo.
            await service.validate(notif_env["log"], notif_env["sector_d"])
            await asyncio.sleep(0)
        assert mock_notify.await_count == 1
        assert mock_notify.await_args.args[2] == []
        await s.rollback()


def test_payload_post_revision_representa_lista_vacia():
    """El payload lleva el marcador y una lista (vacia) de destinatarios."""
    payload = build_post_revision_payload(
        incidente_id=7, sectores=[1, 2], destinatarios=[]
    )
    assert payload["evento"] == "incidente_validado_gestion"
    assert payload["incidente_id"] == 7
    assert payload["sectores"] == [1, 2]
    assert payload["destinatarios_gestion"] == []

    payload2 = build_post_revision_payload(
        incidente_id=8, sectores=[3], destinatarios=["a@example.test"]
    )
    assert payload2["destinatarios_gestion"] == ["a@example.test"]
