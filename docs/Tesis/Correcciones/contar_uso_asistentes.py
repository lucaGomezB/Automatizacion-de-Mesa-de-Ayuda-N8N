"""Cuenta el uso de asistentes de IA registrado en el historial de git (c-237).

Deriva, solo del repositorio, cuantos commits llevan la marca de co-autoria de un
asistente de IA (`Co-Authored-By`), por periodo y por modelo, y cuantos changes
archivados nombran cada ambito en sus tareas. El conteo es una **cota inferior**
de commits asistidos, no una proporcion de autoria (design D2). No emite nombres
ni correos de personas: los co-autores se identifican por su nombre de pantalla,
sin la parte del correo.

Uso, desde la raiz del repositorio:

    python3 -I docs/Tesis/Correcciones/contar_uso_asistentes.py \\
        --ref v1.5.2 --desde-ref v1.2.18 \\
        --archivo-changes openspec/changes/archive \\
        --salida /tmp/fragmento.md
"""
import argparse
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

# Prefijos de nombre de pantalla que identifican a un asistente de IA. Un
# co-autor cuyo nombre no empieza por ninguno de estos prefijos se registra como
# "otros co-autores" y NO cuenta como asistencia (no confundir co-autoria humana
# con asistencia).
PREFIJOS_ASISTENTE = (
    "Claude",
    "GPT",
    "Gemini",
    "Copilot",
    "Codex",
    "Cursor",
    "Aider",
    "Devin",
    "OpenAI",
    "Anthropic",
    "Llama",
    "Mistral",
)

# Patrones de ambito que se buscan en el texto de un `tasks.md` archivado.
PATRONES_AMBITO = (
    ("codigo", re.compile(r"\bApp/(?:Backend|Frontend)")),
    ("analisis", re.compile(r"evaluation/|docs/Tesis/Correcciones/")),
    ("prosa", re.compile(r"\.tex\b")),
    ("n8n", re.compile(r"\bn8n/workflow")),
)

FORMATO_LOG = "%H%x09%ad%x09%(trailers:key=Co-Authored-By,valueonly,separator=|)"


@dataclass(frozen=True)
class Commit:
    hash: str
    fecha: str
    coautores: tuple


@dataclass(frozen=True)
class Conteo:
    total: int
    con_trailer: int
    sin_trailer: int
    por_modelo: dict
    otros_coautores: dict


def _sin_correo(valor):
    """Devuelve el nombre de pantalla de un trailer, sin la parte del correo."""
    return valor.split("<")[0].strip()


def es_asistente(nombre):
    """True si el nombre de pantalla corresponde a un asistente de IA conocido."""
    return any(
        nombre == prefijo or nombre.startswith(prefijo + " ")
        for prefijo in PREFIJOS_ASISTENTE
    )


def parsear_log(texto):
    """Parsea la salida de `git log --format=FORMATO_LOG` a una lista de Commit.

    Cada linea esperada es `hash<TAB>fecha<TAB>trailers`; los trailers van
    separados por `|`. Las lineas vacias o malformadas se ignoran.
    """
    commits = []
    for linea in texto.splitlines():
        if not linea.strip():
            continue
        partes = linea.split("\t")
        if len(partes) < 3 or not partes[0].strip():
            continue
        hash_commit = partes[0].strip()
        fecha = partes[1].strip()
        coautores = tuple(
            nombre
            for nombre in (_sin_correo(v) for v in partes[2].split("|"))
            if nombre
        )
        commits.append(Commit(hash=hash_commit, fecha=fecha, coautores=coautores))
    return commits


def contar(commits):
    """Cuenta commits totales, con y sin marca de asistente, y desglosa por modelo.

    Un commit cuenta una sola vez en `con_trailer` aunque lleve varias marcas de
    asistente; en `por_modelo` aparece bajo cada modelo marcado. En el historial
    de este repositorio cada commit asistido lleva una sola marca, de modo que la
    suma del desglose coincide con `con_trailer`.
    """
    por_modelo = Counter()
    otros = Counter()
    con_trailer = 0
    for commit in commits:
        asistentes = [n for n in commit.coautores if es_asistente(n)]
        if asistentes:
            con_trailer += 1
            for nombre in dict.fromkeys(asistentes):
                por_modelo[nombre] += 1
        for nombre in commit.coautores:
            if not es_asistente(nombre):
                otros[nombre] += 1
    total = len(commits)
    return Conteo(
        total=total,
        con_trailer=con_trailer,
        sin_trailer=total - con_trailer,
        por_modelo=dict(sorted(por_modelo.items())),
        otros_coautores=dict(sorted(otros.items())),
    )


def clasificar_change(texto_tasks):
    """Devuelve el conjunto de ambitos que el texto de un `tasks.md` nombra."""
    return {
        ambito for ambito, patron in PATRONES_AMBITO if patron.search(texto_tasks)
    }


def _tabla(encabezados, filas):
    lineas = [
        "| " + " | ".join(encabezados) + " |",
        "|" + "|".join("---" for _ in encabezados) + "|",
    ]
    lineas += ["| " + " | ".join(str(c) for c in fila) + " |" for fila in filas]
    return lineas


def renderizar_markdown(periodos, mapa_ambitos):
    """Arma las tablas de las secciones 2 y 4 del inventario.

    `periodos` es una lista de dicts con `etiqueta`, `ref` y `conteo`; el conteo
    se desglosa por modelo. `mapa_ambitos` mapea cada ambito a la lista de
    changes que lo nombran.
    """
    lineas = ["## Conteos de commits por periodo", ""]
    for periodo in periodos:
        conteo = periodo["conteo"]
        lineas.append(f"### {periodo['etiqueta']} (`{periodo['ref']}`)")
        lineas.append("")
        lineas += _tabla(
            ("Concepto", "Valor"),
            [
                ("Commits", conteo.total),
                ("Con marca de asistente (cota inferior)", conteo.con_trailer),
                ("Sin marca", conteo.sin_trailer),
            ],
        )
        lineas.append("")
        if conteo.por_modelo:
            lineas += _tabla(
                ("Modelo de asistente", "Commits"),
                sorted(conteo.por_modelo.items()),
            )
        else:
            lineas.append("Sin marcas de asistente en el periodo.")
        lineas.append("")
    lineas += ["## Changes archivados por ambito", ""]
    filas = []
    for ambito, _ in PATRONES_AMBITO:
        changes = sorted(mapa_ambitos.get(ambito, []))
        ejemplo = changes[0] if changes else "-"
        filas.append((ambito, len(changes), ejemplo))
    lineas += _tabla(("Ambito", "Changes que lo nombran", "Ejemplo"), filas)
    return "\n".join(lineas) + "\n"


def _git(args):
    """Ejecuta git sin shell y devuelve su salida estandar."""
    proc = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=True
    )
    return proc.stdout


def _contar_ref(ref, desde_ref=None):
    rango = f"{desde_ref}..{ref}" if desde_ref else ref
    texto = _git(["log", rango, f"--format={FORMATO_LOG}", "--date=short"])
    return parsear_log(texto)


def _mapa_ambitos(archivo_changes):
    mapa = {ambito: [] for ambito, _ in PATRONES_AMBITO}
    base = Path(archivo_changes)
    for tasks in sorted(base.glob("*/tasks.md")):
        texto = tasks.read_text(encoding="utf-8", errors="replace")
        for ambito in clasificar_change(texto):
            mapa[ambito].append(tasks.parent.name)
    return mapa


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ref", default="HEAD")
    ap.add_argument("--desde-ref", default=None)
    ap.add_argument("--archivo-changes", required=True)
    ap.add_argument("--salida", default=None)
    args = ap.parse_args(argv)
    if not Path(args.archivo_changes).is_dir():
        print(f"No existe el arbol de changes: {args.archivo_changes}", file=sys.stderr)
        return 2
    periodos = [
        {
            "etiqueta": "Historial hasta",
            "ref": args.ref,
            "conteo": contar(_contar_ref(args.ref)),
        }
    ]
    if args.desde_ref:
        periodos.append(
            {
                "etiqueta": f"Rango {args.desde_ref}..{args.ref}",
                "ref": f"{args.desde_ref}..{args.ref}",
                "conteo": contar(_contar_ref(args.ref, args.desde_ref)),
            }
        )
    texto = renderizar_markdown(periodos, _mapa_ambitos(args.archivo_changes))
    if args.salida:
        Path(args.salida).write_bytes(texto.encode("utf-8"))
    else:
        sys.stdout.write(texto)
    return 0


if __name__ == "__main__":
    sys.exit(main())
