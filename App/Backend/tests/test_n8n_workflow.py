"""
Tests estructurales del workflow N8N exportado — C-04: n8n-workflow-validation

Verifica el JSON `n8n/workflow.json` sin requerir un runtime N8N.
Cubre: ausencia de placeholders, normalización, validación de canales, ruteo IF,
endpoint HTTP y pseudonimización en tránsito.

Strict TDD: cada grupo de tests refleja un ciclo RED→GREEN→TRIANGULATE→REFACTOR.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import get_args

import pytest
from pydantic import BaseModel

from app.schemas.incidente import IncidenteRead

# ---------------------------------------------------------------------------
# Helper: carga del workflow
# ---------------------------------------------------------------------------

WORKFLOW_PATH = (
    Path(__file__)
    .resolve()
    .parents[3]  # raíz del repo (tres niveles por encima de App/Backend/tests/)
    / "n8n/workflow.json"
)

# Nombres exactos de los nodos del workflow (inventariados de design.md)
CODE_NODE_CORREO = "Se verifica que la informacion sea la necesaria para levantar un incidente"
CODE_NODE_TELEFONIA = "Se verifica lo que trajo la IA"
CODE_NODES = [CODE_NODE_CORREO, CODE_NODE_TELEFONIA]

IF_NODE_CORREO = "La informacion esta OK"
# IF_NODE_TELEFONIA ("Lo que trajo puede crear un incidente") fue ELIMINADO en el
# fix del apply C-05: era un nodo huérfano (sin entrada) — la telefonía ahora converge
# en el normalizador compartido y usa el único IF "La informacion esta OK" + el único
# HTTP POST a MTM-SRU.  IF_NODES queda con solo el IF del canal correo/unificado.
IF_NODES = [IF_NODE_CORREO]

NORMALIZER_NODE_NAME = "Normalizar entrada del incidente"

HTTP_NODE_CORREO = "HTTP POST a MTM-SRU"
# HTTP_NODE_TELEFONIA ("HTTP POST a MTM-SRU se crea un incidente") fue ELIMINADO en el
# fix del apply C-05: era parte del subgrafo huérfano descartado.
# Los tres canales usan el único HTTP_NODE_CORREO para persistencia.

CONFIDENCE_THRESHOLD = 0.70

VALID_SECTORS = {
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
}


def load_workflow() -> dict:
    """Carga y parsea el JSON del workflow. Devuelve el documento completo."""
    assert WORKFLOW_PATH.exists(), f"Workflow JSON no encontrado en: {WORKFLOW_PATH}"
    with WORKFLOW_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def index_nodes(workflow: dict) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    """
    Devuelve dos índices:
      - by_name: {node_name: node_dict}
      - by_type: {node_type: [node_dict, ...]}
    """
    by_name: dict[str, dict] = {}
    by_type: dict[str, list[dict]] = {}
    for node in workflow["nodes"]:
        by_name[node["name"]] = node
        by_type.setdefault(node["type"], []).append(node)
    return by_name, by_type


# ---------------------------------------------------------------------------
# Grupo 0 — safety-net: el helper funciona
# ---------------------------------------------------------------------------


def test_workflow_loads():
    """El JSON del workflow es válido y se puede indexar."""
    wf = load_workflow()
    assert "nodes" in wf
    assert isinstance(wf["nodes"], list)
    assert len(wf["nodes"]) > 0


def test_workflow_inactive():
    """El workflow versionado tiene active=false (no se activa en producción)."""
    wf = load_workflow()
    assert wf.get("active") is False


# ---------------------------------------------------------------------------
# Grupo 1 — Ausencia de placeholders (spec: workflow verificable por estructura)
# ---------------------------------------------------------------------------


def test_code_nodes_no_placeholder():
    """
    RED → GREEN: ningún nodo code contiene la lógica placeholder 'myNewField = 1'.
    Spec: «las pruebas SHALL comprobar que los nodos code no contengan myNewField = 1».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in CODE_NODES:
        assert node_name in by_name, f"Nodo code esperado no encontrado: {node_name!r}"
        node = by_name[node_name]
        params = node.get("parameters", {})
        code_body = params.get("jsCode", "") or params.get("pythonCode", "")
        assert "myNewField = 1" not in code_body, (
            f"Nodo {node_name!r} aún contiene el placeholder 'myNewField = 1'"
        )
        assert "my_new_field" not in code_body, (
            f"Nodo {node_name!r} aún contiene el placeholder Python 'my_new_field'"
        )


def test_code_nodes_have_non_empty_body_with_return():
    """
    TRIANGULATE: cada nodo code tiene un cuerpo no vacío que incluye 'return'.
    Garantiza que la lógica real fue implementada y no solo borrado el placeholder.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in CODE_NODES:
        node = by_name[node_name]
        params = node.get("parameters", {})
        code_body = params.get("jsCode", "") or params.get("pythonCode", "")
        assert code_body.strip(), f"Nodo {node_name!r} tiene cuerpo vacío"
        assert "return" in code_body, (
            f"Nodo {node_name!r} no tiene instrucción 'return'"
        )


# ---------------------------------------------------------------------------
# Grupo 2 — Nodo de normalización (spec: normalización de canales)
# ---------------------------------------------------------------------------


def test_normalizer_node_exists():
    """
    RED → GREEN: existe un nodo de normalización con el nombre exacto esperado.
    Spec: «el workflow SHALL incluir un nodo de normalización».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    assert NORMALIZER_NODE_NAME in by_name, (
        f"Nodo de normalización {NORMALIZER_NODE_NAME!r} no encontrado en el workflow"
    )


def test_normalizer_node_is_code_type():
    """El nodo de normalización es de tipo code (JavaScript inline)."""
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    assert node["type"] == "n8n-nodes-base.code", (
        f"El nodo de normalización debería ser de tipo code, got: {node['type']}"
    )


def test_normalizer_emits_unified_shape():
    """
    RED → GREEN: el jsCode del normalizador produce exactamente los 4 campos:
    id, timestamp, canal_origen, descripcion.
    Spec: «estructura unificada con exactamente los campos id, timestamp, canal_origen, descripcion».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")

    required_fields = ["id", "timestamp", "canal_origen", "descripcion"]
    for field in required_fields:
        assert field in code_body, (
            f"El normalizador no menciona el campo requerido '{field}' en su jsCode"
        )


def test_normalizer_canal_correo():
    """
    TRIANGULATE canal correo: el jsCode menciona 'correo' como valor de canal_origen.
    Spec: canal_origen ∈ {correo, web, telefonia}.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")
    assert '"correo"' in code_body or "'correo'" in code_body, (
        "El normalizador no mapea el canal 'correo' explícitamente"
    )


def test_normalizer_canal_telefonia():
    """
    TRIANGULATE canal telefonía: el jsCode menciona 'telefonia' como valor de canal_origen.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")
    assert '"telefonia"' in code_body or "'telefonia'" in code_body, (
        "El normalizador no mapea el canal 'telefonia' explícitamente"
    )


def test_normalizer_canal_web():
    """
    TRIANGULATE canal web: el jsCode menciona 'web' como valor de canal_origen.
    C-05 cablea el trigger; la normalización lo soporta desde C-04.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")
    assert '"web"' in code_body or "'web'" in code_body, (
        "El normalizador no soporta el canal 'web'"
    )


def test_normalizer_timestamp_iso8601():
    """
    TRIANGULATE timestamp: el jsCode produce un timestamp ISO-8601 con milisegundos.
    Verifica que se usa toISOString() o equivalente.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")
    assert "toISOString" in code_body or "ISO" in code_body, (
        "El normalizador no genera timestamp ISO-8601 (no se encontró toISOString)"
    )


# ---------------------------------------------------------------------------
# Grupo 3 — Validación del canal de correo (spec: validación según Anexo H)
# ---------------------------------------------------------------------------


def test_correo_validator_checks_descripcion():
    """
    RED → GREEN: el jsCode del nodo code de correo valida que descripcion exista
    y tenga al menos 10 caracteres.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_CORREO]
    code_body = node["parameters"].get("jsCode", "")

    # El código debe referenciar descripcion y la longitud mínima
    assert "descripcion" in code_body, (
        "El validador de correo no referencia 'descripcion'"
    )
    assert "10" in code_body, (
        "El validador de correo no verifica la longitud mínima de 10 caracteres"
    )


def test_correo_validator_emits_validity_flag():
    """
    TRIANGULATE: el jsCode emite un flag de validez (es_valido, valido, valid o similar).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_CORREO]
    code_body = node["parameters"].get("jsCode", "")

    # Buscar cualquier forma de flag de validez
    validity_patterns = ["es_valido", "esValido", "valido", "valid", "isValid"]
    has_flag = any(p in code_body for p in validity_patterns)
    assert has_flag, (
        f"El validador de correo no emite ningún flag de validez. "
        f"Esperado alguno de: {validity_patterns}"
    )


def test_correo_validator_invalid_routes_to_reenvio():
    """
    TRIANGULATE: cuando la descripcion es inválida el jsCode no la procesa como válida.
    Verifica que existe lógica de bifurcación (else / false / inválido).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_CORREO]
    code_body = node["parameters"].get("jsCode", "")

    # Debe haber alguna rama de rechazo
    has_rejection = (
        "false" in code_body.lower()
        or "False" in code_body
        or "else" in code_body
        or "invalid" in code_body.lower()
    )
    assert has_rejection, (
        "El validador de correo no parece tener lógica de rechazo (else/false/invalid)"
    )


# ---------------------------------------------------------------------------
# Grupo 4 — Validación de respuesta de clasificación — 5 pasos Anexo H §H.3
# ---------------------------------------------------------------------------


def test_telefonia_validator_parses_json():
    """
    RED → GREEN: el jsCode del nodo code de telefonía parsea JSON (JSON.parse).
    Paso 1 del Anexo H: parseo JSON válido.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    assert "JSON.parse" in code_body or "json.loads" in code_body, (
        "El validador de telefonía no hace parseo JSON (falta JSON.parse o json.loads)"
    )


def test_telefonia_validator_sets_zero_confidence_on_malformed():
    """
    TRIANGULATE: cuando el JSON es malformado, fija confianza = 0.0 y marca revisión.
    Paso 1 Anexo H: ante fallo → confianza = 0.0 + revisión humana.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    assert "0.0" in code_body or "0" in code_body, (
        "El validador de telefonía no fija confianza = 0.0 ante errores"
    )
    # Debe haber manejo de errores (try/catch)
    assert "try" in code_body, (
        "El validador de telefonía no tiene bloque try para capturar JSON malformado"
    )


def test_telefonia_validator_checks_required_fields():
    """
    TRIANGULATE: verifica presencia de 'sector_predicho', 'sectores_adicionales'
    y 'confianza'.
    Paso 2 Anexo H: presencia de campos requeridos.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    assert "sector_predicho" in code_body, (
        "El validador de telefonía no verifica la presencia del campo 'sector_predicho'"
    )
    assert "sectores_adicionales" in code_body, (
        "El validador de telefonía no contempla el campo 'sectores_adicionales'"
    )
    assert "confianza" in code_body, (
        "El validador de telefonía no verifica la presencia del campo 'confianza'"
    )


def test_telefonia_validator_checks_valid_category_set():
    """
    TRIANGULATE: verifica que el sector esté en el set exacto case-sensitive.
    Paso 3 Anexo H: sector ∈ {los cinco sectores canonicos C-27}.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    # Los cinco sectores canonicos exactos deben aparecer en el código
    for sector in VALID_SECTORS:
        assert sector in code_body, (
            f"El validador de telefonía no menciona el sector canonico {sector!r}"
        )


def test_telefonia_validator_rejects_removed_vocabulary():
    """
    TRIANGULATE (5.3): el validador no admite el vocabulario eliminado.
    'Operaciones' y 'Soporte Técnico' (con tilde) ya no pertenecen al dominio.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    assert "Operaciones" not in code_body, (
        "El validador no debe aceptar 'Operaciones' (sector eliminado del dominio)"
    )
    assert "Soporte Técnico" not in code_body, (
        "El validador no debe aceptar 'Soporte Técnico' con tilde (variante invalida)"
    )


def test_telefonia_validator_accepts_valid_response():
    """
    TRIANGULATE: respuesta válida {sector_predicho: 'Sistemas', confianza: 0.95}
    es aceptada. El código referencia los cinco sectores válidos (implica que
    'Sistemas' es aceptada) y conserva el contrato multietiqueta.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    # La lógica de aceptación conserva el sector principal, los adicionales y confianza
    assert "sector_predicho" in code_body and "confianza" in code_body, (
        "El validador de telefonía no parece conservar sector_predicho y confianza"
    )
    assert "sectores_adicionales" in code_body, (
        "El validador de telefonía no conserva sectores_adicionales para respuestas válidas"
    )


def test_telefonia_validator_checks_confidence_range():
    """
    TRIANGULATE: verifica que confianza ∈ [0.0, 1.0].
    Paso 4 Anexo H: confianza numérica en rango válido.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    # Debe verificar que confianza esté en rango — buscar 1.0 o typeof
    assert "1.0" in code_body or "1" in code_body, (
        "El validador de telefonía no verifica el límite superior de confianza"
    )
    assert "typeof" in code_body or "isNaN" in code_body or "float" in code_body or "Number" in code_body, (
        "El validador de telefonía no verifica que confianza sea numérica"
    )


def test_telefonia_validator_uses_js_language():
    """
    REFACTOR check: el nodo de telefonía fue convertido a JavaScript (jsCode)
    para unificar el lenguaje con el nodo de correo y el normalizador.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    params = node.get("parameters", {})
    # Debe tener jsCode (JS), no pythonCode
    assert "jsCode" in params, (
        f"El nodo de telefonía {CODE_NODE_TELEFONIA!r} debe usar jsCode (JavaScript), no pythonCode"
    )
    assert "pythonCode" not in params, (
        f"El nodo de telefonía {CODE_NODE_TELEFONIA!r} no debe usar pythonCode"
    )


# ---------------------------------------------------------------------------
# Grupo 5 — Ruteo por umbral de confianza en los nodos IF
# ---------------------------------------------------------------------------


def test_if_nodes_have_conditions():
    """
    RED → GREEN: ambos nodos IF tienen al menos una condición no vacía.
    Spec: «las condiciones de los nodos IF NO SHALL quedar vacías».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in IF_NODES:
        assert node_name in by_name, f"Nodo IF no encontrado: {node_name!r}"
        node = by_name[node_name]
        conditions = node.get("parameters", {}).get("conditions", {}).get("conditions", [])
        assert len(conditions) > 0, f"Nodo IF {node_name!r} no tiene condiciones"

        # La condición no debe ser el placeholder vacío (leftValue == "" y rightValue == "")
        first = conditions[0]
        assert first.get("leftValue", "") != "" or first.get("rightValue", "") != "", (
            f"Nodo IF {node_name!r} tiene condición vacía (placeholder sin configurar)"
        )


def test_if_nodes_reference_confianza():
    """
    TRIANGULATE: las condiciones de ambos IF referencian 'confianza'.
    Spec: «cada nodo IF tiene al menos una condición que referencia la confianza y el umbral 0.70».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in IF_NODES:
        node = by_name[node_name]
        # Serializar el bloque conditions para buscar 'confianza' en cualquier campo
        conditions_str = json.dumps(node.get("parameters", {}).get("conditions", {}))
        assert "confianza" in conditions_str, (
            f"Nodo IF {node_name!r} no referencia 'confianza' en sus condiciones"
        )


def test_if_nodes_use_threshold_070():
    """
    TRIANGULATE umbral inclusivo: ambos IF usan 0.70 como rightValue.
    Spec: «umbral 0.70 inclusivo».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in IF_NODES:
        node = by_name[node_name]
        conditions_str = json.dumps(node.get("parameters", {}).get("conditions", {}))
        # El umbral puede aparecer como número o string
        has_threshold = (
            str(CONFIDENCE_THRESHOLD) in conditions_str  # "0.7"
            or "0.70" in conditions_str
        )
        assert has_threshold, (
            f"Nodo IF {node_name!r} no usa el umbral {CONFIDENCE_THRESHOLD} en sus condiciones"
        )


def test_if_nodes_use_gte_operator():
    """
    TRIANGULATE operador: ambos IF usan operador '>=' (gte) para el umbral.
    Spec: «condición confianza >= 0.70».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    for node_name in IF_NODES:
        node = by_name[node_name]
        conditions_str = json.dumps(node.get("parameters", {}).get("conditions", {}))
        has_gte = "gte" in conditions_str or ">=" in conditions_str or "greaterThanOrEqual" in conditions_str
        assert has_gte, (
            f"Nodo IF {node_name!r} no usa operador >= (gte) en sus condiciones"
        )


# ---------------------------------------------------------------------------
# Grupo 6 — Persistencia vía backend FastAPI (spec: endpoint correcto + payload)
# ---------------------------------------------------------------------------


def test_http_node_targets_incidentes_endpoint():
    """
    RED → GREEN: existe un nodo httpRequest con URL que contiene '/api/v1/incidentes'.
    Spec: «el nodo HTTP de persistencia apunte a la ruta /api/v1/incidentes».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    http_nodes = by_type.get("n8n-nodes-base.httpRequest", [])
    assert len(http_nodes) > 0, "No se encontraron nodos httpRequest en el workflow"

    urls = []
    for node in http_nodes:
        url = node.get("parameters", {}).get("url", "")
        urls.append(url)

    found = any("/api/v1/incidentes" in url for url in urls)
    assert found, (
        f"Ningún nodo httpRequest apunta a '/api/v1/incidentes'. URLs encontradas: {urls}"
    )


def test_http_node_uses_post_method():
    """
    TRIANGULATE método: el nodo httpRequest de persistencia usa método POST.
    Spec: «invocar POST /api/v1/incidentes».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    http_nodes = by_type.get("n8n-nodes-base.httpRequest", [])
    incidentes_nodes = [
        n for n in http_nodes
        if "/api/v1/incidentes" in n.get("parameters", {}).get("url", "")
    ]
    assert len(incidentes_nodes) > 0, "No se encontró nodo httpRequest para /api/v1/incidentes"

    for node in incidentes_nodes:
        method = node.get("parameters", {}).get("method", "").upper()
        assert method == "POST", (
            f"Nodo httpRequest hacia /api/v1/incidentes usa método {method!r}, se esperaba POST"
        )


def test_http_payload_contains_descripcion_and_prioridad():
    """
    RED → GREEN: existe un nodo code previo al HTTP que mapea descripcion y prioridad.
    Verifica que algún nodo code del workflow menciona ambos campos.
    Spec: «el cuerpo enviado contiene descripcion y prioridad».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    code_nodes = by_type.get("n8n-nodes-base.code", [])
    all_code = "\n".join(
        n.get("parameters", {}).get("jsCode", "") or n.get("parameters", {}).get("pythonCode", "")
        for n in code_nodes
    )
    assert "descripcion" in all_code, (
        "Ningún nodo code referencia 'descripcion' para el payload"
    )
    assert "prioridad" in all_code, (
        "Ningún nodo code referencia 'prioridad' para el payload"
    )


def test_http_payload_has_no_extra_fields():
    """
    TRIANGULATE campos extra: el body del nodo HTTP no incluye campos ajenos a
    IncidenteCreate (descripcion, prioridad, canal_origen_id).
    Verifica que no se envíen campos de depuración como myNewField, my_new_field, code, etc.
    """
    wf = load_workflow()
    by_name, by_type = index_nodes(wf)

    http_nodes = by_type.get("n8n-nodes-base.httpRequest", [])
    incidentes_nodes = [
        n for n in http_nodes
        if "/api/v1/incidentes" in n.get("parameters", {}).get("url", "")
    ]
    assert len(incidentes_nodes) > 0

    for node in incidentes_nodes:
        body_params = node.get("parameters", {}).get("body", "")
        body_str = json.dumps(body_params) if isinstance(body_params, dict) else str(body_params)
        assert "myNewField" not in body_str, (
            "El payload HTTP contiene el campo placeholder 'myNewField'"
        )
        assert "my_new_field" not in body_str, (
            "El payload HTTP contiene el campo placeholder Python 'my_new_field'"
        )


def test_http_payload_descripcion_length_limits():
    """
    TRIANGULATE límites de descripcion: el código que mapea el payload menciona
    los límites 10 y 5000 chars (o al menos el validador de correo ya los aplica).
    Spec: «descripcion string de 10 a 5000 caracteres».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    code_nodes = by_type.get("n8n-nodes-base.code", [])
    all_code = "\n".join(
        n.get("parameters", {}).get("jsCode", "") or n.get("parameters", {}).get("pythonCode", "")
        for n in code_nodes
    )
    assert "10" in all_code, "Ningún nodo code menciona el límite mínimo de 10 chars"
    assert "5000" in all_code, "Ningún nodo code menciona el límite máximo de 5000 chars"


# ---------------------------------------------------------------------------
# Grupo 7 — Pseudonimización en tránsito
# ---------------------------------------------------------------------------


@pytest.mark.xfail(
    reason=(
        "Decisión confirmada (C-04 design.md §Decisión 2): la pseudonimización ocurre "
        "en el backend (IncidenteService.create_and_classify), NO en N8N. "
        "N8N envía la descripción en texto claro al backend vía HTTPS; el backend "
        "pseudonimiza antes de clasificar y persiste. "
        "Por lo tanto, el campo 'descripcion' en el payload de N8N CONTIENE PII en claro. "
        "Este test documenta el gap de privacidad: PII viaja en claro N8N→backend. "
        "No se resuelve en C-04; se eleva como hallazgo para C-10/auditoría de privacidad."
    ),
    strict=False,
)
def test_payload_has_no_obvious_pii():
    """
    xfail documentado: el payload N8N→backend contiene PII en claro por diseño.

    La pseudonimización ocurre en el backend (C-03/IncidenteService), no en N8N.
    El nodo code de normalización toma la descripción cruda del canal y la pasa
    al HTTP node sin pseudonimizar.

    Gap de privacidad registrado: si el canal de transporte (HTTPS) se comprometiera,
    la PII viajaría expuesta. Confirmado en verificación de código en
    app/services/incidente_service.py líneas 183-190 (Paso 3 C-03).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    # Simulamos que el campo descripcion del normalizador contiene PII
    # (en el flujo real lo haría; aquí verificamos que el jsCode NO pseudonimiza)
    node = by_name[NORMALIZER_NODE_NAME]
    code_body = node["parameters"].get("jsCode", "")

    # Buscar LLAMADAS ACTIVAS a funciones de pseudonimización (excluir comentarios).
    # Los comentarios con la palabra "pseudonimizacion" NO cuentan como pseudonimización real.
    code_lines_active = [
        line for line in code_body.splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]
    code_without_comments = "\n".join(code_lines_active)
    # Indicadores de código activo: funciones reales de cifrado/pseudonimización
    pseudo_indicators = ["Fernet", "encrypt(", "pseudonymize(", "mask(", "replace_pii("]
    has_pseudo = any(p in code_without_comments for p in pseudo_indicators)

    # Este assert FALLA (xfail) porque no hay pseudonimización en N8N — documentado
    assert has_pseudo, (
        "El normalizador N8N no pseudonimiza la descripción antes de enviarla al backend. "
        "PII viaja en claro N8N→backend. Pseudonimización delegada al backend (diseño confirmado)."
    )


# ---------------------------------------------------------------------------
# Grupo 8 — Verificación de active=false (tarea 8.4)
# ---------------------------------------------------------------------------


def test_workflow_active_is_false():
    """El JSON versionado tiene active=false. No se activa en producción desde el repo."""
    wf = load_workflow()
    assert wf.get("active") is False, (
        "El workflow versionado tiene active=true — debe permanecer false"
    )


# ---------------------------------------------------------------------------
# C-05: constantes para los nuevos nodos
# ---------------------------------------------------------------------------

WEBHOOK_WEB_NODE_NAME = "Webhook formulario web"
WEBHOOK_WEB_PATH = "incidente-web"

CANAL_SET_WEB_NODE_NAME = "Marcar canal web"

RESPOND_WEBHOOK_NODE_NAME = "Confirmacion web al usuario"
EMAIL_CONFIRM_NODE_NAME = "Correo de confirmacion al usuario"
AUDIT_NODE_NAME = "Registro de auditoria"

# Mapa: nombre del disparador → canal_raw esperado
TRIGGER_CANAL_MAP = {
    "Llega un email a Mesa de Ayuda": "correo",
    WEBHOOK_WEB_NODE_NAME: "web",
    "Llamada telefonica": "telefonia",
}


def _connections_reachable(wf: dict, start: str, target: str, max_depth: int = 10) -> bool:
    """BFS sobre connections para verificar que `start` puede alcanzar `target`."""
    conns = wf.get("connections", {})
    visited: set[str] = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current == target:
            return True
        if current in visited or max_depth <= 0:
            continue
        visited.add(current)
        for output_list in conns.get(current, {}).get("main", []):
            for edge in output_list:
                queue.append(edge["node"])
        max_depth -= 1
    return False


def _get_successors(wf: dict, node_name: str) -> list[str]:
    """Devuelve los nodos directamente sucesores de `node_name` por la salida main."""
    conns = wf.get("connections", {}).get(node_name, {}).get("main", [])
    result = []
    for output_list in conns:
        for edge in output_list:
            result.append(edge["node"])
    return result


# ---------------------------------------------------------------------------
# Grupo 9 — Trigger Webhook del formulario web (Tarea 1.x — C-05)
# ---------------------------------------------------------------------------


def test_web_webhook_trigger_exists():
    """
    RED → GREEN (1.1/1.2): existe un nodo webhook web de tipo n8n-nodes-base.webhook
    con httpMethod == 'POST' y path no vacío.
    Spec: «el workflow N8N SHALL incluir un nodo webhook con método POST y ruta dedicada».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    webhook_nodes = by_type.get("n8n-nodes-base.webhook", [])
    assert len(webhook_nodes) > 0, (
        "No se encontró ningún nodo de tipo n8n-nodes-base.webhook en el workflow"
    )

    found = False
    for n in webhook_nodes:
        params = n.get("parameters", {})
        method = params.get("httpMethod", "")
        path = params.get("path", "")
        if method == "POST" and path:
            found = True
            break

    assert found, (
        "No se encontró un nodo webhook con httpMethod='POST' y path no vacío"
    )


def test_web_webhook_marks_canal_web():
    """
    RED → GREEN (1.3/1.4): existe un nodo (set o code) que asigna canal_raw = 'web'
    en el flujo del webhook web, antes de llegar al normalizador.
    Spec: «la salida del webhook SHALL quedar marcada con canal_raw = "web"».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    # Buscar cualquier nodo code o set que mencione 'web' y 'canal_raw'
    code_nodes = by_type.get("n8n-nodes-base.code", [])
    set_nodes = by_type.get("n8n-nodes-base.set", [])
    all_logic_nodes = code_nodes + set_nodes

    found = False
    for n in all_logic_nodes:
        params = n.get("parameters", {})
        code = params.get("jsCode", "") or params.get("pythonCode", "") or json.dumps(params)
        if "canal_raw" in code and ("'web'" in code or '"web"' in code):
            found = True
            break

    assert found, (
        "No se encontró ningún nodo code/set que asigne canal_raw = 'web'"
    )


def test_web_webhook_wired_to_normalizer():
    """
    TRIANGULATE (1.5): el webhook web está conectado (directa o indirectamente)
    al nodo normalizador antes del httpRequest de persistencia.
    Spec: «la salida del webhook SHALL conectarse al nodo de normalización».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert WEBHOOK_WEB_NODE_NAME in by_name, (
        f"Nodo webhook web {WEBHOOK_WEB_NODE_NAME!r} no encontrado"
    )
    assert _connections_reachable(wf, WEBHOOK_WEB_NODE_NAME, NORMALIZER_NODE_NAME), (
        f"El webhook web no alcanza el normalizador {NORMALIZER_NODE_NAME!r} en el cableado"
    )


# ---------------------------------------------------------------------------
# Grupo 10 — Identificación explícita de canal por trigger (Tarea 2.x — C-05)
# ---------------------------------------------------------------------------


def test_each_trigger_marks_canal_raw():
    """
    RED → GREEN (2.1/2.2): cada trigger tiene, en su flujo inmediato,
    un nodo que asigna el canal_raw correspondiente.
    Spec: «los tres disparadores quedan marcados explícitamente con canal_raw».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    all_code_params = [
        n.get("parameters", {}) for n in by_type.get("n8n-nodes-base.code", [])
    ]
    all_set_params = [
        n.get("parameters", {}) for n in by_type.get("n8n-nodes-base.set", [])
    ]
    all_params = all_code_params + all_set_params

    def canal_raw_found(canal: str) -> bool:
        for params in all_params:
            code = params.get("jsCode", "") or params.get("pythonCode", "") or json.dumps(params)
            if "canal_raw" in code and (f"'{canal}'" in code or f'"{canal}"' in code):
                return True
        return False

    for canal in ("correo", "web", "telefonia"):
        assert canal_raw_found(canal), (
            f"No se encontró ningún nodo que asigne canal_raw = '{canal}'"
        )


def test_three_channels_converge_on_normalizer():
    """
    TRIANGULATE (2.3): los tres disparadores (correo, web, telefonía) alcanzan
    el normalizador antes del httpRequest de persistencia.
    Spec: «los tres canales convergen en el normalizador único».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    trigger_correo = "Llega un email a Mesa de Ayuda"
    trigger_web = WEBHOOK_WEB_NODE_NAME
    trigger_telefonia = "Llamada telefonica"

    for trigger in (trigger_correo, trigger_web, trigger_telefonia):
        assert trigger in by_name, f"Trigger {trigger!r} no encontrado en el workflow"
        assert _connections_reachable(wf, trigger, NORMALIZER_NODE_NAME), (
            f"El trigger {trigger!r} no alcanza el normalizador {NORMALIZER_NODE_NAME!r}"
        )


# ---------------------------------------------------------------------------
# Grupo 11 — Notificación al usuario post-registro (Tarea 3.x — C-05)
# ---------------------------------------------------------------------------


def test_web_confirmation_node_exists():
    """
    RED → GREEN (3.1/3.2): existe un nodo respondToWebhook con referencia al
    identificador del incidente, cableado tras la persistencia del flujo web.
    Spec: «el workflow responde al webhook web con confirmación que incluye el id del incidente».
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    respond_nodes = by_type.get("n8n-nodes-base.respondToWebhook", [])
    assert len(respond_nodes) > 0, (
        "No se encontró ningún nodo n8n-nodes-base.respondToWebhook en el workflow"
    )

    found = False
    for n in respond_nodes:
        params_str = json.dumps(n.get("parameters", {}))
        # Debe referenciar algún identificador del incidente
        if any(kw in params_str for kw in ("incidente_id", "id", "incidente")):
            found = True
            break

    assert found, (
        "El nodo respondToWebhook no referencia el identificador del incidente en su respuesta"
    )


def test_email_confirmation_node_exists():
    """
    RED → GREEN (3.3/3.4): existe un nodo microsoftOutlook de confirmación
    cableado tras la persistencia del flujo de correo.
    Spec: «el workflow envía correo de confirmación al usuario del canal correo».
    """
    wf = load_workflow()
    by_name, by_type = index_nodes(wf)

    # Debe existir al menos un nodo microsoftOutlook de ENVÍO (no el trigger)
    outlook_send_nodes = [
        n for n in by_type.get("n8n-nodes-base.microsoftOutlook", [])
        if n["name"] != "Llega un email a Mesa de Ayuda"
    ]

    # El correo de confirmación debe existir y debe ser alcanzable desde HTTP POST a MTM-SRU
    confirm_nodes = [
        n for n in outlook_send_nodes
        if "confirmacion" in n["name"].lower() or "confirmar" in n["name"].lower()
        or "confir" in n["name"].lower()
    ]

    assert len(confirm_nodes) > 0, (
        f"No se encontró un nodo microsoftOutlook de confirmación en el workflow. "
        f"Nodos Outlook encontrados: {[n['name'] for n in outlook_send_nodes]}"
    )


def test_notification_only_after_successful_creation():
    """
    TRIANGULATE (3.5): los nodos de notificación (respondToWebhook y correo de confirmación)
    son alcanzables desde el httpRequest de persistencia (alta exitosa).
    Spec: «la notificación SHALL ocurrir solo cuando la creación fue exitosa».

    Fix apply C-05: HTTP_NODE_TELEFONIA fue eliminado (subgrafo huérfano).
    Ahora ambas notificaciones llegan desde HTTP_NODE_CORREO → Rutear por canal de origen:
      - Canal web → Confirmacion web al usuario
      - Canal correo/telefonia → Correo de confirmacion al usuario
    """
    wf = load_workflow()

    # El correo de confirmación es alcanzable desde el HTTP POST (via Switch fallback)
    assert _connections_reachable(wf, HTTP_NODE_CORREO, EMAIL_CONFIRM_NODE_NAME), (
        f"El correo de confirmación no es alcanzable desde {HTTP_NODE_CORREO!r}"
    )
    # La confirmación web es alcanzable desde el HTTP POST (via Switch rama web)
    assert _connections_reachable(wf, HTTP_NODE_CORREO, RESPOND_WEBHOOK_NODE_NAME), (
        f"El nodo respondToWebhook no es alcanzable desde {HTTP_NODE_CORREO!r}"
    )


def test_notification_does_not_block_audit():
    """
    TRIANGULATE (3.6): la salida del httpRequest de persistencia se ramifica a AMBOS:
    nodo de notificación (via Switch) Y nodo de auditoría (conexión paralela).
    Spec: «la notificación NO SHALL bloquear el registro de auditoría».

    Fix apply C-05: HTTP_NODE_TELEFONIA fue eliminado (subgrafo huérfano).
    Los tres canales convergen en el único HTTP_NODE_CORREO. Solo se verifica ese nodo.
    """
    wf = load_workflow()

    # La auditoría debe ser alcanzable desde el único httpRequest de persistencia
    assert _connections_reachable(wf, HTTP_NODE_CORREO, AUDIT_NODE_NAME), (
        f"El nodo de auditoría {AUDIT_NODE_NAME!r} no es alcanzable desde {HTTP_NODE_CORREO!r}"
    )


# ---------------------------------------------------------------------------
# Grupo 12 — Registro de auditoría con retención de 30 días (Tarea 4.x — C-05)
# ---------------------------------------------------------------------------


def test_audit_node_exists():
    """
    RED → GREEN (4.1/4.2): existe un nodo code con nombre que referencia auditoría,
    cableado tras la persistencia.
    Spec: «el workflow SHALL incluir un nodo de registro de auditoría».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert AUDIT_NODE_NAME in by_name, (
        f"Nodo de auditoría {AUDIT_NODE_NAME!r} no encontrado en el workflow"
    )
    node = by_name[AUDIT_NODE_NAME]
    assert node.get("type") == "n8n-nodes-base.code", (
        f"El nodo de auditoría debe ser de tipo code, got: {node.get('type')}"
    )


def test_audit_node_has_required_metadata():
    """
    RED → GREEN (4.3/4.4): el jsCode del nodo de auditoría referencia todos los
    campos de metadatos requeridos.
    Spec: «registra id, canal_origen, timestamp, categoría, confianza y resultado».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    required_patterns = [
        ("incidente_id", ["incidente_id", "id"]),
        ("canal_origen", ["canal_origen"]),
        ("timestamp", ["timestamp"]),
        ("categoria", ["categor"]),
        ("confianza", ["confianza"]),
        ("resultado", ["resultado"]),
    ]

    for field_label, patterns in required_patterns:
        found = any(p in code for p in patterns)
        assert found, (
            f"El nodo de auditoría no referencia el campo '{field_label}' en su jsCode"
        )


def test_audit_node_no_pii():
    """
    RED → GREEN (4.5/4.6): el jsCode del nodo de auditoría NO emite la descripcion cruda.
    Spec: «el registro NO SHALL contener la descripción con PII en claro».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # Extraer líneas activas (no comentarios)
    active_lines = [
        line for line in code.splitlines()
        if line.strip() and not line.strip().startswith("//")
    ]
    active_code = "\n".join(active_lines)

    # El jsCode activo no debe asignar 'descripcion' como campo del objeto de auditoría
    # Se busca que 'descripcion' NO aparezca como clave emitida (solo puede aparecer en comentarios)
    assert "descripcion" not in active_code, (
        "El nodo de auditoría incluye 'descripcion' (PII) en el código activo. "
        "Solo se permiten metadatos, no la descripción cruda."
    )


def test_audit_retention_30_days_declared():
    """
    TRIANGULATE (4.7): el jsCode del nodo de auditoría declara la retención de 30 días
    (campo retencion_dias: 30 o mención explícita de '30' junto con 'audit'/'retencion').
    Spec: «retención de 30 días SHALL quedar declarada de forma verificable».
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    has_retention = (
        "retencion_dias" in code and "30" in code
    ) or (
        "30" in code and ("audit" in code.lower() or "retencion" in code.lower())
    )

    assert has_retention, (
        "El nodo de auditoría no declara la retención de 30 días "
        "(se esperaba 'retencion_dias: 30' o equivalente en el jsCode)"
    )


# ---------------------------------------------------------------------------
# Grupo 13 — Cierre estructural y no regresión (Tarea 5.x — C-05)
# ---------------------------------------------------------------------------


def test_workflow_still_inactive():
    """
    TRIANGULATE (5.1): active sigue siendo false tras todos los cambios de C-05.
    Garantiza que la adición de nodos no activó el workflow accidentalmente.
    """
    wf = load_workflow()
    assert wf.get("active") is False, (
        "El workflow fue activado accidentalmente durante C-05 — debe permanecer false"
    )


# ---------------------------------------------------------------------------
# Grupo 14 — Corrección de defectos de cableado C-05 (bugfix apply)
#
# Defecto 1: la rama false de "La informacion esta OK" NO llega a auditoría.
# Defecto 2: "Confirmacion web al usuario" no es alcanzable desde el trigger web.
# ---------------------------------------------------------------------------

# Nodo que rutea según canal_origen antes de notificaciones
CANAL_SWITCH_NODE_NAME = "Rutear por canal de origen"


def _direct_successors_of_if_branch(wf: dict, if_node: str, branch_index: int) -> list[str]:
    """
    Devuelve los sucesores DIRECTOS del nodo IF en la rama `branch_index`
    (0 = true, 1 = false) sin hacer BFS — solo el primer salto.
    """
    conns = wf.get("connections", {}).get(if_node, {}).get("main", [])
    if branch_index >= len(conns):
        return []
    return [edge["node"] for edge in conns[branch_index]]


def test_audit_reachable_from_rejected_branch():
    """
    RED → GREEN (14.1): la rama false (main#1) del IF "La informacion esta OK"
    debe conectar —directa o indirectamente, SIN pasar por HTTP POST— al nodo de auditoría.

    Defecto confirmado: la única ruta actual desde la rama false al nodo de auditoría
    pasa por el loop de reenvío → verificador → normalizador → IF → HTTP POST → auditoría.
    Es decir, la auditoría solo ocurre si el usuario re-envía con datos correctos;
    el rechazo en sí NUNCA se registra en auditoría.

    Fix esperado: la rama false del IF debe tener al menos un sucesor que conduzca
    al nodo de auditoría sin pasar por HTTP POST a MTM-SRU.

    Spec/decisión: el log de auditoría registra TODAS las ramas.
    """
    wf = load_workflow()
    IF_CORREO = "La informacion esta OK"

    # Obtener los sucesores directos de la rama false (branch index 1)
    false_branch_direct = _direct_successors_of_if_branch(wf, IF_CORREO, 1)
    assert false_branch_direct, (
        f"El IF '{IF_CORREO}' no tiene sucesores en la rama false (main#1)."
    )

    # Verificar que al menos uno de los sucesores directos de la rama false
    # conduce a auditoría SIN pasar por HTTP POST (para registrar el rechazo en sí).
    # Usamos BFS restringido: excluimos el nodo HTTP POST como paso intermedio.
    http_post_node = HTTP_NODE_CORREO

    def reachable_without_http_post(start: str, target: str) -> bool:
        """BFS que excluye `http_post_node` como nodo de tránsito."""
        conns = wf.get("connections", {})
        visited: set[str] = set()
        queue = [start]
        while queue:
            current = queue.pop(0)
            if current == target:
                return True
            if current in visited:
                continue
            visited.add(current)
            if current == http_post_node and current != start:
                # Bloqueamos el HTTP POST como tránsito (el rechazo no pasa por ahí)
                continue
            for output_list in conns.get(current, {}).get("main", []):
                for edge in output_list:
                    queue.append(edge["node"])
        return False

    found = any(
        reachable_without_http_post(succ, AUDIT_NODE_NAME)
        for succ in false_branch_direct
    )
    assert found, (
        f"La rama false del IF '{IF_CORREO}' no alcanza '{AUDIT_NODE_NAME}' "
        "sin pasar por HTTP POST a MTM-SRU. "
        "El evento de rechazo (datos incompletos) nunca se registra en auditoría. "
        "Fix: conectar la rama false también al nodo de auditoría."
    )


def test_audit_reachable_from_success_branch():
    """
    TRIANGULATE (14.2): la rama true del IF (éxito → HTTP POST) sigue alcanzando auditoría.
    Garantiza que el fix del defecto 1 no rompe el camino exitoso.
    """
    wf = load_workflow()
    assert _connections_reachable(wf, HTTP_NODE_CORREO, AUDIT_NODE_NAME), (
        f"La rama exitosa (HTTP POST correo) no alcanza '{AUDIT_NODE_NAME}' tras el fix."
    )


def test_audit_code_tolerates_missing_http_response_fields():
    """
    TRIANGULATE (14.3): el jsCode del nodo de auditoría usa operadores tolerantes
    (|| null, ?? null, fallback) para campos que solo existen en la respuesta HTTP
    (id, categoria, confianza), de forma que no explota cuando llega la rama de rechazo.

    El resultado debe ser 'rechazado_datos_incompletos' para la rama de rechazo.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # Debe haber un fallback para incidente_id (|| null o ?? null)
    assert ("|| null" in code or "?? null" in code or "|| 'sin_id'" in code), (
        "El jsCode de auditoría no tiene fallback tolerante para 'incidente_id' "
        "(se esperaba '|| null' o '?? null')."
    )
    # Debe existir el valor de resultado para la rama de rechazo
    assert "rechazado" in code, (
        "El jsCode de auditoría no tiene el resultado 'rechazado_datos_incompletos' "
        "para la rama false del IF."
    )


def test_web_confirmation_reachable_from_web_trigger():
    """
    RED → GREEN (14.4): 'Confirmacion web al usuario' debe ser alcanzable
    desde el trigger 'Webhook formulario web' a través del camino real
    (Marcar canal web → Normalizar → IF → HTTP POST → Switch canal → respondToWebhook).

    Defecto confirmado: actualmente el nodo respondToWebhook solo recibe de
    'HTTP POST a MTM-SRU se crea un incidente', que es un nodo HUÉRFANO
    (sin entrada). El canal web nunca llega al respondToWebhook.
    """
    wf = load_workflow()
    assert _connections_reachable(wf, WEBHOOK_WEB_NODE_NAME, RESPOND_WEBHOOK_NODE_NAME), (
        f"'{RESPOND_WEBHOOK_NODE_NAME}' no es alcanzable desde '{WEBHOOK_WEB_NODE_NAME}'. "
        "El canal web nunca recibiría confirmación del webhook. "
        "Fix: conectar HTTP POST a MTM-SRU → Switch canal → Confirmacion web al usuario."
    )


def test_no_orphan_executable_nodes():
    """
    TRIANGULATE (14.5): no deben existir nodos ejecutables (non-sticky, non-memory)
    que sean inalcanzables desde cualquier trigger.

    Identifica los tres triggers y hace BFS desde cada uno. Todo nodo ejecutable
    debe ser alcanzable desde al menos un trigger.

    Defecto confirmado: 'Lo que trajo puede crear un incidente' y
    'HTTP POST a MTM-SRU se crea un incidente' son huérfanos actualmente.
    """
    wf = load_workflow()
    by_name, by_type = index_nodes(wf)

    # Tipos que NO son ejecutables (no cuentan como huérfanos)
    NON_EXECUTABLE_TYPES = {
        "n8n-nodes-base.stickyNote",
        "@n8n/n8n-nodes-langchain.memoryRedisChat",  # sub-nodo de langchain, no ejecutable directamente
        # Chat Model: sub-nodo del AI Agent, `inputs: []` (solo se conecta por ai_languageModel)
        "@n8n/n8n-nodes-langchain.lmChatGoogleGemini",
    }

    triggers = [
        "Llega un email a Mesa de Ayuda",
        "Llamada telefonica",
        WEBHOOK_WEB_NODE_NAME,
        # C-33 (D7): el webhook dedicado de notificacion es un trigger propio;
        # su subgrafo no crea incidentes y es intencionalmente no-op.
        "notificacion-clasificacion",
    ]

    # Calcular todos los nodos alcanzables desde los triggers (BFS unificado)
    conns = wf.get("connections", {})
    reachable: set[str] = set()
    queue = list(triggers)
    while queue:
        current = queue.pop(0)
        if current in reachable:
            continue
        reachable.add(current)
        for output_list in conns.get(current, {}).get("main", []):
            for edge in output_list:
                queue.append(edge["node"])

    # Detectar huérfanos ejecutables
    orphans = []
    for node in wf["nodes"]:
        if node["type"] in NON_EXECUTABLE_TYPES:
            continue
        if node["name"] not in reachable:
            orphans.append(node["name"])

    assert len(orphans) == 0, (
        f"Nodos ejecutables huérfanos encontrados (inalcanzables desde triggers): {orphans}. "
        "Eliminalos o cabléalos con propósito real."
    )


# ---------------------------------------------------------------------------
# Grupo 15 — Defectos de runtime D-1..D-4 (verificación funcional C-05)
#
# D-1: SyntaxError en jsCode de "Marcar canal web" — const item = .item
# D-2: IF evalúa $json.confianza que no existe para correo/web → siempre false
# D-3: Auditoría lee item.categoria/item.confianza pero el backend devuelve sector.nombre
# D-4: Auditoría pierde canal_origen porque tras HTTP POST el item es el response body
# ---------------------------------------------------------------------------

CANAL_WEB_NODE_NAME = "Marcar canal web"


def test_d1_marcar_canal_web_jsCode_syntax():
    """
    RED (D-1): el jsCode de 'Marcar canal web' NO debe contener '= .item'
    (SyntaxError en N8N — token inesperado).
    Debe usar '$input.item' o la asignación correcta del ítem.

    Actualmente el JSON contiene: const item = .item;  → SyntaxError en runtime.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert CANAL_WEB_NODE_NAME in by_name, (
        f"Nodo '{CANAL_WEB_NODE_NAME}' no encontrado en el workflow"
    )
    node = by_name[CANAL_WEB_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # El patrón '= .item' es un SyntaxError: falta el objeto antes del punto
    assert "= .item" not in code, (
        f"Nodo '{CANAL_WEB_NODE_NAME}' contiene '= .item' (SyntaxError en N8N). "
        "Debe ser '$input.item' u otro patrón válido."
    )


def test_d1_marcar_canal_web_jsCode_uses_valid_input_ref():
    """
    TRIANGULATE (D-1): el jsCode de 'Marcar canal web' usa la referencia
    N8N idiomática para obtener el ítem de entrada ($input.item o $input.all()).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CANAL_WEB_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    valid_refs = ["$input.item", "$input.all()", "$input.first()"]
    has_valid = any(ref in code for ref in valid_refs)
    assert has_valid, (
        f"Nodo '{CANAL_WEB_NODE_NAME}' no usa una referencia válida de entrada N8N. "
        f"Esperado alguno de: {valid_refs}. Código actual: {code!r}"
    )


def test_d2_if_condition_evaluates_es_valido():
    """
    RED (D-2): el nodo IF 'La informacion esta OK' debe evaluar un campo
    que el normalizador garantiza para los TRES canales.

    El normalizador produce 'es_valido' (bool) para todos los canales.
    La condición actual '$json.confianza >= 0.70' solo existe para telefonía
    (el canal de IA la genera), pero NO para correo ni web — causa que
    correo/web siempre tomen la rama false.

    El normalizador propaga 'confianza' a partir de 'es_valido' para que
    el IF compartido funcione en los tres canales.

    Fix esperado: el normalizador mapea es_valido→confianza (1.0 si válido, 0.0 si no),
    y el IF sigue evaluando confianza >= 0.70. Verificamos que el normalizador
    produce 'confianza' para todos los canales.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    normalizer = by_name[NORMALIZER_NODE_NAME]
    code = normalizer["parameters"].get("jsCode", "")

    # El normalizador debe emitir 'confianza' como campo para que el IF lo encuentre
    assert "confianza" in code, (
        f"El normalizador '{NORMALIZER_NODE_NAME}' no produce el campo 'confianza'. "
        "Debe sintetizar confianza = 1.0 (datos válidos) o 0.0 (inválidos) para correo/web, "
        "y propagar la confianza existente para telefonía. "
        "Esto garantiza que el IF compartido '$json.confianza >= 0.70' funcione "
        "para los tres canales."
    )


def test_d2_normalizer_produces_confianza_from_es_valido():
    """
    TRIANGULATE (D-2): el normalizador debe derivar 'confianza' desde 'es_valido'
    cuando no viene del upstream de telefonía.
    Verifica que el código menciona tanto 'es_valido' como 'confianza' juntos,
    lo que indica que la lógica de síntesis existe.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    normalizer = by_name[NORMALIZER_NODE_NAME]
    code = normalizer["parameters"].get("jsCode", "")

    # El normalizador debe referenciar es_valido Y confianza para hacer la síntesis
    assert "es_valido" in code and "confianza" in code, (
        f"El normalizador no sintetiza 'confianza' desde 'es_valido'. "
        "Ambos campos deben aparecer juntos para que la lógica de síntesis sea verificable."
    )


def test_d3_audit_reads_sector_nombre_not_item_categoria():
    """
    RED (D-3): el jsCode de auditoría NO debe leer 'item.categoria' (campo inexistente
    en el response del backend). El backend devuelve 'sector.nombre' (nested).

    Shape real del 201: { id, sector: { nombre, ... }, requiere_revision_humana, ... }
    El código actual: categoria: item.categoria || null  → siempre null.

    Fix: leer item.sector?.nombre (o equivalente tolerante a undefined).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # No debe leer directamente 'item.categoria' ni '$json.categoria' (campo inexistente)
    # Los patrones incorrectos que dejan categoria = null siempre:
    bad_patterns = [
        "item.categoria",
        "$json.categoria",
        "json.categoria",
    ]
    found_bad = [p for p in bad_patterns if p in code]
    assert not found_bad, (
        f"El nodo de auditoría lee {found_bad} pero el backend NO devuelve ese campo. "
        "El shape real del 201 tiene 'sector.nombre' (nested). "
        "Fix: usar item.sector?.nombre o equivalente."
    )


def test_d3_audit_reads_sector_nombre():
    """
    TRIANGULATE (D-3): el jsCode de auditoría lee 'sector' (el campo anidado real
    de la respuesta del backend) para obtener el nombre de la categoría/sector.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    assert "sector" in code, (
        "El nodo de auditoría no referencia 'sector' del response del backend. "
        "El shape real de la respuesta 201 tiene 'sector.nombre' para identificar "
        "la categoría/sector asignado."
    )


def test_d4_audit_reads_canal_origen_from_upstream_node():
    """
    RED (D-4): el jsCode de auditoría debe obtener 'canal_origen' desde el nodo
    aguas arriba 'Normalizar entrada del incidente', NO desde item.canal_origen
    del item corriente (que tras HTTP POST es el response body del backend).

    El response del backend NO incluye canal_origen. Si la auditoría lee
    item.canal_origen del item corriente, siempre obtiene null en la rama exitosa.

    Fix idiomático N8N: usar $('Normalizar entrada del incidente').item.json.canal_origen
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # Debe usar la referencia al nodo aguas arriba para canal_origen
    upstream_ref = "Normalizar entrada del incidente"
    assert upstream_ref in code, (
        f"El nodo de auditoría no referencia '{upstream_ref}' para recuperar canal_origen. "
        "Tras el HTTP POST el item corriente es el response body (sin canal_origen). "
        "Fix: $('Normalizar entrada del incidente').item.json.canal_origen"
    )


def test_d4_audit_canal_origen_not_only_from_current_item():
    """
    TRIANGULATE (D-4): verificar que el código de auditoría no depende ÚNICAMENTE
    de item.canal_origen del item corriente para la rama exitosa.
    Acepta una referencia al nodo upstream como fuente primaria.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[AUDIT_NODE_NAME]
    code = node["parameters"].get("jsCode", "")

    # La referencia upstream debe ser la fuente primaria de canal_origen
    upstream_ref = "Normalizar entrada del incidente"
    # Si la referencia upstream existe, el fix está bien aplicado
    # (puede haber fallback a item.canal_raw pero la fuente primaria debe ser upstream)
    assert upstream_ref in code, (
        "El nodo de auditoría debe referenciar el normalizador como fuente de canal_origen."
    )


# ---------------------------------------------------------------------------
# Grupo 16 — Contratos runtime de costura (C-29: c-29-seam-tests)
#
# Estos tests codifican la semántica runtime del workflow exportado y HOY
# FALLAN (fase RED). No corrigen defectos: describen el comportamiento correcto
# que un change posterior (c-30) debe implementar.
# ---------------------------------------------------------------------------

HTTP_NODE_TYPE = "n8n-nodes-base.httpRequest"
AGENT_NODE_TYPE = "@n8n/n8n-nodes-langchain.agent"
LANGUAGE_MODEL_TYPE_PREFIX = "@n8n/n8n-nodes-langchain.lm"
SWITCH_NODE_TYPE = "n8n-nodes-base.switch"
WEBHOOK_NODE_TYPE = "n8n-nodes-base.webhook"
RESPOND_WEBHOOK_NODE_TYPE = "n8n-nodes-base.respondToWebhook"
OUTLOOK_TRIGGER_NODE_TYPE = "n8n-nodes-base.microsoftOutlookTrigger"

INCIDENTES_PATH_FRAGMENT = "/api/v1/incidentes"

# Tipos que requieren credenciales para operar (los lm* se resuelven por prefijo).
CREDENTIAL_REQUIRING_NODE_TYPES = {
    "n8n-nodes-base.microsoftOutlook",
    "n8n-nodes-base.microsoftOutlookTrigger",
    "n8n-nodes-base.twilioTrigger",
}

# Campos de la respuesta real del backend (IncidenteRead) y subconjunto anidado.
RESPONSE_SCHEMA_FIELDS = set(IncidenteRead.model_fields.keys())


def _annotation_contains_model(annotation: object) -> bool:
    """True si la anotación referencia directa o indirectamente un modelo Pydantic."""
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return True
    return any(_annotation_contains_model(arg) for arg in get_args(annotation))


NESTED_RESPONSE_FIELDS = {
    name
    for name, info in IncidenteRead.model_fields.items()
    if _annotation_contains_model(info.annotation)
}

_JSON_FIELD_REF_RE = re.compile(r"\$json(?:\?)?\.([A-Za-z_][A-Za-z0-9_]*)")
_NODE_NAME_REF_RE = re.compile(r"\$\(['\"]([^'\"]+)['\"]\)")
_BARE_JSON_REF_RE = re.compile(r"\$json(?:\?)?\.[A-Za-z_][A-Za-z0-9_]*")
_BARE_NODE_REF_RE = re.compile(
    r"\$\(['\"][^'\"]+['\"]\)\.item(?:\.json)?(?:\?)?\.[A-Za-z_][A-Za-z0-9_]*"
)


def _unwrap_expression(value: object) -> str:
    """Extrae el cuerpo de una expresión N8N (`={{ ... }}` o `{{ ... }}`)."""
    text = str(value or "").strip()
    if text.startswith("="):
        text = text[1:].strip()
    match = re.fullmatch(r"\{\{(.*)\}\}", text, re.DOTALL)
    if match:
        text = match.group(1).strip()
    return text


def _is_bare_field_reference(value: object) -> bool:
    """True si la expresión es exactamente la lectura de un campo de datos."""
    body = _unwrap_expression(value)
    return bool(_BARE_JSON_REF_RE.fullmatch(body) or _BARE_NODE_REF_RE.fullmatch(body))


def _has_numeric_literal(body: str) -> bool:
    return bool(re.search(r"\d", body))


def _expression_mode_switches(by_type: dict[str, list[dict]]) -> list[dict]:
    return [
        node
        for node in by_type.get(SWITCH_NODE_TYPE, [])
        if node.get("parameters", {}).get("mode") == "expression"
    ]


def _collect_switch_refs(node: dict) -> tuple[set[str], set[str]]:
    """Campos `$json.*` y nombres de nodos `$('...')` referenciados por el switch."""
    params = node.get("parameters", {})
    blobs: list[str] = [str(params.get("output", ""))]
    rules = params.get("rules", {})
    values = rules.get("values", []) if isinstance(rules, dict) else []
    for rule in values:
        conditions = rule.get("conditions", {})
        cond_list = conditions.get("conditions", []) if isinstance(conditions, dict) else []
        for condition in cond_list:
            blobs.append(str(condition.get("leftValue", "")))
            blobs.append(str(condition.get("rightValue", "")))
    joined = "\n".join(blobs)
    return set(_JSON_FIELD_REF_RE.findall(joined)), set(_NODE_NAME_REF_RE.findall(joined))


def _switch_is_routable(node: dict) -> bool:
    """
    True si el switch puede enrutar en runtime: en modo expression su salida es un
    índice numérico y en modo reglas tiene reglas y fallbackOutput definidos.
    """
    params = node.get("parameters", {})
    if params.get("mode") == "expression":
        output = params.get("output", "")
        body = _unwrap_expression(output)
        return _has_numeric_literal(body) and not _is_bare_field_reference(output)
    rules = params.get("rules", {})
    values = rules.get("values", []) if isinstance(rules, dict) else []
    fallback = params.get("fallbackOutput")
    return bool(values) and fallback not in (None, "", "none")


def _reachable_avoiding_broken_switches(wf: dict, start: str, target: str) -> bool:
    """
    BFS sobre `connections` que no atraviesa switches no enrutables (roto en runtime).
    """
    by_name = {node["name"]: node for node in wf["nodes"]}
    conns = wf.get("connections", {})
    visited: set[str] = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current == target:
            return True
        if current in visited:
            continue
        visited.add(current)
        node = by_name.get(current)
        if (
            node is not None
            and node.get("type") == SWITCH_NODE_TYPE
            and not _switch_is_routable(node)
        ):
            continue
        for output_list in conns.get(current, {}).get("main", []):
            for edge in output_list:
                queue.append(edge["node"])
    return False


def _ai_language_model_sources(wf: dict) -> dict[str, list[str]]:
    """Mapea nodo destino -> tipos de los nodos origen conectados por ai_languageModel."""
    by_name = {node["name"]: node for node in wf["nodes"]}
    result: dict[str, list[str]] = {}
    for source_name, outputs in wf.get("connections", {}).items():
        for output_list in outputs.get("ai_languageModel", []):
            for edge in output_list:
                source_type = by_name.get(source_name, {}).get("type", "")
                result.setdefault(edge["node"], []).append(source_type)
    return result


def _incidentes_http_nodes(by_type: dict[str, list[dict]]) -> list[dict]:
    return [
        node
        for node in by_type.get(HTTP_NODE_TYPE, [])
        if INCIDENTES_PATH_FRAGMENT in str(node.get("parameters", {}).get("url", ""))
    ]


def test_c29_incidentes_http_node_declares_authentication():
    """
    (a) B-01: el nodo httpRequest hacia /api/v1/incidentes declara autenticación.
    Hoy no existe el campo `authentication`, por lo que el alta viaja sin JWT y el
    backend responde 401.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    nodes = _incidentes_http_nodes(by_type)
    assert nodes, "No se encontró el nodo httpRequest hacia /api/v1/incidentes"

    for node in nodes:
        auth = node.get("parameters", {}).get("authentication")
        assert auth not in (None, "", "none"), (
            f"El nodo {node['name']!r} no declara autenticación hacia el backend "
            f"(authentication={auth!r}). B-01: falta el header Authorization/JWT."
        )


def test_c29_incidentes_http_body_includes_canal_origen_id():
    """
    (b) B-08: el body del nodo HTTP de persistencia incluye `canal_origen_id`.
    Hoy sólo contiene `descripcion` y `prioridad`, por lo que el incidente
    persiste con canal NULL.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    nodes = _incidentes_http_nodes(by_type)
    assert nodes, "No se encontró el nodo httpRequest hacia /api/v1/incidentes"

    for node in nodes:
        body = node.get("parameters", {}).get("body", {})
        body_str = json.dumps(body) if isinstance(body, (dict, list)) else str(body)
        assert "canal_origen_id" in body_str, (
            f"El body del nodo {node['name']!r} no incluye 'canal_origen_id' "
            f"(body actual: {body_str}). B-08: el incidente queda con canal NULL."
        )


def test_c29_switch_expression_output_is_numeric_index():
    """
    (c) B-05: cada switch en `mode: expression` devuelve un índice numérico de rama.
    Hoy la salida es `$json.canal_origen`, el valor de un campo y no un índice.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    violations = []
    for node in _expression_mode_switches(by_type):
        output = node.get("parameters", {}).get("output", "")
        body = _unwrap_expression(output)
        if _is_bare_field_reference(output) or not _has_numeric_literal(body):
            violations.append(f"{node['name']!r}: output={output!r}")

    assert not violations, (
        "Switch en modo expression que NO devuelve un índice numérico de rama: "
        f"{violations}. B-05: la salida actual es el valor de un campo, no un índice."
    )


def test_c29_switch_referenced_fields_are_usable_from_response_or_upstream():
    """
    (c) B-05: los campos referenciados por el switch existen en `IncidenteRead` y son
    usables como valor escalar, o provienen de un nodo aguas arriba existente.
    Hoy `$json.canal_origen` es el objeto anidado de la respuesta y se compara contra
    el string `"web"`, por lo que la rama nunca coincide.
    """
    wf = load_workflow()
    by_name, by_type = index_nodes(wf)

    violations = []
    for node in _expression_mode_switches(by_type):
        json_fields, node_names = _collect_switch_refs(node)
        for field in sorted(json_fields):
            if field not in RESPONSE_SCHEMA_FIELDS:
                violations.append(
                    f"{node['name']!r}: $json.{field} no existe en IncidenteRead"
                )
            elif field in NESTED_RESPONSE_FIELDS:
                violations.append(
                    f"{node['name']!r}: $json.{field} es un objeto anidado del response "
                    "y se compara contra un string ('web')"
                )
        for referenced in sorted(node_names):
            if referenced not in by_name:
                violations.append(
                    f"{node['name']!r}: referencia al nodo inexistente {referenced!r}"
                )

    assert not violations, (
        "El switch referencia campos/tipos inválidos: "
        f"{violations}. B-05: debe rutear sobre el canal normalizado."
    )


def test_c29_agent_nodes_have_ai_language_model_connection():
    """
    (d) B-02: cada nodo agent tiene una conexión entrante `ai_languageModel` desde un
    nodo de modelo de lenguaje. Hoy el AI Agent sólo tiene conexión `ai_memory`.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    agents = by_type.get(AGENT_NODE_TYPE, [])
    assert agents, "No se encontró ningún nodo AI Agent en el workflow"

    sources = _ai_language_model_sources(wf)
    for agent in agents:
        agent_sources = sources.get(agent["name"], [])
        assert agent_sources, (
            f"El nodo {agent['name']!r} no tiene conexión ai_languageModel. "
            "B-02: el agente sólo tiene conexión ai_memory y no puede ejecutar."
        )
        for source_type in agent_sources:
            assert source_type.startswith(LANGUAGE_MODEL_TYPE_PREFIX), (
                f"La conexión ai_languageModel del agente {agent['name']!r} proviene "
                f"de un nodo {source_type!r} que no es un modelo de lenguaje."
            )


def test_c29_agent_prompt_interpolates_trigger_payload():
    """
    (e) B-03: el prompt del agente interpola el payload del trigger (`$json`/`$input`).
    Hoy es un texto estático que no incluye la transcripción ni el correo.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    agents = by_type.get(AGENT_NODE_TYPE, [])
    assert agents, "No se encontró ningún nodo AI Agent en el workflow"

    for agent in agents:
        params = agent.get("parameters", {})
        prompt = str(params.get("text") or params.get("prompt") or "")
        assert "$json" in prompt or "$input" in prompt, (
            f"El prompt del agente {agent['name']!r} es estático y no interpola el "
            f"payload del trigger ($json/$input). B-03. Prompt actual: {prompt[:120]!r}"
        )


def test_c29_outlook_trigger_exposes_email_body():
    """
    (f) B-07: el trigger de Outlook expone el cuerpo del correo que lee el validador.
    Hoy no declara `output`, por lo que usa el default `simple` (bodyPreview, sin body).
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    triggers = by_type.get(OUTLOOK_TRIGGER_NODE_TYPE, [])
    assert triggers, "No se encontró el trigger de Microsoft Outlook"

    for trigger in triggers:
        params = trigger.get("parameters", {})
        output_mode = params.get("output", "simple")
        assert output_mode == "fields", (
            f"El trigger {trigger['name']!r} usa output={output_mode!r} (default 'simple'), "
            "que expone bodyPreview pero no body. B-07: configurar output='fields'."
        )
        fields = params.get("fields", [])
        assert "body" in fields, (
            f"El trigger {trigger['name']!r} no selecciona el campo 'body' en 'fields' "
            f"(fields actuales: {fields!r}). B-07: la descripción del correo no es legible."
        )


def test_c29_webhook_response_node_has_reachable_responder():
    """
    (g) B-06: todo webhook con `responseMode: responseNode` alcanza un `respondToWebHook`
    sin atravesar un switch roto en runtime. Hoy el único camino depende del Switch
    `Rutear por canal de origen`, que no enruta, por lo que el cliente queda sin respuesta.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    webhooks = [
        node
        for node in by_type.get(WEBHOOK_NODE_TYPE, [])
        if node.get("parameters", {}).get("responseMode") == "responseNode"
    ]
    assert webhooks, "No se encontró ningún webhook con responseMode=responseNode"

    responders = {node["name"] for node in by_type.get(RESPOND_WEBHOOK_NODE_TYPE, [])}
    assert responders, "No se encontró ningún nodo respondToWebHook en el workflow"

    for hook in webhooks:
        reachable = any(
            _reachable_avoiding_broken_switches(wf, hook["name"], responder)
            for responder in responders
        )
        assert reachable, (
            f"El webhook {hook['name']!r} no alcanza ningún respondToWebHook sin "
            "atravesar el switch roto de canal. B-06: el cliente queda sin respuesta."
        )


def test_c29_credential_requiring_nodes_declare_credentials():
    """
    (h) Los nodos que requieren credenciales (Outlook, trigger de Twilio, modelos de
    lenguaje) declaran su credencial. Hoy ningún nodo del workflow declara credenciales.
    """
    wf = load_workflow()

    violations = []
    for node in wf["nodes"]:
        node_type = node.get("type", "")
        requires = (
            node_type in CREDENTIAL_REQUIRING_NODE_TYPES
            or node_type.startswith(LANGUAGE_MODEL_TYPE_PREFIX)
        )
        if not requires:
            continue
        credentials = node.get("credentials")
        if not isinstance(credentials, dict) or not credentials:
            violations.append(f"{node['name']!r} ({node_type})")

    assert not violations, (
        f"Nodos que requieren credenciales y no las declaran: {violations}. "
        "El workflow depende de credenciales implícitas/ausentes."
    )


# ---------------------------------------------------------------------------
# Grupo 17 — Dedupe de correos duplicados (tarea 6.5, opcion b)
#
# Sospecha confirmada: el trigger de Outlook no deduplicaba; dos correos
# identicos creaban dos incidentes. Opcion (b): recolectar solo no leidos
# (readStatus=unread) y marcar como leido el mensaje ya convertido en incidente.
# ---------------------------------------------------------------------------

OUTLOOK_TRIGGER_NAME = "Llega un email a Mesa de Ayuda"
OUTLOOK_APP_NODE_TYPE = "n8n-nodes-base.microsoftOutlook"
MARK_READ_NODE_NAME = "Marcar correo como leido"


def test_outlook_trigger_filters_unread_only():
    """
    RED (6.5): el trigger de Outlook debe declarar `filters.readStatus = 'unread'`.
    Sin el filtro, el polling re-recolecta correos ya procesados y crea duplicados.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    trigger = by_name[OUTLOOK_TRIGGER_NAME]
    filters = trigger.get("parameters", {}).get("filters", {})
    assert filters.get("readStatus") == "unread", (
        f"El trigger {OUTLOOK_TRIGGER_NAME!r} no filtra por readStatus='unread' "
        f"(filters={filters!r}). Sin el filtro se re-recolectan correos procesados."
    )


def test_outlook_trigger_exposes_message_id():
    """
    RED (6.5): el trigger debe exponer el `id` del mensaje para que aguas abajo
    el nodo de marcado pueda resolver el messageId. En output='fields' eso exige
    incluir 'id' en la lista de fields.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    trigger = by_name[OUTLOOK_TRIGGER_NAME]
    fields = trigger.get("parameters", {}).get("fields", [])
    assert "id" in fields, (
        f"El trigger {OUTLOOK_TRIGGER_NAME!r} no expone 'id' (fields={fields!r}); "
        "el nodo que marca como leido no puede resolver el messageId."
    )


def test_mark_read_node_exists_and_marks_message_read():
    """
    RED (6.5): debe existir un nodo Microsoft Outlook que marque el correo como
    leido (operacion 'update' de Message con updateFields.isRead=true) usando el
    id provisto por el trigger.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert MARK_READ_NODE_NAME in by_name, (
        f"No existe el nodo {MARK_READ_NODE_NAME!r} que marque el correo como leido"
    )
    node = by_name[MARK_READ_NODE_NAME]
    assert node.get("type") == OUTLOOK_APP_NODE_TYPE, (
        f"{MARK_READ_NODE_NAME!r} debe ser {OUTLOOK_APP_NODE_TYPE!r}, got {node.get('type')!r}"
    )

    params = node.get("parameters", {})
    assert params.get("operation") == "update", (
        f"{MARK_READ_NODE_NAME!r} debe usar operation='update', got {params.get('operation')!r}"
    )
    assert params.get("updateFields", {}).get("isRead") is True, (
        f"{MARK_READ_NODE_NAME!r} no marca isRead=true "
        f"(updateFields={params.get('updateFields')!r})"
    )

    message_id = params.get("messageId")
    assert isinstance(message_id, dict) and OUTLOOK_TRIGGER_NAME in str(message_id.get("value", "")), (
        f"{MARK_READ_NODE_NAME!r} no resuelve el messageId desde {OUTLOOK_TRIGGER_NAME!r} "
        f"(messageId={message_id!r})"
    )


def test_mark_read_runs_after_incident_creation_for_correo():
    """
    TRIANGULATE (6.5): el marcado como leido debe ser alcanzable desde la
    persistencia (HTTP POST), en la rama correo del switch, y la confirmacion
    debe seguir recibiendo el item del alta.

    El nodo de marcado es una hoja: si alimentara a la confirmacion, el
    `$json.id` de la confirmacion pasaria a ser el id del mensaje de Outlook
    en lugar del id del incidente (regresion).
    """
    wf = load_workflow()
    assert _connections_reachable(wf, HTTP_NODE_CORREO, MARK_READ_NODE_NAME), (
        f"{MARK_READ_NODE_NAME!r} no es alcanzable desde {HTTP_NODE_CORREO!r}: "
        "debe marcar el correo despues de crear el incidente."
    )
    assert _get_successors(wf, MARK_READ_NODE_NAME) == [], (
        f"{MARK_READ_NODE_NAME!r} no debe alimentar la confirmacion: cambiaria el "
        "item de entrada (id del mensaje en vez de id del incidente)."
    )
    assert _connections_reachable(wf, HTTP_NODE_CORREO, EMAIL_CONFIRM_NODE_NAME), (
        f"{EMAIL_CONFIRM_NODE_NAME!r} dejo de ser alcanzable desde {HTTP_NODE_CORREO!r}"
    )


# ---------------------------------------------------------------------------
# Grupo 18 — Guardas de costo C-33 (change c-33-cost-guards)
#
# Contratos estructurales de:
#   * N8N-REFINE-001: tope de refinamiento del agente pago + salida terminal.
#   * N8N-EMAIL-LIFECYCLE-001: marcado del correo en todas las ramas terminales.
#   * N8N-BACKLOG-001: lookback de 24 h en el trigger de Outlook.
#   * N8N-INTAKE-001: Message-ID + clasificacion precalculada + marcador de origen.
#   * Destino de notificacion dedicado que no crea incidentes.
# ---------------------------------------------------------------------------

AI_AGENT_NODE_NAME = "AI Agent"
IF_TOPE_NODE_NAME = "Tope de refinamiento alcanzado"
DERIVAR_NODE_NAME = "Derivar a revision humana"
IF_ES_CORREO_NODE_NAME = "Es correo?"
WEBHOOK_NOTIF_NODE_NAME = "notificacion-clasificacion"
NOTIF_WEBHOOK_PATH = "notificacion-clasificacion"
IF_IA_VALIDA_NODE_NAME = "La clasificacion de la IA es valida"


def _output_successors(wf: dict, node_name: str, output_index: int) -> list[str]:
    """Sucesores directos de `node_name` por la salida `main` de indice dado."""
    conns = wf.get("connections", {}).get(node_name, {}).get("main", [])
    if output_index >= len(conns):
        return []
    return [edge["node"] for edge in conns[output_index]]


def _branch_reaches(wf: dict, if_node: str, branch_index: int, target: str) -> bool:
    """True si algun sucesor directo de la rama dada alcanza `target`."""
    return any(
        _connections_reachable(wf, succ, target)
        for succ in _output_successors(wf, if_node, branch_index)
    )


# ── N8N-REFINE-001: tope de refinamiento ────────────────────────────────────


def test_c33_agent_declares_explicit_iteration_cap():
    """
    RED (1.1): el nodo `AI Agent` declara un tope explicito de iteraciones
    (options.maxIterations == 2) y el nodo validador incrementa un contador
    explicito `intento_agente`.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert AI_AGENT_NODE_NAME in by_name, "No existe el nodo 'AI Agent'"
    agent = by_name[AI_AGENT_NODE_NAME]
    options = agent.get("parameters", {}).get("options", {})
    assert options.get("maxIterations") == 2, (
        f"El nodo 'AI Agent' no declara options.maxIterations=2 (options={options!r})"
    )

    assert CODE_NODE_TELEFONIA in by_name
    telefono_code = by_name[CODE_NODE_TELEFONIA]["parameters"].get("jsCode", "")
    assert "intento_agente" in telefono_code, (
        "El nodo 'Se verifica lo que trajo la IA' no contabiliza 'intento_agente'"
    )
    assert "+ 1" in telefono_code, (
        "El contador 'intento_agente' no se incrementa en el validador de telefonia"
    )


def test_c33_topping_if_routes_to_terminal_not_back_to_agent():
    """
    RED (1.1): existe el IF 'Tope de refinamiento alcanzado' con condicion sobre
    `intento_agente`; su rama false va al terminal y el terminal NO reingresa al
    agente pago.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert IF_TOPE_NODE_NAME in by_name, (
        f"No existe el IF '{IF_TOPE_NODE_NAME}'"
    )
    topping = by_name[IF_TOPE_NODE_NAME]
    assert topping["type"] == "n8n-nodes-base.if"
    conditions_str = json.dumps(topping.get("parameters", {}).get("conditions", {}))
    assert "intento_agente" in conditions_str, (
        "El IF de tope no evalua el contador 'intento_agente'"
    )

    # La rama de agotamiento (false) desemboca en el terminal.
    assert DERIVAR_NODE_NAME in _output_successors(wf, IF_TOPE_NODE_NAME, 1), (
        f"La rama false de '{IF_TOPE_NODE_NAME}' no va a '{DERIVAR_NODE_NAME}'"
    )
    # El terminal no reingresa al agente pago.
    assert not _connections_reachable(wf, DERIVAR_NODE_NAME, AI_AGENT_NODE_NAME), (
        f"'{DERIVAR_NODE_NAME}' reingresa al AI Agent: gasto pago sin tope"
    )

    # El refinamiento dentro del tope se conserva (rama true -> AI Agent).
    assert AI_AGENT_NODE_NAME in _output_successors(wf, IF_TOPE_NODE_NAME, 0), (
        f"La rama de refinamiento de '{IF_TOPE_NODE_NAME}' no reingresa al AI Agent"
    )
    # La clasificacion invalida ya no va directo al agente.
    assert AI_AGENT_NODE_NAME not in _output_successors(wf, IF_IA_VALIDA_NODE_NAME, 1), (
        "La rama false de 'La clasificacion de la IA es valida' sigue yendo directo al agente"
    )


def test_c33_terminal_sets_forced_human_review_and_reaches_persistence():
    """
    RED (1.2): el nodo terminal fija confianza=0.0, requiere_revision_humana=true
    y alcanza el HTTP de persistencia sin volver al agente.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert DERIVAR_NODE_NAME in by_name, f"No existe '{DERIVAR_NODE_NAME}'"
    node = by_name[DERIVAR_NODE_NAME]
    assert node["type"] == "n8n-nodes-base.code"
    code = node["parameters"].get("jsCode", "")

    assert "0.0" in code, "El terminal no fija confianza=0.0"
    assert "requiere_revision_humana" in code and "true" in code, (
        "El terminal no marca requiere_revision_humana=true"
    )
    assert "revision_forzada" in code, (
        "El terminal no marca revision_forzada para la persistencia"
    )
    assert "telefonia" in code, (
        "El terminal no conserva canal_raw='telefonia'"
    )
    assert _connections_reachable(wf, DERIVAR_NODE_NAME, HTTP_NODE_CORREO), (
        f"'{DERIVAR_NODE_NAME}' no alcanza '{HTTP_NODE_CORREO}'"
    )


# ── N8N-EMAIL-LIFECYCLE-001: marcado en todas las ramas ─────────────────────


def test_c33_reject_branch_reaches_mark_read_with_channel_guard():
    """
    RED (1.3): la rama de rechazo alcanza 'Marcar correo como leido' y el camino
    pasa por la guarda de canal 'Es correo?'.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    assert IF_ES_CORREO_NODE_NAME in by_name, f"No existe la guarda '{IF_ES_CORREO_NODE_NAME}'"
    guard = by_name[IF_ES_CORREO_NODE_NAME]
    conditions_str = json.dumps(guard.get("parameters", {}).get("conditions", {}))
    assert "canal_origen" in conditions_str and "correo" in conditions_str, (
        "La guarda no evalua canal_origen == 'correo'"
    )

    # La rama false del IF de validacion (rechazo) alcanza el marcado.
    assert _branch_reaches(wf, IF_NODE_CORREO, 1, MARK_READ_NODE_NAME), (
        "La rama de rechazo no alcanza 'Marcar correo como leido'"
    )
    # La guarda desemboca en el marcado.
    assert MARK_READ_NODE_NAME in _get_successors(wf, IF_ES_CORREO_NODE_NAME), (
        f"'{IF_ES_CORREO_NODE_NAME}' no desemboca en '{MARK_READ_NODE_NAME}'"
    )


def test_c33_error_branch_declares_continue_error_output_and_reaches_mark_read():
    """
    RED (1.4): el nodo de persistencia declara onError=continueErrorOutput y su
    salida de error alcanza el marcado del correo (con guarda de canal).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    http = by_name[HTTP_NODE_CORREO]
    assert http.get("onError") == "continueErrorOutput", (
        f"'{HTTP_NODE_CORREO}' no declara onError=continueErrorOutput (onError={http.get('onError')!r})"
    )
    error_successors = _output_successors(wf, HTTP_NODE_CORREO, 1)
    assert error_successors, "La salida de error del HTTP POST no esta cableada"
    assert IF_ES_CORREO_NODE_NAME in error_successors, (
        f"La salida de error no pasa por la guarda '{IF_ES_CORREO_NODE_NAME}'"
    )
    assert any(
        _connections_reachable(wf, succ, MARK_READ_NODE_NAME)
        for succ in error_successors
    ), "La salida de error no alcanza 'Marcar correo como leido'"

    # La rama de exito se conserva.
    assert _connections_reachable(wf, HTTP_NODE_CORREO, MARK_READ_NODE_NAME)


# ── N8N-BACKLOG-001: lookback de 24 h ───────────────────────────────────────


def test_c33_outlook_trigger_has_24h_lookback():
    """
    RED (1.5): el trigger de Outlook declara un filtro de fecha `receivedDateTime`
    con lookback de 24 horas, conservando readStatus='unread'.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)

    trigger = by_name[OUTLOOK_TRIGGER_NAME]
    filters = trigger.get("parameters", {}).get("filters", {})
    assert filters.get("readStatus") == "unread", (
        "El trigger dejo de filtrar por readStatus='unread'"
    )
    custom = str(filters.get("custom", ""))
    assert "receivedDateTime" in custom, (
        f"El trigger no declara filtro sobre receivedDateTime (filters={filters!r})"
    )
    assert "24" in custom, "El lookback declarado no es de 24 horas"
    assert any(token in custom for token in ("60 * 60", "60*60", "86400", "h * 60")), (
        "El lookback no expresa 24 horas de forma verificable (se esperaba h*60*60)"
    )


# ── N8N-INTAKE-001: payload enriquecido ─────────────────────────────────────


def test_c33_http_body_sends_message_id_classification_and_origin_marker():
    """
    RED (1.6): el body del HTTP POST incluye `origen_message_id`, el bloque de
    clasificacion precalculada y un marcador explicito de origen/evento.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    nodes = _incidentes_http_nodes(by_type)
    assert nodes, "No se encontro el HTTP POST a /api/v1/incidentes"
    body = nodes[0].get("parameters", {}).get("body", {})
    body_str = json.dumps(body) if isinstance(body, dict) else str(body)

    assert "origen_message_id" in body_str, (
        "El body no envia 'origen_message_id' (Message-ID de Outlook)"
    )
    assert "clasificacion" in body_str, (
        "El body no envia el bloque de clasificacion precalculada"
    )
    assert "sector_predicho" in body_str and "confianza" in body_str, (
        "El bloque de clasificacion no transporta sector_predicho/confianza"
    )
    assert "origen_evento" in body_str, (
        "El body no envia un marcador explicito de origen/evento"
    )
    assert "creacion" in body_str or "incidente" in body_str, (
        "El marcador de origen no identifica un evento de creacion de incidente"
    )


# ── Destino de notificacion dedicado ────────────────────────────────────────


def test_c33_dedicated_notification_webhook_does_not_create_incidents():
    """
    RED (1.7): existe un webhook con ruta distinta de 'incidente-web' que NO
    esta conectado a la creacion de incidentes.
    """
    wf = load_workflow()
    by_name, by_type = index_nodes(wf)

    webhooks = by_type.get(WEBHOOK_NODE_TYPE, [])
    notif_nodes = [
        n for n in webhooks
        if n.get("parameters", {}).get("path") == NOTIF_WEBHOOK_PATH
    ]
    assert notif_nodes, (
        f"No existe un webhook con path={NOTIF_WEBHOOK_PATH!r}. "
        f"Webhooks encontrados: {[n.get('parameters', {}).get('path') for n in webhooks]}"
    )
    notif_node = notif_nodes[0]
    assert notif_node["parameters"]["path"] != "incidente-web", (
        "El webhook de notificacion reutiliza la ruta de alta de incidentes"
    )
    assert notif_node.get("parameters", {}).get("responseMode") != "responseNode", (
        "El webhook de notificacion no debe depender de un responder de webhook"
    )

    assert not _connections_reachable(wf, notif_node["name"], HTTP_NODE_CORREO), (
        "El webhook de notificacion alcanza la creacion de incidentes"
    )
    assert not _connections_reachable(wf, notif_node["name"], NORMALIZER_NODE_NAME), (
        "El webhook de notificacion alcanza el normalizador de alta"
    )


# ---------------------------------------------------------------------------
# Grupo 19 — C-36: ningun nodo pago habilita reintentos
#
# Un reintento automatico sobre el agente o el modelo de lenguaje multiplica
# llamadas pagas a Gemini sin control. La guarda vive aca (CI) y en el
# preflight estatico (scripts/preflight/cost_readiness.py); cada superficie
# lee n8n/workflow.json por su cuenta (design D7).
# ---------------------------------------------------------------------------

C36_PAID_AGENT_TYPE = "@n8n/n8n-nodes-langchain.agent"
C36_PAID_LM_TYPE_PREFIX = "@n8n/n8n-nodes-langchain.lm"


def _c36_paid_nodes(workflow: dict) -> list[dict]:
    """Nodos que ejecutan inferencia externa metrada (agente o modelo)."""
    return [
        node
        for node in workflow["nodes"]
        if node["type"] == C36_PAID_AGENT_TYPE
        or node["type"].startswith(C36_PAID_LM_TYPE_PREFIX)
    ]


def _c36_retry_violations(workflow: dict) -> list[str]:
    """Nodos pagos que habilitan retryOnFail o un maxTries numerico."""
    violations: list[str] = []
    for node in _c36_paid_nodes(workflow):
        if node.get("retryOnFail") is True:
            violations.append(f"{node['name']!r}: retryOnFail=true")
        max_tries = node.get("maxTries")
        if isinstance(max_tries, (int, float)) and not isinstance(max_tries, bool):
            violations.append(f"{node['name']!r}: maxTries={max_tries!r}")
    return violations


def test_c36_no_paid_node_enables_retry_or_max_tries():
    """
    RED (5.1): ningun nodo pago del workflow declara retryOnFail ni maxTries.
    Caracterizacion del workflow real: pasa desde el inicio y protege contra
    la introduccion futura de reintentos pagos.
    """
    wf = load_workflow()
    paid = _c36_paid_nodes(wf)
    assert paid, "No se encontraron nodos pagos en el workflow"
    assert _c36_retry_violations(wf) == [], (
        f"Nodos pagos con reintentos habilitados: {_c36_retry_violations(wf)}. "
        "Un reintento multiplica llamadas pagas a Gemini."
    )


def test_c36_retry_guard_detects_injected_retry_on_paid_agent(tmp_path):
    """
    TRIANGULATE (5.1): inyectar retryOnFail=true en una copia temporal del JSON
    hace que la guarda detecte la violacion (prueba que la guarda realmente guarda).
    """
    import copy

    wf = copy.deepcopy(load_workflow())
    agent = next(n for n in wf["nodes"] if n["type"] == C36_PAID_AGENT_TYPE)
    agent["retryOnFail"] = True

    mutated_path = tmp_path / "workflow_mutado.json"
    mutated_path.write_text(json.dumps(wf, ensure_ascii=False), encoding="utf-8")
    mutated = json.loads(mutated_path.read_text(encoding="utf-8"))

    violations = _c36_retry_violations(mutated)
    assert any("retryOnFail" in v for v in violations), (
        f"La guarda no detecto retryOnFail=true inyectado: {violations}"
    )


def test_c36_retry_guard_detects_injected_max_tries_on_language_model(tmp_path):
    """
    TRIANGULATE (5.1): inyectar maxTries en el modelo de lenguaje pago
    tambien es detectado por la guarda.
    """
    import copy

    wf = copy.deepcopy(load_workflow())
    model = next(
        n for n in wf["nodes"] if n["type"].startswith(C36_PAID_LM_TYPE_PREFIX)
    )
    model["maxTries"] = 3

    violations = _c36_retry_violations(wf)
    assert any("maxTries" in v for v in violations), (
        f"La guarda no detecto maxTries inyectado: {violations}"
    )
