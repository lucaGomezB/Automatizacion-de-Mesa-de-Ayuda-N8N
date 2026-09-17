#!/usr/bin/env python3
"""Zero-cost local dry-run harness for the Mesa de Ayuda stack.

This CLI validates the shared incident-registration tramo (the tramo the three
channels converge on) BEFORE any paid credential is used:

    webhook N8N -> normalizar/validar -> login dinamico -> POST /incidentes/ ->
    persistir + clasificar -> confirmacion

It is deliberately cost-zero:

* The backend is lifted with a DUMMY ``GEMINI_API_KEY`` (compose override at
  ``scripts/dry_run/compose.dry-run.yml``) and the harness asserts the effective
  key is fictitious before sending anything. Any escalation falls back safely.
* Nothing in this harness ever calls Twilio.

Exit codes:

    0  all checks passed (only if every check ran and passed)
    1  any wiring break, aborted preflight, or pending/incomplete check

Usage:
    python scripts/dry_run/dry_run.py --help
    python scripts/dry_run/dry_run.py
    python scripts/dry_run/dry_run.py --skip-up --skip-import
    make dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import re
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

# Make ``import checks`` work both when executed as a script and when imported.
_DRY_RUN_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DRY_RUN_DIR.parents[1]
sys.path.insert(0, str(_DRY_RUN_DIR))

import checks  # noqa: E402
from checks import (  # noqa: E402
    DUMMY_GEMINI_API_KEY,
    Check,
    exit_code,
    extract_canal_origen_id,
    extract_incidente_id,
    failing,
    format_summary,
    is_dummy_gemini_key,
    passing,
    pending,
    pick_working_scheme,
)

COMPOSE_FILES = ["-f", "docker-compose.yml", "-f", "scripts/dry_run/compose.dry-run.yml"]

WORKFLOW_ID = "P7w2iELDu7O3e8B0"
WORKFLOW_MOUNT_PATH = "/data/Automatizacion_Mesa_de_Ayuda.json"
WEBHOOK_PATH = "incidente-web"
CANAL_EMAIL_ID = 1  # correo electronico (catalogo canal_origen, migracion 001)
CANAL_WEB_ID = 2  # formulario web (catalogo canal_origen, migracion 001)
CANAL_PHONE_ID = 3  # llamada telefonica (catalogo canal_origen, migracion 001)

BACKEND_CONTAINER = "mesa_local-backend-1"
N8N_CONTAINER = "mesa_local-n8n-1"
LOGIN_CREDENTIAL_NAME = "Operador Mesa de Ayuda (login)"

# Deterministic description: hardware keywords + a stable marker.
TEST_DESCRIPTION = "La impresora del sector no enciende y la pantalla del equipo falla"


# ── subprocess helpers ───────────────────────────────────────────────────────


def _run(cmd: list[str], timeout: int = 300, stdin: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(_REPO_ROOT),
        input=stdin,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def compose(args: list[str], timeout: int = 600, stdin: str | None = None) -> subprocess.CompletedProcess:
    return _run(["docker", "compose", *COMPOSE_FILES, *args], timeout=timeout, stdin=stdin)


def docker(args: list[str], timeout: int = 120) -> subprocess.CompletedProcess:
    return _run(["docker", *args], timeout=timeout)


def n8n_cli(args: list[str], timeout: int = 180, stdin: str | None = None) -> subprocess.CompletedProcess:
    return _run(
        ["docker", "compose", *COMPOSE_FILES, "exec", "-T", "n8n", "n8n", *args],
        timeout=timeout,
        stdin=stdin,
    )


def container_state(name: str) -> str:
    result = docker(["inspect", "--format",
                     "{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}", name])
    if result.returncode != 0:
        return "missing"
    return result.stdout.strip() or "unknown"


# ── HTTP helper: no redirect following, unverified TLS (self-signed) ─────────


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D401
        return None


def _build_opener() -> urllib.request.OpenerDirector:
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    return urllib.request.build_opener(_NoRedirect(), urllib.request.HTTPSHandler(context=context))


def http_request(
    method: str,
    url: str,
    body: dict | None = None,
    headers: dict | None = None,
    timeout: int = 15,
) -> tuple[int | None, dict, str]:
    hdrs = dict(headers or {})
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        hdrs.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=hdrs, method=method)
    try:
        with _build_opener().open(request, timeout=timeout) as response:
            return response.status, dict(response.headers), response.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as error:
        return error.code, dict(error.headers), error.read().decode("utf-8", "replace")
    except Exception as error:  # connection refused, TLS error, timeout...
        return None, {}, f"{type(error).__name__}: {error}"


def _json_or_none(text: str):
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return None


# ── Stack lift / reuse ───────────────────────────────────────────────────────


def lift_stack(args) -> list[Check]:
    results: list[Check] = []
    result = compose(["up", "-d"], timeout=900)
    if result.returncode != 0:
        results.append(
            failing(
                "stack:up",
                (result.stderr or result.stdout).strip()[-400:],
                "run `docker compose -f docker-compose.yml -f scripts/dry_run/compose.dry-run.yml up -d` manually to see the error",
            )
        )
        return results

    deadline = time.time() + args.health_timeout
    backend_state = n8n_state = "unknown"
    while time.time() < deadline:
        backend_state = container_state(BACKEND_CONTAINER)
        n8n_state = container_state(N8N_CONTAINER)
        if backend_state == "healthy" and n8n_state in ("running", "healthy"):
            break
        time.sleep(3)

    if backend_state == "healthy" and n8n_state in ("running", "healthy"):
        results.append(passing("stack:up", f"backend={backend_state} n8n={n8n_state} (project mesa_local)"))
    else:
        results.append(
            failing(
                "stack:up",
                f"backend={backend_state} n8n={n8n_state} after {args.health_timeout}s",
                "inspect `docker compose ps` and `docker compose logs backend`; the stack did not become healthy",
            )
        )
    return results


def assert_dummy_key() -> Check:
    result = compose(["exec", "-T", "backend", "printenv", "GEMINI_API_KEY"], timeout=60)
    effective = result.stdout.strip()
    if result.returncode != 0:
        return failing(
            "guardrail:gemini-key",
            f"could not read GEMINI_API_KEY from backend ({result.stderr.strip()[-160:]})",
            "ensure the backend container is running and was lifted with the dry-run overlay",
        )
    if is_dummy_gemini_key(effective):
        return passing("guardrail:gemini-key", "effective GEMINI_API_KEY is fictitious (cost-zero)")
    return failing(
        "guardrail:gemini-key",
        "effective GEMINI_API_KEY is NOT fictitious - aborting before any paid call",
        "lift the backend with `-f scripts/dry_run/compose.dry-run.yml` (env_file overrides are not enough)",
    )


# ── N8N workflow import / activation ─────────────────────────────────────────


def _load_workflow() -> dict:
    return json.loads((_REPO_ROOT / "n8n" / "workflow.json").read_text(encoding="utf-8"))


_WHOLE_EXPRESSION = re.compile(r"^=\{\{\s*(.*?)\s*\}\}$", re.DOTALL)


def _body_value_to_js(value) -> str:
    """Render a stored body value as a JavaScript literal/expression.

    Values authored as N8N whole-value expressions (``={{ ... }}``) keep their
    inner expression verbatim; anything else is embedded as a JSON literal.
    """
    if isinstance(value, str):
        match = _WHOLE_EXPRESSION.match(value)
        if match:
            return match.group(1)
    return json.dumps(value)


def _json_body_expression(body: dict) -> str:
    """Build a ``={{ JSON.stringify({...}) }}`` expression from a legacy body.

    HTTP Request v4.4 IGNORES a bare ``body`` object when ``contentType`` is
    ``json``; it only sends a JSON payload through ``specifyBody='json'`` plus
    ``jsonBody``. Workers authored against an older shape leave the payload in
    ``body``, so N8N silently falls back to the default ``keypair`` body
    (``{"": ""}``) and the backend rejects the request. This mirrors the editor's
    output for the same intent.
    """
    pairs = [f"{json.dumps(key)}: {_body_value_to_js(value)}" for key, value in body.items()]
    return "={{ JSON.stringify({ " + ", ".join(pairs) + " }) }}"


def _normalize_json_body(parameters: dict) -> None:
    """Migrate an ignored legacy ``body`` object to ``jsonBody`` (v4.4 contract)."""
    body = parameters.get("body")
    if parameters.get("contentType") != "json" or not isinstance(body, dict):
        return
    parameters.pop("body", None)
    parameters.pop("bodyParameters", None)
    parameters["specifyBody"] = "json"
    parameters["jsonBody"] = _json_body_expression(body)


def _workflow_for_dry_run(username: str, password: str) -> tuple[dict, list[str]]:
    """Return a cost-zero copy of the workflow plus the names of removed nodes.

    Three adaptations are needed so a fresh N8N can activate the web channel
    without any external credential:

    1. The login node references a placeholder ``httpCustomAuth`` credential.
       The harness injects the local operator credentials directly into the node
       (equivalent to an operator configuring that credential in the UI).
       HTTP Request v4.4 only sends a JSON body when ``specifyBody='json'`` and
       ``jsonBody`` are set; a bare ``body`` key is ignored and N8N falls back
       to the default ``keypair`` body (``{"": ""}``), which the backend
       rejects with HTTP 422 and the workflow dies before responding.
    2. Every node whose ``credentials`` still points at a ``REPLACE_WITH_*``
       placeholder is removed. In particular the Twilio and Outlook triggers
       block activation of the WHOLE workflow because their credentials do not
       exist. Removing them is also the strongest form of the cost-zero
       guardrail: the paid channels are not even present in the running graph.
       Only the web channel (the mandatory dry-run path) remains wired.
    3. The webhook node must carry a stable ``webhookId``. On CLI import N8N
       does NOT generate one, and without it N8N 2.x registers the production
       path as ``<workflowId>/<nodeName>/<path>`` (see
       ``NodeHelpers.getNodeWebhookPath``) instead of the declared ``<path>``,
       so POSTs to ``/webhook/<path>`` never match. The editor writes this field
       when a workflow is saved; the harness mirrors that here.
    """
    workflow = _load_workflow()

    # 1. Inline the local operator credentials into the login node.
    for node in workflow.get("nodes", []):
        if node.get("name") == "Login operador":
            node.pop("credentials", None)
            node.pop("authentication", None)
            node.pop("genericAuthType", None)
            node["parameters"] = {
                "method": "POST",
                "url": "http://backend:8000/api/v1/auth/login",
                "sendBody": True,
                "contentType": "json",
                "specifyBody": "json",
                "jsonBody": json.dumps({"username": username, "password": password}),
                "options": {},
            }

    # 1b. Give every webhook trigger a stable webhookId so N8N registers the
    #     declared path (isFullPath=true) rather than the workflow/node
    #     fallback path. Deterministic per workflow+node keeps re-imports
    #     idempotent.
    for node in workflow.get("nodes", []):
        if node.get("type") == "n8n-nodes-base.webhook" and not node.get("webhookId"):
            node["webhookId"] = str(
                uuid.uuid5(uuid.NAMESPACE_URL, f"dry-run:{WORKFLOW_ID}:{node.get('name')}")
            )

    # 2. Strip placeholder credentials. Nodes that stay on the web path keep
    #    their place (the HTTP POST node authenticates with an explicit
    #    Authorization header, so its credential reference is redundant);
    #    paid-channel nodes (Twilio/Outlook/Gemini) are removed entirely so the
    #    workflow can activate without those credentials.
    keep_but_strip = {"Login operador", "HTTP POST a MTM-SRU"}
    removed: list[str] = []
    retained: list[dict] = []
    for node in workflow.get("nodes", []):
        name = node.get("name")
        credentials = node.get("credentials") or {}
        has_placeholder = any("REPLACE_WITH" in json.dumps(value) for value in credentials.values())
        if has_placeholder and name not in keep_but_strip:
            removed.append(name)
            continue
        if name in keep_but_strip:
            node.pop("credentials", None)
            node.pop("authentication", None)
            node.pop("genericAuthType", None)
            parameters = node.get("parameters")
            if isinstance(parameters, dict):
                # The HTTP Request node stores its auth mode INSIDE
                # ``parameters`` (``authentication`` + ``genericAuthType``), not
                # at the node level. If only the node-level key is dropped, N8N
                # still tries to resolve the now-absent credential and aborts
                # with "Credentials not found".
                parameters.pop("genericAuthType", None)
                if "authentication" in parameters:
                    parameters["authentication"] = "none"
                _normalize_json_body(parameters)
        retained.append(node)
    workflow["nodes"] = retained

    # 3. Rewrite connections so no edge points at a removed node.
    connections = workflow.get("connections", {})
    cleaned: dict = {}
    for source, value in connections.items():
        if source in removed:
            continue
        main = value.get("main", [])
        cleaned[source] = {
            "main": [
                [edge for edge in (branch or []) if edge.get("node") not in removed]
                for branch in main
            ]
        }
    workflow["connections"] = cleaned
    return workflow, removed


def wait_for_n8n(host: str, port: int, timeout: int) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        status, _, _ = http_request("GET", f"http://{host}:{port}/webhook/{WEBHOOK_PATH}", timeout=5)
        if status is not None:
            return True
        time.sleep(3)
    return False


def import_and_activate_workflow(args) -> list[Check]:
    results: list[Check] = []

    workflow, removed = _workflow_for_dry_run(args.username, args.password)
    source_label = "cost-zero dry-run workflow (inline login"
    if removed:
        source_label += f", removed paid-channel nodes: {', '.join(removed)}"
    source_label += ")"

    local_copy = _DRY_RUN_DIR / ".workflow.dry-run.json"
    # The copy inlines the operator credentials, so it must never be left behind
    # (not even on an early failure return below).
    try:
        local_copy.write_text(json.dumps(workflow, ensure_ascii=False), encoding="utf-8")
        container_copy = "/tmp/workflow.dry-run.json"
        copied = docker(["cp", str(local_copy), f"{N8N_CONTAINER}:{container_copy}"], timeout=120)
        if copied.returncode != 0:
            results.append(
                failing(
                    "n8n:import",
                    f"could not copy workflow into {N8N_CONTAINER} ({copied.stderr.strip()[-160:]})",
                    "ensure the n8n container is running",
                )
            )
            return results

        imported = n8n_cli(["import:workflow", f"--input={container_copy}"], timeout=180)
        if imported.returncode != 0:
            results.append(
                failing(
                    "n8n:import",
                    (imported.stderr or imported.stdout).strip()[-300:],
                    "run `docker compose exec n8n n8n import:workflow --input=/tmp/workflow.dry-run.json` manually",
                )
            )
            return results
        results.append(passing("n8n:import", f"imported {source_label} (id={WORKFLOW_ID})"))

        # Activate. N8N 2.x uses a publish model: set active, publish the version,
        # then restart so the webhook is registered in the running process.
        n8n_cli(["update:workflow", f"--id={WORKFLOW_ID}", "--active=true"], timeout=120)
        published = n8n_cli(["publish:workflow", f"--id={WORKFLOW_ID}"], timeout=120)
        if published.returncode != 0:
            results.append(
                failing(
                    "n8n:activate",
                    (published.stderr or published.stdout).strip()[-300:],
                    "activate the workflow manually in the N8N UI (toggle 'Active')",
                )
            )
            return results

        restarted = compose(["restart", "n8n"], timeout=180)
        if restarted.returncode != 0 or not wait_for_n8n(args.n8n_host, args.n8n_port, args.health_timeout):
            results.append(
                failing(
                    "n8n:activate",
                    "n8n did not come back after restart",
                    "check `docker compose logs n8n`; the webhook stays unregistered while n8n is down",
                )
            )
            return results
        results.append(passing("n8n:activate", f"workflow {WORKFLOW_ID} active and webhook registered"))
        return results
    finally:
        try:
            local_copy.unlink()
        except OSError:
            pass


# ── Preflight ────────────────────────────────────────────────────────────────


def resolve_webhook(args) -> tuple[str | None, list[tuple[str, int | None]], Check]:
    probes: list[tuple[str, bool]] = []
    raw: list[tuple[str, int | None]] = []
    for scheme in ("http", "https"):
        url = f"{scheme}://{args.n8n_host}:{args.n8n_port}/webhook/{WEBHOOK_PATH}"
        status, _, _ = http_request("GET", url, timeout=args.timeout)
        probes.append((scheme, status is not None))
        raw.append((scheme, status))
    scheme = pick_working_scheme(probes)
    if scheme is None:
        check = failing(
            "preflight:webhook-reachable",
            f"no scheme responded on {args.n8n_host}:{args.n8n_port} (http/https)",
            "ensure N8N is running and port 5678 is published",
        )
    else:
        observed = ", ".join(f"{s}={st}" for s, st in raw)
        check = passing("preflight:webhook-reachable", f"scheme={scheme} ({observed})")
    return scheme, raw, check


def run_preflight(args, base_url: str) -> tuple[list[Check], dict]:
    results: list[Check] = []
    context: dict = {}

    # 1. Login contract
    status, _, text = http_request(
        "POST",
        f"{base_url}/api/v1/auth/login",
        {"username": args.username, "password": args.password},
        timeout=args.timeout,
    )
    payload = _json_or_none(text)
    if status == 200 and isinstance(payload, dict) and payload.get("access_token"):
        token = payload["access_token"]
        context["token"] = token
        context["token_type"] = payload.get("token_type")
        results.append(passing("preflight:login", f"access_token received (token_type={payload.get('token_type')})"))
    else:
        results.append(
            failing(
                "preflight:login",
                f"POST /api/v1/auth/login -> {status}: {text.strip()[:200]}",
                "verify the seeded operator (admin/admin123) and that the backend reached 'healthy'",
            )
        )
        return results, context

    auth = {"Authorization": f"Bearer {context['token']}"}

    # 2. Valid creation -> 201
    status, _, text = http_request(
        "POST",
        f"{base_url}/api/v1/incidentes/",
        {"descripcion": TEST_DESCRIPTION, "canal_origen_id": CANAL_WEB_ID},
        headers=auth,
        timeout=args.timeout,
    )
    payload = _json_or_none(text)
    incidente_id = extract_incidente_id(payload)
    if status == 201 and incidente_id is not None:
        results.append(passing("preflight:create-201", f"created incidente_id={incidente_id}"))
    else:
        results.append(
            failing(
                "preflight:create-201",
                f"POST /api/v1/incidentes/ -> {status}: {text.strip()[:200]}",
                "verify the trailing slash is present and the Authorization header is forwarded",
            )
        )

    # 3. Short description -> 422
    status, _, text = http_request(
        "POST",
        f"{base_url}/api/v1/incidentes/",
        {"descripcion": "corto", "canal_origen_id": CANAL_WEB_ID},
        headers=auth,
        timeout=args.timeout,
    )
    if status == 422:
        results.append(passing("preflight:min-length-422", "short descripcion rejected with 422"))
    else:
        results.append(
            failing(
                "preflight:min-length-422",
                f"expected 422, got {status}: {text.strip()[:200]}",
                "verify IncidenteCreate.descripcion min_length=10 is enforced",
            )
        )

    # 4. Missing trailing slash -> 307 (redirects NOT followed)
    status, headers, text = http_request(
        "POST",
        f"{base_url}/api/v1/incidentes",
        {"descripcion": TEST_DESCRIPTION, "canal_origen_id": CANAL_WEB_ID},
        headers=auth,
        timeout=args.timeout,
    )
    if status == 307:
        location = headers.get("Location", headers.get("location", ""))
        results.append(
            passing("preflight:missing-slash-307", f"redirect detected (Location={location or 'n/a'})")
        )
    else:
        results.append(
            failing(
                "preflight:missing-slash-307",
                f"expected 307, got {status}",
                "callers MUST keep the trailing slash; a 307 drops Authorization and body",
            )
        )

    # 5. N8N webhook reachable
    scheme, _, webhook_check = resolve_webhook(args)
    results.append(webhook_check)
    if scheme:
        context["n8n_scheme"] = scheme

    return results, context


# ── End-to-end web channel ───────────────────────────────────────────────────


def run_e2e(args, base_url: str, context: dict) -> list[Check]:
    results: list[Check] = []
    scheme = context.get("n8n_scheme")
    if not scheme:
        return [pending("e2e:web", "webhook scheme unresolved", "fix the webhook reachability check first")]

    webhook_url = f"{scheme}://{args.n8n_host}:{args.n8n_port}/webhook/{WEBHOOK_PATH}"
    incidente_id = None
    status: int | None = None
    text = ""
    # Activation is asynchronous: retry while N8N reports the webhook as not
    # registered yet (a plain 404 JSON body) up to the poll window.
    deadline = time.time() + args.poll_timeout
    while True:
        status, _, text = http_request(
            "POST",
            webhook_url,
            {"descripcion": TEST_DESCRIPTION, "prioridad": "media"},
            timeout=args.e2e_timeout,
        )
        payload = _json_or_none(text)
        incidente_id = extract_incidente_id(payload)
        if incidente_id is not None or status != 404 or time.time() >= deadline:
            break
        time.sleep(3)

    if status is None or incidente_id is None:
        results.append(
            failing(
                "e2e:webhook-response",
                f"POST {webhook_url} -> {status}: {text.strip()[:220]}",
                "the N8N workflow failed before responding; check `docker compose logs n8n` and the login credential/backend link",
            )
        )
        return results
    results.append(passing("e2e:webhook-response", f"incidente_id={incidente_id}"))

    auth = {"Authorization": f"Bearer {context['token']}"}
    deadline = time.time() + args.poll_timeout
    observed_canal = None
    while time.time() < deadline:
        status, _, text = http_request(
            "GET",
            f"{base_url}/api/v1/incidentes/{incidente_id}",
            headers=auth,
            timeout=args.timeout,
        )
        if status == 200:
            payload = _json_or_none(text)
            observed_canal = extract_canal_origen_id(payload)
            break
        time.sleep(2)

    if observed_canal is None:
        results.append(
            failing(
                "e2e:persisted",
                f"incidente {incidente_id} not persisted within {args.poll_timeout}s",
                "the webhook did not complete the registration; check backend logs and the N8N HTTP POST node",
            )
        )
        return results
    results.append(passing("e2e:persisted", f"incidente {incidente_id} persisted"))

    if observed_canal == CANAL_WEB_ID:
        results.append(passing("e2e:canal", f"canal_origen_id={observed_canal} (formulario web)"))
    else:
        results.append(
            failing(
                "e2e:canal",
                f"observed canal_origen_id={observed_canal}, expected {CANAL_WEB_ID}",
                "the workflow must send canal_origen_id=2 for the web channel (see 'Marcar canal web')",
            )
        )
    return results


# ── Optional email channel variant (§7.2) ────────────────────────────────────
#
# The email (Outlook) channel is FREE to receive because the N8N trigger polls
# the mailbox. This variant is deliberately OPT-IN and ABSENT from the mandatory
# cost-zero path: unless ``--with-email`` is passed, ``run_email_variant`` runs
# no checks at all, so the default harness completes with no email credentials.
#
# Enabling it requires the N8N Outlook trigger to be active and credentialed for
# the target mailbox (a manual prerequisite; see docs/dry-run-harness.md). The
# variant only SENDS a plain SMTP message and then verifies persistence via the
# backend API. It never touches Twilio or Gemini.

_EMAIL_REQUIRED_ENV = (
    "DRY_RUN_EMAIL_SMTP_HOST",
    "DRY_RUN_EMAIL_FROM",
    "DRY_RUN_EMAIL_TO",
)


def email_config_from_env(environ: dict) -> dict | None:
    """Return SMTP settings when the opt-in email variant is fully configured.

    All three required variables must be present and non-empty; optional values
    fall back to safe defaults. Returns ``None`` when the variant cannot run, so
    the caller emits a PENDING check instead of silently skipping.
    """
    missing = [name for name in _EMAIL_REQUIRED_ENV if not str(environ.get(name, "")).strip()]
    if missing:
        return None
    try:
        port = int(str(environ.get("DRY_RUN_EMAIL_SMTP_PORT", "587")).strip() or "587")
    except ValueError:
        port = 587
    return {
        "host": str(environ["DRY_RUN_EMAIL_SMTP_HOST"]).strip(),
        "port": port,
        "from": str(environ["DRY_RUN_EMAIL_FROM"]).strip(),
        "to": str(environ["DRY_RUN_EMAIL_TO"]).strip(),
        "user": str(environ.get("DRY_RUN_EMAIL_SMTP_USER", "")).strip(),
        "password": str(environ.get("DRY_RUN_EMAIL_SMTP_PASSWORD", "")),
        "use_tls": str(environ.get("DRY_RUN_EMAIL_USE_TLS", "true")).strip().lower()
        not in ("0", "false", "no", "off"),
    }


def _send_email(config: dict, subject: str, body: str) -> None:
    """Send one plain-text message over SMTP (standard library only)."""
    import smtplib  # local import: the default cost-zero path never needs SMTP
    from email.message import EmailMessage

    message = EmailMessage()
    message["From"] = config["from"]
    message["To"] = config["to"]
    message["Subject"] = subject
    message.set_content(body)
    with smtplib.SMTP(config["host"], config["port"], timeout=30) as smtp:
        if config["use_tls"]:
            smtp.starttls()
        if config["user"]:
            smtp.login(config["user"], config["password"])
        smtp.send_message(message)


def _snapshot_incidente_ids(base_url: str, auth: dict, timeout: int) -> set[int]:
    """Return the set of incidente ids currently visible to the operator."""
    status, _, text = http_request(
        "GET", f"{base_url}/api/v1/incidentes/?limit=200", headers=auth, timeout=timeout
    )
    if status != 200:
        return set()
    payload = _json_or_none(text)
    if not isinstance(payload, list):
        return set()
    return {
        entry["id"]
        for entry in payload
        if isinstance(entry, dict) and isinstance(entry.get("id"), int) and not isinstance(entry.get("id"), bool)
    }


def run_email_variant(args, base_url: str, context: dict) -> list[Check]:
    """OPT-IN automated walk of the email channel (§7.2).

    Absent from the mandatory path: returns no checks unless ``--with-email`` was
    passed. When enabled but unconfigured it returns a PENDING check (never a
    success) and therefore a non-zero exit code. When configured it induces a
    message and verifies the incident against ``canal_origen_id == 1``.
    """
    if not getattr(args, "with_email", False):
        return []

    config = email_config_from_env(os.environ)
    if config is None:
        return [
            pending(
                "email:config",
                "--with-email requested but DRY_RUN_EMAIL_SMTP_HOST/FROM/TO are not fully set",
                "set the SMTP env vars (see docs/dry-run-harness.md) or drop --with-email to stay on the cost-zero path",
            )
        ]

    token = context.get("token")
    if not token:
        return [
            failing(
                "email:induce",
                "no operator token available for the email variant",
                "run the preflight successfully before enabling --with-email",
            )
        ]

    auth = {"Authorization": f"Bearer {token}"}
    before = _snapshot_incidente_ids(base_url, auth, args.timeout)

    marker = uuid.uuid4().hex[:12]
    subject = f"[DRY-RUN EMAIL] {marker}"
    body = f"{TEST_DESCRIPTION} (dry-run marker {marker})"
    try:
        _send_email(config, subject, body)
    except Exception as error:  # SMTP/DNS/TLS misconfiguration
        return [
            failing(
                "email:induce",
                f"could not send dry-run email: {type(error).__name__}: {error}",
                f"verify SMTP settings for {config['host']}:{config['port']} and that the Outlook trigger polls {config['to']}",
            )
        ]
    results = [passing("email:induced", f"dry-run email sent to {config['to']} (marker {marker})")]

    deadline = time.time() + args.poll_timeout
    while time.time() < deadline:
        current = _snapshot_incidente_ids(base_url, auth, args.timeout)
        for new_id in sorted(current - before):
            status, _, text = http_request(
                "GET", f"{base_url}/api/v1/incidentes/{new_id}", headers=auth, timeout=args.timeout
            )
            if status != 200:
                continue
            if extract_canal_origen_id(_json_or_none(text)) == CANAL_EMAIL_ID:
                results.append(
                    passing(
                        "email:persisted",
                        f"incidente {new_id} persisted with canal_origen_id={CANAL_EMAIL_ID} (correo)",
                    )
                )
                return results
        time.sleep(3)

    results.append(
        failing(
            "email:persisted",
            f"no new incident with canal_origen_id={CANAL_EMAIL_ID} appeared within {args.poll_timeout}s",
            "ensure the N8N Outlook trigger is active and credentialed for the target mailbox and that the message reached it",
        )
    )
    return results


# ── CLI ──────────────────────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dry_run.py",
        description="Zero-cost local dry-run harness for the Mesa de Ayuda shared incident tramo.",
    )
    parser.add_argument("--base-url", default="https://localhost",
                        help="Edge URL of the backend (via nginx). Default: https://localhost")
    parser.add_argument("--n8n-host", default="localhost", help="N8N host. Default: localhost")
    parser.add_argument("--n8n-port", type=int, default=5678, help="N8N published port. Default: 5678")
    parser.add_argument("--username", default=os.environ.get("DRY_RUN_USERNAME", "admin"),
                        help="Operator username (env DRY_RUN_USERNAME). Default: admin")
    parser.add_argument("--password", default=os.environ.get("DRY_RUN_PASSWORD", "admin123"),
                        help="Operator password (env DRY_RUN_PASSWORD). Never printed.")
    parser.add_argument("--skip-up", action="store_true", help="Do not lift/reuse the compose stack")
    parser.add_argument("--skip-import", action="store_true", help="Do not import/activate the N8N workflow")
    parser.add_argument(
        "--with-email",
        action="store_true",
        help="OPT-IN: also walk the (free) email channel. Off by default and absent from the cost-zero path.",
    )
    parser.add_argument("--timeout", type=int, default=15, help="Per-request timeout in seconds. Default: 15")
    parser.add_argument("--e2e-timeout", type=int, default=60, help="Webhook POST timeout. Default: 60")
    parser.add_argument("--poll-timeout", type=int, default=45, help="Persistence polling window. Default: 45")
    parser.add_argument("--health-timeout", type=int, default=180, help="Stack health wait. Default: 180")
    parser.add_argument("--json", action="store_true", help="Emit the check list as JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    results: list[Check] = []

    if not args.skip_up:
        results.extend(lift_stack(args))
        if exit_code(results) != 0:
            return _finish(results, args)

    key_check = assert_dummy_key()
    results.append(key_check)
    if not key_check.ok:
        return _finish(results, args)

    if not args.skip_import:
        results.extend(import_and_activate_workflow(args))
        if exit_code(results) != 0:
            return _finish(results, args)

    preflight, context = run_preflight(args, args.base_url.rstrip("/"))
    results.extend(preflight)
    if exit_code(preflight) != 0:
        # Early abort: no incident is sent over the webhook (§4.6).
        return _finish(results, args)

    results.extend(run_e2e(args, args.base_url.rstrip("/"), context))
    results.extend(run_email_variant(args, args.base_url.rstrip("/"), context))
    return _finish(results, args)


def _finish(results: list[Check], args) -> int:
    if args.json:
        print(json.dumps([r.__dict__ for r in results], ensure_ascii=False, indent=2))
    else:
        print(format_summary(results))
    return exit_code(results)


if __name__ == "__main__":
    raise SystemExit(main())
