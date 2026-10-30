"""
Tests del plan de campana por caso (c-166, ECM-004 y parte de ECM-007).

Cubren `ordenar_casos` (cuatro modos), `generar_plan_campana` con su contrabalanceo
de CONDICION, `verificar_balance`, el CSV del plan, los sub-planes por turno, la copia
de campana del corpus y el CLI. Todo corre sin red y sin tocar el corpus real: los
corpus de prueba son copias en `tmp_path` de `tests/fixtures/corpus_fixture.json`.
"""

from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import subprocess
import sys
import unicodedata
from collections import Counter

import pytest

from evaluation.corpus import cargar_corpus
from evaluation.plan_campana import (
    AsignacionCaso,
    es_archivo_congelado,
    escribir_plan_csv,
    generar_plan_campana,
    leer_plan_csv,
    main,
    ordenar_casos,
    preparar_corpus_campana,
    subplan,
    verificar_balance,
)
from evaluation.tests.conftest import CORPUS_FIXTURE_PATH

IDS_6 = ["R001", "R002", "R003", "R004", "R005", "R006"]


# ---------------------------------------------------------------------------
# 1.1 — ordenar_casos: los cuatro modos
# ---------------------------------------------------------------------------
def test_ordenar_directo_preserva_el_orden():
    assert ordenar_casos(IDS_6, "directo") == IDS_6


def test_ordenar_inverso_invierte_el_orden():
    assert ordenar_casos(IDS_6, "inverso") == list(reversed(IDS_6))


def test_ordenar_alternado_intercala_primera_y_segunda_mitad():
    assert ordenar_casos([1, 2, 3, 4, 5, 6], "alternado") == [1, 4, 2, 5, 3, 6]


def test_ordenar_aleatorio_con_semilla_es_una_permutacion_de_los_mismos_elementos():
    resultado = ordenar_casos(IDS_6, "aleatorio", seed=7)

    assert sorted(resultado) == sorted(IDS_6)
    assert len(resultado) == len(IDS_6)


@pytest.mark.parametrize("modo", ["directo", "inverso", "alternado", "aleatorio"])
def test_ordenar_no_muta_la_entrada_y_devuelve_una_lista_nueva(modo):
    entrada = list(IDS_6)

    resultado = ordenar_casos(entrada, modo, seed=3)

    assert entrada == IDS_6
    assert resultado is not entrada


# ---------------------------------------------------------------------------
# 1.3 — TRIANGULATE: N impar, bordes y reproducibilidad
# ---------------------------------------------------------------------------
def test_ordenar_alternado_con_n_impar_deja_el_ultimo_elemento_en_la_segunda_mitad():
    casos = [1, 2, 3, 4, 5, 6, 7]
    primera_mitad, segunda_mitad = casos[:3], casos[3:]

    resultado = ordenar_casos(casos, "alternado")

    assert resultado == [1, 4, 2, 5, 3, 6, 7]
    assert len(primera_mitad) == 3 and len(segunda_mitad) == 4
    assert resultado[-1] in segunda_mitad
    assert sorted(resultado) == casos


@pytest.mark.parametrize("modo", ["directo", "inverso", "alternado", "aleatorio"])
def test_ordenar_sin_casos_devuelve_lista_vacia(modo):
    assert ordenar_casos([], modo, seed=1) == []


@pytest.mark.parametrize("modo", ["directo", "inverso", "alternado", "aleatorio"])
def test_ordenar_con_un_solo_caso_lo_devuelve_tal_cual(modo):
    assert ordenar_casos(["R001"], modo, seed=1) == ["R001"]


def test_ordenar_aleatorio_con_la_misma_semilla_da_el_mismo_orden():
    casos = list(range(50))

    assert ordenar_casos(casos, "aleatorio", seed=20261021) == ordenar_casos(
        casos, "aleatorio", seed=20261021
    )


def test_ordenar_aleatorio_con_otra_semilla_da_otro_orden():
    casos = list(range(50))

    assert ordenar_casos(casos, "aleatorio", seed=1) != ordenar_casos(
        casos, "aleatorio", seed=2
    )


# ---------------------------------------------------------------------------
# 1.4 — Errores accionables
# ---------------------------------------------------------------------------
def test_ordenar_aleatorio_sin_semilla_levanta_error_que_pide_seed():
    with pytest.raises(ValueError, match="--seed"):
        ordenar_casos(IDS_6, "aleatorio")


def test_ordenar_aleatorio_acepta_la_semilla_cero():
    resultado = ordenar_casos(IDS_6, "aleatorio", seed=0)

    assert sorted(resultado) == sorted(IDS_6)


def test_ordenar_modo_desconocido_levanta_error_que_lista_los_modos_validos():
    with pytest.raises(ValueError) as excinfo:
        ordenar_casos(IDS_6, "zigzag")

    mensaje = str(excinfo.value)
    assert "zigzag" in mensaje
    for modo in ("directo", "inverso", "alternado", "aleatorio"):
        assert modo in mensaje


# ---------------------------------------------------------------------------
# 1.5 — generar_plan_campana: forma de la asignacion
# ---------------------------------------------------------------------------
def test_generar_devuelve_una_asignacion_por_caso_con_posicion_de_1_a_n():
    plan = generar_plan_campana(IDS_6, "directo")

    assert all(isinstance(fila, AsignacionCaso) for fila in plan)
    assert [fila.id_caso for fila in plan] == IDS_6
    assert [fila.posicion for fila in plan] == [1, 2, 3, 4, 5, 6]
    assert {fila.modo for fila in plan} == {"directo"}


def test_generar_asigna_mitad_1_hasta_n_div_2_y_mitad_2_el_resto():
    plan = generar_plan_campana(IDS_6, "directo")

    assert [fila.mitad for fila in plan] == [1, 1, 1, 2, 2, 2]


def test_generar_alterna_el_brazo_primero_por_posicion():
    plan = generar_plan_campana(IDS_6, "directo")

    assert [fila.brazo_primero for fila in plan] == [
        "manual",
        "automatizado",
        "manual",
        "automatizado",
        "manual",
        "automatizado",
    ]


def test_generar_numera_las_posiciones_segun_el_orden_resultante_del_modo():
    plan = generar_plan_campana(IDS_6, "inverso")

    assert [fila.id_caso for fila in plan] == list(reversed(IDS_6))
    assert [fila.posicion for fila in plan] == [1, 2, 3, 4, 5, 6]


@pytest.mark.parametrize("modo", ["directo", "inverso", "alternado"])
def test_generar_deja_la_semilla_vacia_fuera_de_aleatorio(modo):
    plan = generar_plan_campana(IDS_6, modo, seed=99)

    assert {fila.seed for fila in plan} == {None}


def test_generar_aleatorio_registra_la_semilla_en_cada_fila():
    plan = generar_plan_campana(IDS_6, "aleatorio", seed=42)

    assert {fila.seed for fila in plan} == {42}
    assert {fila.modo for fila in plan} == {"aleatorio"}


def test_generar_aleatorio_con_la_misma_semilla_produce_planes_identicos():
    ids = [f"R{numero:03d}" for numero in range(1, 41)]

    assert generar_plan_campana(ids, "aleatorio", seed=5) == generar_plan_campana(
        ids, "aleatorio", seed=5
    )


def test_generar_aleatorio_sin_semilla_levanta_error_que_pide_seed():
    with pytest.raises(ValueError, match="--seed"):
        generar_plan_campana(IDS_6, "aleatorio")


def test_generar_con_ids_repetidos_levanta_value_error_que_nombra_el_id():
    with pytest.raises(ValueError, match="R002"):
        generar_plan_campana(["R001", "R002", "R002"], "directo")


def test_generar_sin_casos_devuelve_un_plan_vacio():
    assert generar_plan_campana([], "directo") == []


def test_asignacion_caso_es_inmutable():
    fila = generar_plan_campana(IDS_6, "directo")[0]

    with pytest.raises(dataclasses.FrozenInstanceError):
        fila.posicion = 9  # type: ignore[misc]


# ---------------------------------------------------------------------------
# 1.7 — TRIANGULATE: balance por mitad (N par, N impar, N variable)
# ---------------------------------------------------------------------------
MODOS_TODOS = ("directo", "inverso", "alternado", "aleatorio")


def _conteo_por_mitad_y_brazo(plan):
    return Counter((fila.mitad, fila.brazo_primero) for fila in plan)


@pytest.mark.parametrize("modo", MODOS_TODOS)
def test_plan_de_200_casos_tiene_50_manual_y_50_automatizado_en_cada_mitad(modo):
    ids = [f"R{numero:03d}" for numero in range(1, 201)]

    plan = generar_plan_campana(ids, modo, seed=20261021)

    assert _conteo_por_mitad_y_brazo(plan) == {
        (1, "manual"): 50,
        (1, "automatizado"): 50,
        (2, "manual"): 50,
        (2, "automatizado"): 50,
    }


def test_plan_de_7_casos_tiene_mitades_de_3_y_4_y_diferencia_de_a_lo_sumo_1():
    plan = generar_plan_campana(list("ABCDEFG"), "directo")

    conteo = _conteo_por_mitad_y_brazo(plan)
    assert sum(1 for fila in plan if fila.mitad == 1) == 3
    assert sum(1 for fila in plan if fila.mitad == 2) == 4
    for mitad in (1, 2):
        assert abs(conteo[(mitad, "manual")] - conteo[(mitad, "automatizado")]) <= 1


@pytest.mark.parametrize("modo", MODOS_TODOS)
@pytest.mark.parametrize("n", range(0, 26))
def test_cualquier_n_deja_mitades_de_n_div_2_y_el_resto_con_diferencia_maxima_1(n, modo):
    ids = [f"C{numero:02d}" for numero in range(n)]

    plan = generar_plan_campana(ids, modo, seed=1)

    conteo = _conteo_por_mitad_y_brazo(plan)
    assert sum(1 for fila in plan if fila.mitad == 1) == n // 2
    assert sum(1 for fila in plan if fila.mitad == 2) == n - n // 2
    for mitad in (1, 2):
        assert abs(conteo[(mitad, "manual")] - conteo[(mitad, "automatizado")]) <= 1


# ---------------------------------------------------------------------------
# 1.7 — verificar_balance: criterio de aceptacion ejecutable del contrabalanceo
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("n", [200, 7])
def test_verificar_balance_pasa_con_un_plan_generado(n):
    ids = [f"R{numero:03d}" for numero in range(1, n + 1)]

    conteo = verificar_balance(generar_plan_campana(ids, "alternado"))

    assert sum(conteo.values()) == n


def test_verificar_balance_devuelve_el_conteo_por_mitad_y_brazo():
    conteo = verificar_balance(generar_plan_campana(IDS_6, "directo"))

    assert conteo == {
        (1, "manual"): 2,
        (1, "automatizado"): 1,
        (2, "manual"): 1,
        (2, "automatizado"): 2,
    }


def test_verificar_balance_falla_si_una_mitad_queda_3_a_0():
    plan = generar_plan_campana(IDS_6, "directo")
    adulterado = [
        dataclasses.replace(fila, brazo_primero="manual") if fila.mitad == 1 else fila
        for fila in plan
    ]

    with pytest.raises(ValueError, match="mitad 1") as excinfo:
        verificar_balance(adulterado)

    assert "manual=3" in str(excinfo.value)
    assert "automatizado=0" in str(excinfo.value)


def test_verificar_balance_falla_si_la_segunda_mitad_esta_desbalanceada():
    plan = generar_plan_campana(IDS_6, "directo")
    adulterado = [
        dataclasses.replace(fila, brazo_primero="automatizado") if fila.mitad == 2 else fila
        for fila in plan
    ]

    with pytest.raises(ValueError, match="mitad 2"):
        verificar_balance(adulterado)


@pytest.mark.parametrize(
    "cambio",
    [{"brazo_primero": "ambos"}, {"mitad": 3}],
    ids=["brazo_fuera_de_dominio", "mitad_fuera_de_dominio"],
)
def test_verificar_balance_rechaza_valores_fuera_de_dominio(cambio):
    plan = generar_plan_campana(IDS_6, "directo")
    plan[0] = dataclasses.replace(plan[0], **cambio)

    with pytest.raises(ValueError, match="R001"):
        verificar_balance(plan)


# ---------------------------------------------------------------------------
# 1.8 — CSV del plan: escritura y lectura
# ---------------------------------------------------------------------------
ENCABEZADO_PLAN = "id_caso,posicion,mitad,brazo_primero,modo,seed"

PLAN_CSV_VALIDO = [
    ENCABEZADO_PLAN,
    "R001,1,1,manual,directo,",
    "R002,2,1,automatizado,directo,",
    "R003,3,2,manual,directo,",
    "R004,4,2,automatizado,directo,",
]


def _escribir_lineas(ruta, lineas):
    ruta.write_bytes(("\n".join(lineas) + "\n").encode("utf-8"))
    return ruta


def test_escribir_plan_csv_produce_utf8_con_coma_lf_y_el_encabezado_del_plan(tmp_path):
    ruta = tmp_path / "plan.csv"

    escribir_plan_csv(generar_plan_campana(IDS_6, "aleatorio", seed=42), ruta)

    crudo = ruta.read_bytes()
    lineas = crudo.decode("utf-8").splitlines()
    assert lineas[0] == ENCABEZADO_PLAN
    assert len(lineas) == 7
    assert not crudo.startswith(b"\xef\xbb\xbf")
    assert b"\r" not in crudo
    assert lineas[1].endswith(",aleatorio,42")


def test_escribir_plan_csv_deja_la_celda_seed_vacia_fuera_de_aleatorio(tmp_path):
    ruta = tmp_path / "plan.csv"

    escribir_plan_csv(generar_plan_campana(IDS_6, "directo"), ruta)

    assert ruta.read_text(encoding="utf-8").splitlines()[1] == "R001,1,1,manual,directo,"


def test_escribir_plan_csv_crea_las_carpetas_intermedias(tmp_path):
    ruta = tmp_path / "campana" / "corrida" / "plan.csv"

    escribir_plan_csv(generar_plan_campana(IDS_6, "directo"), ruta)

    assert ruta.is_file()


@pytest.mark.parametrize(
    ("modo", "seed"),
    [("directo", None), ("inverso", None), ("alternado", None), ("aleatorio", 20261021)],
)
def test_plan_csv_hace_ida_y_vuelta_exacta(tmp_path, modo, seed):
    plan = generar_plan_campana([f"R{n:03d}" for n in range(1, 31)], modo, seed=seed)
    ruta = tmp_path / "plan.csv"

    escribir_plan_csv(plan, ruta)

    assert leer_plan_csv(ruta) == plan


def test_leer_plan_csv_acepta_el_plan_valido_escrito_a_mano(tmp_path):
    ruta = _escribir_lineas(tmp_path / "plan.csv", PLAN_CSV_VALIDO)

    plan = leer_plan_csv(ruta)

    assert [fila.id_caso for fila in plan] == ["R001", "R002", "R003", "R004"]
    assert plan[0] == AsignacionCaso("R001", 1, 1, "manual", "directo", None)


@pytest.mark.parametrize(
    ("lineas", "fragmento"),
    [
        (
            ["id_caso,posicion,mitad,brazo_primero,modo", "R001,1,1,manual,directo"],
            "seed",
        ),
        (
            [ENCABEZADO_PLAN + ",nombre", "R001,1,1,manual,directo,,Ana"],
            "nombre",
        ),
        (
            PLAN_CSV_VALIDO[:3] + ["R003,4,2,manual,directo,"],
            "posicion",
        ),
        (
            PLAN_CSV_VALIDO[:3] + ["R002,3,2,manual,directo,"],
            "R002",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,1,3,manual,directo,"],
            "mitad",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,1,1,ambos,directo,"],
            "brazo_primero",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,1,1,manual,zigzag,"],
            "modo",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,uno,1,manual,directo,"],
            "posicion",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,1,1,manual,aleatorio,abc"],
            "seed",
        ),
        (
            PLAN_CSV_VALIDO[:1] + [",1,1,manual,directo,"],
            "id_caso",
        ),
        (
            PLAN_CSV_VALIDO[:1] + ["R001,1,1,manual"],
            "columnas",
        ),
    ],
    ids=[
        "columna_faltante",
        "columna_extra",
        "posiciones_no_contiguas",
        "id_repetido",
        "mitad_fuera_de_dominio",
        "brazo_fuera_de_dominio",
        "modo_fuera_de_dominio",
        "posicion_no_entera",
        "semilla_no_entera",
        "id_vacio",
        "fila_corta",
    ],
)
def test_leer_plan_csv_rechaza_planes_mal_formados(tmp_path, lineas, fragmento):
    ruta = _escribir_lineas(tmp_path / "plan.csv", lineas)

    with pytest.raises(ValueError, match=fragmento):
        leer_plan_csv(ruta)


def test_leer_plan_csv_rechaza_un_archivo_vacio(tmp_path):
    ruta = tmp_path / "plan.csv"
    ruta.write_bytes(b"")

    with pytest.raises(ValueError, match="columnas"):
        leer_plan_csv(ruta)


def test_leer_plan_csv_parcial_acepta_posiciones_crecientes_no_contiguas(tmp_path):
    ruta = _escribir_lineas(
        tmp_path / "subplan.csv",
        [ENCABEZADO_PLAN, "R002,2,1,automatizado,directo,", "R004,4,2,automatizado,directo,"],
    )

    assert [fila.posicion for fila in leer_plan_csv(ruta, completo=False)] == [2, 4]
    with pytest.raises(ValueError, match="posicion"):
        leer_plan_csv(ruta)


@pytest.mark.parametrize("posiciones", [(4, 2), (2, 2)], ids=["decrecientes", "repetidas"])
def test_leer_plan_csv_parcial_rechaza_posiciones_no_crecientes(tmp_path, posiciones):
    lineas = [ENCABEZADO_PLAN] + [
        f"R{indice:03d},{posicion},1,manual,directo,"
        for indice, posicion in enumerate(posiciones, start=1)
    ]
    ruta = _escribir_lineas(tmp_path / "subplan.csv", lineas)

    with pytest.raises(ValueError, match="posicion"):
        leer_plan_csv(ruta, completo=False)


# ---------------------------------------------------------------------------
# 1.9 — Sub-planes por turno
# ---------------------------------------------------------------------------
IDS_12 = [f"R{numero:03d}" for numero in range(1, 13)]


def test_subplan_turno_1_devuelve_los_casos_de_la_mitad_donde_el_brazo_va_primero():
    plan = generar_plan_campana(IDS_12, "directo")

    filas = subplan(plan, mitad=1, brazo="manual", turno=1)

    assert [fila.id_caso for fila in filas] == ["R001", "R003", "R005"]
    assert {fila.brazo_primero for fila in filas} == {"manual"}
    assert {fila.mitad for fila in filas} == {1}


def test_subplan_turno_2_devuelve_los_casos_donde_el_otro_brazo_va_primero():
    plan = generar_plan_campana(IDS_12, "directo")

    filas = subplan(plan, mitad=1, brazo="manual", turno=2)

    assert [fila.id_caso for fila in filas] == ["R002", "R004", "R006"]
    assert {fila.brazo_primero for fila in filas} == {"automatizado"}


def test_subplan_conserva_la_posicion_global_y_el_orden_del_plan():
    plan = generar_plan_campana(IDS_12, "inverso")

    filas = subplan(plan, mitad=2, brazo="automatizado", turno=1)

    assert [fila.posicion for fila in filas] == [8, 10, 12]
    assert [fila.id_caso for fila in filas] == ["R005", "R003", "R001"]
    assert filas == [fila for fila in plan if fila.posicion in (8, 10, 12)]


@pytest.mark.parametrize("n", [12, 7])
@pytest.mark.parametrize("mitad", [1, 2])
def test_los_cuatro_subplanes_de_una_mitad_cubren_cada_caso_una_vez_por_brazo(n, mitad):
    ids = [f"R{numero:03d}" for numero in range(1, n + 1)]
    plan = generar_plan_campana(ids, "aleatorio", seed=11)

    cubiertos = Counter(
        (fila.id_caso, brazo)
        for brazo in ("manual", "automatizado")
        for turno in (1, 2)
        for fila in subplan(plan, mitad=mitad, brazo=brazo, turno=turno)
    )

    casos_de_la_mitad = {fila.id_caso for fila in plan if fila.mitad == mitad}
    assert set(cubiertos) == {
        (caso, brazo) for caso in casos_de_la_mitad for brazo in ("manual", "automatizado")
    }
    assert set(cubiertos.values()) == {1}


@pytest.mark.parametrize(
    ("argumento_invalido", "argumentos"),
    [
        ("mitad", {"mitad": 3, "brazo": "manual", "turno": 1}),
        ("brazo", {"mitad": 1, "brazo": "ambos", "turno": 1}),
        ("turno", {"mitad": 1, "brazo": "manual", "turno": 3}),
    ],
)
def test_subplan_rechaza_argumentos_fuera_de_dominio(argumento_invalido, argumentos):
    plan = generar_plan_campana(IDS_12, "directo")

    with pytest.raises(ValueError, match=argumento_invalido):
        subplan(plan, **argumentos)


# ---------------------------------------------------------------------------
# 1.10 — Archivos congelados y copia de campana del corpus
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "ruta",
    [
        "data/corpus_evaluacion_pseudonimizado.json",
        "data/corpus_resultados.json",
        "data/corpus_resultados_telefonia.json",
        "data/corpus_resultados_n8n.json",
        "data/corpus_resultados_otra_corrida.json",
        "./data/../data/corpus_resultados.json",
    ],
)
def test_es_archivo_congelado_detecta_la_lista_explicita_y_el_patron(ruta, tmp_path):
    assert es_archivo_congelado(ruta, raiz=tmp_path) is True


def test_es_archivo_congelado_detecta_la_ruta_absoluta_bajo_la_raiz(tmp_path):
    assert es_archivo_congelado(tmp_path / "data" / "corpus_resultados.json", raiz=tmp_path)


def test_es_archivo_congelado_detecta_la_ruta_relativa_aun_desde_otro_directorio(
    tmp_path, monkeypatch
):
    monkeypatch.chdir(tmp_path)

    assert es_archivo_congelado("data/corpus_evaluacion_pseudonimizado.json", raiz=tmp_path / "x")


@pytest.mark.parametrize(
    "ruta",
    [
        "evaluation/data/campana/corpus_campana.json",
        "evaluation/data/corpus_resultados_x.json",
        "data/otro_archivo.json",
        "data/corpus_resultados_campana.csv",
        "corpus_resultados.json",
    ],
)
def test_es_archivo_congelado_no_marca_rutas_de_campana_ni_ajenas(ruta, tmp_path):
    assert es_archivo_congelado(ruta, raiz=tmp_path) is False


def test_es_archivo_congelado_no_marca_un_archivo_homonimo_fuera_de_la_raiz(tmp_path):
    ajeno = tmp_path / "otro_repo" / "data" / "corpus_resultados.json"

    assert es_archivo_congelado(ajeno, raiz=tmp_path / "este_repo") is False


def _copia_del_fixture(tmp_path):
    origen = tmp_path / "origen" / "corpus.json"
    origen.parent.mkdir()
    origen.write_bytes(CORPUS_FIXTURE_PATH.read_bytes())
    return origen


def test_preparar_corpus_campana_copia_el_corpus_con_los_tiempos_en_null(tmp_path):
    origen = _copia_del_fixture(tmp_path)
    destino = tmp_path / "campana" / "corpus_campana.json"

    preparar_corpus_campana(origen, destino, raiz=tmp_path)

    original = cargar_corpus(origen)
    copia = cargar_corpus(destino)
    assert len(copia) == len(original) == 9
    assert all(caso.tiempo_manual_s is None for caso in copia)
    assert all(caso.tiempo_automatizado_s is None for caso in copia)
    assert any(caso.tiempo_manual_s is not None for caso in original)
    assert [
        (c.id, c.descripcion, c.canal_origen, c.sector_asignado, c.sectores_adicionales)
        for c in copia
    ] == [
        (c.id, c.descripcion, c.canal_origen, c.sector_asignado, c.sectores_adicionales)
        for c in original
    ]


def test_preparar_corpus_campana_no_modifica_el_origen_y_escribe_solo_lf(tmp_path):
    origen = _copia_del_fixture(tmp_path)
    antes = origen.read_bytes()
    destino = tmp_path / "corpus_campana.json"

    preparar_corpus_campana(origen, destino, raiz=tmp_path)

    assert origen.read_bytes() == antes
    assert b"\r" not in destino.read_bytes()
    assert json.loads(destino.read_text(encoding="utf-8"))["metadata"]["total_casos"] == 9


def test_preparar_corpus_campana_rechaza_un_destino_existente_sin_tocarlo(tmp_path):
    origen = _copia_del_fixture(tmp_path)
    destino = tmp_path / "corpus_campana.json"
    destino.write_text("contenido previo", encoding="utf-8")

    with pytest.raises(ValueError, match="ya existe"):
        preparar_corpus_campana(origen, destino, raiz=tmp_path)

    assert destino.read_text(encoding="utf-8") == "contenido previo"


@pytest.mark.parametrize(
    "ruta_relativa",
    [
        "data/corpus_evaluacion_pseudonimizado.json",
        "data/corpus_resultados.json",
        "data/corpus_resultados_telefonia.json",
    ],
)
def test_preparar_corpus_campana_rechaza_un_destino_congelado_y_no_lo_crea(
    tmp_path, ruta_relativa
):
    origen = _copia_del_fixture(tmp_path)
    destino = tmp_path / ruta_relativa

    with pytest.raises(ValueError, match="congelado"):
        preparar_corpus_campana(origen, destino, raiz=tmp_path)

    assert not destino.exists()


def test_preparar_corpus_campana_no_deja_un_destino_si_el_origen_no_es_un_corpus_valido(
    tmp_path,
):
    origen = tmp_path / "invalido.json"
    origen.write_text(
        json.dumps({"schema_version": 1, "metadata": {}, "casos": [{"id": "1"}]}),
        encoding="utf-8",
    )
    destino = tmp_path / "corpus_campana.json"

    with pytest.raises(ValueError):
        preparar_corpus_campana(origen, destino, raiz=tmp_path)

    assert not destino.exists()


# ---------------------------------------------------------------------------
# 1.11 — CLI `python -m evaluation.plan_campana`
# ---------------------------------------------------------------------------
RAIZ_REPO = pathlib.Path(__file__).resolve().parents[2]

#: El hijo escribe en UTF-8 (en Windows el default es la pagina de codigos local).
ENTORNO_CLI = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def test_cli_generar_escribe_un_plan_balanceado_con_la_semilla_registrada(tmp_path, capsys):
    corpus = _copia_del_fixture(tmp_path)
    salida = tmp_path / "plan.csv"

    codigo = main(
        ["generar", "--corpus", str(corpus), "--modo", "aleatorio", "--seed", "42",
         "--salida", str(salida)]
    )

    plan = leer_plan_csv(salida)
    assert codigo == 0
    assert sorted(fila.id_caso for fila in plan) == [str(n) for n in range(1, 10)]
    assert {fila.seed for fila in plan} == {42}
    assert verificar_balance(plan)
    assert "9 casos" in capsys.readouterr().out


def test_cli_generar_con_la_misma_semilla_escribe_bytes_identicos(tmp_path):
    corpus = _copia_del_fixture(tmp_path)
    argumentos = ["generar", "--corpus", str(corpus), "--modo", "aleatorio", "--seed", "7"]

    assert main([*argumentos, "--salida", str(tmp_path / "a.csv")]) == 0
    assert main([*argumentos, "--salida", str(tmp_path / "b.csv")]) == 0

    assert (tmp_path / "a.csv").read_bytes() == (tmp_path / "b.csv").read_bytes()


def test_cli_generar_aplica_limit_antes_de_ordenar(tmp_path):
    corpus = _copia_del_fixture(tmp_path)
    salida = tmp_path / "plan.csv"

    codigo = main(
        ["generar", "--corpus", str(corpus), "--modo", "inverso", "--limit", "4",
         "--salida", str(salida)]
    )

    assert codigo == 0
    assert [fila.id_caso for fila in leer_plan_csv(salida)] == ["4", "3", "2", "1"]


def test_cli_generar_aleatorio_sin_seed_sale_con_2_y_no_escribe_el_plan(tmp_path, capsys):
    corpus = _copia_del_fixture(tmp_path)
    salida = tmp_path / "plan.csv"

    codigo = main(["generar", "--corpus", str(corpus), "--modo", "aleatorio", "--salida", str(salida)])

    assert codigo == 2
    assert "--seed" in capsys.readouterr().err
    assert not salida.exists()


def test_cli_generar_no_sobrescribe_una_salida_existente(tmp_path, capsys):
    corpus = _copia_del_fixture(tmp_path)
    salida = tmp_path / "plan.csv"
    salida.write_text("plan previo", encoding="utf-8")

    codigo = main(["generar", "--corpus", str(corpus), "--modo", "directo", "--salida", str(salida)])

    assert codigo == 2
    assert "ya existe" in capsys.readouterr().err
    assert salida.read_text(encoding="utf-8") == "plan previo"


def test_cli_generar_con_corpus_inexistente_sale_con_2(tmp_path, capsys):
    codigo = main(
        ["generar", "--corpus", str(tmp_path / "no_existe.json"), "--modo", "directo",
         "--salida", str(tmp_path / "plan.csv")]
    )

    assert codigo == 2
    assert "no_existe.json" in capsys.readouterr().err


def test_cli_subplan_escribe_las_filas_del_turno_con_la_posicion_global(tmp_path):
    plan_completo = tmp_path / "plan.csv"
    escribir_plan_csv(generar_plan_campana(IDS_12, "directo"), plan_completo)
    salida = tmp_path / "subplan.csv"

    codigo = main(
        ["subplan", "--plan", str(plan_completo), "--mitad", "1", "--brazo", "manual",
         "--turno", "1", "--salida", str(salida)]
    )

    assert codigo == 0
    assert [fila.posicion for fila in leer_plan_csv(salida, completo=False)] == [1, 3, 5]


def test_cli_subplan_sobre_un_subplan_sale_con_2(tmp_path, capsys):
    plan_completo = tmp_path / "plan.csv"
    escribir_plan_csv(generar_plan_campana(IDS_12, "directo"), plan_completo)
    subplan_1 = tmp_path / "subplan.csv"
    assert main(
        ["subplan", "--plan", str(plan_completo), "--mitad", "1", "--brazo", "manual",
         "--turno", "1", "--salida", str(subplan_1)]
    ) == 0

    codigo = main(
        ["subplan", "--plan", str(subplan_1), "--mitad", "1", "--brazo", "manual",
         "--turno", "1", "--salida", str(tmp_path / "otro.csv")]
    )

    assert codigo == 2
    assert "posiciones" in capsys.readouterr().err


def test_cli_preparar_corpus_escribe_la_copia_con_tiempos_nulos(tmp_path):
    origen = _copia_del_fixture(tmp_path)
    destino = tmp_path / "corpus_campana.json"

    codigo = main(["preparar-corpus", "--origen", str(origen), "--destino", str(destino)])

    assert codigo == 0
    assert all(caso.tiempo_automatizado_s is None for caso in cargar_corpus(destino))


def test_cli_preparar_corpus_rechaza_un_destino_existente(tmp_path, capsys):
    origen = _copia_del_fixture(tmp_path)
    destino = tmp_path / "corpus_campana.json"
    destino.write_text("{}", encoding="utf-8")

    codigo = main(["preparar-corpus", "--origen", str(origen), "--destino", str(destino)])

    assert codigo == 2
    assert "ya existe" in capsys.readouterr().err


def test_cli_sin_subcomando_sale_con_2():
    with pytest.raises(SystemExit) as excinfo:
        main([])

    assert excinfo.value.code == 2


def test_cli_como_modulo_genera_el_plan_desde_la_raiz_del_repo(tmp_path):
    corpus = _copia_del_fixture(tmp_path)
    salida = tmp_path / "plan.csv"

    proceso = subprocess.run(
        [sys.executable, "-m", "evaluation.plan_campana", "generar", "--corpus", str(corpus),
         "--modo", "alternado", "--salida", str(salida)],
        cwd=RAIZ_REPO,
        env=ENTORNO_CLI,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )

    assert proceso.returncode == 0, proceso.stderr
    assert [fila.id_caso for fila in leer_plan_csv(salida)] == ["1", "5", "2", "6", "3", "7", "4", "8", "9"]


# ---------------------------------------------------------------------------
# 4.9 — Referencia in-sample documentada en el README de campana
# ---------------------------------------------------------------------------
README_CAMPANA = RAIZ_REPO / "evaluation" / "data" / "campana" / "README.md"
EVIDENCIA_IN_SAMPLE = (
    RAIZ_REPO / "evaluation" / "evidence" / "predicciones_hybrid-v3_2026-10-07.json"
)


def _campo_del_readme(texto: str, campo: str) -> str | None:
    coincidencia = re.search(rf"^- {campo}:[ \t]*(.+?)[ \t]*$", texto, re.MULTILINE)
    return coincidencia.group(1) if coincidencia else None


def test_el_readme_de_campana_registra_la_referencia_in_sample_coherente_con_la_evidencia():
    texto = README_CAMPANA.read_text(encoding="utf-8")
    evidencia = json.loads(EVIDENCIA_IN_SAMPLE.read_text(encoding="utf-8"))["cache_meta"]

    assert _campo_del_readme(texto, "classifier_version_in_sample") == evidencia["classifier_version"]
    assert evidencia["generated_at"].startswith("2026-10-07T22:22:01")
    assert "2026-10-07T22:22:01Z" in texto
    commit_in_sample = _campo_del_readme(texto, "commit_in_sample") or ""
    assert "no registrado" in commit_in_sample and "fec4c42" in commit_in_sample
    pines_in_sample = _campo_del_readme(texto, "pines_in_sample") or ""
    assert "gemini-3.6-flash" in pines_in_sample and ">=2.20.0" in pines_in_sample


def test_la_evidencia_in_sample_no_trae_commit_ni_pines_y_el_readme_lo_declara():
    texto = README_CAMPANA.read_text(encoding="utf-8")
    evidencia = json.loads(EVIDENCIA_IN_SAMPLE.read_text(encoding="utf-8"))["cache_meta"]

    sin_acentos = "".join(
        c for c in unicodedata.normalize("NFKD", texto) if not unicodedata.combining(c)
    )
    assert "commit" not in evidencia and "pines" not in evidencia
    assert "no registro `commit` ni `pines`" in sin_acentos


def test_el_readme_de_campana_cita_las_dos_fuentes_de_los_pines():
    texto = README_CAMPANA.read_text(encoding="utf-8")

    assert "openspec/config.yaml" in texto and "stack.inference" in texto
    assert "configuracion-evaluada-entregada" in texto and "Anexo B" in texto
