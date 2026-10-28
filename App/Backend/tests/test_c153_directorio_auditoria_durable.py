"""
Tests de la auditoria durable del directorio (c-153, Tema D, DIR-013).

Cubren el contrato de la traza DURABLE y append-only de las operaciones del
directorio, analoga a `incidente_evento`:

    - Cada operacion de gestion (alta, edicion, desactivacion, reactivacion y
      borrado ARCO) deja una fila durable con actor, operacion, resultado e
      instante, ADEMAS del evento structlog.
    - La resolucion de contactos (email, telefono y usuario) deja traza durable
      con el canal y el resultado, SIN el valor de contacto en claro.
    - La tabla de auditoria NO contiene email, telefono ni nombre en claro.
    - La traza es append-only: el repositorio no expone update/delete y no
      existe endpoint de edicion ni de borrado.

Estrategia RED (5.1): estos tests fallan mientras no exista el almacen durable
(modelo `DirectorioAuditoria`, repositorio y helper de emision).
"""

import pytest
from sqlalchemy import select, text

from app.models.catalog import Sector
from app.models.directorio_auditoria import DirectorioAuditoria
from app.models.empleado import Empleado, RolEmpleado
from app.services.contact_resolution_service import ContactResolutionService
from app.services.directorio_service import DirectorioService

_TABLA = "directorio_auditoria"


async def _seed_sector(session, nombre: str = "Sistemas") -> Sector:
    sector = Sector(nombre=nombre, descripcion="d")
    session.add(sector)
    await session.flush()
    return sector


async def _seed_empleado(session, sector_id: int) -> Empleado:
    empleado = Empleado(
        legajo="AUD-1",
        nombre="Nombre PII Auditoria",
        email="auditoria.durable@example.test",
        telefono="+5491100012345",
        sector_id=sector_id,
        rol=RolEmpleado.usuario_final,
        activo=True,
    )
    session.add(empleado)
    await session.flush()
    return empleado


def _svc(session, actor_id: int | None = 42) -> DirectorioService:
    return DirectorioService(session, actor_id=actor_id)


async def _registros(session) -> list[DirectorioAuditoria]:
    result = await session.execute(
        select(DirectorioAuditoria).order_by(DirectorioAuditoria.id)
    )
    return list(result.scalars().all())


# ── 5.2 / 5.3: filas durables por operacion ────────────────────────────────────


@pytest.mark.asyncio
async def test_alta_produce_fila_durable_con_actor_operacion_resultado_e_instante(
    db_session,
):
    """(5.3) El alta deja una fila durable completa, ademas del log."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=42)

    empleado = await svc.crear_empleado(
        legajo="DUR-1",
        nombre="Alta Durable",
        email="alta.durable@example.test",
        telefono="+5491100022200",
        sector_id=sector.id,
        rol="usuario_final",
    )

    registros = await _registros(db_session)
    assert len(registros) == 1
    fila = registros[0]
    assert fila.operacion == "alta"
    assert fila.resultado == "ok"
    assert fila.actor_empleado_id == 42
    assert fila.empleado_id == empleado.id
    assert fila.created_at is not None


@pytest.mark.asyncio
async def test_cada_operacion_de_gestion_produce_su_fila_durable(db_session):
    """(5.3) Alta, edicion, desactivacion, reactivacion y borrado auditan."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=77)

    empleado = await svc.crear_empleado(
        legajo="DUR-2",
        nombre="Ciclo Durable",
        email="ciclo.durable@example.test",
        sector_id=sector.id,
        rol="usuario_final",
    )
    await svc.actualizar_empleado(empleado.id, nombre="Ciclo Editado")
    await svc.desactivar_empleado(empleado.id)
    await svc.reactivar_empleado(empleado.id)
    await svc.borrar_empleado_arco(empleado.id)

    registros = await _registros(db_session)
    assert [f.operacion for f in registros] == [
        "alta",
        "edicion",
        "desactivacion",
        "reactivacion",
        "borrado_arco",
    ]
    for fila in registros:
        assert fila.resultado == "ok"
        assert fila.actor_empleado_id == 77
        assert fila.created_at is not None


@pytest.mark.asyncio
async def test_la_auditoria_durable_convive_con_el_registro_estructurado(
    db_session,
):
    """(5.3) La auditoria se enruta al almacen durable ADEMAS de structlog."""
    from structlog.testing import capture_logs

    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=11)

    with capture_logs() as logs:
        await svc.crear_empleado(
            legajo="DUR-3",
            nombre="Doble Canal",
            email="doble.canal@example.test",
            sector_id=sector.id,
            rol="usuario_final",
        )

    eventos = [e for e in logs if e.get("event") == "directorio_auditoria"]
    assert eventos and eventos[-1].get("operacion") == "alta"
    assert len(await _registros(db_session)) == 1


# ── 5.4: canales de resolucion de contacto ────────────────────────────────────


@pytest.mark.asyncio
async def test_resolucion_por_email_y_telefono_deja_traza_durable_sin_pii(
    db_session,
):
    """(5.4) La resolucion por email/telefono audita canal y resultado sin PII."""
    sector = await _seed_sector(db_session)
    empleado = await _seed_empleado(db_session, sector.id)
    resolucion = ContactResolutionService(db_session, actor_id=5)

    await resolucion.resolver_por_email("auditoria.durable@example.test")
    await resolucion.resolver_por_telefono("+5491100012345")

    registros = [
        f for f in await _registros(db_session) if f.operacion == "resolucion_contacto"
    ]
    assert len(registros) == 2
    assert {f.canal for f in registros} == {"email", "telefono"}
    assert all(f.resultado == "encontrado" for f in registros)
    assert all(f.empleado_id == empleado.id for f in registros)
    assert all(f.created_at is not None for f in registros)

    serializado = repr([(f.canal, f.resultado, f.empleado_id) for f in registros])
    assert "auditoria.durable@example.test" not in serializado
    assert "+5491100012345" not in serializado
    assert "Nombre PII Auditoria" not in serializado


@pytest.mark.asyncio
async def test_resolucion_no_encontrada_tambien_audita_sin_pii(db_session):
    """(5.4) Un resultado no encontrado deja traza durable con canal y resultado."""
    resolucion = ContactResolutionService(db_session)

    await resolucion.resolver_por_email("fantasma@example.test")

    registros = [
        f for f in await _registros(db_session) if f.operacion == "resolucion_contacto"
    ]
    assert len(registros) == 1
    fila = registros[0]
    assert fila.canal == "email"
    assert fila.resultado == "no_encontrado"
    assert fila.empleado_id is None
    assert "fantasma@example.test" not in repr(
        (fila.canal, fila.resultado, fila.empleado_id)
    )


# ── 5.5: triangulacion (no PII y append-only) ─────────────────────────────────


@pytest.mark.asyncio
async def test_tabla_auditoria_no_contiene_email_telefono_ni_nombre_en_claro(
    db_session,
):
    """(5.5) La inspeccion cruda de la tabla no revela datos personales."""
    sector = await _seed_sector(db_session)
    svc = _svc(db_session, actor_id=3)
    email = "sin.pii.auditoria@example.test"
    telefono = "+5491100098765"
    nombre = "Nombre Sensible Auditoria"

    empleado = await svc.crear_empleado(
        legajo="DUR-4",
        nombre=nombre,
        email=email,
        telefono=telefono,
        sector_id=sector.id,
        rol="usuario_final",
    )
    await svc.actualizar_empleado(empleado.id, nombre="Nombre Editado Sensible")
    resolucion = ContactResolutionService(db_session)
    await resolucion.resolver_por_email(email)
    await resolucion.resolver_por_telefono(telefono)

    filas = (await db_session.execute(text(f"SELECT * FROM {_TABLA}"))).all()
    volcado = repr(filas)
    for valor in (email, telefono, nombre, "Nombre Editado Sensible"):
        assert valor not in volcado

    columnas = {columna.name for columna in DirectorioAuditoria.__table__.columns}
    assert not ({"email", "telefono", "nombre"} & columnas)


def test_la_tabla_de_auditoria_es_append_only_en_el_repositorio():
    """(5.5) El repositorio solo registra y lee: no expone update ni delete."""
    from app.repositories.directorio_auditoria_repository import (
        DirectorioAuditoriaRepository,
    )

    metodos = {
        nombre
        for nombre in dir(DirectorioAuditoriaRepository)
        if not nombre.startswith("_")
    }
    prohibidos = {"update", "delete", "actualizar", "borrar", "modificar", "remove"}
    assert not (metodos & prohibidos)
    assert "registrar" in metodos


def test_no_existe_endpoint_de_edicion_ni_borrado_de_auditoria():
    """(5.2) El router del directorio no expone ninguna ruta de auditoria."""
    from app.routes.directorio import router

    rutas = [(getattr(r, "path", ""), getattr(r, "methods", set()) or set()) for r in router.routes]
    assert not any("auditoria" in path for path, _ in rutas)


def test_el_modelo_de_auditoria_es_inmutable_sin_updated_at():
    """(5.5) La fila durable no se actualiza: no hereda TimestampMixin."""
    assert not hasattr(DirectorioAuditoria, "updated_at")
    assert hasattr(DirectorioAuditoria, "created_at")
