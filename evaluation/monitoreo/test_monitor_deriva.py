"""
Tests del job de monitoreo de deriva (c-227, D3-D7; grupo 3).

Cubren las funciones puras (`metricas_canario`, `comparar_con_base`,
`detectar_deriva`, `evaluar_alertas`, `identidad_proveedor`), la integridad del
conjunto canario y su linea de base congelada, y el `main()` del job (offline por
defecto; corrida paga detras del gate de confirmacion; salida determinista).

Funciones puras y offline: no invocan al proveedor. La corrida paga solo se prueba
verificando que ABORTA sin confirmacion, sin invocarlo.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import sys

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from evaluation import metrics as M  # noqa: E402
from evaluation.corpus import cargar_corpus, SECTORES_CANONICOS  # noqa: E402
from evaluation.monitoreo import monitor_deriva as md  # noqa: E402

# Valores exactos de la linea de base congelada (tolerancia delta = 0.05).
BASELINE_EXACTITUD = 0.8446601941747572
BASELINE_F1_MACRO = 0.7446560846560847
PISO_EXACTITUD = BASELINE_EXACTITUD - 0.05
PISO_F1_MACRO = BASELINE_F1_MACRO - 0.05


class _ConfigFalsa:
    """Config con la forma de `Settings` que el job consume."""

    def __init__(
        self,
        *,
        inference_provider: str = "gemini",
        inference_model: str = "gemini-3.6-flash",
        monitoring_tolerancia: float = 0.05,
        monitoring_exactitud_estricta_floor: float = PISO_EXACTITUD,
        monitoring_f1_macro_floor: float = PISO_F1_MACRO,
    ) -> None:
        self.inference_provider = inference_provider
        self.inference_model = inference_model
        self.monitoring_tolerancia = monitoring_tolerancia
        self.monitoring_exactitud_estricta_floor = monitoring_exactitud_estricta_floor
        self.monitoring_f1_macro_floor = monitoring_f1_macro_floor


def _par(caso_id: str, real: str, predicho, adicionales=()) -> md.ParCanario:
    return md.ParCanario(
        caso_id=caso_id, real=real, predicho=predicho, adicionales=tuple(adicionales)
    )


# ---------------------------------------------------------------------------
# 3.1 — metricas_canario
# ---------------------------------------------------------------------------
def test_metricas_canario_calcula_exactitud_y_f1() -> None:
    pares = [
        _par("I1", "Sistemas", "Sistemas"),
        _par("I2", "Bases de Datos", "Sistemas"),
    ]
    m = md.metricas_canario(pares)

    assert m.casos == 2
    assert m.exactitud_estricta == pytest.approx(0.5)
    # El F1 macro debe coincidir con la funcion pura compartida de evaluation.metrics.
    mc = M.matriz_confusion(["Sistemas", "Bases de Datos"], ["Sistemas", "Sistemas"])
    assert m.f1_macro == pytest.approx(M.f1_macro(M.f1_por_clase(mc)))
    assert set(m.f1_por_sector) == set(SECTORES_CANONICOS)


def test_metricas_canario_expone_las_metricas_monitoreadas() -> None:
    m = md.metricas_canario([_par("I1", "Sistemas", "Sistemas")])
    assert set(m.monitoreadas()) == set(md.METRICAS_MONITOREADAS)
    assert m.monitoreadas()["exactitud_estricta"] == pytest.approx(1.0)


def test_metricas_canario_prediccion_ausente_cuenta_como_error() -> None:
    pares = [_par("I1", "Sistemas", None), _par("I2", "Sistemas", "Sistemas")]
    m = md.metricas_canario(pares)
    assert m.exactitud_estricta == pytest.approx(0.5)


# ---------------------------------------------------------------------------
# 3.1 — comparar_con_base
# ---------------------------------------------------------------------------
def test_comparar_con_base_reporta_diferencias_y_degradacion() -> None:
    actual = {"exactitud_estricta": 0.80, "f1_macro": 0.76}
    base = {"exactitud_estricta": 0.845, "f1_macro": 0.75}

    diferencias = md.comparar_con_base(actual, base)

    assert diferencias["exactitud_estricta"].diferencia == pytest.approx(-0.045)
    assert diferencias["exactitud_estricta"].degradada is True
    assert diferencias["f1_macro"].diferencia == pytest.approx(0.01)
    assert diferencias["f1_macro"].degradada is False


# ---------------------------------------------------------------------------
# 3.1/3.3 — detectar_deriva (sin deriva / metrica / identidad / ambas)
# ---------------------------------------------------------------------------
def _metricas(**valores) -> dict:
    base = {"exactitud_estricta": BASELINE_EXACTITUD, "f1_macro": BASELINE_F1_MACRO}
    base.update(valores)
    return base


def _tolerancias(delta: float = 0.05) -> dict:
    return {m: delta for m in md.METRICAS_MONITOREADAS}


def test_detectar_deriva_sin_cambio() -> None:
    v = md.detectar_deriva(
        _metricas(), _metricas(), _tolerancias(), ("gemini", "m"), ("gemini", "m")
    )
    assert v.veredicto == "sin_deriva"
    assert v.metricas_degradadas == ()


def test_detectar_deriva_de_metrica_sobre_la_tolerancia() -> None:
    v = md.detectar_deriva(
        _metricas(exactitud_estricta=BASELINE_EXACTITUD - 0.10),
        _metricas(),
        _tolerancias(),
        ("gemini", "m"),
        ("gemini", "m"),
    )
    assert v.veredicto == "deriva_de_metrica"
    assert v.metricas_degradadas == ("exactitud_estricta",)


def test_detectar_deriva_dentro_de_la_tolerancia_no_es_deriva() -> None:
    v = md.detectar_deriva(
        _metricas(f1_macro=BASELINE_F1_MACRO - 0.04),
        _metricas(),
        _tolerancias(),
        ("gemini", "m"),
        ("gemini", "m"),
    )
    assert v.veredicto == "sin_deriva"


def test_detectar_deriva_de_identidad() -> None:
    v = md.detectar_deriva(
        _metricas(), _metricas(), _tolerancias(), ("otro", "m"), ("gemini", "m")
    )
    assert v.veredicto == "deriva_de_identidad"
    assert v.identidad_cambio is True
    assert v.metricas_degradadas == ()


def test_detectar_ambas() -> None:
    v = md.detectar_deriva(
        _metricas(f1_macro=BASELINE_F1_MACRO - 0.20),
        _metricas(),
        _tolerancias(),
        ("gemini", "gemini-otro"),
        ("gemini", "gemini-3.6-flash"),
    )
    assert v.veredicto == "ambas"


# ---------------------------------------------------------------------------
# 3.1/3.3 — evaluar_alertas
# ---------------------------------------------------------------------------
def test_evaluar_alertas_emite_bajo_el_piso() -> None:
    metricas = {"exactitud_estricta": PISO_EXACTITUD - 0.01, "f1_macro": BASELINE_F1_MACRO}
    pisos = {"exactitud_estricta": PISO_EXACTITUD, "f1_macro": PISO_F1_MACRO}

    alertas = md.evaluar_alertas(metricas, pisos)

    assert [a.metrica for a in alertas] == ["exactitud_estricta"]
    assert alertas[0].valor == pytest.approx(PISO_EXACTITUD - 0.01)
    assert alertas[0].piso == pytest.approx(PISO_EXACTITUD)


def test_evaluar_alertas_sin_alerta_sobre_el_piso() -> None:
    metricas = {"exactitud_estricta": BASELINE_EXACTITUD, "f1_macro": BASELINE_F1_MACRO}
    pisos = {"exactitud_estricta": PISO_EXACTITUD, "f1_macro": PISO_F1_MACRO}
    assert md.evaluar_alertas(metricas, pisos) == []


# ---------------------------------------------------------------------------
# 3.1 — identidad_proveedor
# ---------------------------------------------------------------------------
def test_identidad_proveedor_desde_config() -> None:
    assert md.identidad_proveedor(_ConfigFalsa()) == ("gemini", "gemini-3.6-flash")


# ---------------------------------------------------------------------------
# 3.5 — integridad del conjunto canario
# ---------------------------------------------------------------------------
def test_canario_tiene_103_casos_y_los_cinco_sectores() -> None:
    canario = cargar_corpus(md.CANARIO_PATH)
    assert len(canario) == 103
    assert {c.sector_asignado for c in canario} == set(SECTORES_CANONICOS)


def test_canario_es_disjunto_del_corpus_de_ajuste() -> None:
    from evaluation.no_solape import verificar_no_solape

    ajuste = cargar_corpus(_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json")
    canario = cargar_corpus(md.CANARIO_PATH)
    # No debe lanzar: ids `I*` y descripciones sin solape con el corpus de ajuste.
    verificar_no_solape(ajuste, canario)


def test_suma_sha256_del_canario_coincide() -> None:
    texto = (md.CANARIO_SHA256SUMS_PATH).read_text(encoding="utf-8")
    declarados = {
        linea.split()[1]: linea.split()[0]
        for linea in texto.strip().splitlines()
        if linea.strip()
    }
    for nombre, esperado in declarados.items():
        contenido = (md.CANARIO_DIR / nombre).read_bytes()
        assert hashlib.sha256(contenido).hexdigest() == esperado, nombre


# ---------------------------------------------------------------------------
# 3.6 — linea de base congelada reproducible
# ---------------------------------------------------------------------------
def test_la_linea_de_base_reproduce_desde_los_artefactos() -> None:
    reproducida = md.calcular_linea_de_base(
        md.CANARIO_PATH, md.CANARIO_PREDICCIONES_PATH, tolerancia=0.05
    )
    congelada = json.loads(md.BASELINE_PATH.read_text(encoding="utf-8"))

    assert reproducida["metricas"] == pytest.approx(congelada["metricas"])
    assert reproducida["canario_count"] == congelada["canario_count"] == 103
    assert reproducida["identidad"] == congelada["identidad"]
    assert reproducida["pisos"] == pytest.approx(congelada["pisos"])


def test_los_pisos_de_settings_derivan_de_la_linea_de_base() -> None:
    from evaluation.run_evaluation import _ensure_backend_on_path

    _ensure_backend_on_path()
    from app.config.settings import Settings  # type: ignore[import]

    settings = Settings(
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-gemini-key",  # gitleaks:allow
        pseudonymization_encryption_key="2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ=",
        jwt_secret_key="fake-jwt-secret",
        cost_guard_caller_hmac_key="fake-hmac-key",  # gitleaks:allow
        directory_blind_index_key="fake-blind-index-key",  # gitleaks:allow
    )
    assert settings.monitoring_tolerancia == pytest.approx(0.05)
    assert settings.monitoring_exactitud_estricta_floor == pytest.approx(PISO_EXACTITUD)
    assert settings.monitoring_f1_macro_floor == pytest.approx(PISO_F1_MACRO)


# ---------------------------------------------------------------------------
# 3.7/3.8 — main() del job
# ---------------------------------------------------------------------------
def test_main_offline_reproduce_la_linea_de_base_sin_invocar_al_proveedor(
    tmp_path, monkeypatch
) -> None:
    def _no_llamar():
        raise AssertionError("el modo offline no debe resolver el clasificador pago")

    monkeypatch.setattr(md, "_resolver_clasificador_real", _no_llamar)

    resultado = md.main(fecha="2026-11-15", config=_ConfigFalsa(), reportes_dir=tmp_path)

    assert resultado.veredicto.veredicto == "sin_deriva"
    assert resultado.alertas == []
    assert resultado.reporte_path.exists()
    contenido = resultado.reporte_path.read_text(encoding="utf-8")
    assert "sin_deriva" in contenido
    assert "0.8446601941747572" in contenido  # exactitud estricta de la linea de base


def test_main_fresh_sin_confirmacion_aborta_sin_invocar_al_proveedor(
    tmp_path, monkeypatch
) -> None:
    llamado = {"resolver": False}

    def _resolver():
        llamado["resolver"] = True
        raise AssertionError("no debe resolver el clasificador sin confirmacion")

    monkeypatch.setattr(md, "_resolver_clasificador_real", _resolver)
    monkeypatch.delenv(md.CONFIRM_PAID_ENV_VAR, raising=False)

    with pytest.raises(md.PaidRunNotConfirmedError):
        md.main(
            fresh=True,
            confirm_paid=False,
            fecha="2026-11-15",
            config=_ConfigFalsa(),
            reportes_dir=tmp_path,
        )
    assert llamado["resolver"] is False


def test_main_dos_corridas_byte_identicas(tmp_path) -> None:
    r1 = md.main(fecha="2026-11-15", config=_ConfigFalsa(), reportes_dir=tmp_path)
    r2 = md.main(fecha="2026-11-15", config=_ConfigFalsa(), reportes_dir=tmp_path)
    assert r1.reporte_path.read_bytes() == r2.reporte_path.read_bytes()


def test_alerta_nombra_metrica_valor_piso_y_corrida(tmp_path) -> None:
    # Piso por encima de la metrica real: fuerza una alerta en exactitud estricta.
    config = _ConfigFalsa(monitoring_exactitud_estricta_floor=0.99)
    resultado = md.main(fecha="2026-11-15", config=config, reportes_dir=tmp_path)

    assert [a.metrica for a in resultado.alertas] == ["exactitud_estricta"]
    contenido = resultado.reporte_path.read_text(encoding="utf-8")
    assert "exactitud_estricta" in contenido
    assert "0.99" in contenido  # el piso
    assert "2026-11-15" in contenido  # la corrida
    assert "fallback" in contenido.lower()
