"""
Tests de la intervencion humana registrada por la validacion (c-165, ASG-005).

Cubren las tareas 2.5, 2.6 y 2.7 sobre `PATCH /clasificaciones/{log_id}/validar`:
    - 2.5: el servicio persiste actor, inicio, `validado_en` (instante del SERVIDOR) y
      origen; el origen se deriva SIEMPRE del flag `requiere_revision_humana` del LOG
      (`gate` si esta marcado, `muestreo` si no); el inicio se normaliza a UTC.
    - 2.6: actor NULL con la cuenta sin empleado (fixture `client`, `User(id=1)`) y el
      id del empleado con una cuenta vinculada; sin PII en la respuesta.
    - 2.7: la ultima escritura gana (las cuatro columnas, `sector_id_validado` y
      `sectores_validados` como unidad), incluido el reemplazo por el conjunto VACIO.
"""

from datetime import datetime, timedelta, timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.core.exceptions import EntityNotFoundError
from app.services.clasificacion_service import ClasificacionService
from tests.c165_support import (
    como_utc,
    crear_log,
    desactivar_empleado,
    leer_log,
    cliente_con_cuenta,
    limpiar_entorno,
    sembrar_entorno,
)


@pytest_asyncio.fixture
async def entorno(engine):
    ent = await sembrar_entorno(engine)
    yield ent
    await limpiar_entorno(engine)


def _url(log_id: int) -> str:
    return f"/api/v1/clasificaciones/{log_id}/validar"


# -- 2.5: persistencia y derivacion del origen ---------------------------------


@pytest.mark.asyncio
async def test_log_marcado_para_revision_se_valida_con_origen_gate(client, engine, entorno):
    ids = await crear_log(engine, entorno, requiere_revision=True)
    antes = datetime.now(timezone.utc)

    resp = await client.patch(
        _url(ids["log_id"]),
        json={
            "sector_validado": "Sistemas",
            "intervencion_inicio_en": "2026-10-30T15:00:00Z",
        },
    )
    despues = datetime.now(timezone.utc)

    assert resp.status_code == 200, resp.text
    cuerpo = resp.json()
    assert cuerpo["origen_intervencion"] == "gate"
    assert como_utc(cuerpo["intervencion_inicio_en"]) == datetime(
        2026, 10, 30, 15, 0, tzinfo=timezone.utc
    )
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "gate"
    # `validado_en` es el instante del SERVIDOR: cae dentro de la ventana de la llamada
    # y es posterior a la creacion del log (no se confunde con `created_at`).
    validado_en = como_utc(log.validado_en)
    assert antes - timedelta(seconds=1) <= validado_en <= despues + timedelta(seconds=1)
    assert validado_en > como_utc(log.created_at)
    assert como_utc(cuerpo["validado_en"]) == validado_en


@pytest.mark.asyncio
async def test_log_no_marcado_se_valida_con_origen_muestreo(client, engine, entorno):
    ids = await crear_log(engine, entorno, requiere_revision=False)

    resp = await client.patch(_url(ids["log_id"]), json={"sector_validado": "Sistemas"})

    assert resp.status_code == 200, resp.text
    assert resp.json()["origen_intervencion"] == "muestreo"
    log = await leer_log(engine, ids["log_id"])
    assert log.origen_intervencion == "muestreo"
    assert log.validado_en is not None


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "log_marcado, incidente_marcado, esperado",
    [(True, False, "gate"), (False, True, "muestreo")],
)
async def test_el_origen_sale_del_flag_del_log_y_no_del_del_incidente(
    client, engine, entorno, log_marcado, incidente_marcado, esperado
):
    ids = await crear_log(
        engine,
        entorno,
        requiere_revision=log_marcado,
        incidente_requiere_revision=incidente_marcado,
    )

    resp = await client.patch(_url(ids["log_id"]), json={"sector_validado": "Sistemas"})

    assert resp.status_code == 200, resp.text
    assert (await leer_log(engine, ids["log_id"])).origen_intervencion == esperado


@pytest.mark.asyncio
async def test_el_inicio_con_otra_zona_se_persiste_normalizado_a_utc(client, engine, entorno):
    """SQLite descarta la zona: sin normalizar, 12:00-03:00 se guardaria como 12:00."""
    ids = await crear_log(engine, entorno)

    resp = await client.patch(
        _url(ids["log_id"]),
        json={
            "sector_validado": "Sistemas",
            "intervencion_inicio_en": "2026-10-30T12:00:00-03:00",
        },
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert como_utc(log.intervencion_inicio_en) == datetime(2026, 10, 30, 15, 0, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_validar_sin_inicio_registra_instante_y_origen_con_inicio_nulo(
    client, engine, entorno
):
    ids = await crear_log(engine, entorno)

    resp = await client.patch(_url(ids["log_id"]), json={"sector_validado": "Sistemas"})

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.intervencion_inicio_en is None
    assert log.validado_en is not None
    assert log.origen_intervencion == "gate"


@pytest.mark.asyncio
async def test_validate_del_servicio_acepta_la_llamada_posicional_previa(engine, entorno):
    """Los parametros nuevos son opcionales y por nombre: las llamadas viejas no se rompen."""
    ids = await crear_log(engine, entorno, requiere_revision=True)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as s:
        log = await ClasificacionService(s).validate(ids["log_id"], entorno.sector["Sistemas"])
        await s.commit()

    assert log.origen_intervencion == "gate"
    assert log.validado_en is not None
    assert log.validado_por_empleado_id is None
    assert log.intervencion_inicio_en is None


# -- 2.6: actor nulo sin empleado vinculado / id con empleado vinculado ---------


@pytest.mark.asyncio
async def test_cuenta_sin_empleado_valida_con_actor_nulo_y_registra_el_resto(
    client, engine, entorno
):
    """`client` autentica `User(id=1)`, que no tiene empleado: la validacion NO falla."""
    ids = await crear_log(engine, entorno, requiere_revision=True)

    resp = await client.patch(_url(ids["log_id"]), json={"sector_validado": "Sistemas"})

    assert resp.status_code == 200, resp.text
    cuerpo = resp.json()
    assert cuerpo["validado_por_empleado_id"] is None
    assert cuerpo["validado_en"] is not None
    assert cuerpo["origen_intervencion"] == "gate"
    log = await leer_log(engine, ids["log_id"])
    assert log.validado_por_empleado_id is None


@pytest.mark.asyncio
async def test_cuenta_con_empleado_vinculado_registra_su_id_y_no_expone_pii(
    engine, entorno
):
    ids = await crear_log(engine, entorno, requiere_revision=False)

    async with cliente_con_cuenta(engine, entorno.user_actor_id) as c:
        resp = await c.patch(
            _url(ids["log_id"]),
            json={
                "sector_validado": "Sistemas",
                "intervencion_inicio_en": "2026-10-30T15:00:00Z",
            },
        )

    assert resp.status_code == 200, resp.text
    cuerpo = resp.json()
    assert cuerpo["validado_por_empleado_id"] == entorno.empleado_actor_id
    assert cuerpo["origen_intervencion"] == "muestreo"
    # Solo el id del actor: ni email ni nombre ni legajo del empleado en la respuesta.
    for dato in ("c165.actor@example.test", "Actor Dos", "C165-ACT"):
        assert dato not in resp.text
    log = await leer_log(engine, ids["log_id"])
    assert log.validado_por_empleado_id == entorno.empleado_actor_id


@pytest.mark.asyncio
async def test_empleado_dado_de_baja_no_se_registra_como_actor(engine, entorno):
    """Triangulacion: `EmpleadoDep` solo resuelve empleados ACTIVOS; el resto queda NULL."""
    ids = await crear_log(engine, entorno)
    await desactivar_empleado(engine, entorno.empleado_actor_id)

    async with cliente_con_cuenta(engine, entorno.user_actor_id, alcance_global=True) as c:
        resp = await c.patch(_url(ids["log_id"]), json={"sector_validado": "Sistemas"})

    assert resp.status_code == 200, resp.text
    assert resp.json()["validado_por_empleado_id"] is None
    log = await leer_log(engine, ids["log_id"])
    assert log.validado_por_empleado_id is None
    assert log.validado_en is not None


# -- 2.7: re-validacion, gana la ultima escritura -------------------------------


@pytest.mark.asyncio
async def test_revalidar_sobrescribe_como_unidad_y_deja_vacio_el_conjunto_validado(
    client, engine, entorno
):
    ids = await crear_log(engine, entorno, requiere_revision=True)

    async with cliente_con_cuenta(engine, entorno.user_actor_id) as con_empleado:
        primera = await con_empleado.patch(
            _url(ids["log_id"]),
            json={
                "sector_validado": "Sistemas",
                "sectores_adicionales": ["Bases de Datos"],
                "intervencion_inicio_en": "2026-10-30T15:00:00Z",
            },
        )
    assert primera.status_code == 200, primera.text
    tras_primera = await leer_log(engine, ids["log_id"])
    assert [s.nombre for s in tras_primera.sectores_validados] == ["Bases de Datos"]
    assert tras_primera.validado_por_empleado_id == entorno.empleado_actor_id
    assert tras_primera.intervencion_inicio_en is not None

    segunda = await client.patch(
        _url(ids["log_id"]),
        json={"sector_validado": "Soporte Tecnico Software", "sectores_adicionales": []},
    )
    assert segunda.status_code == 200, segunda.text

    log = await leer_log(engine, ids["log_id"])
    assert log.sector_id_validado == entorno.sector["Soporte Tecnico Software"]
    # El reemplazo vale tambien cuando la lista llega vacia (defecto previo: se salteaba).
    assert list(log.sectores_validados) == []
    # Las cuatro columnas se sobrescriben como unidad con la ultima validacion.
    assert log.validado_por_empleado_id is None
    assert log.intervencion_inicio_en is None
    assert log.origen_intervencion == "gate"
    assert como_utc(log.validado_en) > como_utc(tras_primera.validado_en)


@pytest.mark.asyncio
async def test_revalidar_con_adicionales_reemplaza_el_conjunto_anterior(client, engine, entorno):
    ids = await crear_log(engine, entorno)
    await client.patch(
        _url(ids["log_id"]),
        json={"sector_validado": "Sistemas", "sectores_adicionales": ["Bases de Datos"]},
    )

    resp = await client.patch(
        _url(ids["log_id"]),
        json={"sector_validado": "Sistemas", "sectores_adicionales": ["Soporte Tecnico Software"]},
    )

    assert resp.status_code == 200, resp.text
    log = await leer_log(engine, ids["log_id"])
    assert [s.nombre for s in log.sectores_validados] == ["Soporte Tecnico Software"]


@pytest.mark.asyncio
async def test_un_adicional_inexistente_no_deja_el_log_a_medias(engine, entorno):
    """El adicional se resuelve ANTES de mutar: ante el 404 el log no queda validado."""
    from sqlalchemy import delete

    from app.models.catalog import Sector

    ids = await crear_log(engine, entorno)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as s:
        await s.execute(delete(Sector).where(Sector.nombre == "Seguridad Informatica"))
        await s.commit()

    async with factory() as s:
        service = ClasificacionService(s)
        with pytest.raises(EntityNotFoundError):
            await service.validate(
                ids["log_id"], entorno.sector["Sistemas"], ["Seguridad Informatica"]
            )
        # Misma sesion, sin rollback: lo flusheado antes del error seria visible aca.
        log = await service._repo.get_by_id(ids["log_id"])
        assert log.sector_id_validado is None
        assert log.validado_en is None
        assert log.origen_intervencion is None
        await s.rollback()
