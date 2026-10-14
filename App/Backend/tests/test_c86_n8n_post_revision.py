"""Test estructural del aviso post-revision en el workflow N8N (c-86, NR-008).

Verifica que `n8n/workflow.json` entrega el aviso a `destinatarios_gestion`:
    - El webhook `notificacion-clasificacion` rutea segun el marcador
      `incidente_validado_gestion`.
    - Un nodo code prepara un item por destinatario de `destinatarios_gestion`.
    - Un nodo emailSend notifica con credencial SMTP.
"""

import json
from pathlib import Path

WORKFLOW_PATH = (
    Path(__file__).resolve().parents[3] / "n8n" / "workflow.json"
)

MARCADOR = "incidente_validado_gestion"


def _by_name(workflow: dict) -> dict:
    return {n["name"]: n for n in workflow["nodes"]}


def _reachable(wf: dict, start: str, target: str) -> bool:
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
        for output_list in conns.get(current, {}).get("main", []):
            for edge in output_list:
                queue.append(edge["node"])
    return False


def test_workflow_documenta_el_marcador():
    """El marcador `incidente_validado_gestion` esta documentado en el workflow."""
    wf = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert MARCADOR in json.dumps(wf), "El marcador no aparece en el workflow"


def test_workflow_rutea_el_aviso_post_revision():
    """El webhook rutea el aviso y alcanza preparacion y notificacion."""
    wf = json.loads(WORKFLOW_PATH.read_text(encoding="utf-8"))
    by_name = _by_name(wf)

    assert "Es aviso post-revision?" in by_name
    gate = by_name["Es aviso post-revision?"]
    assert gate["type"] == "n8n-nodes-base.if"
    assert MARCADOR in json.dumps(gate.get("parameters", {}))

    preparar = by_name["Preparar destinatarios gestion"]
    assert preparar["type"] == "n8n-nodes-base.code"
    assert "destinatarios_gestion" in preparar["parameters"]["jsCode"]

    notificar = by_name["Notificar gestion post-revision"]
    assert notificar["type"] == "n8n-nodes-base.emailSend"
    assert "smtp" in (notificar.get("credentials") or {})

    assert _reachable(wf, "notificacion-clasificacion", "Es aviso post-revision?")
    assert _reachable(wf, "Es aviso post-revision?", "Preparar destinatarios gestion")
    assert _reachable(wf, "Preparar destinatarios gestion", "Notificar gestion post-revision")
