"""
Tests de la integración notify_n8n en IncidenteService.

Responsabilidad:
    Verifica que IncidenteService._apply_classification() invoca notify_n8n
    (fire-and-forget) tras clasificar un incidente, y que cualquier fallo
    del webhook NO se propaga al llamador ni impide la persistencia del incidente.

    Se cubren dos capas:
        * Unitaria  — mockea notify_n8n con AsyncMock; prueba el contrato de
                      invocación del service (qué se llama y con qué args).
        * Integración — usa la función notify_n8n REAL contra un servidor HTTP
                        mock levantado con httpx.ASGITransport + una app FastAPI
                        mínima de un solo endpoint (no hay pytest-httpx/respx en
                        requirements.txt, se usa el fallback ASGI).

Decisiones de implementación:
    - Parche en `app.services.incidente_service.notify_n8n` (referencia local
      del import), NO en `app.utils.n8n_webhook.notify_n8n`.
    - `asyncio.sleep(0)` drena el event loop para que la tarea creada con
      create_task sea ejecutada antes de los asserts.
    - La configuración de n8n_webhook_url en tests de integración se inyecta
      monkeyparcheando `get_settings` con una instancia Settings controlada.
"""

import asyncio
from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import Settings, get_settings
from app.models.catalog import Estado, Sector
from app.schemas.clasificacion import ClasificacionResult
from app.schemas.incidente import IncidenteCreate
from app.services.incidente_service import IncidenteService


# ── Helpers de semillado de catálogos ───────────────────────────────────────


async def _seed_catalogs(session: AsyncSession) -> tuple[Estado, Sector]:
    """
    Siembra las filas mínimas de catálogo que IncidenteService necesita.

    Inserta un Estado "nuevo" y un Sector "Sistemas" (valores exactos que
    el servicio busca al clasificar un incidente). Hace flush para que los
    IDs autoincrement estén disponibles sin committear (el test maneja la
    transacción).

    Args:
        session: Sesión activa de base de datos (SQLite in-memory de test).

    Returns:
        Tupla (estado_nuevo, sector_sistemas) ya persistidos en memoria.
    """
    estado = Estado(nombre="nuevo", descripcion="Incidente recibido, sin asignar")
    sector = Sector(nombre="Sistemas", descripcion="Infraestructura y redes")
    session.add(estado)
    session.add(sector)
    await session.flush()
    return estado, sector


def _make_clasificacion_result(
    categoria: str = "Sistemas",
    confianza: float = 0.95,
    etapa: str = "deterministic",
    requiere_revision_humana: bool = False,
) -> ClasificacionResult:
    """
    Construye un ClasificacionResult con valores configurables.

    Función auxiliar que evita la repetición de campos en cada test.

    Args:
        categoria:               Nombre del sector predicho.
        confianza:               Nivel de certeza (0.0 – 1.0).
        etapa:                   Etapa del pipeline que clasificó.
        requiere_revision_humana: Si el operador debe revisar el caso.

    Returns:
        ClasificacionResult instanciado.
    """
    return ClasificacionResult(
        categoria=categoria,
        confianza=confianza,
        etapa=etapa,
        requiere_revision_humana=requiere_revision_humana,
    )


def _make_payload(descripcion: str = "El servidor de base de datos no responde") -> IncidenteCreate:
    """
    Construye un IncidenteCreate con descripción configurable.

    Args:
        descripcion: Texto del incidente (mínimo 10 caracteres).

    Returns:
        IncidenteCreate listo para pasar al service.
    """
    return IncidenteCreate(descripcion=descripcion)


# ── Tests unitarios — contrato de invocación del service ────────────────────


@pytest.mark.asyncio
async def test_create_and_classify_invokes_notify_n8n_with_correct_args(db_session):
    """
    WHEN se crea y clasifica un incidente
    THEN notify_n8n es invocado exactamente una vez con (incidente.id, result).

    RED → este test FALLA antes de que _apply_classification llame a notify_n8n.
    GREEN → pasa tras agregar asyncio.create_task(notify_n8n(...)) en el service.

    Parche: app.services.incidente_service.notify_n8n (referencia local del import).
    Drenaje del loop: await asyncio.sleep(0) da una oportunidad al event loop
    de ejecutar la tarea programada con create_task antes del assert.
    """
    # Arrange
    result_esperado = _make_clasificacion_result()
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=result_esperado)
    await _seed_catalogs(db_session)
    payload = _make_payload()

    # Act
    with patch(
        "app.services.incidente_service.notify_n8n",
        new_callable=AsyncMock,
    ) as mock_notify:
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        # Drenar el event loop para que la tarea creada con create_task se ejecute
        await asyncio.sleep(0)

    # Assert
    mock_notify.assert_called_once_with(incidente.id, result_esperado)


@pytest.mark.asyncio
async def test_notify_n8n_receives_actual_classification_result(db_session):
    """
    TRIANGULATE: verifica que el result exacto del clasificador se pasa a
    notify_n8n y no está hardcodeado.

    Usa un ClasificacionResult distinto al del test anterior (fallback,
    confianza=0.0, requiere_revision_humana=True) para probar que el valor
    proviene del clasificador, no de una constante.
    """
    # Arrange
    result_fallback = _make_clasificacion_result(
        categoria="Sistemas",
        confianza=0.0,
        etapa="fallback",
        requiere_revision_humana=True,
    )
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=result_fallback)
    await _seed_catalogs(db_session)
    payload = _make_payload()

    # Act
    with patch(
        "app.services.incidente_service.notify_n8n",
        new_callable=AsyncMock,
    ) as mock_notify:
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # Assert — el result exacto del clasificador llegó a notify_n8n
    mock_notify.assert_called_once_with(incidente.id, result_fallback)
    args, _ = mock_notify.call_args
    assert args[1].etapa == "fallback"
    assert args[1].requiere_revision_humana is True
    assert args[1].confianza == 0.0


@pytest.mark.asyncio
async def test_notify_n8n_called_even_when_webhook_url_empty(db_session):
    """
    TRIANGULATE (borde): cuando n8n_webhook_url está vacío, el service IGUAL
    llama a notify_n8n (la decisión de no-op vive en la utilidad, no en el service).

    Confirma el contrato: el service siempre invoca notify_n8n; es la utilidad
    quien decide si hacer o no el HTTP POST según la configuración.
    """
    # Arrange
    result_esperado = _make_clasificacion_result()
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=result_esperado)
    await _seed_catalogs(db_session)
    payload = _make_payload()

    # Override: n8n_webhook_url vacío (simula entorno sin N8N configurado)
    settings_sin_webhook = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-key",
        n8n_webhook_url="",
    )

    # Act
    with patch("app.services.incidente_service.notify_n8n", new_callable=AsyncMock) as mock_notify, \
         patch("app.utils.n8n_webhook.get_settings", return_value=settings_sin_webhook):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # Assert — el service invocó notify_n8n (la utilidad se encargará del no-op)
    mock_notify.assert_called_once()


# ── Tests de aislamiento de fallos — fire-and-forget ────────────────────────


@pytest.mark.asyncio
async def test_create_and_classify_succeeds_when_notify_n8n_raises(db_session):
    """
    WHEN notify_n8n lanza una excepción (fallo de red, timeout, etc.)
    THEN create_and_classify() NO propaga la excepción y retorna el incidente.

    Con asyncio.create_task(), la excepción queda atrapada en la tarea y
    no llega al llamador. El incidente ya fue persistido antes de que la
    tarea intente la notificación.
    """
    # Arrange
    result_esperado = _make_clasificacion_result()
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=result_esperado)
    await _seed_catalogs(db_session)
    payload = _make_payload()

    # Act — notify_n8n falla con RuntimeError
    with patch(
        "app.services.incidente_service.notify_n8n",
        new_callable=AsyncMock,
        side_effect=RuntimeError("boom — fallo de red simulado"),
    ):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        # No debe propagarse la excepción
        incidente = await service.create_and_classify(payload)
        # Drenar el loop para que la tarea falle silenciosamente
        await asyncio.sleep(0)

    # Assert (a) — el incidente fue retornado (create_and_classify no propagó)
    assert incidente is not None
    assert incidente.id is not None


@pytest.mark.asyncio
async def test_incidente_persists_in_db_when_notify_n8n_raises(db_session):
    """
    WHEN la notificación a N8N falla después de que el incidente fue clasificado
    THEN el incidente y su clasificacion_log permanecen en la base de datos.

    Verifica el escenario "El incidente persiste pese al fallo de N8N" de la spec.
    """
    # Arrange
    result_esperado = _make_clasificacion_result(requiere_revision_humana=False)
    classifier_mock = AsyncMock()
    classifier_mock.classify = AsyncMock(return_value=result_esperado)
    await _seed_catalogs(db_session)
    payload = _make_payload()

    # Act — notify_n8n falla
    with patch(
        "app.services.incidente_service.notify_n8n",
        new_callable=AsyncMock,
        side_effect=Exception("error de integración"),
    ):
        service = IncidenteService(session=db_session, classifier=classifier_mock)
        incidente = await service.create_and_classify(payload)
        await asyncio.sleep(0)

    # Assert (b) — el incidente existe y fue clasificado correctamente
    assert incidente.id is not None
    assert incidente.requiere_revision_humana is False
    # Verificar que el incidente persiste en la sesión
    from sqlalchemy import select
    from app.models.incidente import Incidente
    result = await db_session.execute(
        select(Incidente).where(Incidente.id == incidente.id)
    )
    incidente_db = result.scalar_one_or_none()
    assert incidente_db is not None


# ── Tests de integración — webhook real contra servidor mock ASGI ────────────


def _make_webhook_mock_app(captured: list[dict], fail: bool = False) -> object:
    """
    Construye una aplicación FastAPI mínima que captura el payload recibido.

    La app registra el endpoint en /webhook (ruta que coincide con la URL
    de test `http://mock-n8n/webhook`). Si `fail` es True, responde 500 para
    simular un webhook no disponible.

    Args:
        captured: Lista mutable donde se almacenará el payload recibido.
        fail:     Si True, el endpoint responde siempre con HTTP 500.

    Returns:
        Aplicación FastAPI lista para usar con httpx.ASGITransport.
    """
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse

    mock_app = FastAPI()

    @mock_app.post("/webhook")
    async def webhook_handler(request: Request):
        if fail:
            return JSONResponse({"error": "internal error"}, status_code=500)
        body = await request.json()
        captured.append(body)
        return JSONResponse({"ok": True}, status_code=200)

    return mock_app


@pytest.mark.asyncio
async def test_notify_n8n_posts_expected_payload_to_webhook():
    """
    INTEGRACIÓN: notify_n8n REAL envía un POST cuyo JSON contiene todos los
    campos del contrato de payload definidos en la spec.

    Cubre el Scenario: "Contenido del payload enviado al webhook".

    Estrategia: app FastAPI mínima vía httpx.ASGITransport captura el request;
    no se hacen llamadas HTTP reales a N8N. El cliente httpx se reemplaza por
    una función factory que crea siempre un AsyncClient con el transport ASGI.
    """
    # Arrange
    captured: list[dict] = []
    mock_app = _make_webhook_mock_app(captured, fail=False)

    incidente_id = 42
    result = _make_clasificacion_result(
        categoria="Sistemas",
        confianza=0.91,
        etapa="deterministic",
        requiere_revision_humana=False,
    )

    # La URL en settings y la URL que POSTea notify_n8n deben coincidir con la
    # ruta registrada en el mock_app (/webhook). El transport ASGI sirve esa ruta.
    webhook_url = "http://mock-n8n/webhook"
    settings_test = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-key",
        n8n_webhook_url=webhook_url,
        n8n_webhook_secret="",
    )

    import httpx
    from app.utils import n8n_webhook as n8n_mod

    transport = ASGITransport(app=mock_app)
    # Capturar el constructor original ANTES de parchear para evitar recursión
    _OriginalAsyncClient = httpx.AsyncClient

    def make_asgi_client(**kwargs):
        """
        Factory que crea un AsyncClient con transporte ASGI en lugar del real.

        Usa _OriginalAsyncClient (capturado antes del patch) para evitar que
        la llamada a httpx.AsyncClient dentro de la factory redirija al mock
        (recursión infinita).
        """
        kwargs.pop("timeout", None)
        return _OriginalAsyncClient(transport=transport, timeout=5.0)

    # Act — notify_n8n real con httpx.AsyncClient reemplazado por la factory ASGI
    with patch.object(n8n_mod, "get_settings", return_value=settings_test), \
         patch.object(httpx, "AsyncClient", make_asgi_client):
        from app.utils.n8n_webhook import notify_n8n
        await notify_n8n(incidente_id, result)

    # Assert — el mock recibió exactamente un POST con los campos del contrato
    assert len(captured) == 1, f"Se esperaba 1 request, se recibieron {len(captured)}"
    payload = captured[0]
    assert payload["incidente_id"] == incidente_id
    assert payload["categoria"] == "Sistemas"
    assert payload["confianza"] == pytest.approx(0.91)
    assert payload["etapa"] == "deterministic"
    assert payload["requiere_revision_humana"] is False


@pytest.mark.asyncio
async def test_notify_n8n_swallows_error_on_webhook_500():
    """
    INTEGRACIÓN TRIANGULATE: cuando el webhook responde 500, notify_n8n
    NO relanza la excepción (retorna None) y registra n8n_notification_failed.

    Cubre el Scenario: "El webhook de N8N falla".
    Verifica el aislamiento de fallos a nivel de la utilidad notify_n8n.
    """
    # Arrange
    captured: list[dict] = []
    mock_app = _make_webhook_mock_app(captured, fail=True)  # siempre responde 500

    incidente_id = 99
    result = _make_clasificacion_result(confianza=0.85)

    settings_test = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-key",
        n8n_webhook_url="http://mock-n8n/webhook",
        n8n_webhook_secret="",
    )

    import httpx
    from app.utils import n8n_webhook as n8n_mod

    transport = ASGITransport(app=mock_app)
    _OriginalAsyncClient = httpx.AsyncClient

    def make_asgi_client_500(**kwargs):
        kwargs.pop("timeout", None)
        return _OriginalAsyncClient(transport=transport, timeout=5.0)

    # Act — notify_n8n no debe relanzar aunque el webhook retorne 500
    returned = None
    raised = None
    with patch.object(n8n_mod, "get_settings", return_value=settings_test), \
         patch.object(httpx, "AsyncClient", make_asgi_client_500):
        from app.utils.n8n_webhook import notify_n8n
        try:
            returned = await notify_n8n(incidente_id, result)
        except Exception as exc:
            raised = exc

    # Assert — no se propagó ninguna excepción
    assert raised is None, f"notify_n8n propagó una excepción: {raised}"
    assert returned is None  # La función retorna None siempre (fire-and-forget)
