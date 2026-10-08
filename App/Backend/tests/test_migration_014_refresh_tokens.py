"""Tests de la migracion 014: refresh_token y token_version (IAH-003/004, c-63a).

Verifica la cadena de revisiones, que `upgrade head` crea la tabla
`refresh_token` (hash, user_id, expires_at, revoked_at, rotated_from) y agrega
`token_version` a `users`, y que `downgrade -1` revierte ambos cambios.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "014"
_DOWN_REVISION = "013"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    db_path = tmp_path / "test_migration_014_refresh.db"
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


def _tables(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return set(inspect(engine).get_table_names())
    finally:
        engine.dispose()


def _columns(db_path: Path, table: str) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return {c["name"] for c in inspect(engine).get_columns(table)}
    finally:
        engine.dispose()


def test_revision_chain_014_down_revision_013():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION


def test_upgrade_creates_refresh_token_and_token_version(db_file):
    _run_alembic(["upgrade", "head"], db_file)

    assert "refresh_token" in _tables(db_file)
    assert {
        "token_hash",
        "user_id",
        "expires_at",
        "revoked_at",
        "rotated_from",
    } <= _columns(db_file, "refresh_token")
    assert "token_version" in _columns(db_file, "users")


def test_downgrade_reverts_refresh_token_and_token_version(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    # Bajar a "013" explicitamente (no "-1"): el head avanzo con 015 y un "-1"
    # solo revertiria 015, no la migracion bajo prueba.
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    assert "refresh_token" not in _tables(db_file)
    assert "token_version" not in _columns(db_file, "users")

    # Reversible: un upgrade posterior recrea ambos.
    _run_alembic(["upgrade", "head"], db_file)
    assert "refresh_token" in _tables(db_file)
    assert "token_version" in _columns(db_file, "users")