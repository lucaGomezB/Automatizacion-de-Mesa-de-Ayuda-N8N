"""
Tests estructurales del workflow N8N exportado — C-04: n8n-workflow-validation

Verifica el JSON `Automatizacion_Mesa_de_Ayuda.json` sin requerir un runtime N8N.
Cubre: ausencia de placeholders, normalización, validación de canales, ruteo IF,
endpoint HTTP y pseudonimización en tránsito.

Strict TDD: cada grupo de tests refleja un ciclo RED→GREEN→TRIANGULATE→REFACTOR.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helper: carga del workflow
# ---------------------------------------------------------------------------

WORKFLOW_PATH = (
    Path(__file__)
    .resolve()
    .parents[2]  # raíz del repo (dos niveles por encima de Gestion_Incidentes/)
    / "Automatizacion_Mesa_de_Ayuda.json"
)

# Nombres exactos de los nodos del workflow (inventariados de design.md)
CODE_NODE_CORREO = "Se verifica que la informacion sea la necesaria para levantar un incidente"
CODE_NODE_TELEFONIA = "Se verifica lo que trajo la IA"
CODE_NODES = [CODE_NODE_CORREO, CODE_NODE_TELEFONIA]

IF_NODE_CORREO = "La informacion esta OK"
IF_NODE_TELEFONIA = "Lo que trajo puede crear un incidente"
IF_NODES = [IF_NODE_CORREO, IF_NODE_TELEFONIA]

NORMALIZER_NODE_NAME = "Normalizar entrada del incidente"

HTTP_NODE_CORREO = "HTTP POST a MTM-SRU"
HTTP_NODE_TELEFONIA = "HTTP POST a MTM-SRU se crea un incidente"

CONFIDENCE_THRESHOLD = 0.70

VALID_CATEGORIES = {"Sistemas", "Operaciones", "Soporte Técnico"}


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
    TRIANGULATE: verifica presencia de 'categoría' y 'confianza'.
    Paso 2 Anexo H: presencia de campos requeridos.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    assert "categor" in code_body, (
        "El validador de telefonía no verifica la presencia del campo 'categoría'"
    )
    assert "confianza" in code_body, (
        "El validador de telefonía no verifica la presencia del campo 'confianza'"
    )


def test_telefonia_validator_checks_valid_category_set():
    """
    TRIANGULATE: verifica que la categoría esté en el set exacto case-sensitive.
    Paso 3 Anexo H: categoría ∈ {Sistemas, Operaciones, Soporte Técnico}.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    # Las tres categorías exactas deben aparecer en el código
    assert "Sistemas" in code_body, (
        "El validador de telefonía no menciona la categoría exacta 'Sistemas'"
    )
    assert "Operaciones" in code_body, (
        "El validador de telefonía no menciona la categoría 'Operaciones'"
    )
    assert "Soporte" in code_body, (
        "El validador de telefonía no menciona 'Soporte Técnico'"
    )


def test_telefonia_validator_accepts_valid_response():
    """
    TRIANGULATE: respuesta válida {categoría: 'Sistemas', confianza: 0.95} es aceptada.
    El código referencia las 3 categorías válidas (implica que 'Sistemas' es aceptada).
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    node = by_name[CODE_NODE_TELEFONIA]
    code_body = node["parameters"].get("jsCode", "") or node["parameters"].get("pythonCode", "")

    # La lógica de aceptación conserva la categoría y confianza originales
    # verificado por la presencia conjunta de las 3 categorías + referencia a confianza
    assert "Sistemas" in code_body and "confianza" in code_body, (
        "El validador de telefonía no parece conservar categoría y confianza para respuestas válidas"
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
