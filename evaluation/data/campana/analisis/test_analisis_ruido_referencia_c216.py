"""Pruebas de las funciones puras del analisis de ruido de referencia (c-216).

Casos sinteticos, sin I/O ni red. Cubren kernel fila-estocastico, calibracion de
lambda, cotas distribution-free, rango de tres vias y verificacion de anclajes.
"""

from __future__ import annotations

import math
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_ruido_referencia_c216 as c216  # noqa: E402

CLASES = c216.CLASES
X, Y, Z, W, V = CLASES


def _referencia_uniforme(n_por_clase=4):
    """Referencia con las cinco clases y `n_por_clase` casos por clase."""
    referencia = {}
    for indice, clase in enumerate(CLASES):
        for k in range(n_por_clase):
            referencia[f"C{indice}{k}"] = clase
    return referencia


def _etiquetas_de(referencia, etiquetadores=("E3", "E4")):
    """Etiquetas perfectas: cada etiquetador repite la referencia en todos los casos."""
    return {
        caso: {etiquetador: clase for etiquetador in etiquetadores}
        for caso, clase in referencia.items()
    }


# ---------------------------------------------------------------------------
# Kernel fila-estocastico
# ---------------------------------------------------------------------------
def test_kernel_con_etiquetas_perfectas_es_una_matriz_identidad():
    referencia = _referencia_uniforme(3)
    kernel = c216.construir_kernel(referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0)
    for clase in CLASES:
        assert kernel["probabilidades"][clase][clase] == pytest.approx(1.0)
        for otra in CLASES:
            if otra != clase:
                assert kernel["probabilidades"][clase][otra] == pytest.approx(0.0)
        assert sum(kernel["probabilidades"][clase].values()) == pytest.approx(1.0)


def test_kernel_suavizado_laplace_mantiene_filas_estocasticas_con_soporte_chico():
    referencia = {f"c{k}": X for k in range(2)}
    etiquetas = {
        "c0": {"E3": X, "E4": X},
        "c1": {"E3": Y, "E4": X},
    }
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.5)
    for clase in CLASES:
        assert sum(kernel["probabilidades"][clase].values()) == pytest.approx(1.0)
    assert kernel["soporte"][X] == 4
    assert kernel["soporte"][Y] == 0
    assert kernel["conteos"][X][X] == 3
    assert kernel["conteos"][X][Y] == 1
    assert kernel["probabilidades"][Y][Y] > 0.0


def test_kernel_pondera_cada_etiquetador_por_los_casos_que_etiqueto():
    referencia = {"a": X, "b": X, "c": Y}
    etiquetas = {
        "a": {"E3": X, "E4": X, "E5": X},
        "b": {"E3": X, "E4": Y},
        "c": {"E3": Y, "E4": Y},
    }
    kernel = c216.construir_kernel(referencia, etiquetas, [X, Y], suavizado=0.0)
    assert kernel["conteos"][X][X] == 4
    assert kernel["conteos"][X][Y] == 1
    assert kernel["conteos"][Y][Y] == 2
    assert kernel["soporte"][X] == 5
    assert kernel["soporte"][Y] == 2


def test_kernel_etiqueta_fuera_de_las_clases_aborta():
    referencia = {"a": X}
    etiquetas = {"a": {"E3": "No Existe"}}
    with pytest.raises(ValueError, match="No Existe"):
        c216.construir_kernel(referencia, etiquetas, CLASES)


# ---------------------------------------------------------------------------
# Kappa esperado y calibracion de lambda
# ---------------------------------------------------------------------------
def test_kappa_esperado_perfecto_es_uno():
    referencia = _referencia_uniforme(3)
    kernel = c216.construir_kernel(referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    mezcla = c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES)
    assert c216.kappa_esperado(mezcla, marginal, CLASES) == pytest.approx(1.0)


def test_kappa_esperado_nulo_en_lambda_uno_es_cero():
    referencia = _referencia_uniforme(3)
    kernel = c216.construir_kernel(referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    mezcla = c216.mezclar_kernel(kernel["probabilidades"], marginal, 1.0, CLASES)
    assert c216.kappa_esperado(mezcla, marginal, CLASES) == pytest.approx(0.0, abs=1e-12)


def test_kappa_esperado_decrece_con_lambda():
    referencia = _referencia_uniforme(20)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        # Cada fila conserva 80 % de acierto y reparte el resto entre las otras clases.
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1 + (k % 4)) % len(CLASES)]
        etiquetas[caso] = {"E3": clase, "E4": clase, "E5": alterna}
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    valores = [
        c216.kappa_esperado(c216.mezclar_kernel(kernel["probabilidades"], marginal, lam, CLASES), marginal, CLASES)
        for lam in (0.0, 0.25, 0.5, 0.75, 1.0)
    ]
    assert valores[0] > valores[1] > valores[2] > valores[3] > valores[4]
    assert valores[4] == pytest.approx(0.0, abs=1e-12)


def test_calibrar_lambda_reproduce_un_kappa_intermedio_dentro_de_la_tolerancia():
    referencia = _referencia_uniforme(20)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1 + (k % 4)) % len(CLASES)]
        etiquetas[caso] = {"E3": clase, "E4": clase, "E5": alterna}
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    kappa_cero = c216.kappa_esperado(
        c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES), marginal, CLASES
    )
    objetivo = kappa_cero / 2
    calibracion = c216.calibrar_lambda(kernel["probabilidades"], marginal, CLASES, objetivo, 0.005)
    assert 0.0 < calibracion["lambda"] < 1.0
    assert calibracion["kappa"] == pytest.approx(objetivo, abs=0.005)
    assert abs(calibracion["kappa"] - objetivo) <= 0.005


def test_calibrar_lambda_con_objetivo_igual_al_kappa_sin_ruido_devuelve_cero():
    referencia = _referencia_uniforme(10)
    kernel = c216.construir_kernel(referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    calibracion = c216.calibrar_lambda(kernel["probabilidades"], marginal, CLASES, 1.0, 0.005)
    assert calibracion["lambda"] == pytest.approx(0.0, abs=1e-9)
    assert calibracion["kappa"] == pytest.approx(1.0)


def test_calibrar_lambda_sin_solucion_aborta():
    referencia = _referencia_uniforme(20)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1 + (k % 4)) % len(CLASES)]
        etiquetas[caso] = {"E3": clase, "E4": clase, "E5": alterna}
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    kappa_cero = c216.kappa_esperado(
        c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES), marginal, CLASES
    )
    with pytest.raises(ValueError, match="no hay"):
        c216.calibrar_lambda(
            kernel["probabilidades"], marginal, CLASES, kappa_cero + 0.1, 0.005
        )


# ---------------------------------------------------------------------------
# Cotas distribution-free
# ---------------------------------------------------------------------------
def test_cotas_distribution_free_con_delta_conocido():
    cotas = c216.cotas_distribution_free(80, 100, 0.20)
    assert cotas["m"] == 20
    assert cotas["inferior"] == pytest.approx(0.60)
    assert cotas["superior"] == pytest.approx(1.00)


def test_cotas_distribution_free_sin_error_de_referencia_son_el_valor_observado():
    cotas = c216.cotas_distribution_free(142, 206, 0.0)
    assert cotas["m"] == 0
    assert cotas["inferior"] == pytest.approx(142 / 206)
    assert cotas["superior"] == pytest.approx(142 / 206)


def test_cotas_distribution_free_se_recortan_a_cero_y_uno():
    cotas = c216.cotas_distribution_free(1, 10, 1.0)
    assert cotas["inferior"] == pytest.approx(0.0)
    assert cotas["superior"] == pytest.approx(1.0)


def test_cotas_contienen_la_exactitud_observada():
    cotas = c216.cotas_distribution_free(142, 206, 0.37)
    assert cotas["inferior"] <= 142 / 206 <= cotas["superior"]


# ---------------------------------------------------------------------------
# Rango de tres vias
# ---------------------------------------------------------------------------
def test_rango_tres_vias_con_tres_etiquetas_distintas():
    referencia = {"A": X, "B": Y}
    predicciones = {"A": X, "B": Y}
    etiquetas = {
        "A": {"E3": Z, "E4": W, "E5": X},
        "B": {"E3": Y, "E4": Y, "E5": Y},
    }
    resultado = c216.rango_tres_vias(referencia, predicciones, etiquetas, ["A"])
    caso = resultado["casos"][0]
    assert caso["caso_id"] == "A"
    assert caso["asignaciones"] == {"E3": Z, "E4": W, "E5": X}
    assert caso["aciertos_por_asignacion"]["E5"] == 2
    assert caso["aciertos_por_asignacion"]["E3"] == 1
    assert resultado["aciertos_min"] == 1
    assert resultado["aciertos_max"] == 2
    assert resultado["exactitud_min"] == pytest.approx(1 / 2)
    assert resultado["exactitud_max"] == pytest.approx(2 / 2)


def test_rango_tres_vias_no_elige_una_etiqueta_verdadera():
    referencia = {"A": X}
    predicciones = {"A": X}
    etiquetas = {"A": {"E3": Y, "E4": W, "E5": X}}
    resultado = c216.rango_tres_vias(referencia, predicciones, etiquetas, ["A"])
    caso = resultado["casos"][0]
    assert set(caso["asignaciones"]) == {"E3", "E4", "E5"}
    assert caso["aciertos_por_asignacion"] == {"E3": 0, "E4": 0, "E5": 1}
    assert resultado["aciertos_max"] - resultado["aciertos_min"] == 1
    assert resultado["exactitud_max"] - resultado["exactitud_min"] == pytest.approx(1.0)


def test_rango_tres_vias_cada_caso_mueve_a_lo_sumo_un_caso():
    referencia = {f"C{k}": X for k in range(20)}
    predicciones = {caso: X for caso in referencia}
    etiquetas = {
        caso: {"E3": Y, "E4": Z, "E5": X}
        for caso in referencia
    }
    resultado = c216.rango_tres_vias(referencia, predicciones, etiquetas, ["C0", "C1"])
    assert resultado["aciertos_min"] == 18
    assert resultado["aciertos_max"] == 20
    assert resultado["aciertos_max"] - resultado["aciertos_min"] == 2
    assert resultado["exactitud_min"] == pytest.approx(18 / 20)


# ---------------------------------------------------------------------------
# Anclajes
# ---------------------------------------------------------------------------
def test_verificar_anclajes_acepta_los_valores_canonicos():
    c216.verificar_anclajes(206, 142, 0.7024)


def test_verificar_anclajes_aborta_si_los_aciertos_no_coinciden():
    with pytest.raises(c216.AnclaNoReproducida, match="142"):
        c216.verificar_anclajes(206, 141, 0.7024)


def test_verificar_anclajes_aborta_si_la_macro_f1_no_coincide():
    with pytest.raises(c216.AnclaNoReproducida, match="macro-F1"):
        c216.verificar_anclajes(206, 142, 0.7000)

# ---------------------------------------------------------------------------
# Triangulacion: casos adicionales (tarea 2.3)
# ---------------------------------------------------------------------------
def test_calibrar_lambda_reproduce_el_objetivo_canonico_0_6055():
    referencia = _referencia_uniforme(40)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1) % len(CLASES)]
        etiquetas[caso] = {
            "E3": clase,
            "E4": clase,
            "E5": alterna if k % 5 == 0 else clase,
        }
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.5)
    marginal = c216.marginal_empirica(referencia, CLASES)
    kappa_cero = c216.kappa_esperado(
        c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES), marginal, CLASES
    )
    assert kappa_cero > 0.6055
    calibracion = c216.calibrar_lambda(
        kernel["probabilidades"], marginal, CLASES, 0.6055, 0.005
    )
    assert abs(calibracion["kappa"] - 0.6055) <= 0.005
    assert 0.0 < calibracion["lambda"] < 1.0
    assert 0.0 <= calibracion["p_o"] <= 1.0
    assert calibracion["p_o"] >= calibracion["kappa"]


def test_calibrar_lambda_con_una_fila_de_soporte_uno():
    referencia = {f"C{indice}": clase for indice, clase in enumerate(CLASES)}
    etiquetas = {caso: {"E3": clase, "E4": clase} for caso, clase in referencia.items()}
    # La fila de Bases de Datos conserva un unico caso y una unica etiqueta no perfecta.
    etiquetas["C3"] = {"E3": CLASES[0], "E4": CLASES[1]}
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.5)
    assert kernel["soporte"][CLASES[3]] == 2
    for clase in CLASES:
        assert sum(kernel["probabilidades"][clase].values()) == pytest.approx(1.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    kappa_cero = c216.kappa_esperado(
        c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES), marginal, CLASES
    )
    objetivo = kappa_cero / 2.0
    calibracion = c216.calibrar_lambda(
        kernel["probabilidades"], marginal, CLASES, objetivo, 0.005
    )
    assert abs(calibracion["kappa"] - objetivo) <= 0.005
    assert 0.0 < calibracion["lambda"] < 1.0


def test_probabilidad_media_alternativa_extremos():
    referencia = _referencia_uniforme(5)
    kernel = c216.construir_kernel(referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0)
    marginal = c216.marginal_empirica(referencia, CLASES)
    sin_ruido = c216.mezclar_kernel(kernel["probabilidades"], marginal, 0.0, CLASES)
    independiente = c216.mezclar_kernel(kernel["probabilidades"], marginal, 1.0, CLASES)
    assert c216.probabilidad_media_alternativa(sin_ruido, marginal, CLASES) == pytest.approx(0.0)
    assert c216.probabilidad_media_alternativa(
        independiente, marginal, CLASES
    ) == pytest.approx(1.0 - sum(p ** 2 for p in marginal.values()))


def test_cotas_con_delta_de_la_mezcla_contienen_la_exactitud_observada():
    referencia = _referencia_uniforme(40)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1) % len(CLASES)]
        etiquetas[caso] = {
            "E3": clase,
            "E4": clase,
            "E5": alterna if k % 5 == 0 else clase,
        }
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.5)
    marginal = c216.marginal_empirica(referencia, CLASES)
    calibracion = c216.calibrar_lambda(
        kernel["probabilidades"], marginal, CLASES, 0.6055, 0.005
    )
    mezcla = c216.mezclar_kernel(
        kernel["probabilidades"], marginal, calibracion["lambda"], CLASES
    )
    media = c216.probabilidad_media_alternativa(mezcla, marginal, CLASES)
    _, delta = c216.intervalo_wilson(
        media * len(referencia), len(referencia), c216.NIVEL_COTA
    )
    cotas = c216.cotas_distribution_free(40, len(referencia), delta)
    observado = 40 / len(referencia)
    assert cotas["inferior"] <= observado <= cotas["superior"]
    assert 0.0 < delta < 1.0


def test_rango_tres_vias_seis_casos_con_tres_etiquetas_distintas():
    referencia = {f"C{k}": X for k in range(10)}
    predicciones = {caso: X for caso in referencia}
    etiquetas = {}
    casos = []
    for k in range(6):
        caso = f"C{k}"
        etiquetas[caso] = {"E3": Y, "E4": Z, "E5": X}
        casos.append(caso)
    for k in range(6, 10):
        etiquetas[f"C{k}"] = {"E3": X, "E4": X, "E5": X}
    resultado = c216.rango_tres_vias(referencia, predicciones, etiquetas, casos)
    assert resultado["aciertos_base"] == 10
    assert resultado["aciertos_min"] == 4
    assert resultado["aciertos_max"] == 10
    assert resultado["exactitud_min"] == pytest.approx(0.4)
    assert resultado["exactitud_max"] == pytest.approx(1.0)
    for caso in resultado["casos"]:
        assert set(caso["asignaciones"].values()) == {X, Y, Z}
        assert max(caso["aciertos_por_asignacion"].values()) - min(
            caso["aciertos_por_asignacion"].values()
        ) == 1


# ---------------------------------------------------------------------------
# Simulacion de referencias alternativas (tarea 2.5)
# ---------------------------------------------------------------------------
def _kernel_mezclado_de_prueba():
    referencia = _referencia_uniforme(8)
    etiquetas = {}
    for k, (caso, clase) in enumerate(referencia.items()):
        indice = CLASES.index(clase)
        alterna = CLASES[(indice + 1) % len(CLASES)]
        etiquetas[caso] = {
            "E3": clase,
            "E4": clase,
            "E5": alterna if k % 4 == 0 else clase,
        }
    kernel = c216.construir_kernel(referencia, etiquetas, CLASES, suavizado=0.5)
    marginal = c216.marginal_empirica(referencia, CLASES)
    predicciones = {caso: clase for caso, clase in referencia.items()}
    return referencia, predicciones, kernel["probabilidades"], marginal


def test_simular_referencias_es_determinista_con_la_misma_semilla():
    referencia, predicciones, probabilidades, marginal = _kernel_mezclado_de_prueba()
    primera = c216.simular_referencias(
        referencia, predicciones, probabilidades, marginal, 0.5, 25, 20261021, CLASES
    )
    segunda = c216.simular_referencias(
        referencia, predicciones, probabilidades, marginal, 0.5, 25, 20261021, CLASES
    )
    assert primera == segunda


def test_simular_referencias_cambia_con_la_semilla():
    referencia, predicciones, probabilidades, marginal = _kernel_mezclado_de_prueba()
    primera = c216.simular_referencias(
        referencia, predicciones, probabilidades, marginal, 0.5, 25, 20261021, CLASES
    )
    segunda = c216.simular_referencias(
        referencia, predicciones, probabilidades, marginal, 0.5, 25, 7, CLASES
    )
    assert primera != segunda


def test_simular_referencias_con_referencia_perfecta_da_exactitud_uno():
    referencia = _referencia_uniforme(3)
    kernel = c216.construir_kernel(
        referencia, _etiquetas_de(referencia), CLASES, suavizado=0.0
    )
    marginal = c216.marginal_empirica(referencia, CLASES)
    predicciones = dict(referencia)
    resultado = c216.simular_referencias(
        referencia, predicciones, kernel["probabilidades"], marginal, 0.0, 5, 1, CLASES
    )
    assert resultado["exactitud"]["aciertos"] == [len(referencia)] * 5
    assert resultado["exactitud"]["proporcion_ge_0_6893"] == 1.0
    assert resultado["macro_f1"]["valores"] == [1.0] * 5


def test_simular_referencias_informa_distribucion_completa_y_ordenada():
    referencia, predicciones, probabilidades, marginal = _kernel_mezclado_de_prueba()
    resultado = c216.simular_referencias(
        referencia, predicciones, probabilidades, marginal, 0.3, 30, 20261021, CLASES
    )
    exactitud = resultado["exactitud"]
    macro_f1 = resultado["macro_f1"]
    assert len(exactitud["aciertos"]) == 30
    assert len(macro_f1["valores"]) == 30
    assert exactitud["q2_5"] <= exactitud["mediana"] <= exactitud["q97_5"]
    assert macro_f1["q2_5"] <= macro_f1["mediana"] <= macro_f1["q97_5"]
    assert all(0 <= aciertos <= len(referencia) for aciertos in exactitud["aciertos"])
    assert all(0.0 <= valor <= 1.0 for valor in macro_f1["valores"])
    assert 0.0 <= exactitud["proporcion_ge_0_6893"] <= 1.0
    assert resultado["errores"]["valores"][0] == len(referencia) - exactitud["aciertos"][0]


# ---------------------------------------------------------------------------
# Integracion con los artefactos versionados (tarea 2.5)
# ---------------------------------------------------------------------------
def test_cargar_entradas_valida_conteos_y_hashes():
    entradas = c216.cargar_entradas()
    assert entradas["conteos"] == {
        "casos": 206,
        "filas_etiquetado": 476,
        "arbitrados_e5": 64,
        "tres_vias": 6,
        "predicciones": 206,
    }
    assert set(entradas["entradas_sha256"]) == {
        "corpus_independiente_arbitrado.json",
        "predicciones_arbitrado.json",
        "doble_etiquetado_arbitrado.csv",
        "arbitraje_tres_vias.json",
    }
    assert entradas["entradas_sha256"]["corpus_independiente_arbitrado.json"] == (
        "cb2874e649fb932c00b536100025c0a0137b3314ab12d45234e4c29049adc67e"
    )


def test_documento_real_reproduce_anclajes_y_declara_caracter_aditivo():
    doc = c216.construir_documento(replicas=20, semilla=20261021)
    assert doc["anclajes"]["n"] == 206
    assert doc["anclajes"]["aciertos_estrictos"] == 142
    assert doc["anclajes"]["macro_f1"] == pytest.approx(0.7024, abs=1e-4)
    assert doc["anclajes"]["acuerdo_e3_e4"]["p_o"] == pytest.approx(0.6867, abs=1e-4)
    assert doc["anclajes"]["acuerdo_e3_e4"]["kappa"] == pytest.approx(0.6055, abs=1e-4)
    assert doc["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert doc["calibracion"]["lambda"] > 0.0
    assert abs(doc["calibracion"]["kappa_esperado"] - 0.6055) <= 0.005
    assert doc["cotas"]["inferior"] <= 142 / 206 <= doc["cotas"]["superior"]
    assert doc["tres_vias"]["n"] == 6
    assert len(doc["tres_vias"]["casos"]) == 6
    assert doc["tres_vias"]["exactitud_min"] <= doc["tres_vias"]["exactitud_max"]
