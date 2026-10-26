"""
Pruebas del modulo de sensibilidad frente a los ajustes del clasificador (c-142).

Se construye por TDD estricto (bloques 3 a 6 y 8 de las tareas): cada seccion
corresponde a un ciclo RED -> GREEN -> TRIANGULATE -> REFACTOR. Sin Gemini, sin
red y sin escribir fuera de `tmp_path`.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

import pytest

import evaluation.sensibilidad_ajustes as sa
from evaluation.corpus import CasoEvaluacion, cargar_corpus
from evaluation.deterministic_measurement import PrediccionCacheada, recolectar_observaciones
from evaluation.metrics import intervalo_wilson
from evaluation.run_evaluation import PaidRunNotConfirmedError, Prediccion

FUENTE_ASIGNACION_ANOTADA = r'''"""Vocabulario de prueba."""
from typing import Final

from app.constants import SECTOR_SISTEMAS

KEYWORD_MAP: Final[dict[str, list[str]]] = {
    "Sistemas": [r"\bservidor\b", r"red"],
    "Bases de Datos": [r"\bbackup\b"],
    "Seguridad Informatica": [],
}
'''


# ---------------------------------------------------------------------------
# Bloque 3 - keyword_map_desde_fuente (D6)
# ---------------------------------------------------------------------------
def test_keyword_map_desde_fuente_anotada_devuelve_dict_con_orden_de_claves():
    mapa = sa.keyword_map_desde_fuente(FUENTE_ASIGNACION_ANOTADA)

    assert list(mapa) == ["Sistemas", "Bases de Datos", "Seguridad Informatica"]
    assert mapa["Sistemas"] == [r"\bservidor\b", "red"]
    assert mapa["Seguridad Informatica"] == []


def test_keyword_map_desde_fuente_asignacion_simple():
    mapa = sa.keyword_map_desde_fuente('KEYWORD_MAP = {"Sistemas": ["a"], "Bases de Datos": ["b", "c"]}\n')

    assert mapa == {"Sistemas": ["a"], "Bases de Datos": ["b", "c"]}
    assert list(mapa) == ["Sistemas", "Bases de Datos"]


def test_keyword_map_desde_fuente_ignora_otras_asignaciones_y_no_ejecuta_el_modulo():
    fuente = 'OTRO = {"x": ["y"]}\nraise RuntimeError("no debe ejecutarse")\nKEYWORD_MAP = {"Sistemas": ["a"]}\n'

    assert sa.keyword_map_desde_fuente(fuente) == {"Sistemas": ["a"]}


def test_keyword_map_desde_fuente_sin_keyword_map_falla_con_mensaje_claro():
    with pytest.raises(ValueError, match="KEYWORD_MAP"):
        sa.keyword_map_desde_fuente("OTRO = {}\n")


def test_keyword_map_desde_fuente_valor_no_literal_falla():
    with pytest.raises(ValueError, match="literal"):
        sa.keyword_map_desde_fuente('KEYWORD_MAP = dict(Sistemas=["a"])\n')


def test_keyword_map_desde_fuente_con_error_de_sintaxis_falla_con_value_error():
    with pytest.raises(ValueError, match="sintaxis"):
        sa.keyword_map_desde_fuente("KEYWORD_MAP = {\n")


# ---------------------------------------------------------------------------
# Bloque 3 (tarea 3.5) - CARACTERIZACION de los artefactos versionados (D6).
# No conduce codigo de produccion: no sigue el ciclo RED/GREEN y asi se declara
# en la evidencia TDD. Verifica integridad y estructura de los datos historicos.
# ---------------------------------------------------------------------------

_REPO = pathlib.Path(__file__).resolve().parents[2]
_DATOS = _REPO / "evaluation" / "data" / "sensibilidad_ajustes"
_KEYWORDS_VIGENTE = _REPO / "App" / "Backend" / "app" / "classifiers" / "keywords.py"
_PROMPT_VIGENTE = _REPO / "docs" / "prompt_gemini.txt"
BLOB_KEYWORDS_PREVIO = "858f1c679c660e5e2a88a06544f2cdc3bfcb6328"
BLOB_PROMPT_PREVIO = "1daceb384f0a585941afaf2a9b87de8bffb31db8"
SECTORES = (
    "Seguridad Informatica",
    "Soporte Tecnico Hardware",
    "Soporte Tecnico Software",
    "Bases de Datos",
    "Sistemas",
)


def _sha256(ruta: pathlib.Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _normalizar_lf(texto: str) -> str:
    return texto.replace("\r\n", "\n")


def _quitar_reglas_de_frontera(prompt: str) -> str:
    """Helper de test: elimina el bloque REGLAS DE FRONTERA del prompt vigente."""
    prompt = _normalizar_lf(prompt)
    inicio = prompt.index("REGLAS DE FRONTERA\n")
    fin = prompt.index("FORMATO DE RESPUESTA\n")
    return prompt[:inicio] + prompt[fin:]


@pytest.mark.parametrize("nombre", ["keywords_pre_c71.json", "prompt_gemini_pre_c72.txt"])
def test_artefactos_historicos_coinciden_con_el_sha256_de_procedencia(nombre):
    procedencia = json.loads((_DATOS / "procedencia.json").read_text(encoding="utf-8"))

    assert procedencia["archivos"][nombre]["sha256"] == _sha256(_DATOS / nombre)


def test_procedencia_registra_commit_blob_fecha_y_comando_de_cada_archivo():
    procedencia = json.loads((_DATOS / "procedencia.json").read_text(encoding="utf-8"))

    assert set(procedencia["archivos"]) == {"keywords_pre_c71.json", "prompt_gemini_pre_c72.txt"}
    for datos in procedencia["archivos"].values():
        for campo in ("ruta_origen", "commit_de_extraccion", "blob", "comando_de_extraccion", "sha256"):
            assert datos[campo], campo
        assert "commit_de_extraccion_fecha" in datos
    assert procedencia["archivos"]["keywords_pre_c71.json"]["blob"] == BLOB_KEYWORDS_PREVIO
    assert procedencia["archivos"]["prompt_gemini_pre_c72.txt"]["blob"] == BLOB_PROMPT_PREVIO


def test_vocabulario_previo_tiene_las_cinco_claves_en_el_orden_del_vigente():
    v0 = json.loads((_DATOS / "keywords_pre_c71.json").read_text(encoding="utf-8"))
    v1 = sa.keyword_map_desde_fuente(_KEYWORDS_VIGENTE.read_text(encoding="utf-8"))

    assert list(v0) == list(v1)
    assert set(v0) == set(SECTORES)


def test_vocabulario_previo_esta_contenido_en_el_vigente_con_62_patrones_menos():
    v0 = json.loads((_DATOS / "keywords_pre_c71.json").read_text(encoding="utf-8"))
    v1 = sa.keyword_map_desde_fuente(_KEYWORDS_VIGENTE.read_text(encoding="utf-8"))

    for sector, patrones in v0.items():
        assert set(patrones) <= set(v1[sector]), sector
    assert sum(len(p) for p in v0.values()) == 89
    assert sum(len(p) for p in v1.values()) == 151
    assert {s: len(v1[s]) - len(v0[s]) for s in v0} == {
        "Seguridad Informatica": 12,
        "Soporte Tecnico Hardware": 20,
        "Soporte Tecnico Software": 17,
        "Bases de Datos": 3,
        "Sistemas": 10,
    }


def test_prompt_previo_es_el_vigente_sin_el_bloque_reglas_de_frontera():
    previo = (_DATOS / "prompt_gemini_pre_c72.txt").read_text(encoding="utf-8")
    vigente = _PROMPT_VIGENTE.read_text(encoding="utf-8")

    assert "REGLAS DE FRONTERA" not in previo
    assert "REGLAS DE FRONTERA" in vigente
    assert _normalizar_lf(previo) == _quitar_reglas_de_frontera(vigente)


def _blob_git(ruta_en_commit_o_blob: str):
    if shutil.which("git") is None:
        return None
    try:
        return subprocess.run(
            ["git", "-C", str(_REPO), "cat-file", "-p", ruta_en_commit_o_blob],
            check=True, capture_output=True,
        ).stdout
    except (subprocess.CalledProcessError, OSError):
        return None


@pytest.mark.skipif(
    _blob_git(BLOB_PROMPT_PREVIO) is None,
    reason="historial git no disponible (clon superficial o sin git)",
)
def test_prompt_previo_es_identico_al_blob_del_historial():
    assert (_DATOS / "prompt_gemini_pre_c72.txt").read_bytes() == _blob_git(BLOB_PROMPT_PREVIO)


@pytest.mark.skipif(
    _blob_git(BLOB_KEYWORDS_PREVIO) is None,
    reason="historial git no disponible (clon superficial o sin git)",
)
def test_vocabulario_previo_equivale_al_keyword_map_del_blob_del_historial():
    fuente = _blob_git(BLOB_KEYWORDS_PREVIO).decode("utf-8")
    v0 = json.loads((_DATOS / "keywords_pre_c71.json").read_text(encoding="utf-8"))

    assert sa.keyword_map_desde_fuente(fuente) == v0


# ---------------------------------------------------------------------------
# Bloque 4 - vocabulario inyectado (D5) y replica historica (D4)
# ---------------------------------------------------------------------------
@pytest.fixture
def entorno_backend(monkeypatch):
    """Entorno inerte para construir `Settings` del backend sin credenciales reales."""
    sa.asegurar_backend_en_path()
    pytest.importorskip("app.config.settings")
    for clave, valor in sa.ENTORNO_OFFLINE.items():
        monkeypatch.setenv(clave, valor)
    from app.config.settings import get_settings

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


MAPA_JUGUETE = {
    "Seguridad Informatica": [r"zzphishing"],
    "Soporte Tecnico Hardware": [r"zzimpresora"],
    "Soporte Tecnico Software": [r"zzoutlook"],
    "Bases de Datos": [r"zzbackup"],
    "Sistemas": [r"zzservidor"],
}


async def test_adaptador_con_mapa_de_juguete_predice_con_el_patron_del_mapa(entorno_backend):
    clasificador = sa.clasificador_con_vocabulario(MAPA_JUGUETE)

    resultado = await clasificador.classify("falla de la zzimpresora del piso 3")

    assert resultado.sector_predicho == "Soporte Tecnico Hardware"
    assert resultado.sin_prediccion is False


async def test_adaptador_ignora_los_terminos_del_vocabulario_vigente(entorno_backend):
    clasificador = sa.clasificador_con_vocabulario(MAPA_JUGUETE)

    resultado = await clasificador.classify("el servidor de correo esta caido por un virus y un firewall")

    assert resultado.sector_predicho is None
    assert resultado.sin_prediccion is True


def _vocabulario_vigente():
    return sa.keyword_map_desde_fuente(_KEYWORDS_VIGENTE.read_text(encoding="utf-8"))


_TEXTOS_CON_SENAL = [
    "Detectamos un ataque de phishing y malware en la red, el firewall bloqueo la VPN.",
    "La impresora del piso 2 no imprime y el mouse del puesto tampoco funciona.",
    "No puedo abrir Outlook, la aplicacion se traba al instalar la actualizacion.",
    "Fallo el backup de la base de datos durante la replicacion de la consulta.",
    "Se cayo el servidor de correo y hay error de red en el servicio.",
    "Texto sin ninguna palabra clave del dominio.",
]


async def test_adaptador_con_el_vocabulario_vigente_reproduce_al_clasificador_de_produccion(
    entorno_backend, corpus_fixture_path
):
    from app.classifiers.deterministic import DeterministicClassifier  # type: ignore
    from evaluation.corpus import cargar_corpus

    produccion = DeterministicClassifier()
    adaptador = sa.clasificador_con_vocabulario(_vocabulario_vigente())
    textos = [c.descripcion for c in cargar_corpus(corpus_fixture_path)] + _TEXTOS_CON_SENAL

    for texto in textos:
        esperado = await produccion.classify(texto)
        obtenido = await adaptador.classify(texto)
        for campo in (
            "sector_predicho", "confianza", "score_correctitud", "sin_prediccion",
            "ambiguo", "sectores_adicionales",
        ):
            assert getattr(obtenido, campo) == getattr(esperado, campo), (campo, texto)


async def test_adaptador_distingue_los_vocabularios_y_deja_intacta_la_cache_de_produccion(entorno_backend):
    from app.classifiers.deterministic import DeterministicClassifier, _compile_patterns  # type: ignore

    v0 = json.loads((_DATOS / "keywords_pre_c71.json").read_text(encoding="utf-8"))
    adaptador_v0 = sa.clasificador_con_vocabulario(v0)
    nueva = DeterministicClassifier()

    assert sum(len(p) for p in adaptador_v0._patterns.values()) == 89
    assert sum(len(p) for p in nueva._patterns.values()) == 151
    assert nueva._patterns is _compile_patterns()


def test_adaptador_rechaza_un_mapa_sin_las_cinco_claves_canonicas():
    with pytest.raises(ValueError, match="cinco claves"):
        sa.clasificador_con_vocabulario({"Sistemas": ["a"]})


def test_adaptador_falla_con_error_explicito_si_produccion_no_expone_patterns(entorno_backend, monkeypatch):
    import app.classifiers.deterministic as modulo  # type: ignore

    class ClasificadorSinPatterns:
        pass

    monkeypatch.setattr(modulo, "DeterministicClassifier", ClasificadorSinPatterns)

    with pytest.raises(AttributeError, match="D5"):
        sa.clasificador_con_vocabulario(MAPA_JUGUETE)


# --- replica historica L0 (D4): ClasificadorLegadoPreC71 y regla_legado ------


def _caso(caso_id, texto, sector="Sistemas", adicionales=(), canal="correo electronico"):
    return CasoEvaluacion(
        id=caso_id, descripcion=texto, sector_asignado=sector,
        sectores_adicionales=list(adicionales), canal_origen=canal,
    )


def _mapa_legado(**patrones_por_sector):
    """Mapa de cinco claves en el orden canonico con los patrones dados (resto vacio)."""
    return {s: list(patrones_por_sector.get(s.replace(" ", "_"), [])) for s in SECTORES}


def _tokens(prefijo, n):
    return [rf"\b{prefijo}{i}\b" for i in range(1, n + 1)]


def _texto(prefijo, n):
    return " ".join(f"{prefijo}{i}" for i in range(1, n + 1))


async def _clasificar_legado(mapa, texto):
    return await sa.ClasificadorLegadoPreC71(mapa).classify(texto)


async def test_legado_un_solo_sector_con_coincidencias_da_confianza_w_sobre_w_mas_eps_y_cortocircuita():
    mapa = _mapa_legado(Sistemas=_tokens("s", 3))

    resultado = await _clasificar_legado(mapa, _texto("s", 3))
    (obs,) = await recolectar_observaciones(
        [_caso("1", _texto("s", 3))], sa.ClasificadorLegadoPreC71(mapa)
    )

    assert resultado.sector_predicho == "Sistemas"
    assert resultado.confianza == pytest.approx(3 / (3 + 1e-6), abs=1e-12)
    assert sa.regla_legado(0.90)(obs) is True


async def test_legado_empate_uno_a_uno_elige_el_primer_sector_del_mapa_con_confianza_un_medio():
    mapa = _mapa_legado(Soporte_Tecnico_Hardware=[r"\bh1\b"], Sistemas=[r"\bs1\b"])
    texto = "h1 s1"

    resultado = await _clasificar_legado(mapa, texto)
    (obs,) = await recolectar_observaciones([_caso("1", texto)], sa.ClasificadorLegadoPreC71(mapa))

    assert resultado.sector_predicho == "Soporte Tecnico Hardware"
    assert resultado.confianza == pytest.approx(0.5, abs=1e-6)
    assert sa.regla_legado(0.90)(obs) is False


async def test_legado_sin_coincidencias_elige_la_primera_clave_del_mapa_con_confianza_cero():
    mapa = _mapa_legado(Sistemas=[r"\bs1\b"])

    resultado = await _clasificar_legado(mapa, "texto sin senal")

    assert resultado.sector_predicho == "Seguridad Informatica"
    assert resultado.confianza == 0.0
    assert resultado.sectores_adicionales == []


@pytest.mark.parametrize(
    "ganador,segundo,confianza,cortocircuita",
    [
        (10, 1, 10 / (11 + 1e-6), True),   # 0,90909...: supera 0,90
        (9, 1, 9 / (10 + 1e-6), False),    # 0,89999991: la constante 1e-6 deja el 9:1 apenas por debajo
        (8, 1, 8 / (9 + 1e-6), False),
    ],
)
async def test_legado_umbral_de_cortocircuito_con_segundo_sector(ganador, segundo, confianza, cortocircuita):
    mapa = _mapa_legado(Sistemas=_tokens("s", ganador), Bases_de_Datos=_tokens("b", segundo))
    texto = f"{_texto('s', ganador)} {_texto('b', segundo)}"

    resultado = await _clasificar_legado(mapa, texto)
    (obs,) = await recolectar_observaciones([_caso("1", texto)], sa.ClasificadorLegadoPreC71(mapa))

    assert resultado.sector_predicho == "Sistemas"
    assert resultado.confianza == pytest.approx(confianza, abs=1e-12)
    assert sa.regla_legado(0.90)(obs) is cortocircuita


async def test_legado_tres_sectores_con_senal_el_segundo_define_el_margen_y_los_demas_son_adicionales():
    mapa = _mapa_legado(
        Soporte_Tecnico_Hardware=_tokens("h", 2),
        Bases_de_Datos=_tokens("b", 3),
        Sistemas=_tokens("s", 6),
    )
    texto = f"{_texto('h', 2)} {_texto('b', 3)} {_texto('s', 6)}"

    resultado = await _clasificar_legado(mapa, texto)

    assert resultado.sector_predicho == "Sistemas"
    assert resultado.confianza == pytest.approx(6 / (6 + 3 + 1e-6), abs=1e-12)
    assert resultado.sectores_adicionales == ["Soporte Tecnico Hardware", "Bases de Datos"]


async def test_legado_el_ganador_de_un_empate_depende_del_orden_de_las_claves_del_mapa():
    sin_patrones = [s for s in SECTORES if s not in ("Sistemas", "Bases de Datos")]
    sistemas_primero = {"Sistemas": [r"\bx\b"], "Bases de Datos": [r"\by\b"], **{s: [] for s in sin_patrones}}
    datos_primero = {"Bases de Datos": [r"\by\b"], "Sistemas": [r"\bx\b"], **{s: [] for s in sin_patrones}}

    ganador_a = (await _clasificar_legado(sistemas_primero, "x y")).sector_predicho
    ganador_b = (await _clasificar_legado(datos_primero, "x y")).sector_predicho

    assert (ganador_a, ganador_b) == ("Sistemas", "Bases de Datos")


async def test_legado_la_confianza_queda_acotada_a_uno():
    mapa = _mapa_legado(Sistemas=_tokens("s", 400))

    resultado = await _clasificar_legado(mapa, _texto("s", 400))

    assert resultado.confianza <= 1.0
    assert resultado.confianza == pytest.approx(1.0, abs=1e-8)


def test_regla_vigente_exige_senal_dominante_y_score_en_o_sobre_el_umbral():
    def obs(score, sin_prediccion=False, ambiguo=False):
        return sa.ObservacionDeterminista(
            caso_id="1", sector_asignado="Sistemas", verdad=frozenset({"Sistemas"}),
            sector_predicho=None if (sin_prediccion or ambiguo) else "Sistemas",
            confianza=0.0, sin_prediccion=sin_prediccion, ambiguo=ambiguo, score=score,
        )

    regla = sa.regla_vigente(0.5166)

    assert regla(obs(0.5166)) is True
    assert regla(obs(0.5165)) is False
    assert regla(obs(0.9, ambiguo=True)) is False
    assert regla(obs(0.9, sin_prediccion=True)) is False


# ---------------------------------------------------------------------------
# Bloque 5 - metricas puras de sensibilidad (D3, D8)
# ---------------------------------------------------------------------------


def _obs(caso_id, predicho, asignado="Sistemas", score=0.9, confianza=0.0,
         sin_prediccion=False, ambiguo=False, verdad=None):
    return sa.ObservacionDeterminista(
        caso_id=caso_id,
        sector_asignado=asignado,
        verdad=frozenset(verdad if verdad is not None else {asignado}),
        sector_predicho=None if (sin_prediccion or ambiguo) else predicho,
        confianza=confianza,
        sin_prediccion=sin_prediccion,
        ambiguo=ambiguo,
        score=score,
    )


def _obs_resumen():
    """10 casos: 6 pasan score >= 0,5 (4 aciertos estrictos, 5 laxos), 2 ambiguos/sin senal, 2 bajo el umbral."""
    return [
        _obs("1", "Sistemas"),
        _obs("2", "Sistemas"),
        _obs("3", "Sistemas"),
        _obs("4", "Sistemas"),
        _obs("5", "Bases de Datos", verdad={"Sistemas", "Bases de Datos"}),  # laxo, no estricto
        _obs("6", "Bases de Datos"),                                          # error
        _obs("7", "Sistemas", score=0.2),
        _obs("8", "Sistemas", score=0.4),
        _obs("9", "Sistemas", ambiguo=True),
        _obs("10", "Sistemas", sin_prediccion=True),
    ]


def test_resumen_cortocircuito_regla_vigente_cuenta_casos_aciertos_exactitud_ic_y_cobertura():
    resumen = sa.resumen_cortocircuito(_obs_resumen(), sa.regla_vigente(0.5))

    assert (resumen.total, resumen.casos, resumen.aciertos, resumen.aciertos_laxos) == (10, 6, 4, 5)
    assert resumen.exactitud == pytest.approx(4 / 6)
    assert resumen.ic == intervalo_wilson(4, 6)
    assert resumen.cobertura == pytest.approx(0.6)


def test_resumen_cortocircuito_regla_legado_usa_la_confianza():
    observaciones = [
        _obs("1", "Sistemas", confianza=0.95),
        _obs("2", "Bases de Datos", confianza=0.90),
        _obs("3", "Sistemas", confianza=0.8999),
    ]

    resumen = sa.resumen_cortocircuito(observaciones, sa.regla_legado(0.90))

    assert (resumen.casos, resumen.aciertos) == (2, 1)
    assert resumen.ic == intervalo_wilson(1, 2)


def test_resumen_cortocircuito_sin_casos_seleccionados_deja_exactitud_e_ic_en_none():
    resumen = sa.resumen_cortocircuito(_obs_resumen(), sa.regla_vigente(0.99))

    assert (resumen.casos, resumen.aciertos, resumen.aciertos_laxos) == (0, 0, 0)
    assert resumen.exactitud is None
    assert resumen.ic is None
    assert resumen.cobertura == 0.0


def _obs_sinteticas(seleccionados, aciertos, total, atributo):
    """`total` observaciones; `seleccionados` pasan la regla (`atributo`), `aciertos` de ellas aciertan."""
    observaciones = []
    for i in range(total):
        pasa = i < seleccionados
        acierta = i < aciertos
        valor = 0.9 if pasa else 0.1
        observaciones.append(
            _obs(str(i), "Sistemas" if acierta else "Bases de Datos", **{atributo: valor})
        )
    return observaciones


def _redondeado(ic):
    return (round(ic[0], 4), round(ic[1], 4))


def test_resumen_cortocircuito_reproduce_el_oraculo_97_de_131_del_documento_de_calibracion():
    observaciones = _obs_sinteticas(131, 97, 200, "score")

    resumen = sa.resumen_cortocircuito(observaciones, sa.regla_vigente(0.5166))

    assert (resumen.casos, resumen.aciertos) == (131, 97)
    assert round(resumen.exactitud, 4) == 0.7405
    assert _redondeado(resumen.ic) == (0.6593, 0.8079)
    assert round(resumen.cobertura, 4) == 0.655


def test_resumen_cortocircuito_reproduce_el_oraculo_37_de_72_de_la_linea_base_de_c71():
    observaciones = _obs_sinteticas(72, 37, 200, "confianza")

    resumen = sa.resumen_cortocircuito(observaciones, sa.regla_legado(0.90))

    assert (resumen.casos, resumen.aciertos) == (72, 37)
    assert round(resumen.exactitud, 4) == 0.5139
    assert _redondeado(resumen.ic) == (0.4007, 0.6257)
    assert round(resumen.cobertura, 4) == 0.36


def test_resumen_cortocircuito_los_aciertos_laxos_no_son_menores_que_los_estrictos():
    for regla in (sa.regla_vigente(0.0), sa.regla_vigente(0.5), sa.regla_legado(0.0)):
        resumen = sa.resumen_cortocircuito(_obs_resumen(), regla)
        assert resumen.aciertos_laxos >= resumen.aciertos


def _par_de_vocabularios():
    """Referencia (V1) y alternativa (V0) alineadas por caso."""
    ref = [
        _obs("A", "Sistemas"),                       # ref: selecciona, acierta
        _obs("B", "Sistemas"),                       # ref: selecciona, acierta
        _obs("C", "Bases de Datos"),                 # ref: selecciona, falla
        _obs("D", "Sistemas"),                       # ref: selecciona, acierta (solo ref)
        _obs("E", "Bases de Datos", score=0.1),      # ref: no selecciona, su prediccion fallaria
    ]
    alt = [
        _obs("A", "Sistemas"),                       # alt: selecciona, acierta
        _obs("B", "Bases de Datos"),                 # alt: selecciona, falla
        _obs("C", "Sistemas"),                       # alt: selecciona, acierta
        _obs("D", "Sistemas", ambiguo=True),         # alt: no selecciona (ambiguo)
        _obs("E", "Sistemas"),                       # alt: selecciona, acierta (solo alt)
    ]
    return ref, alt


def test_descomposicion_pareada_separa_comunes_solo_referencia_y_solo_alternativa():
    ref, alt = _par_de_vocabularios()

    d = sa.descomposicion_pareada(ref, alt, sa.regla_vigente(0.5), sa.regla_vigente(0.5))

    assert (d.comunes.casos, d.comunes.aciertos_ref, d.comunes.aciertos_alt) == (3, 2, 2)
    assert (d.solo_ref.casos, d.solo_ref.aciertos_ref, d.solo_ref.aciertos_alt) == (1, 1, 0)
    assert (d.solo_alt.casos, d.solo_alt.aciertos_ref, d.solo_alt.aciertos_alt) == (1, 0, 1)


def test_descomposicion_pareada_es_aditiva_con_los_resumenes_de_cada_vocabulario():
    ref, alt = _par_de_vocabularios()
    regla = sa.regla_vigente(0.5)

    d = sa.descomposicion_pareada(ref, alt, regla, regla)
    r_ref = sa.resumen_cortocircuito(ref, regla)
    r_alt = sa.resumen_cortocircuito(alt, regla)

    assert d.comunes.casos + d.solo_ref.casos == r_ref.casos
    assert d.comunes.aciertos_ref + d.solo_ref.aciertos_ref == r_ref.aciertos
    assert d.comunes.casos + d.solo_alt.casos == r_alt.casos
    assert d.comunes.aciertos_alt + d.solo_alt.aciertos_alt == r_alt.aciertos


def test_descomposicion_pareada_aplica_mcnemar_sobre_los_casos_comunes():
    ref, alt = _par_de_vocabularios()

    d = sa.descomposicion_pareada(ref, alt, sa.regla_vigente(0.5), sa.regla_vigente(0.5))

    m = d.mcnemar_comunes
    assert (m.pares, m.ambas, m.solo_a, m.solo_b, m.ninguna) == (3, 1, 1, 1, 0)
    assert m.p_exacto == pytest.approx(1.0)


def test_descomposicion_pareada_sin_casos_comunes_declara_mcnemar_no_aplicable():
    ref = [_obs("A", "Sistemas"), _obs("B", "Sistemas", score=0.1)]
    alt = [_obs("A", "Sistemas", ambiguo=True), _obs("B", "Sistemas")]
    regla = sa.regla_vigente(0.5)

    d = sa.descomposicion_pareada(ref, alt, regla, regla)

    assert d.comunes.casos == 0
    assert (d.solo_ref.ids, d.solo_alt.ids) == (("A",), ("B",))
    assert d.mcnemar_comunes.aplicable is False
    assert d.mcnemar_comunes.criterio == "no aplicable"
    assert d.mcnemar_comunes.pares == 0


def test_descomposicion_pareada_con_predicciones_identicas_en_los_comunes_no_tiene_discordancias():
    ref = [_obs("A", "Sistemas"), _obs("B", "Bases de Datos"), _obs("C", "Sistemas")]
    alt = [_obs("A", "Sistemas"), _obs("B", "Bases de Datos"), _obs("C", "Sistemas")]
    regla = sa.regla_vigente(0.5)

    d = sa.descomposicion_pareada(ref, alt, regla, regla)

    m = d.mcnemar_comunes
    assert (m.solo_a, m.solo_b) == (0, 0)
    assert (m.ambas, m.ninguna) == (2, 1)
    assert m.aplicable is False
    assert d.solo_ref.casos == d.solo_alt.casos == 0


def test_descomposicion_pareada_usa_reglas_distintas_para_cada_lado():
    ref = [_obs("A", "Sistemas", score=0.9), _obs("B", "Sistemas", score=0.9)]
    alt = [_obs("A", "Sistemas", confianza=0.95), _obs("B", "Bases de Datos", confianza=0.2)]

    d = sa.descomposicion_pareada(ref, alt, sa.regla_vigente(0.5), sa.regla_legado(0.90))

    assert (d.comunes.casos, d.solo_ref.casos, d.solo_alt.casos) == (1, 1, 0)
    assert d.solo_ref.ids == ("B",)


def test_descomposicion_pareada_rechaza_observaciones_de_casos_distintos():
    with pytest.raises(ValueError, match="mismos casos"):
        sa.descomposicion_pareada(
            [_obs("A", "Sistemas")], [_obs("Z", "Sistemas")],
            sa.regla_vigente(0.5), sa.regla_vigente(0.5),
        )


# --- exactitud global con las predicciones de Gemini fijas (E3, D8) -----------


def _pred(sector, etapa="gemini"):
    return PrediccionCacheada(sector_predicho=sector, etapa=etapa)


def _casos_global():
    """Casos 1-5 alineados: ver el comentario de cada uno."""
    ref = [
        _obs("1", "Sistemas"),                      # ambos cortocircuitan; ref acierta
        _obs("2", "Bases de Datos", score=0.1),     # ambos escalan; cache acierta
        _obs("3", "Sistemas"),                      # ref cortocircuita (acierta); alt escala
        _obs("4", "Bases de Datos", score=0.1),     # ambos escalan; cache ausente
        _obs("5", "Bases de Datos", score=0.1),     # ambos escalan; entrada de la cache es deterministica
    ]
    alt = [
        _obs("1", "Bases de Datos"),                # alt cortocircuita y falla
        _obs("2", "Bases de Datos", score=0.1),
        _obs("3", "Bases de Datos", score=0.1),     # alt escala
        _obs("4", "Bases de Datos", score=0.1),
        _obs("5", "Bases de Datos", score=0.1),
    ]
    cache = {
        "2": _pred("Sistemas"),
        "3": _pred("Bases de Datos"),               # prediccion de Gemini equivocada
        "5": _pred("Sistemas", etapa="deterministic"),
    }
    return ref, alt, cache


def test_exactitud_global_con_cache_usa_solo_predicciones_gemini_y_excluye_los_casos_sin_ellas():
    ref, alt, cache = _casos_global()

    g = sa.exactitud_global_con_cache(ref, alt, cache, sa.regla_vigente(0.5166))

    assert g.casos == 3
    assert g.excluidos == ("4", "5")
    assert (g.aciertos_ref, g.aciertos_alt) == (3, 1)


def test_exactitud_global_con_cache_aplica_mcnemar_sobre_el_mismo_conjunto():
    ref, alt, cache = _casos_global()

    g = sa.exactitud_global_con_cache(ref, alt, cache, sa.regla_vigente(0.5166))

    m = g.mcnemar
    assert (m.pares, m.ambas, m.solo_a, m.solo_b, m.ninguna) == (3, 1, 2, 0, 0)
    assert m.p_exacto == pytest.approx(0.5)


def test_exactitud_global_con_cache_vacia_conserva_los_casos_cortocircuitados_por_ambos_lados():
    ref = [_obs("1", "Sistemas"), _obs("2", "Bases de Datos")]
    alt = [_obs("1", "Sistemas"), _obs("2", "Sistemas")]

    g = sa.exactitud_global_con_cache(ref, alt, {}, sa.regla_vigente(0.5166))

    assert (g.casos, g.aciertos_ref, g.aciertos_alt, g.excluidos) == (2, 1, 2, ())
    assert (g.mcnemar.solo_a, g.mcnemar.solo_b) == (0, 1)


def test_exactitud_global_con_cache_caso_escalado_en_ambos_lados_es_un_par_concordante():
    ref = [_obs("1", "Bases de Datos", score=0.1), _obs("2", "Bases de Datos", score=0.1)]
    alt = [_obs("1", "Sistemas", score=0.1), _obs("2", "Sistemas", score=0.1)]
    cache = {"1": _pred("Sistemas"), "2": _pred("Bases de Datos")}

    g = sa.exactitud_global_con_cache(ref, alt, cache, sa.regla_vigente(0.5166))

    assert (g.casos, g.aciertos_ref, g.aciertos_alt) == (2, 1, 1)
    assert (g.mcnemar.ambas, g.mcnemar.ninguna, g.mcnemar.aplicable) == (1, 1, False)


def test_exactitud_global_con_cache_una_entrada_deterministica_cuenta_como_ausente():
    ref = [_obs("1", "Sistemas"), _obs("2", "Sistemas", score=0.1)]
    alt = [_obs("1", "Sistemas", score=0.1), _obs("2", "Sistemas", score=0.1)]
    cache = {"1": _pred("Sistemas", etapa="deterministic"), "2": _pred("Sistemas", etapa="deterministic")}

    g = sa.exactitud_global_con_cache(ref, alt, cache, sa.regla_vigente(0.5166))

    assert g.casos == 0
    assert g.excluidos == ("1", "2")
    assert g.mcnemar.aplicable is False


def test_exactitud_global_con_cache_rechaza_observaciones_desalineadas():
    with pytest.raises(ValueError, match="mismos casos"):
        sa.exactitud_global_con_cache(
            [_obs("1", "Sistemas")], [_obs("2", "Sistemas")], {}, sa.regla_vigente(0.5166)
        )


# --- 5.10 integracion (reuso, sin RED): contraste_det_gem_en_s sobre V0 --------
def test_contraste_det_gem_en_s_aplicado_a_observaciones_de_v0_aparea_su_conjunto_y_lista_excluidos():
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    v0 = [
        _obs("1", "Sistemas"),                        # V0 cortocircuita; Gemini acierta
        _obs("2", "Bases de Datos"),                  # V0 cortocircuita; Gemini acierta -> V0 falla
        _obs("3", "Sistemas", score=0.1),             # V0 escala: fuera de S
        _obs("4", "Sistemas"),                        # V0 cortocircuita; sin prediccion de Gemini
    ]
    cache = {"1": _pred("Sistemas"), "2": _pred("Sistemas"), "3": _pred("Sistemas")}

    contraste = contraste_det_gem_en_s(v0, cache, 0.5166)

    assert (contraste.tamano_s, contraste.pares, contraste.excluidos) == (3, 2, ("4",))
    assert (contraste.aciertos_det, contraste.aciertos_gem) == (1, 2)


# --- 5.11 control de fidelidad contra la linea base documentada por c-71 -------
def test_linea_base_c71_tiene_los_valores_documentados():
    assert sa.LINEA_BASE_C71 == {
        "cortocircuitados": 72,
        "cortocircuitados_correo": 22,
        "cortocircuitados_web": 14,
        "cortocircuitados_telefono": 36,
        "aciertos": 37,
        "aciertos_correo": 13,
        "aciertos_web": 7,
        "aciertos_telefono": 17,
        "aciertos_laxos": 55,
        "sin_coincidencias": 119,
        "predicciones_seguridad_informatica": 126,
    }


def _obs_legado_toy():
    obs = [
        _obs("c1", "Sistemas", confianza=0.95),                                           # correo, acierta
        _obs("c2", "Bases de Datos", confianza=0.91, verdad={"Sistemas", "Bases de Datos"}),  # correo, laxo
        _obs("c3", "Bases de Datos", confianza=0.95),                                     # web, error
        _obs("c4", "Seguridad Informatica", confianza=0.0),                               # telefono, sin coincidencias
        _obs("c5", "Seguridad Informatica", confianza=0.5),                               # telefono, no cortocircuita
    ]
    canales = {
        "c1": "correo electronico", "c2": "correo electronico", "c3": "formulario web",
        "c4": "llamada telefonica", "c5": "llamada telefonica",
    }
    return obs, canales


_DOCUMENTADO_TOY = {
    "cortocircuitados": 3, "cortocircuitados_correo": 2, "cortocircuitados_web": 1,
    "cortocircuitados_telefono": 0, "aciertos": 1, "aciertos_correo": 1, "aciertos_web": 0,
    "aciertos_telefono": 0, "aciertos_laxos": 2, "sin_coincidencias": 1,
    "predicciones_seguridad_informatica": 2,
}
_CANALES_TOY = {"correo": "correo electronico", "web": "formulario web", "telefono": "llamada telefonica"}


def test_comparar_linea_base_c71_marca_coincide_cuando_todas_las_metricas_reproducen_lo_documentado():
    obs, canales = _obs_legado_toy()

    filas = sa.comparar_linea_base_c71(obs, canales, _DOCUMENTADO_TOY, canales_corpus=_CANALES_TOY)

    assert [f.metrica for f in filas] == list(_DOCUMENTADO_TOY)
    assert [f.reproducido for f in filas] == list(_DOCUMENTADO_TOY.values())
    assert all(f.coincide for f in filas)


def test_comparar_linea_base_c71_una_sola_metrica_distinta_es_la_unica_que_difiere():
    obs, canales = _obs_legado_toy()
    documentado = {**_DOCUMENTADO_TOY, "aciertos_laxos": 55}

    filas = sa.comparar_linea_base_c71(obs, canales, documentado, canales_corpus=_CANALES_TOY)

    distintas = [f for f in filas if not f.coincide]
    assert [(f.metrica, f.documentado, f.reproducido) for f in distintas] == [("aciertos_laxos", 55, 2)]
    assert sum(f.coincide for f in filas) == len(filas) - 1


def test_comparar_linea_base_c71_un_canal_sin_casos_cuenta_cero_explicito():
    obs, canales = _obs_legado_toy()
    sin_telefono = {k: v for k, v in canales.items() if v != "llamada telefonica"}
    documentado = {**_DOCUMENTADO_TOY, "cortocircuitados_telefono": 5}

    filas = {f.metrica: f for f in sa.comparar_linea_base_c71(obs, sin_telefono, documentado, canales_corpus=_CANALES_TOY)}

    assert filas["cortocircuitados_telefono"].reproducido == 0
    assert filas["cortocircuitados_telefono"].coincide is False
    assert filas["aciertos_telefono"].reproducido == 0
    assert filas["aciertos_telefono"].coincide is True


def test_comparar_linea_base_c71_usa_por_defecto_los_valores_de_canal_del_corpus_real():
    assert sa.CANALES_CORPUS == {
        "correo": "correo electr\u00f3nico",
        "web": "formulario web",
        "telefono": "llamada telef\u00f3nica",
    }


# ---------------------------------------------------------------------------
# Bloque 6 - reporte (D10)
# ---------------------------------------------------------------------------


def _resultados(**cambios):
    """`ResultadosSensibilidad` minimo (sin caches ni nivel del prompt) construido con las funciones reales."""
    regla = sa.regla_vigente(0.5166)
    ref = _obs_sinteticas(131, 97, 200, "score")
    alt = _obs_sinteticas(100, 60, 200, "score")
    legado = _obs_sinteticas(72, 37, 200, "confianza")
    base = sa.ResultadosSensibilidad(
        procedencia={
            "corpus_sha256": "1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb",
            "tau": 0.5166,
            "pesos": {"margen": 0.5, "evidencia": 0.3, "densidad": 0.2},
            "blobs": {"keywords_pre_c71": "858f1c6", "keywords_vigente": "334a8ed",
                      "prompt_pre_c72": "1daceb3", "prompt_vigente": "49267f4"},
            "sha256_artefactos": {"keywords_pre_c71.json": "aa" * 32, "prompt_gemini_pre_c72.txt": "bb" * 32},
        },
        evaluada=sa.resumen_cortocircuito(ref, regla),
        esperada_evaluada=(131, 97),
        variante_principal=sa.resumen_cortocircuito(alt, regla),
        descomposicion=sa.descomposicion_pareada(ref, alt, regla, regla),
        referencia_historica=sa.resumen_cortocircuito(legado, sa.regla_legado(0.90)),
        fidelidad=sa.comparar_linea_base_c71(
            legado, {o.caso_id: "formulario web" for o in legado}, sa.LINEA_BASE_C71
        ),
    )
    return dataclasses.replace(base, **cambios)


_ENCABEZADOS_EN_ORDEN = [
    "## Procedencia",
    "## Configuracion evaluada",
    "## Variante principal",
    "## Referencia historica",
    "## Variante por pliegues",
    "## Sensibilidad global y piso comparativo",
    "## Sensibilidad del prompt",
]


def test_reporte_tiene_las_secciones_de_d10_en_orden():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    posiciones = [texto.index(h) for h in _ENCABEZADOS_EN_ORDEN]
    assert posiciones == sorted(posiciones)
    assert texto.startswith("# Sensibilidad frente a los ajustes del clasificador (c-142)")


def test_reporte_usa_cuatro_decimales_con_punto_y_el_ic_de_wilson():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    assert "0.7405" in texto
    assert "[0.6593, 0.8079]" in texto
    assert "131/200" in texto and "97/131" in texto
    assert "0,7405" not in texto


def test_reporte_incluye_procedencia_con_blobs_hashes_tau_y_pesos():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    for esperado in ("1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb",
                     "858f1c6", "334a8ed", "1daceb3", "49267f4", "0.5166", "aa" * 32, "bb" * 32):
        assert esperado in texto, esperado


def test_reporte_declara_la_variante_por_pliegues_no_factible_con_su_motivo():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    seccion = texto.split("## Variante por pliegues")[1].split("## Sensibilidad global")[0]
    assert "no factible" in seccion
    assert "no registra" in seccion


def test_reporte_sin_caches_rotula_no_computable_no_computado_y_no_aplicable():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    seccion_global = texto.split("## Sensibilidad global")[1].split("## Sensibilidad del prompt")[0]
    seccion_prompt = texto.split("## Sensibilidad del prompt")[1]
    assert "no computable" in seccion_global
    assert "no computado" in seccion_prompt


def test_reporte_no_lleva_marcas_de_tiempo_de_generacion():
    texto = sa.formatear_reporte_sensibilidad(_resultados())

    assert re.search(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}", texto) is None


def _resultados_con_caches(**cambios):
    from evaluation.deterministic_measurement import contraste_det_gem_en_s

    ref, alt, cache = _casos_global()
    regla = sa.regla_vigente(0.5166)
    contraste = contraste_det_gem_en_s(
        [_obs("1", "Sistemas"), _obs("2", "Bases de Datos")],
        {"1": _pred("Sistemas"), "2": _pred("Sistemas")}, 0.5166,
    )
    return _resultados(
        global_cache=sa.exactitud_global_con_cache(ref, alt, cache, regla),
        global_documentado=146,
        piso_v1=contraste,
        piso_v0=contraste,
        **cambios,
    )


def test_reporte_con_caches_informa_e3_y_e4_en_lugar_de_no_computable():
    texto = sa.formatear_reporte_sensibilidad(_resultados_con_caches())

    seccion = texto.split("## Sensibilidad global")[1].split("## Sensibilidad del prompt")[0]
    assert "no computable" not in seccion
    assert "V1 3/3 (documentado sobre los 200 casos: 146); V0 1/3" in seccion
    assert "excluidos de ambos lados (sin prediccion de Gemini): 4, 5" in seccion
    assert "E4 (V0): |S| = 2; pares 2" in seccion
    assert "McNemar: p binomial exacto bilateral" in seccion


def test_reporte_nivel_a_aplicable_y_no_aplicable():
    aplicable = sa.ResultadoNivelA(("R002", "R038"), 69, 50, 67, 49)
    no_aplicable = sa.ResultadoNivelA((), 69, 50, 69, 50)

    con = sa.formatear_reporte_sensibilidad(_resultados(nivel_a=aplicable))
    sin = sa.formatear_reporte_sensibilidad(_resultados(nivel_a=no_aplicable))

    assert "motivadores entre los 69 casos escalados: R002, R038" in con
    assert "todos los casos 50/69; sin los motivadores 49/67" in con
    assert "Nivel a: no aplicable; ninguno de los casos motivadores" in sin


def test_reporte_nivel_b_solo_compara_si_la_clasificacion_es_previa_confirmada():
    comparacion = sa.ComparacionCorridas(69, 49, 50, sa.contraste_mcnemar([True, False], [False, True]))
    posterior = sa.ResultadoNivelB("posterior", "2026-10-07T20:33:03+00:00")
    previa = sa.ResultadoNivelB("previa confirmada", "2026-10-05T23:00:00+00:00", comparacion)

    t_posterior = sa.formatear_reporte_sensibilidad(_resultados(nivel_b=posterior))
    t_previa = sa.formatear_reporte_sensibilidad(_resultados(nivel_b=previa))

    assert 'clasificada como "posterior"' in t_posterior
    assert "Nivel b: no aplicable" in t_posterior
    assert 'clasificada como "previa confirmada"' in t_previa
    assert "FORCE-ESCALATE 49/69 frente a corrida oficial 50/69" in t_previa


def test_reporte_nivel_b_indeterminada_sin_fecha_la_rotula_ausente():
    texto = sa.formatear_reporte_sensibilidad(_resultados(nivel_b=sa.ResultadoNivelB("indeterminada", None)))

    assert "generated_at: ausente" in texto


def test_reporte_nivel_c_ejecutado_reemplaza_la_leyenda_no_computado():
    class NivelCFalso:
        def lineas(self):
            return ["- Nivel c: 40/69 frente a 45/69."]

    texto = sa.formatear_reporte_sensibilidad(_resultados(nivel_c=NivelCFalso()))

    assert "Nivel c: 40/69 frente a 45/69." in texto
    assert "no computado" not in texto


def test_reporte_dos_llamadas_consecutivas_producen_salida_identica():
    resultados = _resultados_con_caches(nivel_a=sa.ResultadoNivelA((), 69, 50, 69, 50))

    assert sa.formatear_reporte_sensibilidad(resultados) == sa.formatear_reporte_sensibilidad(resultados)


def test_reporte_marca_difiere_si_la_configuracion_evaluada_no_reproduce_lo_esperado():
    texto = sa.formatear_reporte_sensibilidad(_resultados(esperada_evaluada=(131, 98)))

    assert "131/97 frente a 131/98 esperados: difiere" in texto


# ---------------------------------------------------------------------------
# Bloque 7 (soporte de los niveles a y b del prompt, D9) - TDD de las funciones puras
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    "generated_at,esperado",
    [
        ("2026-10-05T23:59:59+00:00", "previa confirmada"),
        ("2026-10-06T00:50:04Z", "previa confirmada"),
        ("2026-10-06T00:50:05Z", "probablemente previa"),
        ("2026-10-06T19:38:19+00:00", "probablemente previa"),
        ("2026-10-06T19:38:20Z", "posterior"),
        ("2026-10-07T20:33:03.438926+00:00", "posterior"),
        # -03:00 de la hora local de los commits: 2026-10-06T21:00-03:00 = 00:00Z del 07.
        ("2026-10-06T21:00:00-03:00", "posterior"),
        (None, "indeterminada"),
        ("", "indeterminada"),
        ("no es una fecha", "indeterminada"),
    ],
)
def test_clasificar_prompt_de_la_cache_segun_la_fecha_de_generacion(generated_at, esperado):
    assert sa.clasificar_prompt_de_la_cache(generated_at) == esperado


def _escalados_nivel_a():
    """Cuatro casos escalados (score bajo) y uno cortocircuitado."""
    obs = [
        _obs("R002", "Sistemas", score=0.1),
        _obs("R038", "Sistemas", score=0.1),
        _obs("R100", "Sistemas", score=0.1),
        _obs("R101", "Sistemas", score=0.1),
        _obs("R015", "Sistemas"),  # cortocircuitado: su motivador no esta entre los escalados
    ]
    cache = {
        "R002": _pred("Bases de Datos"), "R038": _pred("Sistemas"),
        "R100": _pred("Sistemas"), "R101": _pred("Bases de Datos"),
    }
    return obs, cache


def test_nivel_a_retira_solo_los_motivadores_que_estan_entre_los_escalados():
    obs, cache = _escalados_nivel_a()

    a = sa.calcular_nivel_a(obs, cache, sa.regla_vigente(0.5166))

    assert a.motivadores_en_escalados == ("R002", "R038")
    assert (a.casos, a.aciertos) == (4, 2)
    assert (a.casos_sin_motivadores, a.aciertos_sin_motivadores) == (2, 1)


def test_nivel_a_sin_motivadores_entre_los_escalados_queda_no_aplicable():
    obs = [_obs("R100", "Sistemas", score=0.1), _obs("R015", "Sistemas")]

    a = sa.calcular_nivel_a(obs, {"R100": _pred("Sistemas")}, sa.regla_vigente(0.5166))

    assert a.motivadores_en_escalados == ()
    assert (a.casos, a.aciertos, a.casos_sin_motivadores, a.aciertos_sin_motivadores) == (1, 1, 1, 1)


def test_nivel_a_falla_si_la_cache_no_tiene_a_gemini_para_un_caso_escalado():
    with pytest.raises(ValueError, match="R100"):
        sa.calcular_nivel_a([_obs("R100", "Sistemas", score=0.1)], {}, sa.regla_vigente(0.5166))


def test_nivel_a_una_entrada_deterministica_no_vale_como_prediccion_de_gemini():
    with pytest.raises(ValueError, match="R100"):
        sa.calcular_nivel_a(
            [_obs("R100", "Sistemas", score=0.1)],
            {"R100": _pred("Sistemas", etapa="deterministic")},
            sa.regla_vigente(0.5166),
        )


def test_comparar_corridas_aparea_los_casos_escalados_y_lista_los_excluidos():
    obs = [
        _obs("1", "Sistemas", score=0.1),
        _obs("2", "Sistemas", score=0.1),
        _obs("3", "Sistemas", score=0.1),
        _obs("4", "Sistemas"),                       # cortocircuitado: no entra
        _obs("5", "Sistemas", score=0.1),            # sin entrada gemini en la corrida A
    ]
    cache_a = {"1": _pred("Sistemas"), "2": _pred("Bases de Datos"), "3": _pred("Sistemas"),
               "5": _pred("Sistemas", etapa="deterministic")}
    cache_b = {"1": _pred("Sistemas"), "2": _pred("Sistemas"), "3": _pred("Bases de Datos"),
               "5": _pred("Sistemas")}

    c = sa.comparar_corridas(obs, sa.regla_vigente(0.5166), cache_a, cache_b)

    assert (c.casos, c.aciertos_a, c.aciertos_b, c.excluidos) == (3, 2, 2, ("5",))
    assert (c.mcnemar.ambas, c.mcnemar.solo_a, c.mcnemar.solo_b) == (1, 1, 1)


def test_nivel_b_con_prompt_previo_confirmado_incluye_la_comparacion():
    obs = [_obs("1", "Sistemas", score=0.1), _obs("2", "Sistemas", score=0.1)]
    fe = {"1": _pred("Sistemas"), "2": _pred("Bases de Datos")}
    oficial = {"1": _pred("Sistemas"), "2": _pred("Sistemas")}

    b = sa.calcular_nivel_b("2026-10-05T12:00:00+00:00", obs, sa.regla_vigente(0.5166), fe, oficial)

    assert b.clasificacion == "previa confirmada"
    assert (b.comparacion.aciertos_a, b.comparacion.aciertos_b, b.comparacion.casos) == (1, 2, 2)


@pytest.mark.parametrize("generated_at", ["2026-10-06T10:00:00+00:00", "2026-10-07T20:33:03+00:00", None])
def test_nivel_b_con_prompt_no_confirmado_como_previo_no_compara(generated_at):
    obs = [_obs("1", "Sistemas", score=0.1)]
    cache = {"1": _pred("Sistemas")}

    b = sa.calcular_nivel_b(generated_at, obs, sa.regla_vigente(0.5166), cache, cache)

    assert b.comparacion is None
    assert b.generated_at == generated_at


# ---------------------------------------------------------------------------
# Bloque 6 (cont.) - main con corpus y fabricas inyectados (D10)
# ---------------------------------------------------------------------------


class _ClasificadorTabla:
    """Clasificador falso: resultado preasignado por descripcion; nunca llama a un servicio."""

    def __init__(self, tabla):
        self._tabla = tabla

    async def classify(self, descripcion):
        sector, confianza, score = self._tabla[descripcion]
        return sa.ResultadoLegado(
            sector_predicho=sector, confianza=confianza, sectores_adicionales=[], score_correctitud=score,
        )


def _tablas_de_juguete(corpus):
    """V1: 9 cortocircuitados, 6 aciertos. V0: los 5 primeros, 4 aciertos. L0: los 4 primeros, 3 aciertos."""
    def tabla(cortocircuitados, errores):
        filas = {}
        for i, caso in enumerate(corpus):
            equivocado = "Sistemas" if caso.sector_asignado != "Sistemas" else "Bases de Datos"
            sector = equivocado if i in errores else caso.sector_asignado
            alta = i < cortocircuitados
            filas[caso.descripcion] = (sector, 0.95 if alta else 0.1, 0.9 if alta else 0.1)
        return filas

    return {
        "v1": tabla(9, {6, 7, 8}),
        "v0": tabla(5, {4}),
        "l0": tabla(4, {3}),
    }


def _fabricas(tablas):
    return (
        lambda mapa: _ClasificadorTabla(tablas[mapa["nombre"]]),
        lambda mapa: _ClasificadorTabla(tablas[mapa["nombre"]]),
    )


def _argumentos_main(corpus, tmp_path, **cambios):
    tablas = _tablas_de_juguete(corpus)
    fabrica_vocabulario, fabrica_legado = _fabricas(tablas)
    argumentos = dict(
        corpus=corpus,
        vocab_v1={"nombre": "v1"},
        vocab_v0={"nombre": "v0"},
        vocab_legado={"nombre": "l0"},
        umbral=0.5166,
        fabrica_vocabulario=fabrica_vocabulario,
        fabrica_legado=fabrica_legado,
        report_path=tmp_path / "salida" / "report_sensibilidad_ajustes.md",
        esperada_evaluada=(9, 6),
        procedencia={"corpus_sha256": "abc", "tau": 0.5166},
    )
    argumentos.update(cambios)
    return argumentos


async def test_main_escribe_solo_el_reporte_indicado_y_devuelve_los_resultados(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)

    resultados = await sa.main(**_argumentos_main(corpus, tmp_path))

    escritos = sorted(p.relative_to(tmp_path).as_posix() for p in tmp_path.rglob("*") if p.is_file())
    assert escritos == ["salida/report_sensibilidad_ajustes.md"]
    texto = (tmp_path / "salida" / "report_sensibilidad_ajustes.md").read_text(encoding="utf-8")
    assert texto == sa.formatear_reporte_sensibilidad(resultados)
    assert (resultados.evaluada.casos, resultados.evaluada.aciertos) == (9, 6)
    assert (resultados.variante_principal.casos, resultados.variante_principal.aciertos) == (5, 4)
    assert (resultados.referencia_historica.casos, resultados.referencia_historica.aciertos) == (4, 3)
    assert resultados.global_cache is None and resultados.piso_v0 is None
    assert resultados.nivel_a is None and resultados.nivel_b is None


async def test_main_no_toca_el_reporte_oficial_ni_las_caches_del_repositorio(corpus_fixture_path, tmp_path):
    protegidos = [
        _REPO / "evaluation" / "report.md",
        _REPO / "evaluation" / "predicciones.json",
        _REPO / "evaluation" / "predicciones_calibracion.json",
    ]
    antes = {p: (p.read_bytes() if p.exists() else None) for p in protegidos}

    await sa.main(**_argumentos_main(cargar_corpus(corpus_fixture_path), tmp_path))

    assert {p: (p.read_bytes() if p.exists() else None) for p in protegidos} == antes


async def test_main_no_construye_el_clasificador_hibrido_ni_el_de_gemini(
    entorno_backend, corpus_fixture_path, tmp_path, monkeypatch
):
    import app.classifiers.gemini_classifier as gemini  # type: ignore
    import app.classifiers.hybrid as hybrid  # type: ignore

    def prohibido(*args, **kwargs):
        raise AssertionError("la sensibilidad offline no puede construir clasificadores con Gemini")

    monkeypatch.setattr(gemini, "GeminiClassifier", prohibido)
    monkeypatch.setattr(hybrid, "HybridClassifier", prohibido)

    resultados = await sa.main(**_argumentos_main(cargar_corpus(corpus_fixture_path), tmp_path))

    assert resultados.evaluada.casos == 9


async def test_main_falla_con_error_explicito_si_la_configuracion_evaluada_no_reproduce_los_conteos(
    corpus_fixture_path, tmp_path
):
    argumentos = _argumentos_main(cargar_corpus(corpus_fixture_path), tmp_path, esperada_evaluada=(131, 97))

    with pytest.raises(sa.ConfiguracionNoReproducidaError, match=r"9/6.*131/97"):
        await sa.main(**argumentos)

    assert not argumentos["report_path"].exists()


def _escribir_cache(ruta, corpus, predicciones, generated_at, descripcion_alterada=None):
    """Escribe una cache con el formato del runner. `predicciones`: indice -> (sector, etapa)."""
    items = []
    for i, caso in enumerate(corpus):
        if i not in predicciones:
            continue
        sector, etapa = predicciones[i]
        items.append({
            "caso_id": caso.id,
            "descripcion": descripcion_alterada if i == 0 and descripcion_alterada else caso.descripcion,
            "sector_asignado": caso.sector_asignado,
            "sector_predicho": sector,
            "confianza": 0.9,
            "etapa": etapa,
            "sectores_adicionales": [],
        })
    ruta.write_text(
        json.dumps({"cache_meta": {"generated_at": generated_at}, "predictions": items}), encoding="utf-8"
    )


def _tabla_v1_siete(corpus):
    filas = {}
    for i, caso in enumerate(corpus):
        equivocado = "Sistemas" if caso.sector_asignado != "Sistemas" else "Bases de Datos"
        sector = equivocado if i in {5, 6} else caso.sector_asignado
        alta = i < 7
        filas[caso.descripcion] = (sector, 0.95 if alta else 0.1, 0.9 if alta else 0.1)
    return filas


def _main_con_caches(corpus, tmp_path, generated_at="2026-10-07T20:33:03+00:00", descripcion_alterada=None):
    tablas = _tablas_de_juguete(corpus)
    tablas["v1"] = _tabla_v1_siete(corpus)
    fabrica_vocabulario, fabrica_legado = _fabricas(tablas)
    asignado = {i: (c.sector_asignado, "gemini") for i, c in enumerate(corpus)}
    equivocado = lambda c: "Sistemas" if c.sector_asignado != "Sistemas" else "Bases de Datos"  # noqa: E731
    fe = {**asignado, 7: (equivocado(corpus[7]), "gemini")}
    oficial = {**asignado, 8: (equivocado(corpus[8]), "gemini")}
    _escribir_cache(tmp_path / "fe.json", corpus, fe, generated_at, descripcion_alterada)
    _escribir_cache(tmp_path / "oficial.json", corpus, oficial, "2026-10-07T22:22:01+00:00")
    return sa.main(**_argumentos_main(
        corpus, tmp_path,
        fabrica_vocabulario=fabrica_vocabulario, fabrica_legado=fabrica_legado,
        esperada_evaluada=(7, 5),
        cache_fe_path=tmp_path / "fe.json", cache_oficial_path=tmp_path / "oficial.json",
        motivadores=("8",),
    ))


async def test_main_con_caches_calcula_e3_e4_y_los_niveles_a_y_b(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)

    r = await _main_con_caches(corpus, tmp_path)

    g = r.global_cache
    assert (g.casos, g.aciertos_ref, g.aciertos_alt, g.excluidos) == (9, 6, 7, ())
    assert (r.piso_v1.tamano_s, r.piso_v1.pares, r.piso_v1.aciertos_det, r.piso_v1.aciertos_gem) == (7, 7, 5, 7)
    assert (r.piso_v0.tamano_s, r.piso_v0.pares, r.piso_v0.aciertos_det, r.piso_v0.aciertos_gem) == (5, 5, 4, 5)
    assert r.nivel_a.motivadores_en_escalados == ("8",)
    assert (r.nivel_a.casos, r.nivel_a.aciertos) == (2, 1)
    assert (r.nivel_a.casos_sin_motivadores, r.nivel_a.aciertos_sin_motivadores) == (1, 0)
    assert r.nivel_b.clasificacion == "posterior"
    assert r.nivel_b.generated_at == "2026-10-07T20:33:03+00:00"
    assert r.nivel_b.comparacion is None


async def test_main_con_prompt_previo_confirmado_compara_la_force_escalate_con_la_oficial(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)

    r = await _main_con_caches(corpus, tmp_path, generated_at="2026-10-05T12:00:00+00:00")

    c = r.nivel_b.comparacion
    assert r.nivel_b.clasificacion == "previa confirmada"
    assert (c.casos, c.aciertos_a, c.aciertos_b) == (2, 1, 1)
    assert (c.mcnemar.solo_a, c.mcnemar.solo_b) == (1, 1)


async def test_main_rechaza_una_cache_que_no_corresponde_al_corpus(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)

    with pytest.raises(ValueError, match="descripcion distinta"):
        await _main_con_caches(corpus, tmp_path, descripcion_alterada="otra descripcion")


async def test_main_ignora_las_caches_que_no_existen_y_las_rotula_no_computables(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)

    r = await sa.main(**_argumentos_main(
        corpus, tmp_path, cache_fe_path=tmp_path / "no_existe.json", cache_oficial_path=tmp_path / "tampoco.json"
    ))

    texto = sa.formatear_reporte_sensibilidad(r)
    assert r.global_cache is None and r.nivel_a is None and r.nivel_b is None
    assert "E3 (exactitud global con las predicciones de Gemini fijas): no computable" in texto
    assert "Nivel a (sin los casos motivadores de c-72): no computable" in texto
    assert "Nivel b (FORCE-ESCALATE frente a corrida oficial): no computable" in texto


# ---------------------------------------------------------------------------
# Bloque 6 (cont.) - procedencia y CLI offline
# ---------------------------------------------------------------------------
def test_blob_git_reproduce_los_ids_conocidos_de_git():
    assert sa.blob_git(b"") == "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391"
    assert sa.blob_git(b"hello\n") == "ce013625030ba8dba906f756967f9e9ca394464a"


def test_blob_git_normaliza_crlf_a_lf_como_el_blob_versionado():
    assert sa.blob_git(b"a\r\nb\r\n") == sa.blob_git(b"a\nb\n")


def test_construir_procedencia_registra_los_blobs_vigentes_y_los_hashes_de_los_artefactos(entorno_backend):
    p = sa.construir_procedencia(
        corpus_path=_REPO / "data" / "corpus_evaluacion_pseudonimizado.json", umbral=0.5166,
        pesos={"margen": 0.5},
    )

    assert p["blobs"]["keywords_pre_c71 (7925903)"] == BLOB_KEYWORDS_PREVIO
    assert p["blobs"]["prompt_pre_c72 (a76851e^)"] == BLOB_PROMPT_PREVIO
    assert p["blobs"]["keywords_vigente"] == "334a8edb296cf8e88468164c9a35d57f80952c0e"
    assert p["blobs"]["prompt_vigente"] == "49267f4a5cf214bf46899c5177661f1cdbfd10fb"
    assert p["sha256_artefactos"]["keywords_pre_c71.json"] == _sha256(_DATOS / "keywords_pre_c71.json")
    assert p["tau"] == 0.5166 and p["pesos"] == {"margen": 0.5}


@pytest.mark.skipif(
    not (_REPO / "data" / "corpus_evaluacion_pseudonimizado.json").exists(), reason="corpus ausente"
)
def test_construir_procedencia_hashea_el_corpus_con_fin_de_linea_normalizado():
    p = sa.construir_procedencia(
        corpus_path=_REPO / "data" / "corpus_evaluacion_pseudonimizado.json", umbral=0.5166, pesos={}
    )

    assert p["corpus_sha256"] == "1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb"


def test_leer_punto_de_operacion_toma_tau_y_pesos_de_settings(entorno_backend):
    tau, pesos = sa.leer_punto_de_operacion()

    assert tau == 0.5166
    assert set(pesos) == {"margen", "evidencia", "densidad"}
    assert all(isinstance(v, float) for v in pesos.values())


def test_resolver_caches_prefiere_la_copia_viva_y_cae_en_la_evidencia_versionada(tmp_path):
    ev = tmp_path / "evaluation" / "evidence"
    ev.mkdir(parents=True)
    (ev / "predicciones_calibracion_hybrid-v2_2026-10-07.json").write_text("{}", encoding="utf-8")
    (ev / "predicciones_hybrid-v3_2026-10-07.json").write_text("{}", encoding="utf-8")

    fe, oficial = sa.resolver_caches(tmp_path)
    assert fe == ev / "predicciones_calibracion_hybrid-v2_2026-10-07.json"
    assert oficial == ev / "predicciones_hybrid-v3_2026-10-07.json"

    (tmp_path / "evaluation" / "predicciones_calibracion.json").write_text("{}", encoding="utf-8")
    (tmp_path / "evaluation" / "predicciones.json").write_text("{}", encoding="utf-8")
    fe, oficial = sa.resolver_caches(tmp_path)
    assert fe == tmp_path / "evaluation" / "predicciones_calibracion.json"
    assert oficial == tmp_path / "evaluation" / "predicciones.json"


def test_resolver_caches_sin_ninguna_devuelve_none(tmp_path):
    assert sa.resolver_caches(tmp_path) == (None, None)


def _capturar_cli(monkeypatch, argv):
    capturado = {}

    async def main_falso(corpus, **kwargs):
        capturado["corpus"] = corpus
        capturado.update(kwargs)

    monkeypatch.setattr(sa, "main", main_falso)
    return capturado, sa.cli(argv)


def test_cli_offline_usa_el_vocabulario_vigente_y_el_previo_y_los_valores_de_settings(
    entorno_backend, monkeypatch, corpus_fixture_path, tmp_path
):
    salida = tmp_path / "r.md"
    capturado, codigo = _capturar_cli(
        monkeypatch, ["--corpus", str(corpus_fixture_path), "--report", str(salida)]
    )

    assert codigo == 0
    assert sum(len(p) for p in capturado["vocab_v1"].values()) == 151
    assert sum(len(p) for p in capturado["vocab_v0"].values()) == 89
    assert capturado["umbral"] == 0.5166
    assert capturado["report_path"] == salida
    assert capturado["esperada_evaluada"] == (131, 97)
    assert len(capturado["corpus"]) == 9
    assert capturado["procedencia"]["blobs"]["keywords_vigente"] == "334a8edb296cf8e88468164c9a35d57f80952c0e"


def test_cli_acepta_rutas_explicitas_de_las_caches(entorno_backend, monkeypatch, corpus_fixture_path, tmp_path):
    capturado, _ = _capturar_cli(monkeypatch, [
        "--corpus", str(corpus_fixture_path), "--report", str(tmp_path / "r.md"),
        "--cache-fe", str(tmp_path / "fe.json"), "--cache-oficial", str(tmp_path / "of.json"),
    ])

    assert capturado["cache_fe_path"] == tmp_path / "fe.json"
    assert capturado["cache_oficial_path"] == tmp_path / "of.json"


def test_cli_informa_el_error_de_reproduccion_con_codigo_distinto_de_cero(
    entorno_backend, monkeypatch, corpus_fixture_path, tmp_path, capsys
):
    async def main_que_falla(corpus, **kwargs):
        raise sa.ConfiguracionNoReproducidaError("deriva simulada")

    monkeypatch.setattr(sa, "main", main_que_falla)

    codigo = sa.cli(["--corpus", str(corpus_fixture_path), "--report", str(tmp_path / "r.md")])

    assert codigo == 1
    assert "deriva simulada" in capsys.readouterr().err


# ---------------------------------------------------------------------------
# Bloque 8 - ablacion paga del prompt (D9 nivel c): el instrumento, sin invocar al proveedor
# ---------------------------------------------------------------------------
def test_seleccionar_casos_escalados_devuelve_los_no_cortocircuitados_en_el_orden_del_corpus():
    observaciones = [
        _obs("A", "Sistemas"),
        _obs("B", "Sistemas", score=0.1),
        _obs("C", "Sistemas", ambiguo=True),
        _obs("D", "Sistemas"),
        _obs("E", "Sistemas", sin_prediccion=True),
    ]

    escalados = sa.seleccionar_casos_escalados(observaciones, sa.regla_vigente(0.5166))

    assert [o.caso_id for o in escalados] == ["B", "C", "E"]


def test_seleccionar_casos_escalados_con_todos_cortocircuitados_devuelve_lista_vacia():
    observaciones = [_obs("A", "Sistemas"), _obs("B", "Bases de Datos")]

    assert sa.seleccionar_casos_escalados(observaciones, sa.regla_vigente(0.5166)) == []


def test_seleccionar_casos_escalados_con_ninguno_cortocircuitado_devuelve_todos():
    observaciones = [_obs("A", "Sistemas", score=0.0), _obs("B", "Sistemas", ambiguo=True)]

    assert [o.caso_id for o in sa.seleccionar_casos_escalados(observaciones, sa.regla_vigente(0.5166))] == ["A", "B"]


# --- 8.4 correr_brazo_prompt (gate de corrida paga) con clasificador falso ----


class _GeminiFalso:
    """Doble de HybridClassifier: registra las llamadas y no usa ningun servicio."""

    def __init__(self, etapas=None, sectores=None):
        self.llamadas = []
        self._etapas = etapas or {}
        self._sectores = sectores or {}

    async def classify(self, descripcion):
        self.llamadas.append(descripcion)
        return sa.ResultadoLegado(
            sector_predicho=self._sectores.get(descripcion, "Sistemas"),
            confianza=0.8,
            sectores_adicionales=[],
            etapa=self._etapas.get(descripcion, "gemini"),
        )


def _casos_brazo():
    return [_caso("R1", "falla del servidor uno"), _caso("R2", "falla del servidor dos", sector="Bases de Datos")]


def _meta_brazo():
    return {
        "gemini_model": "gemini-2.5-flash", "gemini_temperature": 0.3,
        "classifier_version": "hybrid-v3", "corpus_hash": "h" * 64,
    }


async def _correr(tmp_path, brazo="vigente", confirm_paid=True, prompt_cargado=None, fabrica=None, **kw):
    if prompt_cargado is None:
        prompt_cargado = sa.prompt_esperado(brazo).texto
    falso = fabrica or _GeminiFalso()
    llamadas_a_la_fabrica = []

    def fabrica_clasificador():
        llamadas_a_la_fabrica.append(1)
        return falso

    salida = kw.pop("salida", tmp_path / f"predicciones_sensibilidad_prompt_{brazo}.json")
    predicciones = await sa.correr_brazo_prompt(
        _casos_brazo(), brazo, salida, confirm_paid, fabrica_clasificador, prompt_cargado,
        meta=_meta_brazo(), **kw,
    )
    return predicciones, salida, falso, llamadas_a_la_fabrica


async def test_brazo_sin_confirmacion_falla_antes_de_construir_el_clasificador(tmp_path):
    with pytest.raises(PaidRunNotConfirmedError):
        await _correr(tmp_path, confirm_paid=False)

    assert not (tmp_path / "predicciones_sensibilidad_prompt_vigente.json").exists()


async def test_brazo_con_prompt_distinto_del_esperado_falla_antes_de_la_primera_llamada(tmp_path):
    llamadas = []

    def fabrica():
        llamadas.append(1)
        return _GeminiFalso()

    with pytest.raises(sa.PromptInesperadoError, match="sin-reglas"):
        await sa.correr_brazo_prompt(
            _casos_brazo(), "sin-reglas", tmp_path / "s.json", True, fabrica,
            sa.prompt_esperado("vigente").texto, meta=_meta_brazo(),
        )

    assert llamadas == []
    assert not (tmp_path / "s.json").exists()


async def test_brazo_correcto_escribe_las_predicciones_con_cache_meta_ampliado(tmp_path, capsys):
    predicciones, salida, falso, construcciones = await _correr(tmp_path)

    assert [p.caso_id for p in predicciones] == ["R1", "R2"]
    assert falso.llamadas == ["falla del servidor uno", "falla del servidor dos"]
    assert construcciones == [1]
    datos = json.loads(salida.read_text(encoding="utf-8"))
    meta = datos["cache_meta"]
    esperado = sa.prompt_esperado("vigente")
    assert meta["brazo"] == "vigente"
    assert meta["prompt_sha256"] == esperado.sha256 == hashlib.sha256(esperado.texto.encode("utf-8")).hexdigest()
    assert meta["prompt_origen"] == esperado.origen
    assert (meta["gemini_model"], meta["gemini_temperature"]) == ("gemini-2.5-flash", 0.3)
    assert (meta["classifier_version"], meta["corpus_hash"]) == ("hybrid-v3", "h" * 64)
    assert meta["casos"] == ["R1", "R2"] and meta["fallbacks"] == 0
    assert re.match(r"\d{4}-\d{2}-\d{2}T", meta["generated_at"])
    assert [p["caso_id"] for p in datos["predictions"]] == ["R1", "R2"]
    assert "Casos del corpus: 2" in capsys.readouterr().out


async def test_brazo_sin_reglas_espera_el_prompt_previo_a_c72(tmp_path):
    _, salida, _, _ = await _correr(tmp_path, brazo="sin-reglas")

    meta = json.loads(salida.read_text(encoding="utf-8"))["cache_meta"]
    assert meta["brazo"] == "sin-reglas"
    assert meta["prompt_sha256"] == sa.prompt_esperado("sin-reglas").sha256
    assert meta["prompt_sha256"] != sa.prompt_esperado("vigente").sha256
    assert "prompt_gemini_pre_c72.txt" in meta["prompt_origen"]


@pytest.mark.parametrize("nombre", ["predicciones.json", "predicciones_calibracion.json", "report.md"])
async def test_brazo_rechaza_las_rutas_de_salida_oficiales(tmp_path, nombre):
    llamadas = []

    with pytest.raises(ValueError, match="oficial"):
        await sa.correr_brazo_prompt(
            _casos_brazo(), "vigente", _REPO / "evaluation" / nombre, True,
            lambda: llamadas.append(1), sa.prompt_esperado("vigente").texto, meta=_meta_brazo(),
        )

    assert llamadas == []


async def test_brazo_con_nombre_desconocido_falla(tmp_path):
    with pytest.raises(ValueError, match="brazo"):
        await sa.correr_brazo_prompt(
            _casos_brazo(), "otro", tmp_path / "x.json", True, lambda: None, "", meta=_meta_brazo()
        )


async def test_brazo_una_respuesta_de_reserva_se_cuenta_como_fallback(tmp_path):
    falso = _GeminiFalso(etapas={"falla del servidor dos": "fallback"})

    _, salida, _, _ = await _correr(tmp_path, fabrica=falso)

    meta = json.loads(salida.read_text(encoding="utf-8"))["cache_meta"]
    assert meta["fallbacks"] == 1


async def test_brazo_con_una_prediccion_deterministica_falla_sin_escribir_la_salida(tmp_path):
    falso = _GeminiFalso(etapas={"falla del servidor uno": "deterministic"})

    with pytest.raises(RuntimeError, match="caso no escalado.*R1"):
        await _correr(tmp_path, fabrica=falso)

    assert not (tmp_path / "predicciones_sensibilidad_prompt_vigente.json").exists()


async def test_brazo_prompt_esperado_difiere_entre_brazos_y_coincide_con_los_archivos():
    vigente, previo = sa.prompt_esperado("vigente"), sa.prompt_esperado("sin-reglas")

    assert "REGLAS DE FRONTERA" in vigente.texto
    assert "REGLAS DE FRONTERA" not in previo.texto
    assert vigente.texto == _normalizar_lf(_PROMPT_VIGENTE.read_text(encoding="utf-8")).strip()


# --- 8.7 comparar_brazos ------------------------------------------------------


def _p(caso_id, predicho, etapa="gemini", asignado="Sistemas"):
    return Prediccion(
        caso_id=caso_id, descripcion="d", sector_asignado=asignado,
        sector_predicho=predicho, confianza=0.8, etapa=etapa,
    )


def test_comparar_brazos_cuenta_aciertos_de_cada_brazo_sobre_los_mismos_casos_y_aplica_mcnemar():
    control = [_p("1", "Sistemas"), _p("2", "Sistemas"), _p("3", "Bases de Datos"), _p("4", "Sistemas")]
    sin_reglas = [_p("1", "Sistemas"), _p("2", "Bases de Datos"), _p("3", "Bases de Datos"), _p("4", "Bases de Datos")]

    r = sa.comparar_brazos(control, sin_reglas)

    assert (r.casos, r.aciertos_vigente, r.aciertos_sin_reglas) == (4, 3, 1)
    assert (r.mcnemar.ambas, r.mcnemar.solo_a, r.mcnemar.solo_b, r.mcnemar.ninguna) == (1, 2, 0, 1)
    assert r.mcnemar.p_exacto == pytest.approx(0.5)
    assert r.deriva is None


def test_comparar_brazos_con_conjuntos_de_casos_distintos_falla():
    with pytest.raises(ValueError, match="mismos casos"):
        sa.comparar_brazos([_p("1", "Sistemas")], [_p("2", "Sistemas")])


def test_comparar_brazos_una_reserva_cuenta_como_error_y_se_informa():
    control = [_p("1", "Sistemas"), _p("2", "Sistemas", etapa="fallback")]
    sin_reglas = [_p("1", "Sistemas"), _p("2", "Sistemas")]

    r = sa.comparar_brazos(control, sin_reglas)

    assert (r.aciertos_vigente, r.aciertos_sin_reglas) == (1, 2)
    assert (r.reservas_vigente, r.reservas_sin_reglas) == (1, 0)


def test_comparar_brazos_con_la_corrida_oficial_informa_la_deriva_del_brazo_control():
    control = [_p("1", "Sistemas"), _p("2", "Bases de Datos"), _p("3", "Sistemas")]
    sin_reglas = [_p("1", "Sistemas"), _p("2", "Sistemas"), _p("3", "Sistemas")]
    oficial = {"1": _pred("Sistemas"), "2": _pred("Sistemas"), "3": _pred("Bases de Datos")}

    r = sa.comparar_brazos(control, sin_reglas, oficial)

    assert (r.deriva.casos, r.deriva.aciertos_a, r.deriva.aciertos_b) == (3, 2, 2)
    assert (r.deriva.mcnemar.solo_a, r.deriva.mcnemar.solo_b) == (1, 1)


def test_comparar_brazos_lineas_informa_k_p0_k_p1_reservas_y_deriva():
    control = [_p("1", "Sistemas"), _p("2", "Bases de Datos")]
    sin_reglas = [_p("1", "Sistemas"), _p("2", "Sistemas")]
    oficial = {"1": _pred("Sistemas"), "2": _pred("Bases de Datos")}

    texto = "\n".join(sa.comparar_brazos(control, sin_reglas, oficial).lineas())

    assert "Nivel c" in texto
    assert "prompt vigente 1/2" in texto and "sin reglas de frontera 2/2" in texto
    assert "reservas" in texto
    assert "deriva del brazo control frente a la corrida oficial" in texto
    assert "McNemar: p binomial exacto" in texto


def test_reporte_con_nivel_c_incluye_sus_lineas_en_lugar_de_no_computado():
    control = [_p("1", "Sistemas")]
    nivel_c = sa.comparar_brazos(control, control)

    texto = sa.formatear_reporte_sensibilidad(_resultados(nivel_c=nivel_c))

    assert "prompt vigente 1/1" in texto
    assert "Nivel c (ablacion controlada de dos brazos, corrida paga): no computado" not in texto


# --- 8.5/8.6 CLI: subcomando `prompt` y entrega de los brazos al reporte -------
def test_cli_prompt_sin_confirmacion_sale_con_codigo_2_sin_construir_nada(monkeypatch, capsys):
    monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    construido = []
    monkeypatch.setattr(sa, "_construir_hybrid_real", lambda: construido.append(1))
    monkeypatch.setattr(sa, "_prompt_cargado_por_el_backend", lambda brazo: construido.append(2))

    codigo = sa.cli(["prompt", "--brazo", "vigente"])

    assert codigo == 2
    assert construido == []
    assert "confirm" in capsys.readouterr().err.lower()


@pytest.mark.parametrize("argumentos,entorno", [(["--confirm-paid"], None), ([], "1")])
def test_cli_prompt_con_confirmacion_por_flag_o_entorno_delega_en_correr_brazo(
    entorno_backend, monkeypatch, corpus_fixture_path, tmp_path, argumentos, entorno
):
    if entorno is None:
        monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    else:
        monkeypatch.setenv("EVALUATION_CONFIRM_PAID", entorno)
    capturado = {}

    async def brazo_falso(casos, brazo, salida, confirm_paid, fabrica, prompt_cargado, **kw):
        capturado.update(casos=casos, brazo=brazo, salida=salida, confirm_paid=confirm_paid,
                         prompt_cargado=prompt_cargado, meta=kw.get("meta"))
        return []

    monkeypatch.setattr(sa, "correr_brazo_prompt", brazo_falso)
    monkeypatch.setattr(sa, "_prompt_cargado_por_el_backend", lambda brazo: "PROMPT")
    monkeypatch.setattr(sa, "_meta_corrida_paga", lambda corpus_path: {"gemini_model": "m"})
    async def escalados_falsos(corpus, umbral):
        return list(corpus)[:2]
    monkeypatch.setattr(sa, "_casos_escalados_reales", escalados_falsos)

    codigo = sa.cli(["prompt", "--brazo", "sin-reglas", "--corpus", str(corpus_fixture_path),
                     "--salida", str(tmp_path / "s.json"), *argumentos])

    assert codigo == 0
    assert capturado["brazo"] == "sin-reglas" and capturado["confirm_paid"] is True
    assert capturado["salida"] == tmp_path / "s.json"
    assert capturado["prompt_cargado"] == "PROMPT" and capturado["meta"] == {"gemini_model": "m"}
    assert len(capturado["casos"]) == 2


def test_salida_por_defecto_de_cada_brazo_es_un_archivo_propio_ignorado_por_git():
    assert sa.salida_por_defecto("sin-reglas") == _REPO / "evaluation" / "predicciones_sensibilidad_prompt_sin_reglas.json"
    assert sa.salida_por_defecto("vigente") == _REPO / "evaluation" / "predicciones_sensibilidad_prompt_vigente.json"


def test_cli_offline_con_los_dos_brazos_entrega_el_nivel_c_al_reporte(
    entorno_backend, monkeypatch, corpus_fixture_path, tmp_path
):
    from evaluation.run_evaluation import guardar_predicciones

    guardar_predicciones([_p("1", "Sistemas")], tmp_path / "v.json", cache_meta={"brazo": "vigente"})
    guardar_predicciones([_p("1", "Bases de Datos")], tmp_path / "s.json", cache_meta={"brazo": "sin-reglas"})

    capturado, _ = _capturar_cli(monkeypatch, [
        "--corpus", str(corpus_fixture_path), "--report", str(tmp_path / "r.md"),
        "--brazo-vigente", str(tmp_path / "v.json"), "--brazo-sin-reglas", str(tmp_path / "s.json"),
    ])

    nivel_c = capturado["nivel_c"]
    assert (nivel_c.casos, nivel_c.aciertos_vigente, nivel_c.aciertos_sin_reglas) == (1, 1, 0)


def test_cli_offline_sin_brazos_deja_el_nivel_c_en_none(entorno_backend, monkeypatch, corpus_fixture_path, tmp_path):
    capturado, _ = _capturar_cli(monkeypatch, ["--corpus", str(corpus_fixture_path), "--report", str(tmp_path / "r.md")])

    assert capturado["nivel_c"] is None


# --- cobertura de ramas de soporte (verificacion de caches, camino real aislado) ---


def test_asegurar_backend_en_path_lo_agrega_una_sola_vez(monkeypatch):
    ruta = str(_REPO / "App" / "Backend")
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != ruta])

    sa.asegurar_backend_en_path()
    sa.asegurar_backend_en_path()

    assert sys.path.count(ruta) == 1


def test_clasificar_prompt_de_la_cache_interpreta_una_fecha_sin_zona_como_utc():
    assert sa.clasificar_prompt_de_la_cache("2026-10-05T12:00:00") == "previa confirmada"
    assert sa.clasificar_prompt_de_la_cache("2026-10-07T12:00:00") == "posterior"


def test_verificar_cache_contra_corpus_informa_ausentes_sector_distinto_y_sobrantes(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)
    items = [
        {"caso_id": c.id, "descripcion": c.descripcion, "sector_asignado": c.sector_asignado}
        for c in corpus[2:]
    ]
    items[0]["sector_asignado"] = "Sistemas" if items[0]["sector_asignado"] != "Sistemas" else "Bases de Datos"
    items.append({"caso_id": "ZZ", "descripcion": "x", "sector_asignado": "Sistemas"})
    ruta = tmp_path / "c.json"
    ruta.write_text(json.dumps({"predictions": items}), encoding="utf-8")

    with pytest.raises(ValueError) as error:
        sa.verificar_cache_contra_corpus(ruta, corpus)

    mensaje = str(error.value)
    assert "1: ausente en la cache" in mensaje and "2: ausente en la cache" in mensaje
    assert "3: sector asignado distinto" in mensaje
    assert "ZZ: no esta en el corpus" in mensaje


def test_verificar_cache_contra_corpus_acepta_el_formato_de_arreglo_plano(corpus_fixture_path, tmp_path):
    corpus = cargar_corpus(corpus_fixture_path)
    ruta = tmp_path / "plano.json"
    ruta.write_text(json.dumps([
        {"caso_id": c.id, "descripcion": c.descripcion, "sector_asignado": c.sector_asignado} for c in corpus
    ]), encoding="utf-8")

    assert sa.verificar_cache_contra_corpus(ruta, corpus) is None


def test_construir_hybrid_real_devuelve_la_instancia_del_clasificador_del_backend(entorno_backend, monkeypatch):
    import app.classifiers.hybrid as hybrid  # type: ignore

    monkeypatch.setattr(hybrid, "HybridClassifier", lambda: "instancia")

    assert sa._construir_hybrid_real() == "instancia"


@pytest.mark.parametrize("brazo,fragmento", [("vigente", "prompt_gemini.txt"), ("sin-reglas", "prompt_gemini_pre_c72.txt")])
def test_prompt_cargado_por_el_backend_apunta_gemini_prompt_path_al_archivo_del_brazo(
    entorno_backend, monkeypatch, brazo, fragmento
):
    import app.classifiers.gemini_classifier as gemini  # type: ignore

    monkeypatch.setattr(gemini, "_PROMPT_TEMPLATE", "TEXTO DEL BACKEND")
    monkeypatch.delenv("GEMINI_PROMPT_PATH", raising=False)

    assert sa._prompt_cargado_por_el_backend(brazo) == "TEXTO DEL BACKEND"

    import os

    assert os.environ["GEMINI_PROMPT_PATH"].endswith(fragmento)
    monkeypatch.delenv("GEMINI_PROMPT_PATH", raising=False)


def test_meta_corrida_paga_registra_modelo_temperatura_version_y_hash_del_corpus(entorno_backend, corpus_fixture_path):
    meta = sa._meta_corrida_paga(corpus_fixture_path)

    assert set(meta) == {"gemini_model", "gemini_temperature", "classifier_version", "corpus_hash"}
    assert meta["gemini_temperature"] == 0.3
    assert meta["classifier_version"] == "hybrid-v3"
    assert len(meta["corpus_hash"]) == 64


async def test_casos_escalados_reales_devuelve_los_que_la_configuracion_vigente_no_cortocircuita(entorno_backend):
    corpus = [
        _caso("A", "Detectamos phishing y malware, el firewall bloqueo la VPN.", sector="Seguridad Informatica"),
        _caso("B", "hola buen dia necesito ayuda por favor gracias"),
    ]

    escalados = await sa._casos_escalados_reales(corpus, 0.5166)

    assert [c.id for c in escalados] == ["B"]


def test_cli_prompt_con_un_prompt_inesperado_sale_con_codigo_2_y_el_mensaje(
    entorno_backend, monkeypatch, corpus_fixture_path, tmp_path, capsys
):
    async def brazo_que_falla(*args, **kwargs):
        raise sa.PromptInesperadoError("prompt equivocado")

    async def escalados(corpus, umbral):
        return []

    monkeypatch.setattr(sa, "correr_brazo_prompt", brazo_que_falla)
    monkeypatch.setattr(sa, "_prompt_cargado_por_el_backend", lambda brazo: "x")
    monkeypatch.setattr(sa, "_meta_corrida_paga", lambda p: {})
    monkeypatch.setattr(sa, "_casos_escalados_reales", escalados)

    codigo = sa.cli(["prompt", "--brazo", "vigente", "--confirm-paid", "--corpus", str(corpus_fixture_path)])

    assert codigo == 2
    assert "prompt equivocado" in capsys.readouterr().err
