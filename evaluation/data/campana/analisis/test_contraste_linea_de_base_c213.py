"""Pruebas del contraste pareado linea de base frente a hibrido (c-213).

Cifras ancla (artefactos versionados): linea de base balanceada 67/103 y sin
re-ponderacion 60/103 (c-210); hibrido 87/103 (c-205).
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import contraste_linea_de_base_c213 as c213  # noqa: E402


# ---------------------------------------------------------------------------
# Emparejamiento por caso_id
# ---------------------------------------------------------------------------
def test_emparejar_respeta_el_orden_de_la_referencia():
    referencia = {"A": "x", "B": "y", "C": "x"}
    sistema_1 = {"C": "x", "A": "y", "B": "y"}
    sistema_2 = {"B": "x", "A": "x", "C": "x"}
    ids, aciertos_1, aciertos_2 = c213.emparejar(referencia, sistema_1, sistema_2)
    assert ids == ["A", "B", "C"]
    assert aciertos_1 == [False, True, True]
    assert aciertos_2 == [True, False, True]


def test_emparejar_otro_orden_y_otros_datos():
    referencia = {"Z9": "s", "Z1": "t"}
    ids, a1, a2 = c213.emparejar(referencia, {"Z1": "t", "Z9": "t"}, {"Z1": "s", "Z9": "s"})
    assert ids == ["Z9", "Z1"]
    assert a1 == [False, True]
    assert a2 == [True, False]


def test_emparejar_caso_sin_pareja_aborta():
    with pytest.raises(ValueError, match="B"):
        c213.emparejar({"A": "x", "B": "y"}, {"A": "x"}, {"A": "x", "B": "y"})


def test_emparejar_caso_sin_pareja_en_el_segundo_sistema_aborta():
    with pytest.raises(ValueError, match="A"):
        c213.emparejar({"A": "x"}, {"A": "x"}, {})


# ---------------------------------------------------------------------------
# Tabla 2x2 y McNemar
# ---------------------------------------------------------------------------
def test_tabla_2x2_con_discordancias_suma_n_y_calcula_la_diferencia():
    hibrido = [True] * 7 + [True] * 3 + [False] * 1 + [False] * 4
    base = [True] * 7 + [False] * 3 + [True] * 1 + [False] * 4
    r = c213.contraste_pareado(hibrido, base)
    assert r["tabla_2x2"] == {
        "ambos_aciertan": 7,
        "solo_hibrido": 3,
        "solo_linea_de_base": 1,
        "ninguno": 4,
    }
    assert sum(r["tabla_2x2"].values()) == 15
    assert r["n"] == 15
    assert r["diferencia_exactitud"]["valor"] == pytest.approx(2 / 15)
    assert r["mcnemar"]["aplicable"] is True
    assert r["mcnemar"]["p_exacto"] == pytest.approx(0.625)  # 2*P(X<=1 | 4, 0.5)
    assert r["mcnemar"]["p_corregido"] is not None


def test_tabla_2x2_segundo_caso_con_otras_cifras():
    hibrido = [True, True, True, True, False, False]
    base = [False, False, False, True, True, False]
    r = c213.contraste_pareado(hibrido, base, remuestreos=200)
    assert r["tabla_2x2"]["solo_hibrido"] == 3
    assert r["tabla_2x2"]["solo_linea_de_base"] == 1
    assert r["tabla_2x2"]["ambos_aciertan"] == 1
    assert r["tabla_2x2"]["ninguno"] == 1
    assert r["diferencia_exactitud"]["valor"] == pytest.approx(2 / 6)


def test_sin_discordancias_el_contraste_no_es_aplicable_y_no_hay_p():
    aciertos = [True, False, True, False]
    r = c213.contraste_pareado(aciertos, list(aciertos))
    assert r["mcnemar"]["aplicable"] is False
    assert r["mcnemar"]["p_exacto"] is None
    assert r["mcnemar"]["p_corregido"] is None
    assert r["diferencia_exactitud"]["valor"] == 0.0
    assert r["diferencia_exactitud"]["ic95"] == [0.0, 0.0]


def test_sin_discordancias_con_otros_aciertos():
    r = c213.contraste_pareado([True] * 5, [True] * 5)
    assert r["mcnemar"]["aplicable"] is False
    assert r["tabla_2x2"]["ambos_aciertan"] == 5


# ---------------------------------------------------------------------------
# Bootstrap pareado
# ---------------------------------------------------------------------------
def test_bootstrap_con_semilla_fija_es_reproducible_y_contiene_el_valor():
    hibrido = [True] * 30 + [True] * 10 + [False] * 3 + [False] * 7
    base = [True] * 30 + [False] * 10 + [True] * 3 + [False] * 7
    r1 = c213.contraste_pareado(hibrido, base, remuestreos=500, semilla=7)
    r2 = c213.contraste_pareado(hibrido, base, remuestreos=500, semilla=7)
    assert r1 == r2
    inferior, superior = r1["diferencia_exactitud"]["ic95"]
    assert inferior <= r1["diferencia_exactitud"]["valor"] <= superior
    assert inferior < superior
    assert r1["diferencia_exactitud"]["valor"] == pytest.approx(7 / 50)


def test_bootstrap_cambia_con_la_semilla():
    hibrido = [True] * 25 + [False] * 15
    base = [True] * 3 + [False] * 22 + [True] * 6 + [False] * 9
    ic_a = c213.contraste_pareado(hibrido, base, remuestreos=40, semilla=1)["diferencia_exactitud"]["ic95"]
    ic_b = c213.contraste_pareado(hibrido, base, remuestreos=40, semilla=2)["diferencia_exactitud"]["ic95"]
    assert ic_a != ic_b


def test_bootstrap_longitudes_distintas_aborta():
    with pytest.raises(ValueError):
        c213.contraste_pareado([True, False], [True])


# ---------------------------------------------------------------------------
# Anclas
# ---------------------------------------------------------------------------
def test_verificar_anclas_pasa_cuando_coinciden():
    c213.verificar_anclas({"balanceada": 67, "sin_repoderacion": 60, "hibrido": 87},
                          {"balanceada": 67, "sin_repoderacion": 60, "hibrido": 87})


def test_verificar_anclas_aborta_y_nombra_la_diferencia():
    with pytest.raises(c213.AnclaNoReproducida, match="sin_repoderacion"):
        c213.verificar_anclas({"balanceada": 67, "sin_repoderacion": 59, "hibrido": 87},
                              {"balanceada": 67, "sin_repoderacion": 60, "hibrido": 87})


def test_verificar_anclas_aborta_con_otro_sistema():
    with pytest.raises(c213.AnclaNoReproducida, match="hibrido"):
        c213.verificar_anclas({"balanceada": 67, "sin_repoderacion": 60, "hibrido": 88},
                              {"balanceada": 67, "sin_repoderacion": 60, "hibrido": 87})


# ---------------------------------------------------------------------------
# Corrida real (insumos versionados)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def doc_real():
    return c213.construir_documento()


def test_documento_real_reproduce_las_anclas(doc_real):
    assert doc_real["n"] == 103
    assert doc_real["aciertos"] == {"hibrido": 87, "balanceada": 67, "sin_repoderacion": 60}
    for variante in ("balanceada", "sin_repoderacion"):
        tabla = doc_real["contrastes"][variante]["tabla_2x2"]
        assert sum(tabla.values()) == 103
        assert tabla["ambos_aciertan"] + tabla["solo_hibrido"] == 87


def test_documento_real_trae_predicciones_por_caso_y_hashes(doc_real):
    assert len(doc_real["casos"]) == 103
    fila = doc_real["casos"][0]
    assert {"caso_id", "referencia", "hibrido", "balanceada", "sin_repoderacion",
            "acierto_hibrido", "acierto_balanceada", "acierto_sin_repoderacion"} <= set(fila)
    assert doc_real["aditivo"]["reemplaza_numeros_canonicos"] is False
    assert all(len(h) == 64 for h in doc_real["entradas_sha256"].values())


def test_referencia_alternativa_con_n_esperado_distinto_aborta():
    with pytest.raises(ValueError, match="n esperado"):
        c213.construir_documento(n_esperado=150)


def test_escritura_es_determinista_byte_a_byte(tmp_path, doc_real):
    c213.escribir(doc_real, tmp_path / "a")
    c213.escribir(doc_real, tmp_path / "b")
    for nombre in (c213.NOMBRE_JSON, c213.NOMBRE_MD):
        a = (tmp_path / "a" / nombre).read_bytes()
        b = (tmp_path / "b" / nombre).read_bytes()
        assert a == b
        assert b"\r" not in a and not a.startswith(b"\xef\xbb\xbf")


def test_anclas_no_reproducidas_no_escribe_artefactos(tmp_path):
    with pytest.raises(c213.AnclaNoReproducida):
        c213.ejecutar(salida=tmp_path, anclas_esperadas={"balanceada": 1, "sin_repoderacion": 60, "hibrido": 87})
    assert list(tmp_path.iterdir()) == []
