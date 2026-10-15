"""Contrato OpenAPI: el parametro `q` aparece en el listado de incidentes (c-88, D7).

Verifica que `docs/openapi.json` (contrato estatico commiteado) declare el query
param `q` en la operacion GET del listado de incidentes. Falla hasta que el
esquema se regenere con `python scripts/export_openapi.py`.
"""

import json
from pathlib import Path

_THIS_FILE = Path(__file__).resolve()
_REPO_ROOT = _THIS_FILE.parent.parent.parent.parent
_OPENAPI_PATH = _REPO_ROOT / "docs" / "openapi.json"


def _parametros_get_listado() -> set[str]:
    schema = json.loads(_OPENAPI_PATH.read_text(encoding="utf-8"))
    operacion = schema["paths"]["/api/v1/incidentes/"]["get"]
    return {p["name"] for p in operacion.get("parameters", [])}


def test_openapi_declara_parametro_q_en_el_listado():
    """El GET /api/v1/incidentes/ declara el query param opcional `q`."""
    assert "q" in _parametros_get_listado()
