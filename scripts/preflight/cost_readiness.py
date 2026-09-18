"""Preflight estatico de preparacion de costo (C-36).

Verifica, leyendo unicamente artefactos del repositorio, que las guardas de
costo de c-33 (workflow) y c-34 (compose) estan cableadas antes de habilitar
servicios pagos. No accede a red, no requiere Docker ni credenciales.

Contrato:
- ``check_workflow(path)`` y ``check_compose(path)`` devuelven ``list[Check]``.
- ``run_preflight(workflow_path, compose_path)`` combina ambos.
- ``exit_code(checks)`` es 0 si y solo si TODOS los checks son PASS.
- ``format_summary(checks)`` renderiza la lista y el sintesis final.

CLI (desde la raiz del repo):
    python scripts/preflight/cost_readiness.py
    python scripts/preflight/cost_readiness.py --workflow X --compose Y
"""

from __future__ import annotations

import argparse
import json
import pathlib
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional

try:  # PyYAML se declara en scripts/preflight/requirements.txt
    import yaml  # type: ignore
except ImportError:  # pragma: no cover - se ejercita simulando yaml = None
    yaml = None  # type: ignore

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / "n8n" / "workflow.json"
COMPOSE_PATH = REPO_ROOT / "docker-compose.yml"

STATUS_PASS = "PASS"
STATUS_FAIL = "FAIL"

EXIT_OK = 0
EXIT_FAIL = 1

# Nombres de nodos y rutas anclados por la spec cost-readiness (literales).
AI_AGENT_NODE = "AI Agent"
HTTP_NODE = "HTTP POST a MTM-SRU"
IF_NODE_CORREO = "Entrada valida"
MARK_READ_NODE = "Marcar correo como leido"
NORMALIZER_NODE = "Normalizar entrada del incidente"
NOTIF_WEBHOOK_PATH = "notificacion-clasificacion"
INCIDENTES_PATH_FRAGMENT = "/api/v1/incidentes"
WEBHOOK_NODE_TYPE = "n8n-nodes-base.webhook"
HTTP_NODE_TYPE = "n8n-nodes-base.httpRequest"
OUTLOOK_TRIGGER_TYPE = "n8n-nodes-base.microsoftOutlookTrigger"
PAID_AGENT_TYPE = "@n8n/n8n-nodes-langchain.agent"
PAID_LM_TYPE_PREFIX = "@n8n/n8n-nodes-langchain.lm"
WEBHOOK_NOTIF_URL = "/webhook/notificacion-clasificacion"


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


# ---------------------------------------------------------------------------
# Helpers de navegacion del workflow
# ---------------------------------------------------------------------------
def _nodes_by_name(workflow: dict) -> dict:
    return {node["name"]: node for node in workflow.get("nodes", [])}


def _find_node_by_type(workflow: dict, node_type: str) -> Optional[dict]:
    for node in workflow.get("nodes", []):
        if node.get("type") == node_type:
            return node
    return None


def _main_outputs(workflow: dict, name: str) -> list:
    connections = workflow.get("connections", {}).get(name, {})
    return connections.get("main", [])


def _successors(workflow: dict, name: str, output_index: int) -> List[str]:
    outputs = _main_outputs(workflow, name)
    if output_index >= len(outputs):
        return []
    return [edge["node"] for edge in outputs[output_index]]


def _bfs_first(workflow: dict, start: str, predicate: Callable[[str, Optional[dict]], bool]) -> bool:
    """BFS sobre las conexiones `main`; True si algun nodo satisface `predicate`."""
    by_name = _nodes_by_name(workflow)
    visited = set()
    queue = [start]
    while queue:
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        if predicate(current, by_name.get(current)):
            return True
        for output in _main_outputs(workflow, current):
            for edge in output:
                queue.append(edge["node"])
    return False


def _reachable(workflow: dict, start: str, target: str) -> bool:
    """BFS sobre las conexiones `main`, siguiendo todas las salidas."""
    return _bfs_first(workflow, start, lambda name, _node: name == target)


def _reaches_predicate(workflow: dict, start: str, predicate: Callable[[dict], bool]) -> bool:
    return _bfs_first(
        workflow,
        start,
        lambda _name, node: node is not None and predicate(node),
    )


def _is_paid_node(node: dict) -> bool:
    node_type = str(node.get("type", ""))
    return node_type == PAID_AGENT_TYPE or node_type.startswith(PAID_LM_TYPE_PREFIX)


def _is_numeric(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _body_to_text(body: object) -> str:
    if isinstance(body, (dict, list)):
        return json.dumps(body, ensure_ascii=False)
    return str(body or "")


# ---------------------------------------------------------------------------
# Guardas del workflow
# ---------------------------------------------------------------------------
WORKFLOW_GUARD_AGENT = (
    "workflow: AI Agent declara tope de iteraciones (options.maxIterations)"
)
WORKFLOW_GUARD_OUTLOOK = (
    "workflow: trigger de Outlook filtra no leidos con lookback de 24h"
)
WORKFLOW_GUARD_MARK_READ = (
    "workflow: 'Marcar correo como leido' alcanzable desde exito/rechazo/error"
)
WORKFLOW_GUARD_BODY = (
    "workflow: body de 'HTTP POST a MTM-SRU' con origen_message_id + "
    "clasificacion + origen_evento"
)
WORKFLOW_GUARD_NOTIF = (
    "workflow: webhook dedicado 'notificacion-clasificacion' aislado de la "
    "creacion de incidentes"
)
WORKFLOW_GUARD_RETRY = (
    "workflow: ningun nodo pago habilita reintentos (retryOnFail/maxTries)"
)


def _check_agent_iterations(workflow: dict) -> Check:
    by_name = _nodes_by_name(workflow)
    agent = by_name.get(AI_AGENT_NODE)
    if agent is None:
        return _failing(WORKFLOW_GUARD_AGENT, f"No existe el nodo {AI_AGENT_NODE!r}")
    options = agent.get("parameters", {}).get("options", {})
    max_iterations = options.get("maxIterations")
    if not _is_numeric(max_iterations) or max_iterations <= 0:
        return _failing(
            WORKFLOW_GUARD_AGENT,
            f"options.maxIterations ausente o no acotado (options={options!r})",
        )
    return _passing(WORKFLOW_GUARD_AGENT, f"maxIterations={max_iterations}")


def _check_outlook_lookback(workflow: dict) -> Check:
    trigger = _find_node_by_type(workflow, OUTLOOK_TRIGGER_TYPE)
    if trigger is None:
        return _failing(
            WORKFLOW_GUARD_OUTLOOK, "No existe el trigger de Outlook"
        )
    filters = trigger.get("parameters", {}).get("filters", {})
    if filters.get("readStatus") != "unread":
        return _failing(
            WORKFLOW_GUARD_OUTLOOK,
            f"readStatus != 'unread' (filters={filters!r})",
        )
    custom = str(filters.get("custom", ""))
    has_field = "receivedDateTime" in custom
    has_24h = "24" in custom and any(
        token in custom for token in ("60 * 60", "60*60", "86400", "h * 60", "h*60")
    )
    if not (has_field and has_24h):
        return _failing(
            WORKFLOW_GUARD_OUTLOOK,
            f"lookback de 24h sobre receivedDateTime ausente (custom={custom!r})",
        )
    return _passing(WORKFLOW_GUARD_OUTLOOK, "readStatus=unread + lookback 24h")


def _check_mark_read_reachable(workflow: dict) -> Check:
    by_name = _nodes_by_name(workflow)
    if MARK_READ_NODE not in by_name:
        return _failing(
            WORKFLOW_GUARD_MARK_READ, f"No existe el nodo {MARK_READ_NODE!r}"
        )

    success = any(
        _reachable(workflow, succ, MARK_READ_NODE)
        for succ in _successors(workflow, HTTP_NODE, 0)
    )
    error = any(
        _reachable(workflow, succ, MARK_READ_NODE)
        for succ in _successors(workflow, HTTP_NODE, 1)
    )
    reject = any(
        _reachable(workflow, succ, MARK_READ_NODE)
        for succ in _successors(workflow, IF_NODE_CORREO, 1)
    )
    if success and error and reject:
        return _passing(WORKFLOW_GUARD_MARK_READ, "exito, rechazo y error alcanzan")
    missing = [
        label
        for label, reached in (
            ("exito", success),
            ("rechazo", reject),
            ("error", error),
        )
        if not reached
    ]
    return _failing(
        WORKFLOW_GUARD_MARK_READ,
        f"no alcanzable desde: {', '.join(missing)}",
    )


def _check_enriched_body(workflow: dict) -> Check:
    by_name = _nodes_by_name(workflow)
    node = by_name.get(HTTP_NODE)
    if node is None:
        return _failing(WORKFLOW_GUARD_BODY, f"No existe el nodo {HTTP_NODE!r}")
    body_text = _body_to_text(node.get("parameters", {}).get("body"))
    required = (
        "origen_message_id",
        "clasificacion",
        "sector_predicho",
        "confianza",
        "origen_evento",
    )
    missing = [key for key in required if key not in body_text]
    if missing:
        return _failing(
            WORKFLOW_GUARD_BODY, f"faltan en el body: {', '.join(missing)}"
        )
    return _passing(WORKFLOW_GUARD_BODY, "origen_message_id + clasificacion + evento")


def _check_notification_webhook(workflow: dict) -> Check:
    webhooks = [
        node
        for node in workflow.get("nodes", [])
        if node.get("type") == WEBHOOK_NODE_TYPE
        and node.get("parameters", {}).get("path") == NOTIF_WEBHOOK_PATH
    ]
    if not webhooks:
        return _failing(
            WORKFLOW_GUARD_NOTIF,
            f"No existe un webhook con path={NOTIF_WEBHOOK_PATH!r}",
        )
    node = webhooks[0]
    node_name = node["name"]

    def _is_incident_creation(candidate: dict) -> bool:
        if candidate.get("type") == HTTP_NODE_TYPE and INCIDENTES_PATH_FRAGMENT in str(
            candidate.get("parameters", {}).get("url", "")
        ):
            return True
        return candidate.get("name") == NORMALIZER_NODE

    if _reaches_predicate(workflow, node_name, _is_incident_creation):
        return _failing(
            WORKFLOW_GUARD_NOTIF,
            f"El webhook {node_name!r} alcanza la creacion de incidentes",
        )
    return _passing(
        WORKFLOW_GUARD_NOTIF, f"path={NOTIF_WEBHOOK_PATH!r} sin ruta a incidentes"
    )


def _check_paid_retries(workflow: dict) -> Check:
    violations = []
    for node in workflow.get("nodes", []):
        if not _is_paid_node(node):
            continue
        if node.get("retryOnFail") is True:
            violations.append(f"{node['name']!r}: retryOnFail=true")
        if _is_numeric(node.get("maxTries")):
            violations.append(f"{node['name']!r}: maxTries={node['maxTries']!r}")
    if violations:
        return _failing(WORKFLOW_GUARD_RETRY, "nodos pagos con reintentos: " + "; ".join(violations))
    return _passing(WORKFLOW_GUARD_RETRY, "ningun nodo pago reintenta")


def check_workflow(path: "pathlib.Path | str") -> List[Check]:
    """Verifica las guardas del workflow exportado."""
    try:
        workflow = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [
            _failing(
                "workflow: legible", f"No se pudo leer el workflow {path!r}: {exc}"
            )
        ]

    checks = [
        _check_agent_iterations(workflow),
        _check_outlook_lookback(workflow),
        _check_mark_read_reachable(workflow),
        _check_enriched_body(workflow),
        _check_notification_webhook(workflow),
        _check_paid_retries(workflow),
    ]
    return checks


# ---------------------------------------------------------------------------
# Guardas del compose
# ---------------------------------------------------------------------------
COMPOSE_GUARD_IMAGE = "compose: imagen del servicio n8n pineada a version explicita"
COMPOSE_GUARD_WEBHOOK_URL = (
    "compose: N8N_WEBHOOK_URL apunta a la ruta dedicada de notificacion"
)
COMPOSE_GUARD_TIMEOUT = (
    "compose: EXECUTIONS_TIMEOUT declarado en el environment de n8n"
)
COMPOSE_GUARD_TIMEOUT_COHERENT = (
    "compose: cotas EXECUTIONS_TIMEOUT/EXECUTIONS_TIMEOUT_MAX coherentes"
)


def _n8n_environment(compose: dict) -> dict:
    services = compose.get("services", {}) if isinstance(compose, dict) else {}
    n8n = services.get("n8n", {}) if isinstance(services, dict) else {}
    env = n8n.get("environment", {}) if isinstance(n8n, dict) else {}
    return env if isinstance(env, dict) else {}


def _iter_environment_values(compose: dict, key: str) -> Iterable[str]:
    services = compose.get("services", {}) if isinstance(compose, dict) else {}
    for service in services.values() if isinstance(services, dict) else []:
        env = service.get("environment", {}) if isinstance(service, dict) else {}
        if isinstance(env, dict) and key in env:
            yield str(env[key])


def _check_pinned_image(compose: dict) -> Check:
    services = compose.get("services", {}) if isinstance(compose, dict) else {}
    n8n = services.get("n8n", {}) if isinstance(services, dict) else {}
    image = str(n8n.get("image", "")) if isinstance(n8n, dict) else ""
    if not image:
        return _failing(COMPOSE_GUARD_IMAGE, "El servicio n8n no declara image")
    tag = image.rsplit(":", 1)[1] if ":" in image.rsplit("/", 1)[-1] else ""
    if not tag or tag == "latest":
        return _failing(
            COMPOSE_GUARD_IMAGE, f"La imagen no esta pineada a version explicita: {image!r}"
        )
    return _passing(COMPOSE_GUARD_IMAGE, image)


def _check_webhook_url(compose: dict) -> Check:
    values = list(_iter_environment_values(compose, "N8N_WEBHOOK_URL"))
    if not values:
        return _failing(
            COMPOSE_GUARD_WEBHOOK_URL, "N8N_WEBHOOK_URL no esta declarada"
        )
    if not any(value.endswith(WEBHOOK_NOTIF_URL) for value in values):
        return _failing(
            COMPOSE_GUARD_WEBHOOK_URL,
            f"N8N_WEBHOOK_URL no apunta a {WEBHOOK_NOTIF_URL!r}: {values!r}",
        )
    return _passing(COMPOSE_GUARD_WEBHOOK_URL, values[0])


def _check_executions_timeout_present(compose: dict) -> Check:
    env = _n8n_environment(compose)
    if "EXECUTIONS_TIMEOUT" not in env:
        return _failing(
            COMPOSE_GUARD_TIMEOUT,
            "El environment de n8n no declara EXECUTIONS_TIMEOUT",
        )
    return _passing(COMPOSE_GUARD_TIMEOUT, f"EXECUTIONS_TIMEOUT={env['EXECUTIONS_TIMEOUT']}")


def _check_executions_timeout_coherent(compose: dict) -> Check:
    env = _n8n_environment(compose)
    default_raw = env.get("EXECUTIONS_TIMEOUT")
    max_raw = env.get("EXECUTIONS_TIMEOUT_MAX")
    # W-1: ambas cotas son obligatorias. La ausencia de la cota por defecto la
    # reporta _check_executions_timeout_present; esta guarda se ocupa del techo
    # ausente para no emitir un falso PASS ni duplicar el FAIL de la otra guarda.
    if default_raw is None:
        return _passing(
            COMPOSE_GUARD_TIMEOUT_COHERENT,
            "no evaluable: falta EXECUTIONS_TIMEOUT (lo reporta la guarda de presencia)",
        )
    if max_raw is None:
        return _failing(
            COMPOSE_GUARD_TIMEOUT_COHERENT,
            "El environment de n8n no declara EXECUTIONS_TIMEOUT_MAX",
        )
    try:
        default = int(str(default_raw))
        maximum = int(str(max_raw))
    except (TypeError, ValueError):
        return _failing(
            COMPOSE_GUARD_TIMEOUT_COHERENT,
            f"cotas no numericas: default={default_raw!r} max={max_raw!r}",
        )
    if maximum < default:
        return _failing(
            COMPOSE_GUARD_TIMEOUT_COHERENT,
            f"EXECUTIONS_TIMEOUT_MAX={maximum} < EXECUTIONS_TIMEOUT={default}",
        )
    return _passing(
        COMPOSE_GUARD_TIMEOUT_COHERENT, f"default={default}s max={maximum}s"
    )


def check_compose(path: "pathlib.Path | str") -> List[Check]:
    """Verifica las guardas de docker-compose.yml. Nunca produce un falso PASS."""
    if yaml is None:
        return [
            _failing(
                "compose: dependencia PyYAML disponible",
                "No se puede importar PyYAML; instala scripts/preflight/requirements.txt "
                "para verificar el compose",
            )
        ]
    try:
        compose = yaml.safe_load(pathlib.Path(path).read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        return [
            _failing(
                "compose: legible", f"No se pudo leer el compose {path!r}: {exc}"
            )
        ]

    checks = [
        _check_pinned_image(compose),
        _check_webhook_url(compose),
        _check_executions_timeout_present(compose),
        _check_executions_timeout_coherent(compose),
    ]
    return checks


# ---------------------------------------------------------------------------
# Orquestacion pura y CLI
# ---------------------------------------------------------------------------
def run_preflight(
    workflow_path: "pathlib.Path | str" = WORKFLOW_PATH,
    compose_path: "pathlib.Path | str" = COMPOSE_PATH,
) -> List[Check]:
    """Ejecuta las guardas del workflow y del compose sobre los artefactos dados."""
    checks: List[Check] = []
    checks.extend(check_workflow(workflow_path))
    checks.extend(check_compose(compose_path))
    return checks


def exit_code(checks: List[Check]) -> int:
    """0 si y solo si hay checks y todos son PASS; 1 en cualquier otro caso."""
    if not checks:
        return EXIT_FAIL
    if all(check.ok for check in checks):
        return EXIT_OK
    return EXIT_FAIL


def format_summary(checks: List[Check]) -> str:
    """Renderiza cada check con su estado y el sintesis final."""
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
        lines.append(f"RESULT: {passed}/{total} guardas en PASS. Preflight GREEN.")
    else:
        failed = sum(1 for check in checks if check.status == STATUS_FAIL)
        lines.append(
            f"RESULT: {passed}/{total} guardas en PASS ({failed} en FAIL). "
            "Preflight RED."
        )
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight estatico de preparacion de costo: verifica las guardas "
            "de n8n/workflow.json y docker-compose.yml sin red ni Docker."
        )
    )
    parser.add_argument(
        "--workflow",
        default=str(WORKFLOW_PATH),
        help="Ruta al workflow exportado (default: n8n/workflow.json).",
    )
    parser.add_argument(
        "--compose",
        default=str(COMPOSE_PATH),
        help="Ruta al docker-compose.yml (default: ./docker-compose.yml).",
    )
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    """Punto de entrada CLI. Imprime el resumen y devuelve 0/1."""
    args = _build_parser().parse_args(argv)
    checks = run_preflight(args.workflow, args.compose)
    print(format_summary(checks))
    return exit_code(checks)


if __name__ == "__main__":
    raise SystemExit(main())