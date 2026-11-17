"""Pruebas del analisis offline de robustez de la linea de base (c-225).

TDD estricto de las funciones puras con casos sinteticos (sin I/O de red) mas la
integracion con los artefactos versionados. Cubre la derivacion de los tres subconjuntos
de referencia, el contraste pareado por subconjunto y variante, la verificacion de anclas
que aborta antes de escribir y la escritura determinista byte a byte.
"""
# Nota (c-240): se retiraron de este modulo las pruebas que leian los archivos
# `evaluation/data/campana/corpus_independiente.json` y/o `corpus_independiente_arbitrado.json`,
# eliminados del repositorio publico por la decision de los autores (c-240, OOS-027). Las pruebas
# restantes no dependen de esos archivos. El nuevo estado se verifica en
# `evaluation/tests/test_retiro_corpus_independiente_c240.py`.

from __future__ import annotations

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


# ---------------------------------------------------------------------------
# Salidas: aborto sin escribir, declaracion aditiva y determinismo
# ---------------------------------------------------------------------------


