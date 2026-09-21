"""
Tests de la migracion 007: contadores de la guarda de costo (c-45, ALTA).

Verifica que la migracion:
    - Declara `revision = "007"` y `down_revision = "006"`.
    - Crea la tabla `costo_guarda_contador` con las columnas esperadas.
    - Define la restriccion unica (ambito, clave, ventana_inicio) y el indice
      por `ventana_inicio`.
    - Es reversible: el downgrade dropea la tabla y un upgrade posterior la
      vuelve a crear.

Estrategia:
    SQLite en archivo temporal (mismo patron que test_migration_006_timing.py),
    porque Alembic necesita una conexion real para gestionar el historial de
    revisiones. La cadena de revisiones se lee del `ScriptDirectory`, no por
    substring del archivo.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "007"
_DOWN_REVISION = "006"
_TABLE = "costo_guarda_contador"
_COLUMNS = (
    "id",
    "ambito",
    "clave",
    "ventana_inicio",
    "llamadas",
    "costo_usd",
    "created_at",
    "updated_at",
)


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_007_cost_guard.db"
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


def test_revision_chain_007_down_revision_006():
    """La revision 007 encadena sobre 006 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe en alembic/versions"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_crea_tabla_de_contadores(db_file):
    """La tabla `costo_guarda_contador` existe con todas sus columnas."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        inspector = inspect(engine)
        assert _TABLE in inspector.get_table_names(), (
            f"La tabla {_TABLE!r} no existe tras upgrade head"
        )
        columns = {col["name"] for col in inspector.get_columns(_TABLE)}
    finally:
        engine.dispose()

    assert set(_COLUMNS) <= columns, (
        f"Faltan columnas en {_TABLE!r}: {set(_COLUMNS) - columns}"
    )


def test_tabla_tiene_unicidad_e_indice_de_ventana(db_file):
    """Existe la unica (ambito, clave, ventana_inicio) y el indice por ventana."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        inspector = inspect(engine)
        unique_cols = {
            tuple(c.get("column_names", []))
            for c in inspector.get_unique_constraints(_TABLE)
        }
        indexes = {idx["name"] for idx in inspector.get_indexes(_TABLE)}
    finally:
        engine.dispose()

    assert ("ambito", "clave", "ventana_inicio") in unique_cols, (
        "Falta la restriccion unica (ambito, clave, ventana_inicio)"
    )
    assert "ix_costo_guarda_contador_ventana_inicio" in indexes, (
        "Falta el indice por ventana_inicio"
    )


def test_downgrade_dropea_tabla_y_upgrade_la_recrea(db_file):
    """El downgrade a 006 elimina la tabla y el upgrade la recrea."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE not in inspect(engine).get_table_names(), (
            "El downgrade de 007 no elimino la tabla de contadores"
        )
    finally:
        engine.dispose()

    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE in inspect(engine).get_table_names(), (
            "El upgrade posterior al downgrade no recreo la tabla de contadores"
        )
    finally:
        engine.dispose()
