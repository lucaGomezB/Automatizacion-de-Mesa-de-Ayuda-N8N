"""
Renderizado de TwiML para el webhook de voz pre-llamada de Twilio.

c-52: el backend pasa a ser dueno de la descarga y la transcripcion (STT).
El `<Record>` graba en modo MONO (ya no se usa Twilio Batch Transcription),
declara la URL de callback de estado de grabacion y la accion posterior a la
finalizacion, y ELIMINA `transcribe="true"` (reconocimiento de voz embebido de
Twilio, limitado a ingles estadounidense).

El `<Say>` de cierre se sirve en el documento `action`
(`render_twiml_record_complete`), porque con `action` declarado Twilio redirige
a esa URL al terminar la grabacion y un `<Say>` inline tras `<Record>` no se
reproduciria. Ese mensaje NO promete la creacion inmediata del ticket: el alta
es asincrona (el backend transcribe, pseudonimiza y hace handoff a n8n).

Los callbacks se construyen desde `settings.backend_public_base_url` (o desde
`base_url` inyectado, para los tests). El texto es estatico (sin interpolacion
de datos del llamador), de modo que no hay riesgo de inyeccion en el XML.
"""

from app.config.settings import get_settings

_XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

# Rutas publicas de los callbacks de Twilio (prefijo /api/v1).
_STATUS_PATH = "/api/v1/telefonia/recording-status"
_ACTION_PATH = "/api/v1/telefonia/record-complete"

TWIML_MEDIA_TYPE = "text/xml"


def _resolve_base_url(base_url: str | None) -> str:
    """Resuelve la base publica del backend, sin barra final duplicada."""
    if base_url is None:
        base_url = get_settings().backend_public_base_url
    return base_url.rstrip("/")


def render_twiml_allowed(base_url: str | None = None) -> str:
    """
    TwiML que graba la llamada en MONO con señales de estado y fin.

    Sin `transcribe`: la transcripcion la realiza el backend con el motor
    dedicado de speech-to-text, no el reconocimiento embebido de Twilio.
    """
    base = _resolve_base_url(base_url)
    return (
        _XML_HEADER
        + "<Response>"
        + '<Say voice="Polly.Mia-Neural" language="es-US">'
        + "Bienvenido a la mesa de ayuda. "
        + "Describi tu problema despues del tono. "
        + "Cuando termines, presiona numeral. "
        + "Tenes hasta cuarenta y cinco segundos."
        + "</Say>"
        + '<Record maxLength="45" finishOnKey="#" playBeep="true" '
        + f'recordingStatusCallback="{base}{_STATUS_PATH}" '
        + f'action="{base}{_ACTION_PATH}"/>'
        + "</Response>"
    )


def render_twiml_record_complete() -> str:
    """
    Documento `action`: mensaje de cierre ALCANZABLE tras la grabacion.

    No promete la creacion inmediata del ticket (el alta es asincrona): solo
    confirma la recepcion del mensaje.
    """
    return (
        _XML_HEADER
        + "<Response>"
        + '<Say voice="Polly.Mia-Neural" language="es-US">'
        + "Gracias. Estamos procesando tu mensaje. "
        + "Te vamos a contactar a la brevedad."
        + "</Say>"
        + "</Response>"
    )


def render_twiml_denied() -> str:
    """TwiML que rechaza la grabacion con un mensaje y cuelga la llamada."""
    return (
        _XML_HEADER
        + "<Response>"
        + '<Say voice="Polly.Mia-Neural" language="es-US">'
        + "El servicio no esta disponible en este momento. Intente mas tarde."
        + "</Say>"
        + "<Hangup/>"
        + "</Response>"
    )


__all__ = [
    "render_twiml_allowed",
    "render_twiml_record_complete",
    "render_twiml_denied",
    "TWIML_MEDIA_TYPE",
]