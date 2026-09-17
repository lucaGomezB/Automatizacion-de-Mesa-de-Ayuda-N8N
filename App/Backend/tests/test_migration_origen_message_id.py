"""
Tests de la migracion 005: `origen_message_id` y `origen_evento` (C-33, ALTA).

Verifica que la migracion:
    - Agrega `origen_message_id` a `incidente` como columna nullable.
    - Impone una restriccion de unicidad sobre `origen_message_id`.
    - Agrega `origen_evento` a `incidente` como columna nullable, sin unicidad.
    - Es reversible: el downgrade elimina ambas columnas y un upgrade posterior
      las vuelve a crear.
    - NO modifica `001_seed_catalogs.py` (hash SHA-256 intacto).

Estrategia:
    SQLite en archivo temporal (mismo patron que test_migration_sectores.py),
    porque Alembic necesita una conexion real para gestionar el historial de
    revisiones.
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

_COLUMN_NAME = "origen_message_id"

# C-33, W2: la migracion 005 tambien agrega el marcador de evento en la MISMA
# revision (nullable, sin unicidad) para registrar el origen declarado.
_COLUMN_ORIGEN_EVENTO = "origen_evento"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_origen_message_id.db"
    db_url = f"sqlite+aiosqlite:///{db_path}"

    monkeypatch.setenv("DATABASE_URL", db_url)
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("PSEUDONYMIZATION_ENCRYPTION_KEY", _TEST_FERNET_KEY)
    monkeypatch.setenv("PSEUDONYMIZATION_INTERNAL_DOMAINS", "[]")
    monkeypatch.setenv("N8N_WEBHOOK_URL", "")

    from app.config.settings import get_settings
    get_settings.cache_clear()

    import app.utils.encryption as enc_module
    enc_module._fernet_instance = None

    yield db_path

    enc_module._fernet_instance = None
    get_settings.cache_clear()


def _run_alembic(command: list[str], db_path: Path) -> None:
    from alembic import command as alembic_cmd
    from alembic.config import Config

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_ROOT / "alembic"))
    cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")

    import logging
    logging.getLogger("alembic").setLevel(logging.WARNING)

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


def _incidente_unique_indexes(db_path: Path) -> list[dict]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        indexes = inspect(engine).get_indexes("incidente")
        constraints = inspect(engine).get_unique_constraints("incidente")
    finally:
        engine.dispose()
    return [
        {"column_names": list(i.get("column_names", [])), "unique": True}
        for i in indexes
        if i.get("unique")
    ] + [
        {"column_names": list(c.get("column_names", [])), "unique": True}
        for c in constraints
    ]


def test_001_seed_catalogs_no_fue_modificado():
    """La migracion no debe mutar 001_seed_catalogs.py (hash SHA-256 intacto)."""
    digest = hashlib.sha256(_SEED_001_PATH.read_bytes()).hexdigest()
    assert digest == _HASH_001_SEED, (
        "001_seed_catalogs.py fue modificado; la migracion 005 debe ser aditiva."
    )


def test_upgrade_head_agrega_columna_nullable(db_file):
    """La columna `origen_message_id` existe y es nullable tras upgrade head."""
    _run_alembic(["upgrade", "head"], db_file)

    columns = _incidente_columns(db_file)
    assert _COLUMN_NAME in columns, (
        f"La columna {_COLUMN_NAME!r} no existe en 'incidente' tras upgrade head"
    )
    assert columns[_COLUMN_NAME]["nullable"] is True, (
        f"{_COLUMN_NAME!r} debe ser nullable para no obligar a los emisores"
    )


def test_upgrade_head_agrega_origen_evento_nullable(db_file):
    """La columna `origen_evento` existe, es nullable y no es unica."""
    _run_alembic(["upgrade", "head"], db_file)

    columns = _incidente_columns(db_file)
    assert _COLUMN_ORIGEN_EVENTO in columns, (
        f"La columna {_COLUMN_ORIGEN_EVENTO!r} no existe en 'incidente' "
        f"tras upgrade head (la migracion 005 debe declarar ambos campos)"
    )
    assert columns[_COLUMN_ORIGEN_EVENTO]["nullable"] is True, (
        f"{_COLUMN_ORIGEN_EVENTO!r} debe ser nullable: el alta directa puede "
        f"no declarar marcador de evento"
    )

    unique_indexes = _incidente_unique_indexes(db_file)
    assert not any(
        idx["column_names"] == [_COLUMN_ORIGEN_EVENTO] for idx in unique_indexes
    ), (
        f"{_COLUMN_ORIGEN_EVENTO!r} no debe tener restriccion UNIQUE"
    )


def test_upgrade_head_impone_unicidad(db_file):
    """Existe una restriccion/indice unico sobre `origen_message_id`."""
    _run_alembic(["upgrade", "head"], db_file)

    unique_indexes = _incidente_unique_indexes(db_file)
    assert any(
        idx["column_names"] == [_COLUMN_NAME] for idx in unique_indexes
    ), (
        f"No hay restriccion UNIQUE sobre {_COLUMN_NAME!r}; "
        f"indices unicos encontrados: {unique_indexes}"
    )


def test_downgrade_elimina_columnas_y_upgrade_las_recrea(db_file):
    """El downgrade de 005 elimina ambas columnas y el upgrade las recrea.

    Se baja explicitamente hasta la revision `004` (destino), no con `-1`
    relativo, para no depender de migraciones que se agreguen por encima de 005.
    """
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", "004"], db_file)

    columnas = _incidente_columns(db_file)
    assert _COLUMN_NAME not in columnas, (
        "El downgrade de 005 no elimino la columna origen_message_id"
    )
    assert _COLUMN_ORIGEN_EVENTO not in columnas, (
        "El downgrade de 005 no elimino la columna origen_evento"
    )

    _run_alembic(["upgrade", "head"], db_file)
    columnas = _incidente_columns(db_file)
    assert _COLUMN_NAME in columnas, (
        "El upgrade posterior al downgrade no recreo la columna origen_message_id"
    )
    assert _COLUMN_ORIGEN_EVENTO in columnas, (
        "El upgrade posterior al downgrade no recreo la columna origen_evento"
    )
