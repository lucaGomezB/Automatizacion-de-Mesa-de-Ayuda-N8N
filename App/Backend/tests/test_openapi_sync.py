"""
Test de sincronía entre docs/openapi.json y el esquema generado por la app FastAPI.

Propósito (Decisión D3 del diseño de C-10):
    Detectar en CI cuando docs/openapi.json queda desactualizado respecto
    del esquema que la app genera en el momento.

Estrategia:
    1. Regenerar el esquema en memoria llamando a app.openapi().
    2. Cargar el archivo commiteado docs/openapi.json.
    3. Comparar ambos dicts; fallar con mensaje accionable si difieren.

El archivo docs/openapi.json está en la raíz del REPO, tres niveles arriba
de este directorio (App/Backend/tests/). Se localiza de forma
reproducible usando __file__ para no depender del directorio de trabajo.

Variables de entorno requeridas (mismas que CI de C-09):
    DATABASE_URL, GEMINI_API_KEY, PSEUDONYMIZATION_ENCRYPTION_KEY
    Se inyectan en conftest o vía el entorno del runner.
"""

import json
import os
from pathlib import Path

# El repo root es 3 niveles arriba de App/Backend/tests/
_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent.parent.parent  # repo root
_OPENAPI_PATH = _REPO_ROOT / "docs" / "openapi.json"


def _get_app_schema() -> dict:
    """Genera el esquema OpenAPI desde la app FastAPI en memoria."""
    from app.main import create_app

    app = create_app()
    # Forzar la generación del schema (FastAPI lo cachea en app.openapi_schema)
    app.openapi_schema = None
    return app.openapi()


def test_openapi_file_exists():
    """
    RED → GREEN: el archivo docs/openapi.json debe existir en el repo.

    Si falla, ejecutar el script de generación:
        cd App/Backend && python scripts/export_openapi.py
    """
    assert _OPENAPI_PATH.exists(), (
        f"docs/openapi.json no encontrado en {_OPENAPI_PATH}.\n"
        "Regenerarlo con: cd App/Backend && python scripts/export_openapi.py"
    )


def test_openapi_is_valid_json():
    """El archivo commiteado debe ser JSON válido."""
    if not _OPENAPI_PATH.exists():
        import pytest

        pytest.skip("openapi.json ausente — ejecutar test_openapi_file_exists primero")
    content = _OPENAPI_PATH.read_text(encoding="utf-8")
    try:
        json.loads(content)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"docs/openapi.json no es JSON válido: {exc}") from exc


def test_openapi_version_is_31():
    """El campo 'openapi' debe comenzar con '3.1'."""
    if not _OPENAPI_PATH.exists():
        import pytest

        pytest.skip("openapi.json ausente")
    schema = json.loads(_OPENAPI_PATH.read_text(encoding="utf-8"))
    version = schema.get("openapi", "")
    assert version.startswith("3.1"), (
        f"Se esperaba OpenAPI 3.1.x; se encontró '{version}'. "
        "Regenerar con scripts/export_openapi.py"
    )


def test_openapi_contains_expected_paths():
    """El spec debe contener las rutas de incidentes, clasificaciones y health."""
    if not _OPENAPI_PATH.exists():
        import pytest

        pytest.skip("openapi.json ausente")
    schema = json.loads(_OPENAPI_PATH.read_text(encoding="utf-8"))
    paths = schema.get("paths", {})
    expected_prefixes = ["/api/v1/incidentes", "/api/v1/clasificaciones", "/health"]
    for prefix in expected_prefixes:
        matching = [p for p in paths if p.startswith(prefix)]
        assert matching, (
            f"No se encontró ninguna ruta que comience con '{prefix}' en paths. "
            f"Rutas presentes: {sorted(paths.keys())}"
        )


def test_openapi_in_sync_with_app():
    """
    Caso principal de sincronía (triangulación caso en-sincronía):
    El archivo commiteado debe ser idéntico al esquema generado por la app.

    Falla con mensaje accionable si difieren:
        cd App/Backend && python scripts/export_openapi.py
    """
    if not _OPENAPI_PATH.exists():
        import pytest

        pytest.skip("openapi.json ausente — el test test_openapi_file_exists ya lo reporta")

    committed_schema = json.loads(_OPENAPI_PATH.read_text(encoding="utf-8"))
    live_schema = _get_app_schema()

    # Serializar ambos con la misma indentación y orden de claves para comparar
    committed_str = json.dumps(committed_schema, indent=2, sort_keys=True, ensure_ascii=False)
    live_str = json.dumps(live_schema, indent=2, sort_keys=True, ensure_ascii=False)

    assert committed_str == live_str, (
        "docs/openapi.json está DESACTUALIZADO respecto del esquema que la app genera.\n"
        "Regenerarlo con:\n"
        "    cd App/Backend\n"
        "    python scripts/export_openapi.py\n"
        "Luego commitear docs/openapi.json."
    )
