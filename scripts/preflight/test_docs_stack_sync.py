"""Tests del preflight estatico de sincronizacion documental del stack (c-145, DOC-005).

Logica pura: se verifica `scripts/preflight/docs_stack_sync.py` leyendo los
artefactos reales (settings, constantes, requirements, compose, `openspec/config.yaml`
y `CLAUDE.md`) y fixtures mutados en `tmp_path`. Sin red, sin Docker y sin credenciales.

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q

Strict TDD: RED (modulo ausente) -> GREEN -> TRIANGULATE (mutaciones) -> REFACTOR.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402

import docs_stack_sync  # noqa: E402
from docs_stack_sync import (  # noqa: E402
    Check,
    exit_code,
    format_summary,
    run_docs_stack_sync,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SETTINGS_REL = "App/Backend/app/config/settings.py"
CONSTANTS_REL = "App/Backend/app/constants.py"
REQUIREMENTS_REL = "App/Backend/requirements.txt"
COMPOSE_REL = "docker-compose.yml"
CONFIG_REL = "openspec/config.yaml"
CLAUDE_REL = "CLAUDE.md"


# ---------------------------------------------------------------------------
# Fixtures: copia del arbol real y version sincronizada
# ---------------------------------------------------------------------------
def _copiar_arbol(tmp_path: pathlib.Path) -> pathlib.Path:
    raiz = tmp_path / "repo"
    for relativo in (SETTINGS_REL, CONSTANTS_REL, REQUIREMENTS_REL, COMPOSE_REL, CONFIG_REL, CLAUDE_REL):
        destino = raiz / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(REPO_ROOT / relativo, destino)
    return raiz


def _sincronizar(raiz: pathlib.Path) -> pathlib.Path:
    """Aplica las correcciones del bloque G (documentacion == codigo)."""
    config = (raiz / CONFIG_REL).read_text(encoding="utf-8")
    config = config.replace("Gemini 2.5 Flash", "Gemini 3.6 Flash")
    config = config.replace("google-genai >= 1.0", "google-genai >=2.31,<3")
    config = config.replace("FastAPI 0.115 + Uvicorn", "FastAPI 0.143 + Uvicorn 0.54")
    config = config.replace(
        "timeout_s: 10 }", "timeout_s: 30, total_timeout_s: 60, max_retries: 2 }"
    )
    (raiz / CONFIG_REL).write_text(config, encoding="utf-8")
    (raiz / CLAUDE_REL).write_text(
        "# CLAUDE.md\n\nModelo de inferencia: Gemini 3.6 Flash.\n", encoding="utf-8"
    )
    return raiz


def _checks(raiz: pathlib.Path):
    return run_docs_stack_sync(
        settings_path=raiz / SETTINGS_REL,
        constants_path=raiz / CONSTANTS_REL,
        requirements_path=raiz / REQUIREMENTS_REL,
        compose_path=raiz / COMPOSE_REL,
        config_path=raiz / CONFIG_REL,
        claude_path=raiz / CLAUDE_REL,
    )


def _mutar(raiz: pathlib.Path, relativo: str, viejo: str, nuevo: str) -> None:
    ruta = raiz / relativo
    texto = ruta.read_text(encoding="utf-8")
    assert viejo in texto, f"No se encontro {viejo!r} en {relativo}"
    ruta.write_text(texto.replace(viejo, nuevo), encoding="utf-8")


def _claude_con(texto: str):
    return lambda raiz: (raiz / CLAUDE_REL).write_text(texto, encoding="utf-8")


def _summary(checks) -> str:
    return " || ".join(f"{c.status}:{c.name}:{c.detail}" for c in checks)


def _fails(checks) -> list:
    return [c for c in checks if c.status == "FAIL"]


def _assert_fails_naming(checks, needle: str) -> None:
    fails = _fails(checks)
    assert fails, f"Se esperaba al menos un FAIL: {_summary(checks)}"
    assert any(needle in c.name or needle in c.detail for c in fails), (
        f"Los FAIL no nombran {needle!r}: {_summary(checks)}"
    )


def _solo_un_fail(checks) -> None:
    fails = _fails(checks)
    assert len(fails) == 1, f"Se esperaba exactamente un FAIL: {_summary(checks)}"


# ===========================================================================
# (a) Los documentos sincronizados no producen hallazgos
# ===========================================================================
def test_a_documentos_sincronizados_cero_hallazgos(tmp_path):
    checks = _checks(_sincronizar(_copiar_arbol(tmp_path)))

    assert all(c.status == "PASS" for c in checks), _summary(checks)
    assert exit_code(checks) == 0


# ===========================================================================
# Chequeo 1 - modelo de inferencia
# ===========================================================================
def test_chequeo_1_modelo_de_config_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "Gemini 3.6 Flash (google-genai", "Gemini 9.9 Flash (google-genai")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "9.9 Flash")
    _solo_un_fail(checks)


def test_chequeo_1_modelo_de_claude_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text("Modelo: Gemini 2.5 Flash.\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "CLAUDE.md")


# ===========================================================================
# Chequeo 2 - timeout y reintentos
# ===========================================================================
def test_chequeo_2_timeout_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "timeout_s: 30", "timeout_s: 10")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "timeout_s")
    _solo_un_fail(checks)


def test_chequeo_2_reintentos_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "max_retries: 2", "max_retries: 0")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "max_retries")


# ===========================================================================
# Chequeo 3 - parametros de muestreo
# ===========================================================================
def test_chequeo_3_temperature_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "temperature: 0.3", "temperature: 0.5")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "temperature")
    _solo_un_fail(checks)


# ===========================================================================
# Chequeo 4 - FastAPI / Uvicorn
# ===========================================================================
def test_chequeo_4_fastapi_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "FastAPI 0.143", "FastAPI 0.115")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.115")
    _solo_un_fail(checks)


def test_chequeo_4_uvicorn_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "Uvicorn 0.54", "Uvicorn 0.40")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.40")


# ===========================================================================
# Chequeo 5 - google-genai
# ===========================================================================
def test_chequeo_5_google_genai_de_config_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "google-genai >=2.31,<3", "google-genai >= 1.0")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "google-genai")
    _solo_un_fail(checks)


def test_chequeo_5_google_genai_de_claude_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. SDK: google-genai >= 1.0.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "CLAUDE.md")


# ===========================================================================
# Chequeo 6 - version de N8N frente a la imagen del compose
# ===========================================================================
def test_chequeo_6_n8n_de_config_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "N8N 2.11.2", "N8N 1.62")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "1.62")
    _solo_un_fail(checks)


def test_chequeo_6_n8n_de_claude_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Stack: N8N 1.62.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "1.62")


# ===========================================================================
# Chequeo 7 - servicios descritos que no existen en el compose
# ===========================================================================
def test_chequeo_7_servicio_inexistente_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Servicios: N8N, PostgreSQL y Redis.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "Redis")
    _solo_un_fail(checks)


def test_chequeo_7_servicio_existente_pasa(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Servicios: N8N, PostgreSQL y Nginx.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


# ===========================================================================
# Chequeo 8 - etapa retirada descrita como vigente
# ===========================================================================
def test_chequeo_8_etapa_retirada_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Flujo: LangChain AI Agent -> Redis.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "LangChain")


# ===========================================================================
# Chequeo 9 - config.yaml valido como YAML
# ===========================================================================
def test_chequeo_9_yaml_malformado_falla_sin_traza(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CONFIG_REL).write_text("stack: [sin cerrar\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "config.yaml")
    assert exit_code(checks) == 1


def test_chequeo_9_seccion_ausente_falla_no_excepcion(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CONFIG_REL).write_text("project:\n  name: x\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "stack")


# ===========================================================================
# Chequeo 10 - umbrales
# ===========================================================================
def test_chequeo_10_umbral_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "deterministic_score: 0.5166", "deterministic_score: 0.5")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "deterministic_score")
    _solo_un_fail(checks)


def test_chequeo_10_human_review_diverge_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "human_review: 0.70", "human_review: 0.8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "human_review")


# ===========================================================================
# Chequeo 11 - categorias (contenido y orden)
# ===========================================================================
def test_chequeo_11_sector_en_otro_orden_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(
        raiz,
        CONFIG_REL,
        '["Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"]',
        '["Seguridad Informatica", "Soporte Tecnico Hardware", "Sistemas", "Bases de Datos", "Soporte Tecnico Software"]',
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "categorias")
    _solo_un_fail(checks)


def test_chequeo_11_sector_retirado_falla(tmp_path):
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, '"Sistemas"]', '"Operaciones"]')

    checks = _checks(raiz)
    _assert_fails_naming(checks, "categorias")


# ===========================================================================
# Chequeo 12 - duplicacion de literales volatiles en CLAUDE.md
# ===========================================================================
@pytest.mark.parametrize("literal", ["0.5166", "0.70", "0.115", ">= 1.0", "2.11.2"])
def test_g_literal_volatil_en_claude_falla(tmp_path, literal):
    """(g) cualquiera de los cinco literales volatiles derivados de config.yaml."""
    raiz = _copiar_arbol(tmp_path)  # config.yaml sin corregir: los cinco literales vigentes
    (raiz / CLAUDE_REL).write_text(
        f"Modelo: Gemini 3.6 Flash. Valor: {literal}.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "duplicacion")


def test_h_remision_a_config_pasa(tmp_path):
    """(h) el mismo valor expresado como remision a config.yaml no es duplicacion."""
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash.\n"
        "Los umbrales viven en openspec/config.yaml (conventions.thresholds).\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_i_umbral_nuevo_restateado_falla(tmp_path):
    """(i) la lista se deriva: un umbral NUEVO restateado en CLAUDE.md tambien falla."""
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    _mutar(raiz, CONFIG_REL, "deterministic_score: 0.5166", "deterministic_score: 0.4242")
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Umbral: 0.4242.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.4242")


def test_j_identificador_retirado_falla(tmp_path):
    """(j) un identificador retirado que ya no figura en config.yaml falla por la lista estatica."""
    raiz = _sincronizar(_copiar_arbol(tmp_path))
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 2.5 Flash.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "2.5 Flash")


# ===========================================================================
# Contrato de salida
# ===========================================================================
def test_exit_code_solo_cero_si_todo_pasa():
    assert exit_code([Check("a", "PASS"), Check("b", "PASS")]) == 0
    assert exit_code([Check("a", "PASS"), Check("b", "FAIL", "falta")]) == 1
    assert exit_code([]) == 1


def test_format_summary_nombra_cada_check():
    summary = format_summary([Check("chequeo-uno", "PASS"), Check("chequeo-dos", "FAIL")])
    assert "chequeo-uno" in summary
    assert "chequeo-dos" in summary


def test_el_modulo_no_usa_red_ni_credenciales():
    fuente = pathlib.Path(docs_stack_sync.__file__).read_text(encoding="utf-8").lower()
    for token in ("import requests", "import httpx", "urllib.request", "gemini_api_key"):
        assert token not in fuente, f"El preflight no debe usar {token!r}"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
