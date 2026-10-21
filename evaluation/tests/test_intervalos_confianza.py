"""
Tests para los intervalos de confianza de c-108.

Cubre las funciones puras de `evaluation/metrics.py`:
- `intervalos_por_clase`: IC de precision y sensibilidad por Wilson y IC de
  F1 por bootstrap percentil a nivel de caso, con semilla fija.
- `intervalos_conjunto`: IC bootstrap percentil a nivel de caso para subset
  accuracy, Hamming loss y micro-F1.

TDD — ciclos RED -> GREEN -> TRIANGULATE -> REFACTOR. Funciones puras, sin I/O
ni servicios externos; deterministas con semilla fija.
"""

from __future__ import annotations

# Sectores canonicos abreviados para legibilidad
SEG = "Seguridad Informatica"
SIH = "Soporte Tecnico Hardware"
SISW = "Soporte Tecnico Software"
BD = "Bases de Datos"
SIS = "Sistemas"


# ---------------------------------------------------------------------------
# Dataset de juguete: soporte >= 2 en cuatro clases, soporte 1 en BD
# ---------------------------------------------------------------------------
def _toy_primario():
    """Verad/predicho principal con conteos conocidos por clase."""
    reales = (
        [SIH] * 5
        + [SISW] * 4
        + [SEG] * 3
        + [SIS] * 2
        + [BD] * 1
    )
    predichos = (
        [SIH] * 5
        + [SISW] * 3 + [SIH]
        + [SEG] * 2 + [SISW]
        + [SIS] * 1 + [SISW]
        + [SIS]
    )
    return reales, predichos


# ===========================================================================
# 1. IC por clase
# ===========================================================================
def test_intervalos_por_clase_reporta_tres_intervalos_en_clases_estimables():
    """Cada clase con soporte >= 2 devuelve IC de precision, sensibilidad y F1."""
    from evaluation.metrics import intervalos_por_clase

    reales, predichos = _toy_primario()
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    for clase in (SIH, SISW, SEG, SIS):
        ic = resultado[clase]
        assert ic.estimable is True
        assert ic.precision is not None
        assert ic.sensibilidad is not None
        assert ic.f1 is not None
        assert ic.soporte >= 2


def test_intervalos_por_clase_marca_la_clase_unitaria_como_no_estimable():
    """`Bases de Datos` (soporte 1) es no estimable y sin IC."""
    from evaluation.metrics import intervalos_por_clase

    reales, predichos = _toy_primario()
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    ic = resultado[BD]
    assert ic.estimable is False
    assert ic.soporte == 1
    assert ic.precision is None
    assert ic.sensibilidad is None
    assert ic.f1 is None


def test_intervalos_por_clase_precision_coincide_con_wilson_analitico():
    """El IC de precision de cada clase usa `intervalo_wilson(tp, tp + fp)`."""
    from evaluation.metrics import intervalo_wilson, intervalos_por_clase

    reales, predichos = _toy_primario()
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    # SIH: tp = 5 (5 correctos), fp = 1 (un SISW mal predicho como SIH)
    esperado = intervalo_wilson(5, 6)
    assert resultado[SIH].precision == esperado


def test_intervalos_por_clase_es_reproducible_con_la_misma_semilla():
    """La misma semilla produce exactamente los mismos intervalos de F1."""
    from evaluation.metrics import intervalos_por_clase

    reales, predichos = _toy_primario()
    primera = intervalos_por_clase(reales, predichos, semilla=1234, remuestreos=300)
    segunda = intervalos_por_clase(reales, predichos, semilla=1234, remuestreos=300)

    for clase in (SIH, SISW, SEG, SIS):
        assert primera[clase].f1 == segunda[clase].f1


def test_intervalos_por_clase_f1_queda_en_el_rango_unitario():
    """Los limites del bootstrap de F1 caen en [0, 1] y estan ordenados."""
    from evaluation.metrics import intervalos_por_clase

    reales, predichos = _toy_primario()
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    for clase in (SIH, SISW, SEG, SIS):
        bajo, alto = resultado[clase].f1
        assert 0.0 <= bajo <= alto <= 1.0


def test_intervalos_por_clase_clasificacion_perfecta_f1_tiene_techo_uno():
    """
    Con prediccion perfecta, todo remuestreo que retiene la clase da F1 = 1.0,
    de modo que el limite superior del IC de F1 es exactamente 1.0. El limite
    inferior puede ser menor porque un remuestreo a nivel de caso puede omitir
    por completo una clase de soporte pequeno.
    """
    from evaluation.metrics import intervalos_por_clase

    reales = [SIH] * 3 + [SISW] * 2 + [SEG] * 2
    predichos = [SIH] * 3 + [SISW] * 2 + [SEG] * 2
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    for clase in (SIH, SISW, SEG):
        bajo, alto = resultado[clase].f1
        assert alto == 1.0
        assert bajo <= 1.0


def test_intervalos_por_clase_sensibilidad_coincide_con_wilson_analitico():
    """El IC de sensibilidad de cada clase usa `intervalo_wilson(tp, soporte)`."""
    from evaluation.metrics import intervalo_wilson, intervalos_por_clase

    reales, predichos = _toy_primario()
    resultado = intervalos_por_clase(reales, predichos, remuestreos=300)

    # SISW: soporte = 4, tp = 3 (una SISW mal predicha como SIH)
    assert resultado[SISW].sensibilidad == intervalo_wilson(3, 4)


def test_intervalos_por_clase_segundo_dataset_distintos_conteos():
    """Segundo dataset de juguete con conteos distintos: soporte y estimabilidad."""
    from evaluation.metrics import intervalos_por_clase

    # SEG 6 reales, 5 correctos; SIH 2 reales, 0 correctos; BD 3, 0 correctos
    reales = [SEG] * 6 + [SIH] * 2 + [BD] * 3
    predichos = [SEG] * 5 + [SISW] + [SISW] * 2 + [SISW] * 3
    resultado = intervalos_por_clase(reales, predichos, semilla=7, remuestreos=300)

    assert resultado[SEG].soporte == 6
    assert resultado[SEG].estimable is True
    assert resultado[SIH].soporte == 2
    assert resultado[SIH].estimable is True
    # SIH no recibe predicciones: precision puntual 0 y Wilson acota en [0, 1]
    bajo, alto = resultado[SIH].precision
    assert bajo == 0.0
    assert alto <= 1.0
    # BD tiene soporte 3 (estimable), pero cero aciertos: sensibilidad ~ 0
    assert resultado[BD].estimable is True
    assert resultado[BD].sensibilidad[0] <= 1e-12


# ===========================================================================
# 2. IC de las metricas de conjunto
# ===========================================================================
def _toy_conjuntos():
    """Verdad y prediccion multietiqueta con subset parcial."""
    verdad = [
        frozenset({SIH}),
        frozenset({SIH, SISW}),
        frozenset({SEG}),
        frozenset({SIS}),
        frozenset({SISW, BD}),
        frozenset({SEG}),
        frozenset({SIH}),
        frozenset({SIS}),
        frozenset({SISW}),
        frozenset({SEG}),
    ]
    predicho = [
        frozenset({SIH}),
        frozenset({SIH}),
        frozenset({SEG}),
        frozenset({SIS}),
        frozenset({SISW}),
        frozenset({SEG}),
        frozenset({SIH}),
        frozenset({SIH}),
        frozenset({SISW}),
        frozenset({SEG}),
    ]
    return verdad, predicho


def test_intervalos_conjunto_reporta_las_tres_metricas():
    """Devuelve IC para subset accuracy, Hamming loss y micro-F1."""
    from evaluation.metrics import intervalos_conjunto

    verdad, predicho = _toy_conjuntos()
    resultado = intervalos_conjunto(verdad, predicho, remuestreos=300)

    for intervalo in (
        resultado.subset_accuracy,
        resultado.hamming_loss,
        resultado.micro_f1,
    ):
        bajo, alto = intervalo
        assert 0.0 <= bajo <= alto <= 1.0


def test_intervalos_conjunto_es_reproducible_con_la_misma_semilla():
    """La misma semilla reproduce los tres intervalos de conjunto."""
    from evaluation.metrics import intervalos_conjunto

    verdad, predicho = _toy_conjuntos()
    primera = intervalos_conjunto(verdad, predicho, semilla=99, remuestreos=300)
    segunda = intervalos_conjunto(verdad, predicho, semilla=99, remuestreos=300)

    assert primera.subset_accuracy == segunda.subset_accuracy
    assert primera.hamming_loss == segunda.hamming_loss
    assert primera.micro_f1 == segunda.micro_f1


def test_intervalos_conjunto_perfecto_colapsa_en_los_extremos():
    """Con conjunto perfecto: subset y micro-F1 en 1.0, Hamming loss en 0.0."""
    from evaluation.metrics import intervalos_conjunto

    verdad = [frozenset({SIH, SISW}), frozenset({SEG}), frozenset({SIS})]
    predicho = [frozenset({SIH, SISW}), frozenset({SEG}), frozenset({SIS})]
    resultado = intervalos_conjunto(verdad, predicho, remuestreos=300)

    assert resultado.subset_accuracy == (1.0, 1.0)
    assert resultado.hamming_loss == (0.0, 0.0)
    assert resultado.micro_f1 == (1.0, 1.0)


def test_intervalos_conjunto_segundo_dataset_distintos_conteos():
    """Segundo dataset multietiqueta: acota las tres metricas puntuales."""
    from evaluation.metrics import (
        exactitud_subconjunto,
        f1_micro,
        intervalos_conjunto,
        perdida_hamming,
    )

    verdad = (
        [frozenset({SIH})] * 4
        + [frozenset({SIH, SISW})] * 3
        + [frozenset({SEG, BD})] * 3
        + [frozenset({SIS})] * 2
    )
    predicho = (
        [frozenset({SIH})] * 4
        + [frozenset({SIH})] * 3
        + [frozenset({SEG})] * 3
        + [frozenset({SIS, SISW})] * 2
    )

    resultado = intervalos_conjunto(verdad, predicho, semilla=2024, remuestreos=500)

    for intervalo in (
        resultado.subset_accuracy,
        resultado.hamming_loss,
        resultado.micro_f1,
    ):
        bajo, alto = intervalo
        assert 0.0 <= bajo <= alto <= 1.0

    # El IC percentil contiene el valor puntual para este dataset no degenerado
    assert (
        resultado.subset_accuracy[0]
        <= exactitud_subconjunto(verdad, predicho)
        <= resultado.subset_accuracy[1]
    )
    assert (
        resultado.hamming_loss[0]
        <= perdida_hamming(verdad, predicho)
        <= resultado.hamming_loss[1]
    )
    assert resultado.micro_f1[0] <= f1_micro(verdad, predicho) <= resultado.micro_f1[1]
