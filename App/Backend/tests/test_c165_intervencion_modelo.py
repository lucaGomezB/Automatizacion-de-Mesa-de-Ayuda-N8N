"""
Tests del modelo y del schema de lectura de la intervencion humana (c-165, ASG-005).

Cubren la tarea 2.3:
    - `ClasificacionLog` declara las cuatro columnas nuevas, nullable, con la FK
      nombrada `fk_clasificacion_log_validado_por_directorio_empleado` (`ON DELETE
      SET NULL`) y el indice del actor.
    - Un log recien creado queda `no_intervenido`: las cuatro columnas en NULL, tanto
      en la base como en la lectura HTTP.
    - `ClasificacionLogRead` expone SOLO el id del actor (nunca datos del empleado) y
      el origen se tipa con el vocabulario cerrado de `app.constants`.
    - La FK del actor se anula (`SET NULL`) al borrar al empleado: la purga por
      retencion del directorio (DIR-007) no toca el log.

Aislamiento: el motor SQLite de la suite tiene `PRAGMA foreign_keys=ON`, de modo que
`ON DELETE SET NULL` se ejerce de verdad. El gemelo PostgreSQL de este ultimo test
vive en `tests/test_migration_024_clasificacion_log_intervencion.py` (marker
`integration`).
"""

from datetime import datetime, timezone
from types import SimpleNamespace
from typing import get_args

import pytest
import pytest_asyncio
from sqlalchemy import DateTime, Integer, String, delete, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.catalog import Estado, Sector
from app.models.clasificacion_log import ClasificacionLog
from app.models.empleado import Empleado, RolEmpleado
from app.models.incidente import Incidente, PrioridadEnum
from app.schemas.clasificacion import ClasificacionLogRead, ClasificacionResult

CAMPOS_INTERVENCION = (
    "validado_por_empleado_id",
    "intervencion_inicio_en",
    "validado_en",
    "origen_intervencion",
)
DESCRIPCION = "Servidor de base de datos principal no responde desde las 08:00."


def _result_pendiente() -> ClasificacionResult:
    return ClasificacionResult(
        sector_predicho="Sistemas",
        confianza=0.55,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw='{"categoria": "Sistemas", "confianza": 0.55}',
    )


# -- Modelo ORM ---------------------------------------------------------------


def test_modelo_declara_las_cuatro_columnas_nullable_con_su_tipo():
    """Las cuatro columnas existen, son nullable y de los tipos aprobados en el checkpoint."""
    tabla = ClasificacionLog.__table__
    for nombre in CAMPOS_INTERVENCION:
        assert nombre in tabla.columns, f"falta la columna {nombre}"
        assert tabla.columns[nombre].nullable is True
        assert tabla.columns[nombre].default is None
        assert tabla.columns[nombre].server_default is None

    assert isinstance(tabla.columns["validado_por_empleado_id"].type, Integer)
    for nombre in ("intervencion_inicio_en", "validado_en"):
        tipo = tabla.columns[nombre].type
        assert isinstance(tipo, DateTime)
        assert tipo.timezone is True
    origen = tabla.columns["origen_intervencion"].type
    assert isinstance(origen, String)
    assert origen.length == 20
    # Sin CHECK: el vocabulario se valida en la capa de aplicacion.
    assert not [c for c in tabla.constraints if c.__class__.__name__ == "CheckConstraint"]


def test_modelo_actor_es_fk_nombrada_set_null_hacia_el_directorio_e_indexada():
    """La FK del actor es nombrada, apunta a directorio_empleado.id con SET NULL y esta indexada."""
    tabla = ClasificacionLog.__table__
    columna = tabla.columns["validado_por_empleado_id"]

    fks = list(columna.foreign_keys)
    assert len(fks) == 1
    fk = fks[0]
    assert fk.column.table.name == "directorio_empleado"
    assert fk.column.name == "id"
    assert (fk.ondelete or "").upper() == "SET NULL"
    assert fk.constraint.name == "fk_clasificacion_log_validado_por_directorio_empleado"

    indices = {i.name: i for i in tabla.indexes}
    assert "ix_clasificacion_log_validado_por_empleado_id" in indices
    assert [c.name for c in indices["ix_clasificacion_log_validado_por_empleado_id"].columns] == [
        "validado_por_empleado_id"
    ]


def test_modelo_y_migracion_declaran_el_mismo_conjunto_de_columnas(tmp_path, monkeypatch):
    """Deriva de esquema: el modelo y `alembic upgrade head` producen las mismas columnas."""
    from pathlib import Path

    from alembic import command as alembic_cmd
    from alembic.config import Config
    from sqlalchemy import create_engine, text

    from app.config.settings import get_settings

    backend = Path(__file__).resolve().parent.parent
    db_path = tmp_path / "deriva_modelo_migracion.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    monkeypatch.setenv("PSEUDONYMIZATION_ENCRYPTION_KEY", "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ=")
    monkeypatch.setenv("JWT_SECRET_KEY", "test-jwt-secret")
    monkeypatch.setenv("DIRECTORY_BLIND_INDEX_KEY", "clave-de-indice-ciego-de-migracion")
    get_settings.cache_clear()
    try:
        cfg = Config(str(backend / "alembic.ini"))
        cfg.set_main_option("script_location", str(backend / "alembic"))
        cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
        alembic_cmd.upgrade(cfg, "head")
    finally:
        get_settings.cache_clear()

    engine = create_engine(f"sqlite:///{db_path}")
    try:
        with engine.connect() as conn:
            migradas = {r[1] for r in conn.execute(text("PRAGMA table_info(clasificacion_log)"))}
    finally:
        engine.dispose()

    assert migradas == set(ClasificacionLog.__table__.columns.keys())


# -- Schema de lectura --------------------------------------------------------


def _log_leido(**extra) -> SimpleNamespace:
    base = dict(
        id=1,
        incidente_id=2,
        confianza=0.55,
        etapa="gemini",
        requiere_revision_humana=True,
        respuesta_raw=None,
        created_at=datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc),
        sector_predicho=None,
        sector_validado=None,
        sectores_predichos=[],
        sectores_validados=[],
        validado_por_empleado_id=None,
        intervencion_inicio_en=None,
        validado_en=None,
        origen_intervencion=None,
    )
    base.update(extra)
    return SimpleNamespace(**base)


def test_lectura_expone_los_campos_de_intervencion_con_valores():
    """Un log intervenido se serializa con actor (solo id), inicio, instante y origen."""
    inicio = datetime(2026, 10, 30, 12, 0, 5, tzinfo=timezone.utc)
    validado = datetime(2026, 10, 30, 12, 0, 40, tzinfo=timezone.utc)

    leido = ClasificacionLogRead.model_validate(
        _log_leido(
            validado_por_empleado_id=7,
            intervencion_inicio_en=inicio,
            validado_en=validado,
            origen_intervencion="gate",
        )
    )

    assert leido.validado_por_empleado_id == 7
    assert leido.intervencion_inicio_en == inicio
    assert leido.validado_en == validado
    assert leido.origen_intervencion == "gate"


def test_lectura_de_un_log_no_intervenido_deja_los_cuatro_campos_en_none():
    """Triangulacion: sin intervencion, la lectura no inventa actor, inicio, instante ni origen."""
    leido = ClasificacionLogRead.model_validate(_log_leido())

    assert [getattr(leido, c) for c in CAMPOS_INTERVENCION] == [None, None, None, None]


def test_lectura_no_expone_datos_del_empleado_mas_alla_del_id():
    """El schema de lectura no tiene campos de nombre, email, telefono ni legajo del actor."""
    campos = set(ClasificacionLogRead.model_fields)
    assert set(CAMPOS_INTERVENCION) <= campos
    prohibidos = {"validado_por", "actor", "empleado", "nombre", "email", "telefono", "legajo"}
    assert prohibidos.isdisjoint(campos)


def test_origen_se_tipa_con_el_vocabulario_cerrado_de_constants():
    """`OrigenIntervencion` (schema) y `ORIGENES_INTERVENCION` (constants) no pueden divergir."""
    from app.constants import ORIGENES_INTERVENCION
    from app.schemas.clasificacion import OrigenIntervencion

    assert ORIGENES_INTERVENCION == ("gate", "muestreo", "rederivacion", "completado_manual")
    assert get_args(OrigenIntervencion) == ORIGENES_INTERVENCION


def test_lectura_rechaza_un_origen_fuera_del_vocabulario():
    """Un valor ajeno al vocabulario no se serializa en silencio."""
    with pytest.raises(ValueError):
        ClasificacionLogRead.model_validate(_log_leido(origen_intervencion="review"))


# -- Un log recien creado queda no_intervenido --------------------------------


@pytest.mark.asyncio
async def test_log_recien_creado_queda_no_intervenido_en_base_y_en_la_lectura(
    seed_catalogs, make_client_with_classifier, engine
):
    """Las cuatro columnas nacen en NULL: el alta de un incidente no inventa metadatos."""
    async with make_client_with_classifier(_result_pendiente()) as client:
        alta = await client.post(
            "/api/v1/incidentes/", json={"descripcion": DESCRIPCION, "prioridad": "media"}
        )
        assert alta.status_code == 201, alta.text
        incidente_id = alta.json()["id"]
        historial = (await client.get(f"/api/v1/clasificaciones/incidente/{incidente_id}")).json()

    assert len(historial) == 1
    for campo in CAMPOS_INTERVENCION:
        assert campo in historial[0], f"la lectura no expone {campo}"
        assert historial[0][campo] is None

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        log = (
            await session.scalars(
                select(ClasificacionLog).where(ClasificacionLog.incidente_id == incidente_id)
            )
        ).one()
    assert [getattr(log, c) for c in CAMPOS_INTERVENCION] == [None, None, None, None]
    assert log.sector_id_validado is None


# -- FK del actor: SET NULL al borrar al empleado -----------------------------


@pytest_asyncio.fixture
async def log_con_actor(engine):
    """Un log intervenido por un empleado del directorio (se limpia al terminar)."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        sector = Sector(nombre="Sistemas", descripcion="A")
        estado = Estado(nombre="nuevo", descripcion="n", es_terminal=False)
        s.add_all([sector, estado])
        await s.flush()
        empleado = Empleado(
            legajo="C165-MOD",
            nombre="Actor C165",
            email="c165.modelo@example.test",
            rol=RolEmpleado.mesa_de_ayuda,
        )
        s.add(empleado)
        await s.flush()
        incidente = Incidente(
            descripcion_original="caso c165",
            descripcion_pseudonimizada="caso c165",
            estado_id=estado.id,
            sector_id=sector.id,
            prioridad=PrioridadEnum.media,
        )
        s.add(incidente)
        await s.flush()
        log = ClasificacionLog(
            incidente_id=incidente.id,
            sector_id_predicho=sector.id,
            confianza=0.55,
            etapa="gemini",
            requiere_revision_humana=True,
            respuesta_raw="{}",
            sector_id_validado=sector.id,
            validado_por_empleado_id=empleado.id,
            intervencion_inicio_en=datetime(2026, 10, 30, 12, 0, 0, tzinfo=timezone.utc),
            validado_en=datetime(2026, 10, 30, 12, 0, 30, tzinfo=timezone.utc),
            origen_intervencion="gate",
        )
        s.add(log)
        await s.commit()
        ids = {"log": log.id, "empleado": empleado.id}

    yield ids

    async with factory() as s:
        await s.execute(delete(ClasificacionLog))
        await s.execute(delete(Incidente))
        await s.execute(delete(Empleado))
        await s.execute(delete(Estado))
        await s.execute(delete(Sector))
        await s.commit()


@pytest.mark.asyncio
async def test_borrar_al_empleado_anula_el_actor_y_conserva_el_resto_de_la_intervencion(
    engine, log_con_actor
):
    """ON DELETE SET NULL: la purga del directorio deja el actor en NULL sin tocar el log."""
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        await s.execute(delete(Empleado).where(Empleado.id == log_con_actor["empleado"]))
        await s.commit()

    async with factory() as s:
        fila = (
            await s.execute(
                select(
                    ClasificacionLog.validado_por_empleado_id,
                    ClasificacionLog.validado_en,
                    ClasificacionLog.origen_intervencion,
                    ClasificacionLog.sector_id_validado,
                ).where(ClasificacionLog.id == log_con_actor["log"])
            )
        ).one()

    assert fila.validado_por_empleado_id is None
    assert fila.validado_en is not None
    assert fila.origen_intervencion == "gate"
    assert fila.sector_id_validado is not None


@pytest.mark.asyncio
async def test_el_actor_debe_existir_en_el_directorio_cuando_se_informa(engine, log_con_actor):
    """Triangulacion: la FK rechaza un actor inexistente (no se registran ids huerfanos)."""
    from sqlalchemy.exc import IntegrityError

    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        log = await s.get(ClasificacionLog, log_con_actor["log"])
        log.validado_por_empleado_id = 987654
        with pytest.raises(IntegrityError):
            await s.flush()
        await s.rollback()
