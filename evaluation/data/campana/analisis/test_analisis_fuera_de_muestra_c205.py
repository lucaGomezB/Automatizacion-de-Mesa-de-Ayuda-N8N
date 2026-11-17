"""Pruebas del analisis ampliado fuera de muestra (c-205).

Las cifras ancla provienen de la Seccion 3.19 del memo canonico (c-191): n efectivo 103,
exactitud estricta 87/103, laxa 90/103, 47 excluidos de 150.
"""
# Nota (c-240): se retiraron de este modulo las pruebas que leian los archivos
# `evaluation/data/campana/corpus_independiente.json` y/o `corpus_independiente_arbitrado.json`,
# eliminados del repositorio publico por la decision de los autores (c-240, OOS-027). Las pruebas
# restantes no dependen de esos archivos. El nuevo estado se verifica en
# `evaluation/tests/test_retiro_corpus_independiente_c240.py`.

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_fuera_de_muestra_c205 as c205  # noqa: E402

SECTORES = [
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
]


@pytest.fixture(scope="module")
def documento() -> dict:
    return c205.construir_documento()


def test_macro_f1_incluye_clase_de_soporte_cero():
    # Cuatro clases con soporte; "Sistemas" sin soporte ni predicciones -> F1 = 0.0
    reales = SECTORES[:4] * 2
    predichos = list(reales)
    m = c205.metricas_clasificacion(reales, predichos)
    assert m["por_clase"]["Sistemas"]["soporte"] == 0
    assert m["por_clase"]["Sistemas"]["f1"] == 0.0
    # cuatro F1 = 1.0 y una = 0.0 -> media sobre CINCO clases = 0.8 (no 1.0)
    assert m["macro_f1"] == pytest.approx(0.8)
    assert m["balanced_accuracy"]["valor"] == pytest.approx(0.8)


def test_balanced_accuracy_difiere_de_exactitud_con_desbalance():
    reales = ["Sistemas"] * 8 + ["Bases de Datos"] * 2
    predichos = ["Sistemas"] * 8 + ["Sistemas"] * 2
    m = c205.metricas_clasificacion(reales, predichos)
    assert m["balanced_accuracy"]["exactitud_estricta"] == pytest.approx(0.8)
    # sensibilidades: Sistemas 1.0, Bases 0.0, resto 0.0 -> media 0.2
    assert m["balanced_accuracy"]["valor"] == pytest.approx(0.2)


@pytest.mark.parametrize(
    "aciertos,n,esperado",
    [(50, 100, 0.0962), (87, 103, 0.0698)],
)
def test_semi_ancho_wilson(aciertos, n, esperado):
    assert c205.semi_ancho_wilson(aciertos, n) == pytest.approx(esperado, abs=5e-4)


def test_escenarios_exclusion_peor_mejor_y_regla():
    e = c205.escenarios_exclusion(87, 103, 47)
    assert e["peor_caso"]["exactitud"] == pytest.approx(87 / 150)
    assert e["mejor_caso"]["exactitud"] == pytest.approx(134 / 150)
    assert e["regla_decision"]["peor_caso_sostiene_umbral"] is False
    assert e["peor_caso"]["exactitud"] < e["cota"]["exactitud"] < e["mejor_caso"]["exactitud"]
    # 0,85 * 150 = 127,5 -> 128 aciertos totales -> 41 entre los excluidos
    assert e["aciertos_minimos_excluidos_para_umbral"]["minimo"] == 41
    # con un resultado perfecto el peor caso si sostiene el umbral
    assert c205.escenarios_exclusion(100, 100, 10)["regla_decision"][
        "peor_caso_sostiene_umbral"
    ] is True


def test_balance_neto_reproduce_formula_de_la_seccion_3_11():
    # con e_aut = 53/200 el memo da B(15 %, 10 min) = -18,5 h y a* = 77,7 %
    b = c205.balance_neto(53, 200)
    fila = next(e for e in b["escenarios"] if e["e_man"] == "0.15" and e["costo_min"] == 10)
    assert fila["balance_h"] == "-18.5"
    assert fila["a_estrella_pct"] == "77.7"
