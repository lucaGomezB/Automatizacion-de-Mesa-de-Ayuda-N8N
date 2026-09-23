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
from app.schemas.telefonia import (
    RecordingStatusCallback,
    TelefoniaRecordingResponse,
)
from app.services.cost_guard_service import CostGuardService
from app.services.telefonia_service import TRANSIENT_ERROR_STATES, TelefoniaService

router = APIRouter(prefix="/telefonia", tags=["Telefonia"])

_SIGNATURE_HEADER = "X-Twilio-Signature"

SignatureHeader = Annotated[str | None, Header(alias=_SIGNATURE_HEADER)]
SessionDep = Annotated[AsyncSession, Depends(get_db_session)]


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


__all__ = ["router", "get_telefonia_service"]