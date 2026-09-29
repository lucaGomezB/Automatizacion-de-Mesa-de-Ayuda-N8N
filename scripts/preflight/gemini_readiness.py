"""Preflight estatico de la superficie Gemini del workflow (c-58-resiliencia-gemini).

Verifica, leyendo UNICAMENTE artefactos del repositorio, que la superficie Gemini
del workflow de n8n esta pineada y es resiliente:

- El nodo de modelo `@n8n/n8n-nodes-langchain.lmChatGoogleGemini` declara un
  `modelName` explicito no vacio (no depende del default implicito del nodo).
- El nodo `AI Agent` declara un reintento acotado y explicito
  (`retryOnFail` verdadero con `maxTries` dentro del tope y `waitBetweenTries`
  no menor al minimo).

NO accede a red, no requiere Docker ni credenciales y NO lee ni imprime la clave
de API. La sonda viva de disponibilidad queda explicitamente fuera de este
chequeo y del pipeline de CI (c-58 D6).

Contrato (mismo patron que `cost_readiness.py`):
- ``check_workflow(path)`` devuelve ``list[Check]``.
- ``run_gemini_readiness(path)`` devuelve ``list[Check]``.
- ``exit_code(checks)`` es 0 si y solo si TODOS los checks son PASS.
- ``format_summary(checks)`` renderiza la lista y la sintesis final.

CLI (desde la raiz del repo):
    python3 scripts/preflight/gemini_readiness.py
    python3 scripts/preflight/gemini_readiness.py --workflow X
"""

from __future__ import annotations

import argparse
import json
import pathlib
from dataclasses import dataclass
from typing import List, Optional

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

EXIT_OK = 0
EXIT_FAIL = 1

# Nombres y tipos anclados por la spec cost-readiness / n8n-workflow.
GEMINI_MODEL_NODE_NAME = "Google Gemini Chat Model"
GEMINI_MODEL_NODE_TYPE = "@n8n/n8n-nodes-langchain.lmChatGoogleGemini"
AI_AGENT_NODE_NAME = "AI Agent"
PAID_AGENT_TYPE = "@n8n/n8n-nodes-langchain.agent"

# Cotas del reintento acotado del agente (espejo de cost_readiness.py).
AGENT_MAX_TRIES_CAP = 3
AGENT_MIN_WAIT_BETWEEN_TRIES_MS = 500

GUARD_MODEL = "gemini: nodo de modelo declara modelName explicito"
GUARD_AGENT_RETRY = "gemini: AI Agent declara reintento acotado"


@dataclass
class Check:
    """Resultado de una guarda verificada."""

    name: str
    status: str
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == STATUS_PASS


def _passing(name: str, detail: str = "") -> Check:
    return Check(name=name, status=STATUS_PASS, detail=detail)


def _failing(name: str, detail: str) -> Check:
    return Check(name=name, status=STATUS_FAIL, detail=detail)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _nodes_by_name(workflow: dict) -> dict:
    return {node.get("name"): node for node in workflow.get("nodes", [])}


def _find_by_type(workflow: dict, node_type: str) -> Optional[dict]:
    for node in workflow.get("nodes", []):
        if node.get("type") == node_type:
            return node
    return None


def _find_gemini_model_node(workflow: dict) -> Optional[dict]:
    node = _find_by_type(workflow, GEMINI_MODEL_NODE_TYPE)
    if node is not None:
        return node
    # Fallback por nombre: permite reportar el nodo aunque el tipo derive.
    return _nodes_by_name(workflow).get(GEMINI_MODEL_NODE_NAME)


def _find_agent_node(workflow: dict) -> Optional[dict]:
    node = _find_by_type(workflow, PAID_AGENT_TYPE)
    if node is not None:
        return node
    return _nodes_by_name(workflow).get(AI_AGENT_NODE_NAME)


def _check_model_pinned(workflow: dict) -> Check:
    node = _find_gemini_model_node(workflow)
    if node is None:
        return _failing(
            GUARD_MODEL, "No existe el nodo de modelo Gemini en el workflow"
        )
    model_name = node.get("parameters", {}).get("modelName")
    if not isinstance(model_name, str) or not model_name.strip():
        return _failing(
            GUARD_MODEL,
            f"modelName ausente o vacio (modelName={model_name!r}): el modelo no "
            "debe depender del default implicito del nodo",
        )
    return _passing(GUARD_MODEL, model_name)


def _check_agent_retry(workflow: dict) -> Check:
    node = _find_agent_node(workflow)
    if node is None:
        return _failing(
            GUARD_AGENT_RETRY, f"No existe el nodo {AI_AGENT_NODE_NAME!r}"
        )
    retry = node.get("retryOnFail")
    max_tries = node.get("maxTries")
    wait = node.get("waitBetweenTries")

    if retry is not True:
        return _failing(
            GUARD_AGENT_RETRY,
            f"retryOnFail ausente o falso (retryOnFail={retry!r}): una falla "
            "transitoria del modelo abortaria la clasificacion telefonica",
        )
    if not _is_numeric(max_tries) or max_tries > AGENT_MAX_TRIES_CAP:
        return _failing(
            GUARD_AGENT_RETRY,
            f"maxTries ausente o fuera del tope de {AGENT_MAX_TRIES_CAP} "
            f"(maxTries={max_tries!r})",
        )
    if not _is_numeric(wait) or wait < AGENT_MIN_WAIT_BETWEEN_TRIES_MS:
        return _failing(
            GUARD_AGENT_RETRY,
            f"waitBetweenTries ausente o menor al minimo de "
            f"{AGENT_MIN_WAIT_BETWEEN_TRIES_MS} ms (waitBetweenTries={wait!r})",
        )
    return _passing(
        GUARD_AGENT_RETRY,
        f"retryOnFail=true maxTries={max_tries} waitBetweenTries={wait}",
    )


def check_workflow(path: "pathlib.Path | str") -> List[Check]:
    """Verifica la superficie Gemini del workflow exportado."""
    try:
        workflow = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [
            _failing(
                "gemini: workflow legible",
                f"No se pudo leer el workflow {path!r}: {exc}",
            )
        ]
    return [_check_model_pinned(workflow), _check_agent_retry(workflow)]


def run_gemini_readiness(
    workflow_path: "pathlib.Path | str" = WORKFLOW_PATH,
) -> List[Check]:
    """Ejecuta las guardas de la superficie Gemini sobre el workflow dado."""
    return check_workflow(workflow_path)


def exit_code(checks: List[Check]) -> int:
    """0 si y solo si hay checks y todos son PASS; 1 en cualquier otro caso."""
    if not checks:
        return EXIT_FAIL
    if all(check.ok for check in checks):
        return EXIT_OK
    return EXIT_FAIL


def format_summary(checks: List[Check]) -> str:
    """Renderiza cada check con su estado y la sintesis final."""
    lines = []
    for check in checks:
        line = f"[{check.status}] {check.name}"
        if check.detail:
            line += f" - {check.detail}"
        lines.append(line)
    passed = sum(1 for check in checks if check.ok)
    total = len(checks)
    lines.append("")
    if total and passed == total:
        lines.append(f"RESULT: {passed}/{total} guardas en PASS. Readiness GREEN.")
    else:
        failed = sum(1 for check in checks if check.status == STATUS_FAIL)
        lines.append(
            f"RESULT: {passed}/{total} guardas en PASS ({failed} en FAIL). "
            "Readiness RED."
        )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight estatico de la superficie Gemini del workflow: verifica "
            "el modelo pineado y el reintento acotado del agente sin red ni clave."
        )
    )
    parser.add_argument(
        "--workflow",
        default=str(WORKFLOW_PATH),
        help="Ruta al workflow exportado (default: n8n/workflow.json).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Punto de entrada CLI. Imprime el resumen y devuelve 0/1."""
    args = _build_parser().parse_args(argv)
    checks = run_gemini_readiness(args.workflow)
    print(format_summary(checks))
    return exit_code(checks)


if __name__ == "__main__":
    raise SystemExit(main())
