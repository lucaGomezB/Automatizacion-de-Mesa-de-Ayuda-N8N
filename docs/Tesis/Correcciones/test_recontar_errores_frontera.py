"""Pruebas de recontar_errores_frontera.py (c-159, tareas 5.1 a 5.4).

Se ejecutan desde la raiz del repositorio con pytest, por ejemplo en la imagen
`eval-tests`:

    docker run --rm -v "<raiz>:/repo" -w /repo eval-tests python -m pytest docs/Tesis/Correcciones/test_recontar_errores_frontera.py -q

Las pruebas unitarias usan datos sinteticos; la de caracterizacion fija las
cifras que cita la tesis sobre el corpus y la evidencia reales y se omite si
esos archivos no estan.
"""
import hashlib
import json

import pytest

import recontar_errores_frontera as ref

HW = "Soporte Tecnico Hardware"
SW = "Soporte Tecnico Software"
SEG = "Seguridad Informatica"
BD = "Bases de Datos"
SIS = "Sistemas"


def _caso(cid, asignado, adicionales=(), descripcion=None):
    return {
        "id": cid,
        "descripcion": descripcion or f"descripcion {cid}",
        "sector_asignado": asignado,
        "sectores_adicionales": list(adicionales),
    }


def _pred(cid, predicho, descripcion=None, confianza=0.9, etapa="gemini"):
    return {
        "caso_id": cid,
        "descripcion": descripcion or f"descripcion {cid}",
        "sector_predicho": predicho,
        "confianza": confianza,
        "etapa": etapa,
    }


def _unidos(pares):
    """pares: (asignado, adicionales, predicho) -> casos unidos sinteticos."""
    casos = [_caso(f"C{i}", a, ad) for i, (a, ad, _) in enumerate(pares)]
    preds = [_pred(f"C{i}", p) for i, (_, _, p) in enumerate(pares)]
    return ref.unir_casos(casos, preds)


# --- hash con normalizacion de fin de linea ---------------------------------


def test_hash_normaliza_crlf_a_lf():
    assert ref.hash_normalizado(b"a\r\nb\r\n") == hashlib.sha256(b"a\nb\n").hexdigest()


def test_hash_coincide_con_lf_sin_cambios():
    assert ref.hash_normalizado(b"a\nb\n") == ref.hash_normalizado(b"a\r\nb\r\n")


def test_hash_distinto_si_cambia_el_contenido():
    assert ref.hash_normalizado(b"a\n") != ref.hash_normalizado(b"b\n")


def test_verificar_hash_rechaza_un_hash_distinto():
    with pytest.raises(ref.ValidacionError):
        ref.verificar_hash(b"contenido\n", "0" * 64)


def test_verificar_hash_acepta_el_hash_correcto():
    esperado = hashlib.sha256(b"contenido\n").hexdigest()
    ref.verificar_hash(b"contenido\r\n", esperado)


# --- cache_meta ---------------------------------------------------------------


def _meta(**cambios):
    meta = {"corpus_hash": "h", "corpus_count": 200, "classifier_version": "hybrid-v3"}
    meta.update(cambios)
    return meta


def test_cache_meta_valida_acepta_la_evidencia_esperada():
    ref.validar_cache_meta(_meta(), "h", 200, "hybrid-v3")


@pytest.mark.parametrize(
    "cambio",
    [
        {"corpus_hash": "otro"},
        {"corpus_count": 199},
        {"classifier_version": "hybrid-v2"},
    ],
)
def test_cache_meta_rechaza_cada_desvio(cambio):
    with pytest.raises(ref.ValidacionError):
        ref.validar_cache_meta(_meta(**cambio), "h", 200, "hybrid-v3")


# --- union por identificador --------------------------------------------------


def test_union_devuelve_un_registro_por_caso_en_el_orden_del_corpus():
    unidos = ref.unir_casos(
        [_caso("A", SW), _caso("B", HW)],
        [_pred("B", SW), _pred("A", SW)],
    )
    assert [u["id"] for u in unidos] == ["A", "B"]
    assert [u["sector_predicho"] for u in unidos] == [SW, SW]


def test_union_rechaza_caso_faltante_en_la_evidencia():
    with pytest.raises(ref.ValidacionError):
        ref.unir_casos([_caso("A", SW), _caso("B", HW)], [_pred("A", SW)])


def test_union_rechaza_prediccion_sin_caso_en_el_corpus():
    with pytest.raises(ref.ValidacionError):
        ref.unir_casos([_caso("A", SW)], [_pred("A", SW), _pred("Z", SW)])


def test_union_rechaza_identificador_duplicado():
    with pytest.raises(ref.ValidacionError):
        ref.unir_casos([_caso("A", SW)], [_pred("A", SW), _pred("A", SW)])


def test_union_rechaza_descripcion_distinta():
    with pytest.raises(ref.ValidacionError):
        ref.unir_casos([_caso("A", SW, descripcion="uno")], [_pred("A", SW, descripcion="dos")])


# --- frontera como par no ordenado -------------------------------------------


def test_frontera_sigue_el_orden_de_clases():
    assert ref.frontera(SW, HW) == (HW, SW)


def test_frontera_es_simetrica():
    assert ref.frontera(HW, SW) == ref.frontera(SW, HW)


def test_frontera_con_sistemas_y_seguridad():
    assert ref.frontera(SIS, SEG) == (SEG, SIS)


# --- conteo de errores y aciertos laxos --------------------------------------


def test_conteo_por_frontera_con_errores_laxos_y_plenos():
    unidos = _unidos(
        [
            (HW, (), SW),  # error pleno HW-SW
            (HW, (SW,), SW),  # error laxo HW-SW
            (SW, (), HW),  # error pleno, invertido, misma frontera
            (SW, (), SW),  # acierto
            (SIS, (SW,), SW),  # error laxo SIS-SW
        ]
    )
    res = ref.contar(unidos)
    assert res.total_casos == 5
    assert res.total_errores == 4
    assert res.total_laxos == 2
    assert res.por_frontera[ref.frontera(HW, SW)] == (3, 1)
    assert res.por_frontera[ref.frontera(SW, SIS)] == (1, 1)


def test_conteo_sin_errores_devuelve_ceros():
    res = ref.contar(_unidos([(SW, (), SW), (HW, (), HW)]))
    assert res.total_errores == 0
    assert res.total_laxos == 0
    assert res.por_frontera == {}


def test_conteo_todos_los_errores_laxos():
    res = ref.contar(_unidos([(HW, (SW,), SW), (SEG, (BD,), BD)]))
    assert (res.total_errores, res.total_laxos) == (2, 2)


def test_conteo_ningun_error_laxo():
    res = ref.contar(_unidos([(HW, (), SW), (SEG, (), BD)]))
    assert (res.total_errores, res.total_laxos) == (2, 0)


def test_prediccion_fuera_de_clases_es_error_no_laxo():
    res = ref.contar(_unidos([(HW, (), "Otro sector")]))
    assert (res.total_errores, res.total_laxos) == (1, 0)


def test_identidad_de_exactitud_laxa():
    res = ref.contar(_unidos([(HW, (SW,), SW), (SW, (), SW), (SIS, (), HW)]))
    assert res.aciertos_estrictos == 1
    assert res.aciertos_laxos_totales == 2


# --- agrupamiento -------------------------------------------------------------


def test_agrupar_deja_las_principales_y_suma_el_resto():
    por_frontera = {
        ref.frontera(HW, SW): (14, 5),
        ref.frontera(SW, SIS): (12, 10),
        ref.frontera(SEG, SW): (11, 8),
        ref.frontera(BD, SIS): (10, 6),
        ref.frontera(SEG, SIS): (6, 3),
    }
    filas = ref.agrupar(por_frontera)
    assert filas == [
        ("Hardware-Software", 14, 5),
        ("Sistemas-Software", 12, 10),
        ("Seguridad-Software", 11, 8),
        ("Demás fronteras", 16, 9),
    ]


def test_agrupar_sin_demas_fronteras_devuelve_cero():
    filas = ref.agrupar({ref.frontera(HW, SW): (2, 1)})
    assert filas[-1] == ("Demás fronteras", 0, 0)
    assert filas[0] == ("Hardware-Software", 2, 1)


# --- porcentaje --------------------------------------------------------------


@pytest.mark.parametrize(
    "n, d, esperado",
    [
        (9, 16, "56,3"),  # 56,25 sube (mitad hacia arriba)
        (32, 53, "60,4"),
        (21, 53, "39,6"),
        (14, 53, "26,4"),
        (0, 5, "0,0"),
        (5, 5, "100,0"),
    ],
)
def test_porcentaje_con_un_decimal_mitad_hacia_arriba(n, d, esperado):
    assert ref.porcentaje(n, d) == esperado


# --- salida Markdown ---------------------------------------------------------


def _resultado_demo():
    unidos = _unidos([(HW, (SW,), SW), (HW, (), SW), (SW, (), SW)])
    return unidos, ref.contar(unidos)


def test_formato_es_deterministico():
    unidos, res = _resultado_demo()
    assert ref.formatear(res, unidos, ("C0",)) == ref.formatear(res, unidos, ("C0",))


def test_formato_incluye_cifras_y_caso_literal():
    unidos, res = _resultado_demo()
    salida = ref.formatear(res, unidos, ("C0",))
    assert "Errores estrictos: 2 de 3" in salida
    assert "Aciertos laxos entre los errores: 1 de 2 (50,0 %)" in salida
    assert "Hardware-Software | 2 | 1 |" in salida
    assert "C0" in salida and "descripcion C0" in salida


# --- main --------------------------------------------------------------------


def _escribir_entradas(tmp_path):
    casos = [
        {**_caso("A", HW, (SW,)), "canal_origen": "web"},
        {**_caso("B", SW), "canal_origen": "web"},
    ]
    corpus = (json.dumps({"casos": casos}, ensure_ascii=False) + "\n").encode("utf-8")
    ruta_corpus = tmp_path / "corpus.json"
    ruta_corpus.write_bytes(corpus.replace(b"\n", b"\r\n"))
    hash_corpus = hashlib.sha256(corpus).hexdigest()
    evidencia = {
        "cache_meta": {
            "corpus_hash": hash_corpus,
            "corpus_count": 2,
            "classifier_version": "hybrid-v3",
        },
        "predictions": [_pred("A", SW), _pred("B", SW)],
    }
    ruta_evidencia = tmp_path / "evidencia.json"
    ruta_evidencia.write_text(json.dumps(evidencia, ensure_ascii=False), encoding="utf-8")
    return ruta_corpus, ruta_evidencia, hash_corpus


def _argv(corpus, evidencia, hash_esperado):
    return [
        "--corpus", str(corpus),
        "--evidencia", str(evidencia),
        "--hash-esperado", hash_esperado,
        "--casos-esperados", "2",
        "--casos", "A",
    ]


def test_main_devuelve_cero_e_imprime_las_cifras(tmp_path, capsys):
    corpus, evidencia, hash_corpus = _escribir_entradas(tmp_path)
    codigo = ref.main(_argv(corpus, evidencia, hash_corpus))
    salida = capsys.readouterr().out
    assert codigo == 0
    assert "Errores estrictos: 1 de 2" in salida


def test_main_falla_sin_imprimir_cifras_si_el_hash_no_coincide(tmp_path, capsys):
    corpus, evidencia, _ = _escribir_entradas(tmp_path)
    codigo = ref.main(_argv(corpus, evidencia, "0" * 64))
    capturado = capsys.readouterr()
    assert codigo != 0
    assert "Errores estrictos" not in capturado.out
    assert capturado.err


# --- caracterizacion sobre el corpus y la evidencia reales --------------------

_CORPUS_REAL = ref.RAIZ / ref.RUTA_CORPUS
_EVIDENCIA_REAL = ref.RAIZ / ref.RUTA_EVIDENCIA


@pytest.fixture(scope="module")
def real():
    unidos = ref.cargar_y_unir(_CORPUS_REAL, _EVIDENCIA_REAL)
    return unidos, ref.contar(unidos)


@pytest.mark.skipif(
    not (_CORPUS_REAL.exists() and _EVIDENCIA_REAL.exists()),
    reason="faltan el corpus o la evidencia reales",
)
class TestCaracterizacionReal:
    def test_totales(self, real):
        _, res = real
        assert (res.total_casos, res.total_errores, res.total_laxos) == (200, 53, 32)

    def test_por_frontera_agrupado(self, real):
        _, res = real
        assert ref.agrupar(res.por_frontera) == [
            ("Hardware-Software", 14, 5),
            ("Sistemas-Software", 12, 10),
            ("Seguridad-Software", 11, 8),
            ("Demás fronteras", 16, 9),
        ]

    def test_identidad_147_mas_32_igual_179(self, real):
        _, res = real
        assert res.aciertos_estrictos == 147
        assert res.aciertos_laxos_totales == 179

    def test_casos_ilustrativos(self, real):
        unidos, _ = real
        por_id = {u["id"]: u for u in unidos}
        r001, r032, r015 = (por_id[c] for c in ("R001", "R032", "R015"))
        assert r001["descripcion"] == "No puede ingresar al sistema principal"
        assert (r001["sector_asignado"], r001["sector_predicho"]) == (SEG, SW)
        assert (r001["confianza"], r001["etapa"]) == (0.95, "gemini")
        assert r032["descripcion"] == (
            "Su PC se reinicia a cada rato, sospecha que son los cables de la computadora."
        )
        assert (r032["sector_asignado"], r032["sector_predicho"]) == (SW, HW)
        assert r032["confianza"] == 0.5
        assert r015["descripcion"] == (
            "No le salen correos por flujo del sistema principal y no le llegan las instancias"
        )
        assert (r015["sector_asignado"], r015["sector_predicho"]) == (SIS, SW)
        assert (r015["confianza"], r015["etapa"]) == (0.85, "gemini")
        for caso in (r001, r032, r015):
            assert caso["sector_predicho"] in caso["sectores_adicionales"]
