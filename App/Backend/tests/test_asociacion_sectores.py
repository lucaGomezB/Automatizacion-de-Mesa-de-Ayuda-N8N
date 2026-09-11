"""
Tests de los modelos ORM de las tablas de union de sectores (C-27).

Verifica:
    - `Incidente.sectores_adicionales` (N-a-N hacia Sector).
    - `ClasificacionLog.sectores_predichos` y `.sectores_validados`.
    - PK compuesta que impide duplicar el mismo sector adicional.
    - Integridad referencial: FK a `sector` y `incidente`/`clasificacion_log`.
    - Cascada ORM: eliminar el incidente limpia sus filas de union.
"""

import pytest
from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError

from app.models.asociaciones import (
    clasificacion_sector_predicho,
    clasificacion_sector_validado,
    incidente_sector_adicional,
)
from app.models.catalog import Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.incidente import Incidente


def test_incidente_tiene_relacion_sectores_adicionales():
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(Incidente)
    assert "sectores_adicionales" in mapper.relationships


def test_clasificacion_log_tiene_relaciones_predicho_y_validado():
    from sqlalchemy import inspect as sa_inspect

    mapper = sa_inspect(ClasificacionLog)
    assert "sectores_predichos" in mapper.relationships
    assert "sectores_validados" in mapper.relationships


def test_pk_compuesta_de_tablas_union():
    assert {c.name for c in incidente_sector_adicional.primary_key.columns} == {
        "incidente_id",
        "sector_id",
    }
    assert {c.name for c in clasificacion_sector_predicho.primary_key.columns} == {
        "clasificacion_log_id",
        "sector_id",
    }
    assert {c.name for c in clasificacion_sector_validado.primary_key.columns} == {
        "clasificacion_log_id",
        "sector_id",
    }


def test_fks_apuntan_a_sector_e_incidente():
    fk_sector = next(iter(incidente_sector_adicional.c.sector_id.foreign_keys))
    fk_incidente = next(iter(incidente_sector_adicional.c.incidente_id.foreign_keys))
    assert fk_sector.column.table.name == "sector"
    assert fk_incidente.column.table.name == "incidente"
    assert fk_incidente.ondelete == "CASCADE"
    assert fk_sector.ondelete in ("RESTRICT", "SET NULL", "CASCADE")


async def _seed_estado_sectores(session):
    estado = Estado(nombre="nuevo", descripcion="x", es_terminal=False)
    s1 = Sector(nombre="Sistemas", descripcion="x")
    s2 = Sector(nombre="Bases de Datos", descripcion="x")
    session.add_all([estado, s1, s2])
    await session.flush()
    return estado, s1, s2


@pytest.mark.asyncio
async def test_duplicado_sector_adicional_rechazado(db_session):
    estado, s1, _ = await _seed_estado_sectores(db_session)
    incidente = Incidente(
        descripcion_original="x",
        descripcion_pseudonimizada="x",
        prioridad="media",
        estado_id=estado.id,
    )
    db_session.add(incidente)
    await db_session.flush()

    await db_session.execute(
        insert(incidente_sector_adicional).values(
            incidente_id=incidente.id, sector_id=s1.id
        )
    )
    with pytest.raises(IntegrityError):
        await db_session.execute(
            insert(incidente_sector_adicional).values(
                incidente_id=incidente.id, sector_id=s1.id
            )
        )
        await db_session.flush()


@pytest.mark.asyncio
async def test_cascade_al_eliminar_incidente(db_session):
    estado, s1, s2 = await _seed_estado_sectores(db_session)
    incidente = Incidente(
        descripcion_original="x",
        descripcion_pseudonimizada="x",
        prioridad="media",
        estado_id=estado.id,
    )
    incidente.sectores_adicionales = [s1, s2]
    db_session.add(incidente)
    await db_session.flush()
    incidente_id = incidente.id

    await db_session.delete(incidente)
    await db_session.flush()

    rows = (
        await db_session.execute(
            select(incidente_sector_adicional).where(
                incidente_sector_adicional.c.incidente_id == incidente_id
            )
        )
    ).all()
    assert rows == []


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fk_sector_inexistente_rechazado_postgresql(pg_session, seed_pg_catalogs):
    """En PostgreSQL una FK a un sector inexistente debe violar integridad."""
    estado = seed_pg_catalogs["estado_nuevo"]
    incidente = Incidente(
        descripcion_original="x",
        descripcion_pseudonimizada="x",
        prioridad="media",
        estado_id=estado.id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    with pytest.raises(IntegrityError):
        await pg_session.execute(
            insert(incidente_sector_adicional).values(
                incidente_id=incidente.id, sector_id=999999
            )
        )
        await pg_session.flush()
