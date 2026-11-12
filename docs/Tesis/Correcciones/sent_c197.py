#!/usr/bin/env python3
"""Regla de conteo D1 de c-197 (solo lectura).

Cuenta oraciones y palabras de los archivos .tex de la tesis con una regla unica:
una oracion por signo de cierre (. ! ?), excluyendo comandos LaTeX, matematicas,
entornos de tabla/figura/listado y comentarios. Tambien cuenta "de modo que".

Uso:
    python3 sent_c197.py [ruta_sections]

Salida: por archivo, total de oraciones, oraciones de mas de 40 palabras,
oraciones de mas de 60 palabras y ocurrencias de "de modo que"; y un total global.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# Abreviaturas cuyo punto no cierra oracion. Se protegen antes de partir.
ABBREVIATIONS = [
    "et al.", "p. ej.", "e.g.", "i.e.", "cf.", "vs.", "etc.", "aprox.",
    "fig.", "tab.", "cap.", "sec.", "núm.", "num.", "art.", "vol.", "pp.", "p.",
    "Dr.", "Dra.", "Prof.", "Ing.", "Sr.", "Sra.", "Sres.", "Lic.", "Mg.",
    "máx.", "mín.", "leg.",
]
ABBREV_RE = re.compile(
    r"(?<![0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ])(?:"
    + "|".join(re.escape(a) for a in ABBREVIATIONS)
    + r")(?![0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ])"
)

# Entornos cuyo contenido no es prosa (tablas, figuras, listados, matematicas).
EXCLUDED_ENVIRONMENTS = [
    "table", "table*", "tabular", "tabular*", "tabularx", "longtable",
    "figure", "figure*", "verbatim", "lstlisting", "minted",
    "equation", "equation*", "align", "align*", "gather", "gather*",
    "multline", "multline*", "array", "matrix", "displaymath", "math",
]

ENV_BLOCK = re.compile(
    r"\\begin\{(" + "|".join(re.escape(e) for e in EXCLUDED_ENVIRONMENTS) + r")\}(?:\[[^\]]*\])?.*?\\end\{\1\}",
    re.DOTALL,
)

# Comandos de referencia/etiqueta: se eliminan por completo (no son prosa).
REF_COMMANDS = re.compile(
    r"\\(?:label|ref|autoref|pageref|cite|citep|citet|path|url|verb|footnote|"
    r"index|glossary|acrshort|acrlong|acrfull)\*?(?:\[[^\]]*\])?\{[^{}]*\}"
)
INLINE_VERB = re.compile(r"\\verb\*?(?P<delim>.)(?P<body>.*?)(?P=delim)")
MATH_INLINE = re.compile(r"\$[^$]*\$")
MATH_PAREN = re.compile(r"\\\(.*?\\\)", re.DOTALL)
MATH_BRACKET = re.compile(r"\\\[.*?\\\]", re.DOTALL)
COMMAND_WITH_ARG = re.compile(r"\\(?:[a-zA-Z@]+|.)\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?")
SPACES = re.compile(r"[ \t\r\n]+")
WORD = re.compile(r"\S")
NON_ALNUM = re.compile(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ]")


def strip_comments(text: str) -> str:
    out_lines = []
    for line in text.splitlines():
        i = 0
        while i < len(line):
            if line[i] == "%" and (i == 0 or line[i - 1] != "\\"):
                line = line[:i]
                break
            i += 1
        out_lines.append(line)
    return "\n".join(out_lines)


def clean(text: str) -> str:
    text = strip_comments(text)
    text = ENV_BLOCK.sub(" ", text)
    text = INLINE_VERB.sub(" ", text)
    text = MATH_PAREN.sub(" ", text)
    text = MATH_BRACKET.sub(" ", text)
    text = MATH_INLINE.sub(" ", text)
    text = REF_COMMANDS.sub(" ", text)
    # Conserva el texto de los argumentos de los comandos restantes.
    text = COMMAND_WITH_ARG.sub(lambda m: " " + " ".join(re.findall(r"\{([^{}]*)\}", m.group(0))) + " ", text)
    text = text.replace("~", " ").replace("{", " ").replace("}", " ")
    text = text.replace("\\", " ")
    return SPACES.sub(" ", text).strip()


def split_sentences(text: str) -> list[str]:
    protected = ABBREV_RE.sub(lambda m: m.group(0).replace(".", "@@ABBR@@"), text)
    # Una oracion por signo de cierre seguido de espacio o fin de texto.
    parts = re.split(r"(?<=[.!?])\s+", protected)
    restored = [p.replace("@@ABBR@@", ".").strip() for p in parts]
    return [p for p in restored if p]


def word_count(sentence: str) -> int:
    tokens = [t for t in sentence.split() if NON_ALNUM.sub("", t)]
    return len(tokens)


def measure_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    text = clean(raw)
    sentences = split_sentences(text)
    counts = [word_count(s) for s in sentences]
    return {
        "file": path.name,
        "sentences": len(sentences),
        "over40": sum(1 for c in counts if c > 40),
        "over60": sum(1 for c in counts if c > 60),
        "de_modo_que": len(re.findall(r"\bde modo que\b", text, flags=re.IGNORECASE)),
        "longest": max(counts) if counts else 0,
    }


def main() -> int:
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "docs/Tesis/v10 (IA)/paper/sections"
    )
    files = sorted(p for p in base.glob("*.tex") if p.name[:2].isdigit())
    if not files:
        print(f"No se encontraron .tex en {base}", file=sys.stderr)
        return 1

    rows = [measure_file(p) for p in files]
    print(f"# Regla D1 c-197 — {base}")
    print(f"{'Archivo':<28}{'Oraciones':>10}{'>40':>6}{'>60':>6}{'de modo que':>13}{'max':>6}")
    for r in rows:
        print(
            f"{r['file']:<28}{r['sentences']:>10}{r['over40']:>6}{r['over60']:>6}"
            f"{r['de_modo_que']:>13}{r['longest']:>6}"
        )
    total_s = sum(r["sentences"] for r in rows)
    total_40 = sum(r["over40"] for r in rows)
    total_60 = sum(r["over60"] for r in rows)
    total_dmq = sum(r["de_modo_que"] for r in rows)
    pct_40 = 100.0 * total_40 / total_s if total_s else 0.0
    print("-" * 69)
    print(
        f"{'TOTAL':<28}{total_s:>10}{total_40:>6}{total_60:>6}{total_dmq:>13}"
        f"{'':>6}"
    )
    print(f"Porcentaje de oraciones de mas de 40 palabras: {pct_40:.2f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
