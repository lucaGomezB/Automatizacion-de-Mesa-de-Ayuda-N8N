"""
Pruebas del ejecutor del brazo «Gemini solo» (c-215).

Strict TDD. Todas las pruebas usan un cliente simulado: sin red, sin API de Gemini, sin
credenciales reales y sin escribir fuera de `tmp_path`.
"""

from __future__ import annotations

import asyncio
import hashlib
import json
import pathlib
from types import SimpleNamespace
from typing import Any, List, Optional

import pytest

import evaluation.brazo_gemini_solo as bgs
from evaluation.corpus import CasoEvaluacion
from evaluation.run_evaluation import PaidRunNotConfirmedError

SECTOR_OK = "Seguridad Informatica"
CLAVE_FALSA = "clave-falsa-de-prueba-no-real"  # gitleaks:allow (ficticia)


# ---------------------------------------------------------------------------
# Dobles de prueba
# ---------------------------------------------------------------------------
class RespuestaFalsa:
    """Imita la respuesta de `generate_content` (`.text` y `.usage_metadata`)."""

    def __init__(self, texto: str, uso: Any = "por_defecto"):
        self.text = texto
        if uso == "por_defecto":
            uso = SimpleNamespace(
                prompt_token_count=800,
                candidates_token_count=20,
                thoughts_token_count=None,
                total_token_count=820,
            )
        self.usage_metadata = uso


def json_ok(sector: str = SECTOR_OK, confianza: float = 0.9) -> str:
    return json.dumps({"categoría": sector, "confianza": confianza}, ensure_ascii=False)


class ClienteFalso:
    """Cliente `genai` simulado: `aio.models.generate_content` devuelve lo programado."""

    def __init__(self, guion: Optional[List[Any]] = None, por_defecto: Optional[str] = None):
        self.guion = list(guion or [])
        self.por_defecto = por_defecto if por_defecto is not None else json_ok()
        self.llamadas: List[dict] = []
        self.aio = SimpleNamespace(models=SimpleNamespace(generate_content=self._generar))

    async def _generar(self, *, model, contents, config):
        self.llamadas.append({"model": model, "contents": contents})
        item = self.guion.pop(0) if self.guion else self.por_defecto
        if isinstance(item, BaseException):
            raise item
        return item if isinstance(item, RespuestaFalsa) else RespuestaFalsa(item)


class ErrorTransitorio(Exception):
    """Falla transitoria: la etapa Gemini real la trata como reintentable via TimeoutError."""


def reloj_falso(pasos: List[float]):
    valores = iter(pasos)
    return lambda: next(valores)


async def sin_espera(_segundos: float) -> None:
    return None


@pytest.fixture(autouse=True)
def entorno_inerte(monkeypatch):
    """Variables inertes para construir `Settings` del backend; la clave es ficticia."""
    for clave, valor in bgs.ENTORNO_INERTE.items():
        monkeypatch.setenv(clave, valor)
    monkeypatch.setenv("GEMINI_API_KEY", CLAVE_FALSA)
    bgs.asegurar_backend_en_path()
    from app.config.settings import get_settings  # type: ignore

    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def clasificador_real(cliente: Any):
    """La etapa Gemini REAL del backend con el cliente inyectado y sin esperas."""
    from app.classifiers.gemini_classifier import GeminiClassifier  # type: ignore

    return GeminiClassifier(client=cliente, sleep=sin_espera, random_fn=lambda: 0.0)


# ---------------------------------------------------------------------------
# 1.1 Version del SDK, tope permitido y costo (funciones puras)
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("version", ["2.33.0", "2.34.0", "2.99.1", "2.33"])
def test_version_sdk_dentro_del_pin_se_acepta(version):
    bgs.verificar_version_sdk(version)  # no lanza


@pytest.mark.parametrize("version", ["2.8.0", "2.32.9", "3.0.0", "3.1.0", "1.0.0"])
def test_version_sdk_fuera_del_pin_aborta_citando_instalada_y_rango(version):
    with pytest.raises(bgs.VersionSdkIncompatibleError) as exc:
        bgs.verificar_version_sdk(version)
    assert version in str(exc.value)
    assert ">=2.33,<3" in str(exc.value)


def test_version_sdk_no_parseable_aborta():
    with pytest.raises(bgs.VersionSdkIncompatibleError):
        bgs.verificar_version_sdk("desconocida")


@pytest.mark.parametrize("tope", [1, 303, 400])
def test_tope_hasta_el_prerregistrado_es_valido(tope):
    assert bgs.verificar_tope(tope) == tope


@pytest.mark.parametrize("tope", [401, 1000])
def test_tope_sobre_el_prerregistrado_aborta_citando_400(tope):
    with pytest.raises(bgs.TopeNoPermitidoError) as exc:
        bgs.verificar_tope(tope)
    assert "400" in str(exc.value)


@pytest.mark.parametrize("tope", [0, -5])
def test_tope_no_positivo_aborta(tope):
    with pytest.raises(bgs.TopeNoPermitidoError):
        bgs.verificar_tope(tope)


def test_costo_estimado_con_precios_declarados_por_escenario():
    # 800 tokens de entrada y 30 de salida por llamada (supuesto de la tesis).
    intro = bgs.estimar_costo_usd(1000, 30, "introductorio")
    estandar = bgs.estimar_costo_usd(1000, 30, "estandar")
    assert intro == pytest.approx(1000 * 1e-6 * 0.75 + 30 * 1e-6 * 3.75)
    assert estandar == pytest.approx(2 * intro)
    assert bgs.estimar_costo_usd(0, 0, "introductorio") == 0.0


def test_costo_por_llamada_supuesta_es_la_de_la_tesis():
    assert bgs.costo_llamada_supuesta_usd("introductorio") == pytest.approx(0.0007125)
    assert bgs.costo_llamada_supuesta_usd("estandar") == pytest.approx(0.001425)


def test_escenario_de_precio_desconocido_falla():
    with pytest.raises(KeyError):
        bgs.estimar_costo_usd(1, 1, "inexistente")


# ---------------------------------------------------------------------------
# 1.1 Cliente instrumentado
# ---------------------------------------------------------------------------
async def test_cliente_instrumentado_mide_latencia_tokens_e_intentos():
    base = ClienteFalso()
    contador = bgs.ContadorLlamadas(tope=10)
    cliente = bgs.ClienteInstrumentado(base, contador, reloj=reloj_falso([1.0, 1.25, 2.0, 2.5]))
    cliente.abrir_caso()
    await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    medicion = cliente.cerrar_caso()
    assert medicion.intentos == 2
    assert medicion.latencias_intento_ms == [250.0, 500.0]
    assert medicion.tokens_entrada == 1600
    assert medicion.tokens_salida == 40
    assert medicion.tokens_total == 1640
    assert medicion.tokens_origen == "api"
    assert contador.total == 2


async def test_cliente_instrumentado_suma_razonamiento_a_la_salida():
    uso = SimpleNamespace(
        prompt_token_count=500, candidates_token_count=10, thoughts_token_count=7, total_token_count=517
    )
    base = ClienteFalso(guion=[RespuestaFalsa(json_ok(), uso)])
    cliente = bgs.ClienteInstrumentado(base, bgs.ContadorLlamadas(tope=5), reloj=reloj_falso([0.0, 0.1]))
    cliente.abrir_caso()
    await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    medicion = cliente.cerrar_caso()
    assert (medicion.tokens_entrada, medicion.tokens_salida) == (500, 17)


async def test_cliente_instrumentado_sin_usage_metadata_imputa_el_supuesto_de_la_tesis():
    base = ClienteFalso(guion=[RespuestaFalsa(json_ok(), None)])
    cliente = bgs.ClienteInstrumentado(base, bgs.ContadorLlamadas(tope=5), reloj=reloj_falso([0.0, 0.1]))
    cliente.abrir_caso()
    await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    medicion = cliente.cerrar_caso()
    assert medicion.tokens_origen == "supuesto"
    assert (medicion.tokens_entrada, medicion.tokens_salida) == (800, 30)


async def test_cliente_instrumentado_cuenta_el_intento_fallido_como_llamada():
    base = ClienteFalso(guion=[TimeoutError("lento")])
    contador = bgs.ContadorLlamadas(tope=5)
    cliente = bgs.ClienteInstrumentado(base, contador, reloj=reloj_falso([0.0, 0.5]))
    cliente.abrir_caso()
    with pytest.raises(TimeoutError):
        await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    medicion = cliente.cerrar_caso()
    assert medicion.intentos == 1
    assert contador.total == 1
    assert medicion.latencias_intento_ms == [500.0]


async def test_cliente_instrumentado_se_niega_a_superar_el_tope_sin_llamar():
    base = ClienteFalso()
    contador = bgs.ContadorLlamadas(tope=2)
    cliente = bgs.ClienteInstrumentado(base, contador, reloj=reloj_falso([0.0, 0.1, 0.2, 0.3]))
    cliente.abrir_caso()
    for _ in range(2):
        await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    with pytest.raises(bgs.TopeDeLlamadasExcedido):
        await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    assert len(base.llamadas) == 2
    assert contador.total == 2


async def test_contador_parte_del_total_acumulado_de_reanudaciones():
    contador = bgs.ContadorLlamadas(tope=10, acumuladas=9)
    cliente = bgs.ClienteInstrumentado(ClienteFalso(), contador, reloj=reloj_falso([0.0, 0.1, 0.2]))
    cliente.abrir_caso()
    await cliente.aio.models.generate_content(model="m", contents="p", config=None)
    with pytest.raises(bgs.TopeDeLlamadasExcedido):
        await cliente.aio.models.generate_content(model="m", contents="p", config=None)


# ---------------------------------------------------------------------------
# 1.3 Prompt congelado
# ---------------------------------------------------------------------------
def test_prompt_congelado_coincidente_devuelve_el_sha256(tmp_path):
    ruta = tmp_path / "prompt.txt"
    ruta.write_text("  PROMPT DE PRUEBA\n", encoding="utf-8")
    sha = bgs.verificar_prompt_congelado("PROMPT DE PRUEBA", ruta)
    assert sha == hashlib.sha256(b"PROMPT DE PRUEBA").hexdigest()


def test_prompt_distinto_aborta_nombrando_ambos_sha256(tmp_path):
    ruta = tmp_path / "prompt.txt"
    ruta.write_text("congelado", encoding="utf-8")
    cargado = "otro texto"
    with pytest.raises(bgs.PromptNoCongeladoError) as exc:
        bgs.verificar_prompt_congelado(cargado, ruta)
    assert hashlib.sha256(cargado.encode()).hexdigest() in str(exc.value)
    assert hashlib.sha256(b"congelado").hexdigest() in str(exc.value)


def test_prompt_real_del_backend_coincide_con_docs_prompt_gemini():
    from app.classifiers import gemini_classifier  # type: ignore

    sha = bgs.verificar_prompt_congelado(gemini_classifier._PROMPT_TEMPLATE)
    assert len(sha) == 64
