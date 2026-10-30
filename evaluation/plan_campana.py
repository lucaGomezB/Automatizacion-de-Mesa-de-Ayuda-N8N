"""
Plan de campana por caso: contrabalanceo de CONDICION (c-166, ECM-004).

El efecto de orden que importa en la campana es el del operador humano, no el de
una maquina que recibe envios: lo que hay que contrabalancear es QUE BRAZO (manual o
automatizado) VE PRIMERO cada caso. El plan asigna a cada caso su `posicion` (1..n),
su `mitad` y su `brazo_primero`; lo siguen el operador del brazo manual (fuera del
repositorio), los harnesses de `scripts/corpus_ingest/` y el operador del softphone.

Reglas del plan:

- Modos (`ordenar_casos`): `directo` preserva el orden, `inverso` lo invierte,
  `alternado` intercala las mitades (1, n//2+1, 2, n//2+2, ...) y `aleatorio` baraja
  con `random.Random(seed)`. `aleatorio` EXIGE semilla y la deja registrada en cada
  fila: con la misma semilla y los mismos casos el plan es identico. En los otros
  modos la semilla no tiene efecto y la celda `seed` queda vacia.
- Mitades: `mitad = 1` si `posicion <= n // 2` y `2` si no. Con N impar la primera
  mitad tiene n//2 casos y la segunda uno mas (el caso del medio cae en la segunda);
  en `alternado` el ultimo elemento es de la segunda mitad. N = 0 da un plan vacio y
  N = 1 da un unico caso en la mitad 2.
- Condicion: `brazo_primero` es `manual` en las posiciones impares y `automatizado` en
  las pares, de modo que en cada mitad ambos brazos difieren en a lo sumo 1 caso
  (`verificar_balance`). La aleatorizacion de QUE caso cae en cada brazo la aporta el
  modo: para la campana se recomienda `aleatorio` con la semilla registrada.
- `--limit` (en los harnesses y en el CLI `generar`) se aplica ANTES de ordenar: el
  plan es siempre sobre los primeros N casos del corpus. Un plan ya generado es la
  seleccion; para acotarlo se genera uno mas chico o se extrae un `subplan`.

El modulo solo usa la biblioteca estandar y `evaluation.corpus`; no requiere red.
CLI: `python -m evaluation.plan_campana generar|subplan|preparar-corpus`.
"""

from __future__ import annotations

import argparse
import csv
import fnmatch
import json
import os
import pathlib
import random
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Iterable, Sequence, TypeVar

from evaluation.corpus import CorpusError, cargar_corpus

T = TypeVar("T")

MODO_DIRECTO = "directo"
MODO_INVERSO = "inverso"
MODO_ALTERNADO = "alternado"
MODO_ALEATORIO = "aleatorio"
#: Modos de ordenamiento admitidos.
MODOS: tuple[str, ...] = (MODO_DIRECTO, MODO_INVERSO, MODO_ALTERNADO, MODO_ALEATORIO)

BRAZO_MANUAL = "manual"
BRAZO_AUTOMATIZADO = "automatizado"
#: Brazos de la medicion; `brazo_primero` es uno de ellos.
BRAZOS: tuple[str, ...] = (BRAZO_MANUAL, BRAZO_AUTOMATIZADO)

#: Raiz del repositorio (`evaluation/` vive en ella).
RAIZ_REPO = pathlib.Path(__file__).resolve().parent.parent

#: Archivos versionados que ninguna corrida de campana puede escribir (rutas relativas
#: a la raiz del repo). `data/corpus_resultados_n8n.json` es el sidecar por defecto de
#: `ingest_via_n8n.py` (gitignorado) y se protege igual.
ARCHIVOS_CONGELADOS: tuple[str, ...] = (
    "data/corpus_evaluacion_pseudonimizado.json",
    "data/corpus_resultados.json",
    "data/corpus_resultados_telefonia.json",
    "data/corpus_resultados_n8n.json",
)
#: Cualquier otro resultado de ingesta bajo `data/` tambien esta congelado.
PATRON_RESULTADOS_CONGELADOS = "data/corpus_resultados*.json"

#: Rutas canonicas de los artefactos de campana (relativas a la raiz del repo).
RUTA_PLAN_CANONICA = "evaluation/data/campana/plan_campana.csv"
RUTA_CORPUS_CAMPANA = "evaluation/data/campana/corpus_campana.json"

#: Columnas del CSV del plan, en orden (`evaluation/data/campana/plan_campana.csv`).
COLUMNAS_PLAN: tuple[str, ...] = (
    "id_caso",
    "posicion",
    "mitad",
    "brazo_primero",
    "modo",
    "seed",
)


class PlanCampanaError(ValueError):
    """Error de uso o de contrato del plan de campana (el mensaje dice como corregirlo)."""


@dataclass(frozen=True)
class AsignacionCaso:
    """Fila del plan: que lugar y que brazo-primero le toca a un caso."""

    id_caso: str
    posicion: int
    mitad: int
    brazo_primero: str
    modo: str
    seed: int | None = None


def _ids_repetidos(ids: Iterable[str]) -> list[str]:
    return sorted(id_caso for id_caso, veces in Counter(ids).items() if veces > 1)


def ordenar_casos(casos: Sequence[T], modo: str, seed: int | None = None) -> list[T]:
    """Devuelve una lista NUEVA con los `casos` en el orden del `modo`.

    No muta la entrada. Es generica sobre los elementos (ids, `Case`, `CorpusCase`).
    `alternado` con N impar deja el ultimo elemento de la segunda mitad. `aleatorio`
    sin `seed` y un `modo` desconocido levantan `PlanCampanaError` (un `ValueError`)
    con un mensaje que dice como corregirlo.
    """
    if modo not in MODOS:
        raise PlanCampanaError(
            f"modo de orden desconocido: {modo!r}. Modos validos: {', '.join(MODOS)}."
        )
    if modo == MODO_ALEATORIO and seed is None:
        raise PlanCampanaError(
            "el modo aleatorio exige --seed <entero>; registra la semilla en el plan "
            "para poder reproducirlo."
        )
    copia = list(casos)
    if modo == MODO_INVERSO:
        copia.reverse()
    elif modo == MODO_ALTERNADO:
        mitad = len(copia) // 2
        primera, segunda = copia[:mitad], copia[mitad:]
        copia = []
        for i, caso in enumerate(segunda):
            if i < len(primera):
                copia.append(primera[i])
            copia.append(caso)
    elif modo == MODO_ALEATORIO:
        random.Random(seed).shuffle(copia)
    return copia


def generar_plan_campana(
    casos: Sequence[str], modo: str, seed: int | None = None
) -> list[AsignacionCaso]:
    """Asigna a cada `id_caso` su posicion, su mitad y el brazo que lo ve primero.

    `casos` es la secuencia de ids ya seleccionada (el `--limit` se aplica antes, al
    elegirla). La posicion sigue el orden que resulta de `ordenar_casos`; ver las
    reglas de mitad, N impar y condicion en la docstring del modulo. Ids repetidos
    levantan `PlanCampanaError`.
    """
    repetidos = _ids_repetidos(casos)
    if repetidos:
        raise PlanCampanaError(f"ids de caso repetidos en el plan: {', '.join(repetidos)}.")
    ordenados = ordenar_casos(casos, modo, seed)
    n = len(ordenados)
    semilla = seed if modo == MODO_ALEATORIO else None
    return [
        AsignacionCaso(
            id_caso=id_caso,
            posicion=posicion,
            mitad=1 if posicion <= n // 2 else 2,
            brazo_primero=BRAZO_MANUAL if posicion % 2 else BRAZO_AUTOMATIZADO,
            modo=modo,
            seed=semilla,
        )
        for posicion, id_caso in enumerate(ordenados, start=1)
    ]


def verificar_balance(plan: Sequence[AsignacionCaso]) -> dict[tuple[int, str], int]:
    """Criterio de aceptacion ejecutable del contrabalanceo de condicion.

    Cuenta `mitad x brazo_primero` y falla si en alguna mitad la cantidad de casos
    `manual`-primero y `automatizado`-primero difiere en mas de 1. Devuelve el conteo
    (con las cuatro combinaciones, aun en cero) para poder informarlo.
    """
    for fila in plan:
        if fila.mitad not in (1, 2) or fila.brazo_primero not in BRAZOS:
            raise PlanCampanaError(
                f"fila fuera de dominio en el caso {fila.id_caso}: mitad={fila.mitad!r}, "
                f"brazo_primero={fila.brazo_primero!r} (mitad 1 o 2; brazo {' o '.join(BRAZOS)})."
            )
    conteo = Counter((fila.mitad, fila.brazo_primero) for fila in plan)
    resultado = {(mitad, brazo): conteo[(mitad, brazo)] for mitad in (1, 2) for brazo in BRAZOS}
    for mitad in (1, 2):
        manual = resultado[(mitad, BRAZO_MANUAL)]
        automatizado = resultado[(mitad, BRAZO_AUTOMATIZADO)]
        if abs(manual - automatizado) > 1:
            raise PlanCampanaError(
                f"plan desbalanceado en la mitad {mitad}: manual={manual}, "
                f"automatizado={automatizado} (la diferencia debe ser de a lo sumo 1)."
            )
    return resultado


# ---------------------------------------------------------------------------
# CSV del plan
# ---------------------------------------------------------------------------
def escribir_plan_csv(plan: Sequence[AsignacionCaso], ruta: pathlib.Path | str) -> None:
    """Escribe el plan en CSV UTF-8 (separador `,`, fin de linea LF, sin BOM)."""
    destino = pathlib.Path(ruta)
    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo, lineterminator="\n")
        escritor.writerow(COLUMNAS_PLAN)
        for fila in plan:
            semilla = "" if fila.seed is None else fila.seed
            escritor.writerow(
                [fila.id_caso, fila.posicion, fila.mitad, fila.brazo_primero, fila.modo, semilla]
            )


def _entero(valor: str, columna: str, numero_fila: int) -> int:
    try:
        return int(valor)
    except ValueError:
        raise PlanCampanaError(
            f"fila {numero_fila}: {columna} debe ser un entero y es {valor!r}."
        ) from None


def _parsear_fila_plan(numero_fila: int, registro: dict[str, str | None]) -> AsignacionCaso:
    if None in registro or any(valor is None for valor in registro.values()):
        raise PlanCampanaError(
            f"fila {numero_fila}: cantidad de columnas incorrecta (se esperan {len(COLUMNAS_PLAN)})."
        )
    celdas = {columna: (valor or "").strip() for columna, valor in registro.items()}
    if not celdas["id_caso"]:
        raise PlanCampanaError(f"fila {numero_fila}: id_caso vacio.")
    mitad = _entero(celdas["mitad"], "mitad", numero_fila)
    if mitad not in (1, 2):
        raise PlanCampanaError(f"fila {numero_fila}: mitad debe ser 1 o 2 y es {mitad}.")
    if celdas["brazo_primero"] not in BRAZOS:
        raise PlanCampanaError(
            f"fila {numero_fila}: brazo_primero debe ser {' o '.join(BRAZOS)} "
            f"y es {celdas['brazo_primero']!r}."
        )
    if celdas["modo"] not in MODOS:
        raise PlanCampanaError(
            f"fila {numero_fila}: modo debe ser uno de {', '.join(MODOS)} "
            f"y es {celdas['modo']!r}."
        )
    semilla = _entero(celdas["seed"], "seed", numero_fila) if celdas["seed"] else None
    return AsignacionCaso(
        id_caso=celdas["id_caso"],
        posicion=_entero(celdas["posicion"], "posicion", numero_fila),
        mitad=mitad,
        brazo_primero=celdas["brazo_primero"],
        modo=celdas["modo"],
        seed=semilla,
    )


def leer_plan_csv(ruta: pathlib.Path | str, completo: bool = True) -> list[AsignacionCaso]:
    """Lee y valida un plan en CSV.

    Valida columnas exactas, valores de dominio, ids unicos y posiciones. Con
    `completo=True` (un plan entero) las posiciones deben ser exactamente 1..n; con
    `completo=False` (un sub-plan, que conserva la posicion global) solo deben ser
    estrictamente crecientes.
    """
    with pathlib.Path(ruta).open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        columnas = tuple(lector.fieldnames or ())
        faltantes = [c for c in COLUMNAS_PLAN if c not in columnas]
        sobrantes = [c for c in columnas if c not in COLUMNAS_PLAN]
        if faltantes or sobrantes:
            raise PlanCampanaError(
                f"columnas del plan invalidas en {ruta}: faltan {faltantes or 'ninguna'}, "
                f"sobran {sobrantes or 'ninguna'} (esperadas: {', '.join(COLUMNAS_PLAN)})."
            )
        plan = [
            _parsear_fila_plan(numero_fila, registro)
            for numero_fila, registro in enumerate(lector, start=2)
        ]
    repetidos = _ids_repetidos(fila.id_caso for fila in plan)
    if repetidos:
        raise PlanCampanaError(f"ids de caso repetidos en el plan: {', '.join(repetidos)}.")
    posiciones = [fila.posicion for fila in plan]
    if completo and posiciones != list(range(1, len(plan) + 1)):
        raise PlanCampanaError(
            "las posiciones del plan deben ser contiguas de 1 a n; "
            "si es un sub-plan, leelo con completo=False."
        )
    if not completo and any(b <= a for a, b in zip(posiciones, posiciones[1:])):
        raise PlanCampanaError("las posiciones del sub-plan deben ser estrictamente crecientes.")
    return plan


def subplan(
    plan: Sequence[AsignacionCaso], mitad: int, brazo: str, turno: int
) -> list[AsignacionCaso]:
    """Filas de una `mitad` que le tocan a un `brazo` en un `turno`.

    Turno 1: los casos donde `brazo` va primero (`brazo_primero == brazo`). Turno 2:
    los casos donde va primero el otro brazo, o sea donde `brazo` va segundo. Conserva
    la `posicion` global y el orden del plan, de modo que el operador (y el harness)
    ejecutan dentro de cada mitad primero un turno y despues el otro.
    """
    if mitad not in (1, 2):
        raise PlanCampanaError(f"mitad debe ser 1 o 2 y es {mitad!r}.")
    if brazo not in BRAZOS:
        raise PlanCampanaError(f"brazo debe ser {' o '.join(BRAZOS)} y es {brazo!r}.")
    if turno not in (1, 2):
        raise PlanCampanaError(f"turno debe ser 1 o 2 y es {turno!r}.")
    return [
        fila
        for fila in plan
        if fila.mitad == mitad and (fila.brazo_primero == brazo) == (turno == 1)
    ]


# ---------------------------------------------------------------------------
# Archivos congelados y copia de campana del corpus
# ---------------------------------------------------------------------------
def _clave_ruta(ruta: pathlib.Path | str) -> str:
    return os.path.normcase(os.path.normpath(str(ruta))).replace("\\", "/")


def es_archivo_congelado(ruta: pathlib.Path | str, raiz: pathlib.Path = RAIZ_REPO) -> bool:
    """True si `ruta` es uno de los archivos versionados que la campana no puede escribir.

    Compara la ruta tal como se escribio (para que `data/corpus_resultados.json` se
    reconozca aunque el cwd no sea la raiz) y la ruta resuelta relativa a `raiz`. Un
    archivo homonimo fuera de la raiz del repositorio no se considera congelado.
    """
    claves = {_clave_ruta(ruta)}
    try:
        resuelta = pathlib.Path(ruta).resolve()
        claves.add(_clave_ruta(resuelta.relative_to(pathlib.Path(raiz).resolve())))
    except ValueError:
        pass  # fuera de la raiz: solo vale la clave "tal como se escribio"
    congelados = {_clave_ruta(archivo) for archivo in ARCHIVOS_CONGELADOS}
    patron = _clave_ruta(PATRON_RESULTADOS_CONGELADOS)
    return any(clave in congelados or fnmatch.fnmatchcase(clave, patron) for clave in claves)


def preparar_corpus_campana(
    origen: pathlib.Path | str,
    destino: pathlib.Path | str,
    raiz: pathlib.Path = RAIZ_REPO,
) -> None:
    """Copia el corpus de `origen` a `destino` con los tiempos en `null`.

    Con `tiempo_automatizado_s` y `tiempo_manual_s` en `null`, un caso no medido en la
    campana queda nulo y no hereda el tiempo canonico (`merge_evaluation_json` solo
    escribe mediciones validas). No modifica `origen`, rechaza un `destino` existente o
    congelado y no deja un `destino` que no cargue con `cargar_corpus`.
    """
    origen, destino = pathlib.Path(origen), pathlib.Path(destino)
    if es_archivo_congelado(destino, raiz):
        raise PlanCampanaError(
            f"el destino {destino} es un archivo congelado; usa {RUTA_CORPUS_CAMPANA}."
        )
    if destino.exists():
        raise PlanCampanaError(
            f"el destino {destino} ya existe; no se sobrescribe. Borralo a mano si es una "
            "copia de campana que queres regenerar."
        )
    documento = json.loads(origen.read_text(encoding="utf-8"))
    casos = documento.get("casos") if isinstance(documento, dict) else None
    if not isinstance(casos, list) or not all(isinstance(caso, dict) for caso in casos):
        raise PlanCampanaError(
            f"el corpus de origen {origen} no tiene la forma esperada ('casos' como lista de objetos)."
        )
    for caso in casos:
        caso["tiempo_manual_s"] = None
        caso["tiempo_automatizado_s"] = None
    if isinstance(documento.get("metadata"), dict):
        documento["metadata"]["total_casos"] = len(casos)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    try:
        cargar_corpus(destino)
    except CorpusError as exc:
        destino.unlink()
        raise PlanCampanaError(f"el corpus de origen {origen} no es un corpus valido: {exc}") from exc


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _rechazar_si_existe(ruta: pathlib.Path) -> None:
    if ruta.exists():
        raise PlanCampanaError(
            f"{ruta} ya existe; no se sobrescribe. Elegi otra --salida o borralo a mano."
        )


def _resumen_balance(conteo: dict[tuple[int, str], int]) -> str:
    return "; ".join(
        f"mitad {mitad}: manual={conteo[(mitad, BRAZO_MANUAL)]} "
        f"automatizado={conteo[(mitad, BRAZO_AUTOMATIZADO)]}"
        for mitad in (1, 2)
    )


def _comando_generar(args: argparse.Namespace) -> str:
    ids = [caso.id for caso in cargar_corpus(args.corpus)]
    if args.limit is not None:
        ids = ids[: max(args.limit, 0)]  # --limit se aplica ANTES de ordenar
    _rechazar_si_existe(args.salida)
    plan = generar_plan_campana(ids, args.modo, args.seed)
    balance = verificar_balance(plan)
    escribir_plan_csv(plan, args.salida)
    semilla = plan[0].seed if plan else None
    return (
        f"OK: plan de {len(plan)} casos (modo={args.modo}, seed={semilla}) escrito en "
        f"{args.salida}. Balance: {_resumen_balance(balance)}."
    )


def _comando_subplan(args: argparse.Namespace) -> str:
    filas = subplan(leer_plan_csv(args.plan), args.mitad, args.brazo, args.turno)
    _rechazar_si_existe(args.salida)
    escribir_plan_csv(filas, args.salida)
    return (
        f"OK: sub-plan (mitad={args.mitad}, brazo={args.brazo}, turno={args.turno}) de "
        f"{len(filas)} casos escrito en {args.salida}."
    )


def _comando_preparar_corpus(args: argparse.Namespace) -> str:
    preparar_corpus_campana(args.origen, args.destino)
    return f"OK: copia de campana (tiempos en null) escrita en {args.destino}."


_COMANDOS: dict[str, Callable[[argparse.Namespace], str]] = {
    "generar": _comando_generar,
    "subplan": _comando_subplan,
    "preparar-corpus": _comando_preparar_corpus,
}


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.plan_campana",
        description="Plan de campana por caso: contrabalanceo de condicion (c-166).",
    )
    comandos = parser.add_subparsers(dest="comando", required=True)

    generar = comandos.add_parser("generar", help="genera el plan de un corpus y lo escribe en CSV")
    generar.add_argument("--corpus", required=True, type=pathlib.Path, help="corpus JSON")
    generar.add_argument("--modo", required=True, choices=MODOS)
    generar.add_argument("--seed", type=int, default=None, help="entero; obligatoria con aleatorio")
    generar.add_argument(
        "--limit",
        type=int,
        default=None,
        help="usa solo los primeros N casos del corpus (se aplica ANTES de ordenar)",
    )
    generar.add_argument("--salida", required=True, type=pathlib.Path, help="CSV a crear")

    sub_plan = comandos.add_parser("subplan", help="extrae el sub-plan de un turno de un plan")
    sub_plan.add_argument("--plan", required=True, type=pathlib.Path, help="plan completo (CSV)")
    sub_plan.add_argument("--mitad", required=True, type=int, choices=(1, 2))
    sub_plan.add_argument("--brazo", required=True, choices=BRAZOS)
    sub_plan.add_argument("--turno", required=True, type=int, choices=(1, 2))
    sub_plan.add_argument("--salida", required=True, type=pathlib.Path, help="CSV a crear")

    preparar = comandos.add_parser(
        "preparar-corpus", help="copia el corpus con los tiempos en null (copia de campana)"
    )
    preparar.add_argument("--origen", required=True, type=pathlib.Path, help="corpus JSON")
    preparar.add_argument("--destino", required=True, type=pathlib.Path, help="JSON a crear")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI. Devuelve 0 si salio bien y 2 ante un error de uso."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    args = _construir_parser().parse_args(argv)  # error de uso -> SystemExit(2)
    try:
        mensaje = _COMANDOS[args.comando](args)
    except (OSError, ValueError) as exc:  # PlanCampanaError y CorpusError son ValueError
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(mensaje)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
