"""Resume el registro de compilacion de la tesis (c-188, B7, design D5-A).

Lee `main.log`, `main.blg` y `main.pdf` y escribe un Markdown determinista
(`paper/compilacion.md`) con los conteos que el registro afirma: motor y version
de biber, paginas, errores fatales, referencias y citas indefinidas, etiquetas
duplicadas, `Overfull \\hbox` (cantidad y maximo en pt), lineas WARN/ERROR del
`.blg` y SHA-256 del PDF. Sin red, sin subprocesos y sin fecha del sistema:
mismas entradas, mismos bytes.

Uso, desde la raiz del repositorio:

    python -I docs/Tesis/Correcciones/resumir_registro_compilacion.py \\
        --log "docs/Tesis/v10 (IA)/paper/main.log" \\
        --blg "docs/Tesis/v10 (IA)/paper/main.blg" \\
        --pdf "docs/Tesis/v10 (IA)/paper/main.pdf" \\
        --fuente "arbol de trabajo sobre <hash corto>" \\
        --salida "docs/Tesis/v10 (IA)/paper/compilacion.md"
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

_RE_ERROR = re.compile(r"^!", re.M)
_RE_REF = re.compile(r"^LaTeX Warning: Reference `[^']*' on page \d+ undefined", re.M)
_RE_CITA = re.compile(r"^LaTeX Warning: Citation `[^']*' on page \d+ undefined", re.M)
_RE_DUP = re.compile(r"^LaTeX Warning: Label `[^']*' multiply defined", re.M)
_RE_OVERFULL = re.compile(r"^Overfull \\hbox \(([\d.]+)pt too wide\)", re.M)
_RE_PAGINAS = re.compile(r"Output written on \S+ \((\d+) pages?")
_RE_MOTOR = re.compile(
    r"^This is XeTeX, Version (\S+) \((TeX Live [^)]*)\)", re.M
)
_RE_BIBER = re.compile(r"This is Biber (\S+)")
_RE_WARN = re.compile(r"^\S*\s*\S+> WARN - ", re.M)
_RE_BLG_ERROR = re.compile(r"^\S*\s*\S+> ERROR - ", re.M)


def contar_errores(log):
    return len(_RE_ERROR.findall(log))


def contar_indefinidas(log):
    """Devuelve (referencias indefinidas, citas indefinidas)."""
    return len(_RE_REF.findall(log)), len(_RE_CITA.findall(log))


def contar_duplicadas(log):
    return len(_RE_DUP.findall(log))


def analizar_overfull(log):
    """Devuelve (cantidad de Overfull \\hbox, maximo en pt)."""
    valores = [float(v) for v in _RE_OVERFULL.findall(log)]
    return len(valores), (max(valores) if valores else 0.0)


def paginas(log):
    m = _RE_PAGINAS.search(log)
    return int(m.group(1)) if m else None


def version_motor(log):
    m = _RE_MOTOR.search(log)
    return f"XeTeX {m.group(1)} ({m.group(2)})" if m else "no registrado"


def version_biber(blg):
    m = _RE_BIBER.search(blg)
    return m.group(1) if m else "no registrada"


def contar_avisos_blg(blg):
    """Devuelve (lineas WARN, lineas ERROR) del .blg."""
    return len(_RE_WARN.findall(blg)), len(_RE_BLG_ERROR.findall(blg))


def sha256_bytes(datos):
    return hashlib.sha256(datos).hexdigest()


def resumir(log, blg, pdf_bytes, fuente):
    refs, citas = contar_indefinidas(log)
    n_over, max_over = analizar_overfull(log)
    warn, error = contar_avisos_blg(blg)
    return {
        "fuente": fuente,
        "motor": version_motor(log),
        "biber": version_biber(blg),
        "paginas": paginas(log),
        "errores": contar_errores(log),
        "referencias_indefinidas": refs,
        "citas_indefinidas": citas,
        "duplicadas": contar_duplicadas(log),
        "overfull": n_over,
        "overfull_max_pt": max_over,
        "blg_warn": warn,
        "blg_error": error,
        "sha256": sha256_bytes(pdf_bytes),
    }


def _pt(valor):
    return f"{valor:.1f}".replace(".", ",") + " pt"


def a_markdown(r):
    paginas_txt = "no registradas" if r["paginas"] is None else str(r["paginas"])
    filas = [
        ("Fuente compilada", r["fuente"]),
        ("Motor", r["motor"]),
        ("Biber", r["biber"]),
        ("Paginas", paginas_txt),
        ("Errores fatales", str(r["errores"])),
        ("Referencias indefinidas", str(r["referencias_indefinidas"])),
        ("Citas indefinidas", str(r["citas_indefinidas"])),
        ("Etiquetas duplicadas (multiply defined)", str(r["duplicadas"])),
        (
            "Overfull \\hbox (maximo)",
            f"{r['overfull']} ({_pt(r['overfull_max_pt'])})",
        ),
        ("Lineas WARN de biber", str(r["blg_warn"])),
        ("Lineas ERROR de biber", str(r["blg_error"])),
        ("SHA-256 de main.pdf", f"`{r['sha256']}`"),
    ]
    lineas = [
        "# Resumen del registro de compilacion",
        "",
        "Generado por `docs/Tesis/Correcciones/resumir_registro_compilacion.py` a partir de",
        "`main.log`, `main.blg` y `main.pdf`. No editar a mano.",
        "",
        "| Concepto | Valor |",
        "|---|---|",
    ]
    lineas += [f"| {k} | {v} |" for k, v in filas]
    return "\n".join(lineas) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--log", required=True)
    ap.add_argument("--blg", required=True)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--fuente", required=True)
    ap.add_argument("--salida", required=True)
    args = ap.parse_args(argv)
    try:
        log = Path(args.log).read_text(encoding="utf-8", errors="replace")
        blg = Path(args.blg).read_text(encoding="utf-8", errors="replace")
        pdf = Path(args.pdf).read_bytes()
    except OSError as exc:
        print(f"No se pudo leer una entrada: {exc}", file=sys.stderr)
        return 2
    texto = a_markdown(resumir(log, blg, pdf, args.fuente))
    Path(args.salida).write_bytes(texto.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
