"""
Tests para evaluation/run_evaluation.py — runner de evaluacion multietiqueta (C-27).

TDD — ciclos: RED -> GREEN -> TRIANGULATE -> REFACTOR
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: el runner recolecta una prediccion multietiqueta por caso
# ---------------------------------------------------------------------------
async def test_runner_recolecta_una_prediccion_por_caso(
    fake_classifier,
    corpus_fixture_path,
):
    """Por cada caso del corpus JSON, el runner registra exactamente una prediccion."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import CLASES
    from evaluation.run_evaluation import evaluar_corpus

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    assert len(predicciones) == len(corpus)

    for pred in predicciones:
        assert hasattr(pred, "sector_asignado")
        assert hasattr(pred, "sector_predicho")
        assert hasattr(pred, "sectores_adicionales")
        assert hasattr(pred, "confianza")
        assert hasattr(pred, "etapa")
        assert not hasattr(pred, "categoria_real")
        assert not hasattr(pred, "categoria_predicha")
        assert pred.sector_predicho in CLASES
        assert isinstance(pred.sectores_adicionales, list)
        for sector in pred.sectores_adicionales:
            assert sector in CLASES
        assert 0.0 <= pred.confianza <= 1.0
        assert pred.etapa in {"deterministic", "gemini", "fallback"}


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: el reporte expone todas las metricas multietiqueta
# ---------------------------------------------------------------------------
async def test_runner_genera_report_md_con_metricas(
    fake_classifier,
    corpus_fixture_path,
    tmp_path,
):
    """Tras correr, se escribe report.md con matriz 5x5, exactitud, subset, Hamming y F1."""
    from evaluation.corpus import cargar_corpus
    from evaluation.metrics import CLASES
    from evaluation.run_evaluation import evaluar_corpus, generar_reporte

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)

    reporte_path = tmp_path / "report.md"
    contenido = generar_reporte(predicciones, corpus, output_path=reporte_path)

    assert reporte_path.exists()
    assert "Exactitud" in contenido
    assert "Matriz" in contenido
    assert "Subset" in contenido or "subconjunto" in contenido.lower()
    assert "Hamming" in contenido
    assert "Micro" in contenido
    assert "Macro" in contenido
    for sector in CLASES:
        assert sector in contenido


# ---------------------------------------------------------------------------
# 7.8 RED -> 7.9 GREEN: corpus real ausente falla con mensaje claro
# ---------------------------------------------------------------------------
async def test_runner_corpus_real_ausente_falla_claro(fake_classifier, tmp_path):
    """Si el corpus JSON no existe, el runner falla claro y no inventa datos."""
    from evaluation.run_evaluation import main_con_corpus_real

    ruta_ausente = tmp_path / "corpus_ausente.json"
    with pytest.raises(FileNotFoundError, match="corpus_ausente.json"):
        await main_con_corpus_real(corpus_path=ruta_ausente, classifier=fake_classifier)


def test_ruta_canonica_del_corpus_real_es_json():
    """La ruta por defecto del corpus real debe apuntar al JSON, no al CSV."""
    from evaluation.run_evaluation import CORPUS_REAL_PATH

    assert CORPUS_REAL_PATH.suffix == ".json"
    assert CORPUS_REAL_PATH.name == "corpus_evaluacion_pseudonimizado.json"


# ---------------------------------------------------------------------------
# C-34 RED (1.1): cache hit omite la clasificacion
# ---------------------------------------------------------------------------
async def test_cache_hit_omite_clasificacion(corpus_fixture_path, tmp_path):
    """
    En la segunda corrida con cache valido, el clasificador NO recibe ninguna llamada.

    Usa SpyClassifier (subclase que cuenta llamadas) sobre el mismo corpus y tmp_path.
    Primera corrida: genera el cache. Segunda corrida: debe cargar del cache sin clasificar.
    """
    import shutil

    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import main_con_corpus_real

    class SpyClassifier(FakeClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        async def classify(self, descripcion: str) -> ClasificacionResultFake:
            self.call_count += 1
            return await super().classify(descripcion)

    casos = cargar_corpus(corpus_fixture_path)
    predicciones_map = {
        caso.descripcion: ClasificacionResultFake(
            sector_predicho=caso.sector_asignado,
            sectores_adicionales=list(caso.sectores_adicionales),
            confianza=0.95,
            etapa="deterministic",
        )
        for caso in casos
    }
    spy = SpyClassifier(predicciones=predicciones_map)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)

    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Primera corrida: genera el cache
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    calls_after_first = spy.call_count
    assert calls_after_first > 0, "La primera corrida debe invocar el clasificador"

    # Segunda corrida: debe usar el cache (sin clasificar)
    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count == 0, (
        f"La segunda corrida con cache valido NO debe invocar el clasificador, "
        f"pero se invoco {spy.call_count} veces"
    )


# ---------------------------------------------------------------------------
# C-34 RED (1.2): cambio en el corpus invalida el cache
# ---------------------------------------------------------------------------
async def test_cambio_en_corpus_invalida_cache(corpus_fixture_path, tmp_path):
    """
    Si el corpus cambia (nuevo caso dummy), el cache se invalida y el clasificador
    es invocado en la segunda corrida.
    """
    import json
    import shutil

    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import main_con_corpus_real

    class SpyClassifier(FakeClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        async def classify(self, descripcion: str) -> ClasificacionResultFake:
            self.call_count += 1
            return await super().classify(descripcion)

    spy = SpyClassifier(default_sector="Sistemas")

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Primera corrida: genera el cache
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )

    # Modificar el corpus: agregar un caso dummy
    data = json.loads(corpus_copy.read_text(encoding="utf-8"))
    data["casos"].append(
        {
            "id": "99",
            "descripcion": "Caso dummy para invalidar el cache",
            "canal_origen": "correo",
            "sector_asignado": "Sistemas",
            "sectores_adicionales": [],
            "tiempo_manual_s": 100,
            "tiempo_automatizado_s": 5,
        }
    )
    data["metadata"]["total_casos"] = len(data["casos"])
    corpus_copy.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Segunda corrida: corpus cambio, debe clasificar de nuevo
    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count > 0, (
        "Tras cambiar el corpus, el clasificador debe ser invocado (cache invalido)"
    )


# ---------------------------------------------------------------------------
# C-34 RED (1.3): flag force bypasea el cache valido
# ---------------------------------------------------------------------------
async def test_force_flag_bypasea_cache_valido(corpus_fixture_path, tmp_path):
    """
    Con force=True, el clasificador es invocado incluso cuando el cache es valido.
    """
    import shutil

    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import main_con_corpus_real

    class SpyClassifier(FakeClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        async def classify(self, descripcion: str) -> ClasificacionResultFake:
            self.call_count += 1
            return await super().classify(descripcion)

    casos = cargar_corpus(corpus_fixture_path)
    predicciones_map = {
        caso.descripcion: ClasificacionResultFake(
            sector_predicho=caso.sector_asignado,
            sectores_adicionales=list(caso.sectores_adicionales),
            confianza=0.95,
            etapa="deterministic",
        )
        for caso in casos
    }
    spy = SpyClassifier(predicciones=predicciones_map)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Primera corrida: genera el cache
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )

    # Segunda corrida con force=True: debe clasificar aunque el cache sea valido
    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
        force=True,
    )
    assert spy.call_count > 0, (
        "Con force=True, el clasificador DEBE ser invocado aunque el cache sea valido"
    )


# ---------------------------------------------------------------------------
# C-34 RED (1.4): predicciones.json contiene cache_meta con los campos requeridos
# ---------------------------------------------------------------------------
async def test_predicciones_json_incluye_cache_meta(corpus_fixture_path, tmp_path):
    """
    Tras una corrida, predicciones.json debe contener cache_meta con los campos:
    corpus_hash, corpus_count, classifier_version y generated_at.
    """
    import json
    import shutil

    from evaluation.tests.conftest import FakeClassifier
    from evaluation.run_evaluation import main_con_corpus_real

    spy = FakeClassifier(default_sector="Sistemas")

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )

    assert pred_path.exists(), "predicciones.json debe existir tras la corrida"
    data = json.loads(pred_path.read_text(encoding="utf-8"))

    assert "cache_meta" in data, "predicciones.json debe contener 'cache_meta'"
    meta = data["cache_meta"]
    assert "corpus_hash" in meta, "cache_meta debe contener 'corpus_hash'"
    assert "corpus_count" in meta, "cache_meta debe contener 'corpus_count'"
    assert "classifier_version" in meta, "cache_meta debe contener 'classifier_version'"
    assert "generated_at" in meta, "cache_meta debe contener 'generated_at'"
    assert isinstance(meta["corpus_hash"], str) and len(meta["corpus_hash"]) == 64
    assert isinstance(meta["corpus_count"], int)
    assert isinstance(meta["classifier_version"], str)
    assert "predictions" in data, "predicciones.json debe contener 'predictions'"
    assert isinstance(data["predictions"], list)


# ---------------------------------------------------------------------------
# C-34 RED (1.5): archivo sin cache_meta se considera invalido
# ---------------------------------------------------------------------------
async def test_predicciones_json_sin_cache_meta_se_considera_invalido(
    corpus_fixture_path, tmp_path
):
    """
    Un predicciones.json con formato antiguo (arreglo plano, sin cache_meta)
    se trata como cache invalido: el clasificador debe ser invocado.
    """
    import json
    import shutil

    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier
    from evaluation.run_evaluation import main_con_corpus_real

    class SpyClassifier(FakeClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        async def classify(self, descripcion: str) -> ClasificacionResultFake:
            self.call_count += 1
            return await super().classify(descripcion)

    spy = SpyClassifier(default_sector="Sistemas")

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Escribir un predicciones.json con formato antiguo (arreglo plano)
    legacy_data = [
        {
            "caso_id": "1",
            "descripcion": "desc",
            "sector_asignado": "Sistemas",
            "sector_predicho": "Sistemas",
            "confianza": 0.9,
            "etapa": "deterministic",
            "sectores_adicionales": [],
        }
    ]
    pred_path.write_text(json.dumps(legacy_data, ensure_ascii=False), encoding="utf-8")

    # El archivo existe pero sin cache_meta: debe clasificar de nuevo
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count > 0, (
        "Un predicciones.json sin cache_meta debe tratarse como invalido "
        "y el clasificador debe ser invocado"
    )


# ---------------------------------------------------------------------------
# C-34 TRIANGULATE (3.1): un cache hit produce el mismo reporte
# ---------------------------------------------------------------------------
async def test_cache_hit_produce_mismo_reporte(corpus_fixture_path, tmp_path):
    """Dos corridas con cache valido generan un report.md identico byte a byte."""
    import shutil

    from evaluation.tests.conftest import FakeClassifier
    from evaluation.run_evaluation import main_con_corpus_real

    spy = FakeClassifier(default_sector="Sistemas")
    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    first = report_path.read_bytes()

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    second = report_path.read_bytes()

    assert first == second, "Un cache hit debe regenerar un reporte identico"


# ---------------------------------------------------------------------------
# C-34 TRIANGULATE (3.2): un cambio en CACHE_VERSION invalida el cache
# ---------------------------------------------------------------------------
async def test_cambio_en_classifier_version_invalida_cache(corpus_fixture_path, tmp_path):
    """Si cambia CACHE_VERSION del clasificador, el cache se invalida."""
    import shutil

    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier
    from evaluation.run_evaluation import main_con_corpus_real

    class SpyClassifier(FakeClassifier):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.call_count = 0

        async def classify(self, descripcion: str) -> ClasificacionResultFake:
            self.call_count += 1
            return await super().classify(descripcion)

    spy = SpyClassifier(default_sector="Sistemas")
    spy.CACHE_VERSION = "v1"

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )

    # La version del clasificador cambia: el cache deja de ser valido
    spy.CACHE_VERSION = "v2"
    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count > 0, (
        "Cambiar CACHE_VERSION debe invalidar el cache y re-clasificar"
    )


# ---------------------------------------------------------------------------
# C-34 TRIANGULATE (3.3): --force y --no-cache son equivalentes en el CLI
# ---------------------------------------------------------------------------
def test_no_cache_flag_es_equivalente_a_force(monkeypatch):
    """Tanto --force como --no-cache mapean a force=True en el CLI."""
    import sys

    from evaluation import run_evaluation

    captured: dict = {}

    async def fake_main(*args, **kwargs):
        captured["force"] = kwargs.get("force")

    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_main)

    for flag in ("--force", "--no-cache"):
        captured.clear()
        monkeypatch.setattr(sys, "argv", ["run_evaluation", flag])
        run_evaluation.main()
        assert captured.get("force") is True, f"{flag} debe mapear a force=True"
