"""
Tests de la migracion 022: indice ciego del directorio (c-153, Tema B).

Verifica que la migracion:
    - Declara `revision = "022"` y `down_revision = "021"` (cadena lineal).
    - Agrega `email_bidx` (NOT NULL, unico) y `telefono_bidx` (nullable, no unico)
      a `directorio_empleado`.
    - RELLENA (backfill) las filas existentes derivando el HMAC-SHA-256 del
      contacto normalizado (descifrando primero el ciphertext de 021).
    - Es REVERSIBLE: el downgrade elimina las dos columnas y sus indices.

Estrategia: SQLite en archivo temporal (mismo patron que test_migration_021).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_BLIND_KEY = "clave-de-indice-ciego-de-migracion"

_REVISION = "022"
_DOWN_REVISION = "021"
_TABLE = "directorio_empleado"

_INSERT = text(
    f"INSERT INTO {_TABLE} "
    "(legajo, nombre, email, telefono, rol, activo, created_at, updated_at) "
    "VALUES (:legajo, :nombre, :email, :telefono, 'usuario_final', 1, "
    "'2026-01-01', '2026-01-01')"
)


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_022_directorio_indice_ciego.db"
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


def _insertar(db_path: Path, legajo: str, email: str, telefono: str | None) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.begin() as conn:
            conn.execute(
                _INSERT,
                {
                    "legajo": legajo,
                    "nombre": "Sintetico",
                    "email": email,
                    "telefono": telefono,
                },
            )
    finally:
        engine.dispose()


def _columnas(db_path: Path) -> set[str]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({_TABLE})")).all()
    finally:
        engine.dispose()
    return {row[1] for row in rows}


def _indices_bidx(
    db_path: Path, legajo: str
) -> tuple[str | None, str | None, str | None]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    f"SELECT email, email_bidx, telefono_bidx FROM {_TABLE} "
                    "WHERE legajo = :l"
                ),
                {"l": legajo},
            ).one()
    finally:
        engine.dispose()
    return row[0], row[1], row[2]


def test_revision_chain_022_down_revision_021():
    """La revision 022 encadena sobre 021 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_agrega_las_columnas_del_indice(db_file):
    """Tras el upgrade head existen email_bidx y telefono_bidx."""
    _run_alembic(["upgrade", "head"], db_file)

    columnas = _columnas(db_file)
    assert {"email_bidx", "telefono_bidx"} <= columnas


def test_upgrade_head_deriva_el_indice_del_contacto_existente(db_file):
    """RED/GREEN (3.1/3.2): el backfill deriva el HMAC del contacto normalizado."""
    email = "backfill.bidx@example.test"
    telefono = "+5491100003300"

    _run_alembic(["upgrade", "020"], db_file)
    _insertar(db_file, "BIDX-BF", email, telefono)
    _run_alembic(["upgrade", "head"], db_file)

    raw_email, email_bidx, telefono_bidx = _indices_bidx(db_file, "BIDX-BF")

    from app.utils.blind_index import indice_ciego_email, indice_ciego_telefono
    from app.utils.encryption import decrypt_value

    assert raw_email.startswith("gAAAA")
    assert decrypt_value(raw_email) == email
    assert email_bidx == indice_ciego_email(email, _BLIND_KEY)
    assert telefono_bidx == indice_ciego_telefono(telefono, _BLIND_KEY)
    assert email_bidx != email
    assert len(email_bidx) == 64


def test_upgrade_head_telefono_nulo_deriva_indice_nulo(db_file):
    """Un empleado sin telefono conserva `telefono_bidx` nulo."""
    email = "sintel.bidx@example.test"

    _run_alembic(["upgrade", "020"], db_file)
    _insertar(db_file, "BIDX-NT", email, None)
    _run_alembic(["upgrade", "head"], db_file)

    _raw_email, email_bidx, telefono_bidx = _indices_bidx(db_file, "BIDX-NT")

    assert telefono_bidx is None
    assert email_bidx is not None and len(email_bidx) == 64


def test_downgrade_elimina_las_columnas_del_indice(db_file):
    """El downgrade a 021 elimina email_bidx y telefono_bidx (reversible).

    La fila se inserta en 021 (contacto en texto) para no depender del NOT NULL
    de `email_bidx`; el upgrade a head backfillea de forma tolerante.
    """
    email = "revert.bidx@example.test"

    _run_alembic(["upgrade", _DOWN_REVISION], db_file)
    _insertar(db_file, "BIDX-RV", email, "+5491100003400")
    _run_alembic(["upgrade", "head"], db_file)

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    columnas = _columnas(db_file)
    assert "email_bidx" not in columnas
    assert "telefono_bidx" not in columnas