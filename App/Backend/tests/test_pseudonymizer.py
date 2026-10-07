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
    assert resultado.conteos == {
        "email": 0,
        "telefono": 0,
        "tarjeta": 0,
        "host": 0,
        "persona": 0,
    }


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


@pytest.mark.parametrize(
    "texto,esperado",
    [
        ("El interno es 261 555 12345.", "El interno es [TELEFONO]."),
        ("Numero 261 555 123456.", "Numero [TELEFONO]."),
        ("Contacto 26155512345.", "Contacto [TELEFONO]."),
    ],
)
def test_pseudonymize_telefono_seguido_de_digito_no_deja_orfano(
    texto: str, esperado: str
) -> None:
    """
    Un teléfono seguido de más dígitos (número local más largo) debe consumir
    toda la corrida de dígitos y no dejar un dígito huérfano pegado a la etiqueta.
    """
    resultado = pseudonymize(texto, [])

    assert resultado.texto == esperado
    assert resultado.conteos["telefono"] == 1


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
    Los cinco sectores canónicos no son marcados como [PERSONA] aunque empiecen
    con mayúscula. Es crítico para los nombres multi-palabra (p. ej.
    "Soporte Tecnico Hardware"), que de otro modo matchearían la heurística.
    """
    from app.constants import SECTORES_CANONICOS

    for sector in SECTORES_CANONICOS:
        resultado = pseudonymize(f"Clasificado como {sector} por el modelo.", [])
        assert sector in resultado.texto, (
            f"El sector {sector!r} fue enmascarado como [PERSONA]"
        )
        assert "[PERSONA]" not in resultado.texto


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


# ─── Sección 7: allowlist de términos técnicos/productos/marcas (C-30 BE B4) ──

def test_pseudonymize_preserva_productos_de_infraestructura() -> None:
    """
    Productos multi-palabra de infraestructura no deben enmascararse como
    [PERSONA]; el conteo de la categoría persona debe ser cero.
    """
    resultado = pseudonymize("Falla en Windows Server y Active Directory", [])

    assert "Windows Server" in resultado.texto
    assert "Active Directory" in resultado.texto
    assert resultado.conteos["persona"] == 0


@pytest.mark.parametrize("termino", ["SQL Server", "Google Chrome"])
def test_pseudonymize_preserva_bases_de_datos_y_navegadores(termino: str) -> None:
    """`SQL Server` y `Google Chrome` permanecen en el texto y no cuentan como persona."""
    resultado = pseudonymize(f"Problema detectado con {termino} en la estación.", [])

    assert termino in resultado.texto
    assert resultado.conteos["persona"] == 0


def test_pseudonymize_nombre_real_junto_a_termino_tecnico() -> None:
    """
    Un nombre propio real se sigue enmascarando aunque conviva con términos
    técnicos preservados en la misma oración.
    """
    resultado = pseudonymize("Juan Pérez reportó una falla en Windows Server", [])

    assert "Windows Server" in resultado.texto
    assert "Juan Pérez" not in resultado.texto
    assert resultado.conteos["persona"] >= 1


# ─── Sección 8: TARJETA con disparador contextual (c-73) ─────────────────────

def test_pseudonymize_reemplaza_tarjeta_agrupada_con_espacios() -> None:
    """
    Un número de tarjeta 4-4-4-4 con espacios, precedido por la mención
    'tarjeta' dentro de la ventana, se reemplaza por [TARJETA] sin dejar
    ningún dígito en claro y con conteo 1.
    """
    texto = "mi tarjeta numero 4517 6712 3456 7890 vencio"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" in resultado.texto
    assert "4517 6712 3456 7890" not in resultado.texto
    assert "4517" not in resultado.texto
    assert "7890" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 1


def test_pseudonymize_reemplaza_tarjeta_contigua_de_16_digitos() -> None:
    """
    La forma contigua de 16 dígitos con contexto de 'tarjeta' se reemplaza
    completa por [TARJETA] y el conteo es 1.
    """
    texto = "Hola, mi tarjeta es 0102301239999320 y no puedo operar"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" in resultado.texto
    assert "0102301239999320" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 1


def test_pseudonymize_reemplaza_tarjeta_agrupada_con_guiones() -> None:
    """
    Un número de tarjeta agrupado con guiones, precedido por 'tarjeta'
    dentro de la ventana, se reemplaza por [TARJETA] y el conteo es 1.
    """
    texto = "el numero de tarjeta 4517-6712-3456-7890 fue rechazado"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" in resultado.texto
    assert "4517-6712-3456-7890" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 1


# ─── Sección 9: TRIANGULATE TARJETA — escenarios del spec (c-73) ─────────────

def test_pseudonymize_etiqueta_tarjeta_es_exactamente_mayusculas() -> None:
    """La etiqueta insertada es exactamente [TARJETA], sin variantes de casing."""
    resultado = pseudonymize("mi tarjeta numero 4517 6712 3456 7890 vencio", [])

    assert "[TARJETA]" in resultado.texto
    assert "[Tarjeta]" not in resultado.texto
    assert "[tarjeta]" not in resultado.texto


@pytest.mark.parametrize(
    "disparador",
    [
        "tarjeta de credito",
        "tarjeta de debito",
        "numero de tarjeta",
        "tarjetas",
    ],
)
def test_pseudonymize_variantes_de_disparador_activan_tarjeta(disparador: str) -> None:
    """Cada variante del disparador activa el reemplazo de la corrida de 16 dígitos."""
    texto = f"mi {disparador} 4517 6712 3456 7890 vencio"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" in resultado.texto
    assert "4517" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 1


def test_pseudonymize_numero_a_mas_de_40_chars_no_se_enmascara() -> None:
    """Una corrida a más de 40 caracteres del disparador (sin nueva mención) no se enmascara."""
    relleno = "x" * 45
    texto = f"mi tarjeta {relleno} 4517 6712 3456 7890"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 0


def test_pseudonymize_numero_a_40_chars_se_enmascara() -> None:
    """La ventana incluye un número exactamente a 40 caracteres del disparador."""
    relleno = "x" * 38  # " " + 38 + " " == 40 caracteres de ventana
    texto = f"mi tarjeta {relleno} 4517 6712 3456 7890"
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" in resultado.texto
    assert resultado.conteos["tarjeta"] == 1


def test_pseudonymize_16_digitos_sin_mencion_no_se_enmascara() -> None:
    """Sin mención de 'tarjeta' la regla no se activa aunque haya 16 dígitos."""
    resultado = pseudonymize("el codigo 0102301239999320 fue registrado", [])

    assert "[TARJETA]" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 0


def test_pseudonymize_tarjeta_no_se_fragmenta_como_telefono() -> None:
    """
    El número de tarjeta con contexto se consume completo como [TARJETA]:
    no queda ningún dígito en claro ni se fragmenta como [TELEFONO].
    """
    resultado = pseudonymize("mi tarjeta numero 4517 6712 3456 7890 vencio", [])

    assert resultado.conteos["tarjeta"] == 1
    assert resultado.conteos["telefono"] == 0
    assert "[TELEFONO]" not in resultado.texto
    assert not any(caracter.isdigit() for caracter in resultado.texto)


def test_pseudonymize_determinista_con_tarjeta() -> None:
    """Dos invocaciones con contexto de tarjeta devuelven texto y conteos idénticos."""
    texto = "mi tarjeta es 4517 6712 3456 7890"
    r1 = pseudonymize(texto, [])
    r2 = pseudonymize(texto, [])

    assert r1.texto == r2.texto
    assert r1.conteos == r2.conteos
    assert r1.conteos["tarjeta"] == 1


def test_pseudonymize_combinacion_con_tarjeta() -> None:
    """Texto con nombre, email, teléfono, tarjeta y host: cada etiqueta y conteo."""
    texto = (
        "Carlos García (carlos.garcia@empresa.com) llamó al +54 261 555-9876 "
        "para reportar que su tarjeta numero 4517 6712 3456 7890 y srv-db01 no responde."
    )
    resultado = pseudonymize(texto, [])

    assert "[EMAIL]" in resultado.texto
    assert "[TELEFONO]" in resultado.texto
    assert "[TARJETA]" in resultado.texto
    assert "[HOST]" in resultado.texto
    assert "[PERSONA]" in resultado.texto

    assert "carlos.garcia@empresa.com" not in resultado.texto
    assert "+54 261 555-9876" not in resultado.texto
    assert "4517 6712 3456 7890" not in resultado.texto
    assert "srv-db01" not in resultado.texto
    assert "Carlos García" not in resultado.texto

    assert resultado.conteos["email"] == 1
    assert resultado.conteos["telefono"] == 1
    assert resultado.conteos["tarjeta"] == 1
    assert resultado.conteos["host"] == 1
    assert resultado.conteos["persona"] >= 1


def test_pseudonymize_multiples_tarjetas_con_un_solo_disparador() -> None:
    """
    Un único disparador 'tarjetas' cubre varios números de tarjeta dentro de la
    ventana forward de 40 caracteres: TODOS se enmascaran (no solo el primero),
    la frase del disparador se preserva y no queda ningún dígito visible.
    """
    texto = "mis tarjetas 1111 1111 1111 1111 y 2222 2222 2222 2222"
    resultado = pseudonymize(texto, [])

    assert resultado.texto == "mis tarjetas [TARJETA] y [TARJETA]"
    assert resultado.texto.count("[TARJETA]") == 2
    assert resultado.conteos["tarjeta"] == 2
    assert not any(caracter.isdigit() for caracter in resultado.texto)


def test_pseudonymize_multiples_tarjetas_contiguas_con_un_disparador() -> None:
    """
    TRIANGULATE: la cobertura múltiple funciona también con la forma contigua de
    16 dígitos; ambos números comparten el disparador y se enmascaran los dos.
    """
    texto = "mi tarjeta 1111111111111111 y 2222222222222222"
    resultado = pseudonymize(texto, [])

    assert resultado.texto == "mi tarjeta [TARJETA] y [TARJETA]"
    assert resultado.conteos["tarjeta"] == 2
    assert not any(caracter.isdigit() for caracter in resultado.texto)


# ─── Sección 10: No regresión de corridas sin contexto (c-73) ────────────────

def test_pseudonymize_r067_dll_no_se_clasifica_como_tarjeta() -> None:
    """
    La corrida de 22 dígitos del DLL de R067 (sin la palabra 'tarjeta')
    no se clasifica como [TARJETA] ni incrementa el conteo.
    """
    texto = (
        'Le sale un cartel "Falta el dll axm0102301239999320002302" '
        "al intentar iniciar el sistema principal"
    )
    resultado = pseudonymize(texto, [])

    assert "[TARJETA]" not in resultado.texto
    assert resultado.conteos["tarjeta"] == 0


def test_pseudonymize_r169_mencion_sin_digitos_no_altera_texto() -> None:
    """La mención de 'tarjeta' sin dígitos (R169) no modifica el texto ni los conteos."""
    texto = "Tiene problemas al dar de alta una tarjeta"
    resultado = pseudonymize(texto, [])

    assert resultado.texto == texto
    assert resultado.conteos["tarjeta"] == 0



