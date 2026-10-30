"""
Tests del helper que ensambla las dos entradas del analisis de campana (c-170, ECM-011..013).

`evaluation/preparar_entradas_analisis.py` produce, offline y de solo lectura sobre sus
fuentes, `plantilla_etiquetado.csv` (union C1 de `doble_etiquetado.csv` + `brazo_manual.csv`)
y `predicciones_in_sample.json` (copia byte a byte del cache congelado de v9). Todo corre
sobre fixtures SINTETICOS (`tests/fixtures/`, ver `tests/fixtures/README.md`), con la red
bloqueada.
"""

from __future__ import annotations

import csv
import hashlib
import pathlib
import shutil
import socket

import pytest

from evaluation import preparar_entradas_analisis as preparar
from evaluation.corpus import cargar_corpus

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parents[1]
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
CORPUS = FIXTURES / "corpus_fixture.json"
DOBLE = FIXTURES / "campana" / "doble_etiquetado_fixture.csv"
CACHE_CONGELADO = RAIZ_EVALUATION / "evidence" / "predicciones_hybrid-v3_2026-10-07.json"


def _sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _escribir_csv(ruta: pathlib.Path, filas: list[dict[str, str]]) -> pathlib.Path:
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(
            archivo, fieldnames=list(preparar.COLUMNAS_C1), lineterminator="\n"
        )
        escritor.writeheader()
        escritor.writerows(filas)
    return ruta


def _derivar_brazo(origen: pathlib.Path, destino: pathlib.Path) -> pathlib.Path:
    """Deriva una planilla `brazo_manual` valida de la de `doble_etiquetado`."""
    with origen.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    nuevas = []
    for fila in filas:
        nueva = dict(fila)
        nueva["tarea"] = "brazo_manual"
        nueva["id_etiquetador"] = {"E1": "O1", "E2": "O2"}[fila["id_etiquetador"]]
        nueva["inicio"] = fila["inicio"] or fila["timestamp"]
        nuevas.append(nueva)
    return _escribir_csv(destino, nuevas)


def _preparar_fuentes(entrada: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, pathlib.Path]:
    entrada.mkdir(parents=True, exist_ok=True)
    corpus = entrada / "corpus.json"
    shutil.copyfile(CORPUS, corpus)
    doble = entrada / "doble_etiquetado.csv"
    shutil.copyfile(DOBLE, doble)
    brazo = _derivar_brazo(DOBLE, entrada / "brazo_manual.csv")
    return corpus, doble, brazo


def _poner_sector_no_canonico(ruta: pathlib.Path) -> None:
    with ruta.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    filas[0]["sector_etiquetado"] = "Sector Inexistente"
    _escribir_csv(ruta, filas)


def _bloquear_red(monkeypatch: pytest.MonkeyPatch) -> None:
    """Prohibe abrir cualquier socket: el helper es offline."""

    def _prohibido(*args: object, **kwargs: object) -> None:
        raise AssertionError("el helper no debe abrir conexiones de red")

    monkeypatch.setattr(socket, "socket", _prohibido)
    monkeypatch.setattr(socket, "create_connection", _prohibido)


def _argumentos(entrada: pathlib.Path, corpus: pathlib.Path, cache: pathlib.Path) -> list[str]:
    return [
        "--entrada",
        str(entrada),
        "--corpus",
        str(corpus),
        "--cache-in-sample",
        str(cache),
    ]


# ---------------------------------------------------------------------------
# 1.1 — RED: union C1 con un unico encabezado
# ---------------------------------------------------------------------------
def test_union_escribe_encabezado_c1_unico(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "campana" / "plantilla_etiquetado.csv"

    preparar.preparar_planilla(doble, brazo, destino, corpus)

    with destino.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.reader(archivo))
    assert tuple(filas[0]) == preparar.COLUMNAS_C1
    encabezados = sum(1 for fila in filas if fila == list(preparar.COLUMNAS_C1))
    assert encabezados == 1
    tareas = [fila[2] for fila in filas[1:]]
    assert tareas == ["doble_etiquetado"] * 18 + ["brazo_manual"] * 18


def test_union_preserva_las_filas_de_origen(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "plantilla_etiquetado.csv"

    preparar.preparar_planilla(doble, brazo, destino, corpus)

    with destino.open(encoding="utf-8", newline="") as archivo:
        filas = list(csv.DictReader(archivo))
    with doble.open(encoding="utf-8", newline="") as archivo:
        esperadas_doble = list(csv.DictReader(archivo))
    with brazo.open(encoding="utf-8", newline="") as archivo:
        esperadas_brazo = list(csv.DictReader(archivo))
    assert filas == esperadas_doble + esperadas_brazo


# ---------------------------------------------------------------------------
# 1.3 — Triangular: validacion por tarea y fuente ausente
# ---------------------------------------------------------------------------
def test_union_valida_por_tarea_y_aborta_sin_escribir(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "campana" / "plantilla_etiquetado.csv"
    _poner_sector_no_canonico(brazo)

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.preparar_planilla(doble, brazo, destino, corpus)

    mensaje = str(excinfo.value)
    assert "brazo_manual.csv" in mensaje
    assert "brazo_manual" in mensaje
    assert not destino.exists()


def test_falta_fuente_aborta_nombrando_el_archivo(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "campana" / "plantilla_etiquetado.csv"
    doble.unlink()

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.preparar_planilla(doble, brazo, destino, corpus)

    assert "doble_etiquetado.csv" in str(excinfo.value)
    assert not destino.exists()


def test_falta_cache_in_sample_aborta_nombrando_el_archivo(tmp_path):
    origen = tmp_path / "predicciones_hybrid-v3_2026-10-07.json"
    destino = tmp_path / "predicciones_in_sample.json"

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.copia_in_sample(origen, destino, raiz=tmp_path)

    assert "predicciones_hybrid-v3_2026-10-07.json" in str(excinfo.value)
    assert not destino.exists()


# ---------------------------------------------------------------------------
# 1.4 — Reproducibilidad y fin de linea LF sin BOM
# ---------------------------------------------------------------------------
def test_reproducibilidad_byte_a_byte(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    primera = tmp_path / "primera.csv"
    segunda = tmp_path / "segunda.csv"

    preparar.preparar_planilla(doble, brazo, primera, corpus)
    preparar.preparar_planilla(doble, brazo, segunda, corpus)

    assert primera.read_bytes() == segunda.read_bytes()
    assert _sha256(primera) == _sha256(segunda)


def test_salida_lf_sin_bom(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "plantilla_etiquetado.csv"

    preparar.preparar_planilla(doble, brazo, destino, corpus)

    contenido = destino.read_bytes()
    assert b"\r\n" not in contenido
    assert not contenido.startswith(b"\xef\xbb\xbf")


# ---------------------------------------------------------------------------
# 1.5 — Staging in-sample byte a byte
# ---------------------------------------------------------------------------
def test_copia_in_sample_byte_a_byte_y_fuente_intacta(tmp_path):
    origen = tmp_path / "predicciones_hybrid-v3_2026-10-07.json"
    origen.write_bytes(b'{"cache_meta": {"classifier_version": "hybrid-v3"}}\n')
    antes = origen.read_bytes()
    destino = tmp_path / "predicciones_in_sample.json"

    preparar.copia_in_sample(origen, destino, raiz=tmp_path)

    assert destino.read_bytes() == antes
    assert origen.read_bytes() == antes
    assert _sha256(destino) == _sha256(origen)


def test_copia_in_sample_de_la_evidencia_congelada(tmp_path):
    destino = tmp_path / "predicciones_in_sample.json"

    preparar.copia_in_sample(CACHE_CONGELADO, destino, raiz=tmp_path)

    assert destino.read_bytes() == CACHE_CONGELADO.read_bytes()
    assert _sha256(destino) == _sha256(CACHE_CONGELADO)


def test_reproducibilidad_de_la_copia(tmp_path):
    origen = tmp_path / "cache.json"
    origen.write_bytes(b"{}\n")
    primera = tmp_path / "a.json"
    segunda = tmp_path / "b.json"

    preparar.copia_in_sample(origen, primera, raiz=tmp_path)
    preparar.copia_in_sample(origen, segunda, raiz=tmp_path)

    assert primera.read_bytes() == segunda.read_bytes() == origen.read_bytes()


# ---------------------------------------------------------------------------
# 1.6 — Proteccion de artefactos congelados y de las fuentes
# ---------------------------------------------------------------------------
def test_rechaza_destino_congelado(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)
    destino = tmp_path / "data" / "corpus_resultados.json"
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text("protegido\n")

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.preparar_planilla(doble, brazo, destino, corpus, raiz=tmp_path)

    assert "congelado" in str(excinfo.value)
    assert destino.read_text() == "protegido\n"


def test_rechaza_destino_en_evidence(tmp_path):
    origen = tmp_path / "cache.json"
    origen.write_bytes(b"{}\n")
    destino = tmp_path / "evaluation" / "evidence" / "plantilla_etiquetado.csv"

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.copia_in_sample(origen, destino, raiz=tmp_path)

    assert "evidence" in str(excinfo.value)
    assert not destino.exists()


def test_rechaza_destino_igual_a_una_fuente(tmp_path):
    corpus_path, doble, brazo = _preparar_fuentes(tmp_path / "campana")
    corpus = cargar_corpus(corpus_path)

    with pytest.raises(preparar.PrepararEntradasError) as excinfo:
        preparar.preparar_planilla(doble, brazo, doble, corpus, raiz=tmp_path)

    assert "fuente" in str(excinfo.value)


# ---------------------------------------------------------------------------
# 1.7 — CLI: imprime SHA-256 y procedencia, devuelve 0
# ---------------------------------------------------------------------------
def test_main_imprime_sha256_y_procedencia_y_devuelve_cero(tmp_path, capsys):
    entrada = tmp_path / "campana"
    corpus_path, doble, brazo = _preparar_fuentes(entrada)
    cache = tmp_path / "predicciones_hybrid-v3_2026-10-07.json"
    cache.write_bytes(b'{"cache_meta": {}}\n')

    codigo = preparar.main(_argumentos(entrada, corpus_path, cache))

    assert codigo == 0
    salida = capsys.readouterr().out
    planilla = entrada / "plantilla_etiquetado.csv"
    in_sample = entrada / "predicciones_in_sample.json"
    assert preparar.NOMBRE_PLANILLA in salida
    assert preparar.NOMBRE_IN_SAMPLE in salida
    assert _sha256(planilla) in salida
    assert _sha256(cache) in salida
    assert str(doble) in salida
    assert str(brazo) in salida
    assert str(cache) in salida
    assert in_sample.read_bytes() == cache.read_bytes()


def test_main_es_offline(tmp_path, monkeypatch):
    entrada = tmp_path / "campana"
    corpus_path, _, _ = _preparar_fuentes(entrada)
    cache = tmp_path / "predicciones_hybrid-v3_2026-10-07.json"
    cache.write_bytes(b'{"cache_meta": {}}\n')
    _bloquear_red(monkeypatch)

    assert preparar.main(_argumentos(entrada, corpus_path, cache)) == 0


def test_main_aborta_sin_escribir_si_falta_una_fuente(tmp_path, capsys):
    entrada = tmp_path / "campana"
    corpus_path, doble, _ = _preparar_fuentes(entrada)
    doble.unlink()
    cache = tmp_path / "predicciones_hybrid-v3_2026-10-07.json"
    cache.write_bytes(b'{"cache_meta": {}}\n')

    codigo = preparar.main(_argumentos(entrada, corpus_path, cache))

    assert codigo == 2
    assert "doble_etiquetado.csv" in capsys.readouterr().err
    assert not (entrada / "plantilla_etiquetado.csv").exists()
    assert not (entrada / "predicciones_in_sample.json").exists()
