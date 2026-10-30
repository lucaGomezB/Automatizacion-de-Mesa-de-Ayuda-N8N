"""
Tests de la metrica backend `tasa_intervencion_backend` (c-165, ECM-003; tareas 3.1 y 3.2).

Cohorte: logs de clasificacion con `created_at` en `[desde, hasta)` (limite superior
EXCLUSIVO). Numerador: logs de la cohorte con `validado_en` no nulo. Denominador: los
logs de la cohorte, EXCLUIDOS los legados (`intervencion_legada_sin_metadatos`), cuya
cantidad se declara. Una confirmacion sin cambio de sector CUENTA; un log marcado para
revision que nadie valido NO cuenta.

Capa repositorio (`contar_intervenciones`) y capa servicio (`get_resumen`).
"""

from datetime import date, datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.constants import ORIGENES_INTERVENCION
from app.repositories.estadisticas_repository import (
    ConteoIntervenciones,
    EstadisticasRepository,
)
from app.services.estadisticas_service import EstadisticasService
from tests.c165_support import crear_log, limpiar_entorno, sembrar_entorno

DESDE = datetime(2026, 10, 1, 0, 0, tzinfo=timezone.utc)
HASTA = datetime(2026, 11, 1, 0, 0, tzinfo=timezone.utc)
DENTRO = datetime(2026, 10, 15, 12, 0, tzinfo=timezone.utc)
VALIDADO = datetime(2026, 10, 15, 12, 5, tzinfo=timezone.utc)


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


async def _intervenido(engine, ent, origen, *, predicho="Sistemas", validado="Sistemas",
                       created_at=DENTRO):
    return await crear_log(
        engine, ent, predicho=predicho, validado=validado, created_at=created_at,
        validado_en=VALIDADO, origen_intervencion=origen,
    )


async def _sembrar_cohorte(engine, ent) -> None:
    """Cohorte del rango: 4 intervenidos, 1 marcado sin validar, 1 legado; mas 2 fuera."""
    await _intervenido(engine, ent, "gate")                                    # confirmacion
    await _intervenido(engine, ent, "gate", created_at=DESDE)                  # limite inferior
    await _intervenido(engine, ent, "muestreo", validado="Bases de Datos")     # correccion
    await _intervenido(engine, ent, "rederivacion", validado="Bases de Datos") # correccion
    await crear_log(engine, ent, requiere_revision=True, created_at=DENTRO)    # no intervenido
    await crear_log(engine, ent, validado="Sistemas", created_at=DENTRO)       # legado
    await _intervenido(engine, ent, "gate", created_at=datetime(2026, 9, 30, 23, 59, tzinfo=timezone.utc))
    await _intervenido(engine, ent, "gate", created_at=HASTA)                  # limite superior


# -- 3.1: repositorio ------------------------------------------------------------


@pytest.mark.asyncio
async def test_contar_intervenciones_cuenta_la_cohorte_por_created_at(engine, entorno):
    await _sembrar_cohorte(engine, entorno)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        conteo = await EstadisticasRepository(s).contar_intervenciones(DESDE, HASTA)

    assert isinstance(conteo, ConteoIntervenciones)
    # Cohorte: 4 intervenidos + 1 no intervenido + 1 legado. Los de 30-09 y de HASTA quedan fuera
    # (inferior inclusivo, superior exclusivo).
    assert conteo.total_cohorte == 6
    assert conteo.legados == 1
    assert conteo.intervenidos == 4
    assert conteo.por_origen == {
        "gate": 2, "muestreo": 1, "rederivacion": 1, "completado_manual": 0,
    }
    assert conteo.por_cambio_sector == {"true": 2, "false": 2}


@pytest.mark.asyncio
async def test_contar_intervenciones_informa_las_cuatro_claves_del_vocabulario_en_cero(
    engine, entorno
):
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        conteo = await EstadisticasRepository(s).contar_intervenciones(DESDE, HASTA)

    assert conteo.total_cohorte == 0
    assert conteo.intervenidos == 0
    assert conteo.legados == 0
    assert tuple(conteo.por_origen) == ORIGENES_INTERVENCION
    assert set(conteo.por_origen.values()) == {0}
    assert conteo.por_cambio_sector == {"true": 0, "false": 0}


@pytest.mark.asyncio
async def test_un_rango_sin_logs_no_arrastra_los_de_otro_rango(engine, entorno):
    await _sembrar_cohorte(engine, entorno)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        conteo = await EstadisticasRepository(s).contar_intervenciones(
            datetime(2026, 12, 1, tzinfo=timezone.utc), datetime(2026, 12, 31, tzinfo=timezone.utc)
        )

    assert (conteo.total_cohorte, conteo.intervenidos, conteo.legados) == (0, 0, 0)


@pytest.mark.asyncio
async def test_un_predicho_nulo_cuenta_como_cambio_de_sector(engine, entorno):
    await _intervenido(engine, entorno, "rederivacion", predicho=None, validado="Sistemas")
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        conteo = await EstadisticasRepository(s).contar_intervenciones(DESDE, HASTA)

    assert conteo.por_cambio_sector == {"true": 1, "false": 0}


# -- 3.2: servicio ------------------------------------------------------------------
#
# El servicio recibe DIAS de negocio (UTC-3): [2026-10-01 00:00 BA, 2026-11-01 00:00 BA).
# Los logs de estos tests se crean a mediodia UTC, lejos de los limites.


async def _resumen(engine) -> dict:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        return await EstadisticasService(s).get_resumen(
            desde=date(2026, 10, 1), hasta=date(2026, 10, 31)
        )


@pytest.mark.asyncio
async def test_la_tasa_es_intervenciones_sobre_la_cohorte_sin_legados(engine, entorno):
    await _sembrar_cohorte(engine, entorno)

    resumen = await _resumen(engine)

    # 4 intervenidos / (6 de la cohorte - 1 legado) = 0.8
    assert resumen["tasa_intervencion_backend"] == 0.8
    assert resumen["intervenciones_legadas_excluidas"] == 1
    assert resumen["intervenciones_por_origen"] == {
        "gate": 2, "muestreo": 1, "rederivacion": 1, "completado_manual": 0,
    }
    assert resumen["intervenciones_por_cambio_sector"] == {"true": 2, "false": 2}


@pytest.mark.asyncio
async def test_una_confirmacion_sin_cambio_de_sector_cuenta_como_intervencion(engine, entorno):
    await _intervenido(engine, entorno, "gate", predicho="Sistemas", validado="Sistemas")

    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 1.0
    assert resumen["intervenciones_por_cambio_sector"] == {"true": 0, "false": 1}


@pytest.mark.asyncio
async def test_un_marcado_sin_validar_no_cuenta_pero_si_esta_en_el_denominador(engine, entorno):
    await crear_log(engine, entorno, requiere_revision=True, created_at=DENTRO)
    await _intervenido(engine, entorno, "gate")

    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 0.5


@pytest.mark.asyncio
async def test_los_legados_no_entran_ni_al_numerador_ni_al_denominador_y_se_declaran(
    engine, entorno
):
    await crear_log(engine, entorno, validado="Sistemas", created_at=DENTRO)  # legado
    await _intervenido(engine, entorno, "muestreo")

    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 1.0
    assert resumen["intervenciones_legadas_excluidas"] == 1


@pytest.mark.asyncio
async def test_una_cohorte_solo_de_legados_da_tasa_cero_y_los_declara(engine, entorno):
    await crear_log(engine, entorno, validado="Sistemas", created_at=DENTRO)

    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 0.0
    assert resumen["intervenciones_legadas_excluidas"] == 1


@pytest.mark.asyncio
async def test_una_cohorte_vacia_da_tasa_cero(engine, entorno):
    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 0.0
    assert resumen["intervenciones_legadas_excluidas"] == 0
    assert resumen["intervenciones_por_origen"] == dict.fromkeys(ORIGENES_INTERVENCION, 0)


@pytest.mark.asyncio
async def test_la_metrica_es_reproducible_sobre_los_mismos_datos(engine, entorno):
    await _sembrar_cohorte(engine, entorno)

    primera = await _resumen(engine)
    segunda = await _resumen(engine)

    assert primera["tasa_intervencion_backend"] == 0.8
    assert primera == segunda


@pytest.mark.asyncio
async def test_el_resumen_conserva_tasa_revision_humana_junto_a_la_de_intervencion(
    engine, entorno
):
    """La metrica nueva se expone junto a (no en lugar de) `tasa_revision_humana`."""
    await crear_log(engine, entorno, requiere_revision=True, created_at=DENTRO)
    await _intervenido(engine, entorno, "gate", created_at=DENTRO)

    resumen = await _resumen(engine)

    assert resumen["tasa_intervencion_backend"] == 0.5
    assert "tasa_revision_humana" in resumen
