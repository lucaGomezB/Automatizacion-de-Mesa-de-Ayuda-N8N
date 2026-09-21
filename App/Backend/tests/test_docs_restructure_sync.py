"""
Tests estructurales de la documentacion post-reestructuracion — C-43: docs-restructure-sync

Verifica que la documentacion vigente quede sincronizada con la estructura real
del repositorio tras el change c-24 (el modulo Python vive en `App/Backend/`, no
en el obsoleto `Gestion_Incidentes/`):

- la tabla de variables de entorno de `README.md` (seccion "Configurar las
  variables de entorno") y el bloque dotenv de la seccion 1.2 de
  `docs/operational-guide.md` listan `JWT_SECRET_KEY`;
- los documentos vigentes referencian `App/Backend/` y ya no presentan
  `Gestion_Incidentes/` como ubicacion actual;
- `docs/security-hardening.md` conserva el hecho historico (el archivo estaba en
  `Gestion_Incidentes/.env`) y lo anota como ruta historica.

Strict TDD: cada grupo de tests refleja un ciclo RED->GREEN->TRIANGULATE->REFACTOR.
Los asserts apuntan solo a tokens estables (rutas y nombres de variables), nunca a
oraciones completas: una mejora de redaccion no debe producir un falso rojo. El
caso del README se aisla por encabezado de seccion para no pasar de forma trivial
por la mencion en prosa que c-42 ya dejo fuera de la tabla.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

# Raiz del repo: tres niveles por encima de App/Backend/tests/ (patron de
# test_docs_bootstrap_sync.py).
REPO_ROOT = Path(__file__).resolve().parents[3]

README = "README.md"
OPERATIONAL_GUIDE = "docs/operational-guide.md"
SECURITY_HARDENING = "docs/security-hardening.md"

README_ENV_HEADING = "### 2. Configurar las variables de entorno"
GUIDE_ENV_HEADING = "### 1.2 Configurar variables de entorno"

# Tokens estables del contrato de reestructuracion.
TOKEN_JWT_SECRET_KEY = "JWT_SECRET_KEY"
# El nombre base del modulo obsoleto, sin barra: el corpus lo usa desnudo en
# `PYTHONPATH=Gestion_Incidentes` (linea 189), por lo que un control con barra
# no lo detectaria.
TOKEN_OBSOLETE_MODULE = "Gestion_Incidentes"
TOKEN_HISTORICAL_PATH = "Gestion_Incidentes/.env"
TOKEN_CURRENT_PATH = "App/Backend/"
TOKEN_HISTORICAL_MARKER = "ruta historica"

# Tokens de c-42 que no deben regresar (cobertura de triangulacion).
TOKEN_SKIP_COST_PREFLIGHT = "UP_SKIP_COST_PREFLIGHT"
TOKEN_HEALTH_URL = "https://localhost/api/v1/health"
TOKEN_SINGLE_COMMAND = "scripts/up.sh"
TOKEN_MAKE_UP = "make up"
SINGLE_COMMAND_TOKENS = (TOKEN_SINGLE_COMMAND, TOKEN_MAKE_UP)
TOKEN_MANUAL_UP = "docker compose up -d"

# Documentos vigentes que deben referenciar la ubicacion actual del modulo.
STALE_PATH_DOCS = (
    OPERATIONAL_GUIDE,
    "docs/troubleshooting.md",
    "docs/como_cargar_datos_corpus.md",
    "docs/diagrams/componentes.md",
    "docs/parameters_gemini.md",
    "docs/pseudonymization.md",
    "docs/anexo_c_esquema_bd.md",
)

HEADING_RE = re.compile(r"^#{1,6}\s")


def doc_path(doc: str) -> Path:
    """Resuelve la ruta absoluta de un documento del repo."""
    return REPO_ROOT / doc


def read_doc(doc: str) -> str:
    """Lee un documento del repo, fallando con mensaje accionable si no existe."""
    path = doc_path(doc)
    assert path.exists(), f"Documento no encontrado en: {path}"
    return path.read_text(encoding="utf-8")


def read_section(doc: str, heading: str) -> str:
    """
    Devuelve el texto de la seccion que comienza con `heading` hasta el siguiente
    encabezado de cualquier nivel, ignorando `#` dentro de bloques con fences.
    """
    lines = read_doc(doc).splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.strip() == heading), None
    )
    assert start is not None, f"{doc} no contiene el encabezado {heading!r}"

    collected = [lines[start]]
    in_fence = False
    for line in lines[start + 1 :]:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            collected.append(line)
            continue
        if not in_fence and HEADING_RE.match(line):
            break
        collected.append(line)
    return "\n".join(collected)


def require_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` contiene `token`, con un mensaje accionable."""
    assert token in text, f"{doc} no contiene {token!r} ({context})"


def require_absent_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` NO contiene `token` (control negativo)."""
    assert token not in text, f"{doc} contiene {token!r} (no permitido: {context})"


def contains_any_token(text: str, tokens: tuple[str, ...]) -> bool:
    """Devuelve True si `text` contiene al menos uno de `tokens`."""
    return any(token in text for token in tokens)


# ---------------------------------------------------------------------------
# Grupo 1 — README: tabla de variables de entorno (RED)
# ---------------------------------------------------------------------------


def test_readme_env_section_lists_jwt_secret_key():
    """
    RED -> GREEN (1.1 / 2.1): la tabla de la seccion "Configurar las variables de
    entorno" de `README.md` lista `JWT_SECRET_KEY`.
    Spec: «la tabla lista JWT_SECRET_KEY ademas de GEMINI_API_KEY,
    PSEUDONYMIZATION_ENCRYPTION_KEY y DATABASE_URL».
    """
    section = read_section(README, README_ENV_HEADING)
    require_token(
        section,
        TOKEN_JWT_SECRET_KEY,
        README,
        "tabla de variables de entorno de la seccion 2",
    )


# ---------------------------------------------------------------------------
# Grupo 2 — Guia operativa: bloque dotenv de la seccion 1.2 (RED)
# ---------------------------------------------------------------------------


def test_guide_env_section_lists_jwt_secret_key():
    """
    RED -> GREEN (1.2 / 2.2): el bloque dotenv de la seccion 1.2 de
    `docs/operational-guide.md` incluye `JWT_SECRET_KEY`.
    Spec: «el bloque dotenv incluye JWT_SECRET_KEY junto a DATABASE_URL,
    GEMINI_API_KEY y PSEUDONYMIZATION_ENCRYPTION_KEY».
    """
    section = read_section(OPERATIONAL_GUIDE, GUIDE_ENV_HEADING)
    require_token(
        section,
        TOKEN_JWT_SECRET_KEY,
        OPERATIONAL_GUIDE,
        "bloque dotenv de la seccion 1.2",
    )


# ---------------------------------------------------------------------------
# Grupo 3 — Documentos vigentes referencian la ruta actual (RED)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("doc", STALE_PATH_DOCS)
def test_stale_path_docs_reference_current_module_path(doc: str):
    """
    RED -> GREEN (1.3 / 3.2-3.6): cada documento en alcance referencia `App/Backend/`
    donde describe la ubicacion del modulo, su `.env`, modelos, migraciones o comandos.
    Spec: «referencian las rutas vigentes bajo App/Backend/».
    """
    require_token(
        read_doc(doc),
        TOKEN_CURRENT_PATH,
        doc,
        "ruta vigente del modulo",
    )


# ---------------------------------------------------------------------------
# Grupo 4 — Control negativo: el token obsoleto desaparece (RED)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("doc", STALE_PATH_DOCS)
def test_stale_path_docs_do_not_present_obsolete_module_path(doc: str):
    """
    RED -> GREEN (1.4 / 3.2-3.6): ninguno de los documentos vigentes en alcance
    presenta `Gestion_Incidentes/` como ubicacion actual.
    Spec: «no presentan Gestion_Incidentes/ como la ubicacion actual».
    `docs/security-hardening.md` queda EXCLUIDO: conserva el hecho historico.
    """
    require_absent_token(
        read_doc(doc),
        TOKEN_OBSOLETE_MODULE,
        doc,
        "ruta obsoleta post-reestructuracion",
    )


# ---------------------------------------------------------------------------
# Grupo 5 — Narrativa historica conservada con anotacion (RED)
# ---------------------------------------------------------------------------


def test_security_hardening_keeps_historical_fact_with_annotation():
    """
    RED -> GREEN (1.5 / 4.1): la narrativa historica conserva el hecho (el archivo
    estaba en `Gestion_Incidentes/.env`) y lo anota como ruta historica.
    Spec: «el hecho documentado se conserva sin reescribirse» y «la mencion se
    anota como ruta historica, indicando que hoy el modulo vive en App/Backend/».
    """
    hardening = read_doc(SECURITY_HARDENING)
    require_token(
        hardening,
        TOKEN_HISTORICAL_PATH,
        SECURITY_HARDENING,
        "hecho historico conservado",
    )
    require_token(
        hardening,
        TOKEN_HISTORICAL_MARKER,
        SECURITY_HARDENING,
        "anotacion de ruta historica",
    )
    require_token(
        hardening,
        TOKEN_CURRENT_PATH,
        SECURITY_HARDENING,
        "ubicacion vigente indicada en la anotacion",
    )


# ---------------------------------------------------------------------------
# Grupo 6 — TRIANGULATE: alcance del control negativo y no-regresion de c-42
# ---------------------------------------------------------------------------


def test_negative_control_scope_is_exact():
    """
    TRIANGULATE (5.1): el control negativo cubre exactamente los siete documentos
    vigentes en alcance y excluye `docs/security-hardening.md`.
    Spec: «cualquier mencion en la tesis permanece sin cambios» y la excepcion
    historica de security-hardening.
    """
    assert SECURITY_HARDENING not in STALE_PATH_DOCS, (
        f"{SECURITY_HARDENING} no debe estar en el control negativo: conserva el "
        "hecho historico"
    )
    assert OPERATIONAL_GUIDE in STALE_PATH_DOCS
    assert len(STALE_PATH_DOCS) == 7, (
        f"el alcance debe cubrir 7 documentos, encontrados: {len(STALE_PATH_DOCS)}"
    )


def test_readme_keeps_c42_tokens():
    """
    TRIANGULATE (5.2): el README conserva los tokens de c-42
    (`UP_SKIP_COST_PREFLIGHT` y `https://localhost/api/v1/health`) como guarda
    contra regresion.
    """
    readme = read_doc(README)
    require_token(
        readme,
        TOKEN_SKIP_COST_PREFLIGHT,
        README,
        "bypass del preflight de costo (c-42)",
    )
    require_token(readme, TOKEN_HEALTH_URL, README, "URL de salud HTTPS (c-42)")


def test_guide_keeps_single_command_and_manual_path():
    """
    TRIANGULATE (5.3): la guia conserva el comando unico (`scripts/up.sh` o
    `make up`) y el camino manual (`docker compose up -d`).
    Spec: «presenta el comando unico como el camino recomendado» sin eliminar el
    camino manual.
    """
    guide = read_doc(OPERATIONAL_GUIDE)
    assert contains_any_token(guide, SINGLE_COMMAND_TOKENS), (
        f"{OPERATIONAL_GUIDE} no referencia el comando unico "
        f"({TOKEN_SINGLE_COMMAND} o {TOKEN_MAKE_UP})"
    )
    require_token(guide, TOKEN_MANUAL_UP, OPERATIONAL_GUIDE, "camino manual")