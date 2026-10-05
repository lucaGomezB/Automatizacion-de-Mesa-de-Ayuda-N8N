"""
Endpoints del canal de telefonia asincronico (c-52).

Rutas expuestas (prefijo /api/v1/telefonia):
    POST /recording-status  -> callback de estado de grabacion de Twilio.
    POST /record-complete   -> accion posterior a la grabacion (TwiML de cierre).

Seguridad (gobernanza CRITICA):
    Ambos endpoints se autentican EXCLUSIVAMENTE con la firma
    `X-Twilio-Signature` (HMAC-SHA1 sobre la URL completa mas los parametros de
    formulario ordenados; ver `app/cost_guard/twilio_signature.py`). Twilio
    Programmable Voice NO puede adjuntar headers personalizados, por lo que la
    firma es la unica via. La validacion es FAIL-CLOSED: firma ausente/invalida
    -> 401; `TWILIO_AUTH_TOKEN` no configurado -> 401 (el endpoint NUNCA queda
    abierto).

    El callback de estado de grabacion NO provee `From`; por eso el numero
    llamante es opcional y el endpoint no depende de el.

El endpoint de callback delega en `TelefoniaService`, que persiste el ingreso
en cualquiera de sus estados (transcrito, error de descarga/STT o guarda
denegada) y reprocesa un ingreso en estado terminal de error ante un callback
repetido (W5). Un fallo de descarga/STT persiste el ingreso y responde 503 para
invitar el reintento nativo de Twilio; nunca responde 500 ni pierde el ingreso.
"""

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Header,
    HTTPException,
    Query,
    Request,
    Response,
)
from fastapi import status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings
from app.core.database import get_db_session
from app.cost_guard.dependencies import get_cost_guard
from app.cost_guard.guard import CostGuard
from app.cost_guard.twilio_signature import verify_signature
from app.cost_guard.twiml import TWIML_MEDIA_TYPE, render_twiml_record_complete
from app.models.empleado import Empleado
from app.routes.directorio import require_directorio_admin
from app.schemas.incidente import _derivar_latencia_e2e_ms
from app.schemas.telefonia import (
    RecordingStatusCallback,
    TelefoniaCorpusDeleteResult,
    TelefoniaIngresoRead,
    TelefoniaRecordingResponse,
)
from app.services.cost_guard_service import CostGuardService
from app.services.telefonia_pending_call_service import TelefoniaPendingCallService
from app.services.telefonia_service import TRANSIENT_ERROR_STATES, TelefoniaService

router = APIRouter(prefix="/telefonia", tags=["Telefonia"])

_SIGNATURE_HEADER = "X-Twilio-Signature"

SignatureHeader = Annotated[str | None, Header(alias=_SIGNATURE_HEADER)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
AdminDep = Annotated[Empleado, Depends(require_directorio_admin)]


class TwimlResponse(Response):
    """Respuesta TwiML (media type `text/xml`) documentada en el OpenAPI."""

    media_type = TWIML_MEDIA_TYPE


def get_telefonia_service(
    session: SessionDep,
    cost_guard: Annotated[CostGuard | None, Depends(get_cost_guard)] = None,
) -> TelefoniaService:
    """
    Fabrica del servicio de ingreso de telefonia.

    Construye el servicio con la sesion de la solicitud, la guarda de costo
    (reserva de `backend_stt`) y la configuracion efectiva. Los clientes STT y
    de descarga de Twilio se resuelven perezosamente desde `Settings`.
    """
    return TelefoniaService(
        session,
        cost_guard=CostGuardService(cost_guard),
        settings=get_settings(),
    )


ServiceDep = Annotated[TelefoniaService, Depends(get_telefonia_service)]


def get_pending_call_service(session: SessionDep) -> TelefoniaPendingCallService:
    """
    Fabrica del servicio del store efimero de correlacion (c-70, D2).

    Se expone como dependencia para que el webhook de voz (definido en el router
    de la guarda) y el callback de grabacion compartan el mismo contrato sin
    duplicar la construccion.
    """
    return TelefoniaPendingCallService(session)


PendingServiceDep = Annotated[
    TelefoniaPendingCallService, Depends(get_pending_call_service)
]


async def require_twilio_signature(
    request: Request,
    x_twilio_signature: SignatureHeader = None,
) -> None:
    """
    Exige `X-Twilio-Signature` (fail-closed).

    Se expone como DEPENDENCIA de FastAPI para que corra ANTES de la validacion
    de los campos de formulario del endpoint: asi una peticion sin firma (o con
    firma invalida) responde 401 aunque le falten campos requeridos, en lugar de
    caer primero en un 422 de validacion. Sin `TWILIO_AUTH_TOKEN` configurado se
    rechaza con 401: el endpoint nunca queda abierto. Con token configurado, una
    firma ausente o invalida tambien se rechaza con 401.
    """
    auth_token = get_settings().twilio_auth_token
    if not auth_token:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Twilio auth token is not configured",
        )
    form = await request.form()
    if not verify_signature(auth_token, x_twilio_signature, str(request.url), form):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Twilio signature",
        )


SignatureDep = Annotated[None, Depends(require_twilio_signature)]


async def _resolver_corpus_case_id(
    pending: TelefoniaPendingCallService, call_sid: str
) -> str | None:
    """
    Resuelve el `corpus_case_id` del `CallSid` y purga las filas vencidas (D2).

    La resolucion BORRA la fila pendiente; la purga es oportunista. Ambos pasos
    corren en la misma sesion/transaccion que el procesamiento del callback.
    """
    corpus_case_id = await pending.resolver_y_borrar(call_sid)
    await pending.purgar_vencidas()
    return corpus_case_id


@router.post(
    "/recording-status",
    response_model=TelefoniaRecordingResponse,
    summary="Callback de estado de grabacion de Twilio",
    responses={
        http_status.HTTP_401_UNAUTHORIZED: {
            "description": (
                "Firma `X-Twilio-Signature` ausente o invalida, o "
                "`TWILIO_AUTH_TOKEN` no configurado (fail-closed)."
            )
        },
        http_status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": (
                "Fallo transitorio de descarga o STT. El ingreso queda "
                "persistido en estado de error para que Twilio reintente el "
                "callback (W5)."
            )
        },
    },
)
async def recording_status(
    service: ServiceDep,
    _signature: SignatureDep,
    pending: PendingServiceDep,
    account_sid: str | None = Form(None, alias="AccountSid"),
    call_sid: str = Form(..., alias="CallSid"),
    recording_sid: str | None = Form(None, alias="RecordingSid"),
    recording_url: str = Form(..., alias="RecordingUrl"),
    recording_status: str | None = Form(None, alias="RecordingStatus"),
    recording_duration: int | None = Form(None, alias="RecordingDuration"),
    recording_channels: int | None = Form(None, alias="RecordingChannels"),
    recording_source: str | None = Form(None, alias="RecordingSource"),
    from_number: str | None = Form(None, alias="From"),
) -> TelefoniaRecordingResponse:
    """
    Procesa la notificacion de grabacion disponible de Twilio.

    Idempotente por `CallSid`: un callback repetido sobre un ingreso ya
    transcrito o `pendiente` no re-descarga, no re-transcribe ni re-reserva. Si
    el ingreso quedo en un estado terminal de error, el callback lo reprocesa.

    Codigos de respuesta segun el estado resultante:
        - `transcrito`, `pendiente` o `guarda_denegada` -> 200.
        - `error_descarga` o `error_stt` -> 503, para invitar el reintento nativo
          de Twilio. El estado de error se confirma antes de responder para que
          el siguiente callback pueda reprocesarlo.
    """
    callback = RecordingStatusCallback(
        account_sid=account_sid,
        call_sid=call_sid,
        recording_sid=recording_sid,
        recording_url=recording_url,
        recording_status=recording_status,
        recording_duration=recording_duration,
        recording_channels=recording_channels,
        recording_source=recording_source,
        caller=from_number,
        corpus_case_id=await _resolver_corpus_case_id(pending, call_sid),
    )
    ingreso = await service.process_recording(callback)
    if ingreso.transcripcion_estado in TRANSIENT_ERROR_STATES:
        # Persistir el estado terminal antes del 503: `get_db_session` revierte la
        # transaccion ante la excepcion, y el reintento de Twilio debe encontrar
        # el ingreso en error para reprocesarlo.
        await service.commit_error_state()
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Transient ingestion failure; a callback retry is expected.",
        )
    return TelefoniaRecordingResponse(
        status="accepted",
        call_sid=ingreso.call_sid,
        transcripcion_estado=ingreso.transcripcion_estado,
    )


def _ingreso_to_read(ingreso) -> TelefoniaIngresoRead:
    """
    Proyecta un ingreso a su representacion de lectura del corpus (D5).

    Deriva la latencia end-to-end del incidente vinculado con la MISMA funcion
    que `IncidenteRead`/`IncidenteListItem` (fuente unica de la metrica). El
    incidente llega eager-loaded (`selectinload`) o None si el alta aun no se
    resolvio.
    """
    incidente = ingreso.incidente
    latencia = None
    if incidente is not None:
        latencia = _derivar_latencia_e2e_ms(
            incidente.ingresado_en, incidente.persistido_en
        )
    return TelefoniaIngresoRead(
        id=ingreso.id,
        call_sid=ingreso.call_sid,
        corpus_case_id=ingreso.corpus_case_id,
        transcripcion_estado=ingreso.transcripcion_estado,
        ingresado_en=ingreso.ingresado_en,
        persistido_en=ingreso.persistido_en,
        incidente_id=ingreso.incidente_id,
        latencia_e2e_ms=latencia,
    )


@router.get(
    "/ingresos",
    response_model=TelefoniaIngresoRead,
    summary="Ultimo ingreso de un caso del corpus (administrador)",
    responses={
        http_status.HTTP_403_FORBIDDEN: {
            "description": "Se requiere el rol administrador_directorio."
        },
        http_status.HTTP_404_NOT_FOUND: {
            "description": "No hay ningun ingreso para el corpus_case_id."
        },
    },
)
async def obtener_ingreso_corpus(
    service: ServiceDep,
    _admin: AdminDep,
    corpus_case_id: str = Query(..., min_length=1),
    latest: bool = True,
) -> TelefoniaIngresoRead:
    """
    Recupera el ULTIMO ingreso de telefonia de un `corpus_case_id` (OQ5/D5).

    Exige JWT de un operador `administrador_directorio`. Devuelve la metrica
    end-to-end del incidente vinculado (`latencia_e2e_ms`), fuente unica de la
    medicion de telefonia. `latest` documenta el contrato (`latest=true`); la
    recuperacion siempre devuelve el ingreso mas reciente.
    """
    ingreso = await service.obtener_ultimo_ingreso_por_corpus_case_id(
        corpus_case_id
    )
    if ingreso is None:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="No hay ingreso para el corpus_case_id indicado.",
        )
    return _ingreso_to_read(ingreso)


@router.delete(
    "/ingresos",
    response_model=TelefoniaCorpusDeleteResult,
    summary="Borrado acotado por corpus_case_id para --replace (administrador)",
    responses={
        http_status.HTTP_403_FORBIDDEN: {
            "description": "Se requiere el rol administrador_directorio."
        },
    },
)
async def eliminar_ingresos_corpus(
    service: ServiceDep,
    _admin: AdminDep,
    corpus_case_id: str = Query(..., min_length=1),
    dry_run: bool = True,
) -> TelefoniaCorpusDeleteResult:
    """
    Elimina los ingresos e incidentes PREVIOS de un caso, conservando el ultimo.

    Destructivo con `dry_run=True` por defecto (governance ALTO): sin
    `dry_run=false` explicito no borra nada, solo reporta. El borrado esta
    acotado al `corpus_case_id` y respeta el orden FK (incidente -> ingreso).
    """
    counts = await service.eliminar_previos_por_corpus_case_id(
        corpus_case_id, dry_run=dry_run
    )
    return TelefoniaCorpusDeleteResult(
        corpus_case_id=corpus_case_id, dry_run=dry_run, **counts
    )


@router.post(
    "/record-complete",
    summary="Accion posterior a la grabacion (TwiML de cierre)",
    response_class=TwimlResponse,
    responses={
        http_status.HTTP_401_UNAUTHORIZED: {
            "description": (
                "Firma `X-Twilio-Signature` ausente o invalida, o "
                "`TWILIO_AUTH_TOKEN` no configurado (fail-closed)."
            )
        },
    },
)
async def record_complete(
    _signature: SignatureDep,
) -> Response:
    """
    Documento `action` del `<Record>`: mensaje de cierre ALCANZABLE.

    No promete la creacion inmediata del ticket: el alta es asincrona (el
    backend transcribe, pseudonimiza y hace handoff a n8n).
    """
    return TwimlResponse(content=render_twiml_record_complete())


__all__ = ["router", "get_telefonia_service", "get_pending_call_service"]