"""Pruebas del clasificador supervisado clasico de linea de base (c-209).

Ciclo TDD: la primera version de este archivo se escribio ANTES que
`evaluation/linea_de_base.py` y fallo por modulo ausente (RED). Cubre la
estructura del documento, las metricas sobre entradas sinteticas, el soporte
por clase, el determinismo byte a byte y la ausencia de red, Gemini y API paga.

Las cifras ancla del conjunto fuera de muestra (n efectivo 103, 47 excluidos)
provienen de c-191/c-205 y NO se recalculan ni se reinterpretan aqui.
"""

from __future__ import annotations

import ast
import json
import pathlib
import socket

import pytest

from evaluation import linea_de_base
from evaluation.corpus import SECTORES_CANONICOS, CasoEvaluacion

SECTORES = list(SECTORES_CANONICOS)


def _caso(caso_id: str, descripcion: str, sector: str) -> CasoEvaluacion:
    return CasoEvaluacion(id=caso_id, descripcion=descripcion, sector_asignado=sector)


@pytest.fixture(scope="module")
def documento() -> dict:
    return linea_de_base.construir_documento()


# ---------------------------------------------------------------------------
# 1.1 / 1.2 — estructura del documento
# ---------------------------------------------------------------------------
def test_documento_estructura_entrenamiento_prueba_y_metricas(documento):
    assert documento["change"] == "c-210-medicion-de-la-linea-de-base"
    assert documento["n_entrenamiento"] == 200
    assert documento["n_prueba"] == 103
    assert documento["excluidos"] == 47
    assert set(documento["variantes"]) == {"balanceada", "sin_repoderacion"}
    for variante in documento["variantes"].values():
        metricas = variante["lectura_muestral"]["metricas"]
        assert {"exactitud_estricta", "exactitud_laxa", "macro_f1", "balanced_accuracy"} <= set(
            metricas
        )
        assert set(metricas["por_clase"]) == set(SECTORES)
        assert sum(d["soporte"] for d in metricas["por_clase"].values()) == 103
    assert documento["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert documento["n_prueba_efectivo_declarado"] == 103
    assert documento["discordantes_excluidos"] == 47


def test_documento_incluye_comparacion_con_el_hibrido_c205(documento):
    comparacion = documento["comparacion_hibrido"]
    assert comparacion["procedencia"].endswith("analisis_fuera_de_muestra_c205.json")
    assert comparacion["n"] == 103
    assert round(comparacion["exactitud_estricta"]["valor"], 4) == 0.8447
    assert round(comparacion["macro_f1"], 4) == 0.7447
    assert round(comparacion["por_clase"]["Sistemas"]["f1"], 4) == 0.2222
    assert round(comparacion["por_clase"]["Bases de Datos"]["f1"], 4) == 0.963
    assert comparacion["por_clase"]["Sistemas"]["soporte"] == 5
    assert comparacion["por_clase"]["Bases de Datos"]["soporte"] == 13


# ---------------------------------------------------------------------------
# 1.3 — triangulacion: metricas sobre entradas sinteticas distintas
# ---------------------------------------------------------------------------
def test_metricas_sinteticas_prediccion_perfecta():
    reales = SECTORES * 2
    predichos = list(reales)
    conjuntos = [frozenset({s}) for s in reales]
    m = linea_de_base.metricas_de_prediccion(reales, predichos, conjuntos)
    assert m["n"] == 10
    assert m["exactitud_estricta"]["valor"] == pytest.approx(1.0)
    assert m["exactitud_laxa"]["valor"] == pytest.approx(1.0)
    assert m["macro_f1"] == pytest.approx(1.0)
    assert m["balanced_accuracy"] == pytest.approx(1.0)


def test_metricas_sinteticas_con_desbalance_difieren_exactitud_y_balanced():
    reales = ["Sistemas"] * 8 + ["Bases de Datos"] * 2
    predichos = ["Sistemas"] * 8 + ["Sistemas"] * 2
    conjuntos = [frozenset({s}) for s in reales]
    m = linea_de_base.metricas_de_prediccion(reales, predichos, conjuntos)
    assert m["exactitud_estricta"]["valor"] == pytest.approx(0.8)
    assert m["balanced_accuracy"] == pytest.approx(0.2)
    assert m["por_clase"]["Sistemas"]["sensibilidad"] == pytest.approx(1.0)
    assert m["por_clase"]["Bases de Datos"]["sensibilidad"] == pytest.approx(0.0)


def test_metricas_sinteticas_soporte_por_clase():
    reales = ["Sistemas", "Sistemas", "Bases de Datos", "Seguridad Informatica"]
    predichos = ["Sistemas", "Bases de Datos", "Bases de Datos", "Seguridad Informatica"]
    conjuntos = [frozenset({s}) for s in reales]
    m = linea_de_base.metricas_de_prediccion(reales, predichos, conjuntos)
    soporte = {c: m["por_clase"][c]["soporte"] for c in SECTORES}
    assert soporte == {
        "Seguridad Informatica": 1,
        "Soporte Tecnico Hardware": 0,
        "Soporte Tecnico Software": 0,
        "Bases de Datos": 1,
        "Sistemas": 2,
    }
    assert sum(soporte.values()) == 4


def test_metricas_clase_de_soporte_cero_aporta_f1_cero_al_macro():
    reales = SECTORES[:4] * 2
    predichos = list(reales)
    conjuntos = [frozenset({s}) for s in reales]
    m = linea_de_base.metricas_de_prediccion(reales, predichos, conjuntos)
    assert m["por_clase"]["Sistemas"]["soporte"] == 0
    assert m["por_clase"]["Sistemas"]["f1"] == 0.0
    assert m["macro_f1"] == pytest.approx(0.8)


def test_metricas_exactitud_laxa_usa_conjunto_de_verdad():
    reales = ["Seguridad Informatica"]
    predichos = ["Soporte Tecnico Software"]
    conjuntos = [frozenset({"Seguridad Informatica", "Soporte Tecnico Software"})]
    m = linea_de_base.metricas_de_prediccion(reales, predichos, conjuntos)
    assert m["exactitud_estricta"]["valor"] == pytest.approx(0.0)
    assert m["exactitud_laxa"]["valor"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 1.4 — determinismo byte a byte
# ---------------------------------------------------------------------------
def test_salidas_deterministas_byte_a_byte(documento, tmp_path):
    h1 = linea_de_base.escribir_salidas(documento, tmp_path)
    bytes_1 = {nombre: (tmp_path / nombre).read_bytes() for nombre in h1}
    h2 = linea_de_base.escribir_salidas(documento, tmp_path)
    assert h1 == h2
    for nombre, contenido in bytes_1.items():
        assert (tmp_path / nombre).read_bytes() == contenido
        assert b"\r\n" not in contenido
        assert not contenido.startswith(b"\xef\xbb\xbf")


def test_dos_construcciones_del_documento_son_identicas():
    a = linea_de_base.construir_documento()
    b = linea_de_base.construir_documento()
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)


def test_sha256_de_archivo_coincide_con_hashlib(tmp_path):
    import hashlib

    ruta = tmp_path / "x.bin"
    ruta.write_bytes(b"linea de base")
    assert linea_de_base.sha256_de_archivo(ruta) == hashlib.sha256(b"linea de base").hexdigest()


# ---------------------------------------------------------------------------
# 1.5 — ausencia de red, Gemini y API paga
# ---------------------------------------------------------------------------
def _modulos_importados(fuente: str) -> set[str]:
    arbol = ast.parse(fuente)
    modulos: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            for alias in nodo.names:
                modulos.add(alias.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.module:
                modulos.add(nodo.module.split(".")[0])
    return modulos


def test_modulo_no_importa_red_gemini_ni_app():
    fuente = pathlib.Path(linea_de_base.__file__).read_text(encoding="utf-8")
    modulos = _modulos_importados(fuente)
    prohibidos = {"google", "requests", "httpx", "urllib", "socket", "aiohttp", "App"}
    assert modulos & prohibidos == set()


def test_ejecucion_no_abre_sockets(monkeypatch):
    def _prohibido(*_args, **_kwargs):
        raise AssertionError("la linea de base no debe abrir conexiones de red")

    monkeypatch.setattr(socket.socket, "connect", _prohibido)
    monkeypatch.setattr(socket, "create_connection", _prohibido)
    entrenamiento = [
        _caso("T1", "No puede ingresar al sistema principal", "Seguridad Informatica"),
        _caso("T2", "La impresora no imprime", "Soporte Tecnico Hardware"),
        _caso("T3", "El sistema se cierra solo", "Soporte Tecnico Software"),
        _caso("T4", "La base de datos no responde", "Bases de Datos"),
        _caso("T5", "El servidor esta caido", "Sistemas"),
    ]
    prueba = [_caso("P1", "No puede ingresar al sistema principal", "Seguridad Informatica")]
    predichos = linea_de_base.predecir(entrenamiento, prueba, class_weight="balanced")
    assert len(predichos) == 1
    assert predichos[0] in SECTORES


# ---------------------------------------------------------------------------
# 2.x — prevalencia natural y lectura ponderada
# ---------------------------------------------------------------------------
def test_prevalencia_natural_del_corpus_de_ajuste(documento):
    prevalencia = documento["prevalencia_natural"]
    assert prevalencia["Soporte Tecnico Hardware"] == pytest.approx(85 / 200)
    assert prevalencia["Soporte Tecnico Software"] == pytest.approx(67 / 200)
    assert prevalencia["Seguridad Informatica"] == pytest.approx(31 / 200)
    assert prevalencia["Sistemas"] == pytest.approx(16 / 200)
    assert prevalencia["Bases de Datos"] == pytest.approx(1 / 200)
    assert sum(prevalencia.values()) == pytest.approx(1.0)


def test_lectura_ponderada_repondera_por_prevalencia():
    por_clase = {
        c: {"precision": 0.0, "sensibilidad": 0.0, "f1": 0.0, "soporte": 0} for c in SECTORES
    }
    por_clase["Sistemas"] = {"precision": 0.5, "sensibilidad": 1.0, "f1": 0.4, "soporte": 10}
    por_clase["Bases de Datos"] = {
        "precision": 1.0,
        "sensibilidad": 0.0,
        "f1": 0.2,
        "soporte": 5,
    }
    prevalencia = {c: 0.0 for c in SECTORES}
    prevalencia["Sistemas"] = 0.75
    prevalencia["Bases de Datos"] = 0.25
    ponderada = linea_de_base.lectura_ponderada(por_clase, prevalencia)
    assert ponderada["macro_f1"] == pytest.approx(0.75 * 0.4 + 0.25 * 0.2)
    assert ponderada["balanced_accuracy"] == pytest.approx(0.75 * 1.0 + 0.25 * 0.0)
    assert ponderada["precision"] == pytest.approx(0.75 * 0.5 + 0.25 * 1.0)


def test_documento_trae_ambas_lecturas_rotuladas(documento):
    for variante in documento["variantes"].values():
        muestral = variante["lectura_muestral"]
        ponderada = variante["lectura_ponderada_prevalencia_natural"]
        assert muestral["rotulo"]
        assert muestral["procedencia"]
        assert ponderada["rotulo"]
        assert ponderada["procedencia"]


# ---------------------------------------------------------------------------
# 2.4 — CLI
# ---------------------------------------------------------------------------
def test_cli_escribe_json_markdown_y_sums(tmp_path):
    codigo = linea_de_base.main(["--salida", str(tmp_path)])
    assert codigo == 0
    assert (tmp_path / "linea_de_base_clasica_c210.json").exists()
    assert (tmp_path / "linea_de_base_clasica_c210.md").exists()
    assert (tmp_path / "SHA256SUMS.txt").exists()
    sums = (tmp_path / "SHA256SUMS.txt").read_text(encoding="utf-8")
    assert "linea_de_base_clasica_c210.json" in sums
    assert "linea_de_base_clasica_c210.md" in sums
