"""Verifica las matrices de trazabilidad de los dictamenes v10 (c-141, c-188).

Recorre TODA tabla de 7 columnas con encabezado "Fragmento verificable" de
dictamen-correcciones.md, en cualquier seccion `## ` (dictamenes del 22-10, del
28-10 y del 8-11). Para cada fila comprueba que el fragmento verificable
aparece en el archivo citado y que el \\label ancla existe en el. Si el
fragmento esta en otra linea que la citada, la fila pasa con el aviso
"desplazada N -> M" (las anclas de linea son orientativas); con --estricto la
linea exacta es obligatoria. Las filas cuyo estado empieza con PENDIENTE o
SUPERADA (esta ultima debe nombrar el change que reescribio el parrafo, por
ejemplo "SUPERADA por c-187") se omiten.

Uso, desde la raiz del repositorio:

    python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py
    python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py --estricto
    python -I docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py --rev v1.2.12

Toda seccion `## Dictamen ...` cuyo titulo nombre un change c-NNN con NNN >= 190 debe
tener al menos una fila de matriz; si no, cuenta como falla ("seccion sin matriz").

Con --rev lee los archivos con `git show REV:ruta` (el arbol etiquetado); sin
el, lee el arbol de trabajo. Codigo de salida 0 si todas las filas pasan.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

ENCABEZADO = "Fragmento verificable"
RAIZ = Path(__file__).resolve().parents[3]
REGISTRO = Path(__file__).resolve().parent / "dictamen-correcciones.md"
BASE_TESIS = "docs/Tesis/v10 (IA)/paper/"


def _celda(texto):
    return texto.strip().strip("`").strip()


def resolver_ruta(archivo):
    """Un nombre suelto (sin directorio) es un archivo de `paper/sections/`."""
    if "/" in archivo:
        return archivo
    return BASE_TESIS + "sections/" + archivo


def parsear_matriz(texto):
    """Devuelve las filas de toda matriz con "Fragmento verificable" como dicts."""
    seccion = ""
    en_matriz = False
    filas = []
    for linea in texto.splitlines():
        linea = linea.rstrip("\r")
        if linea.startswith("## "):
            seccion = linea[3:].strip()
            en_matriz = False
            continue
        if not linea.startswith("|"):
            en_matriz = False  # una linea que no es de tabla cierra la tabla
            continue
        celdas = linea.strip().strip("|").split("|")
        if ENCABEZADO in linea and len(celdas) == 7:
            en_matriz = True
            continue
        if not en_matriz:
            continue
        if len(celdas) != 7:
            continue
        if set(celdas[0].strip()) <= {"-"}:
            continue
        archivo, _, numero = _celda(celdas[3]).rpartition(":")
        filas.append(
            {
                "seccion": seccion,
                "rec": _celda(celdas[0]),
                "change": _celda(celdas[2]),
                "archivo": archivo,
                "linea": int(numero) if numero.isdigit() else 0,
                "ancla": _celda(celdas[4]),
                "fragmento": _celda(celdas[5]),
                "estado": _celda(celdas[6]),
            }
        )
    return filas


def secciones_sin_matriz(texto, desde=190):
    """Titulos `## Dictamen ...` con un change `c-NNN` >= `desde` y sin ninguna fila de matriz.

    El change es el ULTIMO `c-NNN` del titulo. Detecta un ciclo de correcciones que no se
    trazo (c-195, dictamen del 9-11 sobre v1.2.16). Las secciones anteriores a `desde`
    y las de titulo sin change no se cuentan.
    """
    con_matriz = {f["seccion"] for f in parsear_matriz(texto)}
    faltantes = []
    for linea in texto.splitlines():
        if not linea.startswith("## Dictamen"):
            continue
        titulo = linea[3:].strip()
        cambios = re.findall(r"\bc-(\d+)\b", titulo)
        if cambios and int(cambios[-1]) >= desde and titulo not in con_matriz:
            faltantes.append(titulo)
    return faltantes


def verificar_fila(fila, leer, estricto=False):
    """Verifica una fila; `leer(ruta)` devuelve la lista de lineas del archivo."""
    estado = fila["estado"].upper()
    if estado.startswith("PENDIENTE"):
        return True, f"{fila['rec']}: omitida ({fila['estado'][:40]})"
    if estado.startswith("SUPERADA"):
        if not re.search(r"\bc-\d+\b", fila["estado"]):
            return False, f"{fila['rec']}: SUPERADA debe nombrar el change (c-NNN)"
        return True, f"{fila['rec']}: omitida ({fila['estado'][:40]})"
    lineas = leer(fila["archivo"])
    n = fila["linea"]
    exacta = 1 <= n <= len(lineas) and fila["fragmento"] in lineas[n - 1]
    aviso = ""
    if not exacta:
        real = reubicar_fila(fila, leer)
        if real is None:
            return False, (
                f"{fila['rec']}: el fragmento \"{fila['fragmento']}\" no esta en {fila['archivo']}"
            )
        if estricto:
            return False, (
                f"{fila['rec']}: linea {n} sin el fragmento en {fila['archivo']} "
                f"(esta en la {real}; --estricto)"
            )
        aviso = f" desplazada {n} -> {real}"
        n = real
    ancla = fila["ancla"]
    if ancla not in ("", "-"):
        if not any("\\label{" + ancla + "}" in l for l in lineas):
            return False, f"{fila['rec']}: el ancla {ancla} no existe en {fila['archivo']}"
    return True, f"{fila['rec']}: ok{aviso} ({fila['archivo']}:{n})"


def reubicar_fila(fila, leer):
    """Primera linea del archivo que contiene el fragmento, o None si no hay."""
    for i, linea in enumerate(leer(fila["archivo"]), 1):
        if fila["fragmento"] in linea:
            return i
    return None


def reemplazar_linea(texto, archivo, vieja, nueva):
    """Cambia `archivo:vieja` por `archivo:nueva` en el texto del registro."""
    return texto.replace(f"`{archivo}:{vieja}`", f"`{archivo}:{nueva}`")


def resumen_por_seccion(resultados):
    """`resultados`: lista de (seccion, ok, mensaje). Devuelve conteos por seccion."""
    r = {}
    for seccion, ok, msg in resultados:
        c = r.setdefault(seccion, {"filas": 0, "avisos": 0, "fallas": 0})
        c["filas"] += 1
        c["avisos"] += 1 if "desplazada" in msg else 0
        c["fallas"] += 0 if ok else 1
    return r


def formatear_resumen(resumen):
    return "\n".join(
        f"[{s}] filas: {c['filas']}; avisos: {c['avisos']}; fallas: {c['fallas']}"
        for s, c in resumen.items()
    )


def _lector(rev):
    def leer(ruta):
        ruta = resolver_ruta(ruta)
        if rev:
            salida = subprocess.run(
                ["git", "show", f"{rev}:{ruta}"], cwd=RAIZ, capture_output=True, check=True
            ).stdout.decode("utf-8")
        else:
            salida = (RAIZ / ruta).read_text(encoding="utf-8")
        return salida.replace("\r\n", "\n").split("\n")

    return leer


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--rev", help="revision git (por ejemplo v1.2.0); por defecto el arbol de trabajo")
    ap.add_argument(
        "--reubicar",
        action="store_true",
        help="reescribe en el registro la linea de las filas cuyo fragmento se desplazo (solo arbol de trabajo)",
    )
    ap.add_argument(
        "--estricto",
        action="store_true",
        help="exige que el fragmento este en la linea citada (sin avisos de desplazamiento)",
    )
    args = ap.parse_args(argv)
    original = REGISTRO.read_bytes().decode("utf-8")
    texto = original
    filas = parsear_matriz(texto)
    if not filas:
        print("No se encontro ninguna matriz con 'Fragmento verificable' en el registro.")
        return 2
    leer = _lector(args.rev)
    fallas = 0
    resultados = []
    for fila in filas:
        try:
            ok, msg = verificar_fila(fila, leer, estricto=args.estricto)
            if args.reubicar and not args.rev:
                nueva = None if ok and "desplazada" not in msg else reubicar_fila(fila, leer)
                if nueva is not None and nueva != fila["linea"]:
                    texto = reemplazar_linea(texto, fila["archivo"], fila["linea"], nueva)
                    ok, msg = True, f"{fila['rec']}: reubicada {fila['linea']} -> {nueva}"
        except (OSError, subprocess.CalledProcessError) as exc:
            ok, msg = False, f"{fila['rec']}: no se pudo leer {fila['archivo']} ({exc.__class__.__name__})"
        print(("OK   " if ok else "FALLA ") + msg)
        resultados.append((fila["seccion"], ok, msg))
        fallas += 0 if ok else 1
    if texto != original:
        REGISTRO.write_bytes(texto.encode("utf-8"))
        print("Registro actualizado con las lineas reubicadas.")
    for titulo in secciones_sin_matriz(texto):
        print(f"FALLA seccion sin matriz: {titulo}")
        fallas += 1
    print(formatear_resumen(resumen_por_seccion(resultados)))
    avisos = sum(1 for _, _, m in resultados if "desplazada" in m)
    print(f"Filas: {len(filas)}; avisos: {avisos}; fallas: {fallas}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
