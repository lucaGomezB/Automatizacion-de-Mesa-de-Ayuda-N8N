"""Pure, side-effect-free evaluators for the c-140 E2E smoke checks.

Everything here is deterministic and unit-testable: it takes already-fetched API
payloads (the shape of the real endpoints) or already-observed header maps and
returns a ``Check``. No network, no Docker, no filesystem access.

``dry_run.py`` remains the orchestrator: it performs the I/O and delegates the
judgement to these functions. Keeping the judgement pure is what lets the harness
suite run offline in ``backend-tests`` (c-140, D14).

Endpoints modelled:
    GET /api/v1/clasificaciones/incidente/{id} -> list[ClasificacionLogRead]
    GET /api/v1/incidentes/?origen_message_id=... -> list[IncidenteListItem]
"""

from __future__ import annotations

from checks import (
    Check,
    extract_incidente_id,
    failing,
    passing,
    redact,
)

# ── Check names and canonical values ─────────────────────────────────────────

ETAPA_DETERMINISTIC = "deterministic"

CHECK_ETAPA = "e2e:etapa"
CHECK_IDEMPOTENCIA = "e2e:idempotencia"
CHECK_REINTENTO = "e2e:reintento"
CHECK_COST_GUARD_BUDGET = "guardrail:cost-guard-budget"


# ── Stage assertion (e2e:etapa) ──────────────────────────────────────────────


def evaluate_etapa(payload) -> Check:
    """Evaluate the classification history of the dry-run incident.

    The history must contain exactly one record and its ``etapa`` must be the
    deterministic one (cost-zero by construction). Any other stage
    (``gemini``/``fallback``/``precalculada``) or a non-single history is a loud
    failure naming what was observed.
    """
    if not isinstance(payload, list):
        return failing(
            CHECK_ETAPA,
            f"respuesta de clasificaciones no es una lista JSON ({type(payload).__name__})",
            "the clasificaciones endpoint must return a JSON array; check the backend link and the operator token",
        )
    if len(payload) == 0:
        return failing(
            CHECK_ETAPA,
            "sin registros de clasificacion para el incidente",
            "the incident was not classified; check `docker compose logs backend` and the workflow POST",
        )
    if len(payload) > 1:
        return failing(
            CHECK_ETAPA,
            f"se esperaba un unico registro de clasificacion, se observaron {len(payload)}",
            "a dry-run incident must be classified exactly once; check for duplicate POSTs or a replay",
        )
    etapa = payload[0].get("etapa") if isinstance(payload[0], dict) else None
    if etapa != ETAPA_DETERMINISTIC:
        return failing(
            CHECK_ETAPA,
            f"etapa observada={etapa!r}, esperada={ETAPA_DETERMINISTIC!r}",
            "the test description must resolve in the deterministic stage; pick deterministic hardware keywords",
        )
    return passing(CHECK_ETAPA, f"un unico registro, etapa={ETAPA_DETERMINISTIC}")


# ── Idempotency (e2e:idempotencia) ───────────────────────────────────────────


def evaluate_idempotency(first_payload, second_payload, listing, origen_message_id) -> Check:
    """Evaluate the web replay: same incident and a single filtered row."""
    first_id = extract_incidente_id(first_payload)
    second_id = extract_incidente_id(second_payload)
    if first_id is None or second_id is None:
        return failing(
            CHECK_IDEMPOTENCIA,
            f"respuestas del webhook sin incidente_id (primera={first_id}, segunda={second_id})",
            "the N8N webhook must respond with an incidente_id for both sends; check the workflow response node",
        )
    if first_id != second_id:
        return failing(
            CHECK_IDEMPOTENCIA,
            f"ids distintos entre reenvios: {first_id} != {second_id}",
            "the same origen_message_id must replay to the same incident (C-33/C-69); check the idempotency short-circuit",
        )
    if not isinstance(listing, list):
        return failing(
            CHECK_IDEMPOTENCIA,
            f"el listado filtrado no es una lista JSON ({type(listing).__name__})",
            "GET /api/v1/incidentes/?origen_message_id=... must return a JSON array",
        )
    if len(listing) != 1:
        return failing(
            CHECK_IDEMPOTENCIA,
            f"el listado por origen_message_id={origen_message_id!r} devolvio {len(listing)} incidentes (esperado 1)",
            "a replay must not create a second row; check the UNIQUE index on origen_message_id",
        )
    return passing(
        CHECK_IDEMPOTENCIA,
        f"mismo incidente_id={first_id} en ambos envios y listado filtrado unico",
    )


# ── Retry recovery (e2e:reintento) ───────────────────────────────────────────


def evaluate_retry_recovery(response_payload, listing, origen_message_id) -> Check:
    """Evaluate the opt-in recovery walk after a transient backend outage.

    Passes only when the webhook still answered with an incident and the filtered
    listing has exactly one row for the run identifier (no duplicate from the
    retry).
    """
    incidente_id = extract_incidente_id(response_payload)
    if incidente_id is None:
        return failing(
            CHECK_REINTENTO,
            "la respuesta del webhook no trae incidente tras la reconexion",
            "check `docker compose logs n8n`; the retry policy must recover within the wait window",
        )
    if not isinstance(listing, list):
        return failing(
            CHECK_REINTENTO,
            f"el listado filtrado no es una lista JSON ({type(listing).__name__})",
            "GET /api/v1/incidentes/?origen_message_id=... must return a JSON array",
        )
    if len(listing) != 1:
        return failing(
            CHECK_REINTENTO,
            f"el listado por origen_message_id={origen_message_id!r} devolvio {len(listing)} incidentes (esperado 1)",
            "a recovered retry must not duplicate the incident; check the idempotency short-circuit",
        )
    return passing(
        CHECK_REINTENTO,
        f"incidente_id={incidente_id} y fila unica tras recuperacion",
    )


# ── Cost-guard budget (guardrail:cost-guard-budget) ──────────────────────────


def evaluate_cost_guard_budget(effective_value) -> Check:
    """Evaluate the effective runtime cost-guard budget (layer 2 of cost zero).

    The dry-run overlay must force ``COST_GUARD_BUDGET_USD=0`` so any escalation
    is denied before any paid call. A missing, non-numeric or non-zero value
    aborts the run.
    """
    if effective_value is None or str(effective_value).strip() == "":
        return failing(
            CHECK_COST_GUARD_BUDGET,
            "COST_GUARD_BUDGET_USD no esta definida en el backend",
            "lift the backend with the dry-run overlay (scripts/dry_run/compose.dry-run.yml)",
        )
    raw = str(effective_value).strip()
    try:
        value = float(raw)
    except ValueError:
        return failing(
            CHECK_COST_GUARD_BUDGET,
            f"COST_GUARD_BUDGET_USD no es numerico: {raw!r}",
            'set COST_GUARD_BUDGET_USD: "0" in scripts/dry_run/compose.dry-run.yml',
        )
    if value != 0.0:
        return failing(
            CHECK_COST_GUARD_BUDGET,
            f"el presupuesto efectivo de la guarda es {value!r}, se exige 0 (abortar: evita costo pago)",
            'set COST_GUARD_BUDGET_USD: "0" in scripts/dry_run/compose.dry-run.yml',
        )
    return passing(
        CHECK_COST_GUARD_BUDGET,
        "presupuesto efectivo de la guarda de costo = 0 (capa 2 de costo cero)",
    )


# ── Evidence report ──────────────────────────────────────────────────────────


def groups_from_checks(results: list[Check]) -> list[str]:
    """Return the check-name prefixes in first-seen order (report grouping)."""
    groups: list[str] = []
    for result in results:
        prefix = result.name.split(":", 1)[0] if ":" in result.name else result.name
        if prefix not in groups:
            groups.append(prefix)
    return groups


def _scrub_secrets(value, secrets: list[str]):
    """Redact pattern-like credentials and every explicitly supplied secret."""
    if not isinstance(value, str):
        return value
    scrubbed = redact(value)
    for secret in secrets:
        if secret:
            scrubbed = scrubbed.replace(str(secret), "[REDACTED]")
    return scrubbed


def build_evidence_report(
    *,
    commit: str,
    timestamp_utc: str,
    n8n_version: str,
    groups: list[str],
    results: list[Check],
    secrets: list[str] | None = None,
) -> dict:
    """Build the versionable evidence report for the harness run.

    Contains the verified commit, the UTC timestamp, the N8N version, the groups
    executed and the outcome of each check. Never contains the operator password,
    the access token, API keys or cryptographic material.
    """
    secret_values = [s for s in (secrets or []) if s]
    checks_payload = [
        {
            "name": _scrub_secrets(result.name, secret_values),
            "status": result.status,
            "detail": _scrub_secrets(result.detail, secret_values),
            "action": _scrub_secrets(result.action, secret_values),
        }
        for result in results
    ]
    return {
        "commit": commit,
        "timestamp_utc": timestamp_utc,
        "n8n_version": n8n_version,
        "groups": list(groups),
        "summary": {
            "passed": sum(1 for result in results if result.ok),
            "total": len(results),
            "green": bool(results) and all(result.ok for result in results),
        },
        "checks": checks_payload,
    }
