"""
Tests de contrato c-72: la clasificacion telefonica es propiedad del backend.

Regla (design D1/D2, specs sector-assignment ASG-010 y telefonia-stt-intake):
    Un alta del canal telefonico resuelve su sector por la CASCADA hibrida del
    backend sobre la descripcion PSEUDONIMIZADA, ignorando cualquier bloque
    `clasificacion` precalculado que el canal pudiera enviar. Los canales correo
    y web conservan el atajo precalculado (sin cambio de comportamiento).

Estructura TDD:
    - 1.2 RED: telefonia con precalculada difiere -> gana la cascada.
    - 1.4 TRIANGULATE: telefonia sin precalculada; correo con precalculada.
    - 1.5/1.6 contrato de pseudonimizacion: la entrada de la cascada es la
      descripcion pseudonimizada, nunca el texto crudo con PII.
"""

import pytest

from app.schemas.clasificacion import ClasificacionResult

# Descripcion con PII (email) para verificar la frontera de pseudonimizacion.
DESCRIPCION_CON_PII = (
    "Falla al enviar un correo a usuario@empresa.com desde el servidor contable."
)
EMAIL_CRUDO = "usuario@empresa.com"


def _result(
    sector_predicho: str = "Bases de Datos",
    confianza: float = 0.95,
    etapa: str = "deterministic",
    requiere_revision_humana: bool = False,
) -> ClasificacionResult:
    """Resultado que devuelve el clasificador doble (representa la cascada)."""
    return ClasificacionResult(
        sector_predicho=sector_predicho,
        confianza=confianza,
        etapa=etapa,
        requiere_revision_humana=requiere_revision_humana,
        respuesta_raw=None,
    )


def _precalculada(sector: str = "Sistemas", confianza: float = 0.92) -> dict:
    """Bloque de clasificacion precalculada tal como lo enviaria el canal."""
    return {
        "sector_predicho": sector,
        "sectores_adicionales": [],
        "confianza": confianza,
        "requiere_revision_humana": False,
        "origen": "n8n",
    }


def _payload(canal_origen_id: int, **overrides) -> dict:
    """Payload de alta con canal explicito (telefonia o correo)."""
    base = {
        "descripcion": DESCRIPCION_CON_PII,
        "prioridad": "media",
        "canal_origen_id": canal_origen_id,
        "origen_evento": "creacion_incidente",
    }
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_1_2_telefonia_con_precalculada_gana_la_cascada(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (1.2): una alta telefonica con `clasificacion` precalculada NO usa ese
    valor como sector; resuelve por la cascada del backend. La cascada devuelve
    "Bases de Datos" mientras la precalculada dice "Sistemas".
    """
    result = _result(sector_predicho="Bases de Datos")
    canal_llamada = seed_catalogs["canal_llamada"]
    payload = _payload(
        canal_llamada.id, clasificacion=_precalculada(sector="Sistemas")
    )

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["sector"]["nombre"] == "Bases de Datos", (
        "La telefonia persistio la clasificacion precalculada en vez de la cascada"
    )
    assert spy.classify.await_count == 1, (
        "La cascada del backend no se invoco para el alta telefonica"
    )


@pytest.mark.asyncio
async def test_1_4_telefonia_sin_precalculada_usa_la_cascada(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    TRIANGULATE (1.4): una alta telefonica SIN bloque precalculado resuelve por
    la cascada, igual que correo y web.
    """
    result = _result(sector_predicho="Soporte Tecnico Software")
    canal_llamada = seed_catalogs["canal_llamada"]

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post(
            "/api/v1/incidentes/", json=_payload(canal_llamada.id)
        )

    assert response.status_code == 201, response.text
    assert response.json()["sector"]["nombre"] == "Soporte Tecnico Software"
    assert spy.classify.await_count == 1


@pytest.mark.asyncio
async def test_1_4_correo_con_precalculada_conserva_el_atajo(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    TRIANGULATE (1.4): para correo el bloque precalculado sigue teniendo efecto
    (sin cambio de comportamiento); la cascada NO se invoca.
    """
    result = _result(sector_predicho="Bases de Datos")
    canal_correo = seed_catalogs["canal_correo"]
    payload = _payload(
        canal_correo.id, clasificacion=_precalculada(sector="Sistemas")
    )

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["sector"]["nombre"] == "Sistemas"
    assert spy.classify.await_count == 0, (
        "El correo con precalculada no debe invocar la cascada"
    )


@pytest.mark.asyncio
async def test_1_4_web_con_precalculada_conserva_el_atajo(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    TRIANGULATE (1.4): el canal web tampoco cambia de comportamiento; el bloque
    precalculado sigue teniendo efecto y la cascada NO se invoca.
    """
    result = _result(sector_predicho="Bases de Datos")
    canal_web = seed_catalogs["canal_formulario"]
    payload = _payload(canal_web.id, clasificacion=_precalculada(sector="Sistemas"))

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    assert response.json()["sector"]["nombre"] == "Sistemas"
    assert spy.classify.await_count == 0


@pytest.mark.asyncio
async def test_1_5_cascada_recibe_la_descripcion_pseudonimizada(
    seed_catalogs, make_client_with_spy_classifier
):
    """
    RED (1.5): la entrada de la cascada para telefonia es la descripcion
    pseudonimizada; el texto crudo con PII nunca llega al clasificador.
    """
    result = _result(sector_predicho="Bases de Datos")
    canal_llamada = seed_catalogs["canal_llamada"]
    payload = _payload(
        canal_llamada.id, clasificacion=_precalculada(sector="Sistemas")
    )

    async with make_client_with_spy_classifier(result) as (client, spy):
        response = await client.post("/api/v1/incidentes/", json=payload)

    assert response.status_code == 201, response.text
    assert spy.classify.await_count == 1, (
        "La cascada no se invoco: no se puede verificar la frontera de pseudonimizacion"
    )
    texto_clasificado = spy.classify.call_args.args[0]
    assert EMAIL_CRUDO not in texto_clasificado, (
        "El texto crudo con PII llego al clasificador (frontera vulnerada)"
    )
    assert "[EMAIL]" in texto_clasificado, (
        "La entrada de la cascada no es la descripcion pseudonimizada"
    )
