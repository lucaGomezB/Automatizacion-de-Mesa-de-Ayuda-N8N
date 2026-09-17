"""
Tests unitarios del IncidenteRepository (C-33).

Cubre `get_by_origen_message_id`, la consulta de idempotencia del contrato de
alta: devuelve la fila asociada al identificador de mensaje de origen o None.
"""

import pytest

from app.models.catalog import Estado
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
