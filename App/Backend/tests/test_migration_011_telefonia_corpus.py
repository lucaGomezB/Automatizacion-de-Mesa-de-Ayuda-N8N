"""
Tests de la migracion 011: `corpus_case_id` y `telefonia_pending_call` (c-70).

Verifica que la migracion:
    - Declara `revision = "011"` y `down_revision = "010"` (cadena lineal).
    - Agrega la columna nullable `corpus_case_id` a `telefonia_ingreso` con su
      indice.
    - Crea la tabla corta `telefonia_pending_call` (`call_sid` PK,
      `corpus_case_id`, `created_at`).
    - Es reversible: el downgrade a 010 elimina columna, indice y tabla, y un
      upgrade posterior las vuelve a crear.

Estrategia: SQLite en archivo temporal (mismo patron que
test_migration_010_fecha_baja.py).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "011"
_DOWN_REVISION = "010"
_TABLE_INGRESO = "telefonia_ingreso"
_COLUMN = "corpus_case_id"
_INDEX = "ix_telefonia_ingreso_corpus_case_id"
_TABLE_PENDING = "telefonia_pending_call"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_011_corpus.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("PSEUDONYMIZATION_ENCRYPTION_KEY", _TEST_FERNET_KEY)
    monkeypatch.setenv("PSEUDONYMIZATION_INTERNAL_DOMAINS", "[]")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")

    from app.config.settings import get_settings

    get_settings.cache_clear()

    import app.utils.encryption as enc_module

    enc_module._fernet_instance = None

    yield db_path

    enc_module._fernet_instance = None
    get_settings.cache_clear()


def _alembic_config(db_path: Path):
    from alembic.config import Config

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def _run_alembic(command: list[str], db_path: Path) -> None:
    from alembic import command as alembic_cmd

    import logging

    logging.getLogger("alembic").setLevel(logging.WARNING)

    cfg = _alembic_config(db_path)
    if command[0] == "upgrade":
        alembic_cmd.upgrade(cfg, command[1])
    elif command[0] == "downgrade":
        alembic_cmd.downgrade(cfg, command[1])


def _script_directory():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_revision_chain_011_down_revision_010():
    """La revision 011 encadena sobre 010 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_agrega_columna_e_indice(db_file):
    """Tras upgrade head, `corpus_case_id` existe, es nullable y esta indexada."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"]: c for c in inspect(engine).get_columns(_TABLE_INGRESO)}
        indices = {i["name"] for i in inspect(engine).get_indexes(_TABLE_INGRESO)}
    finally:
        engine.dispose()

    assert _COLUMN in columnas, f"Falta la columna {_COLUMN!r} en {_TABLE_INGRESO!r}"
    assert columnas[_COLUMN]["nullable"] is True, "corpus_case_id debe ser nullable"
    assert _INDEX in indices, f"Falta el indice {_INDEX!r}"


def test_upgrade_head_crea_la_tabla_corta(db_file):
    """Tras upgrade head, `telefonia_pending_call` existe con sus columnas."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"] for c in inspect(engine).get_columns(_TABLE_PENDING)}
        pk = inspect(engine).get_pk_constraint(_TABLE_PENDING)
    finally:
        engine.dispose()

    assert {"call_sid", "corpus_case_id", "created_at"} <= columnas
    assert pk["constrained_columns"] == ["call_sid"]


def test_downgrade_quita_columna_tabla_y_upgrade_la_recrea(db_file):
    """El downgrade a 010 elimina columna y tabla; el upgrade las recrea."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"] for c in inspect(engine).get_columns(_TABLE_INGRESO)}
        tablas = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    assert _COLUMN not in columnas, "El downgrade de 011 no quito corpus_case_id"
    assert _TABLE_PENDING not in tablas, "El downgrade de 011 no quito la tabla corta"

    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"] for c in inspect(engine).get_columns(_TABLE_INGRESO)}
        tablas = set(inspect(engine).get_table_names())
    finally:
        engine.dispose()
    assert _COLUMN in columnas, "El upgrade posterior no recreo corpus_case_id"
    assert _TABLE_PENDING in tablas, "El upgrade posterior no recreo la tabla corta"
