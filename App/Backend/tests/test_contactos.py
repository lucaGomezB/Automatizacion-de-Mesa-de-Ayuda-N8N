"""
Tests de normalizacion y validacion de datos de contacto (c-54, seccion 2).

Cubren:
    - Normalizacion de email a minusculas/trim y extraccion desde una
      estructura de remitente ("Nombre <direccion>").
    - Normalizacion de telefono a E.164 (con o sin codigo de pais).
    - Validacion accionable de formato (email malformado, telefono fuera de
      E.164) y rechazo explicito.
    - Idempotencia de la normalizacion (normalizar dos veces = mismo resultado).

Los normalizadores son funciones puras: no tocan base de datos, red ni
configuracion.
"""

import pytest

from app.utils.contactos import (
    es_email_valido,
    es_telefono_valido,
    normalizar_email,
    normalizar_telefono,
)

# ── Email ──────────────────────────────────────────────────────────────────────


def test_normalizar_email_minusculas_y_trim():
    """El email se normaliza a minusculas sin espacios en los bordes."""
    assert normalizar_email("  Juan.PEREZ@Empresa.COM  ") == "juan.perez@empresa.com"


def test_normalizar_email_extrae_direccion_efectiva():
    """Acepta una estructura de remitente del canal de correo y extrae la direccion."""
    assert normalizar_email("Juan Perez <JPerez@Empresa.com>") == "jperez@empresa.com"


def test_normalizar_email_malformado_lanza_value_error():
    """Un email sin forma basica valida es rechazado con un error accionable."""
    with pytest.raises(ValueError):
        normalizar_email("no-es-un-email")
    with pytest.raises(ValueError):
        normalizar_email("sin@dominio")
    with pytest.raises(ValueError):
        normalizar_email("")


def test_es_email_valido():
    """El validador acepta direcciones bien formadas y rechaza las malformadas."""
    assert es_email_valido("a@b.com") is True
    assert es_email_valido("  A@B.COM  ") is True
    assert es_email_valido("sin-arroba") is False
    assert es_email_valido("a@b") is False


def test_normalizar_email_es_idempotente():
    """Normalizar un valor ya normalizado devuelve el mismo valor."""
    normalizado = normalizar_email("  A@B.COM ")
    assert normalizar_email(normalizado) == normalizado


# ── Telefono ───────────────────────────────────────────────────────────────────


def test_normalizar_telefono_e164_internacional():
    """Un numero internacional con separadores se compacta a E.164."""
    assert normalizar_telefono("+54 9 11 1234-5678") == "+5491112345678"
    assert normalizar_telefono("+54 (11) 1234.5678") == "+541112345678"


def test_normalizar_telefono_prefijo_00():
    """El prefijo internacional 00 se reemplaza por +."""
    assert normalizar_telefono("005491112345678") == "+5491112345678"


def test_normalizar_telefono_local_agrega_codigo_de_pais():
    """Un numero local argentino se normaliza agregando el codigo de pais."""
    assert normalizar_telefono("01112345678") == "+541112345678"


def test_normalizar_telefono_invalido_lanza_value_error():
    """Un telefono fuera de E.164 es rechazado con error accionable."""
    with pytest.raises(ValueError):
        normalizar_telefono("123")
    with pytest.raises(ValueError):
        normalizar_telefono("")
    with pytest.raises(ValueError):
        normalizar_telefono("abc")


def test_es_telefono_valido():
    """El validador E.164 acepta numeros normalizados y rechaza el resto."""
    assert es_telefono_valido("+5491112345678") is True
    assert es_telefono_valido("+1") is False
    assert es_telefono_valido("5491112345678") is False
    assert es_telefono_valido("+0123456789") is False


def test_normalizar_telefono_es_idempotente():
    """Normalizar un telefono ya normalizado devuelve el mismo valor."""
    normalizado = normalizar_telefono("+54 9 11 1234-5678")
    assert normalizar_telefono(normalizado) == normalizado
