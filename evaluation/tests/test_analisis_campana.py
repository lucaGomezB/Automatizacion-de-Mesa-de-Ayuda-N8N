"""
Tests del CLI de solo lectura del analisis de campana (c-167, seccion 8).

El CLI `evaluation/analisis_campana.py` lee las entradas (planilla C1, registro de sujetos
C2, export C5, plan C6, corpus de campana, predicciones in-sample y fuera de muestra C9),
re-verifica lo minimo, delega en las funciones puras de `evaluation/campana.py` y
`evaluation/kappa.py` y escribe SOLO `resultados.json`, `resultados.md` y `SHA256SUMS.txt`
en la carpeta de salida. Todo corre offline sobre los fixtures SINTETICOS
(`tests/fixtures/campana/`, ver `tests/fixtures/README.md`), con la red bloqueada.
"""

from __future__ import annotations

import csv
import json
import pathlib
import shutil
import socket

import pytest

from evaluation import analisis_campana
from evaluation.tests import helpers_campana as h

SALIDAS = ("resultados.json", "resultados.md", "SHA256SUMS.txt")

#: Entradas que el CLI espera encontrar por nombre canonico dentro de --entrada.
FIXTURES_ENTRADA: dict[str, pathlib.Path] = {
    "plantilla_etiquetado.csv": h.PLANILLA,
    "registro_sujetos.csv": h.REGISTRO_SUJETOS,
    "intervenciones.csv": h.INTERVENCIONES,
    "plan_campana.csv": h.PLAN,
    "corpus_campana.json": h.CORPUS_CAMPANA,
    "predicciones_in_sample.json": h.PREDICCIONES_IN_SAMPLE,
    "predicciones_independiente.json": h.PREDICCIONES_INDEPENDIENTE,
    "corpus_independiente.json": h.CORPUS_INDEPENDIENTE,
}


def _preparar_entrada(destino: pathlib.Path, omitir: tuple[str, ...] = ()) -> pathlib.Path:
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, origen in FIXTURES_ENTRADA.items():
        if nombre in omitir:
            continue
        shutil.copyfile(origen, destino / nombre)
    return destino


def _argumentos(entrada: pathlib.Path, salida: pathlib.Path) -> list[str]:
    return [
        "--entrada",
        str(entrada),
        "--salida",
        str(salida),
        "--pines-in-sample",
        json.dumps(h.PINES_IN_SAMPLE),
        "--rango-google-genai-vigente",
        h.RANGO_VIGENTE_GOOGLE_GENAI,
    ]


def _archivos_bajo(raiz: pathlib.Path) -> set[pathlib.Path]:
    return {ruta for ruta in raiz.rglob("*") if ruta.is_file()}


def _bloquear_red(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prohibe abrir cualquier socket: el analisis es offline."""

    def _prohibido(*args: object, **kwargs: object) -> None:
        raise AssertionError("el CLI de solo lectura no debe abrir conexiones de red")

    monkeypatch.setattr(socket, "socket", _prohibido)
    monkeypatch.setattr(socket, "create_connection", _prohibido)


# ---------------------------------------------------------------------------
# 8.1 — RED: end-to-end sobre los fixtures, con la red bloqueada
# ---------------------------------------------------------------------------
def test_el_cli_escribe_solo_las_tres_salidas_con_la_red_bloqueada(tmp_path, monkeypatch):
    entrada = _preparar_entrada(tmp_path / "entrada")
    salida = tmp_path / "salida"
    antes = _archivos_bajo(tmp_path)
    _bloquear_red(monkeypatch)

    codigo = analisis_campana.main(_argumentos(entrada, salida))

    assert codigo == 0
    assert sorted(ruta.name for ruta in salida.iterdir()) == sorted(SALIDAS)
    assert _archivos_bajo(tmp_path) - antes == {salida / nombre for nombre in SALIDAS}


def test_el_cli_reporta_las_cinco_secciones_y_la_referencia_usada(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada")
    salida = tmp_path / "salida"

    analisis_campana.main(_argumentos(entrada, salida))

    documento = json.loads((salida / "resultados.json").read_text(encoding="utf-8"))
    assert documento["referencia_usada"] == "consenso_doble_etiquetado"
    assert set(documento["secciones"]) == {
        "kappa",
        "exactitud_brazo_manual",
        "intervencion",
        "orden",
        "fuera_de_muestra",
    }
    assert all(seccion["obtenido"] for seccion in documento["secciones"].values())
    assert documento["secciones"]["kappa"]["resultado"]["kappa"] == pytest.approx(
        0.7922077922077922, abs=1e-12
    )


# ---------------------------------------------------------------------------
# 8.3 — Triangular: dataset ausente y columna faltante
# ---------------------------------------------------------------------------
def test_sin_intervenciones_la_seccion_se_declara_no_obtenida_y_lo_demas_se_reporta(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada", omitir=("intervenciones.csv",))
    salida = tmp_path / "salida"

    codigo = analisis_campana.main(_argumentos(entrada, salida))

    assert codigo == 0
    documento = json.loads((salida / "resultados.json").read_text(encoding="utf-8"))
    assert documento["secciones"]["intervencion"]["obtenido"] is False
    assert "intervenciones.csv" in documento["secciones"]["intervencion"]["motivo"]
    assert documento["secciones"]["kappa"]["obtenido"] is True
    assert documento["secciones"]["exactitud_brazo_manual"]["obtenido"] is True
    markdown = (salida / "resultados.md").read_text(encoding="utf-8")
    assert "Intervencion" in markdown and "no se obtuvo" in markdown


def _sin_columna(origen: pathlib.Path, destino: pathlib.Path, columna: str) -> pathlib.Path:
    with origen.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.reader(archivo))
    indice = filas[0].index(columna)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.writer(archivo)
        for fila in filas:
            escritor.writerow([valor for posicion, valor in enumerate(fila) if posicion != indice])
    return destino


def test_una_columna_inicio_faltante_falla_nombrando_el_archivo_y_la_columna(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada")
    _sin_columna(h.PLANILLA, entrada / "plantilla_etiquetado.csv", "inicio")
    salida = tmp_path / "salida"

    with pytest.raises(analisis_campana.ErrorDeEntrada) as excinfo:
        analisis_campana.main(_argumentos(entrada, salida))

    mensaje = str(excinfo.value)
    assert "plantilla_etiquetado.csv" in mensaje
    assert "inicio" in mensaje
    assert not salida.exists()


# ---------------------------------------------------------------------------
# 8.4 — Reproducibilidad: dos corridas byte a byte identicas
# ---------------------------------------------------------------------------
def test_dos_corridas_producen_json_y_suma_identicos(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada")
    salida_1 = tmp_path / "salida_1"
    salida_2 = tmp_path / "salida_2"

    analisis_campana.main(_argumentos(entrada, salida_1))
    analisis_campana.main(_argumentos(entrada, salida_2))

    for nombre in ("resultados.json", "resultados.md", "SHA256SUMS.txt"):
        assert (salida_1 / nombre).read_bytes() == (salida_2 / nombre).read_bytes()


def test_la_suma_de_comprobacion_cubre_salidas_y_entradas_leidas(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada")
    salida = tmp_path / "salida"

    analisis_campana.main(_argumentos(entrada, salida))

    lineas = (salida / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    nombres = {linea.split("  ", 1)[1] for linea in lineas}
    assert {"resultados.json", "resultados.md"} <= nombres
    assert {"plantilla_etiquetado.csv", "plan_campana.csv", "corpus_campana.json"} <= nombres


def _secciones(salida: pathlib.Path) -> dict[str, dict]:
    documento = json.loads((salida / "resultados.json").read_text(encoding="utf-8"))
    return documento["secciones"]


# ---------------------------------------------------------------------------
# 8.3 — Triangular (casos adicionales): cada dataset ausente detiene solo su seccion
# ---------------------------------------------------------------------------
def test_sin_plan_de_campana_orden_e_intervencion_se_declaran_no_obtenidas(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada", omitir=("plan_campana.csv",))
    salida = tmp_path / "salida"

    assert analisis_campana.main(_argumentos(entrada, salida)) == 0

    secciones = _secciones(salida)
    assert secciones["orden"]["obtenido"] is False
    assert "plan_campana.csv" in secciones["orden"]["motivo"]
    assert secciones["intervencion"]["obtenido"] is False
    assert "plan_campana.csv" in secciones["intervencion"]["motivo"]
    assert secciones["kappa"]["obtenido"] is True
    assert secciones["exactitud_brazo_manual"]["obtenido"] is True


def test_sin_registro_de_sujetos_la_exactitud_se_declara_no_obtenida_y_el_kappa_se_reporta(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada", omitir=("registro_sujetos.csv",))
    salida = tmp_path / "salida"

    assert analisis_campana.main(_argumentos(entrada, salida)) == 0

    secciones = _secciones(salida)
    assert secciones["exactitud_brazo_manual"]["obtenido"] is False
    assert "registro_sujetos.csv" in secciones["exactitud_brazo_manual"]["motivo"]
    assert secciones["kappa"]["obtenido"] is True


def test_sin_corpus_independiente_la_evaluacion_fuera_de_muestra_se_declara_no_obtenida(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada", omitir=("corpus_independiente.json",))
    salida = tmp_path / "salida"

    assert analisis_campana.main(_argumentos(entrada, salida)) == 0

    seccion = _secciones(salida)["fuera_de_muestra"]
    assert seccion["obtenido"] is False
    assert "fuera de muestra" in seccion["motivo"]


def test_pines_del_cache_independiente_distintos_no_reportan_metricas_fuera_de_muestra(tmp_path):
    entrada = _preparar_entrada(
        tmp_path / "entrada",
        omitir=("predicciones_independiente.json",),
    )
    shutil.copyfile(h.PREDICCIONES_INDEPENDIENTE_PINES, entrada / "predicciones_independiente.json")
    salida = tmp_path / "salida"

    assert analisis_campana.main(_argumentos(entrada, salida)) == 0

    seccion = _secciones(salida)["fuera_de_muestra"]
    assert seccion["obtenido"] is False
    assert "modelo distinto" in seccion["motivo"]


def test_la_referencia_original_se_rotula_y_usa_el_corpus_de_campana(tmp_path):
    entrada = _preparar_entrada(tmp_path / "entrada")
    salida = tmp_path / "salida"

    argumentos = _argumentos(entrada, salida) + ["--referencia", "consenso_original"]
    analisis_campana.main(argumentos)

    documento = json.loads((salida / "resultados.json").read_text(encoding="utf-8"))
    assert documento["referencia_usada"] == "consenso_original"
    assert documento["secciones"]["exactitud_brazo_manual"]["resultado"]["referencia_usada"] == (
        "consenso_original"
    )
