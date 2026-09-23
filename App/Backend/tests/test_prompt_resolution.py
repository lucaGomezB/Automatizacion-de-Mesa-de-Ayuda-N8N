"""
Tests de resolución de la ruta del prompt de Gemini (change c-01-foundation-setup).

Cubren los tres escenarios del requirement "Resolución del prompt de Gemini
independiente del cwd" (specs/foundation-environment/spec.md):
    1. El default se ancla a la raíz del repositorio (docs/prompt_gemini.txt),
       no al directorio de trabajo ni a BackEnd/docs/.
    2. La variable de entorno GEMINI_PROMPT_PATH tiene precedencia sobre el default.
    3. Ante ruta inexistente, _load_prompt degrada a la copia embebida sin lanzar.
"""

import types
from pathlib import Path

import app.classifiers.gemini_classifier as gemini_classifier
from app.classifiers.gemini_classifier import _load_prompt, _resolve_prompt_path
from app.config.settings import get_settings

# Layout plano equivalente al de la imagen Docker: build context ./App/Backend,
# COPY . . → /app/app/classifiers/gemini_classifier.py. Tiene solo 4 parents
# (índices 0..3), por lo que parents[4] lanza IndexError en tiempo de import.
_CONTAINER_MODULE_FILE = Path("/app/app/classifiers/gemini_classifier.py")


def test_default_path_resolver_accepts_shallow_module_path() -> None:
    """El resolver default no debe lanzar con un layout de menos de 5 parents (Docker)."""
    assert len(_CONTAINER_MODULE_FILE.resolve().parents) < 5

    resolved = gemini_classifier._default_prompt_path(_CONTAINER_MODULE_FILE)

    assert isinstance(resolved, Path)


def test_module_import_in_container_layout_does_not_raise() -> None:
    """Reejecutar el módulo con un __file__ plano (Docker) no debe lanzar al importar.

    Reproduce el fallo real: la evaluación ansiosa de `Path(__file__).parents[4]`
    en el cuerpo del módulo aborta `import app.main` y el contenedor nunca arranca.
    """
    source = Path(gemini_classifier.__file__).read_text(encoding="utf-8")
    shallow_file = _CONTAINER_MODULE_FILE

    module = types.ModuleType("gemini_classifier_container_layout")
    module.__file__ = str(shallow_file)

    # No debe lanzar IndexError (ni ninguna otra excepción) durante la ejecución.
    exec(compile(source, str(shallow_file), "exec"), module.__dict__)


def test_default_prompt_path_finds_docs_directory_in_repo() -> None:
    """El default debe encontrar docs/prompt_gemini.txt subiendo por los parents."""
    repo_root = Path(gemini_classifier.__file__).resolve().parents[4]
    expected = repo_root / "docs" / "prompt_gemini.txt"

    resolved = gemini_classifier._default_prompt_path()

    assert resolved == expected
    assert resolved.exists()


def test_default_prompt_path_falls_back_when_no_docs_found() -> None:
    """Sin docs/ en ningún parent, devuelve una ruta inexistente y no lanza."""
    resolved = gemini_classifier._default_prompt_path(_CONTAINER_MODULE_FILE)

    assert isinstance(resolved, Path)
    assert not resolved.exists()


def test_container_layout_import_degrades_to_embedded_prompt(monkeypatch) -> None:
    """En layout Docker sin docs/, el import completa y usa la copia embebida."""
    monkeypatch.delenv("GEMINI_PROMPT_PATH", raising=False)
    get_settings.cache_clear()
    try:
        source = Path(gemini_classifier.__file__).read_text(encoding="utf-8")
        module = types.ModuleType("gemini_classifier_container_degrade")
        module.__file__ = str(_CONTAINER_MODULE_FILE)

        exec(compile(source, str(_CONTAINER_MODULE_FILE), "exec"), module.__dict__)

        assert "INSTRUCCIÓN DE ROL" in module._PROMPT_TEMPLATE
    finally:
        get_settings.cache_clear()


def test_default_prompt_path_anchors_to_repo_root() -> None:
    """El default debe apuntar a docs/prompt_gemini.txt en la RAÍZ del repo y existir."""
    resolved = _resolve_prompt_path()

    # Ancla esperada: cuatro niveles arriba del módulo (classifiers→app→Backend→App→raíz)
    repo_root = Path(gemini_classifier.__file__).resolve().parents[4]
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
