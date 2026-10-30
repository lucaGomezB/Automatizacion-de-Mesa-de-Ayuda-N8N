"""
Tests del escritor de `rederivacion` desde PATCH /incidentes/{id} (c-165, ASG-005; 2.8).

Cuando el PATCH trae un `sector_id` DISTINTO del actual, `IncidenteService.update_incidente`
registra la intervencion en el log MAS RECIENTE del incidente (el de mayor `id`):
`sector_id_validado`, `validado_en`, `origen_intervencion = rederivacion`, el actor (o
NULL) e inicio NULL. Un PATCH con el mismo sector o sin `sector_id` no registra nada, un
incidente sin log responde como siempre y `validate()` no dispara este escritor.

Decision del checkpoint 2.1 (opcion A, seccion 8): la rederivacion de un log pendiente
lo saca de la cola (`sector_id_validado` deja de ser NULL) mientras el flag
`requiere_revision_humana` del INCIDENTE queda como estaba. La divergencia se documenta
y se prueba aca (`test_la_rederivacion_de_un_log_pendiente_...`).
"""

from datetime import datetime, timezone

import pytest
import pytest_asyncio
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.models.clasificacion_log import ClasificacionLog
from tests.c165_support import (
    como_utc,
    cliente_con_cuenta,
    crear_log,
    leer_incidente,
    leer_log,
    limpiar_entorno,
    sembrar_entorno,
)


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


def _patch_url(incidente_id: int) -> str:
    return f"/api/v1/incidentes/{incidente_id}"


def _sin_metadatos(log) -> bool:
    return (
        log.validado_en is None
        and log.origen_intervencion is None
        and log.validado_por_empleado_id is None
        and log.intervencion_inicio_en is None
    )


@pytest.mark.asyncio
async def test_el_cambio_de_sector_registra_la_rederivacion_con_el_empleado_actor(engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)
    antes = datetime.now(timezone.utc)

    async with cliente_con_cuenta(engine, entorno.user_actor_id) as c:
        resp = await c.patch(
            _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
        )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.sector_id_validado == entorno.sector["Bases de Datos"]
    assert log.origen_intervencion == "rederivacion"
    assert log.validado_por_empleado_id == entorno.empleado_actor_id
    assert log.intervencion_inicio_en is None
    assert como_utc(log.validado_en) >= antes.replace(microsecond=0)
    # El log conserva la prediccion original y su flag: solo se agrega la intervencion.
    assert log.sector_id_predicho == entorno.sector["Sistemas"]
    assert log.requiere_revision_humana is True
    incidente = await leer_incidente(engine, ids["incidente_id"])
    assert incidente.sector_id == entorno.sector["Bases de Datos"]


@pytest.mark.asyncio
async def test_la_cuenta_sin_empleado_rederiva_con_actor_nulo(client, engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas")

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "rederivacion"
    assert log.validado_por_empleado_id is None
    assert log.validado_en is not None


@pytest.mark.asyncio
async def test_un_patch_con_el_mismo_sector_no_registra_intervencion(client, engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas")

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Sistemas"]}
    )

    assert resp.status_code == 200, resp.text
    assert _sin_metadatos(await leer_log(engine, ids["log_id"]))
    assert (await leer_log(engine, ids["log_id"])).sector_id_validado is None


@pytest.mark.asyncio
async def test_un_patch_sin_sector_id_no_registra_intervencion(client, engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas")

    resp = await client.patch(_patch_url(ids["incidente_id"]), json={"prioridad": "alta"})

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert _sin_metadatos(log)
    assert log.sector_id_validado is None


@pytest.mark.asyncio
async def test_un_incidente_sin_log_responde_como_siempre_y_no_crea_ninguno(
    client, engine, entorno
):
    ids = await crear_log(engine, entorno, predicho="Sistemas")
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        await s.delete(await s.get(ClasificacionLog, ids["log_id"]))
        await s.commit()

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["sector"]["id"] == entorno.sector["Bases de Datos"]
    async with factory() as s:
        total = await s.scalar(
            select(func.count()).select_from(ClasificacionLog).where(
                ClasificacionLog.incidente_id == ids["incidente_id"]
            )
        )
    assert total == 0


@pytest.mark.asyncio
async def test_la_rederivacion_se_registra_en_el_log_de_mayor_id_aunque_no_sea_el_mas_reciente_por_fecha(
    client, engine, entorno
):
    """El log destino es el de mayor `id` (no el de `created_at` mayor)."""
    primero = await crear_log(
        engine, entorno, predicho="Sistemas",
        created_at=datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc),
    )
    # Un segundo log del MISMO incidente: id mayor, pero created_at anterior.
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        segundo = ClasificacionLog(
            incidente_id=primero["incidente_id"],
            sector_id_predicho=entorno.sector["Sistemas"],
            confianza=0.55,
            etapa="gemini",
            requiere_revision_humana=True,
            respuesta_raw="{}",
            created_at=datetime(2026, 10, 1, 12, 0, tzinfo=timezone.utc),
        )
        s.add(segundo)
        await s.commit()
        segundo_id = segundo.id
    assert segundo_id > primero["log_id"]

    resp = await client.patch(
        _patch_url(primero["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    assert (await leer_log(engine, segundo_id)).origen_intervencion == "rederivacion"
    assert _sin_metadatos(await leer_log(engine, primero["log_id"]))


@pytest.mark.asyncio
async def test_validar_no_dispara_el_escritor_de_rederivacion(client, engine, entorno):
    """`validate()` propaga el sector al incidente por el repositorio, no por el servicio."""
    ids = await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)

    resp = await client.patch(
        f"/api/v1/clasificaciones/{ids['log_id']}/validar",
        json={"sector_validado": "Bases de Datos"},
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "gate"
    incidente = await leer_incidente(engine, ids["incidente_id"])
    assert incidente.sector_id == entorno.sector["Bases de Datos"]


@pytest.mark.asyncio
async def test_rederivar_un_log_ya_validado_pisa_la_intervencion_anterior(client, engine, entorno):
    """Gana la ultima escritura: el origen `gate` previo deja de estar registrado."""
    ids = await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)
    async with cliente_con_cuenta(engine, entorno.user_actor_id) as con_empleado:
        await con_empleado.patch(
            f"/api/v1/clasificaciones/{ids['log_id']}/validar",
            json={
                "sector_validado": "Sistemas",
                "intervencion_inicio_en": "2026-10-30T15:00:00Z",
            },
        )
    assert (await leer_log(engine, ids["log_id"])).origen_intervencion == "gate"

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "rederivacion"
    assert log.validado_por_empleado_id is None  # la cuenta de `client` no tiene empleado
    assert log.intervencion_inicio_en is None
    assert log.sector_id_validado == entorno.sector["Bases de Datos"]


@pytest.mark.asyncio
async def test_la_rederivacion_no_vacia_los_adicionales_y_retira_solo_el_nuevo_principal(
    client, engine, entorno
):
    ids = await crear_log(
        engine, entorno, predicho="Sistemas", validado="Sistemas",
        adicionales_validados=("Bases de Datos", "Soporte Tecnico Software"),
        validado_en=datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc),
        origen_intervencion="gate",
    )

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    # El nuevo principal ya no puede figurar entre los adicionales; el resto se conserva.
    assert [s.nombre for s in log.sectores_validados] == ["Soporte Tecnico Software"]


@pytest.mark.asyncio
async def test_la_rederivacion_conserva_los_adicionales_si_el_principal_no_figura_entre_ellos(
    client, engine, entorno
):
    ids = await crear_log(
        engine, entorno, predicho="Sistemas", validado="Sistemas",
        adicionales_validados=("Soporte Tecnico Software",),
        validado_en=datetime(2026, 10, 30, 12, 0, tzinfo=timezone.utc),
        origen_intervencion="muestreo",
    )

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "rederivacion"
    assert [s.nombre for s in log.sectores_validados] == ["Soporte Tecnico Software"]


@pytest.mark.asyncio
async def test_un_incidente_cerrado_responde_409_y_no_registra_nada(client, engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas", cerrado=True)

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )

    assert resp.status_code == 409, resp.text
    assert _sin_metadatos(await leer_log(engine, ids["log_id"]))


@pytest.mark.asyncio
async def test_un_sector_inexistente_responde_404_y_no_registra_nada(client, engine, entorno):
    ids = await crear_log(engine, entorno, predicho="Sistemas")

    resp = await client.patch(_patch_url(ids["incidente_id"]), json={"sector_id": 987654})

    assert resp.status_code == 404, resp.text
    assert _sin_metadatos(await leer_log(engine, ids["log_id"]))


@pytest.mark.asyncio
async def test_la_rederivacion_de_un_log_pendiente_lo_saca_de_la_cola_pero_no_limpia_el_flag_del_incidente(
    client, engine, entorno
):
    """Divergencia declarada (checkpoint 2.1, opcion A): cola por log vs. flag por incidente."""
    ids = await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)

    antes = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
    assert ids["log_id"] in [item["id"] for item in antes]

    resp = await client.patch(
        _patch_url(ids["incidente_id"]), json={"sector_id": entorno.sector["Bases de Datos"]}
    )
    assert resp.status_code == 200, resp.text

    despues = (await client.get("/api/v1/clasificaciones/revision-pendiente")).json()
    assert ids["log_id"] not in [item["id"] for item in despues]
    assert (await client.get("/api/v1/clasificaciones/revision-pendiente/count")).json() == {
        "total": 0
    }
    # El flag del incidente sigue en True: el mismo PATCH no lo limpia.
    assert (await leer_incidente(engine, ids["incidente_id"])).requiere_revision_humana is True


@pytest.mark.asyncio
async def test_el_mismo_patch_puede_limpiar_el_flag_del_incidente_y_rederivar(
    client, engine, entorno
):
    ids = await crear_log(engine, entorno, predicho="Sistemas", requiere_revision=True)

    resp = await client.patch(
        _patch_url(ids["incidente_id"]),
        json={"sector_id": entorno.sector["Bases de Datos"], "requiere_revision_humana": False},
    )

    assert resp.status_code == 200, resp.text
    assert (await leer_incidente(engine, ids["incidente_id"])).requiere_revision_humana is False
    assert (await leer_log(engine, ids["log_id"])).origen_intervencion == "rederivacion"
