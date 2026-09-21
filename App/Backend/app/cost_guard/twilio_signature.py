"""
Validacion de la firma de webhooks de Twilio (`X-Twilio-Signature`).

Algoritmo documentado por Twilio (https://www.twilio.com/docs/usage/webhooks/webhooks-security)
y confirmado contra la implementacion de referencia del SDK oficial
(`twilio-python`, `twilio/request_validator.py`):

    1. Tomar la URL COMPLETA del webhook (incluidos los query params tal como
       los recibe Twilio, sin re-codificar).
    2. Ordenar alfabeticamente los nombres de los parametros de formulario.
       Para cada nombre, agregar `nombre + valor` (los valores multiples se
       ordenan y deduplican).
    3. Calcular HMAC-SHA1 sobre (URL + concatenacion de parametros) usando el
       auth token de la cuenta como clave y codificar en base64.

Twilio es inconsistente respecto del puerto en la URL firmada, por lo que la
validacion acepta tanto la URL con puerto (443/80 por defecto) como sin puerto,
igual que el SDK oficial.

Nota de version: la firma de webhooks usa HMAC-SHA1. El algoritmo SHA-256 que
aparece en la documentacion corresponde al hash del cuerpo JSON (`bodySHA256`),
NO a la firma; para webhooks `application/x-www-form-urlencoded` (el caso del
webhook de voz) se usa HMAC-SHA1.

Se implementa con `hmac`/`hashlib` de la stdlib y comparacion en tiempo
constante (`hmac.compare_digest`).
"""

import base64
import hmac
from collections.abc import Mapping
from hashlib import sha1
from typing import Any
from urllib.parse import urlsplit, urlunsplit


def _iter_values(params: Any, name: str) -> list[str]:
    """Valores asociados a un nombre, soportando multidicts (FormData/MultiDict)."""
    getall = getattr(params, "getall", None)
    if callable(getall):
        return [str(value) for value in getall(name)]
    getlist = getattr(params, "getlist", None)
    if callable(getlist):
        return [str(value) for value in getlist(name)]
    value = params[name]
    if isinstance(value, str):
        return [value]
    return [str(item) for item in value]


def compute_signature(
    auth_token: str, url: str, params: Mapping[str, Any] | Any
) -> str:
    """
    Calcula la firma HMAC-SHA1 que Twilio envia en `X-Twilio-Signature`.

    Args:
        auth_token: auth token de la cuenta de Twilio (clave del HMAC).
        url: URL completa del webhook (con query params incluidos).
        params: parametros de formulario recibidos (dict o multidict).

    Returns:
        Firma codificada en base64.
    """
    payload = url
    if params:
        for name in sorted(set(params)):
            for value in sorted(set(_iter_values(params, name))):
                payload += name + value
    mac = hmac.new(auth_token.encode("utf-8"), payload.encode("utf-8"), sha1)
    return base64.b64encode(mac.digest()).decode("utf-8").strip()


def _with_port(url: str, port: int) -> str:
    """URL con el puerto por defecto agregado cuando no lo declara."""
    parts = urlsplit(url)
    netloc = parts.netloc
    host = netloc.rsplit("@", 1)[-1]
    if ":" in host:
        return url
    return urlunsplit(
        (parts.scheme, f"{netloc}:{port}", parts.path, parts.query, parts.fragment)
    )


def _without_port(url: str) -> str:
    """URL sin el puerto explicito cuando lo declara."""
    parts = urlsplit(url)
    netloc = parts.netloc
    userinfo = ""
    if "@" in netloc:
        userinfo, netloc = netloc.rsplit("@", 1)
        userinfo += "@"
    if ":" in netloc:
        netloc = netloc.split(":", 1)[0]
    return urlunsplit(
        (parts.scheme, f"{userinfo}{netloc}", parts.path, parts.query, parts.fragment)
    )


def verify_signature(
    auth_token: str,
    signature: str | None,
    url: str,
    params: Mapping[str, Any] | Any,
) -> bool:
    """
    Verifica la firma de Twilio en tiempo constante.

    Acepta la URL con y sin puerto para tolerar la inconsistencia del backend
    de Twilio al firmar, replicando el comportamiento del SDK oficial.
    """
    if not signature:
        return False

    default_port = 443 if url.lower().startswith("https") else 80
    candidates = {compute_signature(auth_token, url, params)}
    try:
        candidates.add(
            compute_signature(auth_token, _with_port(url, default_port), params)
        )
    except ValueError:  # URL no parseable: se conserva el candidato original
        pass
    try:
        candidates.add(compute_signature(auth_token, _without_port(url), params))
    except ValueError:
        pass

    provided = signature.encode("utf-8")
    return any(
        hmac.compare_digest(provided, candidate.encode("utf-8"))
        for candidate in candidates
    )


__all__ = ["compute_signature", "verify_signature"]