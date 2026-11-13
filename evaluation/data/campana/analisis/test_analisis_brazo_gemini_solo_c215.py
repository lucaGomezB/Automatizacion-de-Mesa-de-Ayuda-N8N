"""Pruebas del analisis pareado del brazo «Gemini solo» frente al hibrido (c-215).

Todo con cachés SINTETICOS en `tmp_path`: sin red, sin Gemini, sin salidas reales.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_brazo_gemini_solo_c215 as ana  # noqa: E402

from evaluation.metrics import f1_macro, f1_por_clase, matriz_confusion  # noqa: E402
from evaluation.run_evaluation import _compute_corpus_hash  # noqa: E402

SEG = "Seguridad Informatica"
SIS = "Sistemas"
HW = "Soporte Tecnico Hardware"


# ---------------------------------------------------------------------------
# Regla de decision prerregistrada (funcion pura)
# ---------------------------------------------------------------------------
def decidir(**kw):
    base = dict(
        delta_inf=-0.02, delta_sup=0.06, razon_costo_sup=0.40, razon_llamadas_sup=0.40, tasa_fallos=0.0
    )
    base.update(kw)
    return ana.decidir(**base)


def test_sostenida_si_no_inferior_y_eficiencia_cumplida():
    d = decidir(delta_inf=-0.049)
    assert d["veredicto"] == "sostenida"
    assert d["componente_exactitud"] == "no inferior" and d["componente_eficiencia"] == "cumplido"


def test_sostenida_con_delta_positivo_claro():
    assert decidir(delta_inf=0.01, delta_sup=0.2)["veredicto"] == "sostenida"


def test_el_margen_es_estricto_en_el_limite_inferior():
    # Delta_inf == -0,05 exacto NO es mayor que -delta: queda indeterminado.
    d = decidir(delta_inf=-0.05, delta_sup=0.04)
    assert d["componente_exactitud"] == "indeterminado" and d["veredicto"] == "no concluyente"


def test_no_sostenida_por_inferioridad_aunque_la_eficiencia_se_cumpla():
    d = decidir(delta_inf=-0.20, delta_sup=-0.051)
    assert d["componente_exactitud"] == "inferior"
    assert d["veredicto"] == "no sostenida"


def test_no_sostenida_si_la_eficiencia_no_se_cumple_aunque_no_sea_inferior():
    d = decidir(delta_inf=0.0, delta_sup=0.1, razon_costo_sup=0.95)
    assert d["componente_eficiencia"] == "no cumplido" and d["veredicto"] == "no sostenida"


def test_la_eficiencia_exige_ambas_razones_bajo_0_90():
    assert decidir(razon_costo_sup=0.89, razon_llamadas_sup=0.90)["componente_eficiencia"] == "no cumplido"
    assert decidir(razon_costo_sup=0.89, razon_llamadas_sup=0.89)["componente_eficiencia"] == "cumplido"


def test_no_concluyente_si_la_exactitud_es_indeterminada_y_la_eficiencia_se_cumple():
    assert decidir(delta_inf=-0.12, delta_sup=0.03)["veredicto"] == "no concluyente"


def test_razon_no_calculable_cuenta_como_eficiencia_no_cumplida():
    d = decidir(razon_costo_sup=None)
    assert d["componente_eficiencia"] == "no cumplido" and d["veredicto"] == "no sostenida"


def test_demasiados_fallos_fuerzan_no_concluyente_con_motivo():
    d = decidir(delta_inf=0.01, delta_sup=0.2, tasa_fallos=0.051)
    assert d["veredicto"] == "no concluyente"
    assert "fallback" in d["motivo"] and "5" in d["motivo"]


def test_fallos_exactamente_en_el_tope_no_invalidan():
    assert decidir(delta_inf=0.01, delta_sup=0.2, tasa_fallos=0.05)["veredicto"] == "sostenida"


def test_la_inferioridad_tambien_se_anula_con_demasiados_fallos():
    assert decidir(delta_inf=-0.3, delta_sup=-0.2, tasa_fallos=0.2)["veredicto"] == "no concluyente"


# ---------------------------------------------------------------------------
# Macro-F1 con casos sin prediccion
# ---------------------------------------------------------------------------
def test_f1_macro_coincide_con_metrics_cuando_todo_tiene_prediccion():
    reales = [SEG, SEG, SIS, HW, SIS, SEG]
    predichos = [SEG, SIS, SIS, HW, SEG, SEG]
    esperado = f1_macro(f1_por_clase(matriz_confusion(reales, predichos)))
    assert ana.f1_macro_con_sin_prediccion(reales, predichos) == pytest.approx(esperado)


def test_f1_macro_otro_conjunto_coincide_con_metrics():
    reales = [HW, HW, HW, SIS]
    predichos = [HW, SIS, SIS, SIS]
    esperado = f1_macro(f1_por_clase(matriz_confusion(reales, predichos)))
    assert ana.f1_macro_con_sin_prediccion(reales, predichos) == pytest.approx(esperado)


def test_f1_macro_un_caso_sin_prediccion_es_falso_negativo_sin_falso_positivo():
    # SEG real sin prediccion: recall de SEG baja, ninguna otra clase suma un falso positivo.
    con = ana.f1_macro_con_sin_prediccion([SEG, SEG], [SEG, None])
    # SEG: tp=1, fn=1, fp=0 -> f1 = 2/3; las otras 4 clases valen 0 -> macro = (2/3)/5
    assert con == pytest.approx((2 / 3) / 5)


# ---------------------------------------------------------------------------
# Escenario sintetico (calculable a mano)
# ---------------------------------------------------------------------------
def escribir_corpus(ruta, ids_y_sector):
    casos = [
        {
            "id": i,
            "descripcion": f"descripcion {i}",
            "canal_origen": "email",
            "sector_asignado": s,
            "sectores_adicionales": extra,
        }
        for i, s, extra in ids_y_sector
    ]
    ruta.write_text(
        json.dumps({"schema_version": 1, "metadata": {"descripcion": "t", "total_casos": len(casos)}, "casos": casos}),
        encoding="utf-8",
    )
    return ruta


def escribir_hibrido(ruta, filas):
    """`filas`: (caso_id, sector_asignado, predicho, etapa)."""
    preds = [
        {
            "caso_id": i, "descripcion": f"descripcion {i}", "sector_asignado": s,
            "sector_predicho": p, "confianza": 0.9, "etapa": e, "sectores_adicionales": [],
        }
        for i, s, p, e in filas
    ]
    ruta.write_text(
        json.dumps({"cache_meta": {"classifier_version": "hybrid-v3"}, "predictions": preds}), encoding="utf-8"
    )
    return ruta


def registro_l(caso_id, bloque, predicho, *, intentos=1, latencia=100.0, etapa="gemini", error=None):
    return {
        "tipo": "caso", "bloque": bloque, "caso_id": caso_id, "sector_predicho": predicho,
        "confianza": 0.9 if predicho else 0.0, "etapa": etapa, "intentos": intentos,
        "latencia_ms": latencia, "latencias_intento_ms": [latencia / intentos] * intentos,
        "tokens_entrada": 800 * intentos, "tokens_salida": 20 * intentos,
        "tokens_total": 820 * intentos, "tokens_origen": "api", "error": error,
        "t_inicio_utc": "2026-11-20T10:00:00+00:00",
    }


def escribir_cache(ruta, meta_extra, registros):
    meta = {
        "tipo": "meta", "modelo": "gemini-3.6-flash", "sdk_version": "2.34.0",
        "prompt_sha256": "c" * 64, "generado_en": "2026-11-20T10:00:00+00:00",
        "precios_usd_por_millon": {"introductorio": {"entrada": 0.75, "salida": 3.75},
                                    "estandar": {"entrada": 1.5, "salida": 7.5}},
        **meta_extra,
    }
    texto = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in [meta, *registros])
    ruta.write_bytes(texto.encode("utf-8"))
    return ruta


# Escenario S1 (fuera de muestra, n = 10, referencia SEG salvo que se indique):
#  I001-I003: H deterministica acierta, L acierta
#  I004, I005: H escala (gemini) acierta, L acierta   (I004 con 2 intentos y 300 ms)
#  I006: H deterministica acierta, L falla
#  I007: H escala y falla, L acierta
#  I008, I009: H escala y falla, L falla
#  I010: H deterministica acierta, L acierta
# a = 6 (ambos), b = 1 (solo H), c = 1 (solo L), d = 2 (ninguno); acc(H) = acc(L) = 0,7
FILAS_H_S1 = [
    ("I001", SEG, SEG, "deterministic"), ("I002", SEG, SEG, "deterministic"), ("I003", SEG, SEG, "deterministic"),
    ("I004", SEG, SEG, "gemini"), ("I005", SEG, SEG, "gemini"), ("I006", SEG, SEG, "deterministic"),
    ("I007", SEG, SIS, "gemini"), ("I008", SEG, SIS, "gemini"), ("I009", SEG, SIS, "gemini"),
    ("I010", SEG, SEG, "deterministic"),
]
PRED_L_S1 = {"I001": SEG, "I002": SEG, "I003": SEG, "I004": SEG, "I005": SEG, "I006": SIS,
             "I007": SEG, "I008": SIS, "I009": HW, "I010": SEG}


@pytest.fixture
def escenario(tmp_path):
    """Entradas sinteticas completas: 4 casos dentro de la muestra y los 10 de S1 fuera."""
    dentro = escribir_corpus(
        tmp_path / "dentro.json",
        [("R001", SEG, []), ("R002", SEG, []), ("R003", SIS, []), ("R004", SIS, [SEG])],
    )
    fuera = escribir_corpus(tmp_path / "fuera.json", [(i, s, []) for i, s, _, _ in FILAS_H_S1])
    h_dentro = escribir_hibrido(
        tmp_path / "h_dentro.json",
        [("R001", SEG, SEG, "deterministic"), ("R002", SEG, SIS, "gemini"),
         ("R003", SIS, SIS, "deterministic"), ("R004", SIS, SEG, "gemini")],
    )
    h_fuera = escribir_hibrido(tmp_path / "h_fuera.json", FILAS_H_S1)
    registros = [
        registro_l("R001", "dentro_muestra", SEG), registro_l("R002", "dentro_muestra", SEG),
        registro_l("R003", "dentro_muestra", SIS), registro_l("R004", "dentro_muestra", SEG),
    ]
    for i, _, _, _ in FILAS_H_S1:
        kw = {"intentos": 2, "latencia": 300.0} if i == "I004" else {}
        registros.append(registro_l(i, "fuera_muestra", PRED_L_S1[i], **kw))
    cache = escribir_cache(
        tmp_path / "cache.jsonl",
        {"corpus_hash_dentro": _compute_corpus_hash(dentro), "corpus_hash_fuera": _compute_corpus_hash(fuera)},
        registros,
    )
    return {
        "cache": cache, "ruta_corpus_dentro": dentro, "ruta_corpus_fuera": fuera,
        "ruta_hibrido_dentro": h_dentro, "ruta_hibrido_fuera": h_fuera,
    }


def documento(escenario, **kw):
    return ana.construir_documento(escenario["cache"], **{k: v for k, v in escenario.items() if k != "cache"},
                                   remuestreos=kw.pop("remuestreos", 500), **kw)


def test_calidad_exactitud_estricta_laxa_y_macro_f1_por_brazo(escenario):
    bloque = documento(escenario)["bloques"]["fuera_muestra"]
    assert bloque["n"] == 10
    assert bloque["brazos"]["H"]["exactitud_estricta"]["aciertos"] == 7
    assert bloque["brazos"]["L"]["exactitud_estricta"]["aciertos"] == 7
    assert bloque["brazos"]["L"]["exactitud_estricta"]["valor"] == pytest.approx(0.7)
    lo, hi = bloque["brazos"]["L"]["exactitud_estricta"]["ic95_wilson"]
    assert lo < 0.7 < hi
    reales = [SEG] * 10
    predichos = [PRED_L_S1[i] for i, _, _, _ in FILAS_H_S1]
    esperado = f1_macro(f1_por_clase(matriz_confusion(reales, predichos)))
    assert bloque["brazos"]["L"]["macro_f1"] == pytest.approx(esperado)


def test_exactitud_laxa_usa_los_sectores_adicionales_de_la_referencia(escenario):
    dentro = documento(escenario)["bloques"]["dentro_muestra"]
    # R004: referencia SIS con adicional SEG. H predijo SEG (laxo ok); L predijo SEG (laxo ok).
    assert dentro["brazos"]["H"]["exactitud_laxa"]["aciertos"] == 3
    assert dentro["brazos"]["L"]["exactitud_laxa"]["aciertos"] == 4
    assert dentro["brazos"]["L"]["exactitud_estricta"]["aciertos"] == 3


def test_contraste_tabla_2x2_mcnemar_y_diferencia(escenario):
    c = documento(escenario)["bloques"]["fuera_muestra"]["contraste"]
    assert c["tabla_2x2"] == {"ambos_aciertan": 6, "solo_hibrido": 1, "solo_gemini_solo": 1, "ninguno": 2}
    assert c["mcnemar"]["p_exacto"] == pytest.approx(1.0)
    d = c["diferencia_exactitud"]
    assert d["valor"] == pytest.approx(0.0) and d["semilla"] == 20261021
    assert d["ic95"][0] <= 0.0 <= d["ic95"][1]


def test_contraste_triangulado_con_otra_asimetria(tmp_path, escenario):
    # L falla ademas I001, I002 y I003: solo H acierta en 4 casos (b = 4), c = 1.
    preds = dict(PRED_L_S1, I001=SIS, I002=SIS, I003=SIS)
    registros = [registro_l(i, "fuera_muestra", preds[i]) for i, _, _, _ in FILAS_H_S1]
    registros += [registro_l(i, "dentro_muestra", p) for i, p in
                  [("R001", SEG), ("R002", SEG), ("R003", SIS), ("R004", SEG)]]
    cache = escribir_cache(
        tmp_path / "otro.jsonl",
        {"corpus_hash_dentro": _compute_corpus_hash(escenario["ruta_corpus_dentro"]),
         "corpus_hash_fuera": _compute_corpus_hash(escenario["ruta_corpus_fuera"])},
        registros,
    )
    doc = ana.construir_documento(cache, **{k: v for k, v in escenario.items() if k != "cache"}, remuestreos=500)
    c = doc["bloques"]["fuera_muestra"]["contraste"]
    assert c["tabla_2x2"]["solo_hibrido"] == 4 and c["tabla_2x2"]["solo_gemini_solo"] == 1
    assert c["diferencia_exactitud"]["valor"] == pytest.approx(0.3)
    # b + c = 5: p exacto = 2 * P(X <= 1), X ~ Bin(5; 0,5) = 2 * 6/32
    assert c["mcnemar"]["p_exacto"] == pytest.approx(2 * 6 / 32)


def test_bootstrap_con_semilla_fija_es_reproducible(escenario):
    a = documento(escenario)["bloques"]["fuera_muestra"]["contraste"]["diferencia_exactitud"]["ic95"]
    b = documento(escenario)["bloques"]["fuera_muestra"]["contraste"]["diferencia_exactitud"]["ic95"]
    assert a == b


# ---------------------------------------------------------------------------
# Carga y alineacion: abortos sin escribir
# ---------------------------------------------------------------------------
def test_cache_inexistente_aborta_con_error_claro(tmp_path, escenario):
    entradas = {k: v for k, v in escenario.items() if k != "cache"}
    with pytest.raises(ana.CacheAusenteError) as exc:
        ana.construir_documento(tmp_path / "no_existe.jsonl", **entradas)
    assert "no_existe.jsonl" in str(exc.value)


def test_cache_incompleto_aborta_nombrando_los_casos_faltantes(tmp_path, escenario):
    lineas = escenario["cache"].read_text(encoding="utf-8").splitlines()
    sin_i007 = [x for x in lineas if '"I007"' not in x]
    escenario["cache"].write_text("\n".join(sin_i007) + "\n", encoding="utf-8")
    with pytest.raises(ana.CorridaIncompletaError) as exc:
        documento(escenario)
    assert "I007" in str(exc.value)


def test_cache_con_casos_sobrantes_aborta(tmp_path, escenario):
    with open(escenario["cache"], "a", encoding="utf-8") as f:
        f.write(json.dumps(registro_l("X999", "fuera_muestra", SEG)) + "\n")
    with pytest.raises(ana.CorridaIncompletaError) as exc:
        documento(escenario)
    assert "X999" in str(exc.value)


def test_hash_de_corpus_distinto_al_del_cache_aborta(tmp_path, escenario):
    escenario["ruta_corpus_fuera"].write_text(
        escenario["ruta_corpus_fuera"].read_text(encoding="utf-8").replace("descripcion I001", "otra I001"),
        encoding="utf-8",
    )
    with pytest.raises(ana.CorridaIncompletaError) as exc:
        documento(escenario)
    assert "corpus_hash_fuera" in str(exc.value)


def test_hibrido_con_casos_faltantes_aborta(tmp_path, escenario):
    escribir_hibrido(escenario["ruta_hibrido_fuera"], FILAS_H_S1[:-1])
    with pytest.raises(ana.CorridaIncompletaError) as exc:
        documento(escenario)
    assert "I010" in str(exc.value)


# ---------------------------------------------------------------------------
# Eficiencia (valores calculados a mano sobre S1)
# ---------------------------------------------------------------------------
def test_eficiencia_llamadas_tokens_y_costo_con_imputacion_para_el_hibrido(escenario):
    e = documento(escenario)["bloques"]["fuera_muestra"]["eficiencia"]
    # L: 9 casos x 1 intento + I004 x 2 = 11. H escala I004 (2), I005, I007, I008, I009 = 6.
    assert e["llamadas"]["L"] == 11 and e["llamadas"]["H"] == 6
    assert e["llamadas"]["razon"]["valor"] == pytest.approx(6 / 11)
    assert e["tokens"]["L"] == {"entrada": 8800, "salida": 220}
    assert e["tokens"]["H"] == {"entrada": 4800, "salida": 120}
    assert e["costo_usd"]["introductorio"]["L"] == pytest.approx(8800e-6 * 0.75 + 220e-6 * 3.75)
    assert e["costo_usd"]["introductorio"]["H"] == pytest.approx(4800e-6 * 0.75 + 120e-6 * 3.75)
    assert e["costo_usd"]["estandar"]["L"] == pytest.approx(2 * e["costo_usd"]["introductorio"]["L"])
    assert e["razon_costo"]["valor"] == pytest.approx(6 / 11)
    assert e["casos_escalados_h"] == 5
    lo, hi = e["razon_costo"]["ic95"]
    assert 0 < lo <= 6 / 11 <= hi <= 1


def test_eficiencia_latencia_media_por_caso_y_diferencia_con_ic(escenario):
    lat = documento(escenario)["bloques"]["fuera_muestra"]["eficiencia"]["latencia_ms"]
    # L: (9 x 100 + 300) / 10 = 120. H imputada: (300 + 100 x 4) / 10 = 70; reglas = 0 ms.
    assert lat["media_L"] == pytest.approx(120.0) and lat["media_H"] == pytest.approx(70.0)
    assert lat["diferencia_L_menos_H"]["valor"] == pytest.approx(50.0)
    lo, hi = lat["diferencia_L_menos_H"]["ic95"]
    assert 0 <= lo <= 50.0 <= hi
    assert "no es tiempo de extremo a extremo" in lat["nota"]


def test_los_precios_se_toman_de_los_metadatos_del_cache(tmp_path, escenario):
    lineas = escenario["cache"].read_text(encoding="utf-8").splitlines()
    meta = json.loads(lineas[0])
    meta["precios_usd_por_millon"]["introductorio"] = {"entrada": 1.5, "salida": 7.5}
    cache = tmp_path / "caro.jsonl"
    cache.write_text("\n".join([json.dumps(meta)] + lineas[1:]) + "\n", encoding="utf-8")
    doc = ana.construir_documento(cache, **{k: v for k, v in escenario.items() if k != "cache"}, remuestreos=200)
    costo = doc["bloques"]["fuera_muestra"]["eficiencia"]["costo_usd"]["introductorio"]["L"]
    assert costo == pytest.approx(8800e-6 * 1.5 + 220e-6 * 7.5)
    assert doc["procedencia"]["precios_usd_por_millon"]["introductorio"]["entrada"] == 1.5


def test_se_informa_cuantos_casos_usaron_tokens_supuestos(tmp_path, escenario):
    lineas = escenario["cache"].read_text(encoding="utf-8").splitlines()
    nuevas = [
        l.replace('"tokens_origen": "api"', '"tokens_origen": "supuesto"') if '"I005"' in l else l
        for l in lineas
    ]
    escenario["cache"].write_text("\n".join(nuevas) + "\n", encoding="utf-8")
    e = documento(escenario)["bloques"]["fuera_muestra"]["eficiencia"]
    assert e["tokens"]["casos_con_tokens_supuestos"] == 1


# ---------------------------------------------------------------------------
# Sensibilidad H*, control de deriva y veredicto
# ---------------------------------------------------------------------------
def test_sensibilidad_hstar_toma_la_nueva_prediccion_de_gemini_donde_h_escalo(escenario):
    s = documento(escenario)["bloques"]["fuera_muestra"]["sensibilidad_hstar"]
    assert s["exactitud_estricta"]["aciertos"] == 8
    assert s["contraste"]["tabla_2x2"]["solo_hibrido"] == 1  # I006 (reglas acierta, L falla)
    assert s["contraste"]["tabla_2x2"]["solo_gemini_solo"] == 0
    assert s["contraste"]["diferencia_exactitud"]["valor"] == pytest.approx(0.1)


def test_control_de_deriva_mide_concordancia_en_los_casos_que_h_ya_escalo(escenario):
    d = documento(escenario)["control_deriva"]
    # Fuera: I004, I005, I008 coinciden; I007 e I009 no. Dentro: R004 coincide; R002 no.
    assert (d["fuera_muestra"]["n_escalados"], d["fuera_muestra"]["concordancia"]["aciertos"]) == (5, 3)
    assert (d["dentro_muestra"]["n_escalados"], d["dentro_muestra"]["concordancia"]["aciertos"]) == (2, 1)
    assert (d["total"]["n_escalados"], d["total"]["concordancia"]["aciertos"]) == (7, 4)
    assert d["total"]["concordancia"]["valor"] == pytest.approx(4 / 7)
    assert d["umbral"] == 0.90 and d["bandera"] is True
    assert "deriva o ruido relevante" in d["lectura"]


def variante(tmp_path, escenario, preds_fuera, **kw_registro):
    """Cache con las predicciones de L indicadas para el bloque de fuera de muestra."""
    registros = [registro_l(i, "dentro_muestra", p) for i, p in
                 [("R001", SEG), ("R002", SIS), ("R003", SIS), ("R004", SEG)]]
    for i, _, _, _ in FILAS_H_S1:
        registros.append(registro_l(i, "fuera_muestra", preds_fuera[i], **kw_registro.get(i, {})))
    cache = escribir_cache(
        tmp_path / "variante.jsonl",
        {"corpus_hash_dentro": _compute_corpus_hash(escenario["ruta_corpus_dentro"]),
         "corpus_hash_fuera": _compute_corpus_hash(escenario["ruta_corpus_fuera"])},
        registros,
    )
    return ana.construir_documento(cache, **{k: v for k, v in escenario.items() if k != "cache"}, remuestreos=400)


def test_sin_deriva_la_bandera_no_se_levanta(tmp_path, escenario):
    # L repite exactamente la prediccion cacheada de H en los casos escalados.
    preds = {i: p for i, _, p, _ in FILAS_H_S1}
    doc = variante(tmp_path, escenario, preds)
    d = doc["control_deriva"]
    assert d["fuera_muestra"]["concordancia"]["valor"] == pytest.approx(1.0)
    assert d["dentro_muestra"]["concordancia"]["valor"] == pytest.approx(1.0)
    assert d["bandera"] is False and "deriva o ruido relevante" not in d["lectura"]


def test_hipotesis_sostenida_en_un_escenario_sin_discordancias_y_poco_escalado(tmp_path, escenario):
    # L repite las predicciones de H: sin discordancias, delta = 0 sin variabilidad. Como H solo
    # escala un caso de diez, el ahorro de llamadas y costo es material.
    filas = [(i, s, p, "gemini" if i == "I001" else "deterministic") for i, s, p, _ in FILAS_H_S1]
    escribir_hibrido(escenario["ruta_hibrido_fuera"], filas)
    preds = {i: p for i, _, p, _ in FILAS_H_S1}
    doc = variante(tmp_path, escenario, preds)
    assert doc["bloques"]["fuera_muestra"]["decision"]["componente_exactitud"] == "no inferior"
    assert doc["bloques"]["fuera_muestra"]["decision"]["componente_eficiencia"] == "cumplido"
    assert doc["veredicto"]["veredicto"] == "sostenida" and doc["veredicto"]["bloque"] == "fuera_muestra"


def test_hipotesis_no_sostenida_si_el_hibrido_es_claramente_inferior(tmp_path, escenario):
    # H falla siempre; L acierta siempre: delta = -1 sin variabilidad.
    filas = [(i, SEG, SIS, e) for i, _, _, e in FILAS_H_S1]
    escribir_hibrido(escenario["ruta_hibrido_fuera"], filas)
    doc = variante(tmp_path, escenario, {i: SEG for i, _, _, _ in FILAS_H_S1})
    assert doc["bloques"]["fuera_muestra"]["decision"]["componente_exactitud"] == "inferior"
    assert doc["veredicto"]["veredicto"] == "no sostenida"


def test_demasiados_fallos_del_brazo_fuerzan_no_concluyente(tmp_path, escenario):
    preds = {i: p for i, _, p, _ in FILAS_H_S1}
    fallos = {i: {"etapa": "fallback", "error": "respuesta_invalida"} for i in ("I002", "I003")}
    doc = variante(tmp_path, escenario, preds, **fallos)
    b = doc["bloques"]["fuera_muestra"]["eficiencia"]
    assert b["fallbacks_o_errores_l"] == 2 and b["tasa_fallos_l"] == pytest.approx(0.2)
    assert doc["veredicto"]["veredicto"] == "no concluyente" and "fallback" in doc["veredicto"]["motivo"]


def test_un_caso_con_error_del_proveedor_sin_sector_cuenta_como_no_acierto(tmp_path, escenario):
    preds = {i: p for i, _, p, _ in FILAS_H_S1}
    preds["I001"] = None
    doc = variante(tmp_path, escenario, preds, I001={"etapa": "fallback", "error": "GeminiTimeoutError"})
    assert doc["bloques"]["fuera_muestra"]["brazos"]["L"]["exactitud_estricta"]["aciertos"] == 6


def test_los_analisis_secundarios_no_cambian_el_veredicto(tmp_path, escenario):
    doc = documento(escenario)
    primario = doc["bloques"]["fuera_muestra"]["decision"]
    assert doc["veredicto"]["veredicto"] == primario["veredicto"]
    assert "decision" in doc["bloques"]["dentro_muestra"]
    assert "decision" in doc["bloques"]["fuera_muestra"]["sensibilidad_hstar"]


# ---------------------------------------------------------------------------
# Salidas deterministas y CLI
# ---------------------------------------------------------------------------
def test_las_salidas_son_deterministas_con_lf_y_sin_bom(tmp_path, escenario):
    doc = documento(escenario)
    rutas_1 = ana.escribir(doc, tmp_path / "s1")
    rutas_2 = ana.escribir(documento(escenario), tmp_path / "s2")
    for a, b in zip(rutas_1, rutas_2):
        assert a.read_bytes() == b.read_bytes()
        assert b"\r" not in a.read_bytes() and not a.read_bytes().startswith(b"\xef\xbb\xbf")
    assert [r.name for r in rutas_1] == [ana.NOMBRE_JSON, ana.NOMBRE_MD, ana.NOMBRE_SUMAS]


def test_las_sumas_sha256_coinciden_con_los_archivos(tmp_path, escenario):
    rutas = ana.escribir(documento(escenario), tmp_path / "s")
    sumas = rutas[2].read_text(encoding="utf-8").splitlines()
    esperadas = [f"{hashlib.sha256(r.read_bytes()).hexdigest()}  {r.name}" for r in rutas[:2]]
    assert sumas == esperadas


def test_el_markdown_informa_veredicto_deriva_y_el_rotulo_aditivo(tmp_path, escenario):
    doc = documento(escenario)
    _, md = ana.renderizar(doc)
    assert doc["veredicto"]["veredicto"] in md
    assert "deriva o ruido relevante" in md
    assert "aditivas" in md and "dentro de la muestra" in md.lower()
    assert "H*" in md


def argumentos(escenario, salida):
    return [
        "--cache", str(escenario["cache"]), "--salida", str(salida),
        "--corpus-dentro", str(escenario["ruta_corpus_dentro"]), "--corpus-fuera", str(escenario["ruta_corpus_fuera"]),
        "--hibrido-dentro", str(escenario["ruta_hibrido_dentro"]), "--hibrido-fuera", str(escenario["ruta_hibrido_fuera"]),
    ]


def test_cli_con_cache_inexistente_sale_distinto_de_cero_sin_escribir(tmp_path, escenario, capsys):
    salida = tmp_path / "salida"
    args = argumentos(escenario, salida)
    args[1] = str(tmp_path / "no_existe.jsonl")
    codigo = ana.main(args)
    assert codigo != 0
    assert "no existe el cache" in capsys.readouterr().err
    assert not salida.exists()


def test_cli_con_cache_incompleto_sale_con_codigo_1_sin_escribir(tmp_path, escenario, capsys):
    lineas = escenario["cache"].read_text(encoding="utf-8").splitlines()
    escenario["cache"].write_text("\n".join(l for l in lineas if '"I003"' not in l) + "\n", encoding="utf-8")
    salida = tmp_path / "salida"
    assert ana.main(argumentos(escenario, salida)) == 1
    assert "I003" in capsys.readouterr().err and not salida.exists()


def test_cli_ok_escribe_tres_archivos_e_imprime_las_sumas(tmp_path, escenario, capsys):
    salida = tmp_path / "salida"
    assert ana.main(argumentos(escenario, salida)) == 0
    assert sorted(p.name for p in salida.iterdir()) == sorted([ana.NOMBRE_JSON, ana.NOMBRE_MD, ana.NOMBRE_SUMAS])
    assert ana.NOMBRE_JSON in capsys.readouterr().out
