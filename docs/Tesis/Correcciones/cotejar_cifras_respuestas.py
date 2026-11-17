"""Coteja las cifras de las respuestas al tribunal contra el ejemplar corregido (c-239).

Script de solo lectura (biblioteca estandar). Extrae las cifras numericas de
`docs/defensa/respuestas-tribunal.md` (enteros de dos o mas digitos, decimales
con coma, porcentajes, fracciones `a/b` y valores con signo), las normaliza y
verifica que cada una figure en el texto extraido del ejemplar corregido o en la
lista blanca versionada en la que cada entrada lleva su justificacion. Informa
ademas, como fallas, las cifras de una lista de valores retirados que aparezcan
fuera de una oracion de retiro y los restos de sintaxis LaTeX. El codigo de
salida es 0 solo si no hay fallas. No modifica ningun archivo.

Uso, desde la raiz del repositorio:

    python3 -I docs/Tesis/Correcciones/cotejar_cifras_respuestas.py \\
        --respuestas docs/defensa/respuestas-tribunal.md \\
        --ejemplar "docs/Tesis/v10 (IA)/tesis_completa_extraida.txt" \\
        --lista-blanca docs/defensa/cotejo-lista-blanca.tsv
"""
import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Cifras de la validacion fuera de muestra retirada: si aparecen fuera de una
# oracion que declare el retiro o la superacion, el cotejo las informa.
RETIRADAS = frozenset(
    {"0,6893", "142/206", "0,7489", "0,7024", "-18,5", "-43,9", "+30,6", "206", "56"}
)

# Contextos que no son cifras de resultado: rutas/identificadores entre comillas
# invertidas, remisiones de seccion, encabezados Qn/Pn, aliases e identificadores
# (E1, O2, N-01, c-235, R001, I151, ...).
BACKTICK_RE = re.compile(r"`[^`]*`")
SECCION_RE = re.compile(r"(?:§|subsecci[oó]n|secci[oó]n)\s*\d+(?:\.\d+)*", re.IGNORECASE)
QPN_RE = re.compile(r"(?<![0-9A-Za-z])[QP]\d+(?![0-9A-Za-z])")
ID_RE = re.compile(r"(?<![0-9A-Za-z])[A-Za-z]{1,4}-?\d{1,4}(?![0-9A-Za-z])")

# Restos de sintaxis LaTeX que no deben quedar en el documento.
LATEX_RES = (
    re.compile(r"~\\%"),
    re.compile(r"\{,\}"),
    re.compile(r"\\texttt"),
    re.compile(r"\\ref"),
)

# Un token numerico: fraccion, decimal con coma, millar con punto, o entero de
# dos o mas digitos; con signo opcional.
TOKEN_RE = re.compile(
    r"(?<![0-9A-Za-z.,])(?:"
    r"[+\-]?\d+/\d+"
    r"|[+\-]?\d+(?:,\d+)+"
    r"|[+\-]?\d{1,3}(?:\.\d{3})+"
    r"|[+\-]?\d{2,}"
    r")(?![0-9A-Za-z])"
)


@dataclass(frozen=True)
class Cifra:
    crudo: str
    normalizado: str


@dataclass(frozen=True)
class Falla:
    tipo: str
    cifra: str
    linea: int
    mensaje: str


def normalizar_cifra(valor):
    """Normaliza una cifra: `{,}` -> `,`, `−` -> `-`, sin espacios ni `%` ni millar."""
    valor = valor.replace("{,}", ",").replace("\u2212", "-")
    valor = valor.replace("~", "").replace("\\", "").replace("%", "")
    valor = re.sub(r"[\s\u00a0\u202f\u2009]", "", valor)
    valor = valor.replace(".", "")
    return valor


def _normalizar_texto(texto):
    return texto.replace("{,}", ",").replace("\u2212", "-")


def _enmascarar(texto):
    for rx in (BACKTICK_RE, SECCION_RE, QPN_RE, ID_RE):
        texto = rx.sub(lambda m: " " * len(m.group(0)), texto)
    return texto


def _iter_cifras(texto):
    """Itera (Cifra, inicio, fin) sobre el texto con los contextos excluidos."""
    enmascarado = _enmascarar(_normalizar_texto(texto))
    for m in TOKEN_RE.finditer(enmascarado):
        yield Cifra(m.group(0), normalizar_cifra(m.group(0))), m.start(), m.end()


def extraer_cifras(texto):
    """Devuelve la lista de Cifra del texto, con los contextos excluidos."""
    return [c for c, _, _ in _iter_cifras(texto)]


def _linea_de(texto, pos):
    return texto.count("\n", 0, pos) + 1


def _oracion(texto, pos):
    """Fragmento de oracion que contiene la posicion (para la regla de retiro)."""
    ini = 0
    for corte in (".", "\n", "!", "?"):
        i = texto.rfind(corte, 0, pos)
        ini = max(ini, i + 1)
    fin = len(texto)
    for corte in (".", "!", "?"):
        i = texto.find(corte, pos)
        if i != -1:
            fin = min(fin, i + 1)
    return texto[ini:fin]


def leer_lista_blanca(ruta):
    """Lee un TSV `cifra<TAB>justificacion` y devuelve el conjunto de cifras."""
    cifras = set()
    for linea in Path(ruta).read_text(encoding="utf-8").splitlines():
        if not linea.strip():
            continue
        celda = linea.split("\t")[0].strip()
        if celda.lower() == "cifra":
            continue
        if celda:
            cifras.add(normalizar_cifra(celda))
    return cifras


def cotejar(respuestas, ejemplar, lista_blanca=()):
    """Devuelve la lista de Falla del cotejo (vacia si todo pasa)."""
    blanco = {normalizar_cifra(c) for c in lista_blanca}
    cifras_ejemplar = {c.normalizado for c in extraer_cifras(ejemplar)}
    fallas = []

    for rx in LATEX_RES:
        for m in rx.finditer(respuestas):
            linea = _linea_de(respuestas, m.start())
            fallas.append(
                Falla("latex", m.group(0), linea, f"resto de LaTeX {m.group(0)!r} en la linea {linea}")
            )

    for cifra, inicio, _ in _iter_cifras(respuestas):
        linea = _linea_de(respuestas, inicio)
        if cifra.normalizado in RETIRADAS:
            if not re.search(r"retir|super", _oracion(respuestas, inicio), re.IGNORECASE):
                fallas.append(
                    Falla(
                        "retirada",
                        cifra.normalizado,
                        linea,
                        f"valor retirado {cifra.normalizado} en la linea {linea} sin declarar el retiro",
                    )
                )
            continue
        if cifra.normalizado in blanco:
            continue
        if cifra.normalizado not in cifras_ejemplar:
            fallas.append(
                Falla(
                    "ausente",
                    cifra.normalizado,
                    linea,
                    f"cifra {cifra.normalizado} (linea {linea}) ausente del ejemplar y de la lista blanca",
                )
            )

    return fallas


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--respuestas", required=True)
    ap.add_argument("--ejemplar", required=True)
    ap.add_argument("--lista-blanca", default=None)
    args = ap.parse_args(argv)

    respuestas = Path(args.respuestas).read_text(encoding="utf-8")
    ejemplar = Path(args.ejemplar).read_text(encoding="utf-8")
    blanco = leer_lista_blanca(args.lista_blanca) if args.lista_blanca else set()

    fallas = cotejar(respuestas, ejemplar, blanco)
    for falla in fallas:
        print(f"FALLA [{falla.tipo}] {falla.mensaje}")
    print(f"Cifras extraidas del documento: {len(extraer_cifras(respuestas))}; fallas: {len(fallas)}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
