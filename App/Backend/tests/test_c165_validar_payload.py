"""
Tests del payload de validacion humana (c-165, ASG-005; tarea 2.4).

`ClasificacionValidar` acepta SOLO `intervencion_inicio_en` (opcional, con zona) como
dato de la intervencion. El ORIGEN lo deriva el backend: un payload que trae la clave
`origen_intervencion`, con cualquier valor, se rechaza con 422 sin reflejar el valor
sometido y sin modificar el log. El schema NO pasa a `extra="forbid"`: los demas campos
desconocidos se tratan igual que antes (se ignoran).
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from pydantic import ValidationError

from app.schemas.clasificacion import ClasificacionValidar
from tests.c165_support import (
    crear_log,
    leer_incidente,
    leer_log,
    limpiar_entorno,
    sembrar_entorno,
)

# -- Schema -------------------------------------------------------------------


def test_payload_acepta_el_inicio_con_zona_y_lo_conserva_como_instante():
    payload = ClasificacionValidar(
        sector_validado="Sistemas", intervencion_inicio_en="2026-10-30T12:00:00-03:00"
    )

    assert payload.intervencion_inicio_en == datetime(2026, 10, 30, 15, 0, tzinfo=timezone.utc)
    assert payload.intervencion_inicio_en.utcoffset() == timedelta(hours=-3)


def test_payload_acepta_el_inicio_en_utc_con_z():
    payload = ClasificacionValidar(
        sector_validado="Sistemas", intervencion_inicio_en="2026-10-30T15:00:00Z"
    )

    assert payload.intervencion_inicio_en == datetime(2026, 10, 30, 15, 0, tzinfo=timezone.utc)


def test_payload_sin_inicio_sigue_siendo_valido():
    payload = ClasificacionValidar(sector_validado="Sistemas")

    assert payload.intervencion_inicio_en is None


@pytest.mark.parametrize(
    "instante", ["2026-10-30T12:00:00", "2026-10-30 12:00:00.123456"]
)
def test_payload_rechaza_un_inicio_sin_zona(instante):
    with pytest.raises(ValidationError) as exc:
        ClasificacionValidar(sector_validado="Sistemas", intervencion_inicio_en=instante)

    errores = exc.value.errors()
    assert [e["loc"] for e in errores] == [("intervencion_inicio_en",)]
    assert errores[0]["type"] == "timezone_aware"


@pytest.mark.parametrize("valor", ["gate", "muestreo", "rederivacion", "review", "", None, 7])
def test_payload_rechaza_la_clave_origen_intervencion_con_cualquier_valor(valor):
    with pytest.raises(ValidationError) as exc:
        ClasificacionValidar.model_validate(
            {"sector_validado": "Sistemas", "origen_intervencion": valor}
        )

    errores = exc.value.errors()
    assert len(errores) == 1
    mensaje = errores[0]["msg"]
    assert "origen_intervencion" in mensaje
    # El mensaje es generico: nombra el campo, no refleja el valor sometido.
    if valor not in ("", None):
        assert str(valor) not in mensaje
        assert str(valor) not in repr(errores[0].get("ctx", {}))


def test_payload_sigue_tratando_igual_a_los_campos_desconocidos():
    """No hay `extra="forbid"`: un campo ajeno se ignora como antes de c-165."""
    payload = ClasificacionValidar.model_validate(
        {"sector_validado": "Sistemas", "campo_ajeno": "valor"}
    )

    assert payload.sector_validado == "Sistemas"
    assert not hasattr(payload, "campo_ajeno")
    assert ClasificacionValidar.model_config.get("extra") != "forbid"


# -- API ----------------------------------------------------------------------


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


async def _log_pendiente(engine, ent):
    return await crear_log(engine, ent, predicho="Sistemas", requiere_revision=True)


async def _assert_log_sin_modificar(engine, ids):
    log = await leer_log(engine, ids["log_id"])
    assert log.sector_id_validado is None
    assert log.validado_en is None
    assert log.origen_intervencion is None
    assert log.validado_por_empleado_id is None
    assert log.intervencion_inicio_en is None
    assert list(log.sectores_validados) == []
    assert (await leer_incidente(engine, ids["incidente_id"])).requiere_revision_humana is True


@pytest.mark.asyncio
@pytest.mark.parametrize("valor", ["gate", "review"])
async def test_validar_con_origen_enviado_responde_422_sin_reflejar_el_valor(
    client, engine, entorno, valor
):
    ids = await _log_pendiente(engine, entorno)

    resp = await client.patch(
        f"/api/v1/clasificaciones/{ids['log_id']}/validar",
        json={"sector_validado": "Sistemas", "origen_intervencion": valor},
    )

    assert resp.status_code == 422, resp.text
    assert resp.json()["error"]["code"] == "VALIDATION_ERROR"
    assert valor not in resp.text, "el 422 no debe reflejar el valor sometido"
    assert "origen_intervencion" in resp.text, "el 422 debe identificar el campo"
    await _assert_log_sin_modificar(engine, ids)


@pytest.mark.asyncio
async def test_validar_con_inicio_sin_zona_responde_422_y_no_modifica_el_log(
    client, engine, entorno
):
    ids = await _log_pendiente(engine, entorno)

    resp = await client.patch(
        f"/api/v1/clasificaciones/{ids['log_id']}/validar",
        json={"sector_validado": "Sistemas", "intervencion_inicio_en": "2026-10-30T12:00:00"},
    )

    assert resp.status_code == 422, resp.text
    assert "intervencion_inicio_en" in resp.text
    assert "2026-10-30T12:00:00" not in resp.text
    await _assert_log_sin_modificar(engine, ids)


@pytest.mark.asyncio
async def test_validar_sin_intervencion_inicio_en_sigue_respondiendo_200(client, engine, entorno):
    ids = await _log_pendiente(engine, entorno)

    resp = await client.patch(
        f"/api/v1/clasificaciones/{ids['log_id']}/validar",
        json={"sector_validado": "Sistemas"},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["sector_validado"]["nombre"] == "Sistemas"


@pytest.mark.asyncio
async def test_validar_con_un_campo_desconocido_se_trata_igual_que_antes(client, engine, entorno):
    ids = await _log_pendiente(engine, entorno)

    resp = await client.patch(
        f"/api/v1/clasificaciones/{ids['log_id']}/validar",
        json={"sector_validado": "Sistemas", "campo_ajeno": "valor"},
    )

    assert resp.status_code == 200, resp.text
