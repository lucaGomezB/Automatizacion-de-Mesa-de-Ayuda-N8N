"""
Tests del servicio de directorio (c-54, seccion 4).

Cubren validaciones de alta/edicion (campos obligatorios, unicidad de email,
telefono repetible, rol valido, E.164, sector obligatorio por rol), el ciclo de
vida (desactivacion, reactivacion, borrado ARCO) y la AUDITORIA sin PII
(DIR-006): los logs estructurados nunca contienen email ni telefono en claro.
"""

import pytest
from structlog.testing import capture_logs

from app.core.exceptions import (
    DirectorioValidationError,
    EntityNotFoundError,
    SectorNotFoundError,
)
from app.models.catalog import Sector
from app.models.empleado import Empleado, RolEmpleado
from app.services.directorio_service import DirectorioService


async def _seed_sector(session, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


def _svc(session, actor_id: int | None = 99) -> DirectorioService:
    return DirectorioService(session, actor_id=actor_id)


# ── Alta ───────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_alta_valida_con_y_sin_telefono(db_session):
    """El alta acepta legajo/nombre/email y el telefono es opcional."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)

    con_tel = await svc.crear_empleado(
        legajo="A-1",
        nombre="Ana Sintetica",
        email="  Ana@Example.TEST ",
        telefono="+54 9 11 1111-1111",
        sector_id=sector.id,
        rol="usuario_final",
    )
    sin_tel = await svc.crear_empleado(
        legajo="A-2",
        nombre="Beto Sintetico",
        email="beto@example.test",
        sector_id=sector.id,
        rol=RolEmpleado.operador,
    )

    assert con_tel.email == "ana@example.test"  # normalizado
    assert con_tel.telefono == "+5491111111111"  # E.164
    assert con_tel.rol == RolEmpleado.usuario_final
    assert con_tel.activo is True
    assert sin_tel.telefono is None


@pytest.mark.asyncio
async def test_email_debe_ser_unico(db_session):
    """Un email ya asignado es rechazado."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)
    await svc.crear_empleado(
        legajo="B-1", nombre="Uno", email="dup@example.test",
        sector_id=sector.id, rol="usuario_final",
    )

    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(
            legajo="B-2", nombre="Dos", email="DUP@example.test",
            sector_id=sector.id, rol="usuario_final",
        )


@pytest.mark.asyncio
async def test_telefono_repetido_permitido(db_session):
    """Dos empleados pueden compartir telefono (mesa de area / casilla comun)."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)

    await svc.crear_empleado(
        legajo="C-1", nombre="Uno", email="c1@example.test",
        telefono="+5491100000010", sector_id=sector.id, rol="usuario_final",
    )
    await svc.crear_empleado(
        legajo="C-2", nombre="Dos", email="c2@example.test",
        telefono="+5491100000010", sector_id=sector.id, rol="operador",
    )

    registro = await svc.listar()
    assert len([e for e in registro if e.telefono == "+5491100000010"]) == 2


@pytest.mark.asyncio
async def test_campos_obligatorios(db_session):
    """legajo, nombre y email son obligatorios."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)
    base = dict(nombre="N", email="n@example.test", sector_id=sector.id, rol="usuario_final")

    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(legajo="", **base)
    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(legajo="Z-1", nombre="  ", email="n2@example.test",
                                 sector_id=sector.id, rol="usuario_final")
    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(legajo="Z-2", nombre="N", email="malformado",
                                 sector_id=sector.id, rol="usuario_final")


# ── Triangulacion de validaciones ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_rol_invalido_rechazado(db_session):
    """Un rol fuera del vocabulario es rechazado."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)

    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(
            legajo="D-1", nombre="N", email="d1@example.test",
            sector_id=sector.id, rol="supervisor",
        )


@pytest.mark.asyncio
async def test_usuario_final_y_operador_requieren_sector(db_session):
    """Sin sector, usuario_final y operador son rechazados."""
    svc = _svc(db_session)

    for rol in ("usuario_final", "operador"):
        with pytest.raises(DirectorioValidationError):
            await svc.crear_empleado(
                legajo=f"E-{rol}", nombre="N", email=f"{rol}@example.test", rol=rol,
            )


@pytest.mark.asyncio
async def test_administrador_con_sector_rechazado(db_session):
    """El administrador no puede tener sector asignado."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)

    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(
            legajo="F-1", nombre="N", email="f1@example.test",
            sector_id=sector.id, rol="administrador_directorio",
        )


@pytest.mark.asyncio
async def test_sector_inexistente_rechazado(db_session):
    """Un sector_id que no existe en el catalogo es rechazado."""
    svc = _svc(db_session)

    with pytest.raises(SectorNotFoundError):
        await svc.crear_empleado(
            legajo="G-1", nombre="N", email="g1@example.test",
            sector_id=999999, rol="usuario_final",
        )


@pytest.mark.asyncio
async def test_telefono_fuera_de_e164_rechazado(db_session):
    """Un telefono que no normaliza a E.164 es rechazado."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)

    with pytest.raises(DirectorioValidationError):
        await svc.crear_empleado(
            legajo="H-1", nombre="N", email="h1@example.test",
            telefono="123", sector_id=sector.id, rol="usuario_final",
        )


# ── Ciclo de vida ─────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_desactivacion_no_borra_y_reactivacion(db_session):
    """Desactivar marca activo=False; reactivar lo vuelve elegible."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)
    empleado = await svc.crear_empleado(
        legajo="I-1", nombre="N", email="i1@example.test",
        sector_id=sector.id, rol="usuario_final",
    )

    desactivado = await svc.desactivar_empleado(empleado.id)
    assert desactivado.activo is False
    assert (await svc.obtener(empleado.id)).legajo == "I-1"  # sigue existiendo

    reactivado = await svc.reactivar_empleado(empleado.id)
    assert reactivado.activo is True


@pytest.mark.asyncio
async def test_borrado_arco_elimina_fisicamente(db_session):
    """El borrado ARCO elimina la fila fisicamente (no es el camino operativo)."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)
    empleado = await svc.crear_empleado(
        legajo="J-1", nombre="N", email="j1@example.test",
        sector_id=sector.id, rol="usuario_final",
    )

    await svc.borrar_empleado_arco(empleado.id, actor_id=1)

    with pytest.raises(EntityNotFoundError):
        await svc.obtener(empleado.id)


@pytest.mark.asyncio
async def test_obtener_inexistente_lanza_entity_not_found(db_session):
    """Consultar un id inexistente lanza EntityNotFoundError."""
    with pytest.raises(EntityNotFoundError):
        await _svc(db_session).obtener(999999)


@pytest.mark.asyncio
async def test_actualizacion_parcial_y_unicidad(db_session):
    """La edicion cambia solo lo enviado y respeta la unicidad del email."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session)
    a = await svc.crear_empleado(
        legajo="K-1", nombre="A", email="k1@example.test",
        sector_id=sector.id, rol="usuario_final",
    )
    await svc.crear_empleado(
        legajo="K-2", nombre="B", email="k2@example.test",
        sector_id=sector.id, rol="usuario_final",
    )

    actualizado = await svc.actualizar_empleado(a.id, nombre="A Modificado")
    assert actualizado.nombre == "A Modificado"
    assert actualizado.email == "k1@example.test"

    with pytest.raises(DirectorioValidationError):
        await svc.actualizar_empleado(a.id, email="k2@example.test")


# ── Auditoria y no-PII en logs ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_auditoria_registra_actor_operacion_sin_pii(db_session):
    """El alta queda auditada con actor/operacion/resultado y sin contacto en claro."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=42)
    email = "auditoria.pii@example.test"
    telefono = "+5491188887777"

    with capture_logs() as logs:
        await svc.crear_empleado(
            legajo="L-1", nombre="Nombre PII", email=email,
            telefono=telefono, sector_id=sector.id, rol="usuario_final",
        )

    auditorias = [e for e in logs if e.get("event") == "directorio_auditoria"]
    assert auditorias, "Debe existir al menos un evento de auditoria"
    alta = auditorias[-1]
    assert alta.get("operacion") == "alta"
    assert alta.get("resultado") == "ok"
    assert alta.get("actor_id") == 42

    serializado = repr(logs)
    assert email not in serializado, "El email no debe aparecer en los logs"
    assert telefono not in serializado, "El telefono no debe aparecer en los logs"
    assert "Nombre PII" not in serializado, "El nombre no debe aparecer en los logs"


@pytest.mark.asyncio
async def test_auditoria_de_desactivacion_y_borrado_sin_pii(db_session):
    """Desactivacion y borrado ARCO tambien auditan sin PII."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=7)
    email = "ciclo.pii@example.test"
    empleado = await svc.crear_empleado(
        legajo="M-1", nombre="N", email=email,
        sector_id=sector.id, rol="usuario_final",
    )

    with capture_logs() as logs:
        await svc.desactivar_empleado(empleado.id)
        await svc.borrar_empleado_arco(empleado.id)

    operaciones = {
        e.get("operacion") for e in logs if e.get("event") == "directorio_auditoria"
    }
    assert {"desactivacion", "borrado_arco"} <= operaciones
    assert email not in repr(logs)
