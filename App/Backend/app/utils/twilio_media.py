"""
Descarga autenticada de la grabacion de Twilio (c-52).

Responsabilidad:
    Descarga el audio de una grabacion desde la URL provista por Twilio
    (`RecordingUrl`) usando autenticacion HTTP Basic con las credenciales de la
    cuenta (`AccountSid:AuthToken`). La URL admite seleccionar el formato
    (`.wav` o `.mp3`).

Diseno:
    El cliente HTTP es INYECTABLE, de modo que los tests ejercitan el flujo sin
    red (`httpx.MockTransport`). Cuando no se inyecta, se crea un
    `httpx.AsyncClient` por descarga con un timeout configurable.

    La descarga SOLO debe invocarse despues de que la guarda de costo reservo la
    superficie de transcripcion (design.md D6); este modulo no decide eso.

Referencias:
    design.md D2, D6
    specs/telefonia-stt-intake/spec.md (descarga autenticada de la grabacion)
"""

from __future__ import annotations

import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)

_ALLOWED_EXTENSIONS: frozenset[str] = frozenset({"wav", "mp3"})
_DEFAULT_TIMEOUT_SECONDS = 30.0


class TwilioMediaError(Exception):
    """Error base de la descarga de media de Twilio."""

    def __init__(self, message: str, *, details: dict | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:  # pragma: no cover - representacion
        return self.message


class TwilioMediaConfigError(TwilioMediaError):
    """Credenciales de Twilio no configuradas (fail-closed)."""


class TwilioMediaDownloadError(TwilioMediaError):
    """La descarga fallo (estado no exitoso, timeout u otro error HTTP)."""


def build_recording_url(recording_url: str, extension: str = "wav") -> str:
    """
    Construye la URL de descarga con la extension solicitada.

    Twilio permite pedir un formato especifico agregando `.wav` o `.mp3` a la
    `RecordingUrl`. Si la URL ya declara una extension soportada, se reemplaza
    en lugar de duplicarla.

    Args:
        recording_url: URL base de la grabacion provista por Twilio.
        extension:     `wav` (por defecto) o `mp3`.

    Returns:
        La URL con la extension indicada.

    Raises:
        ValueError: si la extension no esta soportada.
    """
    ext = extension.lower().lstrip(".")
    if ext not in _ALLOWED_EXTENSIONS:
        raise ValueError(f"Extension de grabacion no soportada: {extension!r}")

    base = recording_url
    for known in _ALLOWED_EXTENSIONS:
        suffix = f".{known}"
        if base.lower().endswith(suffix):
            base = base[: -len(suffix)]
            break
    return f"{base}.{ext}"


class TwilioMediaClient:
    """Descarga autenticada (Basic) de la grabacion de Twilio."""

    def __init__(
        self,
        account_sid: str,
        auth_token: str,
        http_client: httpx.AsyncClient | None = None,
        timeout: float = _DEFAULT_TIMEOUT_SECONDS,
    ) -> None:
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._http_client = http_client
        self._timeout = timeout

    async def download(self, recording_url: str, extension: str = "wav") -> bytes:
        """
        Descarga la grabacion y devuelve su contenido binario.

        Args:
            recording_url: URL base de la grabacion (`RecordingUrl`).
            extension:     formato de descarga (`wav` por defecto, o `mp3`).

        Returns:
            Contenido binario de la grabacion.

        Raises:
            TwilioMediaConfigError:   si faltan las credenciales.
            TwilioMediaDownloadError: si la descarga falla.
        """
        if not self._account_sid or not self._auth_token:
            raise TwilioMediaConfigError(
                "Credenciales de Twilio no configuradas para descargar la grabacion."
            )

        url = build_recording_url(recording_url, extension)
        auth = httpx.BasicAuth(self._account_sid, self._auth_token)

        try:
            if self._http_client is not None:
                response = await self._http_client.get(url, auth=auth)
            else:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.get(url, auth=auth)
        except httpx.TimeoutException as exc:
            logger.error("twilio_media_timeout", error_class=type(exc).__name__)
            raise TwilioMediaDownloadError(
                "Timeout al descargar la grabacion de Twilio."
            ) from exc
        except httpx.HTTPError as exc:
            logger.error("twilio_media_http_error", error_class=type(exc).__name__)
            raise TwilioMediaDownloadError(
                "Fallo la descarga de la grabacion de Twilio."
            ) from exc

        if response.status_code >= 400:
            logger.error(
                "twilio_media_bad_status", status_code=response.status_code
            )
            raise TwilioMediaDownloadError(
                "Descarga de la grabacion no exitosa.",
                details={"status_code": response.status_code},
            )

        return response.content


__all__ = [
    "TwilioMediaClient",
    "TwilioMediaError",
    "TwilioMediaConfigError",
    "TwilioMediaDownloadError",
    "build_recording_url",
]