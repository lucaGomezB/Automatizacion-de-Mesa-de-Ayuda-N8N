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

c-156 (PRIV-003): el `<Say>` de la llamada admitida abre con el aviso de
privacidad del canal telefonico (grabacion, finalidad, responsable,
transferencia internacional y derechos del titular), como parte del deber de
informacion de la Ley 25.326 art. 6. El aviso es texto estatico, no recolecta
datos del llamante y no promete el alta inmediata del incidente.
"""

import re

from app.config.settings import get_settings

_XML_HEADER = '<?xml version="1.0" encoding="UTF-8"?>'

# Rutas publicas de los callbacks de Twilio (prefijo /api/v1).
_STATUS_PATH = "/api/v1/telefonia/recording-status"
_ACTION_PATH = "/api/v1/telefonia/record-complete"

# Tasa de locucion del aviso (c-175): forma porcentual acotada a 20-200%.
# La validacion vive en la frontera del XML: el valor saneado solo se usa como
# atributo `rate`; nunca se interpola en el TEXTO del aviso.
_RATE_PATTERN = re.compile(r"^\d{1,3}%$")
_RATE_MIN = 20
_RATE_MAX = 200

TWIML_MEDIA_TYPE = "text/xml"


def _resolve_base_url(base_url: str | None) -> str:
    """Resuelve la base publica del backend, sin barra final duplicada."""
    if base_url is None:
        base_url = get_settings().backend_public_base_url
    return base_url.rstrip("/")


def _normalize_rate(rate: str | None) -> str | None:
    """
    Normaliza la tasa de locucion del `<Say>` a un porcentaje saneado.

    Devuelve un valor `"<n>%"` dentro del rango 20-200% o `None` cuando no hay
    tasa utilizable (ausente o con formato invalido). El resultado solo se usa
    como atributo `rate`, de modo que la validacion impide la inyeccion de XML
    o de valores no acotados.
    """
    if rate is None:
        return None
    candidate = rate.strip()
    if not _RATE_PATTERN.match(candidate):
        return None
    value = int(candidate[:-1])
    value = max(_RATE_MIN, min(_RATE_MAX, value))
    return f"{value}%"


# Aviso de privacidad del canal telefonico (c-156, PRIV-003). Texto ESTATICO:
# no interpola datos del llamante, de modo que no hay riesgo de inyeccion.
_NOTICE_TEXT = (
    "Esta llamada sera grabada. "
    "La finalidad del tratamiento es registrar y clasificar su incidente de mesa de ayuda. "
    "El responsable del tratamiento es el grupo de desarrollo del sistema. "
    "Sus datos pueden ser objeto de transferencia internacional a Estados Unidos para el procesamiento automatizado. "
    "Usted puede ejercer sus derechos de acceso, rectificacion y supresion conforme a la politica de privacidad. "
    "El sistema esta alineado con la Ley 25.326. "
    "Bienvenido a la mesa de ayuda. "
    "Describí tu problema después del tono. "
    "Cuando termines, cuelga la llamada. "
    "En unos minutos vas a recibir una notificación con el número de incidente."
)

_SAY_OPEN = '<Say voice="Polly.Mia-Neural" language="es-US">'
_SAY_CLOSE = "</Say>"


def _render_notice_say(rate: str | None) -> str:
    """
    `<Say>` del aviso, opcionalmente envuelto en `<prosody rate="...">`.

    `rate` es el valor YA saneado (o `None`): la validacion no vive aqui.
    """
    if rate is None:
        content = _NOTICE_TEXT
    else:
        content = f'<prosody rate="{rate}">{_NOTICE_TEXT}</prosody>'
    return _SAY_OPEN + content + _SAY_CLOSE


def render_twiml_allowed(
    base_url: str | None = None, rate: str | None = None
) -> str:
    """
    TwiML que graba la llamada en MONO con señales de estado y fin.

    Sin `transcribe`: la transcripcion la realiza el backend con el motor
    dedicado de speech-to-text, no el reconocimiento embebido de Twilio.

    c-175: `rate` opcional ajusta la tasa de locucion del aviso. Cuando es
    valido, el contenido del `<Say>` se envuelve en `<prosody rate="...">`.
    Cuando esta ausente o es invalido, la salida es byte-identica a la vigente
    (tasa normal), de modo que el aviso de produccion no cambia. El TEXTO del
    aviso nunca cambia.
    """
    base = _resolve_base_url(base_url)
    say = _render_notice_say(_normalize_rate(rate))
    return (
        _XML_HEADER
        + "<Response>"
        + say
        + '<Record maxLength="45" finishOnKey="#" playBeep="true" '
        + 'channels="mono" '
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