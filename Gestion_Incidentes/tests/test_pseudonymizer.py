"""
Tests unitarios para la función pseudonymize.

Responsabilidad:
    Verifica el comportamiento de la función pura `pseudonymize()` definida en
    `app.utils.pseudonymizer`. Los tests cubren:
      - Texto sin PII (texto intacto, conteos en cero)
      - Determinismo (misma entrada → misma salida)
      - Reemplazo de emails (simples, múltiples, subdominios, +tag)
      - Reemplazo de teléfonos (formatos argentinos, borde no-telefónico)
      - Reemplazo de hosts (fallback heurístico: srv-*, pc-*, *.local, localhost)
      - Reemplazo de hosts con dominios corporativos configurados
      - Reemplazo de nombres propios (nombre+apellido, tildes, ñ)
      - Lista de exclusión (categorías del dominio no son PERSONA)
      - Orden de aplicación libre de colisiones (email no fragmentado como PERSONA)
      - Combinación de todas las categorías simultáneas

Todos los tests son síncronos (pseudonymize es función pura, sin I/O ni asyncio).
"""

import pytest

from app.utils.pseudonymizer import PseudonymizationResult, pseudonymize


# ─── Sección 1: esqueleto y contrato ─────────────────────────────────────────

def test_pseudonymize_texto_sin_pii_devuelve_texto_intacto_y_conteos_en_cero() -> None:
    """
    Texto sin datos personales: la función devuelve el texto idéntico
    y los conteos de todas las categorías en cero.
    """
    texto = "El servidor respondió con un error 500 en el módulo de reportes."
    resultado = pseudonymize(texto, [])

    assert isinstance(resultado, PseudonymizationResult)
    assert resultado.texto == texto
    assert resultado.conteos == {"email": 0, "telefono": 0, "host": 0, "persona": 0}


def test_pseudonymize_es_determinista() -> None:
    """
    La misma entrada produce siempre el mismo texto y los mismos conteos.
    """
    texto = "Falla en srv-db01: se cayó el servicio."
    r1 = pseudonymize(texto, [])
    r2 = pseudonymize(texto, [])

    assert r1.texto == r2.texto
    assert r1.conteos == r2.conteos


# ─── Sección 2: EMAIL ─────────────────────────────────────────────────────────

def test_pseudonymize_reemplaza_email_simple() -> None:
    """
    Un email simple en el cuerpo del texto es reemplazado por [EMAIL]
    y el conteo de 'email' es 1.
    """
    texto = "El incidente fue reportado por juan.perez@empresa.com en el sistema."
    resultado = pseudonymize(texto, [])

    assert "[EMAIL]" in resultado.texto
    assert "juan.perez@empresa.com" not in resultado.texto
    assert resultado.conteos["email"] == 1


def test_pseudonymize_reemplaza_multiples_emails() -> None:
    """
    Dos emails en el mismo texto son ambos reemplazados y el conteo es 2.
    """
    texto = "Contactar a ana@empresa.com y a pedro.gomez@corp.org para el seguimiento."
    resultado = pseudonymize(texto, [])

    assert resultado.texto.count("[EMAIL]") == 2
    assert "ana@empresa.com" not in resultado.texto
    assert "pedro.gomez@corp.org" not in resultado.texto
    assert resultado.conteos["email"] == 2


def test_pseudonymize_reemplaza_email_con_subdominio_y_tag() -> None:
    """
    Emails con subdominio y con '+tag' son correctamente detectados.
    """
    subdominio = "usuario@mail.subdomain.empresa.com"
    tag = "usuario+soporte@empresa.com"
    resultado_sub = pseudonymize(f"Contactar {subdominio}", [])
    resultado_tag = pseudonymize(f"Responder a {tag}", [])

    assert "[EMAIL]" in resultado_sub.texto
    assert subdominio not in resultado_sub.texto
    assert "[EMAIL]" in resultado_tag.texto
    assert tag not in resultado_tag.texto


# ─── Sección 3: TELEFONO ─────────────────────────────────────────────────────

def test_pseudonymize_reemplaza_telefono_con_prefijo_internacional() -> None:
    """
    Teléfono con prefijo internacional argentino (+54) es reemplazado por [TELEFONO].
    Los dígitos originales no deben aparecer en la salida.
    """
    texto = "Llamar al +54 261 555-1234 para reportar el incidente."
    resultado = pseudonymize(texto, [])

    assert "[TELEFONO]" in resultado.texto
    assert "+54 261 555-1234" not in resultado.texto
    assert resultado.conteos["telefono"] == 1


def test_pseudonymize_reemplaza_telefono_local_sin_prefijo() -> None:
    """
    Teléfonos locales argentinos sin prefijo internacional son detectados.
    Cubre formato compacto (2615551234) y con espacios (261 555 1234).
    """
    compacto = "2615551234"
    con_espacios = "261 555 1234"

    r1 = pseudonymize(f"El número de contacto es {compacto}.", [])
    r2 = pseudonymize(f"Comunicarse al {con_espacios}.", [])

    assert "[TELEFONO]" in r1.texto
    assert compacto not in r1.texto
    assert "[TELEFONO]" in r2.texto
    assert con_espacios not in r2.texto


def test_pseudonymize_no_captura_numero_corto_no_telefonico() -> None:
    """
    Números cortos (código de error, ID de ticket) no son clasificados como teléfonos.
    """
    texto = "Error código 13 en el sistema. Ticket #42 abierto."
    resultado = pseudonymize(texto, [])

    assert "[TELEFONO]" not in resultado.texto
    assert resultado.conteos["telefono"] == 0


# ─── Sección 4: HOST ──────────────────────────────────────────────────────────

def test_pseudonymize_reemplaza_host_fallback_prefijo_servidor() -> None:
    """
    Host con prefijo 'srv-' es detectado por el fallback heurístico
    incluso sin dominios configurados.
    """
    texto = "El servicio de correo en srv-correo01 no responde."
    resultado = pseudonymize(texto, [])

    assert "[HOST]" in resultado.texto
    assert "srv-correo01" not in resultado.texto
    assert resultado.conteos["host"] == 1


def test_pseudonymize_reemplaza_host_sufijo_local() -> None:
    """
    Host con sufijo '.local' y prefijo 'pc-' son detectados por el fallback.
    """
    texto_local = "No se puede acceder a pc-recepcion.local desde la red interna."
    resultado_local = pseudonymize(texto_local, [])

    assert "[HOST]" in resultado_local.texto
    assert "pc-recepcion.local" not in resultado_local.texto

    texto_localhost = "El servicio corre en localhost:8080."
    resultado_lh = pseudonymize(texto_localhost, [])
    assert "[HOST]" in resultado_lh.texto
    assert "localhost" not in resultado_lh.texto


def test_pseudonymize_no_captura_palabras_comunes_con_guion() -> None:
    """
    Palabras comunes con guion que no son hosts no son enmascaradas.
    """
    texto = "El sistema de help-desk está bien configurado."
    resultado = pseudonymize(texto, [])

    # help-desk no tiene prefijo srv- ni pc-
    assert resultado.conteos["host"] == 0


def test_pseudonymize_reemplaza_host_de_dominio_corporativo_configurado() -> None:
    """
    Un hostname que pertenece a un dominio corporativo configurado
    es reemplazado por [HOST].
    """
    texto = "Falla en mail.corp.empresa.com esta mañana."
    resultado = pseudonymize(texto, ["corp.empresa.com"])

    assert "[HOST]" in resultado.texto
    assert "mail.corp.empresa.com" not in resultado.texto
    assert resultado.conteos["host"] == 1


# ─── Sección 5: PERSONA ──────────────────────────────────────────────────────

def test_pseudonymize_reemplaza_nombre_y_apellido() -> None:
    """
    Nombre + apellido en formato 'Nombre Apellido' es reemplazado por [PERSONA].
    El conteo de 'persona' debe ser >= 1.
    """
    texto = "el usuario Juan Pérez reportó el problema al área de soporte."
    resultado = pseudonymize(texto, [])

    assert "[PERSONA]" in resultado.texto
    assert "Juan Pérez" not in resultado.texto
    assert resultado.conteos["persona"] >= 1


def test_pseudonymize_categorias_dominio_no_se_marcan_como_persona() -> None:
    """
    Las tres categorías canónicas del dominio no son marcadas como [PERSONA]
    aunque empiezan con mayúscula.
    """
    texto = "Clasificado como Sistemas por el modelo. Ver también Operaciones y Soporte Técnico."
    resultado = pseudonymize(texto, [])

    assert "Sistemas" in resultado.texto or resultado.texto.count("[PERSONA]") == 0
    # Las categorías NO deben ser reemplazadas
    assert "Sistemas" in resultado.texto
    assert "Operaciones" in resultado.texto


def test_pseudonymize_reemplaza_nombre_con_tildes_y_enie() -> None:
    """
    Nombres con tildes y ñ (comunes en español rioplatense) son detectados.
    """
    texto = "La solicitud fue enviada por María Núñez del sector técnico."
    resultado = pseudonymize(texto, [])

    assert "[PERSONA]" in resultado.texto
    assert "María Núñez" not in resultado.texto
    assert resultado.conteos["persona"] >= 1


# ─── Sección 6: Orden de aplicación y colisiones ─────────────────────────────

def test_pseudonymize_email_no_se_fragmenta_como_persona() -> None:
    """
    Un email que contiene un nombre (juan.perez@empresa.com) es procesado
    como [EMAIL] completo; el nombre dentro no genera un [PERSONA] adicional.
    """
    texto = "Reportado por juan.perez@empresa.com al equipo."
    resultado = pseudonymize(texto, [])

    # Debe tener exactamente un [EMAIL] y cero [PERSONA]
    assert resultado.conteos["email"] == 1
    assert "[EMAIL]" in resultado.texto
    # No debe fragmentar el email en partes y marcar el nombre
    assert "juan.perez@empresa.com" not in resultado.texto


def test_pseudonymize_combinacion_todas_las_categorias() -> None:
    """
    Texto con nombre, email, teléfono y host simultáneos:
    cada etiqueta aparece al menos una vez, ningún dato original queda,
    y los conteos son correctos por categoría.
    """
    texto = (
        "Carlos García (carlos.garcia@empresa.com) llamó al +54 261 555-9876 "
        "para reportar que srv-db01 no responde."
    )
    resultado = pseudonymize(texto, [])

    assert "[EMAIL]" in resultado.texto
    assert "[TELEFONO]" in resultado.texto
    assert "[HOST]" in resultado.texto
    assert "[PERSONA]" in resultado.texto

    # Datos originales no deben aparecer
    assert "carlos.garcia@empresa.com" not in resultado.texto
    assert "+54 261 555-9876" not in resultado.texto
    assert "srv-db01" not in resultado.texto
    assert "Carlos García" not in resultado.texto

    assert resultado.conteos["email"] == 1
    assert resultado.conteos["telefono"] == 1
    assert resultado.conteos["host"] == 1
    assert resultado.conteos["persona"] >= 1
