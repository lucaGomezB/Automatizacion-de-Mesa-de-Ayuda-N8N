"""
Tests del score calibrado de correctitud del clasificador determinista (c-74).

Strict TDD:
    1.2 (RED)   -> el resultado determinista expone `score_correctitud` acotado a
                    [0.0, 1.0], determinista y derivado solo de features
                    observables (score ganador, runner-up, margen, cantidad de
                    matches, longitud del texto y senales por sector).
    1.4 (TRI)   -> monotonia esperada respecto de la evidencia y del margen;
                    el conteo minimo de matches es FEATURE del score y no un gate
                    binario (OQ4/D5); texto vacio y texto largo cubiertos.

Restricciones duras (c-74): el score es puro y no invoca proveedores pagos ni
depende de datos no disponibles en runtime.
"""

from __future__ import annotations

import pytest

from app.classifiers.deterministic import (
    DeterministicClassifier,
    FeaturesDeterministas,
    PesosScore,
    extraer_features,
    score_correctitud,
)


@pytest.fixture
def classifier() -> DeterministicClassifier:
    return DeterministicClassifier()


@pytest.fixture
def pesos() -> PesosScore:
    return PesosScore(
        w_margin=0.5,
        w_evidence=0.3,
        w_density=0.2,
        length_reference=200.0,
    )


# ---------------------------------------------------------------------------
# 1.2 RED -> contrato del score expuesto por el clasificador
# ---------------------------------------------------------------------------
class TestContratoDelScore:
    @pytest.mark.asyncio
    async def test_resultado_expone_score_acotado(self, classifier):
        result = await classifier.classify(
            "impresora teclado mouse monitor pantalla laptop"
        )
        assert 0.0 <= result.score_correctitud <= 1.0

    @pytest.mark.asyncio
    async def test_sin_senal_el_score_es_cero(self, classifier):
        result = await classifier.classify(
            "Necesitamos reservar una sala para una reunion de planificacion."
        )
        assert result.sin_prediccion is True
        assert result.score_correctitud == 0.0

    @pytest.mark.asyncio
    async def test_ambiguo_el_score_es_cero(self, classifier):
        result = await classifier.classify("Hay un firewall y un servidor.")
        assert result.ambiguo is True
        assert result.score_correctitud == 0.0

    @pytest.mark.asyncio
    async def test_el_score_es_determinista(self, classifier):
        primero = await classifier.classify("impresora teclado mouse")
        segundo = await classifier.classify("impresora teclado mouse")
        assert primero.score_correctitud == segundo.score_correctitud

    @pytest.mark.asyncio
    async def test_un_unico_match_tiene_score_no_nulo(self, classifier):
        """OQ4/D5: el conteo minimo es feature, no un gate que anule el score."""
        result = await classifier.classify("Se rompio el teclado.")
        assert result.confianza == 0.0, "la confianza es fuerza de senal (min_matches gate)"
        assert result.score_correctitud > 0.0, "el score NO se anula con un unico match"


# ---------------------------------------------------------------------------
# 1.2 RED -> extraccion de features observables
# ---------------------------------------------------------------------------
class TestFeaturesObservables:
    def test_extrae_todas_las_features(self):
        features = extraer_features(
            {"A": 2.0, "B": 1.0, "C": 0.0}, text_length=50, min_matches=2
        )
        assert isinstance(features, FeaturesDeterministas)
        assert features.winner_score == 2.0
        assert features.runner_up_score == 1.0
        assert features.margin == 1.0
        assert features.margin_ratio == pytest.approx(1 / 3)
        assert features.total_matches == 3.0
        assert features.text_length == 50
        assert features.sectores_con_senal == 2
        assert features.min_matches == 2

    def test_features_sin_senal_no_dividen_por_cero(self):
        features = extraer_features({"A": 0.0, "B": 0.0}, text_length=0, min_matches=2)
        assert features.winner_score == 0.0
        assert features.runner_up_score == 0.0
        assert features.margin == 0.0
        assert features.margin_ratio == 0.0
        assert features.sectores_con_senal == 0


# ---------------------------------------------------------------------------
# 1.2 RED / 1.4 TRIANGULATE -> propiedades del score puro
# ---------------------------------------------------------------------------
class TestScoreCorrectitud:
    @pytest.mark.parametrize(
        "winner,runner_up,longitud",
        [(1, 0, 5), (2, 1, 50), (3, 0, 2000), (5, 5, 10), (0, 0, 0)],
    )
    def test_score_acotado_en_rango(self, pesos, winner, runner_up, longitud):
        features = extraer_features(
            {"A": float(winner), "B": float(runner_up)},
            text_length=longitud,
            min_matches=2,
        )
        valor = score_correctitud(features, pesos)
        assert 0.0 <= valor <= 1.0

    def test_sin_senal_el_score_es_cero(self, pesos):
        features = extraer_features({"A": 0.0}, text_length=10, min_matches=2)
        assert score_correctitud(features, pesos) == 0.0

    def test_monotono_en_evidencia(self, pesos):
        """1.4: mas matches del ganador, mismo margen y longitud, sube el score."""
        debil = extraer_features({"A": 1.0, "B": 0.0}, text_length=40, min_matches=2)
        fuerte = extraer_features({"A": 2.0, "B": 0.0}, text_length=40, min_matches=2)
        assert score_correctitud(fuerte, pesos) > score_correctitud(debil, pesos)

    def test_monotono_en_margen(self, pesos):
        """1.4: mismo ganador y longitud, mayor margen sobre el segundo sube el score."""
        angosto = extraer_features({"A": 2.0, "B": 1.0}, text_length=40, min_matches=2)
        amplio = extraer_features({"A": 2.0, "B": 0.0}, text_length=40, min_matches=2)
        assert score_correctitud(amplio, pesos) > score_correctitud(angosto, pesos)

    def test_penaliza_texto_largo(self, pesos):
        """1.4: la misma senal en un texto mas largo es evidencia mas debil."""
        corto = extraer_features({"A": 2.0, "B": 0.0}, text_length=30, min_matches=2)
        largo = extraer_features({"A": 2.0, "B": 0.0}, text_length=1500, min_matches=2)
        assert score_correctitud(corto, pesos) > score_correctitud(largo, pesos)

    def test_min_matches_informa_el_score_sin_anularlo(self, pesos):
        """OQ4: cambiar `min_matches` mueve el score (feature), no lo apaga."""
        con_dos = extraer_features({"A": 1.0, "B": 0.0}, text_length=40, min_matches=2)
        con_tres = extraer_features({"A": 1.0, "B": 0.0}, text_length=40, min_matches=3)
        assert score_correctitud(con_dos, pesos) > 0.0
        assert score_correctitud(con_tres, pesos) > 0.0
        assert score_correctitud(con_dos, pesos) != score_correctitud(con_tres, pesos)

    def test_margen_minimo_rinde_menos_que_margen_maximo(self, pesos):
        """1.4: mismo ganador y longitud, margen minimo vs margen maximo."""
        margen_minimo = extraer_features(
            {"A": 10.0, "B": 9.0}, text_length=60, min_matches=2
        )
        margen_maximo = extraer_features(
            {"A": 10.0, "B": 0.0}, text_length=60, min_matches=2
        )
        assert score_correctitud(margen_minimo, pesos) < score_correctitud(
            margen_maximo, pesos
        )

    @pytest.mark.asyncio
    async def test_texto_vacio_score_cero(self, classifier):
        result = await classifier.classify("")
        assert result.score_correctitud == 0.0

    @pytest.mark.asyncio
    async def test_texto_largo_multi_match_tiene_score_acotado(self, classifier):
        largo = "impresora " * 200 + "teclado mouse monitor pantalla laptop"
        result = await classifier.classify(largo)
        assert 0.0 <= result.score_correctitud <= 1.0

