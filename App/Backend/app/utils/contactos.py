"""
Normalizadores y validadores de datos de contacto (c-54).

Responsabilidad:
    Provee funciones puras para normalizar y validar los datos de contacto del
    directorio de empleados: email (minusculas/trim y extraccion de la direccion
    efectiva de una estructura de remitente) y telefono (formato E.164).

Diseno (D4/D6 del design de c-54):
    El contacto se almacena en TEXTO PLANO. La normalizacion es determinista e
    idempotente: el valor normalizado es el que se persiste y el que se usa para
    la comparacion por igualdad. NO hay cifrado de aplicacion ni indice ciego.

    Estas funciones no acceden a base de datos, red ni configuracion: son
    puramente funcionales y por eso se testean de forma aislada.
"""

import re

# Forma basica de un email: usuario@dominio.tld, sin espacios.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# Estructura de remitente "Nombre Apellido <direccion@dominio.tld>".
_EMAIL_ANGLE_RE = re.compile(r"<([^<>]+)>")

# E.164: '+' seguido de 7 a 15 digitos, el primero distinto de cero.
_E164_RE = re.compile(r"^\+[1-9]\d{6,14}$")

# Codigo de pais por defecto (Argentina). Configurable por parametro.
_PAIS_POR_DEFECTO = "54"


def _extraer_direccion(valor: str) -> str:
    """Extrae la direccion efectiva de un email o estructura de remitente."""
    match = _EMAIL_ANGLE_RE.search(valor)
    if match:
        return match.group(1).strip()
    return valor.strip()


def es_email_valido(valor: str | None) -> bool:
    """
    Indica si el valor tiene forma basica de email.

    No valida la existencia del dominio ni del buzon: solo la forma
    (usuario@dominio.tld). La comparacion ignora espacios externos.
    """
    if not valor or not isinstance(valor, str):
        return False
    return bool(_EMAIL_RE.match(_extraer_direccion(valor)))


def normalizar_email(valor: str | None) -> str:
    """
    Normaliza un email a minusculas/trim, extrayendo la direccion efectiva.

    Args:
        valor: direccion simple o estructura de remitente del canal de correo.

    Returns:
        El email normalizado (minusculas, sin espacios).

    Raises:
        ValueError: si el valor no tiene forma basica de email.
    """
    if not valor or not isinstance(valor, str):
        raise ValueError("El email es obligatorio y debe ser una cadena.")
    direccion = _extraer_direccion(valor).lower()
    if not _EMAIL_RE.match(direccion):
        raise ValueError(
            f"El email '{valor}' no tiene un formato valido (usuario@dominio.tld)."
        )
    return direccion


def es_telefono_valido(valor: str | None) -> bool:
    """
    Indica si el valor ya esta en formato E.164 (+ y 7 a 15 digitos).

    Es un validador estricto del formato almacenado, no un normalizador.
    """
    if not valor or not isinstance(valor, str):
        return False
    return bool(_E164_RE.match(valor.strip()))


def normalizar_telefono(
    valor: str | None, codigo_pais: str = _PAIS_POR_DEFECTO
) -> str:
    """
    Normaliza un numero telefonico a formato E.164.

    Acepta numeros internacionales (prefijo '+' o '00'), numeros locales con
    prefijo de marcado '0' y numeros con separadores (espacios, guiones,
    parentesis, puntos).

    Args:
        valor:       numero telefonico en cualquier formato razonable.
        codigo_pais: codigo de pais a anteponer cuando el numero es local.

    Returns:
        El numero normalizado en E.164 (ej. '+5491112345678').

    Raises:
        ValueError: si no contiene digitos suficientes o queda fuera de E.164.
    """
    if not valor or not isinstance(valor, str):
        raise ValueError("El telefono debe ser una cadena no vacia.")

    texto = valor.strip()
    digitos = re.sub(r"\D", "", texto)
    if not digitos:
        raise ValueError(f"El telefono '{valor}' no contiene digitos.")

    if texto.startswith("00"):
        # Prefijo internacional 00 → se descarta y se usa '+'.
        resultado = "+" + digitos[2:]
    elif texto.startswith("+"):
        resultado = "+" + digitos
    else:
        # Numero local/regional: se descarta el prefijo de marcado '0'
        # y se antepone el codigo de pais.
        local = digitos.lstrip("0") or digitos
        resultado = "+" + codigo_pais + local

    if not es_telefono_valido(resultado):
        raise ValueError(
            f"El telefono '{valor}' no se puede normalizar a un E.164 valido."
        )
    return resultado
