"""
Tests estructurales y funcional de la sincronizacion de la documentacion de
evaluacion y del script de exportacion OpenAPI — C-44: docs-evaluation-sync

Verifica que:

- la seccion 8 de `docs/operational-guide.md` use la invocacion real del runner
  (`PYTHONPATH=App/Backend python -m evaluation.run_evaluation`) y no el
  `python run_evaluation.py` ni el `cd evaluation` que no resuelven los imports;
- la seccion 8 no referencie `evaluation/generate_corpus.py` (eliminado por C-27)
  ni afirme un generador de corpus con seed fijo, y apunte al procedimiento real
  documentado en `docs/como_cargar_datos_corpus.md`;
- la guia y `evaluation/README.md` documenten el gate de corrida paga
  (`--confirm-paid` / `EVALUATION_CONFIRM_PAID`);
- `App/Backend/scripts/export_openapi.py` declare `JWT_SECRET_KEY` en sus dummies
  y no conserve rutas obsoletas (`Gestion_Incidentes`).

Strict TDD: cada grupo de tests refleja un ciclo RED->GREEN->TRIANGULATE->REFACTOR.
Los asserts apuntan solo a tokens estables (comandos, nombres de variables y
rutas), nunca a oraciones completas: una mejora de redaccion no debe producir un
falso rojo. El caso funcional ejecuta el script en un subproceso con el entorno
depurado para reproducir el fallo de `Settings` sin fugas de `.env`.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

# Raiz del repo: tres niveles por encima de App/Backend/tests/ (patron de
# test_docs_restructure_sync.py).
REPO_ROOT = Path(__file__).resolve().parents[3]

OPERATIONAL_GUIDE = "docs/operational-guide.md"
EVALUATION_README = "evaluation/README.md"
EXPORT_OPENAPI_SCRIPT = "App/Backend/scripts/export_openapi.py"
CORPUS_PROCEDURE_DOC = "docs/como_cargar_datos_corpus.md"

# Encabezado que aisla la seccion de evaluacion de la guia.
GUIDE_SECTION_8_HEADING = "## 8. Evaluacion del clasificador"

# Tokens estables del flujo de evaluacion.
TOKEN_RUNNER_INVOCATION = "PYTHONPATH=App/Backend python -m evaluation.run_evaluation"
TOKEN_BROKEN_RUNNER = "python run_evaluation.py"
TOKEN_BROKEN_CD = "cd evaluation"
TOKEN_GENERATE_CORPUS = "generate_corpus.py"
TOKEN_SEED_CLAIM = "seed fijo"
TOKEN_CORPUS_PROCEDURE = "docs/como_cargar_datos_corpus.md"
TOKEN_CONFIRM_PAID = "confirm-paid"
TOKEN_CONFIRM_PAID_ENV = "EVALUATION_CONFIRM_PAID"
TOKEN_REPORT = "evaluation/report.md"

# Tokens estables del script de exportacion OpenAPI.
TOKEN_JWT_SECRET_KEY = "JWT_SECRET_KEY"
TOKEN_OBSOLETE_MODULE = "Gestion_Incidentes"
TOKEN_OPENAPI_31 = "3.1"

# Tokens de c-43 que no deben regresar (cobertura de triangulacion cruzada).
TOKEN_CURRENT_PATH = "App/Backend/"
TOKEN_SKIP_COST_PREFLIGHT = "UP_SKIP_COST_PREFLIGHT"
TOKEN_MANUAL_UP = "docker compose up -d"

HEADING_RE = re.compile(r"^(?P<level>#{1,6})\s")
DUMMIES_BLOCK_RE = re.compile(r"_DUMMIES\s*=\s*\{(?P<body>[^}]*)\}")
FENCE_RE = re.compile(r"```[^\n]*\n(?P<body>.*?)```", re.DOTALL)

# Variables requeridas por Settings que el script inyecta como dummies.
SETTINGS_REQUIRED_ENV_VARS = (
    "DATABASE_URL",
    "GEMINI_API_KEY",
    "PSEUDONYMIZATION_ENCRYPTION_KEY",
    "JWT_SECRET_KEY",
)


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
    encabezado de nivel igual o superior, ignorando `#` dentro de bloques con
    fences. Las subsecciones (`###`) de la seccion se incluyen.
    """
    lines = read_doc(doc).splitlines()
    start = next(
        (i for i, line in enumerate(lines) if line.strip() == heading), None
    )
    assert start is not None, f"{doc} no contiene el encabezado {heading!r}"

    start_match = HEADING_RE.match(heading.strip())
    assert start_match is not None, f"el encabezado {heading!r} no es un titulo Markdown"
    start_level = len(start_match.group("level"))

    collected = [lines[start]]
    in_fence = False
    for line in lines[start + 1 :]:
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            collected.append(line)
            continue
        match = None if in_fence else HEADING_RE.match(line)
        if match and len(match.group("level")) <= start_level:
            break
        collected.append(line)
    return "\n".join(collected)


def read_dummies_block(script: str) -> str:
    """
    Extrae el cuerpo del diccionario `_DUMMIES` de un script Python.

    Se aisla el bloque para no pasar de forma trivial por una mencion de
    `JWT_SECRET_KEY` fuera de los dummies.
    """
    text = read_doc(script)
    match = DUMMIES_BLOCK_RE.search(text)
    assert match is not None, f"{script} no declara un bloque `_DUMMIES = {{...}}`"
    return match.group("body")


def read_fenced_blocks(text: str) -> list[str]:
    """Devuelve el contenido de cada bloque de codigo con fences de `text`."""
    return [match.group("body") for match in FENCE_RE.finditer(text)]


def require_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` contiene `token`, con un mensaje accionable."""
    assert token in text, f"{doc} no contiene {token!r} ({context})"


def require_absent_token(text: str, token: str, doc: str, context: str) -> None:
    """Asserta que `text` NO contiene `token` (control negativo)."""
    assert token not in text, f"{doc} contiene {token!r} (no permitido: {context})"


def run_export_script(
    tmp_path: Path,
    *,
    extra_env: dict[str, str] | None = None,
    strip_env: tuple[str, ...] = SETTINGS_REQUIRED_ENV_VARS,
    output_name: str = "openapi.json",
) -> tuple[subprocess.CompletedProcess[str], Path]:
    """
    Ejecuta `export_openapi.py` en un subproceso con entorno depurado y cwd en un
    directorio temporal (sin `.env` descubrible), apuntando a una salida temporal.

    Returns:
        La tupla (proceso completado, ruta del archivo de salida).
    """
    env = {key: value for key, value in os.environ.items() if key not in strip_env}
    if extra_env:
        env.update(extra_env)
    output = tmp_path / output_name
    process = subprocess.run(
        [
            sys.executable,
            str(doc_path(EXPORT_OPENAPI_SCRIPT)),
            "--output",
            str(output),
        ],
        cwd=str(tmp_path),
        env=env,
        capture_output=True,
        text=True,
    )
    return process, output


def load_openapi(output: Path) -> dict:
    """Carga el JSON generado y valida que sea un documento OpenAPI 3.1 valido."""
    assert output.exists(), f"El script no genero el archivo: {output}"
    schema = json.loads(output.read_text(encoding="utf-8"))
    openapi_version = schema.get("openapi", "")
    assert openapi_version.startswith(TOKEN_OPENAPI_31), (
        f"El documento no declara OpenAPI 3.1: {openapi_version!r}"
    )
    assert schema.get("paths"), "El documento OpenAPI no contiene rutas en `paths`"
    return schema


def assert_script_succeeded(
    process: subprocess.CompletedProcess[str], output: Path, context: str
) -> dict:
    """Asserta exit code 0 con mensaje accionable y valida el OpenAPI generado."""
    assert process.returncode == 0, (
        f"el script fallo {context}:\n"
        f"stdout: {process.stdout}\nstderr: {process.stderr}"
    )
    return load_openapi(output)


# ---------------------------------------------------------------------------
# Grupo 1 — Seccion 8 de la guia: invocacion real del runner (RED)
# ---------------------------------------------------------------------------


def test_guide_section_8_uses_real_runner_invocation():
    """
    RED -> GREEN (1.2 / 2.1): la seccion 8 de `docs/operational-guide.md`
    documenta la invocacion real del runner desde la raiz del repositorio y no
    presenta `python run_evaluation.py` ni un `cd evaluation` en la invocacion del
    runner.
    Spec: «el comando de corrida documentado es
    PYTHONPATH=App/Backend python -m evaluation.run_evaluation, ejecutado desde la
    raiz del repositorio» y «no presenta python run_evaluation.py ni un cd
    evaluation que no resuelva los imports del paquete como forma de invocacion».
    El control de `cd evaluation` se limita al bloque de invocacion del runner: el
    bloque de tests del framework (§8.3) usa `cd evaluation` legitimamente porque
    sus imports si resuelven.
    """
    section = read_section(OPERATIONAL_GUIDE, GUIDE_SECTION_8_HEADING)
    require_token(
        section,
        TOKEN_RUNNER_INVOCATION,
        OPERATIONAL_GUIDE,
        "invocacion real del runner en la seccion 8",
    )
    require_absent_token(
        section,
        TOKEN_BROKEN_RUNNER,
        OPERATIONAL_GUIDE,
        "invocacion rota del runner",
    )
    runner_blocks = [
        block
        for block in read_fenced_blocks(section)
        if TOKEN_RUNNER_INVOCATION in block
    ]
    assert runner_blocks, (
        f"{OPERATIONAL_GUIDE} no expone la invocacion real del runner en un bloque "
        "de codigo"
    )
    for block in runner_blocks:
        require_absent_token(
            block,
            TOKEN_BROKEN_CD,
            OPERATIONAL_GUIDE,
            "cd evaluation en la invocacion del runner",
        )


# ---------------------------------------------------------------------------
# Grupo 2 — Seccion 8 de la guia: corpus real, no generador eliminado (RED)
# ---------------------------------------------------------------------------


def test_guide_section_8_drops_deleted_corpus_generator():
    """
    RED -> GREEN (1.3 / 2.2): la seccion 8 no referencia
    `evaluation/generate_corpus.py` ni afirma un generador de corpus con seed
    fijo, y apunta al procedimiento real de carga del corpus.
    Spec: «no referencia evaluation/generate_corpus.py ni afirma un generador de
    corpus con seed fijo» y «apunta al procedimiento real de carga del corpus en
    docs/como_cargar_datos_corpus.md».
    """
    section = read_section(OPERATIONAL_GUIDE, GUIDE_SECTION_8_HEADING)
    require_absent_token(
        section,
        TOKEN_GENERATE_CORPUS,
        OPERATIONAL_GUIDE,
        "generador de corpus eliminado por C-27",
    )
    require_absent_token(
        section,
        TOKEN_SEED_CLAIM,
        OPERATIONAL_GUIDE,
        "afirmacion de generador con seed fijo",
    )
    require_token(
        section,
        TOKEN_CORPUS_PROCEDURE,
        OPERATIONAL_GUIDE,
        "puntero al procedimiento real de carga del corpus",
    )


# ---------------------------------------------------------------------------
# Grupo 3 — Gate de corrida paga documentado en guia y README (RED)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("doc", [OPERATIONAL_GUIDE, EVALUATION_README])
def test_paid_run_gate_tokens_documented(doc: str):
    """
    RED -> GREEN (1.4 / 2.3 / 3.1): la guia y `evaluation/README.md` documentan
    el gate de corrida paga nombrando `confirm-paid` y `EVALUATION_CONFIRM_PAID`.
    Spec: el README «MUST nombrar las dos formas de confirmación (--confirm-paid y
    EVALUATION_CONFIRM_PAID=1)»; la guia «menciona que una corrida que invocaria
    el clasificador real exige confirmacion explicita con --confirm-paid o
    EVALUATION_CONFIRM_PAID=1».
    """
    text = read_doc(doc)
    require_token(text, TOKEN_CONFIRM_PAID, doc, "flag de confirmacion paga")
    require_token(
        text,
        TOKEN_CONFIRM_PAID_ENV,
        doc,
        "variable de entorno de confirmacion paga",
    )


# ---------------------------------------------------------------------------
# Grupo 4 — Script de exportacion OpenAPI: dummies y rutas (RED)
# ---------------------------------------------------------------------------


def test_export_script_dummies_include_jwt_secret_key():
    """
    RED -> GREEN (1.5 / 4.1): el bloque `_DUMMIES` de `export_openapi.py` declara
    `JWT_SECRET_KEY` para instanciar `Settings` sin entorno real.
    Spec: «ese conjunto MUST incluir explícitamente JWT_SECRET_KEY».
    """
    dummies = read_dummies_block(EXPORT_OPENAPI_SCRIPT)
    require_token(
        dummies,
        TOKEN_JWT_SECRET_KEY,
        EXPORT_OPENAPI_SCRIPT,
        "dummy de JWT_SECRET_KEY en el bloque _DUMMIES",
    )


def test_export_script_drops_obsolete_module_path():
    """
    RED -> GREEN (1.5 / 4.2): el script no presenta `Gestion_Incidentes` como
    ubicacion del modulo ni de sus comandos.
    Spec: «MUST NOT presentar Gestion_Incidentes/ como ubicación del módulo ni de
    sus comandos».
    """
    require_absent_token(
        read_doc(EXPORT_OPENAPI_SCRIPT),
        TOKEN_OBSOLETE_MODULE,
        EXPORT_OPENAPI_SCRIPT,
        "ruta obsoleta post-reestructuracion",
    )


# ---------------------------------------------------------------------------
# Grupo 5 — Funcional: el script corre sin JWT_SECRET_KEY real (RED)
# ---------------------------------------------------------------------------


def test_export_openapi_runs_without_jwt_env(tmp_path: Path):
    """
    RED -> GREEN (1.6 / 4.1): ejecutar `export_openapi.py` en un subproceso con
    `JWT_SECRET_KEY` (y demas variables requeridas) eliminadas del entorno y cwd
    en un directorio temporal sin `.env` descubrible termina con exit code 0 y
    produce un OpenAPI 3.1 valido con `paths` no vacio.
    Spec: «termina con código de salida 0 y produce un documento OpenAPI 3.1
    válido, sin fallar la validación de Settings».
    Antes de agregar el dummy, el script falla con el error de validacion de
    `Settings` (`jwt_secret_key` requerido).
    """
    process, output = run_export_script(tmp_path)
    assert_script_succeeded(process, output, "en un entorno sin JWT_SECRET_KEY real")


# ---------------------------------------------------------------------------
# Grupo 6 — TRIANGULATE: no-regresion de comportamiento y tokens cruzados
# ---------------------------------------------------------------------------


def test_guide_section_8_keeps_report_reference():
    """
    TRIANGULATE (5.1): la seccion 8 conserva la mencion a `evaluation/report.md`,
    comportamiento del runner que no debe perderse al reescribir la seccion.
    """
    section = read_section(OPERATIONAL_GUIDE, GUIDE_SECTION_8_HEADING)
    require_token(
        section,
        TOKEN_REPORT,
        OPERATIONAL_GUIDE,
        "reporte generado por el runner",
    )


def test_evaluation_readme_keeps_command_and_gemini_key():
    """
    TRIANGULATE (5.2): `evaluation/README.md` conserva el comando unico
    `PYTHONPATH=App/Backend python -m evaluation.run_evaluation` y la
    configuracion de `GEMINI_API_KEY` como no-regresion.
    Spec: «MUST describir ese gate ... junto al comando único de corrida y a la
    configuración de GEMINI_API_KEY».
    """
    readme = read_doc(EVALUATION_README)
    require_token(
        readme,
        TOKEN_RUNNER_INVOCATION,
        EVALUATION_README,
        "comando unico de corrida",
    )
    require_token(
        readme,
        "GEMINI_API_KEY",
        EVALUATION_README,
        "configuracion de GEMINI_API_KEY",
    )


def test_guide_keeps_c43_tokens():
    """
    TRIANGULATE (5.3): la guia conserva los tokens de c-43 (`App/Backend/`,
    `UP_SKIP_COST_PREFLIGHT`, `docker compose up -d`) para evitar regresion
    cruzada.
    """
    guide = read_doc(OPERATIONAL_GUIDE)
    require_token(guide, TOKEN_CURRENT_PATH, OPERATIONAL_GUIDE, "ruta vigente (c-43)")
    require_token(
        guide,
        TOKEN_SKIP_COST_PREFLIGHT,
        OPERATIONAL_GUIDE,
        "bypass del preflight de costo (c-42)",
    )
    require_token(guide, TOKEN_MANUAL_UP, OPERATIONAL_GUIDE, "camino manual (c-42)")


def test_export_openapi_respects_existing_jwt_env(tmp_path: Path):
    """
    TRIANGULATE (5.4): con `JWT_SECRET_KEY` presente en el entorno y una salida
    distinta, el script sigue produciendo un OpenAPI 3.1 valido: el dummy no pisa
    el valor real del entorno.
    """
    process, output = run_export_script(
        tmp_path,
        extra_env={"JWT_SECRET_KEY": "real-env-secret-key"},
        strip_env=("DATABASE_URL", "GEMINI_API_KEY", "PSEUDONYMIZATION_ENCRYPTION_KEY"),
        output_name="openapi_with_env.json",
    )
    assert_script_succeeded(
        process, output, "con JWT_SECRET_KEY presente en el entorno"
    )


# ---------------------------------------------------------------------------
# Grupo 7 — Cierre de drift: invocacion del runner en como_cargar_datos_corpus.md
# ---------------------------------------------------------------------------


def test_corpus_procedure_runner_invocation_has_no_cd():
    """
    RED -> GREEN (7.1 / 7.2): `docs/como_cargar_datos_corpus.md` documenta la
    invocacion real del runner desde la raiz del repositorio y no presenta un
    `cd evaluation` en el bloque de invocacion del runner.
    El comentario «Desde la raiz del repositorio» y el `cd evaluation` se
    contradecian: tras el `cd`, `python -m evaluation.run_evaluation` no resuelve
    el paquete. El mismo `cd evaluation` es legitimo en los bloques de tests del
    framework (`evaluation/README.md`, guia §8.3) y no se controla aqui.
    """
    doc_text = read_doc(CORPUS_PROCEDURE_DOC)
    require_token(
        doc_text,
        TOKEN_RUNNER_INVOCATION,
        CORPUS_PROCEDURE_DOC,
        "invocacion real del runner",
    )
    runner_blocks = [
        block
        for block in read_fenced_blocks(doc_text)
        if TOKEN_RUNNER_INVOCATION in block
    ]
    assert runner_blocks, (
        f"{CORPUS_PROCEDURE_DOC} no expone la invocacion real del runner en un "
        "bloque de codigo"
    )
    for block in runner_blocks:
        require_absent_token(
            block,
            TOKEN_BROKEN_CD,
            CORPUS_PROCEDURE_DOC,
            "cd evaluation en la invocacion del runner",
        )
