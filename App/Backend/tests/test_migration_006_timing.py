"""
Tests de la migracion 006: instrumentacion temporal end-to-end (C-39, ALTA).

Verifica que la migracion:
    - Declara `revision = "006"` y `down_revision = "005"`.
    - Agrega `ingresado_en` y `persistido_en` a `incidente` como columnas
      TIMESTAMPTZ nullable (sin backfill, sin indices).
    - Es reversible: el downgrade elimina ambas columnas y un upgrade posterior
      las vuelve a crear.
    - NO modifica `001_seed_catalogs.py` (hash SHA-256 intacto).

Estrategia:
    SQLite en archivo temporal (mismo patron que test_migration_origen_message_id.py),
    porque Alembic necesita una conexion real para gestionar el historial de
    revisiones. La cadena de revisiones se lee del `ScriptDirectory`, no por
    substring del archivo, para no acoplarse al formato textual.
"""

import hashlib
from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_SEED_001_PATH = _BACKEND_ROOT / "alembic" / "versions" / "001_seed_catalogs.py"

# Hash SHA-256 de 001 congelado desde C-27. Si cambia, esta migracion dejo de
# respetar la regla "no mutar 001".
_HASH_001_SEED = "c1c1f81778c58c63005579250d917a392ab53d8e086dc1bf14191713de76ca52"

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "006"
_DOWN_REVISION = "005"

_COLUMN_INGRESADO = "ingresado_en"
_COLUMN_PERSISTIDO = "persistido_en"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_006_timing.db"
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


def _incidente_columns(db_path: Path) -> dict[str, dict]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        return {col["name"]: col for col in inspect(engine).get_columns("incidente")}
    finally:
        engine.dispose()


def _script_directory():
    from alembic.config import Config
    from alembic.script import ScriptDirectory

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    return ScriptDirectory.from_config(cfg)


def test_001_seed_catalogs_no_fue_modificado():
    """La migracion 006 no debe mutar 001_seed_catalogs.py (hash SHA-256 intacto)."""
    digest = hashlib.sha256(_SEED_001_PATH.read_bytes()).hexdigest()
    assert digest == _HASH_001_SEED, (
        "001_seed_catalogs.py fue modificado; la migracion 006 debe ser aditiva."
    )


def test_revision_chain_006_down_revision_005():
    """La revision 006 encadena sobre 005 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe en alembic/versions"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_agrega_columnas_nullable(db_file):
    """`ingresado_en` y `persistido_en` existen y son nullable tras upgrade head."""
    _run_alembic(["upgrade", "head"], db_file)

    columns = _incidente_columns(db_file)
    for name in (_COLUMN_INGRESADO, _COLUMN_PERSISTIDO):
        assert name in columns, (
            f"La columna {name!r} no existe en 'incidente' tras upgrade head"
        )
        assert columns[name]["nullable"] is True, (
            f"{name!r} debe ser nullable: el contrato tolera la ausencia del instante"
        )


def test_columnas_no_son_onupdate_ni_unicas(db_file):
    """Ninguna de las dos columnas es UNIQUE ni tiene default de servidor."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        unique_indexes = inspect(engine).get_indexes("incidente")
        unique_constraints = inspect(engine).get_unique_constraints("incidente")
    finally:
        engine.dispose()

    unique_cols = {
        tuple(idx.get("column_names", []))
        for idx in unique_indexes
        if idx.get("unique")
    } | {
        tuple(c.get("column_names", [])) for c in unique_constraints
    }

    for name in (_COLUMN_INGRESADO, _COLUMN_PERSISTIDO):
        assert (name,) not in unique_cols, (
            f"{name!r} no debe tener restriccion UNIQUE"
        )


def test_downgrade_elimina_columnas_y_upgrade_las_recrea(db_file):
    """El downgrade de 006 elimina ambas columnas y el upgrade las recrea.

    Se baja explicitamente hasta la revision `005` (destino), no con `-1`
    relativo, para no depender de migraciones que se agreguen por encima de 006.
    """
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", "005"], db_file)

    columnas = _incidente_columns(db_file)
    assert _COLUMN_INGRESADO not in columnas, (
        "El downgrade de 006 no elimino la columna ingresado_en"
    )
    assert _COLUMN_PERSISTIDO not in columnas, (
        "El downgrade de 006 no elimino la columna persistido_en"
    )

    _run_alembic(["upgrade", "head"], db_file)
    columnas = _incidente_columns(db_file)
    assert _COLUMN_INGRESADO in columnas, (
        "El upgrade posterior al downgrade no recreo la columna ingresado_en"
    )
    assert _COLUMN_PERSISTIDO in columnas, (
        "El upgrade posterior al downgrade no recreo la columna persistido_en"
    )
