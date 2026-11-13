"""
Tests del ensamblado del corpus arbitrado final (c-206, tarea 4.5).

El ensamblador toma la planilla de `E3`/`E4`, la de `E5` y el JSON de trabajo (con las
descripciones), arma el corpus final con el mismo esquema que
`evaluation/data/campana/corpus_independiente.json` y escribe un sidecar con la bandera
`tres_vias` por caso (decision D9). Todo corre sin red y con casos SINTETICOS.
"""

from __future__ import annotations

import hashlib
import json

import pytest

from evaluation.corpus import CasoEvaluacion

INICIO_OK = "2026-11-13T14:00:00-03:00"
FIN_OK = "2026-11-13T14:05:00-03:00"
SEG = "Seguridad Informatica"
HW = "Soporte Tecnico Hardware"
SW = "Soporte Tecnico Software"
BD = "Bases de Datos"
SIS = "Sistemas"

COLUMNAS_CORPUS = (
    "id",
    "descripcion",
    "canal_origen",
    "sector_asignado",
    "sectores_adicionales",
    "tiempo_manual_s",
    "tiempo_automatizado_s",
)


def _fila(id_caso, alias, sector, adicionales=""):
    return {
        "id_caso": id_caso,
        "id_etiquetador": alias,
        "tarea": "doble_etiquetado",
        "sector_etiquetado": sector,
        "sectores_adicionales_etiquetados": adicionales,
        "inicio": INICIO_OK,
        "timestamp": FIN_OK,
    }


def _caso(id_caso, descripcion=None):
    return CasoEvaluacion(
        id=id_caso,
        descripcion=descripcion or f"descripcion sintetica {id_caso}",
        sector_asignado=SIS,
        sectores_adicionales=[],
        canal_origen="correo",
        tiempo_manual_s=120.0,
        tiempo_automatizado_s=3.5,
    )


@pytest.fixture
def trabajo():
    return [_caso(i) for i in ("I001", "I002", "I003")]


@pytest.fixture
def registros():
    """I001 concordante; I002 discordante de dos vias (E5 = E4); I003 discordante de tres vias."""
    return [
        _fila("I001", "E3", SEG),
        _fila("I001", "E4", SEG),
        _fila("I002", "E3", SEG),
        _fila("I002", "E4", HW),
        _fila("I002", "E5", HW),
        _fila("I003", "E3", BD),
        _fila("I003", "E4", SIS),
        _fila("I003", "E5", SW),
    ]


def _por_id(casos):
    return {caso["id"]: caso for caso in casos}


def _sidecar_por_id(sidecar):
    return {caso["id"]: caso for caso in sidecar["casos"]}


# ---------------------------------------------------------------------------
# Esquema y contenido del corpus
# ---------------------------------------------------------------------------
def test_el_corpus_ensamblado_usa_el_mismo_esquema_que_el_versionado(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)

    assert list(ensamblado.corpus) == ["schema_version", "metadata", "casos"]
    assert ensamblado.corpus["schema_version"] == 1
    assert ensamblado.corpus["metadata"]["total_casos"] == 3
    for caso in ensamblado.corpus["casos"]:
        assert tuple(caso) == COLUMNAS_CORPUS


def test_los_casos_salen_ordenados_por_id_y_con_la_descripcion_del_trabajo(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)

    assert [caso["id"] for caso in ensamblado.corpus["casos"]] == ["I001", "I002", "I003"]
    por_id = _por_id(ensamblado.corpus["casos"])
    assert por_id["I001"]["descripcion"] == "descripcion sintetica I001"
    assert por_id["I001"]["canal_origen"] == "correo"
    assert por_id["I001"]["tiempo_manual_s"] == 120.0


def test_el_concordante_toma_el_consenso_de_e3_e4(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)

    assert _por_id(ensamblado.corpus["casos"])["I001"]["sector_asignado"] == SEG
    assert _sidecar_por_id(ensamblado.sidecar)["I001"]["origen"] == "consenso_e3_e4"


def test_el_discordante_toma_la_etiqueta_de_e5(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)

    assert _por_id(ensamblado.corpus["casos"])["I002"]["sector_asignado"] == HW
    assert _sidecar_por_id(ensamblado.sidecar)["I002"]["origen"] == "arbitraje_e5"


def test_el_discordante_de_tres_vias_marca_la_bandera_y_toma_e5(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)
    sidecar = _sidecar_por_id(ensamblado.sidecar)

    assert _por_id(ensamblado.corpus["casos"])["I003"]["sector_asignado"] == SW
    assert sidecar["I003"]["tres_vias"] is True
    assert sidecar["I002"]["tres_vias"] is False
    assert sidecar["I001"]["tres_vias"] is False
    assert ensamblado.sidecar["metadata"]["n_tres_vias"] == 1
    assert ensamblado.sidecar["metadata"]["n_arbitraje_e5"] == 2


def test_los_adicionales_del_arbitrado_exigen_dos_de_tres(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    for fila in registros:
        if fila["id_caso"] == "I002":
            fila["sectores_adicionales_etiquetados"] = {
                "E3": f"{BD}|{SIS}",
                "E4": BD,
                "E5": f"{SIS}|{SW}",
            }[fila["id_etiquetador"]]

    ensamblado = ensamblar_corpus(registros, trabajo)

    assert _por_id(ensamblado.corpus["casos"])["I002"]["sectores_adicionales"] == sorted((BD, SIS))


# ---------------------------------------------------------------------------
# Sidecar: la bandera no entra al esquema del corpus (decision D9)
# ---------------------------------------------------------------------------
def test_la_bandera_tres_vias_vive_solo_en_el_sidecar(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)

    for caso in ensamblado.corpus["casos"]:
        assert "tres_vias" not in caso and "origen" not in caso
    assert list(ensamblado.sidecar) == ["schema_version", "metadata", "casos"]
    for caso in ensamblado.sidecar["casos"]:
        assert tuple(caso) == ("id", "origen", "tres_vias")


def test_el_sidecar_liga_al_corpus_por_su_sha256(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)
    sha = hashlib.sha256(ensamblado.texto_corpus.encode("utf-8")).hexdigest()

    assert ensamblado.sha256_corpus == sha
    assert ensamblado.sidecar["metadata"]["corpus_sha256"] == sha
    assert ensamblado.sidecar["metadata"]["corpus"] == "corpus_independiente_arbitrado.json"


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------
def test_un_discordante_sin_e5_falla(registros, trabajo):
    from evaluation.arbitraje import ArbitrajeError, ensamblar_corpus

    registros = [r for r in registros if not (r["id_caso"] == "I002" and r["id_etiquetador"] == "E5")]

    with pytest.raises(ArbitrajeError, match="I002"):
        ensamblar_corpus(registros, trabajo)


def test_un_caso_arbitrado_sin_descripcion_en_el_trabajo_falla(registros):
    from evaluation.arbitraje import EnsambladoError, ensamblar_corpus

    trabajo = [_caso("I001"), _caso("I002")]  # falta I003

    with pytest.raises(EnsambladoError, match="I003"):
        ensamblar_corpus(registros, trabajo)


def test_un_caso_del_trabajo_sin_etiqueta_falla(registros, trabajo):
    from evaluation.arbitraje import EnsambladoError, ensamblar_corpus

    trabajo = [*trabajo, _caso("I004")]  # I004 no tiene etiquetas

    with pytest.raises(EnsambladoError, match="I004"):
        ensamblar_corpus(registros, trabajo)


# ---------------------------------------------------------------------------
# Reproducibilidad
# ---------------------------------------------------------------------------
def test_dos_corridas_producen_bytes_identicos(registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus

    primera = ensamblar_corpus(registros, trabajo)
    segunda = ensamblar_corpus(registros, trabajo)

    assert primera.texto_corpus == segunda.texto_corpus
    assert primera.texto_sidecar == segunda.texto_sidecar
    assert primera.sha256_corpus == segunda.sha256_corpus


def test_el_corpus_ensamblado_es_cargable(tmp_path, registros, trabajo):
    from evaluation.arbitraje import ensamblar_corpus
    from evaluation.corpus import cargar_corpus

    ensamblado = ensamblar_corpus(registros, trabajo)
    ruta = tmp_path / "corpus_independiente_arbitrado.json"
    ruta.write_bytes(ensamblado.texto_corpus.encode("utf-8"))

    casos = cargar_corpus(ruta)

    assert [caso.id for caso in casos] == ["I001", "I002", "I003"]
    assert casos[2].sector_asignado == SW


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def _escribir_csv(ruta, filas, columnas=None):
    import csv

    encabezado = list(columnas) if columnas is not None else list(filas[0])
    with ruta.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=encabezado, lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


def _escribir_csv_vacio(ruta):
    _escribir_csv(
        ruta,
        [],
        columnas=(
            "id_caso",
            "id_etiquetador",
            "tarea",
            "sector_etiquetado",
            "sectores_adicionales_etiquetados",
            "inicio",
            "timestamp",
        ),
    )


def _escribir_corpus(ruta, casos):
    documento = {
        "schema_version": 1,
        "metadata": {"total_casos": len(casos)},
        "casos": [
            {
                "id": caso.id,
                "descripcion": caso.descripcion,
                "canal_origen": caso.canal_origen,
                "sector_asignado": caso.sector_asignado,
                "sectores_adicionales": list(caso.sectores_adicionales),
                "tiempo_manual_s": caso.tiempo_manual_s,
                "tiempo_automatizado_s": caso.tiempo_automatizado_s,
            }
            for caso in casos
        ],
    }
    ruta.write_text(json.dumps(documento, ensure_ascii=False, indent=2), encoding="utf-8")


def test_cli_ensamblar_escribe_corpus_y_sidecar(tmp_path, registros, trabajo, capsys):
    from evaluation.arbitraje import main

    primaria, arbitraje, corpus_json = tmp_path / "e34.csv", tmp_path / "e5.csv", tmp_path / "t.json"
    salida, sidecar = tmp_path / "arb.json", tmp_path / "side.json"
    _escribir_csv(primaria, [r for r in registros if r["id_etiquetador"] != "E5"])
    _escribir_csv(arbitraje, [r for r in registros if r["id_etiquetador"] == "E5"])
    _escribir_corpus(corpus_json, trabajo)

    codigo = main(
        [
            "ensamblar",
            "--primaria",
            str(primaria),
            "--arbitraje",
            str(arbitraje),
            "--corpus",
            str(corpus_json),
            "--salida",
            str(salida),
            "--sidecar",
            str(sidecar),
        ]
    )

    assert codigo == 0
    assert salida.exists() and sidecar.exists()
    assert hashlib.sha256(salida.read_bytes()).hexdigest() in capsys.readouterr().out
    documento = json.loads(salida.read_text(encoding="utf-8"))
    assert [caso["id"] for caso in documento["casos"]] == ["I001", "I002", "I003"]


def test_cli_ensamblar_es_reproducible(tmp_path, registros, trabajo):
    from evaluation.arbitraje import main

    primaria, arbitraje, corpus_json = tmp_path / "e34.csv", tmp_path / "e5.csv", tmp_path / "t.json"
    salida, sidecar = tmp_path / "arb.json", tmp_path / "side.json"
    _escribir_csv(primaria, [r for r in registros if r["id_etiquetador"] != "E5"])
    _escribir_csv(arbitraje, [r for r in registros if r["id_etiquetador"] == "E5"])
    _escribir_corpus(corpus_json, trabajo)
    argumentos = [
        "ensamblar",
        "--primaria",
        str(primaria),
        "--arbitraje",
        str(arbitraje),
        "--corpus",
        str(corpus_json),
        "--salida",
        str(salida),
        "--sidecar",
        str(sidecar),
    ]

    assert main(argumentos) == 0
    primera = (salida.read_bytes(), sidecar.read_bytes())
    assert main(argumentos) == 0

    assert (salida.read_bytes(), sidecar.read_bytes()) == primera


def test_cli_ensamblar_sin_e5_sale_con_el_codigo_de_la_primera_regla(tmp_path, registros, trabajo):
    from evaluation.arbitraje import main

    primaria, arbitraje, corpus_json = tmp_path / "e34.csv", tmp_path / "e5.csv", tmp_path / "t.json"
    _escribir_csv(primaria, [r for r in registros if r["id_etiquetador"] != "E5"])
    _escribir_csv_vacio(arbitraje)  # encabezado solo: E5 aun no etiqueto
    _escribir_corpus(corpus_json, trabajo)

    codigo = main(
        [
            "ensamblar",
            "--primaria",
            str(primaria),
            "--arbitraje",
            str(arbitraje),
            "--corpus",
            str(corpus_json),
            "--salida",
            str(tmp_path / "arb.json"),
            "--sidecar",
            str(tmp_path / "side.json"),
        ]
    )

    assert codigo == 10  # regla (a) / (b): falta E5


def test_cli_ensamblar_sin_archivo_sale_con_dos(tmp_path):
    from evaluation.arbitraje import main

    assert (
        main(
            [
                "ensamblar",
                "--primaria",
                str(tmp_path / "no.csv"),
                "--arbitraje",
                str(tmp_path / "no2.csv"),
                "--corpus",
                str(tmp_path / "no.json"),
                "--salida",
                str(tmp_path / "arb.json"),
                "--sidecar",
                str(tmp_path / "side.json"),
            ]
        )
        == 2
    )
