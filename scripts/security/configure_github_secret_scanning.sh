#!/usr/bin/env bash
# ==============================================================================
# Configure GitHub secret scanning protections for this repository.
#
# Enables by `gh api` the protections that are API-settable (secret scanning and
# push protection), always prints the UI-only steps, and optionally resolves a
# secret scanning alert by number. Idempotent: reads the current state and only
# writes what is missing.
#
# No secrets are embedded and git history is never rewritten.
#
# Usage:
#   bash scripts/security/configure_github_secret_scanning.sh [--dry-run]
#   bash scripts/security/configure_github_secret_scanning.sh --repo owner/name
#   bash scripts/security/configure_github_secret_scanning.sh \
#       --resolve-alert 1 --resolution revoked --confirm
#
# Environment:
#   GH_BIN  path to the gh binary (default: gh)
#
# Exit codes:
#   0 — success (or dry-run)
#   1 — error (missing gh, failed API call, resolution without --confirm)
# ==============================================================================

set -euo pipefail

GH_BIN="${GH_BIN:-gh}"
DRY_RUN="false"
REPO=""
RESOLVE_ALERT=""
RESOLUTION=""
CONFIRM="false"

log() { printf '%s\n' "$*"; }
err() { printf 'ERROR: %s\n' "$*" >&2; }

usage() {
  cat <<'EOF'
Usage: configure_github_secret_scanning.sh [options]

Options:
  --dry-run             Print the planned operations without writing.
  --repo owner/name     Target repository (default: resolved via gh repo view).
  --resolve-alert N     Resolve alert number N (requires --confirm).
  --resolution RES      revoked | false_positive | used_in_tests | wont_fix.
  --confirm             Confirm an external write (required for --resolve-alert).
  -h, --help            Show this help.

Environment:
  GH_BIN                Path to the gh binary (default: gh).
EOF
}

parse_args() {
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --dry-run) DRY_RUN="true"; shift ;;
      --repo) REPO="${2:-}"; shift 2 ;;
      --resolve-alert) RESOLVE_ALERT="${2:-}"; shift 2 ;;
      --resolution) RESOLUTION="${2:-}"; shift 2 ;;
      --confirm) CONFIRM="true"; shift ;;
      -h|--help) usage; exit 0 ;;
      *) err "opcion desconocida: $1"; usage >&2; exit 1 ;;
    esac
  done
}

require_gh() {
  if ! command -v "$GH_BIN" >/dev/null 2>&1; then
    err "no se encontro el binario '$GH_BIN'. Instala GitHub CLI o define GH_BIN con su ruta."
    exit 1
  fi
}

gh_api() {
  local out
  if ! out="$("$GH_BIN" api "$@")"; then
    err "fallo 'gh api $*'. Verifica que '$GH_BIN' este autenticado con permisos de administracion del repositorio."
    return 1
  fi
  printf '%s' "$out"
}

resolve_repo() {
  [[ -n "$REPO" ]] && return 0
  local json
  if ! json="$("$GH_BIN" repo view --json nameWithOwner)"; then
    err "no se pudo resolver el repositorio con 'gh repo view'. Usa --repo owner/name o autentica gh."
    exit 1
  fi
  REPO="$(python3 -c 'import sys, json; print(json.load(sys.stdin)["nameWithOwner"])' <<< "$json")"
}

read_status() {
  local json
  json="$(gh_api "repos/$REPO")"
  python3 -c '
import sys, json
analysis = json.load(sys.stdin)["security_and_analysis"]
print(
    analysis["secret_scanning"]["status"],
    analysis["secret_scanning_push_protection"]["status"],
)
' <<< "$json"
}

ui_steps() {
  local features=(
    "secret_scanning_non_provider_patterns"
    "secret_scanning_validity_checks"
  )
  local index=1
  local feature
  log ""
  log "Funciones NO disponibles en este repo (requieren GitHub Secret Protection, plan pago)."
  log "No son configurables por API REST (la API las ignora en silencio) y la UI no muestra los toggles:"
  for feature in "${features[@]}"; do
    log "  $index. $feature -> Settings > Security and quality > Advanced Security (solo con plan pago)"
    index=$((index + 1))
  done
}

enable_protections() {
  local secret_scanning="$1"
  local push_protection="$2"
  local fields=()
  if [[ "$secret_scanning" != "enabled" ]]; then
    fields+=("-f" "security_and_analysis[secret_scanning][status]=enabled")
  fi
  if [[ "$push_protection" != "enabled" ]]; then
    fields+=("-f" "security_and_analysis[secret_scanning_push_protection][status]=enabled")
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "[dry-run] Operaciones API-settable sobre repos/$REPO:"
    log "[dry-run]   security_and_analysis[secret_scanning][status]=enabled (actual: $secret_scanning)"
    log "[dry-run]   security_and_analysis[secret_scanning_push_protection][status]=enabled (actual: $push_protection)"
    if [[ ${#fields[@]} -eq 0 ]]; then
      log "[dry-run] Sin cambios necesarios: ambas ya estan habilitadas."
    fi
    return 0
  fi
  if [[ ${#fields[@]} -eq 0 ]]; then
    log "secret scanning y push protection ya estaban habilitadas; no hay cambios."
    return 0
  fi
  gh_api "repos/$REPO" --method PATCH "${fields[@]}" >/dev/null
  log "Protecciones habilitadas por API en repos/$REPO."
}

list_alerts() {
  local json
  json="$(gh_api "repos/$REPO/secret-scanning/alerts?state=open")"
  log ""
  log "Alertas abiertas de secret scanning:"
  python3 -c '
import sys, json
alerts = json.load(sys.stdin)
if not alerts:
    print("  (ninguna)")
for alert in alerts:
    print("  - #%s %s" % (alert["number"], alert["secret_type"]))
' <<< "$json"
}

resolve_alert() {
  [[ -z "$RESOLVE_ALERT" ]] && return 0
  if [[ -z "$RESOLUTION" ]]; then
    err "--resolve-alert requiere --resolution (revoked|false_positive|used_in_tests|wont_fix)."
    exit 1
  fi
  if [[ "$CONFIRM" != "true" ]]; then
    err "--resolve-alert requiere --confirm explicito para modificar el estado de auditoria del repositorio."
    exit 1
  fi
  if [[ "$DRY_RUN" == "true" ]]; then
    log "[dry-run] gh api --method PATCH repos/$REPO/secret-scanning/alerts/$RESOLVE_ALERT -f state=resolved -f resolution=$RESOLUTION"
    return 0
  fi
  local json
  json="$(gh_api "repos/$REPO/secret-scanning/alerts/$RESOLVE_ALERT" --method PATCH -f state=resolved -f "resolution=$RESOLUTION")"
  log "Alerta #$RESOLVE_ALERT resuelta: $(python3 -c 'import sys, json; d = json.load(sys.stdin); print(d.get("state"), d.get("resolution"))' <<< "$json")"
}

main() {
  parse_args "$@"
  require_gh
  resolve_repo
  local status secret_scanning push_protection
  status="$(read_status)"
  read -r secret_scanning push_protection <<< "$status"
  log "Repositorio: $REPO"
  log "secret_scanning: $secret_scanning"
  log "secret_scanning_push_protection: $push_protection"
  enable_protections "$secret_scanning" "$push_protection"
  ui_steps
  list_alerts
  resolve_alert
  log ""
  log "Listo."
}

main "$@"
