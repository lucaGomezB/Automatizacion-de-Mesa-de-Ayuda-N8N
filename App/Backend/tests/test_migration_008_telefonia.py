"""
Tests de la migracion 008: ingreso de telefonia asincronico (c-52, ALTA).

Verifica que la migracion:
    - Declara `revision = "008"` y `down_revision = "007"`.
    - Crea la tabla `telefonia_ingreso` con las columnas esperadas.
    - Define el indice UNIQUE sobre `call_sid` (clave de idempotencia) y los
      indices de apoyo por `incidente_id` y `created_at`.
    - Es reversible: el downgrade dropea la tabla y un upgrade posterior la
      vuelve a crear.

Estrategia:
    SQLite en archivo temporal (mismo patron que test_migration_007_cost_guard.py),
    porque Alembic necesita una conexion real para gestionar el historial de
    revisiones. La cadena de revisiones se lee del `ScriptDirectory`, no por
    substring del archivo.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, inspect

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "008"
_DOWN_REVISION = "007"
_TABLE = "telefonia_ingreso"
_COLUMNS = (
    "id",
    "call_sid",
    "recording_sid",
    "caller_cifrado",
    "duracion_segundos",
    "transcript_original",
    "descripcion_pseudonimizada",
    "ingresado_en",
    "persistido_en",
    "transcripcion_estado",
    "incidente_id",
    "error_detalle",
    "provider",
    "model",
    "created_at",
    "updated_at",
)
_INDEX_CALL_SID = "ix_telefonia_ingreso_call_sid"
_INDEX_INCIDENTE = "ix_telefonia_ingreso_incidente_id"
_INDEX_CREATED = "ix_telefonia_ingreso_created_at"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_008_telefonia.db"
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


def test_revision_chain_008_down_revision_007():
    """La revision 008 encadena sobre 007 (cadena lineal, sin ramas)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe en alembic/versions"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_crea_tabla_de_ingreso(db_file):
    """La tabla `telefonia_ingreso` existe con todas sus columnas."""
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


def test_call_sid_tiene_indice_unico_e_indices_de_apoyo(db_file):
    """Existe el indice UNIQUE de call_sid y los indices de incidente/creacion."""
    _run_alembic(["upgrade", "head"], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        inspector = inspect(engine)
        indexes = {idx["name"]: idx for idx in inspector.get_indexes(_TABLE)}
    finally:
        engine.dispose()

    assert _INDEX_CALL_SID in indexes, (
        "Falta el indice UNIQUE sobre call_sid (clave de idempotencia)"
    )
    assert bool(indexes[_INDEX_CALL_SID].get("unique")), (
        "El indice sobre call_sid debe ser UNIQUE"
    )
    assert _INDEX_INCIDENTE in indexes, "Falta el indice por incidente_id"
    assert _INDEX_CREATED in indexes, "Falta el indice por created_at"


def test_downgrade_dropea_tabla_y_upgrade_la_recrea(db_file):
    """El downgrade a 007 elimina la tabla y el upgrade la recrea."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE not in inspect(engine).get_table_names(), (
            "El downgrade de 008 no elimino la tabla de ingreso de telefonia"
        )
    finally:
        engine.dispose()

    _run_alembic(["upgrade", "head"], db_file)
    engine = create_engine(f"sqlite:///{db_file}")
    try:
        assert _TABLE in inspect(engine).get_table_names(), (
            "El upgrade posterior al downgrade no recreo la tabla de ingreso"
        )
    finally:
        engine.dispose()
