"""Modo campana de los harnesses de ingesta (c-166, ECM-004 y ECM-007).

Helper compartido por ``ingest_via_n8n.py``, ``ingest_corpus.py`` e
``ingest_telefonia_corpus.py``: registra los flags ``--plan``, ``--orden``, ``--seed`` e
``--id-corrida``, valida su uso antes de leer credenciales o enviar nada y resuelve que
casos se procesan y en que orden. El plan en si (ordenamiento, balance, CSV, archivos
congelados) vive en ``evaluation/plan_campana.py``, que corre en el gate de CI.

El modo campana se activa con ``--plan`` o ``--orden``. Sin ninguno de los dos, los
harnesses se comportan exactamente como antes de este change.
"""

from __future__ import annotations

import argparse
import dataclasses
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

# El plan vive en `evaluation/`; se agrega la raiz del repo a sys.path de forma
# relativa a este archivo (mismo patron que pseudonymize_corpus.py con App/Backend).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evaluation import plan_campana as pc  # noqa: E402

#: Excepciones que el modo campana levanta por un uso incorrecto (plan ilegible, ids
#: ausentes, etc.); los harnesses las informan y terminan con codigo 2 sin enviar nada.
ERRORES_DE_USO = (OSError, pc.PlanCampanaError)

#: Codigo de salida de un error de uso (igual que "faltan credenciales").
CODIGO_USO = 2


def informar_error(error: object) -> int:
    """Imprime ``ERROR: <error>`` en stderr y devuelve el codigo de salida de un error de uso."""
    print(f"ERROR: {error}", file=sys.stderr)
    return CODIGO_USO


def registrar_argumentos(parser: argparse.ArgumentParser, *, con_orden: bool = True) -> None:
    """Agrega ``--plan`` e ``--id-corrida`` y, si ``con_orden``, ``--orden`` y ``--seed``."""
    parser.add_argument(
        "--plan",
        default=None,
        help="CSV del plan de campana: se envia en el orden de `posicion` (modo campana).",
    )
    if con_orden:
        parser.add_argument(
            "--orden",
            choices=pc.MODOS,
            default=None,
            help="Atajo: genera el plan con este modo y procesa en ese orden (modo campana).",
        )
        parser.add_argument(
            "--seed",
            type=int,
            default=None,
            help="Semilla entera; obligatoria con --orden aleatorio.",
        )
    parser.add_argument(
        "--id-corrida",
        default=None,
        help="Identificador de la corrida; obligatorio con --plan/--orden (va a cada entrada del sidecar).",
    )


def esta_activo(args: argparse.Namespace) -> bool:
    """True si la corrida usa ``--plan`` o ``--orden``."""
    return bool(args.plan or getattr(args, "orden", None))


def resolver_sidecar(args: argparse.Namespace, por_defecto: str) -> None:
    """Aplica el sidecar por defecto del harness, salvo en modo campana.

    ``--sidecar`` nace sin default: con ``--plan``/``--orden`` queda en ``None`` y
    ``validar_argumentos`` lo exige explicito; fuera del modo campana toma ``por_defecto``.
    """
    if args.sidecar is None and not esta_activo(args):
        args.sidecar = por_defecto


def _error_archivo_congelado(flag: str, valor: str, id_corrida: str | None) -> str:
    if flag == "json":
        return (
            f"--json apunta a {valor}, un archivo versionado y congelado: con --plan/--orden "
            f"usa la copia de campana ({pc.RUTA_CORPUS_CAMPANA}), que se crea con: "
            "python -m evaluation.plan_campana preparar-corpus "
            f"--origen data/corpus_evaluacion_pseudonimizado.json --destino {pc.RUTA_CORPUS_CAMPANA}"
        )
    return (
        f"--sidecar apunta a {valor}, un archivo versionado y congelado: con --plan/--orden "
        "usa un sidecar propio de la corrida, por ejemplo "
        f"evaluation/data/campana/sidecar_{id_corrida or '<id-corrida>'}.json"
    )


def validar_argumentos(args: argparse.Namespace) -> list[str]:
    """Errores de uso del modo campana (lista vacia si no hay ninguno). Funcion pura.

    Se evalua antes de leer el corpus o las credenciales y de enviar nada. ``--json`` y
    ``--sidecar`` (los que el harness tenga) no pueden apuntar a un archivo versionado.
    """
    errores: list[str] = []
    if args.plan and getattr(args, "orden", None):
        errores.append(
            "--plan y --orden son excluyentes: --plan sigue un plan ya generado y --orden "
            "genera uno al vuelo."
        )
    if esta_activo(args) and not args.id_corrida:
        errores.append(
            "--id-corrida es obligatorio con --plan/--orden: identifica la corrida en cada "
            "entrada del sidecar."
        )
    if esta_activo(args) and args.sidecar is None:
        errores.append(
            "--sidecar es obligatorio con --plan/--orden y debe ser propio de la corrida (sin "
            f"default), por ejemplo evaluation/data/campana/sidecar_{args.id_corrida or '<id-corrida>'}.json"
        )
    if esta_activo(args):
        for flag in ("json", "sidecar"):
            valor = getattr(args, flag, None)
            if valor is not None and pc.es_archivo_congelado(valor):
                errores.append(_error_archivo_congelado(flag, valor, args.id_corrida))
    if args.plan and args.limit is not None:
        errores.append(
            "--limit no se admite con --plan: el plan ya es la seleccion de casos. Para acotarla "
            "genera un plan mas chico (python -m evaluation.plan_campana generar --limit N) o "
            "un sub-plan (python -m evaluation.plan_campana subplan)."
        )
    return errores


def verificar_sidecar_nuevo(ruta: str | Path) -> str | None:
    """Motivo del rechazo si ``ruta`` ya existe; ``None`` si se puede crear.

    Es la regla de los harnesses cuyo writer sobrescribe el sidecar entero: no hay
    reanudacion, cada corrida de campana usa otro ``--id-corrida`` y otro ``--sidecar``.
    """
    if Path(ruta).exists():
        return (
            f"el sidecar {ruta} ya existe y este harness lo sobrescribe entero: no hay "
            "reanudacion. Corre con otro --id-corrida y un --sidecar nuevo."
        )
    return None


def preflight(
    args: argparse.Namespace, verificar_sidecar: Callable[[str, str], str | None]
) -> int | None:
    """Valida el modo campana ANTES de leer el corpus o las credenciales.

    Devuelve ``None`` si se puede seguir (tambien fuera del modo campana) o el codigo de
    salida de un error de uso, ya informado en stderr. ``verificar_sidecar(ruta,
    id_corrida)`` es la politica de sidecar del harness: devuelve el motivo del rechazo
    o ``None``.
    """
    errores = validar_argumentos(args)
    if not errores and esta_activo(args):
        motivo = verificar_sidecar(args.sidecar, args.id_corrida)
        errores = [motivo] if motivo else []
    for error in errores:
        informar_error(error)
    return CODIGO_USO if errores else None


@dataclass(frozen=True)
class SeleccionCampana:
    """Casos a procesar, en orden, y la asignacion del plan para cada ``case_id``."""

    casos: list[Any]
    asignaciones: dict[str, pc.AsignacionCaso]


def ruta_plan_generado(sidecar: str | Path) -> Path:
    """Donde ``--orden`` deja el plan que genero: junto al sidecar, ``<sidecar>.plan.csv``."""
    return Path(f"{sidecar}.plan.csv")


def _persistir_plan_generado(plan: list[pc.AsignacionCaso], ruta: Path) -> None:
    """Escribe el plan; si ya hay uno, solo se acepta el identico (reanudar la corrida)."""
    if ruta.exists():
        if pc.leer_plan_csv(ruta) != plan:
            raise pc.PlanCampanaError(
                f"{ruta} ya existe con un plan distinto: la corrida ya se inicio con otro "
                "orden o semilla. Reanudala con los mismos --orden/--seed o usa otro --id-corrida "
                "y otro --sidecar."
            )
        return
    pc.escribir_plan_csv(plan, ruta)


def seleccionar_casos(
    args: argparse.Namespace,
    todos: Sequence[Any],
    seleccionar_base: Callable[[Sequence[Any]], list[Any]],
) -> SeleccionCampana:
    """Resuelve los casos de la corrida de campana, en el orden del plan.

    ``seleccionar_base`` aplica el filtro de canal y el ``--limit`` del harness. Con
    ``--orden`` se aplica ANTES de ordenar (``--limit 3 --orden inverso`` da el reverso de
    los tres primeros). Los casos deben exponer ``case_id``. Con ``--plan`` se envian los
    casos del plan (completo o sub-plan) en el orden de ``posicion``; un ``id_caso`` ausente
    del corpus levanta ``PlanCampanaError``. Con ``--orden`` el plan generado se escribe
    junto al sidecar (``<sidecar>.plan.csv``), salvo en un ``--dry-run``.
    """
    if args.plan:
        plan = pc.leer_plan_csv(args.plan, completo=False)  # acepta sub-planes
        por_id = {caso.case_id: caso for caso in todos}
        ausentes = [fila.id_caso for fila in plan if fila.id_caso not in por_id]
        if ausentes:
            resto = " ..." if len(ausentes) > 10 else ""
            raise pc.PlanCampanaError(
                f"el plan {args.plan} incluye casos que no estan en el corpus: "
                f"{', '.join(ausentes[:10])}{resto}."
            )
        casos = seleccionar_base([por_id[fila.id_caso] for fila in plan])
    else:
        base = seleccionar_base(list(todos))
        plan = pc.generar_plan_campana([caso.case_id for caso in base], args.orden, args.seed)
        if not args.dry_run:
            _persistir_plan_generado(plan, ruta_plan_generado(args.sidecar))
        por_id = {caso.case_id: caso for caso in base}
        casos = [por_id[fila.id_caso] for fila in plan]
    return SeleccionCampana(casos=casos, asignaciones={fila.id_caso: fila for fila in plan})


def anotar_resultados(
    resultados: Sequence[Any],
    asignaciones: dict[str, pc.AsignacionCaso],
    id_corrida: str,
) -> list[Any]:
    """Copia cada resultado con ``orden``, ``posicion``, ``mitad``, ``brazo_primero`` e ``id_corrida``.

    ``orden`` guarda el modo del plan y ``posicion`` es la posicion GLOBAL del plan.
    Sirve para ``CaseResult`` y ``CorpusResult`` (ambos tienen los cinco campos).
    """
    anotados = []
    for resultado in resultados:
        fila = asignaciones[resultado.case_id]
        anotados.append(
            dataclasses.replace(
                resultado,
                orden=fila.modo,
                posicion=fila.posicion,
                mitad=fila.mitad,
                brazo_primero=fila.brazo_primero,
                id_corrida=id_corrida,
            )
        )
    return anotados
