"""Tests de la migracion 018 y de los modelos del ciclo de cierre (c-86).

Verifica que la migracion:
    - Declara `revision = "018"` y `down_revision = "017"` (cadena lineal).
    - Tras `upgrade head`, el CHECK `ck_directorio_empleado_rol` acepta los cuatro
      valores del vocabulario (incluido `gestion_incidentes`) y sigue rechazando
      `operador`.
    - Crea `incidente_cierre_sector`, `incidente_evento` e `incidente_comentario`
      con sus columnas, la PK compuesta del cierre y las FKs con el `ondelete`
      esperado (CASCADE / SET NULL / RESTRICT).
    - El `downgrade` reasigna `gestion_incidentes -> usuario_final` ANTES de
      restaurar el CHECK de tres valores, de modo que no queden filas que lo
      violen; elimina las tres tablas.

Verifica tambien el modelo ORM (enum de cuatro valores, CHECK y metadatos de las
tablas nuevas).

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 008+).
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_REVISION = "018"
_DOWN_REVISION = "017"
_DIRECTORIO = "directorio_empleado"

_CUATRO_ROLES = {
    "usuario_final",
    "mesa_de_ayuda",
    "administrador_directorio",
    "gestion_incidentes",
}


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_018_gestion_incidentes.db"
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


def _tablas(db_path: Path) -> set[str]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text("SELECT name FROM sqlite_master WHERE type = 'table'")
            ).fetchall()
    finally:
        engine.dispose()
    return {r[0] for r in rows}


def _columnas(db_path: Path, tabla: str) -> set[str]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
    finally:
        engine.dispose()
    return {r[1] for r in rows}


def _pk_columns(db_path: Path, tabla: str) -> set[str]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA table_info({tabla})")).fetchall()
    finally:
        engine.dispose()
    # La columna `pk` (indice 5) es >0 para las columnas que forman la PK.
    return {r[1] for r in rows if r[5]}


def _fks(db_path: Path, tabla: str) -> list[dict]:
    engine = _sync_engine(db_path)
    try:
        with engine.connect() as conn:
            rows = conn.execute(text(f"PRAGMA foreign_key_list({tabla})")).fetchall()
    finally:
        engine.dispose()
    # columnas: id, seq, table, from, to, on_update, on_delete, match
    return [
        {
            "tabla_destino": r[2],
            "from": r[3],
            "to": r[4],
            "on_delete": (r[6] or "").upper(),
        }
        for r in rows
    ]


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


# ── Cadena de revisiones ───────────────────────────────────────────────────────


def test_revision_chain_018_down_revision_017():
    """La revision 018 encadena sobre 017 (cadena lineal, sin multi-head)."""
    revision = _script_directory().get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION, (
        f"La revision {_REVISION!r} debe declarar down_revision={_DOWN_REVISION!r}; "
        f"valor actual: {revision.down_revision!r}"
    )


# ── Upgrade: CHECK de cuatro valores ──────────────────────────────────────────


def test_upgrade_check_acepta_cuatro_y_rechaza_operador(db_file):
    """El CHECK recreado acepta `gestion_incidentes` y sigue rechazando `operador`."""
    _run_alembic(["upgrade", "head"], db_file)

    _insertar_empleado(
        db_file, "NEW-GEST", "gestion_incidentes", "new.gest@example.test"
    )
    _insertar_empleado(db_file, "NEW-MDA", "mesa_de_ayuda", "new.mda@example.test")
    _insertar_empleado(db_file, "NEW-UF", "usuario_final", "new.uf@example.test")
    _insertar_empleado(
        db_file, "NEW-ADM", "administrador_directorio", "new.adm@example.test"
    )

    with pytest.raises(IntegrityError):
        _insertar_empleado(db_file, "NEW-OP", "operador", "new.op@example.test")


# ── Upgrade: tablas del ciclo ─────────────────────────────────────────────────


def test_upgrade_crea_tablas_del_ciclo(db_file):
    """Las tres tablas nuevas existen con sus columnas esperadas."""
    _run_alembic(["upgrade", "head"], db_file)

    tablas = _tablas(db_file)
    assert {"incidente_cierre_sector", "incidente_evento", "incidente_comentario"} <= tablas

    assert {"incidente_id", "sector_id", "cerrado_por", "cerrado_en"} <= _columnas(
        db_file, "incidente_cierre_sector"
    )
    assert {
        "id",
        "incidente_id",
        "tipo",
        "actor_empleado_id",
        "sector_id",
        "estado_anterior",
        "estado_nuevo",
        "created_at",
    } <= _columnas(db_file, "incidente_evento")
    assert {
        "id",
        "incidente_id",
        "autor_empleado_id",
        "texto",
        "created_at",
    } <= _columnas(db_file, "incidente_comentario")


def test_cierre_sector_tiene_pk_compuesta(db_file):
    """`incidente_cierre_sector` tiene PK compuesta (incidente_id, sector_id)."""
    _run_alembic(["upgrade", "head"], db_file)
    assert _pk_columns(db_file, "incidente_cierre_sector") == {
        "incidente_id",
        "sector_id",
    }


def test_fks_del_ciclo_con_ondelete(db_file):
    """Las FKs del ciclo declaran el `ondelete` esperado (D4/D7/D8)."""
    _run_alembic(["upgrade", "head"], db_file)

    cierre = {
        (fk["from"], fk["tabla_destino"]): fk["on_delete"]
        for fk in _fks(db_file, "incidente_cierre_sector")
    }
    assert cierre[("incidente_id", "incidente")] == "CASCADE"
    assert cierre[("sector_id", "sector")] == "RESTRICT"
    assert cierre[("cerrado_por", "directorio_empleado")] == "SET NULL"

    evento = {
        (fk["from"], fk["tabla_destino"]): fk["on_delete"]
        for fk in _fks(db_file, "incidente_evento")
    }
    assert evento[("incidente_id", "incidente")] == "CASCADE"
    assert evento[("actor_empleado_id", "directorio_empleado")] == "SET NULL"
    assert evento[("sector_id", "sector")] == "SET NULL"

    comentario = {
        (fk["from"], fk["tabla_destino"]): fk["on_delete"]
        for fk in _fks(db_file, "incidente_comentario")
    }
    assert comentario[("incidente_id", "incidente")] == "CASCADE"
    assert comentario[("autor_empleado_id", "directorio_empleado")] == "SET NULL"


# ── Downgrade: reasigna antes del CHECK de tres valores ───────────────────────


def test_downgrade_reasigna_gestion_antes_del_check(db_file):
    """El downgrade pasa `gestion_incidentes` a `usuario_final` y quita las tablas."""
    _run_alembic(["upgrade", "head"], db_file)
    _insertar_empleado(db_file, "G-1", "gestion_incidentes", "g1@example.test")

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    # La fila no quedo violando el CHECK restaurado.
    rol = _contar(db_file, f"SELECT rol FROM {_DIRECTORIO} WHERE legajo = 'G-1'")
    assert rol == "usuario_final"

    # Las tablas del ciclo desaparecen.
    assert "incidente_cierre_sector" not in _tablas(db_file)
    assert "incidente_evento" not in _tablas(db_file)
    assert "incidente_comentario" not in _tablas(db_file)

    # El CHECK de tres valores vuelve a rechazar `gestion_incidentes`.
    with pytest.raises(IntegrityError):
        _insertar_empleado(
            db_file, "G-2", "gestion_incidentes", "g2@example.test"
        )


# ── Modelo ORM ────────────────────────────────────────────────────────────────


def test_modelo_rol_tiene_cuatro_valores():
    """El enum `RolEmpleado` declara exactamente los cuatro valores canonicos."""
    from app.models.empleado import RolEmpleado

    assert {r.value for r in RolEmpleado} == _CUATRO_ROLES


def test_modelo_check_enumera_cuatro_valores():
    """El CHECK del modelo enumera los cuatro valores y no `operador`."""
    from sqlalchemy import CheckConstraint

    from app.models.empleado import Empleado

    checks = [
        c
        for c in Empleado.__table__.constraints
        if isinstance(c, CheckConstraint) and c.name == "ck_directorio_empleado_rol"
    ]
    assert checks, "Falta el CHECK ck_directorio_empleado_rol"
    sqltext = str(checks[0].sqltext)
    for valor in _CUATRO_ROLES:
        assert f"'{valor}'" in sqltext, f"El CHECK no incluye {valor!r}"
    assert "'operador'" not in sqltext


def test_modelo_cierre_sector_pk_y_fks():
    """El modelo ORM del cierre declara PK compuesta y FKs con ondelete."""
    from app.models.incidente import IncidenteCierreSector

    tabla = IncidenteCierreSector.__table__
    assert {c.name for c in tabla.primary_key.columns} == {
        "incidente_id",
        "sector_id",
    }
    ondelete = {
        fk.parent.name: (fk.ondelete or "").upper() for fk in tabla.foreign_keys
    }
    assert ondelete["incidente_id"] == "CASCADE"
    assert ondelete["sector_id"] == "RESTRICT"
    assert ondelete["cerrado_por"] == "SET NULL"


def test_modelo_evento_y_comentario_fks():
    """Los modelos de evento y comentario declaran FKs SET NULL/CASCADE."""
    from app.models.incidente import IncidenteComentario, IncidenteEvento

    evento_fk = {
        fk.parent.name: (fk.ondelete or "").upper()
        for fk in IncidenteEvento.__table__.foreign_keys
    }
    assert evento_fk["incidente_id"] == "CASCADE"
    assert evento_fk["actor_empleado_id"] == "SET NULL"
    assert evento_fk["sector_id"] == "SET NULL"

    comentario_fk = {
        fk.parent.name: (fk.ondelete or "").upper()
        for fk in IncidenteComentario.__table__.foreign_keys
    }
    assert comentario_fk["incidente_id"] == "CASCADE"
    assert comentario_fk["autor_empleado_id"] == "SET NULL"
