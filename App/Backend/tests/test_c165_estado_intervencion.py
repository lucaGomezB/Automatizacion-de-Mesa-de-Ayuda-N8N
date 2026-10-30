"""
Tests del estado de la intervencion de un log (c-165, ASG-005 y ECM-003; tarea 2.9).

Tres estados derivados, sin columna propia ni backfill:
    - `no_intervenido`: sin `validado_en` ni `sector_id_validado`.
    - `intervenido`: con `validado_en`.
    - `intervencion_legada_sin_metadatos`: con `sector_id_validado` y sin `validado_en`
      (validado antes de la migracion 024; no se le inventa instante ni origen).

La funcion pura de Python (export) y los predicados SQL (metrica) deben coincidir:
se prueban fila por fila contra la base.
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.clasificacion_log import ClasificacionLog
from app.services.intervencion_estado import (
    ESTADO_INTERVENIDO,
    ESTADO_LEGADO,
    ESTADO_NO_INTERVENIDO,
    condicion_cambio_de_sector,
    condicion_intervenido,
    condicion_legado,
    condicion_no_intervenido,
    estado_intervencion,
    hubo_cambio_de_sector,
)
from tests.c165_support import crear_log, limpiar_entorno, sembrar_entorno

AHORA = datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "validado_en, sector_id_validado, esperado",
    [
        (None, None, ESTADO_NO_INTERVENIDO),
        (None, 3, ESTADO_LEGADO),
        (AHORA, 3, ESTADO_INTERVENIDO),
        # El sector validado se puede anular si el sector se borra (SET NULL): sigue intervenido.
        (AHORA, None, ESTADO_INTERVENIDO),
    ],
)
def test_estado_intervencion_clasifica_las_cuatro_combinaciones(
    validado_en, sector_id_validado, esperado
):
    assert (
        estado_intervencion(validado_en=validado_en, sector_id_validado=sector_id_validado)
        == esperado
    )


def test_los_nombres_de_los_estados_son_los_de_la_especificacion():
    assert ESTADO_NO_INTERVENIDO == "no_intervenido"
    assert ESTADO_INTERVENIDO == "intervenido"
    assert ESTADO_LEGADO == "intervencion_legada_sin_metadatos"


@pytest.mark.parametrize(
    "predicho, validado, esperado",
    [(3, 3, False), (3, 4, True), (None, 3, True), (3, None, True), (None, None, False)],
)
def test_hubo_cambio_de_sector_un_predicho_nulo_cuenta_como_cambio(predicho, validado, esperado):
    assert hubo_cambio_de_sector(predicho, validado) is esperado


# -- Python y SQL coinciden -----------------------------------------------------


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


async def _sembrar_combinaciones(engine, ent) -> dict[str, int]:
    """Un log por combinacion relevante; devuelve nombre -> log_id."""
    ids = {}
    ids["no_intervenido"] = (await crear_log(engine, ent, predicho="Sistemas"))["log_id"]
    ids["legado"] = (
        await crear_log(engine, ent, predicho="Sistemas", validado="Bases de Datos")
    )["log_id"]
    ids["confirmado"] = (
        await crear_log(
            engine, ent, predicho="Sistemas", validado="Sistemas",
            validado_en=AHORA, origen_intervencion="gate",
        )
    )["log_id"]
    ids["corregido"] = (
        await crear_log(
            engine, ent, predicho="Sistemas", validado="Bases de Datos",
            validado_en=AHORA, origen_intervencion="muestreo",
        )
    )["log_id"]
    ids["predicho_nulo"] = (
        await crear_log(
            engine, ent, predicho=None, validado="Sistemas",
            validado_en=AHORA, origen_intervencion="rederivacion",
        )
    )["log_id"]
    return ids


@pytest.mark.asyncio
async def test_los_predicados_sql_coinciden_con_la_funcion_pura(engine, entorno):
    ids = await _sembrar_combinaciones(engine, entorno)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async def seleccionar(condicion) -> set[int]:
        async with factory() as s:
            return set((await s.scalars(select(ClasificacionLog.id).where(condicion))).all())

    assert await seleccionar(condicion_no_intervenido()) == {ids["no_intervenido"]}
    assert await seleccionar(condicion_legado()) == {ids["legado"]}
    assert await seleccionar(condicion_intervenido()) == {
        ids["confirmado"], ids["corregido"], ids["predicho_nulo"],
    }
    # La funcion pura clasifica cada fila igual que el predicado SQL que la selecciona.
    esperado_por_log = {
        ids["no_intervenido"]: ESTADO_NO_INTERVENIDO,
        ids["legado"]: ESTADO_LEGADO,
        ids["confirmado"]: ESTADO_INTERVENIDO,
        ids["corregido"]: ESTADO_INTERVENIDO,
        ids["predicho_nulo"]: ESTADO_INTERVENIDO,
    }
    async with factory() as s:
        logs = (await s.scalars(select(ClasificacionLog))).all()
    assert len(logs) == len(esperado_por_log)
    for log in logs:
        assert (
            estado_intervencion(
                validado_en=log.validado_en, sector_id_validado=log.sector_id_validado
            )
            == esperado_por_log[log.id]
        )


@pytest.mark.asyncio
async def test_el_cambio_de_sector_en_sql_coincide_con_la_funcion_pura(engine, entorno):
    ids = await _sembrar_combinaciones(engine, entorno)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        con_cambio_sql = set(
            (
                await s.scalars(
                    select(ClasificacionLog.id).where(
                        condicion_intervenido(), condicion_cambio_de_sector()
                    )
                )
            ).all()
        )
        intervenidos = (
            await s.scalars(select(ClasificacionLog).where(condicion_intervenido()))
        ).all()
    con_cambio_python = {
        log.id
        for log in intervenidos
        if hubo_cambio_de_sector(log.sector_id_predicho, log.sector_id_validado)
    }

    assert con_cambio_sql == con_cambio_python == {ids["corregido"], ids["predicho_nulo"]}
    assert ids["confirmado"] not in con_cambio_sql


# -- Un log legado no inventa metadatos -----------------------------------------


@pytest.mark.asyncio
async def test_un_log_legado_se_clasifica_como_tal_y_la_lectura_no_inventa_metadatos(
    client, engine, entorno
):
    ids = await crear_log(engine, entorno, predicho="Sistemas", validado="Bases de Datos")

    historial = (
        await client.get(f"/api/v1/clasificaciones/incidente/{ids['incidente_id']}")
    ).json()

    assert historial[0]["sector_validado"]["nombre"] == "Bases de Datos"
    assert historial[0]["validado_en"] is None
    assert historial[0]["origen_intervencion"] is None
    assert historial[0]["validado_por_empleado_id"] is None
    assert historial[0]["intervencion_inicio_en"] is None
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        log = await s.get(ClasificacionLog, ids["log_id"])
    assert (
        estado_intervencion(validado_en=log.validado_en, sector_id_validado=log.sector_id_validado)
        == ESTADO_LEGADO
    )
