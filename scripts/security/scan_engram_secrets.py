#!/usr/bin/env python3
"""Escáner de secretos para la memoria de Engram.

La carpeta `.engram/` se versiona en un repositorio PÚBLICO y es evidencia para
la auditoría de la tesis. `engram sync` escribe los chunks como
`.engram/chunks/*.jsonl.gz`, y cada chunk es un único objeto JSON en una sola
línea. El hook `.githooks/pre-commit` no inspecciona archivos `.gz`, por lo que
una credencial podría publicarse sin ser detectada.

Este script cierra ese hueco: recorre los paths indicados, descomprime los
`.gz` en memoria y busca patrones de credenciales sobre el texto completo,
match por match. La allowlist se evalúa contra una ventana chica alrededor de
cada match, de modo que la palabra "example" en otra parte de la misma línea no
suprime un secreto real que esté lejos de ella.

Uso:
    python3 scripts/security/scan_engram_secrets.py [PATH ...]

Salida:
    <path> [<pattern_name>] <redacted>     (una línea por hallazgo)
    Total: <n> hallazgo(s)

Exit codes:
    0 = limpio, 1 = hallazgos, 2 = error de uso o de I/O.

Restricción de seguridad: NUNCA se imprime el valor completo del secreto. El
campo redactado conserva solo los primeros 4 caracteres seguidos de `***`.
"""

from __future__ import annotations

import argparse
import gzip
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

# ---------------------------------------------------------------------------
# Patrones
# ---------------------------------------------------------------------------
# Cada entry es (nombre, expresión regular, flags). Las banderas IGNORECASE se
# aplican a los patrones marcados como (i) en la especificación.
_PATTERN_DEFS: tuple[tuple[str, str, int], ...] = (
    ("google_api_key", r"AIza[0-9A-Za-z_\-]{10,}", 0),
    ("google_oauth", r"AQ\.[0-9A-Za-z_\-]{30,}", 0),
    ("private_key_pem", r"-----BEGIN [A-Z ]*PRIVATE KEY-----", 0),
    (
        "assignment_secret",
        r"""(api[_-]?key|apikey|secret|token|passwd|password|encryption[_-]?key)"""
        r"""["']?\s*[:=]\s*["']?[A-Za-z0-9+/_.=-]{20,}""",
        re.IGNORECASE,
    ),
    ("twilio", r"(AC|SK)[0-9a-fA-F]{32}", 0),
    ("jwt", r"eyJ[A-Za-z0-9_\-]{10,}\.eyJ[A-Za-z0-9_\-]{10,}", 0),
    ("fernet_key", r"[A-Za-z0-9_\-]{43}=", 0),
    ("ngrok", r"2[0-9A-Za-z]{20,}_[0-9A-Za-z]{20,}", 0),
    ("aws_key", r"AKIA[0-9A-Z]{16}", 0),
    ("github_pat", r"gh[ps]_[A-Za-z0-9]{36,}", 0),
    ("slack", r"xox[baprs]-[A-Za-z0-9-]{10,}", 0),
    ("stripe", r"sk_live_[A-Za-z0-9]{20,}", 0),
    ("conn_string_creds", r"[a-z][a-z0-9+.\-]*://[^/\s:@]+:[^/\s:@]+@", 0),
    (
        "default_credentials",
        r"\badmin/admin123\b|\badmin/admin\b|\bmesa:mesa\b|\bmesa_local_dev\b|\bn8n_local_dev\b",
        re.IGNORECASE,
    ),
)

# Nombres en orden de declaración (expuestos para tests y diagnóstico).
PATTERN_NAMES: tuple[str, ...] = tuple(name for name, _regex, _flags in _PATTERN_DEFS)

_COMPILED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(regex, flags)) for name, regex, flags in _PATTERN_DEFS
)

# Tokens que desactivan un match cuando aparecen en su ventana de contexto
# (case-insensitive). Cubren placeholders, marcadores de redacción, valores de
# CI y hashes de lockfiles.
ALLOWLIST: tuple[str, ...] = (
    "gitleaks:allow",
    "your-",
    "your_",
    "example",
    "placeholder",
    "changeme",
    "replace_with_",
    "[redactado]",
    "[clave-de-prueba]",
    "ci-dummy",
    "dummy",
    "dry-run-dummy",
    "mesa_ci_local",
    "integrity",
    "sha256-",
    "sha384-",
    "sha512-",
)

# Cantidad de caracteres de contexto (antes y después del match) donde se busca
# un token de allowlist.
_CONTEXT_WINDOW = 40


@dataclass(frozen=True)
class Finding:
    """Un hallazgo: dónde, qué patrón y el valor ya redactado."""

    source: str
    pattern_name: str
    redacted: str


# Referencia a código: ruta de atributos punteada (p.ej. `settings.gemini_api_key`).
# Se usa SOLO para excluir el patrón `assignment_secret`: `settings.gemini_api_key`,
# `settings.n8n_webhook_secret` y similares son referencias a atributos del código,
# no credenciales literales; un secreto literal no tiene forma de identificador
# punteado. No es una allowlist genérica ni relaja ningún otro patrón.
_CODE_REFERENCE_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)+$")


def _redact(value: str) -> str:
    """Conserva solo los primeros 4 caracteres del valor y tapa el resto."""
    return value[:4] + "***"


def _assignment_value(matched: str) -> str:
    """Extrae el valor asignado de un match de `assignment_secret`.

    El match tiene la forma `<clave><sep><valor>`; el separador es el primer `:`
    o `=` (la clave no contiene ninguno). Se recortan espacios y comillas.
    """
    parts = re.split(r"[:=]", matched, maxsplit=1)
    value = parts[1] if len(parts) > 1 else ""
    return value.strip().strip("\"'")


def _is_allowlisted(text: str, start: int, end: int) -> bool:
    """Evalúa la allowlist contra la ventana de contexto alrededor del match."""
    lowered = text[max(0, start - _CONTEXT_WINDOW) : end + _CONTEXT_WINDOW].lower()
    return any(token in lowered for token in ALLOWLIST)


def find_secrets(text: str, source: str) -> list[Finding]:
    """Busca secretos en `text` match por match y devuelve los hallazgos.

    La allowlist se evalúa por match (no por línea) para que un token lejano
    dentro de la misma línea no oculte un secreto real. Además, para
    `assignment_secret` se descartan las referencias a código (rutas de
    atributos punteadas), que no son credenciales literales.
    """
    findings: list[Finding] = []
    for name, regex in _COMPILED:
        for match in regex.finditer(text):
            if _is_allowlisted(text, match.start(), match.end()):
                continue
            if name == "assignment_secret" and _CODE_REFERENCE_RE.match(
                _assignment_value(match.group(0))
            ):
                continue
            findings.append(Finding(source, name, _redact(match.group(0))))
    return findings


def _decode(raw: bytes) -> str:
    return raw.decode("utf-8", errors="replace")


def scan_file(path: Path) -> list[Finding]:
    """Lee (y descomprime si es `.gz`) un archivo y devuelve sus hallazgos."""
    raw = path.read_bytes()
    if path.suffix == ".gz" or path.name.endswith(".gz"):
        raw = gzip.decompress(raw)
    return find_secrets(_decode(raw), str(path))


def _iter_files(paths: Sequence[str]) -> Iterable[Path]:
    """Expande cada path a archivos regulares, de forma determinista."""
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise FileNotFoundError(f"no existe el path: {path}")
        if path.is_dir():
            yield from sorted(p for p in path.rglob("*") if p.is_file())
        elif path.is_file():
            yield path
        else:
            raise OSError(f"path no soportado: {path}")


def scan_paths(paths: Sequence[str]) -> list[Finding]:
    """Recorre los paths y acumula los hallazgos de todos sus archivos."""
    findings: list[Finding] = []
    for path in _iter_files(paths):
        findings.extend(scan_file(path))
    return findings


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada CLI. Devuelve el exit code (0/1/2)."""
    parser = argparse.ArgumentParser(
        prog="scan_engram_secrets.py",
        description=(
            "Escanea la memoria de Engram (.engram) en busca de credenciales "
            "antes de publicarla en el repositorio."
        ),
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Paths a escanear (default: .engram).",
    )
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse ya imprimió el mensaje de uso
        code = exc.code
        return code if isinstance(code, int) else 2

    paths = args.paths or [".engram"]

    try:
        findings = scan_paths(paths)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    for finding in findings:
        print(f"{finding.source} [{finding.pattern_name}] {finding.redacted}")

    print(f"Total: {len(findings)} hallazgo(s)")

    if findings:
        print(
            "Se detectaron posibles secretos. Saneá los valores antes de "
            "commitear la memoria de Engram.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
