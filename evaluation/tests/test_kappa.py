"""
Tests del kappa de Cohen entre los etiquetadores nuevos (c-167, evaluation/kappa.py).

Kappa no ponderado, 5 clases (`SECTORES_CANONICOS`), sobre la etiqueta primaria y con
exactamente dos etiquetadores fijos. El oraculo numerico se verifico por separado con
Python (formula de Fleiss, Cohen y Everitt, 1969, varianza bajo H1):

    matriz [[20, 5, 0], [3, 15, 2], [0, 4, 11]] (n = 60)
    kappa = 0,642553; SE = 0,083594; p_o = 0,766667; p_e = 0,347222;
    IC 95 % asintotico = [0,478711; 0,806395]; PABAK (k = 5) = 0,708333.

Todo corre sin red ni Gemini; los datos son SINTETICOS.
"""

from __future__ import annotations

import random

import pytest

from evaluation import kappa, metrics
from evaluation.corpus import SECTORES_CANONICOS
from evaluation.kappa import kappa_cohen, kappa_doble_etiquetado, rotulo_landis_koch
from evaluation.metrics import (
    NIVEL_CONFIANZA,
    REMUESTREOS_BOOTSTRAP,
    SEMILLA_BOOTSTRAP,
    percentil_intervalo,
    remuestreos_indices,
)
from evaluation.tests import helpers_campana as h

TOLERANCIA = 1e-6

MATRIZ_ORACULO = [[20, 5, 0], [3, 15, 2], [0, 4, 11]]


def pares_desde_matriz(matriz: list[list[int]]) -> list[tuple[str, str]]:
    """Pares (E1, E2) con las frecuencias de `matriz`, inmersa en las primeras clases canonicas."""
    pares: list[tuple[str, str]] = []
    for i, fila in enumerate(matriz):
        for j, frecuencia in enumerate(fila):
            pares += [(SECTORES_CANONICOS[i], SECTORES_CANONICOS[j])] * frecuencia
    return pares


# ---------------------------------------------------------------------------
# 2.1 — oraculo de kappa, p_o y p_e
# ---------------------------------------------------------------------------
def test_oraculo_kappa_po_y_pe_con_la_matriz_inmersa_en_las_cinco_clases():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert resultado.n == 60
    assert resultado.kappa == pytest.approx(0.642553, abs=TOLERANCIA)
    assert resultado.p_o == pytest.approx(0.766667, abs=TOLERANCIA)
    assert resultado.p_e == pytest.approx(0.347222, abs=TOLERANCIA)


# ---------------------------------------------------------------------------
# 2.3 — triangulacion: acuerdo perfecto, acuerdo igual al azar, un solo sector
# ---------------------------------------------------------------------------
def test_diagonal_perfecta_con_mas_de_un_sector_da_kappa_uno():
    resultado = kappa_cohen(pares_desde_matriz([[10, 0], [0, 10]]))

    assert resultado.n == 20
    assert resultado.kappa == pytest.approx(1.0, abs=TOLERANCIA)
    assert resultado.p_o == pytest.approx(1.0, abs=TOLERANCIA)
    assert resultado.p_e == pytest.approx(0.5, abs=TOLERANCIA)


def test_acuerdo_igual_al_azar_da_kappa_cero():
    resultado = kappa_cohen(pares_desde_matriz([[4, 4], [4, 4]]))

    assert resultado.kappa == pytest.approx(0.0, abs=TOLERANCIA)
    assert resultado.p_o == pytest.approx(resultado.p_e, abs=TOLERANCIA)


def test_desacuerdo_total_da_kappa_menos_uno():
    resultado = kappa_cohen(pares_desde_matriz([[0, 3], [3, 0]]))

    assert resultado.kappa == pytest.approx(-1.0, abs=TOLERANCIA)
    assert resultado.p_o == 0.0


def test_un_unico_sector_en_todos_los_casos_deja_pe_en_uno_y_kappa_no_estimable():
    resultado = kappa_cohen(pares_desde_matriz([[7]]))

    assert resultado.n == 7
    assert resultado.p_e == 1.0
    assert resultado.p_o == 1.0
    assert resultado.kappa is None


def test_una_etiqueta_no_canonica_falla_y_la_nombra():
    pares = [(SECTORES_CANONICOS[0], "Redes")]

    with pytest.raises(ValueError, match="Redes"):
        kappa_cohen(pares)


def test_sin_pares_falla_en_lugar_de_dividir_por_cero():
    with pytest.raises(ValueError, match="sin pares|ningun par|no hay pares"):
        kappa_cohen([])


# ---------------------------------------------------------------------------
# 2.4 — error estandar asintotico e IC del oraculo
# ---------------------------------------------------------------------------
def test_oraculo_error_estandar_asintotico_e_ic_del_95_por_ciento():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert resultado.error_estandar == pytest.approx(0.083594, abs=TOLERANCIA)
    assert resultado.ic_asintotico == pytest.approx((0.478711, 0.806395), abs=TOLERANCIA)
    assert resultado.nivel_confianza == 0.95


# ---------------------------------------------------------------------------
# 2.6 — triangulacion del IC asintotico: diagonal perfecta, recorte y p_e = 1
# ---------------------------------------------------------------------------
def test_diagonal_perfecta_da_error_estandar_cero_e_ic_uno_uno():
    resultado = kappa_cohen(pares_desde_matriz([[10, 0], [0, 10]]))

    assert resultado.error_estandar == pytest.approx(0.0, abs=TOLERANCIA)
    assert resultado.ic_asintotico == (1.0, 1.0)


def test_el_limite_superior_que_excede_uno_se_recorta_a_uno():
    # kappa = 0,9 y SE = 0,096979: kappa + 1,96 * SE = 1,0901 > 1.
    resultado = kappa_cohen(pares_desde_matriz([[9, 1], [0, 10]]))

    assert resultado.kappa == pytest.approx(0.9, abs=TOLERANCIA)
    assert resultado.error_estandar == pytest.approx(0.096979, abs=TOLERANCIA)
    assert resultado.ic_asintotico[1] == 1.0
    assert resultado.ic_asintotico[0] == pytest.approx(0.709924, abs=TOLERANCIA)


def test_el_limite_inferior_por_debajo_de_menos_uno_se_recorta_a_menos_uno():
    # kappa = -0,8 y SE = 0,587878: kappa - 1,96 * SE = -1,9522 < -1.
    resultado = kappa_cohen(pares_desde_matriz([[0, 1], [2, 0]]))

    assert resultado.kappa == pytest.approx(-0.8, abs=TOLERANCIA)
    assert resultado.ic_asintotico[0] == -1.0
    assert resultado.ic_asintotico[1] == pytest.approx(0.352219, abs=TOLERANCIA)


def test_con_pe_igual_a_uno_no_hay_error_estandar_ni_intervalo():
    resultado = kappa_cohen(pares_desde_matriz([[7]]))

    assert resultado.error_estandar is None
    assert resultado.ic_asintotico is None


def test_un_nivel_de_confianza_menor_da_un_intervalo_mas_angosto():
    pares = pares_desde_matriz(MATRIZ_ORACULO)

    ic_95 = kappa_cohen(pares).ic_asintotico
    ic_90 = kappa_cohen(pares, nivel_confianza=0.90).ic_asintotico

    assert ic_90[0] > ic_95[0] and ic_90[1] < ic_95[1]
    assert ic_90 == pytest.approx((0.505053, 0.780054), abs=TOLERANCIA)


# ---------------------------------------------------------------------------
# 2.7 — IC bootstrap por casos: reproducible y con los helpers de metrics.py
# ---------------------------------------------------------------------------
def kappa_ingenuo(pares: list[tuple[str, str]]) -> float | None:
    """Kappa recomputado con conteos por etiqueta (camino distinto del de kappa.py)."""
    n = len(pares)
    p_o = sum(a == b for a, b in pares) / n
    p_e = sum(
        (sum(a == c for a, _ in pares) / n) * (sum(b == c for _, b in pares) / n)
        for c in SECTORES_CANONICOS
    )
    return None if p_e == 1.0 else (p_o - p_e) / (1.0 - p_e)


def test_el_ic_bootstrap_es_identico_en_dos_corridas():
    pares = pares_desde_matriz(MATRIZ_ORACULO)

    primera = kappa_cohen(pares)
    segunda = kappa_cohen(pares)

    assert primera.ic_bootstrap is not None
    assert primera.ic_bootstrap == segunda.ic_bootstrap


def test_kappa_usa_los_helpers_y_las_constantes_de_metrics_sin_redefinirlos():
    assert kappa.percentil_intervalo is metrics.percentil_intervalo
    assert kappa.remuestreos_indices is metrics.remuestreos_indices
    assert kappa.SEMILLA_BOOTSTRAP is metrics.SEMILLA_BOOTSTRAP
    assert kappa.REMUESTREOS_BOOTSTRAP is metrics.REMUESTREOS_BOOTSTRAP


def test_el_ic_bootstrap_coincide_con_una_recomputacion_independiente():
    pares = pares_desde_matriz(MATRIZ_ORACULO)
    valores = []
    generador = random.Random(SEMILLA_BOOTSTRAP)
    for indices in remuestreos_indices(generador, len(pares), REMUESTREOS_BOOTSTRAP):
        valor = kappa_ingenuo([pares[i] for i in indices])
        if valor is not None:
            valores.append(valor)
    esperado = percentil_intervalo(valores, NIVEL_CONFIANZA)

    resultado = kappa_cohen(pares)

    assert resultado.ic_bootstrap == pytest.approx(esperado, abs=1e-12)
    assert resultado.semilla == SEMILLA_BOOTSTRAP
    assert resultado.remuestreos == REMUESTREOS_BOOTSTRAP
    assert resultado.remuestras_degeneradas == 0
    assert resultado.bootstrap_computable is True


def test_el_ic_bootstrap_del_oraculo_contiene_a_kappa_y_es_razonable():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    inferior, superior = resultado.ic_bootstrap
    assert inferior < resultado.kappa < superior
    assert 0.40 < inferior < 0.60 and 0.75 < superior < 0.90


# ---------------------------------------------------------------------------
# 2.9 — triangulacion: remuestras degeneradas (p_e = 1) y la regla del 5 %
# ---------------------------------------------------------------------------
UN_SECTOR_DOMINANTE_CHICO = [(SECTORES_CANONICOS[0], SECTORES_CANONICOS[0])] * 4 + [
    (SECTORES_CANONICOS[1], SECTORES_CANONICOS[1])
]  # n = 5: ~34 % de las remuestras caen todas en el sector dominante
UN_SECTOR_DOMINANTE_MEDIANO = (
    [(SECTORES_CANONICOS[0], SECTORES_CANONICOS[0])] * 26
    + [(SECTORES_CANONICOS[1], SECTORES_CANONICOS[1])] * 2
    + [(SECTORES_CANONICOS[0], SECTORES_CANONICOS[1]), (SECTORES_CANONICOS[1], SECTORES_CANONICOS[0])]
)  # n = 30: ~1 % de las remuestras caen todas en (sector 0, sector 0)


def test_mas_del_cinco_por_ciento_de_remuestras_degeneradas_no_emite_ic_bootstrap():
    resultado = kappa_cohen(UN_SECTOR_DOMINANTE_CHICO)

    assert resultado.remuestras_degeneradas > 0.05 * REMUESTREOS_BOOTSTRAP
    assert resultado.bootstrap_computable is False
    assert resultado.ic_bootstrap is None
    assert "IC bootstrap no computable" in resultado.motivo_bootstrap
    assert str(resultado.remuestras_degeneradas) in resultado.motivo_bootstrap
    # El kappa y su IC asintotico siguen disponibles: solo el bootstrap queda sin emitir.
    assert resultado.kappa == pytest.approx(1.0, abs=TOLERANCIA)
    assert resultado.ic_asintotico == (1.0, 1.0)


def test_con_menos_del_cinco_por_ciento_el_ic_se_emite_y_el_conteo_se_reporta():
    resultado = kappa_cohen(UN_SECTOR_DOMINANTE_MEDIANO)

    assert 0 < resultado.remuestras_degeneradas <= 0.05 * REMUESTREOS_BOOTSTRAP
    assert resultado.bootstrap_computable is True
    assert resultado.ic_bootstrap is not None
    assert resultado.motivo_bootstrap is None


def test_las_remuestras_degeneradas_se_descartan_y_se_cuentan_sin_sesgar_el_ic():
    pares = UN_SECTOR_DOMINANTE_MEDIANO
    valores = []
    generador = random.Random(SEMILLA_BOOTSTRAP)
    for indices in remuestreos_indices(generador, len(pares), REMUESTREOS_BOOTSTRAP):
        valor = kappa_ingenuo([pares[i] for i in indices])
        if valor is not None:
            valores.append(valor)

    resultado = kappa_cohen(pares)

    assert resultado.remuestras_degeneradas == REMUESTREOS_BOOTSTRAP - len(valores)
    assert resultado.ic_bootstrap == pytest.approx(percentil_intervalo(valores, NIVEL_CONFIANZA), abs=1e-12)


def test_kappa_no_estimable_no_calcula_el_ic_bootstrap():
    resultado = kappa_cohen(pares_desde_matriz([[7]]))

    assert resultado.ic_bootstrap is None
    assert resultado.bootstrap_computable is False
    assert "p_e = 1" in resultado.motivo_bootstrap


# ---------------------------------------------------------------------------
# 2.10 — PABAK y rotulos de Landis y Koch
# ---------------------------------------------------------------------------
def test_pabak_del_oraculo_es_cinco_po_menos_uno_sobre_cuatro():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert resultado.pabak == pytest.approx((5 * resultado.p_o - 1) / 4, abs=1e-12)
    assert resultado.pabak == pytest.approx(0.708333, abs=TOLERANCIA)


def test_pabak_usa_k_igual_a_cinco_aunque_solo_se_usen_dos_sectores():
    resultado = kappa_cohen(pares_desde_matriz([[9, 1], [0, 10]]))

    assert resultado.pabak == pytest.approx((5 * 0.95 - 1) / 4, abs=TOLERANCIA)


@pytest.mark.parametrize(
    ("valor", "rotulo"),
    [
        (-1.0, "pobre"),
        (-0.01, "pobre"),
        (0.0, "leve"),
        (0.20, "leve"),
        (0.2001, "aceptable"),
        (0.40, "aceptable"),
        (0.4001, "moderado"),
        (0.60, "moderado"),
        (0.6001, "sustancial"),
        (0.80, "sustancial"),
        (0.8001, "casi perfecto"),
        (1.0, "casi perfecto"),
    ],
)
def test_rotulo_de_landis_y_koch_en_los_bordes_de_cada_categoria(valor, rotulo):
    assert rotulo_landis_koch(valor) == rotulo


def test_el_oraculo_tiene_rotulo_sustancial():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert resultado.rotulo == "sustancial"


def test_los_rotulos_del_ic_asintotico_del_oraculo_abarcan_tres_categorias():
    # IC [0,478711; 0,806395]: el limite inferior es "moderado" y el superior, al pasar
    # 0,80, "casi perfecto"; entre ambos queda "sustancial".
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert resultado.rotulos_ic_asintotico == ("moderado", "sustancial", "casi perfecto")
    assert "moderado" in resultado.nota_rotulo_ic and "casi perfecto" in resultado.nota_rotulo_ic
    assert "puede abarcar" in resultado.nota_rotulo_ic


def test_los_rotulos_del_ic_bootstrap_se_listan_de_menor_a_mayor_categoria():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    categorias = ["pobre", "leve", "aceptable", "moderado", "sustancial", "casi perfecto"]
    posiciones = [categorias.index(rotulo) for rotulo in resultado.rotulos_ic_bootstrap]
    assert posiciones == list(range(posiciones[0], posiciones[-1] + 1))
    assert resultado.rotulos_ic_bootstrap[0] == rotulo_landis_koch(resultado.ic_bootstrap[0])
    assert resultado.rotulos_ic_bootstrap[-1] == rotulo_landis_koch(resultado.ic_bootstrap[1])


def test_un_ic_dentro_de_una_sola_categoria_lista_una_sola_categoria():
    resultado = kappa_cohen(pares_desde_matriz([[10, 0], [0, 10]]))

    assert resultado.rotulos_ic_asintotico == ("casi perfecto",)


def test_kappa_no_estimable_no_tiene_rotulos_pero_si_pabak():
    resultado = kappa_cohen(pares_desde_matriz([[7]]))

    assert resultado.rotulo is None
    assert resultado.rotulos_ic_asintotico == ()
    assert resultado.rotulos_ic_bootstrap == ()
    assert resultado.pabak == 1.0


# ---------------------------------------------------------------------------
# 2.11 — kappa desde la planilla: exactamente dos etiquetadores y declaraciones
# ---------------------------------------------------------------------------
@pytest.fixture
def planilla() -> list[dict[str, str]]:
    """Planilla SINTETICA de C1 con las dos tareas (doble etiquetado y brazo manual)."""
    return h.leer_csv(h.PLANILLA)


def test_kappa_desde_la_planilla_usa_solo_las_filas_de_doble_etiquetado(planilla):
    resultado = kappa_doble_etiquetado(planilla)

    assert resultado.n == 24
    assert resultado.etiquetadores == ("E1", "E2")
    assert resultado.p_o == pytest.approx(20 / 24, abs=TOLERANCIA)
    assert resultado.kappa == pytest.approx(0.792208, abs=TOLERANCIA)


def test_kappa_de_la_planilla_coincide_con_scikit_learn(planilla):
    metricas = pytest.importorskip("sklearn.metrics")
    por_caso: dict[str, dict[str, str]] = {}
    for fila in planilla:
        if fila["tarea"] == "doble_etiquetado":
            por_caso.setdefault(fila["id_caso"], {})[fila["id_etiquetador"]] = fila["sector_etiquetado"]
    casos = sorted(por_caso)

    esperado = metricas.cohen_kappa_score(
        [por_caso[c]["E1"] for c in casos], [por_caso[c]["E2"] for c in casos]
    )

    assert kappa_doble_etiquetado(planilla).kappa == pytest.approx(esperado, abs=1e-12)


def test_el_resultado_no_depende_del_orden_de_las_filas_de_la_planilla(planilla):
    desordenada = list(reversed(planilla))

    assert kappa_doble_etiquetado(desordenada) == kappa_doble_etiquetado(planilla)


def test_con_un_solo_etiquetador_falla_y_nombra_el_alias(planilla):
    solo_e1 = [f for f in planilla if not (f["tarea"] == "doble_etiquetado" and f["id_etiquetador"] == "E2")]

    with pytest.raises(ValueError, match="exactamente dos") as excinfo:
        kappa_doble_etiquetado(solo_e1)

    assert "E1" in str(excinfo.value) and "E2" not in str(excinfo.value)


def test_con_tres_etiquetadores_falla_y_nombra_los_tres_alias(planilla):
    tercero = [dict(f, id_etiquetador="E3") for f in planilla if f["tarea"] == "doble_etiquetado"]

    with pytest.raises(ValueError, match="exactamente dos") as excinfo:
        kappa_doble_etiquetado(planilla + tercero)

    mensaje = str(excinfo.value)
    assert "E1" in mensaje and "E2" in mensaje and "E3" in mensaje
    assert "Fleiss" in mensaje


def test_sin_filas_de_doble_etiquetado_falla(planilla):
    solo_manual = [f for f in planilla if f["tarea"] == "brazo_manual"]

    with pytest.raises(ValueError, match="exactamente dos"):
        kappa_doble_etiquetado(solo_manual)


def test_un_caso_sin_etiqueta_de_e2_falla_y_nombra_caso_y_alias(planilla):
    sin_e2 = [f for f in planilla if not (f["id_caso"] == "S05" and f["id_etiquetador"] == "E2")]

    with pytest.raises(ValueError) as excinfo:
        kappa_doble_etiquetado(sin_e2)

    assert "S05" in str(excinfo.value) and "E2" in str(excinfo.value)


def test_un_registro_duplicado_falla_y_nombra_caso_y_alias(planilla):
    duplicada = planilla + [next(f for f in planilla if f["id_caso"] == "S03" and f["id_etiquetador"] == "E1")]

    with pytest.raises(ValueError) as excinfo:
        kappa_doble_etiquetado(duplicada)

    assert "S03" in str(excinfo.value) and "E1" in str(excinfo.value)


def test_un_sector_no_canonico_falla_y_nombra_caso_y_alias(planilla):
    mal = [dict(f, sector_etiquetado="Redes") if (f["id_caso"] == "S07" and f["id_etiquetador"] == "E2") else f
           for f in planilla]

    with pytest.raises(ValueError) as excinfo:
        kappa_doble_etiquetado(mal)

    mensaje = str(excinfo.value)
    assert "S07" in mensaje and "E2" in mensaje and "Redes" in mensaje


def test_la_salida_declara_que_fleiss_queda_fuera_y_que_es_el_kappa_de_los_etiquetadores_nuevos(planilla):
    resultado = kappa_doble_etiquetado(planilla)

    declaraciones = " | ".join(resultado.declaraciones)
    assert "Fleiss fuera del alcance" in declaraciones
    assert "kappa de etiquetadores nuevos, no IC del 0,87 original" in declaraciones


def test_kappa_cohen_directo_tambien_trae_las_declaraciones():
    resultado = kappa_cohen(pares_desde_matriz(MATRIZ_ORACULO))

    assert len(resultado.declaraciones) == 2
    assert resultado.etiquetadores == ()
