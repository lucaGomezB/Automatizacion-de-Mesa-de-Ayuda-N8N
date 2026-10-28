"""
Indice ciego determinista del directorio (c-153, Tema B — DIR-011/DIR-012).

Responsabilidad:
    Derivar un indice ciego determinista (HMAC-SHA-256, hexadecimal) de la forma
    NORMALIZADA del contacto del directorio. Como el cifrado Fernet de
    `EncryptedText` NO es determinista (IV aleatorio), la igualdad SQL sobre la
    columna cifrada no sirve para buscar; el repositorio resuelve por estas
    columnas derivadas (`email_bidx`, `telefono_bidx`).

Decision (design.md D2/D3):
    - HMAC-SHA-256 con una clave DEDICADA (`directory_blind_index_key`),
      independiente de la clave Fernet de pseudonimizacion. Un hash SIN clave
      (SHA-256 puro) seria vulnerable a diccionario porque el espacio de
      email/telefono es enumerable.
    - La unicidad del email se preserva creando un indice UNIQUE sobre
      `email_bidx`; el telefono es repetible (`telefono_bidx` sin UNIQUE).

Pureza (tarea 3.5):
    Las funciones `derivar_indice_ciego`, `indice_ciego_email` e
    `indice_ciego_telefono` son PURAS (reciben la clave como parametro, no
    acceden a configuracion) y por eso se testean de forma aislada. Los wrappers
    `email_blind_index` y `telefono_blind_index` resuelven la clave desde
    `Settings` para el uso en la capa de modelo y de repositorio.

Tolerancia de normalizacion:
    La normalizacion es IDEMPOTENTE y TOLERANTE: el servicio rechaza el contacto
    mal formado ANTES de persistir, pero una fila legada o insertada fuera de la
    aplicacion con un valor no normalizable no debe romper la derivacion. Ante un
    valor invalido, se usa una forma canonica de respaldo (trim + minusculas para
    el email; trim para el telefono) para que el digest siga siendo determinista.
"""

import hashlib
import hmac

from app.config.settings import get_settings
from app.utils.contactos import normalizar_email, normalizar_telefono


def derivar_indice_ciego(valor_normalizado: str, clave: str) -> str:
    """
    Deriva el indice ciego de un valor YA normalizado.

    Es una funcion PURA y determinista: el mismo valor normalizado y la misma
    clave producen siempre el mismo digest; una clave distinta produce un digest
    distinto (dependencia de clave del HMAC).

    Args:
        valor_normalizado: valor en su forma normalizada (minusculas/trim para el
            email; E.164 para el telefono).
        clave:             clave dedicada del indice ciego.

    Returns:
        El digest HMAC-SHA-256 en hexadecimal (64 caracteres).
    """
    return hmac.new(
        clave.encode("utf-8"),
        valor_normalizado.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()


def _email_normalizado(email: str) -> str:
    """Normaliza el email; ante un valor invalido usa trim + minusculas."""
    try:
        return normalizar_email(email)
    except ValueError:
        return str(email).strip().lower()


def _telefono_normalizado(telefono: str) -> str:
    """Normaliza el telefono a E.164; ante un valor invalido usa trim."""
    try:
        return normalizar_telefono(telefono)
    except ValueError:
        return str(telefono).strip()


def indice_ciego_email(email: str, clave: str) -> str:
    """Normaliza el email y deriva su indice ciego (funcion pura)."""
    return derivar_indice_ciego(_email_normalizado(email), clave)


def indice_ciego_telefono(telefono: str, clave: str) -> str:
    """Normaliza el telefono a E.164 y deriva su indice ciego (funcion pura)."""
    return derivar_indice_ciego(_telefono_normalizado(telefono), clave)


def email_blind_index(email: str) -> str:
    """Deriva el `email_bidx` con la clave dedicada de `Settings`."""
    return indice_ciego_email(email, get_settings().directory_blind_index_key)


def telefono_blind_index(telefono: str | None) -> str | None:
    """Deriva el `telefono_bidx` con la clave dedicada; None -> None."""
    if telefono is None or not str(telefono).strip():
        return None
    return indice_ciego_telefono(telefono, get_settings().directory_blind_index_key)