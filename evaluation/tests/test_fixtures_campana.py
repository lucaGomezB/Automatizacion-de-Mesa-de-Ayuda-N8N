"""
Prueba de humo de los fixtures SINTETICOS del analisis de campana (c-167, tareas 0.4 y 0.5).

Los fixtures de `tests/fixtures/campana/` deben cargar con los lectores del repo y respetar
los encabezados de los contratos que c-167 consume: C1 (planilla de etiquetado, c-168),
C2 (registro de sujetos), C5 (export de intervencion, c-165) y C6 (plan de campana, c-166).
Tambien se verifica que tengan la forma que los demas tests suponen (discordantes, coberturas
distintas, un solape de persona, una fila de intervencion sin `id_caso`, etc.).

Nada de esto es dato de campo: todos los archivos son SINTETICOS.
"""

from __future__ import annotations

from collections import Counter

import pytest

from evaluation.corpus import cargar_corpus
from evaluation.doble_etiquetado import COLUMNAS_C1, validar_doble_etiquetado
from evaluation.no_solape import SolapeError, verificar_no_solape
from evaluation.plan_campana import COLUMNAS_PLAN, leer_plan_csv
from evaluation.run_evaluation import cargar_cache_meta, cargar_predicciones
from evaluation.tests import helpers_campana as h


@pytest.fixture
def corpus_campana(tmp_path):
    return cargar_corpus(h.copiar_fixture(h.CORPUS_CAMPANA, tmp_path))


@pytest.fixture
def corpus_independiente(tmp_path):
    return cargar_corpus(h.copiar_fixture(h.CORPUS_INDEPENDIENTE, tmp_path))


# ---------------------------------------------------------------------------
# C1 — planilla de etiquetado
# ---------------------------------------------------------------------------
def test_planilla_respeta_el_encabezado_de_c1():
    assert h.encabezado_csv(h.PLANILLA) == COLUMNAS_C1


@pytest.mark.parametrize("tarea", ["doble_etiquetado", "brazo_manual"])
def test_planilla_valida_con_el_validador_unico_de_c168(corpus_campana, tarea):
    filas = h.filas_de_tarea(h.leer_csv(h.PLANILLA), tarea)

    resultado = validar_doble_etiquetado(filas, corpus_campana, tarea)

    assert resultado.valida, [o.detalle for o in resultado.ofensas]


def test_doble_etiquetado_tiene_concordantes_y_al_menos_tres_discordantes():
    filas = h.filas_de_tarea(h.leer_csv(h.PLANILLA), "doble_etiquetado")
    etiqueta = {(f["id_caso"], f["id_etiquetador"]): f["sector_etiquetado"] for f in filas}
    casos = {f["id_caso"] for f in filas}

    discordantes = sorted(c for c in casos if etiqueta[(c, "E1")] != etiqueta[(c, "E2")])

    assert {f["id_etiquetador"] for f in filas} == {"E1", "E2"}
    assert discordantes == ["S04", "S11", "S17", "S21"]
    assert len(casos) - len(discordantes) >= 10


def test_brazo_manual_tiene_casos_compartidos_y_exclusivos_de_cada_operador():
    filas = h.filas_de_tarea(h.leer_csv(h.PLANILLA), "brazo_manual")
    de = lambda operador: {f["id_caso"] for f in filas if f["id_etiquetador"] == operador}  # noqa: E731

    assert {f["id_etiquetador"] for f in filas} == {"O1", "O2"}
    assert len(de("O1") & de("O2")) == 12
    assert len(de("O1") - de("O2")) == 6
    assert len(de("O2") - de("O1")) == 6


def test_brazo_manual_trae_inicio_en_todas_las_filas():
    filas = h.filas_de_tarea(h.leer_csv(h.PLANILLA), "brazo_manual")

    assert all(f["inicio"] for f in filas)


# ---------------------------------------------------------------------------
# C2 — registro de sujetos
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("ruta", [h.REGISTRO_SUJETOS, h.REGISTRO_SUJETOS_SOLAPE])
def test_registro_de_sujetos_respeta_el_encabezado_de_c2(ruta):
    assert h.encabezado_csv(ruta) == h.COLUMNAS_C2


def test_registro_valido_asigna_un_solo_rol_a_cada_persona():
    filas = h.leer_csv(h.REGISTRO_SUJETOS)
    roles_por_persona: dict[str, set[str]] = {}
    for fila in filas:
        roles_por_persona.setdefault(fila["persona"], set()).add(fila["rol"])

    assert all(len(roles) == 1 for roles in roles_por_persona.values())
    assert {f["rol"] for f in filas} == {"etiquetador", "operador", "analista_original", "autor"}
    assert all(f["persona"].startswith("P") for f in filas)


def test_registro_con_solape_tiene_una_persona_operador_y_etiquetador_bajo_dos_alias():
    filas = h.leer_csv(h.REGISTRO_SUJETOS_SOLAPE)
    por_persona = {}
    for fila in filas:
        por_persona.setdefault(fila["persona"], []).append((fila["alias"], fila["rol"]))

    repetidas = {p: v for p, v in por_persona.items() if len({rol for _, rol in v}) > 1}

    assert repetidas == {"P3": [("E2", "etiquetador"), ("O1", "operador")]}


# ---------------------------------------------------------------------------
# C5 — export de intervencion
# ---------------------------------------------------------------------------
def test_intervenciones_respeta_el_encabezado_de_c5():
    assert h.encabezado_csv(h.INTERVENCIONES) == h.COLUMNAS_C5


def test_intervenciones_cubre_origenes_cambio_de_sector_y_celdas_nulas():
    filas = h.leer_csv(h.INTERVENCIONES)

    assert {f["origen_intervencion"] for f in filas} >= {"gate", "muestreo", "rederivacion"}
    assert {f["cambio_sector"] for f in filas} == {"true", "false"}
    assert [f["id_caso"] for f in filas].count("") == 1
    assert [f["duracion_s"] for f in filas].count("") == 1


# ---------------------------------------------------------------------------
# C6 — plan de campana
# ---------------------------------------------------------------------------
def test_plan_respeta_el_encabezado_de_c6():
    assert h.encabezado_csv(h.PLAN) == COLUMNAS_PLAN


def test_plan_tiene_al_menos_seis_casos_por_condicion_y_por_mitad(corpus_campana):
    plan = leer_plan_csv(h.PLAN)

    celdas = Counter((fila.mitad, fila.brazo_primero) for fila in plan)

    assert len(celdas) == 4
    assert min(celdas.values()) >= 6
    assert {fila.id_caso for fila in plan} == {caso.id for caso in corpus_campana}


# ---------------------------------------------------------------------------
# Corpus de campana y corpus independiente
# ---------------------------------------------------------------------------
def test_corpus_de_campana_trae_tiempo_automatizado_y_casos_sin_el(corpus_campana):
    con_tiempo = [c for c in corpus_campana if c.tiempo_automatizado_s is not None]

    assert len(corpus_campana) == 24
    assert len(con_tiempo) == 22
    assert all(c.tiempo_manual_s is None for c in corpus_campana)


def test_corpus_independiente_tiene_ids_con_prefijo_i_y_no_solapa(corpus_campana, corpus_independiente):
    assert [c.id for c in corpus_independiente] == [f"I{n:03d}" for n in range(1, 13)]
    assert verificar_no_solape(corpus_campana, corpus_independiente) == []


def test_variante_del_corpus_independiente_en_solape_es_rechazada(corpus_campana, tmp_path):
    solape = cargar_corpus(h.copiar_fixture(h.CORPUS_INDEPENDIENTE_SOLAPE, tmp_path))

    with pytest.raises(SolapeError, match="I012"):
        verificar_no_solape(corpus_campana, solape)


# ---------------------------------------------------------------------------
# C9 — predicciones in-sample e independientes
# ---------------------------------------------------------------------------
def test_cache_in_sample_es_como_el_de_v9_sin_commit_ni_pines():
    meta = cargar_cache_meta(h.PREDICCIONES_IN_SAMPLE)

    assert meta["classifier_version"] == "hybrid-v3"
    assert {"corpus_hash", "corpus_count", "generated_at"} <= set(meta)
    assert "commit" not in meta and "pines" not in meta
    assert len(cargar_predicciones(h.PREDICCIONES_IN_SAMPLE)) == meta["corpus_count"] == 24


def test_cache_independiente_trae_version_commit_y_pines():
    meta = cargar_cache_meta(h.PREDICCIONES_INDEPENDIENTE)

    assert meta["classifier_version"] == "hybrid-v3"
    assert meta["commit"]
    assert meta["pines"] == {"google_genai": "2.34.0", "modelo": "gemini-3.6-flash"}
    assert len(cargar_predicciones(h.PREDICCIONES_INDEPENDIENTE)) == meta["corpus_count"] == 12


def test_variantes_del_cache_independiente_difieren_solo_en_pines_o_en_version():
    base = cargar_cache_meta(h.PREDICCIONES_INDEPENDIENTE)
    pines = cargar_cache_meta(h.PREDICCIONES_INDEPENDIENTE_PINES)
    version = cargar_cache_meta(h.PREDICCIONES_INDEPENDIENTE_VERSION)

    assert pines["pines"] != base["pines"] and pines["classifier_version"] == base["classifier_version"]
    assert version["classifier_version"] != base["classifier_version"] and version["pines"] == base["pines"]


def test_los_ids_de_las_predicciones_coinciden_con_los_de_sus_corpus(corpus_campana, corpus_independiente):
    ids_in_sample = [p.caso_id for p in cargar_predicciones(h.PREDICCIONES_IN_SAMPLE)]
    ids_independiente = [p.caso_id for p in cargar_predicciones(h.PREDICCIONES_INDEPENDIENTE)]

    assert ids_in_sample == [c.id for c in corpus_campana]
    assert ids_independiente == [c.id for c in corpus_independiente]
