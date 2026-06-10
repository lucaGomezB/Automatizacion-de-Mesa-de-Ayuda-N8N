"""
Tests de resolución de la ruta del prompt de Gemini (change c-01-foundation-setup).

Cubren los tres escenarios del requirement "Resolución del prompt de Gemini
independiente del cwd" (specs/foundation-environment/spec.md):
    1. El default se ancla a la raíz del repositorio (docs/prompt_gemini.txt),
       no al directorio de trabajo ni a BackEnd/docs/.
    2. La variable de entorno GEMINI_PROMPT_PATH tiene precedencia sobre el default.
    3. Ante ruta inexistente, _load_prompt degrada a la copia embebida sin lanzar.
"""

from pathlib import Path

import app.classifiers.gemini_classifier as gemini_classifier
from app.classifiers.gemini_classifier import _load_prompt, _resolve_prompt_path
from app.config.settings import get_settings


def test_default_prompt_path_anchors_to_repo_root() -> None:
    """El default debe apuntar a docs/prompt_gemini.txt en la RAÍZ del repo y existir."""
    resolved = _resolve_prompt_path()

    # Ancla esperada: tres niveles arriba del módulo (classifiers→app→BackEnd→raíz)
    repo_root = Path(gemini_classifier.__file__).resolve().parents[3]
    assert resolved == repo_root / "docs" / "prompt_gemini.txt"
    # Regresión del bug prompt_file_not_found: la ruta default debe existir realmente
    assert resolved.exists(), f"El prompt no existe en la ruta resuelta: {resolved}"


def test_default_prompt_loads_real_content() -> None:
    """Con el default correcto, _load_prompt lee el archivo real (no la copia embebida)."""
    real_content = _resolve_prompt_path().read_text(encoding="utf-8").strip()
    assert _load_prompt() == real_content


def test_env_override_takes_precedence(monkeypatch, tmp_path) -> None:
    """GEMINI_PROMPT_PATH debe redirigir tanto la resolución como la carga."""
    custom = tmp_path / "prompt_custom.txt"
    custom.write_text("PROMPT DE PRUEBA PERSONALIZADO", encoding="utf-8")

    monkeypatch.setenv("GEMINI_PROMPT_PATH", str(custom))
    get_settings.cache_clear()
    try:
        assert _resolve_prompt_path() == custom
        assert _load_prompt() == "PROMPT DE PRUEBA PERSONALIZADO"
    finally:
        # Restaurar el caché para no contaminar otros tests
        get_settings.cache_clear()


def test_missing_prompt_degrades_to_embedded_copy(monkeypatch, tmp_path) -> None:
    """Ruta inexistente: warning + copia embebida, nunca una excepción (RN-CL-06)."""
    monkeypatch.setenv("GEMINI_PROMPT_PATH", str(tmp_path / "no_existe.txt"))
    get_settings.cache_clear()
    try:
        content = _load_prompt()  # no debe lanzar
        # La copia embebida replica el prompt real del Anexo H
        assert "INSTRUCCIÓN DE ROL" in content
        assert "Soporte Técnico" in content
    finally:
        get_settings.cache_clear()
