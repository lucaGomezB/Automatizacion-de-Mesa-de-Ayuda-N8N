"""Genera una copia PSEUDONIMIZADA del corpus de la tesis (Ley 25.326).

Proposito
---------
Lee el CSV del corpus (``data/Corpus Tesis - Hoja 1.csv``), enmascara la PII
del UNICO campo de texto libre (``Descripcion``) reutilizando el pseudonimizador
de produccion (``app.utils.pseudonymizer.pseudonymize``) y escribe una copia
separada lista para publicar. NUNCA sobrescribe la entrada original.

Privacidad
----------
Este modulo NUNCA imprime ni loguea una descripcion de caso. Solo emite conteos
agregados por categoria de reemplazo y el resultado del escaneo residual. La
verificacion residual es la red de seguridad: si el enmascarado deja emails o
telefonos, el proceso termina con codigo distinto de cero.

Dependencias
------------
Solo CSV + stdlib. ``openpyxl`` NO es necesario (el XLSX no se toca). El backend
se agrega a ``sys.path`` de forma relativa a este archivo para importar el
pseudonimizador de produccion, que es la unica fuente de verdad de los patrones.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

# ── Import del pseudonimizador de produccion ────────────────────────────────


def _ensure_backend_on_path() -> Path:
    """Agrega ``App/Backend`` al ``sys.path`` desde la ubicacion de este archivo.

    El script vive en ``scripts/corpus_ingest/``, por lo que la raiz del repo es
    ``parents[2]`` y el backend ``<repo>/App/Backend``.
    """
    backend = Path(__file__).resolve().parents[2] / "App" / "Backend"
    backend_str = str(backend)
    if backend_str not in sys.path:
        sys.path.insert(0, backend_str)
    return backend


_ensure_backend_on_path()

from app.utils.pseudonymizer import pseudonymize  # noqa: E402


# ── Contrato del corpus ─────────────────────────────────────────────────────

DEFAULT_CSV = "data/Corpus Tesis - Hoja 1.csv"
DEFAULT_OUT = "data/Corpus Tesis - Hoja 1 (pseudonimizado).csv"

HEADER_ID = "ID"
HEADER_DESCRIPCION = "Descripcion"

_ENV_INTERNAL_DOMAINS = "PSEUDONYMIZATION_INTERNAL_DOMAINS"

_CATEGORIAS = ("email", "telefono", "host", "persona")


# ── Escaneo residual (independiente del enmascarado) ────────────────────────

_RE_RESIDUAL_EMAIL = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_RE_RESIDUAL_PHONE = re.compile(r"\+?\d[\d\s.\-()]{6,}\d")

# Un telefono argentino tiene >= 9 digitos (area + local). Exigir 9 evita
# falsos positivos sobre rangos de anios ("2015-2022") o codigos cortos.
_MIN_RESIDUAL_PHONE_DIGITS = 9


def count_residual_pii(text: str) -> dict[str, int]:
    """Cuenta emails y telefonos que aun quedan visibles en ``text``.

    Detector independiente del pseudonimizador (verificacion post-enmascarado).
    No cuenta rangos de anios ni secuencias de menos de 9 digitos.
    """
    emails = len(_RE_RESIDUAL_EMAIL.findall(text))
    phones = 0
    for match in _RE_RESIDUAL_PHONE.finditer(text):
        if sum(c.isdigit() for c in match.group(0)) >= _MIN_RESIDUAL_PHONE_DIGITS:
            phones += 1
    return {"email": emails, "telefono": phones}


# ── Helpers puros ───────────────────────────────────────────────────────────


def _norm(value: object) -> str:
    if value is None:
        return ""
    return str(value).strip().lower()


def find_header_index(rows: Sequence[Sequence[str]]) -> int:
    """Indice de la fila de encabezados (primera con ``ID`` y ``Descripcion``)."""
    for idx, row in enumerate(rows):
        normalized = {_norm(cell) for cell in row}
        if HEADER_ID.lower() in normalized and HEADER_DESCRIPCION.lower() in normalized:
            return idx
    raise ValueError("No se encontro la fila de encabezados (ID/Descripcion) en el CSV.")


def column_index(header: Sequence[str], name: str) -> int:
    target = _norm(name)
    for idx, cell in enumerate(header):
        if _norm(cell) == target:
            return idx
    raise ValueError(f"Columna requerida ausente en el encabezado: {name!r}")


def parse_internal_domains(raw: str | None) -> list[str]:
    """Parsea dominios internos desde JSON (estilo pydantic) o lista separada por comas."""
    if raw is None:
        return []
    text = raw.strip()
    if not text:
        return []
    if text.startswith("["):
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            parsed = None
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    return [part.strip() for part in text.split(",") if part.strip()]


def _default_internal_domains() -> list[str]:
    """Deriva los dominios internos igual que produccion: variable de entorno."""
    return parse_internal_domains(os.environ.get(_ENV_INTERNAL_DOMAINS))


# ── Resultado ───────────────────────────────────────────────────────────────


@dataclass
class PseudonymizeOutcome:
    """Filas enmascaradas + conteos agregados (sin PII)."""

    rows: list[list[str]]
    conteos: dict[str, int] = field(default_factory=dict)
    casos: int = 0


# ── Enmascarado ─────────────────────────────────────────────────────────────


def pseudonymize_rows(
    rows: Sequence[Sequence[str]], internal_domains: list[str]
) -> PseudonymizeOutcome:
    """Enmascara solo la columna ``Descripcion``; el resto queda intacto.

    Preserva la fila de titulo, el encabezado y cada fila/columna original. Solo
    se modifican las celdas de ``Descripcion``. Los conteos se agregan por
    categoria (email/telefono/host/persona), sin exponer texto de caso.
    """
    copied: list[list[str]] = [list(row) for row in rows]
    header_idx = find_header_index(copied)
    desc_col = column_index(copied[header_idx], HEADER_DESCRIPCION)

    conteos = {categoria: 0 for categoria in _CATEGORIAS}
    casos = 0
    for row in copied[header_idx + 1 :]:
        if len(row) <= desc_col:
            continue
        result = pseudonymize(row[desc_col], internal_domains)
        row[desc_col] = result.texto
        for categoria, cantidad in result.conteos.items():
            conteos[categoria] = conteos.get(categoria, 0) + cantidad
        casos += 1

    return PseudonymizeOutcome(rows=copied, conteos=conteos, casos=casos)


def _residual_totals(rows: Sequence[Sequence[str]]) -> dict[str, int]:
    """Suma PII residual en la columna ``Descripcion`` de las filas dadas."""
    header_idx = find_header_index(rows)
    desc_col = column_index(rows[header_idx], HEADER_DESCRIPCION)
    totals = {"email": 0, "telefono": 0}
    for row in rows[header_idx + 1 :]:
        if len(row) <= desc_col:
            continue
        found = count_residual_pii(row[desc_col])
        totals["email"] += found["email"]
        totals["telefono"] += found["telefono"]
    return totals


# ── I/O ─────────────────────────────────────────────────────────────────────


def read_rows(path: str | Path) -> list[list[str]]:
    with open(path, encoding="utf-8", newline="") as fh:
        return list(csv.reader(fh))


def write_rows(path: str | Path, rows: Sequence[Sequence[str]]) -> None:
    """Escribe CSV preservando estilo del corpus: CRLF y quoting minimal."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with open(target, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\r\n", quoting=csv.QUOTE_MINIMAL)
        writer.writerows(rows)


# ── CLI ─────────────────────────────────────────────────────────────────────


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Genera una copia PSEUDONIMIZADA del corpus de la tesis. Enmascara "
            "solo la columna Descripcion con el pseudonimizador de produccion y "
            "verifica que no quede PII residual. Nunca imprime descripciones."
        )
    )
    parser.add_argument("--csv", default=DEFAULT_CSV, help="CSV de entrada (crudo).")
    parser.add_argument("--out", default=DEFAULT_OUT, help="CSV de salida pseudonimizado.")
    parser.add_argument(
        "--internal-domains",
        default=None,
        help=(
            "Dominios corporativos a enmascarar como [HOST], separados por comas "
            "(o lista JSON). Default: variable de entorno "
            f"{_ENV_INTERNAL_DOMAINS} (como produccion)."
        ),
    )
    parser.add_argument("--dry-run", action="store_true", help="No escribe ningun archivo.")
    return parser.parse_args(argv)


def run(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    csv_path = Path(args.csv)
    out_path = Path(args.out)

    if csv_path.resolve() == out_path.resolve():
        print(
            "ERROR: --out no puede ser igual a --csv (no se sobrescribe la entrada).",
            file=sys.stderr,
        )
        return 2

    rows = read_rows(csv_path)
    internal_domains = (
        parse_internal_domains(args.internal_domains)
        if args.internal_domains is not None
        else _default_internal_domains()
    )

    outcome = pseudonymize_rows(rows, internal_domains)
    residual = _residual_totals(outcome.rows)

    print(f"Casos procesados: {outcome.casos}")
    print("Reemplazos por categoria (agregado, sin texto de caso):")
    for categoria in _CATEGORIAS:
        print(f"  {categoria}: {outcome.conteos.get(categoria, 0)}")
    print("PII residual en la salida:")
    print(f"  email: {residual['email']}")
    print(f"  telefono: {residual['telefono']}")

    if args.dry_run:
        print("DRY-RUN: no se escribio ningun archivo.")
    else:
        write_rows(out_path, outcome.rows)
        print(f"Escrito: {out_path}")

    if residual["email"] or residual["telefono"]:
        print(
            "ERROR: se detecto PII residual (email/telefono) en la salida. "
            "No publicar hasta resolverlo.",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
