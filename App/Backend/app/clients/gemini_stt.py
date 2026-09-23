"""
Cliente de speech-to-text dedicado del backend (Gemini, modo verbatim) — c-52.

Responsabilidad:
    Transcribe el audio de una grabacion de Twilio usando el modelo dedicado
    de transcripcion de Gemini. Se aisla en un cliente propio para no acoplar
    el clasificador hibrido a la transcripcion y para facilitar la inyeccion
    de un cliente simulado en los tests (design.md D2, D10).

API (google-genai >= 2.20.0):
    - `client.aio.files.upload(file=..., config={"mime_type": ...})` sube el
      audio y devuelve un archivo con `uri`.
    - `client.aio.interactions.create(model=..., input=[AudioContent], ...,
      generation_config=GenerationConfig(transcription_config=...), store=False)`
      devuelve una `Interaction` cuyo `output_text` es el transcript.

Config verbatim:
    `mode=VerbatimTranscriptionMode(timestamp_granularities=["word"])` evita el
    resumen/alucinacion del modo smart; `language_codes=["es-419"]` (espanol
    latinoamericano, cubre Argentina; `es-AR` NO esta soportado).

Frontera de PII:
    Este cliente solo PRODUCE el texto crudo. La pseudonimizacion ocurre
    inmediatamente despues, en el servicio, antes de cualquier handoff
    (design.md D9).

Referencias:
    design.md D2, D10
    specs/telefonia-stt-intake/spec.md (transcripcion con motor dedicado)
"""

from __future__ import annotations

import io
from typing import Sequence

from google.genai import interactions as genai_interactions

from app.classifiers.gemini_classifier import get_genai_client
from app.config.settings import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Espanol latinoamericano: cubre Argentina. `es-AR` NO esta soportado.
DEFAULT_LANGUAGE_CODES: tuple[str, ...] = ("es-419",)
DEFAULT_MIME_TYPE = "audio/wav"


class SttTranscriptionError(Exception):
    """
    Fallo explicito de la transcripcion (cliente o respuesta vacia).

    Se lanza en lugar de devolver un string vacio en silencio, de modo que el
    servicio pueda persistir el ingreso con estado de error y detalle
    (design.md D11).
    """

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:  # pragma: no cover - representacion
        return self.message


class GeminiSttClient:
    """Transcribe audio con el modelo dedicado de Gemini (verbatim)."""

    def __init__(
        self,
        client: object | None = None,
        model: str | None = None,
        language_codes: Sequence[str] | None = None,
    ) -> None:
        """
        Args:
            client: cliente de Gemini inyectable (por defecto, el compartido
                    a nivel de proceso). Los tests inyectan un doble.
            model:  nombre del modelo (por defecto, `settings.gemini_stt_model`).
            language_codes: codigos BCP-47 (por defecto, `["es-419"]`).
        """
        self._client = client if client is not None else get_genai_client()
        settings = get_settings()
        self._model = model or settings.gemini_stt_model
        self._language_codes = (
            list(language_codes)
            if language_codes is not None
            else list(DEFAULT_LANGUAGE_CODES)
        )

    @property
    def model(self) -> str:
        """Modelo configurado para la transcripcion."""
        return self._model

    async def transcribe(
        self, audio_bytes: bytes, mime_type: str = DEFAULT_MIME_TYPE
    ) -> str:
        """
        Sube y transcribe el audio en modo verbatim.

        Args:
            audio_bytes: contenido binario de la grabacion.
            mime_type:   tipo MIME del audio (por defecto `audio/wav`).

        Returns:
            El texto transcripto, no vacio.

        Raises:
            SttTranscriptionError: si el cliente falla o la respuesta es vacia.
        """
        try:
            uploaded = await self._client.aio.files.upload(
                file=io.BytesIO(audio_bytes),
                config={"mime_type": mime_type},
            )
            generation_config = genai_interactions.GenerationConfig(
                transcription_config=genai_interactions.TranscriptionConfig(
                    mode=genai_interactions.VerbatimTranscriptionMode(
                        timestamp_granularities=["word"],
                    ),
                    language_codes=list(self._language_codes),
                ),
            )
            interaction = await self._client.aio.interactions.create(
                model=self._model,
                input=[
                    {
                        "type": "audio",
                        "uri": uploaded.uri,
                        "mime_type": mime_type,
                    }
                ],
                generation_config=generation_config,
                store=False,
            )
        except SttTranscriptionError:
            raise
        except Exception as exc:
            logger.error(
                "gemini_stt_failed",
                model=self._model,
                error_class=type(exc).__name__,
            )
            raise SttTranscriptionError(
                "La transcripcion fallo.", details={"error_class": type(exc).__name__}
            ) from exc

        texto = getattr(interaction, "output_text", None)
        if not texto or not texto.strip():
            logger.error("gemini_stt_empty_response", model=self._model)
            raise SttTranscriptionError(
                "La transcripcion devolvio una respuesta vacia."
            )
        return texto.strip()


__all__ = [
    "GeminiSttClient",
    "SttTranscriptionError",
    "DEFAULT_LANGUAGE_CODES",
    "DEFAULT_MIME_TYPE",
]