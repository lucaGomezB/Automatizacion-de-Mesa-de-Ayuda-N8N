"""Pruebas del analisis de solo lectura del dictamen CONEAU v1.3.0 (c-207).

Cifras ancla (memo canonico): reduccion relativa del tiempo 0,7116 sobre 200 pares (Seccion
3.1); acuerdo E3/E4 103 de 150 (c-191, Seccion 3.19).
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_dictamen_c207 as c207  # noqa: E402


# ---------------------------------------------------------------------------
# Rec. 6: IC de la reduccion relativa del tiempo
# ---------------------------------------------------------------------------
def test_razon_constante_el_ic_degenera_en_el_valor_puntual():
    manual = [10.0, 20.0, 30.0, 40.0, 50.0]
    automatizado = [x * 0.3 for x in manual]
    r = c207.ic_reduccion_tiempo(manual, automatizado)
    assert r["reduccion"] == pytest.approx(0.7)
    assert r["ic_reduccion"][0] == pytest.approx(0.7)
    assert r["ic_reduccion"][1] == pytest.approx(0.7)


def test_razon_no_constante_el_ic_contiene_el_valor_puntual_y_tiene_ancho():
    manual = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    automatizado = [9.0, 5.0, 25.0, 8.0, 12.0, 6.0]
    r = c207.ic_reduccion_tiempo(manual, automatizado)
    inferior, superior = r["ic_reduccion"]
    assert inferior < r["reduccion"] < superior
    assert superior - inferior > 0.05
    # diferencia de medias en segundos: manual - automatizado
    assert r["diferencia_medias_s"] == pytest.approx(35.0 - 65.0 / 6)
    lo, hi = r["ic_diferencia_medias_s"]
    assert lo < r["diferencia_medias_s"] < hi


def test_dos_corridas_dan_el_mismo_ic():
    manual = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]
    automatizado = [9.0, 5.0, 25.0, 8.0, 12.0, 6.0]
    assert c207.ic_reduccion_tiempo(manual, automatizado) == c207.ic_reduccion_tiempo(
        manual, automatizado
    )


def test_pares_de_distinta_longitud_o_vacios_se_rechazan():
    with pytest.raises(ValueError):
        c207.ic_reduccion_tiempo([1.0, 2.0], [1.0])
    with pytest.raises(ValueError):
        c207.ic_reduccion_tiempo([], [])
    with pytest.raises(ValueError):
        c207.ic_reduccion_tiempo([0.0, 0.0], [1.0, 1.0])  # media manual cero


def test_corpus_versionado_reproduce_0_7116_sobre_200_pares():
    manual, automatizado = c207.cargar_pares_tiempo()
    assert len(manual) == len(automatizado) == 200
    r = c207.ic_reduccion_tiempo(manual, automatizado)
    assert round(r["reduccion"], 4) == 0.7116
    assert round(r["diferencia_medias_s"], 2) == 43.82
    assert r["ic_reduccion"][0] < 0.7116 < r["ic_reduccion"][1]


# ---------------------------------------------------------------------------
# Rec. 1: acuerdo entre E3 y E4
# ---------------------------------------------------------------------------
def _fila(caso: str, alias: str, sector: str) -> dict:
    return {
        "id_caso": caso,
        "id_etiquetador": alias,
        "tarea": "doble_etiquetado",
        "sector_etiquetado": sector,
        "sectores_adicionales_etiquetados": "",
    }


SEG = "Seguridad Informatica"
SIS = "Sistemas"
HW = "Soporte Tecnico Hardware"


def _planilla_sintetica() -> list[dict]:
    # 4 casos: 3 concordantes (2 SEG, 1 HW) y 1 discordante (SEG vs SIS)
    filas = []
    for caso, e3, e4 in [
        ("I1", SEG, SEG),
        ("I2", SEG, SEG),
        ("I3", HW, HW),
        ("I4", SEG, SIS),
    ]:
        filas += [_fila(caso, "E3", e3), _fila(caso, "E4", e4)]
    return filas


def test_acuerdo_sobre_planilla_sintetica():
    r = c207.acuerdo_e3_e4(_planilla_sintetica(), esperado_concordantes=3, esperado_total=4)
    assert (r["total"], r["concordantes"], r["discordantes"]) == (4, 3, 1)
    assert r["acuerdo_observado"] == pytest.approx(0.75)
    assert r["etiquetadores"] == ["E3", "E4"]
    assert r["kappa"]["n"] == 4


def test_acuerdo_con_otra_planilla_sintetica_cambia_la_cuenta():
    filas = []
    for caso, e3, e4 in [("I1", SEG, HW), ("I2", HW, SEG), ("I3", SEG, SEG)]:
        filas += [_fila(caso, "E3", e3), _fila(caso, "E4", e4)]
    r = c207.acuerdo_e3_e4(filas, esperado_concordantes=1, esperado_total=3)
    assert (r["concordantes"], r["discordantes"]) == (1, 2)
    assert r["acuerdo_observado"] == pytest.approx(1 / 3)


def test_acuerdo_falla_si_no_coincide_con_el_n_efectivo_esperado():
    with pytest.raises(ValueError, match="concordantes"):
        c207.acuerdo_e3_e4(_planilla_sintetica(), esperado_concordantes=103, esperado_total=4)
    with pytest.raises(ValueError, match="total"):
        c207.acuerdo_e3_e4(_planilla_sintetica(), esperado_concordantes=3, esperado_total=150)


def test_acuerdo_versionado_es_103_de_150_y_coincide_con_c205():
    r = c207.acuerdo_e3_e4_versionado()
    assert (r["concordantes"], r["total"], r["discordantes"]) == (103, 150, 47)
    assert round(r["acuerdo_observado"], 4) == 0.6867
    assert r["n_efectivo_c205"] == 103
    k = r["kappa"]
    assert round(k["kappa"], 4) == 0.6055
    assert k["ic_asintotico"][0] < k["kappa"] < k["ic_asintotico"][1]
    assert k["ic_bootstrap"][0] < k["kappa"] < k["ic_bootstrap"][1]


# ---------------------------------------------------------------------------
# Rec. 5: balance neto con referencia comun
# ---------------------------------------------------------------------------
AHORRO_BRUTO_H = 2646 * 43.82 / 3600  # 32,2 h-persona por trimestre


def test_verificacion_declara_la_referencia_de_cada_tasa_y_la_asimetria():
    v = c207.verificar_asimetria_balance()
    assert v["e_aut_texto"]["errores"] == 53 and v["e_aut_texto"]["n"] == 200
    assert "original" in v["e_aut_texto"]["referencia"]
    assert v["e_man_texto"]["errores"] == 26 and v["e_man_texto"]["n"] == 151
    assert "E1" in v["e_man_texto"]["referencia"] and "E2" in v["e_man_texto"]["referencia"]
    assert v["e_aut_consenso"]["errores"] == 28 and v["e_aut_consenso"]["n"] == 138
    assert v["asimetria_confirmada"] is True


def test_asimetria_no_se_confirma_si_ambas_tasas_usan_la_misma_referencia():
    a = {"errores": 1, "n": 4, "referencia": "consenso E1/E2"}
    m = {"errores": 1, "n": 4, "referencia": "consenso E1/E2"}
    assert c207.hay_asimetria_de_referencia(a, m) is False
    m2 = {"errores": 1, "n": 4, "referencia": "etiquetado original"}
    assert c207.hay_asimetria_de_referencia(a, m2) is True


def test_con_error_igual_el_balance_es_el_ahorro_bruto_en_todo_costo():
    # e_aut = e_man = 0,25 con una derivacion manual por caso
    casos = [(1, 0, 1), (0, 1, 1), (0, 0, 1), (0, 0, 1)]
    r = c207.balance_con_referencia_comun(casos)
    assert r["e_aut"] == pytest.approx(0.25) and r["e_man"] == pytest.approx(0.25)
    assert r["diferencia"] == pytest.approx(0.0)
    for esc in r["escenarios"]:
        assert esc["balance_h"] == pytest.approx(AHORRO_BRUTO_H)


def test_signo_conocido_clasificador_peor_resta_y_mejor_suma():
    peor = [(1, 0, 1), (1, 0, 1), (0, 0, 1), (0, 0, 1)]  # e_aut=0,5; e_man=0
    r = c207.balance_con_referencia_comun(peor)
    esc = {e["costo_min"]: e for e in r["escenarios"]}
    assert esc[10]["balance_h"] == pytest.approx(AHORRO_BRUTO_H - 0.5 * 2646 * 600 / 3600)
    assert esc[10]["balance_h"] < 0
    mejor = [(0, 1, 1), (0, 1, 1), (0, 0, 1), (0, 0, 1)]  # e_aut=0; e_man=0,5
    r2 = c207.balance_con_referencia_comun(mejor)
    esc2 = {e["costo_min"]: e for e in r2["escenarios"]}
    assert esc2[10]["balance_h"] == pytest.approx(AHORRO_BRUTO_H + 0.5 * 2646 * 600 / 3600)


def test_a_estrella_y_la_tasa_manual_por_derivacion():
    # un caso con dos derivaciones: e_man = errores / derivaciones, no por caso
    casos = [(0, 1, 2), (0, 0, 1), (0, 0, 1)]
    r = c207.balance_con_referencia_comun(casos)
    assert r["e_man"] == pytest.approx(0.25)
    esc = {e["costo_min"]: e for e in r["escenarios"]}
    assert esc[5]["a_estrella"] == pytest.approx(1 - 0.25 - 43.82 / 300)


def test_el_ic_fija_el_signo_solo_si_no_cruza_cero():
    # todos los casos iguales en una muestra mas grande: diferencia constante
    casos = [(1, 0, 1)] * 6 + [(0, 0, 1)] * 6
    r = c207.balance_con_referencia_comun(casos)
    esc = {e["costo_min"]: e for e in r["escenarios"]}
    # e_aut=0,5 varia por remuestreo: el IC no es degenerado
    lo, hi = esc[10]["balance_h_ic"]
    assert lo < esc[10]["balance_h"] < hi
    # caso degenerado: sin variacion el IC colapsa y el signo queda fijado
    r0 = c207.balance_con_referencia_comun([(0, 0, 1)] * 5)
    e0 = {e["costo_min"]: e for e in r0["escenarios"]}
    assert e0[10]["balance_h_ic"][0] == pytest.approx(AHORRO_BRUTO_H)
    assert e0[10]["signo_fijado_por_ic"] == "positivo"
    assert esc[15]["signo_fijado_por_ic"] in {"positivo", "negativo", "no fijado"}


def test_casos_sin_derivaciones_o_vacios_se_rechazan():
    with pytest.raises(ValueError):
        c207.balance_con_referencia_comun([])
    with pytest.raises(ValueError):
        c207.balance_con_referencia_comun([(0, 0, 0), (1, 0, 0)])


def test_recalculo_sobre_artefactos_reproduce_los_conteos():
    b = c207.balance_neto_referencia_comun()
    c = b["referencia_consenso"]
    assert (c["errores_automatizado"], c["casos"]) == (28, 138)
    assert (c["errores_manual"], c["derivaciones_manual"]) == (26, 151)
    assert b["verificacion"]["asimetria_confirmada"] is True
    o = b["referencia_original"]
    assert o["casos"] == 200 and o["errores_automatizado"] == 53
    assert o["derivaciones_manual"] == 220
    assert b["limites_no_igualables"]


# ---------------------------------------------------------------------------
# Documento y salidas
# ---------------------------------------------------------------------------
def test_documento_reune_los_tres_bloques_y_los_sha256_de_las_entradas():
    doc = c207.construir_documento()
    assert {"ic_reduccion_tiempo", "acuerdo_e3_e4", "balance_neto_referencia_comun"} <= set(doc)
    assert round(doc["ic_reduccion_tiempo"]["reduccion"], 4) == 0.7116
    assert doc["acuerdo_e3_e4"]["concordantes"] == 103
    assert len(doc["entradas_sha256"]) >= 6
    assert all(len(h) == 64 for h in doc["entradas_sha256"].values())


def test_salidas_son_deterministas_utf8_sin_bom_y_lf(tmp_path):
    json_a, md_a = c207.renderizar(c207.construir_documento())
    json_b, md_b = c207.renderizar(c207.construir_documento())
    assert (json_a, md_a) == (json_b, md_b)
    c207.escribir(c207.construir_documento(), tmp_path)
    for nombre in ("analisis_dictamen_c207.json", "analisis_dictamen_c207.md"):
        datos = (tmp_path / nombre).read_bytes()
        assert not datos.startswith(b"\xef\xbb\xbf")
        assert b"\r" not in datos
        datos.decode("utf-8")


def test_no_se_escribe_nada_si_el_acuerdo_no_coincide(tmp_path, monkeypatch):
    def falla(*_a, **_k):
        raise ValueError("las concordantes no coinciden")

    monkeypatch.setattr(c207, "acuerdo_e3_e4_versionado", falla)
    with pytest.raises(ValueError):
        c207.main(["--salida", str(tmp_path)])
    assert list(tmp_path.iterdir()) == []
