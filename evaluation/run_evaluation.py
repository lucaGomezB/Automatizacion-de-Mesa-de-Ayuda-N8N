"""
Runner de evaluación del clasificador híbrido (multietiqueta, C-27).

Orquesta la carga del corpus JSON, la invocación del clasificador caso por caso,
el cálculo de métricas multietiqueta y la escritura del reporte.

Uso (corpus real):
    python -m evaluation.run_evaluation

    Requiere:
    - data/corpus_evaluacion_pseudonimizado.json (no trackeado en git)
    - GEMINI_API_KEY en el entorno
    - PYTHONPATH configurado para incluir App/Backend/

Regenerar solo la sección "Tiempos" (sin Gemini, sin cache, sin gate pago):
    python -m evaluation.run_evaluation --solo-tiempos

Diseño (D1): el clasificador se inyecta por parámetro, lo que permite
    testear con FakeClassifier sin llamadas a Gemini.
    El main() real usa HybridClassifier; los tests usan FakeClassifier.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import pathlib
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

from evaluation.corpus import CasoEvaluacion, cargar_corpus
from evaluation.metrics import (
    BANDAS_CALIBRACION_DEFECTO,
    CLASES,
    ETAPAS_PIPELINE,
    ResumenExactitud,
    aciertos_estrictos,
    aciertos_laxos,
    aciertos_pertenencia,
    calibracion_por_bandas,
    calibracion_por_etapa,
    contingencia_confianza,
    desglose_exactitud,
    distribucion_confianza,
    exactitud_global,
    exactitud_subconjunto,
    f1_macro,
    f1_micro,
    f1_por_clase,
    intervalo_wilson,
    jaccard_promedio,
    matriz_confusion,
    perdida_hamming,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)
from evaluation.stats import (
    ARE_WILCOXON_MINIMA,
    ResultadoWilcoxon,
    efecto_minimo_detectable,
    escenario_sensibilidad,
    estadisticos_descriptivos,
    granularidad_manual,
    reduccion_relativa,
    reduccion_tiempos,
    shapiro_normalidad,
    tamano_efecto_dz,
    wilcoxon_tiempos_detallado,
)

# ---------------------------------------------------------------------------
# Rutas por defecto
# ---------------------------------------------------------------------------
_REPO_ROOT = pathlib.Path(__file__).parent.parent
CORPUS_REAL_PATH = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
REPORT_PATH = pathlib.Path(__file__).parent / "report.md"
PREDICCIONES_PATH = pathlib.Path(__file__).parent / "predicciones.json"


# ---------------------------------------------------------------------------
# Gate de corrida paga y estimacion de costo (C-36)
# ---------------------------------------------------------------------------
class PaidRunNotConfirmedError(RuntimeError):
    """La corrida paga fue rechazada por falta de confirmacion explicita."""


# Orden de magnitud orientativo para Gemini 2.5 Flash con un perfil de
# ~1.500 tokens de entrada y ~200 de salida. No es una tarifa de facturacion.
ESTIMATED_COST_PER_CALL_USD = 0.0002

CONFIRM_PAID_ENV_VAR = "EVALUATION_CONFIRM_PAID"
_TRUTHY_VALUES = {"1", "true", "yes"}


def estimated_cost_usd(corpus_count: int) -> float:
    """Costo total estimado de clasificar ``corpus_count`` casos."""
    return corpus_count * ESTIMATED_COST_PER_CALL_USD


def format_cost_estimation(
    corpus_count: int,
    cost_per_call: Optional[float] = None,
) -> str:
    """Renderiza la estimacion orientativa previa a una corrida paga."""
    if cost_per_call is None:
        cost_per_call = ESTIMATED_COST_PER_CALL_USD
    total = corpus_count * cost_per_call
    return "\n".join(
        [
            "Estimacion de costo (orientativa, no es una factura):",
            f"- Casos del corpus: {corpus_count}",
            f"- Costo asumido por llamada: USD {cost_per_call:.6f}",
            f"- Costo total estimado: USD {total:.6f}",
        ]
    )


def _env_confirm_paid() -> bool:
    """True si EVALUATION_CONFIRM_PAID tiene un valor verdadero (1/true/yes)."""
    value = os.environ.get(CONFIRM_PAID_ENV_VAR, "")
    return value.strip().lower() in _TRUTHY_VALUES


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------
@dataclass
class Prediccion:
    """Resultado de clasificar un caso del corpus."""

    caso_id: str
    descripcion: str
    sector_asignado: str
    sector_predicho: str
    confianza: float
    etapa: str  # "deterministic" | "gemini" | "fallback"
    sectores_adicionales: List[str] = field(default_factory=list)


class ClasificadorProtocol(Protocol):
    """Protocolo mínimo que debe cumplir el clasificador inyectado."""

    async def classify(self, descripcion: str) -> Any:
        ...


# ---------------------------------------------------------------------------
# Core: recolección de predicciones
# ---------------------------------------------------------------------------
async def evaluar_corpus(
    corpus: List[CasoEvaluacion],
    classifier: ClasificadorProtocol,
) -> List[Prediccion]:
    """
    Ejecuta el clasificador sobre cada caso del corpus y recolecta predicciones.

    Args:
        corpus: Lista de casos cargados del JSON.
        classifier: Clasificador con método `async classify(descripcion)`.

    Returns:
        Lista de Prediccion en el mismo orden que el corpus.
    """
    predicciones: List[Prediccion] = []
    for caso in corpus:
        resultado = await classifier.classify(caso.descripcion)
        pred = Prediccion(
            caso_id=caso.id,
            descripcion=caso.descripcion,
            sector_asignado=caso.sector_asignado,
            sector_predicho=resultado.sector_predicho,
            sectores_adicionales=list(resultado.sectores_adicionales),
            confianza=float(resultado.confianza),
            etapa=str(resultado.etapa),
        )
        predicciones.append(pred)
    return predicciones


# ---------------------------------------------------------------------------
# Core: generación de reporte
# ---------------------------------------------------------------------------
# Mínimo de pares que exige la prueba de Wilcoxon para reportar un resultado.
_MIN_PARES_WILCOXON = 2
# Ámbitos de las tablas de tiempos: pares (manual, automatizado) por etiqueta.
_Ambitos = List[tuple[str, List[tuple[float, float]]]]
_NO_APLICABLE = "no aplicable"
_AMBITO_GLOBAL = "Global"
_NO_CANAL = "sin canal"
# Descuentos (en segundos) de los escenarios de sensibilidad del manual (c-134).
_DESCUENTOS_SENSIBILIDAD_S = (5, 10)


def _fmt_p(valor: float) -> str:
    """Formato determinista del valor p (3 cifras significativas)."""
    return f"{valor:.3g}"


def _pares_tiempos(
    corpus: List[CasoEvaluacion],
) -> tuple[List[tuple[float, float]], int]:
    """
    Extrae los pares (manual, automatizado) válidos y cuenta los excluidos.

    Un par es válido solo si ambos tiempos son numéricos (no nulos). El orden
    se preserva para mantener el determinismo (D4).
    """
    pares: List[tuple[float, float]] = []
    excluidos = 0
    for caso in corpus:
        if caso.tiempo_manual_s is None or caso.tiempo_automatizado_s is None:
            excluidos += 1
            continue
        pares.append((float(caso.tiempo_manual_s), float(caso.tiempo_automatizado_s)))
    return pares, excluidos


def _wilcoxon_o_no_aplicable(pares: List[tuple[float, float]]) -> Optional[ResultadoWilcoxon]:
    """
    Wilcoxon sobre los pares, o None si la prueba no es aplicable.

    No aplicable cuando hay menos de `_MIN_PARES_WILCOXON` pares válidos o
    cuando no hay diferencias no nulas (scipy rechaza el caso degenerado).
    """
    if len(pares) < _MIN_PARES_WILCOXON:
        return None
    manual = [m for m, _ in pares]
    automatizado = [a for _, a in pares]
    try:
        return wilcoxon_tiempos_detallado(manual, automatizado)
    except ValueError:
        return None


def _fila_wilcoxon(
    n: int,
    resultado: Optional[ResultadoWilcoxon],
    canal: Optional[str] = None,
) -> str:
    """
    Fila de tabla de Wilcoxon; declara no aplicable cuando no hay resultado.

    Si se pasa `canal`, se antepone como primera celda (desglose por canal).
    """
    if resultado is None:
        celdas = [str(n), _NO_APLICABLE, _NO_APLICABLE, _NO_APLICABLE, _NO_APLICABLE, _NO_APLICABLE]
    else:
        celdas = [
            str(resultado.n),
            f"{resultado.estadistico:.4f}",
            f"{resultado.t_positivos:.4f}",
            f"{resultado.t_negativos:.4f}",
            _fmt_p(resultado.p),
            f"{resultado.r:.4f}",
        ]
    if canal is not None:
        celdas = [canal, *celdas]
    return "| " + " | ".join(celdas) + " |"


def _fmt_num(valor: Optional[float]) -> str:
    """Formato determinista de una cantidad (4 decimales) o "no aplicable"."""
    return _NO_APLICABLE if valor is None else f"{valor:.4f}"


def _fmt_pct(fraccion: Optional[float]) -> str:
    """Formato determinista de una fracción como porcentaje (2 decimales)."""
    return _NO_APLICABLE if fraccion is None else f"{fraccion * 100:.2f}"


def _fmt_p_opcional(valor: Optional[float]) -> str:
    """Valor p con 3 cifras significativas o "no aplicable"."""
    return _NO_APLICABLE if valor is None else _fmt_p(valor)


def _pares_por_canal(
    corpus: List[CasoEvaluacion],
) -> _Ambitos:
    """
    Agrupa los pares válidos por valor crudo de `canal_origen`.

    Orden canónico estable: conteo descendente y desempate alfabético (c-99,
    D4); un canal nulo se rotula "sin canal".
    """
    canales: Dict[Optional[str], List[tuple[float, float]]] = {}
    for caso in corpus:
        if caso.tiempo_manual_s is None or caso.tiempo_automatizado_s is None:
            continue
        canales.setdefault(caso.canal_origen, []).append(
            (float(caso.tiempo_manual_s), float(caso.tiempo_automatizado_s))
        )
    orden = sorted(canales, key=lambda c: (-len(canales[c]), str(c)))
    return [(_NO_CANAL if c is None else str(c), canales[c]) for c in orden]


def _ambitos_tiempos(
    corpus: List[CasoEvaluacion],
    pares: List[tuple[float, float]],
) -> _Ambitos:
    """Ámbitos de las tablas de c-134: fila "Global" y luego cada canal."""
    return [(_AMBITO_GLOBAL, pares), *_pares_por_canal(corpus)]


def _tabla_descriptivos(
    ambitos: _Ambitos,
) -> List[str]:
    """Tabla de descriptivos de ambos brazos, reducción relativa y no más rápidos."""
    lineas = [
        "| Ámbito | n | Manual media (s) | Manual mediana (s) | Manual desvío (s) "
        "| Manual mín (s) | Manual máx (s) | Automatizado media (s) "
        "| Automatizado mediana (s) | Automatizado desvío (s) "
        "| Automatizado mín (s) | Automatizado máx (s) "
        "| Reducción de la media (%) | Reducción de la mediana (%) | No más rápidos |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for etiqueta, pares_ambito in ambitos:
        if not pares_ambito:
            celdas = [etiqueta, "0", *([_NO_APLICABLE] * 13)]
        else:
            manual = [m for m, _ in pares_ambito]
            automatizado = [a for _, a in pares_ambito]
            dm = estadisticos_descriptivos(manual)
            da = estadisticos_descriptivos(automatizado)
            relativa = reduccion_relativa(manual, automatizado)
            no_rapidos = reduccion_tiempos(manual, automatizado).pares_no_mas_rapidos
            celdas = [
                etiqueta,
                str(dm.n),
                _fmt_num(dm.media),
                _fmt_num(dm.mediana),
                _fmt_num(dm.desvio),
                _fmt_num(dm.minimo),
                _fmt_num(dm.maximo),
                _fmt_num(da.media),
                _fmt_num(da.mediana),
                _fmt_num(da.desvio),
                _fmt_num(da.minimo),
                _fmt_num(da.maximo),
                _fmt_pct(relativa.media),
                _fmt_pct(relativa.mediana),
                str(no_rapidos),
            ]
        lineas.append("| " + " | ".join(celdas) + " |")
    return lineas


def _tabla_contraste(
    ambitos: _Ambitos,
) -> List[str]:
    """Tabla de p bilateral y unilateral, d_z y efecto mínimo detectable."""
    lineas = [
        f"| Ámbito | n | p bilateral | p unilateral | d_z | MDE (ARE = 1) "
        f"| MDE (ARE = {ARE_WILCOXON_MINIMA}) |",
        "|---|---|---|---|---|---|---|",
    ]
    for etiqueta, pares_ambito in ambitos:
        n = len(pares_ambito)
        wilcoxon = _wilcoxon_o_no_aplicable(pares_ambito)
        manual = [m for m, _ in pares_ambito]
        automatizado = [a for _, a in pares_ambito]
        mde_sin_ajuste = efecto_minimo_detectable(n) if n >= 1 else None
        mde_con_are = (
            efecto_minimo_detectable(n, eficiencia_relativa=ARE_WILCOXON_MINIMA)
            if n >= 1
            else None
        )
        celdas = [
            etiqueta,
            str(n),
            _fmt_p_opcional(wilcoxon.p if wilcoxon else None),
            _fmt_p_opcional(wilcoxon.p_unilateral if wilcoxon else None),
            _fmt_num(tamano_efecto_dz(manual, automatizado)),
            _fmt_num(mde_sin_ajuste),
            _fmt_num(mde_con_are),
        ]
        lineas.append("| " + " | ".join(celdas) + " |")
    return lineas


def _tabla_sensibilidad(pares: List[tuple[float, float]]) -> List[str]:
    """Tabla de escenarios que descuentan segundos fijos al tiempo manual."""
    lineas = [
        "| Descuento al manual (s) | Media manual ajustada (s) "
        "| Reducción de la media (%) | p bilateral | p unilateral | r |",
        "|---|---|---|---|---|---|",
    ]
    manual = [m for m, _ in pares]
    automatizado = [a for _, a in pares]
    for descuento in _DESCUENTOS_SENSIBILIDAD_S:
        if len(pares) < _MIN_PARES_WILCOXON:
            celdas = [str(descuento), *([_NO_APLICABLE] * 5)]
        else:
            try:
                escenario = escenario_sensibilidad(manual, automatizado, descuento)
            except ValueError:
                celdas = [str(descuento), *([_NO_APLICABLE] * 5)]
            else:
                celdas = [
                    str(descuento),
                    _fmt_num(escenario.media_manual_ajustada),
                    _fmt_pct(escenario.reduccion_relativa_media),
                    _fmt_p(escenario.wilcoxon.p),
                    _fmt_p(escenario.wilcoxon.p_unilateral),
                    f"{escenario.wilcoxon.r:.4f}",
                ]
        lineas.append("| " + " | ".join(celdas) + " |")
    return lineas


def _subseccion_descriptivos(ambitos: _Ambitos) -> List[str]:
    """Subsección "Descriptivos global y por canal" (c-134, D4)."""
    return [
        "",
        "### Descriptivos global y por canal",
        "",
        "Desvío estándar con la convención muestral (divisor n − 1). La reducción relativa es",
        "1 − media(automatizado) / media(manual) (y su análoga con la mediana). \"No más",
        "rápidos\" cuenta los pares con `automatizado >= manual`.",
        "",
        *_tabla_descriptivos(ambitos),
    ]


def _subseccion_contraste(ambitos: _Ambitos) -> List[str]:
    """Subsección "Contraste direccional y tamaño del efecto" (c-134, D4)."""
    return [
        "",
        "### Contraste direccional y tamaño del efecto estandarizado",
        "",
        "El p bilateral corresponde a la convención W = min(T+, T−); el p unilateral contrasta",
        "H1: manual > automatizado (`alternative=\"greater\"` sobre manual − automatizado).",
        "d_z = media(d) / desvío(d) con d = manual − automatizado (desvío muestral).",
        "El efecto mínimo detectable (MDE, en escala d_z) usa la aproximación normal",
        "(z_(1−alfa/2) + z_potencia) / raíz(n · ARE) con alfa = 0.05 (bilateral),",
        f"potencia = 0.80 y ARE = 1 (sin ajuste) o ARE = {ARE_WILCOXON_MINIMA} "
        "(cota inferior de la eficiencia de la prueba de rangos frente a la t pareada).",
        "",
        *_tabla_contraste(ambitos),
    ]


def _subseccion_sensibilidad(
    pares: List[tuple[float, float]],
    manual: List[float],
) -> List[str]:
    """Subsección de sensibilidad del redondeo manual y granularidad (c-134, D4)."""
    total = len(manual)
    granularidad = granularidad_manual(manual)
    return [
        "",
        "### Escenarios de sensibilidad del redondeo manual",
        "",
        "Se descuenta una cantidad fija de segundos a cada `tiempo_manual_s` y se recalcula el",
        "contraste de Wilcoxon sobre los pares ajustados (conjunto global).",
        "",
        *_tabla_sensibilidad(pares),
        "",
        f"- Granularidad de `tiempo_manual_s`: {granularidad[5]} / {total} valores "
        f"múltiplos de 5 s; {granularidad[10]} / {total} múltiplos de 10 s.",
    ]


def _seccion_tiempos(
    corpus: List[CasoEvaluacion],
    corpus_hash: Optional[str] = None,
) -> List[str]:
    """
    Construye la sección "Tiempos" aditiva del reporte (c-99, D7).

    Incluye normalidad (Shapiro-Wilk), prueba de Wilcoxon global, divulgación
    del redondeo y de la reducción conservadora, y desglose por canal.
    """
    pares, excluidos = _pares_tiempos(corpus)
    manual = [m for m, _ in pares]
    automatizado = [a for _, a in pares]
    diferencias = [m - a for m, a in pares]

    lineas: List[str] = [
        "## Tiempos",
        "",
        "Análisis sobre los pares (tiempo_manual_s, tiempo_automatizado_s) del corpus cargado.",
        f"Pares válidos: {len(pares)}; excluidos por tiempo nulo: {excluidos}.",
        "",
        "### Normalidad (Shapiro-Wilk)",
        "",
        "| Conjunto | n | W | p |",
        "|---|---|---|---|",
    ]
    series = (
        ("Manual", manual),
        ("Automatizado", automatizado),
        ("Diferencias", diferencias),
    )
    for etiqueta, serie in series:
        resultado = shapiro_normalidad(serie)
        if resultado.aplicable:
            lineas.append(
                f"| {etiqueta} | {resultado.n} | {resultado.w:.4f} | {_fmt_p(resultado.p)} |"
            )
        else:
            lineas.append(
                f"| {etiqueta} | {resultado.n} | {_NO_APLICABLE} | {_NO_APLICABLE} |"
            )

    lineas += [
        "",
        "### Prueba de Wilcoxon (rangos con signo)",
        "",
        "Convención: W = min(T+, T−) (dos colas); tamaño del efecto rank-biserial "
        "r = (T+ − T−) / (n(n+1)/2).",
        "",
        "| n | W | T+ | T− | p | r |",
        "|---|---|---|---|---|---|",
        _fila_wilcoxon(len(pares), _wilcoxon_o_no_aplicable(pares)),
    ]

    reduccion = reduccion_tiempos(manual, automatizado)
    lineas += [
        "",
        "### Reducción de tiempos",
        "",
        "`tiempo_manual_s` se midió en vivo con redondeo al alza (sesgo sistemático), por lo",
        "que su valor real no es mayor que el reportado. Se reporta la reducción sobre los",
        "valores reportados y una cota conservadora que descuenta 1 s al manual por caso.",
        "",
        "| Métrica | Reportada (s) | Conservadora (s) |",
        "|---|---|---|",
        f"| Reducción media | {reduccion.reduccion_media_reportada:.2f} "
        f"| {reduccion.reduccion_media_conservadora:.2f} |",
        f"| Reducción mediana | {reduccion.reduccion_mediana_reportada:.2f} "
        f"| {reduccion.reduccion_mediana_conservadora:.2f} |",
        "",
        "- Pares en que el flujo automatizado no fue más rápido "
        f"(invertidos/empatados): {reduccion.pares_no_mas_rapidos}.",
        f"- Casos excluidos por tiempo nulo: {excluidos}.",
    ]

    lineas += [
        "",
        "### Desglose por canal",
        "",
        "Segmentación por el valor crudo de `canal_origen` del corpus.",
        "",
        "| Canal | Pares válidos | W | T+ | T− | p | r |",
        "|---|---|---|---|---|---|---|",
    ]
    # Orden canónico estable: conteo descendente y desempate alfabético (D4).
    for canal, pares_canal in _pares_por_canal(corpus):
        resultado_canal = _wilcoxon_o_no_aplicable(pares_canal)
        lineas.append(_fila_wilcoxon(len(pares_canal), resultado_canal, canal=canal))

    ambitos = _ambitos_tiempos(corpus, pares)
    lineas += _subseccion_descriptivos(ambitos)
    lineas += _subseccion_contraste(ambitos)
    lineas += _subseccion_sensibilidad(pares, manual)

    if corpus_hash is not None:
        lineas += ["", f"- **SHA-256 del corpus:** `{corpus_hash}`"]

    return lineas


# ---------------------------------------------------------------------------
# Secciones aditivas de c-131 (D7): exactitud por etapa, por canal y calibración
# ---------------------------------------------------------------------------
def _fmt_intervalo(intervalo: Optional[tuple[float, float]]) -> str:
    """Intervalo `[inferior, superior]` (4 decimales) o "no aplicable"."""
    if intervalo is None:
        return _NO_APLICABLE
    return f"[{intervalo[0]:.4f}, {intervalo[1]:.4f}]"


def _celdas_exactitud(resumen: ResumenExactitud) -> List[str]:
    """Celdas de una fila de exactitud: estricta y laxa, cada una con su IC de Wilson."""
    return [
        str(resumen.aciertos_estrictos),
        _fmt_num(resumen.exactitud_estricta),
        _fmt_intervalo(resumen.ic_estricta),
        str(resumen.aciertos_laxos),
        _fmt_num(resumen.exactitud_laxa),
        _fmt_intervalo(resumen.ic_laxa),
    ]


_ENCABEZADO_EXACTITUD = (
    "| Casos | Aciertos (estrictos) | Exactitud (estricta) | IC Wilson 95% (estricto) "
    "| Aciertos (laxos) | Exactitud (laxa) | IC Wilson 95% (laxo) |"
)


def _etapa_normalizada(etapa: str) -> str:
    """Etapa del pipeline; una etapa desconocida se cuenta como `fallback`."""
    return etapa if etapa in ETAPAS_PIPELINE else "fallback"


def _seccion_exactitud_por_etapa(
    predicciones: List[Prediccion],
    reales: List[str],
    predichas: List[str],
    conjuntos_verdad: List[frozenset],
) -> List[str]:
    """
    Sección "Exactitud por etapa del pipeline" (c-131, D7).

    Exactitud estricta y laxa con IC de Wilson de cada etapa, en el orden
    `deterministic`, `gemini`, `fallback`. Una etapa sin casos se declara
    "no aplicable". Las filas suman los totales globales.
    """
    desglose = desglose_exactitud(
        [_etapa_normalizada(p.etapa) for p in predicciones],
        reales,
        predichas,
        conjuntos_verdad,
        orden=ETAPAS_PIPELINE,
    )
    lineas = [
        "",
        "## Exactitud por etapa del pipeline",
        "",
        "Segmentación por la etapa que resolvió cada caso. Exactitud estricta (sector",
        "principal igual al asignado) y laxa (sector principal dentro del conjunto de",
        "verdad), cada una con su IC de Wilson al 95%. Una etapa sin casos se declara",
        f"\"{_NO_APLICABLE}\".",
        "",
        "| Etapa " + _ENCABEZADO_EXACTITUD,
        "|---|---|---|---|---|---|---|---|",
    ]
    for etapa, resumen in desglose.items():
        celdas = [etapa, str(resumen.casos), *_celdas_exactitud(resumen)]
        lineas.append("| " + " | ".join(celdas) + " |")
    return lineas


# Umbrales de la calibración (c-131): el gate de revisión humana y el tramo de alta confianza.
_UMBRAL_GATE = 0.70
_UMBRAL_ALTA_CONFIANZA = 0.90

# Ámbito: nombre de la fila y posiciones de las predicciones que abarca.
_AmbitoCalibracion = tuple[str, List[int]]


def _etiqueta_banda(inferior: float, superior: float, ultima: bool) -> str:
    """Rótulo de banda: `[inf, sup)`, o `[inf, sup]` si es la última (cerrada)."""
    cierre = "]" if ultima else ")"
    return f"[{inferior:.2f}, {superior:.2f}{cierre}"


def _exactitud_o_na(aciertos: int, total: int) -> str:
    """Exactitud con 4 decimales, o "no aplicable" si no hay casos."""
    return _fmt_num(aciertos / total if total else None)


def _ambitos_calibracion(etapas: List[str]) -> List[_AmbitoCalibracion]:
    """Ámbitos de la calibración: "Global" y luego cada etapa en su orden canónico."""
    ambitos: List[_AmbitoCalibracion] = [("Global", list(range(len(etapas))))]
    for etapa in ETAPAS_PIPELINE:
        ambitos.append((etapa, [i for i, valor in enumerate(etapas) if valor == etapa]))
    return ambitos


def _tabla_bandas_globales(
    confianzas: List[float], reales: List[str], predichas: List[str]
) -> List[str]:
    """Tabla de bandas global (reproduce la Tabla 7.5 de la tesis)."""
    lineas = [
        "",
        "### Bandas de confianza (global)",
        "",
        "| Banda | Casos | Aciertos | Exactitud |",
        "|---|---|---|---|",
    ]
    ultima = len(BANDAS_CALIBRACION_DEFECTO) - 1
    for indice, banda in enumerate(calibracion_por_bandas(confianzas, reales, predichas)):
        etiqueta = _etiqueta_banda(banda.limite_inferior, banda.limite_superior, indice == ultima)
        lineas.append(
            f"| {etiqueta} | {banda.total} | {banda.aciertos} "
            f"| {_exactitud_o_na(banda.aciertos, banda.total)} |"
        )
    return lineas


def _tabla_contingencia(
    ambitos: List[_AmbitoCalibracion],
    confianzas: List[float],
    reales: List[str],
    predichas: List[str],
) -> List[str]:
    """Contingencia en el umbral 0,70, global y por etapa."""
    lineas = [
        "",
        "### Contingencia en el umbral 0,70",
        "",
        "Confianza `>= 0,70` frente a `< 0,70`, global y por etapa.",
        "",
        "| Ámbito | Casos >= 0,70 | Aciertos >= 0,70 | Exactitud >= 0,70 "
        "| Casos < 0,70 | Aciertos < 0,70 | Exactitud < 0,70 |",
        "|---|---|---|---|---|---|---|",
    ]
    for nombre, indices in ambitos:
        c = contingencia_confianza(
            [confianzas[i] for i in indices],
            [reales[i] for i in indices],
            [predichas[i] for i in indices],
            umbral=_UMBRAL_GATE,
        )
        lineas.append(
            f"| {nombre} | {c.alta_total} | {c.alta_aciertos} "
            f"| {_exactitud_o_na(c.alta_aciertos, c.alta_total)} "
            f"| {c.baja_total} | {c.baja_aciertos} "
            f"| {_exactitud_o_na(c.baja_aciertos, c.baja_total)} |"
        )
    return lineas


def _tabla_tramo_alta_confianza(
    ambitos: List[_AmbitoCalibracion],
    confianzas: List[float],
    reales: List[str],
    predichas: List[str],
) -> List[str]:
    """Casos y errores con confianza `>= 0,90`, global y por etapa."""
    lineas = [
        "",
        "### Tramo de confianza >= 0,90",
        "",
        "Casos y errores (predicción estricta distinta de la asignada) con confianza `>= 0,90`.",
        "",
        "| Ámbito | Casos | Errores |",
        "|---|---|---|",
    ]
    for nombre, indices in ambitos:
        en_tramo = [i for i in indices if confianzas[i] >= _UMBRAL_ALTA_CONFIANZA]
        errores = sum(1 for i in en_tramo if reales[i] != predichas[i])
        lineas.append(f"| {nombre} | {len(en_tramo)} | {errores} |")
    return lineas


def _tabla_bandas_por_etapa(
    confianzas: List[float], reales: List[str], predichas: List[str], etapas: List[str]
) -> List[str]:
    """Bandas de confianza de cada etapa, con IC de Wilson de las no vacías."""
    lineas = [
        "",
        "### Bandas de confianza por etapa",
        "",
        "Exactitud por banda dentro de cada etapa, con IC de Wilson al 95%. La suma de las",
        "etapas reproduce la tabla global. Una banda sin casos se declara "
        f"\"{_NO_APLICABLE}\".",
        "",
        "| Etapa | Banda | Casos | Aciertos | Exactitud | IC Wilson 95% |",
        "|---|---|---|---|---|---|",
    ]
    ultima = len(BANDAS_CALIBRACION_DEFECTO) - 1
    por_etapa = calibracion_por_etapa(confianzas, reales, predichas, etapas)
    for etapa in ETAPAS_PIPELINE:
        for indice, banda in enumerate(por_etapa[etapa]):
            etiqueta = _etiqueta_banda(
                banda.limite_inferior, banda.limite_superior, indice == ultima
            )
            intervalo = intervalo_wilson(banda.aciertos, banda.total) if banda.total else None
            lineas.append(
                f"| {etapa} | {etiqueta} | {banda.total} | {banda.aciertos} "
                f"| {_exactitud_o_na(banda.aciertos, banda.total)} | {_fmt_intervalo(intervalo)} |"
            )
    return lineas


def _tabla_distribucion_por_etapa(
    ambitos: List[_AmbitoCalibracion],
    confianzas: List[float],
    reales: List[str],
    predichas: List[str],
) -> List[str]:
    """Valores distintos de confianza de cada etapa, con casos y aciertos."""
    lineas = [
        "",
        "### Distribución de valores de confianza por etapa",
        "",
        "Valores distintos de confianza observados (redondeados a 4 decimales), en orden",
        "ascendente, con sus casos y aciertos estrictos.",
        "",
        "| Etapa | Confianza | Casos | Aciertos |",
        "|---|---|---|---|",
    ]
    for etapa, indices in ambitos[1:]:
        valores = distribucion_confianza(
            [confianzas[i] for i in indices],
            [reales[i] for i in indices],
            [predichas[i] for i in indices],
        )
        if not valores:
            lineas.append(f"| {etapa} | {_NO_APLICABLE} | 0 | 0 |")
        for valor in valores:
            lineas.append(f"| {etapa} | {valor.valor:.4f} | {valor.casos} | {valor.aciertos} |")
    return lineas


def _seccion_calibracion(
    predicciones: List[Prediccion],
    reales: List[str],
    predichas: List[str],
) -> List[str]:
    """
    Sección "Calibración de la confianza" (c-131, D7).

    Reproduce la tabla de bandas global (Tabla 7.5), la contingencia en 0,70 y el
    tramo `>= 0,90` en forma global y por etapa, las bandas por etapa con IC de
    Wilson y la distribución de valores de confianza por etapa. Las etapas y
    bandas vacías se declaran "no aplicable". Las confianzas de la etapa
    determinística y de Gemini son magnitudes de naturaleza distinta, por lo que
    comparar bandas agregadas compara etapas.
    """
    confianzas = [p.confianza for p in predicciones]
    etapas = [_etapa_normalizada(p.etapa) for p in predicciones]
    ambitos = _ambitos_calibracion(etapas)

    lineas = [
        "",
        "## Calibración de la confianza",
        "",
        "Relación entre la confianza devuelta por caso y la exactitud estricta. La etapa",
        "determinística y la etapa Gemini emiten magnitudes de confianza distintas: una",
        "banda agregada compara etapas, no mide la calibración del modelo. Se reporta en",
        "forma global y desagregada por etapa.",
    ]
    lineas += _tabla_bandas_globales(confianzas, reales, predichas)
    lineas += _tabla_contingencia(ambitos, confianzas, reales, predichas)
    lineas += _tabla_tramo_alta_confianza(ambitos, confianzas, reales, predichas)
    lineas += _tabla_bandas_por_etapa(confianzas, reales, predichas, etapas)
    lineas += _tabla_distribucion_por_etapa(ambitos, confianzas, reales, predichas)
    return lineas


def _lineas_procedencia(procedencia: Optional[Dict[str, Any]]) -> List[str]:
    """Línea de procedencia de las predicciones (vacía si no hay metadata)."""
    if not procedencia:
        return []
    version = procedencia.get("classifier_version", _NO_APLICABLE)
    fecha = procedencia.get("generated_at", _NO_APLICABLE)
    return [
        "",
        "**Procedencia de las predicciones:** "
        f"`classifier_version` = `{version}`; `generated_at` = `{fecha}`.",
    ]


def _validar_alineacion(predicciones: List[Prediccion], corpus: List[CasoEvaluacion]) -> None:
    """
    Verifica que `predicciones[i]` corresponda a `corpus[i]` (c-131, D7).

    El desglose por canal asocia cada predicción a su caso por posición; si los
    identificadores no coinciden, el desglose saldría desalineado, así que se
    falla con un error que nombra la posición y ambos identificadores.

    Raises:
        ValueError: Si las longitudes difieren o algún `caso_id` no coincide.
    """
    if len(predicciones) != len(corpus):
        raise ValueError(
            f"Predicciones desalineadas con el corpus: {len(predicciones)} "
            f"predicciones frente a {len(corpus)} casos."
        )
    for posicion, (prediccion, caso) in enumerate(zip(predicciones, corpus)):
        if prediccion.caso_id != caso.id:
            raise ValueError(
                f"Predicciones desalineadas con el corpus en la posición {posicion}: "
                f"caso_id de la predicción '{prediccion.caso_id}' frente a id del caso "
                f"'{caso.id}'."
            )


def _seccion_exactitud_por_canal(
    predicciones: List[Prediccion],
    corpus: List[CasoEvaluacion],
    reales: List[str],
    predichas: List[str],
    conjuntos_verdad: List[frozenset],
) -> List[str]:
    """
    Sección "Exactitud por canal de origen" (c-131, D7).

    Casos, composición por etapa del pipeline y exactitud estricta y laxa con IC
    de Wilson por valor de `canal_origen`, con el mismo orden que el desglose de
    tiempos (conteo descendente y desempate alfabético; canal nulo = "sin canal").
    """
    conteo: Dict[Optional[str], int] = {}
    for caso in corpus:
        conteo[caso.canal_origen] = conteo.get(caso.canal_origen, 0) + 1
    orden_crudo = sorted(conteo, key=lambda canal: (-conteo[canal], str(canal)))
    etiqueta = {canal: (_NO_CANAL if canal is None else str(canal)) for canal in orden_crudo}

    claves = [etiqueta[caso.canal_origen] for caso in corpus]
    desglose = desglose_exactitud(
        claves,
        reales,
        predichas,
        conjuntos_verdad,
        orden=[etiqueta[canal] for canal in orden_crudo],
    )
    composicion: Dict[str, Dict[str, int]] = {
        clave: {etapa: 0 for etapa in ETAPAS_PIPELINE} for clave in desglose
    }
    for clave, prediccion in zip(claves, predicciones):
        composicion[clave][_etapa_normalizada(prediccion.etapa)] += 1

    lineas = [
        "",
        "## Exactitud por canal de origen",
        "",
        "Segmentación por el valor crudo de `canal_origen` del corpus, con el mismo orden",
        "que el desglose por canal de tiempos. La composición sectorial y la proporción de",
        "casos multietiqueta difieren entre canales: la comparación no aísla el efecto del canal.",
        "",
        "| Canal | Casos | Deterministic | Gemini | Fallback | Aciertos (estrictos) "
        "| Exactitud (estricta) | IC Wilson 95% (estricto) | Aciertos (laxos) "
        "| Exactitud (laxa) | IC Wilson 95% (laxo) |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for canal, resumen in desglose.items():
        celdas = [
            canal,
            str(resumen.casos),
            *(str(composicion[canal][etapa]) for etapa in ETAPAS_PIPELINE),
            *_celdas_exactitud(resumen),
        ]
        lineas.append("| " + " | ".join(celdas) + " |")
    return lineas


def generar_reporte(
    predicciones: List[Prediccion],
    corpus: List[CasoEvaluacion],
    output_path: pathlib.Path = REPORT_PATH,
    corpus_hash: Optional[str] = None,
    procedencia: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Genera el reporte de métricas multietiqueta en Markdown.

    Reutiliza las funciones puras de evaluation.metrics (design D5).

    Args:
        predicciones: Lista de predicciones del runner.
        corpus: Lista de casos originales del corpus (mismo orden).
        output_path: Ruta donde escribir el reporte (default: evaluation/report.md).
        corpus_hash: SHA-256 opcional del corpus. Si se pasa, se emite dentro de
            la sección "Tiempos"; si es None, la línea se omite (D3).
        procedencia: `cache_meta` de las predicciones usadas (c-131, D7). Si trae
            `classifier_version` y `generated_at`, el reporte declara la versión
            y la fecha de generación; si es None o está vacío, la línea se omite.

    Returns:
        Contenido del reporte como string.
    """
    _validar_alineacion(predicciones, corpus)

    reales = [p.sector_asignado for p in predicciones]
    # c-71: un sector ausente (fallback sin estimacion) cuenta como error y se
    # excluye de la matriz de confusion (que solo admite los 5 canonicos).
    predichas = [(p.sector_predicho or "") for p in predicciones]
    adicionales_predichos = [p.sectores_adicionales for p in predicciones]

    conjuntos_verdad = [caso.conjunto_verdad for caso in corpus]
    conjuntos_predichos = [
        frozenset(
            etiqueta
            for etiqueta in (p.sector_predicho, *p.sectores_adicionales)
            if etiqueta in CLASES
        )
        for p in predicciones
    ]

    pares_canonicos = [
        (real, predicho)
        for real, predicho in zip(reales, predichas)
        if predicho in CLASES
    ]
    mc = matriz_confusion(
        [real for real, _ in pares_canonicos],
        [predicho for _, predicho in pares_canonicos],
    )
    exactitud = exactitud_global(reales, predichos=predichas)
    aciertos = aciertos_estrictos(reales, predichas)
    lower_ic, upper_ic = intervalo_wilson(aciertos, len(reales))

    aciertos_pert = aciertos_pertenencia(reales, predichas, adicionales_predichos)
    lower_pert, upper_pert = intervalo_wilson(aciertos_pert, len(reales))
    exactitud_pert = aciertos_pert / len(reales) if reales else 0.0

    aciertos_lax = aciertos_laxos(predichas, conjuntos_verdad)
    lower_lax, upper_lax = intervalo_wilson(aciertos_lax, len(reales))
    exactitud_lax = aciertos_lax / len(reales) if reales else 0.0

    subset = exactitud_subconjunto(conjuntos_verdad, conjuntos_predichos)
    hamming = perdida_hamming(conjuntos_verdad, conjuntos_predichos)
    micro_f1 = f1_micro(conjuntos_verdad, conjuntos_predichos)
    jaccard = jaccard_promedio(conjuntos_verdad, conjuntos_predichos)

    precisiones = precision_por_clase(mc)
    sensibilidades = sensibilidad_por_clase(mc)
    f1s = f1_por_clase(mc)
    f1_m = f1_macro(f1s)
    soportes = soporte_por_clase(mc)

    etapas: Dict[str, int] = {"deterministic": 0, "gemini": 0, "fallback": 0}
    for pred in predicciones:
        etapa = pred.etapa if pred.etapa in etapas else "fallback"
        etapas[etapa] += 1

    lineas = [
        "# Reporte de Evaluación del Clasificador (multietiqueta)",
        "",
        f"**Total de casos evaluados:** {len(predicciones)}",
        *_lineas_procedencia(procedencia),
        "",
        "## Etapas del pipeline",
        "",
        "| Etapa | Casos |",
        "|-------|-------|",
        f"| Deterministic | {etapas['deterministic']} |",
        f"| Gemini | {etapas['gemini']} |",
        f"| Fallback | {etapas['fallback']} |",
        "",
        "## Exactitud",
        "",
        "Definiciones (design D5): igualdad estricta del sector principal y",
        "pertenencia del sector asignado al conjunto predicho.",
        "",
        f"- **Exactitud (estricta):** {exactitud:.4f} ({exactitud * 100:.1f}%)",
        f"- **Aciertos (estrictos):** {aciertos} / {len(reales)}",
        f"- **IC Wilson 95% (estricto):** [{lower_ic:.4f}, {upper_ic:.4f}]",
        f"- **Exactitud (pertenencia):** {exactitud_pert:.4f} ({exactitud_pert * 100:.1f}%)",
        f"- **Aciertos (pertenencia):** {aciertos_pert} / {len(reales)}",
        f"- **IC Wilson 95% (pertenencia):** [{lower_pert:.4f}, {upper_pert:.4f}]",
        "",
        "Exactitud laxa (c-131, D5): el sector predicho principal pertenece al conjunto de",
        "verdad del caso (`sector_asignado` más `sectores_adicionales` del corpus). No es la",
        "pertenencia, que mide el sector asignado dentro del conjunto predicho.",
        "",
        f"- **Exactitud (laxa):** {exactitud_lax:.4f} ({exactitud_lax * 100:.1f}%)",
        f"- **Aciertos (laxos):** {aciertos_lax} / {len(reales)}",
        f"- **IC Wilson 95% (laxo):** [{lower_lax:.4f}, {upper_lax:.4f}]",
        "",
        "## Matriz de Confusión (primaria 5x5)",
        "",
        "Filas = sector asignado | Columnas = sector predicho principal",
        "",
    ]

    header = "| Asignado \\ Predicho | " + " | ".join(CLASES) + " |"
    separator = "|" + "---|" * (len(CLASES) + 1)
    lineas.append(header)
    lineas.append(separator)
    for sector_asignado in CLASES:
        fila = f"| **{sector_asignado}** | "
        celdas = " | ".join(str(mc[sector_asignado][p]) for p in CLASES)
        lineas.append(fila + celdas + " |")

    lineas += [
        "",
        "## Métricas por sector (one-vs-rest)",
        "",
        "| Sector | Precisión | Sensibilidad | F1 | Soporte |",
        "|--------|-----------|--------------|-----|---------|",
    ]
    for sector in CLASES:
        lineas.append(
            f"| {sector} | {precisiones[sector]:.4f} | {sensibilidades[sector]:.4f} "
            f"| {f1s[sector]:.4f} | {soportes[sector]} |"
        )

    lineas += [
        "",
        "## Métricas de conjunto",
        "",
        f"- **Subset accuracy:** {subset:.4f}",
        f"- **Hamming loss:** {hamming:.4f}",
        f"- **Micro-F1:** {micro_f1:.4f}",
        f"- **Macro-F1:** {f1_m:.4f}",
        f"- **Jaccard (IoU) promedio:** {jaccard:.4f}",
    ]

    lineas += _seccion_exactitud_por_etapa(predicciones, reales, predichas, conjuntos_verdad)
    lineas += _seccion_exactitud_por_canal(
        predicciones, corpus, reales, predichas, conjuntos_verdad
    )
    lineas += _seccion_calibracion(predicciones, reales, predichas)
    lineas += [""]

    lineas += _seccion_tiempos(corpus, corpus_hash)

    lineas += [
        "",
        "---",
        "_Generado automáticamente por `evaluation/run_evaluation.py`_",
    ]

    contenido = "\n".join(lineas)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(contenido, encoding="utf-8")
    return contenido


# ---------------------------------------------------------------------------
# Regeneración de la sección "Tiempos" sin predicciones (c-134, D5)
# ---------------------------------------------------------------------------
_ENCABEZADO_TIEMPOS = "## Tiempos"
_PIE_REPORTE = "---"


def reemplazar_seccion_tiempos(reporte: str, seccion: str) -> str:
    """
    Reemplaza en `reporte` solo el bloque "## Tiempos" por `seccion`.

    Función pura. El bloque va desde la línea `## Tiempos` hasta antes del
    siguiente encabezado que empiece con `## ` o de la línea `---` del pie;
    las líneas en blanco que lo separan de lo que sigue se conservan. Si el
    bloque no existe, la sección se inserta antes del pie (o al final, si no
    hay pie). El resto del reporte queda idéntico byte a byte.

    Args:
        reporte: Contenido completo del reporte (con saltos de línea LF).
        seccion: Bloque nuevo, sin salto de línea final, que empieza en
            `## Tiempos`.

    Returns:
        Reporte con el bloque de tiempos reemplazado o insertado.
    """
    lineas = reporte.split("\n")
    nueva = seccion.split("\n")

    inicio = next(
        (i for i, linea in enumerate(lineas) if linea == _ENCABEZADO_TIEMPOS), None
    )
    if inicio is None:
        pie = next(
            (i for i in range(len(lineas) - 1, -1, -1) if lineas[i] == _PIE_REPORTE),
            None,
        )
        if pie is None:
            return "\n".join([*lineas, "", *nueva])
        previas = lineas[:pie]
        while previas and previas[-1] == "":
            previas.pop()
        return "\n".join([*previas, "", *nueva, "", *lineas[pie:]])

    fin = next(
        (
            j
            for j in range(inicio + 1, len(lineas))
            if lineas[j].startswith("## ") or lineas[j] == _PIE_REPORTE
        ),
        len(lineas),
    )
    # Las líneas en blanco finales del bloque pertenecen al separador siguiente.
    while fin > inicio + 1 and lineas[fin - 1] == "":
        fin -= 1
    return "\n".join([*lineas[:inicio], *nueva, *lineas[fin:]])


# ---------------------------------------------------------------------------
# Helpers de cache (D1, D2, D3)
# ---------------------------------------------------------------------------
def _compute_corpus_hash(corpus_path: pathlib.Path) -> str:
    """
    Calcula el hash SHA-256 del contenido del archivo de corpus.

    Los fines de línea se normalizan a LF antes de hashear (c-134, D6): una copia
    con CRLF (por ejemplo, un checkout de Windows con `core.autocrlf=true`) y
    una con LF producen la misma huella, igual a la del blob versionado. Una
    diferencia de contenido distinta del fin de línea sí cambia la huella.

    Args:
        corpus_path: Ruta al archivo de corpus JSON.

    Returns:
        Hex digest SHA-256 (64 caracteres).
    """
    contenido = corpus_path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(contenido).hexdigest()


def _get_classifier_version(classifier: Any) -> str:
    """
    Obtiene la clave de version del clasificador.

    Devuelve `classifier.CACHE_VERSION` si el atributo existe;
    en caso contrario, devuelve `type(classifier).__name__`.

    Args:
        classifier: Instancia del clasificador.

    Returns:
        String identificador de version del clasificador.
    """
    return getattr(classifier, "CACHE_VERSION", type(classifier).__name__)


def _is_cache_valid(
    predicciones_path: pathlib.Path,
    corpus_hash: str,
    corpus_count: int,
    classifier_version: str,
) -> bool:
    """
    Verifica si el archivo de predicciones existente es un cache valido.

    Un cache es valido si y solo si:
    - El archivo existe.
    - Contiene el campo `cache_meta` de nivel superior.
    - `cache_meta.corpus_hash` coincide con `corpus_hash`.
    - `cache_meta.corpus_count` coincide con `corpus_count`.
    - `cache_meta.classifier_version` coincide con `classifier_version`.

    Args:
        predicciones_path: Ruta al archivo predicciones.json.
        corpus_hash: Hash SHA-256 del archivo de corpus actual.
        corpus_count: Cantidad de casos en el corpus actual.
        classifier_version: Clave de version del clasificador actual.

    Returns:
        True si el cache es valido, False en cualquier otro caso.
    """
    if not predicciones_path.exists():
        return False
    try:
        data = json.loads(predicciones_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    if not isinstance(data, dict) or "cache_meta" not in data:
        return False

    meta = data["cache_meta"]
    return (
        meta.get("corpus_hash") == corpus_hash
        and meta.get("corpus_count") == corpus_count
        and meta.get("classifier_version") == classifier_version
    )


# ---------------------------------------------------------------------------
# Persistencia de predicciones (artefacto intermedio)
# ---------------------------------------------------------------------------
def guardar_predicciones(
    predicciones: List[Prediccion],
    output_path: pathlib.Path = PREDICCIONES_PATH,
    cache_meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Persiste las predicciones a JSON para no re-invocar Gemini al regenerar el reporte.

    El archivo escrito usa el nuevo formato con `cache_meta` de nivel superior:

        {
            "cache_meta": { ... },
            "predictions": [ ... ]
        }

    Si `cache_meta` es None, se escribe el campo como objeto vacio ({}). Los callers
    que generan el cache completo deben pasar el dict de metadata; esta firma permite
    compatibilidad con usos directos que no necesitan cache.

    Args:
        predicciones: Lista de predicciones a persistir.
        output_path: Ruta del JSON (default: evaluation/predicciones.json).
        cache_meta: Metadata de cache a incluir en el archivo. Si es None, se usa {}.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "cache_meta": cache_meta if cache_meta is not None else {},
        "predictions": [asdict(p) for p in predicciones],
    }
    output_path.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cargar_cache_meta(input_path: pathlib.Path) -> Optional[Dict[str, Any]]:
    """
    Lee el `cache_meta` de un archivo de predicciones (c-131, D7).

    Returns:
        El diccionario `cache_meta`, o None si el archivo no existe, no es JSON
        válido, no tiene `cache_meta` de nivel superior o este no es un objeto.
    """
    try:
        data = json.loads(pathlib.Path(input_path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    meta = data.get("cache_meta")
    return meta if isinstance(meta, dict) else None


def cargar_predicciones(input_path: pathlib.Path) -> List[Prediccion]:
    """
    Carga predicciones previamente persistidas desde JSON.

    Compatible con ambos formatos:
    - Nuevo formato: `{"cache_meta": {...}, "predictions": [...]}` — lee desde `predictions`.
    - Formato antiguo (arreglo plano): lee directamente el arreglo.

    Args:
        input_path: Ruta del JSON con predicciones.

    Returns:
        Lista de Prediccion.
    """
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "predictions" in data:
        datos = data["predictions"]
    else:
        datos = data
    return [Prediccion(**d) for d in datos]


# ---------------------------------------------------------------------------
# main_con_corpus_real — punto de entrada para la corrida real (testeable)
# ---------------------------------------------------------------------------
def _ensure_backend_on_path() -> None:
    """Agrega App/Backend/ a sys.path para importar los clasificadores reales."""
    backend_path = str(_REPO_ROOT / "App" / "Backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def _version_clasificador_real() -> str:
    """Devuelve el CACHE_VERSION del HybridClassifier real sin construirlo (W-3).

    Construir el clasificador real exige credenciales (GeminiClassifier ->
    get_settings). Un cache hit no debe pagar ese costo: la version vive en
    ``app.constants`` (modulo liviano) y se lee sin importar ``app.classifiers``,
    que arrastra ``app.core.database`` -> ``get_settings()``.
    """
    try:
        _ensure_backend_on_path()
        from app.constants import HYBRID_CACHE_VERSION  # type: ignore[import]

        return HYBRID_CACHE_VERSION
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar HYBRID_CACHE_VERSION. "
            "Asegurate de correr con PYTHONPATH que incluya App/Backend/. "
            "Ver evaluation/README.md para instrucciones de setup."
        ) from exc


def _resolver_clasificador_real() -> ClasificadorProtocol:
    """Importa y construye el HybridClassifier real (camino pago).

    Se aísla en una funcion para que los tests puedan sustituirla sin tocar
    el backend ni disparar una llamada paga.
    """
    try:
        _ensure_backend_on_path()
        from app.classifiers.hybrid import HybridClassifier  # type: ignore[import]

        return HybridClassifier()
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar HybridClassifier. "
            "Asegurate de correr con PYTHONPATH que incluya App/Backend/. "
            "Ver evaluation/README.md para instrucciones de setup."
        ) from exc


async def main_con_corpus_real(
    corpus_path: pathlib.Path = CORPUS_REAL_PATH,
    classifier: Optional[ClasificadorProtocol] = None,
    report_path: pathlib.Path = REPORT_PATH,
    predicciones_path: pathlib.Path = PREDICCIONES_PATH,
    force: bool = False,
    confirm_paid: bool = False,
    estimated_cost_per_call: Optional[float] = None,
) -> None:
    """
    Carga el corpus real, evalua y genera el reporte.

    Si el corpus no existe en `corpus_path`, lanza FileNotFoundError con
    mensaje claro indicando donde colocar el corpus (sin inventar datos).

    Logica de cache (D4):
    - Si `force=False` y `predicciones_path` contiene un cache valido (mismo hash
      SHA-256 del corpus, mismo corpus_count y misma version del clasificador),
      las predicciones se cargan del archivo y se omite la invocacion al clasificador.
    - En cualquier otro caso (cache ausente, invalido o `force=True`), se ejecuta
      `evaluar_corpus` y se persiste el resultado con metadata de cache.

    Args:
        corpus_path: Ruta al corpus JSON (default: data/corpus_evaluacion_pseudonimizado.json).
        classifier: Clasificador a inyectar (None = usar HybridClassifier real).
        report_path: Donde escribir el reporte.
        predicciones_path: Donde persistir las predicciones.
        force: Si True, bypasea el cache y re-ejecuta la clasificacion completa.
        confirm_paid: Si True, autoriza la corrida que invoca al clasificador real
            cuando no hay cache valido. Un cache hit o un clasificador inyectado
            no requieren confirmacion.
        estimated_cost_per_call: Override del costo estimado por llamada (USD).
    """
    corpus_path = pathlib.Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"El corpus de evaluacion no esta en: {corpus_path}\n"
            f"Coloca el archivo 'corpus_evaluacion_pseudonimizado.json' en la carpeta 'data/' "
            f"antes de ejecutar la evaluacion. Ver evaluation/README.md para instrucciones."
        )

    corpus = cargar_corpus(corpus_path)

    corpus_hash = _compute_corpus_hash(corpus_path)
    corpus_count = len(corpus)
    usa_clasificador_real = classifier is None

    cache_hit = False
    if not force:
        # W-3: la version del clasificador real se lee sin construirlo, de modo
        # que un cache hit no exija credenciales ni invoque Gemini.
        classifier_version = (
            _version_clasificador_real()
            if classifier is None
            else _get_classifier_version(classifier)
        )
        cache_hit = _is_cache_valid(
            predicciones_path, corpus_hash, corpus_count, classifier_version
        )

    if cache_hit:
        predicciones = cargar_predicciones(predicciones_path)
        procedencia = cargar_cache_meta(predicciones_path)
        print(
            f"Cache valido encontrado. Predicciones cargadas desde: {predicciones_path}"
        )
    else:
        if usa_clasificador_real:
            # El gate de costo se evalua ANTES de construir el clasificador real.
            if not confirm_paid:
                raise PaidRunNotConfirmedError(
                    "Corrida paga sin confirmar: la evaluacion invocaria el "
                    "HybridClassifier real. Confirma explicitamente con "
                    "--confirm-paid o "
                    f"{CONFIRM_PAID_ENV_VAR}=1."
                )
            classifier = _resolver_clasificador_real()
            print(
                format_cost_estimation(corpus_count, estimated_cost_per_call)
            )
        classifier_version = _get_classifier_version(classifier)
        predicciones = await evaluar_corpus(corpus, classifier)
        cache_meta: Dict[str, Any] = {
            "corpus_hash": corpus_hash,
            "corpus_count": corpus_count,
            "classifier_version": classifier_version,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        guardar_predicciones(predicciones, predicciones_path, cache_meta=cache_meta)
        procedencia = cache_meta

    generar_reporte(
        predicciones, corpus, report_path, corpus_hash=corpus_hash, procedencia=procedencia
    )
    print(f"Evaluacion completa. Reporte escrito en: {report_path}")


def main_solo_tiempos(
    corpus_path: pathlib.Path = CORPUS_REAL_PATH,
    report_path: pathlib.Path = REPORT_PATH,
) -> None:
    """
    Regenera solo el bloque "## Tiempos" de un reporte existente (c-134, D5).

    No construye ni invoca el clasificador, no lee ni escribe el cache de
    predicciones y no exige la confirmación de corrida paga: la sección de
    tiempos depende únicamente del corpus. El resto del reporte se conserva
    byte a byte y el bloque resultante es idéntico al de la corrida completa
    sobre el mismo corpus.

    Args:
        corpus_path: Ruta al corpus JSON.
        report_path: Reporte existente a actualizar.

    Raises:
        FileNotFoundError: Si falta el corpus o si el reporte no existe (en ese
            caso no se crea un reporte parcial).
    """
    corpus_path = pathlib.Path(corpus_path)
    report_path = pathlib.Path(report_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"El corpus de evaluacion no esta en: {corpus_path}\n"
            f"Coloca el archivo 'corpus_evaluacion_pseudonimizado.json' en la carpeta 'data/' "
            f"antes de ejecutar la evaluacion. Ver evaluation/README.md para instrucciones."
        )
    if not report_path.exists():
        raise FileNotFoundError(
            f"No existe el reporte a actualizar: {report_path}\n"
            f"El modo --solo-tiempos solo reemplaza el bloque '## Tiempos': genera "
            f"primero el reporte completo (python -m evaluation.run_evaluation)."
        )

    corpus = cargar_corpus(corpus_path)
    seccion = "\n".join(_seccion_tiempos(corpus, _compute_corpus_hash(corpus_path)))
    reporte = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        reemplazar_seccion_tiempos(reporte, seccion), encoding="utf-8"
    )
    print(f"Seccion 'Tiempos' regenerada en: {report_path}")


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------
def main() -> None:
    """Punto de entrada para `python -m evaluation.run_evaluation`."""
    parser = argparse.ArgumentParser(
        description="Runner de evaluacion del clasificador de mesa de ayuda."
    )
    parser.add_argument(
        "--force",
        "--no-cache",
        dest="force",
        action="store_true",
        default=False,
        help=(
            "Bypasea el cache de predicciones y re-ejecuta la clasificacion completa, "
            "aunque predicciones.json exista y sea valido."
        ),
    )
    parser.add_argument(
        "--confirm-paid",
        dest="confirm_paid",
        action="store_true",
        default=False,
        help=(
            "Autoriza explicitamente una corrida que invoque al clasificador pago "
            "real cuando no haya cache valido. Tambien puede habilitarse con "
            f"{CONFIRM_PAID_ENV_VAR}=1."
        ),
    )
    parser.add_argument(
        "--estimated-cost-per-call",
        dest="estimated_cost_per_call",
        type=float,
        default=None,
        help="Override del costo estimado por llamada (USD), solo para la estimacion.",
    )
    parser.add_argument(
        "--solo-tiempos",
        dest="solo_tiempos",
        action="store_true",
        default=False,
        help=(
            "Regenera solo el bloque '## Tiempos' de evaluation/report.md a partir del "
            "corpus, sin clasificador, sin cache de predicciones y sin gate de corrida "
            "paga (no requiere GEMINI_API_KEY)."
        ),
    )
    args = parser.parse_args()
    if args.solo_tiempos:
        # D5: el modo de solo tiempos no usa cache ni clasificador pago; combinarlo
        # con los flags de esa ruta es un error de uso, no una opcion ignorada.
        if args.force or args.confirm_paid:
            parser.error(
                "--solo-tiempos no se puede combinar con --force, --no-cache "
                "ni --confirm-paid (no usa clasificador ni cache de predicciones)."
            )
        main_solo_tiempos()
        return
    confirm_paid = args.confirm_paid or _env_confirm_paid()
    try:
        asyncio.run(
            main_con_corpus_real(
                force=args.force,
                confirm_paid=confirm_paid,
                estimated_cost_per_call=args.estimated_cost_per_call,
            )
        )
    except PaidRunNotConfirmedError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
