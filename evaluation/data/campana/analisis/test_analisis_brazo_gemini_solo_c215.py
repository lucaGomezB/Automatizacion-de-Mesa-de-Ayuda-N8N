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
