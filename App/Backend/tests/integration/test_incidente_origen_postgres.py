"""
Tests de integracion PostgreSQL del filtro por `origen_message_id` (c-69).

Requieren un PostgreSQL alcanzable (base DESCARTABLE `mesa_de_ayuda_test`).
Marcados `@pytest.mark.integration`. Verifican el comportamiento real de:
    - La coincidencia EXACTA de `list_filtered(origen_message_id=...)`.
    - La unicidad de `origen_message_id` a nivel de indice (migracion 005).
    - La consulta de idempotencia `get_by_origen_message_id`.

La ejecucion local requiere `docker compose up -d postgres`; en CI corre contra
el contenedor de servicio dedicado (`TEST_PG_URL`).
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.repositories.incidente_repository import IncidenteRepository

pytestmark = pytest.mark.integration


def _make_incidente(origen_message_id: str) -> dict:
    return {
        "descripcion_original": "El servidor de correo no responde",
        "descripcion_pseudonimizada": "El servidor de correo no responde",
        "origen_message_id": origen_message_id,
    }


@pytest.mark.asyncio
async def test_filter_exacto_origen_message_id(pg_session, seed_pg_catalogs):
    """`list_filtered(origen_message_id=...)` devuelve solo la fila exacta."""
    estado = seed_pg_catalogs["estado_nuevo"]
    repo = IncidenteRepository(pg_session)
    await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-1"))
    await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-2"))

    resultado = await repo.list_filtered(origen_message_id="pg-origen-1")

    assert [i.origen_message_id for i in resultado] == ["pg-origen-1"]


@pytest.mark.asyncio
async def test_filter_parcial_no_matchea(pg_session, seed_pg_catalogs):
    """La coincidencia es exacta; un prefijo no matchea."""
    estado = seed_pg_catalogs["estado_nuevo"]
    repo = IncidenteRepository(pg_session)
    await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-3"))

    assert await repo.list_filtered(origen_message_id="pg-origen") == []


@pytest.mark.asyncio
async def test_unicidad_origen_message_id_a_nivel_de_base(pg_session, seed_pg_catalogs):
    """El indice único impide registrar dos filas con el mismo identificador."""
    estado = seed_pg_catalogs["estado_nuevo"]
    repo = IncidenteRepository(pg_session)
    await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-uniq"))

    with pytest.raises(IntegrityError):
        await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-uniq"))
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_get_by_origen_message_id_devuelve_la_fila(pg_session, seed_pg_catalogs):
    """La reconsulta de idempotencia ubica la fila por su identificador."""
    estado = seed_pg_catalogs["estado_nuevo"]
    repo = IncidenteRepository(pg_session)
    creado = await repo.create(estado_id=estado.id, **_make_incidente("pg-origen-get"))

    encontrado = await repo.get_by_origen_message_id("pg-origen-get")

    assert encontrado is not None
    assert encontrado.id == creado.id
