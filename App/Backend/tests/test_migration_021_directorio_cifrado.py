"""
Tests de la migracion 021: cifrado at-rest del contacto del directorio (c-153).

Verifica que la migracion:
    - Declara `revision = "021"` y `down_revision = "020"` (cadena lineal).
    - Convierte `email`/`telefono` a TEXT y RELLENA (backfill) las filas
      existentes cifrandolas con Fernet, de modo que no queda contacto en claro.
    - Es REVERSIBLE: el downgrade descifra y restaura el texto plano.

Estrategia: SQLite en archivo temporal (mismo patron que test_migration_012),
porque Alembic necesita una conexion real para el historial de revisiones.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "021"
_DOWN_REVISION = "020"
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
    db_path = tmp_path / "test_migration_021_directorio_cifrado.db"
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


def _contacto_crudo(db_path: Path, legajo: str) -> tuple[str | None, str | None]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(f"SELECT email, telefono FROM {_TABLE} WHERE legajo = :l"),
                {"l": legajo},
            ).one()
    finally:
        engine.dispose()
    return row[0], row[1]


def test_revision_chain_021_down_revision_020():
    """La revision 021 encadena sobre 020 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_cifra_el_contacto_existente(db_file):
    """RED/GREEN (2.4/2.5): tras el backfill no queda contacto en claro."""
    email = "backfill@example.test"
    telefono = "+5491100002100"
    _run_alembic(["upgrade", "020"], db_file)
    _insertar(db_file, "C153-BF", email, telefono)

    # Antes de 021 el contacto esta en claro (precondicion del backfill).
    assert _contacto_crudo(db_file, "C153-BF") == (email, telefono)

    _run_alembic(["upgrade", "head"], db_file)

    raw_email, raw_tel = _contacto_crudo(db_file, "C153-BF")
    assert raw_email != email and raw_email.startswith("gAAAA"), raw_email
    assert raw_tel != telefono and raw_tel.startswith("gAAAA"), raw_tel

    from app.utils.encryption import decrypt_value

    assert decrypt_value(raw_email) == email
    assert decrypt_value(raw_tel) == telefono


def test_downgrade_restaura_el_texto_plano(db_file):
    """El downgrade descifra y restaura el contacto en claro (reversible)."""
    email = "revert@example.test"
    telefono = "+5491100002200"
    _run_alembic(["upgrade", "head"], db_file)
    _insertar(db_file, "C153-RV", email, telefono)

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    assert _contacto_crudo(db_file, "C153-RV") == (email, telefono)


def test_telefono_nulo_sobrevive_al_backfill(db_file):
    """Un empleado sin telefono conserva None tras el cifrado (sin crash)."""
    email = "sintel@example.test"
    _run_alembic(["upgrade", "020"], db_file)
    _insertar(db_file, "C153-NT", email, None)

    _run_alembic(["upgrade", "head"], db_file)

    raw_email, raw_tel = _contacto_crudo(db_file, "C153-NT")
    assert raw_tel is None
    assert raw_email.startswith("gAAAA")
