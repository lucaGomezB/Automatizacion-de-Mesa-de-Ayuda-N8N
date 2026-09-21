"""
Tests estructurales de la documentacion de bootstrap — C-42: bootstrap-docs-sync

Verifica que `README.md` y `docs/operational-guide.md` queden sincronizados con el
contrato real del bootstrap local:

- el preflight de entorno exige `JWT_SECRET_KEY` (ademas de `GEMINI_API_KEY` y
  `PSEUDONYMIZATION_ENCRYPTION_KEY`);
- el comando unico ejecuta un preflight de costo antes de tocar Docker y admite el
  bypass explicito `UP_SKIP_COST_PREFLIGHT=1`;
- la guia operativa presenta el comando unico como camino recomendado sin eliminar
  el camino manual.

Strict TDD: cada grupo de tests refleja un ciclo RED->GREEN->TRIANGULATE->REFACTOR.
Los asserts apuntan solo a tokens estables (nombres de variables, comandos y URLs),
nunca a oraciones completas: una mejora de redaccion no debe producir un falso rojo.
"""

from __future__ import annotations

from pathlib import Path

# Raiz del repo: tres niveles por encima de App/Backend/tests/ (patron de
# test_n8n_workflow.py).
REPO_ROOT = Path(__file__).resolve().parents[3]

README = "README.md"
OPERATIONAL_GUIDE = "docs/operational-guide.md"

DOC_PATHS = {
    README: REPO_ROOT / README,
    OPERATIONAL_GUIDE: REPO_ROOT / OPERATIONAL_GUIDE,
}

# Tokens estables del contrato de bootstrap (nombres de variables, comandos, URLs).
TOKEN_JWT_SECRET_KEY = "JWT_SECRET_KEY"
TOKEN_SKIP_COST_PREFLIGHT = "UP_SKIP_COST_PREFLIGHT"
TOKEN_SINGLE_COMMAND = "scripts/up.sh"
TOKEN_MAKE_UP = "make up"
TOKEN_MANUAL_UP = "docker compose up -d"
TOKEN_MANUAL_CERTS = "openssl/generate-certs.sh"
TOKEN_HEALTH_URL = "https://localhost/api/v1/health"
TOKEN_MANUAL_RECOMMENDED = "camino manual recomendado"


def read_doc(doc: str) -> str:
    """Lee un documento del repo por su ruta relativa, fallando si no existe."""
    path = DOC_PATHS[doc]
    assert path.exists(), f"Documento no encontrado en: {path}"
    return path.read_text(encoding="utf-8")


def require_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` contiene `token`, con un mensaje accionable."""
    assert token in text, f"{doc} no contiene {token!r} ({context})"


def require_absent_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` NO contiene `token` (control negativo)."""
    assert token not in text.lower(), f"{doc} contiene {token!r} (no permitido: {context})"


# ---------------------------------------------------------------------------
# Grupo 1 — README sincronizado con el preflight de entorno (RED)
# ---------------------------------------------------------------------------


def test_readme_documents_jwt_secret_key():
    """
    RED -> GREEN (1.1): el README nombra `JWT_SECRET_KEY` entre las condiciones
    de fallo del comando unico.
    Spec: «nombra GEMINI_API_KEY, PSEUDONYMIZATION_ENCRYPTION_KEY y JWT_SECRET_KEY
    como las variables que no deben estar ausentes, vacias ni conservar placeholders».
    """
    require_token(
        read_doc(README),
        TOKEN_JWT_SECRET_KEY,
        README,
        "condiciones de fallo del comando unico",
    )


def test_readme_documents_cost_preflight_bypass():
    """
    RED -> GREEN (1.2): el README documenta el bypass `UP_SKIP_COST_PREFLIGHT`
    del preflight de costo.
    Spec: «documenta el bypass explicito UP_SKIP_COST_PREFLIGHT=1 y que su uso
    emite una advertencia audible».
    """
    require_token(
        read_doc(README),
        TOKEN_SKIP_COST_PREFLIGHT,
        README,
        "bypass del preflight de costo",
    )


# ---------------------------------------------------------------------------
# Grupo 2 — Guia operativa sincronizada con el comando unico (RED)
# ---------------------------------------------------------------------------


def test_guide_documents_single_command_and_cost_gate():
    """
    RED -> GREEN (1.3): la guia operativa referencia el comando unico
    (`scripts/up.sh` o `make up`) y documenta `UP_SKIP_COST_PREFLIGHT`.
    Spec: «la guia presenta el comando unico como el camino recomendado» y
    «documenta el bypass explicito UP_SKIP_COST_PREFLIGHT=1».
    """
    guide = read_doc(OPERATIONAL_GUIDE)
    has_single_command = (
        TOKEN_SINGLE_COMMAND in guide or TOKEN_MAKE_UP in guide
    )
    assert has_single_command, (
        f"{OPERATIONAL_GUIDE} no referencia el comando unico "
        f"({TOKEN_SINGLE_COMMAND} o {TOKEN_MAKE_UP}) como camino recomendado"
    )
    require_token(
        guide,
        TOKEN_SKIP_COST_PREFLIGHT,
        OPERATIONAL_GUIDE,
        "bypass del preflight de costo",
    )


# ---------------------------------------------------------------------------
# Grupo 3 — TRIANGULATE: el camino manual y la salud siguen documentados
# ---------------------------------------------------------------------------


def test_guide_keeps_manual_path():
    """
    TRIANGULATE (4.1): la guia conserva `docker compose up -d` como alternativa
    manual.
    Spec: «los comandos de generacion manual de certificados y docker compose up -d
    siguen documentados como alternativa».
    """
    guide = read_doc(OPERATIONAL_GUIDE)
    require_token(guide, TOKEN_MANUAL_UP, OPERATIONAL_GUIDE, "camino manual")
    require_token(
        guide, TOKEN_MANUAL_CERTS, OPERATIONAL_GUIDE, "generacion manual de certificados"
    )


def test_readme_keeps_manual_path_and_health_url():
    """
    TRIANGULATE (4.2): el README conserva `docker compose up -d` y la URL de
    verificacion de salud `https://localhost/api/v1/health`.
    Spec: «las URL de verificacion de salud MUST referenciar
    https://localhost/api/v1/health».
    """
    readme = read_doc(README)
    require_token(readme, TOKEN_MANUAL_UP, README, "camino manual")
    require_token(readme, TOKEN_HEALTH_URL, README, "URL de salud HTTPS")


def test_readme_does_not_present_manual_as_recommended():
    """
    TRIANGULATE negativo (4.3): control que guarda contra presentar el camino
    manual como recomendado en el README.
    Spec: el comando unico es el camino recomendado; el manual es una alternativa.
    """
    require_absent_token(
        read_doc(README),
        TOKEN_MANUAL_RECOMMENDED,
        README,
        "solo el comando unico debe ser el camino recomendado",
    )