"""
Tests estructurales c-72 (Section 2): la clasificacion telefonica deja de ocurrir
en n8n y la rama `AI Agent` se retira.

Contratos (design D2/D3/D8, specs n8n-workflow N8N-INTAKE-002 / N8N-UNIFY-001):
    - El POST de persistencia NO transporta una `clasificacion` precalculada.
    - La telefonia NO se clasifica en n8n: no existe el `AI Agent` ni su modelo
      Gemini en el workflow.
    - Ninguna rama terminal telefonica queda sin salida y existe un camino
      terminal con `requiere_revision_humana = true`.

Estructura TDD:
    - 2.2 RED: el POST telefonico no incluye `clasificacion`.
    - 2.4 GREEN (OQ1/OQ3): retiro del AI Agent y limpieza de huerfanos.
    - 2.5 RED: alcanzabilidad + camino terminal con revision humana.
    - 2.6/2.7 TRIANGULATE/REFACTOR: sin huerfanos, tests verdes.
"""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"

POST_NODE_NAME = "HTTP POST a MESA-AYUDAS"
TELEFONIA_TRIGGER = "Llamada telefonica"
SELLO_NODE_NAME = "Sellar ingreso telefonia"
NORMALIZER_NODE_NAME = "Normalizar entrada del incidente"
IF_ENTRADA_VALIDA = "Entrada valida"
IF_ES_WEB = "Es web?"
IF_ES_CORREO = "Es correo?"
DERIVAR_NODE_NAME = "Derivar a revision humana"

# Nodos de clasificacion en n8n que la decision OQ1=A retira por completo.
REMOVED_NODE_NAMES = {
    "AI Agent",
    "Google Gemini Chat Model",
    "Con el fin de enviar los datos que parsee la IA como JSON, se guardaran en memoria por un momento",
    "Se verifica lo que trajo la IA",
    "La clasificacion de la IA es valida",
    "Tope de refinamiento alcanzado",
    "Guard de costo",
    "Restaurar item telefonia",
    "Guard permite?",
    "Derivar a revision humana",
}

AGENT_TYPE = "@n8n/n8n-nodes-langchain.agent"
LANGUAGE_MODEL_TYPE_PREFIX = "@n8n/n8n-nodes-langchain.lm"

NON_EXECUTABLE_TYPES = {
    "n8n-nodes-base.stickyNote",
}


def load_workflow() -> dict:
    with WORKFLOW_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def index_nodes(workflow: dict) -> tuple[dict[str, dict], dict[str, list[dict]]]:
    by_name: dict[str, dict] = {}
    by_type: dict[str, list[dict]] = {}
    for node in workflow["nodes"]:
        by_name[node["name"]] = node
        by_type.setdefault(node["type"], []).append(node)
    return by_name, by_type


def output_successors(wf: dict, node_name: str, output_index: int) -> list[str]:
    conns = wf.get("connections", {}).get(node_name, {}).get("main", [])
    if output_index >= len(conns):
        return []
    return [edge["node"] for edge in conns[output_index]]


def reachable_from(wf: dict, start: str) -> set[str]:
    conns = wf.get("connections", {})
    visited: set[str] = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        for output_list in conns.get(current, {}).get("main", []):
            for edge in output_list:
                queue.append(edge["node"])
    return visited


def can_reach(wf: dict, start: str, target: str) -> bool:
    return target in reachable_from(wf, start)


# ---------------------------------------------------------------------------
# 2.2 RED — el POST telefonico no incluye clasificacion precalculada
# ---------------------------------------------------------------------------


def test_2_2_post_no_incluye_clasificacion_precalculada():
    """
    El body del POST de persistencia NO transporta `clasificacion` ni los campos
    `sector_predicho`/`confianza` producidos fuera del backend.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    assert POST_NODE_NAME in by_name, f"No existe el nodo {POST_NODE_NAME!r}"
    raw_body = str(by_name[POST_NODE_NAME]["parameters"].get("jsonBody", ""))

    assert "clasificacion" not in raw_body, (
        "El POST todavia transporta `clasificacion`: el backend podria saltear su cascada"
    )
    assert "sector_predicho" not in raw_body, (
        "El POST todavia transporta `sector_predicho` (clasificacion precalculada)"
    )
    assert "origen_message_id" in raw_body, (
        "El POST debe seguir enviando el identificador de origen"
    )
    assert "origen_evento" in raw_body, (
        "El POST debe seguir enviando el marcador explicito de origen/evento"
    )


# ---------------------------------------------------------------------------
# 2.4 GREEN (OQ1/OQ3) — retiro del AI Agent y su modelo
# ---------------------------------------------------------------------------


def test_2_4_no_existe_ai_agent_ni_modelo_de_lenguaje():
    """
    La telefonia NO se clasifica en n8n: no queda ningun nodo agente ni modelo de
    lenguaje (Gemini) en el workflow.
    """
    wf = load_workflow()
    _, by_type = index_nodes(wf)

    assert by_type.get(AGENT_TYPE, []) == [], (
        "El workflow conserva el nodo AI Agent: la telefonia seguiria clasificando en n8n"
    )
    lm_nodes = [
        node["name"]
        for node in wf["nodes"]
        if node["type"].startswith(LANGUAGE_MODEL_TYPE_PREFIX)
    ]
    assert lm_nodes == [], (
        f"El workflow conserva nodos de modelo de lenguaje: {lm_nodes}"
    )


def test_2_4_nodos_de_clasificacion_retirados():
    """Los nodos de clasificacion/refinamiento en n8n ya no existen."""
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    presentes = sorted(REMOVED_NODE_NAMES & set(by_name))
    assert presentes == [], f"Nodos de clasificacion no retirados: {presentes}"


def test_2_4_telefonia_alcanza_el_normalizador_sin_agente():
    """
    El webhook telefonico fluye al normalizador compartido y NO pasa por ningun
    nodo agente de n8n.
    """
    wf = load_workflow()
    reachable = reachable_from(wf, TELEFONIA_TRIGGER)
    assert NORMALIZER_NODE_NAME in reachable, (
        "La telefonia no alcanza el normalizador compartido"
    )
    by_name, _ = index_nodes(wf)
    agent_in_path = [
        name
        for name in reachable
        if by_name.get(name, {}).get("type", "").startswith(LANGUAGE_MODEL_TYPE_PREFIX)
        or by_name.get(name, {}).get("type") == AGENT_TYPE
    ]
    assert agent_in_path == [], (
        f"La ruta telefonica todavia atraviesa nodos de clasificacion: {agent_in_path}"
    )


# ---------------------------------------------------------------------------
# 2.5 RED — alcanzabilidad y camino terminal con revision humana
# ---------------------------------------------------------------------------


def test_2_5_telefonia_alcanza_un_terminal_de_persistencia():
    """
    La ruta telefonica NO queda truncada tras retirar el AI Agent: alcanza el
    normalizador compartido y la persistencia (POST /api/v1/incidentes).
    """
    wf = load_workflow()
    reachable = reachable_from(wf, TELEFONIA_TRIGGER)
    assert SELLO_NODE_NAME in reachable, (
        "El webhook telefonico no alcanza el sello de ingreso"
    )
    assert NORMALIZER_NODE_NAME in reachable, (
        "La ruta telefonica no alcanza el normalizador compartido (rama sin salida)"
    )
    assert POST_NODE_NAME in reachable, (
        "La ruta telefonica no alcanza la persistencia (rama sin salida)"
    )


def test_2_5_existe_camino_terminal_con_revision_humana():
    """
    Existe un camino terminal, alcanzable desde el webhook telefonico, que
    resuelve la revision humana: el gate post-POST `Requiere revision humana`
    lee el flag del backend y notifica al operador designado.
    """
    wf = load_workflow()
    reachable = reachable_from(wf, TELEFONIA_TRIGGER)

    assert "Requiere revision humana" in reachable, (
        "La ruta telefonica no alcanza el gate de revision humana post-POST"
    )
    assert "Notificar operador designado" in output_successors(
        wf, "Requiere revision humana", 0
    ), (
        "La rama de revision humana no desemboca en el terminal de notificacion"
    )


def test_2_5_sin_ramas_terminales_muertas_en_la_ruta_telefonica():
    """
    Ninguna rama terminal telefonica queda sin salida: todo nodo alcanzable que
    no sea un sumidero legitimo (respondToWebhook / emailSend / auditoria) tiene
    al menos una conexion de salida.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    reachable = reachable_from(wf, TELEFONIA_TRIGGER)

    sink_types = {
        "n8n-nodes-base.respondToWebhook",
        "n8n-nodes-base.emailSend",
    }
    # La auditoria es un sumidero de observabilidad (no rutea).
    allowed_sinks = {"Registro de auditoria"}

    sin_salida = []
    for name in reachable:
        node = by_name.get(name, {})
        node_type = node.get("type", "")
        if node_type in sink_types or name in allowed_sinks:
            continue
        branches = wf.get("connections", {}).get(name, {}).get("main", [])
        if sum(len(b) for b in branches) == 0:
            sin_salida.append(name)

    assert sin_salida == [], (
        f"Ramas terminales telefonicas sin salida: {sin_salida}"
    )


# ---------------------------------------------------------------------------
# 2.6/2.7 — sin huerfanos ejecutables
# ---------------------------------------------------------------------------


def test_2_7_no_hay_nodos_ejecutables_huerfanos():
    """
    Todo nodo ejecutable es alcanzable desde algun trigger (no quedan huerfanos
    tras retirar la rama de clasificacion).
    """
    wf = load_workflow()
    triggers = [
        "Llega un email a Mesa de Ayuda",
        "Webhook formulario web",
        TELEFONIA_TRIGGER,
        "notificacion-clasificacion",
    ]
    reachable: set[str] = set()
    for trigger in triggers:
        reachable |= reachable_from(wf, trigger)

    orphans = [
        node["name"]
        for node in wf["nodes"]
        if node["type"] not in NON_EXECUTABLE_TYPES and node["name"] not in reachable
    ]
    assert orphans == [], f"Nodos ejecutables huerfanos: {orphans}"


# ---------------------------------------------------------------------------
# N-3 — canal de origen invalido rechazado por el normalizador
# ---------------------------------------------------------------------------


def test_normalizer_rechaza_canal_de_origen_invalido():
    """
    N-3 (n8n-workflow, Normalizacion de canales): un `canal_raw` fuera de
    {correo, web, telefonia} NO se propaga como canal valido. El normalizador lo
    rechaza con `es_valido=false`, `canal_origen_id=null` y el marcador
    observable `error_normalizacion='canal_invalido'`, de modo que el IF
    compartido lo deriva a revision humana en lugar de persistir un canal nulo.
    """
    wf = load_workflow()
    by_name, _ = index_nodes(wf)
    code = by_name[NORMALIZER_NODE_NAME]["parameters"].get("jsCode", "")

    assert "CANALES_VALIDOS" in code, (
        "El normalizador no define el conjunto de canales validos"
    )
    assert "error_normalizacion" in code and "canal_invalido" in code, (
        "El normalizador no marca el canal invalido con error_normalizacion='canal_invalido'"
    )
    assert "canal_origen_id: null" in code, (
        "La rama de canal invalido no anula canal_origen_id"
    )
    assert "es_valido: false" in code, (
        "La rama de canal invalido no marca es_valido=false"
    )