"""
Tests del contraste pareado de McNemar entre etapas (c-131, D13).

Strict TDD (tareas 7.1-7.7):
    RED  -> `evaluation.stats` no expone `contraste_mcnemar`/`ResultadoMcNemar` y
            `evaluation.deterministic_measurement` no ensambla el contraste sobre S.
    GREEN -> funcion pura en `stats.py`; ensamblado + linea del reporte offline.

Convencion: `b` = acierta solo la primera serie (etapa deterministica), `c` = acierta
solo la segunda (Gemini). Estadistico corregido por continuidad
`max(0, |b - c| - 1)^2 / (b + c)` (1 gl); p exacto bilateral
`min(1, 2 P(X <= min(b, c)))`, `X ~ Bin(b + c; 0,5)`. El p primario es el exacto si
`b + c < 25` y el corregido en otro caso.
"""

from __future__ import annotations

import dataclasses

import pytest


def _pares(ambas: int, solo_a: int, solo_b: int, ninguna: int):
    """Dos secuencias pareadas de aciertos con la tabla 2x2 pedida."""
    a = [True] * ambas + [True] * solo_a + [False] * solo_b + [False] * ninguna
    b = [True] * ambas + [False] * solo_a + [True] * solo_b + [False] * ninguna
    return a, b


# ---------------------------------------------------------------------------
# 7.1 / 7.2 contraste_mcnemar: tabla 2x2, estadistico, p y criterio
# ---------------------------------------------------------------------------
def test_tabla_2x2_cuenta_ambas_solo_a_solo_b_y_ninguna_y_suma_los_pares():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=60, solo_a=10, solo_b=2, ninguna=28))

    assert (r.ambas, r.solo_a, r.solo_b, r.ninguna) == (60, 10, 2, 28)
    assert r.pares == 100
    assert r.ambas + r.solo_a + r.solo_b + r.ninguna == r.pares


def test_oraculo_b10_c2_estadistico_corregido_p_chi2_y_p_exacto():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=5, solo_a=10, solo_b=2, ninguna=3))

    assert r.estadistico == pytest.approx(4.0833, abs=5e-5)
    assert r.p_corregido == pytest.approx(0.0433, abs=5e-5)
    assert r.p_exacto == pytest.approx(0.0386, abs=5e-5)


def test_pocas_discordancias_usan_el_p_exacto_como_primario():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=5, solo_a=10, solo_b=2, ninguna=3))

    assert r.criterio == "exacto"
    assert r.p_primario == r.p_exacto


def test_longitudes_distintas_levantan_value_error():
    from evaluation.stats import contraste_mcnemar

    with pytest.raises(ValueError, match="longitud"):
        contraste_mcnemar([True, False], [True])


def test_sin_discordancias_es_no_aplicable_sin_fabricar_estadistico_ni_p():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=4, solo_a=0, solo_b=0, ninguna=2))

    assert r.aplicable is False
    assert r.criterio == "no aplicable"
    assert r.estadistico is None
    assert r.p_corregido is None
    assert r.p_exacto is None
    assert r.p_primario is None
    assert (r.ambas, r.ninguna, r.pares) == (4, 2, 6)


def test_resultado_es_inmutable():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(1, 1, 0, 0))
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.solo_a = 99  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 7.3 TRIANGULATE: otros oraculos calculados a mano
# ---------------------------------------------------------------------------
def test_oraculo_b30_c15_muchas_discordancias_usa_el_chi2_corregido():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=20, solo_a=30, solo_b=15, ninguna=10))

    assert r.estadistico == pytest.approx(4.3556, abs=5e-5)
    assert r.p_corregido == pytest.approx(0.0369, abs=5e-5)
    assert r.p_exacto == pytest.approx(0.0357, abs=5e-5)
    assert r.criterio == "corregido"
    assert r.p_primario == r.p_corregido


def test_oraculo_b_igual_c_no_produce_estadistico_positivo():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=3, solo_a=5, solo_b=5, ninguna=2))

    assert r.estadistico == pytest.approx(0.0, abs=5e-5)
    assert r.p_corregido == pytest.approx(1.0, abs=5e-5)
    assert r.p_exacto == pytest.approx(1.0, abs=5e-5)
    assert r.aplicable is True


def test_oraculo_b7_c0_una_sola_direccion():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar(*_pares(ambas=1, solo_a=7, solo_b=0, ninguna=1))

    assert r.estadistico == pytest.approx(5.1429, abs=5e-5)
    assert r.p_corregido == pytest.approx(0.0233, abs=5e-5)
    assert r.p_exacto == pytest.approx(0.0156, abs=5e-5)
    assert r.criterio == "exacto"


def test_frontera_24_y_25_discordancias_cambia_el_criterio():
    from evaluation.stats import contraste_mcnemar

    en_24 = contraste_mcnemar(*_pares(0, 14, 10, 0))
    en_25 = contraste_mcnemar(*_pares(0, 15, 10, 0))

    assert (en_24.solo_a + en_24.solo_b, en_24.criterio) == (24, "exacto")
    assert (en_25.solo_a + en_25.solo_b, en_25.criterio) == (25, "corregido")


def test_el_p_exacto_se_trunca_en_uno_y_es_simetrico_en_b_y_c():
    from evaluation.stats import contraste_mcnemar

    a = contraste_mcnemar(*_pares(0, 10, 2, 0))
    b = contraste_mcnemar(*_pares(0, 2, 10, 0))

    assert a.p_exacto == pytest.approx(b.p_exacto)
    assert a.estadistico == pytest.approx(b.estadistico)
    assert contraste_mcnemar(*_pares(0, 1, 1, 0)).p_exacto == 1.0


def test_acepta_secuencias_de_enteros_0_y_1():
    from evaluation.stats import contraste_mcnemar

    r = contraste_mcnemar([1, 1, 0, 1], [0, 1, 1, 0])

    assert (r.ambas, r.solo_a, r.solo_b, r.ninguna) == (1, 2, 1, 0)


# ===========================================================================
# 7.4 / 7.5 / 7.6 Ensamblado sobre S y linea del reporte comparativo offline
# ===========================================================================
SIS = "Sistemas"
BD = "Bases de Datos"
SW = "Soporte Tecnico Software"
TAU = 0.5166


def _obs(
    caso_id: str,
    predicho: str | None,
    score: float,
    *,
    asignado: str = SIS,
    verdad: frozenset | None = None,
    ambiguo: bool = False,
    sin_prediccion: bool = False,
):
    from evaluation.deterministic_measurement import ObservacionDeterminista

    return ObservacionDeterminista(
        caso_id=caso_id,
        sector_asignado=asignado,
        verdad=verdad if verdad is not None else frozenset({asignado}),
        sector_predicho=predicho,
        confianza=0.5,
        sin_prediccion=sin_prediccion,
        ambiguo=ambiguo,
        score=score,
    )


def _gem(sector: str | None, etapa: str = "gemini"):
    from evaluation.deterministic_measurement import PrediccionCacheada

    return PrediccionCacheada(sector_predicho=sector, etapa=etapa)


def _escenario():
    """
    S = {o1, o2, o3, o4, o6}. Pares: o1 (ambas), o2 (solo det), o3 (solo gem).
    o4 no tiene prediccion de Gemini; o6 solo tiene una cacheada de etapa
    'deterministic'. o5 es ambiguo y o7 queda bajo el umbral: fuera de S.
    """
    observaciones = [
        _obs("o1", SIS, 0.9),
        _obs("o2", SIS, 0.8),
        _obs("o3", BD, 0.7),
        _obs("o4", SIS, 0.6),
        _obs("o5", SIS, 0.9, ambiguo=True),
        _obs("o6", SIS, 0.6),
        _obs("o7", SIS, 0.3),
    ]
    cache = {
        "o1": _gem(SIS),
        "o2": _gem(BD),
        "o3": _gem(SIS),
        "o5": _gem(BD),
        "o6": _gem(SIS, etapa="deterministic"),
        "o7": _gem(BD),
    }
    return observaciones, cache


def test_contraste_usa_solo_S_aparea_por_caso_y_excluye_los_sin_gemini():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    observaciones, cache = _escenario()
    c = contraste_det_gem_en_s(observaciones, cache, TAU)

    assert c.tamano_s == 5
    assert c.pares == 3
    assert c.excluidos == ("o4", "o6")
    assert (c.mcnemar.ambas, c.mcnemar.solo_a, c.mcnemar.solo_b, c.mcnemar.ninguna) == (
        1, 1, 1, 0
    )
    assert c.mcnemar.pares == c.pares


def test_contraste_exactitud_de_cada_etapa_sobre_los_pares():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    observaciones, cache = _escenario()
    c = contraste_det_gem_en_s(observaciones, cache, TAU)

    assert (c.aciertos_det, c.aciertos_gem) == (2, 2)
    assert c.exactitud_det == pytest.approx(2 / 3)
    assert c.exactitud_gem == pytest.approx(2 / 3)


def test_contraste_mide_el_acierto_estricto_contra_sector_asignado_no_la_verdad_laxa():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    # Gemini cae en un adicional de verdad (laxo) pero no en el asignado: no acierta.
    observaciones = [_obs("a", SIS, 0.9, verdad=frozenset({SIS, SW}))]
    cache = {"a": _gem(SW)}

    c = contraste_det_gem_en_s(observaciones, cache, TAU)

    assert (c.aciertos_det, c.aciertos_gem) == (1, 0)
    assert (c.mcnemar.solo_a, c.mcnemar.solo_b) == (1, 0)


def test_contraste_umbral_mas_alto_reduce_S_y_los_pares():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    observaciones, cache = _escenario()
    c = contraste_det_gem_en_s(observaciones, cache, 0.75)

    assert c.tamano_s == 2  # o1 (0.9) y o2 (0.8)
    assert c.pares == 2
    assert c.excluidos == ()


def test_contraste_sin_pares_es_no_aplicable_sin_fallar():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    c = contraste_det_gem_en_s([_obs("a", SIS, 0.9)], {}, TAU)

    assert c.pares == 0
    assert c.excluidos == ("a",)
    assert c.exactitud_det is None and c.exactitud_gem is None
    assert c.mcnemar.aplicable is False


def test_lineas_del_contraste_reportan_pares_excluidos_tabla_y_p():
    from evaluation.deterministic_measurement import (
        contraste_det_gem_en_s,
        lineas_contraste_mcnemar,
    )

    observaciones, cache = _escenario()
    texto = "\n".join(lineas_contraste_mcnemar(contraste_det_gem_en_s(observaciones, cache, TAU)))

    assert "McNemar" in texto
    assert "|S| = 5" in texto
    assert "pares con prediccion de ambas etapas: 3" in texto
    assert "excluidos (sin prediccion de Gemini): o4, o6" in texto
    assert "solo la deterministica (b) 1" in texto
    assert "solo Gemini (c) 1" in texto
    assert "criterio exacto" in texto


def test_lineas_del_contraste_sin_resultado_dicen_no_computable():
    from evaluation.deterministic_measurement import lineas_contraste_mcnemar

    texto = "\n".join(lineas_contraste_mcnemar(None))

    assert "McNemar" in texto
    assert "no computable" in texto


def test_lineas_del_contraste_sin_discordancias_dicen_no_aplicable():
    from evaluation.deterministic_measurement import (
        contraste_det_gem_en_s,
        lineas_contraste_mcnemar,
    )

    c = contraste_det_gem_en_s([_obs("a", SIS, 0.9)], {"a": _gem(SIS)}, TAU)
    texto = "\n".join(lineas_contraste_mcnemar(c))

    assert "no aplicable" in texto
    assert "p primario" not in texto


def test_el_reporte_comparativo_imprime_la_linea_cuando_recibe_el_contraste():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    texto = _reporte_comparativo_de_juguete(contraste=contraste_det_gem_en_s(*_escenario(), TAU))

    assert "## Contraste pareado de McNemar entre etapas sobre S (c-131)" in texto
    assert "pares con prediccion de ambas etapas: 3" in texto


def test_el_reporte_comparativo_sin_contraste_declara_no_computable():
    texto = _reporte_comparativo_de_juguete(contraste=None)

    assert "## Contraste pareado de McNemar entre etapas sobre S (c-131)" in texto
    assert "no computable" in texto


def _reporte_comparativo_de_juguete(contraste):
    from evaluation.deterministic_measurement import (
        calibrar_comparativo_out_of_fold,
        curva_comparativa,
        curva_precision_cobertura,
        elegir_umbral,
        formatear_reporte_comparativo,
        metricas_deterministas,
        resumen_vocabulario,
    )

    observaciones, cache = _escenario()
    gem_map = {k: (p.sector_predicho if p.etapa == "gemini" else None) for k, p in cache.items()}
    legacy = curva_precision_cobertura(observaciones)
    return formatear_reporte_comparativo(
        resumen=resumen_vocabulario(observaciones),
        metricas_det=metricas_deterministas(observaciones),
        curva_legacy=legacy,
        umbral_legacy=elegir_umbral(legacy, 0.90),
        piso_precision=0.90,
        curva_comp=curva_comparativa(observaciones, gem_map),
        punto=None,
        oof=calibrar_comparativo_out_of_fold(observaciones, gem_map, n_folds=2),
        umbral_settings=TAU,
        hibrido=None,
        contraste=contraste,
    )


# ---------------------------------------------------------------------------
# 7.6 TRIANGULATE: la cache OFICIAL no sirve para el contraste (S no llamo a Gemini)
# ---------------------------------------------------------------------------
def test_contraste_para_cache_usa_solo_la_cache_force_escalate(tmp_path):
    from evaluation.deterministic_measurement import contraste_para_cache

    observaciones, cache = _escenario()

    calibracion = contraste_para_cache(
        observaciones, cache, TAU, tmp_path / "predicciones_calibracion.json"
    )
    oficial = contraste_para_cache(observaciones, cache, TAU, tmp_path / "predicciones.json")
    sin_tau = contraste_para_cache(
        observaciones, cache, None, tmp_path / "predicciones_calibracion.json"
    )

    assert calibracion is not None and calibracion.pares == 3
    assert oficial is None  # en hybrid-v3 los casos de S no llamaron a Gemini
    assert sin_tau is None  # sin punto de operacion no hay S
