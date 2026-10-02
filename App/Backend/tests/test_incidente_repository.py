"""
Tests unitarios del IncidenteRepository (C-33).

Cubre `get_by_origen_message_id`, la consulta de idempotencia del contrato de
alta: devuelve la fila asociada al identificador de mensaje de origen o None.

c-69: cubre el filtro exacto `origen_message_id` de `list_filtered` (correlacion
determinista item-enviado ↔ incidente-persistido).
"""

import pytest

from app.models.catalog import Estado, Sector
from app.repositories.incidente_repository import IncidenteRepository


def _make_incidente(**kwargs) -> dict:
    base = {
        "descripcion_original": "El servidor de correo no responde",
        "descripcion_pseudonimizada": "El servidor de correo no responde",
        "origen_message_id": "mid-001",
    }
    base.update(kwargs)
    return base


@pytest.mark.asyncio
async def test_get_by_origen_message_id_returns_row(db_session):
    """Devuelve la fila cuyo `origen_message_id` coincide."""
    estado = Estado(nombre="nuevo", descripcion="Incidente recibido")
    db_session.add(estado)
    await db_session.flush()

    repo = IncidenteRepository(db_session)
    creado = await repo.create(estado_id=estado.id, **_make_incidente())

    encontrado = await repo.get_by_origen_message_id("mid-001")

    assert encontrado is not None
    assert encontrado.id == creado.id


@pytest.mark.asyncio
async def test_get_by_origen_message_id_returns_none_when_missing(db_session):
    """Devuelve None cuando el identificador no existe (o es nulo)."""
    repo = IncidenteRepository(db_session)
    assert await repo.get_by_origen_message_id("no-existe") is None


# ── c-69: filtro exacto por origen_message_id ────────────────────────────────


async def _seed_estado(db_session) -> Estado:
    """Siembra un estado 'nuevo' minimo y lo devuelve."""
    estado = Estado(nombre="nuevo", descripcion="Incidente recibido")
    db_session.add(estado)
    await db_session.flush()
    return estado


@pytest.mark.asyncio
async def test_list_filtered_por_origen_message_id_exacto(db_session):
    """
    c-69 (2.1 RED → 2.2 GREEN):
    `list_filtered(origen_message_id=...)` devuelve solo el incidente cuyo
    identificador coincide exactamente.
    """
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R001"))
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R002"))

    resultado = await repo.list_filtered(origen_message_id="corpus-R001")

    assert [i.origen_message_id for i in resultado] == ["corpus-R001"]


@pytest.mark.asyncio
async def test_list_filtered_origen_message_id_inexistente_vacio(db_session):
    """
    c-69 (2.1 RED): un valor inexistente devuelve lista vacia, sin error.
    """
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R001"))

    assert await repo.list_filtered(origen_message_id="no-existe") == []


@pytest.mark.asyncio
async def test_list_filtered_origen_message_id_parcial_no_matchea(db_session):
    """
    c-69 (2.3 TRIANGULATE c): la coincidencia es exacta; un prefijo no matchea.
    """
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R001"))

    assert await repo.list_filtered(origen_message_id="corpus-R00") == []


@pytest.mark.asyncio
async def test_list_filtered_sin_origen_message_id_no_altera(db_session):
    """
    c-69 (2.3 TRIANGULATE b): la ausencia del filtro conserva el listado.
    """
    estado = await _seed_estado(db_session)
    repo = IncidenteRepository(db_session)
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R001"))
    await repo.create(estado_id=estado.id, **_make_incidente(origen_message_id="corpus-R002"))

    assert len(await repo.list_filtered()) == 2


@pytest.mark.asyncio
async def test_list_filtered_origen_message_id_combinado_con_sector(db_session):
    """
    c-69 (2.3 TRIANGULATE a): el filtro de origen se combina con AND logico con
    los demas filtros (por ejemplo sector_id).
    """
    estado = await _seed_estado(db_session)
    sector_a = Sector(nombre="Sistemas", descripcion="A")
    sector_b = Sector(nombre="Bases de Datos", descripcion="B")
    db_session.add_all([sector_a, sector_b])
    await db_session.flush()

    repo = IncidenteRepository(db_session)
    await repo.create(
        estado_id=estado.id,
        sector_id=sector_a.id,
        **_make_incidente(origen_message_id="corpus-A"),
    )
    await repo.create(
        estado_id=estado.id,
        sector_id=sector_b.id,
        **_make_incidente(origen_message_id="corpus-B"),
    )

    resultado = await repo.list_filtered(
        sector_id=sector_a.id, origen_message_id="corpus-A"
    )
    cruza_sectores = await repo.list_filtered(
        sector_id=sector_a.id, origen_message_id="corpus-B"
    )

    assert len(resultado) == 1
    assert resultado[0].sector_id == sector_a.id
    # AND logico: el id de B existe, pero fuera del sector A no se devuelve.
    assert cruza_sectores == []
