"""Clientes de integracion con servicios externos del backend (c-52)."""

from app.clients.gemini_stt import (
    DEFAULT_LANGUAGE_CODES,
    DEFAULT_MIME_TYPE,
    GeminiSttClient,
    SttTranscriptionError,
)

__all__ = [
    "GeminiSttClient",
    "SttTranscriptionError",
    "DEFAULT_LANGUAGE_CODES",
    "DEFAULT_MIME_TYPE",
]