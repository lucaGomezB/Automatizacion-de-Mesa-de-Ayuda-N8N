"""Pruebas del analisis offline de la acotacion del arbitraje por mayoria (c-224).

TDD estricto de las funciones puras con casos sinteticos (sin I/O de red) mas la
integracion con los artefactos versionados. Cubre la carga de etiquetas y de origen,
la regla vigente y la mayoria, la coincidencia 200/206, los 6 casos sin mayoria, el
rango de exactitud 142-147, las metricas por clase en ambos extremos, los anclajes
que abortan antes de escribir y la escritura determinista byte a byte.
"""
# Nota (c-240): se retiraron de este modulo las pruebas que leian los archivos
# `evaluation/data/campana/corpus_independiente.json` y/o `corpus_independiente_arbitrado.json`,
# eliminados del repositorio publico por la decision de los autores (c-240, OOS-027). Las pruebas
# restantes no dependen de esos archivos. El nuevo estado se verifica en
# `evaluation/tests/test_retiro_corpus_independiente_c240.py`.

from __future__ import annotations

import json
import pathlib
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_arbitraje_mayoria_c224 as c224  # noqa: E402


# ---------------------------------------------------------------------------
# Carga de etiquetas (funcion pura sobre CSV)
# ---------------------------------------------------------------------------
def _escribir_csv_etiquetas(ruta: pathlib.Path, filas: list[tuple[str, str, str]]) -> None:
    lineas = ["id_caso,id_etiquetador,tarea,sector_etiquetado"]
    for id_caso, id_etiquetador, sector in filas:
        lineas.append(f"{id_caso},{id_etiquetador},doble_etiquetado,{sector}")
    ruta.write_text("\n".join(lineas) + "\n", encoding="utf-8")


def test_cargar_etiquetas_agrupa_por_caso_y_etiquetador(tmp_path):
    ruta = tmp_path / "etiquetas.csv"
    _escribir_csv_etiquetas(
        ruta,
        [
            ("C1", "E3", "Seguridad Informatica"),
            ("C1", "E4", "Seguridad Informatica"),
            ("C2", "E3", "Soporte Tecnico Hardware"),
            ("C2", "E4", "Soporte Tecnico Software"),
            ("C2", "E5", "Soporte Tecnico Hardware"),
            ("C3", "E3", "Soporte Tecnico Software"),
            ("C3", "E4", "Sistemas"),
            ("C3", "E5", "Bases de Datos"),
        ],
    )

    etiquetas = c224.cargar_etiquetas(ruta)

    assert set(etiquetas) == {"C1", "C2", "C3"}
    assert etiquetas["C1"]["E3"] == "Seguridad Informatica"
    assert etiquetas["C1"]["E4"] == "Seguridad Informatica"
    assert etiquetas["C1"]["E5"] is None
    assert etiquetas["C2"]["E5"] == "Soporte Tecnico Hardware"
    assert etiquetas["C3"]["E3"] == "Soporte Tecnico Software"
    assert etiquetas["C3"]["E4"] == "Sistemas"
    assert etiquetas["C3"]["E5"] == "Bases de Datos"


def test_cargar_etiquetas_no_inventa_etiquetadores_ausentes(tmp_path):
    ruta = tmp_path / "etiquetas.csv"
    _escribir_csv_etiquetas(
        ruta,
        [
            ("C1", "E3", "Sistemas"),
            ("C1", "E4", "Sistemas"),
        ],
    )

    etiquetas = c224.cargar_etiquetas(ruta)

    assert etiquetas["C1"] == {"E3": "Sistemas", "E4": "Sistemas", "E5": None}


# ---------------------------------------------------------------------------
# Carga de origen (funcion pura sobre JSON)
# ---------------------------------------------------------------------------
def test_cargar_origen_lee_origen_y_bandera(tmp_path):
    ruta = tmp_path / "arbitraje.json"
    ruta.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "metadata": {"total_casos": 3},
                "casos": [
                    {"id": "C1", "origen": "consenso_e3_e4", "tres_vias": False},
                    {"id": "C2", "origen": "arbitraje_e5", "tres_vias": False},
                    {"id": "C3", "origen": "arbitraje_e5", "tres_vias": True},
                ],
            }
        ),
        encoding="utf-8",
    )

    origen = c224.cargar_origen(ruta)

    assert set(origen) == {"C1", "C2", "C3"}
    assert origen["C1"] == {"origen": "consenso_e3_e4", "tres_vias": False}
    assert origen["C2"] == {"origen": "arbitraje_e5", "tres_vias": False}
    assert origen["C3"] == {"origen": "arbitraje_e5", "tres_vias": True}


# ---------------------------------------------------------------------------
# Carga de predicciones y referencia (funciones puras sobre JSON)
# ---------------------------------------------------------------------------
def _escribir_predicciones(ruta: pathlib.Path, filas: list[tuple[str, str]]) -> None:
    documento = {
        "cache_meta": {"corpus_count": len(filas)},
        "predictions": [
            {"caso_id": caso, "sector_asignado": "X", "sector_predicho": predicho}
            for caso, predicho in filas
        ],
    }
    ruta.write_text(json.dumps(documento), encoding="utf-8")


def _escribir_referencia(ruta: pathlib.Path, filas: list[tuple[str, str]]) -> None:
    documento = {
        "schema_version": 1,
        "metadata": {"total_casos": len(filas)},
        "casos": [{"id": caso, "sector_asignado": sector} for caso, sector in filas],
    }
    ruta.write_text(json.dumps(documento), encoding="utf-8")


def test_cargar_predicciones_mapea_caso_a_sector_predicho(tmp_path):
    ruta = tmp_path / "predicciones.json"
    _escribir_predicciones(ruta, [("C1", "Sistemas"), ("C2", "Bases de Datos")])

    predicciones = c224.cargar_predicciones(ruta)

    assert predicciones == {"C1": "Sistemas", "C2": "Bases de Datos"}


def test_cargar_referencia_mapea_caso_a_sector_asignado(tmp_path):
    ruta = tmp_path / "referencia.json"
    _escribir_referencia(ruta, [("C1", "Sistemas"), ("C2", "Bases de Datos")])

    referencia = c224.cargar_referencia(ruta)

    assert referencia == {"C1": "Sistemas", "C2": "Bases de Datos"}


# ---------------------------------------------------------------------------
# Regla vigente y mayoria (funciones puras)
# ---------------------------------------------------------------------------
def _caso(e3: str, e4: str, e5: str | None, origen: str) -> dict[str, object]:
    etiquetas = {"E3": e3, "E4": e4, "E5": e5}
    distintos = {valor for valor in etiquetas.values() if valor is not None}
    return {
        "etiquetas": etiquetas,
        "origen": {"origen": origen, "tres_vias": len(distintos) == 3},
    }


def _casos_reales() -> dict[str, dict[str, object]]:
    etiquetas = c224.cargar_etiquetas(c224.CAMPANA / "doble_etiquetado_arbitrado.csv")
    origen = c224.cargar_origen(c224.CAMPANA / "arbitraje_tres_vias.json")
    return {
        caso: {"etiquetas": etiquetas[caso], "origen": origen[caso]}
        for caso in sorted(etiquetas)
    }


def _seis_reales() -> dict[str, dict[str, str | None]]:
    casos = _casos_reales()
    return {caso: casos[caso]["etiquetas"] for caso in c224.casos_sin_mayoria(casos)}


def test_regla_vigente_usa_consenso_cuando_e3_y_e4_coinciden():
    caso = _caso("Sistemas", "Sistemas", None, "consenso_e3_e4")
    assert c224.regla_vigente(caso["etiquetas"], caso["origen"]) == "Sistemas"


def test_regla_vigente_usa_e5_cuando_e3_y_e4_difieren():
    caso = _caso("Sistemas", "Bases de Datos", "Soporte Tecnico Hardware", "arbitraje_e5")
    assert c224.regla_vigente(caso["etiquetas"], caso["origen"]) == "Soporte Tecnico Hardware"


def test_mayoria_devuelve_la_etiqueta_repetida():
    assert c224.mayoria({"E3": "Sistemas", "E4": "Sistemas", "E5": None}) == "Sistemas"
    assert c224.mayoria({"E3": "Sistemas", "E4": "Bases de Datos", "E5": "Sistemas"}) == "Sistemas"
    assert c224.mayoria({"E3": "Sistemas", "E4": "Sistemas", "E5": "Bases de Datos"}) == "Sistemas"


def test_mayoria_devuelve_none_con_tres_etiquetas_distintas():
    etiquetas = {"E3": "Sistemas", "E4": "Bases de Datos", "E5": "Seguridad Informatica"}
    assert c224.mayoria(etiquetas) is None


# ---------------------------------------------------------------------------
# Coincidencia con la mayoria
# ---------------------------------------------------------------------------
def test_acuerdo_con_mayoria_cuenta_y_lista_los_casos_coincidentes():
    casos = {
        "C1": _caso("Sistemas", "Sistemas", None, "consenso_e3_e4"),
        "C2": _caso("Sistemas", "Bases de Datos", "Sistemas", "arbitraje_e5"),
        "C3": _caso("Sistemas", "Bases de Datos", "Seguridad Informatica", "arbitraje_e5"),
    }

    resultado = c224.acuerdo_con_mayoria(casos)

    assert resultado["n"] == 2
    assert resultado["total"] == 3
    assert resultado["ids"] == ["C1", "C2"]


def test_acuerdo_con_mayoria_anclaje_real_200_de_206():
    resultado = c224.acuerdo_con_mayoria(_casos_reales())

    assert resultado["n"] == 200
    assert resultado["total"] == 206


# ---------------------------------------------------------------------------
# Casos sin mayoria
# ---------------------------------------------------------------------------
def test_casos_sin_mayoria_lista_solo_las_tres_vias():
    casos = {
        "C1": _caso("Sistemas", "Sistemas", None, "consenso_e3_e4"),
        "C2": _caso("Sistemas", "Bases de Datos", "Sistemas", "arbitraje_e5"),
        "C3": _caso("Sistemas", "Bases de Datos", "Seguridad Informatica", "arbitraje_e5"),
    }

    assert c224.casos_sin_mayoria(casos) == ["C3"]


def test_casos_sin_mayoria_anclaje_real_6_identificadores():
    assert c224.casos_sin_mayoria(_casos_reales()) == [
        "I033",
        "I042",
        "I056",
        "I130",
        "I194",
        "I198",
    ]


# ---------------------------------------------------------------------------
# Rango de exactitud
# ---------------------------------------------------------------------------
def test_rango_exactitud_calcula_minimo_maximo_y_reasignables():
    referencia = {"C1": "A", "C2": "B", "C3": "C", "C4": "D"}
    predicciones = {"C1": "A", "C2": "X", "C3": "C", "C4": "Y"}
    seis = {
        "C1": {"E3": "A", "E4": "B", "E5": "C"},
        "C2": {"E3": "A", "E4": "B", "E5": "C"},
    }

    resultado = c224.rango_exactitud(referencia, predicciones, seis)

    # Aciertos vigentes: C1 y C3. C1 tiene la prediccion dentro de las etiquetas
    # del caso; C2 no. Por eso k = 1 y el maximo es 3.
    assert resultado["aciertos"] == 2
    assert resultado["total"] == 4
    assert resultado["k"] == 1
    assert resultado["max"] == 3
    assert resultado["reasignables"] == ["C1"]
    assert resultado["no_reasignables"] == ["C2"]


# ---------------------------------------------------------------------------
# Metricas por clase bajo extremos
# ---------------------------------------------------------------------------
def test_metricas_por_clase_bajo_extremos_devuelve_ambos_extremos():
    referencia = {
        "C1": "Seguridad Informatica",
        "C2": "Soporte Tecnico Hardware",
        "C3": "Soporte Tecnico Software",
        "C4": "Bases de Datos",
        "C5": "Sistemas",
    }
    predicciones = {
        "C1": "Soporte Tecnico Hardware",
        "C2": "Soporte Tecnico Hardware",
        "C3": "Soporte Tecnico Software",
        "C4": "Bases de Datos",
        "C5": "Sistemas",
    }
    seis = {
        "C1": {
            "E3": "Seguridad Informatica",
            "E4": "Soporte Tecnico Software",
            "E5": "Soporte Tecnico Hardware",
        }
    }

    resultado = c224.metricas_por_clase_bajo_extremos(referencia, predicciones, seis)

    assert set(resultado) == {"vigente", "maximo"}
    for extremo in resultado.values():
        assert set(extremo) == {"matriz", "precision", "sensibilidad", "f1", "soporte", "macro_f1"}
    # El extremo maximo reasigna C1 a Soporte Tecnico Hardware y deja el resto igual.
    assert resultado["vigente"]["matriz"]["Seguridad Informatica"]["Soporte Tecnico Hardware"] == 1
    assert resultado["maximo"]["matriz"]["Seguridad Informatica"]["Soporte Tecnico Hardware"] == 0
    assert resultado["maximo"]["matriz"]["Soporte Tecnico Hardware"]["Soporte Tecnico Hardware"] == 2


# ---------------------------------------------------------------------------
# Anclajes y salidas
# ---------------------------------------------------------------------------


