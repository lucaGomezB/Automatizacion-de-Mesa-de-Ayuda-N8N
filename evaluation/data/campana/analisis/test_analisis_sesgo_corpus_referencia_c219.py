"""Pruebas de las funciones puras del analisis de sesgo de corpus y referencia (c-219).

Casos sinteticos (vocabularios y textos inventados), sin leer el corpus ni usar red. Los
valores esperados se calcularon a mano con la formula del backend:

    score = (0,5 * margin_ratio + 0,3 * evidence + 0,2 * density) / 1,0
    margin_ratio = (ganador - segundo) / (ganador + segundo)
    evidence     = ganador / (ganador + min_matches)       con min_matches = 2
    density      = min(1, 200 / largo_del_texto)
    cortocircuita si hay ganador unico y score >= 0,5166
"""

from __future__ import annotations

import pathlib
import sys

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import analisis_sesgo_corpus_referencia_c219 as c219  # noqa: E402

VOCAB = {
    "A": [r"\bfoo\b", r"\bbar\b", r"\bqux\b"],
    "B": [r"\bbaz\b", r"\bzap\b"],
}


def _evaluar(texto, vocab=VOCAB):
    return c219.evaluar_texto(texto, c219.compilar_vocabulario(vocab))


# ---------------------------------------------------------------------------
# Adaptador de scoring (2.1 a 2.3)
# ---------------------------------------------------------------------------
def test_puntaje_cuenta_patrones_distintos_y_no_repeticiones():
    # "foo foo foo bar": 2 patrones distintos de A (foo, bar), ninguno de B.
    resultado = _evaluar("foo foo foo bar")
    assert resultado["puntajes"] == {"A": 2.0, "B": 0.0}


def test_dos_matches_sin_rival_cortocircuitan_con_score_0_85():
    # "foo bar" (7 caracteres): margin 1; evidence 2/4 = 0,5; density 1.
    # score = 0,5*1 + 0,3*0,5 + 0,2*1 = 0,85.
    resultado = _evaluar("foo bar")
    assert resultado["sector"] == "A"
    assert resultado["score_correctitud"] == pytest.approx(0.85)
    assert resultado["cortocircuita"] is True
    assert resultado["cubierto"] is True


def test_un_solo_match_en_texto_largo_conserva_score_no_nulo_0_64():
    # 1 match en 1000 caracteres: margin 1; evidence 1/3; density 0,2.
    # score = 0,5 + 0,3/3 + 0,2*0,2 = 0,5 + 0,1 + 0,04 = 0,64.
    texto = "foo " + "x" * 996  # 1000 caracteres
    assert len(texto) == 1000
    resultado = _evaluar(texto)
    assert resultado["score_correctitud"] == pytest.approx(0.64)
    assert resultado["cortocircuita"] is True


def test_borde_del_umbral_acepta_0_516667_y_rechaza_0_48():
    # "foo bar baz" (11 car.): A=2, B=1: margin 1/3; evidence 0,5; density 1.
    # score = 0,5/3 + 0,15 + 0,2 = 0,516667 >= 0,5166 -> cortocircuita.
    borde = _evaluar("foo bar baz")
    assert borde["score_correctitud"] == pytest.approx(0.5 / 3 + 0.35)
    assert borde["cortocircuita"] is True
    # "foo bar qux baz zap" (19 car.): A=3, B=2: margin 0,2; evidence 0,6; density 1.
    # score = 0,1 + 0,18 + 0,2 = 0,48 < 0,5166 -> escala aunque haya ganador.
    debajo = _evaluar("foo bar qux baz zap")
    assert debajo["sector"] == "A"
    assert debajo["score_correctitud"] == pytest.approx(0.48)
    assert debajo["cortocircuita"] is False
    assert debajo["cubierto"] is True


def test_empate_no_tiene_ganador_ni_cortocircuita_pero_cuenta_como_cubierto():
    resultado = _evaluar("foo baz")
    assert resultado["sector"] is None
    assert resultado["cortocircuita"] is False
    assert resultado["score_correctitud"] == 0.0
    assert resultado["cubierto"] is True


def test_sin_match_no_esta_cubierto_ni_cortocircuita():
    resultado = _evaluar("texto sin ningun termino")
    assert resultado["puntajes"] == {"A": 0.0, "B": 0.0}
    assert resultado["sector"] is None
    assert resultado["cubierto"] is False
    assert resultado["cortocircuita"] is False


def test_vocabulario_vacio_no_cubre_ni_cortocircuita_y_no_falla():
    resultado = _evaluar("foo bar baz", vocab={"A": [], "B": []})
    assert resultado["puntajes"] == {"A": 0.0, "B": 0.0}
    assert resultado["cubierto"] is False
    assert resultado["cortocircuita"] is False


def test_matching_ignora_mayusculas_y_respeta_limites_de_palabra():
    assert _evaluar("FOO Bar")["puntajes"]["A"] == 2.0
    # "foobar" no contiene las palabras completas foo ni bar.
    assert _evaluar("foobar")["puntajes"]["A"] == 0.0


# ---------------------------------------------------------------------------
# Metricas por vocabulario y delta (2.1, 2.3)
# ---------------------------------------------------------------------------
def _evaluaciones():
    # Cuatro casos: c1 cortocircuita en A (acierta), c2 cortocircuita en B (falla contra A),
    # c3 cubierto pero empatado, c4 sin match.
    textos = {
        "c1": "foo bar",
        "c2": "baz zap",
        "c3": "foo baz",
        "c4": "nada",
    }
    compilado = c219.compilar_vocabulario(VOCAB)
    return {k: c219.evaluar_texto(t, compilado) for k, t in textos.items()}


def test_metricas_cuentan_cobertura_cortocircuito_aciertos_y_wilson():
    referencia = {"c1": "A", "c2": "A", "c3": "A", "c4": "B"}
    metricas = c219.metricas_vocabulario(_evaluaciones(), referencia)
    assert metricas["casos"] == 4
    assert metricas["cobertura"] == 3
    assert metricas["cortocircuito"] == 2
    assert metricas["aciertos"] == 1
    assert metricas["precision"] == pytest.approx(0.5)
    # Wilson 95 % para 1/2: [0,0945; 0,9055] (valor conocido de la formula cerrada).
    bajo, alto = metricas["ic_precision"]
    assert bajo == pytest.approx(0.0945, abs=5e-4)
    assert alto == pytest.approx(0.9055, abs=5e-4)


def test_metricas_sin_cortocircuitados_dan_precision_nula_y_ic_completo():
    referencia = {"c4": "B"}
    ev = {"c4": _evaluaciones()["c4"]}
    metricas = c219.metricas_vocabulario(ev, referencia)
    assert metricas["cortocircuito"] == 0
    assert metricas["precision"] is None
    assert metricas["ic_precision"] == (0.0, 1.0)


def test_delta_frente_a_base_resta_cobertura_cortocircuito_y_puntos_de_precision():
    base = {"cobertura": 131, "cortocircuito": 115, "precision": 0.75}
    otro = {"cobertura": 100, "cortocircuito": 74, "precision": 0.5}
    delta = c219.delta_frente_a(otro, base)
    assert delta["cobertura"] == -31
    assert delta["cortocircuito"] == -41
    assert delta["precision_puntos"] == pytest.approx(-25.0)


def test_delta_sin_precision_en_alguno_de_los_dos_es_nulo():
    base = {"cobertura": 5, "cortocircuito": 0, "precision": None}
    otro = {"cobertura": 7, "cortocircuito": 2, "precision": 0.5}
    assert c219.delta_frente_a(otro, base)["precision_puntos"] is None
    assert c219.delta_frente_a(otro, base)["cobertura"] == 2


# ---------------------------------------------------------------------------
# Subconjuntos de la referencia (3.1 a 3.3)
# ---------------------------------------------------------------------------
def _origen():
    origen = {f"k{i}": "consenso_e3_e4" for i in range(5)}
    origen.update({f"a{i}": "arbitraje_e5" for i in range(3)})
    return origen


def test_subconjuntos_separan_consenso_arbitrado_tres_vias_y_union():
    sub = c219.construir_subconjuntos(_origen(), tres_vias_ids=["a2"])
    assert len(sub["consenso"]) == 5
    assert len(sub["arbitrado"]) == 3
    assert sub["tres_vias"] == ["a2"]
    assert sub["total"] == sorted(_origen())
    assert set(sub["consenso"]) | set(sub["arbitrado"]) == set(sub["total"])
    assert set(sub["consenso"]) & set(sub["arbitrado"]) == set()


def test_subconjuntos_rechaza_origen_desconocido_y_tres_vias_fuera_de_arbitrados():
    with pytest.raises(c219.EntradaInconsistente):
        c219.construir_subconjuntos({"x": "otro"}, tres_vias_ids=[])
    with pytest.raises(c219.EntradaInconsistente):
        c219.construir_subconjuntos(_origen(), tres_vias_ids=["k0"])


def test_conjunto_literal_e3_e4_e5_es_vacio_cuando_e5_solo_etiqueto_discordantes():
    etiquetas = {
        "k0": {"E3": "A", "E4": "A"},  # consenso: sin E5
        "a0": {"E3": "A", "E4": "B", "E5": "A"},  # discordante: E5 etiqueto
        "a1": {"E3": "B", "E4": "A", "E5": "B"},
    }
    assert c219.conjunto_e3_e4_e5(etiquetas) == []


def test_conjunto_literal_e3_e4_e5_detecta_coincidencia_triple_si_existiera():
    etiquetas = {
        "x": {"E3": "A", "E4": "A", "E5": "A"},
        "y": {"E3": "A", "E4": "B", "E5": "A"},
        "z": {"E3": "A", "E4": "A"},
    }
    assert c219.conjunto_e3_e4_e5(etiquetas) == ["x"]


def test_exactitud_estricta_y_laxa_por_subconjunto_con_wilson():
    referencia = {"c1": "A", "c2": "A", "c3": "B", "c4": "B"}
    predicciones = {"c1": "A", "c2": "B", "c3": "B", "c4": "A"}
    adicionales = {"c1": [], "c2": ["B"], "c3": [], "c4": []}
    # Estricta: c1 y c3 aciertan = 2/4. Laxa: c2 acierta por adicional = 3/4.
    r = c219.exactitud_subconjunto(
        ["c1", "c2", "c3", "c4"], referencia, predicciones, adicionales
    )
    assert (r["casos"], r["aciertos"]) == (4, 2)
    assert r["exactitud"] == pytest.approx(0.5)
    assert (r["aciertos_laxos"], r["exactitud_laxa"]) == (3, pytest.approx(0.75))
    # Wilson para 2/4: [0,1500; 0,8500].
    assert r["ic"][0] == pytest.approx(0.1500, abs=5e-4)
    assert r["ic"][1] == pytest.approx(0.8500, abs=5e-4)


def test_exactitud_de_subconjunto_vacio_es_nula_con_ic_completo():
    r = c219.exactitud_subconjunto([], {}, {}, {})
    assert r["casos"] == 0
    assert r["exactitud"] is None
    assert r["ic"] == (0.0, 1.0)


def test_wilson_reproduce_los_anclajes_del_diseno():
    # Valores del design.md D3 (4 decimales).
    for aciertos, total, bajo, alto in (
        (109, 142, 0.6916, 0.8295),
        (33, 64, 0.3958, 0.6337),
        (142, 206, 0.6231, 0.7486),
    ):
        ic_bajo, ic_alto = c219.intervalo_wilson(aciertos, total)
        assert round(ic_bajo, 4) == pytest.approx(bajo, abs=1e-4)
        assert round(ic_alto, 4) == pytest.approx(alto, abs=1e-4)


# ---------------------------------------------------------------------------
# Vocabulario y anclajes (2.5, 2.6)
# ---------------------------------------------------------------------------
def test_vocabulario_corpus_blind_fijado_cubre_las_cinco_clases_y_su_hash():
    vocab = c219.cargar_vocabulario_corpus_blind()
    assert set(vocab) == set(c219.CLASES_CANONICAS)
    assert all(len(patrones) > 0 for patrones in vocab.values())
    assert c219.hash_vocabulario(vocab) == c219.SHA256_VOCABULARIO_FIJADO


def test_vocabulario_modificado_no_coincide_con_el_hash_fijado(tmp_path):
    import json

    original = json.loads(c219.RUTA_VOCABULARIO.read_text(encoding="utf-8"))
    original["vocabulario"]["Sistemas"].append(r"\bagregado\b")
    ruta = tmp_path / "vocab.json"
    ruta.write_text(json.dumps(original), encoding="utf-8")
    with pytest.raises(c219.EntradaInconsistente):
        c219.cargar_vocabulario_corpus_blind(ruta)


def test_verificar_anclajes_acepta_los_valores_esperados_y_rechaza_cualquier_otro():
    c219.verificar_anclajes(cortocircuito=115, aciertos_det=88, aciertos_hibrido=142, n=206)
    with pytest.raises(c219.AnclaNoReproducida):
        c219.verificar_anclajes(cortocircuito=114, aciertos_det=88, aciertos_hibrido=142, n=206)
    with pytest.raises(c219.AnclaNoReproducida):
        c219.verificar_anclajes(cortocircuito=115, aciertos_det=88, aciertos_hibrido=141, n=206)


# ---------------------------------------------------------------------------
# Integracion sobre los artefactos versionados (no imprimen descripciones)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def entradas():
    return c219.cargar_entradas()


@pytest.fixture(scope="module")
def documento(entradas):
    return c219.construir_documento(entradas)


def test_entradas_reproducen_los_conteos_y_los_subconjuntos_de_referencia(entradas):
    assert entradas["conteos"] == {
        "casos": 206,
        "filas_etiquetado": 476,
        "consenso": 142,
        "arbitrados_e5": 64,
        "tres_vias": 6,
        "predicciones": 206,
    }
    sub = entradas["subconjuntos"]
    assert len(sub["consenso"]) + len(sub["arbitrado"]) == 206
    assert c219.conjunto_e3_e4_e5(entradas["etiquetas"]) == []


def test_ancla_incumplida_aborta_sin_escribir_salidas(entradas, tmp_path, monkeypatch):
    monkeypatch.setattr(c219, "ANCLA_CORTOCIRCUITO", 116)
    with pytest.raises(c219.AnclaNoReproducida):
        c219.ejecutar(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_el_documento_reproduce_los_anclajes_del_diseno(documento):
    ancla = documento["anclajes"]
    assert (ancla["cortocircuito_v1"], ancla["aciertos_det_v1"]) == (115, 88)
    assert (ancla["aciertos_hibrido"], ancla["casos"]) == (142, 206)
    assert ancla["patrones"] == {"v1": 151, "v0": 89, "derivados_del_corpus": 62}
    sub = documento["subconjuntos"]
    assert (sub["consenso"]["aciertos"], sub["consenso"]["casos"]) == (109, 142)
    assert (sub["arbitrado"]["aciertos"], sub["arbitrado"]["casos"]) == (33, 64)
    assert documento["conjunto_literal_e3_e4_e5"]["casos"] == 0


def test_dos_construcciones_y_escrituras_son_identicas_byte_a_byte(entradas, tmp_path):
    uno, dos = tmp_path / "uno", tmp_path / "dos"
    c219.escribir(c219.construir_documento(entradas), uno)
    c219.escribir(c219.construir_documento(entradas), dos)
    nombres = sorted(p.name for p in uno.iterdir())
    assert len(nombres) == 3
    for nombre in nombres:
        contenido = (uno / nombre).read_bytes()
        assert contenido == (dos / nombre).read_bytes()
        assert b"\r" not in contenido and not contenido.startswith(b"\xef\xbb\xbf")
