"""
Schemas Pydantic del canal de telefonia asincronico (c-52).

Contratos HTTP y de handoff del canal:

    RecordingStatusCallback    — parametros del callback de estado de grabacion
                                 de Twilio. NO depende de `From` (ese callback
                                 no lo provee); el campo `caller` queda opcional.
    TelefoniaRecordingResponse — respuesta del endpoint de callback.
    TelefoniaHandoffPayload    — payload EXACTO del handoff backend -> n8n.
                                 Solo la descripcion pseudonimizada, el CallSid,
                                 el llamante y el `ingresado_en` sellado. El
                                 transcript crudo NUNCA viaja en este payload.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RecordingStatusCallback(BaseModel):
    """
    Callback de estado de grabacion de Twilio.

    Los parametros de formulario del callback son `AccountSid`, `CallSid`,
    `RecordingSid`, `RecordingUrl`, `RecordingStatus`, `RecordingDuration`,
    `RecordingChannels` y `RecordingSource`; NO incluye `From`, por lo que
    `caller` es opcional (el endpoint lo toma de `From` cuando esta presente).
    """

    model_config = ConfigDict(extra="ignore")

    account_sid: str | None = None
    call_sid: str = Field(min_length=1)
    recording_sid: str | None = None
    recording_url: str = Field(min_length=1)
    recording_status: str | None = None
    recording_duration: int | None = Field(default=None, ge=0)
    recording_channels: int | None = None
    recording_source: str | None = None
    # Numero llamante (`From`). El callback de grabacion no lo provee; el
    # webhook de voz si, cuando esta disponible.
    caller: str | None = None


class TelefoniaRecordingResponse(BaseModel):
    """Respuesta del endpoint de callback (Twilio solo requiere 2xx)."""

    status: str
    call_sid: str
    transcripcion_estado: str


class TelefoniaHandoffPayload(BaseModel):
    """Payload EXACTO del handoff autenticado backend -> n8n."""

    descripcion_pseudonimizada: str
    call_sid: str
    caller: str | None = None
    ingresado_en: str | None = None


__all__ = [
    "RecordingStatusCallback",
    "TelefoniaRecordingResponse",
    "TelefoniaHandoffPayload",
]