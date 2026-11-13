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
import hashlib
import json
import pathlib
import sys
from collections import Counter
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

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
# Ensamblado del corpus final arbitrado (tarea 4.5)
# ---------------------------------------------------------------------------
#: Nombre canonico del corpus final y del sidecar de banderas en `E/`.
NOMBRE_CORPUS_ARBITRADO = "corpus_independiente_arbitrado.json"
NOMBRE_SIDECAR_TRES_VIAS = "arbitraje_tres_vias.json"

#: Esquema del corpus arbitrado: identico al de `corpus_independiente.json`.
COLUMNAS_CASO_CORPUS: tuple[str, ...] = (
    "id",
    "descripcion",
    "canal_origen",
    "sector_asignado",
    "sectores_adicionales",
    "tiempo_manual_s",
    "tiempo_automatizado_s",
)

DESCRIPCION_CORPUS_ARBITRADO = (
    "Corpus independiente arbitrado (c-206) de la validacion fuera de muestra: la referencia "
    "es el consenso de E3/E4 cuando coinciden y la etiqueta del tercero E5 cuando difieren; los "
    "adicionales son los marcados por al menos dos de los tres. Las descripciones son el texto "
    "pseudonimizado y los tiempos salen del JSON de trabajo."
)
DESCRIPCION_SIDECAR_TRES_VIAS = (
    "Sidecar del arbitraje (c-206): por caso, el origen de la referencia "
    "(consenso_e3_e4 | arbitraje_e5) y la bandera de discordancia residual de tres vias. Nace "
    "separado de corpus_independiente_arbitrado.json para no cambiar el esquema de cargar_corpus."
)


class EnsambladoError(ValueError):
    """El JSON de trabajo no cubre los casos arbitrados o trae casos sin etiqueta."""


@dataclass(frozen=True)
class Ensamblado:
    """Corpus arbitrado y su sidecar, con su serializacion determinista y sus SHA-256."""

    corpus: dict[str, Any]
    sidecar: dict[str, Any]
    texto_corpus: str
    texto_sidecar: str
    sha256_corpus: str
    sha256_sidecar: str


def _serializar(documento: Mapping[str, Any]) -> str:
    """Serializacion determinista (misma que el corpus versionado: indent 2, LF, sin BOM)."""
    return json.dumps(documento, ensure_ascii=False, indent=2) + "\n"


def ensamblar_corpus(
    registros: Sequence[Mapping[str, str | None]],
    corpus_trabajo: Sequence[CasoEvaluacion],
) -> Ensamblado:
    """Arma el corpus final arbitrado (esquema de `corpus_independiente.json`) y su sidecar.

    Reutiliza `construir_referencia` (consenso `E3`/`E4`; `E5` en los discordantes; adicionales
    por mayoria de dos de tres). Toma las descripciones, el canal y los tiempos del JSON de
    trabajo y sobreescribe `sector_asignado`/`sectores_adicionales` con la referencia. La bandera
    `tres_vias` y el `origen` viven SOLO en el sidecar (decision D9): el esquema del corpus no
    cambia.

    Raises:
        ArbitrajeError: Un discordante no tiene la etiqueta de `E5`.
        EnsambladoError: El JSON de trabajo no tiene un caso arbitrado o trae un caso sin etiqueta.
    """
    referencia = construir_referencia(registros)
    por_id = {caso.id: caso for caso in corpus_trabajo}
    ids_referencia = {ref.id_caso for ref in referencia}
    faltantes = sorted(ids_referencia - set(por_id))
    if faltantes:
        raise EnsambladoError(
            f"el JSON de trabajo no tiene el caso arbitrado {faltantes[0]} (sin descripcion)"
        )
    sin_etiqueta = sorted(set(por_id) - ids_referencia)
    if sin_etiqueta:
        raise EnsambladoError(
            f"el JSON de trabajo trae el caso {sin_etiqueta[0]} sin etiqueta de E3/E4/E5"
        )
    casos = []
    banderas = []
    for ref in referencia:
        caso = por_id[ref.id_caso]
        casos.append(
            {
                "id": ref.id_caso,
                "descripcion": caso.descripcion,
                "canal_origen": caso.canal_origen,
                "sector_asignado": ref.sector,
                "sectores_adicionales": list(ref.sectores_adicionales),
                "tiempo_manual_s": caso.tiempo_manual_s,
                "tiempo_automatizado_s": caso.tiempo_automatizado_s,
            }
        )
        banderas.append(
            {"id": ref.id_caso, "origen": ref.origen, "tres_vias": ref.tres_vias}
        )
    corpus = {
        "schema_version": 1,
        "metadata": {"descripcion": DESCRIPCION_CORPUS_ARBITRADO, "total_casos": len(casos)},
        "casos": casos,
    }
    texto_corpus = _serializar(corpus)
    sha256_corpus = hashlib.sha256(texto_corpus.encode("utf-8")).hexdigest()
    sidecar = {
        "schema_version": 1,
        "metadata": {
            "descripcion": DESCRIPCION_SIDECAR_TRES_VIAS,
            "total_casos": len(banderas),
            "n_arbitraje_e5": sum(1 for ref in referencia if ref.origen == ORIGEN_ARBITRAJE),
            "n_tres_vias": sum(1 for ref in referencia if ref.tres_vias),
            "corpus": NOMBRE_CORPUS_ARBITRADO,
            "corpus_sha256": sha256_corpus,
        },
        "casos": banderas,
    }
    texto_sidecar = _serializar(sidecar)
    return Ensamblado(
        corpus=corpus,
        sidecar=sidecar,
        texto_corpus=texto_corpus,
        texto_sidecar=texto_sidecar,
        sha256_corpus=sha256_corpus,
        sha256_sidecar=hashlib.sha256(texto_sidecar.encode("utf-8")).hexdigest(),
    )


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.arbitraje",
        description=(
            "Arbitraje de los discordantes (E3/E4/E5): validar la planilla, armar la hoja "
            "ciega o ensamblar el corpus final arbitrado."
        ),
    )
    sub = parser.add_subparsers(dest="comando", required=True)
    validar = sub.add_parser("validar", help="valida la planilla con E3, E4 y E5")
    validar.add_argument("--planilla", required=True, type=pathlib.Path)
    validar.add_argument("--corpus", required=True, type=pathlib.Path)
    hoja = sub.add_parser("hoja-ciega", help="arma la hoja ciega (id_caso,descripcion) de E5")
    hoja.add_argument("--primaria", required=True, type=pathlib.Path, help="tabla E3/E4")
    hoja.add_argument("--corpus", required=True, type=pathlib.Path, help="JSON de trabajo")
    hoja.add_argument("--salida", required=True, type=pathlib.Path)
    ensamblar = sub.add_parser(
        "ensamblar", help="ensambla el corpus final arbitrado y su sidecar de tres vias"
    )
    ensamblar.add_argument(
        "--primaria",
        required=True,
        type=pathlib.Path,
        help="planilla E3/E4, p. ej. ~/Desktop/campana-hojas/campana_extra/doble_etiquetado_independiente.csv",
    )
    ensamblar.add_argument(
        "--arbitraje",
        required=True,
        type=pathlib.Path,
        help="planilla E5, p. ej. ~/Desktop/campana-hojas/campana_extra/E5/etiquetas_E5.csv",
    )
    ensamblar.add_argument(
        "--corpus",
        required=True,
        type=pathlib.Path,
        help="JSON de trabajo con las descripciones, p. ej. ~/Desktop/campana-hojas/campana_extra/corpus_independiente_trabajo.json",
    )
    ensamblar.add_argument(
        "--salida",
        type=pathlib.Path,
        default=pathlib.Path("evaluation/data/campana") / NOMBRE_CORPUS_ARBITRADO,
        help=f"corpus final (por defecto: evaluation/data/campana/{NOMBRE_CORPUS_ARBITRADO})",
    )
    ensamblar.add_argument(
        "--sidecar",
        type=pathlib.Path,
        default=pathlib.Path("evaluation/data/campana") / NOMBRE_SIDECAR_TRES_VIAS,
        help=f"sidecar de banderas (por defecto: evaluation/data/campana/{NOMBRE_SIDECAR_TRES_VIAS})",
    )
    return parser


def _reportar_ofensas(resultado: ResultadoValidacion) -> int:
    """Imprime las ofensas y devuelve el exit code de la primera regla ofendida."""
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
    return _reportar_ofensas(resultado)


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


def _ensamblar(args: argparse.Namespace) -> int:
    registros = _leer_planilla(args.primaria) + _leer_planilla(args.arbitraje)
    corpus = cargar_corpus(args.corpus)
    resultado = validar_arbitraje(registros, corpus)
    if not resultado.valida:
        return _reportar_ofensas(resultado)
    ensamblado = ensamblar_corpus(registros, corpus)
    args.salida.write_bytes(ensamblado.texto_corpus.encode("utf-8"))
    args.sidecar.write_bytes(ensamblado.texto_sidecar.encode("utf-8"))
    print(f"corpus arbitrado: {len(ensamblado.corpus['casos'])} casos -> {args.salida}")
    print(f"sha256 corpus: {ensamblado.sha256_corpus}")
    print(
        f"sidecar tres vias: {ensamblado.sidecar['metadata']['n_tres_vias']} casos -> "
        f"{args.sidecar}"
    )
    print(f"sha256 sidecar: {ensamblado.sha256_sidecar}")
    return EXIT_OK


def main(argv: Sequence[str] | None = None) -> int:
    """Punto de entrada del CLI. Devuelve el exit code (`0`, `2` o el de la primera regla)."""
    for flujo in (sys.stdout, sys.stderr):
        if hasattr(flujo, "reconfigure"):
            flujo.reconfigure(errors="backslashreplace")
    args = _construir_parser().parse_args(argv)
    flujos = {"validar": _validar, "hoja-ciega": _hoja_ciega, "ensamblar": _ensamblar}
    try:
        return flujos[args.comando](args)
    except (
        OSError,
        UnicodeDecodeError,
        csv.Error,
        CorpusError,
        ArbitrajeError,
        EnsambladoError,
    ) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USO


if __name__ == "__main__":
    raise SystemExit(main())
