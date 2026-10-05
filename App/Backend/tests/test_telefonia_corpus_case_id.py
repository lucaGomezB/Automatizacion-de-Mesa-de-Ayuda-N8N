"""
Tests de la persistencia del `corpus_case_id` en el ingreso de telefonia (c-70).

Strict TDD: se escriben ANTES del modelo y del repositorio.

Cubren (tareas 1.2, 1.4, 1.5, 1.7):
    - La columna nullable `corpus_case_id` (String(64), indexada) existe en
      `TelefoniaIngreso` y el ORM acepta el valor o lo deja en None.
    - Round-trip de persistencia con `corpus_case_id` presente y ausente.
    - `call_sid` sigue siendo la clave unica de idempotencia.
    - El repositorio recupera el ULTIMO ingreso por `corpus_case_id`, con
      `selectinload(incidente)` explicito, o None si no existe.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select

from app.config.settings import get_settings

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="


@pytest.fixture(autouse=True)
def override_encryption_key(monkeypatch):
    """Inyecta la clave Fernet de prueba y resetea el cache lazy."""
    mock_settings = MagicMock()
    mock_settings.pseudonymization_encryption_key = _TEST_FERNET_KEY

    get_settings.cache_clear()
    monkeypatch.setattr("app.utils.encryption.get_settings", lambda: mock_settings)

    import app.utils.encryption as enc_module

    enc_module._fernet_instance = None
    yield
    enc_module._fernet_instance = None
    get_settings.cache_clear()


def _model():
    from app.models.telefonia_ingreso import TelefoniaIngreso

    return TelefoniaIngreso


def _repo(session):
    from app.repositories.telefonia_ingreso_repository import (
        TelefoniaIngresoRepository,
    )

    return TelefoniaIngresoRepository(session)


async def _make_incidente(db_session):
    from app.models.catalog import Estado
    from app.models.incidente import Incidente

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


# ── 1.2 RED — Estructura del modelo ─────────────────────────────────────────


def test_columna_corpus_case_id_existe_nullable_e_indexada():
    mapper = sa_inspect(_model())
    assert "corpus_case_id" in mapper.columns
    col = mapper.columns["corpus_case_id"]
    assert col.nullable is True
    assert col.index is True
    assert col.type.length == 64


def test_modelo_acepta_corpus_case_id_opcional():
    fila = _model()(
        call_sid="CA-X",
        transcripcion_estado="pendiente",
        corpus_case_id="CASO-001",
    )
    sin_caso = _model()(call_sid="CA-Y", transcripcion_estado="pendiente")
    assert fila.corpus_case_id == "CASO-001"
    assert sin_caso.corpus_case_id is None


# ── 1.4 TRIANGULATE — Round-trip en persistencia ─────────────────────────────


async def test_persiste_corpus_case_id_y_none(db_session):
    model = _model()
    db_session.add(
        model(
            call_sid="CA-C1",
            transcripcion_estado="pendiente",
            corpus_case_id="CASO-PERSIST",
        )
    )
    db_session.add(model(call_sid="CA-C2", transcripcion_estado="pendiente"))
    await db_session.flush()

    con_caso = (
        await db_session.execute(select(model).where(model.call_sid == "CA-C1"))
    ).scalar_one()
    sin_caso = (
        await db_session.execute(select(model).where(model.call_sid == "CA-C2"))
    ).scalar_one()

    assert con_caso.corpus_case_id == "CASO-PERSIST"
    assert sin_caso.corpus_case_id is None


async def test_call_sid_sigue_siendo_la_clave_unica(db_session):
    model = _model()
    mapper = sa_inspect(model)
    assert mapper.columns["call_sid"].unique is True

    db_session.add(
        model(call_sid="CA-UNIQ", transcripcion_estado="pendiente", corpus_case_id="A")
    )
    await db_session.flush()
    db_session.add(
        model(call_sid="CA-UNIQ", transcripcion_estado="pendiente", corpus_case_id="B")
    )
    from sqlalchemy.exc import IntegrityError

    with pytest.raises(IntegrityError):
        await db_session.flush()


# ── 1.5 / 1.7 RED + TRIANGULATE — Recuperacion del ultimo ingreso ────────────


async def test_get_latest_by_corpus_case_id_devuelve_el_ultimo(db_session):
    repo = _repo(db_session)
    await repo.create(
        call_sid="CA-LAT-1",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-LAT",
    )
    ultimo = await repo.create(
        call_sid="CA-LAT-2",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-LAT",
    )

    encontrado = await repo.get_latest_by_corpus_case_id("CASO-LAT")

    assert encontrado is not None
    assert encontrado.id == ultimo.id
    assert encontrado.call_sid == "CA-LAT-2"


async def test_get_latest_by_corpus_case_id_none_si_no_existe(db_session):
    repo = _repo(db_session)
    assert await repo.get_latest_by_corpus_case_id("NO-EXISTE") is None


async def test_get_latest_carga_el_incidente_vinculado_sin_lazy_load(db_session):
    repo = _repo(db_session)
    ingreso = await repo.create(
        call_sid="CA-LAT-3",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-LAT-INC",
    )
    incidente = await _make_incidente(db_session)
    await repo.link_incidente(ingreso, incidente.id)

    encontrado = await repo.get_latest_by_corpus_case_id("CASO-LAT-INC")

    assert encontrado is not None
    assert encontrado.incidente is not None
    assert encontrado.incidente.id == incidente.id


async def test_get_latest_no_mezcla_casos_distintos(db_session):
    repo = _repo(db_session)
    await repo.create(
        call_sid="CA-OTRO",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-OTRO",
    )
    esperado = await repo.create(
        call_sid="CA-MIO",
        transcripcion_estado="transcrito",
        corpus_case_id="CASO-MIO",
    )

    encontrado = await repo.get_latest_by_corpus_case_id("CASO-MIO")

    assert encontrado is not None
    assert encontrado.id == esperado.id


async def test_get_latest_acepta_id_con_caracteres_especiales(db_session):
    repo = _repo(db_session)
    caso = "CASO-2026/telefono #7"
    creado = await repo.create(
        call_sid="CA-ESP",
        transcripcion_estado="transcrito",
        corpus_case_id=caso,
    )

    encontrado = await repo.get_latest_by_corpus_case_id(caso)

    assert encontrado is not None
    assert encontrado.id == creado.id
