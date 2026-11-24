"""Pruebas del recomputo por regimen y de la sonda de latencia (c-249, D6).

TDD estricto de las funciones puras con casos sinteticos (sin red, sin base de datos y
sin invocar al modelo) mas la escritura determinista de las salidas. Cubre el conteo de
aciertos por canal y por regimen, el intervalo de Wilson, las proporciones 25/200 y
25/147 con su binomial unilateral frente a 0,15 y la extraccion del p95 del nivel 5 de
N8N en ambas corridas y del subconjunto deterministico de la ampliada.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_regimen_c249 as c249  # noqa: E402


CASOS = [
    {"id": "R001", "canal_origen": "correo electrónico", "sector_asignado": "Sistemas"},
    {"id": "R002", "canal_origen": "formulario web", "sector_asignado": "Sistemas"},
    {"id": "R003", "canal_origen": "llamada telefónica", "sector_asignado": "Bases de Datos"},
    {"id": "R004", "canal_origen": "correo electrónico", "sector_asignado": "Sistemas"},
]

PREDICCIONES = [
    {"caso_id": "R001", "sector_asignado": "Sistemas", "sector_predicho": "Sistemas"},
    {"caso_id": "R002", "sector_asignado": "Sistemas", "sector_predicho": "Soporte Tecnico Software"},
    {"caso_id": "R003", "sector_asignado": "Bases de Datos", "sector_predicho": "Bases de Datos"},
    {"caso_id": "R004", "sector_asignado": "Sistemas", "sector_predicho": "Sistemas"},
]


def _carga(p95_n5: float, det_n5: float | None = None) -> dict:
    """Estructura minima de una corrida de carga, con los niveles 1 y 5."""
    return {
        "capas": {
            "n8n": {
                "niveles": [
                    {"concurrencia": 1, "p95_ms": 100.0},
                    {
                        "concurrencia": 5,
                        "p95_ms": p95_n5,
                        "inferencia": {"deterministico": {"p95_ms": det_n5}},
                    },
                ]
            }
        }
    }


def _intervenciones(cambios: int, confirmaciones: int) -> list[dict]:
    return [{"cambio_sector": "true"}] * cambios + [{"cambio_sector": "false"}] * confirmaciones


# ---------------------------------------------------------------------------
# Exactitud por canal
# ---------------------------------------------------------------------------
def test_exactitud_por_canal_cuenta_aciertos():
    r = c249.exactitud_por_canal(CASOS, PREDICCIONES)
    assert r["correo electrónico"]["aciertos"] == 2
    assert r["correo electrónico"]["total"] == 2
    assert r["formulario web"]["aciertos"] == 0
    assert r["formulario web"]["total"] == 1
    assert r["llamada telefónica"]["aciertos"] == 1


def test_exactitud_por_canal_proporcion_e_intervalo():
    r = c249.exactitud_por_canal(CASOS, PREDICCIONES)
    assert r["formulario web"]["proporcion"] == pytest.approx(0.0)
    lo, hi = r["formulario web"]["ic95"]
    assert 0.0 <= lo <= hi <= 1.0
    assert r["correo electrónico"]["proporcion"] == pytest.approx(1.0)


def test_exactitud_por_canal_ignora_casos_sin_prediccion():
    r = c249.exactitud_por_canal(CASOS, PREDICCIONES[:2])
    assert r["llamada telefónica"]["total"] == 0
    assert r["llamada telefónica"]["proporcion"] is None


# ---------------------------------------------------------------------------
# Exactitud por regimen
# ---------------------------------------------------------------------------
def test_exactitud_por_regimen_agrega_a_y_b():
    r = c249.exactitud_por_regimen(CASOS, PREDICCIONES)
    assert (r["a"]["aciertos"], r["a"]["total"]) == (2, 3)
    assert (r["b"]["aciertos"], r["b"]["total"]) == (1, 1)
    assert r["a"]["proporcion"] == pytest.approx(2 / 3)


def test_exactitud_por_regimen_sin_casos_del_regimen_b():
    r = c249.exactitud_por_regimen(CASOS[:2], PREDICCIONES[:2])
    assert r["b"]["total"] == 0
    assert r["b"]["proporcion"] is None
    assert r["b"]["ic95"] is None


# ---------------------------------------------------------------------------
# Intervencion manual
# ---------------------------------------------------------------------------
def test_intervencion_manual_proporciones_200_y_147():
    r = c249.intervencion_manual(_intervenciones(2, 8), n_corpus=20)
    assert r["cambio_total"] == 2
    assert r["revisados"] == 10
    assert r["proporcion_200"]["denominador"] == 20
    assert r["proporcion_200"]["proporcion"] == pytest.approx(0.10)
    assert r["proporcion_147"]["denominador"] == 10
    assert r["proporcion_147"]["proporcion"] == pytest.approx(0.20)


def test_intervencion_manual_binomial_unilateral():
    r = c249.intervencion_manual(_intervenciones(2, 8), n_corpus=20)
    assert r["cota"] == pytest.approx(0.15)
    assert r["alternativa"] == "greater"
    assert 0.0 <= r["binomial_p"] <= 1.0


def test_intervencion_manual_sin_cambios():
    r = c249.intervencion_manual(_intervenciones(0, 10), n_corpus=20)
    assert r["proporcion_200"]["proporcion"] == pytest.approx(0.0)
    assert r["proporcion_147"]["proporcion"] == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Sonda de latencia
# ---------------------------------------------------------------------------
def test_p95_sonda_extrae_el_nivel_5():
    r = c249.p95_sonda(_carga(3660.4, 5024.7), _carga(7545.7, 5024.7))
    assert r["original_n5"] == pytest.approx(3660.4)
    assert r["ampliada_n5"] == pytest.approx(7545.7)
    assert r["ampliada_det_n5"] == pytest.approx(5024.7)


def test_p95_sonda_sin_nivel_5_falla():
    vacia = {"capas": {"n8n": {"niveles": [{"concurrencia": 1, "p95_ms": 1.0}]}}}
    with pytest.raises(ValueError):
        c249.p95_sonda(vacia, vacia)


def test_p95_sonda_sin_subconjunto_deterministico():
    r = c249.p95_sonda(_carga(3660.4), _carga(7545.7))
    assert r["ampliada_det_n5"] is None


# ---------------------------------------------------------------------------
# Resultado y escritura determinista
# ---------------------------------------------------------------------------
def _resultado_sintetico() -> dict:
    return c249.construir_resultado(
        casos=CASOS,
        predicciones=PREDICCIONES,
        intervenciones=_intervenciones(2, 8),
        n_corpus=20,
        original=_carga(3660.4, 5024.7),
        ampliada=_carga(7545.7, 5024.7),
        rutas_entrada={"corpus": "sintetico"},
    )


def test_construir_resultado_incluye_las_cuatro_secciones():
    r = _resultado_sintetico()
    assert set(r) >= {"schema_version", "exactitud_por_canal", "exactitud_por_regimen",
                      "intervencion_manual", "sonda_nivel_5", "entradas"}


def test_escritura_determinista(tmp_path):
    r = _resultado_sintetico()
    a = c249.escribir_salidas(r, tmp_path / "a")
    b = c249.escribir_salidas(r, tmp_path / "b")
    for pa, pb in zip(a, b):
        assert pa.name == pb.name
        assert pa.read_bytes() == pb.read_bytes()


def test_escritura_emite_json_md_y_suma(tmp_path):
    rutas = c249.escribir_salidas(_resultado_sintetico(), tmp_path)
    nombres = [p.name for p in rutas]
    assert any(n.endswith(".json") for n in nombres)
    assert any(n.endswith(".md") for n in nombres)
    assert any(n.endswith(".SHA256SUMS.txt") for n in nombres)