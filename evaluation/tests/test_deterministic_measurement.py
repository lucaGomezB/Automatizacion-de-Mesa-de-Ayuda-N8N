"""
Tests de la calibracion offline del clasificador deterministico (c-71).

Strict TDD:
    3.5 RED   -> existe una curva precision/cobertura y el umbral elegido
                 respeta el piso de precision de OQ1.
    3.7 TRI   -> umbrales por encima y por debajo del calibrado.
"""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from evaluation.corpus import CasoEvaluacion
from evaluation.deterministic_measurement import (
    PISO_PRECISION_DEFAULT,
    ObservacionDeterminista,
    curva_precision_cobertura,
    punto_en_umbral,
    recolectar_observaciones,
    resumen_vocabulario,
    umbrales_candidatos,
    elegir_umbral,
)


# ---------------------------------------------------------------------------
# Fixtures de observaciones sinteticas
# ---------------------------------------------------------------------------
def _obs(
    caso_id: str,
    predicho,
    confianza: float,
    *,
    asignado: str = "Sistemas",
    sin_prediccion: bool = False,
    ambiguo: bool = False,
) -> ObservacionDeterminista:
    return ObservacionDeterminista(
        caso_id=caso_id,
        sector_asignado=asignado,
        verdad=frozenset({asignado}),
        sector_predicho=predicho,
        confianza=confianza,
        sin_prediccion=sin_prediccion,
        ambiguo=ambiguo,
    )


@pytest.fixture
def observaciones():
    return [
        _obs("a", "Sistemas", 1.0),
        _obs("b", "Sistemas", 0.75),
        _obs("c", "Bases de Datos", 0.75),  # incorrecto
        _obs("d", "Sistemas", 0.5),
        _obs("e", None, 0.0, sin_prediccion=True),
        _obs("f", None, 0.0, ambiguo=True),
    ]


# ---------------------------------------------------------------------------
# 3.5 RED -> 3.6 GREEN
# ---------------------------------------------------------------------------
def test_umbrales_candidatos_solo_de_cortocircuitables(observaciones):
    candidatos = umbrales_candidatos(observaciones)
    assert 1.0 in candidatos
    assert set(candidatos) >= {0.5, 0.75, 1.0}
    # Los estados sin senal/ambiguos NO son umbrales candidatos utiles.
    assert 0.0 not in candidatos


def test_curva_precision_cobertura_calcula_puntos(observaciones):
    curva = curva_precision_cobertura(observaciones)
    por_umbral = {p.umbral: p for p in curva}

    p1 = por_umbral[1.0]
    assert p1.cortocircuitados == 1
    assert p1.precision == pytest.approx(1.0)
    assert p1.cobertura == pytest.approx(1 / 6)

    p075 = por_umbral[0.75]
    assert p075.cortocircuitados == 3
    assert p075.precision == pytest.approx(2 / 3)
    assert p075.cobertura == pytest.approx(0.5)

    p05 = por_umbral[0.5]
    assert p05.cortocircuitados == 4
    assert p05.precision == pytest.approx(0.75)


def test_umbral_elegido_respeta_piso_de_precision(observaciones):
    """3.5: con piso 0.90 solo el umbral mas alto es admisible."""
    curva = curva_precision_cobertura(observaciones)
    umbral = elegir_umbral(curva, PISO_PRECISION_DEFAULT)
    assert umbral == 1.0
    assert punto_en_umbral(observaciones, umbral).precision >= PISO_PRECISION_DEFAULT


def test_piso_bajo_prioriza_cobertura(observaciones):
    """3.7: con piso menor se elige el umbral de mayor cobertura admisible."""
    curva = curva_precision_cobertura(observaciones)
    umbral = elegir_umbral(curva, 0.6)
    assert umbral == 0.5
    punto = punto_en_umbral(observaciones, umbral)
    assert punto.precision >= 0.6
    assert punto.cobertura == pytest.approx(4 / 6)


def test_piso_inalcanzable_devuelve_none(observaciones):
    curva = curva_precision_cobertura(observaciones)
    assert elegir_umbral(curva, 1.01) is None


def test_cobertura_no_crece_al_subir_el_umbral(observaciones):
    """3.7: subir el umbral nunca aumenta la cobertura (monotonia)."""
    bajo = punto_en_umbral(observaciones, 0.5)
    medio = punto_en_umbral(observaciones, 0.75)
    alto = punto_en_umbral(observaciones, 1.0)
    assert bajo.cobertura >= medio.cobertura >= alto.cobertura
    assert bajo.cortocircuitados >= medio.cortocircuitados >= alto.cortocircuitados


# ---------------------------------------------------------------------------
# Cobertura del vocabulario
# ---------------------------------------------------------------------------
def test_resumen_vocabulario_global_y_por_sector(observaciones):
    resumen = resumen_vocabulario(observaciones)
    assert resumen.total == 6
    assert resumen.sin_match == 1
    assert resumen.cobertura_global == pytest.approx(5 / 6)
    assert resumen.cobertura_por_sector["Sistemas"] == pytest.approx(5 / 6)
    assert resumen.no_match_por_sector["Sistemas"] == 1


# ---------------------------------------------------------------------------
# Recoleccion con un clasificador falso (sin Gemini)
# ---------------------------------------------------------------------------
class _FakeDeterministico:
    def __init__(self, mapping):
        self._mapping = mapping
        self.llamadas = 0

    async def classify(self, descripcion: str):
        self.llamadas += 1
        return self._mapping[descripcion]


@pytest.mark.asyncio
async def test_recolectar_observaciones_mapea_el_contrato_aditivo():
    casos = [
        CasoEvaluacion(
            id="1",
            descripcion="con senal",
            sector_asignado="Sistemas",
            sectores_adicionales=[],
        ),
        CasoEvaluacion(
            id="2",
            descripcion="sin senal",
            sector_asignado="Bases de Datos",
            sectores_adicionales=[],
        ),
    ]
    fake = _FakeDeterministico(
        {
            "con senal": SimpleNamespace(
                sector_predicho="Sistemas",
                confianza=0.9,
                sin_prediccion=False,
                ambiguo=False,
                sectores_adicionales=[],
            ),
            "sin senal": SimpleNamespace(
                sector_predicho=None,
                confianza=0.0,
                sin_prediccion=True,
                ambiguo=False,
                sectores_adicionales=[],
            ),
        }
    )
    observaciones = await recolectar_observaciones(casos, fake)
    assert fake.llamadas == 2
    assert observaciones[0].sin_prediccion is False
    assert observaciones[1].sin_prediccion is True
    assert observaciones[1].sector_predicho is None


# ---------------------------------------------------------------------------
# c-71 §5.3 — _a_float permanece intacto
# ---------------------------------------------------------------------------
def _escribir_corpus_con_tiempo_nulo(path):
    import json

    doc = {
        "schema_version": 1,
        "metadata": {"total_casos": 1},
        "casos": [
            {
                "id": "1",
                "descripcion": "desc",
                "canal_origen": "correo",
                "sector_asignado": "Sistemas",
                "sectores_adicionales": [],
                "tiempo_manual_s": 1.0,
                "tiempo_automatizado_s": None,
            }
        ],
    }
    path.write_text(json.dumps(doc), encoding="utf-8")


def test_cargar_corpus_estricto_sigue_rechazando_tiempos_nulos(tmp_path):
    """_a_float permanece intacto: un tiempo None sigue siendo CorpusError."""
    from evaluation.corpus import CorpusError, cargar_corpus

    path = tmp_path / "corpus.json"
    _escribir_corpus_con_tiempo_nulo(path)
    with pytest.raises(CorpusError):
        cargar_corpus(path)


def test_cargar_corpus_tolerante_admite_tiempos_nulos(tmp_path):
    """El loader tolerante (solo medicion offline) admite el tiempo None."""
    from evaluation.deterministic_measurement import cargar_corpus_tolerante

    path = tmp_path / "corpus.json"
    _escribir_corpus_con_tiempo_nulo(path)
    casos = cargar_corpus_tolerante(path)
    assert casos[0].tiempo_automatizado_s is None
    assert casos[0].sector_asignado == "Sistemas"
