"""Pruebas del analisis offline de robustez de la linea de base (c-225).

TDD estricto de las funciones puras con casos sinteticos (sin I/O de red) mas la
integracion con los artefactos versionados. Cubre la derivacion de los tres subconjuntos
de referencia, el contraste pareado por subconjunto y variante, la verificacion de anclas
que aborta antes de escribir y la escritura determinista byte a byte.
"""

from __future__ import annotations

import json
import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_robustez_linea_de_base_c225 as c225  # noqa: E402


# ---------------------------------------------------------------------------
# Derivacion de los tres subconjuntos (funcion pura)
# ---------------------------------------------------------------------------
def _ids_y_origen(n: int = 206, consenso: int = 142) -> tuple[list[str], dict[str, str]]:
    ids = [f"I{k:03d}" for k in range(1, n + 1)]
    origen = {
        caso: ("consenso_e3_e4" if k <= consenso else "arbitraje_e5")
        for k, caso in enumerate(ids, start=1)
    }
    return ids, origen


def test_derivar_subconjuntos_separa_consenso_originales_y_completo():
    ids, origen = _ids_y_origen()

    subconjuntos = c225.derivar_subconjuntos(ids, origen)

    assert set(subconjuntos) == {"consenso_e3_e4", "original_150", "arbitrado_completo"}
    assert len(subconjuntos["consenso_e3_e4"]) == 142
    assert len(subconjuntos["original_150"]) == 150
    assert len(subconjuntos["arbitrado_completo"]) == 206
    assert subconjuntos["consenso_e3_e4"] == ids[:142]
    assert subconjuntos["arbitrado_completo"] == ids


def test_derivar_subconjuntos_toma_originales_por_identificador_no_por_posicion():
    ids, origen = _ids_y_origen()
    reordenados = list(reversed(ids))

    subconjuntos = c225.derivar_subconjuntos(reordenados, origen)

    assert subconjuntos["original_150"][0] == "I150"
    assert subconjuntos["original_150"][-1] == "I001"
    assert set(subconjuntos["original_150"]) == {f"I{k:03d}" for k in range(1, 151)}
    assert "I151" not in subconjuntos["original_150"]


def test_derivar_subconjuntos_falla_si_falta_el_origen_de_un_caso():
    ids, origen = _ids_y_origen()
    del origen["I200"]

    with pytest.raises(ValueError, match="I200"):
        c225.derivar_subconjuntos(ids, origen)


def test_derivar_subconjuntos_falla_si_una_cardinalidad_no_coincide():
    ids, origen = _ids_y_origen(n=3, consenso=2)

    with pytest.raises(ValueError, match="cardinalidad"):
        c225.derivar_subconjuntos(ids, origen)


def test_cardinalidades_reales_se_derivan_de_los_artefactos():
    ids, origen = c225.cargar_ids_y_origen(c225.CAMPANA / "arbitraje_tres_vias.json")

    subconjuntos = c225.derivar_subconjuntos(ids, origen)

    assert len(subconjuntos["consenso_e3_e4"]) == 142
    assert len(subconjuntos["original_150"]) == 150
    assert len(subconjuntos["arbitrado_completo"]) == 206
    assert subconjuntos["original_150"] == [f"I{k:03d}" for k in range(1, 151)]

# ---------------------------------------------------------------------------
# Contraste pareado por subconjunto (funcion pura)
# ---------------------------------------------------------------------------
def test_contraste_pareado_calcula_tabla_diferencia_y_mcnemar():
    hibrido = [True, True, True, False]
    base = [False, False, False, True]

    resultado = c225.contraste_pareado(hibrido, base, remuestreos=2000)

    assert resultado["n"] == 4
    assert resultado["aciertos"] == {"hibrido": 3, "linea_de_base": 1}
    assert resultado["tabla_2x2"] == {
        "ambos_aciertan": 0,
        "solo_hibrido": 3,
        "solo_linea_de_base": 1,
        "ninguno": 0,
    }
    assert resultado["mcnemar"]["p_exacto"] == pytest.approx(0.625)
    assert resultado["mcnemar"]["criterio_stats"] == "exacto"
    assert resultado["diferencia_exactitud"]["valor"] == pytest.approx(0.5)
    assert resultado["diferencia_exactitud"]["remuestreos"] == 2000
    inferior, superior = resultado["diferencia_exactitud"]["ic95"]
    assert inferior <= 0.5 <= superior


def test_contraste_pareado_empate_no_aplica_mcnemar_y_diferencia_cero():
    aciertos = [True, False, True, True]

    resultado = c225.contraste_pareado(aciertos, aciertos, remuestreos=100)

    assert resultado["tabla_2x2"] == {
        "ambos_aciertan": 3,
        "solo_hibrido": 0,
        "solo_linea_de_base": 0,
        "ninguno": 1,
    }
    assert resultado["mcnemar"]["aplicable"] is False
    assert resultado["diferencia_exactitud"]["valor"] == 0.0
    assert resultado["diferencia_exactitud"]["ic95"] == [0.0, 0.0]


def test_contraste_pareado_es_reproducible_con_la_misma_semilla():
    hibrido = [True, True, False, True, False, False, True, True]
    base = [False, True, False, False, False, True, True, False]

    primera = c225.contraste_pareado(hibrido, base, remuestreos=500)
    segunda = c225.contraste_pareado(hibrido, base, remuestreos=500)

    assert primera == segunda


# ---------------------------------------------------------------------------
# Anclas verificadas antes de escribir
# ---------------------------------------------------------------------------
def test_verificar_anclas_acepta_los_agregados_versionados():
    c225.verificar_anclas(
        {
            "hibrido": {
                "consenso_e3_e4": 109,
                "original_150": 112,
                "arbitrado_completo": 142,
            },
            "balanceada": {"arbitrado_completo": 101},
            "sin_repoderacion": {"arbitrado_completo": 88},
        }
    )


def test_verificar_anclas_rechaza_un_acierto_distinto():
    observados = {
        "hibrido": {
            "consenso_e3_e4": 109,
            "original_150": 111,
            "arbitrado_completo": 142,
        },
        "balanceada": {"arbitrado_completo": 101},
        "sin_repoderacion": {"arbitrado_completo": 88},
    }

    with pytest.raises(c225.AnclaNoReproducida, match="original_150"):
        c225.verificar_anclas(observados)


def test_verificar_anclas_rechaza_un_sistema_ausente():
    observados = {
        "hibrido": {
            "consenso_e3_e4": 109,
            "original_150": 112,
            "arbitrado_completo": 142,
        },
        "balanceada": {"arbitrado_completo": 101},
    }

    with pytest.raises(c225.AnclaNoReproducida, match="sin_repoderacion"):
        c225.verificar_anclas(observados)


# ---------------------------------------------------------------------------
# Documento real: anclas, subconjuntos y brecha con IC
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def documento_real():
    return c225.construir_documento()


def test_construir_documento_reproduce_anclas_y_reporta_los_tres_subconjuntos(documento_real):
    assert documento_real["anclas_verificadas"] == c225.ANCLAS_ESPERADAS
    assert documento_real["variante_primaria"] == "balanceada"
    assert documento_real["n_entrenamiento"] == 200
    assert documento_real["contexto"] == {
        "arbitraje_e5": 64,
        "tres_vias": 6,
        "nota": "particiones de contexto; no son subconjuntos de contraste",
    }

    subconjuntos = documento_real["subconjuntos"]
    assert set(subconjuntos) == {"consenso_e3_e4", "original_150", "arbitrado_completo"}
    assert {nombre: datos["n"] for nombre, datos in subconjuntos.items()} == {
        "consenso_e3_e4": 142,
        "original_150": 150,
        "arbitrado_completo": 206,
    }
    assert subconjuntos["consenso_e3_e4"]["aciertos"] == {
        "hibrido": 109,
        "balanceada": 76,
        "sin_repoderacion": 63,
    }
    assert subconjuntos["original_150"]["aciertos"] == {
        "hibrido": 112,
        "balanceada": 87,
        "sin_repoderacion": 80,
    }
    assert subconjuntos["arbitrado_completo"]["aciertos"] == {
        "hibrido": 142,
        "balanceada": 101,
        "sin_repoderacion": 88,
    }


def test_construir_documento_reporta_la_brecha_y_su_ic_por_variante(documento_real):
    subconjuntos = documento_real["subconjuntos"]

    balanceada_142 = subconjuntos["consenso_e3_e4"]["contrastes"]["balanceada"]
    assert balanceada_142["diferencia_exactitud"]["valor"] == pytest.approx(33 / 142)
    assert balanceada_142["tabla_2x2"]["solo_hibrido"] == 43
    assert balanceada_142["tabla_2x2"]["solo_linea_de_base"] == 10
    assert balanceada_142["diferencia_exactitud"]["ic95"][0] == pytest.approx(0.1408, abs=1e-4)
    assert balanceada_142["diferencia_exactitud"]["ic95"][1] == pytest.approx(0.3239, abs=1e-4)

    balanceada_150 = subconjuntos["original_150"]["contrastes"]["balanceada"]
    assert balanceada_150["diferencia_exactitud"]["valor"] == pytest.approx(25 / 150)
    assert balanceada_150["diferencia_exactitud"]["ic95"][0] == pytest.approx(0.0733, abs=1e-4)
    assert balanceada_150["diferencia_exactitud"]["ic95"][1] == pytest.approx(0.2600, abs=1e-4)

    balanceada_206 = subconjuntos["arbitrado_completo"]["contrastes"]["balanceada"]
    assert balanceada_206["diferencia_exactitud"]["valor"] == pytest.approx(41 / 206)
    assert balanceada_206["diferencia_exactitud"]["ic95"][0] == pytest.approx(0.1165, abs=1e-4)
    assert balanceada_206["diferencia_exactitud"]["ic95"][1] == pytest.approx(0.2767, abs=1e-4)

    sin_repoderacion_206 = subconjuntos["arbitrado_completo"]["contrastes"][
        "sin_repoderacion"
    ]
    assert sin_repoderacion_206["diferencia_exactitud"]["valor"] == pytest.approx(54 / 206)
    assert sin_repoderacion_206["diferencia_exactitud"]["ic95"][0] == pytest.approx(
        0.1845, abs=1e-4
    )
    assert sin_repoderacion_206["diferencia_exactitud"]["ic95"][1] == pytest.approx(
        0.3398, abs=1e-4
    )


def test_ninguna_brecha_por_subconjunto_cruza_el_cero(documento_real):
    for nombre, datos in documento_real["subconjuntos"].items():
        for variante in ("balanceada", "sin_repoderacion"):
            diferencia = datos["contrastes"][variante]["diferencia_exactitud"]
            assert diferencia["valor"] > 0, (nombre, variante)
            assert diferencia["ic95"][0] > 0, (nombre, variante)
            assert diferencia["ic95"][1] > diferencia["ic95"][0], (nombre, variante)


def test_construir_documento_aborta_si_un_ancla_no_coincide():
    anclas = {sistema: dict(valores) for sistema, valores in c225.ANCLAS_ESPERADAS.items()}
    anclas["hibrido"]["original_150"] = 111

    with pytest.raises(c225.AnclaNoReproducida, match="original_150"):
        c225.construir_documento(anclas_esperadas=anclas)


# ---------------------------------------------------------------------------
# Salidas: aborto sin escribir, declaracion aditiva y determinismo
# ---------------------------------------------------------------------------
def test_ancla_rota_aborta_sin_escribir(tmp_path, monkeypatch):
    def _falla(*_args, **_kwargs):
        raise c225.AnclaNoReproducida("ancla rota")

    monkeypatch.setattr(c225, "verificar_anclas", _falla)

    with pytest.raises(c225.AnclaNoReproducida):
        c225.ejecutar(salida=tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_escribir_declara_sensibilidad_y_conserva_las_cifras_canonicas(tmp_path, documento_real):
    c225.escribir(documento_real, tmp_path)
    datos = json.loads((tmp_path / c225.SALIDA_JSON).read_text(encoding="utf-8"))
    texto_md = (tmp_path / c225.SALIDA_MD).read_text(encoding="utf-8")

    assert datos["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert "0,6893" in datos["aditivo"]["declaracion"]
    assert "0,7024" in datos["aditivo"]["declaracion"]
    assert "0,85" in datos["aditivo"]["declaracion"]
    assert "multiplicidad" in datos["aditivo"]["declaracion"]
    assert "sensibilidad" in texto_md.lower()
    for nombre in ("consenso_e3_e4", "original_150", "arbitrado_completo"):
        assert nombre in texto_md
    assert "IC 95" in texto_md


def test_sha256sums_lista_las_dos_salidas(tmp_path, documento_real):
    c225.escribir(documento_real, tmp_path)
    lineas = (tmp_path / c225.SALIDA_SHA).read_text(encoding="utf-8").splitlines()

    assert len(lineas) == 2
    assert {linea.split("  ", 1)[1] for linea in lineas} == {
        c225.SALIDA_JSON,
        c225.SALIDA_MD,
    }


def test_dos_corridas_producen_bytes_identicos(tmp_path):
    primera = tmp_path / "primera"
    segunda = tmp_path / "segunda"
    primera.mkdir()
    segunda.mkdir()

    c225.ejecutar(salida=primera)
    c225.ejecutar(salida=segunda)

    for nombre in (c225.SALIDA_JSON, c225.SALIDA_MD, c225.SALIDA_SHA):
        assert (primera / nombre).read_bytes() == (segunda / nombre).read_bytes()
