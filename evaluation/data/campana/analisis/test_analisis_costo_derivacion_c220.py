"""Pruebas del analisis del costo de la derivacion erronea (c-220).

TDD estricto de las funciones puras con casos sinteticos (sin I/O ni red) mas
la integracion con los artefactos versionados. Cubre percentiles, bootstrap
determinista, resumen de grupos, diferencia de medias, cobertura de duraciones,
composicion de `c` con propagacion, compuerta de decision D5 y termino de
revision D7.
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_costo_derivacion_c220 as c220  # noqa: E402


# ---------------------------------------------------------------------------
# Percentil e intervalos (funciones puras)
# ---------------------------------------------------------------------------
def test_percentil_intervalo_con_valores_conocidos():
    muestras = [float(k) for k in range(1, 11)]
    bajo, alto = c220.percentil_intervalo(muestras, 0.95)
    assert bajo == pytest.approx(1.225)
    assert alto == pytest.approx(9.775)


def test_percentil_intervalo_degenera_con_un_solo_valor():
    bajo, alto = c220.percentil_intervalo([7.0], 0.95)
    assert (bajo, alto) == (7.0, 7.0)


def test_percentil_intervalo_vacio_devuelve_cero():
    assert c220.percentil_intervalo([], 0.95) == (0.0, 0.0)


# ---------------------------------------------------------------------------
# Bootstrap deterministico
# ---------------------------------------------------------------------------
def test_bootstrap_es_determinista_con_la_misma_semilla():
    valores = [3.0, 8.0, 12.0, 21.0, 6.0]
    primera = c220.bootstrap_estadistico(valores, 40, 20261021)
    segunda = c220.bootstrap_estadistico(valores, 40, 20261021)
    assert primera == segunda


def test_bootstrap_cambia_con_la_semilla():
    valores = [3.0, 8.0, 12.0, 21.0, 6.0]
    primera = c220.bootstrap_estadistico(valores, 40, 20261021)
    segunda = c220.bootstrap_estadistico(valores, 40, 7)
    assert primera != segunda


def test_bootstrap_de_un_grupo_constante_degrada_en_el_valor():
    valores = [5.0] * 10
    assert c220.bootstrap_estadistico(valores, 30, 20261021) == (5.0, 5.0)


# ---------------------------------------------------------------------------
# Resumen de grupo
# ---------------------------------------------------------------------------
def test_resumen_grupo_constante_degrada_en_el_valor():
    resumen = c220.resumen_grupo([4.0] * 12, "constante", remuestreos=30)
    assert resumen["n"] == 12
    assert resumen["media"] == pytest.approx(4.0)
    assert resumen["mediana"] == pytest.approx(4.0)
    assert resumen["desvio"] == pytest.approx(0.0)
    assert resumen["ic_media"] == (pytest.approx(4.0), pytest.approx(4.0))
    assert resumen["ic_mediana"] == (pytest.approx(4.0), pytest.approx(4.0))


def test_resumen_grupo_informa_estadisticos_y_orden():
    resumen = c220.resumen_grupo([1.0, 2.0, 3.0, 4.0], "grupo", remuestreos=50)
    assert resumen["n"] == 4
    assert resumen["media"] == pytest.approx(2.5)
    assert resumen["mediana"] == pytest.approx(2.5)
    assert resumen["desvio"] == pytest.approx(1.118033988749895)
    assert resumen["ic_media"][0] <= resumen["media"] <= resumen["ic_media"][1]
    assert resumen["ic_mediana"][0] <= resumen["mediana"] <= resumen["ic_mediana"][1]


def test_resumen_grupo_vacio_aborta():
    with pytest.raises(ValueError, match="vacio"):
        c220.resumen_grupo([], "vacio")


# ---------------------------------------------------------------------------
# Diferencia de medias
# ---------------------------------------------------------------------------
def test_diferencia_de_medias_constante_es_la_diferencia():
    resultado = c220.diferencia_de_medias([30.0] * 8, [10.0] * 5, remuestreos=30)
    assert resultado["diferencia"] == pytest.approx(20.0)
    assert resultado["ic"] == (pytest.approx(20.0), pytest.approx(20.0))


def test_diferencia_de_medias_es_determinista():
    a = [30.0, 40.0, 25.0, 60.0]
    b = [10.0, 12.0, 8.0, 15.0]
    assert c220.diferencia_de_medias(a, b, remuestreos=40) == c220.diferencia_de_medias(
        a, b, remuestreos=40
    )


# ---------------------------------------------------------------------------
# Cobertura de duraciones (exclusion de faltantes, sin imputacion)
# ---------------------------------------------------------------------------
def _registro(id_caso, duracion, cambio):
    return {
        "id_caso": id_caso,
        "duracion_s": None if duracion is None else float(duracion),
        "cambio_sector": cambio,
    }


def test_cobertura_enumera_los_faltantes_sin_imputar():
    registros = [
        _registro("A", 10.0, False),
        _registro("B", None, True),
        _registro("C", 20.0, True),
    ]
    cobertura = c220.cobertura_duracion(registros)
    assert cobertura["total"] == 3
    assert cobertura["con_duracion"] == 2
    assert cobertura["faltantes"] == ["B"]
    assert cobertura["proporcion"] == pytest.approx(2 / 3)
    # No se imputa: el registro sin duracion sigue sin valor.
    assert registros[1]["duracion_s"] is None


def test_cobertura_sin_faltantes():
    registros = [_registro("A", 10.0, False), _registro("B", 12.0, True)]
    cobertura = c220.cobertura_duracion(registros)
    assert cobertura["faltantes"] == []
    assert cobertura["proporcion"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Composicion de `c` con propagacion (D2, D4)
# ---------------------------------------------------------------------------
def _componente(etiqueta, punto, bajo, alto):
    return {"etiqueta": etiqueta, "punto": punto, "intervalo": (bajo, alto)}


def test_componer_c_bajo_suma_extremos_y_no_incluye_el_ancla():
    correccion = _componente("correccion_compuerta", 24.0, 3.0, 50.0)
    redeccion = _componente("redeccion_proxy", 45.5, 30.0, 56.5)
    ancla = _componente("reanudacion", 120.0, 60.0, 240.0)
    composicion = c220.componer_c([correccion, redeccion], ancla)
    bajo = composicion["escenarios"]["bajo"]
    alto = composicion["escenarios"]["alto"]
    assert bajo["punto"] == pytest.approx(69.5)
    assert bajo["intervalo"] == (pytest.approx(33.0), pytest.approx(106.5))
    assert "reanudacion" not in bajo["componentes"]
    assert alto["disponible"] is True
    assert alto["punto"] == pytest.approx(189.5)
    assert alto["intervalo"] == (pytest.approx(93.0), pytest.approx(346.5))
    assert "reanudacion" in alto["componentes"]


def test_componer_c_sin_ancla_marca_alto_no_disponible():
    correccion = _componente("correccion_compuerta", 24.0, 3.0, 50.0)
    redeccion = _componente("redeccion_proxy", 45.5, 30.0, 56.5)
    composicion = c220.componer_c([correccion, redeccion], None)
    assert composicion["escenarios"]["alto"]["disponible"] is False
    assert "no disponible" in composicion["escenarios"]["alto"]["motivo"]
    assert composicion["escenarios"]["bajo"]["punto"] == pytest.approx(69.5)


def test_componer_c_declara_el_metodo_de_propagacion():
    correccion = _componente("correccion_compuerta", 24.0, 3.0, 50.0)
    composicion = c220.componer_c([correccion], None)
    assert "extremos" in composicion["metodo"]


# ---------------------------------------------------------------------------
# Compuerta de decision D5 contra la banda canonica
# ---------------------------------------------------------------------------
def test_comparar_banda_que_intersecta_es_rama_a():
    comparacion = c220.comparar_banda((500.0, 700.0), (600.0, 900.0))
    assert comparacion["relacion"] == "intersecta"
    assert comparacion["rama"] == "A"


def test_comparar_banda_que_excluye_es_rama_b():
    comparacion = c220.comparar_banda((33.0, 106.0), (600.0, 900.0))
    assert comparacion["relacion"] == "excluida"
    assert comparacion["rama"] == "B"


def test_comparar_banda_contenida_es_rama_a():
    comparacion = c220.comparar_banda((650.0, 850.0), (600.0, 900.0))
    assert comparacion["relacion"] == "contenida"
    assert comparacion["rama"] == "A"


def test_comparar_banda_por_encima_es_rama_b():
    comparacion = c220.comparar_banda((950.0, 1100.0), (600.0, 900.0))
    assert comparacion["relacion"] == "excluida"
    assert comparacion["rama"] == "B"


# ---------------------------------------------------------------------------
# Termino de revision y efectos derivados (D6, D7)
# ---------------------------------------------------------------------------
def test_termino_revision_informa_estadisticos():
    termino = c220.termino_revision([10.0, 20.0, 30.0, 40.0], remuestreos=40)
    assert termino["n"] == 4
    assert termino["media"] == pytest.approx(25.0)
    assert termino["mediana"] == pytest.approx(25.0)


def test_horas_revision_por_trimestre_aplica_la_formula():
    horas = c220.horas_revision_por_trimestre(22.06, n_universo=2646)
    assert horas == pytest.approx(2646 * 22.06 / 3600)


def test_costo_marginal_por_punto_aplica_la_formula():
    horas = c220.costo_marginal_por_punto(69.5, n_universo=2646)
    assert horas == pytest.approx(2646 * 0.01 * 69.5 / 3600)


def test_paridad_manual_es_el_complemento_de_la_tasa():
    assert c220.paridad_manual(26 / 151) == pytest.approx(1 - 26 / 151)


# ---------------------------------------------------------------------------
# Integracion con los artefactos versionados
# ---------------------------------------------------------------------------
def test_cargar_intervenciones_cuenta_duraciones_y_grupos():
    registros = c220.cargar_intervenciones()
    cobertura = c220.cobertura_duracion(registros)
    assert cobertura["total"] == 147
    assert cobertura["con_duracion"] == 138
    assert len(cobertura["faltantes"]) == 9
    assert "R166" in cobertura["faltantes"]
    assert sum(1 for r in registros if r["cambio_sector"]) == 25
    assert sum(1 for r in registros if not r["cambio_sector"]) == 122


def test_cargar_brazo_manual_cuenta_decisiones_y_operadores():
    registros = c220.cargar_brazo_manual()
    assert len(registros) == 220
    operadores = [r["operador"] for r in registros]
    assert operadores.count("O1") == 110
    assert operadores.count("O2") == 110


def test_resumenes_reales_reproducen_los_valores_del_diseno():
    registros = c220.cargar_intervenciones()
    con_duracion = [r for r in registros if r["duracion_s"] is not None]
    grupo_si = [r["duracion_s"] for r in con_duracion if r["cambio_sector"]]
    grupo_no = [r["duracion_s"] for r in con_duracion if not r["cambio_sector"]]
    resumen_si = c220.resumen_grupo(grupo_si, "cambio_sector_true")
    resumen_no = c220.resumen_grupo(grupo_no, "cambio_sector_false")
    assert resumen_si["n"] == 24
    assert resumen_si["media"] == pytest.approx(41.8954, abs=1e-3)
    assert resumen_si["mediana"] == pytest.approx(18.945, abs=1e-3)
    assert resumen_no["n"] == 114
    assert resumen_no["media"] == pytest.approx(17.888, abs=1e-3)
    assert resumen_no["mediana"] == pytest.approx(8.9425, abs=1e-3)


def test_documento_real_determina_rama_b_y_excluye_la_banda():
    doc = c220.construir_documento(remuestreos=200, semilla=20261021)
    assert doc["brazo_manual"]["n"] == 220
    assert doc["brazo_manual"]["mediana"] == pytest.approx(45.5)
    assert doc["brazo_manual"]["por_operador"]["O1"]["mediana"] == pytest.approx(18.0)
    assert doc["brazo_manual"]["por_operador"]["O2"]["mediana"] == pytest.approx(73.0)
    comparacion = doc["compuerta_d5"]
    assert comparacion["rama"] == "B"
    assert comparacion["intervalo"][1] < c220.BANDA_CANONICA[0]
    assert doc["composicion"]["escenarios"]["alto"]["disponible"] is False


def test_documento_real_no_modifica_el_balance_canonico():
    doc = c220.construir_documento(remuestreos=100, semilla=20261021)
    # El termino de revision es una sensibilidad aditiva separada.
    assert doc["termino_revision"]["n"] == 138
    assert doc["termino_revision"]["media"] == pytest.approx(22.0632, abs=1e-3)
    assert doc["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert "B_canonico_no_modificado" in doc["termino_revision"]


def test_renderizar_es_determinista():
    doc = c220.construir_documento(remuestreos=60, semilla=20261021)
    assert c220.renderizar(doc) == c220.renderizar(doc)


def test_ejecutar_escribe_json_md_y_sumas_byte_a_byte(tmp_path):
    rutas = c220.ejecutar(salida=tmp_path, remuestreos=50, semilla=20261021)
    nombres = sorted(r.name for r in rutas)
    assert nombres == sorted(
        [
            "analisis_costo_derivacion_c220.json",
            "analisis_costo_derivacion_c220.md",
            "analisis_costo_derivacion_c220.SHA256SUMS.txt",
        ]
    )
    primera_json = (tmp_path / "analisis_costo_derivacion_c220.json").read_bytes()
    primera_md = (tmp_path / "analisis_costo_derivacion_c220.md").read_bytes()
    c220.ejecutar(salida=tmp_path, remuestreos=50, semilla=20261021)
    assert (tmp_path / "analisis_costo_derivacion_c220.json").read_bytes() == primera_json
    assert (tmp_path / "analisis_costo_derivacion_c220.md").read_bytes() == primera_md
