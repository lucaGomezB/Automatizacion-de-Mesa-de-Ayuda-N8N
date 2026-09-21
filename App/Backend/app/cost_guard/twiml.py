"""
Renderizado de TwiML para el webhook de voz pre-llamada de Twilio.

Contiene el contenido exacto de `n8n/twilio/twiml.xml` para la respuesta que
permite grabar con transcripcion, y la respuesta que rechaza y cuelga. El texto
es estatico (sin interpolacion de datos del llamador), de modo que no hay riesgo
de inyeccion en el XML.
"""

_ALLOWED_TWIML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Response>"
    '<Say voice="Polly.Mia-Neural" language="es-US">'
    "Bienvenido a la mesa de ayuda. "
    "Describi tu problema despues del tono. "
    "Cuando termines, presiona numeral. "
    "Tenes hasta cuarenta y cinco segundos."
    "</Say>"
    '<Record maxLength="45" finishOnKey="#" transcribe="true" playBeep="true"/>'
    '<Say voice="Polly.Mia-Neural" language="es-US">'
    "Gracias. Tu incidente fue registrado. "
    "Vas a recibir un numero de ticket por correo."
    "</Say>"
    "</Response>"
)

_DENIED_TWIML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    "<Response>"
    '<Say voice="Polly.Mia-Neural" language="es-US">'
    "El servicio no esta disponible en este momento. Intente mas tarde."
    "</Say>"
    "<Hangup/>"
    "</Response>"
)

TWIML_MEDIA_TYPE = "text/xml"


def render_twiml_allowed() -> str:
    """TwiML que graba la llamada con transcripcion habilitada."""
    return _ALLOWED_TWIML


def render_twiml_denied() -> str:
    """TwiML que rechaza la grabacion con un mensaje y cuelga la llamada."""
    return _DENIED_TWIML


__all__ = ["render_twiml_allowed", "render_twiml_denied", "TWIML_MEDIA_TYPE"]
