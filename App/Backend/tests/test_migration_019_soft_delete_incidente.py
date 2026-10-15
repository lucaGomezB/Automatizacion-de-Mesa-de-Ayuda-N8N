"""Tests de la migracion 019 y del modelo de borrado logico (c-87, SD-001).

Verifica que la migracion:
    - Declara `revision = "019"` y `down_revision = "018"` (cadena lineal).
    - Tras `upgrade head`, `incidente` incorpora `deleted_at` (TIMESTAMPTZ,
      nullable) y `deleted_by` (INTEGER nullable, FK a `directorio_empleado`
      con `ON DELETE SET NULL`, indexada).
    - El `downgrade` elimina ambas columnas y su indice (esquema previo).
    - No se elimina ni recrea ninguna fila (migracion aditiva).

Verifica tambien el modelo ORM (columnas, nullability, FK e indice).

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 010+).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "019"
_DOWN_REVISION = "018"
_TABLA = "incidente"
_COLUMNAS_NUEVAS = {"deleted_at", "deleted_by"}


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_019_soft_delete_incidente.db"
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


def _sync_engine(db_path: Path):
    return create_engine(f"sqlite:///{db_path}")


def _columnas(db_path: Path, tabla: str) -> set[str]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
    finally:
        engine.dispose()
    return {r[1] for r in rows}


def _columnas_notnull(db_path: Path, tabla: str) -> dict[str, bool]:
    """Mapea columna -> notnull (PRAGMA table_info, indice 3)."""
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
    finally:
        engine.dispose()
    return {r[1]: bool(r[3]) for r in rows}


def _fks(db_path: Path, tabla: str) -> list[dict]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA foreign_key_list({tabla})")).fetchall()
    finally:
        engine.dispose()
    # columnas: id, seq, table, from, to, on_update, on_delete, match
    return [
        {
            "tabla_destino": r[2],
            "from": r[3],
            "to": r[4],
            "on_delete": (r[6] or "").upper(),
        }
        for r in rows
    ]


def _indices(db_path: Path, tabla: str) -> set[str]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA index_list({tabla})")).fetchall()
    finally:
        engine.dispose()
    return {r[1] for r in rows}


# ── Cadena de revisiones ───────────────────────────────────────────────────────


def test_revision_chain_019_down_revision_018():
    """La revision 019 encadena sobre 018 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


# ── Upgrade: columnas de borrado logico ───────────────────────────────────────


def test_upgrade_agrega_columnas_de_borrado(db_file):
    """Tras `upgrade head`, `incidente` tiene `deleted_at` y `deleted_by`."""
    _run_alembic(["upgrade", "head"], db_file)

    columnas = _columnas(db_file, _TABLA)
    assert _COLUMNAS_NUEVAS <= columnas


def test_upgrade_columnas_son_nullable(db_file):
    """Ambas columnas nuevas son nullable (NULL = activo)."""
    _run_alembic(["upgrade", "head"], db_file)

    notnull = _columnas_notnull(db_file, _TABLA)
    assert notnull["deleted_at"] is False
    assert notnull["deleted_by"] is False


def test_upgrade_deleted_by_fk_set_null(db_file):
    """`deleted_by` referencia `directorio_empleado` con ON DELETE SET NULL."""
    _run_alembic(["upgrade", "head"], db_file)

    fks = {fk["from"]: fk for fk in _fks(db_file, _TABLA)}
    assert "deleted_by" in fks
    assert fks["deleted_by"]["tabla_destino"] == "directorio_empleado"
    assert fks["deleted_by"]["on_delete"] == "SET NULL"


def test_upgrade_deleted_by_indexada(db_file):
    """`deleted_by` queda indexada."""
    _run_alembic(["upgrade", "head"], db_file)

    assert "ix_incidente_deleted_by" in _indices(db_file, _TABLA)


# ── Downgrade: elimina las columnas nuevas ────────────────────────────────────


def test_downgrade_elimina_columnas_de_borrado(db_file):
    """El downgrade a 018 restaura el esquema previo (sin las columnas)."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    columnas = _columnas(db_file, _TABLA)
    assert _COLUMNAS_NUEVAS.isdisjoint(columnas)


# ── Modelo ORM ────────────────────────────────────────────────────────────────


def test_modelo_incidente_declara_columnas_de_borrado():
    """El modelo ORM declara `deleted_at` y `deleted_by` nullable."""
    from datetime import datetime

    from sqlalchemy import DateTime

    from app.models.incidente import Incidente

    tabla = Incidente.__table__
    assert "deleted_at" in tabla.columns
    assert "deleted_by" in tabla.columns

    deleted_at = tabla.columns["deleted_at"]
    assert deleted_at.nullable is True
    assert isinstance(deleted_at.type, DateTime)
    assert deleted_at.type.timezone is True
    assert datetime is not None  # anotacion de tipo del Mapped

    deleted_by = tabla.columns["deleted_by"]
    assert deleted_by.nullable is True
    assert deleted_by.index is True


def test_modelo_deleted_by_fk_set_null():
    """La FK del modelo declara ON DELETE SET NULL hacia el directorio."""
    from app.models.incidente import Incidente

    col = Incidente.__table__.columns["deleted_by"]
    fks = list(col.foreign_keys)
    assert len(fks) == 1
    fk = fks[0]
    assert fk.column.table.name == "directorio_empleado"
    assert (fk.ondelete or "").upper() == "SET NULL"
