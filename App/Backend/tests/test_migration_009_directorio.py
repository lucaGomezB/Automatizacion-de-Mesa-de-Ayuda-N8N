"""
Tests de la migracion 009: directorio de empleados (c-54).

Verifica que la migracion:
    - Declara `revision = "009"` y `down_revision = "008"` (cadena lineal).
    - Crea la tabla `directorio_empleado` con las columnas minimizadas.
    - Define indices UNIQUE sobre `legajo` y `email` y de apoyo sobre `telefono`
      y `sector_id`.
    - Es reversible: el downgrade dropea la tabla y un upgrade posterior la
      vuelve a crear.

Estrategia: SQLite en archivo temporal (mismo patron que
test_migration_008_telefonia.py), porque Alembic necesita una conexion real
para gestionar el historial de revisiones.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "009"
_DOWN_REVISION = "008"
_TABLE = "directorio_empleado"
_COLUMNS = (
    "id",
    "legajo",
    "nombre",
    "email",
    "telefono",
    "sector_id",
    "rol",
    "activo",
    "user_id",
    "created_at",
    "updated_at",
)
_INDEX_LEGAJO = "ix_directorio_empleado_legajo"
_INDEX_EMAIL = "ix_directorio_empleado_email"
_INDEX_TELEFONO = "ix_directorio_empleado_telefono"
_INDEX_SECTOR = "ix_directorio_empleado_sector_id"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_009_directorio.db"
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


def test_revision_chain_009_down_revision_008():
    """La revision 009 encadena sobre 008 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_crea_tabla_directorio(db_file):
    """La tabla `directorio_empleado` existe con todas sus columnas."""
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


def test_indices_unicos_y_de_apoyo(db_file):
    """legajo/email tienen indice UNIQUE; telefono/sector_id tienen indice."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        inspector = inspect(engine)
        indexes = {idx["name"]: idx for idx in inspector.get_indexes(_TABLE)}
    finally:
        engine.dispose()

    for nombre in (_INDEX_LEGAJO, _INDEX_EMAIL, _INDEX_TELEFONO, _INDEX_SECTOR):
        assert nombre in indexes, f"Falta el indice {nombre!r}"
    assert bool(indexes[_INDEX_LEGAJO].get("unique")), "legajo debe ser UNIQUE"
    assert bool(indexes[_INDEX_EMAIL].get("unique")), "email debe ser UNIQUE"
    assert not indexes[_INDEX_TELEFONO].get("unique"), "telefono es repetible"
    assert not indexes[_INDEX_SECTOR].get("unique"), "sector_id no es unico"


def test_downgrade_dropea_tabla_y_upgrade_la_recrea(db_file):
    """El downgrade a 008 elimina la tabla y el upgrade la recrea."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE not in inspect(engine).get_table_names(), (
            "El downgrade de 009 no elimino la tabla del directorio"
        )
    finally:
        engine.dispose()

    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE in inspect(engine).get_table_names(), (
            "El upgrade posterior al downgrade no recreo la tabla del directorio"
        )
    finally:
        engine.dispose()
