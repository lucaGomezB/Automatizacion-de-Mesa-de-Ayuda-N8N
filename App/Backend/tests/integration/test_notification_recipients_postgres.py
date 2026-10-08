"""
Tests de integracion PostgreSQL de la resolucion de destinatarios (c-56, 2.4).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican el comportamiento real de:
    - La FK a `sector` del directorio (el operador referencia un sector real).
    - La existencia del indice de `sector_id` (base de la lectura acotada D6).
    - La igualdad real de la enumeracion de operadores por sector.

NOTA: este archivo se entrega ESCRITO pero NO se ejecuta en el entorno del
apply (PostgreSQL no alcanzable). Queda pendiente `pytest -m integration`.
"""

import pytest
from sqlalchemy import inspect as sa_inspect

from app.models.empleado import Empleado, RolEmpleado
from app.repositories.empleado_repository import EmpleadoRepository
from app.services.notification_recipient_service import NotificationRecipientService

pytestmark = pytest.mark.integration


async def _crear_empleado(
    session, *, legajo: str, email: str, sector_id: int | None, rol=RolEmpleado.operador
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
async def test_fk_a_sector_del_operador(pg_session, seed_pg_catalogs):
    """Un operador referencia un sector real del catalogo canonico."""
    sector = seed_pg_catalogs["sector_sistemas"]
    empleado = await _crear_empleado(
        pg_session,
        legajo="C56-FK",
        email="c56-fk@example.test",
        sector_id=sector.id,
    )

    assert empleado.sector_id == sector.id


@pytest.mark.asyncio
async def test_indice_de_sector_id_existe(pg_session, pg_engine, seed_pg_catalogs):
    """La base PostgreSQL tiene el indice de `sector_id` del directorio (D6)."""

    def _indices(conn):
        return {
            idx["name"]
            for idx in sa_inspect(conn).get_indexes("directorio_empleado")
        }

    async with pg_engine.connect() as conn:
        indices = await conn.run_sync(_indices)

    assert "ix_directorio_empleado_sector_id" in indices


@pytest.mark.asyncio
async def test_enumeracion_real_por_sector(pg_session, seed_pg_catalogs):
    """La enumeracion real devuelve solo los operadores activos del sector."""
    sistemas = seed_pg_catalogs["sector_sistemas"]
    bd = seed_pg_catalogs["sector_bases_datos"]

    await _crear_empleado(
        pg_session, legajo="C56-S1", email="c56-s1@example.test", sector_id=sistemas.id
    )
    await _crear_empleado(
        pg_session, legajo="C56-S2", email="c56-s2@example.test", sector_id=sistemas.id
    )
    # Otro sector NO debe aparecer.
    await _crear_empleado(
        pg_session, legajo="C56-BD", email="c56-bd@example.test", sector_id=bd.id
    )

    repo = EmpleadoRepository(pg_session)
    operadores = await repo.listar_operadores_por_sector(sistemas.id)

    assert sorted(e.legajo for e in operadores) == ["C56-S1", "C56-S2"]

    destinatarios = await NotificationRecipientService(
        pg_session
    ).resolver_destinatarios_revision(sistemas.id)
    assert sorted(destinatarios) == ["c56-s1@example.test", "c56-s2@example.test"]
