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

from datetime import datetime

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
    # Correlacion opcional con un caso del corpus (c-70, D2). NO llega como
    # parametro de Twilio: la ruta la resuelve por `call_sid` desde la tabla
    # corta `telefonia_pending_call` antes de construir el callback.
    corpus_case_id: str | None = None


class TelefoniaRecordingResponse(BaseModel):
    """Respuesta del endpoint de callback (Twilio solo requiere 2xx)."""

    status: str
    call_sid: str
    transcripcion_estado: str


class TelefoniaHandoffPayload(BaseModel):
    """Payload EXACTO del handoff autenticado backend -> n8n."""

    descripcion_pseudonimizada: str
    call_sid: str
    caller_number: str | None = None
    ingresado_en: str | None = None


class TelefoniaIngresoRead(BaseModel):
    """
    Lectura del ULTIMO ingreso de telefonia de un caso del corpus (c-70, D5).

    Expone el `corpus_case_id` para permitir la recuperacion exacta y la
    metrica end-to-end del incidente vinculado (`latencia_e2e_ms`), fuente unica
    de la medicion de telefonia. NO expone el transcript ni PII.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    call_sid: str
    corpus_case_id: str | None = None
    transcripcion_estado: str
    ingresado_en: datetime | None = None
    persistido_en: datetime | None = None
    incidente_id: int | None = None
    latencia_e2e_ms: int | None = None


class TelefoniaCorpusDeleteResult(BaseModel):
    """Resultado del borrado acotado por `corpus_case_id` (c-70, D7)."""

    corpus_case_id: str
    dry_run: bool
    ingresos_eliminados: int
    incidentes_eliminados: int


__all__ = [
    "RecordingStatusCallback",
    "TelefoniaRecordingResponse",
    "TelefoniaHandoffPayload",
    "TelefoniaIngresoRead",
    "TelefoniaCorpusDeleteResult",
]