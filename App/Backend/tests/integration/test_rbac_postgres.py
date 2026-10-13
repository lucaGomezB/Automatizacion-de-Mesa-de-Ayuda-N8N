"""
Integracion PostgreSQL del rediseno RBAC (c-82).

Requiere un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Verifica en el motor real:
    - El CHECK de `rol` acepta los tres valores y rechaza `operador`.
    - La FK `incidente.reportante_empleado_id` -> `directorio_empleado.id` existe.
"""

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import IntegrityError

from app.models.empleado import Empleado, RolEmpleado

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_check_rol_acepta_tres_y_rechaza_operador(pg_session):
    """En PostgreSQL, el CHECK acepta los tres roles y rechaza `operador`."""
    pg_session.add(
        Empleado(
            legajo="RBAC-MDA",
            nombre="Mesa Sintetica",
            email="rbac.mda@example.test",
            rol=RolEmpleado.mesa_de_ayuda.value,
        )
    )
    await pg_session.flush()

    pg_session.add(
        Empleado(
            legajo="RBAC-OP",
            nombre="Operador Sintetico",
            email="rbac.op@example.test",
            rol="operador",
        )
    )
    with pytest.raises(IntegrityError):
        await pg_session.flush()
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_fk_reportante_del_incidente_existe(pg_engine, seed_pg_catalogs):
    """La FK `reportante_empleado_id` -> `directorio_empleado.id` existe."""

    def _fks(conn):
        return {
            fk["constrained_columns"][0]
            for fk in sa_inspect(conn).get_foreign_keys("incidente")
        }

    async with pg_engine.connect() as conn:
        fks = await conn.run_sync(_fks)

    assert "reportante_empleado_id" in fks
