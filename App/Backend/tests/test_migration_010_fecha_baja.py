"""
Tests de la migracion 010: `fecha_baja` del directorio (c-54, W2 / DIR-007).

Verifica que la migracion:
    - Declara `revision = "010"` y `down_revision = "009"` (cadena lineal).
    - Agrega la columna nullable `fecha_baja` a `directorio_empleado`.
    - Es reversible: el downgrade a 009 elimina la columna y un upgrade la
      vuelve a agregar.

Estrategia: SQLite en archivo temporal (mismo patron que
test_migration_009_directorio.py).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "010"
_DOWN_REVISION = "009"
_TABLE = "directorio_empleado"
_COLUMN = "fecha_baja"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_010_fecha_baja.db"
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


def test_revision_chain_010_down_revision_009():
    """La revision 010 encadena sobre 009 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_agrega_columna_nullable(db_file):
    """Tras upgrade head, `fecha_baja` existe y es nullable."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"]: c for c in inspect(engine).get_columns(_TABLE)}
    finally:
        engine.dispose()

    assert _COLUMN in columnas, f"Falta la columna {_COLUMN!r} en {_TABLE!r}"
    assert columnas[_COLUMN]["nullable"] is True, "fecha_baja debe ser nullable"


def test_downgrade_quita_columna_y_upgrade_la_recrea(db_file):
    """El downgrade a 009 elimina la columna y el upgrade la vuelve a agregar."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"] for c in inspect(engine).get_columns(_TABLE)}
    finally:
        engine.dispose()
    assert _COLUMN not in columnas, "El downgrade de 010 no quito fecha_baja"

    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        columnas = {c["name"] for c in inspect(engine).get_columns(_TABLE)}
    finally:
        engine.dispose()
    assert _COLUMN in columnas, "El upgrade posterior no recreo fecha_baja"
