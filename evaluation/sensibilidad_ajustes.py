"""
Sensibilidad de las metricas frente a los ajustes del clasificador hechos con el
corpus de evaluacion (c-142, recomendacion A5 del dictamen CONEAU 2026-10-22).

El modulo es offline y de costo cero por defecto: re-mide la etapa deterministica
con el vocabulario previo a c-71 (artefacto versionado con procedencia) y reporta
el resultado en `evaluation/report_sensibilidad_ajustes.md`. Las variantes, los
comparadores y las reglas de lectura estan pre-registrados en
`openspec/changes/c-142-.../design.md` (D2-D4, D8, D9).
"""

from __future__ import annotations

import argparse
import ast
import asyncio
import hashlib
import json
import pathlib
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

from evaluation.corpus import SECTORES_CANONICOS, CasoEvaluacion
from evaluation.deterministic_measurement import (
    ContrasteDetGemEnS,
    ObservacionDeterminista,
    PrediccionCacheada,
    _es_cortocircuitable,
    contraste_det_gem_en_s,
    recolectar_observaciones,
)
from evaluation.metrics import intervalo_wilson
from evaluation.run_evaluation import CONFIRM_PAID_ENV_VAR
from evaluation.stats import ResultadoMcNemar, contraste_mcnemar

#: Umbral de cortocircuito por confianza de la logica previa a c-71 (settings.py:103 de 7925903).
UMBRAL_CONFIANZA_LEGADO = 0.90

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Valores inertes para construir `Settings` del backend sin credenciales reales.
#: El modulo es offline: NUNCA invoca a Gemini, y estos valores no son secretos
#: (son los de relleno del job de CI). Se aplican con `setdefault`.
ENTORNO_OFFLINE: Dict[str, str] = {
    "DATABASE_URL": "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy",
    "GEMINI_API_KEY": "offline-dummy-key-sin-llamadas",  # gitleaks:allow (valor ficticio: modo offline, sin llamadas)
    "PSEUDONYMIZATION_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",  # gitleaks:allow (dummy: base64url de 32 bytes "0")
    "JWT_SECRET_KEY": "ci-dummy-jwt-secret-key-for-testing-only",  # gitleaks:allow (dummy)
    "COST_GUARD_CALLER_HMAC_KEY": "ci-dummy-cost-guard-caller-hmac-key",  # gitleaks:allow (dummy)
}


def keyword_map_desde_fuente(texto: str) -> Dict[str, List[str]]:
    """
    Extrae `KEYWORD_MAP` de un fuente Python SIN ejecutarlo (D6).

    Localiza la asignacion (anotada o simple) de `KEYWORD_MAP` con `ast` y evalua
    solo su valor con `ast.literal_eval`; el modulo historico importa `app.constants`
    y no puede ejecutarse fuera de su epoca. Conserva el orden de las claves, que
    la logica de la epoca usa para desempatar.

    Raises:
        ValueError: fuente con error de sintaxis, sin `KEYWORD_MAP` o con un valor
            que no es un literal.
    """
    try:
        arbol = ast.parse(texto)
    except SyntaxError as exc:
        raise ValueError(f"el fuente tiene un error de sintaxis: {exc}") from exc

    for nodo in arbol.body:
        if isinstance(nodo, ast.AnnAssign):
            objetivos, valor = [nodo.target], nodo.value
        elif isinstance(nodo, ast.Assign):
            objetivos, valor = nodo.targets, nodo.value
        else:
            continue
        if valor is None or not any(
            isinstance(o, ast.Name) and o.id == "KEYWORD_MAP" for o in objetivos
        ):
            continue
        try:
            return ast.literal_eval(valor)
        except ValueError as exc:
            raise ValueError(
                "el valor de KEYWORD_MAP no es un literal evaluable con ast.literal_eval"
            ) from exc
    raise ValueError("el fuente no asigna KEYWORD_MAP")


# ---------------------------------------------------------------------------
# Vocabulario inyectado en una instancia del clasificador de produccion (D5)
# ---------------------------------------------------------------------------
def asegurar_backend_en_path() -> None:
    """Agrega `App/Backend` a `sys.path` (misma resolucion que el resto de `evaluation/`)."""
    ruta = str(_REPO_ROOT / "App" / "Backend")
    if ruta not in sys.path:
        sys.path.insert(0, ruta)


def preparar_entorno_offline() -> None:
    """Completa con valores inertes las variables que exige `Settings` (sin pisar las existentes)."""
    import os

    for clave, valor in ENTORNO_OFFLINE.items():
        os.environ.setdefault(clave, valor)


def _validar_mapa(mapa: Mapping[str, List[str]]) -> None:
    if set(mapa) != set(SECTORES_CANONICOS):
        raise ValueError(
            "el vocabulario debe tener exactamente las cinco claves canonicas; "
            f"recibio {sorted(mapa)}"
        )


def _compilar_patrones(mapa: Mapping[str, List[str]]) -> Dict[str, List["re.Pattern[str]"]]:
    """Compila con los mismos indicadores que `_compile_patterns` de produccion."""
    return {
        sector: [re.compile(p, re.IGNORECASE | re.UNICODE) for p in patrones]
        for sector, patrones in mapa.items()
    }


def clasificador_con_vocabulario(mapa: Mapping[str, List[str]]) -> Any:
    """
    `DeterministicClassifier` real de produccion con el vocabulario `mapa` (D5).

    Reemplaza el atributo de INSTANCIA `_patterns`, de modo que la logica `L1`
    (`_score`, `_confidence`, `extraer_features`, `score_correctitud`) es la de
    produccion y solo cambia el vocabulario. No altera el estado global: la cache
    `lru_cache` de `_compile_patterns` queda intacta.

    Raises:
        ValueError: si `mapa` no tiene las cinco claves canonicas.
        AttributeError: si produccion deja de exponer `_patterns` (acoplamiento a
            un atributo privado, declarado en D5 y vigilado por un test).
    """
    _validar_mapa(mapa)
    asegurar_backend_en_path()
    preparar_entorno_offline()
    from app.classifiers.deterministic import DeterministicClassifier  # type: ignore

    clasificador = DeterministicClassifier()
    if not hasattr(clasificador, "_patterns"):
        raise AttributeError(
            "DeterministicClassifier ya no expone `_patterns`: el adaptador de c-142 "
            "(D5) debe revisarse"
        )
    clasificador._patterns = _compilar_patrones(mapa)
    return clasificador


# ---------------------------------------------------------------------------
# Replica pura de la logica previa a c-71 (L0, D4)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoLegado:
    """Resultado de la replica L0, compatible con `recolectar_observaciones`."""

    sector_predicho: str
    confianza: float
    sectores_adicionales: List[str]
    sin_prediccion: bool = False
    ambiguo: bool = False
    score_correctitud: float = 0.0
    etapa: str = "deterministic"


class ClasificadorLegadoPreC71:
    """
    Replica de la etapa deterministica previa a c-71 (logica `L0`).

    Reproduce `DeterministicClassifier.classify` de
    `git show 7925903:App/Backend/app/classifiers/deterministic.py`:
    `confianza = w / (w + r + 1e-6)` (w: patrones distintos del ganador; r: los del
    segundo), acotada a 1; los sectores se ordenan de mayor a menor puntaje con
    orden estable, de modo que un empate (incluida la ausencia de coincidencias)
    lo gana el primer sector del mapa. El cortocircuito de la epoca era
    `confianza >= 0.90` (`git show 7925903:App/Backend/app/classifiers/hybrid.py`,
    linea 146; `deterministic_confidence_threshold = 0.90` en `settings.py:103`).
    Funcion de medicion pura: no usa `app`, `Settings` ni red.
    """

    _EPS = 1e-6

    def __init__(self, mapa: Mapping[str, List[str]], umbral: float = UMBRAL_CONFIANZA_LEGADO) -> None:
        self._patrones = _compilar_patrones(mapa)
        self.umbral = umbral

    async def classify(self, descripcion: str) -> ResultadoLegado:
        puntajes = {
            sector: float(sum(1 for p in patrones if p.search(descripcion)))
            for sector, patrones in self._patrones.items()
        }
        ordenados = sorted(puntajes.items(), key=lambda par: par[1], reverse=True)
        ganador, w = ordenados[0]
        r = ordenados[1][1] if len(ordenados) > 1 else 0.0
        confianza = min(w / (w + r + self._EPS), 1.0)
        adicionales = [s for s, p in puntajes.items() if p > 0 and s != ganador]
        return ResultadoLegado(
            sector_predicho=ganador, confianza=confianza, sectores_adicionales=adicionales
        )


ReglaCortocircuito = Callable[[ObservacionDeterminista], bool]


def regla_legado(umbral: float = UMBRAL_CONFIANZA_LEGADO) -> ReglaCortocircuito:
    """Cortocircuito de la epoca: confianza (fuerza de senal) `>= umbral`."""
    return lambda obs: obs.confianza >= umbral


def regla_vigente(umbral: float) -> ReglaCortocircuito:
    """Cortocircuito vigente (c-74): senal dominante y `score_correctitud >= umbral`."""
    return lambda obs: _es_cortocircuitable(obs) and obs.score >= umbral


# ---------------------------------------------------------------------------
# Metricas puras de sensibilidad (D3, D8)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResumenCortocircuito:
    """Casos que una regla cortocircuita, con exactitud estricta y laxa."""

    total: int
    casos: int
    aciertos: int
    aciertos_laxos: int
    exactitud: Optional[float]
    ic: Optional[Tuple[float, float]]
    cobertura: float


def resumen_cortocircuito(
    observaciones: Sequence[ObservacionDeterminista], regla: ReglaCortocircuito
) -> ResumenCortocircuito:
    """
    Casos, aciertos, exactitud, IC de Wilson al 95 % y cobertura de la regla.

    Acierto estricto: `sector_predicho == sector_asignado`; laxo: el sector
    predicho pertenece al conjunto de verdad. Sin casos seleccionados la
    exactitud y el IC son `None` (nunca `[0, 1]`).
    """
    seleccionados = [obs for obs in observaciones if regla(obs)]
    casos = len(seleccionados)
    aciertos = sum(1 for o in seleccionados if o.sector_predicho == o.sector_asignado)
    laxos = sum(1 for o in seleccionados if o.sector_predicho in o.verdad)
    total = len(observaciones)
    return ResumenCortocircuito(
        total=total,
        casos=casos,
        aciertos=aciertos,
        aciertos_laxos=laxos,
        exactitud=(aciertos / casos) if casos else None,
        ic=intervalo_wilson(aciertos, casos) if casos else None,
        cobertura=(casos / total) if total else 0.0,
    )


@dataclass(frozen=True)
class SegmentoPareado:
    """Segmento de la descomposicion: casos y aciertos estrictos de cada vocabulario."""

    casos: int
    aciertos_ref: int
    aciertos_alt: int
    ids: Tuple[str, ...] = ()


@dataclass(frozen=True)
class DescomposicionPareada:
    """Casos comunes, solo referencia y solo alternativa, mas McNemar sobre los comunes."""

    comunes: SegmentoPareado
    solo_ref: SegmentoPareado
    solo_alt: SegmentoPareado
    mcnemar_comunes: ResultadoMcNemar


def _validar_alineacion(obs_ref: Sequence[ObservacionDeterminista], obs_alt: Sequence[ObservacionDeterminista]) -> None:
    ids_ref = [o.caso_id for o in obs_ref]
    ids_alt = [o.caso_id for o in obs_alt]
    if ids_ref != ids_alt:
        raise ValueError(
            "las observaciones de referencia y alternativa deben corresponder a los mismos "
            "casos en el mismo orden"
        )


def _acierta(obs: ObservacionDeterminista) -> bool:
    return obs.sector_predicho == obs.sector_asignado


def _segmento(pares: Sequence[Tuple[ObservacionDeterminista, ObservacionDeterminista]]) -> SegmentoPareado:
    return SegmentoPareado(
        casos=len(pares),
        aciertos_ref=sum(1 for r, _ in pares if _acierta(r)),
        aciertos_alt=sum(1 for _, a in pares if _acierta(a)),
        ids=tuple(r.caso_id for r, _ in pares),
    )


def descomposicion_pareada(
    obs_ref: Sequence[ObservacionDeterminista],
    obs_alt: Sequence[ObservacionDeterminista],
    regla_ref: ReglaCortocircuito,
    regla_alt: ReglaCortocircuito,
) -> DescomposicionPareada:
    """
    Descompone los casos cortocircuitados por la referencia y por la alternativa.

    Segmentos: comunes (ambas reglas cortocircuitan), solo referencia y solo
    alternativa. En cada segmento se cuentan los aciertos ESTRICTOS de la
    prediccion de etapa 1 de cada vocabulario, tambien donde ese vocabulario no
    cortocircuita (ausencia o ambiguedad cuentan como error). Los segmentos suman
    los resumenes de cada configuracion. El contraste de McNemar se calcula solo
    sobre los comunes (`contraste_mcnemar` de c-131).

    Raises:
        ValueError: si las observaciones no corresponden a los mismos casos.
    """
    _validar_alineacion(obs_ref, obs_alt)
    pares = list(zip(obs_ref, obs_alt))
    comunes = [(r, a) for r, a in pares if regla_ref(r) and regla_alt(a)]
    solo_ref = [(r, a) for r, a in pares if regla_ref(r) and not regla_alt(a)]
    solo_alt = [(r, a) for r, a in pares if not regla_ref(r) and regla_alt(a)]
    return DescomposicionPareada(
        comunes=_segmento(comunes),
        solo_ref=_segmento(solo_ref),
        solo_alt=_segmento(solo_alt),
        mcnemar_comunes=contraste_mcnemar(
            [_acierta(r) for r, _ in comunes], [_acierta(a) for _, a in comunes]
        ),
    )


@dataclass(frozen=True)
class ExactitudGlobalConCache:
    """Aciertos globales de dos vocabularios con las predicciones de Gemini fijas (E3)."""

    casos: int
    aciertos_ref: int
    aciertos_alt: int
    excluidos: Tuple[str, ...]
    mcnemar: ResultadoMcNemar


def exactitud_global_con_cache(
    obs_ref: Sequence[ObservacionDeterminista],
    obs_alt: Sequence[ObservacionDeterminista],
    cache: Mapping[str, PrediccionCacheada],
    regla: ReglaCortocircuito,
) -> ExactitudGlobalConCache:
    """
    Exactitud estricta del pipeline simulado con ambos vocabularios y UNA sola fuente
    de predicciones de Gemini (D8).

    Un caso cortocircuitado por la regla usa la prediccion de etapa 1 de ese lado;
    uno escalado usa la prediccion `gemini` de la cache. Solo se aceptan entradas
    con `etapa == "gemini"` (una entrada `deterministic` equivale a ausente). Si
    cualquiera de los lados necesita una prediccion ausente, el caso se excluye de
    AMBOS y se lista en `excluidos`. Reutiliza el criterio de
    `medir_hibrido_con_cache` sin modificarlo.
    """
    _validar_alineacion(obs_ref, obs_alt)
    aciertos_ref: List[bool] = []
    aciertos_alt: List[bool] = []
    excluidos: List[str] = []
    for ref, alt in zip(obs_ref, obs_alt):
        cacheada = cache.get(ref.caso_id)
        gemini = cacheada if (cacheada is not None and cacheada.etapa == "gemini") else None
        corta_ref, corta_alt = regla(ref), regla(alt)
        if gemini is None and not (corta_ref and corta_alt):
            excluidos.append(ref.caso_id)
            continue
        pred_ref = ref.sector_predicho if corta_ref else gemini.sector_predicho
        pred_alt = alt.sector_predicho if corta_alt else gemini.sector_predicho
        aciertos_ref.append(pred_ref == ref.sector_asignado)
        aciertos_alt.append(pred_alt == alt.sector_asignado)
    return ExactitudGlobalConCache(
        casos=len(aciertos_ref),
        aciertos_ref=sum(aciertos_ref),
        aciertos_alt=sum(aciertos_alt),
        excluidos=tuple(excluidos),
        mcnemar=contraste_mcnemar(aciertos_ref, aciertos_alt),
    )


# ---------------------------------------------------------------------------
# Control de fidelidad de la replica L0 frente a la linea base de c-71 (D4)
# ---------------------------------------------------------------------------
#: Linea base documentada por c-71 antes de su ajuste (vocabulario y logica de la
#: epoca, 200 casos). Fuente: `openspec/changes/archive/2026-10-06-c-71-hardening-
#: clasificador-determinista/proposal.md:9-13` (64 % de escalamiento = 72 casos
#: cortocircuitados; exactitud estricta 0,51 = 37/72; "pertenencia" 0,76 = 55/72;
#: sobreprediccion de Seguridad Informatica 126) y las notas de desviacion de su
#: `tasks.md` (119 casos sin coincidencias). Los porcentajes por canal implican
#: enteros unicos sobre 66 (correo), 53 (web) y 81 (telefono) casos.
LINEA_BASE_C71: Dict[str, int] = {
    "cortocircuitados": 72,
    "cortocircuitados_correo": 22,
    "cortocircuitados_web": 14,
    "cortocircuitados_telefono": 36,
    "aciertos": 37,
    "aciertos_correo": 13,
    "aciertos_web": 7,
    "aciertos_telefono": 17,
    "aciertos_laxos": 55,
    "sin_coincidencias": 119,
    "predicciones_seguridad_informatica": 126,
}

#: Valores de `canal_origen` del corpus real para cada canal de la linea base.
CANALES_CORPUS: Dict[str, str] = {
    "correo": "correo electrónico",
    "web": "formulario web",
    "telefono": "llamada telefónica",
}


@dataclass(frozen=True)
class FilaFidelidad:
    """Una metrica de la linea base documentada frente a la reproducida por la replica."""

    metrica: str
    documentado: int
    reproducido: int
    coincide: bool


def comparar_linea_base_c71(
    obs_legado: Sequence[ObservacionDeterminista],
    canal_por_caso: Mapping[str, Optional[str]],
    documentado: Mapping[str, int] = LINEA_BASE_C71,
    canales_corpus: Mapping[str, str] = CANALES_CORPUS,
    regla: Optional[ReglaCortocircuito] = None,
) -> List[FilaFidelidad]:
    """
    Compara cada metrica de la linea base de c-71 con lo que reproduce la replica L0.

    Cada fila queda "coincide" (igualdad exacta de enteros) o "difiere"; nunca se
    ajusta la replica a los datos. `sin_coincidencias` cuenta los casos con
    confianza 0,0 (la formula de la epoca solo da 0,0 si el ganador no tiene
    patrones) y `predicciones_seguridad_informatica` los casos cuyo sector
    predicho es el primero del mapa canonico.
    """
    regla = regla or regla_legado()
    cortos = [o for o in obs_legado if regla(o)]

    def por_canal(seleccion: Sequence[ObservacionDeterminista], canal: str) -> List[ObservacionDeterminista]:
        return [o for o in seleccion if canal_por_caso.get(o.caso_id) == canales_corpus[canal]]

    reproducido: Dict[str, int] = {"cortocircuitados": len(cortos)}
    for canal in canales_corpus:
        reproducido[f"cortocircuitados_{canal}"] = len(por_canal(cortos, canal))
    reproducido["aciertos"] = sum(1 for o in cortos if _acierta(o))
    for canal in canales_corpus:
        reproducido[f"aciertos_{canal}"] = sum(1 for o in por_canal(cortos, canal) if _acierta(o))
    reproducido["aciertos_laxos"] = sum(1 for o in cortos if o.sector_predicho in o.verdad)
    reproducido["sin_coincidencias"] = sum(1 for o in obs_legado if o.confianza == 0.0)
    reproducido["predicciones_seguridad_informatica"] = sum(
        1 for o in obs_legado if o.sector_predicho == SECTORES_CANONICOS[0]
    )
    return [
        FilaFidelidad(metrica, documentado[metrica], valor, documentado[metrica] == valor)
        for metrica, valor in reproducido.items()
    ]


# ---------------------------------------------------------------------------
# Reporte (D10)
# ---------------------------------------------------------------------------
NO_COMPUTABLE = "no computable"
NO_COMPUTADO = "no computado"
NO_APLICABLE = "no aplicable"

MOTIVO_PLIEGUES = (
    "El diff de c-71 (commit 1368fd8) solo agrega 62 patrones bajo cinco comentarios de "
    "bloque por sector y no registra que casos del corpus motivaron cada patron; el mensaje "
    "del commit y los artefactos de c-71 describen el procedimiento en forma generica. "
    "Reconstruir el vocabulario por pliegues exigiria una regla de atribucion por patron "
    "que el repositorio no permite verificar, y el resultado dependeria de la regla elegida "
    "(un grado de libertad que el pre-registro D2 excluye). Reversible si los autores "
    "aportan la atribucion por patron."
)


@dataclass(frozen=True)
class ResultadoNivelA:
    """Nivel a del prompt: etapa Gemini con y sin los casos motivadores de c-72 (D9)."""

    motivadores_en_escalados: Tuple[str, ...]
    casos: int
    aciertos: int
    casos_sin_motivadores: int
    aciertos_sin_motivadores: int


@dataclass(frozen=True)
class ComparacionCorridas:
    """Comparacion pareada de dos corridas de la etapa Gemini sobre los mismos casos."""

    casos: int
    aciertos_a: int
    aciertos_b: int
    mcnemar: ResultadoMcNemar
    excluidos: Tuple[str, ...] = ()


@dataclass(frozen=True)
class ResultadoNivelB:
    """Nivel b del prompt: clasificacion de la version del prompt de la FORCE-ESCALATE (D9)."""

    clasificacion: str
    generated_at: Optional[str]
    comparacion: Optional[ComparacionCorridas] = None


@dataclass(frozen=True)
class ResultadosSensibilidad:
    """Todo lo que el reporte necesita; los opcionales en None se rotulan segun su caso."""

    procedencia: Mapping[str, Any]
    evaluada: ResumenCortocircuito
    esperada_evaluada: Tuple[int, int]
    variante_principal: ResumenCortocircuito
    descomposicion: DescomposicionPareada
    referencia_historica: ResumenCortocircuito
    fidelidad: Sequence[FilaFidelidad]
    global_cache: Optional[ExactitudGlobalConCache] = None
    global_documentado: Optional[int] = None
    piso_v1: Optional[ContrasteDetGemEnS] = None
    piso_v0: Optional[ContrasteDetGemEnS] = None
    nivel_a: Optional[ResultadoNivelA] = None
    nivel_b: Optional[ResultadoNivelB] = None
    nivel_c: Optional[Any] = None


def _fmt(valor: Optional[float]) -> str:
    return NO_APLICABLE if valor is None else f"{valor:.4f}"


def _fmt_ic(ic: Optional[Tuple[float, float]]) -> str:
    return NO_APLICABLE if ic is None else f"[{ic[0]:.4f}, {ic[1]:.4f}]"


def _lineas_resumen(resumen: ResumenCortocircuito) -> List[str]:
    return [
        f"- Casos cortocircuitados: {resumen.casos}/{resumen.total} "
        f"(cobertura {resumen.cobertura:.4f}).",
        f"- Aciertos estrictos: {resumen.aciertos}/{resumen.casos}; exactitud "
        f"{_fmt(resumen.exactitud)}; IC de Wilson al 95 %: {_fmt_ic(resumen.ic)}.",
        f"- Aciertos laxos (sector dentro del conjunto de verdad): "
        f"{resumen.aciertos_laxos}/{resumen.casos}.",
    ]


def _lineas_mcnemar(m: ResultadoMcNemar, rotulo_a: str, rotulo_b: str) -> List[str]:
    lineas = [
        f"- Tabla 2x2 ({m.pares} pares): ambas aciertan {m.ambas}; solo {rotulo_a} (b) "
        f"{m.solo_a}; solo {rotulo_b} (c) {m.solo_b}; ninguna {m.ninguna}."
    ]
    if not m.aplicable:
        lineas.append("- McNemar: no aplicable (sin discordancias, b + c = 0).")
    else:
        lineas.append(
            f"- McNemar: p binomial exacto bilateral {m.p_exacto:.4f}; chi-cuadrado corregido "
            f"{m.estadistico:.4f} (p = {m.p_corregido:.4f}); p primario {m.p_primario:.4f} "
            f"(criterio {m.criterio}). Evidencia descriptiva, sin correccion por multiplicidad."
        )
    return lineas


def _seccion_procedencia(p: Mapping[str, Any]) -> List[str]:
    blobs = p.get("blobs", {})
    sha = p.get("sha256_artefactos", {})
    pesos = p.get("pesos", {})
    lineas = [
        "## Procedencia",
        "",
        f"- SHA-256 del corpus: `{p.get('corpus_sha256')}`.",
        f"- Punto de operacion vigente (Settings): tau = {float(p.get('tau', 0.0)):.4f}; "
        "pesos del score de correctitud: "
        + ", ".join(f"{k} = {float(v):.4f}" for k, v in pesos.items())
        + ".",
    ]
    for etiqueta, blob in blobs.items():
        lineas.append(f"- Blob `{etiqueta}`: `{blob}`.")
    for nombre, digest in sha.items():
        lineas.append(f"- SHA-256 de `{nombre}`: `{digest}`.")
    meta_fe = p.get("cache_fe_meta") or {}
    if meta_fe:
        lineas.append(
            "- Cache FORCE-ESCALATE usada en E3/E4: `classifier_version` "
            f"`{meta_fe.get('classifier_version')}`, `corpus_hash` "
            f"`{meta_fe.get('corpus_hash')}` (no coincide con el del corpus vigente). "
            "La guarda `verificar_cache_contra_corpus` verifico identificador, descripcion y "
            "sector asignado de las 200 entradas (0 diferencias); el uso de la cache fue "
            "confirmado por los autores."
        )
    lineas.append(
        "- Pre-registro: variantes, comparadores y reglas de lectura fijados en el design "
        "de c-142 (D2-D4, D8, D9) antes de computar; todas se reportan cualquiera sea el resultado."
    )
    return lineas


def _seccion_evaluada(r: ResultadosSensibilidad) -> List[str]:
    esperados = r.esperada_evaluada
    reproduce = (r.evaluada.casos, r.evaluada.aciertos) == tuple(esperados)
    return [
        "## Configuracion evaluada (V1 + L1)",
        "",
        "Vocabulario vigente (151 patrones) con la logica y el punto de operacion vigentes, "
        "por el adaptador del clasificador de produccion.",
        "",
        *_lineas_resumen(r.evaluada),
        f"- Reproduccion de la configuracion evaluada: {r.evaluada.casos}/{r.evaluada.aciertos} "
        f"frente a {esperados[0]}/{esperados[1]} esperados: "
        f"{'coincide' if reproduce else 'difiere'}.",
    ]


def _fila_segmento(nombre: str, s: SegmentoPareado) -> str:
    return f"| {nombre} | {s.casos} | {s.aciertos_ref} | {s.aciertos_alt} |"


def _seccion_principal(r: ResultadosSensibilidad) -> List[str]:
    d = r.descomposicion
    diferencia = (
        None
        if r.evaluada.exactitud is None or r.variante_principal.exactitud is None
        else r.evaluada.exactitud - r.variante_principal.exactitud
    )
    return [
        "## Variante principal: vocabulario previo a c-71 con la logica vigente (V0 + L1)",
        "",
        "Ablacion de un solo factor: 89 patrones previos a c-71 (blob 858f1c6), misma logica "
        "y mismo punto de operacion.",
        "",
        *_lineas_resumen(r.variante_principal),
        f"- Diferencia descriptiva de exactitud (V1 - V0): {_fmt(diferencia)}; los conjuntos de "
        "casos difieren, por lo que no es una diferencia pareada.",
        "",
        "Descomposicion pareada (aciertos estrictos de la etapa 1 de cada vocabulario):",
        "",
        "| Segmento | Casos | Aciertos V1 | Aciertos V0 |",
        "|---|---|---|---|",
        _fila_segmento("Cortocircuitados por ambos", d.comunes),
        _fila_segmento("Solo V1 (aporta la ampliacion de c-71)", d.solo_ref),
        _fila_segmento("Solo V0", d.solo_alt),
        "",
        "McNemar sobre los casos comunes (V1 frente a V0):",
        "",
        *_lineas_mcnemar(d.mcnemar_comunes, "V1", "V0"),
    ]


def _seccion_historica(r: ResultadosSensibilidad) -> List[str]:
    lineas = [
        "## Referencia historica: vocabulario y logica previos a c-71 (V0 + L0)",
        "",
        "Replica pura de la logica de 7925903 (confianza w/(w + r + 1e-6), cortocircuito con "
        "confianza >= 0.90). Sirve de control de fidelidad contra la linea base documentada "
        "por c-71 y de referencia del punto de partida; no se lee como cota del sesgo.",
        "",
        *_lineas_resumen(r.referencia_historica),
        "",
        "Control de fidelidad (documentado por c-71 frente a reproducido):",
        "",
        "| Metrica | Documentado | Reproducido | Estado |",
        "|---|---|---|---|",
    ]
    for f in r.fidelidad:
        estado = "coincide" if f.coincide else "difiere"
        lineas.append(f"| {f.metrica} | {f.documentado} | {f.reproducido} | {estado} |")
    return lineas


def _seccion_pliegues() -> List[str]:
    return ["## Variante por pliegues", "", f"- Estado: no factible. {MOTIVO_PLIEGUES}"]


def _lineas_piso(rotulo: str, c: Optional[ContrasteDetGemEnS]) -> List[str]:
    if c is None:
        return [f"- {rotulo}: {NO_COMPUTABLE} con los artefactos disponibles."]
    lineas = [
        f"- {rotulo}: |S| = {c.tamano_s}; pares {c.pares}; excluidos "
        f"{', '.join(c.excluidos) if c.excluidos else 'ninguno'}.",
    ]
    if c.pares:
        lineas.append(
            f"- {rotulo}: exactitud de la etapa de reglas {_fmt(c.exactitud_det)} "
            f"({c.aciertos_det}/{c.pares}); de Gemini {_fmt(c.exactitud_gem)} "
            f"({c.aciertos_gem}/{c.pares})."
        )
    lineas += [f"  {linea}" for linea in _lineas_mcnemar(c.mcnemar, "reglas", "Gemini")]
    return lineas


def _seccion_global(r: ResultadosSensibilidad) -> List[str]:
    lineas = ["## Sensibilidad global y piso comparativo", ""]
    g = r.global_cache
    if g is None:
        lineas.append(
            f"- E3 (exactitud global con las predicciones de Gemini fijas): {NO_COMPUTABLE} "
            "con los artefactos disponibles (requiere la cache FORCE-ESCALATE verificada)."
        )
    else:
        documentado = (
            ""
            if r.global_documentado is None
            else f" (documentado sobre los 200 casos: {r.global_documentado})"
        )
        lineas += [
            f"- E3: aciertos estrictos globales sobre {g.casos} casos con una sola fuente de "
            f"predicciones de Gemini: V1 {g.aciertos_ref}/{g.casos}{documentado}; "
            f"V0 {g.aciertos_alt}/{g.casos}.",
            "- E3: casos excluidos de ambos lados (sin prediccion de Gemini): "
            f"{', '.join(g.excluidos) if g.excluidos else 'ninguno'}.",
            *[f"  {linea}" for linea in _lineas_mcnemar(g.mcnemar, "V1", "V0")],
        ]
    lineas += _lineas_piso("E4 referencia en muestra (V1)", r.piso_v1)
    lineas += _lineas_piso("E4 (V0)", r.piso_v0)
    return lineas


def _lineas_nivel_a(a: Optional[ResultadoNivelA]) -> List[str]:
    if a is None:
        return [
            f"- Nivel a (sin los casos motivadores de c-72): {NO_COMPUTABLE} "
            "(requiere la cache oficial)."
        ]
    if not a.motivadores_en_escalados:
        return [
            f"- Nivel a: {NO_APLICABLE}; ninguno de los casos motivadores (R002, R038, R015) "
            f"esta entre los {a.casos} casos escalados a Gemini."
        ]
    return [
        f"- Nivel a: motivadores entre los {a.casos} casos escalados: "
        f"{', '.join(a.motivadores_en_escalados)}.",
        f"- Nivel a: exactitud de la etapa Gemini con todos los casos {a.aciertos}/{a.casos}; "
        f"sin los motivadores {a.aciertos_sin_motivadores}/{a.casos_sin_motivadores}.",
    ]


def _lineas_nivel_b(b: Optional[ResultadoNivelB]) -> List[str]:
    if b is None:
        return [
            "- Nivel b (FORCE-ESCALATE frente a corrida oficial): "
            f"{NO_COMPUTABLE} (requiere ambas caches)."
        ]
    lineas = [
        "- Nivel b: version del prompt de la FORCE-ESCALATE clasificada como "
        f"\"{b.clasificacion}\" (cache_meta.generated_at: {b.generated_at or 'ausente'}).",
    ]
    if b.comparacion is None:
        lineas.append(
            f"- Nivel b: {NO_APLICABLE} (solo la clasificacion \"previa confirmada\" habilita la "
            "comparacion pareada de la FORCE-ESCALATE frente a la corrida oficial)."
        )
    else:
        c = b.comparacion
        lineas += [
            f"- Nivel b: FORCE-ESCALATE {c.aciertos_a}/{c.casos} frente a corrida oficial "
            f"{c.aciertos_b}/{c.casos}; la diferencia confunde el efecto de las reglas con la "
            "variabilidad entre corridas (temperatura 0.3).",
            *[f"  {linea}" for linea in _lineas_mcnemar(c.mcnemar, "FORCE-ESCALATE", "oficial")],
        ]
    return lineas


def _seccion_prompt(r: ResultadosSensibilidad) -> List[str]:
    lineas = [
        "## Sensibilidad del prompt",
        "",
        "Las reglas de frontera de c-72 solo influyeron en los casos que la configuracion "
        "evaluada escala a Gemini. Niveles de evidencia (c > b > a > ninguno, D9).",
        "",
        *_lineas_nivel_a(r.nivel_a),
        *_lineas_nivel_b(r.nivel_b),
    ]
    if r.nivel_c is None:
        lineas.append(
            f"- Nivel c (ablacion controlada de dos brazos, corrida paga): {NO_COMPUTADO}; "
            "requiere autorizacion explicita y no se ejecuto."
        )
    else:
        lineas += r.nivel_c.lineas()
    return lineas


def formatear_reporte_sensibilidad(r: ResultadosSensibilidad) -> str:
    """
    Reporte de sensibilidad en Markdown, determinista y sin marcas de tiempo (D10).

    Cuatro decimales con punto decimal. Las salidas que no se pueden calcular se
    rotulan "no computable" (faltan artefactos), "no computado" (nivel pago no
    ejecutado) o "no aplicable" (sin discordancias o sin casos).
    """
    bloques = [
        ["# Sensibilidad frente a los ajustes del clasificador (c-142)"],
        _seccion_procedencia(r.procedencia),
        _seccion_evaluada(r),
        _seccion_principal(r),
        _seccion_historica(r),
        _seccion_pliegues(),
        _seccion_global(r),
        _seccion_prompt(r),
    ]
    return "\n\n".join("\n".join(b) for b in bloques) + "\n"


# ---------------------------------------------------------------------------
# Sensibilidad del prompt sin costo: niveles a y b (D9)
# ---------------------------------------------------------------------------
#: Propuesta de c-72 (commit 4fedce8, 2026-10-05 21:50 -0300).
PROPUESTA_C72 = datetime(2026, 10, 6, 0, 50, 5, tzinfo=timezone.utc)
#: Aplicacion de c-72 (commit a76851e, 2026-10-06 16:38 -0300).
APLICACION_C72 = datetime(2026, 10, 6, 19, 38, 20, tzinfo=timezone.utc)
#: Casos motivadores documentados de las reglas de frontera (propuesta de c-72 y su test).
MOTIVADORES_C72 = ("R002", "R038", "R015")


def clasificar_prompt_de_la_cache(generated_at: Optional[str]) -> str:
    """
    Clasifica la version del prompt de una cache por su `cache_meta.generated_at` (D9).

    - "previa confirmada": anterior a la propuesta de c-72;
    - "probablemente previa": anterior a su aplicacion;
    - "posterior": en otro caso;
    - "indeterminada": sin fecha o con una fecha que no se puede interpretar.
    Una fecha sin zona horaria se interpreta como UTC.
    """
    if not generated_at:
        return "indeterminada"
    try:
        momento = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
    except ValueError:
        return "indeterminada"
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    if momento < PROPUESTA_C72:
        return "previa confirmada"
    if momento < APLICACION_C72:
        return "probablemente previa"
    return "posterior"


def _prediccion_gemini(cache: Mapping[str, PrediccionCacheada], caso_id: str) -> Optional[PrediccionCacheada]:
    cacheada = cache.get(caso_id)
    return cacheada if (cacheada is not None and cacheada.etapa == "gemini") else None


def calcular_nivel_a(
    observaciones: Sequence[ObservacionDeterminista],
    cache_oficial: Mapping[str, PrediccionCacheada],
    regla: ReglaCortocircuito,
    motivadores: Sequence[str] = MOTIVADORES_C72,
) -> ResultadoNivelA:
    """
    Exactitud de la etapa Gemini sobre los casos escalados, con y sin los motivadores (nivel a).

    Los escalados son los que `regla` no cortocircuita; sus predicciones salen de la
    cache OFICIAL (entradas `gemini`). Es una cota debil: solo retira la influencia
    directa de los casos documentados.

    Raises:
        ValueError: si un caso escalado no tiene prediccion de Gemini en la cache.
    """
    escalados = [o for o in observaciones if not regla(o)]
    faltantes = [o.caso_id for o in escalados if _prediccion_gemini(cache_oficial, o.caso_id) is None]
    if faltantes:
        raise ValueError(
            "la cache no tiene prediccion de Gemini para los casos escalados: " + ", ".join(faltantes)
        )
    aciertos = {
        o.caso_id: _prediccion_gemini(cache_oficial, o.caso_id).sector_predicho == o.sector_asignado
        for o in escalados
    }
    presentes = tuple(m for m in motivadores if m in aciertos)
    resto = [i for i in aciertos if i not in presentes]
    return ResultadoNivelA(
        motivadores_en_escalados=presentes,
        casos=len(aciertos),
        aciertos=sum(aciertos.values()),
        casos_sin_motivadores=len(resto),
        aciertos_sin_motivadores=sum(aciertos[i] for i in resto),
    )


def comparar_corridas(
    observaciones: Sequence[ObservacionDeterminista],
    regla: ReglaCortocircuito,
    cache_a: Mapping[str, PrediccionCacheada],
    cache_b: Mapping[str, PrediccionCacheada],
) -> ComparacionCorridas:
    """
    Compara la etapa Gemini de dos corridas sobre los casos escalados por `regla`.

    Solo cuentan las entradas `gemini`; un caso sin ellas en alguna corrida se
    excluye y se lista. Sin correccion por multiplicidad; la diferencia confunde el
    efecto del prompt con la variabilidad entre corridas.
    """
    aciertos_a: List[bool] = []
    aciertos_b: List[bool] = []
    excluidos: List[str] = []
    for obs in observaciones:
        if regla(obs):
            continue
        pa, pb = _prediccion_gemini(cache_a, obs.caso_id), _prediccion_gemini(cache_b, obs.caso_id)
        if pa is None or pb is None:
            excluidos.append(obs.caso_id)
            continue
        aciertos_a.append(pa.sector_predicho == obs.sector_asignado)
        aciertos_b.append(pb.sector_predicho == obs.sector_asignado)
    return ComparacionCorridas(
        casos=len(aciertos_a),
        aciertos_a=sum(aciertos_a),
        aciertos_b=sum(aciertos_b),
        mcnemar=contraste_mcnemar(aciertos_a, aciertos_b),
        excluidos=tuple(excluidos),
    )


def calcular_nivel_b(
    generated_at: Optional[str],
    observaciones: Sequence[ObservacionDeterminista],
    regla: ReglaCortocircuito,
    cache_fe: Mapping[str, PrediccionCacheada],
    cache_oficial: Mapping[str, PrediccionCacheada],
) -> ResultadoNivelB:
    """
    Clasifica el prompt de la FORCE-ESCALATE y, solo si es "previa confirmada",
    compara su etapa Gemini con la de la corrida oficial (nivel b, D9).
    """
    clasificacion = clasificar_prompt_de_la_cache(generated_at)
    comparacion = (
        comparar_corridas(observaciones, regla, cache_fe, cache_oficial)
        if clasificacion == "previa confirmada"
        else None
    )
    return ResultadoNivelB(clasificacion, generated_at, comparacion)


# ---------------------------------------------------------------------------
# Ablacion paga del prompt (nivel c, D9): seleccion de casos
# ---------------------------------------------------------------------------
def seleccionar_casos_escalados(
    observaciones: Sequence[ObservacionDeterminista], regla: ReglaCortocircuito
) -> List[ObservacionDeterminista]:
    """Casos que la configuracion NO cortocircuita (los que llegan a Gemini), en el orden del corpus."""
    return [obs for obs in observaciones if not regla(obs)]


# ---------------------------------------------------------------------------
# Punto de entrada offline (D10)
# ---------------------------------------------------------------------------
REPORT_SENSIBILIDAD_PATH = pathlib.Path(__file__).parent / "report_sensibilidad_ajustes.md"


class ConfiguracionNoReproducidaError(RuntimeError):
    """La configuracion evaluada (V1 + L1) no reproduce los conteos esperados (D4)."""


def verificar_cache_contra_corpus(ruta: pathlib.Path, corpus: Sequence[CasoEvaluacion]) -> None:
    """
    Verifica que una cache de predicciones corresponde, caso por caso, al corpus.

    Compara identificador, descripcion y sector asignado. Una cache cuyo `corpus_hash`
    difiere del vigente (por ejemplo, por cambios de otros campos del archivo) solo
    es utilizable como fuente de predicciones de Gemini si pasa esta verificacion.

    Raises:
        ValueError: si falta un caso o difiere la descripcion o el sector de alguno.
    """
    datos = json.loads(pathlib.Path(ruta).read_text(encoding="utf-8"))
    items = datos.get("predictions") if isinstance(datos, dict) else datos
    por_id = {str(item["caso_id"]): item for item in items or []}
    problemas: List[str] = []
    for caso in corpus:
        item = por_id.get(caso.id)
        if item is None:
            problemas.append(f"{caso.id}: ausente en la cache")
        elif item.get("descripcion") != caso.descripcion:
            problemas.append(f"{caso.id}: descripcion distinta")
        elif item.get("sector_asignado") != caso.sector_asignado:
            problemas.append(f"{caso.id}: sector asignado distinto")
    extra = sorted(set(por_id) - {c.id for c in corpus})
    problemas += [f"{i}: no esta en el corpus" for i in extra]
    if problemas:
        raise ValueError(
            f"la cache {pathlib.Path(ruta).name} no corresponde al corpus: " + "; ".join(problemas)
        )


def _cargar_cache(ruta: Optional[pathlib.Path], corpus: Sequence[CasoEvaluacion]):
    """Cache de predicciones verificada contra el corpus, con su `cache_meta`; None si no existe."""
    if ruta is None or not pathlib.Path(ruta).exists():
        return None
    from evaluation.deterministic_measurement import cargar_predicciones_cacheadas
    from evaluation.run_evaluation import cargar_cache_meta

    verificar_cache_contra_corpus(ruta, corpus)
    meta = cargar_cache_meta(pathlib.Path(ruta)) or {}
    return cargar_predicciones_cacheadas(ruta), meta


async def main(
    corpus: Sequence[CasoEvaluacion],
    *,
    vocab_v1: Mapping[str, List[str]],
    vocab_v0: Mapping[str, List[str]],
    umbral: float,
    vocab_legado: Optional[Mapping[str, List[str]]] = None,
    fabrica_vocabulario: Callable[[Mapping[str, List[str]]], Any] = clasificador_con_vocabulario,
    fabrica_legado: Callable[[Mapping[str, List[str]]], Any] = ClasificadorLegadoPreC71,
    report_path: pathlib.Path = REPORT_SENSIBILIDAD_PATH,
    esperada_evaluada: Tuple[int, int] = (131, 97),
    linea_base: Mapping[str, int] = LINEA_BASE_C71,
    procedencia: Optional[Mapping[str, Any]] = None,
    cache_fe_path: Optional[pathlib.Path] = None,
    cache_oficial_path: Optional[pathlib.Path] = None,
    global_documentado: Optional[int] = 146,
    nivel_c: Optional[Any] = None,
    motivadores: Sequence[str] = MOTIVADORES_C72,
) -> ResultadosSensibilidad:
    """
    Corre las variantes pre-registradas SIN Gemini y escribe solo `report_path`.

    Las fabricas se inyectan (los tests usan dobles; el camino real usa el adaptador de
    produccion y la replica L0). Las caches son opcionales: sin ellas E3, E4 y los
    niveles a y b se rotulan "no computable". El reporte nunca toca `report.md` ni
    las caches oficiales.

    Raises:
        ConfiguracionNoReproducidaError: si V1 + L1 no da `esperada_evaluada`
            (casos cortocircuitados, aciertos); no se escribe nada.
    """
    regla = regla_vigente(umbral)
    obs_v1 = await recolectar_observaciones(corpus, fabrica_vocabulario(vocab_v1))

    evaluada = resumen_cortocircuito(obs_v1, regla)
    if (evaluada.casos, evaluada.aciertos) != tuple(esperada_evaluada):
        raise ConfiguracionNoReproducidaError(
            f"la configuracion evaluada (V1 + L1) da {evaluada.casos}/{evaluada.aciertos} "
            f"(casos/aciertos) y se esperaba {esperada_evaluada[0]}/{esperada_evaluada[1]}: "
            "deriva entre el codigo y la etapa evaluada; no se reporta ninguna variante"
        )

    obs_v0 = await recolectar_observaciones(corpus, fabrica_vocabulario(vocab_v0))
    obs_l0 = await recolectar_observaciones(
        corpus, fabrica_legado(vocab_legado if vocab_legado is not None else vocab_v0)
    )
    canal_por_caso = {c.id: c.canal_origen for c in corpus}

    fe = _cargar_cache(cache_fe_path, corpus)
    oficial = _cargar_cache(cache_oficial_path, corpus)
    procedencia_efectiva = dict(procedencia or {})

    global_cache = piso_v1 = piso_v0 = nivel_b = nivel_a = None
    if fe is not None:
        cache_fe, meta_fe = fe
        generated_at_fe = meta_fe.get("generated_at")
        procedencia_efectiva["cache_fe_meta"] = meta_fe
        global_cache = exactitud_global_con_cache(obs_v1, obs_v0, cache_fe, regla)
        piso_v1 = contraste_det_gem_en_s(obs_v1, cache_fe, umbral)
        piso_v0 = contraste_det_gem_en_s(obs_v0, cache_fe, umbral)
    if oficial is not None:
        cache_oficial, _ = oficial
        nivel_a = calcular_nivel_a(obs_v1, cache_oficial, regla, motivadores)
    if fe is not None and oficial is not None:
        nivel_b = calcular_nivel_b(generated_at_fe, obs_v1, regla, cache_fe, cache_oficial)

    resultados = ResultadosSensibilidad(
        procedencia=procedencia_efectiva,
        evaluada=evaluada,
        esperada_evaluada=tuple(esperada_evaluada),
        variante_principal=resumen_cortocircuito(obs_v0, regla),
        descomposicion=descomposicion_pareada(obs_v1, obs_v0, regla, regla),
        referencia_historica=resumen_cortocircuito(obs_l0, regla_legado()),
        fidelidad=comparar_linea_base_c71(obs_l0, canal_por_caso, linea_base),
        global_cache=global_cache,
        global_documentado=global_documentado,
        piso_v1=piso_v1,
        piso_v0=piso_v0,
        nivel_a=nivel_a,
        nivel_b=nivel_b,
        nivel_c=nivel_c,
    )
    report_path = pathlib.Path(report_path)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(formatear_reporte_sensibilidad(resultados), encoding="utf-8")
    return resultados


# ---------------------------------------------------------------------------
# Procedencia del reporte (D10)
# ---------------------------------------------------------------------------
DATOS_DIR = pathlib.Path(__file__).parent / "data" / "sensibilidad_ajustes"
CORPUS_REAL_PATH = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
KEYWORDS_VIGENTE_PATH = _REPO_ROOT / "App" / "Backend" / "app" / "classifiers" / "keywords.py"
PROMPT_VIGENTE_PATH = _REPO_ROOT / "docs" / "prompt_gemini.txt"


def blob_git(contenido: bytes) -> str:
    """
    Identificador de blob de git del contenido, con fines de linea normalizados a LF.

    Equivale a `git hash-object` del blob versionado (que se guarda con LF) aunque el
    checkout tenga CRLF (`core.autocrlf=true`); permite verificar el blob vigente sin git.
    """
    datos = contenido.replace(b"\r\n", b"\n")
    return hashlib.sha1(b"blob %d\0" % len(datos) + datos).hexdigest()


def leer_punto_de_operacion() -> Tuple[float, Dict[str, float]]:
    """tau y pesos del score de correctitud vigentes, leidos de `Settings` (sin Gemini)."""
    asegurar_backend_en_path()
    preparar_entorno_offline()
    from app.config.settings import get_settings  # type: ignore

    s = get_settings()
    return float(s.deterministic_score_threshold), {
        "margen": float(s.deterministic_score_weight_margin),
        "evidencia": float(s.deterministic_score_weight_evidence),
        "densidad": float(s.deterministic_score_weight_density),
    }


def construir_procedencia(
    corpus_path: pathlib.Path,
    umbral: float,
    pesos: Mapping[str, float],
    datos_dir: pathlib.Path = DATOS_DIR,
) -> Dict[str, Any]:
    """Procedencia del reporte: SHA-256 del corpus y de los artefactos, blobs, tau y pesos."""
    procedencia_json = json.loads((datos_dir / "procedencia.json").read_text(encoding="utf-8"))
    archivos = procedencia_json["archivos"]
    corpus_sha256 = None
    if pathlib.Path(corpus_path).exists():
        corpus_sha256 = hashlib.sha256(
            pathlib.Path(corpus_path).read_bytes().replace(b"\r\n", b"\n")
        ).hexdigest()
    return {
        "corpus_sha256": corpus_sha256,
        "tau": umbral,
        "pesos": dict(pesos),
        "blobs": {
            "keywords_pre_c71 (7925903)": archivos["keywords_pre_c71.json"]["blob"],
            "keywords_vigente": blob_git(KEYWORDS_VIGENTE_PATH.read_bytes()),
            "prompt_pre_c72 (a76851e^)": archivos["prompt_gemini_pre_c72.txt"]["blob"],
            "prompt_vigente": blob_git(PROMPT_VIGENTE_PATH.read_bytes()),
        },
        "sha256_artefactos": {
            nombre: hashlib.sha256((datos_dir / nombre).read_bytes()).hexdigest() for nombre in archivos
        },
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
_CACHE_FE_VIVA = "evaluation/predicciones_calibracion.json"
_CACHE_FE_EVIDENCIA = "evaluation/evidence/predicciones_calibracion_hybrid-v2_2026-10-07.json"
_CACHE_OFICIAL_VIVA = "evaluation/predicciones.json"
_CACHE_OFICIAL_EVIDENCIA = "evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json"

#: Fuente unica de la credencial real en el camino pago (D1). Los caminos offline
#: NO la leen: usan los valores inertes de `ENTORNO_OFFLINE` para construir `Settings`.
_ENV_BACKEND_PATH = _REPO_ROOT / "App" / "Backend" / ".env"


class CredencialPagaAusenteError(RuntimeError):
    """El camino pago no encontro la credencial del proveedor en el entorno ni en el archivo."""


def resolver_credencial_paga(ruta_env: pathlib.Path = _ENV_BACKEND_PATH) -> str:
    """
    Resuelve la credencial real del proveedor para el camino pago (D1).

    Prioridad: una credencial ya presente en `os.environ` que NO sea el valor inerte
    de `ENTORNO_OFFLINE`; en su defecto, la del archivo `App/Backend/.env` (leida con
    `python-dotenv`), que se inyecta en `os.environ` SOBRESCRIBIENDO cualquier valor
    inerte previo (por ejemplo, el que dejo `preparar_entorno_offline`). Sin ninguna
    de las dos fuentes, falla con un error claro.

    Raises:
        CredencialPagaAusenteError: no hay credencial en el entorno ni en el archivo.
    """
    import os

    from dotenv import dotenv_values

    valor_inerte = ENTORNO_OFFLINE["GEMINI_API_KEY"]
    del_entorno = os.environ.get("GEMINI_API_KEY")
    if del_entorno and del_entorno != valor_inerte:
        return del_entorno
    ruta_env = pathlib.Path(ruta_env)
    del_archivo = dotenv_values(ruta_env).get("GEMINI_API_KEY") if ruta_env.exists() else None
    if del_archivo:
        os.environ["GEMINI_API_KEY"] = del_archivo
        return del_archivo
    raise CredencialPagaAusenteError(
        "corrida paga sin credencial del proveedor: define GEMINI_API_KEY en el entorno "
        f"o en {ruta_env}; el camino pago no puede construir el clasificador con un valor inerte"
    )


def _preparar_credencial_paga() -> str:
    """Inyecta la credencial real y limpia la cache de `Settings` antes de construir el clasificador."""
    credencial = resolver_credencial_paga(_ENV_BACKEND_PATH)
    asegurar_backend_en_path()
    from app.config.settings import get_settings  # type: ignore

    get_settings.cache_clear()
    return credencial


def resolver_caches(repo_root: pathlib.Path) -> Tuple[Optional[pathlib.Path], Optional[pathlib.Path]]:
    """
    Cache FORCE-ESCALATE y cache oficial: la copia viva si existe y, si no, la evidencia
    congelada y versionada de `evaluation/evidence/` (c-143). None si no hay ninguna.
    """
    def primera(*candidatas: str) -> Optional[pathlib.Path]:
        for relativa in candidatas:
            ruta = pathlib.Path(repo_root) / relativa
            if ruta.exists():
                return ruta
        return None

    return (
        primera(_CACHE_FE_VIVA, _CACHE_FE_EVIDENCIA),
        primera(_CACHE_OFICIAL_VIVA, _CACHE_OFICIAL_EVIDENCIA),
    )


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m evaluation.sensibilidad_ajustes",
        description=(
            "Sensibilidad de las metricas frente a los ajustes del clasificador (c-142). "
            "Sin subcomando: corrida offline, sin Gemini, que escribe solo el reporte indicado. "
            "Subcomando `prompt`: UN brazo de la ablacion del prompt (corrida PAGA con gate)."
        ),
        # c-145 (E1): deshabilitar la resolucion por prefijo. Sin esto, en Python
        # 3.12.3 `--brazo` (opcion del subcomando `prompt`) se resuelve contra las
        # opciones de nivel superior `--brazo-vigente` / `--brazo-sin-reglas` y el
        # parser aborta con "ambiguous option". Los nombres deben ser exactos.
        allow_abbrev=False,
    )
    parser.add_argument("--corpus", type=pathlib.Path, default=CORPUS_REAL_PATH)
    parser.add_argument("--report", type=pathlib.Path, default=REPORT_SENSIBILIDAD_PATH)
    parser.add_argument("--cache-fe", type=pathlib.Path, default=None, help="cache FORCE-ESCALATE")
    parser.add_argument("--cache-oficial", type=pathlib.Path, default=None, help="cache oficial")
    parser.add_argument(
        "--esperados", nargs=2, type=int, default=[131, 97], metavar=("CASOS", "ACIERTOS"),
        help="casos cortocircuitados y aciertos que debe reproducir la configuracion evaluada",
    )
    parser.add_argument(
        "--brazo-vigente", type=pathlib.Path, default=None,
        help="predicciones del brazo con el prompt vigente (salida de `prompt --brazo vigente`)",
    )
    parser.add_argument(
        "--brazo-sin-reglas", type=pathlib.Path, default=None,
        help="predicciones del brazo sin reglas de frontera (salida de `prompt --brazo sin-reglas`)",
    )
    sub = parser.add_subparsers(dest="comando")
    prompt = sub.add_parser("prompt", help="un brazo de la ablacion del prompt (corrida paga)")
    prompt.add_argument("--brazo", choices=BRAZOS_PROMPT, required=True)
    prompt.add_argument("--corpus", dest="corpus_prompt", type=pathlib.Path, default=None)
    prompt.add_argument("--salida", type=pathlib.Path, default=None)
    prompt.add_argument(
        "--confirm-paid", dest="confirm_paid", action="store_true",
        help=f"confirma la corrida paga (o {CONFIRM_PAID_ENV_VAR}=1)",
    )
    return parser


def salida_por_defecto(brazo: str) -> pathlib.Path:
    """Archivo de salida propio de cada brazo, junto a las caches y ignorado por git."""
    return pathlib.Path(__file__).parent / f"predicciones_sensibilidad_prompt_{brazo.replace('-', '_')}.json"


def cli(argv: Optional[Sequence[str]] = None) -> int:
    """
    Punto de entrada. Devuelve 0 si todo salio bien, 1 si la replica no reproduce lo
    evaluado y 2 si la corrida paga se rechazo por falta de confirmacion.
    """
    parser = construir_parser()
    args = parser.parse_args(argv)
    if args.comando == "prompt":
        if args.salida is None:
            args.salida = salida_por_defecto(args.brazo)
        return _cli_prompt(args)
    return _cli_offline(args)


def _cargar_nivel_c(args: argparse.Namespace, oficial: Optional[Mapping[str, PrediccionCacheada]]) -> Optional[ResultadoNivelC]:
    """Nivel c a partir de las salidas de los dos brazos; None si no se indicaron ambas."""
    if args.brazo_vigente is None or args.brazo_sin_reglas is None:
        return None
    from evaluation.run_evaluation import cargar_predicciones

    return comparar_brazos(
        cargar_predicciones(args.brazo_vigente), cargar_predicciones(args.brazo_sin_reglas), oficial
    )


def _cli_offline(args: argparse.Namespace) -> int:
    from evaluation.corpus import cargar_corpus
    from evaluation.deterministic_measurement import cargar_predicciones_cacheadas

    corpus = cargar_corpus(args.corpus)
    umbral, pesos = leer_punto_de_operacion()
    fe_defecto, oficial_defecto = resolver_caches(_REPO_ROOT)
    cache_oficial = args.cache_oficial or oficial_defecto
    oficial = (
        cargar_predicciones_cacheadas(cache_oficial)
        if (cache_oficial is not None and pathlib.Path(cache_oficial).exists())
        else None
    )
    try:
        asyncio.run(
            main(
                corpus,
                vocab_v1=keyword_map_desde_fuente(KEYWORDS_VIGENTE_PATH.read_text(encoding="utf-8")),
                vocab_v0=json.loads((DATOS_DIR / "keywords_pre_c71.json").read_text(encoding="utf-8")),
                umbral=umbral,
                report_path=args.report,
                esperada_evaluada=(args.esperados[0], args.esperados[1]),
                procedencia=construir_procedencia(args.corpus, umbral, pesos),
                cache_fe_path=args.cache_fe or fe_defecto,
                cache_oficial_path=cache_oficial,
                nivel_c=_cargar_nivel_c(args, oficial),
            )
        )
    except ConfiguracionNoReproducidaError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Reporte de sensibilidad escrito en: {args.report}")
    return 0


def _construir_hybrid_real() -> Any:
    """Construye el HybridClassifier REAL (camino pago). Aislado para poder sustituirlo en tests."""
    asegurar_backend_en_path()
    from app.classifiers.hybrid import HybridClassifier  # type: ignore

    return HybridClassifier()


def _prompt_cargado_por_el_backend(brazo: str) -> str:
    """
    Prompt que el backend carga en ESTE proceso para el brazo (`GEMINI_PROMPT_PATH`).

    El backend lee el prompt al importar `gemini_classifier`; por eso cada brazo corre en
    un proceso propio. No construye ningun clasificador ni llama al proveedor.
    """
    import os

    prompt_esperado(brazo)  # valida el nombre del brazo
    ruta = PROMPT_VIGENTE_PATH if brazo == "vigente" else DATOS_DIR / "prompt_gemini_pre_c72.txt"
    os.environ["GEMINI_PROMPT_PATH"] = str(ruta)
    asegurar_backend_en_path()
    from app.config.settings import get_settings  # type: ignore

    get_settings.cache_clear()
    from app.classifiers import gemini_classifier  # type: ignore

    return gemini_classifier._PROMPT_TEMPLATE


def _meta_corrida_paga(corpus_path: pathlib.Path) -> Dict[str, Any]:
    """Metadatos de la corrida paga: modelo, temperatura, version del clasificador y hash del corpus."""
    from app.config.settings import get_settings  # type: ignore
    from evaluation.run_evaluation import _compute_corpus_hash, _version_clasificador_real

    s = get_settings()
    return {
        "gemini_model": s.gemini_model,
        "gemini_temperature": s.gemini_temperature,
        "classifier_version": _version_clasificador_real(),
        "corpus_hash": _compute_corpus_hash(pathlib.Path(corpus_path)),
    }


async def _casos_escalados_reales(corpus: Sequence[CasoEvaluacion], umbral: float) -> List[CasoEvaluacion]:
    """Casos que `V1 + L1` no cortocircuita (los 69 de la etapa Gemini), seleccionados offline."""
    observaciones = await recolectar_observaciones(
        corpus,
        clasificador_con_vocabulario(
            keyword_map_desde_fuente(KEYWORDS_VIGENTE_PATH.read_text(encoding="utf-8"))
        ),
    )
    ids = {o.caso_id for o in seleccionar_casos_escalados(observaciones, regla_vigente(umbral))}
    return [c for c in corpus if c.id in ids]


def _cli_prompt(args: argparse.Namespace) -> int:
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import PaidRunNotConfirmedError, _env_confirm_paid

    confirm_paid = args.confirm_paid or _env_confirm_paid()
    if not confirm_paid:
        print(
            "ERROR: corrida paga sin confirmar. Confirma explicitamente con --confirm-paid o "
            f"{CONFIRM_PAID_ENV_VAR}=1.",
            file=sys.stderr,
        )
        return 2
    try:
        _preparar_credencial_paga()
    except CredencialPagaAusenteError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    corpus_path = args.corpus_prompt or args.corpus
    corpus = cargar_corpus(corpus_path)
    umbral, _ = leer_punto_de_operacion()
    casos = asyncio.run(_casos_escalados_reales(corpus, umbral))
    try:
        asyncio.run(
            correr_brazo_prompt(
                casos,
                args.brazo,
                args.salida,
                confirm_paid,
                _construir_hybrid_real,
                _prompt_cargado_por_el_backend(args.brazo),
                meta=_meta_corrida_paga(corpus_path),
            )
        )
    except (PaidRunNotConfirmedError, PromptInesperadoError, ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(f"Brazo '{args.brazo}' escrito en: {args.salida}")
    return 0


# ---------------------------------------------------------------------------
# Ablacion paga del prompt (nivel c, D9): un brazo por proceso
# ---------------------------------------------------------------------------
BRAZOS_PROMPT = ("vigente", "sin-reglas")


class PromptInesperadoError(RuntimeError):
    """El prompt cargado por el backend no es el que corresponde al brazo (D9)."""


@dataclass(frozen=True)
class PromptEsperado:
    """Texto (con `.strip()`, como `_load_prompt`), SHA-256 y origen del prompt de un brazo."""

    texto: str
    sha256: str
    origen: str


def prompt_esperado(
    brazo: str,
    prompt_vigente_path: pathlib.Path = PROMPT_VIGENTE_PATH,
    datos_dir: pathlib.Path = DATOS_DIR,
) -> PromptEsperado:
    """Prompt que debe tener cargado el backend en cada brazo: vigente o previo a c-72."""
    if brazo not in BRAZOS_PROMPT:
        raise ValueError(f"brazo desconocido '{brazo}'; validos: {', '.join(BRAZOS_PROMPT)}")
    ruta = prompt_vigente_path if brazo == "vigente" else datos_dir / "prompt_gemini_pre_c72.txt"
    texto = pathlib.Path(ruta).read_text(encoding="utf-8").strip()
    origen = (
        "docs/prompt_gemini.txt"
        if brazo == "vigente"
        else "evaluation/data/sensibilidad_ajustes/prompt_gemini_pre_c72.txt"
    )
    return PromptEsperado(texto, hashlib.sha256(texto.encode("utf-8")).hexdigest(), origen)


def _rutas_oficiales() -> Tuple[pathlib.Path, ...]:
    base = pathlib.Path(__file__).parent
    return (base / "report.md", base / "predicciones.json", base / "predicciones_calibracion.json")


async def correr_brazo_prompt(
    casos: Sequence[CasoEvaluacion],
    brazo: str,
    salida: pathlib.Path,
    confirm_paid: bool,
    fabrica_clasificador: Callable[[], Any],
    prompt_cargado: str,
    *,
    meta: Optional[Mapping[str, Any]] = None,
) -> List[Any]:
    """
    Corre UN brazo de la ablacion del prompt sobre los casos escalados (corrida paga).

    Orden de las guardas, todas ANTES de construir el clasificador y de la primera
    llamada: brazo valido, ruta de salida distinta de las oficiales, confirmacion de
    corrida paga y SHA-256 del prompt cargado igual al esperado del brazo. Luego
    imprime la estimacion de costo, evalua con `evaluar_corpus` y guarda las
    predicciones con un `cache_meta` ampliado. Un `fallback` cuenta como error y suma
    en `fallbacks`; una prediccion de la etapa `deterministic` indica un caso no
    escalado y aborta sin escribir.

    Raises:
        ValueError: brazo desconocido o ruta de salida oficial.
        PaidRunNotConfirmedError: sin confirmacion explicita.
        PromptInesperadoError: el prompt cargado no es el del brazo.
        RuntimeError: una prediccion salio de la etapa deterministica.
    """
    from evaluation.run_evaluation import (
        PaidRunNotConfirmedError,
        evaluar_corpus,
        format_cost_estimation,
        guardar_predicciones,
    )

    esperado = prompt_esperado(brazo)
    salida = pathlib.Path(salida)
    if salida.resolve() in {r.resolve() for r in _rutas_oficiales()}:
        raise ValueError(f"la salida {salida} es una ruta oficial y no se puede sobrescribir")
    if not confirm_paid:
        raise PaidRunNotConfirmedError(
            "Ablacion del prompt sin confirmar: invocaria al clasificador real (corrida paga). "
            "Confirma explicitamente con --confirm-paid o EVALUATION_CONFIRM_PAID=1."
        )
    digest = hashlib.sha256(prompt_cargado.encode("utf-8")).hexdigest()
    if digest != esperado.sha256:
        raise PromptInesperadoError(
            f"el prompt cargado (SHA-256 {digest}) no es el del brazo '{brazo}' "
            f"({esperado.sha256}, {esperado.origen})"
        )

    print(format_cost_estimation(len(casos)))
    predicciones = await evaluar_corpus(list(casos), fabrica_clasificador())
    no_escalados = [p.caso_id for p in predicciones if p.etapa == "deterministic"]
    if no_escalados:
        raise RuntimeError("caso no escalado (etapa deterministica): " + ", ".join(no_escalados))

    meta = meta or {}
    cache_meta = {
        "brazo": brazo,
        "prompt_sha256": esperado.sha256,
        "prompt_origen": esperado.origen,
        "gemini_model": meta.get("gemini_model"),
        "gemini_temperature": meta.get("gemini_temperature"),
        "classifier_version": meta.get("classifier_version"),
        "corpus_hash": meta.get("corpus_hash"),
        "casos": [c.id for c in casos],
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "fallbacks": sum(1 for p in predicciones if p.etapa == "fallback"),
    }
    guardar_predicciones(predicciones, salida, cache_meta=cache_meta)
    return predicciones



@dataclass(frozen=True)
class ResultadoNivelC:
    """Nivel c: ablacion controlada del prompt (brazo vigente frente a brazo sin reglas)."""

    casos: int
    aciertos_vigente: int
    aciertos_sin_reglas: int
    reservas_vigente: int
    reservas_sin_reglas: int
    mcnemar: ResultadoMcNemar
    deriva: Optional[ComparacionCorridas] = None

    def lineas(self) -> List[str]:
        """Lineas del reporte para el nivel c (D9)."""
        lineas = [
            f"- Nivel c (ablacion controlada de dos brazos, misma sesion): prompt vigente "
            f"{self.aciertos_vigente}/{self.casos} frente a sin reglas de frontera "
            f"{self.aciertos_sin_reglas}/{self.casos}.",
            f"- Nivel c: reservas (fallback, cuentan como error): vigente {self.reservas_vigente}; "
            f"sin reglas {self.reservas_sin_reglas}.",
            *[f"  {linea}" for linea in _lineas_mcnemar(self.mcnemar, "prompt vigente", "sin reglas")],
        ]
        if self.deriva is not None:
            d = self.deriva
            lineas.append(
                f"- Nivel c: deriva del brazo control frente a la corrida oficial: {d.aciertos_a}/{d.casos} "
                f"frente a {d.aciertos_b}/{d.casos} (variabilidad entre corridas, temperatura 0.3)."
            )
            lineas += [f"  {linea}" for linea in _lineas_mcnemar(d.mcnemar, "control", "oficial")]
        return lineas


def _aciertos_brazo(predicciones: Sequence[Any]) -> Dict[str, bool]:
    """Acierto estricto por caso; una respuesta de reserva (`fallback`) cuenta como error."""
    return {
        p.caso_id: (p.etapa != "fallback" and p.sector_predicho == p.sector_asignado)
        for p in predicciones
    }


def comparar_brazos(
    pred_vigente: Sequence[Any],
    pred_sin_reglas: Sequence[Any],
    oficial: Optional[Mapping[str, PrediccionCacheada]] = None,
) -> ResultadoNivelC:
    """
    Compara los dos brazos de la ablacion del prompt sobre los mismos casos (D9, nivel c).

    Aciertos estrictos de cada brazo, reservas como error, McNemar exacto y, con la cache
    oficial, la deriva del brazo control frente a la corrida oficial.

    Raises:
        ValueError: si los brazos no corresponden a los mismos casos.
    """
    a_vigente, a_sin = _aciertos_brazo(pred_vigente), _aciertos_brazo(pred_sin_reglas)
    if set(a_vigente) != set(a_sin):
        raise ValueError("los dos brazos deben corresponder a los mismos casos")
    ids = [p.caso_id for p in pred_vigente]
    deriva = None
    if oficial is not None:
        asignados = {p.caso_id: p.sector_asignado for p in pred_vigente}
        pares = [
            (i, _prediccion_gemini(oficial, i))
            for i in ids
        ]
        validos = [(i, p) for i, p in pares if p is not None]
        deriva = ComparacionCorridas(
            casos=len(validos),
            aciertos_a=sum(a_vigente[i] for i, _ in validos),
            aciertos_b=sum(p.sector_predicho == asignados[i] for i, p in validos),
            mcnemar=contraste_mcnemar(
                [a_vigente[i] for i, _ in validos],
                [p.sector_predicho == asignados[i] for i, p in validos],
            ),
            excluidos=tuple(i for i, p in pares if p is None),
        )
    return ResultadoNivelC(
        casos=len(ids),
        aciertos_vigente=sum(a_vigente.values()),
        aciertos_sin_reglas=sum(a_sin.values()),
        reservas_vigente=sum(1 for p in pred_vigente if p.etapa == "fallback"),
        reservas_sin_reglas=sum(1 for p in pred_sin_reglas if p.etapa == "fallback"),
        mcnemar=contraste_mcnemar([a_vigente[i] for i in ids], [a_sin[i] for i in ids]),
        deriva=deriva,
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(cli())
