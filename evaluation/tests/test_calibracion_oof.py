"""
Tests de la calibracion con procedencia anti-fuga (c-74, evaluation-framework).

Strict TDD:
    2.2 (RED) -> el ajuste del umbral NO usa el fold evaluado (cross-fitting) y
                 las metricas se reportan out-of-fold. Debe fallar contra la
                 implementacion previa (no existia calibracion out-of-fold).
    2.4 (TRI) -> el umbral de cada fold excluye el fold evaluado; las metricas
                 reportadas se calculan sobre folds intocados y la procedencia
                 queda documentada.

Procedencia elegida por el autor (OQ2): cross-fitting / conformal out-of-fold.
El corpus de evaluacion es el test reportado: NUNCA se usa para ajustar la
prediccion de un caso evaluado.
"""

from __future__ import annotations

import pytest

from evaluation.deterministic_measurement import (
    ObservacionDeterminista,
    PROCEDENCIA_CROSS_FITTING,
    asignar_folds,
    calibrar_out_of_fold,
    curva_precision_cobertura_score,
    elegir_umbral,
    punto_score_en_umbral,
    recolectar_observaciones,
    seleccionar_umbral,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _obs(
    caso_id: str,
    score: float,
    *,
    correcto: bool = True,
    confianza: float = 0.0,
) -> ObservacionDeterminista:
    """Observacion sintetica con verdad simple (Sistemas vs Bases de Datos)."""
    return ObservacionDeterminista(
        caso_id=caso_id,
        sector_asignado="Sistemas",
        verdad=frozenset({"Sistemas"}),
        sector_predicho="Sistemas" if correcto else "Bases de Datos",
        confianza=confianza,
        sin_prediccion=False,
        ambiguo=False,
        score=score,
    )


# Escenario controlado: el umbral in-sample (sobre todo el conjunto) difiere del
# out-of-fold, de modo que un ajuste con fuga se detectaria de inmediato.
OBSERVACIONES = [
    _obs("A1", 0.9, correcto=True),
    _obs("A2", 0.4, correcto=False),
    _obs("B1", 0.9, correcto=True),
    _obs("B2", 0.9, correcto=True),
    _obs("B3", 0.4, correcto=True),
    _obs("B4", 0.4, correcto=True),
]
ASIGNACION_2_FOLDS = {"A1": 0, "A2": 0, "B1": 1, "B2": 1, "B3": 1, "B4": 1}


# ---------------------------------------------------------------------------
# 2.2 RED -> asignacion de folds determinista
# ---------------------------------------------------------------------------
def test_asignar_folds_particiona_y_es_determinista():
    folds_a = asignar_folds(OBSERVACIONES, n_folds=2)
    folds_b = asignar_folds(OBSERVACIONES, n_folds=2)
    assert folds_a == folds_b, "la particion debe ser determinista"
    assert set(folds_a.values()) == {0, 1}
    assert len(folds_a) == len(OBSERVACIONES)


# ---------------------------------------------------------------------------
# 2.2 RED -> seleccion del umbral a partir solo de entrenamiento (score)
# ---------------------------------------------------------------------------
def test_seleccionar_umbral_solo_mira_el_entrenamiento():
    entrenamiento = [o for o in OBSERVACIONES if ASIGNACION_2_FOLDS[o.caso_id] == 1]
    esperado = elegir_umbral(
        curva_precision_cobertura_score(entrenamiento), piso_precision=0.85
    )
    assert seleccionar_umbral(entrenamiento, piso_precision=0.85) == esperado


def test_punto_score_usa_el_score_no_la_confianza():
    """La curva de calibracion se construye sobre `score`, no sobre `confianza`."""
    punto = punto_score_en_umbral(OBSERVACIONES, 0.9)
    assert punto.cortocircuitados == 3  # A1, B1, B2 (score >= 0.9)
    assert punto.precision == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 2.2 RED / 2.4 TRI -> el ajuste excluye el fold evaluado
# ---------------------------------------------------------------------------
def test_calibracion_oof_umbral_por_fold_excluye_fold_evaluado():
    resultado = calibrar_out_of_fold(
        OBSERVACIONES,
        piso_precision=0.85,
        asignacion=ASIGNACION_2_FOLDS,
    )
    # El umbral de cada fold se deriva SOLO de los otros folds.
    for fold in (0, 1):
        entrenamiento = [
            o for o in OBSERVACIONES if ASIGNACION_2_FOLDS[o.caso_id] != fold
        ]
        esperado = seleccionar_umbral(entrenamiento, piso_precision=0.85)
        assert resultado.umbrales_por_fold[fold] == esperado

    assert resultado.umbrales_por_fold == (0.4, 0.9)


def test_calibracion_oof_metricas_sobre_datos_intocados():
    """2.4: las metricas se calculan sobre el fold no usado para ajustar."""
    resultado = calibrar_out_of_fold(
        OBSERVACIONES,
        piso_precision=0.85,
        asignacion=ASIGNACION_2_FOLDS,
    )
    # Fold0 (umbral 0.4): A1 (0.9, correcto) + A2 (0.4, incorrecto) -> 1/2.
    # Fold1 (umbral 0.9): B1 + B2 (0.9, correctos)                  -> 2/2.
    assert resultado.cortocircuitados_oof == 4
    assert resultado.aciertos_oof == 3
    assert resultado.precision_oof == pytest.approx(3 / 4)
    assert resultado.cobertura_oof == pytest.approx(4 / 6)


def test_calibracion_oof_no_reproduce_el_umbral_in_sample():
    """2.2: un ajuste con fuga daria otra metrica; la OOF es la honesta."""
    in_sample = elegir_umbral(
        curva_precision_cobertura_score(OBSERVACIONES), piso_precision=0.85
    )
    resultado = calibrar_out_of_fold(
        OBSERVACIONES,
        piso_precision=0.85,
        asignacion=ASIGNACION_2_FOLDS,
    )
    assert in_sample == 0.9
    # El in-sample reportaria precision 1.0; el out-of-fold, 0.75 (honesto).
    assert punto_score_en_umbral(OBSERVACIONES, in_sample).precision == pytest.approx(
        1.0
    )
    assert resultado.precision_oof == pytest.approx(0.75)


# ---------------------------------------------------------------------------
# 2.4 TRI -> procedencia documentada
# ---------------------------------------------------------------------------
def test_procedencia_queda_documentada():
    resultado = calibrar_out_of_fold(
        OBSERVACIONES,
        piso_precision=0.85,
        asignacion=ASIGNACION_2_FOLDS,
    )
    assert resultado.procedencia == PROCEDENCIA_CROSS_FITTING
    assert "out-of-fold" in resultado.procedencia
    assert "cross-fitting" in resultado.procedencia
    assert resultado.n_folds == 2
    assert resultado.piso_precision == 0.85


def test_calibracion_oof_por_defecto_evalua_todos_los_casos_una_vez():
    """TRI: con la particion por defecto, cada caso se evalua exactamente una vez."""
    resultado = calibrar_out_of_fold(OBSERVACIONES, piso_precision=0.85, n_folds=3)
    assert sum(punto.n_test for punto in resultado.puntos) == len(OBSERVACIONES)
    assert len(resultado.umbrales_por_fold) == 3


def test_seleccionar_umbral_none_si_el_piso_es_inalcanzable():
    entrenamiento = [_obs("X", 0.5, correcto=False), _obs("Y", 0.5, correcto=True)]
    assert seleccionar_umbral(entrenamiento, piso_precision=0.99) is None


def test_calibracion_oof_sin_umbral_viable_no_fabrica_cobertura():
    """TRI: si el piso es inalcanzable, la cobertura out-of-fold es 0 (honesta)."""
    resultado = calibrar_out_of_fold(OBSERVACIONES, piso_precision=1.01, n_folds=2)
    assert resultado.cortocircuitados_oof == 0
    assert resultado.cobertura_oof == 0.0
    assert resultado.precision_oof == 0.0


# ---------------------------------------------------------------------------
# 2.2 RED -> la recoleccion conserva el score de correctitud
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_recolectar_observaciones_conserva_el_score():
    from evaluation.corpus import CasoEvaluacion

    class _Fake:
        async def classify(self, descripcion: str):
            return type(
                "R",
                (),
                {
                    "sector_predicho": "Sistemas",
                    "confianza": 0.0,
                    "sin_prediccion": False,
                    "ambiguo": False,
                    "sectores_adicionales": [],
                    "score_correctitud": 0.77,
                },
            )()

    casos = [
        CasoEvaluacion(
            id="1",
            descripcion="con senal",
            sector_asignado="Sistemas",
            sectores_adicionales=[],
        )
    ]
    observaciones = await recolectar_observaciones(casos, _Fake())
    assert observaciones[0].score == pytest.approx(0.77)
