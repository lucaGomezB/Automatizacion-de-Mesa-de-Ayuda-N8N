"""
Tests de integracion PostgreSQL del directorio de empleados (c-54, seccion 3.7).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican el comportamiento real de:
    - FK a `sector` y a `users` (ON DELETE SET NULL).
    - UNIQUE de `legajo` y `email`.
    - Busqueda por igualdad exacta sobre texto plano.
    - Existencia del indice de `telefono`.
"""

import pytest
from sqlalchemy import inspect as sa_inspect, select
from sqlalchemy.exc import IntegrityError

from app.models.empleado import Empleado, RolEmpleado
from app.models.user import User
from app.repositories.empleado_repository import EmpleadoRepository

pytestmark = pytest.mark.integration


async def _crear_user(session, username: str) -> User:
    user = User(username=username, hashed_password="x", is_active=True)
    session.add(user)
    await session.flush()
    return user


async def _crear_empleado(session, **kwargs) -> Empleado:
    valores = {
        "legajo": "PG-1",
        "nombre": "Empleado PG",
        "email": "pg1@example.test",
        "rol": RolEmpleado.usuario_final,
        **kwargs,
    }
    empleado = Empleado(**valores)
    session.add(empleado)
    await session.flush()
    return empleado


@pytest.mark.asyncio
async def test_fk_a_sector_y_users(pg_session, seed_pg_catalogs):
    """Un empleado referencia un sector real y una cuenta real."""
    user = await _crear_user(pg_session, "pg-u-1")
    sector = seed_pg_catalogs["sector_sistemas"]
    empleado = await _crear_empleado(
        pg_session, sector_id=sector.id, user_id=user.id
    )

    assert empleado.sector_id == sector.id
    assert empleado.user_id == user.id


@pytest.mark.asyncio
async def test_fk_a_sector_invalido_rechazada(pg_session, seed_pg_catalogs):
    """Un sector_id inexistente viola la FK."""
    with pytest.raises(IntegrityError):
        await _crear_empleado(pg_session, sector_id=999999)
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_unicidad_de_legajo(pg_session, seed_pg_catalogs):
    """`legajo` es unico a nivel de base."""
    await _crear_empleado(pg_session, legajo="PG-2", email="pg2@example.test")

    with pytest.raises(IntegrityError):
        await _crear_empleado(pg_session, legajo="PG-2", email="otro@example.test")
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_unicidad_de_email(pg_session, seed_pg_catalogs):
    """`email` es unico a nivel de base."""
    await _crear_empleado(pg_session, legajo="PG-3", email="pg3@example.test")

    with pytest.raises(IntegrityError):
        await _crear_empleado(pg_session, legajo="PG-3B", email="pg3@example.test")
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_on_delete_set_null_en_user_id(pg_session, seed_pg_catalogs):
    """Al eliminar la cuenta, el vinculo del empleado queda nulo."""
    user = await _crear_user(pg_session, "pg-u-2")
    empleado = await _crear_empleado(
        pg_session, legajo="PG-4", email="pg4@example.test", user_id=user.id
    )

    await pg_session.delete(user)
    await pg_session.flush()
    await pg_session.refresh(empleado)

    assert empleado.user_id is None


@pytest.mark.asyncio
async def test_busqueda_por_igualdad_exacta(pg_session, seed_pg_catalogs):
    """El repositorio resuelve por email y telefono con igualdad exacta."""
    repo = EmpleadoRepository(pg_session)
    await _crear_empleado(
        pg_session,
        legajo="PG-5",
        email="pg5@example.test",
        telefono="+5491100000005",
    )

    assert (await repo.listar_por_email("pg5@example.test"))[0].legajo == "PG-5"
    assert (await repo.listar_por_telefono("+5491100000005"))[0].legajo == "PG-5"
    assert await repo.listar_por_telefono("+5491100000099") == []


@pytest.mark.asyncio
async def test_indice_de_telefono_existe(pg_session, pg_engine, seed_pg_catalogs):
    """La base PostgreSQL tiene el indice de telefono del directorio."""

    def _indices(conn):
        return {
            idx["name"]
            for idx in sa_inspect(conn).get_indexes("directorio_empleado")
        }

    async with pg_engine.connect() as conn:
        indices = await conn.run_sync(_indices)

    assert "ix_directorio_empleado_telefono" in indices
