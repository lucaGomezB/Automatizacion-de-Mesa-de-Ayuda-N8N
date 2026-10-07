"""
Tests del punto de operacion COMPARATIVO del cortocircuito (c-74, OQ3 revisado).

Criterio (design D4 revisado): maximizar cobertura sujeta al piso COMPARATIVO
`precision_det(S) >= precision_gem(S)` sobre el subconjunto cortocircuitable S,
estimado out-of-fold con predicciones de Gemini CACHEADAS (sin invocar al
proveedor). El corpus es el test reportado: no se ajusta nada con el.

Strict TDD:
    4.1 (RED)  -> la curva comparativa y la eleccion del punto existen y usan el
                  piso comparativo, no un piso absoluto.
    4.1 (TRI)  -> un piso comparativo mas exigente (Gemini fuerte) fuerza un
                  umbral mas alto / menor cobertura; la procedencia se documenta.
    4.4 (RED)  -> la re-medicion hibrida offline reutiliza la cache de Gemini y
                  no fabrica predicciones.
"""

from __future__ import annotations

import json

import pytest

from evaluation.deterministic_measurement import (
    ObservacionDeterminista,
    PROCEDENCIA_COMPARATIVA,
    PrediccionCacheada,
    calibrar_comparativo_out_of_fold,
    cargar_predicciones_cacheadas,
    curva_comparativa,
    elegir_punto_comparativo,
    medir_hibrido_con_cache,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _obs(
    caso_id: str,
    score: float,
    *,
    correcto: bool = True,
    asignado: str = "Sistemas",
    sectores_adicionales: tuple[str, ...] = (),
) -> ObservacionDeterminista:
    return ObservacionDeterminista(
        caso_id=caso_id,
        sector_asignado=asignado,
        verdad=frozenset({asignado}),
        sector_predicho=asignado if correcto else "Bases de Datos",
        confianza=0.0,
        sin_prediccion=False,
        ambiguo=False,
        score=score,
        sectores_adicionales=sectores_adicionales,
    )


#: El determinista y Gemini aciertan los dos casos -> cualquier tau cumple el piso.
DET_Y_GEM_OK = {
    "1": "Sistemas",
    "2": "Sistemas",
}

#: Gemini acierta ambos; el determinista falla el caso de score bajo.
DET_FALLA_BAJO = {
    "1": "Sistemas",
    "2": "Sistemas",
}

#: Gemini FUERTE: acierta ambos; el determinista solo acierta el de score alto.
GEM_FUERTE = {
    "1": "Sistemas",
    "2": "Sistemas",
}


# ---------------------------------------------------------------------------
# 4.1 RED -> la curva comparativa expone det vs gem por umbral
# ---------------------------------------------------------------------------
def test_curva_comparativa_calcula_det_y_gem_por_umbral():
    observaciones = [_obs("1", 0.9, correcto=True), _obs("2", 0.5, correcto=False)]
    curva = curva_comparativa(observaciones, DET_Y_GEM_OK)
    por_umbral = {round(p.umbral, 6): p for p in curva}

    alto = por_umbral[0.9]
    assert alto.cortocircuitados == 1
    assert alto.precision_det == pytest.approx(1.0)
    assert alto.precision_gem == pytest.approx(1.0)
    assert alto.cumple_piso_comparativo is True

    bajo = por_umbral[0.5]
    assert bajo.cortocircuitados == 2
    # det acierta 1/2; gemini acierta 2/2 -> el piso comparativo NO se cumple.
    assert bajo.precision_det == pytest.approx(0.5)
    assert bajo.precision_gem == pytest.approx(1.0)
    assert bajo.cumple_piso_comparativo is False


def test_curva_comparativa_excluye_gemini_sin_prediccion_guardada():
    observaciones = [_obs("1", 0.9, correcto=True), _obs("2", 0.5, correcto=True)]
    # El caso 2 no tiene prediccion de Gemini cacheada (None): no entra al denominador.
    curva = curva_comparativa(observaciones, {"1": "Sistemas", "2": None})
    bajo = [p for p in curva if p.cortocircuitados == 2][0]
    assert bajo.casos_gem == 1
    assert bajo.precision_gem == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 4.1 RED -> eleccion del punto: maximiza cobertura sujeta al piso comparativo
# ---------------------------------------------------------------------------
def test_elegir_punto_comparativo_prioriza_cobertura_si_el_piso_se_cumple():
    observaciones = [_obs("1", 0.9, correcto=True), _obs("2", 0.5, correcto=True)]
    curva = curva_comparativa(observaciones, DET_Y_GEM_OK)
    punto = elegir_punto_comparativo(curva)
    assert punto is not None
    assert punto.cobertura == pytest.approx(1.0)
    assert punto.umbral == pytest.approx(0.5)  # el menor score que cubre todo


def test_elegir_punto_comparativo_sube_el_umbral_si_el_piso_obliga():
    """El caso de score bajo hace fallar al determinista: Gemini fuerte lo fuerza.

    Con un piso COMPARATIVO, el punto de operacion debe subir el umbral para
    excluir el caso donde el determinista es peor que Gemini.
    """
    observaciones = [_obs("1", 0.9, correcto=True), _obs("2", 0.5, correcto=False)]
    curva = curva_comparativa(observaciones, GEM_FUERTE)
    punto = elegir_punto_comparativo(curva)
    assert punto is not None
    assert punto.umbral == pytest.approx(0.9)
    assert punto.cobertura == pytest.approx(0.5)
    assert punto.precision_det >= punto.precision_gem


def test_elegir_punto_comparativo_none_si_nunca_gana_el_determinista():
    observaciones = [_obs("1", 0.9, correcto=False), _obs("2", 0.5, correcto=False)]
    curva = curva_comparativa(observaciones, DET_Y_GEM_OK)
    assert elegir_punto_comparativo(curva) is None


def test_punto_comparativo_no_existe_sin_cortocircuitables():
    from evaluation.deterministic_measurement import _es_cortocircuitable  # noqa: F401

    sin_senal = ObservacionDeterminista(
        caso_id="x",
        sector_asignado="Sistemas",
        verdad=frozenset({"Sistemas"}),
        sector_predicho=None,
        confianza=0.0,
        sin_prediccion=True,
        ambiguo=False,
        score=0.0,
    )
    curva = curva_comparativa([sin_senal], {})
    assert elegir_punto_comparativo(curva) is None


# ---------------------------------------------------------------------------
# 4.1 RED/TRI -> la procedencia comparativa se documenta
# ---------------------------------------------------------------------------
def test_procedencia_comparativa_documentada():
    assert "out-of-fold" in PROCEDENCIA_COMPARATIVA
    assert "comparativ" in PROCEDENCIA_COMPARATIVA.lower()


# ---------------------------------------------------------------------------
# 4.1 RED -> calibracion comparativa out-of-fold
# ---------------------------------------------------------------------------
ASIGNACION_2_FOLDS = {"1": 0, "2": 0, "3": 1, "4": 1}


def test_calibrar_comparativo_oof_umbral_por_fold_excluye_fold_evaluado():
    observaciones = [
        _obs("1", 0.9, correcto=True),
        _obs("2", 0.5, correcto=False),
        _obs("3", 0.9, correcto=True),
        _obs("4", 0.5, correcto=False),
    ]
    gem = {cid: "Sistemas" for cid in ("1", "2", "3", "4")}
    resultado = calibrar_comparativo_out_of_fold(
        observaciones, gem, asignacion=ASIGNACION_2_FOLDS
    )
    for fold in (0, 1):
        entrenamiento = [
            o for o in observaciones if ASIGNACION_2_FOLDS[o.caso_id] != fold
        ]
        esperado = elegir_punto_comparativo(
            curva_comparativa(entrenamiento, gem)
        )
        esperado_umbral = esperado.umbral if esperado is not None else None
        assert resultado.umbrales_por_fold[fold] == esperado_umbral


def test_calibrar_comparativo_oof_reporta_cobertura_y_precisiones():
    observaciones = [
        _obs("1", 0.9, correcto=True),
        _obs("2", 0.5, correcto=False),
        _obs("3", 0.9, correcto=True),
        _obs("4", 0.5, correcto=False),
    ]
    gem = {cid: "Sistemas" for cid in ("1", "2", "3", "4")}
    resultado = calibrar_comparativo_out_of_fold(
        observaciones, gem, asignacion=ASIGNACION_2_FOLDS
    )
    # Cada fold entrena con el opuesto: tau=0.9 -> selecciona el caso de score 0.9.
    assert resultado.cortocircuitados_oof == 2
    assert resultado.precision_det_oof == pytest.approx(1.0)
    assert resultado.precision_gem_oof == pytest.approx(1.0)
    assert resultado.cobertura_oof == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 4.4 RED -> re-medicion hibrida offline reutilizando la cache de Gemini
# ---------------------------------------------------------------------------
def _cache(caso_id: str, sector: str | None, etapa: str = "gemini") -> PrediccionCacheada:
    return PrediccionCacheada(
        sector_predicho=sector, sectores_adicionales=(), etapa=etapa
    )


def test_medir_hibrido_con_cache_mezcla_determinista_y_gemini():
    observaciones = [
        _obs("1", 0.9, correcto=True),   # score >= umbral -> determinista
        _obs("2", 0.5, correcto=False),  # score < umbral  -> Gemini (cache)
    ]
    cache = {"1": _cache("1", "Bases de Datos"), "2": _cache("2", "Sistemas")}
    resultado = medir_hibrido_con_cache(observaciones, cache, umbral_score=0.8)

    assert resultado["mix"] == {"deterministic": 1, "gemini": 1}
    # Determinista acierta el caso 1; Gemini (cache) acierta el caso 2 -> 2/2.
    assert resultado["exactitud_estricta"] == pytest.approx(1.0)


def test_medir_hibrido_con_cache_escala_los_no_cortocircuitables():
    sin_senal = ObservacionDeterminista(
        caso_id="9",
        sector_asignado="Bases de Datos",
        verdad=frozenset({"Bases de Datos"}),
        sector_predicho=None,
        confianza=0.0,
        sin_prediccion=True,
        ambiguo=False,
        score=0.0,
    )
    cache = {"9": _cache("9", "Bases de Datos")}
    resultado = medir_hibrido_con_cache([sin_senal], cache, umbral_score=0.5166)
    assert resultado["mix"] == {"deterministic": 0, "gemini": 1}
    assert resultado["exactitud_estricta"] == pytest.approx(1.0)


def test_cargar_predicciones_cacheadas_lee_el_formato_del_runner(tmp_path):
    path = tmp_path / "predicciones.json"
    path.write_text(
        json.dumps(
            {
                "cache_meta": {"classifier_version": "hybrid-v2"},
                "predictions": [
                    {
                        "caso_id": "R001",
                        "sector_asignado": "Sistemas",
                        "sector_predicho": "Sistemas",
                        "confianza": 0.9,
                        "etapa": "gemini",
                        "sectores_adicionales": ["Bases de Datos"],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    cache = cargar_predicciones_cacheadas(path)
    assert set(cache.keys()) == {"R001"}
    assert cache["R001"].sector_predicho == "Sistemas"
    assert cache["R001"].etapa == "gemini"
    assert cache["R001"].sectores_adicionales == ("Bases de Datos",)
