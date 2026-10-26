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


def test_version_de_cache_comparativa_es_hybrid_v3():
    """c-74 (4.2/4.3): el cambio de senal de seleccion sube la version a hybrid-v3."""
    from evaluation.run_evaluation import _version_clasificador_real

    assert _version_clasificador_real() == "hybrid-v3"


def test_cache_de_politica_previa_v2_es_invalido(tmp_path):
    """c-74 (4.3): un cache hybrid-v2 deja de ser valido para el runner v3."""
    import json

    from evaluation.run_evaluation import _is_cache_valid

    path = tmp_path / "predicciones.json"
    path.write_text(
        json.dumps(
            {
                "cache_meta": {
                    "corpus_hash": "h",
                    "corpus_count": 1,
                    "classifier_version": "hybrid-v2",
                },
                "predictions": [],
            }
        ),
        encoding="utf-8",
    )
    assert _is_cache_valid(path, "h", 1, "hybrid-v3") is False
    assert _is_cache_valid(path, "h", 1, "hybrid-v2") is True


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


# ===========================================================================
# c-99 — Sección "Tiempos" del reporte (normalidad + Wilcoxon + divulgación + canal)
# ===========================================================================
def _caso_tiempo(caso_id: str, canal: str, manual, automatizado, sector: str = "Sistemas"):
    """Construye un CasoEvaluacion con tiempos y canal dados."""
    from evaluation.corpus import CasoEvaluacion

    return CasoEvaluacion(
        id=str(caso_id),
        descripcion=f"caso {caso_id}",
        sector_asignado=sector,
        sectores_adicionales=[],
        canal_origen=canal,
        tiempo_manual_s=manual,
        tiempo_automatizado_s=automatizado,
    )


def _reporte_sintetico(corpus, tmp_path, corpus_hash=None):
    """Genera un reporte para un corpus sintético con predicciones triviales."""
    from evaluation.run_evaluation import Prediccion, generar_reporte

    predicciones = [
        Prediccion(
            caso_id=caso.id,
            descripcion=caso.descripcion,
            sector_asignado=caso.sector_asignado,
            sector_predicho=caso.sector_asignado,
            confianza=0.9,
            etapa="deterministic",
            sectores_adicionales=[],
        )
        for caso in corpus
    ]
    return generar_reporte(
        predicciones, corpus, output_path=tmp_path / "report.md", corpus_hash=corpus_hash
    )


def test_generar_reporte_emite_seccion_tiempos(tmp_path):
    """2.1: el reporte incluye la sección Tiempos con Shapiro, Wilcoxon y campos."""
    corpus = [_caso_tiempo(i, "A", 100.0 + i, 10.0) for i in range(1, 6)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "## Tiempos" in contenido
    assert "Shapiro" in contenido
    assert "Wilcoxon" in contenido
    assert "rank-biserial" in contenido
    assert "| n | W | T+ | T− | p | r |" in contenido


async def test_dos_corridas_incluyen_tiempos_y_son_identicas(corpus_fixture_path, tmp_path):
    """2.2: dos corridas producen un reporte idéntico byte a byte con Tiempos."""
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

    assert first == second, "Dos corridas con cache válido deben ser idénticas byte a byte"
    assert "## Tiempos" in first.decode("utf-8")


async def test_seccion_tiempos_no_altera_metricas_de_clasificacion(
    fake_classifier, corpus_fixture_path, tmp_path
):
    """2.3: agregar Tiempos no cambia las métricas de clasificación del fixture."""
    from evaluation.corpus import cargar_corpus
    from evaluation.run_evaluation import evaluar_corpus, generar_reporte

    corpus = cargar_corpus(corpus_fixture_path)
    predicciones = await evaluar_corpus(corpus, fake_classifier)
    contenido = generar_reporte(predicciones, corpus, output_path=tmp_path / "report.md")

    # Constantes del fixture con clasificador perfecto (previas a esta sección).
    assert "- **Exactitud (estricta):** 1.0000 (100.0%)" in contenido
    assert "- **Aciertos (estrictos):** 9 / 9" in contenido
    assert "- **Subset accuracy:** 1.0000" in contenido
    assert "- **Hamming loss:** 0.0000" in contenido
    assert "- **Micro-F1:** 1.0000" in contenido
    assert "- **Macro-F1:** 1.0000" in contenido
    assert "- **Jaccard (IoU) promedio:** 1.0000" in contenido
    # La sección nueva es aditiva.
    assert "## Tiempos" in contenido


def test_seccion_tiempos_divulga_redondeo_y_pares_no_rapidos(tmp_path):
    """2.4: divulga el redondeo al alza, la reducción conservadora y los pares."""
    corpus = [
        _caso_tiempo(1, "A", 100.0, 10.0),
        _caso_tiempo(2, "A", 100.0, 120.0),  # automatizado NO fue más rápido
    ]

    contenido = _reporte_sintetico(corpus, tmp_path).lower()

    assert "redondeo" in contenido
    assert "al alza" in contenido
    assert "conservadora" in contenido
    assert "invertidos/empatados" in contenido


def test_seccion_tiempos_lista_desglose_por_canal(tmp_path):
    """2.5: el reporte lista por canal sus pares y el resultado de Wilcoxon."""
    corpus = [
        _caso_tiempo(1, "correo", 100.0, 10.0),
        _caso_tiempo(2, "correo", 110.0, 11.0),
        _caso_tiempo(3, "llamada", 120.0, 12.0),
        _caso_tiempo(4, "llamada", 130.0, 13.0),
        _caso_tiempo(5, "formulario", 140.0, 14.0),
        _caso_tiempo(6, "formulario", 150.0, 15.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "### Desglose por canal" in contenido
    assert "| Canal | Pares válidos | W | T+ | T− | p | r |" in contenido
    for canal in ("correo", "llamada", "formulario"):
        assert canal in contenido


def test_seccion_tiempos_valores_calculados_a_mano(tmp_path):
    """
    4.2 TRIANGULATE: corpus de 5 pares con rangos conocidos.
    Diferencias manual-automatizado: +10, +20, +30, +40, -50.
    T+ = 10, T- = 5, W = 5, n = 5, r = 1/3, p exacto = 0.625.
    Reducción reportada media = 10.0; conservadora media = 9.0.
    """
    corpus = [
        _caso_tiempo(1, "A", 110.0, 100.0),
        _caso_tiempo(2, "A", 120.0, 100.0),
        _caso_tiempo(3, "A", 130.0, 100.0),
        _caso_tiempo(4, "A", 140.0, 100.0),
        _caso_tiempo(5, "A", 10.0, 60.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path, corpus_hash="abc123")

    assert "| 5 | 5.0000 | 10.0000 | 5.0000 | 0.625 | 0.3333 |" in contenido
    # Reducción reportada (media) = 10.00 s; conservadora (media) = 9.00 s.
    assert "10.00" in contenido
    assert "9.00" in contenido
    # El SHA-256 del corpus se emite cuando se pasa el hash.
    assert "SHA-256 del corpus" in contenido
    assert "abc123" in contenido


def test_seccion_tiempos_canal_con_pares_insuficientes_no_aplicable(tmp_path):
    """
    4.2 TRIANGULATE: un canal con un solo par declara "no aplicable"; un caso
    con tiempo nulo se excluye y se contabiliza.
    """
    corpus = [
        _caso_tiempo(1, "A", 110.0, 100.0),
        _caso_tiempo(2, "A", 120.0, 100.0),
        _caso_tiempo(3, "B", 130.0, 10.0),   # un solo par válido -> no aplicable
        _caso_tiempo(4, "C", None, 10.0),     # tiempo nulo -> excluido
    ]

    contenido = _reporte_sintetico(corpus, tmp_path).lower()

    assert "| b | 1 | no aplicable |" in contenido
    assert "excluido" in contenido


def test_generar_reporte_sin_hash_omite_sha256(tmp_path):
    """D3: sin `corpus_hash` la línea de SHA-256 se omite (compatibilidad)."""
    corpus = [_caso_tiempo(i, "A", 100.0 + i, 10.0) for i in range(1, 6)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "## Tiempos" in contenido
    assert "SHA-256 del corpus" not in contenido


# ===========================================================================
# c-134 — Sección "Tiempos": descriptivos, contraste direccional, d_z, MDE,
#         sensibilidad del redondeo manual y granularidad (aditiva)
# ===========================================================================
_H_DESCRIPTIVOS = "### Descriptivos global y por canal"
_H_CONTRASTE = "### Contraste direccional y tamaño del efecto estandarizado"
_H_SENSIBILIDAD = "### Escenarios de sensibilidad del redondeo manual"


def _corpus_cinco_pares_a_mano():
    """
    Corpus de 5 pares (un solo canal "A") con valores calculables a mano.

    Manual [110, 120, 130, 140, 10]; automatizado [100, 100, 100, 100, 60].
    Diferencias +10, +20, +30, +40, -50 (T+ = 10, T- = 5, W = 5).
    """
    manual = [110.0, 120.0, 130.0, 140.0, 10.0]
    automatizado = [100.0, 100.0, 100.0, 100.0, 60.0]
    return [
        _caso_tiempo(i + 1, "A", m, a)
        for i, (m, a) in enumerate(zip(manual, automatizado))
    ]


def _filas(contenido: str, encabezado: str) -> list:
    """Líneas de tabla ('| ...') del bloque que sigue a `encabezado`."""
    lineas = contenido.splitlines()
    inicio = lineas.index(encabezado) + 1
    filas = []
    for linea in lineas[inicio:]:
        if linea.startswith("### ") or linea.startswith("- **SHA-256"):
            break
        if linea.startswith("|"):
            filas.append(linea)
    return filas


def test_c134_reporte_incluye_subsecciones_nuevas_en_orden(tmp_path):
    """
    3.1 RED: las tres subsecciones nuevas aparecen después del desglose por
    canal y antes de la línea del SHA-256; en las tablas la fila "Global" va
    primero y luego los canales en el orden canónico de c-99 (conteo
    descendente, desempate alfabético): aquí "B" (3 pares) antes que "A" (2).
    """
    corpus = [
        _caso_tiempo(1, "A", 100.0, 10.0),
        _caso_tiempo(2, "A", 120.0, 20.0),
        _caso_tiempo(3, "B", 90.0, 15.0),
        _caso_tiempo(4, "B", 95.0, 12.0),
        _caso_tiempo(5, "B", 130.0, 30.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path, corpus_hash="abc123")

    posiciones = [
        contenido.index("### Desglose por canal"),
        contenido.index(_H_DESCRIPTIVOS),
        contenido.index(_H_CONTRASTE),
        contenido.index(_H_SENSIBILIDAD),
        contenido.index("SHA-256 del corpus"),
    ]
    assert posiciones == sorted(posiciones)

    for encabezado in (_H_DESCRIPTIVOS, _H_CONTRASTE):
        filas_datos = _filas(contenido, encabezado)[2:]  # sin cabecera ni separador
        etiquetas = [f.split("|")[1].strip() for f in filas_datos]
        assert etiquetas == ["Global", "B", "A"]


def test_c134_contraste_declara_supuestos_del_minimo_detectable(tmp_path):
    """3.1 RED: el reporte declara alfa, potencia, lateralidad y ARE del MDE."""
    corpus = [_caso_tiempo(i, "A", 100.0 + i, 10.0) for i in range(1, 6)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "alfa = 0.05 (bilateral)" in contenido
    assert "potencia = 0.80" in contenido
    assert "ARE = 0.864" in contenido
    encabezado = [f for f in _filas(contenido, _H_CONTRASTE) if f.startswith("| Ámbito")]
    assert encabezado == [
        "| Ámbito | n | p bilateral | p unilateral | d_z | MDE (ARE = 1) | MDE (ARE = 0.864) |"
    ]


def test_c134_valores_calculados_a_mano_descriptivos_y_contraste(tmp_path):
    """
    3.1 RED: corpus de 5 pares (ver `_corpus_cinco_pares_a_mano`).

    Manual: media 510/5 = 102, mediana 120, desvío muestral
        sqrt(11080/4) = 52.6308, mín 10, máx 140.
    Automatizado: media 460/5 = 92, mediana 100, desvío sqrt(1280/4) = 17.8885,
        mín 60, máx 100.
    Reducción relativa de la media: 1 - 92/102 = 9.80 %; de la mediana:
        1 - 100/120 = 16.67 %. Pares no más rápidos: 60 >= 10 -> 1.
    Contraste: p bilateral exacto 0.625, p unilateral 10/32 = 0.3125 -> "0.312".
    d_z = media(d) / desvío(d) = 10 / sqrt(5000/4) = 10 / 35.3553 = 0.2828.
    MDE (n = 5): (1.95996 + 0.84162) / sqrt(5) = 1.2529; con ARE 0.864:
        2.80158 / sqrt(4.32) = 1.3479.
    """
    contenido = _reporte_sintetico(_corpus_cinco_pares_a_mano(), tmp_path)

    assert (
        "| Global | 5 | 102.0000 | 120.0000 | 52.6308 | 10.0000 | 140.0000 "
        "| 92.0000 | 100.0000 | 17.8885 | 60.0000 | 100.0000 | 9.80 | 16.67 | 1 |"
    ) in contenido
    assert (
        "| Global | 5 | 0.625 | 0.312 | 0.2828 | 1.2529 | 1.3479 |"
    ) in contenido


def test_c134_sensibilidad_y_granularidad_calculadas_a_mano(tmp_path):
    """
    3.1 RED: manual [30, 40, 50] vs automatizado [10, 10, 10].

    Descuento 5 s: manual [25, 35, 45], media 35; reducción 1 - 10/35 = 71.43 %;
        diferencias 15, 25, 35 (todas positivas, n = 3): p bilateral 2/8 = 0.25,
        p unilateral 1/8 = 0.125, r = (6 - 0) / 6 = 1.
    Descuento 10 s: manual [20, 30, 40], media 30; reducción 1 - 10/30 = 66.67 %.
    Granularidad: 30, 40, 50 son múltiplos de 5 (3 / 3) y de 10 (3 / 3).
    """
    corpus = [
        _caso_tiempo(1, "A", 30.0, 10.0),
        _caso_tiempo(2, "A", 40.0, 10.0),
        _caso_tiempo(3, "A", 50.0, 10.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "| 5 | 35.0000 | 71.43 | 0.25 | 0.125 | 1.0000 |" in contenido
    assert "| 10 | 30.0000 | 66.67 | 0.25 | 0.125 | 1.0000 |" in contenido
    assert (
        "- Granularidad de `tiempo_manual_s`: 3 / 3 valores múltiplos de 5 s; "
        "3 / 3 múltiplos de 10 s."
    ) in contenido


def test_c134_granularidad_distingue_multiplos_de_5_y_de_10(tmp_path):
    """3.1 RED: manual [10, 15, 20, 23] -> múltiplos de 5: 3 / 4, de 10: 2 / 4."""
    corpus = [
        _caso_tiempo(i + 1, "A", m, 5.0) for i, m in enumerate([10.0, 15.0, 20.0, 23.0])
    ]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert (
        "- Granularidad de `tiempo_manual_s`: 3 / 4 valores múltiplos de 5 s; "
        "2 / 4 múltiplos de 10 s."
    ) in contenido


def test_c134_no_regresion_de_las_tablas_previas_de_tiempos(tmp_path):
    """
    3.2 RED: las cabeceras, la fila exacta y la tabla de reducción conservadora
    de 1 s de c-99 se conservan literalmente, y las subsecciones nuevas no se
    intercalan antes del desglose por canal.
    """
    contenido = _reporte_sintetico(_corpus_cinco_pares_a_mano(), tmp_path)

    assert "| n | W | T+ | T− | p | r |" in contenido
    assert "| Canal | Pares válidos | W | T+ | T− | p | r |" in contenido
    assert "| 5 | 5.0000 | 10.0000 | 5.0000 | 0.625 | 0.3333 |" in contenido
    assert "| Métrica | Reportada (s) | Conservadora (s) |" in contenido
    assert "| Reducción media | 10.00 | 9.00 |" in contenido
    assert contenido.index("### Reducción de tiempos") < contenido.index(
        "### Desglose por canal"
    ) < contenido.index(_H_DESCRIPTIVOS)


def test_c134_canal_con_un_unico_par_declara_no_aplicable_sin_romper_tablas(tmp_path):
    """
    3.4 TRIANGULATE: el canal "B" tiene un único par: desvío (manual y
    automatizado), d_z y p son "no aplicable"; las medias, el mínimo detectable
    (n = 1: 2.80158 -> 2.8016; con ARE 0.864: 2.80158 / sqrt(0.864) = 3.0140) y la fila Global siguen presentes.
    """
    corpus = [
        _caso_tiempo(1, "A", 110.0, 100.0),
        _caso_tiempo(2, "A", 120.0, 100.0),
        _caso_tiempo(3, "B", 130.0, 10.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path)

    fila_b_contraste = [
        f for f in _filas(contenido, _H_CONTRASTE) if f.startswith("| B |")
    ]
    assert fila_b_contraste == [
        "| B | 1 | no aplicable | no aplicable | no aplicable | 2.8016 | 3.0140 |"
    ]
    fila_b_descriptivos = [
        f for f in _filas(contenido, _H_DESCRIPTIVOS) if f.startswith("| B |")
    ]
    assert fila_b_descriptivos == [
        "| B | 1 | 130.0000 | 130.0000 | no aplicable | 130.0000 | 130.0000 "
        "| 10.0000 | 10.0000 | no aplicable | 10.0000 | 10.0000 | 92.31 | 92.31 | 0 |"
    ]
    assert any(f.startswith("| Global | 3 |") for f in _filas(contenido, _H_CONTRASTE))


def test_c134_caso_con_tiempo_nulo_se_excluye_del_canal_y_del_global(tmp_path):
    """
    3.4 TRIANGULATE: un caso sin tiempo manual no entra en las tablas nuevas:
    Global n = 2 y el canal "C" no aparece (su único caso es nulo).
    """
    corpus = [
        _caso_tiempo(1, "A", 110.0, 100.0),
        _caso_tiempo(2, "A", 120.0, 100.0),
        _caso_tiempo(3, "C", None, 10.0),
    ]

    contenido = _reporte_sintetico(corpus, tmp_path)

    for encabezado in (_H_DESCRIPTIVOS, _H_CONTRASTE):
        etiquetas = [f.split("|")[1].strip() for f in _filas(contenido, encabezado)[2:]]
        assert etiquetas == ["Global", "A"]
        assert any(f.startswith("| Global | 2 |") for f in _filas(contenido, encabezado))
    assert "2 / 2 valores" in contenido  # granularidad sobre los pares válidos


def test_c134_corpus_sin_pares_validos_no_rompe_las_tablas_nuevas(tmp_path):
    """3.4 TRIANGULATE: sin pares válidos, Global declara todo "no aplicable"."""
    corpus = [_caso_tiempo(1, "A", None, None)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    fila_global = [f for f in _filas(contenido, _H_CONTRASTE) if f.startswith("| Global |")]
    assert fila_global == [
        "| Global | 0 | no aplicable | no aplicable | no aplicable "
        "| no aplicable | no aplicable |"
    ]
    assert _H_SENSIBILIDAD in contenido


async def test_c134_dos_corridas_son_identicas_e_incluyen_subsecciones_nuevas(
    corpus_fixture_path, tmp_path
):
    """3.4: las subsecciones nuevas no rompen el determinismo byte a byte."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real
    from evaluation.tests.conftest import FakeClassifier

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    report_path = tmp_path / "report.md"
    spy = FakeClassifier(default_sector="Sistemas")

    resultados = []
    for _ in range(2):
        await main_con_corpus_real(
            corpus_path=corpus_copy,
            classifier=spy,
            report_path=report_path,
            predicciones_path=tmp_path / "predicciones.json",
        )
        resultados.append(report_path.read_bytes())

    assert resultados[0] == resultados[1]
    texto = resultados[0].decode("utf-8")
    for encabezado in (_H_DESCRIPTIVOS, _H_CONTRASTE, _H_SENSIBILIDAD):
        assert encabezado in texto


def test_c134_sensibilidad_con_descuento_mayor_al_manual_invierte_el_signo(tmp_path):
    """
    3.4 TRIANGULATE: manual [15, 15] vs automatizado [10, 10], descuento 10 s:
    manual ajustado [5, 5] (media 5), reducción 1 - 10/5 = -100 %, diferencias
    -5, -5 (todas negativas, n = 2): T+ = 0, r = (0 - 3) / 3 = -1, p
    unilateral 1 y p bilateral exacto 2/4 = 0.5.
    """
    corpus = [_caso_tiempo(1, "A", 15.0, 10.0), _caso_tiempo(2, "A", 15.0, 10.0)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    assert "| 10 | 5.0000 | -100.00 | 0.5 | 1 | -1.0000 |" in contenido


def test_c134_sensibilidad_declara_no_aplicable_si_el_contraste_es_degenerado(
    tmp_path, monkeypatch
):
    """
    3.4 TRIANGULATE: si el contraste del escenario no es calculable (ValueError
    del cálculo, por ejemplo diferencias ajustadas todas nulas en versiones de
    scipy que lo rechazan), la fila se declara "no aplicable" sin romper la tabla.
    """
    from evaluation import run_evaluation

    def _degenerado(*args, **kwargs):
        raise ValueError("contraste degenerado")

    monkeypatch.setattr(run_evaluation, "escenario_sensibilidad", _degenerado)
    corpus = [_caso_tiempo(1, "A", 15.0, 10.0), _caso_tiempo(2, "A", 20.0, 10.0)]

    contenido = _reporte_sintetico(corpus, tmp_path)

    na = " | ".join(["no aplicable"] * 5)
    assert f"| 5 | {na} |" in contenido
    assert f"| 10 | {na} |" in contenido


# ===========================================================================
# c-134 — Huella del corpus independiente del fin de línea (D6)
# ===========================================================================
_CORPUS_JSON_LF = '{\n  "casos": [\n    {"id": "1", "tiempo_manual_s": 10}\n  ]\n}\n'


def test_c134_huella_crlf_y_lf_son_iguales_y_canonicas(tmp_path):
    """
    4.1 RED: el mismo JSON con fines de línea CRLF y LF produce la misma huella,
    igual al SHA-256 del contenido con LF (la del blob versionado).
    """
    import hashlib

    from evaluation.run_evaluation import _compute_corpus_hash

    bytes_lf = _CORPUS_JSON_LF.encode("utf-8")
    ruta_lf = tmp_path / "corpus_lf.json"
    ruta_crlf = tmp_path / "corpus_crlf.json"
    ruta_lf.write_bytes(bytes_lf)
    ruta_crlf.write_bytes(bytes_lf.replace(b"\n", b"\r\n"))

    esperada = hashlib.sha256(bytes_lf).hexdigest()
    assert _compute_corpus_hash(ruta_lf) == esperada
    assert _compute_corpus_hash(ruta_crlf) == esperada


def test_c134_huella_cambia_si_cambia_el_contenido(tmp_path):
    """4.1 TRIANGULATE: una diferencia real de contenido sí cambia la huella."""
    from evaluation.run_evaluation import _compute_corpus_hash

    original = tmp_path / "a.json"
    modificado = tmp_path / "b.json"
    original.write_bytes(_CORPUS_JSON_LF.encode("utf-8"))
    modificado.write_bytes(
        _CORPUS_JSON_LF.replace('"tiempo_manual_s": 10', '"tiempo_manual_s": 15')
        .replace("\n", "\r\n")
        .encode("utf-8")
    )

    assert _compute_corpus_hash(original) != _compute_corpus_hash(modificado)


def test_c134_cache_con_huella_previa_queda_invalido_tras_cambio_de_contenido(tmp_path):
    """
    4.1 TRIANGULATE: un cache guardado con la huella del contenido original
    deja de ser válido cuando el corpus cambia de contenido, pero sigue siendo
    válido para una copia CRLF del mismo contenido.
    """
    import json

    from evaluation.run_evaluation import _compute_corpus_hash, _is_cache_valid

    bytes_lf = _CORPUS_JSON_LF.encode("utf-8")
    ruta = tmp_path / "corpus.json"
    ruta.write_bytes(bytes_lf)
    huella_original = _compute_corpus_hash(ruta)
    cache = tmp_path / "predicciones.json"
    cache.write_text(
        json.dumps(
            {
                "cache_meta": {
                    "corpus_hash": huella_original,
                    "corpus_count": 1,
                    "classifier_version": "v",
                },
                "predictions": [],
            }
        ),
        encoding="utf-8",
    )

    ruta.write_bytes(bytes_lf.replace(b"\n", b"\r\n"))  # solo fin de línea
    assert _is_cache_valid(cache, _compute_corpus_hash(ruta), 1, "v") is True

    ruta.write_bytes(bytes_lf.replace(b"10", b"11"))  # contenido distinto
    assert _is_cache_valid(cache, _compute_corpus_hash(ruta), 1, "v") is False


# ===========================================================================
# c-134 — reemplazar_seccion_tiempos (D5)
# ===========================================================================
_REPORTE_BASE = (
    "# Reporte\n"
    "\n"
    "## Exactitud\n"
    "\n"
    "- **Exactitud (estricta):** 0.5000\n"
    "\n"
    "## Tiempos\n"
    "\n"
    "contenido viejo\n"
    "### Subseccion vieja\n"
    "\n"
    "- **SHA-256 del corpus:** `viejo`\n"
    "\n"
    "---\n"
    "_Generado automáticamente por `evaluation/run_evaluation.py`_"
)
_SECCION_NUEVA = "## Tiempos\n\ncontenido nuevo\n### Subseccion nueva\n\n- **SHA-256 del corpus:** `nuevo`"


def test_c134_reemplazar_seccion_tiempos_conserva_clasificacion_byte_a_byte():
    """
    4.2 RED: un bloque "## Tiempos" desactualizado se reemplaza y todo lo que
    lo rodea (secciones de clasificación y pie) queda idéntico.
    """
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    resultado = reemplazar_seccion_tiempos(_REPORTE_BASE, _SECCION_NUEVA)

    antes, _, _ = _REPORTE_BASE.partition("## Tiempos")
    pie = _REPORTE_BASE[_REPORTE_BASE.index("\n\n---\n") :]
    assert resultado == antes + _SECCION_NUEVA + pie
    assert "contenido viejo" not in resultado
    assert "`viejo`" not in resultado


def test_c134_reemplazar_seccion_tiempos_conserva_seccion_posterior_ajena():
    """
    4.2 RED: una sección de nivel 2 posterior al bloque (agregada por otro
    change) se conserva; el reemplazo termina antes de ella.
    """
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    reporte = _REPORTE_BASE.replace(
        "\n---\n", "\n## Seccion ajena\n\ntexto ajeno\n\n---\n"
    )

    resultado = reemplazar_seccion_tiempos(reporte, _SECCION_NUEVA)

    assert "## Seccion ajena\n\ntexto ajeno\n\n---\n" in resultado
    assert resultado.index("contenido nuevo") < resultado.index("## Seccion ajena")
    assert "contenido viejo" not in resultado
    # La línea en blanco que separa el bloque de la sección siguiente se conserva.
    assert "`nuevo`\n\n## Seccion ajena" in resultado


def test_c134_reemplazar_seccion_tiempos_sin_bloque_inserta_antes_del_pie():
    """4.2 RED: si falta el bloque, la sección se inserta antes del pie `---`."""
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    sin_bloque = (
        "# Reporte\n\n## Exactitud\n\n- dato\n\n---\n_Generado automáticamente_"
    )

    resultado = reemplazar_seccion_tiempos(sin_bloque, _SECCION_NUEVA)

    assert resultado == (
        "# Reporte\n\n## Exactitud\n\n- dato\n\n"
        + _SECCION_NUEVA
        + "\n\n---\n_Generado automáticamente_"
    )


def test_c134_reemplazar_seccion_tiempos_es_idempotente():
    """4.2 TRIANGULATE: aplicar dos veces el mismo bloque no cambia el texto."""
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    una_vez = reemplazar_seccion_tiempos(_REPORTE_BASE, _SECCION_NUEVA)
    dos_veces = reemplazar_seccion_tiempos(una_vez, _SECCION_NUEVA)

    assert dos_veces == una_vez


def test_c134_reemplazar_seccion_tiempos_sin_pie_ni_bloque_agrega_al_final():
    """4.2 TRIANGULATE: sin pie y sin bloque, la sección se agrega al final."""
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    resultado = reemplazar_seccion_tiempos("# Reporte\n\n## Exactitud\n\n- dato", _SECCION_NUEVA)

    assert resultado == "# Reporte\n\n## Exactitud\n\n- dato\n\n" + _SECCION_NUEVA


def test_c134_reemplazar_seccion_tiempos_al_final_sin_pie():
    """4.2 TRIANGULATE: un bloque que llega hasta el final del texto se reemplaza completo."""
    from evaluation.run_evaluation import reemplazar_seccion_tiempos

    reporte = "# Reporte\n\n## Tiempos\n\nviejo\nmas viejo"

    resultado = reemplazar_seccion_tiempos(reporte, _SECCION_NUEVA)

    assert resultado == "# Reporte\n\n" + _SECCION_NUEVA


# ===========================================================================
# c-134 — main_solo_tiempos (D5)
# ===========================================================================
async def _reporte_completo(corpus_fixture_path, tmp_path):
    """Corrida completa con FakeClassifier; devuelve (corpus, reporte)."""
    import shutil

    from evaluation.run_evaluation import main_con_corpus_real
    from evaluation.tests.conftest import FakeClassifier

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    report_path = tmp_path / "report.md"
    await main_con_corpus_real(
        corpus_path=corpus_copy,
        classifier=FakeClassifier(default_sector="Sistemas"),
        report_path=report_path,
        predicciones_path=tmp_path / "predicciones.json",
    )
    return corpus_copy, report_path


async def test_c134_solo_tiempos_reproduce_byte_a_byte_la_corrida_completa(
    corpus_fixture_path, tmp_path
):
    """
    4.3 RED (a): tras una corrida completa con FakeClassifier, el modo de solo
    tiempos sobre el mismo corpus deja el reporte idéntico byte a byte, y una
    segunda ejecución tampoco lo cambia (idempotencia).
    """
    from evaluation.run_evaluation import main_solo_tiempos

    corpus_copy, report_path = await _reporte_completo(corpus_fixture_path, tmp_path)
    completo = report_path.read_bytes()

    main_solo_tiempos(corpus_copy, report_path)
    primera = report_path.read_bytes()
    main_solo_tiempos(corpus_copy, report_path)
    segunda = report_path.read_bytes()

    assert primera == completo
    assert segunda == completo


async def test_c134_solo_tiempos_no_usa_clasificador_ni_cache(
    corpus_fixture_path, tmp_path, monkeypatch
):
    """
    4.3 RED (b): con el resolutor del clasificador real, la versión del
    clasificador, la evaluación y la lectura/escritura de predicciones
    sustituidos por funciones que lanzan, el modo termina bien y no crea
    ningún `predicciones.json`.
    """
    from evaluation import run_evaluation

    corpus_copy, report_path = await _reporte_completo(corpus_fixture_path, tmp_path)
    (tmp_path / "predicciones.json").unlink()

    def _prohibido(*args, **kwargs):
        raise AssertionError("el modo de solo tiempos no debe tocar clasificador ni cache")

    async def _prohibido_async(*args, **kwargs):
        _prohibido()

    for nombre in (
        "_resolver_clasificador_real",
        "_version_clasificador_real",
        "cargar_predicciones",
        "guardar_predicciones",
    ):
        monkeypatch.setattr(run_evaluation, nombre, _prohibido)
    monkeypatch.setattr(run_evaluation, "evaluar_corpus", _prohibido_async)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)

    run_evaluation.main_solo_tiempos(corpus_copy, report_path)

    assert list(tmp_path.glob("predicciones*.json")) == []


def test_c134_solo_tiempos_con_reporte_ausente_falla_claro_sin_crear_archivo(
    corpus_fixture_path, tmp_path
):
    """
    4.3 RED (c): sin reporte previo el modo falla con FileNotFoundError que
    indica generar primero el reporte completo, y no crea un reporte parcial.
    """
    import shutil

    from evaluation.run_evaluation import main_solo_tiempos

    corpus_copy = tmp_path / "corpus.json"
    shutil.copy(corpus_fixture_path, corpus_copy)
    report_path = tmp_path / "report.md"

    with pytest.raises(FileNotFoundError, match="reporte completo"):
        main_solo_tiempos(corpus_copy, report_path)
    assert not report_path.exists()


def test_c134_solo_tiempos_con_corpus_ausente_falla_claro(tmp_path):
    """4.3 TRIANGULATE: un corpus inexistente falla con mensaje claro."""
    from evaluation.run_evaluation import main_solo_tiempos

    reporte = tmp_path / "report.md"
    reporte.write_text("# Reporte\n\n## Tiempos\n\nviejo", encoding="utf-8")

    with pytest.raises(FileNotFoundError, match="corpus"):
        main_solo_tiempos(tmp_path / "no_existe.json", reporte)
    assert reporte.read_text(encoding="utf-8") == "# Reporte\n\n## Tiempos\n\nviejo"


async def test_c134_solo_tiempos_con_un_tiempo_distinto_cambia_solo_el_bloque(
    corpus_fixture_path, tmp_path
):
    """
    4.3 TRIANGULATE: modificar un tiempo manual del corpus cambia únicamente
    el bloque de tiempos (y su huella); lo anterior al bloque queda idéntico.
    """
    import json

    from evaluation.run_evaluation import main_solo_tiempos

    corpus_copy, report_path = await _reporte_completo(corpus_fixture_path, tmp_path)
    original = report_path.read_text(encoding="utf-8")
    datos = json.loads(corpus_copy.read_text(encoding="utf-8"))
    datos["casos"][0]["tiempo_manual_s"] = 999
    corpus_copy.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")

    main_solo_tiempos(corpus_copy, report_path)
    nuevo = report_path.read_text(encoding="utf-8")

    corte = original.index("## Tiempos")
    assert nuevo[:corte] == original[:corte]
    assert nuevo[corte:] != original[corte:]
    assert "999" not in nuevo[:corte]
    assert nuevo.endswith("_Generado automáticamente por `evaluation/run_evaluation.py`_")


# ===========================================================================
# c-134 — Flag --solo-tiempos del CLI (D5)
# ===========================================================================
def test_c134_cli_solo_tiempos_despacha_main_solo_tiempos(monkeypatch):
    """
    4.4 RED: `--solo-tiempos` invoca `main_solo_tiempos` y nunca
    `main_con_corpus_real`; no exige confirmación de corrida paga.
    """
    import sys

    from evaluation import run_evaluation

    llamadas: list = []

    def fake_solo(*args, **kwargs):
        llamadas.append("solo")

    async def fake_completo(*args, **kwargs):
        llamadas.append("completo")

    monkeypatch.setattr(run_evaluation, "main_solo_tiempos", fake_solo)
    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_completo)
    monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", "--solo-tiempos"])

    run_evaluation.main()

    assert llamadas == ["solo"]


@pytest.mark.parametrize(
    "incompatible", ["--confirm-paid", "--force", "--no-cache"]
)
def test_c134_cli_solo_tiempos_es_incompatible_con_flags_de_corrida_paga(
    monkeypatch, capsys, incompatible
):
    """
    4.4 RED: `--solo-tiempos` combinado con `--confirm-paid`, `--force` o
    `--no-cache` termina con SystemExit código 2 (parser.error) sin ejecutar
    ningún modo.
    """
    import sys

    from evaluation import run_evaluation

    llamadas: list = []

    def fake_solo(*args, **kwargs):
        llamadas.append("solo")

    async def fake_completo(*args, **kwargs):
        llamadas.append("completo")

    monkeypatch.setattr(run_evaluation, "main_solo_tiempos", fake_solo)
    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_completo)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", "--solo-tiempos", incompatible])

    with pytest.raises(SystemExit) as exc_info:
        run_evaluation.main()

    assert exc_info.value.code == 2
    assert "no se puede combinar" in capsys.readouterr().err
    assert llamadas == []


def test_c134_cli_sin_solo_tiempos_conserva_la_combinacion_force_y_confirm_paid(
    monkeypatch,
):
    """
    4.4 TRIANGULATE: sin el flag, el comportamiento previo no cambia:
    `--force --confirm-paid` sigue combinándose y despacha la corrida completa.
    """
    import sys

    from evaluation import run_evaluation

    captured: dict = {}

    async def fake_completo(*args, **kwargs):
        captured.update(kwargs)

    def fake_solo(*args, **kwargs):
        captured["solo"] = True

    monkeypatch.setattr(run_evaluation, "main_con_corpus_real", fake_completo)
    monkeypatch.setattr(run_evaluation, "main_solo_tiempos", fake_solo)
    monkeypatch.delenv("EVALUATION_CONFIRM_PAID", raising=False)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", "--force", "--confirm-paid"])

    run_evaluation.main()

    assert captured["force"] is True
    assert captured["confirm_paid"] is True
    assert "solo" not in captured


# ===========================================================================
# c-145 E2-i — `--solo-tiempos` con reporte ausente falla limpio (sin traza)
# ===========================================================================
def test_c145_cli_solo_tiempos_con_reporte_ausente_falla_sin_traza(
    monkeypatch, capsys, tmp_path
):
    """
    RED (c-145 E2-i): `main()` con `--solo-tiempos` y un reporte inexistente debe
    terminar con codigo distinto de cero e imprimir un mensaje legible, sin
    propagar una traza cruda de `FileNotFoundError`.
    """
    import sys

    from evaluation import run_evaluation

    real_solo = run_evaluation.main_solo_tiempos

    def solo_con_reporte_ausente():
        real_solo(report_path=tmp_path / "reporte_ausente.md")

    monkeypatch.setattr(run_evaluation, "main_solo_tiempos", solo_con_reporte_ausente)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", "--solo-tiempos"])

    with pytest.raises(SystemExit) as exc_info:
        run_evaluation.main()

    err = capsys.readouterr().err
    assert exc_info.value.code != 0
    assert "reporte_ausente.md" in err
    assert "Traceback" not in err
    assert "FileNotFoundError" not in err


def test_c145_cli_solo_tiempos_con_corpus_ausente_falla_sin_traza(
    monkeypatch, capsys, tmp_path
):
    """TRIANGULATE: el corpus ausente tambien sale limpio por el mismo envoltorio."""
    import sys

    from evaluation import run_evaluation

    real_solo = run_evaluation.main_solo_tiempos

    def solo_con_corpus_ausente():
        real_solo(corpus_path=tmp_path / "corpus_ausente.json")

    monkeypatch.setattr(run_evaluation, "main_solo_tiempos", solo_con_corpus_ausente)
    monkeypatch.setattr(sys, "argv", ["run_evaluation", "--solo-tiempos"])

    with pytest.raises(SystemExit) as exc_info:
        run_evaluation.main()

    err = capsys.readouterr().err
    assert exc_info.value.code != 0
    assert "corpus_ausente.json" in err
    assert "Traceback" not in err
