"""
Tests de la interfaz del proveedor de inferencia (c-227, D1/D2).

Cubren el contrato de `inference-provider-abstraction`:
    - La interfaz no filtra tipos del SDK de ningun proveedor (provider.py no
      importa google-genai y sus anotaciones son primitivas).
    - Una implementacion falsa se inyecta en el clasificador sin importar el SDK.
    - La taxonomia traduce los errores del SDK a transitorio/terminal.
    - El registro resuelve el nombre a su factory y falla con error explicito ante
      un nombre desconocido.
    - Los defaults de `Settings` resuelven al proveedor y modelo vigentes; el
      override por entorno los cambia sin recompilar.

Strict TDD: RED -> GREEN -> TRIANGULATE -> REFACTOR.
"""

from __future__ import annotations

import ast
import pathlib
import types
from unittest.mock import MagicMock

import pytest
from google.genai import errors as genai_errors

from app.classifiers import gemini_classifier as gemini_module
from app.classifiers import hybrid as hybrid_module
from app.classifiers.gemini_classifier import GeminiClassifier, GeminiProvider
from app.classifiers.hybrid import HybridClassifier
from app.classifiers.provider import (
    GenerationResult,
    InferenceParams,
    InferenceProvider,
    InferenceTerminalError,
    InferenceTimeoutError,
    InferenceTransientError,
    UnknownProviderError,
    proveedores_registrados,
    resolver_proveedor,
)
from app.config.settings import Settings, get_settings

# Clave Fernet de prueba (no contiene datos reales)
_TEST_KEY = "2BFqlzB9uZlu2axKBM-ZrYJGq3u8JOK93ZYzIwkE3tQ="

_VALID_JSON = '{"categoría": "Sistemas", "confianza": 0.92}'


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


# ---------------------------------------------------------------------------
# Helpers: cliente genai falso y proveedor falso
# ---------------------------------------------------------------------------
class _Respuesta:
    def __init__(self, text: str) -> None:
        self.text = text


class _ModelosFalsos:
    def __init__(self, outcomes) -> None:
        self._outcomes = list(outcomes)
        self.calls = 0

    async def generate_content(self, **kwargs):
        self.calls += 1
        outcome = self._outcomes.pop(0) if self._outcomes else _Respuesta(_VALID_JSON)
        if isinstance(outcome, BaseException):
            raise outcome
        return outcome


class _ClienteFalso:
    def __init__(self, modelos: _ModelosFalsos) -> None:
        self.aio = types.SimpleNamespace(models=modelos)


def _server_error(code: int = 503) -> genai_errors.ServerError:
    return genai_errors.ServerError(code, {"error": {"message": "high demand"}})


def _client_error(code: int) -> genai_errors.ClientError:
    return genai_errors.ClientError(code, {"error": {"message": "terminal"}})


class _ProveedorFalso:
    """Implementacion falsa de `InferenceProvider` (no importa el SDK)."""

    def __init__(self, respuestas=None, error: BaseException | None = None) -> None:
        self._respuestas = list(respuestas or [])
        self._error = error
        self.llamadas = 0
        self.ultimo_params: InferenceParams | None = None

    async def generate(self, *, prompt: str, params: InferenceParams) -> GenerationResult:
        self.llamadas += 1
        self.ultimo_params = params
        if self._error is not None:
            raise self._error
        if self._respuestas:
            return GenerationResult(text=self._respuestas.pop(0))
        return GenerationResult(text=_VALID_JSON)


# ---------------------------------------------------------------------------
# 1.1 — Contrato de la interfaz
# ---------------------------------------------------------------------------
def test_provider_py_no_importa_el_sdk() -> None:
    """`provider.py` no debe importar google-genai (la interfaz es agnostica)."""
    fuente = pathlib.Path(gemini_module.__file__).parent.joinpath("provider.py").read_text(
        encoding="utf-8"
    )
    arbol = ast.parse(fuente)
    modulos_importados: list[str] = []
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            modulos_importados.extend(alias.name for alias in nodo.names)
        elif isinstance(nodo, ast.ImportFrom):
            modulos_importados.append(nodo.module or "")
    assert not any(
        "google" in modulo or "genai" in modulo for modulo in modulos_importados
    ), f"provider.py importa el SDK: {modulos_importados}"


def test_inference_params_solo_primitivos() -> None:
    """Los parametros de inferencia no exponen tipos del SDK."""
    anotaciones = InferenceParams.__annotations__
    assert set(anotaciones) == {
        "model",
        "temperature",
        "top_p",
        "max_output_tokens",
        "candidate_count",
        "timeout",
    }
    assert all(
        tipo in ("str", "float", "int") for tipo in anotaciones.values()
    ), anotaciones


def test_interface_no_filtra_tipos_del_proveedor() -> None:
    """La firma de `generate` solo usa primitivas y `InferenceParams`."""
    anotaciones = InferenceProvider.generate.__annotations__
    assert anotaciones["prompt"] == "str"
    assert anotaciones["params"] == "InferenceParams"
    assert anotaciones["return"] == "GenerationResult"


def test_un_proveedor_falso_cumple_la_interfaz() -> None:
    """Un objeto con `async generate(*, prompt, params)` satisface el Protocol."""
    assert isinstance(_ProveedorFalso(), InferenceProvider)


@pytest.mark.asyncio
async def test_implementacion_falsa_se_inyecta_sin_sdk(monkeypatch) -> None:
    """Inyectada una implementacion falsa, el clasificador la usa sin el SDK."""
    monkeypatch.setattr(gemini_module, "get_settings", lambda: _settings())
    fake = _ProveedorFalso([_VALID_JSON])
    clasificador = GeminiClassifier(provider=fake)

    assert clasificador._client is None  # no se construyo el cliente del SDK
    resultado = await clasificador.classify("descripcion de prueba")

    assert fake.llamadas == 1
    assert resultado.etapa == "gemini"
    assert resultado.sector_predicho == "Sistemas"
    assert resultado.confianza == pytest.approx(0.92)


@pytest.mark.asyncio
async def test_la_validacion_del_contrato_queda_en_el_clasificador(monkeypatch) -> None:
    """El proveedor devuelve texto crudo; el clasificador valida el contrato."""
    monkeypatch.setattr(gemini_module, "get_settings", lambda: _settings())
    fake = _ProveedorFalso(['{"categoría": "SISTEMAS", "confianza": 0.9}'])
    resultado = await GeminiClassifier(provider=fake).classify("x")

    assert resultado.etapa == "fallback"
    assert resultado.confianza == 0.0
    assert resultado.requiere_revision_humana is True


# ---------------------------------------------------------------------------
# 1.3 — Taxonomia transitorio/terminal (traduccion del proveedor Gemini)
# ---------------------------------------------------------------------------
async def _generar_con(outcome) -> str:
    proveedor = GeminiProvider(client=_ClienteFalso(_ModelosFalsos([outcome])))
    params = InferenceParams(
        model="gemini-3.6-flash",
        temperature=0.3,
        top_p=0.9,
        max_output_tokens=100,
        candidate_count=1,
        timeout=30.0,
    )
    return (await proveedor.generate(prompt="p", params=params)).text


@pytest.mark.asyncio
async def test_proveedor_exito_devuelve_texto_crudo() -> None:
    assert await _generar_con(_Respuesta(_VALID_JSON)) == _VALID_JSON


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [500, 502, 503, 504])
async def test_proveedor_5xx_es_transitorio(code: int) -> None:
    with pytest.raises(InferenceTransientError):
        await _generar_con(_server_error(code))


@pytest.mark.asyncio
async def test_proveedor_429_es_transitorio() -> None:
    with pytest.raises(InferenceTransientError):
        await _generar_con(_client_error(429))


@pytest.mark.asyncio
async def test_proveedor_timeout_es_timeout_transitorio() -> None:
    with pytest.raises(InferenceTimeoutError) as excinfo:
        await _generar_con(TimeoutError())
    assert isinstance(excinfo.value, InferenceTransientError)


@pytest.mark.asyncio
@pytest.mark.parametrize("code", [400, 401, 403, 404])
async def test_proveedor_4xx_es_terminal(code: int) -> None:
    with pytest.raises(InferenceTerminalError):
        await _generar_con(_client_error(code))


# ---------------------------------------------------------------------------
# 2.2 — Registro de proveedores
# ---------------------------------------------------------------------------
def test_registro_incluye_a_gemini() -> None:
    assert "gemini" in proveedores_registrados()


def test_resolver_gemini_devuelve_la_implementacion() -> None:
    proveedor = resolver_proveedor("gemini", client=_ClienteFalso(_ModelosFalsos([])))
    assert isinstance(proveedor, GeminiProvider)


def test_resolver_desconocido_falla_explicito() -> None:
    with pytest.raises(UnknownProviderError, match="desconocido"):
        resolver_proveedor("no-existe")


def test_hybrid_con_proveedor_desconocido_falla_en_inicializacion(monkeypatch) -> None:
    monkeypatch.setattr(
        hybrid_module, "get_settings", lambda: _settings(inference_provider="no-existe")
    )
    with pytest.raises(UnknownProviderError):
        HybridClassifier()


@pytest.mark.asyncio
async def test_hybrid_usa_el_proveedor_inyectado_sin_sdk(monkeypatch) -> None:
    settings = _settings()
    monkeypatch.setattr(hybrid_module, "get_settings", lambda: settings)
    monkeypatch.setattr(gemini_module, "get_settings", lambda: settings)
    fake = _ProveedorFalso(['{"categoría": "Bases de Datos", "confianza": 0.8}'])

    clasificador = HybridClassifier(provider=fake)
    # Descripcion sin senal determinista: escala a la etapa semantica.
    resultado = await clasificador.classify("zzq texto sin coincidencias")

    assert fake.llamadas == 1
    assert resultado.etapa == "gemini"
    assert resultado.sector_predicho == "Bases de Datos"


# ---------------------------------------------------------------------------
# 2.1 — Seleccion por configuracion (defaults y override)
# ---------------------------------------------------------------------------
def test_settings_defaults_resuelven_al_vigente() -> None:
    settings = _settings()
    assert settings.inference_provider == "gemini"
    assert settings.inference_model == "gemini-3.6-flash"


def test_settings_inference_model_vacio_hereda_gemini_model(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_MODEL", "gemini-modelo-heredado")
    settings = _settings()
    assert settings.inference_model == "gemini-modelo-heredado"


def test_settings_override_por_entorno(monkeypatch) -> None:
    monkeypatch.setenv("INFERENCE_PROVIDER", "otro-proveedor")
    monkeypatch.setenv("INFERENCE_MODEL", "modelo-x")
    settings = _settings()
    assert settings.inference_provider == "otro-proveedor"
    assert settings.inference_model == "modelo-x"


# ---------------------------------------------------------------------------
# 2.4 — Trazabilidad: el evento identifica proveedor y modelo, sin clave ni texto
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_evento_de_clasificacion_registra_proveedor_y_modelo(monkeypatch) -> None:
    settings = _settings()
    monkeypatch.setattr(gemini_module, "get_settings", lambda: settings)
    fake = _ProveedorFalso([_VALID_JSON])
    clasificador = GeminiClassifier(provider=fake)

    mock_logger = MagicMock()
    monkeypatch.setattr(gemini_module, "logger", mock_logger)
    descripcion = "El servidor de correo de la sucursal no responde"
    await clasificador.classify(descripcion)

    payload = repr(mock_logger.mock_calls)
    assert "gemini_classified" in payload
    assert "proveedor='gemini'" in payload
    assert "modelo='gemini-3.6-flash'" in payload
    assert "fake-gemini-key" not in payload
    assert descripcion not in payload
