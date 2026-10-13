"""
Tests de integracion PostgreSQL de la resolucion de destinatarios (c-82, NR-002).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican el comportamiento real de:
    - La FK a `sector` del directorio (opcional para cualquier rol).
    - La existencia del indice de `sector_id` del directorio.
    - La enumeracion real de los `mesa_de_ayuda` activos, sin filtro de sector.
"""

import pytest
from sqlalchemy import inspect as sa_inspect

from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.services.notification_recipient_service import NotificationRecipientService

pytestmark = pytest.mark.integration


async def _crear_empleado(
    session, *, legajo: str, email: str, sector_id: int | None, rol=RolEmpleado.mesa_de_ayuda
) -> Empleado:
    empleado = Empleado(
        legajo=legajo,
        nombre=f"Empleado {legajo}",
        email=email,
        sector_id=sector_id,
        rol=rol,
        activo=True,
    )
    session.add(empleado)
    await session.flush()
    return empleado


@pytest.mark.asyncio
async def test_fk_a_sector_del_directorio(pg_session, seed_pg_catalogs):
    """Un empleado puede referenciar un sector real del catalogo canonico."""
    sector = seed_pg_catalogs["sector_sistemas"]
    empleado = await _crear_empleado(
        pg_session,
        legajo="C82-FK",
        email="c82-fk@example.test",
        sector_id=sector.id,
    )

    assert empleado.sector_id == sector.id


@pytest.mark.asyncio
async def test_indice_de_sector_id_existe(pg_session, pg_engine, seed_pg_catalogs):
    """La base PostgreSQL tiene el indice de `sector_id` del directorio."""

    def _indices(conn):
        return {
            idx["name"]
            for idx in sa_inspect(conn).get_indexes("directorio_empleado")
        }

    async with pg_engine.connect() as conn:
        indices = await conn.run_sync(_indices)

    assert "ix_directorio_empleado_sector_id" in indices


@pytest.mark.asyncio
async def test_enumeracion_real_de_mesa_de_ayuda(pg_session, seed_pg_catalogs):
    """La enumeracion real devuelve todos los mesa_de_ayuda activos, sin sector."""
    sistemas = seed_pg_catalogs["sector_sistemas"]
    bd = seed_pg_catalogs["sector_bases_datos"]

    await _crear_empleado(
        pg_session, legajo="C82-S1", email="c82-s1@example.test", sector_id=sistemas.id
    )
    await _crear_empleado(
        pg_session, legajo="C82-S2", email="c82-s2@example.test", sector_id=bd.id
    )
    await _crear_empleado(
        pg_session, legajo="C82-SIN", email="c82-sin@example.test", sector_id=None
    )
    # Un usuario_final NO debe aparecer.
    await _crear_empleado(
        pg_session,
        legajo="C82-UF",
        email="c82-uf@example.test",
        sector_id=sistemas.id,
        rol=RolEmpleado.usuario_final,
    )

    repo = EmpleadoRepository(pg_session)
    mesas = await repo.listar_mesa_de_ayuda_activos()

    assert sorted(e.legajo for e in mesas) == ["C82-S1", "C82-S2", "C82-SIN"]

    destinatarios = await NotificationRecipientService(
        pg_session
    ).resolver_destinatarios_revision()
    assert sorted(destinatarios) == [
        "c82-s1@example.test",
        "c82-s2@example.test",
        "c82-sin@example.test",
    ]
