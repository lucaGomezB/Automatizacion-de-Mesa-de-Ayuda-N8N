#!/usr/bin/env python3
"""Convierte las secciones LaTeX de la tesis v10 a un Markdown estructurado.

Determinista: no reinterpreta texto, solo traduce la notacion LaTeX mas comun a
Markdown. Preserva los valores numericos verbatim.
"""
import re
import sys
import pathlib
import subprocess

WORKING_VERSION = "v10"
FALLBACK_RELEASE = "v1.1.1"


def detect_release() -> str:
    """Release vigente: ultimo tag de git; si no hay repo o tag, usa el fallback."""
    try:
        out = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, check=True,
        ).stdout.strip()
        if out:
            return out
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        pass
    return FALLBACK_RELEASE

BASE = pathlib.Path("docs/Tesis/v10 (IA)/paper/sections")
# Orden de inclusion segun main.tex (11-antecedentes-legales va antes de 07-resultados)
ORDER = [
    "00-portada.tex",
    "00-resumen.tex",
    "00-glosario.tex",
    "01-introduccion.tex",
    "02-marco-teorico.tex",
    "03-estado-del-arte.tex",
    "04-marco-metodologico.tex",
    "05-arquitectura.tex",
    "06-implementacion.tex",
    "11-aspectos-legales.tex",
    "07-resultados.tex",
    "08-discusion.tex",
    "09-conclusiones.tex",
    "10-recomendaciones.tex",
    "12-anexos.tex",
]

SPECIAL = {
    r"\%": "%", r"\&": "&", r"\_": "_", r"\#": "#", r"\$": "$",
    r"\textperiodcentered": "·", r"\ldots": "…", r"\dots": "…",
    r"\textquotesingle": "'", r"\textquotedblleft": "«", r"\textquotedblright": "»",
    r"---": "—", r"--": "–", r"~": " ", r"\\,": " ", r"\\;": " ",
    r"\"a": "ä", r"\"o": "ö", r"\"u": "ü", r"\"e": "ë", r"\"i": "ï",
    r"\'a": "á", r"\'e": "é", r"\'i": "í", r"\'o": "ó", r"\'u": "ú",
    r"\textbackslash": "\\", r"\ \ ": " ",
}


def strip_comments(text: str) -> str:
    out = []
    for line in text.splitlines():
        # elimina comentarios (%) que no esten escapados
        res = ""
        i = 0
        while i < len(line):
            if line[i] == "\\" and i + 1 < len(line):
                res += line[i:i + 2]
                i += 2
                continue
            if line[i] == "%":
                break
            res += line[i]
            i += 1
        out.append(res)
    return "\n".join(out)


def convert_envs(text: str) -> str:
    # tabular -> markdown
    def tabular(m):
        body = m.group(2)
        # quitar \multicolumn{N}{spec}{ y \multirow{N}{width}{ (dejando el contenido)
        body = re.sub(r"\\multicolumn\{\d+\}\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}\{", "", body)
        body = re.sub(r"\\multirow\{\d+\}\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}\{", "", body)
        # reglas de tabla
        body = re.sub(r"\\(?:toprule|midrule|bottomrule|hline)\b", "", body)
        body = re.sub(r"\\cmidrule(?:\([^)]*\))?\{[^}]*\}", "", body)
        body = re.sub(r"\\cline\{[^}]*\}", "", body)
        rows = [r.strip() for r in re.split(r"\\\\", body) if r.strip()]
        md = []
        for idx, row in enumerate(rows):
            cells = [c.strip() for c in row.split("&")]
            md.append("| " + " | ".join(cells) + " |")
            if idx == 0:
                md.append("|" + "|".join([" --- "] * len(cells)) + "|")
        return "\n".join(md)

    text = re.sub(r"\\begin\{tabular\}(?:\[[^\]]*\])?\{((?:[^{}]|\{[^{}]*\})*)\}(.*?)\\end\{tabular\}", tabular, text, flags=re.S)

    # figure -> nota
    def figure(m):
        cap = re.search(r"\\caption\{(.+?)\}", m.group(1), flags=re.S)
        lab = re.search(r"\\label\{(.+?)\}", m.group(1))
        name = cap.group(1).strip() if cap else "figura"
        name = re.sub(r"\s+", " ", name)
        ref = f" (`{lab.group(1)}`)" if lab else ""
        return f"\n[Figura: {name}]{ref}\n"

    text = re.sub(r"\\begin\{figure\}(?:\[[^\]]*\])?(.*?)\\end\{figure\}", figure, text, flags=re.S)

    # table wrapper: keep only the tabular (already converted) + caption
    def tablewrap(m):
        body = m.group(1)
        cap = re.search(r"\\caption\{(.+?)\}", body, flags=re.S)
        capname = re.sub(r"\s+", " ", cap.group(1).strip()) if cap else ""
        body = re.sub(r"\\caption\{.+?\}", "", body, flags=re.S)
        body = re.sub(r"\\label\{[^}]*\}", "", body)
        header = f"\n**Tabla: {capname}**\n" if capname else "\n"
        return header + body

    text = re.sub(r"\\begin\{table\}(?:\[[^\]]*\])?(.*?)\\end\{table\}", tablewrap, text, flags=re.S)

    # itemize / enumerate
    text = text.replace(r"\begin{itemize}", "\n")
    text = text.replace(r"\end{itemize}", "\n")
    text = text.replace(r"\begin{enumerate}", "\n")
    text = text.replace(r"\end{enumerate}", "\n")
    text = text.replace(r"\begin{description}", "\n")
    text = text.replace(r"\end{description}", "\n")

    # equations
    text = re.sub(r"\\begin\{equation\*?\}(.*?)\\end\{equation\*?\}", lambda m: "\n    " + re.sub(r"\s+", " ", m.group(1).strip()) + "\n", text, flags=re.S)
    text = re.sub(r"\\\[(.*?)\\\]", lambda m: "\n    " + re.sub(r"\s+", " ", m.group(1).strip()) + "\n", text, flags=re.S)

    # center / small / other wrappers
    for env in ("center", "flushleft", "flushright", "small", "footnotesize", "quote",
                "verbatim", "minipage", "tabularx", "longtable", "abstract"):
        text = re.sub(r"\\begin\{%s\}(\[[^\]]*\})?" % env, "\n", text)
        text = re.sub(r"\\end\{%s\}" % env, "\n", text)
    return text


def convert_inline(text: str) -> str:
    # imagenes y saltos de linea propios de LaTeX
    text = re.sub(r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}", "", text)
    text = re.sub(r"\\\\\[[^\]]*\]", "\n", text)
    text = re.sub(r"\\\\", "\n", text)
    # llaves escapadas
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    # comandos de tamano/familia (no aportan texto)
    text = re.sub(
        r"\\(?:large|Large|LARGE|huge|Huge|small|footnotesize|scriptsize|tiny|"
        r"normalsize|itshape|bfseries|slshape|scshape|upshape|ttfamily|rmfamily|sffamily)\b",
        "", text)
    # headings sin numerar (resumen, glosario, anexos especiales)
    text = re.sub(r"\\section\*\{([^}]*)\}", lambda m: "\n\n## " + m.group(1).strip() + "\n", text)

    # headings
    text = re.sub(r"\\section\{(.+?)\}(\s*\\label\{[^}]*\})?", lambda m: "\n\n## " + m.group(1).strip() + "\n", text, flags=re.S)
    text = re.sub(r"\\subsection\{(.+?)\}(\s*\\label\{[^}]*\})?", lambda m: "\n\n### " + m.group(1).strip() + "\n", text, flags=re.S)
    text = re.sub(r"\\subsubsection\{(.+?)\}(\s*\\label\{[^}]*\})?", lambda m: "\n\n#### " + m.group(1).strip() + "\n", text, flags=re.S)
    text = re.sub(r"\\paragraph\{(.+?)\}", lambda m: "\n\n**" + m.group(1).strip() + "** ", text, flags=re.S)

    # title/author/maketitle leftovers
    text = re.sub(r"\\maketitle|\\thispagestyle\{[^}]*\}|\\newpage|\\clearpage|\\vspace\*?\{[^}]*\}", "\n", text)

    # inline formatting
    text = re.sub(r"\\textbf\{(.+?)\}", r"**\1**", text, flags=re.S)
    text = re.sub(r"\\textit\{(.+?)\}", r"*\1*", text, flags=re.S)
    text = re.sub(r"\\emph\{(.+?)\}", r"*\1*", text, flags=re.S)
    text = re.sub(r"\\texttt\{(.+?)\}", r"`\1`", text, flags=re.S)
    text = re.sub(r"\\textsc\{(.+?)\}", r"\1", text, flags=re.S)
    text = re.sub(r"\\underline\{(.+?)\}", r"\1", text, flags=re.S)
    text = re.sub(r"\\textsuperscript\{(.+?)\}", r"^\1", text, flags=re.S)

    # citations
    text = re.sub(r"\\parencite\{([^}]*)\}", lambda m: "[" + m.group(1).replace(",", ", ") + "]", text)
    text = re.sub(r"\\textcite\{([^}]*)\}", lambda m: "[" + m.group(1).replace(",", ", ") + "]", text)
    text = re.sub(r"\\cite\{([^}]*)\}", lambda m: "[" + m.group(1) + "]", text)
    text = re.sub(r"\\autoref\{([^}]*)\}", lambda m: "§`" + m.group(1) + "`", text)
    text = re.sub(r"\\ref\{([^}]*)\}", lambda m: "`" + m.group(1) + "`", text)
    text = re.sub(r"\\label\{[^}]*\}", "", text)
    text = re.sub(r"\\footnote\{(.+?)\}", r" (\1)", text, flags=re.S)
    text = re.sub(r"\\url\{(.+?)\}", r"\1", text)
    text = re.sub(r"\\ac\{([^}]*)\}", r"\1", text)

    # \item -> bullet (ninguno lleva numero explicito)
    text = re.sub(r"\\item\s*", "- ", text)

    # special chars
    for k, v in SPECIAL.items():
        text = text.replace(k, v)

    # remaining commands \cmd{...} -> keep inner; \cmd -> drop
    text = re.sub(r"\\[a-zA-Z]+", "", text)
    text = text.replace("{", "").replace("}", "")

    # collapse whitespace / blank lines
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text


def main():
    parts = []
    for name in ORDER:
        p = BASE / name
        raw = p.read_text(encoding="utf-8")
        t = strip_comments(raw)
        t = convert_envs(t)
        t = convert_inline(t)
        parts.append(t.strip())
    body = "\n\n".join(parts)
    body = re.sub(r"\n{3,}", "\n\n", body)
    release = detect_release()
    header = (
        f"# Tesis UTN-FRM 2026 - Tesis para agentes ({WORKING_VERSION} / {release})\n\n"
        "> Documento generado a partir de las fuentes LaTeX de `docs/Tesis/v10 (IA)/paper/sections/` "
        f"(version de trabajo {WORKING_VERSION}, release `{release}`). Render Markdown de referencia para agentes. "
        "Los valores numericos son verbatim de las fuentes.\n\n---\n\n"
    )
    sys.stdout.write(header + body + "\n")


if __name__ == "__main__":
    main()
