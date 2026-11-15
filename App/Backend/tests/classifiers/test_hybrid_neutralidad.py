"""
Neutralidad de la abstraccion del proveedor (c-227, D2; tareas 1.7 y 5.4).

Con el proveedor y el modelo por defecto, la etapa semantica a traves de la
INTERFAZ reproduce CASO POR CASO las predicciones congeladas de
`evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, sin invocar al SDK
pagado: un proveedor falso reproduce las respuestas registradas de Gemini. No
cambia ningun numero canonico ni el contrato canonico (cinco sectores, prompt y
parametros).
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[4]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

EVIDENCIA = _ROOT / "evaluation" / "evidence" / "predicciones_hybrid-v3_2026-10-07.json"
CORPUS = _ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"

_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_DELIMITADOR = "DESCRIPCIÓN DEL INCIDENTE:\n"


def _settings():
    from app.config.settings import Settings

    return Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-gemini-key",  # gitleaks:allow
        pseudonymization_encryption_key=_TEST_KEY,
        jwt_secret_key="fake-jwt-secret",
    )


def _cargar_corpus():
    from evaluation.corpus import cargar_corpus

    return cargar_corpus(CORPUS)


def _cargar_evidencia() -> list[dict]:
    return json.loads(EVIDENCIA.read_text(encoding="utf-8"))["predictions"]


class _ProveedorDesdeEvidencia:
    """Proveedor falso que reproduce las respuestas de Gemini de la evidencia.

    No importa el SDK: devuelve el JSON crudo reconstruido desde el sector y la
    confianza congelados. Un caso de etapa `fallback` en la evidencia simula la
    falla terminal del proveedor para reproducir el fallback del hibrido.
    """

    def __init__(self, por_descripcion: dict[str, dict]) -> None:
        self._por_descripcion = por_descripcion
        self.llamadas = 0

    async def generate(self, *, prompt: str, params) -> str:
        self.llamadas += 1
        descripcion = prompt.split(_DELIMITADOR, 1)[1]
        pred = self._por_descripcion[descripcion]
        if pred["etapa"] == "fallback":
            from app.classifiers.provider import InferenceTerminalError

            raise InferenceTerminalError("fallback simulado de la evidencia")
        return json.dumps(
            {"categoría": pred["sector_predicho"], "confianza": pred["confianza"]}
        )


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    from app.config.settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def _entorno(monkeypatch):
    """Fija Settings de prueba en los modulos que construyen el clasificador."""
    from app.classifiers import gemini_classifier as gemini_module
    from app.classifiers import hybrid as hybrid_module

    settings = _settings()
    monkeypatch.setattr(gemini_module, "get_settings", lambda: settings)
    monkeypatch.setattr(hybrid_module, "get_settings", lambda: settings)
    return settings


@pytest.mark.asyncio
async def test_neutralidad_reproduce_la_evidencia_caso_por_caso(_entorno) -> None:
    from app.classifiers.gemini_classifier import GeminiClassifier
    from app.classifiers.hybrid import HybridClassifier

    corpus = _cargar_corpus()
    preds = _cargar_evidencia()
    por_descripcion = {p["descripcion"]: p for p in preds}
    proveedor = _ProveedorDesdeEvidencia(por_descripcion)

    clasificador = HybridClassifier(gemini=GeminiClassifier(provider=proveedor))

    diferencias: list[str] = []
    for caso, esperado in zip(corpus, preds):
        resultado = await clasificador.classify(caso.descripcion)
        if (
            resultado.etapa != esperado["etapa"]
            or (resultado.sector_predicho or "") != (esperado["sector_predicho"] or "")
            or resultado.confianza != pytest.approx(esperado["confianza"])
            or list(resultado.sectores_adicionales)
            != list(esperado["sectores_adicionales"])
        ):
            diferencias.append(
                f"{caso.id}: obtenido=({resultado.etapa}, {resultado.sector_predicho}, "
                f"{resultado.confianza}) esperado=({esperado['etapa']}, "
                f"{esperado['sector_predicho']}, {esperado['confianza']})"
            )

    assert not diferencias, "la abstraccion altero predicciones:\n" + "\n".join(
        diferencias[:20]
    )
    # Solo los casos no deterministicos invocan al proveedor; el cortocircuito no.
    no_deterministicos = sum(1 for p in preds if p["etapa"] != "deterministic")
    assert proveedor.llamadas == no_deterministicos


def test_contrato_canonico_intacto(_entorno) -> None:
    """Los cinco sectores, el prompt y los parametros por defecto no cambian."""
    from app.classifiers.gemini_classifier import GeminiClassifier
    from app.classifiers.gemini_classifier import _PROMPT_TEMPLATE
    from app.constants import SECTORES_CANONICOS

    clasificador = GeminiClassifier(provider=_ProveedorDesdeEvidencia({}))

    enum = clasificador._generation_config.response_schema.properties["categoría"].enum
    assert tuple(enum) == SECTORES_CANONICOS

    params = clasificador._params
    assert (params.temperature, params.top_p) == (0.3, 0.9)
    assert (params.max_output_tokens, params.candidate_count) == (100, 1)
    assert params.model == "gemini-3.6-flash"

    for sector in SECTORES_CANONICOS:
        assert sector in _PROMPT_TEMPLATE
