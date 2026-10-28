"""Tests del preflight estatico de sincronizacion documental del stack (c-145, DOC-005).

Logica pura: se verifica `scripts/preflight/docs_stack_sync.py` sobre un ARBOL
SINTETICO autosuficiente construido en `tmp_path` (settings, constantes,
requirements, compose, `openspec/config.yaml`, `CLAUDE.md`, `knowledge-base/**`,
material de referencia y `api.ts`), con las versiones FIJADAS por la propia suite.
Los fixtures NO leen los archivos reales del repositorio (c-149): asi un bump
legitimo de dependencias no rompe la suite, y una deriva inyectada aisla
exactamente un hallazgo. Sin red, sin Docker y sin credenciales.

Ejecucion (desde la raiz del repo):
    python3 -m pytest scripts/preflight/test_docs_stack_sync.py -q

Strict TDD: RED (acoplamiento al repo real) -> GREEN (fixtures sinteticos) ->
TRIANGULATE (bump coordinado y bump aislado) -> REFACTOR.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest  # noqa: E402
import yaml  # noqa: E402

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
KB_REL = "knowledge-base"
REFERENCIA_REL = ("docs/parameters_gemini.md", "docs/n8n-workflow-guide.md")
API_TS_REL = "App/Frontend/src/services/api.ts"

#: Versiones FIJAS del arbol sintetico: la unica fuente de verdad de la suite.
#: NO se derivan de los archivos reales del repositorio, de modo que un bump
#: legitimo de dependencias (por ejemplo el PR de Dependabot) NO la altera.
_VERS_BASE: dict = {
    "fastapi_pin": "0.143.3",  # pin exacto en requirements.txt
    "fastapi_cfg": "0.143",  # minor declarado en config.yaml (FastAPI <x>)
    "fastapi_kb": "0.143.3",  # parche declarado en la base de conocimiento
    "uvicorn_pin": "0.54.0",
    "uvicorn_cfg": "0.54",
    "n8n": "2.11.2",
    "genai_req": ">=2.33.0,<3",
    "genai_doc": ">=2.33,<3",
}

#: Valores de `Settings` del fixture. Deben coincidir con el `config.yaml` del
#: fixture por construccion (los chequeos 1-3 y 10 los comparan).
_SETTINGS_FIXTURE = """\
class Settings:
    gemini_model: str = "gemini-3.6-flash"
    gemini_temperature: float = 0.3
    gemini_top_p: float = 0.9
    gemini_max_output_tokens: int = 100
    gemini_timeout_seconds: int = 30
    gemini_total_timeout_seconds: int = 60
    gemini_max_retries: int = 2
    deterministic_score_threshold: float = 0.5166
    human_review_threshold: float = 0.70
"""

#: `SECTORES_CANONICOS` del fixture (chequeo 11: contenido y orden).
_CONSTANTS_FIXTURE = """\
SECTORES_CANONICOS: tuple[str, ...] = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)
"""


# ---------------------------------------------------------------------------
# Fixtures: arbol SINTETICO autosuficiente (hermetico, c-149)
# ---------------------------------------------------------------------------
def _contenido_arbol(versiones: dict | None = None) -> dict:
    """Contenido completo del arbol sintetico, indexado por ruta relativa.

    Todos los documentos derivan del mismo mapa de versiones, de modo que el
    arbol nace sincronizado y no depende (ni lee) los archivos reales.
    """
    v = dict(_VERS_BASE)
    if versiones:
        v.update(versiones)
    contenido: dict = {}

    contenido[SETTINGS_REL] = _SETTINGS_FIXTURE
    contenido[CONSTANTS_REL] = _CONSTANTS_FIXTURE
    contenido[REQUIREMENTS_REL] = (
        "# Web framework\n"
        f"fastapi=={v['fastapi_pin']}\n"
        "starlette==1.10.0\n"
        f"uvicorn[standard]=={v['uvicorn_pin']}\n"
        "\n"
        f"google-genai{v['genai_req']}\n"
        "\n"
        "httpx==0.28.1\n"
    )
    contenido[COMPOSE_REL] = (
        "services:\n"
        "  postgres:\n"
        "    image: postgres:15.5-alpine\n"
        "  backend:\n"
        "    build: ./App/Backend\n"
        "  n8n:\n"
        f"    image: n8nio/n8n:{v['n8n']}\n"
        "  nginx:\n"
        "    image: nginx:1.31.7-alpine\n"
        "  ngrok:\n"
        "    image: ngrok/ngrok:3.39.8-debian\n"
    )
    contenido[CONFIG_REL] = (
        "project:\n"
        "  name: fixture-c-149\n"
        "stack:\n"
        "  backend:\n"
        f"    framework: FastAPI {v['fastapi_cfg']} + Uvicorn {v['uvicorn_cfg']}\n"
        "  orchestration:\n"
        f"    tool: N8N {v['n8n']} (Docker autoalojado, imagen pinneada)\n"
        "  inference:\n"
        f"    model: Gemini 3.6 Flash (google-genai {v['genai_doc']})\n"
        "    params: { temperature: 0.3, top_p: 0.9, max_output_tokens: 100, "
        "timeout_s: 30, total_timeout_s: 60, max_retries: 2 }\n"
        "conventions:\n"
        "  thresholds: { deterministic_score: 0.5166, human_review: 0.70 }\n"
        '  categorias: ["Seguridad Informatica", "Soporte Tecnico Hardware", '
        '"Soporte Tecnico Software", "Bases de Datos", "Sistemas"]\n'
    )
    contenido[CLAUDE_REL] = "# CLAUDE.md\n\nModelo de inferencia: Gemini 3.6 Flash.\n"
    contenido[API_TS_REL] = (
        "export const api = axios.create({\n"
        '  baseURL: "/api/v1",\n'
        "  timeout: 65_000,\n"
        "});\n"
    )

    contenido[f"{KB_REL}/README.md"] = "# Base de conocimiento\n"
    contenido[f"{KB_REL}/01_vision_y_objetivos.md"] = (
        "# Vision y objetivos\n\nEl sistema clasifica con Gemini 3.6 Flash.\n"
    )
    contenido[f"{KB_REL}/02_descripcion_general.md"] = (
        "# Descripcion General\n\n"
        "| Capa | Tecnologia | Version |\n"
        "|---|---|---|\n"
        f"| Orquestación | N8N | {v['n8n']} |\n"
        f"| API / Procesamiento | FastAPI + Uvicorn | {v['fastapi_kb']} / {v['uvicorn_pin']} |\n"
        f"| Inferencia LLM | Gemini 3.6 Flash | `google-genai` {v['genai_doc']} |\n"
    )
    contenido[f"{KB_REL}/03_actores_y_roles.md"] = "# Actores y roles\n"
    contenido[f"{KB_REL}/04_modelo_de_datos.md"] = "# Modelo de datos\n"
    contenido[f"{KB_REL}/05_reglas_de_negocio.md"] = (
        "# Reglas de negocio\n\n"
        "La clasificacion usa Gemini 3.6 Flash con timeout 30 s por intento.\n"
    )
    contenido[f"{KB_REL}/06_funcionalidades.md"] = "# Funcionalidades\n"
    contenido[f"{KB_REL}/07_flujos_principales.md"] = "# Flujos principales\n"
    contenido[f"{KB_REL}/08_arquitectura_propuesta.md"] = (
        "# Arquitectura propuesta\n\n"
        f"- Imágenes: `python:3.12-slim`, `postgres:15.5-alpine`, N8N oficial {v['n8n']}.\n"
    )
    contenido[f"{KB_REL}/09_decisiones_y_supuestos.md"] = (
        "# Decisiones y supuestos\n\n"
        f"**Decisión**: FastAPI {v['fastapi_kb']} sobre Uvicorn {v['uvicorn_pin']}.\n"
    )
    contenido[f"{KB_REL}/10_preguntas_abiertas.md"] = "# Preguntas abiertas\n"
    contenido[f"{KB_REL}/11_evaluacion_experimental.md"] = "# Evaluacion experimental\n"

    contenido[REFERENCIA_REL[0]] = (
        "# Parametros Gemini\n\nModelo: Gemini 3.6 Flash con timeout 30 s por intento.\n"
    )
    contenido[REFERENCIA_REL[1]] = (
        "# Guia del Workflow N8N\n\n"
        "| Nodo | Intentos | Timeout | Espera |\n"
        "|---|---|---|---|\n"
        "| `Login operador` | 3 | 5000 ms | 10000 ms (10 s) |\n"
    )
    return contenido


def _arbol_sincronizado(tmp_path: pathlib.Path, versiones: dict | None = None) -> pathlib.Path:
    """Escribe un arbol sintetico autosuficiente y devuelve su raiz.

    Las versiones de componentes provienen de `_VERS_BASE` (o del parametro
    `versiones`), NO de los archivos reales del repositorio: la suite es
    hermética respecto del estado real del repo.
    """
    raiz = tmp_path / "repo"
    for relativo, texto in _contenido_arbol(versiones).items():
        destino = raiz / relativo
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(texto, encoding="utf-8")
    return raiz


def _checks(raiz: pathlib.Path):
    return run_docs_stack_sync(
        settings_path=raiz / SETTINGS_REL,
        constants_path=raiz / CONSTANTS_REL,
        requirements_path=raiz / REQUIREMENTS_REL,
        compose_path=raiz / COMPOSE_REL,
        config_path=raiz / CONFIG_REL,
        claude_path=raiz / CLAUDE_REL,
        kb_dir=raiz / KB_REL,
        referencia_paths=tuple(raiz / rel for rel in REFERENCIA_REL),
        api_ts_path=raiz / API_TS_REL,
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
    checks = _checks(_arbol_sincronizado(tmp_path))

    assert all(c.status == "PASS" for c in checks), _summary(checks)
    assert exit_code(checks) == 0


# ===========================================================================
# Chequeo 1 - modelo de inferencia
# ===========================================================================
def test_chequeo_1_modelo_de_config_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "Gemini 3.6 Flash (google-genai", "Gemini 9.9 Flash (google-genai")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "9.9 Flash")
    _solo_un_fail(checks)


def test_chequeo_1_modelo_de_claude_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text("Modelo: Gemini 2.5 Flash.\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "CLAUDE.md")


# ===========================================================================
# Chequeo 2 - timeout y reintentos
# ===========================================================================
def test_chequeo_2_timeout_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "timeout_s: 30", "timeout_s: 10")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "timeout_s")
    _solo_un_fail(checks)


def test_chequeo_2_reintentos_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "max_retries: 2", "max_retries: 0")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "max_retries")


# ===========================================================================
# Chequeo 3 - parametros de muestreo
# ===========================================================================
def test_chequeo_3_temperature_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "temperature: 0.3", "temperature: 0.5")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "temperature")
    _solo_un_fail(checks)


# ===========================================================================
# Chequeo 4 - FastAPI / Uvicorn
# ===========================================================================
def test_chequeo_4_fastapi_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "FastAPI 0.143", "FastAPI 0.115")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.115")
    _solo_un_fail(checks)


def test_chequeo_4_uvicorn_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "Uvicorn 0.54", "Uvicorn 0.40")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.40")


# ===========================================================================
# Chequeo 5 - google-genai
# ===========================================================================
def test_chequeo_5_google_genai_de_config_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "google-genai >=2.33,<3", "google-genai >= 1.0")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "google-genai")
    _solo_un_fail(checks)


def test_chequeo_5_google_genai_de_claude_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. SDK: google-genai >= 1.0.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "CLAUDE.md")


# ===========================================================================
# Chequeo 6 - version de N8N frente a la imagen del compose
# ===========================================================================
def test_chequeo_6_n8n_de_config_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "N8N 2.11.2", "N8N 1.62")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "1.62")
    _solo_un_fail(checks)


def test_chequeo_6_n8n_de_claude_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Stack: N8N 1.62.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "1.62")


# ===========================================================================
# Chequeo 7 - servicios descritos que no existen en el compose
# ===========================================================================
def test_chequeo_7_servicio_inexistente_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Servicios: N8N, PostgreSQL y Redis.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "Redis")
    _solo_un_fail(checks)


def test_chequeo_7_servicio_existente_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
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
    raiz = _arbol_sincronizado(tmp_path)
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
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CONFIG_REL).write_text("stack: [sin cerrar\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "config.yaml")
    assert exit_code(checks) == 1


def test_chequeo_9_seccion_ausente_falla_no_excepcion(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CONFIG_REL).write_text("project:\n  name: x\n", encoding="utf-8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "stack")


# ===========================================================================
# Chequeo 10 - umbrales
# ===========================================================================
def test_chequeo_10_umbral_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "deterministic_score: 0.5166", "deterministic_score: 0.5")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "deterministic_score")
    _solo_un_fail(checks)


def test_chequeo_10_human_review_diverge_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "human_review: 0.70", "human_review: 0.8")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "human_review")


# ===========================================================================
# Chequeo 11 - categorias (contenido y orden)
# ===========================================================================
def test_chequeo_11_sector_en_otro_orden_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
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
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, '"Sistemas"]', '"Operaciones"]')

    checks = _checks(raiz)
    _assert_fails_naming(checks, "categorias")


# ===========================================================================
# Chequeo 12 - duplicacion de literales volatiles en CLAUDE.md
# ===========================================================================
def _literales_volatiles_del_config():
    """Literales prohibidos derivados del `config.yaml` del FIXTURE, no hardcodeados.

    Se lee el `config.yaml` sintetico (no el real) para que la lista siga
    correspondiendo a la capsula de configuracion sobre la que corre el chequeo.
    """
    config = yaml.safe_load(_contenido_arbol(_VERS_BASE)[CONFIG_REL])
    return [literal for literal in docs_stack_sync._literales_prohibidos(config) if literal]


@pytest.mark.parametrize("literal", _literales_volatiles_del_config())
def test_g_literal_volatil_en_claude_falla(tmp_path, literal):
    """(g) cada literal volatil derivado de config.yaml, restateado en CLAUDE.md, produce FAIL."""
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        f"Modelo: Gemini 3.6 Flash. Valor: {literal}.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "duplicacion")


def test_h_remision_a_config_pasa(tmp_path):
    """(h) el mismo valor expresado como remision a config.yaml no es duplicacion."""
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash.\n"
        "Los umbrales viven en openspec/config.yaml (conventions.thresholds).\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_i_umbral_nuevo_restateado_falla(tmp_path):
    """(i) la lista se deriva: un umbral NUEVO restateado en CLAUDE.md tambien falla."""
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, CONFIG_REL, "deterministic_score: 0.5166", "deterministic_score: 0.4242")
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 3.6 Flash. Umbral: 0.4242.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "0.4242")


def test_j_identificador_retirado_falla(tmp_path):
    """(j) un identificador retirado que ya no figura en config.yaml falla por la lista estatica."""
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / CLAUDE_REL).write_text(
        "Modelo: Gemini 2.5 Flash.\n", encoding="utf-8"
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "2.5 Flash")


# ===========================================================================
# Chequeo 13 - modelo vigente en la superficie ampliada (KB + referencia)
# ===========================================================================
def test_superficie_declarada_incluye_kb_y_referencia():
    assert docs_stack_sync.KB_DIR.name == "knowledge-base"
    nombres = {pathlib.Path(p).name for p in docs_stack_sync.DOCS_REFERENCIA}
    assert {"parameters_gemini.md", "n8n-workflow-guide.md"} <= nombres
    assert docs_stack_sync.API_TS_PATH.name == "api.ts"


def test_chequeo_13_modelo_retirado_en_kb_sin_rotulacion_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / KB_REL / "01_vision_y_objetivos.md"
    ruta.write_text(
        ruta.read_text(encoding="utf-8").replace("Gemini 3.6 Flash", "Gemini 2.5 Flash"),
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "2.5 Flash")
    _assert_fails_naming(checks, "01_vision_y_objetivos.md")


def test_chequeo_13_modelo_retirado_con_rotulacion_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / KB_REL / "01_vision_y_objetivos.md"
    ruta.write_text(
        ruta.read_text(encoding="utf-8").replace(
            "Gemini 3.6 Flash",
            "Gemini 3.6 Flash (el antecedente historico fue Gemini 2.5 Flash)",
            1,
        ),
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_13_modelo_desconocido_en_kb_falla(tmp_path):
    """(g) la regla no esta hardcodeada a 2.5: cualquier token != Settings falla."""
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / KB_REL / "05_reglas_de_negocio.md"
    ruta.write_text(
        ruta.read_text(encoding="utf-8").replace("Gemini 3.6 Flash", "Gemini 9.9 Flash"),
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "9.9 Flash")


def test_chequeo_13_modelo_retirado_en_referencia_sin_rotulacion_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, REFERENCIA_REL[0], "Gemini 3.6 Flash", "Gemini 2.5 Flash")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "parameters_gemini.md")


# ===========================================================================
# Chequeo 14 - timeout vigente en contexto de parametros de Gemini
# ===========================================================================
def test_chequeo_14_timeout_retirado_en_contexto_gemini_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, "knowledge-base/05_reglas_de_negocio.md", "timeout 30 s", "timeout 10 s")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "timeout retirado 10")
    _assert_fails_naming(checks, "05_reglas_de_negocio.md")


def test_chequeo_14_timeout_vigente_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_14_timeout_retirado_con_rotulacion_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/05_reglas_de_negocio.md",
        "timeout 30 s",
        "timeout 30 s (el valor historico calibrado fue timeout 10 s)",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_14_timeout_de_n8n_fuera_de_contexto_no_falla(tmp_path):
    """(negativo) un timeout de N8N sin contexto de Gemini no dispara el chequeo 14."""
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        REFERENCIA_REL[1],
        "| `Login operador` | 3 | 5000 ms | 10000 ms (10 s) |",
        "| `Login operador` | 3 | 5000 ms | 10000 ms (10 s) |  # timeout 10 s",
    )

    checks = _checks(raiz)
    assert not any("timeout retirado" in c.detail for c in _fails(checks)), _summary(checks)


# ===========================================================================
# Chequeo 15 - superficie documental cubierta
# ===========================================================================
def test_chequeo_15_archivo_esperado_ausente_falla_sin_excepcion(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / KB_REL / "01_vision_y_objetivos.md").unlink()

    checks = _checks(raiz)
    _assert_fails_naming(checks, "01_vision_y_objetivos.md")
    assert exit_code(checks) == 1


def test_chequeo_15_referencia_ausente_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    (raiz / REFERENCIA_REL[0]).unlink()

    checks = _checks(raiz)
    _assert_fails_naming(checks, "parameters_gemini.md")


# ===========================================================================
# Chequeo 16 - invariante del timeout del cliente (Bloque E)
# ===========================================================================
def test_chequeo_16_cliente_mayor_que_backend_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_16_cliente_menor_que_backend_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, API_TS_REL, "timeout: 65_000", "timeout: 20_000")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "invariante")
    _assert_fails_naming(checks, "20000")


def test_chequeo_16_cliente_igual_al_backend_falla(tmp_path):
    """(limite) igual no alcanza: el invariante es estricto."""
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, API_TS_REL, "timeout: 65_000", "timeout: 60_000")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "60000")


def test_chequeo_16_sin_declaracion_de_timeout_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, API_TS_REL, "timeout: 65_000,", "")

    checks = _checks(raiz)
    _assert_fails_naming(checks, "no declara")


# ===========================================================================
# Chequeo 17 - versiones de componentes de la base de conocimiento
# ===========================================================================
def test_chequeo_17_n8n_retirado_en_kb_sin_rotulacion_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/08_arquitectura_propuesta.md",
        "N8N oficial 2.11.2",
        "N8N oficial 1.62",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "1.62")
    _assert_fails_naming(checks, "08_arquitectura_propuesta.md")


def test_chequeo_17_n8n_desconocido_en_kb_falla(tmp_path):
    """(triangulacion) la regla no esta hardcodeada a 1.62: cualquier version != compose falla."""
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/02_descripcion_general.md",
        "N8N | 2.11.2",
        "N8N | 9.9.9",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "9.9.9")


def test_chequeo_17_n8n_con_rotulacion_pasa(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/08_arquitectura_propuesta.md",
        "N8N oficial 2.11.2",
        "N8N oficial 2.11.2 (la version historica fue 1.62)",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_17_fastapi_retirado_en_kb_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/02_descripcion_general.md",
        "FastAPI + Uvicorn | 0.143.3 / 0.54.0",
        "FastAPI + Uvicorn | 0.115 / 0.54.0",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "FastAPI 0.115")


def test_chequeo_17_uvicorn_retirado_en_kb_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/02_descripcion_general.md",
        "FastAPI + Uvicorn | 0.143.3 / 0.54.0",
        "FastAPI + Uvicorn | 0.143.3 / 0.32",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "Uvicorn 0.32")


def test_chequeo_17_fastapi_uvicorn_inline_retirado_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/09_decisiones_y_supuestos.md",
        "FastAPI 0.143.3 sobre Uvicorn 0.54.0",
        "FastAPI 0.115 sobre Uvicorn 0.54.0",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "FastAPI 0.115")
    _assert_fails_naming(checks, "09_decisiones_y_supuestos.md")


def test_chequeo_17_genai_retirado_en_kb_falla(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(
        raiz,
        "knowledge-base/02_descripcion_general.md",
        "`google-genai` >=2.33,<3",
        "`google-genai` >= 1.0",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "google-genai >= 1.0")


def test_chequeo_17_genai_no_historico_en_referencia_falla(tmp_path):
    """(RED c-151) una restriccion de `google-genai` mas laxa que el pin, declarada en un
    pasaje NO historico de `docs/parameters_gemini.md`, produce FAIL nombrando el archivo.

    Antes de la ampliacion de la superficie (c-151) el chequeo 17 solo recorria
    `knowledge-base/**`, de modo que este caso no producia ningun hallazgo.
    """
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / REFERENCIA_REL[0]
    ruta.write_text(
        ruta.read_text(encoding="utf-8")
        + "\nVersión de cliente: `google-genai >=2.31,<3`.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "parameters_gemini.md")
    _assert_fails_naming(checks, "google-genai >=2.31,<3")
    _solo_un_fail(checks)


def test_chequeo_17_genai_corregido_en_referencia_pasa(tmp_path):
    """(TRIANGULATE c-151) con la restriccion corregida (`>=2.33,<3`) en el material de
    referencia, el chequeo 17 pasa: la ampliacion no es un falso positivo permanente."""
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / REFERENCIA_REL[0]
    ruta.write_text(
        ruta.read_text(encoding="utf-8")
        + "\nVersión de cliente: `google-genai >=2.33,<3`.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_17_genai_laxo_bajo_encabezado_historico_pasa(tmp_path):
    """(TRIANGULATE c-151) una restriccion mas laxa bajo un encabezado con marcador
    historico queda exenta: la regla de rotulacion historica tambien aplica al material
    de referencia."""
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / REFERENCIA_REL[0]
    ruta.write_text(
        ruta.read_text(encoding="utf-8")
        + "\n## Historial de Cambios (registro historico; antecedentes)\n"
        + "> El valor vigente es `google-genai >=2.31,<3`.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_17_n8n_en_referencia_no_se_barre(tmp_path):
    """(TRIANGULATE c-151, no regresion de alcance) la ampliacion cubre SOLO
    `google-genai`: un registro historico de N8N en el material de referencia
    (`docs/n8n-workflow-guide.md`) NO se barre y no produce FAIL."""
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / REFERENCIA_REL[1]
    ruta.write_text(
        ruta.read_text(encoding="utf-8")
        + "\nResultados de verificación (2026-06-11, C-05): N8N 2.25.7.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    assert all(c.status == "PASS" for c in checks), _summary(checks)


def test_chequeo_17_deriva_valores_del_runtime(tmp_path):
    """(triangulacion) los valores esperados se derivan de requirements/compose, no se hardcodean."""
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "componentes.md").write_text(
        "| Orquestación | N8N | 7.7.7 |\n"
        "| API | FastAPI + Uvicorn | 9.9.9 / 8.8.8 |\n"
        "SDK `google-genai` >=2.31,<3\n",
        encoding="utf-8",
    )
    check = docs_stack_sync._check_versiones_componentes(
        requirements={
            "fastapi": "==9.9.9",
            "uvicorn": "==8.8.8",
            "google-genai": ">=2.31.0,<3",
        },
        compose={"services": {"n8n": {"image": "n8nio/n8n:7.7.7"}}},
        kb_dir=kb,
    )
    assert check.status == "PASS", check.detail


def test_chequeo_17_deriva_valores_del_runtime_falla_si_diverge(tmp_path):
    """(triangulacion) con las mismas fuentes, una version distinta falla y se nombra."""
    kb = tmp_path / "kb"
    kb.mkdir()
    (kb / "componentes.md").write_text(
        "| Orquestación | N8N | 1.62 |\n", encoding="utf-8"
    )
    check = docs_stack_sync._check_versiones_componentes(
        requirements={"fastapi": "==9.9.9", "uvicorn": "==8.8.8"},
        compose={"services": {"n8n": {"image": "n8nio/n8n:7.7.7"}}},
        kb_dir=kb,
    )
    assert check.status == "FAIL"
    assert "1.62" in check.detail


# ===========================================================================
# Residual 2 - `deprecad` no exime un token de modelo retirado
# ===========================================================================
def test_deprecad_no_exime_un_modelo_retirado(tmp_path):
    raiz = _arbol_sincronizado(tmp_path)
    ruta = raiz / KB_REL / "05_reglas_de_negocio.md"
    ruta.write_text(
        ruta.read_text(encoding="utf-8")
        + "\nEl modelo Gemini 2.5 Flash quedo deprecado y ya no se usa.\n",
        encoding="utf-8",
    )

    checks = _checks(raiz)
    _assert_fails_naming(checks, "2.5 Flash")


# ===========================================================================
# Aislamiento del fixture (c-149): la suite NO depende del repositorio real
# ===========================================================================
def test_fixture_no_hereda_los_archivos_reales(tmp_path):
    """El arbol del fixture no copia los archivos reales del repositorio."""
    raiz = _arbol_sincronizado(tmp_path)
    real = (REPO_ROOT / REQUIREMENTS_REL).read_text(encoding="utf-8")
    fixture = (raiz / REQUIREMENTS_REL).read_text(encoding="utf-8")
    assert fixture != real
    assert f"fastapi=={_VERS_BASE['fastapi_pin']}" in fixture


def test_un_bump_coordinado_sigue_sincronizado_y_aisla_un_drift(tmp_path):
    """(triangulacion) un bump de versiones aplicado al fixture (a requirements y
    a la documentacion a la vez, como un change bien hecho) queda sincronizado y
    una deriva inyectada aisla exactamente un FAIL."""
    bump = {
        "fastapi_pin": "0.162.0",
        "fastapi_cfg": "0.162",
        "fastapi_kb": "0.162.0",
        "uvicorn_pin": "0.54.0",
        "uvicorn_cfg": "0.54",
        "n8n": "2.11.2",
        "genai_req": ">=2.33.0,<3",
        "genai_doc": ">=2.33,<3",
    }
    raiz = _arbol_sincronizado(tmp_path, versiones=bump)
    assert all(c.status == "PASS" for c in _checks(raiz)), _summary(_checks(raiz))

    _mutar(raiz, CONFIG_REL, "deterministic_score: 0.5166", "deterministic_score: 0.4242")
    _solo_un_fail(_checks(raiz))


def test_bump_del_solo_pin_de_fastapi_aisla_solo_los_chequeos_de_version(tmp_path):
    """(triangulacion) si SOLO cambia el pin de FastAPI (el estado del PR de
    Dependabot), fallan unicamente los chequeos que comparan ese pin y nada mas."""
    raiz = _arbol_sincronizado(tmp_path)
    _mutar(raiz, REQUIREMENTS_REL, "fastapi==0.143.3", "fastapi==9.9.9")

    fails = _fails(_checks(raiz))
    assert len(fails) == 2, _summary(_checks(raiz))
    assert all("FastAPI" in (c.name + c.detail) for c in fails), _summary(_checks(raiz))


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
