"""Pruebas de las metricas puras de calibracion y discriminacion del gate (c-214, tareas 1.x)."""

from __future__ import annotations

import pytest

from evaluation.calibracion_gate import (
    auroc,
    brier,
    ece,
    ic_bootstrap_metrica,
    sobreconfianza,
)


# --- AUROC ------------------------------------------------------------------------------
def test_auroc_orden_perfecto_es_uno():
    assert auroc([0.9, 0.95, 0.2, 0.1], [True, True, False, False]) == 1.0


def test_auroc_orden_invertido_es_cero():
    assert auroc([0.1, 0.2, 0.9], [True, True, False]) == 0.0


def test_auroc_senal_constante_es_medio():
    assert auroc([0.85] * 6, [True, False, True, False, True, True]) == 0.5


def test_auroc_empates_cuentan_medio():
    # aciertos: 0.9, 0.5 ; errores: 0.5, 0.1 -> pares: (0.9>0.5)=1, (0.9>0.1)=1,
    # (0.5=0.5)=0.5, (0.5>0.1)=1 -> 3.5/4
    assert auroc([0.9, 0.5, 0.5, 0.1], [True, True, False, False]) == pytest.approx(0.875)


def test_auroc_sin_una_clase_es_none():
    assert auroc([0.9, 0.8], [True, True]) is None
    assert auroc([0.9, 0.8], [False, False]) is None


# --- ECE / Brier / sobreconfianza -------------------------------------------------------
def test_ece_senal_calibrada_es_cero():
    # banda [0.9, 1.0]: confianza media 0.9, 9 aciertos de 10 -> exactitud 0.9
    confianzas = [0.9] * 10
    aciertos = [True] * 9 + [False]
    assert ece(confianzas, aciertos) == pytest.approx(0.0)


def test_ece_pondera_por_banda_con_diez_bandas_de_igual_ancho():
    # banda 0.8-0.9: confianza 0.85 x4, exactitud 0.5 -> |0.85-0.5| = 0.35, peso 4/5
    # banda 0.9-1.0 (cerrada en 1.0): confianza 1.0 x1, acierto -> 0
    confianzas = [0.85, 0.85, 0.85, 0.85, 1.0]
    aciertos = [True, True, False, False, True]
    assert ece(confianzas, aciertos) == pytest.approx(0.35 * 4 / 5)


def test_ece_confianza_uno_cae_en_la_ultima_banda():
    assert ece([1.0, 1.0], [True, False]) == pytest.approx(0.5)


def test_brier_valor_conocido():
    assert brier([1.0, 0.0], [True, False]) == pytest.approx(0.0)
    assert brier([0.8, 0.6], [True, False]) == pytest.approx((0.2**2 + 0.6**2) / 2)


def test_sobreconfianza_media():
    assert sobreconfianza([0.9, 0.9, 0.9, 0.9], [True, True, False, False]) == pytest.approx(0.4)
    assert sobreconfianza([0.5, 0.5], [True, True]) == pytest.approx(-0.5)


def test_metricas_rechazan_vacio_longitudes_distintas_y_fuera_de_rango():
    for funcion in (ece, brier, sobreconfianza, auroc):
        with pytest.raises(ValueError):
            funcion([], [])
        with pytest.raises(ValueError):
            funcion([0.5], [True, False])
        with pytest.raises(ValueError):
            funcion([1.2, 0.5], [True, False])
        with pytest.raises(ValueError):
            funcion([-0.1, 0.5], [True, False])


# --- IC bootstrap -----------------------------------------------------------------------
def test_ic_bootstrap_dos_corridas_dan_lo_mismo_y_contiene_el_valor():
    confianzas = [0.95, 0.9, 0.85, 0.85, 0.98, 0.9, 0.95, 0.85] * 3
    aciertos = [True, True, False, True, True, False, True, False] * 3
    a = ic_bootstrap_metrica(confianzas, aciertos, brier)
    b = ic_bootstrap_metrica(confianzas, aciertos, brier)
    assert a == b
    assert a["valor"] == pytest.approx(brier(confianzas, aciertos))
    inferior, superior = a["ic"]
    assert inferior <= a["valor"] <= superior
    assert superior - inferior > 0.0


def test_ic_bootstrap_distinta_semilla_cambia_el_intervalo():
    confianzas = [0.95, 0.9, 0.85, 0.85, 0.98, 0.9, 0.95, 0.85] * 3
    aciertos = [True, True, False, True, True, False, True, False] * 3
    a = ic_bootstrap_metrica(confianzas, aciertos, ece, semilla=1)
    b = ic_bootstrap_metrica(confianzas, aciertos, ece, semilla=2)
    assert a["ic"] != b["ic"]


def test_ic_bootstrap_auroc_omite_remuestras_sin_ambas_clases():
    confianzas = [0.9, 0.8, 0.3]
    aciertos = [True, True, False]
    r = ic_bootstrap_metrica(confianzas, aciertos, auroc, remuestreos=200)
    assert r["valor"] == 1.0
    assert r["remuestras_validas"] <= 200
    assert r["ic"] is not None


def test_ic_bootstrap_con_metrica_indefinida_devuelve_none():
    r = ic_bootstrap_metrica([0.9, 0.8], [True, True], auroc)
    assert r["valor"] is None and r["ic"] is None


# ======================================================================================
# Grupo 2: barrido, regla de seleccion, evaluacion fuera de muestra, isotonica
# ======================================================================================
import math  # noqa: E402

from evaluation.calibracion_gate import (  # noqa: E402
    aplicar_isotonica,
    ajustar_isotonica,
    barrido_umbral,
    evaluar_fuera_de_muestra_gate,
    seleccionar_umbral,
)

INF = math.inf
SENALES = [0.85, 0.85, 0.85, 0.90, 0.90, 0.95, 0.95, 0.95, 0.95, 0.98]
ACIERTOS = [False, False, True, False, True, True, True, True, False, True]


def _fila(barrido, t):
    return next(f for f in barrido if f["umbral"] == t)


def test_barrido_umbral_vigente_sin_derivaciones():
    b = barrido_umbral(SENALES, ACIERTOS, [0.70, INF], n_total_corpus=20)
    f = _fila(b, 0.70)
    assert (f["aceptados"], f["derivados"]) == (10, 0)
    assert f["cobertura"] == 1.0
    assert f["errores_atrapados"] == 0
    assert f["carga_revision"] == 0.0
    assert f["exactitud_selectiva"] == pytest.approx(6 / 10)
    assert f["exactitud_derivados"] is None


def test_barrido_derivar_todo_tiene_cobertura_cero_y_carga_de_los_escalados():
    f = _fila(barrido_umbral(SENALES, ACIERTOS, [INF], n_total_corpus=20), INF)
    assert f["cobertura"] == 0.0
    assert f["aceptados"] == 0 and f["derivados"] == 10
    assert f["carga_revision"] == pytest.approx(10 / 20)
    assert f["errores_atrapados"] == 4
    assert f["exactitud_selectiva"] is None and f["ic_wilson"] is None


def test_barrido_umbral_intermedio_cuenta_aceptados_derivados_y_wilson():
    f = _fila(barrido_umbral(SENALES, ACIERTOS, [0.91], n_total_corpus=20), 0.91)
    # aceptados: 0.95 x4 y 0.98 -> 5 casos, aciertos 3+1 = 4
    assert (f["aceptados"], f["aciertos_aceptados"]) == (5, 4)
    assert f["exactitud_selectiva"] == pytest.approx(0.8)
    assert f["derivados"] == 5 and f["errores_atrapados"] == 3
    assert f["exactitud_derivados"] == pytest.approx(2 / 5)
    assert f["ic_wilson"][0] < 0.8 < f["ic_wilson"][1]
    assert f["carga_revision"] == pytest.approx(5 / 20)


def test_barrido_rechaza_senales_y_aciertos_de_distinta_longitud():
    with pytest.raises(ValueError):
        barrido_umbral([0.9], [True, False], [0.5], n_total_corpus=2)


def _barrido_sintetico():
    # t=0.5: 20 aceptados, exactitud 0.70 ; t=0.8: 12 aceptados, 0.90 ; t=0.9: 4 aceptados, 1.0
    senales = [0.5] * 8 + [0.8] * 8 + [0.9] * 4
    aciertos = [True] * 2 + [False] * 6 + [True] * 7 + [False] + [True] * 4
    return barrido_umbral(senales, aciertos, [0.5, 0.8, 0.9, INF], n_total_corpus=20)


def test_seleccionar_elige_el_menor_umbral_que_cumple_piso_y_minimo():
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.85, min_aceptados=10) == 0.8


def test_seleccionar_exige_el_minimo_de_aceptados():
    # con t=0.9 la exactitud es 1.0 pero solo hay 4 aceptados; con minimo 4 gana t=0.8 por menor
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.99, min_aceptados=10) is None
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.99, min_aceptados=4) == 0.9


def test_seleccionar_ninguno_si_nadie_cumple_y_nunca_elige_derivar_todo():
    assert seleccionar_umbral(_barrido_sintetico(), piso=0.999, min_aceptados=1) == 0.9
    solo_inf = barrido_umbral([0.9, 0.9], [True, True], [INF], n_total_corpus=2)
    assert seleccionar_umbral(solo_inf, piso=0.5, min_aceptados=1) is None


def test_evaluar_confirmado():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 11 + [False] + [True, False, False, False]
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "confirmado"
    assert r["exactitud_selectiva"] == pytest.approx(11 / 12)
    assert r["exactitud_derivados"] == pytest.approx(1 / 4)


def test_evaluar_no_confirmado_si_la_exactitud_selectiva_no_alcanza_el_piso():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 8 + [False] * 4 + [False] * 4
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "no confirmado"


def test_evaluar_no_confirmado_si_los_derivados_no_son_peores():
    senales = [0.9] * 12 + [0.5] * 4
    aciertos = [True] * 11 + [False] + [True] * 4  # derivados 100 % > aceptados 91,7 %
    r = evaluar_fuera_de_muestra_gate(0.8, senales, aciertos, piso=0.85, n_total_corpus=20)
    assert r["veredicto"] == "no confirmado"


def test_evaluar_no_estimable_con_pocos_aceptados_o_sin_derivados():
    pocos = evaluar_fuera_de_muestra_gate(
        0.8, [0.9] * 9 + [0.5] * 5, [True] * 14, piso=0.85, n_total_corpus=20
    )
    assert pocos["veredicto"] == "no estimable"
    sin_derivados = evaluar_fuera_de_muestra_gate(
        0.8, [0.9] * 12, [True] * 12, piso=0.85, n_total_corpus=20
    )
    assert sin_derivados["veredicto"] == "no estimable"


def test_evaluar_sin_umbral_seleccionado_solo_describe():
    r = evaluar_fuera_de_muestra_gate(None, [0.9, 0.5], [True, False], piso=0.85, n_total_corpus=2)
    assert r["veredicto"] == "sin umbral seleccionado"
    assert r["umbral"] is None


def test_evaluar_no_acepta_reelegir_el_umbral_con_datos_fuera_de_muestra():
    with pytest.raises(TypeError):
        evaluar_fuera_de_muestra_gate(  # type: ignore[call-arg]
            0.8, [0.9], [True], piso=0.85, n_total_corpus=1, umbrales=[0.5, 0.9]
        )


def test_isotonica_es_monotona_y_corrige_el_nivel():
    # confianza 0.9 con exactitud 0.5 en el ajuste -> la recalibrada vale 0.5 en 0.9
    modelo = ajustar_isotonica([0.8, 0.8, 0.9, 0.9], [False, False, True, False])
    salidas = aplicar_isotonica(modelo, [0.5, 0.8, 0.85, 0.9, 0.99])
    assert all(a <= b for a, b in zip(salidas, salidas[1:]))
    # escalon: por debajo del minimo ajustado vale el primer bloque; luego el bloque de x <= entrada
    assert salidas == [pytest.approx(0.0), pytest.approx(0.0), pytest.approx(0.0),
                       pytest.approx(0.5), pytest.approx(0.5)]


def test_isotonica_pava_agrupa_violaciones_con_pesos():
    # x=1: 1 de 1 ; x=2: 0 de 3 -> violacion; bloque unico con media 1/4 para ambos
    modelo = ajustar_isotonica([0.1, 0.2, 0.2, 0.2], [True, False, False, False])
    assert aplicar_isotonica(modelo, [0.1, 0.2]) == [pytest.approx(0.25), pytest.approx(0.25)]


def test_isotonica_no_invierte_el_orden_y_conserva_el_auroc_si_no_hay_agrupacion():
    fit_s = [0.2, 0.4, 0.6, 0.8]
    fit_a = [False, False, True, True]
    modelo = ajustar_isotonica(fit_s, fit_a)
    senales = [0.2, 0.4, 0.6, 0.8, 0.8, 0.4]
    aciertos = [False, False, True, True, False, True]
    recal = aplicar_isotonica(modelo, senales)
    assert auroc(recal, aciertos) == pytest.approx(auroc(senales, aciertos))


def test_isotonica_rechaza_ajuste_vacio():
    with pytest.raises(ValueError):
        ajustar_isotonica([], [])


# ======================================================================================
# Grupo 3: senales de las reglas recomputadas (costo cero)
# ======================================================================================
import json  # noqa: E402
import pathlib  # noqa: E402
from types import SimpleNamespace  # noqa: E402

from evaluation.calibracion_gate import (  # noqa: E402
    ACUERDO,
    DESACUERDO,
    NO_APLICA,
    SIN_PREDICCION_REGLAS,
    cargar_clasificador_deterministico,
    recomputar_senales_reglas,
    verificar_reproduccion_cortocircuito,
)

RAIZ = pathlib.Path(__file__).resolve().parents[2]


class ReglasSimuladas:
    """Clasificador determinista simulado: resultado fijado por descripcion."""

    def __init__(self, tabla):
        self.tabla = tabla

    async def classify(self, descripcion):
        sector, score, sin_pred, ambiguo = self.tabla[descripcion]
        return SimpleNamespace(
            sector_predicho=sector,
            score_correctitud=score,
            sin_prediccion=sin_pred,
            ambiguo=ambiguo,
        )


def _pred(caso_id, descripcion, etapa, sector):
    return {"caso_id": caso_id, "descripcion": descripcion, "etapa": etapa, "sector_predicho": sector}


def test_recomputar_clasifica_acuerdo_desacuerdo_sin_prediccion_y_no_aplica():
    reglas = ReglasSimuladas(
        {
            "a": ("Sistemas", 0.30, False, False),  # escalado; Gemini coincide
            "b": ("Sistemas", 0.20, False, False),  # escalado; Gemini discrepa
            "c": (None, 0.0, True, False),  # escalado; sin senal
            "d": (None, 0.0, False, True),  # escalado; empate (open question: sin prediccion)
            "e": ("Bases de Datos", 0.80, False, False),  # cortocircuita
        }
    )
    preds = [
        _pred("1", "a", "gemini", "Sistemas"),
        _pred("2", "b", "gemini", "Bases de Datos"),
        _pred("3", "c", "gemini", "Sistemas"),
        _pred("4", "d", "gemini", "Sistemas"),
        _pred("5", "e", "deterministic", "Bases de Datos"),
    ]
    filas = recomputar_senales_reglas(preds, reglas, tau=0.5166)
    assert [f["acuerdo_con_gemini"] for f in filas] == [
        ACUERDO, DESACUERDO, SIN_PREDICCION_REGLAS, SIN_PREDICCION_REGLAS, NO_APLICA,
    ]
    assert [f["cortocircuita"] for f in filas] == [False, False, False, False, True]
    assert [f["sector_reglas"] for f in filas] == ["Sistemas", "Sistemas", None, None, "Bases de Datos"]
    assert filas[0]["score_correctitud"] == pytest.approx(0.30)
    assert filas[4]["caso_id"] == "5"


def test_recomputar_el_empate_con_score_alto_no_cortocircuita():
    reglas = ReglasSimuladas({"x": (None, 0.9, False, True), "y": ("Sistemas", 0.5166, False, False)})
    filas = recomputar_senales_reglas(
        [_pred("1", "x", "gemini", "Sistemas"), _pred("2", "y", "deterministic", "Sistemas")],
        reglas,
        tau=0.5166,
    )
    assert filas[0]["cortocircuita"] is False  # ambiguo: escala aunque el score sea alto
    assert filas[1]["cortocircuita"] is True  # score == tau cortocircuita (>=)


def test_verificar_reproduccion_acepta_si_coincide_y_detiene_si_hay_deriva():
    reglas = ReglasSimuladas({"a": ("Sistemas", 0.3, False, False), "e": ("Sistemas", 0.8, False, False)})
    bien = [_pred("1", "a", "gemini", "Bases de Datos"), _pred("2", "e", "deterministic", "Sistemas")]
    senales = recomputar_senales_reglas(bien, reglas, tau=0.5166)
    assert verificar_reproduccion_cortocircuito(senales, bien) == {"cortocircuitados": 1, "total": 2}

    otra_etapa = [_pred("1", "a", "deterministic", "Sistemas"), _pred("2", "e", "deterministic", "Sistemas")]
    with pytest.raises(ValueError, match="deriva"):
        verificar_reproduccion_cortocircuito(
            recomputar_senales_reglas(otra_etapa, reglas, tau=0.5166), otra_etapa
        )
    otro_sector = [_pred("1", "a", "gemini", "Sistemas"), _pred("2", "e", "deterministic", "Bases de Datos")]
    with pytest.raises(ValueError, match="deriva"):
        verificar_reproduccion_cortocircuito(
            recomputar_senales_reglas(otro_sector, reglas, tau=0.5166), otro_sector
        )


@pytest.fixture
def entorno_backend_c214(monkeypatch):
    from evaluation.calibracion_gate import ENTORNO_OFFLINE_C214, asegurar_backend_en_path

    asegurar_backend_en_path()
    pytest.importorskip("app.config.settings")
    for clave, valor in ENTORNO_OFFLINE_C214.items():
        monkeypatch.setenv(clave, valor)
    from app.config.settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.mark.parametrize(
    "ruta, total, cortos",
    [
        ("evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json", 200, 131),
        ("evaluation/data/campana/predicciones_independiente.json", 103, 69),
    ],
)
def test_el_recomputo_reproduce_los_cortocircuitados_de_las_caches(
    entorno_backend_c214, ruta, total, cortos
):
    predicciones = json.loads((RAIZ / ruta).read_text(encoding="utf-8"))["predictions"]
    from app.config.settings import get_settings

    tau = get_settings().deterministic_score_threshold
    assert tau == pytest.approx(0.5166)
    senales = recomputar_senales_reglas(predicciones, cargar_clasificador_deterministico(), tau=tau)
    assert verificar_reproduccion_cortocircuito(senales, predicciones) == {
        "cortocircuitados": cortos,
        "total": total,
    }
