"""
Tests de la derivacion OUT-OF-FOLD del tau congelado en Settings (c-74, W1).

Defecto corregido (verificacion independiente W1, HIGH):
    `main()` derivaba el punto de operacion de la curva IN-SAMPLE
    (`elegir_punto_comparativo(curva_comparativa(...))`) mientras que la
    calibracion out-of-fold solo se reportaba. La procedencia anti-fuga
    (`evaluation-framework`) exige que el corpus de test reportado NO participe
    de la seleccion del punto de operacion. El tau CONGELADO
    (`Settings.deterministic_score_threshold`) debe derivarse de
    `ResultadoComparativoOOF.umbrales_por_fold`.

Strict TDD:
    W1 (RED) -> `umbral_de_settings_oof` / `tau_oof_agregado` no existen y la
                constante de Settings no esta atada a la derivacion OOF.
    W1 (TRI) -> la regla de agregacion (coincidencia o minimo) y el truncado
                hacia abajo se verifican con varias entradas; un test atado al
                corpus comprueba la procedencia real del valor 0.5166.
"""

from __future__ import annotations

import pathlib

import pytest

from evaluation.deterministic_measurement import (
    CALIBRACION_CACHE_PATH,
    ResultadoComparativoOOF,
    resolver_cache_calibracion,
    tau_oof_agregado,
    umbral_de_settings_oof,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
def _resultado(*umbrales) -> ResultadoComparativoOOF:
    """Resultado OOF sintetico: solo importan los umbrales por fold."""
    return ResultadoComparativoOOF(
        n_folds=len(umbrales),
        umbrales_por_fold=tuple(umbrales),
        cortocircuitados_oof=0,
        aciertos_det_oof=0,
        precision_det_oof=0.0,
        casos_gem_oof=0,
        aciertos_gem_oof=0,
        precision_gem_oof=0.0,
        cobertura_oof=0.0,
    )


# ---------------------------------------------------------------------------
# RED -> agregacion determinista de los umbrales por fold
# ---------------------------------------------------------------------------
def test_tau_oof_usa_el_valor_comun_cuando_los_folds_coinciden():
    resultado = _resultado(0.5, 0.5, 0.5)
    assert tau_oof_agregado(resultado) == pytest.approx(0.5)


def test_tau_oof_usa_el_minimo_cuando_los_folds_discrepan():
    """Regla documentada ante discrepancia: el minimo (punto menos restrictivo)."""
    resultado = _resultado(0.7, 0.5, 0.6)
    assert tau_oof_agregado(resultado) == pytest.approx(0.5)


def test_tau_oof_ignora_folds_sin_umbral_viable():
    resultado = _resultado(None, 0.5, 0.5, None)
    assert tau_oof_agregado(resultado) == pytest.approx(0.5)


def test_tau_oof_es_none_si_ningun_fold_tuvo_umbral():
    resultado = _resultado(None, None)
    assert tau_oof_agregado(resultado) is None
    assert umbral_de_settings_oof(resultado) is None


# ---------------------------------------------------------------------------
# RED -> el tau prohibido para Settings se trunca hacia abajo
# ---------------------------------------------------------------------------
def test_umbral_de_settings_oof_trunca_el_score_exacto_del_corpus():
    """El valor exacto del corpus (0.516666...) congela 0.5166 sin hardcodearlo."""
    resultado = _resultado(*([0.5166666666666666] * 5))
    exacto = tau_oof_agregado(resultado)
    assert exacto == pytest.approx(0.5166666666666666)
    assert umbral_de_settings_oof(resultado) == 0.5166
    assert umbral_de_settings_oof(resultado) <= exacto


@pytest.mark.parametrize(
    "exacto,esperado",
    [
        (0.9, 0.9),
        (0.5166666666666666, 0.5166),
        (0.123456, 0.1234),
        (1 / 3, 0.3333),
    ],
)
def test_umbral_de_settings_oof_nunca_redondea_hacia_arriba(exacto, esperado):
    resultado = _resultado(exacto, exacto)
    truncado = umbral_de_settings_oof(resultado)
    assert truncado == pytest.approx(esperado)
    assert truncado <= exacto


# ---------------------------------------------------------------------------
# RED -> resolucion de la cache de calibracion (dos-cache, c-74)
# ---------------------------------------------------------------------------
def test_resolver_prefiere_la_cache_de_calibracion_cuando_existe(tmp_path):
    """
    La calibracion comparativa NO puede usar la cache OFICIAL hybrid-v3: en esa
    corrida los 131 cortocircuitables no llaman a Gemini y `precision_gem(S)`
    degenera a 0/0. Por eso el resolver prefiere la cache FORCE-ESCALATE.
    """
    evaluacion = tmp_path / "evaluation"
    evaluacion.mkdir()
    oficial = evaluacion / "predicciones.json"
    calibracion = evaluacion / "predicciones_calibracion.json"
    oficial.write_text("{}", encoding="utf-8")
    calibracion.write_text("{}", encoding="utf-8")

    assert resolver_cache_calibracion(tmp_path) == calibracion


def test_resolver_cae_a_la_cache_oficial_si_falta_la_de_calibracion(tmp_path):
    evaluacion = tmp_path / "evaluation"
    evaluacion.mkdir()
    oficial = evaluacion / "predicciones.json"
    oficial.write_text("{}", encoding="utf-8")

    assert resolver_cache_calibracion(tmp_path) == oficial


def test_resolver_sin_ninguna_cache_devuelve_la_ruta_oficial(tmp_path):
    """Fallback documentado: sin caches devuelve la ruta oficial (fallara al cargar)."""
    assert resolver_cache_calibracion(tmp_path) == tmp_path / "evaluation" / "predicciones.json"


def test_constante_de_cache_de_calibracion_apunta_al_archivo_forzado():
    from pathlib import PurePosixPath

    ruta = PurePosixPath(str(CALIBRACION_CACHE_PATH))
    assert ruta == PurePosixPath("evaluation/predicciones_calibracion.json")


# ---------------------------------------------------------------------------
# RED -> el tau congelado en Settings tiene procedencia OOF verificable
# ---------------------------------------------------------------------------
_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
_CORPUS_REAL = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
_CALIBRACION = _REPO_ROOT / "evaluation" / "predicciones_calibracion.json"


@pytest.mark.skipif(
    not (_CORPUS_REAL.exists() and _CALIBRACION.exists()),
    reason=(
        "corpus/cache de calibracion locales ausentes (no trackeados en git); "
        "el test de procedencia solo corre con los datos reales"
    ),
)
async def test_settings_tau_deriva_del_oof_del_corpus(monkeypatch):
    """
    `Settings.deterministic_score_threshold` == tau derivado OUT-OF-FOLD.

    Usa la cache FORCE-ESCALATE (`predicciones_calibracion.json`) resuelta por el
    helper; sin ella la corrida oficial hybrid-v3 degenera `precision_gem` a 0/0.
    Atar la constante a la derivacion hace verificable su procedencia y reproduce
    los numeros comparativos reales: `precision_gem(S) = 0.6769 (88/130)`.
    """
    monkeypatch.setenv("DATABASE_URL", "postgresql+asyncpg://t:t@localhost:5432/t")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setenv(
        "PSEUDONYMIZATION_ENCRYPTION_KEY",
        "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
    )
    monkeypatch.setenv("JWT_SECRET_KEY", "dummy-jwt")

    from evaluation.deterministic_measurement import (
        _cargar_corpus_real,
        _resolver_clasificador_real,
        calibrar_comparativo_out_of_fold,
        cargar_predicciones_cacheadas,
        recolectar_observaciones,
    )

    # `_resolver_clasificador_real` agrega App/Backend al sys.path e importa el
    # clasificador real (sin invocar a Gemini).
    classifier = _resolver_clasificador_real()

    from app.config.settings import get_settings

    get_settings.cache_clear()

    cache_path = resolver_cache_calibracion(_REPO_ROOT)
    assert cache_path == _CALIBRACION

    corpus = _cargar_corpus_real()
    observaciones = await recolectar_observaciones(corpus, classifier)
    cache = cargar_predicciones_cacheadas(cache_path)
    gem_map = {
        caso_id: (p.sector_predicho if p.etapa == "gemini" else None)
        for caso_id, p in cache.items()
    }

    oof = calibrar_comparativo_out_of_fold(observaciones, gem_map)
    tau_oof = umbral_de_settings_oof(oof)

    assert tau_oof is not None
    assert get_settings().deterministic_score_threshold == tau_oof
    # Numeros comparativos reales (no degenerados): el determinista supera a
    # Gemini en el conjunto cortocircuitable con predicciones FORCE-ESCALATE.
    assert oof.precision_gem_oof == pytest.approx(88 / 130)
    assert oof.casos_gem_oof == 130
    assert oof.precision_det_oof == pytest.approx(97 / 131)
    assert tau_oof == 0.5166