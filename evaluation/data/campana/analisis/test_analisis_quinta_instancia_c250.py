"""Pruebas del recomputo de la asimetria telefonica y de la sub-hipotesis 1 sin
telefonia (c-250, D6).

TDD estricto de las funciones puras con datos sinteticos (sin red, sin base de datos y sin
invocar al modelo) mas la escritura determinista de las salidas. Cubre:

- la mediana y la media de ``duracion_segundos`` (grabacion cruda) frente a ``t_e2e_s``
  (grabacion mas procesamiento) de las 81 grabaciones telefonicas;
- la desagregacion sin telefonia (correo electronico + formulario web) con su diferencia
  pareada y su intervalo bootstrap;
- la reduccion sin telefonia (media manual -> media automatizada) con su intervalo;
- el contraste de Wilcoxon sobre las diferencias pareadas sin telefonia (lectura
  suplementaria, no el contraste primario).
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_quinta_instancia_c250 as c250  # noqa: E402


FILAS_TELEFONIA = [
    {"case_id": "R002", "duracion_segundos": 6, "t_e2e_s": 19.012},
    {"case_id": "R003", "duracion_segundos": 7, "t_e2e_s": 18.698},
    {"case_id": "R004", "duracion_segundos": 5, "t_e2e_s": 20.5},
]

CASOS_WEB = [
    {"id": "R001", "canal_origen": "correo electrónico", "tiempo_manual_s": 75.0, "tiempo_automatizado_s": 21.0},
    {"id": "R002", "canal_origen": "formulario web", "tiempo_manual_s": 40.0, "tiempo_automatizado_s": 1.8},
    {"id": "R003", "canal_origen": "llamada telefónica", "tiempo_manual_s": 90.0, "tiempo_automatizado_s": 20.0},
    {"id": "R004", "canal_origen": "correo electrónico", "tiempo_manual_s": 50.0, "tiempo_automatizado_s": 2.0},
]


# ---------------------------------------------------------------------------
# Telefonia: mediana y media de duracion_segundos vs t_e2e_s
# ---------------------------------------------------------------------------
def test_telefonia_mediana_media_duracion():
    r = c250.telefonia_duraciones(FILAS_TELEFONIA)
    d = r["duracion_segundos"]
    assert r["n"] == 3
    assert d["media"] == pytest.approx(6.0)
    assert d["mediana"] == 6.0
    assert d["min"] == 5.0
    assert d["max"] == 7.0


def test_telefonia_media_t_e2e():
    r = c250.telefonia_duraciones(FILAS_TELEFONIA)
    e = r["t_e2e_s"]
    assert e["media"] == pytest.approx((19.012 + 18.698 + 20.5) / 3, abs=1e-3)
    assert e["mediana"] == pytest.approx(19.012, abs=1e-3)


def test_telefonia_distinta_duracion_y_t_e2e():
    r = c250.telefonia_duraciones(FILAS_TELEFONIA)
    assert r["duracion_segundos"]["media"] != pytest.approx(r["t_e2e_s"]["media"])


def test_telefonia_sin_grabacion_t_e2e_s_opcional():
    filas = FILAS_TELEFONIA + [{"case_id": "R005", "duracion_segundos": 8}]
    r = c250.telefonia_duraciones(filas)
    assert r["n"] == 4
    assert r["duracion_segundos"]["media"] == pytest.approx(6.5)
    # t_e2e_s se calcula solo sobre los registros que lo tienen
    assert r["t_e2e_s"]["n"] == 3


def test_telefonia_vacia():
    r = c250.telefonia_duraciones([])
    assert r["n"] == 0
    assert r["duracion_segundos"]["media"] is None
    assert r["duracion_segundos"]["mediana"] is None
    assert r["t_e2e_s"]["media"] is None


# ---------------------------------------------------------------------------
# Sin telefonia: pares correo+formulario, diferencia pareada y reduccion
# ---------------------------------------------------------------------------
def test_sin_telefonia_filtra_canal():
    manual, auto = c250.pares_web(CASOS_WEB)
    assert len(manual) == 3  # R001, R002, R004 (excluye la llamada)
    assert list(manual) == [75.0, 40.0, 50.0]
    assert list(auto) == [21.0, 1.8, 2.0]


def test_sin_telefonia_medias():
    r = c250.sin_telefonia(CASOS_WEB)
    assert r["n"] == 3
    assert r["media_manual_s"] == pytest.approx((75.0 + 40.0 + 50.0) / 3, abs=1e-3)
    assert r["media_automatizada_s"] == pytest.approx((21.0 + 1.8 + 2.0) / 3, abs=1e-3)


def test_sin_telefonia_reduccion_puntual():
    r = c250.sin_telefonia(CASOS_WEB)
    manual = (75.0 + 40.0 + 50.0) / 3
    auto = (21.0 + 1.8 + 2.0) / 3
    esperado = (manual - auto) / manual
    assert r["reduccion"]["puntual"] == pytest.approx(esperado)


def test_sin_telefonia_diferencia_pareada_media():
    r = c250.sin_telefonia(CASOS_WEB)
    difs = [75.0 - 21.0, 40.0 - 1.8, 50.0 - 2.0]
    assert r["diferencia_pareada"]["media_s"] == pytest.approx(sum(difs) / 3)


def test_sin_telefonia_intervalo_reduccion_dentro_de_rango():
    r = c250.sin_telefonia(CASOS_WEB)
    lo, hi = r["reduccion"]["ic95"]
    assert 0.0 <= lo <= r["reduccion"]["puntual"] <= hi <= 1.0


def test_sin_telefonia_intervalo_diferencia_dentro_de_rango():
    r = c250.sin_telefonia(CASOS_WEB)
    lo, hi = r["diferencia_pareada"]["ic95"]
    assert lo <= r["diferencia_pareada"]["media_s"] <= hi


def test_sin_telefonia_wilcoxon_presente():
    r = c250.sin_telefonia(CASOS_WEB)
    assert 0.0 <= r["wilcoxon"]["p"] <= 1.0
    assert r["wilcoxon"]["T"] >= 0


def test_sin_telefonia_sin_casos_web():
    r = c250.sin_telefonia(
        [
            {"id": "X", "canal_origen": "llamada telefónica", "tiempo_manual_s": 10, "tiempo_automatizado_s": 5},
        ]
    )
    assert r["n"] == 0
    assert r["media_manual_s"] is None
    assert r["reduccion"]["puntual"] is None
    assert r["reduccion"]["ic95"] is None


# ---------------------------------------------------------------------------
# Resultado y escritura determinista
# ---------------------------------------------------------------------------
def _resultado_sintetico() -> dict:
    return c250.construir_resultado(
        filas_telefonia=FILAS_TELEFONIA,
        casos=CASOS_WEB,
        rutas_entrada={"data/ejemplo": "00000000"},
    )


def test_construir_resultado_tiene_secciones():
    r = _resultado_sintetico()
    assert set(r) >= {"schema_version", "telefonia", "sin_telefonia", "metodo", "entradas"}


def test_escritura_determinista(tmp_path):
    r = _resultado_sintetico()
    a = c250.escribir_salidas(r, tmp_path / "a")
    b = c250.escribir_salidas(r, tmp_path / "b")
    for pa, pb in zip(a, b):
        assert pa.name == pb.name
        assert pa.read_bytes() == pb.read_bytes()


def test_escritura_emite_json_md_y_suma(tmp_path):
    rutas = c250.escribir_salidas(_resultado_sintetico(), tmp_path)
    nombres = [p.name for p in rutas]
    assert any(n.endswith(".json") for n in nombres)
    assert any(n.endswith(".md") for n in nombres)
    assert any(n.endswith(".SHA256SUMS.txt") for n in nombres)
