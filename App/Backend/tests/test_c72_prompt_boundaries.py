"""
Tests estructurales c-72 (Section 3): reglas de desambiguacion de frontera en el
prompt compartido de clasificacion.

Contratos (design D4, spec sector-taxonomy TAX-003):
    - `docs/prompt_gemini.txt` incluye reglas de frontera:
        * acceder/iniciar sesion -> Soporte Tecnico Software
        * digitalizacion/escaner/impresora -> Soporte Tecnico Hardware
        * servidor/red/SMTP/VM -> Sistemas
    - El prompt usa exclusivamente los cinco strings canonicos sin tildes.
    - No queda un prompt de clasificacion divergente en n8n.

Estructura TDD:
    - 3.1 RED: el prompt contiene las reglas de frontera y los cinco canonicos.
    - 3.2 GREEN (OQ5): se agregan las reglas con la redaccion del autor.
    - 3.3 TRIANGULATE: casos R002, R038 y un caso de infraestructura + no prompt
      divergente en n8n.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPT_PATH = REPO_ROOT / "docs" / "prompt_gemini.txt"
WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"

CANONICAL_SECTORS = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)


def prompt_text() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 3.1 RED — reglas de frontera presentes
# ---------------------------------------------------------------------------


def test_3_1_prompt_contiene_seccion_de_reglas_de_frontera():
    text = prompt_text()
    assert "REGLAS DE FRONTERA" in text, (
        "docs/prompt_gemini.txt no declara la seccion de reglas de frontera"
    )


def test_3_1_regla_software_para_accesos_a_aplicaciones():
    text = prompt_text()
    assert "acceder" in text and "iniciar sesion" in text, (
        "La regla de Software para accesos (acceder / iniciar sesion) no esta en el prompt"
    )
    assert "Soporte Tecnico Software" in text, (
        "El prompt no usa el string canonico 'Soporte Tecnico Software'"
    )


def test_3_1_regla_hardware_para_digitalizacion():
    text = prompt_text()
    assert "digitalizacion" in text and "escaner" in text and "impresora" in text, (
        "La regla de Hardware para digitalizacion (escaner / impresora) no esta en el prompt"
    )
    assert "Soporte Tecnico Hardware" in text, (
        "El prompt no usa el string canonico 'Soporte Tecnico Hardware'"
    )


def test_3_1_regla_sistemas_para_infraestructura():
    text = prompt_text()
    assert "servidor" in text and "SMTP" in text and "VM" in text, (
        "La regla de Sistemas para infraestructura (servidor / SMTP / VM) no esta en el prompt"
    )
    assert "Sistemas" in text, "El prompt no usa el string canonico 'Sistemas'"


def test_3_1_prompt_usa_los_cinco_strings_canonicos_sin_tildes():
    text = prompt_text()
    for sector in CANONICAL_SECTORS:
        assert sector in text, f"El prompt no usa el string canonico {sector!r}"
    # La seccion de reglas de frontera (la que orienta la clasificacion) no debe
    # introducir la variante con tilde. La prohibicion explicita de la seccion
    # CASING puede mencionarla como contraejemplo.
    reglas = text.split("REGLAS DE FRONTERA", 1)[1].split("FORMATO DE RESPUESTA", 1)[0]
    assert "Soporte Técnico" not in reglas, (
        "Las reglas de frontera usan la variante con tilde 'Soporte Técnico' (prohibida)"
    )


# ---------------------------------------------------------------------------
# 3.3 TRIANGULATE — casos de frontera del corpus
# ---------------------------------------------------------------------------


def test_3_3_caso_r002_acceso_a_sistema_orienta_a_software():
    """
    R002: 'No se puede acceder al ambiente de prueba del sistema secundario'
    (corpus: Soporte Tecnico Software). La regla de accesos cubre 'acceder'.
    """
    text = prompt_text()
    assert "acceder" in text, (
        "El prompt no cubre el caso R002 (acceder a un sistema) -> Software"
    )


def test_3_3_caso_r038_digitalizacion_orienta_a_hardware():
    """
    R038: 'Reporta error de digitalizacion en el sistema principal'
    (corpus: Soporte Tecnico Hardware). La regla de digitalizacion cubre el termino.
    """
    text = prompt_text()
    assert "digitalizacion" in text, (
        "El prompt no cubre el caso R038 (error de digitalizacion) -> Hardware"
    )


def test_3_3_caso_infraestructura_orienta_a_sistemas():
    """
    R015: 'No le salen correos por flujo del sistema principal...' (corpus:
    Sistemas). La regla de infraestructura cubre servidor/red/SMTP/VM.
    """
    text = prompt_text()
    assert any(k in text for k in ("servidor", "SMTP", "red", "VM")), (
        "El prompt no cubre el caso de infraestructura -> Sistemas"
    )


def test_3_3_no_hay_prompt_divergente_en_n8n():
    """
    El flujo telefonico no mantiene un prompt de clasificacion propio: no queda
    ningun nodo agente ni texto que pida `sector_predicho`.
    """
    with WORKFLOW_PATH.open(encoding="utf-8") as fh:
        wf = json.load(fh)
    blob = json.dumps(wf, ensure_ascii=False)
    assert "sector_predicho" not in blob, (
        "n8n conserva un prompt divergente que produce 'sector_predicho'"
    )
    assert "@n8n/n8n-nodes-langchain.agent" not in blob, (
        "n8n conserva el nodo AI Agent con su prompt de clasificacion"
    )