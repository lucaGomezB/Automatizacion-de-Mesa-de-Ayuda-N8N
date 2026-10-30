"""
Validador offline de la planilla de doble etiquetado (c-168, ECM-009).

Es el UNICO validador de planillas etiquetador x caso de la campana: lo reutilizan
el doble etiquetado, el brazo manual y el corpus independiente. El esquema (siete
columnas, formato largo) esta en `evaluation/data/plantilla_etiquetado.csv`.

Reglas (cada una con su funcion privada `_regla_*`):

    (a) etiquetadores fijos por tarea        (f) adicionales sin repetir el principal
    (b) cobertura del corpus                 (g) timestamp / inicio ISO-8601 con zona
    (c) sin duplicados                       (h) sin PII y alias con la forma de la tarea
    (d) id_caso existente en el corpus       (i) tarea valida
    (e) sectores canonicos                   (j) inicio obligatorio (manual) e inicio <= fin

Uso (CLI)::

    python -m evaluation.doble_etiquetado --planilla RUTA --corpus RUTA --tarea TAREA

Sale con 0 si no hay ofensas, con el codigo de la primera regla ofendida en orden
(a)=10 ... (j)=19, o con 2 ante errores de uso o archivo ilegible. Opera sin red ni
servicios externos; solo stdlib y `evaluation.corpus` (las cinco cadenas canonicas se
importan de ahi, nunca se duplican).
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import re
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping, Sequence

from evaluation.corpus import CATEGORIAS_VALIDAS, CasoEvaluacion, CorpusError, cargar_corpus

# ---------------------------------------------------------------------------
# Esquema y constantes
# ---------------------------------------------------------------------------
#: Columnas del esquema C1, en orden (`evaluation/data/plantilla_etiquetado.csv`).
COLUMNAS_C1: tuple[str, ...] = (
    "id_caso",
    "id_etiquetador",
    "tarea",
    "sector_etiquetado",
    "sectores_adicionales_etiquetados",
    "inicio",
    "timestamp",
)

TAREA_DOBLE_ETIQUETADO = "doble_etiquetado"
TAREA_BRAZO_MANUAL = "brazo_manual"
#: Tareas admitidas (regla (i)).
TAREAS_VALIDAS: tuple[str, ...] = (TAREA_DOBLE_ETIQUETADO, TAREA_BRAZO_MANUAL)

#: Operadores del brazo manual (regla (a)): ambos deben aparecer y ningun otro.
OPERADORES_BRAZO_MANUAL: tuple[str, ...] = ("O1", "O2")

#: Separador de `sectores_adicionales_etiquetados` (no colisiona con la `,` del CSV).
SEPARADOR_ADICIONALES = "|"

#: Columnas prohibidas por contener o poder contener PII (sin distinguir mayusculas).
COLUMNAS_PII: frozenset[str] = frozenset(
    {"nombre", "email", "correo", "legajo", "telefono", "descripcion"}
)

#: Forma del alias segun la tarea: `E<n>` (doble) u `O<n>` (manual).
PATRON_ALIAS_POR_TAREA: dict[str, re.Pattern[str]] = {
    TAREA_DOBLE_ETIQUETADO: re.compile(r"E\d+"),
    TAREA_BRAZO_MANUAL: re.compile(r"O\d+"),
}

#: Exit codes del CLI: `0` sin ofensas, `2` uso o archivo ilegible, y uno por regla.
EXIT_OK = 0
EXIT_USO = 2
EXIT_CODE_POR_REGLA: dict[str, int] = {
    "a": 10,
    "b": 11,
    "c": 12,
    "d": 13,
    "e": 14,
    "f": 15,
    "g": 16,
    "h": 17,
    "i": 18,
    "j": 19,
}

Registro = Mapping[str, str]


# ---------------------------------------------------------------------------
# Resultado
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Ofensa:
    """Una violacion de una regla (a)-(j) sobre un registro o sobre la planilla."""

    regla: str
    id_caso: str | None
    id_etiquetador: str | None
    detalle: str


@dataclass(frozen=True)
class ResumenValidacion:
    """Conteos de la planilla validada."""

    n_casos: int
    n_registros: int
    etiquetadores: tuple[str, ...]


@dataclass(frozen=True)
class ResultadoValidacion:
    """Resultado de `validar_doble_etiquetado`: ofensas (en orden de regla) y resumen."""

    ofensas: list[Ofensa]
    resumen: ResumenValidacion

    @property
    def valida(self) -> bool:
        return not self.ofensas


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _ofensa(regla: str, registro: Registro, detalle: str) -> Ofensa:
    """Ofensa que identifica un registro por su `id_caso` y su `id_etiquetador`."""
    return Ofensa(regla, registro["id_caso"], registro["id_etiquetador"], detalle)


def _normalizar(registro: Mapping[str, str | None]) -> dict[str, str]:
    """Copia del registro con las siete columnas C1 como `str` (ausente o `None` = vacio)."""
    normal = dict(registro)
    for columna in COLUMNAS_C1:
        normal[columna] = registro.get(columna) or ""
    return normal


def _etiquetadores(registros: Sequence[Registro]) -> list[str]:
    return sorted({r["id_etiquetador"] for r in registros})


def _adicionales(registro: Registro) -> list[str]:
    crudo = registro["sectores_adicionales_etiquetados"]
    return crudo.split(SEPARADOR_ADICIONALES) if crudo else []


def _parsear_instante(valor: str) -> datetime | None:
    """ISO-8601 con zona horaria; `None` si no se puede parsear o carece de zona."""
    try:
        instante = datetime.fromisoformat(valor)
    except ValueError:
        return None
    return instante if instante.tzinfo is not None else None


# ---------------------------------------------------------------------------
# Reglas
# ---------------------------------------------------------------------------
def _regla_a_etiquetadores_fijos(registros: Sequence[Registro], tarea: str) -> list[Ofensa]:
    """(a) Dos etiquetadores distintos (doble) o ambos O1 y O2 y ninguno mas (manual)."""
    presentes = _etiquetadores(registros)
    if tarea == TAREA_BRAZO_MANUAL:
        sobrantes = [
            Ofensa("a", None, alias, f"operador no admitido en brazo_manual: {alias}")
            for alias in presentes
            if alias not in OPERADORES_BRAZO_MANUAL
        ]
        faltantes = [
            Ofensa("a", None, alias, f"falta el operador {alias} en brazo_manual")
            for alias in OPERADORES_BRAZO_MANUAL
            if alias not in presentes
        ]
        return sobrantes + faltantes
    ofensas = [
        Ofensa("a", None, alias, f"etiquetador sobrante: se admiten exactamente dos ({alias})")
        for alias in presentes[2:]
    ]
    if len(presentes) < 2:
        detalle = f"se requieren exactamente dos etiquetadores y hay {len(presentes)}"
        ofensas.append(Ofensa("a", None, None, detalle))
    return ofensas


def _regla_b_cobertura(
    registros: Sequence[Registro], corpus: Sequence[CasoEvaluacion], tarea: str
) -> list[Ofensa]:
    """(b) Doble: ambos etiquetadores por caso. Manual: al menos un operador por caso."""
    if tarea == TAREA_BRAZO_MANUAL:
        con_registro = {r["id_caso"] for r in registros}
        return [
            Ofensa("b", caso.id, None, "el caso no tiene registro de ningun operador")
            for caso in corpus
            if caso.id not in con_registro
        ]
    etiquetadores = _etiquetadores(registros)
    if len(etiquetadores) != 2:
        return []  # la regla (a) ya informa el conjunto de etiquetadores
    pares = {(r["id_caso"], r["id_etiquetador"]) for r in registros}
    return [
        Ofensa("b", caso.id, alias, f"el etiquetador {alias} no registro el caso")
        for caso in corpus
        for alias in etiquetadores
        if (caso.id, alias) not in pares
    ]


def _regla_c_sin_duplicados(registros: Sequence[Registro]) -> list[Ofensa]:
    """(c) Como maximo un registro por (id_caso, id_etiquetador, tarea)."""
    conteo = Counter((r["id_caso"], r["id_etiquetador"], r["tarea"]) for r in registros)
    return [
        Ofensa(
            "c",
            id_caso,
            id_etiquetador,
            f"registro duplicado ({id_caso}, {id_etiquetador}, {tarea}): {veces} filas",
        )
        for (id_caso, id_etiquetador, tarea), veces in conteo.items()
        if veces > 1
    ]


def _regla_d_id_caso_conocido(
    registros: Sequence[Registro], corpus: Sequence[CasoEvaluacion]
) -> list[Ofensa]:
    """(d) Todo id_caso existe en el corpus indicado (pertenencia, sin regex de prefijo)."""
    ids_corpus = {caso.id for caso in corpus}
    return [
        _ofensa("d", r, "id_caso inexistente en el corpus")
        for r in registros
        if r["id_caso"] not in ids_corpus
    ]


def _regla_e_sectores_canonicos(registros: Sequence[Registro]) -> list[Ofensa]:
    """(e) `sector_etiquetado` y cada adicional pertenecen al vocabulario canonico."""
    ofensas: list[Ofensa] = []
    for r in registros:
        valores = [("sector_etiquetado", r["sector_etiquetado"])]
        valores += [("sectores_adicionales_etiquetados", a) for a in _adicionales(r)]
        ofensas += [
            _ofensa("e", r, f"sector no canonico en {campo}: '{valor}'")
            for campo, valor in valores
            if valor not in CATEGORIAS_VALIDAS
        ]
    return ofensas


def _regla_f_adicionales_sin_repetir_principal(registros: Sequence[Registro]) -> list[Ofensa]:
    """(f) Los adicionales no repiten `sector_etiquetado`."""
    return [
        _ofensa("f", r, f"el adicional repite el sector principal: '{r['sector_etiquetado']}'")
        for r in registros
        if r["sector_etiquetado"] in _adicionales(r)
    ]


def _regla_g_instantes_iso(registros: Sequence[Registro]) -> list[Ofensa]:
    """(g) `timestamp`, e `inicio` si no esta vacio, son ISO-8601 con zona horaria."""
    ofensas: list[Ofensa] = []
    for r in registros:
        campos = [("timestamp", r["timestamp"])]
        if r["inicio"]:
            campos.append(("inicio", r["inicio"]))
        ofensas += [
            _ofensa("g", r, f"{campo} no es ISO-8601 con zona horaria: '{valor}'")
            for campo, valor in campos
            if _parsear_instante(valor) is None
        ]
    return ofensas


def _regla_h_sin_pii(registros: Sequence[Registro], tarea: str) -> list[Ofensa]:
    """(h) Sin columnas de PII y con alias de la forma que corresponde a la tarea."""
    columnas = dict.fromkeys(columna for r in registros for columna in r)
    ofensas = [
        Ofensa("h", None, None, f"columna con PII: '{columna}'")
        for columna in columnas
        if isinstance(columna, str) and columna.strip().lower() in COLUMNAS_PII
    ]
    patron = PATRON_ALIAS_POR_TAREA.get(tarea)
    if patron is not None:
        ofensas += [
            Ofensa("h", None, alias, f"alias sin la forma {patron.pattern} de {tarea}: '{alias}'")
            for alias in _etiquetadores(registros)
            if not patron.fullmatch(alias)
        ]
    return ofensas


def _regla_i_tarea_valida(registros: Sequence[Registro], tarea: str) -> list[Ofensa]:
    """(i) La tarea declarada y la de cada fila son validas y coinciden entre si."""
    ofensas: list[Ofensa] = []
    if tarea not in TAREAS_VALIDAS:
        detalle = f"tarea declarada invalida: '{tarea}' (validas: {', '.join(TAREAS_VALIDAS)})"
        ofensas.append(Ofensa("i", None, None, detalle))
    for r in registros:
        if r["tarea"] not in TAREAS_VALIDAS:
            ofensas.append(_ofensa("i", r, f"tarea de la fila invalida: '{r['tarea']}'"))
        elif tarea in TAREAS_VALIDAS and r["tarea"] != tarea:
            detalle = f"la fila es de '{r['tarea']}' pero la planilla se valida como '{tarea}'"
            ofensas.append(_ofensa("i", r, detalle))
    return ofensas


def _regla_j_inicio_coherente(registros: Sequence[Registro], tarea: str) -> list[Ofensa]:
    """(j) `inicio` obligatorio en brazo_manual y, si se informa, `inicio <= timestamp`."""
    ofensas: list[Ofensa] = []
    for r in registros:
        if not r["inicio"]:
            if tarea == TAREA_BRAZO_MANUAL:
                ofensas.append(_ofensa("j", r, "inicio obligatorio en brazo_manual"))
            continue
        inicio = _parsear_instante(r["inicio"])
        fin = _parsear_instante(r["timestamp"])
        if inicio is not None and fin is not None and inicio > fin:
            detalle = f"inicio posterior al fin: {r['inicio']} > {r['timestamp']}"
            ofensas.append(_ofensa("j", r, detalle))
    return ofensas


# ---------------------------------------------------------------------------
# Validador
# ---------------------------------------------------------------------------
def validar_doble_etiquetado(
    registros: Sequence[Mapping[str, str | None]],
    corpus: Sequence[CasoEvaluacion],
    tarea: str,
) -> ResultadoValidacion:
    """Valida una planilla etiquetador x caso contra el corpus indicado.

    Funcion pura: no lee archivos ni usa red. Evalua las reglas (a)-(j) y devuelve
    TODAS las ofensas, ordenadas por regla. Con una `tarea` declarada invalida solo
    se evaluan las reglas que no dependen de ella (ademas de (i)).
    """
    filas = [_normalizar(r) for r in registros]
    ofensas: list[Ofensa] = []
    if tarea in TAREAS_VALIDAS:  # (a) y (b) dependen de la tarea declarada
        ofensas += _regla_a_etiquetadores_fijos(filas, tarea)
        ofensas += _regla_b_cobertura(filas, corpus, tarea)
    ofensas += _regla_c_sin_duplicados(filas)
    ofensas += _regla_d_id_caso_conocido(filas, corpus)
    ofensas += _regla_e_sectores_canonicos(filas)
    ofensas += _regla_f_adicionales_sin_repetir_principal(filas)
    ofensas += _regla_g_instantes_iso(filas)
    ofensas += _regla_h_sin_pii(filas, tarea)
    ofensas += _regla_i_tarea_valida(filas, tarea)
    ofensas += _regla_j_inicio_coherente(filas, tarea)
    resumen = ResumenValidacion(
        n_casos=len({r["id_caso"] for r in filas}),
        n_registros=len(filas),
        etiquetadores=tuple(_etiquetadores(filas)),
    )
    return ResultadoValidacion(ofensas=ofensas, resumen=resumen)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _leer_planilla(ruta: pathlib.Path) -> list[dict[str, str]]:
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        return list(csv.DictReader(archivo))


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.doble_etiquetado",
        description="Valida una planilla etiquetador x caso contra un corpus (reglas (a)-(j)).",
    )
    parser.add_argument("--planilla", required=True, type=pathlib.Path, help="CSV a validar")
    parser.add_argument("--corpus", required=True, type=pathlib.Path, help="corpus JSON")
    parser.add_argument(
        "--tarea",
        required=True,
        help=f"tarea de la planilla ({' | '.join(TAREAS_VALIDAS)})",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI. Devuelve el exit code (ver `EXIT_CODE_POR_REGLA`)."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    args = _construir_parser().parse_args(argv)  # error de uso -> SystemExit(2)
    try:
        registros = _leer_planilla(args.planilla)
        corpus = cargar_corpus(args.corpus)
    except (OSError, UnicodeDecodeError, csv.Error, CorpusError) as exc:
        print(f"error: no se pudo leer la planilla o el corpus: {exc}", file=sys.stderr)
        return EXIT_USO

    resultado = validar_doble_etiquetado(registros, corpus, args.tarea)
    if resultado.valida:
        resumen = resultado.resumen
        print(
            f"OK: planilla valida (tarea={args.tarea}, n_casos={resumen.n_casos}, "
            f"n_registros={resumen.n_registros}, "
            f"etiquetadores={','.join(resumen.etiquetadores)})"
        )
        return EXIT_OK

    for ofensa in resultado.ofensas:
        print(
            f"[regla {ofensa.regla}] id_caso={ofensa.id_caso} "
            f"id_etiquetador={ofensa.id_etiquetador}: {ofensa.detalle}"
        )
    primera = min(o.regla for o in resultado.ofensas)
    codigo = EXIT_CODE_POR_REGLA[primera]
    print(
        f"FALLA: {len(resultado.ofensas)} ofensas; "
        f"primera regla ofendida: ({primera}) -> exit {codigo}"
    )
    return codigo


if __name__ == "__main__":
    raise SystemExit(main())
