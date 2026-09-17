"""
Tests de la migracion de sectores multietiqueta (C-27, gobernanza ALTA/CRITICA).

Verifica que la migracion (revision siguiente a 003; el numero 002 ya esta
ocupado por la doble representacion de C-03):
    - Siembra exactamente los cinco sectores canonicos.
    - Elimina `Operaciones` y el viejo `Soporte Técnico` (con tilde).
    - Crea las tres tablas de union normalizadas.
    - NO modifica `001_seed_catalogs.py` (hash intacto).
    - Tiene un `downgrade` funcional que restaura el vocabulario previo.

Estrategia:
    SQLite en archivo temporal (mismo patron que test_migration_002.py), porque
    Alembic necesita una conexion real para gestionar el historial de revisiones.
"""

import hashlib
import sqlite3
from pathlib import Path

import pytest

_BACKEND_ROOT = Path(__file__).resolve().parent.parent
_SEED_001_PATH = _BACKEND_ROOT / "alembic" / "versions" / "001_seed_catalogs.py"

# Hash SHA-256 de 001 congelado al iniciar C-27. Si cambia, esta migracion
# dejo de respetar la regla "no mutar 001".
_HASH_001_SEED = "c1c1f81778c58c63005579250d917a392ab53d8e086dc1bf14191713de76ca52"

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_SECTORES_CANONICOS = {
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
}

_TABLAS_UNION = {
    "incidente_sector_adicional",
    "clasificacion_sector_predicho",
    "clasificacion_sector_validado",
}


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_sectores.db"
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


def _sector_names(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    try:
        return {row[0] for row in conn.execute("SELECT nombre FROM sector")}
    finally:
        conn.close()


def _table_names(db_path: Path) -> set[str]:
    conn = sqlite3.connect(str(db_path))
    try:
        return {
            row[0]
            for row in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        }
    finally:
        conn.close()


def test_001_seed_catalogs_no_fue_modificado():
    """La migracion no debe mutar 001_seed_catalogs.py (hash SHA-256 intacto)."""
    digest = hashlib.sha256(_SEED_001_PATH.read_bytes()).hexdigest()
    assert digest == _HASH_001_SEED, (
        "001_seed_catalogs.py fue modificado; la migracion de sectores debe ser "
        "aditiva y no mutar 001."
    )


def test_upgrade_head_siembra_cinco_sectores(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    assert _sector_names(db_file) == _SECTORES_CANONICOS


def test_upgrade_head_elimina_operaciones_y_viejo_soporte(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    nombres = _sector_names(db_file)
    assert "Operaciones" not in nombres
    assert "Soporte Técnico" not in nombres


def test_upgrade_head_crea_tablas_union(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    assert _TABLAS_UNION <= _table_names(db_file)


def test_downgrade_restaura_vocabulario_previo(db_file):
    _run_alembic(["upgrade", "head"], db_file)
    # Bajar explicitamente hasta 003 (estado previo a la 004 de sectores). Se usa
    # la revision destino en lugar de "-1" para no depender de migraciones
    # posteriores que se agreguen por encima de 004.
    _run_alembic(["downgrade", "003"], db_file)

    nombres = _sector_names(db_file)
    assert {"Sistemas", "Operaciones", "Soporte Técnico"} <= nombres
    assert "Seguridad Informatica" not in nombres
    assert "Bases de Datos" not in nombres

    tablas = _table_names(db_file)
    assert not (_TABLAS_UNION & tablas), (
        f"El downgrade debe eliminar las tablas de union; quedaron: "
        f"{_TABLAS_UNION & tablas}"
    )
