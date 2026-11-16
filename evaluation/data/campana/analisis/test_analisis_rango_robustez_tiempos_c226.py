"""Pruebas del analisis offline del rango de robustez de tiempos (c-226).

TDD estricto de las funciones puras con casos sinteticos (sin I/O de red) mas la
integracion con los artefactos versionados. Cubre el rango del estimando primario
(descuentos de 0, 5 y 10 s y su minimo), el desagregado por canal, las reducciones por
operador de la campana complementaria, el efecto de posicion, la cota de granularidad del
instrumento, la verificacion de anclajes que aborta antes de escribir y la escritura
determinista byte a byte.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_rango_robustez_tiempos_c226 as c226  # noqa: E402


# ---------------------------------------------------------------------------
# Rango de descuentos (funcion pura)
# ---------------------------------------------------------------------------
def test_rango_descuentos_calcula_reduccion_por_escenario_y_minimo():
    manual = [100.0, 100.0, 100.0]
    automatizado = [50.0, 50.0, 50.0]

    rango = c226.rango_descuentos(manual, automatizado, descuentos=(0.0, 5.0, 10.0))

    assert [e["descuento_s"] for e in rango["escenarios"]] == [0.0, 5.0, 10.0]
    assert rango["escenarios"][0]["reduccion_media"] == pytest.approx(0.5)
    assert rango["escenarios"][1]["reduccion_media"] == pytest.approx(1 - 50 / 95)
    assert rango["escenarios"][2]["reduccion_media"] == pytest.approx(1 - 50 / 90)
    assert rango["escenario_minimo"]["descuento_s"] == 10.0
    assert rango["escenario_minimo"]["reduccion_media"] == pytest.approx(1 - 50 / 90)
    assert rango["reduccion_primaria"] == pytest.approx(0.5)
    assert rango["rango"] == pytest.approx([1 - 50 / 90, 0.5])


def test_rango_descuentos_es_monotono_decreciente_con_el_descuento():
    manual = [100.0, 100.0, 100.0]
    automatizado = [50.0, 50.0, 50.0]

    rango = c226.rango_descuentos(manual, automatizado)

    reducciones = [e["reduccion_media"] for e in rango["escenarios"]]
    assert reducciones[0] > reducciones[1] > reducciones[2]
    assert rango["escenario_minimo"]["descuento_s"] == 10.0


def test_rango_descuentos_distingue_la_media_manual_ajustada():
    manual = [80.0, 60.0]
    automatizado = [20.0, 20.0]

    rango = c226.rango_descuentos(manual, automatizado, descuentos=(0.0, 10.0))

    assert rango["escenarios"][0]["media_manual_ajustada"] == pytest.approx(70.0)
    assert rango["escenarios"][1]["media_manual_ajustada"] == pytest.approx(60.0)


def test_rango_descuentos_soporta_base_manual_negativa_sin_romper():
    manual = [10.0, 10.0]
    automatizado = [5.0, 5.0]

    rango = c226.rango_descuentos(manual, automatizado, descuentos=(0.0, 20.0))

    assert rango["reduccion_primaria"] == pytest.approx(0.5)
    # Con base manual negativa (descuento 20 s > media 10 s) la formula da 1 - 5/(-10).
    assert rango["escenarios"][1]["reduccion_media"] == pytest.approx(1.5)
    assert rango["escenario_minimo"]["descuento_s"] == 0.0


# ---------------------------------------------------------------------------
# Desagregado por canal (funcion pura)
# ---------------------------------------------------------------------------
def test_resumen_por_canal_separa_canales_y_elige_el_minimo():
    casos = [
        {"canal_origen": "A", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 50.0},
        {"canal_origen": "B", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 25.0},
        {"canal_origen": "C", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 90.0},
    ]

    resumen = c226.resumen_por_canal(casos)

    assert resumen["por_canal"]["A"]["reduccion_media"] == pytest.approx(0.5)
    assert resumen["por_canal"]["B"]["reduccion_media"] == pytest.approx(0.75)
    assert resumen["por_canal"]["C"]["reduccion_media"] == pytest.approx(0.1)
    assert {canal: d["n"] for canal, d in resumen["por_canal"].items()} == {
        "A": 1,
        "B": 1,
        "C": 1,
    }
    assert resumen["canal_minimo"] == "C"
    assert resumen["reduccion_minima"] == pytest.approx(0.1)


def test_resumen_por_canal_agrupa_varios_casos_del_mismo_canal():
    casos = [
        {"canal_origen": "X", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 20.0},
        {"canal_origen": "X", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 60.0},
        {"canal_origen": "Y", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 90.0},
    ]

    resumen = c226.resumen_por_canal(casos)

    assert resumen["por_canal"]["X"]["n"] == 2
    assert resumen["por_canal"]["X"]["reduccion_media"] == pytest.approx(0.6)
    assert resumen["canal_minimo"] == "Y"


def test_resumen_por_canal_con_un_solo_canal_es_su_propio_minimo():
    casos = [
        {"canal_origen": "unico", "tiempo_manual_s": 100.0, "tiempo_automatizado_s": 40.0}
    ]

    resumen = c226.resumen_por_canal(casos)

    assert resumen["canal_minimo"] == "unico"
    assert resumen["por_canal"]["unico"]["reduccion_media"] == pytest.approx(0.6)


# ---------------------------------------------------------------------------
# Reducciones por operador (funcion pura)
# ---------------------------------------------------------------------------
def test_resumen_por_operador_calcula_por_operador_y_agregado():
    registros = [
        {"caso_id": "X", "operador": "O1", "duracion_s": 100.0},
        {"caso_id": "Y", "operador": "O1", "duracion_s": 100.0},
        {"caso_id": "Z", "operador": "O2", "duracion_s": 50.0},
    ]
    automatizado = {"X": 50.0, "Y": 50.0, "Z": 50.0}

    resumen = c226.resumen_por_operador(registros, automatizado)

    assert resumen["por_operador"]["O1"]["n"] == 2
    assert resumen["por_operador"]["O1"]["reduccion_media"] == pytest.approx(0.5)
    assert resumen["por_operador"]["O2"]["n"] == 1
    assert resumen["por_operador"]["O2"]["reduccion_media"] == pytest.approx(0.0)
    assert resumen["agregado"]["n"] == 3
    assert resumen["agregado"]["reduccion_media"] == pytest.approx(1 - 50 / (250 / 3))


def test_resumen_por_operador_promedia_los_casos_con_doble_cobertura():
    registros = [
        {"caso_id": "X", "operador": "O1", "duracion_s": 100.0},
        {"caso_id": "X", "operador": "O2", "duracion_s": 20.0},
    ]
    automatizado = {"X": 40.0}

    resumen = c226.resumen_por_operador(registros, automatizado)

    assert resumen["agregado"]["n"] == 1
    assert resumen["agregado"]["manual_media"] == pytest.approx(60.0)
    assert resumen["agregado"]["reduccion_media"] == pytest.approx(1 - 40 / 60)


def test_resumen_por_operador_con_un_solo_caso_y_un_solo_operador():
    registros = [{"caso_id": "A", "operador": "O1", "duracion_s": 100.0}]

    resumen = c226.resumen_por_operador(registros, {"A": 50.0})

    assert resumen["agregado"]["n"] == 1
    assert resumen["agregado"]["reduccion_media"] == pytest.approx(0.5)
    assert resumen["por_operador"]["O1"]["reduccion_media"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# Efecto de posicion (funcion pura)
# ---------------------------------------------------------------------------
def _resultados_sinteticos():
    return {
        "secciones": {
            "orden": {
                "resultado": {
                    "por_operador": [
                        {
                            "id_etiquetador": "O1",
                            "posicion": {"spearman": {"rho": -0.1, "p": 0.5, "mde": 0.3}},
                        },
                        {
                            "id_etiquetador": "O2",
                            "posicion": {"spearman": {"rho": -0.4, "p": 0.001, "mde": 0.3}},
                        },
                    ]
                }
            }
        }
    }


def test_resumen_posicion_extrae_rho_p_y_mde_por_operador():
    resumen = c226.resumen_posicion(_resultados_sinteticos())

    assert resumen["por_operador"]["O1"]["rho"] == pytest.approx(-0.1)
    assert resumen["por_operador"]["O1"]["p"] == pytest.approx(0.5)
    assert resumen["por_operador"]["O2"]["rho"] == pytest.approx(-0.4)
    assert resumen["por_operador"]["O2"]["significativo"] is True
    assert resumen["por_operador"]["O1"]["significativo"] is False
    assert resumen["mde_rho"] == pytest.approx(0.3)


def test_resumen_posicion_detecta_el_operador_significativo():
    resumen = c226.resumen_posicion(_resultados_sinteticos())

    significativos = [
        op for op, d in resumen["por_operador"].items() if d["significativo"]
    ]
    assert significativos == ["O2"]


# ---------------------------------------------------------------------------
# Cota del instrumento (funcion pura)
# ---------------------------------------------------------------------------
def test_cota_instrumento_cuenta_multiplos_de_cinco_y_diez():
    manual = [10.0, 15.0, 20.0, 25.0, 30.0]

    cota = c226.cota_instrumento(manual)

    assert cota["n"] == 5
    assert cota["multiplos"][5] == 5
    assert cota["multiplos"][10] == 3


def test_cota_instrumento_reconoce_la_telefonia_como_cota_inferior():
    cota = c226.cota_instrumento([7.0])

    assert cota["multiplos"][5] == 0
    assert cota["multiplos"][10] == 0
    assert "45" in cota["nota_telefonia"]
    assert "cota inferior" in cota["nota_telefonia"].lower()


# ---------------------------------------------------------------------------
# Anclajes verificados antes de escribir
# ---------------------------------------------------------------------------
def test_verificar_anclas_acepta_los_valores_canonicos():
    observados = {clave: valor for clave, (valor, _dec) in c226.ANCLAS_ESPERADAS.items()}

    c226.verificar_anclas(observados)


def test_verificar_anclas_rechaza_una_reduccion_global_distinta():
    observados = {clave: valor for clave, (valor, _dec) in c226.ANCLAS_ESPERADAS.items()}
    observados["reduccion_global_10"] = 60.0

    with pytest.raises(c226.AnclaNoReproducida, match="reduccion_global_10"):
        c226.verificar_anclas(observados)


def test_verificar_anclas_rechaza_una_granularidad_distinta():
    observados = {clave: valor for clave, (valor, _dec) in c226.ANCLAS_ESPERADAS.items()}
    observados["granularidad_5"] = 198

    with pytest.raises(c226.AnclaNoReproducida, match="granularidad_5"):
        c226.verificar_anclas(observados)


def test_verificar_anclas_rechaza_una_clave_ausente():
    observados = {clave: valor for clave, (valor, _dec) in c226.ANCLAS_ESPERADAS.items()}
    del observados["reduccion_operador_O1"]

    with pytest.raises(c226.AnclaNoReproducida, match="reduccion_operador_O1"):
        c226.verificar_anclas(observados)


# ---------------------------------------------------------------------------
# Documento real: anclajes, rango primario, canal, operador, posicion
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def documento_real():
    return c226.construir_documento()


def test_construir_documento_reproduce_los_anclajes(documento_real):
    assert documento_real["anclas_verificadas"] == c226.ANCLAS_ESPERADAS


def test_construir_documento_declara_el_rango_primario_y_su_minimo(documento_real):
    rango = documento_real["rango_primario"]

    assert round(rango["escenarios"][0]["reduccion_media"] * 100, 2) == 71.16
    assert round(rango["escenarios"][1]["reduccion_media"] * 100, 2) == 68.61
    assert round(rango["escenario_minimo"]["reduccion_media"] * 100, 2) == 65.57
    assert rango["escenario_minimo"]["descuento_s"] == 10.0
    assert rango["rango"][0] == pytest.approx(rango["escenario_minimo"]["reduccion_media"])
    assert rango["rango"][1] == pytest.approx(rango["escenarios"][0]["reduccion_media"])


def test_construir_documento_reporta_el_canal_minimo_con_rotulo(documento_real):
    canal = documento_real["por_canal"]

    assert round(canal["por_canal"]["llamada telefónica"]["reduccion_media"] * 100, 2) == 76.98
    assert round(canal["por_canal"]["correo electrónico"]["reduccion_media"] * 100, 2) == 51.07
    assert round(canal["por_canal"]["formulario web"]["reduccion_media"] * 100, 2) == 93.44
    assert canal["canal_minimo"] == "correo electrónico"


def test_construir_documento_reporta_las_reducciones_por_operador(documento_real):
    operador = documento_real["por_operador"]

    assert round(operador["por_operador"]["O1"]["reduccion_media"] * 100, 1) == 33.8
    assert round(operador["por_operador"]["O2"]["reduccion_media"] * 100, 1) == 79.7
    assert round(operador["agregado"]["reduccion_media"] * 100, 1) == 69.3
    assert operador["agregado"]["n"] == 200


def test_construir_documento_reporta_el_efecto_de_posicion_real(documento_real):
    posicion = documento_real["efecto_posicion"]

    assert round(posicion["por_operador"]["O1"]["rho"], 4) == -0.0628
    assert round(posicion["por_operador"]["O2"]["rho"], 4) == -0.3604
    assert posicion["por_operador"]["O2"]["significativo"] is True
    assert round(posicion["mde_rho"], 3) == 0.276


def test_construir_documento_reporta_la_granularidad_real(documento_real):
    cota = documento_real["cota_instrumento"]

    assert cota["n"] == 200
    assert cota["multiplos"][5] == 199
    assert cota["multiplos"][10] == 180


def test_construir_documento_aborta_si_un_ancla_no_coincide():
    anclas = dict(c226.ANCLAS_ESPERADAS)
    anclas["reduccion_global_10"] = (60.0, 2)

    with pytest.raises(c226.AnclaNoReproducida, match="reduccion_global_10"):
        c226.construir_documento(anclas_esperadas=anclas)


# ---------------------------------------------------------------------------
# Salidas: aborto sin escribir, declaracion aditiva y determinismo
# ---------------------------------------------------------------------------
def test_ancla_rota_aborta_sin_escribir(tmp_path, monkeypatch):
    def _falla(*_args, **_kwargs):
        raise c226.AnclaNoReproducida("ancla rota")

    monkeypatch.setattr(c226, "verificar_anclas", _falla)

    with pytest.raises(c226.AnclaNoReproducida):
        c226.ejecutar(salida=tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_escribir_declara_sensibilidad_y_conserva_la_cifra_primaria(tmp_path, documento_real):
    c226.escribir(documento_real, tmp_path)
    datos = json.loads((tmp_path / c226.SALIDA_JSON).read_text(encoding="utf-8"))
    texto_md = (tmp_path / c226.SALIDA_MD).read_text(encoding="utf-8")

    assert datos["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert datos["aditivo"]["seccion_memo"] == "3.37"
    assert "71,2" in datos["aditivo"]["declaracion"]
    assert "sensibilidad" in datos["aditivo"]["declaracion"].lower()
    assert "sensibilidad" in texto_md.lower()
    assert "no comparables" in texto_md.lower() or "no comparabilidad" in texto_md.lower()
    for clave in ("rango_primario", "por_canal", "por_operador", "efecto_posicion", "cota_instrumento"):
        assert clave in datos


def test_sha256sums_lista_las_dos_salidas(tmp_path, documento_real):
    c226.escribir(documento_real, tmp_path)
    lineas = (tmp_path / c226.SALIDA_SHA).read_text(encoding="utf-8").splitlines()

    assert len(lineas) == 2
    assert {linea.split("  ", 1)[1] for linea in lineas} == {
        c226.SALIDA_JSON,
        c226.SALIDA_MD,
    }


def test_dos_corridas_producen_bytes_identicos(tmp_path):
    primera = tmp_path / "primera"
    segunda = tmp_path / "segunda"
    primera.mkdir()
    segunda.mkdir()

    c226.ejecutar(salida=primera)
    c226.ejecutar(salida=segunda)

    for nombre in (c226.SALIDA_JSON, c226.SALIDA_MD, c226.SALIDA_SHA):
        assert (primera / nombre).read_bytes() == (segunda / nombre).read_bytes()


def test_main_aborta_con_codigo_uno_si_un_ancla_no_coincide(tmp_path, monkeypatch):
    def _falla(*_args, **_kwargs):
        raise c226.AnclaNoReproducida("ancla rota")

    monkeypatch.setattr(c226, "verificar_anclas", _falla)

    codigo = c226.main(["--salida", str(tmp_path)])

    assert codigo == 1
    assert list(tmp_path.iterdir()) == []


def test_main_escribe_las_tres_salidas(tmp_path):
    codigo = c226.main(["--salida", str(tmp_path)])

    assert codigo == 0
    assert (tmp_path / c226.SALIDA_JSON).exists()
    assert (tmp_path / c226.SALIDA_MD).exists()
    assert (tmp_path / c226.SALIDA_SHA).exists()
