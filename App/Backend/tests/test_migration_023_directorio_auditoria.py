"""
Tests de la migracion 023: auditoria durable del directorio (c-153, Tema D).

Verifica que la migracion:
    - Declara `revision = "023"` y `down_revision = "022"` (cadena lineal).
    - Crea la tabla append-only `directorio_auditoria` con solo identificadores
      internos, operacion, resultado, canal e instante (SIN columnas PII).
    - Es REVERSIBLE: el downgrade elimina la tabla y sus indices.

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 021/022).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_BLIND_KEY = "clave-de-indice-ciego-de-migracion"

_REVISION = "023"
_DOWN_REVISION = "022"
_TABLE = "directorio_auditoria"

_COLUMNAS_ESPERADAS = {
    "id",
    "operacion",
    "resultado",
    "canal",
    "empleado_id",
    "actor_empleado_id",
    "created_at",
}


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_023_directorio_auditoria.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("PSEUDONYMIZATION_ENCRYPTION_KEY", _TEST_FERNET_KEY)
    monkeypatch.setenv("PSEUDONYMIZATION_INTERNAL_DOMAINS", "[]")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setenv("DIRECTORY_BLIND_INDEX_KEY", _BLIND_KEY)

    from app.config.settings import get_settings

    get_settings.cache_clear()

    import app.utils.encryption as enc_module

    enc_module._fernet_instance = None
    enc_module._fernet_key = None

    yield db_path

    enc_module._fernet_instance = None
    enc_module._fernet_key = None
    get_settings.cache_clear()


def _alembic_config(db_path: Path):
    from alembic.config import Config

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    return cfg


def _run_alembic(command: list[str], db_path: Path) -> None:
    import logging

    from alembic import command as alembic_cmd

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


def _tablas(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'table'")
            ).all()
    finally:
        engine.dispose()
    return {row[0] for row in rows}


def _columnas(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({_TABLE})")).all()
    finally:
        engine.dispose()
    return {row[1] for row in rows}


def _indices(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'index' AND tbl_name = :t"
                ),
                {"t": _TABLE},
            ).all()
    finally:
        engine.dispose()
    return {row[0] for row in rows}


def test_revision_y_cadena_lineal():
    """La migracion 023 sigue linealmente a la 022."""
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(_alembic_config(Path("/tmp/unused.db")))
    revision = script.get_revision(_REVISION)
    assert revision.down_revision == _DOWN_REVISION
    assert script.get_current_head() == _REVISION


def test_upgrade_crea_la_tabla_sin_columnas_pii(db_file):
    """El upgrade crea `directorio_auditoria` con solo campos internos."""
    _run_alembic(["upgrade", "head"], db_file)

    assert _TABLE in _tablas(db_file)
    columnas = _columnas(db_file)
    assert columnas == _COLUMNAS_ESPERADAS
    assert not ({"email", "telefono", "nombre"} & columnas)


def test_upgrade_crea_los_indices_de_consulta(db_file):
    """La tabla indexa el sujeto, el actor y el instante de cada evento."""
    _run_alembic(["upgrade", "head"], db_file)

    indices = _indices(db_file)
    assert "ix_directorio_auditoria_empleado_id" in indices
    assert "ix_directorio_auditoria_actor_empleado_id" in indices
    assert "ix_directorio_auditoria_created_at" in indices


def test_downgrade_elimina_la_tabla(db_file):
    """El downgrade a 022 elimina la tabla y sus indices (reversible)."""
    _run_alembic(["upgrade", "head"], db_file)
    assert _TABLE in _tablas(db_file)

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    assert _TABLE not in _tablas(db_file)
