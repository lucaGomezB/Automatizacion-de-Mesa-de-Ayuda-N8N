"""
Derivacion del identificador de origen para los eventos del guarda de costo.

El numero de origen CRUDO es dato personal: NO se emite en los eventos
estructurados (gap 5.34/8.12, change c-66). En su lugar se emite un
identificador DERIVADO no reversible, apto para correlacionar llamadas del
mismo origen dentro de la ventana de conteo sin exponer el numero.

La derivacion es HMAC-SHA-256 con una clave de configuracion DEDICADA
(`cost_guard_caller_hmac_key`), truncada a una longitud corta. NO reutiliza ni
deriva material de la clave Fernet de pseudonimizacion (decision D1/D9): una
clave de un solo proposito evita compartir material entre primitivas y
desacopla la rotacion de la pseudonimizacion de los identificadores de log.
"""

import hashlib
import hmac

# Longitud del identificador truncado (caracteres hex). Mantiene colisiones
# improbables para el volumen del piloto; se puede subir sin cambiar el contrato.
DEFAULT_IDENTIFIER_LENGTH = 12


def derive_caller_identifier(
    caller: str,
    hmac_key: str,
    *,
    length: int = DEFAULT_IDENTIFIER_LENGTH,
) -> str:
    """
    Deriva un identificador no reversible del numero de origen.

    Args:
        caller: numero de origen CRUDO (dato personal que nunca se emite).
        hmac_key: clave DEDICADA (`cost_guard_caller_hmac_key`), independiente
            de la clave de pseudonimizacion.
        length: cantidad de caracteres hexadecimales del identificador.

    Returns:
        Identificador determinista bajo la misma clave y el mismo numero; no
        permite recuperar el numero CRUDO con la informacion del log.
    """
    digest = hmac.new(
        hmac_key.encode("utf-8"),
        caller.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()
    return digest[:length]


__all__ = ["derive_caller_identifier", "DEFAULT_IDENTIFIER_LENGTH"]
