"""
Validador de la planilla de arbitraje y constructor de la referencia arbitrada (c-206).

Los `47` casos discordantes entre `E3` y `E4` del corpus independiente los arbitra un
tercer etiquetador `E5`. Este modulo valida la planilla con EXACTAMENTE `E3`, `E4` y `E5`
y arma la referencia, sin tocar el contrato de dos etiquetadores de
`evaluation/doble_etiquetado.py` (tarea `doble_etiquetado`), cuyos helpers y reglas
(c)-(j) reutiliza.
"""

from __future__ import annotations

import argparse
import csv
import pathlib
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Mapping, Sequence

from evaluation.corpus import CasoEvaluacion, CorpusError, cargar_corpus
from evaluation.doble_etiquetado import (
    EXIT_CODE_POR_REGLA,
    EXIT_OK,
    EXIT_USO,
    TAREA_DOBLE_ETIQUETADO,
    Ofensa,
    ResultadoValidacion,
    ResumenValidacion,
    _adicionales,
    _etiquetadores,
    _leer_planilla,
    _normalizar,
    _regla_c_sin_duplicados,
    _regla_d_id_caso_conocido,
    _regla_e_sectores_canonicos,
    _regla_f_adicionales_sin_repetir_principal,
    _regla_g_instantes_iso,
    _regla_h_sin_pii,
    _regla_i_tarea_valida,
    _regla_j_inicio_coherente,
)

#: Etiquetadores de la tarea de arbitraje: dos primarios y el tercero que arbitra.
ETIQUETADORES_PRIMARIOS: tuple[str, str] = ("E3", "E4")
ETIQUETADOR_ARBITRO = "E5"
ETIQUETADORES_ARBITRAJE: tuple[str, ...] = (*ETIQUETADORES_PRIMARIOS, ETIQUETADOR_ARBITRO)

ORIGEN_CONSENSO = "consenso_e3_e4"
ORIGEN_ARBITRAJE = "arbitraje_e5"

Registro = Mapping[str, str]


class ArbitrajeError(ValueError):
    """La planilla no permite construir la referencia (p. ej. un discordante sin `E5`)."""


@dataclass(frozen=True)
class ReferenciaArbitrada:
    """Referencia de un caso: sector principal, adicionales, origen y bandera de tres vias."""

    id_caso: str
    sector: str
    sectores_adicionales: tuple[str, ...]
    origen: str
    tres_vias: bool


def _regla_a_etiquetadores_arbitraje(registros: Sequence[Registro]) -> list[Ofensa]:
    """(a) Exactamente `E3`, `E4` y `E5`: ni mas ni menos, ni alias desconocidos."""
    presentes = _etiquetadores(registros)
    sobrantes = [
        Ofensa("a", None, alias, f"etiquetador no admitido en el arbitraje: {alias}")
        for alias in presentes
        if alias not in ETIQUETADORES_ARBITRAJE
    ]
    faltantes = [
        Ofensa("a", None, alias, f"falta el etiquetador {alias} en el arbitraje")
        for alias in ETIQUETADORES_ARBITRAJE
        if alias not in presentes
    ]
    return sobrantes + faltantes


def _discordantes(registros: Sequence[Registro]) -> set[str]:
    """Ids de los casos donde `E3` y `E4` asignan un sector principal distinto."""
    sector = {(r["id_caso"], r["id_etiquetador"]): r["sector_etiquetado"] for r in registros}
    ids = {r["id_caso"] for r in registros}
    return {
        id_caso
        for id_caso in ids
        if (id_caso, "E3") in sector
        and (id_caso, "E4") in sector
        and sector[(id_caso, "E3")] != sector[(id_caso, "E4")]
    }


def _regla_b_cobertura(
    registros: Sequence[Registro], corpus: Sequence[CasoEvaluacion]
) -> list[Ofensa]:
    """(b) `E3` y `E4` registran todo el corpus; `E5` registra EXACTAMENTE los discordantes."""
    pares = {(r["id_caso"], r["id_etiquetador"]) for r in registros}
    ofensas = [
        Ofensa("b", caso.id, alias, f"el etiquetador {alias} no registro el caso")
        for caso in corpus
        for alias in ETIQUETADORES_PRIMARIOS
        if (caso.id, alias) not in pares
    ]
    discordantes = _discordantes(registros)
    ofensas += [
        Ofensa("b", id_caso, ETIQUETADOR_ARBITRO, "caso discordante sin la etiqueta de E5")
        for id_caso in sorted(discordantes)
        if (id_caso, ETIQUETADOR_ARBITRO) not in pares
    ]
    ofensas += [
        Ofensa(
            "b",
            id_caso,
            ETIQUETADOR_ARBITRO,
            "E5 solo arbitra los casos discordantes entre E3 y E4",
        )
        for id_caso, alias in sorted(pares)
        if alias == ETIQUETADOR_ARBITRO and id_caso not in discordantes
    ]
    return ofensas


def validar_arbitraje(
    registros: Sequence[Mapping[str, str | None]], corpus: Sequence[CasoEvaluacion]
) -> ResultadoValidacion:
    """Valida la planilla de arbitraje (`E3`, `E4`, `E5`) contra el corpus indicado."""
    filas = [_normalizar(r) for r in registros]
    ofensas: list[Ofensa] = []
    ofensas += _regla_a_etiquetadores_arbitraje(filas)
    ofensas += _regla_b_cobertura(filas, corpus)
    ofensas += _regla_c_sin_duplicados(filas)
    ofensas += _regla_d_id_caso_conocido(filas, corpus)
    ofensas += _regla_e_sectores_canonicos(filas)
    ofensas += _regla_f_adicionales_sin_repetir_principal(filas)
    ofensas += _regla_g_instantes_iso(filas)
    ofensas += _regla_h_sin_pii(filas, TAREA_DOBLE_ETIQUETADO)
    ofensas += _regla_i_tarea_valida(filas, TAREA_DOBLE_ETIQUETADO)
    ofensas += _regla_j_inicio_coherente(filas, TAREA_DOBLE_ETIQUETADO)
    resumen = ResumenValidacion(
        n_casos=len({r["id_caso"] for r in filas}),
        n_registros=len(filas),
        etiquetadores=tuple(_etiquetadores(filas)),
    )
    return ResultadoValidacion(ofensas=ofensas, resumen=resumen)


COLUMNAS_HOJA_CIEGA: tuple[str, str] = ("id_caso", "descripcion")


def construir_hoja_ciega(
    registros: Sequence[Mapping[str, str | None]], corpus: Sequence[CasoEvaluacion]
) -> list[dict[str, str]]:
    """Hoja ciega de `E5`: `id_caso` y `descripcion` de los discordantes, ordenados por id.

    No incluye etiquetas de `E3`/`E4`, referencia ni predicciones. Las descripciones salen del
    JSON de trabajo pseudonimizado indicado (fuera del repositorio).
    """
    descripciones = {caso.id: caso.descripcion for caso in corpus}
    filas = []
    for id_caso in sorted(_discordantes([_normalizar(r) for r in registros])):
        if id_caso not in descripciones:
            raise ArbitrajeError(f"el caso discordante {id_caso} no esta en el corpus indicado")
        filas.append({"id_caso": id_caso, "descripcion": descripciones[id_caso]})
    return filas


def construir_referencia(
    registros: Sequence[Mapping[str, str | None]],
) -> list[ReferenciaArbitrada]:
    """Referencia por caso (regla de arbitraje, design D2).

    - `E3` y `E4` coinciden: sector = consenso; adicionales = interseccion de ambos.
    - `E3` y `E4` difieren: sector = etiqueta de `E5` (tercero, no consenso); adicionales =
      los que marcan al menos dos de los tres etiquetadores, sin repetir el sector.
    - Las tres etiquetas distintas: igual que el anterior, con `tres_vias = True`.
    """
    por_caso: dict[str, dict[str, Registro]] = {}
    for registro in (_normalizar(r) for r in registros):
        por_caso.setdefault(registro["id_caso"], {})[registro["id_etiquetador"]] = registro
    referencia = []
    for id_caso in sorted(por_caso):
        etiquetas = por_caso[id_caso]
        e3, e4 = etiquetas["E3"], etiquetas["E4"]
        if e3["sector_etiquetado"] == e4["sector_etiquetado"]:
            adicionales = set(_adicionales(e3)) & set(_adicionales(e4))
            referencia.append(
                ReferenciaArbitrada(
                    id_caso,
                    e3["sector_etiquetado"],
                    tuple(sorted(adicionales - {e3["sector_etiquetado"]})),
                    ORIGEN_CONSENSO,
                    False,
                )
            )
            continue
        e5 = etiquetas.get(ETIQUETADOR_ARBITRO)
        if e5 is None:
            raise ArbitrajeError(f"el caso discordante {id_caso} no tiene la etiqueta de E5")
        sector = e5["sector_etiquetado"]
        votos = Counter(
            sector_adicional
            for registro in (e3, e4, e5)
            for sector_adicional in set(_adicionales(registro))
        )
        adicionales = {s for s, veces in votos.items() if veces >= 2} - {sector}
        tres_vias = len({e3["sector_etiquetado"], e4["sector_etiquetado"], sector}) == 3
        referencia.append(
            ReferenciaArbitrada(
                id_caso, sector, tuple(sorted(adicionales)), ORIGEN_ARBITRAJE, tres_vias
            )
        )
    return referencia


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.arbitraje",
        description="Arbitraje de los discordantes (E3/E4/E5): validar la planilla o armar la hoja ciega.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    validar = sub.add_parser("validar", help="valida la planilla con E3, E4 y E5")
    validar.add_argument("--planilla", required=True, type=pathlib.Path)
    validar.add_argument("--corpus", required=True, type=pathlib.Path)
    hoja = sub.add_parser("hoja-ciega", help="arma la hoja ciega (id_caso,descripcion) de E5")
    hoja.add_argument("--primaria", required=True, type=pathlib.Path, help="tabla E3/E4")
    hoja.add_argument("--corpus", required=True, type=pathlib.Path, help="JSON de trabajo")
    hoja.add_argument("--salida", required=True, type=pathlib.Path)
    return parser


def _validar(args: argparse.Namespace) -> int:
    registros = _leer_planilla(args.planilla)
    corpus = cargar_corpus(args.corpus)
    resultado = validar_arbitraje(registros, corpus)
    if resultado.valida:
        resumen = resultado.resumen
        print(
            f"OK: planilla de arbitraje valida (n_casos={resumen.n_casos}, "
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


def _hoja_ciega(args: argparse.Namespace) -> int:
    hoja = construir_hoja_ciega(_leer_planilla(args.primaria), cargar_corpus(args.corpus))
    with args.salida.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=list(COLUMNAS_HOJA_CIEGA), lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(hoja)
    print(f"hoja ciega: {len(hoja)} casos -> {args.salida}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI. Devuelve el exit code (`0`, `2` o el de la primera regla)."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    args = _construir_parser().parse_args(argv)
    try:
        return _validar(args) if args.comando == "validar" else _hoja_ciega(args)
    except (OSError, UnicodeDecodeError, csv.Error, CorpusError, ArbitrajeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USO


if __name__ == "__main__":
    raise SystemExit(main())
