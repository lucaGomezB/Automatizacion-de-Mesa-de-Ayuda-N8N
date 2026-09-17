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


# ===========================================================================
# C-36 — Gate de corrida paga y estimacion de costo
#
# Condicion del gate: la corrida invocaria al clasificador (cache miss o
# `force=True`) Y `classifier is None` (se resolveria el HybridClassifier real).
# Un cache hit no exige confirmacion. Un clasificador inyectado tampoco.
# ===========================================================================
def _spy_paid_classifier(corpus_path):
    """Spy que simula el clasificador real: cuenta invocaciones."""
    from evaluation.corpus import cargar_corpus
    from evaluation.tests.conftest import ClasificacionResultFake, FakeClassifier

    casos = cargar_corpus(corpus_path)
    predicciones = {
        caso.descripcion: ClasificacionResultFake(
            sector_predicho=caso.sector_asignado,
            sectores_adicionales=list(caso.sectores_adicionales),
            confianza=0.95,
            etapa="deterministic",
        )
        for caso in casos
    }

    class SpyPaidClassifier(FakeClassifier):
        def __init__(self):
            super().__init__(predicciones=predicciones)
            self.call_count = 0

        async def classify(self, descripcion):
            self.call_count += 1
            return await super().classify(descripcion)

    return SpyPaidClassifier()


def _resolver_a(monkeypatch, spy):
    import evaluation.run_evaluation as run_evaluation

    monkeypatch.setattr(
        run_evaluation, "_resolver_clasificador_real", lambda: spy
    )
    # W-3: el camino real lee la version sin construir el clasificador; los
    # tests la fijan a la version del spy para conservar la semantica del cache.
    monkeypatch.setattr(
        run_evaluation,
        "_version_clasificador_real",
        lambda: run_evaluation._get_classifier_version(spy),
    )


async def test_cache_miss_sin_confirmacion_rechaza_y_no_clasifica(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """3.1: cache miss + clasificador real + sin confirmacion -> rechazo sin invocar."""
    import shutil

    import evaluation.run_evaluation as run_evaluation
    from evaluation.run_evaluation import PaidRunNotConfirmedError, main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)

    with pytest.raises(PaidRunNotConfirmedError) as exc_info:
        await main_con_corpus_real(
            corpus_path=corpus_copy,
            classifier=None,
            report_path=tmp_path / "report.md",
            predicciones_path=tmp_path / "predicciones.json",
        )

    assert spy.call_count == 0, "El gate no debe invocar al clasificador pago"
    mensaje = str(exc_info.value)
    assert "--confirm-paid" in mensaje
    assert "EVALUATION_CONFIRM_PAID" in mensaje


async def test_cache_hit_sin_confirmacion_usa_cache(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """3.2: cache valido + sin confirmacion -> carga cache, no invoca, no exige."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Genera el cache con el clasificador inyectado (no hay gate en ese camino).
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count > 0

    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=None,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count == 0, "Un cache hit no debe invocar al clasificador"


async def test_confirm_paid_true_permite_corrida_paga(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """3.3 (nucleo): confirm_paid=True habilita la corrida paga."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=None,
        report_path=tmp_path / "report.md",
        predicciones_path=tmp_path / "predicciones.json",
        confirm_paid=True,
    )
    assert spy.call_count > 0, "Con confirmacion la corrida paga debe clasificar"


def _capture_cli_confirmation(monkeypatch, argv, env_value):
    import sys

    import evaluation.run_evaluation as run_evaluation

    captured: dict = {}

    async def fake_main(*args, **kwargs):
        captured["confirm_paid"] = kwargs.get("confirm_paid")

    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_main)
    if env_value is None:
        monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    else:
        monkeypatch.setenv("EVALUATION_CONFIRM_PAID", env_value)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", *argv])
    run_evaluation.main()
    return captured.get("confirm_paid")


def test_cli_confirm_paid_por_flag(monkeypatch):
    """3.3: `--confirm-paid` mapea a confirm_paid=True en el CLI."""
    assert _capture_cli_confirmation(monkeypatch, ["--confirm-paid"], None) is True


def test_cli_confirm_paid_por_entorno(monkeypatch):
    """3.3: `EVALUATION_CONFIRM_PAID=1` habilita la corrida paga."""
    assert _capture_cli_confirmation(monkeypatch, [], "1") is True


def test_cli_confirm_paid_env_case_insensitive(monkeypatch):
    """3.3: valores `true`/`yes` en cualquier casing son verdaderos."""
    assert _capture_cli_confirmation(monkeypatch, [], "YES") is True
    assert _capture_cli_confirmation(monkeypatch, [], "True") is True


def test_cli_confirm_paid_valor_falso(monkeypatch):
    """3.3: un valor no listado no habilita la corrida paga."""
    assert _capture_cli_confirmation(monkeypatch, [], "0") is False


def test_cli_gate_rechazado_sale_con_codigo_2(monkeypatch, capsys):
    """4.3: el CLI captura el rechazo, imprime mensaje accionable y sale 2."""
    import sys

    import evaluation.run_evaluation as run_evaluation
    from evaluation.run_evaluation import PaidRunNotConfirmedError

    async def fake_main(*args, **kwargs):
        raise PaidRunNotConfirmedError(
            "Corrida paga sin confirmar: usa --confirm-paid o EVALUATION_CONFIRM_PAID"
        )

    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_main)
    monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    monkeypatch.setattr(sys, "argv", ["run_evaluation"])

    with pytest.raises(SystemExit) as exc_info:
        run_evaluation.main()
    assert exc_info.value.code == 2
    salida = capsys.readouterr()
    assert "--confirm-paid" in (salida.out + salida.err)


async def test_clasificador_inyectado_no_exige_confirmacion(
    corpus_fixture_path, tmp_path
):
    """3.4 (regresion): un clasificador inyectado clasifica sin confirmacion."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=tmp_path / "report.md",
        predicciones_path=tmp_path / "predicciones.json",
    )
    assert spy.call_count > 0


async def test_force_con_clasificador_real_sin_confirmacion_rechaza(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """3.5: `force=True` no sustituye la confirmacion de corrida paga."""
    import shutil

    from evaluation.run_evaluation import PaidRunNotConfirmedError, main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Genera un cache valido (con clasificador inyectado).
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    spy.call_count = 0

    with pytest.raises(PaidRunNotConfirmedError):
        await main_con_corpus_real(
            corpus_path=corpus_copy,
            classifier=None,
            report_path=report_path,
            predicciones_path=pred_path,
            force=True,
        )
    assert spy.call_count == 0


def test_estimated_cost_usd_es_lineal():
    """3.6: la estimacion es `casos * costo_por_llamada`."""
    from evaluation.run_evaluation import (
        ESTIMATED_COST_PER_CALL_USD,
        estimated_cost_usd,
    )

    assert ESTIMATED_COST_PER_CALL_USD > 0
    assert estimated_cost_usd(0) == 0.0
    assert estimated_cost_usd(10) == pytest.approx(10 * ESTIMATED_COST_PER_CALL_USD)


async def test_estimacion_impresa_antes_de_corrida_paga(
    corpus_fixture_path, tmp_path, monkeypatch, capsys
):
    """3.6: antes de clasificar se imprime la cantidad de casos y el costo."""
    import shutil

    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    casos = len(cargar_corpus(corpus_copy))

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=None,
        report_path=tmp_path / "report.md",
        predicciones_path=tmp_path / "predicciones.json",
        confirm_paid=True,
    )

    salida = capsys.readouterr().out
    assert "Estimacion de costo" in salida
    assert str(casos) in salida
    assert "USD" in salida


async def test_cache_hit_no_imprime_costo_pago(
    corpus_fixture_path, tmp_path, monkeypatch, capsys
):
    """3.6: un cache hit no reporta estimacion de costo pago."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    _resolver_a(monkeypatch, spy)

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
    capsys.readouterr()  # descarta la salida de la primera corrida

    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=None,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert "Estimacion de costo" not in capsys.readouterr().out


# ===========================================================================
# W-3 (fix post-verificacion): un cache hit no resuelve el clasificador real
# ===========================================================================
async def test_cache_hit_no_resuelve_clasificador_real(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """W-3: con cache valido y classifier=None no se construye el clasificador real.

    Un cache hit no debe exigir GEMINI_API_KEY: la resolucion del HybridClassifier
    real (que construye GeminiClassifier y llama a get_settings) debe ocurrir solo
    cuando la corrida paga realmente va a clasificar. Aqui el resolver real se
    fuerza a explotar y el runner debe igualmente cargar del cache.
    """
    import shutil

    import evaluation.run_evaluation as run_evaluation
    from evaluation.run_evaluation import main_con_corpus_real

    spy = _spy_paid_classifier(corpus_fixture_path)
    # La version del cache se toma del camino real, sin credenciales. En el
    # codigo previo al fix el helper no existe y se usa el valor canonico para
    # que el RED sea el resolver real invocado antes del cache.
    version_real = getattr(
        run_evaluation, "_version_clasificador_real", lambda: "hybrid-v1"
    )()
    spy.CACHE_VERSION = version_real

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    pred_path = tmp_path / "predicciones.json"
    report_path = tmp_path / "report.md"

    # Primera corrida con clasificador inyectado: genera el cache.
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=spy,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count > 0

    # Segunda corrida: cache valido, classifier=None y resolver real que explota.
    def _resolver_que_explota():
        raise RuntimeError(
            "un cache hit no debe construir el clasificador real"
        )

    monkeypatch.setattr(
        run_evaluation, "_resolver_clasificador_real", _resolver_que_explota
    )
    spy.call_count = 0
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=None,
        report_path=report_path,
        predicciones_path=pred_path,
    )
    assert spy.call_count == 0, "Un cache hit no debe invocar al clasificador"


def test_version_clasificador_real_no_exige_credenciales():
    """W-3: leer la version del clasificador real no carga app.core.database.

    Esta suite corre sin variables de entorno ni .env; si el helper importara
    app.classifiers, get_settings fallaria por credenciales ausentes.
    """
    import sys

    from evaluation import run_evaluation

    version = run_evaluation._version_clasificador_real()
    assert isinstance(version, str) and version
    assert "app.core.database" not in sys.modules, (
        "leer la version real no debe importar app.core.database (exige credenciales)"
    )
