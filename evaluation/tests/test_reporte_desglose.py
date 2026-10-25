"""
Tests de las secciones aditivas del reporte (c-131, D7).

Strict TDD: cada seccion nueva (exactitud laxa, exactitud por etapa, por canal,
calibracion y procedencia) se escribe primero como test rojo.

Salvo el test de caracterizacion 5.1 (`test_reporte_conserva_lineas_previas`,
guarda del caracter aditivo, verde desde el inicio por diseno), todos los demas
nacen en rojo.
"""

from __future__ import annotations

import pathlib
from typing import List, Optional

import pytest

from evaluation.corpus import CasoEvaluacion
from evaluation.run_evaluation import Prediccion

FIXTURES = pathlib.Path(__file__).parent / "fixtures"
REPORTE_PREVIO = FIXTURES / "report_pre_c126.md"

SIS = "Sistemas"
SW = "Soporte Tecnico Software"
HW = "Soporte Tecnico Hardware"
BD = "Bases de Datos"
SEG = "Seguridad Informatica"


# ---------------------------------------------------------------------------
# Helpers de datos sinteticos
# ---------------------------------------------------------------------------
def _caso(
    caso_id: str,
    canal: Optional[str],
    asignado: str,
    adicionales: Optional[List[str]] = None,
) -> CasoEvaluacion:
    return CasoEvaluacion(
        id=caso_id,
        descripcion=f"descripcion {caso_id}",
        sector_asignado=asignado,
        sectores_adicionales=list(adicionales or []),
        canal_origen=canal,
        tiempo_manual_s=30.0,
        tiempo_automatizado_s=10.0,
    )


def _pred(
    caso: CasoEvaluacion,
    predicho: str,
    confianza: float,
    etapa: str,
    adicionales: Optional[List[str]] = None,
) -> Prediccion:
    return Prediccion(
        caso_id=caso.id,
        descripcion=caso.descripcion,
        sector_asignado=caso.sector_asignado,
        sector_predicho=predicho,
        confianza=confianza,
        etapa=etapa,
        sectores_adicionales=list(adicionales or []),
    )


def _predicciones_de_caracterizacion(corpus: List[CasoEvaluacion]) -> List[Prediccion]:
    """
    Predicciones deterministas mixtas sobre el fixture de 9 casos.

    Con el codigo previo a c-131 generaron `fixtures/report_pre_c126.md`
    (`generar_reporte(predicciones, corpus, ruta)` sin `corpus_hash`).
    """
    otro = {SEG: SW, HW: SIS, SW: HW, BD: SEG, SIS: BD}
    predicciones: List[Prediccion] = []
    for indice, caso in enumerate(corpus):
        predicho = caso.sector_asignado if indice % 3 else otro[caso.sector_asignado]
        etapa = "deterministic" if indice % 2 == 0 else "gemini"
        confianza = [0.0, 0.5, 0.75, 0.85, 0.9, 0.95, 0.98, 0.5, 0.9][indice]
        predicciones.append(_pred(caso, predicho, confianza, etapa))
    return predicciones


@pytest.fixture
def corpus_fixture(corpus_fixture_path):
    from evaluation.corpus import cargar_corpus

    return cargar_corpus(corpus_fixture_path)


def _generar(corpus, predicciones, tmp_path, **kwargs) -> str:
    from evaluation.run_evaluation import generar_reporte

    return generar_reporte(predicciones, corpus, tmp_path / "report.md", **kwargs)


# ---------------------------------------------------------------------------
# 5.1 Safety net de caracterizacion: el reporte es ADITIVO
# ---------------------------------------------------------------------------
def test_reporte_conserva_lineas_previas(corpus_fixture, tmp_path):
    """Toda linea del reporte previo a c-131 sigue presente y en el mismo orden relativo."""
    previas = REPORTE_PREVIO.read_text(encoding="utf-8").splitlines()
    nuevo = _generar(
        corpus_fixture, _predicciones_de_caracterizacion(corpus_fixture), tmp_path
    ).splitlines()

    posicion = 0
    for linea in previas:
        try:
            posicion = nuevo.index(linea, posicion) + 1
        except ValueError:  # pragma: no cover - solo en regresion
            pytest.fail(f"Linea previa ausente o fuera de orden: {linea!r}")


# ---------------------------------------------------------------------------
# 5.2 / 5.3 Exactitud laxa en la seccion "Exactitud"
# ---------------------------------------------------------------------------
def _corpus_laxa():
    """
    Seis casos del canal 'correo'. Estricto 2/6, pertenencia 4/6, laxo 3/6:
    L2 es solo laxo (principal en los adicionales de verdad); L3 y L4 son solo
    de pertenencia (asignado dentro de los adicionales predichos).
    """
    casos = [
        _caso("L1", "correo", SIS),
        _caso("L2", "correo", SW, [HW]),
        _caso("L3", "correo", BD),
        _caso("L4", "correo", HW),
        _caso("L5", "correo", SEG),
        _caso("L6", "correo", SIS),
    ]
    predicciones = [
        _pred(casos[0], SIS, 0.95, "gemini"),
        _pred(casos[1], HW, 0.90, "gemini"),
        _pred(casos[2], SEG, 0.85, "gemini", adicionales=[BD]),
        _pred(casos[3], SW, 0.85, "gemini", adicionales=[HW]),
        _pred(casos[4], SEG, 0.95, "gemini"),
        _pred(casos[5], BD, 0.90, "gemini"),
    ]
    return casos, predicciones


def test_reporte_emite_exactitud_laxa_con_wilson_despues_de_la_pertenencia(tmp_path):
    casos, predicciones = _corpus_laxa()
    lineas = _generar(casos, predicciones, tmp_path).splitlines()

    assert "- **Exactitud (laxa):** 0.5000 (50.0%)" in lineas
    assert "- **Aciertos (laxos):** 3 / 6" in lineas
    assert "- **IC Wilson 95% (laxo):** [0.1876, 0.8124]" in lineas
    # se conservan las lineas de estricta y de pertenencia con sus valores propios
    assert "- **Aciertos (estrictos):** 2 / 6" in lineas
    assert "- **Aciertos (pertenencia):** 4 / 6" in lineas
    assert "- **IC Wilson 95% (pertenencia):** [0.3000, 0.9032]" in lineas
    # la laxa va despues de las lineas de pertenencia
    assert lineas.index("- **Aciertos (laxos):** 3 / 6") > lineas.index(
        "- **IC Wilson 95% (pertenencia):** [0.3000, 0.9032]"
    )
    assert lineas.index("- **IC Wilson 95% (laxo):** [0.1876, 0.8124]") < lineas.index(
        "## Matriz de Confusión (primaria 5x5)"
    )


def test_reporte_enuncia_la_definicion_laxa_separada_de_la_pertenencia(tmp_path):
    casos, predicciones = _corpus_laxa()
    lineas = _generar(casos, predicciones, tmp_path).splitlines()

    inicio = [i for i, linea in enumerate(lineas) if linea.startswith("Exactitud laxa")]
    assert len(inicio) == 1
    parrafo = []
    for linea in lineas[inicio[0]:]:
        if not linea:
            break
        parrafo.append(linea)
    texto = " ".join(parrafo)
    assert "conjunto de verdad" in texto
    assert "sectores_adicionales" in texto
    assert "pertenencia" in texto  # la distingue explicitamente de la pertenencia
    # la definicion de pertenencia previa no se toca
    assert "pertenencia del sector asignado al conjunto predicho." in lineas


def test_laxa_nunca_es_menor_que_la_estricta_en_el_reporte(corpus_fixture, tmp_path):
    lineas = _generar(
        corpus_fixture, _predicciones_de_caracterizacion(corpus_fixture), tmp_path
    ).splitlines()

    def aciertos(prefijo: str) -> int:
        linea = next(l for l in lineas if l.startswith(prefijo))
        return int(linea.split(":**")[1].split("/")[0])

    assert aciertos("- **Aciertos (laxos)") >= aciertos("- **Aciertos (estrictos)")
    assert aciertos("- **Aciertos (laxos)") == 7  # id 7 acierta por laxa (BD en la verdad)
    assert aciertos("- **Aciertos (estrictos)") == 6


# ---------------------------------------------------------------------------
# 5.4 / 5.5 Seccion "Exactitud por etapa del pipeline"
# ---------------------------------------------------------------------------
def _seccion(reporte: str, encabezado: str) -> List[str]:
    """Lineas de la seccion `encabezado`, hasta el siguiente encabezado (`#`) o el pie `---`."""
    lineas = reporte.splitlines()
    inicio = lineas.index(encabezado)
    fin = next(
        (j for j in range(inicio + 1, len(lineas))
         if lineas[j].startswith("#") or lineas[j] == "---"),
        len(lineas),
    )
    return lineas[inicio:fin]


def _con_etapas(predicciones, etapas):
    for prediccion, etapa in zip(predicciones, etapas):
        prediccion.etapa = etapa
    return predicciones


def test_seccion_exactitud_por_etapa_lista_las_tres_etapas_en_orden(tmp_path):
    casos, predicciones = _corpus_laxa()
    _con_etapas(
        predicciones,
        ["deterministic", "deterministic", "gemini", "gemini", "gemini", "deterministic"],
    )
    reporte = _generar(casos, predicciones, tmp_path)
    seccion = _seccion(reporte, "## Exactitud por etapa del pipeline")

    filas = [l for l in seccion if l.startswith("| deterministic") or l.startswith("| gemini")
             or l.startswith("| fallback")]
    assert [f.split("|")[1].strip() for f in filas] == ["deterministic", "gemini", "fallback"]
    assert filas[0] == (
        "| deterministic | 3 | 1 | 0.3333 | [0.0615, 0.7923] "
        "| 2 | 0.6667 | [0.2077, 0.9385] |"
    )
    assert filas[1] == (
        "| gemini | 3 | 1 | 0.3333 | [0.0615, 0.7923] "
        "| 1 | 0.3333 | [0.0615, 0.7923] |"
    )


def test_seccion_exactitud_por_etapa_declara_fallback_sin_casos_no_aplicable(tmp_path):
    casos, predicciones = _corpus_laxa()
    _con_etapas(predicciones, ["deterministic"] * 3 + ["gemini"] * 3)
    reporte = _generar(casos, predicciones, tmp_path)
    seccion = _seccion(reporte, "## Exactitud por etapa del pipeline")

    fila = next(l for l in seccion if l.startswith("| fallback"))
    assert fila == (
        "| fallback | 0 | 0 | no aplicable | no aplicable | 0 | no aplicable | no aplicable |"
    )


def test_seccion_exactitud_por_etapa_esta_antes_de_tiempos(tmp_path):
    casos, predicciones = _corpus_laxa()
    lineas = _generar(casos, predicciones, tmp_path).splitlines()

    assert lineas.index("## Exactitud por etapa del pipeline") < lineas.index("## Tiempos")
    assert lineas.index("## Exactitud por etapa del pipeline") > lineas.index(
        "## Métricas de conjunto"
    )


# ---------------------------------------------------------------------------
# 5.6 / 5.7 Seccion "Exactitud por canal de origen" y validacion de alineacion
# ---------------------------------------------------------------------------
def _corpus_tres_canales():
    """
    Siete casos: correo 3 y llamada 3 (empate por conteo: orden alfabetico),
    formulario 1. Estricta y laxa difieren solo en 'llamada' (C2).
    """
    casos = [
        _caso("C1", "llamada", SIS),
        _caso("C2", "llamada", SW, [HW]),
        _caso("C3", "llamada", BD),
        _caso("C4", "correo", SEG),
        _caso("C5", "correo", HW),
        _caso("C6", "correo", SW),
        _caso("C7", "formulario", SIS),
    ]
    predicciones = [
        _pred(casos[0], SIS, 0.0, "deterministic"),
        _pred(casos[1], HW, 0.5, "deterministic"),
        _pred(casos[2], BD, 0.9, "gemini"),
        _pred(casos[3], SIS, 0.85, "gemini"),
        _pred(casos[4], HW, 0.75, "deterministic"),
        _pred(casos[5], SW, 0.95, "gemini"),
        _pred(casos[6], SIS, 0.0, "deterministic"),
    ]
    return casos, predicciones


def test_seccion_por_canal_lista_canales_con_composicion_y_wilson(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    reporte = _generar(casos, predicciones, tmp_path)
    seccion = _seccion(reporte, "## Exactitud por canal de origen")

    filas = [l for l in seccion if l.startswith("| ") and not l.startswith("| Canal")
             and not l.startswith("|---")]
    assert [f.split("|")[1].strip() for f in filas] == ["correo", "llamada", "formulario"]
    assert filas[0] == (
        "| correo | 3 | 1 | 2 | 0 | 2 | 0.6667 | [0.2077, 0.9385] "
        "| 2 | 0.6667 | [0.2077, 0.9385] |"
    )
    assert filas[1] == (
        "| llamada | 3 | 2 | 1 | 0 | 2 | 0.6667 | [0.2077, 0.9385] "
        "| 3 | 1.0000 | [0.4385, 1.0000] |"
    )
    assert filas[2] == (
        "| formulario | 1 | 1 | 0 | 0 | 1 | 1.0000 | [0.2065, 1.0000] "
        "| 1 | 1.0000 | [0.2065, 1.0000] |"
    )


def test_seccion_por_canal_usa_el_mismo_orden_que_el_desglose_de_tiempos(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    reporte = _generar(casos, predicciones, tmp_path)

    def canales(encabezado: str) -> List[str]:
        return [
            l.split("|")[1].strip()
            for l in _seccion(reporte, encabezado)
            if l.startswith("| ") and not l.startswith("| Canal") and not l.startswith("|---")
        ]

    por_canal = canales("## Exactitud por canal de origen")
    assert por_canal == canales("### Desglose por canal")
    assert por_canal == ["correo", "llamada", "formulario"]


def test_alineacion_distinta_entre_prediccion_y_corpus_falla_con_posicion_e_ids(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    predicciones[1].caso_id = "OTRO"
    ruta = tmp_path / "report.md"

    from evaluation.run_evaluation import generar_reporte

    with pytest.raises(ValueError) as error:
        generar_reporte(predicciones, casos, ruta)

    mensaje = str(error.value)
    assert "1" in mensaje and "OTRO" in mensaje and "C2" in mensaje
    assert not ruta.exists()


def test_alineacion_correcta_no_falla(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    assert "## Exactitud por canal de origen" in _generar(casos, predicciones, tmp_path)


# ---------------------------------------------------------------------------
# 5.8 / 5.9 Seccion "Calibracion de la confianza"
# ---------------------------------------------------------------------------
def _corpus_composicion_del_design():
    """
    200 casos con la composicion por etapa y banda de `design.md` (Context):
    131 deterministicos (confianza 0 / 0,5 / 0,75 / 1,0) y 69 de Gemini
    (0,85 / 0,90 / 0,95 / 0,98); todos asignados a 'Sistemas'.
    """
    grupos = [
        ("deterministic", 0.0, 98, 75),
        ("deterministic", 0.5, 26, 19),
        ("deterministic", 0.75, 6, 2),
        ("deterministic", 1.0, 1, 1),
        ("gemini", 0.85, 24, 18),
        ("gemini", 0.90, 7, 4),
        ("gemini", 0.95, 20, 15),
        ("gemini", 0.98, 18, 13),
    ]
    casos, predicciones = [], []
    for etapa, confianza, total, aciertos in grupos:
        for i in range(total):
            caso = _caso(f"K{len(casos):03d}", "correo", SIS)
            casos.append(caso)
            predicciones.append(
                _pred(caso, SIS if i < aciertos else BD, confianza, etapa)
            )
    return casos, predicciones


def _filas_de(seccion: List[str]) -> List[str]:
    return [l for l in seccion if l.startswith("| ") and not l.startswith("|---")]


def test_calibracion_bandas_globales_reproducen_la_tabla_canonica(tmp_path):
    casos, predicciones = _corpus_composicion_del_design()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "### Bandas de confianza (global)"))

    assert filas[1:] == [
        "| [0.00, 0.50) | 98 | 75 | 0.7653 |",
        "| [0.50, 0.70) | 26 | 19 | 0.7308 |",
        "| [0.70, 0.85) | 6 | 2 | 0.3333 |",
        "| [0.85, 0.95) | 31 | 22 | 0.7097 |",
        "| [0.95, 1.00] | 39 | 29 | 0.7436 |",
    ]


def test_calibracion_contingencia_en_070_global_y_por_etapa(tmp_path):
    casos, predicciones = _corpus_composicion_del_design()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "### Contingencia en el umbral 0,70"))

    assert filas[1:] == [
        "| Global | 76 | 53 | 0.6974 | 124 | 94 | 0.7581 |",
        "| deterministic | 7 | 3 | 0.4286 | 124 | 94 | 0.7581 |",
        "| gemini | 69 | 50 | 0.7246 | 0 | 0 | no aplicable |",
        "| fallback | 0 | 0 | no aplicable | 0 | 0 | no aplicable |",
    ]


def test_calibracion_tramo_alta_confianza_desde_090_global_y_por_etapa(tmp_path):
    casos, predicciones = _corpus_composicion_del_design()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "### Tramo de confianza >= 0,90"))

    assert filas[1:] == [
        "| Global | 46 | 13 |",
        "| deterministic | 1 | 0 |",
        "| gemini | 45 | 13 |",
        "| fallback | 0 | 0 |",
    ]


def test_calibracion_bandas_por_etapa_con_wilson_y_no_aplicable_en_las_vacias(tmp_path):
    casos, predicciones = _corpus_composicion_del_design()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "### Bandas de confianza por etapa"))[1:]

    assert "| gemini | [0.85, 0.95) | 31 | 22 | 0.7097 | [0.5341, 0.8390] |" in filas
    assert "| gemini | [0.95, 1.00] | 38 | 28 | 0.7368 | [0.5799, 0.8503] |" in filas
    assert "| deterministic | [0.70, 0.85) | 6 | 2 | 0.3333 | [0.0968, 0.7000] |" in filas
    assert "| deterministic | [0.85, 0.95) | 0 | 0 | no aplicable | no aplicable |" in filas
    assert "| gemini | [0.00, 0.50) | 0 | 0 | no aplicable | no aplicable |" in filas
    # fallback: las cinco bandas, todas vacias
    assert sum(1 for f in filas if f.startswith("| fallback |")) == 5
    assert all("no aplicable | no aplicable |" in f for f in filas if f.startswith("| fallback |"))
    # 3 etapas x 5 bandas
    assert len(filas) == 15


def test_calibracion_distribucion_de_valores_por_etapa(tmp_path):
    casos, predicciones = _corpus_composicion_del_design()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "### Distribución de valores de confianza por etapa"))[1:]

    assert filas == [
        "| deterministic | 0.0000 | 98 | 75 |",
        "| deterministic | 0.5000 | 26 | 19 |",
        "| deterministic | 0.7500 | 6 | 2 |",
        "| deterministic | 1.0000 | 1 | 1 |",
        "| gemini | 0.8500 | 24 | 18 |",
        "| gemini | 0.9000 | 7 | 4 |",
        "| gemini | 0.9500 | 20 | 15 |",
        "| gemini | 0.9800 | 18 | 13 |",
        "| fallback | no aplicable | 0 | 0 |",
    ]


def test_calibracion_esta_entre_el_desglose_por_canal_y_tiempos(tmp_path):
    casos, predicciones = _corpus_laxa()
    lineas = _generar(casos, predicciones, tmp_path).splitlines()

    assert (
        lineas.index("## Exactitud por canal de origen")
        < lineas.index("## Calibración de la confianza")
        < lineas.index("## Tiempos")
    )


# ---------------------------------------------------------------------------
# 5.10 / 5.11 Procedencia de las predicciones
# ---------------------------------------------------------------------------
META = {
    "corpus_hash": "1fd17d7e",
    "corpus_count": 6,
    "classifier_version": "hybrid-v3",
    "generated_at": "2026-10-07T22:22:01.947873+00:00",
}


def test_reporte_con_procedencia_declara_version_y_fecha(tmp_path):
    casos, predicciones = _corpus_laxa()
    lineas = _generar(casos, predicciones, tmp_path, procedencia=META).splitlines()

    linea = next(l for l in lineas if l.startswith("**Procedencia de las predicciones:**"))
    assert "`hybrid-v3`" in linea
    assert "`2026-10-07T22:22:01.947873+00:00`" in linea
    assert lineas.index(linea) > lineas.index("**Total de casos evaluados:** 6")
    assert lineas.index(linea) < lineas.index("## Etapas del pipeline")


@pytest.mark.parametrize("procedencia", [None, {}])
def test_reporte_sin_procedencia_omite_la_linea_y_no_cambia_el_resto(tmp_path, procedencia):
    casos, predicciones = _corpus_laxa()
    con = _generar(casos, predicciones, tmp_path, procedencia=META).splitlines()
    sin = _generar(casos, predicciones, tmp_path, procedencia=procedencia).splitlines()

    assert not any("Procedencia" in l for l in sin)
    # con procedencia, el reporte solo agrega la linea y un separador en blanco
    indice = next(i for i, l in enumerate(con) if l.startswith("**Procedencia"))
    assert con[indice - 1] == ""
    assert con[: indice - 1] + con[indice + 1 :] == sin
    # las secciones nuevas se generan igual
    assert "## Calibración de la confianza" in sin


def test_cargar_cache_meta_devuelve_el_dict_del_archivo(tmp_path):
    import json

    from evaluation.run_evaluation import cargar_cache_meta

    ruta = tmp_path / "predicciones.json"
    ruta.write_text(json.dumps({"cache_meta": META, "predictions": []}), encoding="utf-8")

    assert cargar_cache_meta(ruta) == META


@pytest.mark.parametrize(
    "contenido",
    [None, "{no es json", "[]", '{"predictions": []}', '{"cache_meta": []}'],
    ids=["archivo-ausente", "json-malformado", "arreglo-plano", "sin-cache-meta", "meta-no-dict"],
)
def test_cargar_cache_meta_devuelve_none_si_no_hay_metadata_valida(tmp_path, contenido):
    from evaluation.run_evaluation import cargar_cache_meta

    ruta = tmp_path / "predicciones.json"
    if contenido is not None:
        ruta.write_text(contenido, encoding="utf-8")

    assert cargar_cache_meta(ruta) is None


async def _spy(corpus_fixture_path):
    from evaluation.corpus import cargar_corpus
    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier

    class SpyClassifier(FakeClassifier):
        call_count = 0

        async def classify(self, descripcion):
            type(self).call_count += 1
            return await super().classify(descripcion)

    SpyClassifier.call_count = 0
    casos = cargar_corpus(corpus_fixture_path)
    return SpyClassifier(
        predicciones={
            caso.descripcion: ClasificacionResultFake(
                sector_predicho=caso.sector_asignado,
                sectores_adicionales=list(caso.sectores_adicionales),
                confianza=0.95,
                etapa="gemini",
            )
            for caso in casos
        }
    )


async def test_corrida_nueva_declara_la_procedencia_recien_construida(
    corpus_fixture_path, tmp_path
):
    import json
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    corpus = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus)
    predicciones = tmp_path / "predicciones.json"
    reporte = tmp_path / "report.md"

    spy = await _spy(corpus_fixture_path)
    await main_con_corpus_real(
        corpus_path=corpus, classifier=spy, report_path=reporte, predicciones_path=predicciones
    )

    meta = json.loads(predicciones.read_text(encoding="utf-8"))["cache_meta"]
    texto = reporte.read_text(encoding="utf-8")
    assert spy.call_count > 0
    assert f"`{meta['classifier_version']}`" in texto
    assert f"`{meta['generated_at']}`" in texto


async def test_cache_hit_declara_la_procedencia_leida_del_archivo_sin_clasificar(
    corpus_fixture_path, tmp_path
):
    import json
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    corpus = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus)
    predicciones = tmp_path / "predicciones.json"
    reporte = tmp_path / "report.md"

    spy = await _spy(corpus_fixture_path)
    await main_con_corpus_real(
        corpus_path=corpus, classifier=spy, report_path=reporte, predicciones_path=predicciones
    )
    # Se fija una fecha de generacion distinta en el archivo de cache para probar que
    # el reporte la lee del archivo y no de la corrida actual.
    datos = json.loads(predicciones.read_text(encoding="utf-8"))
    datos["cache_meta"]["generated_at"] = "2026-10-07T22:22:01+00:00"
    predicciones.write_text(json.dumps(datos), encoding="utf-8")

    spy.call_count = 0
    reporte.unlink()
    await main_con_corpus_real(
        corpus_path=corpus, classifier=spy, report_path=reporte, predicciones_path=predicciones
    )

    texto = reporte.read_text(encoding="utf-8")
    assert spy.call_count == 0
    assert "`2026-10-07T22:22:01+00:00`" in texto


# ---------------------------------------------------------------------------
# 5.12 TRIANGULATE: otro corpus, etapa desconocida, canal nulo, reproducibilidad
# ---------------------------------------------------------------------------
def test_dos_llamadas_consecutivas_producen_secciones_identicas(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    primero = _generar(casos, predicciones, tmp_path)
    segundo = _generar(casos, predicciones, tmp_path)

    assert primero == segundo
    assert (tmp_path / "report.md").read_text(encoding="utf-8") == segundo


def test_etapa_desconocida_se_cuenta_como_fallback_y_las_etapas_suman_el_total(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    predicciones[0].etapa = "otra-etapa"
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "## Exactitud por etapa del pipeline"))[1:]

    por_etapa = {f.split("|")[1].strip(): f.split("|") for f in filas}
    assert por_etapa["fallback"][2].strip() == "1"
    assert sum(int(f[2]) for f in por_etapa.values()) == len(casos)


def test_canal_nulo_se_rotula_sin_canal_y_el_desglose_suma_el_total(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    casos[6].canal_origen = None
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "## Exactitud por canal de origen"))[1:]

    assert [f.split("|")[1].strip() for f in filas] == ["correo", "llamada", "sin canal"]
    assert sum(int(f.split("|")[2]) for f in filas) == len(casos)


def test_las_etapas_por_canal_suman_los_casos_de_cada_canal(tmp_path):
    casos, predicciones = _corpus_tres_canales()
    reporte = _generar(casos, predicciones, tmp_path)
    filas = _filas_de(_seccion(reporte, "## Exactitud por canal de origen"))[1:]

    for fila in filas:
        celdas = [c.strip() for c in fila.split("|")]
        assert int(celdas[2]) == int(celdas[3]) + int(celdas[4]) + int(celdas[5])


def test_segundo_corpus_con_banda_vacia_declara_no_aplicable_en_la_banda(tmp_path):
    """Solo hay confianzas altas: las bandas bajas globales quedan en 0 casos."""
    casos, predicciones = _corpus_laxa()
    reporte = _generar(casos, predicciones, tmp_path)
    globales = _filas_de(_seccion(reporte, "### Bandas de confianza (global)"))[1:]

    assert globales[0] == "| [0.00, 0.50) | 0 | 0 | no aplicable |"
    assert globales[1] == "| [0.50, 0.70) | 0 | 0 | no aplicable |"
    assert globales[3] == "| [0.85, 0.95) | 4 | 0 | 0.0000 |"  # L2, L3, L4 y L6: todos errores
    assert globales[4] == "| [0.95, 1.00] | 2 | 2 | 1.0000 |"  # L1 y L5


def test_cantidad_distinta_de_predicciones_y_casos_falla_sin_escribir_el_reporte(tmp_path):
    from evaluation.run_evaluation import generar_reporte

    casos, predicciones = _corpus_tres_canales()
    ruta = tmp_path / "report.md"

    with pytest.raises(ValueError, match="7 casos|6 predicciones"):
        generar_reporte(predicciones[:-1], casos, ruta)

    assert not ruta.exists()
