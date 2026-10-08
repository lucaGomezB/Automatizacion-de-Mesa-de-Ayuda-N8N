"""Tests de la migracion 012: rol `mesa_de_ayuda` en el directorio (c-60).

Verifica que la migracion:
    - Declara `revision = "012"` y `down_revision = "011"` (cadena lineal, tras
      c-70; no colisiona con una segunda 011).
    - Tras `upgrade head`, el CHECK de `rol` acepta `mesa_de_ayuda` y rechaza un
      valor fuera del vocabulario.
    - El `downgrade -1` restaura el CHECK previo de tres valores (rechaza
      `mesa_de_ayuda`) y un upgrade posterior lo vuelve a ampliar.

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones
008-011), porque Alembic necesita una conexion real para el historial de
revisiones. La migracion usa `batch_alter_table` para ser portable.
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "012"
_DOWN_REVISION = "011"
_TABLE = "directorio_empleado"

_INSERT = text(
    f"INSERT INTO {_TABLE} "
    "(legajo, nombre, email, rol, activo, created_at, updated_at) "
    "VALUES (:legajo, :nombre, :email, :rol, 1, '2026-01-01', '2026-01-01')"
)


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_012_directorio_rol.db"
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


def _insertar_rol(db_path: Path, rol: str, legajo: str) -> None:
    """Inserta una fila minima con el rol dado (dispara el CHECK real de la base)."""
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.begin() as conn:
            conn.execute(
                _INSERT,
                {
                    "legajo": legajo,
                    "nombre": "Sintetico",
                    "email": f"{legajo}@example.test",
                    "rol": rol,
                },
            )
    finally:
        engine.dispose()


def test_revision_chain_012_down_revision_011():
    """La revision 012 encadena sobre 011 (cadena lineal, sin multi-head)."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


def test_upgrade_head_acepta_mesa_de_ayuda_y_rechaza_fuera_de_vocabulario(db_file):
    """El CHECK recreado acepta `mesa_de_ayuda` y rechaza un valor invalido."""
    _run_alembic(["upgrade", "head"], db_file)

    _insertar_rol(db_file, "mesa_de_ayuda", "MA-OK")

    with pytest.raises(IntegrityError):
        _insertar_rol(db_file, "supervisor", "MA-BAD")


def test_downgrade_restaura_check_de_tres_valores(db_file):
    """El downgrade a 011 revierte el CHECK y vuelve a rechazar `mesa_de_ayuda`.

    Se baja a "011" explicitamente (no "-1") porque el head del arbol de
    revisiones avanzo con migraciones posteriores (013/014, c-63a): un `-1`
    solo revertiria la ultima migracion, no la 012 bajo prueba.
    """
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    with pytest.raises(IntegrityError):
        _insertar_rol(db_file, "mesa_de_ayuda", "MA-DOWN")

    # Un upgrade posterior la vuelve a aceptar (reversible).
    _run_alembic(["upgrade", "head"], db_file)
    _insertar_rol(db_file, "mesa_de_ayuda", "MA-UP")