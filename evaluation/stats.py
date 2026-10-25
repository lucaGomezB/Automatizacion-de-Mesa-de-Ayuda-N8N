"""
Análisis estadístico de tiempos — funciones puras.

Envuelve scipy.stats.wilcoxon para la prueba de rangos con signo de dos colas
y calcula el tamaño del efecto rank-biserial, consistente con §4.7 y §7.1
de la tesis.

Convención (c-77, D-A1/D-A2):
    T+ = suma de rangos de las diferencias positivas (manual - automatizado).
    T- = suma de rangos de las diferencias negativas.
    W  = min(T+, T-) es el estadístico de contraste de dos colas de scipy.
    r  = (T+ - T-) / (n(n+1)/2), equivalente a 1 - 4W/(n(n+1)) cuando W = T-.
    Rango teórico de r: [-1, +1]. NO se usa r = 1 - 2W/(n(n+1)) (rango [0, 1]).

Contraste direccional (c-134, D1): además del p bilateral, `ResultadoWilcoxon`
informa el p unilateral de H1 `manual > automatizado` (`alternative="greater"`),
sin alterar W, T+, T-, el p bilateral ni r.

Descriptivos, reducción relativa, tamaño del efecto estandarizado d_z, efecto
mínimo detectable, sensibilidad del redondeo manual y granularidad de la
medición son funciones puras (c-134, D2-D4). El desvío es siempre muestral
(divisor n - 1).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import sqrt
from statistics import NormalDist, fmean, median, stdev
from typing import List, Optional, Sequence, Tuple

# Mínimo de pares que exige scipy.stats.shapiro.
_MIN_PARES_SHAPIRO = 3


def _validar_misma_longitud(
    manual: Sequence[float],
    automatizado: Sequence[float],
) -> None:
    """Exige que ambas series tengan la misma longitud (pares)."""
    if len(manual) != len(automatizado):
        raise ValueError(
            f"Las series deben tener la misma longitud. "
            f"Se recibieron: manual={len(manual)}, automatizado={len(automatizado)}."
        )


@dataclass(frozen=True)
class ResultadoWilcoxon:
    """
    Resultado completo de la prueba de Wilcoxon de rangos con signo.

    Attributes:
        estadistico: Estadístico de contraste W = min(T+, T-) (dos colas).
        t_positivos: Suma de rangos de las diferencias positivas (T+).
        t_negativos: Suma de rangos de las diferencias negativas (T-).
        p: Valor p bilateral.
        p_unilateral: Valor p unilateral de la hipótesis direccional
            `manual > automatizado` (c-134, D1), calculado con
            `alternative="greater"` sobre `manual - automatizado`.
        r: Tamaño del efecto rank-biserial (T+ - T-) / (n(n+1)/2).
        n: Número de pares.
    """

    estadistico: float
    t_positivos: float
    t_negativos: float
    p: float
    p_unilateral: float
    r: float
    n: int


def wilcoxon_tiempos_detallado(
    manual: List[float],
    automatizado: List[float],
) -> ResultadoWilcoxon:
    """
    Prueba de Wilcoxon de rangos con signo sobre pares (manual, automatizado).

    Contrasta H₀: mediana(diferencias) = 0 con la variante de dos colas (`W`, `p`
    y `r` conservan su definición). Además informa el p unilateral de la
    hipótesis direccional `manual > automatizado`, obtenido con una segunda
    llamada `alternative="greater"` (no por división del p bilateral).
    El tamaño del efecto se calcula directamente como
    r = (T+ - T-) / (n(n+1)/2), donde T+ y T- son las sumas de rangos de las
    diferencias positivas y negativas.

    Args:
        manual: Lista de tiempos del flujo manual (en segundos).
        automatizado: Lista de tiempos del flujo automatizado (en segundos).
            Debe tener la misma longitud que `manual`.

    Returns:
        ResultadoWilcoxon con el estadístico de contraste, T+, T-, el valor p
        bilateral, el valor p unilateral, el tamaño del efecto y el número de
        pares.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    _validar_misma_longitud(manual, automatizado)

    try:
        from scipy.stats import rankdata, wilcoxon  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "scipy es requerido para el análisis de tiempos. "
            "Instalá las dependencias con: pip install -r evaluation/requirements.txt"
        ) from exc

    diferencias = [m - a for m, a in zip(manual, automatizado)]
    n = len(diferencias)

    resultado = wilcoxon(diferencias, alternative="two-sided")
    p = float(resultado.pvalue)
    p_unilateral = float(wilcoxon(diferencias, alternative="greater").pvalue)

    # Sumas de rangos calculadas explícitamente (los empates en |d| reciben
    # el rango promedio vía rankdata; las diferencias nulas no aportan a T+/T-).
    rangos = rankdata([abs(d) for d in diferencias])
    t_positivos = float(
        sum(rk for rk, d in zip(rangos, diferencias) if d > 0)
    )
    t_negativos = float(
        sum(rk for rk, d in zip(rangos, diferencias) if d < 0)
    )

    estadistico = min(t_positivos, t_negativos)

    denominador = n * (n + 1) / 2
    if denominador == 0:
        r = 0.0
    else:
        r = (t_positivos - t_negativos) / denominador

    return ResultadoWilcoxon(
        estadistico=estadistico,
        t_positivos=t_positivos,
        t_negativos=t_negativos,
        p=p,
        p_unilateral=p_unilateral,
        r=r,
        n=n,
    )


def wilcoxon_tiempos(
    manual: List[float],
    automatizado: List[float],
) -> Tuple[float, float, float]:
    """
    Envoltorio compatible: devuelve (W, p, r).

    W = min(T+, T-) es el estadístico de contraste de dos colas y
    r = (T+ - T-) / (n(n+1)/2) es el tamaño del efecto rank-biserial.
    Para el detalle de T+ y T-, usar `wilcoxon_tiempos_detallado`.
    """
    resultado = wilcoxon_tiempos_detallado(manual, automatizado)
    return resultado.estadistico, resultado.p, resultado.r


# ---------------------------------------------------------------------------
# Normalidad (Shapiro-Wilk) — función pura (c-99, D1)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoShapiro:
    """
    Resultado del contraste de normalidad de Shapiro-Wilk.

    Attributes:
        n: Número de observaciones de la serie.
        w: Estadístico W de Shapiro-Wilk, o None si no aplica.
        p: Valor p bilateral, o None si no aplica.
        aplicable: False cuando la serie no alcanza el mínimo de pares de la
            prueba (`_MIN_PARES_SHAPIRO`); en ese caso `w` y `p` son None.
    """

    n: int
    w: Optional[float]
    p: Optional[float]
    aplicable: bool


def shapiro_normalidad(datos: Sequence[float]) -> ResultadoShapiro:
    """
    Contraste de normalidad de Shapiro-Wilk sobre una serie.

    Función pura, sin I/O ni dependencia del corpus en disco.

    Args:
        datos: Serie numérica a contrastar.

    Returns:
        ResultadoShapiro con W, p y n. Si la serie tiene menos del mínimo de
        pares que exige la prueba (n < 3), se declara no aplicable con
        `aplicable=False`, `w=None` y `p=None`.

    Raises:
        ImportError: Si scipy no está instalado.
    """
    n = len(datos)
    if n < _MIN_PARES_SHAPIRO:
        return ResultadoShapiro(n=n, w=None, p=None, aplicable=False)

    try:
        from scipy.stats import shapiro  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "scipy es requerido para el análisis de tiempos. "
            "Instalá las dependencias con: pip install -r evaluation/requirements.txt"
        ) from exc

    w, p = shapiro(list(datos))
    return ResultadoShapiro(n=n, w=float(w), p=float(p), aplicable=True)


# ---------------------------------------------------------------------------
# Reducción de tiempos — utilidades puras (c-99, D5)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoReduccion:
    """
    Reducción de tiempo entre el flujo manual y el automatizado.

    La reducción se expresa en segundos ahorrados (`manual - automatizado`).
    La cota conservadora descuenta 1 s al tiempo manual por caso, porque
    `tiempo_manual_s` se redondeó al alza y su valor real no es mayor que el
    reportado.

    Attributes:
        n: Número de pares.
        reduccion_media_reportada: Media de la reducción sobre valores reportados.
        reduccion_mediana_reportada: Mediana de la reducción reportada.
        reduccion_media_conservadora: Media de la reducción con descuento de 1 s.
        reduccion_mediana_conservadora: Mediana de la reducción conservadora.
        pares_no_mas_rapidos: Pares en que el automatizado NO fue más rápido
            (invertidos o empatados, `automatizado >= manual`).
    """

    n: int
    reduccion_media_reportada: float
    reduccion_mediana_reportada: float
    reduccion_media_conservadora: float
    reduccion_mediana_conservadora: float
    pares_no_mas_rapidos: int


def _media(xs: List[float]) -> float:
    return fmean(xs) if xs else 0.0


def _mediana(xs: List[float]) -> float:
    return float(median(xs)) if xs else 0.0


def reduccion_tiempos(
    manual: List[float],
    automatizado: List[float],
) -> ResultadoReduccion:
    """
    Calcula la reducción de tiempo reportada y su cota conservadora.

    Args:
        manual: Tiempos del flujo manual (segundos, redondeados al alza).
        automatizado: Tiempos del flujo automatizado (segundos).

    Returns:
        ResultadoReduccion con media/mediana reportada y conservadora, y el
        conteo de pares en que el automatizado no fue más rápido.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    _validar_misma_longitud(manual, automatizado)

    reducciones = [m - a for m, a in zip(manual, automatizado)]
    conservadoras = [(m - 1.0) - a for m, a in zip(manual, automatizado)]
    pares_no_mas_rapidos = sum(
        1 for m, a in zip(manual, automatizado) if a >= m
    )

    return ResultadoReduccion(
        n=len(reducciones),
        reduccion_media_reportada=_media(reducciones),
        reduccion_mediana_reportada=_mediana(reducciones),
        reduccion_media_conservadora=_media(conservadoras),
        reduccion_mediana_conservadora=_mediana(conservadoras),
        pares_no_mas_rapidos=pares_no_mas_rapidos,
    )


# ---------------------------------------------------------------------------
# Descriptivos de tiempos — funciones puras (c-134, D3)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoDescriptivo:
    """
    Estadísticos descriptivos de una serie de tiempos.

    El desvío usa la convención muestral (divisor n - 1), la misma de
    `statistics.stdev` y de `d_z`.

    Attributes:
        n: Cantidad de observaciones.
        media: Media aritmética.
        mediana: Mediana.
        desvio: Desvío estándar muestral, o None con menos de dos valores.
        minimo: Valor mínimo.
        maximo: Valor máximo.
    """

    n: int
    media: float
    mediana: float
    desvio: Optional[float]
    minimo: float
    maximo: float


def estadisticos_descriptivos(serie: Sequence[float]) -> ResultadoDescriptivo:
    """
    Calcula media, mediana, desvío muestral, mínimo y máximo de una serie.

    Args:
        serie: Valores numéricos (segundos).

    Returns:
        ResultadoDescriptivo. El desvío es None con un único valor (no se
        fabrica un cero).

    Raises:
        ValueError: Si la serie está vacía.
    """
    if len(serie) == 0:
        raise ValueError("La serie está vacía: no hay descriptivos que calcular.")
    valores = [float(x) for x in serie]
    return ResultadoDescriptivo(
        n=len(valores),
        media=fmean(valores),
        mediana=float(median(valores)),
        desvio=stdev(valores) if len(valores) >= 2 else None,
        minimo=min(valores),
        maximo=max(valores),
    )


# ---------------------------------------------------------------------------
# Reducción relativa entre flujos (c-134, D3)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoReduccionRelativa:
    """
    Reducción relativa del tiempo automatizado frente al manual.

    Attributes:
        media: 1 - media(automatizado) / media(manual), o None si la media
            manual es cero.
        mediana: 1 - mediana(automatizado) / mediana(manual), o None si la
            mediana manual es cero.
    """

    media: Optional[float]
    mediana: Optional[float]


def _reduccion_relativa_de(base: float, comparado: float) -> Optional[float]:
    """1 - comparado / base, o None si la base es cero (sin división por cero)."""
    if base == 0:
        return None
    return 1.0 - comparado / base


def reduccion_relativa(
    manual: Sequence[float],
    automatizado: Sequence[float],
) -> ResultadoReduccionRelativa:
    """
    Reducción relativa de la media y de la mediana entre flujos.

    Args:
        manual: Tiempos del flujo manual (segundos).
        automatizado: Tiempos del flujo automatizado (segundos).

    Returns:
        ResultadoReduccionRelativa con la reducción de media y de mediana;
        cada una es None cuando su base manual es cero.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    _validar_misma_longitud(manual, automatizado)
    return ResultadoReduccionRelativa(
        media=_reduccion_relativa_de(fmean(manual), fmean(automatizado)),
        mediana=_reduccion_relativa_de(
            float(median(manual)), float(median(automatizado))
        ),
    )


# ---------------------------------------------------------------------------
# Tamaño del efecto estandarizado de muestras pareadas (c-134, D2)
# ---------------------------------------------------------------------------
def tamano_efecto_dz(
    manual: Sequence[float],
    automatizado: Sequence[float],
) -> Optional[float]:
    """
    Tamaño del efecto estandarizado pareado d_z = media(d) / desvío(d).

    d = manual - automatizado y el desvío es muestral (divisor n - 1).

    Args:
        manual: Tiempos del flujo manual (segundos).
        automatizado: Tiempos del flujo automatizado (segundos).

    Returns:
        d_z, o None (no aplicable) con menos de dos pares o con desvío nulo.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    _validar_misma_longitud(manual, automatizado)
    if len(manual) < 2:
        return None
    diferencias = [m - a for m, a in zip(manual, automatizado)]
    desvio = stdev(diferencias)
    if desvio == 0:
        return None
    return fmean(diferencias) / desvio


# ---------------------------------------------------------------------------
# Efecto mínimo detectable en escala d_z (c-134, D2)
# ---------------------------------------------------------------------------
# Cota inferior de Hodges-Lehmann (108/125) de la eficiencia relativa
# asintótica de la prueba de rangos con signo frente a la t pareada.
ARE_WILCOXON_MINIMA = 0.864


def efecto_minimo_detectable(
    n: int,
    alfa: float = 0.05,
    potencia: float = 0.80,
    bilateral: bool = True,
    eficiencia_relativa: float = 1.0,
) -> float:
    """
    Efecto mínimo detectable en escala d_z por aproximación normal.

    MDE = (z_{1-alfa/2} + z_{potencia}) / raíz(n * ARE); en la variante
    unilateral se usa z_{1-alfa}. Usa `statistics.NormalDist` (sin
    dependencias nuevas).

    Args:
        n: Número de pares (>= 1).
        alfa: Nivel de significancia, en (0, 1).
        potencia: Potencia objetivo, en (0, 1).
        bilateral: True para contraste de dos colas; False para una cola.
        eficiencia_relativa: ARE de la prueba (1.0 = sin ajuste; típicamente
            `ARE_WILCOXON_MINIMA`). Debe ser positiva.

    Returns:
        Efecto mínimo detectable expresado como d_z.

    Raises:
        ValueError: Si `n < 1`, `alfa` o `potencia` están fuera de (0, 1) o
            `eficiencia_relativa <= 0`.
    """
    if n < 1:
        raise ValueError(f"n debe ser al menos 1 (se recibió {n}).")
    if not 0.0 < alfa < 1.0:
        raise ValueError(f"alfa debe estar en (0, 1) (se recibió {alfa}).")
    if not 0.0 < potencia < 1.0:
        raise ValueError(f"potencia debe estar en (0, 1) (se recibió {potencia}).")
    if eficiencia_relativa <= 0:
        raise ValueError(
            f"eficiencia_relativa debe ser positiva (se recibió {eficiencia_relativa})."
        )
    normal = NormalDist()
    cola = alfa / 2 if bilateral else alfa
    z_alfa = normal.inv_cdf(1.0 - cola)
    z_potencia = normal.inv_cdf(potencia)
    return (z_alfa + z_potencia) / sqrt(n * eficiencia_relativa)


# ---------------------------------------------------------------------------
# Sensibilidad del redondeo manual (c-134, D4)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class ResultadoSensibilidad:
    """
    Escenario de sensibilidad: se descuenta una cantidad fija al tiempo manual.

    Attributes:
        descuento_s: Segundos descontados a cada tiempo manual.
        media_manual_ajustada: Media del tiempo manual tras el descuento.
        reduccion_relativa_media: 1 - media(automatizado) / media(manual
            ajustada), o None si la media ajustada es cero.
        wilcoxon: Contraste de Wilcoxon sobre los pares ajustados.
    """

    descuento_s: float
    media_manual_ajustada: float
    reduccion_relativa_media: Optional[float]
    wilcoxon: ResultadoWilcoxon


def escenario_sensibilidad(
    manual: Sequence[float],
    automatizado: Sequence[float],
    descuento_s: float,
) -> ResultadoSensibilidad:
    """
    Recalcula el contraste descontando `descuento_s` segundos a cada tiempo manual.

    Args:
        manual: Tiempos del flujo manual (segundos).
        automatizado: Tiempos del flujo automatizado (segundos).
        descuento_s: Segundos a descontar al manual (0 reproduce el original).

    Returns:
        ResultadoSensibilidad con la media manual ajustada, la reducción
        relativa de la media y el Wilcoxon de los pares ajustados.

    Raises:
        ValueError: Si las series tienen distinta longitud.
    """
    _validar_misma_longitud(manual, automatizado)
    ajustado = [float(m) - descuento_s for m in manual]
    automatizado_f = [float(a) for a in automatizado]
    return ResultadoSensibilidad(
        descuento_s=descuento_s,
        media_manual_ajustada=fmean(ajustado),
        reduccion_relativa_media=_reduccion_relativa_de(
            fmean(ajustado), fmean(automatizado_f)
        ),
        wilcoxon=wilcoxon_tiempos_detallado(ajustado, automatizado_f),
    )


# ---------------------------------------------------------------------------
# Granularidad de la medición manual (c-134, D4)
# ---------------------------------------------------------------------------
def granularidad_manual(
    serie: Sequence[float],
    multiplos: Sequence[int] = (5, 10),
) -> Dict[int, int]:
    """
    Cuenta cuántos valores de la serie son múltiplos exactos de cada paso.

    Sirve para precisar la resolución efectiva de la planilla manual (por
    ejemplo, múltiplos de 5 s y de 10 s).

    Args:
        serie: Tiempos manuales (segundos).
        multiplos: Pasos a evaluar (default 5 y 10 s).

    Returns:
        Diccionario `{paso: cantidad de valores múltiplos del paso}`.
    """
    return {
        paso: sum(1 for valor in serie if valor % paso == 0) for paso in multiplos
    }
