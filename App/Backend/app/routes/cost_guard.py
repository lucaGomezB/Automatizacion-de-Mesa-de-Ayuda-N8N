"""
Endpoints de la guarda de costo en runtime (c-45).

Rutas expuestas (prefijo /api/v1/cost-guard):
    POST /reserve        → evaluacion de la guarda para n8n antes del AI Agent.
    POST /twilio/voice   → webhook de voz pre-llamada de Twilio (TwiML).

Seguridad (post-verify, gobernanza ALTA):
    El endpoint de reserva que consume n8n (`POST /reserve`) exige el secreto
    compartido en el header `X-Cost-Guard-Secret`. El secreto NUNCA se acepta
    por query string (los secretos en la URL quedan registrados en logs y
    proxies). Si `COST_GUARD_SHARED_SECRET` no esta configurado, el endpoint
    rechaza toda peticion con HTTP 401: no existe configuracion con la guarda
    habilitada y los endpoints abiertos. El arranque emite la advertencia
    `cost_guard_secret_missing` (ver `app/cost_guard/posture.py`).

    El webhook de voz de Twilio (`POST /twilio/voice`) se autentica EXCLUSIVAMENTE
    con la firma `X-Twilio-Signature` (HMAC-SHA1, ver
    `app/cost_guard/twilio_signature.py`): Twilio Programmable Voice NO puede
    adjuntar headers personalizados a la peticion del webhook, por lo que exigir
    `X-Cost-Guard-Secret` lo tornaria inalcanzable (todo request seria 401). La
    firma se exige SIEMPRE que `TWILIO_AUTH_TOKEN` este configurado. Cuando el
    token NO esta configurado (credencial pendiente), el webhook rechaza con 401
    (fail-closed) y el arranque emite `cost_guard_twilio_token_missing`: antes de
    cargar la credencial Twilio no esta configurado para llamar al endpoint, y al
    cargarla la validacion de firma se activa sin ningun otro cambio. El algoritmo
    implementado es HMAC-SHA1 sobre la URL completa mas los parametros de
    formulario ordenados, en base64, confirmado contra la documentacion
    autoritativa de Twilio
    (https://www.twilio.com/docs/usage/webhooks/webhooks-security) y contra la
    implementacion de referencia del SDK oficial `twilio-python`
    (`twilio/request_validator.py`). El SHA-256 que aparece en esa documentacion
    corresponde al hash del cuerpo JSON (`bodySHA256`), no a la firma.
"""

import hmac
from typing import Annotated

from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Response
from fastapi import status as http_status

from app.config.settings import get_settings
from app.cost_guard.constants import PROVIDER_TWILIO
from app.cost_guard.dependencies import get_cost_guard
from app.cost_guard.guard import CostGuard
from app.cost_guard.twilio_signature import verify_signature
from app.cost_guard.twiml import (
    TWIML_MEDIA_TYPE,
    render_twiml_allowed,
    render_twiml_denied,
)
from app.schemas.cost_guard import (
    CostGuardReserveRequest,
    CostGuardReserveResponse,
)
from app.services.cost_guard_service import CostGuardService

router = APIRouter(prefix="/cost-guard", tags=["Cost Guard"])

_SECRET_HEADER = "X-Cost-Guard-Secret"
_SIGNATURE_HEADER = "X-Twilio-Signature"

SecretHeader = Annotated[str | None, Header(alias=_SECRET_HEADER)]
SignatureHeader = Annotated[str | None, Header(alias=_SIGNATURE_HEADER)]
FromForm = Annotated[str | None, Form(alias="From")]


class TwimlResponse(Response):
    """
    Respuesta TwiML del webhook de voz.

    Declara `text/xml` como media type de la clase, de modo que el OpenAPI
    generado documente el 200 real (y no `application/json`), sin cambiar el
    cuerpo que ya devuelve `render_twiml_*`.
    """

    media_type = TWIML_MEDIA_TYPE


def _require_secret(secret: str | None) -> None:
    """
    Exige el secreto compartido configurado (header `X-Cost-Guard-Secret`).

    Sin secreto configurado, ningun request puede autenticarse: se rechaza con
    401 (fail-closed). Con secreto configurado, un valor ausente o distinto
    tambien se rechaza con 401.
    """
    expected = get_settings().cost_guard_shared_secret
    if not expected:
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Cost guard shared secret is not configured",
        )
    if secret is None or not hmac.compare_digest(
        secret.encode("utf-8"), expected.encode("utf-8")
    ):
        raise HTTPException(
            status_code=http_status.HTTP_401_UNAUTHORIZED,
            detail="Invalid cost guard secret",
        )


async def _require_twilio_signature(
    request: Request, signature: str | None
) -> None:
    """
    Exige `X-Twilio-Signature`, el unico mecanismo de auth que Twilio ofrece.

    Twilio Programmable Voice no puede adjuntar headers personalizados, por lo
    que la firma es la unica via de autenticacion del webhook de voz.

    Sin `TWILIO_AUTH_TOKEN` configurado (credencial pendiente) se rechaza con
    401 (fail-closed): el endpoint NUNCA queda abierto. Con token configurado,
    una firma ausente o invalida tambien se rechaza con 401.
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


def get_cost_guard_service(
    guard: Annotated[CostGuard | None, Depends(get_cost_guard)],
) -> CostGuardService:
    """Fabrica del servicio de guarda para la inyeccion de dependencias."""
    return CostGuardService(guard)


ServiceDep = Annotated[CostGuardService, Depends(get_cost_guard_service)]


@router.post(
    "/reserve",
    response_model=CostGuardReserveResponse,
    summary="Evaluar la guarda de costo antes de una llamada paga",
    responses={
        http_status.HTTP_401_UNAUTHORIZED: {
            "description": (
                "Header `X-Cost-Guard-Secret` ausente o distinto, o "
                "`COST_GUARD_SHARED_SECRET` no configurado (fail-closed)."
            )
        },
    },
)
async def reserve_cost_guard(
    payload: CostGuardReserveRequest,
    service: ServiceDep,
    x_cost_guard_secret: SecretHeader = None,
) -> CostGuardReserveResponse:
    """
    Evalua la guarda antes de invocar al AI Agent de n8n.

    Exige el header `X-Cost-Guard-Secret`. Responde 200 con la decision en el
    cuerpo: `allowed` en true permite continuar; en false indica derivar a
    revision humana. El flujo de n8n rutea segun `allowed` y NO invoca al AI
    Agent cuando es false.
    """
    _require_secret(x_cost_guard_secret)
    decision = await service.reserve(payload.provider, caller=payload.caller)
    return CostGuardReserveResponse(
        allowed=decision.allowed,
        cause=decision.cause,
        provider=payload.provider,
    )


@router.post(
    "/twilio/voice",
    summary="Webhook de voz pre-llamada de Twilio (TwiML)",
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
async def twilio_voice_webhook(
    request: Request,
    service: ServiceDep,
    from_number: FromForm = None,
    x_twilio_signature: SignatureHeader = None,
) -> Response:
    """
    Webhook que Twilio consulta ANTES de grabar y transcribir.

    Se autentica con la firma `X-Twilio-Signature`, exigida siempre que
    `TWILIO_AUTH_TOKEN` este configurado; si el token falta, responde 401
    (fail-closed) para no quedar abierto. NO usa el header
    `X-Cost-Guard-Secret` porque Twilio no puede enviar headers personalizados.

    Permite: responde TwiML con `<Record transcribe="true">`. Deniega: responde
    TwiML con `<Say>` + `<Hangup/>`, de modo que NO se grabe ni se transcriba.
    La reserva es de una unidad del costo unitario de transcripcion por llamada
    concedida (la duracion se desconoce al inicio).
    """
    await _require_twilio_signature(request, x_twilio_signature)
    decision = await service.reserve(PROVIDER_TWILIO, caller=from_number)
    twiml = render_twiml_allowed() if decision.allowed else render_twiml_denied()
    return TwimlResponse(content=twiml)


__all__ = ["router"]