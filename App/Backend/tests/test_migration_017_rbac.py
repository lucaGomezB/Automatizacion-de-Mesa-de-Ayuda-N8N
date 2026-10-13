"""Tests de la migracion 017: rediseno RBAC (c-82).

Verifica que la migracion:
    - Declara `revision = "017"` y `down_revision = "016"` (cadena lineal).
    - Tras `upgrade head`, existe la columna `reportante_empleado_id` (FK nullable
      a `directorio_empleado`) y el CHECK de rol acepta los tres valores nuevos
      (`usuario_final`, `mesa_de_ayuda`, `administrador_directorio`) y rechaza
      `operador`.
    - El backfill migra filas con `rol='operador'` a `mesa_de_ayuda` ANTES del
      CHECK nuevo.
    - El `downgrade` restaura el CHECK de cuatro valores, elimina la columna del
      reportante y NO re-marca las filas migradas.
    - Se inserta (condicional e idempotente) el empleado sintetico
      `administrador_directorio` de la cuenta `admin` (legajo `SYS-ADMIN`, email
      sintetico `sys-admin@example.test`, telefono nulo), cuyo alcance es GLOBAL.

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 008+).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "017"
_DOWN_REVISION = "016"
_INCIDENTE = "incidente"
_DIRECTORIO = "directorio_empleado"


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_017_rbac.db"
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


def _insertar_empleado(db_path: Path, legajo: str, rol: str, email: str) -> None:
    """Inserta una fila minima del directorio (dispara el CHECK real)."""
    engine = _sync_engine(db_path)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(
                    f"INSERT INTO {_DIRECTORIO} "
                    "(legajo, nombre, email, rol, activo, created_at, updated_at) "
                    "VALUES (:legajo, 'Sintetico', :email, :rol, 1, "
                    "'2026-01-01', '2026-01-01')"
                ),
                {"legajo": legajo, "email": email, "rol": rol},
            )
    finally:
        engine.dispose()


def _contar(db_path: Path, sql: str) -> int:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            return conn.execute(text(sql)).scalar()
    finally:
        engine.dispose()


def _leer_admin_empleado(db_path: Path) -> dict | None:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            row = conn.execute(
                text(
                    f"SELECT {_DIRECTORIO}.legajo, {_DIRECTORIO}.email, "
                    f"{_DIRECTORIO}.telefono, {_DIRECTORIO}.rol, "
                    f"{_DIRECTORIO}.user_id "
                    f"FROM {_DIRECTORIO} "
                    "JOIN users ON users.id = "
                    f"{_DIRECTORIO}.user_id "
                    "WHERE users.username = 'admin'"
                )
            ).fetchone()
    finally:
        engine.dispose()
    if row is None:
        return None
    return {
        "legajo": row[0],
        "email": row[1],
        "telefono": row[2],
        "rol": row[3],
        "user_id": row[4],
    }


# ── Cadena de revisiones ───────────────────────────────────────────────────────


def test_revision_chain_017_down_revision_016():
    """La revision 017 encadena sobre 016 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


# ── Upgrade: columna del reportante + CHECK de tres valores ───────────────────


def test_upgrade_agrega_columna_reportante(db_file):
    """Tras `upgrade head` existe `reportante_empleado_id` (nullable)."""
    _run_alembic(["upgrade", "head"], db_file)
    columnas = _columnas(db_file, _INCIDENTE)
    assert "reportante_empleado_id" in columnas


def test_upgrade_backfill_operador_a_mesa_de_ayuda(db_file):
    """Una fila legacy con `operador` migra a `mesa_de_ayuda` (antes del CHECK)."""
    # 1) Subir hasta 016 (CHECK de cuatro valores; `operador` permitido).
    _run_alembic(["upgrade", "016"], db_file)
    _insertar_empleado(db_file, "LEGACY-OP", "operador", "legacy.op@example.test")

    # 2) Aplicar 017: el backfill la migra antes del CHECK nuevo.
    _run_alembic(["upgrade", "head"], db_file)

    rol = _contar(
        db_file, f"SELECT rol FROM {_DIRECTORIO} WHERE legajo = 'LEGACY-OP'"
    )
    assert rol == "mesa_de_ayuda"


def test_upgrade_check_acepta_tres_y_rechaza_operador(db_file):
    """El CHECK recreado acepta los tres valores y rechaza `operador`."""
    _run_alembic(["upgrade", "head"], db_file)

    _insertar_empleado(db_file, "NEW-MDA", "mesa_de_ayuda", "new.mda@example.test")
    _insertar_empleado(db_file, "NEW-UF", "usuario_final", "new.uf@example.test")
    _insertar_empleado(
        db_file, "NEW-ADM", "administrador_directorio", "new.adm@example.test"
    )

    with pytest.raises(IntegrityError):
        _insertar_empleado(db_file, "NEW-OP", "operador", "new.op@example.test")


# ── Downgrade: revierte el CHECK, elimina la columna y NO re-marca ────────────


def test_downgrade_restaura_check_de_cuatro_y_elimina_columna(db_file):
    """El downgrade a 016 restaura el CHECK de cuatro valores y quita la columna."""
    _run_alembic(["upgrade", "016"], db_file)
    _insertar_empleado(db_file, "LEGACY-OP2", "operador", "legacy.op2@example.test")
    _run_alembic(["upgrade", "head"], db_file)

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    # La columna del reportante desaparece.
    assert "reportante_empleado_id" not in _columnas(db_file, _INCIDENTE)

    # El CHECK de cuatro valores vuelve a aceptar `operador`.
    _insertar_empleado(db_file, "REST-OP", "operador", "rest.op@example.test")

    # NO se re-marcan las filas migradas: siguen como `mesa_de_ayuda`.
    rol = _contar(
        db_file, f"SELECT rol FROM {_DIRECTORIO} WHERE legajo = 'LEGACY-OP2'"
    )
    assert rol == "mesa_de_ayuda"


# ── Empleado sintetico de la cuenta `admin` (OQ-3 / D9) ───────────────────────


def test_upgrade_crea_empleado_sintetico_de_admin(db_file):
    """La migracion crea el empleado sintetico de `admin` (sin PII real)."""
    _run_alembic(["upgrade", "head"], db_file)

    admin = _leer_admin_empleado(db_file)
    assert admin is not None, "La cuenta admin debe tener empleado vinculado"
    assert admin["legajo"] == "SYS-ADMIN"
    assert admin["email"] == "sys-admin@example.test"
    assert admin["telefono"] is None
    assert admin["rol"] == "administrador_directorio"


def test_admin_sintetico_alcance_global(db_file):
    """El rol del empleado de `admin` resuelve alcance GLOBAL, no VACIO."""
    from app.services.role_policy import ModoAlcance, politica_de_rol

    _run_alembic(["upgrade", "head"], db_file)
    admin = _leer_admin_empleado(db_file)
    assert admin is not None
    assert politica_de_rol(admin["rol"]).visibilidad is ModoAlcance.GLOBAL


def test_upgrade_es_idempotente_no_duplica_admin(db_file):
    """Reaplicar la insercion del admin no duplica la fila (idempotente)."""
    _run_alembic(["upgrade", "head"], db_file)
    assert (
        _contar(
            db_file, f"SELECT COUNT(*) FROM {_DIRECTORIO} WHERE legajo = 'SYS-ADMIN'"
        )
        == 1
    )

    # Bajar y volver a subir: sigue habiendo una sola fila (no duplica).
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)
    assert (
        _contar(
            db_file, f"SELECT COUNT(*) FROM {_DIRECTORIO} WHERE legajo = 'SYS-ADMIN'"
        )
        == 0
    )
    _run_alembic(["upgrade", "head"], db_file)
    assert (
        _contar(
            db_file, f"SELECT COUNT(*) FROM {_DIRECTORIO} WHERE legajo = 'SYS-ADMIN'"
        )
        == 1
    )

    # La guarda de insercion es idempotente por si misma (segunda corrida no-op).
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "migracion_017",
        _BACKEND_ROOT / "alembic" / "versions" / "017_rbac_redesign.py",
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)

    engine = _sync_engine(db_file)
    try:
        with engine.begin() as conn:
            modulo._insertar_admin_sintetico(conn)
    finally:
        engine.dispose()

    assert (
        _contar(
            db_file, f"SELECT COUNT(*) FROM {_DIRECTORIO} WHERE legajo = 'SYS-ADMIN'"
        )
        == 1
    )
