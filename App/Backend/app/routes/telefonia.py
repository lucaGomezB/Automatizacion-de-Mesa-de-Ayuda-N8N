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
denegada). Un fallo de descarga/STT NO devuelve 500 ni pierde el ingreso.
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
from app.services.telefonia_service import TelefoniaService

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


async def _require_twilio_signature(
    request: Request, signature: str | None
) -> None:
    """
    Exige `X-Twilio-Signature` (fail-closed).

    Sin `TWILIO_AUTH_TOKEN` configurado se rechaza con 401: el endpoint nunca
    queda abierto. Con token configurado, una firma ausente o invalida tambien
    se rechaza con 401.
    """
    auth_token = get_settings().twilio_auth_token
    if not auth_token:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Twilio auth token is not configured",
        )
    form = await request.form()
    if not verify_signature(auth_token, signature, str(request.url), form):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Twilio signature",
        )


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
    },
)
async def recording_status(
    request: Request,
    service: ServiceDep,
    x_twilio_signature: SignatureHeader = None,
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

    Idempotente por `CallSid`: un callback repetido no re-descarga, no
    re-transcribe ni re-reserva. Responde 200 en cualquiera de los estados del
    ingreso para no perder la grabacion ante un fallo aguas abajo.
    """
    await _require_twilio_signature(request, x_twilio_signature)
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
    request: Request,
    x_twilio_signature: SignatureHeader = None,
) -> Response:
    """
    Documento `action` del `<Record>`: mensaje de cierre ALCANZABLE.

    No promete la creacion inmediata del ticket: el alta es asincrona (el
    backend transcribe, pseudonimiza y hace handoff a n8n).
    """
    await _require_twilio_signature(request, x_twilio_signature)
    return TwimlResponse(content=render_twiml_record_complete())


__all__ = ["router", "get_telefonia_service"]