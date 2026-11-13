"""Pruebas del analisis de calibracion y punto de operacion del gate (c-214)."""

from __future__ import annotations

import hashlib
import json
import math
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_calibracion_gate_c214 as c214  # noqa: E402


# --- bloques por senal ------------------------------------------------------------------
def test_bloque_senal_fiabilidad_por_valor_y_metricas_resumen():
    senales = [0.85, 0.85, 0.95, 0.95, 0.95, 0.95]
    aciertos = [True, False, True, True, True, False]
    b = c214.bloque_senal(senales, aciertos)
    assert b["n"] == 6 and b["aciertos"] == 4
    assert [(f["valor"], f["casos"], f["aciertos"]) for f in b["fiabilidad"]] == [
        (0.85, 2, 1),
        (0.95, 4, 3),
    ]
    assert b["fiabilidad"][1]["exactitud"] == pytest.approx(0.75)
    assert b["sobreconfianza"]["valor"] == pytest.approx((0.85 * 2 + 0.95 * 4) / 6 - 4 / 6)
    assert b["brier"]["valor"] == pytest.approx((0.15**2 + 0.85**2 + 3 * 0.05**2 + 0.95**2) / 6)
    assert 0.0 <= b["ece"]["valor"] <= 1.0


def test_bloque_senal_con_una_sola_clase_deja_el_auroc_sin_definir():
    b = c214.bloque_senal([0.9, 0.9, 0.8], [True, True, True])
    assert b["auroc"]["valor"] is None and b["auroc"]["ic"] is None


def test_distribucion_de_valores_cuenta_cada_nivel():
    assert c214.distribucion_valores([0.9, 0.85, 0.9, 0.98]) == {"0.85": 1, "0.9": 2, "0.98": 1}


# --- umbrales de S2 -----------------------------------------------------------------------
def test_umbrales_s2_por_rango_de_posicion():
    assert c214.umbrales_s2([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]) == [0.0, 0.2, 0.4, 0.6, math.inf]
    assert c214.umbrales_s2([0.5, 0.1, 0.3, 0.2, 0.4]) == [0.0, 0.2, 0.3, 0.4, math.inf]


# --- evaluacion de una politica -----------------------------------------------------------
def _datos(aciertos_alto, errores_alto, aciertos_bajo, errores_bajo, alto=0.9, bajo=0.5):
    senales = [alto] * (aciertos_alto + errores_alto) + [bajo] * (aciertos_bajo + errores_bajo)
    aciertos = (
        [True] * aciertos_alto + [False] * errores_alto + [True] * aciertos_bajo + [False] * errores_bajo
    )
    return senales, aciertos


def test_evaluar_politica_selecciona_en_la_muestra_y_confirma_fuera():
    dentro = _datos(18, 2, 2, 8)
    fuera = _datos(11, 1, 1, 4)
    r = c214.evaluar_politica(
        dentro, fuera, [0.0, 0.8, math.inf], piso=0.85, n_total=(30, 17)
    )
    assert r["umbral_seleccionado"] == 0.8
    assert r["fuera_de_muestra"]["veredicto"] == "confirmado"
    assert len(r["barrido_dentro"]) == 3 and len(r["barrido_fuera_descriptivo"]) == 3


def test_evaluar_politica_sin_umbral_dentro_no_elige_con_datos_fuera():
    dentro = _datos(5, 5, 0, 10)
    fuera = _datos(20, 0, 0, 0)  # fuera de la muestra seria perfecto, pero no se reelige
    r = c214.evaluar_politica(dentro, fuera, [0.0, 0.8, math.inf], piso=0.85, n_total=(20, 20))
    assert r["umbral_seleccionado"] is None
    assert r["fuera_de_muestra"]["veredicto"] == "sin umbral seleccionado"
    assert "no sostiene" in r["lectura"]


def test_evaluar_politica_no_confirmado_fuera_de_muestra():
    dentro = _datos(18, 2, 2, 8)
    fuera = _datos(6, 6, 0, 2)
    r = c214.evaluar_politica(dentro, fuera, [0.0, 0.8, math.inf], piso=0.85, n_total=(30, 14))
    assert r["umbral_seleccionado"] == 0.8
    assert r["fuera_de_muestra"]["veredicto"] == "no confirmado"


# --- artefactos reales ---------------------------------------------------------------------
@pytest.fixture(scope="module")
def documento():
    return c214.construir_documento()


def test_documento_trae_los_bloques_prerregistrados(documento):
    assert documento["reproduccion_reglas"] == {
        "dentro_muestra": {"cortocircuitados": 131, "total": 200},
        "fuera_muestra": {"cortocircuitados": 69, "total": 103},
    }
    for corpus, n, escalados in (("dentro_muestra", 200, 69), ("fuera_muestra", 103, 34)):
        c = documento["corpora"][corpus]
        assert c["n"] == n
        assert c["etapas"]["gemini"]["confianza"]["n"] == escalados
        assert set(c["etapas"]["deterministic"]) == {"confianza", "score_correctitud"}
    assert set(documento["politicas"]) == {"confianza_gemini", "s1_acuerdo_entre_etapas", "s2_score_reglas"}
    for politica in documento["politicas"].values():
        assert set(politica) == {"piso_0.85", "piso_0.8278"}
    assert documento["secundarios"]["brazo_gemini_solo"].startswith("no ejecutado")
    assert documento["secundarios"]["corpus_arbitrado_c206"].startswith("no ejecutado")
    assert documento["gobernanza"]["cambia_configuracion"] is False


def test_dos_construcciones_dan_el_mismo_sha256(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    a.mkdir(), b.mkdir()
    c214.escribir(c214.construir_documento(), a)
    c214.escribir(c214.construir_documento(), b)
    for nombre in ("analisis_calibracion_gate_c214.json", "analisis_calibracion_gate_c214.md"):
        assert (a / nombre).read_bytes() == (b / nombre).read_bytes()
        assert b"\r" not in (a / nombre).read_bytes()
        assert not (a / nombre).read_bytes().startswith(b"\xef\xbb\xbf")


def test_csv_de_senales_tiene_una_fila_por_caso_y_lf():
    contenido = c214.RUTA_SENALES.read_bytes()
    assert b"\r" not in contenido
    filas = contenido.decode("utf-8").splitlines()
    assert filas[0] == "caso_id,corpus,score_correctitud,sector_reglas,acuerdo_con_gemini"
    assert len(filas) - 1 == 303
    assert sum(1 for f in filas[1:] if f.split(",")[1] == "dentro_muestra") == 200


def test_el_json_serializa_infinito_como_texto(documento):
    texto = json.dumps(c214.a_json_seguro(documento), allow_nan=False)
    assert '"inf"' in texto


def test_sha256_del_csv_coincide_con_el_registrado_en_el_readme():
    readme = (c214.CAMPANA / "README.md").read_text(encoding="utf-8")
    assert hashlib.sha256(c214.RUTA_SENALES.read_bytes()).hexdigest() in readme
