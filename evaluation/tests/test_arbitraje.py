"""
Tests del validador y del constructor de la referencia arbitrada (c-206, ARB-004/007).

El arbitraje de los discordantes por un tercer etiquetador `E5` vive en un modulo propio
(`evaluation/arbitraje.py`); el contrato de dos etiquetadores de `doble_etiquetado` no se
toca. Todo corre sin red con casos SINTETICOS (ids `I001..`, sin texto real).
"""

from __future__ import annotations

import pytest

from evaluation.corpus import CasoEvaluacion

INICIO_OK = "2026-11-12T14:00:00-03:00"
FIN_OK = "2026-11-12T14:05:00-03:00"
SEG = "Seguridad Informatica"
HW = "Soporte Tecnico Hardware"
SW = "Soporte Tecnico Software"
BD = "Bases de Datos"
SIS = "Sistemas"


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


def _caso(id_caso):
    return CasoEvaluacion(
        id=id_caso,
        descripcion="caso sintetico",
        sector_asignado=SIS,
        sectores_adicionales=[],
        canal_origen="correo",
    )


@pytest.fixture
def corpus():
    return [_caso(i) for i in ("I001", "I002", "I003")]


@pytest.fixture
def registros():
    """I001 concordante (E3=E4); I002 y I003 discordantes arbitrados por E5."""
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


def _reglas(resultado):
    return [o.regla for o in resultado.ofensas]


# ---------------------------------------------------------------------------
# 2.1 — validador de E3/E4/E5
# ---------------------------------------------------------------------------
def test_planilla_con_e3_e4_e5_es_valida(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    resultado = validar_arbitraje(registros, corpus)

    assert resultado.valida is True
    assert resultado.resumen.etiquetadores == ("E3", "E4", "E5")
    assert resultado.resumen.n_casos == 3
    assert resultado.resumen.n_registros == 8


def test_planilla_sin_e5_es_rechazada_por_regla_a(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    sin_e5 = [r for r in registros if r["id_etiquetador"] != "E5"]

    resultado = validar_arbitraje(sin_e5, corpus)

    assert "a" in _reglas(resultado)
    assert any("E5" in (o.id_etiquetador or o.detalle) for o in resultado.ofensas)


def test_planilla_con_cuarto_etiquetador_es_rechazada_por_regla_a(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    registros.append(_fila("I002", "E6", HW))

    resultado = validar_arbitraje(registros, corpus)

    ofensas_a = [o for o in resultado.ofensas if o.regla == "a"]
    assert [o.id_etiquetador for o in ofensas_a] == ["E6"]


def test_alias_desconocido_en_lugar_de_e4_es_rechazado(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    for r in registros:
        if r["id_etiquetador"] == "E4":
            r["id_etiquetador"] = "E7"

    resultado = validar_arbitraje(registros, corpus)

    aliases = {o.id_etiquetador for o in resultado.ofensas if o.regla == "a"}
    assert {"E7", "E4"} <= aliases


# ---------------------------------------------------------------------------
# 2.1 — referencia arbitrada
# ---------------------------------------------------------------------------
def test_referencia_discordante_toma_la_etiqueta_de_e5(registros):
    from evaluation.arbitraje import construir_referencia

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I002"].sector == HW
    assert referencia["I002"].origen == "arbitraje_e5"


def test_referencia_concordante_toma_el_consenso_de_e3_e4(registros):
    from evaluation.arbitraje import construir_referencia

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I001"].sector == SEG
    assert referencia["I001"].origen == "consenso_e3_e4"
    assert referencia["I001"].tres_vias is False


# ---------------------------------------------------------------------------
# 2.3 — bandera de tres vias y conjunto laxo arbitrado
# ---------------------------------------------------------------------------
def test_tres_etiquetas_distintas_marcan_la_bandera_y_toman_e5(registros):
    from evaluation.arbitraje import construir_referencia

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I003"].tres_vias is True
    assert referencia["I003"].sector == SW
    assert referencia["I002"].tres_vias is False  # E5 coincide con E4: dos etiquetas distintas


def test_e5_coincide_con_e3_no_es_discordancia_de_tres_vias(registros):
    from evaluation.arbitraje import construir_referencia

    for r in registros:
        if r["id_caso"] == "I002" and r["id_etiquetador"] == "E5":
            r["sector_etiquetado"] = SEG  # E5 = E3 != E4

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I002"].sector == SEG
    assert referencia["I002"].tres_vias is False


def test_laxo_arbitrado_exige_al_menos_dos_de_tres_etiquetadores(registros):
    from evaluation.arbitraje import construir_referencia

    for r in registros:
        if r["id_caso"] == "I002":
            r["sectores_adicionales_etiquetados"] = {
                "E3": f"{BD}|{SIS}",  # BD y SIS
                "E4": BD,  # BD
                "E5": f"{SIS}|{SW}",  # SIS y SW
            }[r["id_etiquetador"]]

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    # BD (E3+E4) y SIS (E3+E5) llegan a dos; SW solo a uno.
    assert referencia["I002"].sectores_adicionales == tuple(sorted((BD, SIS)))


def test_laxo_arbitrado_un_adicional_de_un_solo_etiquetador_no_entra(registros):
    from evaluation.arbitraje import construir_referencia

    for r in registros:
        if r["id_caso"] == "I002" and r["id_etiquetador"] == "E5":
            r["sectores_adicionales_etiquetados"] = BD

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I002"].sectores_adicionales == ()


def test_laxo_arbitrado_excluye_el_sector_de_la_referencia(registros):
    from evaluation.arbitraje import construir_referencia

    for r in registros:
        if r["id_caso"] == "I002" and r["id_etiquetador"] in ("E3", "E4"):
            r["sectores_adicionales_etiquetados"] = HW  # E5 lo dejo como principal

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert HW not in referencia["I002"].sectores_adicionales


def test_laxo_concordante_es_la_interseccion_de_e3_y_e4(registros):
    from evaluation.arbitraje import construir_referencia

    for r in registros:
        if r["id_caso"] == "I001":
            r["sectores_adicionales_etiquetados"] = {"E3": f"{BD}|{SW}", "E4": SW}[
                r["id_etiquetador"]
            ]

    referencia = {r.id_caso: r for r in construir_referencia(registros)}

    assert referencia["I001"].sectores_adicionales == (SW,)


# ---------------------------------------------------------------------------
# Rechazos adicionales del validador
# ---------------------------------------------------------------------------
def test_caso_sin_registro_de_e4_es_rechazado_por_regla_b(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    registros = [
        r for r in registros if not (r["id_caso"] == "I001" and r["id_etiquetador"] == "E4")
    ]

    resultado = validar_arbitraje(registros, corpus)

    ofensas_b = [(o.id_caso, o.id_etiquetador) for o in resultado.ofensas if o.regla == "b"]
    assert ofensas_b == [("I001", "E4")]


def test_discordante_sin_e5_es_rechazado_por_regla_b(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    registros = [
        r for r in registros if not (r["id_caso"] == "I003" and r["id_etiquetador"] == "E5")
    ]

    resultado = validar_arbitraje(registros, corpus)

    ofensas_b = [(o.id_caso, o.id_etiquetador) for o in resultado.ofensas if o.regla == "b"]
    assert ofensas_b == [("I003", "E5")]


def test_e5_sobre_un_caso_concordante_es_rechazado_por_regla_b(corpus, registros):
    """E5 arbitra solo los discordantes: etiquetar uno concordante lo vuelve un 'consenso' a tres."""
    from evaluation.arbitraje import validar_arbitraje

    registros.append(_fila("I001", "E5", HW))

    resultado = validar_arbitraje(registros, corpus)

    ofensas_b = [(o.id_caso, o.id_etiquetador) for o in resultado.ofensas if o.regla == "b"]
    assert ofensas_b == [("I001", "E5")]


def test_regla_d_id_desconocido_y_regla_e_sector_no_canonico_siguen_vigentes(corpus, registros):
    from evaluation.arbitraje import validar_arbitraje

    registros.append(_fila("I999", "E3", SIS))
    registros[0]["sector_etiquetado"] = "Operaciones"

    resultado = validar_arbitraje(registros, corpus)

    assert {"d", "e"} <= set(_reglas(resultado))


def test_construir_referencia_discordante_sin_e5_falla_con_mensaje_claro(registros):
    from evaluation.arbitraje import ArbitrajeError, construir_referencia

    registros = [
        r for r in registros if not (r["id_caso"] == "I002" and r["id_etiquetador"] == "E5")
    ]

    with pytest.raises(ArbitrajeError, match="I002"):
        construir_referencia(registros)


# ---------------------------------------------------------------------------
# Hoja ciega y CLI
# ---------------------------------------------------------------------------
def _escribir_csv(ruta, filas):
    import csv

    with ruta.open("w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator="\n")
        escritor.writeheader()
        escritor.writerows(filas)


def _escribir_corpus(ruta, ids):
    import json

    casos = [
        {
            "id": i,
            "descripcion": f"descripcion sintetica {i}",
            "canal_origen": "correo",
            "sector_asignado": SIS,
            "sectores_adicionales": [],
        }
        for i in ids
    ]
    documento = {"schema_version": 1, "metadata": {"total_casos": len(ids)}, "casos": casos}
    ruta.write_text(json.dumps(documento), encoding="utf-8")


def test_hoja_ciega_solo_trae_id_y_descripcion_de_los_discordantes(corpus, registros):
    from evaluation.arbitraje import construir_hoja_ciega

    sin_e5 = [r for r in registros if r["id_etiquetador"] != "E5"]

    hoja = construir_hoja_ciega(sin_e5, corpus)

    assert [f["id_caso"] for f in hoja] == ["I002", "I003"]  # orden determinista por id
    assert all(set(f) == {"id_caso", "descripcion"} for f in hoja)


def test_hoja_ciega_no_filtra_etiquetas_ni_referencia(corpus, registros):
    from evaluation.arbitraje import construir_hoja_ciega

    hoja = construir_hoja_ciega(registros, corpus)

    texto = repr(hoja)
    for sector in (SEG, HW, SW, BD):
        assert sector not in texto


def test_hoja_ciega_con_discordante_ausente_del_corpus_falla(registros):
    from evaluation.arbitraje import ArbitrajeError, construir_hoja_ciega

    with pytest.raises(ArbitrajeError, match="I003"):
        construir_hoja_ciega(registros, [_caso("I001"), _caso("I002")])


def test_cli_validar_sale_con_cero_en_planilla_valida(tmp_path, registros):
    from evaluation.arbitraje import main

    planilla, corpus_json = tmp_path / "p.csv", tmp_path / "c.json"
    _escribir_csv(planilla, registros)
    _escribir_corpus(corpus_json, ["I001", "I002", "I003"])

    assert main(["validar", "--planilla", str(planilla), "--corpus", str(corpus_json)]) == 0


def test_cli_validar_sale_con_el_codigo_de_la_primera_regla_ofendida(tmp_path, registros):
    from evaluation.arbitraje import main

    planilla, corpus_json = tmp_path / "p.csv", tmp_path / "c.json"
    _escribir_csv(planilla, [r for r in registros if r["id_etiquetador"] != "E5"])
    _escribir_corpus(corpus_json, ["I001", "I002", "I003"])

    assert main(["validar", "--planilla", str(planilla), "--corpus", str(corpus_json)]) == 10


def test_cli_hoja_ciega_escribe_encabezado_y_filas_en_lf(tmp_path, registros):
    from evaluation.arbitraje import main

    primaria, corpus_json, salida = tmp_path / "p.csv", tmp_path / "c.json", tmp_path / "hoja.csv"
    _escribir_csv(primaria, [r for r in registros if r["id_etiquetador"] != "E5"])
    _escribir_corpus(corpus_json, ["I001", "I002", "I003"])

    codigo = main(
        [
            "hoja-ciega",
            "--primaria",
            str(primaria),
            "--corpus",
            str(corpus_json),
            "--salida",
            str(salida),
        ]
    )

    crudo = salida.read_bytes()
    assert codigo == 0
    assert b"\r" not in crudo and not crudo.startswith(b"\xef\xbb\xbf")
    assert crudo.decode("utf-8").splitlines() == [
        "id_caso,descripcion",
        "I002,descripcion sintetica I002",
        "I003,descripcion sintetica I003",
    ]


def test_cli_sin_archivo_sale_con_dos(tmp_path):
    from evaluation.arbitraje import main

    assert (
        main(
            [
                "validar",
                "--planilla",
                str(tmp_path / "no.csv"),
                "--corpus",
                str(tmp_path / "no.json"),
            ]
        )
        == 2
    )
