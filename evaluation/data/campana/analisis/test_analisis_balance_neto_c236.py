"""Pruebas del recomputo offline del balance neto acotado con el termino de revision (c-236).

TDD estricto de las funciones puras con casos sinteticos (sin I/O ni red) mas la
integracion con los artefactos versionados. Cubre el balance neto con el termino de
revision, la exactitud minima de equilibrio con revision, el costo de equilibrio y su
margen, la cota combinada por suma de extremos sobre 16 esquinas, el bootstrap
condicional con remuestreo independiente (diferencia por caso y `r` por duracion), los
anclajes que abortan antes de escribir, el contenido del documento (cota superior, sin
signo declarado fijado, sin cifras fuera de muestra) y la escritura determinista byte a
byte.

El metodo y la regla se fijan en el docstring del modulo ANTES de generar sus salidas.
El preregistro NO es ciego: el valor central ya lo publico el tribunal.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_balance_neto_c236 as c236  # noqa: E402


# ---------------------------------------------------------------------------
# Balance neto con revision (funcion pura)
# ---------------------------------------------------------------------------
def test_balance_con_revision_sin_revision_reproduce_la_formula_de_c222():
    # Con rho * r = 0 el termino de revision desaparece y la formula coincide con c-222.
    esperado = (2646 / 3600.0) * (43.82 - (0.2028985507246377 - 0.17218543046357615) * 69.51)
    obtenido = c236.balance_neto_con_revision(
        2646, 43.82, 0.0, 0.0, 0.2028985507246377, 0.17218543046357615, 69.51
    )
    assert obtenido == pytest.approx(esperado)


def test_balance_con_revision_baja_exactamente_el_efecto_de_la_revision():
    base = c236.balance_neto_con_revision(
        2646, 43.82, 0.0, 0.0, 0.2028985507246377, 0.17218543046357615, 69.51
    )
    con_revision = c236.balance_neto_con_revision(
        2646, 43.82, 0.735, 22.063166666666667, 0.2028985507246377, 0.17218543046357615, 69.51
    )
    efecto = 2646 * 0.735 * 22.063166666666667 / 3600.0
    assert base - con_revision == pytest.approx(efecto)


def test_balance_con_revision_es_positivo_con_los_insumos_versionados():
    assert c236.balance_neto_con_revision(
        2646, 43.82, 0.735, 22.063166666666667, 0.2028985507246377, 0.17218543046357615, 69.51
    ) > 0


def test_balance_con_revision_decae_con_el_costo():
    bajo = c236.balance_neto_con_revision(2646, 43.82, 0.735, 22.06, 0.203, 0.172, 300.0)
    alto = c236.balance_neto_con_revision(2646, 43.82, 0.735, 22.06, 0.203, 0.172, 900.0)
    assert alto < bajo


def test_balance_con_revision_es_nulo_si_todo_se_compensa():
    # dt - rho*r - (e_aut - e_man)*c = 0 => B = 0.
    c_s = 43.82 / 0.05  # con rho*r = 0
    assert c236.balance_neto_con_revision(
        2646, 43.82, 0.0, 0.0, 0.05, 0.0, c_s
    ) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Exactitud minima de equilibrio con revision (funcion pura)
# ---------------------------------------------------------------------------
def test_exactitud_con_revision_sin_revision_reproduce_la_formula_de_c222():
    esperado = 1.0 - 0.17218543046357615 - 43.82 / 69.51
    obtenido = c236.exactitud_equilibrio_con_revision(
        0.17218543046357615, 43.82, 0.0, 0.0, 69.51
    )
    assert obtenido == pytest.approx(esperado)


def test_exactitud_con_revision_es_mayor_que_sin_revision():
    sin_revision = c236.exactitud_equilibrio_con_revision(0.172, 43.82, 0.0, 0.0, 69.51)
    con_revision = c236.exactitud_equilibrio_con_revision(0.172, 43.82, 0.735, 22.06, 69.51)
    assert con_revision > sin_revision


def test_exactitud_con_revision_crece_con_el_costo():
    bajo = c236.exactitud_equilibrio_con_revision(0.172, 43.82, 0.735, 22.06, 300.0)
    alto = c236.exactitud_equilibrio_con_revision(0.172, 43.82, 0.735, 22.06, 900.0)
    assert alto > bajo


def test_exactitud_con_revision_no_depende_de_n():
    # La firma no admite `n`: el valor depende solo de e_man, dt, rho, r y c.
    a1 = c236.exactitud_equilibrio_con_revision(0.20, 43.82, 0.735, 22.06, 600.0)
    a2 = c236.exactitud_equilibrio_con_revision(0.20, 43.82, 0.735, 22.06, 600.0)
    assert a1 == pytest.approx(a2)


# ---------------------------------------------------------------------------
# Costo de equilibrio y margen del tramo no medido (funcion pura)
# ---------------------------------------------------------------------------
def test_costo_equilibrio_aplica_la_formula():
    # c* = (dt - rho*r) / (e_aut - e_man).
    c_star = c236.costo_equilibrio(43.82, 0.735, 22.06, 0.05)
    assert c_star == pytest.approx((43.82 - 0.735 * 22.06) / 0.05)


def test_costo_equilibrio_sin_diferencia_no_tiene_solucion_finita():
    assert c236.costo_equilibrio(43.82, 0.735, 22.06, 0.0) is None
    assert c236.costo_equilibrio(43.82, 0.735, 22.06, -0.05) is None


def test_margen_tramo_no_medido_es_c_star_menos_el_costo_medido():
    margen = c236.margen_tramo_no_medido(43.82, 0.735, 22.06, 0.05, 69.51)
    assert margen == pytest.approx((43.82 - 0.735 * 22.06) / 0.05 - 69.51)


def test_margen_tramo_no_medido_sin_diferencia_es_none():
    assert c236.margen_tramo_no_medido(43.82, 0.735, 22.06, 0.0, 69.51) is None


# ---------------------------------------------------------------------------
# Cota combinada por suma de extremos (funcion pura)
# ---------------------------------------------------------------------------
def test_suma_de_extremos_devuelve_minimo_y_maximo():
    assert c236.suma_de_extremos([3.0, 1.0, 5.0, 2.0]) == (1.0, 5.0)


def test_suma_de_extremos_aborta_sin_valores():
    with pytest.raises(ValueError):
        c236.suma_de_extremos([])


def test_cota_combinada_evalua_las_16_esquinas():
    rho_ic = (0.6698, 0.7913)
    r_ic = (15.49, 29.39)
    dif_ic = (-0.0460, 0.1070)
    c_ic = (33.42, 106.56)
    esquinas = [
        c236.balance_neto_con_revision(2646, 43.82, rho, r, dif, 0.0, c_s)
        for rho in rho_ic
        for r in r_ic
        for dif in dif_ic
        for c_s in c_ic
    ]
    assert len(esquinas) == 16
    assert c236.cota_combinada(2646, 43.82, rho_ic, r_ic, dif_ic, c_ic) == (
        min(esquinas),
        max(esquinas),
    )


def test_cota_combinada_devuelve_un_par_ordenado():
    bajo, alto = c236.cota_combinada(
        2646, 43.82, (0.6698, 0.7913), (15.49, 29.39), (-0.046, 0.107), (33.42, 106.56)
    )
    assert bajo <= alto


# ---------------------------------------------------------------------------
# Bootstrap condicional con remuestreo independiente (funcion pura)
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


def _duraciones_sinteticas() -> list[float]:
    return [10.0, 20.0, 30.0, 5.0, 15.0, 25.0, 40.0, 12.5]


def test_bootstrap_con_revision_es_determinista_con_la_misma_semilla():
    salida1 = c236.intervalos_condicionales_con_revision(
        _casos_sinteticos(), _duraciones_sinteticas(), 2646, 43.82, 0.735, (300.0,),
        remuestreos=40, semilla=20261021,
    )
    salida2 = c236.intervalos_condicionales_con_revision(
        _casos_sinteticos(), _duraciones_sinteticas(), 2646, 43.82, 0.735, (300.0,),
        remuestreos=40, semilla=20261021,
    )
    assert salida1 == salida2


def test_bootstrap_con_revision_aborta_sin_casos_o_sin_duraciones():
    with pytest.raises(ValueError):
        c236.intervalos_condicionales_con_revision(
            [], _duraciones_sinteticas(), 2646, 43.82, 0.735, (300.0,), remuestreos=5, semilla=1
        )
    with pytest.raises(ValueError):
        c236.intervalos_condicionales_con_revision(
            _casos_sinteticos(), [], 2646, 43.82, 0.735, (300.0,), remuestreos=5, semilla=1
        )


def test_bootstrap_con_revision_informa_punto_e_ic_por_costo():
    salida = c236.intervalos_condicionales_con_revision(
        _casos_sinteticos(), _duraciones_sinteticas(), 2646, 43.82, 0.735, (300.0, 600.0),
        remuestreos=200, semilla=20261021,
    )
    assert [d["c_s"] for d in salida["por_costo"]] == [300.0, 600.0]
    for dato in salida["por_costo"]:
        assert dato["balance_ic"][0] <= dato["balance"] <= dato["balance_ic"][1]
        assert 0.0 <= dato["a_estrella_ic"][0] <= dato["a_estrella_ic"][1] <= 1.0


def test_bootstrap_con_revision_remuestrea_r_por_duracion():
    # Cambiar una sola duracion mueve el IC: `r` se remuestrea de las duraciones.
    base = c236.intervalos_condicionales_con_revision(
        _casos_sinteticos(), _duraciones_sinteticas(), 2646, 43.82, 0.735, (300.0,),
        remuestreos=100, semilla=20261021,
    )
    otras = _duraciones_sinteticas()
    otras[0] = 5000.0
    cambiado = c236.intervalos_condicionales_con_revision(
        _casos_sinteticos(), otras, 2646, 43.82, 0.735, (300.0,),
        remuestreos=100, semilla=20261021,
    )
    assert base["por_costo"][0]["balance"] != cambiado["por_costo"][0]["balance"]


# ---------------------------------------------------------------------------
# Iteracion de los artefactos versionados
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def doc():
    return c236.construir_documento()


def test_anclajes_del_artefacto_se_reproducen(doc):
    ancla = doc["anclajes"]
    assert ancla["balance_sin_revision_redondeado"] == pytest.approx(30.64)
    assert ancla["c_s_redondeado"] == pytest.approx(69.51)
    assert ancla["r_media_redondeada"] == pytest.approx(22.06)
    assert ancla["n_duraciones"] == 138
    assert ancla["rho"] == pytest.approx(147 / 200)


def test_insumos_provienen_de_los_artefactos(doc):
    insumos = doc["insumos"]
    assert insumos["n"] == 2646
    assert insumos["delta_t_s"] == pytest.approx(43.82)
    assert insumos["e_aut"] == pytest.approx(28 / 138)
    assert insumos["e_man"] == pytest.approx(26 / 151)
    assert insumos["c_s"] == pytest.approx(69.50741008771931)


def test_lectura_central_con_revision(doc):
    lectura = doc["lectura_central"]
    assert lectura["balance"] == pytest.approx(18.7196, abs=5e-3)
    assert lectura["a_estrella"] == pytest.approx(0.4307, abs=5e-4)
    assert lectura["balance_ic"][0] < lectura["balance"] < lectura["balance_ic"][1]


def test_lectura_central_se_rotula_cota_superior(doc):
    lectura = doc["lectura_central"]
    assert "cota superior" in lectura["rotulo"].lower()
    assert "cota superior" in doc["metodo"].lower() or "cota superior" in lectura["rotulo"].lower()


def test_cota_combinada_sobre_16_esquinas(doc):
    cota = doc["lectura_central"]["cota_combinada"]
    assert cota == pytest.approx([6.73, 28.19], abs=5e-2)
    assert "tramo activo" in doc["lectura_central"]["cota_combinada_rotulo"].lower()


def test_costo_de_equilibrio_y_margen(doc):
    costo = doc["costo_equilibrio"]
    assert costo["c_s"] == pytest.approx(898.8, abs=5e-1)
    assert costo["margen_s"] == pytest.approx(829.2, abs=5e-1)
    assert costo["c_s_con_diferencia_alta"] == pytest.approx(258.0, abs=5e-1)


def test_rejilla_con_revision_rotulada_como_sensibilidad_al_tramo_no_medido(doc):
    rejilla = doc["sensibilidad_al_tramo_no_medido"]
    assert [fila["c_min"] for fila in rejilla] == [5, 10, 15]
    assert [round(fila["balance"], 2) for fila in rejilla] == [13.52, 6.74, -0.03]
    assert [round(fila["a_estrella"] * 100, 2) for fila in rejilla] == [73.58, 78.18, 79.71]
    assert all(fila["estado"] == "condicional" for fila in rejilla)
    assert all("tramo no medido" in fila["rotulo"].lower() for fila in rejilla)


def test_sensibilidades_de_r_y_de_rho(doc):
    sens = doc["sensibilidades"]
    assert sens["r_mediana"]["balance"] == pytest.approx(25.26, abs=5e-2)
    assert sens["r_sin_solapamiento"]["balance"] == pytest.approx(20.98, abs=5e-2)
    assert sens["rho_uno"]["balance"] == pytest.approx(14.42, abs=5e-2)


def test_el_documento_no_declara_el_signo_del_balance_real_como_fijado(doc):
    texto = json.dumps(doc, ensure_ascii=False)
    assert "signo_fijado" not in texto
    assert "fijado por la muestra" not in texto.lower()
    assert "viabilidad" not in texto.lower()


def test_el_documento_no_incluye_cifras_fuera_de_muestra(doc):
    texto = json.dumps(doc, ensure_ascii=False).lower()
    assert "fuera de muestra" not in texto
    assert "fuera_de_muestra" not in texto
    assert "0.7489" not in texto
    assert "64/206" not in texto
    assert "sensibilidad_mixta" not in texto


def test_el_preregistro_es_no_ciego_y_fijado_en_el_docstring(doc):
    prereg = doc["preregistro"]
    assert prereg["fijado_en_docstring"] is True
    assert prereg["ciego"] is False


def test_entradas_sha256_incluye_los_artefactos_y_las_fuentes(doc):
    entradas = doc["entradas_sha256"]
    for nombre in (
        "analisis_costo_derivacion_c220.json",
        "analisis_balance_neto_c222.json",
        "intervenciones.csv",
        "plantilla_etiquetado.csv",
        "predicciones_in_sample.json",
    ):
        assert nombre in entradas
        assert len(entradas[nombre]) == 64


def test_renderizar_es_determinista(doc):
    assert c236.renderizar(doc) == c236.renderizar(doc)


def test_ejecutar_escribe_json_md_y_sumas_byte_a_byte(tmp_path):
    rutas = c236.ejecutar(salida=tmp_path)
    nombres = sorted(r.name for r in rutas)
    assert nombres == sorted(
        [
            "analisis_balance_neto_c236.json",
            "analisis_balance_neto_c236.md",
            "analisis_balance_neto_c236.SHA256SUMS.txt",
        ]
    )
    primera = {n: (tmp_path / n).read_bytes() for n in nombres}
    for n in nombres:
        assert b"\r" not in primera[n]
        assert not primera[n].startswith(b"\xef\xbb\xbf")
    c236.ejecutar(salida=tmp_path)
    for n in nombres:
        assert (tmp_path / n).read_bytes() == primera[n]


def test_sumas_sha256_listan_las_dos_salidas(tmp_path):
    rutas = c236.ejecutar(salida=tmp_path)
    sumas = (tmp_path / "analisis_balance_neto_c236.SHA256SUMS.txt").read_text(encoding="utf-8")
    for ruta in rutas:
        if ruta.name.endswith(".SHA256SUMS.txt"):
            continue
        assert ruta.name in sumas
        assert c236.sha256(ruta, normalizar_lf=False) in sumas


# ---------------------------------------------------------------------------
# Anclajes que abortan antes de escribir (RED -> GREEN)
# ---------------------------------------------------------------------------
def test_anclaje_de_balance_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c236, "ANCLA_BALANCE_C222", 9.99)
    with pytest.raises(c236.AnclaNoReproducida):
        c236.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_anclaje_de_costo_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c236, "ANCLA_C_S", 999.0)
    with pytest.raises(c236.AnclaNoReproducida):
        c236.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_anclaje_de_r_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c236, "ANCLA_R", 999.0)
    with pytest.raises(c236.AnclaNoReproducida):
        c236.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_anclaje_de_n_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c236, "ANCLA_N_DURACIONES", 1)
    with pytest.raises(c236.AnclaNoReproducida):
        c236.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_anclaje_de_tasa_de_revision_roto_aborta_sin_escribir(tmp_path, monkeypatch):
    monkeypatch.setattr(c236, "ANCLA_RHO", 0.5)
    with pytest.raises(c236.AnclaNoReproducida):
        c236.ejecutar(salida=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_r_media_no_se_lee_de_una_constante_sino_de_las_duraciones():
    duraciones = c236.cargar_duraciones_revision()
    assert len(duraciones) == 138
    assert c236._media(duraciones) == pytest.approx(22.063166666666667)
