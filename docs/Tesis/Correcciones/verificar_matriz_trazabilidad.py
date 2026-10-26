"""Verifica la matriz de trazabilidad del dictamen v10 / v1.1.0 (c-141, tarea 6.1).

Para cada fila de la matriz de la seccion "Dictamen v10 / v1.1.0 (2026-10-22) -
cobertura por change (FASE 36)" de dictamen-correcciones.md comprueba que la
linea citada contiene el fragmento verificable y que el \\label ancla existe en
el mismo archivo. Las filas cuyo estado empieza con PENDIENTE se omiten.

Uso, desde la raiz del repositorio:

    python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py
    python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py --rev v1.2.0

Con --rev lee los archivos con `git show REV:ruta` (el arbol etiquetado); sin
el, lee el arbol de trabajo. Codigo de salida 0 si todas las filas pasan.
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

TITULO_SECCION = "cobertura por change (FASE 36)"
RAIZ = Path(__file__).resolve().parents[3]
REGISTRO = Path(__file__).resolve().parent / "dictamen-correcciones.md"
BASE_TESIS = "docs/Tesis/v10 (IA)/paper/"


def _celda(texto):
    return texto.strip().strip("`").strip()


def parsear_matriz(texto):
    """Devuelve las filas de la matriz de la seccion de cobertura como dicts."""
    en_seccion = False
    en_matriz = False
    filas = []
    for linea in texto.splitlines():
        linea = linea.rstrip("\r")
        if linea.startswith("## "):
            en_seccion = TITULO_SECCION in linea
            en_matriz = False
            continue
        if not en_seccion:
            continue
        if not linea.startswith("|"):
            en_matriz = False  # una linea que no es de tabla cierra la tabla
            continue
        if linea.lstrip("| ").startswith("Rec "):
            en_matriz = "Archivo:linea" in linea
            continue
        if not en_matriz:
            continue
        celdas = [c for c in linea.strip().strip("|").split("|")]
        if len(celdas) != 7:
            continue
        if celdas[0].strip() in ("Rec", "---") or set(celdas[0].strip()) <= {"-"}:
            continue
        archivo, _, numero = _celda(celdas[3]).rpartition(":")
        filas.append(
            {
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


def verificar_fila(fila, leer):
    """Verifica una fila; `leer(ruta)` devuelve la lista de lineas del archivo."""
    if fila["estado"].upper().startswith("PENDIENTE"):
        return True, f"{fila['rec']}: omitida ({fila['estado'][:40]})"
    lineas = leer(fila["archivo"])
    n = fila["linea"]
    if not 1 <= n <= len(lineas):
        return False, f"{fila['rec']}: linea {n} fuera de rango ({len(lineas)} lineas)"
    if fila["fragmento"] not in lineas[n - 1]:
        return False, f"{fila['rec']}: el fragmento no esta en {fila['archivo']}:{n}"
    ancla = fila["ancla"]
    if ancla not in ("", "-"):
        if not any("\\label{" + ancla + "}" in l for l in lineas):
            return False, f"{fila['rec']}: el ancla {ancla} no existe en {fila['archivo']}"
    return True, f"{fila['rec']}: ok ({fila['archivo']}:{n})"


def reubicar_fila(fila, leer):
    """Primera linea del archivo que contiene el fragmento, o None si no hay."""
    for i, linea in enumerate(leer(fila["archivo"]), 1):
        if fila["fragmento"] in linea:
            return i
    return None


def reemplazar_linea(texto, archivo, vieja, nueva):
    """Cambia `archivo:vieja` por `archivo:nueva` en el texto del registro."""
    return texto.replace(f"`{archivo}:{vieja}`", f"`{archivo}:{nueva}`")


def _lector(rev):
    def leer(ruta):
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
    args = ap.parse_args(argv)
    original = REGISTRO.read_bytes().decode("utf-8")
    texto = original
    filas = parsear_matriz(texto)
    if not filas:
        print("No se encontro la matriz de cobertura en el registro.")
        return 2
    leer = _lector(args.rev)
    fallas = 0
    for fila in filas:
        try:
            ok, msg = verificar_fila(fila, leer)
            if not ok and args.reubicar and not args.rev:
                nueva = reubicar_fila(fila, leer)
                if nueva is not None:
                    texto = reemplazar_linea(texto, fila["archivo"], fila["linea"], nueva)
                    ok, msg = True, f"{fila['rec']}: reubicada {fila['linea']} -> {nueva}"
        except (OSError, subprocess.CalledProcessError) as exc:
            ok, msg = False, f"{fila['rec']}: no se pudo leer {fila['archivo']} ({exc.__class__.__name__})"
        print(("OK   " if ok else "FALLA ") + msg)
        fallas += 0 if ok else 1
    if texto != original:
        REGISTRO.write_bytes(texto.encode("utf-8"))
        print("Registro actualizado con las lineas reubicadas.")
    print(f"Filas: {len(filas)}; fallas: {fallas}")
    return 1 if fallas else 0


if __name__ == "__main__":
    sys.exit(main())
