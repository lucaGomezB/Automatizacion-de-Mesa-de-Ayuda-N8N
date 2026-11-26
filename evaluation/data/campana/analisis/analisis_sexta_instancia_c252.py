#!/usr/bin/env python3
"""Extension media de las descripciones del corpus por canal y por regimen (c-252, D-04).

Analisis de solo lectura, determinista y offline. No invoca al modelo, no usa red ni
base de datos, no reclasifica y no modifica el corpus ni ninguna cifra canonica. Es
aditivo: agrega una seccion nueva y no reemplaza ninguna salida anterior de
`evaluation/data/campana/analisis/`.

Sigue el patron de `analisis_regimen_c249.py` (leer `data/corpus_evaluacion_pseudonimizado.json`,
agrupar por `canal_origen`, escribir `.json`, `.md` y `SHA256SUMS.txt` deterministicos).

METODO (fijado en este docstring antes de correr)

1. Por canal: se agrupan los 200 casos segun `canal_origen` del corpus (correo electronico,
   formulario web, llamada telefonica) y se informa, para el campo `descripcion`, la media
   de palabras y de caracteres (sin contar los espacios) y el numero de casos.
2. Por regimen: el regimen (a) es la union de correo electronico y formulario web (119
   casos); el regimen (b) es integramente la llamada telefonica (81 casos). Se informa la
   media de palabras y de caracteres por regimen.
3. Palabras = tokens separados por espacios en blanco consecutivos (colapso de espacios).
   Caracteres = caracteres no espacio. Definiciones simples, sin libreria externa, para que
   la salida sea reproducible y auditable.

Salidas (UTF-8 sin BOM, LF, claves ordenadas): `analisis_sexta_instancia_c252.json`, `.md`
y `.SHA256SUMS.txt`. Dos corridas con las mismas entradas producen salidas identicas byte a
byte.

Uso (desde la raiz del repositorio):
    python3 evaluation/data/campana/analisis/analisis_sexta_instancia_c252.py
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

CANALES = ("correo electrónico", "formulario web", "llamada telefónica")
REGIMEN_B = "llamada telefónica"


def _n_palabras(texto: str) -> int:
    """Cantidad de palabras: tokens separados por uno o mas espacios en blanco."""
    return len(texto.split())


def _n_caracteres(texto: str) -> int:
    """Cantidad de caracteres no espacio."""
    return sum(1 for ch in texto if not ch.isspace())


def _resumen_extension(casos: list[str]) -> dict:
    """Resumen de extension para una lista de descripciones (None si no hay casos)."""
    n = len(casos)
    if n == 0:
        return {"n": 0, "palabras_media": None, "caracteres_media": None}
    palabras = [_n_palabras(c) for c in casos]
    caracteres = [_n_caracteres(c) for c in casos]
    return {
        "n": n,
        "palabras_media": round(sum(palabras) / n, 6),
        "caracteres_media": round(sum(caracteres) / n, 6),
    }


def extension_por_canal(casos: list[dict]) -> dict:
    """Extension media en palabras y caracteres por canal de origen."""
    acumulado: dict[str, list[str]] = {c: [] for c in CANALES}
    for caso in casos:
        canal = caso["canal_origen"]
        acumulado.setdefault(canal, [])
        acumulado[canal].append(caso["descripcion"])
    orden = list(CANALES) + sorted(c for c in acumulado if c not in CANALES)
    return {canal: _resumen_extension(acumulado[canal]) for canal in orden}


def extension_por_regimen(casos: list[dict]) -> dict:
    """Extension media en palabras y caracteres por regimen (a) y (b).

    El regimen (a) es correo electronico + formulario web; el (b), la llamada telefonica.
    """
    por_canal = extension_por_canal(casos)
    descripciones: dict[str, list[str]] = {"a": [], "b": []}
    for canal, datos in por_canal.items():
        regimen = "b" if canal == REGIMEN_B else "a"
        # Reconstruir las listas de descripciones: agrupar por canal desde los casos.
        descripciones[regimen].extend(
            c["descripcion"] for c in casos if c["canal_origen"] == canal
        )
    return {
        "a": _resumen_extension(descripciones["a"]),
        "b": _resumen_extension(descripciones["b"]),
    }


def construir_resultado(*, casos: list[dict], rutas_entrada: dict) -> dict:
    return {
        "schema_version": 1,
        "entradas": rutas_entrada,
        "extension_por_canal": extension_por_canal(casos),
        "extension_por_regimen": extension_por_regimen(casos),
    }


def _fmt(valor: float | None) -> str:
    return "no estimable" if valor is None else f"{valor:.4f}"


def _markdown(r: dict) -> str:
    can = r["extension_por_canal"]
    reg = r["extension_por_regimen"]
    lineas = [
        "# Extension media de las descripciones por canal y regimen (c-252, D-04)",
        "",
        "Salida generada por `analisis_sexta_instancia_c252.py`. Analisis de solo lectura",
        "sobre el corpus versionado; no reclasifica ni modifica el corpus. La palabra es un",
        "token separado por espacios; el caracter no cuenta los espacios.",
        "",
        "## Extension media por canal",
        "",
        "| Canal | Casos | Palabras (media) | Caracteres (media) |",
        "|---|---|---|---|",
    ]
    for canal, d in can.items():
        lineas.append(
            f"| {canal} | {d['n']} | {_fmt(d['palabras_media'])} | {_fmt(d['caracteres_media'])} |"
        )
    lineas += [
        "",
        "## Extension media por regimen",
        "",
        "| Regimen | Casos | Palabras (media) | Caracteres (media) |",
        "|---|---|---|---|",
    ]
    for nombre, etiqueta in (
        ("a", "Regimen (a): correo electronico y formulario web"),
        ("b", "Regimen (b): telefonia"),
    ):
        d = reg[nombre]
        lineas.append(
            f"| {etiqueta} | {d['n']} | {_fmt(d['palabras_media'])} | {_fmt(d['caracteres_media'])} |"
        )
    lineas += [
        "",
        "## Entradas",
        "",
        "| Archivo | SHA-256 |",
        "|---|---|",
    ]
    for ruta, sha in r["entradas"].items():
        lineas.append(f"| `{ruta}` | `{sha}` |")
    lineas.append("")
    return "\n".join(lineas)


def escribir_salidas(resultado: dict, directorio: Path) -> list[Path]:
    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    json_path = directorio / "analisis_sexta_instancia_c252.json"
    md_path = directorio / "analisis_sexta_instancia_c252.md"
    json_texto = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    md_texto = _markdown(resultado)
    json_path.write_bytes(json_texto.encode("utf-8"))
    md_path.write_bytes(md_texto.encode("utf-8"))
    sumas = (
        f"{hashlib.sha256(json_texto.encode('utf-8')).hexdigest()}  {json_path.name}\n"
        f"{hashlib.sha256(md_texto.encode('utf-8')).hexdigest()}  {md_path.name}\n"
    )
    sums_path = directorio / "analisis_sexta_instancia_c252.SHA256SUMS.txt"
    sums_path.write_bytes(sumas.encode("utf-8"))
    return [json_path, md_path, sums_path]


def _sha256(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def main() -> int:
    archivos = {
        "data/corpus_evaluacion_pseudonimizado.json": RAIZ / "data/corpus_evaluacion_pseudonimizado.json",
    }
    corpus = json.loads(archivos["data/corpus_evaluacion_pseudonimizado.json"].read_text(encoding="utf-8"))
    resultado = construir_resultado(
        casos=corpus["casos"],
        rutas_entrada={ruta: _sha256(p) for ruta, p in archivos.items()},
    )
    salidas = escribir_salidas(resultado, Path(__file__).resolve().parent)
    for ruta in salidas:
        print(f"{_sha256(ruta)}  {ruta.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())