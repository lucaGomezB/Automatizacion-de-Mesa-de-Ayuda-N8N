"""Pruebas del analisis de propagacion del arbitraje fuera de muestra (c-221).

TDD estricto de las funciones puras con casos sinteticos (sin I/O ni red) mas la
integracion con los artefactos versionados. Cubre la exactitud ponderada y su IC
bootstrap, el desglose por grupos, las metricas por clase, los destinos de error,
la calibracion descriptiva sin seleccion de umbral, el balance neto, las diferencias
entre corridas, el control de alcanzabilidad del `commit` y los anclajes reales.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_propagacion_arbitraje_c221 as c221  # noqa: E402


# ---------------------------------------------------------------------------
# Exactitud ponderada (funcion pura)
# ---------------------------------------------------------------------------
def test_exactitud_ponderada_con_dos_clases_y_pesos_desiguales():
    reales = [
        "Sistemas",
        "Sistemas",
        "Sistemas",
        "Soporte Tecnico Hardware",
        "Soporte Tecnico Hardware",
    ]
    predichos = [
        "Sistemas",
        "Sistemas",
        "Soporte Tecnico Hardware",
        "Soporte Tecnico Hardware",
        "Sistemas",
    ]
    pesos = {"Sistemas": 2, "Soporte Tecnico Hardware": 1}
    # Sistemas: sensibilidad 2/3; Hardware: 1/2; (2*(2/3) + 1*(1/2)) / 3 = 11/18
    assert c221.exactitud_ponderada(reales, predichos, pesos) == pytest.approx(11 / 18)


def test_exactitud_ponderada_sin_pesos_alternativos_es_la_sensibilidad_unica():
    reales = ["Bases de Datos", "Bases de Datos"]
    predichos = ["Bases de Datos", "Sistemas"]
    assert c221.exactitud_ponderada(reales, predichos, {"Bases de Datos": 1}) == pytest.approx(0.5)


def test_exactitud_ponderada_aborta_si_una_clase_con_peso_no_tiene_soporte():
    with pytest.raises(c221.EntradaInconsistente, match="soporte"):
        c221.exactitud_ponderada(["Sistemas"], ["Sistemas"], {"Sistemas": 1, "Bases de Datos": 1})


# ---------------------------------------------------------------------------
# IC bootstrap ponderada (descarte y conteo de replicas sin alguna clase)
# ---------------------------------------------------------------------------
def test_ic_bootstrap_ponderada_descarta_replicas_sin_alguna_clase():
    reales = ["Sistemas", "Soporte Tecnico Hardware"]
    predichos = ["Sistemas", "Soporte Tecnico Hardware"]
    resultado = c221.ic_bootstrap_ponderada(
        reales, predichos, {"Sistemas": 1, "Soporte Tecnico Hardware": 1}, remuestreos=20
    )
    assert resultado["valor"] == pytest.approx(1.0)
    assert resultado["descartadas"] > 0
    assert resultado["remuestras_validas"] + resultado["descartadas"] == 20


def test_ic_bootstrap_ponderada_es_determinista_con_la_misma_semilla():
    reales = ["Sistemas", "Sistemas", "Soporte Tecnico Hardware", "Bases de Datos"]
    predichos = ["Sistemas", "Sistemas", "Sistemas", "Bases de Datos"]
    pesos = {"Sistemas": 1, "Soporte Tecnico Hardware": 1, "Bases de Datos": 1}
    primera = c221.ic_bootstrap_ponderada(reales, predichos, pesos, remuestreos=50, semilla=20261021)
    segunda = c221.ic_bootstrap_ponderada(reales, predichos, pesos, remuestreos=50, semilla=20261021)
    assert primera == segunda


def test_ic_bootstrap_ponderada_de_un_conjunto_constante_degrada():
    reales = ["Sistemas"] * 6
    predichos = ["Sistemas"] * 6
    resultado = c221.ic_bootstrap_ponderada(
        reales, predichos, {"Sistemas": 1}, remuestreos=30
    )
    assert resultado["valor"] == pytest.approx(1.0)
    assert tuple(resultado["ic"]) == (pytest.approx(1.0), pytest.approx(1.0))


# ---------------------------------------------------------------------------
# Desglose por grupos
# ---------------------------------------------------------------------------
def test_desglose_informa_aciertos_n_exactitud_y_wilson_por_grupo():
    casos = [
        {"real": "A", "predicho": "A", "g": "x"},
        {"real": "B", "predicho": "C", "g": "x"},
        {"real": "A", "predicho": "A", "g": "y"},
    ]
    salida = c221.desglose(casos, "g")
    assert salida["x"]["aciertos"] == 1
    assert salida["x"]["n"] == 2
    assert salida["x"]["exactitud"] == pytest.approx(0.5)
    assert salida["x"]["ic_wilson"][0] <= 0.5 <= salida["x"]["ic_wilson"][1]
    assert salida["y"]["aciertos"] == 1
    assert salida["y"]["n"] == 1


def test_desglose_de_lista_vacia_es_vacio():
    assert c221.desglose([], "g") == {}


# ---------------------------------------------------------------------------
# Metricas por clase y destinos de error
# ---------------------------------------------------------------------------
def test_metricas_por_clase_informa_matriz_y_metricas():
    reales = ["Sistemas", "Sistemas", "Bases de Datos", "Soporte Tecnico Software"]
    predichos = ["Sistemas", "Bases de Datos", "Bases de Datos", "Soporte Tecnico Software"]
    metricas = c221.metricas_por_clase(reales, predichos)
    assert metricas["soporte"]["Sistemas"] == 2
    assert metricas["sensibilidad"]["Sistemas"] == pytest.approx(0.5)
    assert metricas["matriz"]["Sistemas"]["Bases de Datos"] == 1
    assert metricas["f1_macro"] == pytest.approx(metricas["f1_macro"])


def test_destinos_de_error_cuenta_los_sectores_predichos_de_una_clase():
    reales = ["Sistemas", "Sistemas", "Sistemas", "Bases de Datos"]
    predichos = [
        "Soporte Tecnico Software",
        "Soporte Tecnico Software",
        "Seguridad Informatica",
        "Bases de Datos",
    ]
    destinos = c221.destinos_de_error(reales, predichos, "Sistemas")
    assert destinos == {"Soporte Tecnico Software": 2, "Seguridad Informatica": 1}


def test_destinos_de_error_de_una_clase_sin_errores_es_vacio():
    assert c221.destinos_de_error(["Bases de Datos"], ["Bases de Datos"], "Bases de Datos") == {}


# ---------------------------------------------------------------------------
# Calibracion descriptiva (sin seleccionar umbral)
# ---------------------------------------------------------------------------
def test_calibracion_descriptiva_perfecta_no_tiene_error():
    resultado = c221.calibracion_descriptiva([1.0, 0.0], [True, False], [0.70, 0.99])
    assert resultado["exactitud"] == pytest.approx(0.5)
    assert resultado["ece"]["valor"] == pytest.approx(0.0)
    assert resultado["brier"]["valor"] == pytest.approx(0.0)
    assert resultado["sobreconfianza"]["valor"] == pytest.approx(0.0)


def test_calibracion_descriptiva_con_sobreconfianza_constante():
    confianzas = [0.9, 0.9, 0.9, 0.9]
    aciertos = [True, True, False, False]
    resultado = c221.calibracion_descriptiva(confianzas, aciertos, [0.70, 0.99])
    assert resultado["confianza_media"] == pytest.approx(0.9)
    assert resultado["sobreconfianza"]["valor"] == pytest.approx(0.4)
    assert resultado["brier"]["valor"] == pytest.approx(0.41)
    assert resultado["ece"]["valor"] == pytest.approx(0.4)


def test_calibracion_descriptiva_con_orden_invertido_da_auroc_bajo():
    confianzas = [0.9, 0.9, 0.1, 0.1]
    aciertos = [False, False, True, True]
    resultado = c221.calibracion_descriptiva(confianzas, aciertos, [0.70, 0.99])
    assert resultado["auroc"]["valor"] == pytest.approx(0.0)


def test_calibracion_descriptiva_no_devuelve_umbral_seleccionado():
    resultado = c221.calibracion_descriptiva([0.8, 0.9], [True, False], [0.70, 0.86, 0.91])
    assert resultado["umbral_seleccionado"] is None
    assert [fila["umbral"] for fila in resultado["barrido"]] == [0.70, 0.86, 0.91]


# ---------------------------------------------------------------------------
# Balance neto
# ---------------------------------------------------------------------------
def test_balance_neto_positivo_y_negativo():
    positivo = c221.balance_neto(2646, 43.82, 0.15, 0.172, 300)
    negativo = c221.balance_neto(2646, 43.82, 0.35, 0.172, 900)
    assert positivo > 0
    assert negativo < 0


def test_balance_neto_aplica_la_formula():
    esperado = (2646 / 3600) * (43.82 - (0.30 - 0.172) * 600)
    assert c221.balance_neto(2646, 43.82, 0.30, 0.172, 600) == pytest.approx(esperado)


# ---------------------------------------------------------------------------
# Diferencias entre corridas
# ---------------------------------------------------------------------------
def _pred(sector="Sistemas", etapa="gemini", confianza=0.9):
    return {"sector_predicho": sector, "etapa": etapa, "confianza": confianza}


def test_diferencias_entre_corridas_solo_confianza():
    a = {"I001": _pred(), "I002": _pred(confianza=0.8)}
    b = {"I001": _pred(confianza=0.5), "I002": _pred(confianza=0.8)}
    resultado = c221.diferencias_entre_corridas(a, b)
    assert resultado["casos_comunes"] == 2
    assert resultado["confianza"] == ["I001"]
    assert resultado["sector"] == []
    assert resultado["etapa"] == []


def test_diferencias_entre_corridas_solo_sector():
    a = {"I001": _pred(sector="Sistemas")}
    b = {"I001": _pred(sector="Bases de Datos")}
    resultado = c221.diferencias_entre_corridas(a, b)
    assert resultado["sector"] == ["I001"]
    assert resultado["confianza"] == []


def test_diferencias_entre_corridas_sin_diferencias():
    a = {"I001": _pred(), "I002": _pred()}
    b = {"I001": _pred(), "I002": _pred()}
    resultado = c221.diferencias_entre_corridas(a, b)
    assert resultado == {"casos_comunes": 2, "sector": [], "etapa": [], "confianza": []}


# ---------------------------------------------------------------------------
# Control de alcanzabilidad del commit (los tres codigos de salida)
# ---------------------------------------------------------------------------
def test_clasificar_codigo_commit_cero_es_alcanzable():
    assert c221.clasificar_codigo_commit(0) is True


def test_clasificar_codigo_commit_uno_no_es_alcanzable():
    assert c221.clasificar_codigo_commit(1) is False


def test_clasificar_codigo_commit_ausente_no_es_alcanzable():
    assert c221.clasificar_codigo_commit(128) is False


def test_nota_consola_commit_solo_avisa_si_el_objeto_no_esta_en_el_clon():
    assert c221.nota_consola_commit(0) is None
    assert c221.nota_consola_commit(1) is None
    assert "clon" in c221.nota_consola_commit(128)


# ---------------------------------------------------------------------------
# Integracion con los artefactos versionados
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def doc():
    # B reducido solo para acelerar la suite; los anclajes puntuales no dependen de B.
    return c221.construir_documento(remuestreos=400, semilla=20261021)


def test_pesos_leidos_del_corpus_de_ajuste():
    pesos = c221.cargar_pesos()
    assert pesos == {
        "Sistemas": 16,
        "Soporte Tecnico Hardware": 85,
        "Soporte Tecnico Software": 67,
        "Seguridad Informatica": 31,
        "Bases de Datos": 1,
    }
    assert sum(pesos.values()) == 200


def test_anclajes_reales_se_reproducen(doc):
    assert doc["anclajes"]["total"] == (142, 206)
    assert doc["anclajes"]["macro_f1"] == pytest.approx(0.7024, abs=5e-5)
    assert doc["anclajes"]["lectura_103"] == (87, 103)
    assert doc["anclajes"]["ponderada_103"] == pytest.approx(0.8146, abs=5e-5)
    assert doc["anclajes"]["ece_34"] == pytest.approx(0.1715, abs=5e-5)
    assert doc["anclajes"]["brier_34"] == pytest.approx(0.1935, abs=5e-5)
    assert doc["anclajes"]["arbitrados"] == 64
    assert doc["anclajes"]["discordantes_originales"] == 47
    assert doc["anclajes"]["refuerzo"] == 56
    assert doc["anclajes"]["tres_vias"] == 6


def test_tres_lecturas_con_rotulo_y_limite_superior(doc):
    lecturas = doc["lecturas"]
    assert lecturas["primaria"]["etiqueta"] == "primaria"
    assert lecturas["primaria"]["aciertos"] == 142
    assert lecturas["primaria"]["n"] == 206
    assert lecturas["primaria"]["limite_superior_debajo_de_085"] is True
    assert lecturas["ponderada"]["etiqueta"] == "complementaria"
    assert lecturas["ponderada"]["valor"] == pytest.approx(0.7489, abs=5e-5)
    assert lecturas["ponderada"]["limite_superior_debajo_de_085"] is True
    assert lecturas["ciento_cincuenta"]["aciertos"] == 112
    assert lecturas["ciento_cincuenta"]["n"] == 150
    assert lecturas["ciento_cincuenta"]["limite_superior_debajo_de_085"] is True


def test_lectura_103_etapa_previa(doc):
    previa = doc["lectura_103_etapa_previa"]
    assert (previa["aciertos"], previa["n"]) == (87, 103)
    assert previa["exactitud"] == pytest.approx(0.8447, abs=5e-5)


def test_desglose_por_origen_y_por_bloque(doc):
    origen = doc["desglose"]["origen"]
    assert origen["consenso_e3_e4"]["aciertos"] == 109
    assert origen["consenso_e3_e4"]["n"] == 142
    assert origen["arbitraje_e5"]["aciertos"] == 33
    assert origen["arbitraje_e5"]["n"] == 64
    bloques = doc["desglose"]["bloque"]
    assert bloques["consenso_diseno_original"]["n"] == 103
    assert bloques["discordantes_diseno_original"]["aciertos"] == 25
    assert bloques["discordantes_diseno_original"]["n"] == 47
    assert bloques["refuerzo"]["aciertos"] == 30
    assert bloques["refuerzo"]["n"] == 56


def test_desglose_por_origen_anclado_en_c219(doc):
    c219 = doc["c219_origen"]
    assert c219 is not None and c219["presente"] is True
    assert c219["consenso"] == (109, 142)
    assert c219["arbitrado"] == (33, 64)
    assert doc["desglose"]["origen"]["consenso_e3_e4"]["aciertos"] == c219["consenso"][0]
    assert doc["desglose"]["origen"]["arbitraje_e5"]["aciertos"] == c219["arbitrado"][0]


def test_desglose_por_etapa(doc):
    etapas = doc["desglose"]["etapa"]
    assert etapas["deterministic"]["aciertos"] == 88
    assert etapas["deterministic"]["n"] == 115
    assert etapas["gemini"]["aciertos"] == 54
    assert etapas["gemini"]["n"] == 91


def test_sistemas_con_soporte_ampliado_y_destinos(doc):
    sistemas = doc["sistemas"]
    assert sistemas["soporte"] == 61
    assert sistemas["sensibilidad"] == pytest.approx(31 / 61)
    assert sistemas["destinos_error"] == {
        "Soporte Tecnico Software": 16,
        "Seguridad Informatica": 8,
        "Bases de Datos": 3,
        "Soporte Tecnico Hardware": 3,
    }
    assert sistemas["refuerzo_n"] == 40


def test_calibracion_descriptiva_sobre_los_91_y_contraste_34(doc):
    calibracion = doc["calibracion"]
    assert calibracion["arbitrado"]["n"] == 91
    assert calibracion["arbitrado"]["exactitud"] == pytest.approx(0.5934, abs=5e-5)
    assert calibracion["arbitrado"]["confianza_media"] == pytest.approx(0.9055, abs=5e-5)
    assert calibracion["contraste_34"]["n"] == 34
    assert calibracion["contraste_34"]["ece"]["valor"] == pytest.approx(0.1715, abs=5e-5)
    assert calibracion["contraste_34"]["brier"]["valor"] == pytest.approx(0.1935, abs=5e-5)


def test_barrido_descriptivo_sin_umbral_seleccionado(doc):
    barrido = doc["calibracion"]["arbitrado"]["barrido"]
    assert [fila["umbral"] for fila in barrido] == [0.70, 0.86, 0.91, 0.96, 0.99, "inf"]
    assert doc["calibracion"]["arbitrado"]["umbral_seleccionado"] is None


def test_balance_de_sensibilidad_rotulado_y_con_escenario_medido(doc):
    balance = doc["balance"]
    assert balance["rotulo"] == "sensibilidad"
    assert balance["es_coste_medido_incluido"] is True
    por_tasa = balance["por_tasa"]
    for tasa in ("ponderada", "cruda"):
        assert set(por_tasa[tasa]["rejilla"]) == {"5", "10", "15"}
        assert por_tasa[tasa]["c_medido"] is not None


def test_diferencias_entre_corridas_reales(doc):
    dif = doc["reproducibilidad"]["diferencias"]
    assert dif["casos_comunes"] == 103
    assert dif["sector"] == []
    assert dif["etapa"] == []
    assert len(dif["confianza"]) == 7


def test_control_de_commit_registra_alcanzabilidad(doc):
    commits = doc["reproducibilidad"]["commits"]
    assert commits["predicciones_arbitrado.json"]["alcanzable_desde_main"] is True
    inde = commits["predicciones_independiente.json"]
    assert inde["alcanzable_desde_main"] is False
    assert inde["commit_que_versiono_el_archivo"] is not None


def test_cuotas_observadas_de_los_150_y_de_los_56(doc):
    cuotas = doc["cuotas"]
    assert cuotas["canal_150"] == {"Correo": 50, "Formulario Web": 40, "Telefono": 60}
    assert cuotas["canal_refuerzo"] == {"Correo": 28, "Formulario Web": 18, "Telefono": 10}
    assert cuotas["sector_refuerzo"]["Sistemas"] == 40
    assert cuotas["ventana_refuerzo"]["desde"] is not None
    assert cuotas["ventana_refuerzo"]["desde"] <= cuotas["ventana_refuerzo"]["hasta"]


def test_renderizar_es_determinista(doc):
    assert c221.renderizar(doc) == c221.renderizar(doc)


def test_ejecutar_escribe_json_md_y_sumas_byte_a_byte(tmp_path):
    rutas = c221.ejecutar(salida=tmp_path, remuestreos=150, semilla=20261021)
    nombres = sorted(r.name for r in rutas)
    assert nombres == sorted(
        [
            "analisis_propagacion_arbitraje_c221.json",
            "analisis_propagacion_arbitraje_c221.md",
            "analisis_propagacion_arbitraje_c221.SHA256SUMS.txt",
        ]
    )
    primera = {n: (tmp_path / n).read_bytes() for n in nombres}
    for n in nombres:
        assert b"\r" not in primera[n]
        assert not primera[n].startswith(b"\xef\xbb\xbf")
    c221.ejecutar(salida=tmp_path, remuestreos=150, semilla=20261021)
    for n in nombres:
        assert (tmp_path / n).read_bytes() == primera[n]


def test_anclaje_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c221, "ANCLA_TOTAL", (999, 206))
    with pytest.raises(c221.AnclaNoReproducida):
        c221.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_pesos_inconsistentes_abortan_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c221, "PESOS_ESPERADOS", {"Sistemas": 999})
    with pytest.raises(c221.EntradaInconsistente):
        c221.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_sumas_sha256_listan_las_dos_salidas(tmp_path):
    rutas = c221.ejecutar(salida=tmp_path, remuestreos=120, semilla=20261021)
    sumas = (tmp_path / "analisis_propagacion_arbitraje_c221.SHA256SUMS.txt").read_text(encoding="utf-8")
    for ruta in rutas:
        if ruta.name.endswith(".SHA256SUMS.txt"):
            continue
        assert ruta.name in sumas
        assert c221.sha256(ruta, normalizar_lf=False) in sumas
