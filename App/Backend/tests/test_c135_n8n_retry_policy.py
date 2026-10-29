"""
Politica de reintento del tramo de alta N8N -> backend (c-140, tareas 3.2/3.5).

Archivo propio para no alterar el conteo de `test_n8n_workflow.py`, que esta
atado a la guia ("Verifica 176 propiedades estructurales").

El verificador `violaciones_politica_reintento(workflow, compose, settings)` es
PURO: recibe el workflow N8N parseado, el `docker-compose.yml` parseado y un
objeto `settings` con los valores del backend, y devuelve una lista de
violaciones accionables (vacia si la politica es correcta). Las pruebas de 3.5
mutan copias en memoria para confirmar que cada violacion esperada se detecta.

Marcador del change: n8n-workflow (ADDED N8N-RETRY-001) y classification-
resilience (producto acotado de reintentos).
"""

from __future__ import annotations

import copy
from pathlib import Path
from types import SimpleNamespace

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[3]
_WORKFLOW_PATH = _REPO_ROOT / "n8n" / "workflow.json"
_COMPOSE_PATH = _REPO_ROOT / "docker-compose.yml"

NODO_LOGIN = "Login operador"
NODO_ALTA = "HTTP POST a MESA-AYUDAS"
_STICKY = "n8n-nodes-base.stickyNote"


# ── Verificador puro ─────────────────────────────────────────────────────────


def _nodes(workflow: dict) -> dict:
    return {n.get("name"): n for n in workflow.get("nodes", [])}


def _timeout_ms(node: dict):
    return (node.get("parameters") or {}).get("options", {}).get("timeout")


def _max_tries(node: dict):
    value = node.get("maxTries")
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _wait_between(node: dict):
    value = node.get("waitBetweenTries")
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value


def _presupuesto_nodo(node: dict):
    """Peor caso del nodo en segundos, o None si falta algun parametro."""
    mt = _max_tries(node)
    wait = _wait_between(node)
    timeout = _timeout_ms(node)
    if mt is None or wait is None or not isinstance(timeout, (int, float)):
        return None
    return (mt * timeout + (mt - 1) * wait) / 1000.0


def _executions_timeout(compose: dict):
    services = (compose or {}).get("services", {})
    n8n = services.get("n8n", {})
    environment = n8n.get("environment", {})
    if isinstance(environment, list):
        for entry in environment:
            if isinstance(entry, str) and entry.startswith("EXECUTIONS_TIMEOUT"):
                _, _, value = entry.partition("=")
                return int(value)
        return None
    value = environment.get("EXECUTIONS_TIMEOUT") if isinstance(environment, dict) else None
    return int(value) if value is not None else None


def _error_successors(workflow: dict, node_name: str) -> set[str]:
    connections = (workflow.get("connections") or {}).get(node_name, {})
    main = connections.get("main", [])
    if len(main) < 2:
        return set()
    return {edge.get("node") for edge in (main[1] or [])}


def _violaciones_nodo(nombre: str, node: dict | None) -> list[str]:
    if node is None:
        return [f"[retry] falta el nodo {nombre}"]
    out: list[str] = []
    if node.get("retryOnFail") is not True:
        out.append(f"[retry] {nombre} no declara retryOnFail: true")
    mt = _max_tries(node)
    if mt is None or not (2 <= mt <= 3):
        out.append(f"[retry] {nombre} maxTries fuera de [2,3]: {node.get('maxTries')!r}")
    wait = _wait_between(node)
    if wait is None or not (1000 <= wait <= 5000):
        out.append(
            f"[retry] {nombre} waitBetweenTries fuera de [1000,5000]: "
            f"{node.get('waitBetweenTries')!r}"
        )
    timeout = _timeout_ms(node)
    if not isinstance(timeout, (int, float)) or isinstance(timeout, bool) or timeout <= 0:
        out.append(f"[retry] {nombre} parameters.options.timeout ausente o no numerico")
    return out


def violaciones_politica_reintento(workflow: dict, compose: dict, settings) -> list[str]:
    """Devuelve las violaciones de la politica de reintento (vacia si es correcta)."""
    violaciones: list[str] = []
    nodes = _nodes(workflow)
    login = nodes.get(NODO_LOGIN)
    alta = nodes.get(NODO_ALTA)

    violaciones += _violaciones_nodo(NODO_LOGIN, login)
    violaciones += _violaciones_nodo(NODO_ALTA, alta)

    # (b) presupuesto de peor caso < EXECUTIONS_TIMEOUT.
    presupuesto_login = _presupuesto_nodo(login) if login else None
    presupuesto_alta = _presupuesto_nodo(alta) if alta else None
    timeout_ejecucion = _executions_timeout(compose)
    if presupuesto_login is None or presupuesto_alta is None:
        violaciones.append(
            "[presupuesto] no se puede calcular el peor caso del tramo "
            "(faltan maxTries/timeout/waitBetweenTries en algun nodo)"
        )
        presupuesto_total = None
    else:
        presupuesto_total = presupuesto_login + presupuesto_alta
        if timeout_ejecucion is not None and presupuesto_total >= timeout_ejecucion:
            violaciones.append(
                f"[presupuesto] el peor caso {presupuesto_total:.0f}s no es menor "
                f"que EXECUTIONS_TIMEOUT ({timeout_ejecucion}s)"
            )

    # (c) timeout del alta en segundos > gemini_total_timeout_seconds.
    if alta is not None:
        timeout_alta = _timeout_ms(alta)
        total_gemini = getattr(settings, "gemini_total_timeout_seconds", None)
        if not isinstance(timeout_alta, (int, float)) or isinstance(timeout_alta, bool):
            violaciones.append(
                "[timeout-alta] el nodo de alta no declara parameters.options.timeout"
            )
        elif total_gemini is not None and (timeout_alta / 1000.0) <= total_gemini:
            violaciones.append(
                f"[timeout-alta] timeout {timeout_alta / 1000.0:.0f}s no supera "
                f"gemini_total_timeout_seconds ({total_gemini}s)"
            )

        # (d) camino de error terminal preservado.
        if alta.get("onError") != "continueErrorOutput":
            violaciones.append(
                "[error-path] el nodo de alta no conserva onError: continueErrorOutput"
            )
        sucesores_error = _error_successors(workflow, NODO_ALTA)
        for requerido in ("Es correo?", "Registro de auditoria"):
            if requerido not in sucesores_error:
                violaciones.append(
                    f"[error-path] la salida de error del alta no alcanza {requerido}"
                )

        # (e) clave de idempotencia desde el normalizador.
        json_body = (alta.get("parameters") or {}).get("jsonBody", "")
        if (
            "origen_message_id" not in json_body
            or "Normalizar entrada del incidente" not in json_body
        ):
            violaciones.append(
                "[idempotencia] origen_message_id no referencia la salida de "
                "Normalizar entrada del incidente"
            )

    # (f) conteos canonicos.
    all_nodes = workflow.get("nodes", [])
    total = len(all_nodes)
    notas = sum(1 for n in all_nodes if n.get("type") == _STICKY)
    operativos = total - notas
    if total != 32 or notas != 3 or operativos != 29:
        violaciones.append(
            f"[conteos] se esperaban 32 nodos (3 notas, 29 operativos); "
            f"hay {total} ({notas}, {operativos})"
        )

    # (g) producto acotado entre reintentos de transporte y del proveedor.
    gemini_max_retries = getattr(settings, "gemini_max_retries", None)
    if alta is not None:
        mt_alta = _max_tries(alta)
        if (
            mt_alta is not None
            and gemini_max_retries is not None
            and mt_alta * (gemini_max_retries + 1) > 9
        ):
            violaciones.append(
                f"[producto] maxTries(alta) x (gemini_max_retries+1) = "
                f"{mt_alta * (gemini_max_retries + 1)} > 9"
            )

    # (h) el timeout del handoff cubre el presupuesto del tramo.
    handoff = getattr(settings, "telefonia_handoff_timeout_s", None)
    if handoff is not None:
        if presupuesto_total is None:
            violaciones.append(
                "[handoff] TELEFONIA_HANDOFF_TIMEOUT_S no cubre un presupuesto "
                "de tramo incalculable"
            )
        elif handoff < presupuesto_total:
            violaciones.append(
                f"[handoff] TELEFONIA_HANDOFF_TIMEOUT_S ({handoff}s) < presupuesto "
                f"del tramo ({presupuesto_total:.0f}s)"
            )

    return violaciones


# ── Utilidades de carga ──────────────────────────────────────────────────────


def _workflow() -> dict:
    import json

    return json.loads(_WORKFLOW_PATH.read_text(encoding="utf-8"))


def _compose() -> dict:
    return yaml.safe_load(_COMPOSE_PATH.read_text(encoding="utf-8"))


def _settings():
    from app.config.settings import Settings
    from app.utils import n8n_webhook

    return SimpleNamespace(
        gemini_total_timeout_seconds=Settings.model_fields[
            "gemini_total_timeout_seconds"
        ].default,
        gemini_max_retries=Settings.model_fields["gemini_max_retries"].default,
        telefonia_handoff_timeout_s=n8n_webhook.TELEFONIA_HANDOFF_TIMEOUT_S,
    )


def _por_tag(violaciones: list[str], tag: str) -> list[str]:
    return [v for v in violaciones if v.startswith(tag)]


# ── 3.2 RED (a)-(h) ─────────────────────────────────────────────────────────


def test_a_ambos_nodos_declaran_reintento_acotado():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[retry]") == [], (
        f"Los nodos HTTP del tramo de alta deben declarar el reintento acotado: "
        f"{_por_tag(violaciones, '[retry]')}"
    )


def test_b_presupuesto_cabe_en_el_tope_de_ejecucion():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[presupuesto]") == [], (
        f"El peor caso del tramo debe ser menor que EXECUTIONS_TIMEOUT: "
        f"{_por_tag(violaciones, '[presupuesto]')}"
    )


def test_c_timeout_del_alta_supera_el_presupuesto_de_clasificacion():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[timeout-alta]") == [], (
        f"El timeout del alta debe superar gemini_total_timeout_seconds: "
        f"{_por_tag(violaciones, '[timeout-alta]')}"
    )


def test_d_camino_de_error_preservado():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[error-path]") == [], (
        f"El camino de error terminal debe preservarse: "
        f"{_por_tag(violaciones, '[error-path]')}"
    )


def test_e_clave_de_idempotencia_desde_el_normalizador():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[idempotencia]") == []


def test_f_conteos_canonicos():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[conteos]") == []


def test_g_producto_acotado():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[producto]") == []


def test_h_handoff_cubre_el_presupuesto_del_tramo():
    violaciones = violaciones_politica_reintento(_workflow(), _compose(), _settings())
    assert _por_tag(violaciones, "[handoff]") == [], (
        f"TELEFONIA_HANDOFF_TIMEOUT_S debe cubrir el peor caso del tramo: "
        f"{_por_tag(violaciones, '[handoff]')}"
    )


def test_cp3_valores_aprobados():
    """CP3 (APROBADO): login 3/5000/10000; alta 3/5000/75000."""
    workflow = _workflow()
    nodes = _nodes(workflow)
    assert nodes[NODO_LOGIN]["maxTries"] == 3
    assert nodes[NODO_LOGIN]["waitBetweenTries"] == 5000
    assert _timeout_ms(nodes[NODO_LOGIN]) == 10000
    assert nodes[NODO_ALTA]["maxTries"] == 3
    assert nodes[NODO_ALTA]["waitBetweenTries"] == 5000
    assert _timeout_ms(nodes[NODO_ALTA]) == 75000


# ── 3.5 TRIANGULATE: cada mutacion produce la violacion esperada ─────────────


def _base():
    return _workflow(), _compose(), _settings()


def test_mutacion_maxtries_alta_cinco():
    workflow, compose, settings = _base()
    nodes = _nodes(workflow)
    nodes[NODO_ALTA]["maxTries"] = 5
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[retry]"), "maxTries=5 no fue rechazado"


def test_mutacion_timeout_alta_30000():
    workflow, compose, settings = _base()
    nodes = _nodes(workflow)
    nodes[NODO_ALTA]["parameters"]["options"]["timeout"] = 30000
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[timeout-alta]"), (
        "un timeout del alta de 30 s (<= gemini 60 s) no fue rechazado"
    )


def test_mutacion_wait_between_cero():
    workflow, compose, settings = _base()
    nodes = _nodes(workflow)
    nodes[NODO_ALTA]["waitBetweenTries"] = 0
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[retry]"), "waitBetweenTries=0 no fue rechazado"


def test_mutacion_onerror_ausente():
    workflow, compose, settings = _base()
    nodes = _nodes(workflow)
    nodes[NODO_ALTA].pop("onError", None)
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[error-path]"), "onError ausente no fue rechazado"


def test_mutacion_executions_timeout_200():
    workflow, compose, settings = _base()
    compose["services"]["n8n"]["environment"]["EXECUTIONS_TIMEOUT"] = "200"
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[presupuesto]"), (
        "EXECUTIONS_TIMEOUT=200 no rechazo el presupuesto de 275 s"
    )


def test_mutacion_handoff_timeout_30():
    workflow, compose, settings = _base()
    settings.telefonia_handoff_timeout_s = 30.0
    violaciones = violaciones_politica_reintento(workflow, compose, settings)
    assert _por_tag(violaciones, "[handoff]"), (
        "TELEFONIA_HANDOFF_TIMEOUT_S=30 no fue rechazado"
    )
