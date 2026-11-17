"""
Estado posterior al retiro del corpus independiente del repositorio publico (c-240, OOS-027).

Los autores decidieron retirar `corpus_independiente.json` y `corpus_independiente_arbitrado.json`.
Estas pruebas comprueban el nuevo estado: los dos archivos ya no estan versionados, las sumas de
la campana no los exigen y los archivos que conservan copias de los textos (predicciones y
canario) siguen presentes, como insumo tecnico sin referencia acreditada.
"""

from __future__ import annotations

import json
import pathlib

RAIZ = pathlib.Path(__file__).resolve().parents[2]
CAMPANA = RAIZ / "evaluation" / "data" / "campana"
CANARIO = RAIZ / "evaluation" / "data" / "canario"

RETIRADOS = ("corpus_independiente.json", "corpus_independiente_arbitrado.json")
CONSERVAN_COPIAS = (
    CAMPANA / "predicciones_independiente.json",
    CAMPANA / "predicciones_arbitrado.json",
    CANARIO / "canario.json",
    CANARIO / "canario_predicciones.json",
)


def test_los_dos_archivos_del_corpus_independiente_ya_no_estan_en_el_repositorio():
    for nombre in RETIRADOS:
        assert not (CAMPANA / nombre).exists(), nombre


def test_las_sumas_de_la_campana_no_exigen_los_archivos_retirados():
    sumas = (CAMPANA / "analisis" / "SHA256SUMS.txt").read_text(encoding="utf-8")
    for nombre in RETIRADOS:
        assert nombre not in sumas, nombre


def test_los_archivos_que_conservan_copias_de_los_textos_siguen_presentes_y_son_json_validos():
    for ruta in CONSERVAN_COPIAS:
        assert ruta.is_file(), ruta.name
        assert json.loads(ruta.read_text(encoding="utf-8")), ruta.name

