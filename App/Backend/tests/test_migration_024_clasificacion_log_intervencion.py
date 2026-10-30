"""
Tests de la migracion 024: metadatos de intervencion humana en `clasificacion_log`
(c-165, ASG-005, gobernanza ALTA; checkpoint 2.1 aprobado el 2026-10-30).

Verifica que la migracion:
    - Declara `revision = "024"` y `down_revision = "023"` (cadena lineal) y es el
      head.
    - Tras `upgrade head`, `clasificacion_log` incorpora cuatro columnas nullable:
      `validado_por_empleado_id` (INTEGER, FK nombrada a `directorio_empleado` con
      `ON DELETE SET NULL`, indexada), `intervencion_inicio_en` y `validado_en`
      (TIMESTAMPTZ) y `origen_intervencion` (VARCHAR(20), sin CHECK: el vocabulario
      se valida en la capa de aplicacion).
    - Es ADITIVA: las filas previas quedan intactas y SIN backfill (un log validado
      antes de la 024 queda con `validado_en` NULL, es decir, legado).
    - El `downgrade` retira indice, FK y columnas sin tocar las filas.
    - El DDL que emite para PostgreSQL (modo `--sql`, sin conexion) es el aprobado en
      el checkpoint 2.1.

Estrategia: SQLite en archivo temporal (mismo patron que las migraciones 019/023) y
render offline del DDL de PostgreSQL. No se ejecuta `alembic upgrade` contra un
PostgreSQL real (decision del checkpoint 2.1, seccion 8); la FK `SET NULL` sobre
PostgreSQL se prueba en `tests/integration/` sobre el esquema de `create_all`.
"""

import io
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

_BACKEND_ROOT = Path(__file__).resolve().parent.parent

_TEST_FERNET_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="
_BLIND_KEY = "clave-de-indice-ciego-de-migracion"
_URL_POSTGRES = "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy"

_REVISION = "024"
_DOWN_REVISION = "023"
_TABLA = "clasificacion_log"
_NOMBRE_FK = "fk_clasificacion_log_validado_por_directorio_empleado"
_NOMBRE_INDICE = "ix_clasificacion_log_validado_por_empleado_id"

_COLUMNAS_NUEVAS = {
    "validado_por_empleado_id",
    "intervencion_inicio_en",
    "validado_en",
    "origen_intervencion",
}
_COLUMNAS_PREVIAS = {
    "id",
    "incidente_id",
    "sector_id_predicho",
    "confianza",
    "etapa",
    "requiere_revision_humana",
    "respuesta_raw",
    "sector_id_validado",
    "created_at",
    "updated_at",
}


@pytest.fixture()
def db_file(tmp_path, monkeypatch):
    """SQLite en archivo temporal con las env vars requeridas por Alembic/tests."""
    db_path = tmp_path / "test_migration_024_clasificacion_log_intervencion.db"
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


def _alembic_config(db_path: Path, **kwargs):
    from alembic.config import Config

    cfg = Config(str(_BACKEND_ROOT / "alembic.ini"), **kwargs)
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
    from alembic.script import ScriptDirectory

    return ScriptDirectory.from_config(_alembic_config(Path("/tmp/unused.db")))


def _filas(db_path: Path, sql: str, params: dict | None = None) -> list[tuple]:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            return [tuple(r) for r in conn.execute(text(sql), params or {}).fetchall()]
    finally:
        engine.dispose()


def _ejecutar(db_path: Path, sql: str, params: dict | None = None) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.begin() as conn:
            conn.execute(text(sql), params or {})
    finally:
        engine.dispose()


def _columnas(db_path: Path) -> set[str]:
    return {r[1] for r in _filas(db_path, f"PRAGMA table_info({_TABLA})")}


def _info_columnas(db_path: Path) -> dict[str, dict]:
    """Mapea columna -> {tipo, notnull} (PRAGMA table_info)."""
    return {
        r[1]: {"tipo": (r[2] or "").upper(), "notnull": bool(r[3])}
        for r in _filas(db_path, f"PRAGMA table_info({_TABLA})")
    }


def _fks(db_path: Path) -> list[dict]:
    # columnas de PRAGMA foreign_key_list: id, seq, table, from, to, on_update, on_delete
    return [
        {
            "tabla_destino": r[2],
            "from": r[3],
            "to": r[4],
            "on_delete": (r[6] or "").upper(),
        }
        for r in _filas(db_path, f"PRAGMA foreign_key_list({_TABLA})")
    ]


def _indices(db_path: Path) -> set[str]:
    return {r[1] for r in _filas(db_path, f"PRAGMA index_list({_TABLA})")}


def _ddl_tabla(db_path: Path) -> str:
    filas = _filas(
        db_path,
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = :t",
        {"t": _TABLA},
    )
    return filas[0][0]


def _insertar_log(db_path: Path, **valores) -> None:
    """Inserta un log directo (FKs apagadas: el copy-and-move no exige padres)."""
    base = {
        "incidente_id": 1,
        "sector_id_predicho": 1,
        "confianza": 0.55,
        "etapa": "gemini",
        "requiere_revision_humana": 1,
        "respuesta_raw": "{}",
        "sector_id_validado": None,
        "created_at": "2026-10-01 10:00:00.000000",
        "updated_at": "2026-10-01 10:00:00.000000",
    }
    base.update(valores)
    columnas = ", ".join(base)
    marcadores = ", ".join(f":{k}" for k in base)
    _ejecutar(
        db_path,
        f"INSERT INTO {_TABLA} ({columnas}) VALUES ({marcadores})",
        base,
    )


# ── Cadena de revisiones ───────────────────────────────────────────────────────


def test_revision_024_encadena_sobre_023_y_es_el_head():
    """La 024 sigue linealmente a la 023 (sin multi-head) y es el head actual."""
    script = _script_directory()
    revision = script.get_revision(_REVISION)
    assert revision is not None, f"La revision {_REVISION!r} no existe"
    assert revision.down_revision == _DOWN_REVISION
    assert script.get_current_head() == _REVISION
    assert len(script.get_heads()) == 1


# ── Upgrade: cuatro columnas nullable ──────────────────────────────────────────


def test_upgrade_agrega_las_cuatro_columnas_y_conserva_las_previas(db_file):
    """Tras `upgrade head`, `clasificacion_log` tiene 10 + 4 columnas."""
    _run_alembic(["upgrade", "head"], db_file)

    columnas = _columnas(db_file)
    assert _COLUMNAS_NUEVAS <= columnas
    assert _COLUMNAS_PREVIAS <= columnas
    assert columnas == _COLUMNAS_PREVIAS | _COLUMNAS_NUEVAS


def test_upgrade_columnas_nuevas_son_nullable_y_con_el_tipo_aprobado(db_file):
    """Las cuatro columnas son nullable (NULL = no intervenido) y de los tipos del checkpoint."""
    _run_alembic(["upgrade", "head"], db_file)

    info = _info_columnas(db_file)
    assert all(info[c]["notnull"] is False for c in _COLUMNAS_NUEVAS)
    assert info["validado_por_empleado_id"]["tipo"] == "INTEGER"
    assert info["origen_intervencion"]["tipo"] == "VARCHAR(20)"
    # SQLite no distingue TIMESTAMPTZ: DateTime(timezone=True) se declara DATETIME.
    assert info["intervencion_inicio_en"]["tipo"] == "DATETIME"
    assert info["validado_en"]["tipo"] == "DATETIME"


def test_upgrade_actor_referencia_el_directorio_con_set_null_y_fk_nombrada(db_file):
    """`validado_por_empleado_id` -> directorio_empleado.id, ON DELETE SET NULL, FK con nombre."""
    _run_alembic(["upgrade", "head"], db_file)

    fks = {fk["from"]: fk for fk in _fks(db_file)}
    assert fks["validado_por_empleado_id"]["tabla_destino"] == "directorio_empleado"
    assert fks["validado_por_empleado_id"]["to"] == "id"
    assert fks["validado_por_empleado_id"]["on_delete"] == "SET NULL"
    # La FK conserva el nombre aprobado (PRAGMA no lo informa: se lee del DDL).
    assert _NOMBRE_FK in _ddl_tabla(db_file)
    # Las FKs previas (incidente y las dos de sector) siguen presentes tras el copy-and-move.
    assert {"incidente_id", "sector_id_predicho", "sector_id_validado"} <= set(fks)


def test_upgrade_indexa_el_actor_y_conserva_los_indices_previos(db_file):
    """El actor queda indexado y los indices de la 001 sobreviven a la recreacion de la tabla."""
    _run_alembic(["upgrade", "head"], db_file)

    indices = _indices(db_file)
    assert _NOMBRE_INDICE in indices
    assert "ix_clasificacion_log_incidente_id" in indices
    assert "ix_clasificacion_log_created_at" in indices


def test_upgrade_no_impone_check_sobre_el_origen(db_file):
    """El vocabulario del origen NO se fija en la base (se valida en la aplicacion)."""
    _run_alembic(["upgrade", "head"], db_file)

    ddl = _ddl_tabla(db_file).upper()
    assert "CHECK" not in ddl
    # Un valor ajeno al vocabulario se acepta a nivel de esquema: lo rechaza la capa de aplicacion.
    _insertar_log(db_file, origen_intervencion="valor-fuera-de-vocabulario")
    assert _filas(db_file, f"SELECT origen_intervencion FROM {_TABLA}") == [
        ("valor-fuera-de-vocabulario",)
    ]


# ── Upgrade: aditiva, sin backfill ─────────────────────────────────────────────


def test_upgrade_conserva_filas_previas_sin_backfill(db_file):
    """Filas anteriores a la 024 quedan intactas; un log ya validado queda legado."""
    _run_alembic(["upgrade", _DOWN_REVISION], db_file)
    _insertar_log(db_file, id=10, incidente_id=100)
    _insertar_log(
        db_file,
        id=11,
        incidente_id=101,
        sector_id_validado=2,
        requiere_revision_humana=0,
        created_at="2026-10-02 11:00:00.000000",
    )
    previas = _filas(
        db_file,
        f"SELECT {', '.join(sorted(_COLUMNAS_PREVIAS))} FROM {_TABLA} ORDER BY id",
    )

    _run_alembic(["upgrade", _REVISION], db_file)

    posteriores = _filas(
        db_file,
        f"SELECT {', '.join(sorted(_COLUMNAS_PREVIAS))} FROM {_TABLA} ORDER BY id",
    )
    assert posteriores == previas
    assert len(posteriores) == 2
    # Sin backfill: ni el log pendiente ni el ya validado reciben metadatos.
    nuevas = _filas(
        db_file,
        "SELECT id, validado_por_empleado_id, intervencion_inicio_en, validado_en, "
        f"origen_intervencion FROM {_TABLA} ORDER BY id",
    )
    assert nuevas == [(10, None, None, None, None), (11, None, None, None, None)]


# ── Downgrade ─────────────────────────────────────────────────────────────────


def test_downgrade_retira_indice_fk_y_columnas_sin_tocar_las_filas(db_file):
    """El downgrade a 023 restaura el esquema previo y conserva los datos de las columnas viejas."""
    _run_alembic(["upgrade", _REVISION], db_file)
    _insertar_log(
        db_file,
        id=20,
        incidente_id=200,
        sector_id_validado=2,
        validado_por_empleado_id=7,
        intervencion_inicio_en="2026-10-03 09:00:00.000000",
        validado_en="2026-10-03 09:00:30.000000",
        origen_intervencion="gate",
    )

    _run_alembic(["downgrade", _DOWN_REVISION], db_file)

    assert _COLUMNAS_NUEVAS.isdisjoint(_columnas(db_file))
    assert _columnas(db_file) == _COLUMNAS_PREVIAS
    assert _NOMBRE_INDICE not in _indices(db_file)
    assert "validado_por_empleado_id" not in {fk["from"] for fk in _fks(db_file)}
    assert _NOMBRE_FK not in _ddl_tabla(db_file)
    # La fila y sus columnas previas siguen ahi.
    assert _filas(
        db_file, f"SELECT id, incidente_id, sector_id_validado FROM {_TABLA}"
    ) == [(20, 200, 2)]
    # Los indices de la 001 tambien sobreviven al downgrade.
    assert "ix_clasificacion_log_incidente_id" in _indices(db_file)


def test_ciclo_upgrade_downgrade_upgrade_es_repetible(db_file):
    """Subir, bajar y volver a subir no falla ni deja restos (downgrade probado)."""
    _run_alembic(["upgrade", "head"], db_file)
    _run_alembic(["downgrade", _DOWN_REVISION], db_file)
    _run_alembic(["upgrade", "head"], db_file)

    assert _columnas(db_file) == _COLUMNAS_PREVIAS | _COLUMNAS_NUEVAS
    assert _NOMBRE_INDICE in _indices(db_file)


# ── DDL de PostgreSQL (render offline, sin conexion) ──────────────────────────


def _render_postgres(comando: str, rango: str, monkeypatch) -> str:
    """Renderiza el SQL de PostgreSQL del rango dado (alembic `--sql`) normalizando espacios."""
    import logging

    from alembic import command as alembic_cmd

    from app.config.settings import get_settings

    logging.getLogger("alembic").setLevel(logging.WARNING)
    monkeypatch.setenv("DATABASE_URL", _URL_POSTGRES)
    get_settings.cache_clear()

    buffer = io.StringIO()
    cfg = _alembic_config(Path("/tmp/unused.db"), output_buffer=buffer)
    getattr(alembic_cmd, comando)(cfg, rango, sql=True)
    return " ".join(buffer.getvalue().split())


def test_ddl_postgresql_del_upgrade_es_el_aprobado_en_el_checkpoint(db_file, monkeypatch):
    """El SQL de PostgreSQL agrega las columnas, la FK SET NULL nombrada y el indice."""
    sql = _render_postgres("upgrade", f"{_DOWN_REVISION}:{_REVISION}", monkeypatch)

    assert "ALTER TABLE clasificacion_log ADD COLUMN validado_por_empleado_id INTEGER;" in sql
    assert (
        f"ALTER TABLE clasificacion_log ADD CONSTRAINT {_NOMBRE_FK} "
        "FOREIGN KEY(validado_por_empleado_id) REFERENCES directorio_empleado (id) "
        "ON DELETE SET NULL;"
    ) in sql
    assert (
        "ALTER TABLE clasificacion_log ADD COLUMN intervencion_inicio_en "
        "TIMESTAMP WITH TIME ZONE;"
    ) in sql
    assert "ALTER TABLE clasificacion_log ADD COLUMN validado_en TIMESTAMP WITH TIME ZONE;" in sql
    assert "ALTER TABLE clasificacion_log ADD COLUMN origen_intervencion VARCHAR(20);" in sql
    assert (
        f"CREATE INDEX {_NOMBRE_INDICE} ON clasificacion_log (validado_por_empleado_id);"
    ) in sql
    # Aditiva: ni backfill ni CHECK ni NOT NULL.
    assert "UPDATE clasificacion_log" not in sql
    assert "INSERT INTO clasificacion_log" not in sql
    assert "CHECK" not in sql
    assert "NOT NULL" not in sql


def test_ddl_postgresql_del_downgrade_retira_en_orden_inverso(db_file, monkeypatch):
    """El downgrade elimina el indice y luego las columnas (la FK cae con su columna)."""
    sql = _render_postgres("downgrade", f"{_REVISION}:{_DOWN_REVISION}", monkeypatch)

    assert f"DROP INDEX {_NOMBRE_INDICE};" in sql
    for columna in _COLUMNAS_NUEVAS:
        assert f"ALTER TABLE clasificacion_log DROP COLUMN {columna};" in sql
    assert sql.index(f"DROP INDEX {_NOMBRE_INDICE};") < sql.index(
        "ALTER TABLE clasificacion_log DROP COLUMN validado_por_empleado_id;"
    )
    assert "DROP TABLE" not in sql
    assert "DELETE FROM" not in sql


# -- PostgreSQL real: FK ON DELETE SET NULL (marker integration) ---------------
#
# Se ejerce sobre el esquema que crea `Base.metadata.create_all` en `pg_schema`
# (decision del checkpoint 2.1, seccion 8): prueba que la FK DEL MODELO se comporta
# como `SET NULL` en el motor de produccion. La FK de la MIGRACION se cubre con el
# render del DDL de arriba (mismo `ondelete`) y con el `PRAGMA foreign_key_list` de
# SQLite. Corre solo con `pytest -m integration` (necesita PostgreSQL alcanzable).


@pytest.mark.integration
@pytest.mark.asyncio
async def test_fk_del_actor_pasa_a_null_al_borrar_el_empleado_en_postgresql(
    pg_session, seed_pg_catalogs
):
    """Al purgar al empleado (DIR-007) el log conserva la intervencion y pierde solo el actor."""
    from datetime import datetime, timezone

    from sqlalchemy import delete, select

    from app.models.clasificacion_log import ClasificacionLog
    from app.models.empleado import Empleado, RolEmpleado
    from app.models.incidente import Incidente, PrioridadEnum

    cat = seed_pg_catalogs
    empleado = Empleado(
        legajo="C165-PG-FK",
        nombre="Actor Integracion C165",
        email="c165.pg.fk@example.test",
        rol=RolEmpleado.mesa_de_ayuda,
    )
    pg_session.add(empleado)
    await pg_session.flush()

    incidente = Incidente(
        descripcion_original="caso integracion c165",
        descripcion_pseudonimizada="caso integracion c165",
        prioridad=PrioridadEnum.media,
        estado_id=cat["estado_nuevo"].id,
        sector_id=cat["sector_sistemas"].id,
    )
    pg_session.add(incidente)
    await pg_session.flush()

    log = ClasificacionLog(
        incidente_id=incidente.id,
        sector_id_predicho=cat["sector_sistemas"].id,
        confianza=0.55,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw="{}",
        sector_id_validado=cat["sector_sistemas"].id,
        validado_por_empleado_id=empleado.id,
        intervencion_inicio_en=datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc),
        validado_en=datetime(2026, 10, 30, 12, 0, 30, tzinfo=timezone.utc),
        origen_intervencion="gate",
    )
    pg_session.add(log)
    await pg_session.flush()
    log_id = log.id

    # DELETE Core (no ORM): el motor, y no el unit of work, aplica la FK.
    await pg_session.execute(delete(Empleado).where(Empleado.id == empleado.id))
    await pg_session.flush()

    fila = (
        await pg_session.execute(
            select(
                ClasificacionLog.validado_por_empleado_id,
                ClasificacionLog.validado_en,
                ClasificacionLog.origen_intervencion,
                ClasificacionLog.sector_id_validado,
            ).where(ClasificacionLog.id == log_id)
        )
    ).one()
    assert fila.validado_por_empleado_id is None
    assert fila.validado_en is not None
    assert fila.origen_intervencion == "gate"
    assert fila.sector_id_validado == cat["sector_sistemas"].id
