"""Pruebas del recomputo offline del balance neto con el costo medido (c-222).

TDD estricto de las funciones puras con casos sinteticos (sin I/O ni red) mas la
integracion con los artefactos versionados. Cubre el balance neto, la exactitud minima
de equilibrio, el emparejamiento de la referencia comun, el bootstrap condicional con
`c` fijo, la cota por suma de extremos, el signo, los anclajes que abortan antes de
escribir y la escritura determinista byte a byte.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_balance_neto_c222 as c222  # noqa: E402


# ---------------------------------------------------------------------------
# Balance neto (funcion pura)
# ---------------------------------------------------------------------------
def test_balance_neto_es_positivo_cuando_el_ahorro_supera_el_costo():
    assert c222.balance_neto(2646, 43.82, 0.2028985507246377, 0.17218543046357615, 69.51) > 0


def test_balance_neto_es_negativo_cuando_el_costo_supera_el_ahorro():
    assert c222.balance_neto(2646, 43.82, 0.5, 0.1, 900.0) < 0


def test_balance_neto_aplica_la_formula_exacta():
    esperado = (2646 / 3600.0) * (43.82 - (0.30 - 0.172) * 600.0)
    assert c222.balance_neto(2646, 43.82, 0.30, 0.172, 600.0) == pytest.approx(esperado)


def test_balance_neto_es_nulo_si_la_diferencia_es_cero():
    assert c222.balance_neto(2646, 43.82, 0.25, 0.25, 900.0) == pytest.approx((2646 / 3600.0) * 43.82)


# ---------------------------------------------------------------------------
# Exactitud minima de equilibrio (funcion pura)
# ---------------------------------------------------------------------------
def test_exactitud_equilibrio_aplica_la_formula_exacta():
    esperado = 1.0 - 0.17218543046357615 - 43.82 / 69.51
    assert c222.exactitud_equilibrio(0.17218543046357615, 43.82, 69.51) == pytest.approx(esperado)


def test_exactitud_equilibrio_crece_con_el_costo():
    bajo = c222.exactitud_equilibrio(0.17218543046357615, 43.82, 300.0)
    alto = c222.exactitud_equilibrio(0.17218543046357615, 43.82, 900.0)
    assert alto > bajo


def test_exactitud_equilibrio_no_depende_de_e_aut_ni_de_n():
    # La firma solo admite `e_man`, `delta_t` y `c_s`; el valor es reproducible.
    a1 = c222.exactitud_equilibrio(0.20, 43.82, 600.0)
    a2 = c222.exactitud_equilibrio(0.20, 43.82, 600.0)
    assert a1 == pytest.approx(a2)


def test_exactitud_equilibrio_puede_ser_negativa_con_costo_muy_bajo():
    # Con un costo de 10 s, `dt / c` domina y la exactitud de equilibrio es negativa.
    assert c222.exactitud_equilibrio(0.20, 43.82, 10.0) < 0


# ---------------------------------------------------------------------------
# Emparejamiento de la referencia comun (funcion pura)
# ---------------------------------------------------------------------------
def _fila(caso: str, sector: str, tarea: str = "brazo_manual", etiquetador: str = "O1") -> dict:
    return {
        "id_caso": caso,
        "id_etiquetador": etiquetador,
        "tarea": tarea,
        "sector_etiquetado": sector,
        "sectores_adicionales_etiquetados": "",
    }


def test_emparejar_referencia_manual_cuenta_errores_por_caso():
    referencia = {"A": "Sistemas", "B": "Bases de Datos"}
    filas = [
        _fila("A", "Sistemas"),
        _fila("A", "Sistemas", etiquetador="O2"),
        _fila("B", "Sistemas"),
    ]
    predichos = {"A": "Sistemas", "B": "Sistemas"}
    casos = c222.emparejar_referencia_manual(referencia, filas, predichos)
    assert casos == [(0, 0, 2), (1, 1, 1)]


def test_emparejar_referencia_manual_ignora_casos_fuera_de_la_referencia():
    referencia = {"A": "Sistemas"}
    filas = [_fila("A", "Sistemas"), _fila("Z", "Bases de Datos")]
    predichos = {"A": "Sistemas", "Z": "Bases de Datos"}
    casos = c222.emparejar_referencia_manual(referencia, filas, predichos)
    assert casos == [(0, 0, 1)]


def test_emparejar_referencia_manual_aborta_si_un_caso_no_tiene_derivaciones():
    referencia = {"A": "Sistemas", "B": "Bases de Datos"}
    filas = [_fila("A", "Sistemas")]
    with pytest.raises(c222.EntradaInconsistente, match="derivaciones"):
        c222.emparejar_referencia_manual(referencia, filas, {"A": "Sistemas", "B": "Sistemas"})


def test_emparejar_referencia_manual_ordena_por_id_de_caso():
    referencia = {"C": "Sistemas", "A": "Sistemas", "B": "Sistemas"}
    filas = [_fila("C", "Sistemas"), _fila("A", "Sistemas"), _fila("B", "Sistemas")]
    predichos = {"A": "Sistemas", "B": "Sistemas", "C": "Bases de Datos"}
    casos = c222.emparejar_referencia_manual(referencia, filas, predichos)
    assert casos == [(0, 0, 1), (0, 0, 1), (1, 0, 1)]


# ---------------------------------------------------------------------------
# Bootstrap condicional con `c` fijo (funcion pura)
# ---------------------------------------------------------------------------
def _casos_sinteticos() -> list[tuple[int, int, int]]:
    return [
        (0, 0, 1),
        (1, 0, 1),
        (0, 0, 2),
        (1, 1, 1),
        (0, 0, 1),
        (1, 1, 2),
        (0, 1, 1),
        (1, 0, 1),
    ]


def test_bootstrap_casos_es_determinista_con_la_misma_semilla():
    casos = _casos_sinteticos()
    primera = c222.bootstrap_casos(casos, remuestreos=40, semilla=20261021)
    segunda = c222.bootstrap_casos(casos, remuestreos=40, semilla=20261021)
    assert primera == segunda


def test_bootstrap_casos_aborta_sin_casos():
    with pytest.raises(ValueError):
        c222.bootstrap_casos([], remuestreos=10, semilla=20261021)


def test_bootstrap_casos_cada_remuestra_tiene_el_tamano_de_la_muestra():
    casos = _casos_sinteticos()
    rem = c222.bootstrap_casos(casos, remuestreos=5, semilla=20261021)
    assert len(rem) == 5
    # e_aut y e_man son proporciones dentro de [0, 1].
    assert all(0.0 <= a <= 1.0 and 0.0 <= m <= 1.0 for a, m in rem)


def test_intervalos_condicionales_informa_punto_e_ic_por_costo():
    casos = _casos_sinteticos()
    salida = c222.intervalos_condicionales(
        casos, 2646, 43.82, (300.0, 600.0), remuestreos=200, semilla=20261021
    )
    assert [d["c_s"] for d in salida["por_costo"]] == [300.0, 600.0]
    for dato in salida["por_costo"]:
        assert dato["balance_ic"][0] <= dato["balance"] <= dato["balance_ic"][1]
        assert 0.0 <= dato["a_estrella_ic"][0] <= dato["a_estrella_ic"][1] <= 1.0


def test_intervalos_condicionales_el_signo_se_fija_con_la_muestra_sintetica():
    casos = _casos_sinteticos()
    salida = c222.intervalos_condicionales(
        casos, 2646, 43.82, (300.0,), remuestreos=400, semilla=20261021
    )
    assert salida["por_costo"][0]["signo_fijado"] in {"positivo", "negativo", "no fijado"}


def test_intervalos_condicionales_aborta_con_un_caso_sin_derivaciones():
    with pytest.raises(ValueError, match="derivacion"):
        c222.intervalos_condicionales([(0, 0, 0)], 2646, 43.82, (300.0), remuestreos=5, semilla=1)


def test_ic_bootstrap_condicional_conveniencia_de_un_solo_costo():
    casos = _casos_sinteticos()
    unico = c222.ic_bootstrap_condicional(casos, 2646, 43.82, 300.0, remuestreos=100, semilla=20261021)
    lote = c222.intervalos_condicionales(casos, 2646, 43.82, (300.0,), remuestreos=100, semilla=20261021)
    assert unico == lote["por_costo"][0]


# ---------------------------------------------------------------------------
# Cota por suma de extremos (funcion pura)
# ---------------------------------------------------------------------------
def test_suma_de_extremos_devuelve_minimo_y_maximo():
    assert c222.suma_de_extremos([3.0, 1.0, 5.0, 2.0]) == (1.0, 5.0)


def test_intervalo_combinado_evalua_las_cuatro_esquinas():
    # termino y c positivos: el maximo es (termino_min, c_min) y el minimo (termino_max, c_max).
    salida = c222.intervalo_combinado(2646, 43.82, (0.0, 0.10), (300.0, 900.0))
    esquinas = [
        c222.balance_neto(2646, 43.82, termino, 0.0, c_s)
        for c_s in (300.0, 900.0)
        for termino in (0.0, 0.10)
    ]
    assert salida == (min(esquinas), max(esquinas))


def test_intervalo_combinado_con_diferencia_cero_solo_refleja_el_costo():
    salida = c222.intervalo_combinado(2646, 43.82, (0.0, 0.0), (300.0, 900.0))
    assert salida == (c222.balance_neto(2646, 43.82, 0.0, 0.0, 900.0),
                      c222.balance_neto(2646, 43.82, 0.0, 0.0, 300.0))


def test_intervalo_combinado_devuelve_un_par_ordenado():
    bajo, alto = c222.intervalo_combinado(2646, 43.82, (-0.05, 0.11), (33.42, 106.56))
    assert bajo <= alto


def test_signo_fijado_detecta_los_tres_casos():
    assert c222.signo_fijado(1.0, 5.0) == "positivo"
    assert c222.signo_fijado(-5.0, -1.0) == "negativo"
    assert c222.signo_fijado(-1.0, 5.0) == "no fijado"


# ---------------------------------------------------------------------------
# Integracion con los artefactos versionados
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def doc():
    # El bootstrap condicional debe reproducir los anclajes: usa la semilla y B reales.
    return c222.construir_documento()


def test_conteos_de_la_referencia_comun(doc):
    insumos = doc["insumos"]
    assert insumos["casos"] == 138
    assert insumos["errores_automatizado"] == 28
    assert insumos["errores_manual"] == 26
    assert insumos["derivaciones_manual"] == 151
    assert insumos["e_aut"] == pytest.approx(28 / 138)
    assert insumos["e_man"] == pytest.approx(26 / 151)


def test_anclajes_reales_se_reproducen(doc):
    ancla = doc["anclajes"]
    assert ancla["c_s_redondeado"] == pytest.approx(69.51)
    assert ancla["referencia_comun_redondeada"] == [25.4, 18.7, 11.9]
    assert ancla["referencia_comun_ic_redondeada"] == [
        [8.6, 42.4],
        [-15.0, 52.5],
        [-38.6, 62.7],
    ]


def test_escenario_central_con_el_costo_medido(doc):
    cond = doc["condicional_c_fijo"]
    assert cond["balance"] == pytest.approx(30.6386, abs=5e-3)
    assert cond["a_estrella"] == pytest.approx(0.1974, abs=5e-4)
    assert cond["balance_ic"][0] < cond["balance"] < cond["balance_ic"][1]


def test_intervalo_combinado_por_suma_de_extremos(doc):
    combinado = doc["combinado"]
    assert combinado["metodo"].startswith("suma de extremos")
    assert combinado["balance_ic"] == pytest.approx([23.83, 35.81], abs=5e-2)
    assert combinado["signo_fijado"] == "positivo"


def test_grilla_superada_conserva_sus_cifras(doc):
    grilla = doc["grilla_superada"]
    assert [fila["c_min"] for fila in grilla] == [5, 10, 15]
    assert [round(fila["balance"], 1) for fila in grilla] == [25.4, 18.7, 11.9]
    assert [round(fila["a_estrella"] * 100, 1) for fila in grilla] == [68.2, 75.5, 77.9]
    assert all(fila["estado"] == "condicional" for fila in grilla)
    assert all("superad" in fila["rotulo"] for fila in grilla)


def test_sensibilidad_mixta_de_c221_no_se_promueve(doc):
    mixta = doc["sensibilidad_mixta_c221"]
    assert mixta["promovida"] is False
    assert round(mixta["ponderada_c_medido"], 1) == 28.2
    assert round(mixta["cruda_c_medido"], 1) == 25.1


def test_entradas_sha256_incluye_los_artefactos_y_las_fuentes(doc):
    entradas = doc["entradas_sha256"]
    for nombre in (
        "analisis_costo_derivacion_c220.json",
        "analisis_dictamen_c207.json",
        "analisis_propagacion_arbitraje_c221.json",
        "plantilla_etiquetado.csv",
        "predicciones_in_sample.json",
    ):
        assert nombre in entradas
        assert len(entradas[nombre]) == 64


def test_trazabilidad_remite_a_las_claves(doc):
    assert doc["trazabilidad"]["balance_central"] == "condicional_c_fijo.balance"
    assert doc["trazabilidad"]["intervalo_combinado"] == "combinado.balance_ic"


def test_renderizar_es_determinista(doc):
    assert c222.renderizar(doc) == c222.renderizar(doc)


def test_ejecutar_escribe_json_md_y_sumas_byte_a_byte(tmp_path):
    rutas = c222.ejecutar(salida=tmp_path)
    nombres = sorted(r.name for r in rutas)
    assert nombres == sorted(
        [
            "analisis_balance_neto_c222.json",
            "analisis_balance_neto_c222.md",
            "analisis_balance_neto_c222.SHA256SUMS.txt",
        ]
    )
    primera = {n: (tmp_path / n).read_bytes() for n in nombres}
    for n in nombres:
        assert b"\r" not in primera[n]
        assert not primera[n].startswith(b"\xef\xbb\xbf")
    c222.ejecutar(salida=tmp_path)
    for n in nombres:
        assert (tmp_path / n).read_bytes() == primera[n]


def test_anclaje_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c222, "ANCLA_BALANCE_REFERENCIA_COMUN", (9.9, 9.9, 9.9))
    with pytest.raises(c222.AnclaNoReproducida):
        c222.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_costos_inconsistentes_abortan_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c222, "ANCLA_C_S", 999.0)
    with pytest.raises(c222.AnclaNoReproducida):
        c222.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_sumas_sha256_listan_las_dos_salidas(tmp_path):
    rutas = c222.ejecutar(salida=tmp_path)
    sumas = (tmp_path / "analisis_balance_neto_c222.SHA256SUMS.txt").read_text(encoding="utf-8")
    for ruta in rutas:
        if ruta.name.endswith(".SHA256SUMS.txt"):
            continue
        assert ruta.name in sumas
        assert c222.sha256(ruta, normalizar_lf=False) in sumas
