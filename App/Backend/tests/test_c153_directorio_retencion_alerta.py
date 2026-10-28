"""
Tests de la alerta operativa de acumulacion del directorio (c-153, Tema E / DIR-015).

La alerta reporta el CONTEO de filas desactivadas que superaron `fecha_baja + 1
año` y aun no fueron purgadas, para que un `administrador_directorio` dispare la
purga MANUAL. No introduce cron/scheduler/worker (eso lo cubre
`test_directorio_purga_no_automatica.py`) y NUNCA expone datos personales ni el
detalle de las filas: solo el conteo.
"""

from datetime import datetime, timedelta, timezone

import pytest
from structlog.testing import capture_logs

from app.models.catalog import Sector
from app.repositories.empleado_repository import EmpleadoRepository
from app.services.directorio_service import DirectorioService
from scripts.alertar_directorio import alertar_directorio

_AHORA = datetime(2026, 9, 23, 12, 0, tzinfo=timezone.utc)
_EVENTO_ALERTA = "directorio_retencion_alerta"


async def _seed_sector(session, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


async def _empleado_vencido(session, sector_id: int, legajo: str, email: str, *, dias: int = 400):
    """Crea una baja vencida (fecha_baja + 1 año ya superado)."""
    svc = DirectorioService(session)
    empleado = await svc.crear_empleado(
        legajo=legajo,
        nombre="Sintetico Vencido",
        email=email,
        telefono="+5491100000099",
        sector_id=sector_id,
        rol="usuario_final",
    )
    await svc.desactivar_empleado(empleado.id)
    empleado.fecha_baja = _AHORA - timedelta(days=dias)
    session.add(empleado)
    await session.flush()
    return empleado


@pytest.mark.asyncio
async def test_alerta_cuenta_vencidos_y_no_expone_pii(db_session):
    """Con filas vencidas emite la alerta con el conteo y sin datos personales."""
    sector = await _seed_sector(db_session)
    email = "alerta.pii@example.test"
    await _empleado_vencido(db_session, sector.id, "ALR-VIE", email)
    svc = DirectorioService(db_session)

    with capture_logs() as logs:
        conteo = await svc.alertar_acumulacion_vencidos(ahora=_AHORA)

    assert conteo == 1
    eventos = [e for e in logs if e.get("event") == _EVENTO_ALERTA]
    assert eventos, "La acumulacion vencida debe emitir una alerta operativa"
    alerta = eventos[-1]
    assert alerta.get("vencidos_sin_purgar") == 1
    # La alerta es un conteo agregado: sus campos son SOLO metadatos y el conteo.
    assert set(alerta) <= {"event", "log_level", "operacion", "vencidos_sin_purgar"}
    serializado = repr(logs)
    assert email not in serializado
    assert "+5491100000099" not in serializado
    assert "Sintetico Vencido" not in serializado


@pytest.mark.asyncio
async def test_alerta_sin_vencidos_no_emite_evento(db_session):
    """Sin filas vencidas el conteo es cero y no se emite alerta."""
    sector = await _seed_sector(db_session)
    svc = DirectorioService(db_session)
    reciente = await svc.crear_empleado(
        legajo="ALR-REC", nombre="N", email="alr.rec@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    await svc.desactivar_empleado(reciente.id)
    reciente.fecha_baja = _AHORA - timedelta(days=10)
    db_session.add(reciente)
    await db_session.flush()

    with capture_logs() as logs:
        conteo = await svc.alertar_acumulacion_vencidos(ahora=_AHORA)

    assert conteo == 0
    assert [e for e in logs if e.get("event") == _EVENTO_ALERTA] == []


@pytest.mark.asyncio
async def test_alerta_ignora_activos_y_bajas_recientes(db_session):
    """Solo cuentan las bajas vencidas; activos y bajas recientes no suman."""
    sector = await _seed_sector(db_session)
    svc = DirectorioService(db_session)
    activo = await svc.crear_empleado(
        legajo="ALR-ACT", nombre="N", email="alr.act@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    reciente = await svc.crear_empleado(
        legajo="ALR-REC2", nombre="N", email="alr.rec2@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    await svc.desactivar_empleado(reciente.id)
    reciente.fecha_baja = _AHORA - timedelta(days=30)
    db_session.add(reciente)
    await db_session.flush()

    await _empleado_vencido(db_session, sector.id, "ALR-V1", "alr.v1@example.test")
    await _empleado_vencido(db_session, sector.id, "ALR-V2", "alr.v2@example.test")

    with capture_logs() as logs:
        conteo = await svc.alertar_acumulacion_vencidos(ahora=_AHORA)

    assert conteo == 2
    alerta = [e for e in logs if e.get("event") == _EVENTO_ALERTA][-1]
    assert alerta.get("vencidos_sin_purgar") == 2
    assert (await svc.obtener(activo.id)).activo is True


@pytest.mark.asyncio
async def test_script_alertar_reporta_sin_modificar_datos(db_session):
    """El script CLI reporta el conteo y NO modifica las filas (solo lectura)."""
    sector = await _seed_sector(db_session)
    viejo = await _empleado_vencido(db_session, sector.id, "ALR-S1", "alr.s1@example.test")

    conteo = await alertar_directorio(db_session, ahora=_AHORA)

    assert conteo == 1
    # Sigue presente: la alerta no purga ni edita.
    assert await EmpleadoRepository(db_session).get_or_none(viejo.id) is not None
