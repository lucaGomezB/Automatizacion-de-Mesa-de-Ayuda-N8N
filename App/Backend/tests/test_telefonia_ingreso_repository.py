"""
Tests del `TelefoniaIngresoRepository` (c-52).

TDD: se escriben ANTES del repositorio.

Cubren:
    - `create` persiste y devuelve la fila con id.
    - `get_by_call_sid` recupera por la clave de idempotencia, o None.
    - `link_incidente` registra el vinculo con el incidente creado.
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from app.config.settings import get_settings
from app.models.catalog import Estado
from app.models.incidente import Incidente

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="


@pytest.fixture(autouse=True)
def override_encryption_key(monkeypatch):
    mock_settings = MagicMock()
    mock_settings.pseudonymization_encryption_key = _TEST_FERNET_KEY

    get_settings.cache_clear()
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)

    import app.utils.encryption as enc_module

    enc_module._fernet_instance = None
    yield
    enc_module._fernet_instance = None
    get_settings.cache_clear()


def _repo(session):
    from app.repositories.telefonia_ingreso_repository import (
        TelefoniaIngresoRepository,
    )

    return TelefoniaIngresoRepository(session)


async def _make_incidente(db_session) -> Incidente:
    estado = Estado(nombre="nuevo", descripcion="Incidente recibido")
    db_session.add(estado)
    await db_session.flush()
    incidente = Incidente(
        descripcion_original="Juan Perez reporto una falla",
        descripcion_pseudonimizada="[PERSONA] reporto una falla",
        estado_id=estado.id,
        requiere_revision_humana=False,
    )
    db_session.add(incidente)
    await db_session.flush()
    return incidente


# ── 3.5 RED — create / get_by_call_sid ──────────────────────────────────────


async def test_create_persiste_y_devuelve_la_fila(db_session):
    repo = _repo(db_session)
    fila = await repo.create(
        call_sid="CA-R1",
        recording_sid="RE-R1",
        transcripcion_estado="transcrito",
    )
    assert fila.id is not None
    assert fila.call_sid == "CA-R1"
    assert fila.recording_sid == "RE-R1"


async def test_get_by_call_sid_encuentra_la_fila(db_session):
    repo = _repo(db_session)
    creada = await repo.create(call_sid="CA-R2", transcripcion_estado="pendiente")

    encontrada = await repo.get_by_call_sid("CA-R2")

    assert encontrada is not None
    assert encontrada.id == creada.id


async def test_get_by_call_sid_devuelve_none_si_no_existe(db_session):
    repo = _repo(db_session)
    assert await repo.get_by_call_sid("CA-NO-EXISTE") is None


# ── 3.7 TRIANGULATE — Vinculo al incidente y recarga por CallSid ────────────


async def test_link_incidente_registra_el_vinculo(db_session):
    repo = _repo(db_session)
    ingreso = await repo.create(call_sid="CA-R3", transcripcion_estado="transcrito")
    incidente = await _make_incidente(db_session)

    actualizado = await repo.link_incidente(ingreso, incidente.id)

    assert actualizado.incidente_id == incidente.id


async def test_recarga_por_callsid_trae_el_incidente_vinculado(db_session):
    repo = _repo(db_session)
    ingreso = await repo.create(call_sid="CA-R4", transcripcion_estado="transcrito")
    incidente = await _make_incidente(db_session)
    await repo.link_incidente(ingreso, incidente.id)

    reloaded = await repo.get_by_call_sid("CA-R4")

    assert reloaded is not None
    assert reloaded.incidente_id == incidente.id
    # El eager loading debe poblar la relacion (sin lazy-load en async).
    assert reloaded.incidente is not None
    assert reloaded.incidente.id == incidente.id
