"""
Tests de la plantilla, el validador y el CLI del doble etiquetado (c-168).

Cubren ECM-008 (esquema unico de la planilla etiquetador x caso), ECM-009
(validador offline con reglas (a)-(j) y exit codes) y la integridad de la tabla
primaria versionada. Todo corre sin red. El corpus de prueba es
`tests/fixtures/corpus_fixture.json` (ids `1..9`); la planilla de prueba es el
fixture SINTETICO `tests/fixtures/campana/doble_etiquetado_fixture.csv`.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

from evaluation.corpus import cargar_corpus
from evaluation.tests.conftest import CORPUS_FIXTURE_PATH

RAIZ_EVALUATION = pathlib.Path(__file__).resolve().parents[1]
PLANTILLA_PATH = RAIZ_EVALUATION / "data" / "plantilla_etiquetado.csv"

PLANILLA_FIXTURE_PATH = (
    RAIZ_EVALUATION / "tests" / "fixtures" / "campana" / "doble_etiquetado_fixture.csv"
)

ENCABEZADO_C1 = (
    "id_caso,id_etiquetador,tarea,sector_etiquetado,"
    "sectores_adicionales_etiquetados,inicio,timestamp"
)


# ---------------------------------------------------------------------------
# ECM-008 — Plantilla
# ---------------------------------------------------------------------------
def test_plantilla_tiene_encabezado_c1_en_orden():
    contenido = PLANTILLA_PATH.read_text(encoding="utf-8")

    lineas = [linea for linea in contenido.splitlines() if linea.strip()]

    assert lineas == [ENCABEZADO_C1]


def _columnas_de_la_plantilla() -> list[str]:
    with PLANTILLA_PATH.open(encoding="utf-8", newline="") as f:
        return next(csv.reader(f))


def test_plantilla_no_contiene_columnas_pii():
    columnas = {c.lower() for c in _columnas_de_la_plantilla()}

    lista_negra = {"nombre", "email", "correo", "legajo", "telefono", "descripcion"}

    assert columnas & lista_negra == set()


def test_plantilla_no_usa_nombre_sector_asignado():
    columnas = _columnas_de_la_plantilla()

    assert "sector_asignado" not in columnas
    assert "sectores_adicionales" not in columnas


# ---------------------------------------------------------------------------
# ECM-009 — Validador (helpers y fixtures)
# ---------------------------------------------------------------------------
def _leer_registros(path: pathlib.Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.fixture(scope="module")
def corpus(tmp_path_factory):
    """Corpus de fixture (ids 1..9), cargado desde una copia en tmp_path.

    `cargar_corpus` puede reescribir `metadata.total_casos`; se trabaja sobre una
    copia para no tocar el fixture versionado.
    """
    copia = tmp_path_factory.mktemp("corpus") / "corpus_fixture.json"
    shutil.copyfile(CORPUS_FIXTURE_PATH, copia)
    return cargar_corpus(copia)


INICIO_OK = "2026-11-03T14:00:00-03:00"
FIN_OK = "2026-11-03T14:05:00-03:00"
IDS_FIXTURE = [str(n) for n in range(1, 10)]


def _fila(
    id_caso,
    id_etiquetador,
    tarea="doble_etiquetado",
    sector="Sistemas",
    adicionales="",
    inicio=INICIO_OK,
    timestamp=FIN_OK,
) -> dict:
    return {
        "id_caso": str(id_caso),
        "id_etiquetador": id_etiquetador,
        "tarea": tarea,
        "sector_etiquetado": sector,
        "sectores_adicionales_etiquetados": adicionales,
        "inicio": inicio,
        "timestamp": timestamp,
    }


def _ofensas_de(resultado, regla: str) -> list:
    return [o for o in resultado.ofensas if o.regla == regla]


@pytest.fixture
def registros_brazo_manual() -> list[dict]:
    """Planilla `brazo_manual` valida: impares con O1, pares con O2, y el caso 1 con ambos."""
    registros = [
        _fila(i, "O1" if int(i) % 2 else "O2", tarea="brazo_manual") for i in IDS_FIXTURE
    ]
    registros.append(_fila(1, "O2", tarea="brazo_manual"))
    return registros


@pytest.fixture
def registros_validos() -> list[dict]:
    """Planilla `doble_etiquetado` valida (fixture SINTETICO), mutable por test."""
    return _leer_registros(PLANILLA_FIXTURE_PATH)


def test_fixture_valido_no_tiene_ofensas(corpus, registros_validos):
    from evaluation.doble_etiquetado import ResultadoValidacion, validar_doble_etiquetado

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert isinstance(resultado, ResultadoValidacion)
    assert resultado.valida is True
    assert resultado.ofensas == []
    assert resultado.resumen.n_casos == 9
    assert resultado.resumen.n_registros == 18
    assert resultado.resumen.etiquetadores == ("E1", "E2")


# ---------------------------------------------------------------------------
# ECM-009 regla (a) — etiquetadores fijos por tarea
# ---------------------------------------------------------------------------
def test_regla_a_tercer_etiquetador_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos.append(_fila(1, "E3"))

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "a")
    assert resultado.valida is False
    assert [o.id_etiquetador for o in ofensas] == ["E3"]


def test_regla_a_un_solo_etiquetador_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    solo_e1 = [r for r in registros_validos if r["id_etiquetador"] == "E1"]

    resultado = validar_doble_etiquetado(solo_e1, corpus, "doble_etiquetado")

    assert len(_ofensas_de(resultado, "a")) == 1


def test_regla_a_tercer_operador_brazo_manual_falla(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_brazo_manual.append(_fila(2, "O3", tarea="brazo_manual"))

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "a")
    assert [o.id_etiquetador for o in ofensas] == ["O3"]


def test_regla_a_un_solo_operador_brazo_manual_falla(corpus):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    solo_o1 = [_fila(i, "O1", tarea="brazo_manual") for i in IDS_FIXTURE]

    resultado = validar_doble_etiquetado(solo_o1, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "a")
    assert [o.id_etiquetador for o in ofensas] == ["O2"]
    assert "falta" in ofensas[0].detalle
    assert _ofensas_de(resultado, "b") == []


# ---------------------------------------------------------------------------
# ECM-009 regla (b) — cobertura
# ---------------------------------------------------------------------------
def test_regla_b_caso_sin_registro_de_un_etiquetador_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    sin_5_e2 = [
        r for r in registros_validos if not (r["id_caso"] == "5" and r["id_etiquetador"] == "E2")
    ]

    resultado = validar_doble_etiquetado(sin_5_e2, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "b")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("5", "E2")]


def test_regla_b_brazo_manual_cobertura_parcial_valida(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    assert _ofensas_de(resultado, "b") == []
    assert resultado.valida is True


def test_regla_b_brazo_manual_caso_sin_operador_falla(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    sin_caso_7 = [r for r in registros_brazo_manual if r["id_caso"] != "7"]

    resultado = validar_doble_etiquetado(sin_caso_7, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "b")
    assert [o.id_caso for o in ofensas] == ["7"]


# ---------------------------------------------------------------------------
# ECM-009 regla (c) — sin duplicados
# ---------------------------------------------------------------------------
def test_regla_c_registro_duplicado_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    original = next(
        r for r in registros_validos if r["id_caso"] == "3" and r["id_etiquetador"] == "E1"
    )
    registros_validos.append(dict(original))

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "c")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("3", "E1")]
    assert "doble_etiquetado" in ofensas[0].detalle


def test_regla_c_duplicado_brazo_manual_falla(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_brazo_manual.append(_fila(4, "O1", tarea="brazo_manual", sector="Bases de Datos"))
    registros_brazo_manual.append(_fila(4, "O1", tarea="brazo_manual"))

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "c")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("4", "O1")]
    assert "brazo_manual" in ofensas[0].detalle


# ---------------------------------------------------------------------------
# ECM-009 regla (d) — id_caso existente en el corpus indicado
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("id_desconocido", ["99", "R001"])
def test_regla_d_id_caso_desconocido_falla(corpus, registros_validos, id_desconocido):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos.append(_fila(id_desconocido, "E1"))

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "d")
    assert [o.id_caso for o in ofensas] == [id_desconocido]


def test_regla_d_ids_del_corpus_no_se_reportan(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert _ofensas_de(resultado, "d") == []


def test_corpus_independiente_con_prefijo_i_usa_la_misma_plantilla(tmp_path):
    """El validador no impone prefijos: solo pertenencia al corpus indicado (D8)."""
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    ids = ["I001", "I002", "I003"]
    casos = [
        {"id": i, "descripcion": "caso sintetico", "canal_origen": "correo",
         "sector_asignado": "Sistemas", "sectores_adicionales": []}
        for i in ids
    ]
    documento = {"schema_version": 1, "metadata": {"total_casos": 3}, "casos": casos}
    corpus_i = tmp_path / "corpus_independiente.json"
    corpus_i.write_text(json.dumps(documento), encoding="utf-8")
    registros = [_fila(i, alias) for i in ids for alias in ("E1", "E2")]

    resultado = validar_doble_etiquetado(registros, cargar_corpus(corpus_i), "doble_etiquetado")

    assert resultado.valida is True
    assert resultado.resumen.n_casos == 3

    registros.append(_fila("R001", "E1"))  # un id del corpus de ajuste no existe en este corpus
    resultado = validar_doble_etiquetado(registros, cargar_corpus(corpus_i), "doble_etiquetado")
    assert [o.id_caso for o in _ofensas_de(resultado, "d")] == ["R001"]


# ---------------------------------------------------------------------------
# ECM-009 regla (e) — sectores canonicos
# ---------------------------------------------------------------------------
SECTORES_NO_CANONICOS = ["Soporte Técnico Hardware", "sistemas", "Operaciones"]


@pytest.mark.parametrize("valor", SECTORES_NO_CANONICOS)
def test_regla_e_sector_no_canonico_falla_en_sector_etiquetado(corpus, registros_validos, valor):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["sector_etiquetado"] = valor

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "e")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("1", "E1")]
    assert valor in ofensas[0].detalle


@pytest.mark.parametrize("valor", SECTORES_NO_CANONICOS)
def test_regla_e_sector_no_canonico_falla_en_un_adicional(corpus, registros_validos, valor):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["sectores_adicionales_etiquetados"] = f"Bases de Datos|{valor}"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "e")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("1", "E1")]
    assert valor in ofensas[0].detalle


def test_regla_e_sector_etiquetado_vacio_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["sector_etiquetado"] = ""

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert len(_ofensas_de(resultado, "e")) == 1


def test_regla_e_usa_el_vocabulario_de_evaluation_corpus(corpus, registros_validos):
    """Cada cadena canonica de `evaluation.corpus` es aceptada (sin lista propia)."""
    from evaluation.corpus import SECTORES_CANONICOS
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for sector in SECTORES_CANONICOS:
        registros_validos[0]["sector_etiquetado"] = sector
        registros_validos[0]["sectores_adicionales_etiquetados"] = ""

        resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

        assert _ofensas_de(resultado, "e") == [], sector


# ---------------------------------------------------------------------------
# ECM-009 regla (f) — los adicionales no repiten el principal
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "adicionales", ["Sistemas|Bases de Datos", "Bases de Datos|Sistemas", "Sistemas"]
)
def test_regla_f_adicional_repite_principal_falla(corpus, registros_validos, adicionales):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["sector_etiquetado"] = "Sistemas"
    registros_validos[0]["sectores_adicionales_etiquetados"] = adicionales

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "f")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("1", "E1")]


def test_regla_f_adicionales_distintos_del_principal_no_se_reportan(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["sector_etiquetado"] = "Sistemas"
    registros_validos[0]["sectores_adicionales_etiquetados"] = "Bases de Datos|Seguridad Informatica"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert resultado.valida is True


# ---------------------------------------------------------------------------
# ECM-009 regla (g) — timestamp / inicio ISO-8601 con zona horaria
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "timestamp_invalido", ["03/11/2026 14:05", "2026-11-03T14:05:00", ""]
)
def test_regla_g_timestamp_invalido_falla(corpus, registros_validos, timestamp_invalido):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[1]["timestamp"] = timestamp_invalido

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "g")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("1", "E2")]


@pytest.mark.parametrize("inicio_invalido", ["2026-11-03 14:05", "ayer a la tarde"])
def test_regla_g_inicio_informado_invalido_falla(corpus, registros_validos, inicio_invalido):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["inicio"] = inicio_invalido

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "g")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("1", "E1")]


def test_regla_g_zona_utc_con_sufijo_z_es_valida(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["inicio"] = "2026-11-03T17:00:00Z"
    registros_validos[0]["timestamp"] = "2026-11-03T17:05:00+00:00"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert resultado.valida is True


# ---------------------------------------------------------------------------
# ECM-009 regla (h) — sin PII
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "columna", ["nombre", "Email", "correo", "legajo", "telefono", "descripcion"]
)
def test_regla_h_columna_pii_falla(corpus, registros_validos, columna):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_validos:
        r[columna] = "dato"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "h")
    assert len(ofensas) == 1
    assert columna in ofensas[0].detalle


def test_regla_h_columna_pii_tambien_en_brazo_manual(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_brazo_manual:
        r["LEGAJO"] = "12345"

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "h")
    assert len(ofensas) == 1
    assert "LEGAJO" in ofensas[0].detalle


def test_regla_h_alias_con_forma_invalida_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_validos:
        if r["id_etiquetador"] == "E2":
            r["id_etiquetador"] = "Juan Perez"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "h")
    assert [o.id_etiquetador for o in ofensas] == ["Juan Perez"]


def test_regla_h_alias_de_operador_en_doble_etiquetado_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_validos:
        if r["id_etiquetador"] == "E2":
            r["id_etiquetador"] = "O1"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "h")
    assert [o.id_etiquetador for o in ofensas] == ["O1"]


def test_regla_h_alias_de_etiquetador_en_brazo_manual_falla(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_brazo_manual:
        if r["id_etiquetador"] == "O2":
            r["id_etiquetador"] = "E2"

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "h")
    assert [o.id_etiquetador for o in ofensas] == ["E2"]


# ---------------------------------------------------------------------------
# ECM-009 regla (i) — tarea valida
# ---------------------------------------------------------------------------
def test_regla_i_tarea_invalida_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_validos:
        r["tarea"] = "etiquetado"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "etiquetado")

    ofensas = _ofensas_de(resultado, "i")
    assert any(o.id_caso is None and "etiquetado" in o.detalle for o in ofensas)
    assert ("1", "E1") in {(o.id_caso, o.id_etiquetador) for o in ofensas}
    # con la tarea declarada invalida no se evaluan las reglas que dependen de ella
    assert _ofensas_de(resultado, "a") == []
    assert _ofensas_de(resultado, "b") == []


def test_regla_i_una_fila_con_tarea_invalida_falla(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[4]["tarea"] = "etiquetado"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "i")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("3", "E1")]


def test_regla_i_fila_con_otra_tarea_valida_distinta_de_la_declarada_falla(
    corpus, registros_validos
):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[4]["tarea"] = "brazo_manual"

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    ofensas = _ofensas_de(resultado, "i")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("3", "E1")]


# ---------------------------------------------------------------------------
# ECM-009 regla (j) — inicio obligatorio en brazo_manual e inicio <= timestamp
# ---------------------------------------------------------------------------
@pytest.fixture(params=["doble_etiquetado", "brazo_manual"])
def planilla_por_tarea(request, registros_validos, registros_brazo_manual):
    """(tarea, registros) validos para cada una de las dos tareas."""
    if request.param == "brazo_manual":
        return request.param, registros_brazo_manual
    return request.param, registros_validos


def test_regla_j_inicio_ausente_brazo_manual_falla(corpus, registros_brazo_manual):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_brazo_manual[2]["inicio"] = ""

    resultado = validar_doble_etiquetado(registros_brazo_manual, corpus, "brazo_manual")

    ofensas = _ofensas_de(resultado, "j")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [("3", "O1")]
    assert _ofensas_de(resultado, "g") == []


def test_regla_j_inicio_posterior_al_fin_falla(corpus, planilla_por_tarea):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    tarea, registros = planilla_por_tarea
    registros[0]["inicio"] = "2026-11-03T14:10:00-03:00"
    registros[0]["timestamp"] = "2026-11-03T14:05:00-03:00"

    resultado = validar_doble_etiquetado(registros, corpus, tarea)

    ofensas = _ofensas_de(resultado, "j")
    assert [(o.id_caso, o.id_etiquetador) for o in ofensas] == [
        (registros[0]["id_caso"], registros[0]["id_etiquetador"])
    ]


def test_regla_j_compara_instantes_y_no_cadenas_con_zonas_distintas(corpus, planilla_por_tarea):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    tarea, registros = planilla_por_tarea
    # 14:10-03:00 son las 17:10Z: posterior a 17:05Z aunque como cadena "14:10" < "17:05".
    registros[0]["inicio"] = "2026-11-03T14:10:00-03:00"
    registros[0]["timestamp"] = "2026-11-03T17:05:00+00:00"

    resultado = validar_doble_etiquetado(registros, corpus, tarea)

    assert len(_ofensas_de(resultado, "j")) == 1


def test_regla_j_inicio_vacio_doble_etiquetado_valido(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["inicio"] = ""

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert _ofensas_de(resultado, "g") == []
    assert _ofensas_de(resultado, "j") == []


def test_regla_j_inicio_igual_al_fin_valido(corpus, planilla_por_tarea):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    tarea, registros = planilla_por_tarea
    registros[0]["inicio"] = "2026-11-03T14:05:00-03:00"
    registros[0]["timestamp"] = "2026-11-03T14:05:00-03:00"

    resultado = validar_doble_etiquetado(registros, corpus, tarea)

    assert resultado.valida is True


# ---------------------------------------------------------------------------
# ECM-009 — triangulacion: planillas completas
# ---------------------------------------------------------------------------
def test_planilla_brazo_manual_valida(corpus):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    reparto = {"1": "O1", "2": "O2", "3": "O2", "4": "O1", "5": "O1", "6": "O2", "7": "O1",
               "8": "O2", "9": "O1"}
    registros = [
        _fila(i, operador, tarea="brazo_manual", sector="Bases de Datos",
              inicio=f"2026-11-03T14:{int(i):02d}:00-03:00",
              timestamp=f"2026-11-03T14:{int(i):02d}:45-03:00")
        for i, operador in reparto.items()
    ]

    resultado = validar_doble_etiquetado(registros, corpus, "brazo_manual")

    assert resultado.valida is True
    assert resultado.resumen.n_casos == 9
    assert resultado.resumen.n_registros == 9
    assert resultado.resumen.etiquetadores == ("O1", "O2")


def test_planilla_brazo_manual_un_solo_operador_falla_regla_a(corpus):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    solo_o2 = [_fila(i, "O2", tarea="brazo_manual") for i in IDS_FIXTURE]

    resultado = validar_doble_etiquetado(solo_o2, corpus, "brazo_manual")

    assert [(o.regla, o.id_etiquetador) for o in resultado.ofensas] == [("a", "O1")]


def test_varias_ofensas_se_reportan_todas(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros = [
        r for r in registros_validos if not (r["id_caso"] == "5" and r["id_etiquetador"] == "E2")
    ]
    registros[0]["sector_etiquetado"] = "sistemas"  # (e) en (1, E1)
    registros[2]["timestamp"] = "03/11/2026 14:05"  # (g) en (2, E1)

    resultado = validar_doble_etiquetado(registros, corpus, "doble_etiquetado")

    assert [(o.regla, o.id_caso, o.id_etiquetador) for o in resultado.ofensas] == [
        ("b", "5", "E2"),
        ("e", "1", "E1"),
        ("g", "2", "E1"),
    ]
    assert resultado.valida is False


def test_columna_obligatoria_ausente_se_reporta_sin_lanzar_excepcion(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    for r in registros_validos:
        del r["timestamp"]

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert {o.regla for o in resultado.ofensas} == {"g"}
    assert len(resultado.ofensas) == 18


def test_celda_nula_de_csv_con_fila_corta_se_trata_como_vacia(corpus, registros_validos):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    registros_validos[0]["timestamp"] = None  # csv.DictReader pone None en filas cortas

    resultado = validar_doble_etiquetado(registros_validos, corpus, "doble_etiquetado")

    assert [(o.regla, o.id_caso, o.id_etiquetador) for o in resultado.ofensas] == [("g", "1", "E1")]


# ---------------------------------------------------------------------------
# ECM-009 — CLI `python -m evaluation.doble_etiquetado`
# ---------------------------------------------------------------------------
RAIZ_REPO = RAIZ_EVALUATION.parent


def _escribir_planilla(path: pathlib.Path, registros: list[dict]) -> pathlib.Path:
    columnas = list(dict.fromkeys(c for r in registros for c in r))
    with path.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(registros)
    return path


#: El hijo escribe en UTF-8 (en Windows el default es la pagina de codigos local).
ENTORNO_CLI = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def _correr_cli(planilla, corpus_path, tarea) -> subprocess.CompletedProcess:
    return subprocess.run(
        [
            sys.executable, "-m", "evaluation.doble_etiquetado",
            "--planilla", str(planilla), "--corpus", str(corpus_path), "--tarea", tarea,
        ],
        cwd=RAIZ_REPO,
        env=ENTORNO_CLI,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=60,
    )


@pytest.fixture
def corpus_copia(tmp_path) -> pathlib.Path:
    """Copia del corpus de fixture (`cargar_corpus` puede reescribir `total_casos`)."""
    copia = tmp_path / "corpus_fixture.json"
    shutil.copyfile(CORPUS_FIXTURE_PATH, copia)
    return copia


def test_cli_planilla_valida_sale_con_cero(tmp_path, corpus_copia, registros_validos):
    planilla = _escribir_planilla(tmp_path / "planilla.csv", registros_validos)

    proceso = _correr_cli(planilla, corpus_copia, "doble_etiquetado")

    assert proceso.returncode == 0, proceso.stderr
    assert "18" in proceso.stdout and "E1" in proceso.stdout and "E2" in proceso.stdout


def test_cli_fixture_versionado_sale_con_cero(corpus_copia):
    proceso = _correr_cli(PLANILLA_FIXTURE_PATH, corpus_copia, "doble_etiquetado")

    assert proceso.returncode == 0, proceso.stderr


def _con_tercer_etiquetador(r, rb):
    return "doble_etiquetado", r + [_fila(1, "E3")]


def _sin_registro_de_e2_en_5(r, rb):
    return "doble_etiquetado", [x for x in r if not (x["id_caso"] == "5" and x["id_etiquetador"] == "E2")]


def _con_duplicado(r, rb):
    return "doble_etiquetado", r + [dict(r[0])]


def _con_id_desconocido(r, rb):
    return "doble_etiquetado", r + [_fila(99, "E1")]


def _con_sector_no_canonico(r, rb):
    r[0]["sector_etiquetado"] = "sistemas"
    return "doble_etiquetado", r


def _con_adicional_repetido(r, rb):
    r[0]["sector_etiquetado"] = "Sistemas"
    r[0]["sectores_adicionales_etiquetados"] = "Sistemas|Bases de Datos"
    return "doble_etiquetado", r


def _con_timestamp_invalido(r, rb):
    r[0]["timestamp"] = "03/11/2026 14:05"
    return "doble_etiquetado", r


def _con_columna_pii(r, rb):
    for x in r:
        x["nombre"] = "dato"
    return "doble_etiquetado", r


def _con_tarea_invalida(r, rb):
    return "etiquetado", r


def _con_inicio_ausente_en_brazo_manual(r, rb):
    rb[0]["inicio"] = ""
    return "brazo_manual", rb


@pytest.mark.parametrize(
    ("armar", "codigo"),
    [
        (_con_tercer_etiquetador, 10),
        (_sin_registro_de_e2_en_5, 11),
        (_con_duplicado, 12),
        (_con_id_desconocido, 13),
        (_con_sector_no_canonico, 14),
        (_con_adicional_repetido, 15),
        (_con_timestamp_invalido, 16),
        (_con_columna_pii, 17),
        (_con_tarea_invalida, 18),
        (_con_inicio_ausente_en_brazo_manual, 19),
    ],
    ids=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
)
def test_cli_exit_code_por_regla(
    tmp_path, corpus_copia, registros_validos, registros_brazo_manual, armar, codigo
):
    tarea, registros = armar(registros_validos, registros_brazo_manual)
    planilla = _escribir_planilla(tmp_path / "planilla.csv", registros)

    proceso = _correr_cli(planilla, corpus_copia, tarea)

    assert proceso.returncode == codigo, proceso.stdout + proceso.stderr


def test_cli_archivo_inexistente_sale_con_2(tmp_path, corpus_copia):
    proceso = _correr_cli(tmp_path / "no_existe.csv", corpus_copia, "doble_etiquetado")

    assert proceso.returncode == 2


def test_cli_corpus_inexistente_sale_con_2(tmp_path, registros_validos):
    planilla = _escribir_planilla(tmp_path / "planilla.csv", registros_validos)

    proceso = _correr_cli(planilla, tmp_path / "no_existe.json", "doble_etiquetado")

    assert proceso.returncode == 2


def test_cli_sin_argumentos_sale_con_2():
    proceso = subprocess.run(
        [sys.executable, "-m", "evaluation.doble_etiquetado"],
        cwd=RAIZ_REPO, env=ENTORNO_CLI, capture_output=True, text=True, encoding="utf-8",
        timeout=60,
    )

    assert proceso.returncode == 2


def test_cli_reporta_todas_las_ofensas_y_sale_con_la_primera_regla(
    tmp_path, corpus_copia, registros_validos
):
    registros_validos[0]["sector_etiquetado"] = "sistemas"  # (e)
    registros_validos[2]["timestamp"] = "03/11/2026 14:05"  # (g)
    planilla = _escribir_planilla(tmp_path / "planilla.csv", registros_validos)

    proceso = _correr_cli(planilla, corpus_copia, "doble_etiquetado")

    assert proceso.returncode == 14
    assert "sistemas" in proceso.stdout
    assert "03/11/2026 14:05" in proceso.stdout


# ---------------------------------------------------------------------------
# ECM-008 — Integridad de la tabla primaria versionada
# ---------------------------------------------------------------------------
TABLA_PRIMARIA_PATH = RAIZ_EVALUATION / "data" / "campana" / "doble_etiquetado.csv"
README_CAMPANA_PATH = RAIZ_EVALUATION / "data" / "campana" / "README.md"
CORPUS_REAL_PATH = RAIZ_REPO / "data" / "corpus_evaluacion_pseudonimizado.json"


def _campo_declarado(readme_texto: str, campo: str) -> str | None:
    """Valor de la linea `- campo: valor` del README de `campana/` (None si no esta)."""
    coincidencia = re.search(rf"^- {campo}:[ \t]*(.+?)[ \t]*$", readme_texto, re.MULTILINE)
    return coincidencia.group(1) if coincidencia else None


def _validar_csv(planilla: pathlib.Path, corpus_json: pathlib.Path):
    from evaluation.doble_etiquetado import validar_doble_etiquetado

    return validar_doble_etiquetado(
        _leer_registros(planilla), cargar_corpus(corpus_json), "doble_etiquetado"
    )


def _verificar_tabla_primaria(tmp_dir: pathlib.Path) -> None:
    """Comprueba la tabla primaria versionada; omite el test si todavia no existe.

    Lee las rutas de las constantes del modulo (los tests de la propia verificacion
    las redirigen con `monkeypatch`). El corpus se copia a `tmp_dir` porque
    `cargar_corpus` puede reescribir `metadata.total_casos`.
    """
    if not TABLA_PRIMARIA_PATH.exists():
        pytest.skip("tabla primaria pendiente de campana")
    readme = README_CAMPANA_PATH.read_text(encoding="utf-8")

    declarado = _campo_declarado(readme, "sha256")
    assert declarado and re.fullmatch(r"[0-9a-f]{64}", declarado), (
        f"el README de campana/ no declara un sha256 valido: {declarado!r}"
    )
    real = hashlib.sha256(TABLA_PRIMARIA_PATH.read_bytes()).hexdigest()
    assert real == declarado, f"sha256 de la tabla ({real}) distinto del declarado ({declarado})"
    fecha = _campo_declarado(readme, "fecha")
    assert fecha and re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha), (
        f"el README de campana/ no declara la fecha de versionado (AAAA-MM-DD): {fecha!r}"
    )

    copia_corpus = tmp_dir / "corpus.json"
    shutil.copyfile(CORPUS_REAL_PATH, copia_corpus)
    resultado = _validar_csv(TABLA_PRIMARIA_PATH, copia_corpus)
    assert resultado.valida, [(o.regla, o.id_caso, o.id_etiquetador) for o in resultado.ofensas]


def test_tabla_primaria_versionada_integra(tmp_path):
    _verificar_tabla_primaria(tmp_path)


def _preparar_tabla_temporal(tmp_path, monkeypatch, registros, readme_texto):
    """Redirige las rutas del modulo a una tabla + README temporales y al corpus de fixture."""
    modulo = sys.modules[__name__]
    tabla = _escribir_planilla(tmp_path / "doble_etiquetado.csv", registros)
    readme = tmp_path / "README.md"
    readme.write_text(readme_texto, encoding="utf-8", newline="\n")
    monkeypatch.setattr(modulo, "TABLA_PRIMARIA_PATH", tabla)
    monkeypatch.setattr(modulo, "README_CAMPANA_PATH", readme)
    monkeypatch.setattr(modulo, "CORPUS_REAL_PATH", CORPUS_FIXTURE_PATH)
    return tabla


def test_tabla_primaria_ausente_se_omite(tmp_path, monkeypatch):
    modulo = sys.modules[__name__]
    monkeypatch.setattr(modulo, "TABLA_PRIMARIA_PATH", tmp_path / "no_existe.csv")

    with pytest.raises(pytest.skip.Exception, match="pendiente de campana"):
        _verificar_tabla_primaria(tmp_path)


def test_tabla_primaria_con_hash_distinto_al_declarado_falla(
    tmp_path, monkeypatch, registros_validos
):
    readme = "- sha256: " + "0" * 64 + "\n- fecha: 2026-11-10\n"
    _preparar_tabla_temporal(tmp_path, monkeypatch, registros_validos, readme)

    with pytest.raises(AssertionError, match="sha256"):
        _verificar_tabla_primaria(tmp_path)


def _readme_con_hash_de(tabla: pathlib.Path, fecha: str = "2026-11-10") -> str:
    hash_real = hashlib.sha256(tabla.read_bytes()).hexdigest()
    return f"- corpus_sha256: {'f' * 64}\n- sha256: {hash_real}\n- fecha: {fecha}\n"


def test_tabla_primaria_con_hash_declarado_correcto_pasa(tmp_path, monkeypatch, registros_validos):
    tabla = _preparar_tabla_temporal(tmp_path, monkeypatch, registros_validos, "")
    README_CAMPANA_PATH.write_text(_readme_con_hash_de(tabla), encoding="utf-8", newline="\n")

    _verificar_tabla_primaria(tmp_path)  # no lanza


def test_tabla_primaria_existente_con_hash_pendiente_falla(tmp_path, monkeypatch, registros_validos):
    _preparar_tabla_temporal(
        tmp_path, monkeypatch, registros_validos, "- sha256: pendiente\n- fecha: pendiente\n"
    )

    with pytest.raises(AssertionError, match="sha256"):
        _verificar_tabla_primaria(tmp_path)


def test_tabla_primaria_sin_fecha_declarada_falla(tmp_path, monkeypatch, registros_validos):
    tabla = _preparar_tabla_temporal(tmp_path, monkeypatch, registros_validos, "")
    README_CAMPANA_PATH.write_text(
        _readme_con_hash_de(tabla, fecha="pendiente"), encoding="utf-8", newline="\n"
    )

    with pytest.raises(AssertionError, match="fecha"):
        _verificar_tabla_primaria(tmp_path)


def test_tabla_primaria_con_hash_correcto_pero_invalida_falla_el_validador(
    tmp_path, monkeypatch, registros_validos
):
    registros_validos[0]["sector_etiquetado"] = "sistemas"
    tabla = _preparar_tabla_temporal(tmp_path, monkeypatch, registros_validos, "")
    README_CAMPANA_PATH.write_text(_readme_con_hash_de(tabla), encoding="utf-8", newline="\n")

    with pytest.raises(AssertionError, match="'e'"):
        _verificar_tabla_primaria(tmp_path)


def test_readme_de_campana_declara_los_campos_de_procedencia():
    texto = README_CAMPANA_PATH.read_text(encoding="utf-8")

    for campo in (
        "archivo", "sha256", "fecha", "corpus", "corpus_sha256", "tarea",
        "comando_de_validacion", "codebook_sha256", "estado_cegado", "motivo_limitacion",
    ):
        assert _campo_declarado(texto, campo) is not None, campo
    # `sha256` de la tabla no se confunde con `corpus_sha256`
    assert _campo_declarado("- corpus_sha256: aa\n- sha256: bb\n", "sha256") == "bb"
