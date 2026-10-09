"""Tests de la migracion 016: privilegio y campos MFA (c-63b).

Verifica la cadena de revisiones, que `upgrade head` agrega `is_privileged` y los
campos MFA a `users`, que el `admin` sembrado queda privilegiado, y que
`downgrade` a 015 elimina las columnas (reversible).

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 013-015).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "016"
_DOWN_REVISION = "015"
_MFA_COLUMNS = ("is_privileged", "totp_secret", "totp_enabled", "mfa_recovery_codes")


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    db_path = tmp_path / "test_migration_016_mfa_privilege.db"
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


def _columns(db_path: Path, table: str) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return {c["name"] for c in inspect(engine).get_columns(table)}
    finally:
        engine.dispose()


def test_revision_chain_016_down_revision_015():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    script = ScriptDirectory.from_config(cfg)
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION


def test_upgrade_adds_privilege_and_mfa_columns(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    columns = _columns(db_file, "users")
    for name in _MFA_COLUMNS:
        assert name in columns


def test_upgrade_marks_admin_privileged(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        with engine.connect() as conn:
            value = conn.execute(
                text("SELECT is_privileged FROM users WHERE username = 'admin'")
            ).scalar_one()
    finally:
        engine.dispose()
    assert value in (True, 1)


def test_upgrade_leaves_other_users_not_privileged(db_file):
    """Triangulacion: un usuario distinto al admin no queda privilegiado."""
    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO users (username, hashed_password, is_active, "
                    "created_at, updated_at) VALUES ('otro', 'x', 1, "
                    "CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)"
                )
            )
            value = conn.execute(
                text("SELECT is_privileged FROM users WHERE username = 'otro'")
            ).scalar_one()
    finally:
        engine.dispose()
    assert value in (False, 0)


def test_downgrade_removes_privilege_and_mfa_columns(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    columns = _columns(db_file, "users")
    for name in _MFA_COLUMNS:
        assert name not in columns

    # Reversible: un upgrade posterior las vuelve a agregar.
    _run_alembic(["upgrade", "head"], db_file)
    columns = _columns(db_file, "users")
    for name in _MFA_COLUMNS:
        assert name in columns
