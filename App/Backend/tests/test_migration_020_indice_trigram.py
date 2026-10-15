"""Tests de la migracion 020: indice trigram de busqueda (c-88, D6).

La migracion es especifica de PostgreSQL (`CREATE EXTENSION pg_trgm` + indice GIN
`gin_trgm_ops`). En motores que no son PostgreSQL (por ejemplo el SQLite con el
que corren los tests de migraciones) es un NO-OP, de modo que la cadena de
migraciones sigue siendo portable y las migraciones previas no se rompen.

Verifica:
    - Revision lineal `020` -> `down_revision = "019"`.
    - En SQLite, `upgrade head` y `downgrade 019` no alteran el esquema de
      `incidente` (la migracion no aplica su DDL especifico de PostgreSQL).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "020"
_DOWN_REVISION = "019"
_TABLA = "incidente"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_020_indice_trigram.db"
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


def _columnas(db_path: Path, tabla: str) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
    finally:
        engine.dispose()
    return {r[1] for r in rows}


def test_revision_chain_020_down_revision_019():
    """La revision 020 encadena sobre 019 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_y_downgrade_no_alteran_esquema_sqlite(db_file):
    """En SQLite la migracion es NO-OP: el esquema de `incidente` no cambia."""
    _run_alembic(["upgrade", "head"], db_file)
    columnas_upgrade = _columnas(db_file, _TABLA)

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)
    columnas_downgrade = _columnas(db_file, _TABLA)

    assert columnas_upgrade == columnas_downgrade
    assert {"descripcion_pseudonimizada", "deleted_at"} <= columnas_upgrade
