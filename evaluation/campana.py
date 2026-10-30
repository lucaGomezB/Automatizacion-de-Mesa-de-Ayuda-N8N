"""
Analisis de la campana de medicion (c-167, D5 a D9).

Funciones puras y deterministas: reciben registros ya cargados (listas de dicts de CSV,
`CasoEvaluacion`, `AsignacionCaso`, `Prediccion`) y devuelven dataclasses congeladas. No
hacen I/O, salvo `cargar_corpus_solo_lectura` y `evaluar_fuera_de_muestra`, que leen
archivos con los lectores del repo y no escriben nada. Secciones:

1. Registro de sujetos (C2) y referencia del brazo manual.
2. Exactitud del brazo manual por operador y agregada, y contraste manual vs automatizado.
3. Tasa de intervencion humana de campana y proporcion de tiempo.
4. Efecto de orden de condicion y de posicion del operador.
5. Evaluacion fuera de muestra con el clasificador congelado.

Nada de esto escribe `evaluation/report.md` ni `evaluation/predicciones.json`, ni invoca
`run_evaluation.main()` (que llama a Gemini). La exactitud de v9 contra la referencia nueva es
un numero NUEVO y rotulado: no reemplaza los numeros canonicos de v9.
"""

from __future__ import annotations

import math
import pathlib
import random
import re
import shutil
import tempfile
from collections import Counter
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Mapping, Sequence

from evaluation.brazo_manual import desvios_respecto_del_plan, reconstruir_posicion_real
from evaluation.corpus import SECTORES_CANONICOS, CasoEvaluacion, cargar_corpus
from evaluation.doble_etiquetado import (
    SEPARADOR_ADICIONALES,
    TAREA_BRAZO_MANUAL,
    TAREA_DOBLE_ETIQUETADO,
)
from evaluation.kappa import parear_doble_etiquetado
from evaluation.metrics import (
    ETAPAS_PIPELINE,
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    ResumenExactitud,
    desglose_exactitud,
    intervalo_wilson,
    percentil_intervalo,
    remuestreos_indices,
    resumen_exactitud,
)
from evaluation.no_solape import SolapeError, verificar_no_solape
from evaluation.plan_campana import BRAZO_AUTOMATIZADO, BRAZO_MANUAL, AsignacionCaso
from evaluation.run_evaluation import Prediccion, cargar_cache_meta, cargar_predicciones
from evaluation.stats import (
    ARE_WILCOXON_MINIMA,
    ResultadoMcNemar,
    contraste_mcnemar,
    efecto_minimo_detectable,
    tamano_efecto_dz,
    wilcoxon_tiempos_detallado,
)

# ---------------------------------------------------------------------------
# 1. Registro de sujetos (C2)
# ---------------------------------------------------------------------------
ROL_ETIQUETADOR = "etiquetador"
ROL_OPERADOR = "operador"
ROL_ANALISTA_ORIGINAL = "analista_original"
ROL_AUTOR = "autor"
#: Roles admitidos en `registro_sujetos.csv`.
ROLES_VALIDOS: tuple[str, ...] = (
    ROL_ETIQUETADOR,
    ROL_OPERADOR,
    ROL_ANALISTA_ORIGINAL,
    ROL_AUTOR,
)
#: Roles que un alias de la planilla NO puede tener (ni su persona): las personas del consenso
#: original y los autores no pueden etiquetar de nuevo ni operar el brazo manual.
ROLES_EXCLUIDOS_DE_LA_PLANILLA: tuple[str, ...] = (ROL_ANALISTA_ORIGINAL, ROL_AUTOR)
#: Rol que corresponde al alias de cada tarea de la planilla.
ROL_ESPERADO_POR_TAREA: dict[str, str] = {
    TAREA_DOBLE_ETIQUETADO: ROL_ETIQUETADOR,
    TAREA_BRAZO_MANUAL: ROL_OPERADOR,
}
#: Columnas de `registro_sujetos.csv`.
COLUMNAS_REGISTRO_SUJETOS: tuple[str, ...] = ("alias", "rol", "persona")

Fila = Mapping[str, str]


class RegistroSujetosError(ValueError):
    """El registro de sujetos incumple la independencia de roles (el mensaje nombra todo)."""


def _entradas_del_registro(registro: Sequence[Fila]) -> list[tuple[str, str, str]]:
    """Filas `(alias, rol, persona)` sin repetidas exactas; exige las tres columnas."""
    entradas: list[tuple[str, str, str]] = []
    for fila in registro:
        for columna in COLUMNAS_REGISTRO_SUJETOS:
            if columna not in fila:
                raise RegistroSujetosError(
                    f"el registro_sujetos no tiene la columna {columna!r} "
                    f"(columnas esperadas: {', '.join(COLUMNAS_REGISTRO_SUJETOS)})."
                )
        entrada = (fila["alias"].strip(), fila["rol"].strip(), fila["persona"].strip())
        if entrada not in entradas:
            entradas.append(entrada)
    return entradas


def validar_registro_sujetos(registro: Sequence[Fila], planilla: Sequence[Fila]) -> tuple[str, ...]:
    """
    Verifica la independencia de los sujetos (C2) y devuelve los alias de la planilla verificados.

    El control de solape es por `persona`, no por alias, porque una persona puede tener varios
    alias. Falla con `RegistroSujetosError` (un `ValueError`) que nombra persona, alias y roles,
    juntando todos los problemas, si:

    - una misma `persona` figura con mas de un rol;
    - un alias figura con mas de un rol o de una persona, o con un rol desconocido o sin persona;
    - un `id_etiquetador` de la planilla no figura en el registro;
    - el rol de un alias de la planilla no corresponde a su tarea (`etiquetador` en
      `doble_etiquetado`, `operador` en `brazo_manual`);
    - la persona de un alias de la planilla tiene rol `analista_original` o `autor`.
    """
    entradas = _entradas_del_registro(registro)
    problemas: list[str] = []

    roles_de_alias: dict[str, set[str]] = {}
    personas_de_alias: dict[str, set[str]] = {}
    alias_de_persona: dict[str, list[tuple[str, str]]] = {}
    for alias, rol, persona in entradas:
        if rol not in ROLES_VALIDOS:
            problemas.append(
                f"el alias {alias} tiene un rol desconocido: {rol!r} "
                f"(validos: {', '.join(ROLES_VALIDOS)})"
            )
        if not persona:
            problemas.append(f"el alias {alias} no tiene persona")
        roles_de_alias.setdefault(alias, set()).add(rol)
        personas_de_alias.setdefault(alias, set()).add(persona)
        alias_de_persona.setdefault(persona, []).append((alias, rol))

    for alias in sorted(roles_de_alias):
        if len(roles_de_alias[alias]) > 1 or len(personas_de_alias[alias]) > 1:
            problemas.append(
                f"el alias {alias} figura con mas de un rol ({', '.join(sorted(roles_de_alias[alias]))}) "
                f"o de una persona ({', '.join(sorted(personas_de_alias[alias]))})"
            )
    for persona in sorted(alias_de_persona):
        pares = alias_de_persona[persona]
        if persona and len({rol for _, rol in pares}) > 1:
            detalle = ", ".join(f"alias {alias} como {rol}" for alias, rol in sorted(pares))
            problemas.append(f"la persona {persona} figura con mas de un rol: {detalle}")

    alias_de_la_planilla = sorted({(f["id_etiquetador"], f["tarea"]) for f in planilla})
    for alias, tarea in alias_de_la_planilla:
        if alias not in roles_de_alias:
            problemas.append(
                f"el alias {alias} de la planilla ({tarea}) no figura en el registro_sujetos"
            )
            continue
        esperado = ROL_ESPERADO_POR_TAREA.get(tarea)
        roles = roles_de_alias[alias]
        if esperado is not None and roles != {esperado}:
            problemas.append(
                f"el alias {alias} de la planilla ({tarea}) tiene el rol "
                f"{', '.join(sorted(roles))} y deberia ser {esperado}"
            )
        for persona in sorted(personas_de_alias[alias]):
            roles_de_la_persona = {rol for _, rol in alias_de_persona.get(persona, [])}
            excluidos = sorted(roles_de_la_persona & set(ROLES_EXCLUIDOS_DE_LA_PLANILLA))
            if excluidos:
                problemas.append(
                    f"el alias {alias} de la planilla corresponde a la persona {persona}, "
                    f"que tiene el rol {', '.join(excluidos)}"
                )

    if problemas:
        raise RegistroSujetosError(
            "el registro_sujetos no garantiza la independencia de los sujetos: "
            + "; ".join(problemas)
            + "."
        )
    return tuple(alias for alias, _ in sorted({(a, t) for a, t in alias_de_la_planilla}))


# ---------------------------------------------------------------------------
# 1b. Referencia del brazo manual
# ---------------------------------------------------------------------------
REFERENCIA_CONSENSO_NUEVO = "consenso_doble_etiquetado"
REFERENCIA_CONSENSO_ORIGINAL = "consenso_original"
#: Referencias admitidas; la primera es la que se usa por defecto.
REFERENCIAS: tuple[str, ...] = (REFERENCIA_CONSENSO_NUEVO, REFERENCIA_CONSENSO_ORIGINAL)

ADVERTENCIA_SESGO_DISCORDANTES = (
    "La exclusion de los casos discordantes (E1 distinto de E2) sesga la referencia hacia "
    "casos faciles y tiende a sobrestimar la exactitud de ambos brazos."
)


@dataclass(frozen=True)
class CasoReferencia:
    """Sector de referencia de un caso y su conjunto de verdad (para la exactitud laxa)."""

    id_caso: str
    sector: str
    conjunto_verdad: frozenset[str]


@dataclass(frozen=True)
class Referencia:
    """
    Referencia contra la que se mide el brazo manual.

    `casos` indexa por `id_caso` solo los casos que entran en la medicion; `discordantes` son
    los ids excluidos porque E1 y E2 no coinciden (siempre vacio con `consenso_original`).
    Toda salida del analisis declara `rotulo`.
    """

    rotulo: str
    casos: dict[str, CasoReferencia]
    discordantes: tuple[str, ...]
    advertencias: tuple[str, ...]

    @property
    def n_discordantes(self) -> int:
        return len(self.discordantes)


def _adicionales(registro: Fila) -> set[str]:
    """Sectores de `sectores_adicionales_etiquetados` (separador `|`), sin vacios."""
    crudo = registro.get("sectores_adicionales_etiquetados") or ""
    return {sector.strip() for sector in crudo.split(SEPARADOR_ADICIONALES) if sector.strip()}


def construir_referencia(
    rotulo: str,
    *,
    doble_etiquetado: Sequence[Fila] | None = None,
    corpus: Sequence[CasoEvaluacion] | None = None,
) -> Referencia:
    """
    Referencia del brazo manual, rotulada.

    - `consenso_doble_etiquetado` (por defecto): los casos donde E1 y E2 coinciden en
      `sector_etiquetado`. El conjunto de verdad es el sector consensuado mas la INTERSECCION
      de los adicionales de E1 y E2 (solo lo que ambos marcaron). Los discordantes quedan
      afuera y se declaran (ids y advertencia de sesgo hacia casos faciles). Necesita
      `doble_etiquetado` (filas de la planilla de C1; se usan las de esa tarea).
    - `consenso_original`: `sector_asignado` y `conjunto_verdad` del corpus, idem al brazo
      automatizado de v9. Necesita `corpus`.

    Raises:
        ValueError: Rotulo desconocido, falta la entrada que la referencia necesita o la
            planilla no cumple la condicion de dos etiquetadores fijos.
    """
    if rotulo == REFERENCIA_CONSENSO_NUEVO:
        if doble_etiquetado is None:
            raise ValueError(
                f"la referencia {rotulo} exige la planilla de {TAREA_DOBLE_ETIQUETADO} "
                "(parametro doble_etiquetado)."
            )
        _, pares = parear_doble_etiquetado(doble_etiquetado)
        casos: dict[str, CasoReferencia] = {}
        discordantes: list[str] = []
        for par in pares:
            sector = par.registro_1["sector_etiquetado"]
            if sector != par.registro_2["sector_etiquetado"]:
                discordantes.append(par.id_caso)
                continue
            adicionales = _adicionales(par.registro_1) & _adicionales(par.registro_2)
            casos[par.id_caso] = CasoReferencia(par.id_caso, sector, frozenset({sector, *adicionales}))
        advertencias = (ADVERTENCIA_SESGO_DISCORDANTES,) if discordantes else ()
        return Referencia(rotulo, casos, tuple(discordantes), advertencias)
    if rotulo == REFERENCIA_CONSENSO_ORIGINAL:
        if corpus is None:
            raise ValueError(f"la referencia {rotulo} exige el corpus (parametro corpus).")
        casos = {
            caso.id: CasoReferencia(caso.id, caso.sector_asignado, caso.conjunto_verdad)
            for caso in corpus
        }
        return Referencia(rotulo, casos, (), ())
    raise ValueError(
        f"referencia desconocida: {rotulo!r} (validas: {', '.join(REFERENCIAS)})."
    )


# ---------------------------------------------------------------------------
# 2. Exactitud del brazo manual
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class CoberturaOperador:
    """
    Casos que cubrio un operador del brazo manual.

    `etiquetados`, `compartidos` y `exclusivos` describen el reparto de la planilla (un caso
    compartido lo etiqueto tambien otro operador); `evaluados` son los etiquetados que entran
    en la referencia y `excluidos_por_discordancia` los que quedaron afuera porque E1 y E2 no
    coinciden. Un caso no etiquetado por un operador no es un error de ese operador.
    """

    id_etiquetador: str
    etiquetados: int
    compartidos: int
    exclusivos: int
    evaluados: int
    excluidos_por_discordancia: int


METODO_IC_AGREGADA = "bootstrap percentil por caso"


@dataclass(frozen=True)
class ExactitudAgregada:
    """
    Exactitud agregada del brazo manual: aciertos / etiquetas sobre la UNION de casos.

    Cada caso aporta las etiquetas (una o dos) de los operadores que lo etiquetaron. El IC es
    un bootstrap percentil que remuestrea CASOS, no etiquetas: un IC de Wilson sobre el total
    de etiquetas contaria dos veces los casos compartidos (pseudo-replicacion) y saldria
    demasiado angosto.
    """

    casos: int
    etiquetas: int
    aciertos_estrictos: int
    aciertos_laxos: int
    exactitud_estricta: float
    ic_estricta: tuple[float, float]
    exactitud_laxa: float
    ic_laxa: tuple[float, float]
    metodo_ic: str
    nivel_confianza: float
    semilla: int
    remuestreos: int


@dataclass(frozen=True)
class ContrasteManualAutomatizado:
    """
    McNemar entre el acierto estricto de un operador y el de la prediccion v9 del mismo caso.

    El pareo es por `(id_caso, id_etiquetador)`: los pares son los casos de la referencia que
    el operador etiqueto y para los que hay prediccion (`pares_clave`); los que no la tienen
    quedan en `sin_prediccion`. En `mcnemar`, `solo_a` son los pares que acierta SOLO el
    operador y `solo_b` los que acierta SOLO v9.
    """

    id_etiquetador: str
    pares_clave: tuple[tuple[str, str], ...]
    sin_prediccion: tuple[str, ...]
    mcnemar: ResultadoMcNemar


@dataclass(frozen=True)
class ResultadoExactitudManual:
    """Exactitud del brazo manual por operador, con la referencia usada y la cobertura."""

    referencia_usada: str
    nivel_confianza: float
    por_operador: dict[str, ResumenExactitud]
    agregada: ExactitudAgregada | None
    contraste_vs_automatizado: tuple[ContrasteManualAutomatizado, ...]
    automatizado: ResumenExactitud | None
    nota_automatizado: str | None
    cobertura: tuple[CoberturaOperador, ...]
    discordantes: tuple[str, ...]
    n_discordantes: int
    advertencias: tuple[str, ...]


ADVERTENCIA_COBERTURAS_DISTINTAS = (
    "Las coberturas de los operadores difieren (casos exclusivos de cada uno): la comparacion "
    "entre operadores mezcla operador con dificultad de los casos."
)


def _filas_del_brazo_manual(planilla: Sequence[Fila]) -> list[Fila]:
    """Filas `tarea = brazo_manual`, ordenadas por (caso, operador) y verificadas."""
    filas = sorted(
        (f for f in planilla if f["tarea"] == TAREA_BRAZO_MANUAL),
        key=lambda f: (f["id_caso"], f["id_etiquetador"]),
    )
    if not filas:
        raise ValueError(f"la planilla no tiene filas con tarea = {TAREA_BRAZO_MANUAL}.")
    vistos: set[tuple[str, str]] = set()
    for fila in filas:
        clave = (fila["id_caso"], fila["id_etiquetador"])
        if clave in vistos:
            raise ValueError(
                f"el caso {clave[0]} tiene mas de un registro del operador {clave[1]} en "
                f"{TAREA_BRAZO_MANUAL}."
            )
        vistos.add(clave)
        if fila["sector_etiquetado"] not in SECTORES_CANONICOS:
            raise ValueError(
                f"el caso {clave[0]} del operador {clave[1]} tiene un sector no canonico: "
                f"{fila['sector_etiquetado']!r}."
            )
    return filas


def _evaluables(
    filas: Sequence[Fila], referencia: Referencia
) -> tuple[list[tuple[Fila, CasoReferencia]], Counter[str]]:
    """Filas con su referencia y, por operador, cuantas quedaron afuera por discordancia."""
    evaluadas: list[tuple[Fila, CasoReferencia]] = []
    excluidas: Counter[str] = Counter()
    for fila in filas:
        id_caso, operador = fila["id_caso"], fila["id_etiquetador"]
        if id_caso in referencia.casos:
            evaluadas.append((fila, referencia.casos[id_caso]))
        elif id_caso in referencia.discordantes:
            excluidas[operador] += 1
        else:
            raise ValueError(
                f"el caso {id_caso} del operador {operador} no figura en la referencia "
                f"{referencia.rotulo}."
            )
    return evaluadas, excluidas


def _cobertura(
    filas: Sequence[Fila], evaluadas: Sequence[tuple[Fila, CasoReferencia]], excluidas: Counter[str]
) -> tuple[CoberturaOperador, ...]:
    casos_de: dict[str, set[str]] = {}
    for fila in filas:
        casos_de.setdefault(fila["id_etiquetador"], set()).add(fila["id_caso"])
    evaluados = Counter(fila["id_etiquetador"] for fila, _ in evaluadas)
    cobertura: list[CoberturaOperador] = []
    for operador in sorted(casos_de):
        de_otros = set().union(*(c for o, c in casos_de.items() if o != operador))
        compartidos = len(casos_de[operador] & de_otros)
        cobertura.append(
            CoberturaOperador(
                id_etiquetador=operador,
                etiquetados=len(casos_de[operador]),
                compartidos=compartidos,
                exclusivos=len(casos_de[operador]) - compartidos,
                evaluados=evaluados[operador],
                excluidos_por_discordancia=excluidas[operador],
            )
        )
    return tuple(cobertura)


def _exactitud_agregada(
    evaluadas: Sequence[tuple[Fila, CasoReferencia]], semilla: int, remuestreos: int
) -> ExactitudAgregada | None:
    """Aciertos / etiquetas de la union de casos, con IC bootstrap percentil por caso."""
    por_caso: dict[str, list[int]] = {}
    for fila, caso in evaluadas:
        unidad = por_caso.setdefault(fila["id_caso"], [0, 0, 0])
        unidad[0] += fila["sector_etiquetado"] == caso.sector
        unidad[1] += fila["sector_etiquetado"] in caso.conjunto_verdad
        unidad[2] += 1
    if not por_caso:
        return None
    unidades = [por_caso[id_caso] for id_caso in sorted(por_caso)]
    estrictas: list[float] = []
    laxas: list[float] = []
    generador = random.Random(semilla)
    for indices in remuestreos_indices(generador, len(unidades), remuestreos):
        etiquetas = sum(unidades[i][2] for i in indices)
        estrictas.append(sum(unidades[i][0] for i in indices) / etiquetas)
        laxas.append(sum(unidades[i][1] for i in indices) / etiquetas)
    etiquetas_totales = sum(u[2] for u in unidades)
    estrictos = sum(u[0] for u in unidades)
    laxos = sum(u[1] for u in unidades)
    return ExactitudAgregada(
        casos=len(unidades),
        etiquetas=etiquetas_totales,
        aciertos_estrictos=estrictos,
        aciertos_laxos=laxos,
        exactitud_estricta=estrictos / etiquetas_totales,
        ic_estricta=percentil_intervalo(estrictas, NIVEL_CONFIANZA),
        exactitud_laxa=laxos / etiquetas_totales,
        ic_laxa=percentil_intervalo(laxas, NIVEL_CONFIANZA),
        metodo_ic=METODO_IC_AGREGADA,
        nivel_confianza=NIVEL_CONFIANZA,
        semilla=semilla,
        remuestreos=remuestreos,
    )


def _predicciones_por_caso(predicciones: Sequence[Prediccion]) -> dict[str, Prediccion]:
    """Indexa las predicciones por `caso_id`; un caso con dos predicciones es un error."""
    por_caso: dict[str, Prediccion] = {}
    for prediccion in predicciones:
        if prediccion.caso_id in por_caso:
            raise ValueError(f"el caso {prediccion.caso_id} tiene mas de una prediccion.")
        por_caso[prediccion.caso_id] = prediccion
    return por_caso


def _contrastes_vs_automatizado(
    evaluadas: Sequence[tuple[Fila, CasoReferencia]],
    predicciones: dict[str, Prediccion],
) -> tuple[ContrasteManualAutomatizado, ...]:
    """Un McNemar por operador sobre sus casos evaluados que tienen prediccion v9."""
    contrastes: list[ContrasteManualAutomatizado] = []
    for operador in sorted({fila["id_etiquetador"] for fila, _ in evaluadas}):
        pares: list[tuple[str, str]] = []
        aciertos_operador: list[bool] = []
        aciertos_v9: list[bool] = []
        sin_prediccion: list[str] = []
        for fila, caso in evaluadas:
            if fila["id_etiquetador"] != operador:
                continue
            prediccion = predicciones.get(fila["id_caso"])
            if prediccion is None:
                sin_prediccion.append(fila["id_caso"])
                continue
            pares.append((fila["id_caso"], operador))
            aciertos_operador.append(fila["sector_etiquetado"] == caso.sector)
            aciertos_v9.append(prediccion.sector_predicho == caso.sector)
        contrastes.append(
            ContrasteManualAutomatizado(
                id_etiquetador=operador,
                pares_clave=tuple(pares),
                sin_prediccion=tuple(sin_prediccion),
                mcnemar=contraste_mcnemar(aciertos_operador, aciertos_v9),
            )
        )
    return tuple(contrastes)


def _exactitud_v9_sobre_la_referencia(
    evaluadas: Sequence[tuple[Fila, CasoReferencia]],
    predicciones: dict[str, Prediccion],
    rotulo: str,
) -> tuple[ResumenExactitud, str]:
    """Exactitud de v9 sobre los casos evaluados del brazo manual, con su nota de rotulo."""
    casos = sorted({caso.id_caso: caso for _, caso in evaluadas}.values(), key=lambda c: c.id_caso)
    con_prediccion = [c for c in casos if c.id_caso in predicciones]
    resumen = resumen_exactitud(
        [c.sector for c in con_prediccion],
        [predicciones[c.id_caso].sector_predicho for c in con_prediccion],
        [c.conjunto_verdad for c in con_prediccion],
    )
    nota = (
        f"Exactitud de v9 contra la referencia {rotulo} sobre los {resumen.casos} casos evaluados "
        "del brazo manual: es un numero nuevo, rotulado con su referencia, y no reemplaza los "
        "numeros canonicos de v9."
    )
    return resumen, nota


def exactitud_brazo_manual(
    planilla: Sequence[Fila],
    referencia: Referencia,
    registro_sujetos: Sequence[Fila],
    predicciones: Sequence[Prediccion] | None = None,
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> ResultadoExactitudManual:
    """
    Exactitud estricta y laxa del brazo manual, por operador y sobre los casos que etiqueto.

    `planilla` son TODAS las filas de C1 (doble etiquetado y brazo manual): se usan las de
    `tarea = brazo_manual` y las demas solo para verificar la independencia de los sujetos
    con `validar_registro_sujetos(registro_sujetos, planilla)`, que falla antes de reportar
    nada si hay solape de roles. Cada operador se mide sobre los casos de la `referencia` que
    etiqueto, con la misma definicion de acierto que el brazo automatizado de v9 (reutiliza
    `desglose_exactitud`): estricto = `sector_etiquetado` igual al de la referencia; laxo =
    `sector_etiquetado` dentro del conjunto de verdad. Los casos discordantes de la referencia
    se excluyen y se cuentan. La agregada es aciertos / etiquetas sobre la union de casos, con
    IC bootstrap por caso (nunca Wilson sobre el total de etiquetas).

    Con `predicciones` (las de v9, leidas con `cargar_predicciones`; solo se leen), agrega por
    operador el McNemar manual vs automatizado pareado por `(id_caso, id_etiquetador)` contra
    el acierto estricto de v9 sobre la MISMA referencia, y la exactitud de v9 contra esa
    referencia: un numero nuevo y rotulado que no reemplaza los canonicos.

    Raises:
        RegistroSujetosError: El registro de sujetos no garantiza la independencia.
        ValueError: Sin filas de brazo manual, un registro repetido para `(caso, operador)`,
            un sector no canonico o un caso que la referencia no conoce.
    """
    validar_registro_sujetos(registro_sujetos, planilla)
    filas = _filas_del_brazo_manual(planilla)
    evaluadas, excluidas = _evaluables(filas, referencia)
    operadores = sorted({fila["id_etiquetador"] for fila in filas})
    por_operador = desglose_exactitud(
        claves=[fila["id_etiquetador"] for fila, _ in evaluadas],
        reales=[caso.sector for _, caso in evaluadas],
        predichos=[fila["sector_etiquetado"] for fila, _ in evaluadas],
        conjuntos_verdad=[caso.conjunto_verdad for _, caso in evaluadas],
        orden=operadores,
    )
    cobertura = _cobertura(filas, evaluadas, excluidas)
    advertencias = list(referencia.advertencias)
    if any(c.exclusivos for c in cobertura):
        advertencias.append(ADVERTENCIA_COBERTURAS_DISTINTAS)
    contrastes: tuple[ContrasteManualAutomatizado, ...] = ()
    automatizado: ResumenExactitud | None = None
    nota_automatizado: str | None = None
    if predicciones is not None:
        por_caso = _predicciones_por_caso(predicciones)
        contrastes = _contrastes_vs_automatizado(evaluadas, por_caso)
        automatizado, nota_automatizado = _exactitud_v9_sobre_la_referencia(
            evaluadas, por_caso, referencia.rotulo
        )
    return ResultadoExactitudManual(
        referencia_usada=referencia.rotulo,
        nivel_confianza=NIVEL_CONFIANZA,
        por_operador=por_operador,
        agregada=_exactitud_agregada(evaluadas, semilla, remuestreos),
        contraste_vs_automatizado=contrastes,
        automatizado=automatizado,
        nota_automatizado=nota_automatizado,
        cobertura=cobertura,
        discordantes=referencia.discordantes,
        n_discordantes=referencia.n_discordantes,
        advertencias=tuple(advertencias),
    )


# ---------------------------------------------------------------------------
# 3. Tasa de intervencion humana de campana (`subsec:medicion-intervencion`)
# ---------------------------------------------------------------------------
#: Cota de la sub-hipotesis 2: la tasa de intervencion humana deberia quedar por debajo.
COTA_SUBHIPOTESIS_2: float = 0.15

CONTRASTE_COMPATIBLE = "compatible"
CONTRASTE_REFUTADA = "refutada"
CONTRASTE_NO_CONCLUYENTE = "no_concluyente"

#: Vocabulario de `origen_intervencion` del export de C5 (`completado_manual` esta reservado).
ORIGENES_CONOCIDOS: tuple[str, ...] = ("gate", "muestreo", "rederivacion", "completado_manual")
#: Valores de `cambio_sector` en los desgloses, en el orden de reporte.
VALORES_CAMBIO_SECTOR: tuple[str, ...] = ("true", "false")
#: Columnas del export de C5 que usa el analisis. `actor_alias` (HMAC truncado) NO se usa.
COLUMNAS_INTERVENCION_USADAS: tuple[str, ...] = (
    "id_caso",
    "origen_intervencion",
    "cambio_sector",
    "duracion_s",
)

_BOOLEANOS = {"true": "true", "1": "true", "false": "false", "0": "false"}


@dataclass(frozen=True)
class ProporcionCasos:
    """Proporcion de casos de la corrida (`casos` de `denominador`) con IC de Wilson."""

    casos: int
    denominador: int
    proporcion: float
    ic: tuple[float, float]


@dataclass(frozen=True)
class ContrasteCota:
    """
    Contraste de la tasa contra la cota de la sub-hipotesis 2.

    - `compatible`: el limite superior del IC de Wilson queda por debajo de la cota.
    - `refutada`: la estimacion puntual alcanza o supera la cota.
    - `no_concluyente`: la estimacion queda por debajo de la cota pero el limite superior la
      alcanza o la supera.

    Siempre trae la estimacion y ambos limites para que quien redacte los lea.
    """

    cota: float
    estimacion: float
    limite_inferior: float
    limite_superior: float
    resultado: str


@dataclass(frozen=True)
class ResultadoIntervencion:
    """
    Tasa de intervencion humana de la corrida, con su contraste contra la cota.

    `casos_intervenidos` son los casos de la corrida con al menos una fila vinculada;
    `no_vinculables` las filas del export sin `id_caso` (quedan fuera de la tasa, que en ese
    caso es una cota inferior). Los desgloses cuentan casos con al menos una intervencion de
    ese origen o de ese valor de `cambio_sector`: un caso puede figurar en varios y por eso
    no suman la tasa.
    """

    casos_corrida: int
    casos_intervenidos: int
    filas: int
    no_vinculables: int
    tasa: ProporcionCasos
    contraste: ContrasteCota
    por_origen: dict[str, ProporcionCasos]
    por_cambio_sector: dict[str, ProporcionCasos]
    advertencias: tuple[str, ...]


@dataclass(frozen=True)
class FilaIntervencion:
    """Fila del export de C5 ya validada (sin `actor_alias`)."""

    numero: int
    id_caso: str | None
    origen: str
    cambio_sector: str
    duracion_s: float | None


def _proporcion_de_casos(casos: int, denominador: int) -> ProporcionCasos:
    return ProporcionCasos(
        casos=casos,
        denominador=denominador,
        proporcion=casos / denominador,
        ic=intervalo_wilson(casos, denominador, NIVEL_CONFIANZA),
    )


def _contrastar_con_la_cota(tasa: ProporcionCasos, cota: float) -> ContrasteCota:
    inferior, superior = tasa.ic
    if superior < cota:
        resultado = CONTRASTE_COMPATIBLE
    elif tasa.proporcion >= cota:
        resultado = CONTRASTE_REFUTADA
    else:
        resultado = CONTRASTE_NO_CONCLUYENTE
    return ContrasteCota(cota, tasa.proporcion, inferior, superior, resultado)


def _corrida_sin_repetidos(casos_corrida: Sequence[str]) -> list[str]:
    corrida = list(dict.fromkeys(casos_corrida))
    if not corrida:
        raise ValueError(
            "la corrida no tiene casos: el denominador de la tasa sale del plan de campana o "
            "del sidecar de la corrida y no puede ser cero."
        )
    return corrida


def parsear_intervenciones(
    intervenciones: Sequence[Fila], casos_corrida: Sequence[str]
) -> list[FilaIntervencion]:
    """
    Filas del export de C5 validadas contra la corrida.

    Usa `id_caso`, `origen_intervencion`, `cambio_sector` y `duracion_s`; `actor_alias` (un
    HMAC truncado) se ignora. Un `id_caso` vacio queda como `None` (no vinculable).

    Raises:
        ValueError: Falta una columna usada, `cambio_sector` no es booleano, `duracion_s`
            no es un numero no negativo o un `id_caso` no figura en la corrida. El mensaje
            nombra la columna, la fila y el valor.
    """
    corrida = set(casos_corrida)
    filas: list[FilaIntervencion] = []
    for numero, fila in enumerate(intervenciones, start=2):  # la linea 1 es el encabezado
        for columna in COLUMNAS_INTERVENCION_USADAS:
            if columna not in fila:
                raise ValueError(
                    f"el export de intervencion no tiene la columna {columna!r} "
                    f"(columnas usadas: {', '.join(COLUMNAS_INTERVENCION_USADAS)})."
                )
        id_caso = fila["id_caso"].strip() or None
        if id_caso is not None and id_caso not in corrida:
            raise ValueError(
                f"fila {numero}: el id_caso {id_caso} del export no figura en la corrida "
                "(plan de campana o sidecar)."
            )
        cambio = _BOOLEANOS.get(fila["cambio_sector"].strip().lower())
        if cambio is None:
            raise ValueError(
                f"fila {numero} (id_caso {id_caso}): cambio_sector debe ser true o false y es "
                f"{fila['cambio_sector']!r}."
            )
        crudo = fila["duracion_s"].strip()
        duracion: float | None = None
        if crudo:
            try:
                duracion = float(crudo)
            except ValueError:
                duracion = -1.0
            if duracion < 0:
                raise ValueError(
                    f"fila {numero} (id_caso {id_caso}): duracion_s debe ser un numero no "
                    f"negativo o vacio y es {fila['duracion_s']!r}."
                )
        filas.append(FilaIntervencion(numero, id_caso, fila["origen_intervencion"].strip(), cambio, duracion))
    return filas


def _casos_por_valor(
    filas: Sequence[FilaIntervencion], valor_de, claves: Sequence[str], denominador: int
) -> dict[str, ProporcionCasos]:
    """Proporcion de casos con al menos una fila de cada valor de `valor_de(fila)`."""
    por_valor: dict[str, set[str]] = {clave: set() for clave in claves}
    for fila in filas:
        if fila.id_caso is not None:
            por_valor.setdefault(valor_de(fila), set()).add(fila.id_caso)
    return {clave: _proporcion_de_casos(len(casos), denominador) for clave, casos in por_valor.items()}


def tasa_intervencion_humana(
    intervenciones: Sequence[Fila],
    casos_corrida: Sequence[str],
    *,
    cota: float = COTA_SUBHIPOTESIS_2,
) -> ResultadoIntervencion:
    """
    Proporcion de casos de la corrida con al menos una intervencion humana vinculada.

    `intervenciones` son las filas del export de C5 (solo las intervenidas) y `casos_corrida`
    los ids de la corrida, tomados del plan de campana o del sidecar, NUNCA del export (que no
    trae los casos sin intervencion): ese es el denominador. Devuelve la tasa con IC de Wilson,
    su contraste contra la `cota` (tres desenlaces, siempre con estimacion y ambos limites) y
    los desgloses por `origen_intervencion` y por `cambio_sector`.

    Raises:
        ValueError: Corrida vacia o export invalido (ver `parsear_intervenciones`).
    """
    corrida = _corrida_sin_repetidos(casos_corrida)
    filas = parsear_intervenciones(intervenciones, corrida)
    intervenidos = {fila.id_caso for fila in filas if fila.id_caso is not None}
    no_vinculables = sum(1 for fila in filas if fila.id_caso is None)
    tasa = _proporcion_de_casos(len(intervenidos), len(corrida))

    origenes = list(ORIGENES_CONOCIDOS)
    origenes += sorted({fila.origen for fila in filas} - set(ORIGENES_CONOCIDOS))
    advertencias = [
        "Un caso puede figurar en mas de un origen y en ambos valores de cambio_sector: los "
        "desgloses no suman la tasa."
    ]
    if no_vinculables:
        advertencias.append(
            f"{no_vinculables} filas del export no se pudieron vincular a un caso (id_caso vacio) "
            "y quedan fuera de la tasa: la tasa es una cota inferior."
        )
    return ResultadoIntervencion(
        casos_corrida=len(corrida),
        casos_intervenidos=len(intervenidos),
        filas=len(filas),
        no_vinculables=no_vinculables,
        tasa=tasa,
        contraste=_contrastar_con_la_cota(tasa, cota),
        por_origen=_casos_por_valor(filas, lambda f: f.origen, origenes, len(corrida)),
        por_cambio_sector=_casos_por_valor(
            filas, lambda f: f.cambio_sector, VALORES_CAMBIO_SECTOR, len(corrida)
        ),
        advertencias=tuple(advertencias),
    )


# ---------------------------------------------------------------------------
# 3b. Proporcion de tiempo de intervencion
# ---------------------------------------------------------------------------
ROTULO_DENOMINADOR_TIEMPO = "tiempo de registro automatizado"
LIMITACION_DENOMINADOR_TIEMPO = (
    "Limitacion: tiempo_automatizado_s mide solo el registro automatizado del caso; el "
    "denominador (registro automatizado + duracion de la intervencion) no es el tiempo total "
    "de atencion."
)
METODO_IC_TIEMPO = "bootstrap percentil por caso del cociente de sumas"
#: Cobertura minima de duracion (casos intervenidos con duracion completa) para estimar.
COBERTURA_MINIMA_DURACION: float = 0.80


@dataclass(frozen=True)
class ProporcionTiempo:
    """
    Proporcion del tiempo ocupado por la intervencion humana.

    proporcion = suma(duracion_s) / suma(tiempo_automatizado_s + duracion_s) sobre los casos de
    la corrida con tiempo conocido; los no intervenidos aportan duracion 0 y un caso
    intervenido aporta la suma de las `duracion_s` de sus filas. El IC es un bootstrap
    percentil que remuestrea CASOS y recalcula el cociente de sumas (no un IC de Wilson: no es
    una proporcion de casos). El denominador se rotula `tiempo de registro automatizado`.

    `cobertura` es la fraccion de casos intervenidos cuyas filas traen todas la duracion
    (`con_duracion_completa` de `casos_intervenidos`; None sin intervenciones); con cobertura
    menor a `COBERTURA_MINIMA_DURACION` la proporcion no es estimable y `motivo` lo explica.
    Los intervenidos sin duracion completa (`sin_duracion`) y los casos sin
    `tiempo_automatizado_s` (`sin_tiempo_automatizado`) quedan fuera del cociente y se cuentan;
    un caso puede figurar en ambas listas.
    """

    estimable: bool
    motivo: str | None
    proporcion: float | None
    ic: tuple[float, float] | None
    suma_duracion_s: float | None
    suma_tiempo_automatizado_s: float | None
    casos_intervenidos: int
    con_duracion_completa: int
    cobertura: float | None
    casos_incluidos: int
    sin_duracion: tuple[str, ...]
    sin_tiempo_automatizado: tuple[str, ...]
    denominador_rotulo: str
    limitacion: str
    metodo_ic: str
    nivel_confianza: float
    semilla: int
    remuestreos: int


def _bootstrap_del_cociente(
    unidades: Sequence[tuple[float, float]], semilla: int, remuestreos: int
) -> tuple[float, float]:
    """IC percentil por caso de suma(duracion) / suma(registro + duracion)."""
    cocientes: list[float] = []
    generador = random.Random(semilla)
    for indices in remuestreos_indices(generador, len(unidades), remuestreos):
        duracion = sum(unidades[i][0] for i in indices)
        total = duracion + sum(unidades[i][1] for i in indices)
        if total > 0:
            cocientes.append(duracion / total)
    return percentil_intervalo(cocientes, NIVEL_CONFIANZA)


def proporcion_tiempo_intervencion(
    intervenciones: Sequence[Fila],
    casos_corrida: Sequence[str],
    tiempos_automatizado_s: Mapping[str, float | None],
    *,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> ProporcionTiempo:
    """
    Proporcion del tiempo de intervencion sobre el tiempo de registro automatizado + intervencion.

    `tiempos_automatizado_s` indexa por `id_caso` el `tiempo_automatizado_s` de la copia de
    campana del corpus (un caso ausente o `None` no tiene tiempo conocido). Ver
    `ProporcionTiempo` para la definicion, la cobertura minima y las exclusiones.
    """
    corrida = _corrida_sin_repetidos(casos_corrida)
    filas = parsear_intervenciones(intervenciones, corrida)
    duracion_de: dict[str, float] = {}
    incompletos: set[str] = set()
    intervenidos: set[str] = set()
    for fila in filas:
        if fila.id_caso is None:
            continue
        intervenidos.add(fila.id_caso)
        if fila.duracion_s is None:
            incompletos.add(fila.id_caso)
        else:
            duracion_de[fila.id_caso] = duracion_de.get(fila.id_caso, 0.0) + fila.duracion_s
    completos = intervenidos - incompletos
    cobertura = len(completos) / len(intervenidos) if intervenidos else None

    unidades: list[tuple[float, float]] = []
    sin_tiempo: list[str] = []
    for caso in sorted(corrida):
        tiempo = tiempos_automatizado_s.get(caso)
        if tiempo is None:
            sin_tiempo.append(caso)
        elif caso not in incompletos:
            unidades.append((duracion_de.get(caso, 0.0), float(tiempo)))

    motivo: str | None = None
    if cobertura is not None and cobertura < COBERTURA_MINIMA_DURACION:
        motivo = (
            f"cobertura de duracion de {len(completos)} de {len(intervenidos)} casos intervenidos "
            f"({cobertura:.0%}), menor al minimo de {COBERTURA_MINIMA_DURACION:.0%}."
        )
    elif not unidades:
        motivo = "ningun caso de la corrida tiene tiempo_automatizado_s: no hay denominador."
    elif sum(d + t for d, t in unidades) <= 0:
        motivo = "la suma de tiempo_automatizado_s y duracion_s es cero: no hay denominador."

    proporcion: float | None = None
    ic: tuple[float, float] | None = None
    suma_duracion: float | None = None
    suma_registro: float | None = None
    if motivo is None:
        suma_duracion = sum(d for d, _ in unidades)
        suma_registro = sum(t for _, t in unidades)
        proporcion = suma_duracion / (suma_registro + suma_duracion)
        ic = _bootstrap_del_cociente(unidades, semilla, remuestreos)
    return ProporcionTiempo(
        estimable=motivo is None,
        motivo=motivo,
        proporcion=proporcion,
        ic=ic,
        suma_duracion_s=suma_duracion,
        suma_tiempo_automatizado_s=suma_registro,
        casos_intervenidos=len(intervenidos),
        con_duracion_completa=len(completos),
        cobertura=cobertura,
        casos_incluidos=len(unidades),
        sin_duracion=tuple(sorted(incompletos)),
        sin_tiempo_automatizado=tuple(sin_tiempo),
        denominador_rotulo=ROTULO_DENOMINADOR_TIEMPO,
        limitacion=LIMITACION_DENOMINADOR_TIEMPO,
        metodo_ic=METODO_IC_TIEMPO,
        nivel_confianza=NIVEL_CONFIANZA,
        semilla=semilla,
        remuestreos=remuestreos,
    )


@dataclass(frozen=True)
class AnalisisIntervencion:
    """Tasa de intervencion humana y proporcion de tiempo de una misma corrida."""

    tasa: ResultadoIntervencion
    tiempo: ProporcionTiempo


def analizar_intervencion(
    intervenciones: Sequence[Fila],
    casos_corrida: Sequence[str],
    tiempos_automatizado_s: Mapping[str, float | None],
    *,
    cota: float = COTA_SUBHIPOTESIS_2,
    semilla: int = SEMILLA_BOOTSTRAP,
    remuestreos: int = REMUESTREOS_BOOTSTRAP,
) -> AnalisisIntervencion:
    """
    `tasa_intervencion_humana` y `proporcion_tiempo_intervencion` sobre las mismas entradas.

    Si la proporcion de tiempo no es estimable (cobertura insuficiente, sin tiempos), la tasa
    de casos se reporta igual.
    """
    return AnalisisIntervencion(
        tasa=tasa_intervencion_humana(intervenciones, casos_corrida, cota=cota),
        tiempo=proporcion_tiempo_intervencion(
            intervenciones,
            casos_corrida,
            tiempos_automatizado_s,
            semilla=semilla,
            remuestreos=remuestreos,
        ),
    )


# ---------------------------------------------------------------------------
# 4. Efecto de orden de condicion y de posicion del operador del brazo manual
# ---------------------------------------------------------------------------
#: Minimo de casos por grupo (o de pares) para que un contraste de orden sea aplicable: con
#: menos de 6 no se puede alcanzar p < 0,05 en ninguna de las tres pruebas.
MINIMO_POR_GRUPO: int = 6
ALFA: float = 0.05

LECTURA_NO_SIGNIFICATIVO = "no significativo; efectos menores que el MDE no son detectables"
LECTURA_SIGNIFICATIVO = "significativo (p < 0,05)"
LECTURA_NO_APLICABLE = "no aplicable"

ESCALA_MDE_SPEARMAN = "rho (aproximacion de Fisher con n - 3)"
RESPUESTA_DURACION = "duracion del brazo manual (timestamp - inicio), en segundos"
NOTA_NO_SIGNIFICATIVO = (
    "Un resultado no significativo no es ausencia de efecto: solo descarta efectos mayores que "
    "el efecto minimo detectable (MDE) de cada contraste."
)


def _lectura(p: float | None) -> str:
    """Rotulo de un contraste: nunca 'sin efecto'; un p alto solo dice que no se detecto nada."""
    if p is None:
        return LECTURA_NO_APLICABLE
    return LECTURA_SIGNIFICATIVO if p < ALFA else LECTURA_NO_SIGNIFICATIVO


@dataclass(frozen=True)
class ContrastePareado:
    """
    Wilcoxon de rangos con signo entre dos grupos pareados, con nombres neutros.

    Las diferencias son `grupo_a - grupo_b`: `t_a_mayor` suma los rangos de las positivas
    (donde `grupo_a` es mayor), `t_b_mayor` los de las negativas, `p_unilateral_a_mayor_que_b`
    contrasta `grupo_a > grupo_b` y `r` es la correlacion biserial de rangos
    (t_a_mayor - t_b_mayor) / (n (n + 1) / 2). El MDE esta en escala d_z con `n` pares.
    """

    aplicable: bool
    motivo: str | None
    n: int
    estadistico: float | None
    t_a_mayor: float | None
    t_b_mayor: float | None
    p: float | None
    p_unilateral_a_mayor_que_b: float | None
    r: float | None
    dz: float | None
    mde: float | None
    escala_mde: str
    lectura: str


@dataclass(frozen=True)
class ContrasteIndependiente:
    """
    Mann-Whitney bilateral entre dos grupos independientes.

    `estadistico_u` es el U de `grupo_a`; `r = 2 U_a / (n_a n_b) - 1` es la correlacion
    biserial de rangos (-1 si todo `grupo_a` es menor que `grupo_b`, +1 si es mayor). El MDE
    esta en escala d con el n efectivo `n_a n_b / (n_a + n_b)`.
    """

    aplicable: bool
    motivo: str | None
    n_a: int
    n_b: int
    estadistico_u: float | None
    p: float | None
    r: float | None
    n_efectivo: float | None
    mde: float | None
    escala_mde: str
    lectura: str


def _pareado_no_aplicable(n: int, motivo: str) -> ContrastePareado:
    return ContrastePareado(
        aplicable=False,
        motivo=motivo,
        n=n,
        estadistico=None,
        t_a_mayor=None,
        t_b_mayor=None,
        p=None,
        p_unilateral_a_mayor_que_b=None,
        r=None,
        dz=None,
        mde=None,
        escala_mde="d_z",
        lectura=LECTURA_NO_APLICABLE,
    )


def contraste_pareado(
    grupo_a: Sequence[float], grupo_b: Sequence[float], *, minimo: int = MINIMO_POR_GRUPO
) -> ContrastePareado:
    """
    Wilcoxon pareado de `grupo_a` contra `grupo_b`, envolviendo `wilcoxon_tiempos_detallado`.

    No aplicable (sin estadistico ni efecto) con menos de `minimo` pares, con todas las
    diferencias en cero, con un `ValueError` de scipy o con un p NaN. Las diferencias en cero se
    detectan antes de llamar a scipy: segun la version, scipy las rechaza con un `ValueError`
    o devuelve p = 1 con una advertencia de division invalida.

    Raises:
        ValueError: Los grupos tienen distinta cantidad de elementos.
    """
    if len(grupo_a) != len(grupo_b):
        raise ValueError(
            f"los grupos pareados deben tener la misma longitud (grupo_a={len(grupo_a)}, "
            f"grupo_b={len(grupo_b)})."
        )
    n = len(grupo_a)
    if n < minimo:
        return _pareado_no_aplicable(n, f"menos de {minimo} pares (n = {n}).")
    if all(a == b for a, b in zip(grupo_a, grupo_b)):
        return _pareado_no_aplicable(n, "todas las diferencias entre los grupos son cero.")
    try:
        wilcoxon = wilcoxon_tiempos_detallado(list(grupo_a), list(grupo_b))
    except ValueError as exc:
        return _pareado_no_aplicable(n, f"scipy rechazo el contraste: {exc}")
    if math.isnan(wilcoxon.p):
        return _pareado_no_aplicable(n, "el valor p del contraste es NaN.")
    return ContrastePareado(
        aplicable=True,
        motivo=None,
        n=n,
        estadistico=wilcoxon.estadistico,
        t_a_mayor=wilcoxon.t_positivos,
        t_b_mayor=wilcoxon.t_negativos,
        p=wilcoxon.p,
        p_unilateral_a_mayor_que_b=wilcoxon.p_unilateral,
        r=wilcoxon.r,
        dz=tamano_efecto_dz(list(grupo_a), list(grupo_b)),
        mde=efecto_minimo_detectable(n, eficiencia_relativa=ARE_WILCOXON_MINIMA),
        escala_mde="d_z",
        lectura=_lectura(wilcoxon.p),
    )


def _independiente_no_aplicable(n_a: int, n_b: int, motivo: str) -> ContrasteIndependiente:
    return ContrasteIndependiente(
        aplicable=False,
        motivo=motivo,
        n_a=n_a,
        n_b=n_b,
        estadistico_u=None,
        p=None,
        r=None,
        n_efectivo=None,
        mde=None,
        escala_mde="d",
        lectura=LECTURA_NO_APLICABLE,
    )


def contraste_independiente(
    grupo_a: Sequence[float], grupo_b: Sequence[float], *, minimo: int = MINIMO_POR_GRUPO
) -> ContrasteIndependiente:
    """
    Mann-Whitney bilateral de `grupo_a` contra `grupo_b` (grupos independientes).

    No aplicable (sin estadistico ni efecto) si algun grupo tiene menos de `minimo` casos o si
    todos los valores son iguales (sin variabilidad, p NaN en scipy).
    """
    from scipy.stats import mannwhitneyu

    n_a, n_b = len(grupo_a), len(grupo_b)
    if min(n_a, n_b) < minimo:
        return _independiente_no_aplicable(
            n_a, n_b, f"algun grupo tiene menos de {minimo} casos (n_a = {n_a}, n_b = {n_b})."
        )
    if len(set(grupo_a) | set(grupo_b)) == 1:
        return _independiente_no_aplicable(
            n_a, n_b, "sin variabilidad: todos los valores de ambos grupos son iguales."
        )
    resultado = mannwhitneyu(list(grupo_a), list(grupo_b), alternative="two-sided")
    p = float(resultado.pvalue)
    if math.isnan(p):
        return _independiente_no_aplicable(n_a, n_b, "el valor p del contraste es NaN.")
    u = float(resultado.statistic)
    n_efectivo = n_a * n_b / (n_a + n_b)
    return ContrasteIndependiente(
        aplicable=True,
        motivo=None,
        n_a=n_a,
        n_b=n_b,
        estadistico_u=u,
        p=p,
        r=2.0 * u / (n_a * n_b) - 1.0,
        n_efectivo=n_efectivo,
        mde=efecto_minimo_detectable(n_efectivo, eficiencia_relativa=ARE_WILCOXON_MINIMA),
        escala_mde="d",
        lectura=_lectura(p),
    )


# ---------------------------------------------------------------------------
# 4b. Duracion del brazo manual (respuesta primaria del efecto de orden)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class DuracionManual:
    """Duracion, en segundos, que un operador tardo en un caso (`timestamp - inicio`)."""

    id_caso: str
    id_etiquetador: str
    duracion_s: float


def _instante_de(fila: Fila, campo: str) -> datetime:
    """Instante ISO-8601 con zona horaria de `fila[campo]`; `ValueError` que nombra caso y operador."""
    crudo = (fila.get(campo) or "").strip()
    try:
        instante = datetime.fromisoformat(crudo) if crudo else None
    except ValueError:
        instante = None
    if instante is None or instante.tzinfo is None:
        raise ValueError(
            f"el caso {fila['id_caso']} del operador {fila['id_etiquetador']}: {campo} no es un "
            f"instante ISO-8601 con zona horaria ({crudo!r})."
        )
    return instante


def duraciones_brazo_manual(filas: Sequence[Fila]) -> list[DuracionManual]:
    """
    Duracion `timestamp - inicio` de cada `(id_caso, id_etiquetador)` de `tarea = brazo_manual`.

    Es la respuesta primaria del efecto de orden. NO usa el `tiempo_manual_s` del corpus (el
    canonico de la campana 2026-10, que no se toca). Las filas de otras tareas se ignoran y el
    resultado sale ordenado por operador y caso.

    Raises:
        ValueError: Un instante ausente, ilegible o sin zona horaria, o una duracion negativa;
            el mensaje nombra el caso y el operador.
    """
    duraciones: list[DuracionManual] = []
    for fila in filas:
        if fila["tarea"] != TAREA_BRAZO_MANUAL:
            continue
        inicio = _instante_de(fila, "inicio")
        fin = _instante_de(fila, "timestamp")
        segundos = (fin - inicio).total_seconds()
        if segundos < 0:
            raise ValueError(
                f"el caso {fila['id_caso']} del operador {fila['id_etiquetador']} tiene una "
                f"duracion negativa: timestamp {fila['timestamp']} es anterior a inicio "
                f"{fila['inicio']}."
            )
        duraciones.append(DuracionManual(fila["id_caso"], fila["id_etiquetador"], segundos))
    return sorted(duraciones, key=lambda d: (d.id_etiquetador, d.id_caso))


# ---------------------------------------------------------------------------
# 4c. Efecto de orden de condicion (brazo_primero manual frente a automatizado)
# ---------------------------------------------------------------------------
DISENO_INDEPENDIENTE = "grupos_independientes"
DISENO_CRUZADO = "cruzado"


@dataclass(frozen=True)
class CorridaCruzada:
    """
    Segunda corrida de un diseno cruzado: el mismo conjunto de casos con la condicion opuesta.

    `plan` es el plan de esa corrida (cada caso con el `brazo_primero` contrario al de la
    primera) y `registros_manual` las filas de la planilla del brazo manual de esa corrida.
    """

    plan: Sequence[AsignacionCaso]
    registros_manual: Sequence[Fila]


@dataclass(frozen=True)
class AciertoPorCondicion:
    """
    Respuesta secundaria: acierto estricto del operador segun la condicion.

    En grupos independientes no hay pares, asi que McNemar no corresponde: se reporta la
    proporcion de aciertos de cada grupo con Wilson (`casos` = aciertos, `denominador` = casos
    con referencia) y la prueba exacta de Fisher bilateral. En el diseno cruzado, McNemar
    pareado por caso (`solo_a`: acierta solo cuando el caso va manual-primero). Solo entran los
    casos que la referencia conoce (los discordantes quedan afuera) y se exigen 6 por grupo.
    """

    diseno: str
    aplicable: bool
    motivo: str | None
    manual_primero: ProporcionCasos | None
    automatizado_primero: ProporcionCasos | None
    p_fisher: float | None
    mcnemar: ResultadoMcNemar | None
    lectura: str


@dataclass(frozen=True)
class EfectoCondicion:
    """
    Efecto de la condicion (`brazo_primero` manual frente a automatizado) en la duracion.

    - `grupos_independientes` (el plan asigna una sola condicion a cada caso): Mann-Whitney
      con `grupo_a` = casos manual-primero y `grupo_b` = casos automatizado-primero.
    - `cruzado` (el plan cruza los mismos casos en dos corridas con condicion opuesta):
      Wilcoxon pareado por caso, `grupo_a` = la corrida donde el caso fue manual-primero.

    `acierto` es la respuesta secundaria (acierto estricto); es None sin referencia.
    """

    diseno: str
    contraste: ContrasteIndependiente | ContrastePareado
    acierto: AciertoPorCondicion | None = None


@dataclass(frozen=True)
class ContrasteSpearman:
    """
    Correlacion de Spearman entre la duracion y la posicion REAL del caso en la secuencia del operador.

    rho > 0 indica que el operador tarda mas a medida que avanza (fatiga) y rho < 0 que tarda
    menos (aprendizaje). El MDE esta en escala de correlacion: tanh del MDE de Fisher con
    n - 3 grados (aproximacion; no es una cota de eficiencia propia de Spearman).
    """

    aplicable: bool
    motivo: str | None
    n: int
    rho: float | None
    p: float | None
    mde: float | None
    escala_mde: str
    lectura: str


@dataclass(frozen=True)
class EfectoPosicion:
    """
    Efecto de la posicion del caso en la secuencia del operador (aprendizaje o fatiga).

    `spearman` usa la posicion real (el orden en que el operador efectivamente trabajo, por
    `inicio`); `mitades` compara la duracion de los casos de la mitad 1 (`grupo_a`) contra los
    de la mitad 2 (`grupo_b`) segun el plan (analisis por asignacion; r < 0: mitad 1 mas rapida).
    `desvios` y `casos_con_desvio` son los casos cuya posicion real difiere de la planeada, para
    leer la comparacion de mitades con esa salvedad.
    """

    spearman: ContrasteSpearman
    mitades: ContrasteIndependiente
    desvios: int
    casos_con_desvio: tuple[str, ...]


@dataclass(frozen=True)
class OrdenOperador:
    """Efecto de orden de un operador, medido sobre los casos que ese operador etiqueto."""

    id_etiquetador: str
    casos_con_duracion: int
    condicion: EfectoCondicion
    posicion: EfectoPosicion


@dataclass(frozen=True)
class ResultadoOrden:
    """Efecto de orden de condicion por operador, con su respuesta, diseno y lectura."""

    respuesta: str
    diseno: str
    por_operador: tuple[OrdenOperador, ...]
    nota: str


def _plan_por_caso(plan: Sequence[AsignacionCaso]) -> dict[str, AsignacionCaso]:
    return {fila.id_caso: fila for fila in plan}


def _duraciones_por_operador(
    filas: Sequence[Fila], plan: dict[str, AsignacionCaso]
) -> dict[str, dict[str, float]]:
    """Duracion de cada caso por operador; un caso fuera del plan es un error accionable."""
    por_operador: dict[str, dict[str, float]] = {}
    for duracion in duraciones_brazo_manual(filas):
        if duracion.id_caso not in plan:
            raise ValueError(
                f"el caso {duracion.id_caso} del operador {duracion.id_etiquetador} no figura en el "
                "plan de campana."
            )
        por_operador.setdefault(duracion.id_etiquetador, {})[duracion.id_caso] = duracion.duracion_s
    return por_operador


def _verificar_cruce(plan_1: dict[str, AsignacionCaso], plan_2: dict[str, AsignacionCaso]) -> None:
    """El plan cruza los mismos casos en dos corridas con condicion opuesta, o `ValueError`."""
    if set(plan_1) != set(plan_2):
        sobran = sorted(set(plan_2) - set(plan_1))
        faltan = sorted(set(plan_1) - set(plan_2))
        raise ValueError(
            "las dos corridas de un diseno cruzado deben tener los mismos casos "
            f"(solo en la segunda: {sobran or 'ninguno'}; solo en la primera: {faltan or 'ninguno'})."
        )
    repetidos = sorted(c for c in plan_1 if plan_1[c].brazo_primero == plan_2[c].brazo_primero)
    if repetidos:
        raise ValueError(
            "el plan de la segunda corrida debe tener la condicion opuesta (brazo_primero) en "
            f"cada caso y repite la de la primera en: {', '.join(repetidos)}."
        )


def _condicion_independiente(duraciones: dict[str, float], plan: dict[str, AsignacionCaso]) -> EfectoCondicion:
    casos = sorted(duraciones)
    manual_primero = [duraciones[c] for c in casos if plan[c].brazo_primero == BRAZO_MANUAL]
    automatizado_primero = [duraciones[c] for c in casos if plan[c].brazo_primero == BRAZO_AUTOMATIZADO]
    return EfectoCondicion(DISENO_INDEPENDIENTE, contraste_independiente(manual_primero, automatizado_primero))


def _aciertos_por_operador(filas: Sequence[Fila], referencia: Referencia) -> dict[str, dict[str, bool]]:
    """Acierto estricto de cada `(operador, caso)` que la referencia conoce."""
    por_operador: dict[str, dict[str, bool]] = {}
    for fila in filas:
        if fila["tarea"] != TAREA_BRAZO_MANUAL:
            continue
        caso = referencia.casos.get(fila["id_caso"])
        if caso is not None:
            por_operador.setdefault(fila["id_etiquetador"], {})[fila["id_caso"]] = (
                fila["sector_etiquetado"] == caso.sector
            )
    return por_operador


def _acierto_no_aplicable(diseno: str, motivo: str) -> AciertoPorCondicion:
    return AciertoPorCondicion(diseno, False, motivo, None, None, None, None, LECTURA_NO_APLICABLE)


def _acierto_independiente(
    aciertos: dict[str, bool], plan: dict[str, AsignacionCaso]
) -> AciertoPorCondicion:
    from scipy.stats import fisher_exact

    casos = sorted(aciertos)
    manual_primero = [aciertos[c] for c in casos if plan[c].brazo_primero == BRAZO_MANUAL]
    automatizado_primero = [aciertos[c] for c in casos if plan[c].brazo_primero == BRAZO_AUTOMATIZADO]
    n_a, n_b = len(manual_primero), len(automatizado_primero)
    if min(n_a, n_b) < MINIMO_POR_GRUPO:
        return _acierto_no_aplicable(
            DISENO_INDEPENDIENTE,
            f"algun grupo tiene menos de {MINIMO_POR_GRUPO} casos con referencia "
            f"(manual-primero = {n_a}, automatizado-primero = {n_b}).",
        )
    aciertos_a, aciertos_b = sum(manual_primero), sum(automatizado_primero)
    p = float(
        fisher_exact([[aciertos_a, n_a - aciertos_a], [aciertos_b, n_b - aciertos_b]], alternative="two-sided").pvalue
    )
    return AciertoPorCondicion(
        diseno=DISENO_INDEPENDIENTE,
        aplicable=True,
        motivo=None,
        manual_primero=_proporcion_de_casos(aciertos_a, n_a),
        automatizado_primero=_proporcion_de_casos(aciertos_b, n_b),
        p_fisher=p,
        mcnemar=None,
        lectura=_lectura(p),
    )


def _acierto_cruzado(
    aciertos_1: dict[str, bool], aciertos_2: dict[str, bool], plan_1: dict[str, AsignacionCaso]
) -> AciertoPorCondicion:
    comunes = sorted(set(aciertos_1) & set(aciertos_2))
    if len(comunes) < MINIMO_POR_GRUPO:
        return _acierto_no_aplicable(
            DISENO_CRUZADO, f"menos de {MINIMO_POR_GRUPO} pares con referencia (n = {len(comunes)})."
        )
    manual_primero = [
        aciertos_1[c] if plan_1[c].brazo_primero == BRAZO_MANUAL else aciertos_2[c] for c in comunes
    ]
    manual_segundo = [
        aciertos_2[c] if plan_1[c].brazo_primero == BRAZO_MANUAL else aciertos_1[c] for c in comunes
    ]
    mcnemar = contraste_mcnemar(manual_primero, manual_segundo)
    if not mcnemar.aplicable:
        return _acierto_no_aplicable(DISENO_CRUZADO, "sin pares discordantes: McNemar no aplicable.")
    return AciertoPorCondicion(
        diseno=DISENO_CRUZADO,
        aplicable=True,
        motivo=None,
        manual_primero=None,
        automatizado_primero=None,
        p_fisher=None,
        mcnemar=mcnemar,
        lectura=_lectura(mcnemar.p_primario),
    )


def _condicion_cruzada(
    duraciones_1: dict[str, float],
    duraciones_2: dict[str, float],
    plan_1: dict[str, AsignacionCaso],
) -> EfectoCondicion:
    """Pares (duracion cuando el caso fue manual-primero, duracion cuando fue segundo) por caso."""
    comunes = sorted(set(duraciones_1) & set(duraciones_2))
    manual_primero: list[float] = []
    manual_segundo: list[float] = []
    for caso in comunes:
        if plan_1[caso].brazo_primero == BRAZO_MANUAL:
            manual_primero.append(duraciones_1[caso])
            manual_segundo.append(duraciones_2[caso])
        else:
            manual_primero.append(duraciones_2[caso])
            manual_segundo.append(duraciones_1[caso])
    return EfectoCondicion(DISENO_CRUZADO, contraste_pareado(manual_primero, manual_segundo))


def _posicion_sin_casos() -> EfectoPosicion:
    """Efecto de posicion de un operador sin casos en la corrida principal (no aplicable)."""
    return EfectoPosicion(
        spearman=_spearman_no_aplicable(0, "el operador no tiene casos en la corrida principal."),
        mitades=contraste_independiente([], []),
        desvios=0,
        casos_con_desvio=(),
    )


def _spearman_no_aplicable(n: int, motivo: str) -> ContrasteSpearman:
    return ContrasteSpearman(
        aplicable=False,
        motivo=motivo,
        n=n,
        rho=None,
        p=None,
        mde=None,
        escala_mde=ESCALA_MDE_SPEARMAN,
        lectura=LECTURA_NO_APLICABLE,
    )


def contraste_spearman(
    duraciones: Sequence[float], posiciones: Sequence[int], *, minimo: int = MINIMO_POR_GRUPO
) -> ContrasteSpearman:
    """
    Spearman bilateral entre la duracion y la posicion de cada caso.

    No aplicable con menos de `minimo` casos o con duracion constante (scipy devuelve NaN con
    una advertencia).
    """
    from scipy.stats import spearmanr

    n = len(duraciones)
    if n < minimo:
        return _spearman_no_aplicable(n, f"menos de {minimo} casos (n = {n}).")
    if len(set(duraciones)) == 1:
        return _spearman_no_aplicable(n, "la duracion es constante: Spearman no esta definido.")
    resultado = spearmanr(list(duraciones), list(posiciones))
    rho, p = float(resultado.statistic), float(resultado.pvalue)
    if math.isnan(rho) or math.isnan(p):
        return _spearman_no_aplicable(n, "la correlacion o su valor p es NaN.")
    mde = math.tanh(efecto_minimo_detectable(n - 3, eficiencia_relativa=ARE_WILCOXON_MINIMA))
    return ContrasteSpearman(
        aplicable=True,
        motivo=None,
        n=n,
        rho=rho,
        p=p,
        mde=mde,
        escala_mde=ESCALA_MDE_SPEARMAN,
        lectura=_lectura(p),
    )


def _efecto_posicion(
    operador: str,
    duraciones: dict[str, float],
    plan: dict[str, AsignacionCaso],
    posicion_real: dict[tuple[str, str], int],
    desvios_del_operador: Sequence[str],
) -> EfectoPosicion:
    casos = sorted(duraciones)
    mitad_1 = [duraciones[c] for c in casos if plan[c].mitad == 1]
    mitad_2 = [duraciones[c] for c in casos if plan[c].mitad == 2]
    return EfectoPosicion(
        spearman=contraste_spearman(
            [duraciones[c] for c in casos], [posicion_real[(operador, c)] for c in casos]
        ),
        mitades=contraste_independiente(mitad_1, mitad_2),
        desvios=len(desvios_del_operador),
        casos_con_desvio=tuple(sorted(desvios_del_operador)),
    )


def efecto_orden(
    registros_manual: Sequence[Fila],
    plan: Sequence[AsignacionCaso],
    *,
    referencia: Referencia | None = None,
    cruce: CorridaCruzada | None = None,
) -> ResultadoOrden:
    """
    Efecto de orden de condicion en la duracion del brazo manual, por operador.

    La respuesta es `duracion_s = timestamp - inicio` de la planilla (nunca el
    `tiempo_manual_s` del corpus) y cada operador se analiza sobre los casos que etiqueto. El
    diseno lo declara el plan: sin `cruce`, cada caso tiene una sola condicion y se comparan
    grupos independientes (Mann-Whitney, MDE en escala d); con `cruce` (la segunda corrida con
    la condicion opuesta en los mismos casos), Wilcoxon pareado por caso (r, d_z y MDE en escala
    d_z). Un grupo con menos de 6 casos (o menos de 6 pares) es no aplicable.

    Con `referencia`, la respuesta secundaria es el acierto estricto del operador segun la
    condicion (`EfectoCondicion.acierto`): Wilson por grupo y Fisher exacta en grupos
    independientes, McNemar pareado por caso en el diseno cruzado.

    El efecto de posicion (Spearman de la duracion contra la posicion real y mitad 1 contra
    mitad 2 del plan) se estima siempre sobre la corrida principal; la posicion real y los
    desvios respecto del plan salen de `reconstruir_posicion_real` y
    `desvios_respecto_del_plan` de `evaluation/brazo_manual.py` (c-165), que no se reimplementan.

    Raises:
        ValueError: Un caso de la planilla fuera del plan, una duracion invalida (ver
            `duraciones_brazo_manual`) o un `cruce` que no cruza los mismos casos con condicion
            opuesta.
    """
    plan_1 = _plan_por_caso(plan)
    duraciones_1 = _duraciones_por_operador(registros_manual, plan_1)
    filas_manual = [fila for fila in registros_manual if fila["tarea"] == TAREA_BRAZO_MANUAL]
    posiciones = reconstruir_posicion_real(filas_manual)
    posicion_real = {(p.id_etiquetador, p.id_caso): p.posicion for p in posiciones}
    desvios: dict[str, list[str]] = {}
    for desvio in desvios_respecto_del_plan(posiciones, plan):
        desvios.setdefault(desvio.id_etiquetador, []).append(desvio.id_caso)

    def posicion_de(operador: str) -> EfectoPosicion:
        return _efecto_posicion(
            operador, duraciones_1[operador], plan_1, posicion_real, desvios.get(operador, [])
        )

    aciertos_1 = {} if referencia is None else _aciertos_por_operador(registros_manual, referencia)
    ordenes: list[OrdenOperador] = []
    if cruce is None:
        for operador in sorted(duraciones_1):
            condicion = _condicion_independiente(duraciones_1[operador], plan_1)
            if referencia is not None:
                condicion = replace(
                    condicion, acierto=_acierto_independiente(aciertos_1.get(operador, {}), plan_1)
                )
            ordenes.append(
                OrdenOperador(
                    operador, len(duraciones_1[operador]), condicion, posicion_de(operador)
                )
            )
        diseno = DISENO_INDEPENDIENTE
    else:
        plan_2 = _plan_por_caso(cruce.plan)
        _verificar_cruce(plan_1, plan_2)
        duraciones_2 = _duraciones_por_operador(cruce.registros_manual, plan_2)
        aciertos_2 = (
            {} if referencia is None else _aciertos_por_operador(cruce.registros_manual, referencia)
        )
        for operador in sorted(set(duraciones_1) | set(duraciones_2)):
            propias_1 = duraciones_1.get(operador, {})
            propias_2 = duraciones_2.get(operador, {})
            condicion = _condicion_cruzada(propias_1, propias_2, plan_1)
            if referencia is not None:
                condicion = replace(
                    condicion,
                    acierto=_acierto_cruzado(
                        aciertos_1.get(operador, {}), aciertos_2.get(operador, {}), plan_1
                    ),
                )
            ordenes.append(
                OrdenOperador(
                    operador,
                    len(propias_1),
                    condicion,
                    posicion_de(operador) if propias_1 else _posicion_sin_casos(),
                )
            )
        diseno = DISENO_CRUZADO
    return ResultadoOrden(
        respuesta=RESPUESTA_DURACION,
        diseno=diseno,
        por_operador=tuple(ordenes),
        nota=NOTA_NO_SIGNIFICATIVO,
    )


# ---------------------------------------------------------------------------
# 5. Evaluacion fuera de muestra con el clasificador congelado
# ---------------------------------------------------------------------------
ROTULO_IN_SAMPLE = "in-sample"
ROTULO_OUT_OF_SAMPLE = "out-of-sample"

LIMITACION_COMMIT_IN_SAMPLE = (
    "commit in-sample no registrado; comparabilidad verificada por versión y pines"
)
LIMITACION_COMMIT_INDEPENDIENTE = (
    "commit del cache independiente no registrado; comparabilidad verificada por versión y pines"
)

_CLAUSULA_DE_VERSION = re.compile(r"^\s*(>=|<=|==|!=|>|<)?\s*(\d+(?:\.\d+)*)\s*$")
_VERSION_EXACTA = re.compile(r"^\d+(?:\.\d+)*$")


class FueraDeMuestraError(ValueError):
    """
    La evaluacion fuera de muestra se aborta (el mensaje muestra los valores en conflicto).

    Se levanta cuando el clasificador no esta congelado (version, modelo, version instalada de
    google-genai o commit distintos), cuando el corpus independiente solapa el de ajuste, cuando
    las predicciones no se alinean con su corpus o cuando falta un dato obligatorio
    (`pines_in_sample`, el pin vigente o los `pines` del cache independiente).
    """


# --- versiones y rangos de google-genai ---------------------------------------------------
def _version_como_tupla(version: str) -> tuple[int, ...]:
    if not _VERSION_EXACTA.match(version.strip()):
        raise ValueError(f"version no interpretable: {version!r}")
    return tuple(int(parte) for parte in version.strip().split("."))


def _comparar_versiones(a: tuple[int, ...], b: tuple[int, ...]) -> int:
    largo = max(len(a), len(b))
    a, b = a + (0,) * (largo - len(a)), b + (0,) * (largo - len(b))
    return (a > b) - (a < b)


def cumple_rango(version: str, rango: str) -> bool:
    """
    True si `version` cumple el `rango` (clausulas separadas por coma con `>=`, `>`, `<=`, `<`,
    `==` o `!=`; una version sola equivale a `==`), por ejemplo `>=2.33,<3`.

    Raises:
        ValueError: La version o el rango no se pueden interpretar.
    """
    instalada = _version_como_tupla(version)
    for clausula in rango.split(","):
        coincidencia = _CLAUSULA_DE_VERSION.match(clausula)
        if coincidencia is None:
            raise ValueError(f"rango de version no interpretable: {rango!r}")
        operador = coincidencia.group(1) or "=="
        comparacion = _comparar_versiones(instalada, _version_como_tupla(coincidencia.group(2)))
        cumple = {
            ">=": comparacion >= 0,
            ">": comparacion > 0,
            "<=": comparacion <= 0,
            "<": comparacion < 0,
            "==": comparacion == 0,
            "!=": comparacion != 0,
        }[operador]
        if not cumple:
            return False
    return True


def _es_version_exacta(rango: str) -> bool:
    """True si el pin es una version concreta (sin operador o con `==`), no un rango."""
    coincidencia = _CLAUSULA_DE_VERSION.match(rango)
    return coincidencia is not None and (coincidencia.group(1) or "==") == "=="


# --- resultado ----------------------------------------------------------------------------
@dataclass(frozen=True)
class BloqueExactitud:
    """
    Exactitud de un bloque de predicciones: global (estricta y laxa, con Wilson) y por etapa.

    `por_etapa` lista las etapas de la cascada en el orden de `ETAPAS_PIPELINE`, incluidas las
    de cero casos. El bloque in-sample y el out-of-sample nunca se mezclan: cada uno lleva su
    `rotulo`.
    """

    rotulo: str
    casos: int
    classifier_version: str
    resumen: ResumenExactitud
    por_etapa: dict[str, ResumenExactitud]


@dataclass(frozen=True)
class ComparabilidadClasificador:
    """
    Evidencia de que el clasificador de ambos bloques es el mismo (congelado).

    La version del clasificador y el modelo coinciden exactamente. De `google-genai` el
    in-sample solo conserva un RANGO declarado (`rango_in_sample`): lo verificable es que la
    version instalada del cache independiente (`google_genai_instalada`) lo cumpla y cumpla
    tambien el pin vigente de `openspec/config.yaml` (`rango_vigente`). El commit se compara
    solo cuando ambos bloques lo traen.
    """

    classifier_version: str
    modelo: str
    google_genai_instalada: str
    rango_in_sample: str
    rango_vigente: str
    commit_in_sample: str | None
    commit_independiente: str | None


@dataclass(frozen=True)
class ResultadoFueraDeMuestra:
    """
    Resultado de `evaluar_fuera_de_muestra`.

    Con `obtenido = False` la seccion se declara "no se obtuvo": `faltantes` nombra los
    artefactos que no existen y no hay metricas de ningun bloque (tampoco in-sample).
    `limitaciones` lista lo que la comparabilidad NO pudo verificar y no abortó la evaluacion.
    """

    obtenido: bool
    motivo: str | None
    faltantes: tuple[str, ...]
    in_sample: BloqueExactitud | None
    out_of_sample: BloqueExactitud | None
    comparabilidad: ComparabilidadClasificador | None
    limitaciones: tuple[str, ...]


def cargar_corpus_solo_lectura(ruta: pathlib.Path | str) -> list[CasoEvaluacion]:
    """
    Carga un corpus con `cargar_corpus` sin tocar el archivo original.

    `cargar_corpus` reescribe el archivo si `metadata.total_casos` esta desincronizado; el
    analisis es de solo lectura, asi que carga una copia temporal.
    """
    ruta = pathlib.Path(ruta)
    with tempfile.TemporaryDirectory() as temporal:
        copia = pathlib.Path(temporal) / ruta.name
        shutil.copyfile(ruta, copia)
        return cargar_corpus(copia)


def _bloque(
    rotulo: str,
    predicciones: Sequence[Prediccion],
    corpus: Sequence[CasoEvaluacion],
    classifier_version: str,
) -> BloqueExactitud:
    """Exactitud global y por etapa de `predicciones` contra la verdad del `corpus`."""
    por_id = {caso.id: caso for caso in corpus}
    casos = [por_id[prediccion.caso_id] for prediccion in predicciones]
    reales = [caso.sector_asignado for caso in casos]
    predichos = [prediccion.sector_predicho for prediccion in predicciones]
    verdad = [caso.conjunto_verdad for caso in casos]
    return BloqueExactitud(
        rotulo=rotulo,
        casos=len(predicciones),
        classifier_version=classifier_version,
        resumen=resumen_exactitud(reales, predichos, verdad),
        por_etapa=desglose_exactitud(
            claves=[prediccion.etapa for prediccion in predicciones],
            reales=reales,
            predichos=predichos,
            conjuntos_verdad=verdad,
            orden=ETAPAS_PIPELINE,
        ),
    )


def _verificar_alineacion(
    predicciones: Sequence[Prediccion], corpus: Sequence[CasoEvaluacion], bloque: str
) -> None:
    """
    Las predicciones cubren exactamente los casos del corpus, una por caso, con su verdad y una
    etapa de la cascada; si no, `FueraDeMuestraError` nombrando los casos.
    """
    por_id = {caso.id: caso for caso in corpus}
    vistos: set[str] = set()
    for prediccion in predicciones:
        if prediccion.caso_id in vistos:
            raise FueraDeMuestraError(
                f"las predicciones {bloque} traen mas de una prediccion para el caso {prediccion.caso_id}."
            )
        vistos.add(prediccion.caso_id)
    sin_prediccion = sorted(set(por_id) - vistos)
    sin_caso = sorted(vistos - set(por_id))
    if sin_prediccion or sin_caso:
        raise FueraDeMuestraError(
            f"las predicciones {bloque} no se alinean con su corpus: casos del corpus sin "
            f"prediccion: {sin_prediccion or 'ninguno'}; predicciones de casos que el corpus no "
            f"tiene: {sin_caso or 'ninguna'}."
        )
    for prediccion in predicciones:
        caso = por_id[prediccion.caso_id]
        if prediccion.sector_asignado != caso.sector_asignado:
            raise FueraDeMuestraError(
                f"las predicciones {bloque} no se alinean con su corpus: el caso {caso.id} tiene "
                f"sector_asignado {prediccion.sector_asignado!r} en las predicciones y "
                f"{caso.sector_asignado!r} en el corpus."
            )
        if prediccion.etapa not in ETAPAS_PIPELINE:
            raise FueraDeMuestraError(
                f"las predicciones {bloque}: el caso {caso.id} trae la etapa {prediccion.etapa!r}, "
                f"que no es una de la cascada ({', '.join(ETAPAS_PIPELINE)})."
            )


def _meta_obligatoria(meta: Mapping[str, object] | None, bloque: str) -> Mapping[str, object]:
    """El `cache_meta` de un bloque, que debe existir y traer `classifier_version`."""
    if meta is None:
        raise FueraDeMuestraError(
            f"el cache de predicciones {bloque} no tiene cache_meta: sin la version del "
            "clasificador no se puede verificar que este congelado."
        )
    if not meta.get("classifier_version"):
        raise FueraDeMuestraError(
            f"el cache_meta {bloque} no tiene classifier_version: sin ella no se puede verificar "
            "que el clasificador este congelado."
        )
    return meta


def _pines_in_sample_validos(pines: Mapping[str, str] | None) -> Mapping[str, str]:
    if pines is None:
        raise FueraDeMuestraError(
            "falta pines_in_sample (version de google-genai y modelo del bloque in-sample): "
            "tomalos del README de evaluation/data/campana/ (seccion de la referencia in-sample), "
            'por ejemplo {"google_genai": ">=2.20.0", "modelo": "gemini-3.6-flash"}; el cache de '
            "v9 no los registra."
        )
    for clave in ("google_genai", "modelo"):
        if not str(pines.get(clave) or "").strip():
            raise FueraDeMuestraError(
                f"pines_in_sample no trae {clave!r}: se necesitan google_genai y modelo "
                "(README de evaluation/data/campana/)."
            )
    return pines


def _pines_independientes_validos(meta: Mapping[str, object]) -> Mapping[str, str]:
    pines = meta.get("pines")
    if not isinstance(pines, dict) or not all(str(pines.get(c) or "").strip() for c in ("google_genai", "modelo")):
        raise FueraDeMuestraError(
            "el cache independiente no registra pines (google_genai y modelo) en su cache_meta: "
            "regeneralo con el runner de c-166, que los registra antes de clasificar."
        )
    return pines


def _verificar_clasificador_congelado(
    meta_in_sample: Mapping[str, object] | None,
    meta_independiente: Mapping[str, object] | None,
    pines_in_sample: Mapping[str, str] | None,
    rango_vigente: str | None,
    commit_in_sample: str | None,
) -> tuple[ComparabilidadClasificador, tuple[str, ...]]:
    """
    Verifica que el clasificador de ambos bloques sea el mismo o aborta con `FueraDeMuestraError`.

    Orden: datos obligatorios, `classifier_version`, modelo, version instalada de google-genai
    contra el rango in-sample y contra el pin vigente, y commit (solo si ambos lo traen).
    """
    meta_in = _meta_obligatoria(meta_in_sample, "in-sample")
    meta_out = _meta_obligatoria(meta_independiente, "independiente")
    pines_in = _pines_in_sample_validos(pines_in_sample)
    if not (rango_vigente or "").strip():
        raise FueraDeMuestraError(
            "falta el pin vigente de google-genai: tomalo de openspec/config.yaml "
            "(stack.inference), por ejemplo >=2.33,<3."
        )
    try:
        cumple_rango("0", rango_vigente)  # solo valida que el rango se pueda interpretar
    except ValueError as exc:
        raise FueraDeMuestraError(f"el pin vigente de google-genai no se puede interpretar: {exc}") from exc

    version_in, version_out = meta_in["classifier_version"], meta_out["classifier_version"]
    if version_in != version_out:
        raise FueraDeMuestraError(
            f"classifier_version distinto: in-sample {version_in!r} frente a independiente "
            f"{version_out!r}; el clasificador no esta congelado y no se reportan metricas fuera "
            "de muestra."
        )
    pines_out = _pines_independientes_validos(meta_out)
    if pines_in["modelo"] != pines_out["modelo"]:
        raise FueraDeMuestraError(
            f"modelo distinto: in-sample {pines_in['modelo']!r} frente a independiente "
            f"{pines_out['modelo']!r}; no se reportan metricas fuera de muestra."
        )
    instalada, rango_in = str(pines_out["google_genai"]), str(pines_in["google_genai"])
    for descripcion, rango in (("el pin in-sample", rango_in), ("el pin vigente de openspec/config.yaml", rango_vigente)):
        try:
            cumple = cumple_rango(instalada, rango)
        except ValueError as exc:
            raise FueraDeMuestraError(f"no se puede comparar google-genai con {descripcion}: {exc}") from exc
        if not cumple:
            raise FueraDeMuestraError(
                f"la version instalada de google-genai del cache independiente ({instalada}) no "
                f"cumple {descripcion} ({rango}); no se reportan metricas fuera de muestra."
            )

    commit_in = commit_in_sample or (str(meta_in["commit"]) if meta_in.get("commit") else None)
    commit_out = str(meta_out["commit"]) if meta_out.get("commit") else None
    limitaciones: list[str] = []
    if _es_version_exacta(rango_in):
        pass  # el in-sample registra una version concreta: la igualdad ya se verifico arriba
    else:
        limitaciones.append(
            f"versión instalada in-sample no registrada: el in-sample solo conserva el rango "
            f"declarado de google-genai ({rango_in}); la versión instalada del cache independiente "
            f"({instalada}) cumple ese rango y el pin vigente ({rango_vigente})."
        )
    if commit_in is None:
        limitaciones.append(LIMITACION_COMMIT_IN_SAMPLE)
    elif commit_out is None:
        limitaciones.append(LIMITACION_COMMIT_INDEPENDIENTE)
    elif commit_in != commit_out:
        raise FueraDeMuestraError(
            f"commit distinto: in-sample {commit_in!r} frente a independiente {commit_out!r}; "
            "el clasificador no esta congelado y no se reportan metricas fuera de muestra."
        )
    comparabilidad = ComparabilidadClasificador(
        classifier_version=str(version_out),
        modelo=str(pines_out["modelo"]),
        google_genai_instalada=instalada,
        rango_in_sample=rango_in,
        rango_vigente=str(rango_vigente),
        commit_in_sample=commit_in,
        commit_independiente=commit_out,
    )
    return comparabilidad, tuple(limitaciones)


def evaluar_fuera_de_muestra(
    predicciones_in_sample: pathlib.Path | str,
    corpus_ajuste: pathlib.Path | str,
    predicciones_independiente: pathlib.Path | str,
    corpus_independiente: pathlib.Path | str,
    *,
    pines_in_sample: Mapping[str, str] | None = None,
    rango_google_genai_vigente: str | None = None,
    commit_in_sample: str | None = None,
) -> ResultadoFueraDeMuestra:
    """
    Exactitud del clasificador congelado dentro y fuera de la muestra de ajuste.

    Lee las predicciones SOLO con `cargar_predicciones` y `cargar_cache_meta` (nunca invoca
    `run_evaluation.main()`, que llama a Gemini) y los corpus en modo de solo lectura. Devuelve
    un bloque `in-sample` (las predicciones de v9 contra el corpus de ajuste) y otro
    `out-of-sample` (las del corpus independiente), cada uno con su exactitud global y su
    desglose por etapa en cascada.

    Antes de reportar verifica que el clasificador este congelado: `classifier_version` e
    modelo identicos; la version instalada de google-genai del cache independiente debe cumplir
    el rango declarado del in-sample (`pines_in_sample`, del README de
    `evaluation/data/campana/`, porque el cache de v9 no registra pines) y el pin vigente
    (`rango_google_genai_vigente`, de `openspec/config.yaml`); el commit se compara solo si
    ambos bloques lo traen (`commit_in_sample` completa el del in-sample). Lo que no se pudo
    verificar queda en `limitaciones`.

    Antes de reportar re-ejecuta `verificar_no_solape` (c-166) y verifica que las predicciones
    cubran exactamente los casos de su corpus. Si falta alguno de los cuatro artefactos, la
    seccion se declara "no se obtuvo" nombrandolo y NO se sustituye por datos in-sample.

    Raises:
        FueraDeMuestraError: El clasificador no esta congelado, el corpus independiente
            solapa el de ajuste, las predicciones no se alinean con su corpus o falta un dato
            obligatorio.
    """
    rutas = [
        pathlib.Path(predicciones_in_sample),
        pathlib.Path(corpus_ajuste),
        pathlib.Path(predicciones_independiente),
        pathlib.Path(corpus_independiente),
    ]
    faltantes = tuple(ruta.name for ruta in rutas if not ruta.is_file())
    if faltantes:
        return ResultadoFueraDeMuestra(
            obtenido=False,
            motivo=(
                "no se obtuvo la evaluacion fuera de muestra: falta(n) "
                f"{', '.join(faltantes)}; no se reemplaza por metricas in-sample."
            ),
            faltantes=faltantes,
            in_sample=None,
            out_of_sample=None,
            comparabilidad=None,
            limitaciones=(),
        )
    ruta_in_sample, ruta_ajuste, ruta_independiente, ruta_corpus_independiente = rutas
    comparabilidad, limitaciones = _verificar_clasificador_congelado(
        cargar_cache_meta(ruta_in_sample),
        cargar_cache_meta(ruta_independiente),
        pines_in_sample,
        rango_google_genai_vigente,
        commit_in_sample,
    )
    ajuste = cargar_corpus_solo_lectura(ruta_ajuste)
    candidato = cargar_corpus_solo_lectura(ruta_corpus_independiente)
    try:
        verificar_no_solape(ajuste, candidato)
    except SolapeError as exc:
        raise FueraDeMuestraError(
            f"{exc} No se reportan metricas fuera de muestra."
        ) from exc
    predicciones_ajuste = cargar_predicciones(ruta_in_sample)
    predicciones_candidato = cargar_predicciones(ruta_independiente)
    _verificar_alineacion(predicciones_ajuste, ajuste, "in-sample")
    _verificar_alineacion(predicciones_candidato, candidato, "del corpus independiente")
    return ResultadoFueraDeMuestra(
        obtenido=True,
        motivo=None,
        faltantes=(),
        in_sample=_bloque(ROTULO_IN_SAMPLE, predicciones_ajuste, ajuste, comparabilidad.classifier_version),
        out_of_sample=_bloque(
            ROTULO_OUT_OF_SAMPLE, predicciones_candidato, candidato, comparabilidad.classifier_version
        ),
        comparabilidad=comparabilidad,
        limitaciones=limitaciones,
    )
