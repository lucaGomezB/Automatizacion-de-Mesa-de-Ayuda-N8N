"""
Tests del modelo `TelefoniaIngreso` (c-52).

TDD: se escriben ANTES del modelo.

Cubren:
    - Estructura: campos requeridos, `call_sid` UNIQUE, `transcript_original`
      con `EncryptedText`, `incidente_id` FK nullable.
    - Round-trip de cifrado: el valor crudo en la DB es ilegible y el ORM lo
      descifra al leer.
    - Unicidad efectiva de `call_sid` a nivel de persistencia.
"""

from __future__ import annotations

import pytest
from sqlalchemy import inspect as sa_inspect
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from unittest.mock import MagicMock

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


# ── 3.1 RED — Estructura del modelo ─────────────────────────────────────────

_EXPECTED_COLUMNS = {
    "id",
    "call_sid",
    "recording_sid",
    "caller_cifrado",
    "duracion_segundos",
    "transcript_original",
    "descripcion_pseudonimizada",
    "ingresado_en",
    "persistido_en",
    "transcripcion_estado",
    "incidente_id",
    "error_detalle",
    "provider",
    "model",
    "created_at",
    "updated_at",
}


def test_telefonia_ingreso_tiene_los_campos_requeridos():
    mapper = sa_inspect(_model())
    columns = {col.key for col in mapper.columns}
    assert _EXPECTED_COLUMNS <= columns


def test_call_sid_es_unico():
    mapper = sa_inspect(_model())
    col = mapper.columns["call_sid"]
    assert col.nullable is False
    assert col.unique is True


def test_transcript_original_usa_encrypted_text():
    from app.utils.encryption import EncryptedText

    mapper = sa_inspect(_model())
    assert isinstance(mapper.columns["transcript_original"].type, EncryptedText)


def test_caller_cifrado_usa_encrypted_text():
    from app.utils.encryption import EncryptedText

    mapper = sa_inspect(_model())
    assert isinstance(mapper.columns["caller_cifrado"].type, EncryptedText)


def test_incidente_id_es_fk_nullable():
    mapper = sa_inspect(_model())
    col = mapper.columns["incidente_id"]
    assert col.nullable is True
    fk = next(iter(col.foreign_keys))
    assert fk.target_fullname == "incidente.id"


def test_modelo_instanciable():
    model = _model()
    fila = model(
        call_sid="CA123",
        transcripcion_estado="pendiente",
    )
    assert fila.call_sid == "CA123"


# ── 3.3 TRIANGULATE — Cifrado efectivo y unicidad en persistencia ────────────


async def test_transcript_crudo_se_cifra_y_se_descifra_por_el_orm(db_session):
    model = _model()
    plaintext = "Juan Perez reporto una falla en srv-correo01"
    db_session.add(
        model(
            call_sid="CA-ENC-1",
            transcript_original=plaintext,
            descripcion_pseudonimizada="[PERSONA] reporto una falla en [HOST]",
            transcripcion_estado="transcrito",
        )
    )
    await db_session.flush()

    raw = await db_session.execute(
        text("SELECT transcript_original FROM telefonia_ingreso WHERE call_sid = :c"),
        {"c": "CA-ENC-1"},
    )
    raw_value = raw.scalar_one()
    assert raw_value != plaintext
    assert plaintext not in raw_value
    assert raw_value.startswith("gAAAA")  # token Fernet

    loaded = (
        await db_session.execute(
            select(model).where(model.call_sid == "CA-ENC-1")
        )
    ).scalar_one()
    assert loaded.transcript_original == plaintext


async def test_call_sid_duplicado_colisiona(db_session):
    model = _model()
    db_session.add(model(call_sid="CA-DUP", transcripcion_estado="pendiente"))
    await db_session.flush()

    db_session.add(model(call_sid="CA-DUP", transcripcion_estado="pendiente"))
    with pytest.raises(IntegrityError):
        await db_session.flush()
