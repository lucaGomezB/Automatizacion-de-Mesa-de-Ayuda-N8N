"""
Servicio de ingreso asincronico del canal de telefonia (c-52).

Responsabilidad:
    Orquesta el flujo de ingreso de una llamada a partir del callback de estado
    de grabacion de Twilio, en este orden estricto (design.md D4, D6, D8, D9,
    D11; specs/telefonia-stt-intake/spec.md):

        1. Idempotencia por `CallSid` ANTES de cualquier llamada paga.
        2. Sellado de `ingresado_en` (antes de descargar y transcribir).
        3. Reserva de la superficie paga `backend_stt` estimada por duracion
           (cap 45 s) ANTES de descargar.
        4. Descarga autenticada de la grabacion.
        5. Transcripcion con el motor dedicado (Gemini verbatim).
        6. Pseudonimizacion INMEDIATA (antes de cualquier entrega a n8n).
        7. Persistencia cifrada del ingreso (doble representacion).
        8. Handoff autenticado a n8n, fire-and-forget.

Frontera de PII:
    El transcript crudo queda cifrado en `telefonia_ingreso`; la unica
    representacion que cruza el borde hacia n8n es la pseudonimizada.

Manejo de fallos:
    La guarda denegada, el fallo de descarga y el fallo de STT NO abortan ni
    descartan el ingreso: se persiste el estado explicito y el detalle para
    reintento o revision humana (design.md D11).

Referencias:
    design.md D4, D6, D8, D9, D10, D11
    specs/telefonia-stt-intake/spec.md
"""

from __future__ import annotations

import asyncio
from decimal import Decimal
from typing import Awaitable, Callable

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.gemini_stt import GeminiSttClient, SttTranscriptionError
from app.config.settings import Settings, get_settings
from app.core.logging import get_logger
from app.cost_guard.clock import SystemClock
from app.cost_guard.constants import PROVIDER_BACKEND_STT
from app.cost_guard.decision import GuardDecision
from app.cost_guard.protocols import Clock
from app.models.telefonia_ingreso import TelefoniaIngreso, TranscripcionEstado
from app.repositories.telefonia_ingreso_repository import TelefoniaIngresoRepository
from app.schemas.telefonia import RecordingStatusCallback
from app.services.cost_guard_service import CostGuardService
from app.utils.n8n_webhook import (
    build_telefonia_handoff_payload,
    notify_telefonia_handoff,
)
from app.utils.pseudonymizer import pseudonymize
from app.utils.twilio_media import TwilioMediaClient, TwilioMediaError

logger = get_logger(__name__)

# Tope de duracion de la grabacion, consistente con `maxLength="45"` del
# `<Record>` (design.md D6). La reserva de `backend_stt` se estima como
# `min(duracion, 45) / 45` unidades del costo unitario.
STT_DURATION_CAP_SECONDS = 45
_PROVIDER = "gemini"

# Referencias retenidas de las tareas fire-and-forget del handoff (patron de
# `IncidenteService`): evita que el GC recolecte la tarea antes de completarse.
_handoff_tasks: set[asyncio.Task] = set()


def estimate_stt_amount(duracion_segundos: int | None) -> Decimal:
    """
    Estima la reserva de `backend_stt` a partir de la duracion de la grabacion.

    La duracion se acota al tope de 45 s. Una duracion ausente o no positiva se
    estima como una unidad completa (conservador).

    Args:
        duracion_segundos: duracion informada por Twilio (`RecordingDuration`).

    Returns:
        Cantidad de unidades del costo unitario a reservar.
    """
    if duracion_segundos is None or duracion_segundos <= 0:
        return Decimal(1)
    segundos = min(int(duracion_segundos), STT_DURATION_CAP_SECONDS)
    return Decimal(segundos) / Decimal(STT_DURATION_CAP_SECONDS)


def _dispatch_handoff(
    notifier: Callable[[dict], Awaitable[object]], payload: dict
) -> None:
    """Programa el handoff fire-and-forget conservando la referencia de la tarea."""
    task = asyncio.create_task(notifier(payload))
    _handoff_tasks.add(task)
    task.add_done_callback(_handoff_tasks.discard)


class TelefoniaService:
    """Orquesta el ingreso asincronico del canal de telefonia."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        cost_guard: CostGuardService | None = None,
        stt_client: GeminiSttClient | None = None,
        media_client: TwilioMediaClient | None = None,
        notifier: Callable[[dict], Awaitable[object]] | None = None,
        clock: Clock | None = None,
        settings: Settings | None = None,
    ) -> None:
        """
        Args:
            session:      sesion de base de datos de la solicitud.
            cost_guard:   servicio de la guarda de costo (reserva de `backend_stt`).
            stt_client:   cliente de speech-to-text (inyectable en tests).
            media_client: cliente de descarga autenticada de Twilio.
            notifier:     callable del handoff a n8n (inyectable en tests).
            clock:        fuente de tiempo inyectable (sellado de instantes).
            settings:     configuracion efectiva (inyectable en tests).
        """
        self._session = session
        self._ingreso_repo = TelefoniaIngresoRepository(session)
        self._settings = settings if settings is not None else get_settings()
        self._cost_guard = cost_guard
        self._stt = stt_client
        self._media = media_client
        self._notifier = notifier or notify_telefonia_handoff
        self._clock = clock or SystemClock()

    # ── API publica ─────────────────────────────────────────────────────────

    async def process_recording(
        self, callback: RecordingStatusCallback
    ) -> TelefoniaIngreso:
        """
        Procesa el callback de estado de grabacion de Twilio.

        Args:
            callback: parametros del callback ya validados por firma.

        Returns:
            El ingreso persistido, en cualquiera de sus estados (transcrito,
            error de descarga/STT o guarda denegada).
        """
        # 1. Idempotencia por CallSid ANTES de la reserva paga (design.md D8).
        existente = await self._ingreso_repo.get_by_call_sid(callback.call_sid)
        if existente is not None:
            logger.info(
                "telefonia_idempotente",
                call_sid=callback.call_sid,
                ingreso_id=existente.id,
            )
            return existente

        # 2. Sellar `ingresado_en` ANTES de descargar y transcribir (D4).
        ingresado_en = self._clock.now()

        # 3. Persistir el ingreso en estado pendiente (trazabilidad de fallos).
        stt_client = self._resolve_stt()
        try:
            ingreso = await self._ingreso_repo.create(
                call_sid=callback.call_sid,
                recording_sid=callback.recording_sid,
                caller_cifrado=callback.caller,
                duracion_segundos=callback.recording_duration,
                ingresado_en=ingresado_en,
                transcripcion_estado=TranscripcionEstado.pendiente,
                provider=_PROVIDER,
                model=stt_client.model,
            )
        except IntegrityError:
            # Carrera de callbacks concurrentes: el UNIQUE de `call_sid` gana.
            await self._session.rollback()
            existente = await self._ingreso_repo.get_by_call_sid(callback.call_sid)
            if existente is None:
                raise
            return existente

        # 4. Reservar `backend_stt` estimando por duracion (cap 45 s) (D6).
        amount = estimate_stt_amount(callback.recording_duration)
        decision = await self._reserve(amount, callback.caller)
        if not decision.allowed:
            return await self._persist_failure(
                ingreso,
                TranscripcionEstado.guarda_denegada,
                decision.cause or "guarda_denegada",
            )

        # 5. Descargar la grabacion autenticada (D2).
        try:
            audio = await self._resolve_media().download(callback.recording_url)
        except TwilioMediaError as exc:
            return await self._persist_failure(
                ingreso, TranscripcionEstado.error_descarga, exc.message
            )

        # 6. Transcribir con el motor dedicado (D2).
        try:
            texto = await stt_client.transcribe(audio)
        except SttTranscriptionError as exc:
            return await self._persist_failure(
                ingreso, TranscripcionEstado.error_stt, exc.message
            )

        # 7. Pseudonimizar INMEDIATAMENTE, antes de cualquier handoff (D9).
        resultado = pseudonymize(
            texto, self._settings.pseudonymization_internal_domains
        )
        ingreso.transcript_original = texto
        ingreso.descripcion_pseudonimizada = resultado.texto
        ingreso.transcripcion_estado = TranscripcionEstado.transcrito
        ingreso.persistido_en = self._clock.now()
        await self._session.flush()

        # 8. Handoff autenticado fire-and-forget con SOLO la pseudonimizada (D7).
        payload = build_telefonia_handoff_payload(
            descripcion_pseudonimizada=resultado.texto,
            call_sid=ingreso.call_sid,
            caller=callback.caller,
            ingresado_en=ingreso.ingresado_en,
        )
        _dispatch_handoff(self._notifier, payload)
        logger.info(
            "telefonia_transcrito",
            call_sid=ingreso.call_sid,
            ingreso_id=ingreso.id,
        )
        return ingreso

    # ── Helpers ─────────────────────────────────────────────────────────────

    async def _reserve(self, amount: Decimal, caller: str | None) -> GuardDecision:
        """Reserva `backend_stt`; sin guarda inyectada permite (tests/dev)."""
        if self._cost_guard is None:
            return GuardDecision(allowed=True, cause=None)
        return await self._cost_guard.reserve(
            PROVIDER_BACKEND_STT, caller=caller, amount=amount
        )

    async def _persist_failure(
        self,
        ingreso: TelefoniaIngreso,
        estado: TranscripcionEstado,
        detalle: str,
    ) -> TelefoniaIngreso:
        """Persiste un estado de fallo explicito sin abortar la ejecucion (D11)."""
        ingreso.transcripcion_estado = estado
        ingreso.error_detalle = detalle
        ingreso.persistido_en = self._clock.now()
        await self._session.flush()
        logger.warning(
            "telefonia_fallo",
            call_sid=ingreso.call_sid,
            estado=estado.value,
            detalle=detalle,
        )
        return ingreso

    def _resolve_stt(self) -> GeminiSttClient:
        if self._stt is None:
            self._stt = GeminiSttClient()
        return self._stt

    def _resolve_media(self) -> TwilioMediaClient:
        if self._media is None:
            self._media = TwilioMediaClient(
                self._settings.twilio_account_sid,
                self._settings.twilio_auth_token,
            )
        return self._media


__all__ = ["TelefoniaService", "estimate_stt_amount", "STT_DURATION_CAP_SECONDS"]