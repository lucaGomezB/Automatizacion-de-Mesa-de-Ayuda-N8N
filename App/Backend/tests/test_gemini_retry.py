"""
Tests del reintento acotado del clasificador Gemini (c-58-resiliencia-gemini).

Cubren el contrato de `classification-resilience`:
    - Taxonomia pura transitorio/terminal (`_is_transient_error`).
    - Reintento ante 503 transitorio seguido de exito.
    - Agotamiento de intentos ante 503 persistente (fallback en el hibrido).
    - Errores terminales (400/401/403) sin reintento.
    - Timeout por intento reintentado y, agotado, fallback.
    - Respuesta JSON invalida sin reintento.
    - Presupuesto de latencia total que corta los reintentos.
    - Parametros configurables con defaults seguros.
    - Observabilidad estructurada sin clave ni PII.

Estrategia: el cliente genai se reemplaza por un doble (`client=`); el reloj,
el sleep y la fuente de aleatoriedad se inyectan para que la suite sea
determinista, offline y sin costo.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from google.genai import errors as genai_errors

from app.classifiers import gemini_classifier as gemini_module
from app.classifiers.gemini_classifier import GeminiClassifier
from app.classifiers.hybrid import HybridClassifier
from app.config.settings import Settings, get_settings
from app.cost_guard.decision import GuardDecision
from app.schemas.clasificacion import ClasificacionResult

# Clave Fernet de prueba (no contiene datos reales)
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_VALID_JSON = '{"categoría": "Sistemas", "confianza": 0.92}'

# Descripcion de prueba: se usa para verificar que la observabilidad no la filtra.
_DESCRIPCION = "El servidor de correo de la sucursal no responde desde las 9"


# ---------------------------------------------------------------------------
# Helpers de fixtures
# ---------------------------------------------------------------------------
def _settings(**overrides) -> Settings:
    fields = {
        "database_url": "sqlite+aiosqlite:///:memory:",
        "gemini_api_key": "fake-gemini-key",  # gitleaks:allow
        "pseudonymization_encryption_key": _TEST_KEY,
        "jwt_secret_key": "fake-jwt-secret",
    }
    fields.update(overrides)
    return Settings(**fields)


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _response(text: str):
    class _FakeResponse:
        def __init__(self) -> None:
            self.text = text

    return _FakeResponse()


def _server_error(code: int = 503) -> genai_errors.ServerError:
    return genai_errors.ServerError(code, {"error": {"message": "high demand"}})


def _client_error(code: int) -> genai_errors.ClientError:
    return genai_errors.ClientError(code, {"error": {"message": "terminal"}})


class _FakeModels:
    """Doble de `client.aio.models`: devuelve/levanta los outcomes en orden."""

    def __init__(self, outcomes) -> None:
        self._outcomes = list(outcomes)
        self.calls = 0

    async def generate_content(self, **kwargs):
        self.calls += 1
        if not self._outcomes:
            raise AssertionError("generate_content llamado mas veces que outcomes")
        outcome = self._outcomes.pop(0)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class _FakeAio:
    def __init__(self, models: _FakeModels) -> None:
        self.models = models


class _FakeClient:
    def __init__(self, models: _FakeModels) -> None:
        self.aio = _FakeAio(models)


def _make_gemini(
    monkeypatch,
    outcomes,
    *,
    retry_sleep=None,
    clock=None,
    random_fn=None,
    **setting_overrides,
):
    """Construye un GeminiClassifier con cliente/reloj/espera inyectados."""
    settings = _settings(**setting_overrides)
    monkeypatch.setattr(gemini_module, "get_settings", lambda: settings)
    models = _FakeModels(outcomes)
    kwargs: dict = {"client": _FakeClient(models)}
    if retry_sleep is not None:
        kwargs["sleep"] = retry_sleep
    if clock is not None:
        kwargs["monotonic"] = clock
    if random_fn is not None:
        kwargs["random_fn"] = random_fn
    return GeminiClassifier(**kwargs), models


class _LowConfidenceDeterministic:
    """Deterministico de baja confianza para forzar la escalada a Gemini."""

    async def classify(self, descripcion: str) -> ClasificacionResult:
        return ClasificacionResult(
            sector_predicho="Sistemas",
            confianza=0.5,
            etapa="deterministic",
            requiere_revision_humana=False,
        )


async def _no_sleep(_delay: float) -> None:
    return None


def _logged_events(mock_logger) -> list[str]:
    events: list[str] = []
    for method in ("info", "warning", "error"):
        for call in getattr(mock_logger, method).call_args_list:
            if call.args:
                events.append(str(call.args[0]))
    return events


def _logger_repr(mock_logger) -> str:
    return repr(mock_logger.mock_calls)


# ---------------------------------------------------------------------------
# 2.1 — Taxonomia pura transitorio/terminal
# ---------------------------------------------------------------------------
def test_taxonomy_server_error_es_transitorio() -> None:
    assert gemini_module._is_transient_error(_server_error(503)) is True


@pytest.mark.parametrize("code", [500, 502, 504])
def test_taxonomy_otros_5xx_son_transitorios(code: int) -> None:
    assert gemini_module._is_transient_error(_server_error(code)) is True


def test_taxonomy_429_es_transitorio() -> None:
    assert gemini_module._is_transient_error(_client_error(429)) is True


@pytest.mark.parametrize("code", [400, 401, 403, 404])
def test_taxonomy_client_errors_son_terminales(code: int) -> None:
    assert gemini_module._is_transient_error(_client_error(code)) is False


def test_taxonomy_timeout_es_transitorio() -> None:
    assert gemini_module._is_transient_error(TimeoutError()) is True


def test_taxonomy_error_generico_es_terminal() -> None:
    assert gemini_module._is_transient_error(ValueError("boom")) is False


# ---------------------------------------------------------------------------
# 1.2 — 503 transitorio seguido de exito: no degrada
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_503_seguido_de_exito_no_degrada(monkeypatch) -> None:
    classifier, models = _make_gemini(
        monkeypatch,
        [_server_error(503), _response(_VALID_JSON)],
        retry_sleep=_no_sleep,
    )
    result = await classifier.classify(_DESCRIPCION)

    assert result.etapa == "gemini"
    assert result.sector_predicho == "Sistemas"
    assert result.confianza == pytest.approx(0.92)
    assert models.calls == 2


@pytest.mark.asyncio
async def test_max_retries_cero_restaura_un_solo_intento(monkeypatch) -> None:
    """`gemini_max_retries=0` reproduce el comportamiento actual (1 intento)."""
    classifier, models = _make_gemini(
        monkeypatch,
        [_server_error(503)],
        retry_sleep=_no_sleep,
        gemini_max_retries=0,
    )
    with pytest.raises(Exception):
        await classifier.classify(_DESCRIPCION)
    assert models.calls == 1


# ---------------------------------------------------------------------------
# 1.3 — 503 persistente: agota los intentos y cae al fallback del hibrido
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_503_persistente_agota_intentos_y_fallback(monkeypatch) -> None:
    gemini, models = _make_gemini(
        monkeypatch,
        [_server_error(503)] * 3,
        retry_sleep=_no_sleep,
    )
    classifier = HybridClassifier(
        deterministic=_LowConfidenceDeterministic(), gemini=gemini
    )
    result = await classifier.classify(_DESCRIPCION)

    assert models.calls == 3  # gemini_max_retries + 1
    assert result.etapa == "fallback"
    assert result.confianza == 0.0
    assert result.requiere_revision_humana is True


# ---------------------------------------------------------------------------
# 1.4 — Error terminal: una sola llamada, sin reintento
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
@pytest.mark.parametrize("code", [400, 403])
async def test_error_terminal_no_se_reintenta(monkeypatch, code: int) -> None:
    gemini, models = _make_gemini(
        monkeypatch,
        [_client_error(code)],
        retry_sleep=_no_sleep,
    )
    classifier = HybridClassifier(
        deterministic=_LowConfidenceDeterministic(), gemini=gemini
    )
    result = await classifier.classify(_DESCRIPCION)

    assert models.calls == 1
    assert result.etapa == "fallback"
    assert result.confianza == 0.0


# ---------------------------------------------------------------------------
# 1.5 — Timeout: se reintenta y, agotado, fallback
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_timeout_se_reintenta_y_agotado_es_fallback(monkeypatch) -> None:
    gemini, models = _make_gemini(
        monkeypatch,
        [TimeoutError()] * 3,
        retry_sleep=_no_sleep,
    )
    classifier = HybridClassifier(
        deterministic=_LowConfidenceDeterministic(), gemini=gemini
    )
    result = await classifier.classify(_DESCRIPCION)

    assert models.calls == 3
    assert result.etapa == "fallback"
    assert result.confianza == 0.0
    assert result.requiere_revision_humana is True


# ---------------------------------------------------------------------------
# 1.6 — Respuesta invalida: sin reintento, fallback de validacion
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_respuesta_invalida_no_se_reintenta(monkeypatch) -> None:
    classifier, models = _make_gemini(
        monkeypatch,
        [_response("no es json")],
        retry_sleep=_no_sleep,
    )
    result = await classifier.classify(_DESCRIPCION)

    assert models.calls == 1
    assert result.etapa == "fallback"
    assert result.confianza == 0.0


# ---------------------------------------------------------------------------
# 1.7 — Presupuesto de latencia total corta los reintentos
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_presupuesto_de_latencia_corta_antes_del_maximo(monkeypatch) -> None:
    clock = {"t": 0.0}

    def fake_monotonic() -> float:
        return clock["t"]

    def fake_advance_by_attempt(**kwargs):
        # Cada intento consume 55 s del presupuesto de 60 s.
        clock["t"] += 55.0
        raise _server_error(503)

    models = _FakeModels([])

    async def slow_generate_content(**kwargs):
        models.calls += 1
        fake_advance_by_attempt(**kwargs)

    models.generate_content = slow_generate_content  # type: ignore[assignment]

    settings = _settings(gemini_total_timeout_seconds=60)
    monkeypatch.setattr(gemini_module, "get_settings", lambda: settings)
    gemini = GeminiClassifier(
        client=_FakeClient(models),
        sleep=_no_sleep,
        monotonic=fake_monotonic,
        random_fn=lambda: 1.0,
    )
    classifier = HybridClassifier(
        deterministic=_LowConfidenceDeterministic(), gemini=gemini
    )
    result = await classifier.classify(_DESCRIPCION)

    assert models.calls == 2  # corta antes de los 3 intentos configurados
    assert result.etapa == "fallback"


@pytest.mark.asyncio
async def test_backoff_crece_y_esta_acotado(monkeypatch) -> None:
    """La espera crece exponencialmente y no supera la espera maxima."""
    delays: list[float] = []

    async def recording_sleep(delay: float) -> None:
        delays.append(delay)

    classifier, _ = _make_gemini(
        monkeypatch,
        [_server_error(503)] * 3,
        retry_sleep=recording_sleep,
        random_fn=lambda: 0.0,  # jitter nulo: factor 1.0
        gemini_retry_base_delay_seconds=0.5,
        gemini_retry_max_delay_seconds=1.0,
    )
    with pytest.raises(Exception):
        await classifier.classify(_DESCRIPCION)

    assert delays == [0.5, 1.0]  # 1.0 queda topeado en max_delay


# ---------------------------------------------------------------------------
# 1.8 — Parametros configurables con defaults seguros
# ---------------------------------------------------------------------------
def test_settings_defaults_de_resiliencia_seguros() -> None:
    settings = _settings()
    assert settings.gemini_max_retries == 2
    assert settings.gemini_retry_base_delay_seconds == 0.5
    assert settings.gemini_retry_max_delay_seconds == 8.0
    assert settings.gemini_retry_jitter_ratio == 0.5
    assert settings.gemini_total_timeout_seconds == 60
    assert settings.gemini_total_timeout_seconds > settings.gemini_timeout_seconds


def test_settings_override_por_entorno(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MAX_RETRIES", "5")
    monkeypatch.setenv("GEMINI_RETRY_BASE_DELAY_SECONDS", "1.5")
    settings = Settings(
        _env_file=None,
        database_url="sqlite+aiosqlite:///:memory:",
        gemini_api_key="fake-gemini-key",  # gitleaks:allow
        pseudonymization_encryption_key=_TEST_KEY,
        jwt_secret_key="fake-jwt-secret",
    )
    assert settings.gemini_max_retries == 5
    assert settings.gemini_retry_base_delay_seconds == 1.5


# ---------------------------------------------------------------------------
# 2.3 — Observabilidad estructurada sin secretos ni PII
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_evento_reintento_agendado(monkeypatch) -> None:
    classifier, _ = _make_gemini(
        monkeypatch,
        [_server_error(503), _response(_VALID_JSON)],
        retry_sleep=_no_sleep,
    )
    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    await classifier.classify(_DESCRIPCION)
    assert "gemini_retry_scheduled" in _logged_events(mock_logger)


@pytest.mark.asyncio
async def test_evento_agotamiento_y_falla_terminal(monkeypatch) -> None:
    classifier, _ = _make_gemini(
        monkeypatch,
        [_server_error(503), _server_error(503), _server_error(503)],
        retry_sleep=_no_sleep,
    )
    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    with pytest.raises(Exception):
        await classifier.classify(_DESCRIPCION)
    assert "gemini_retry_exhausted" in _logged_events(mock_logger)

    terminal, _ = _make_gemini(
        monkeypatch,
        [_client_error(400)],
        retry_sleep=_no_sleep,
    )
    term_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", term_logger)
    with pytest.raises(Exception):
        await terminal.classify(_DESCRIPCION)
    assert "gemini_retry_terminal" in _logged_events(term_logger)


@pytest.mark.asyncio
async def test_observabilidad_no_expone_pii_ni_clave(monkeypatch) -> None:
    classifier, _ = _make_gemini(
        monkeypatch,
        [_server_error(503), _response(_VALID_JSON)],
        retry_sleep=_no_sleep,
    )
    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    await classifier.classify(_DESCRIPCION)
    payload = _logger_repr(mock_logger)
    assert _DESCRIPCION not in payload
    assert "fake-gemini-key" not in payload

