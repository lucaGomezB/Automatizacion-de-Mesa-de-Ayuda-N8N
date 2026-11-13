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


# ---------------------------------------------------------------------------
# 1.2 Cache JSONL reanudable y bucle de corrida
# ---------------------------------------------------------------------------
def caso(id_: str, desc: str = "no funciona la vpn", sector: str = SECTOR_OK) -> CasoEvaluacion:
    return CasoEvaluacion(id=id_, descripcion=desc, sector_asignado=sector, sectores_adicionales=[])


def casos_de(*ids: str, bloque: str = bgs.BLOQUE_FUERA):
    return [(bloque, caso(i, f"descripcion {i}")) for i in ids]


META = {
    "corpus_hash_dentro": "a" * 64,
    "corpus_hash_fuera": "b" * 64,
    "modelo": "gemini-3.6-flash",
    "temperatura": 0.3,
    "top_p": 0.9,
    "max_output_tokens": 100,
    "max_reintentos": 2,
    "prompt_sha256": "c" * 64,
    "sdk_version": "2.34.0",
    "precios_usd_por_millon": bgs.PRECIOS_USD_POR_MILLON,
    "tope_llamadas": 400,
    "commit": "abc1234",
}


def armar(cliente_base, tope=400):
    contador = bgs.ContadorLlamadas(tope=tope)
    cliente = bgs.ClienteInstrumentado(cliente_base, contador)
    return cliente, clasificador_real(cliente)


def contador_de_reloj(paso: float = 0.1):
    t = {"v": 0.0}

    def reloj():
        t["v"] += paso
        return t["v"]

    return reloj


def correr(casos, cliente, clasificador, ruta, meta=None, reloj=None):
    return asyncio.run(
        bgs.correr_brazo(
            casos,
            clasificador,
            cliente,
            ruta,
            META if meta is None else meta,
            reloj=reloj or contador_de_reloj(),
            ahora=lambda: "2026-11-20T10:00:00+00:00",
        )
    )


def lineas(ruta: pathlib.Path) -> List[dict]:
    return [json.loads(x) for x in ruta.read_text(encoding="utf-8").splitlines()]


def test_leer_cache_inexistente_devuelve_vacio(tmp_path):
    meta, casos, descartes = bgs.leer_cache(tmp_path / "no_existe.jsonl")
    assert meta is None and casos == {} and descartes == 0


def test_corrida_registra_un_caso_por_linea_con_los_campos_comprometidos(tmp_path):
    ruta = tmp_path / "cache.jsonl"
    cliente, clasif = armar(ClienteFalso())
    resultado = correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    assert (resultado.registrados, resultado.omitidos, resultado.pendientes) == (2, 0, 0)
    registros = lineas(ruta)
    assert [r["tipo"] for r in registros] == ["meta", "caso", "caso"]
    primero = registros[1]
    assert set(primero) == {
        "tipo", "bloque", "caso_id", "sector_predicho", "confianza", "etapa", "intentos",
        "latencia_ms", "latencias_intento_ms", "tokens_entrada", "tokens_salida", "tokens_total",
        "tokens_origen", "error", "t_inicio_utc",
    }
    assert primero["caso_id"] == "I001" and primero["bloque"] == bgs.BLOQUE_FUERA
    assert primero["sector_predicho"] == SECTOR_OK and primero["confianza"] == 0.9
    assert primero["etapa"] == "gemini" and primero["error"] is None
    assert primero["intentos"] == 1 and primero["tokens_entrada"] == 800
    assert primero["t_inicio_utc"] == "2026-11-20T10:00:00+00:00"


def test_corrida_envia_a_gemini_el_prompt_completo_con_la_descripcion(tmp_path):
    base = ClienteFalso()
    cliente, clasif = armar(base)
    correr(casos_de("I001"), cliente, clasif, tmp_path / "c.jsonl")
    enviado = base.llamadas[0]["contents"]
    assert "descripcion I001" in enviado and "DESCRIPCIÓN DEL INCIDENTE" in enviado
    assert base.llamadas[0]["model"] == "gemini-3.6-flash"


def test_corrida_ningun_caso_queda_en_etapa_deterministica(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("A1", "A2", "A3", bloque=bgs.BLOQUE_DENTRO), cliente, clasif, ruta)
    etapas = {r["etapa"] for r in lineas(ruta) if r["tipo"] == "caso"}
    assert etapas == {"gemini"}


def test_respuesta_invalida_se_registra_como_fallback_sin_reintento(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso(guion=["esto no es json"]))
    correr(casos_de("I001"), cliente, clasif, ruta)
    reg = lineas(ruta)[1]
    assert reg["etapa"] == "fallback" and reg["confianza"] == 0.0
    assert reg["error"] == "respuesta_invalida" and reg["intentos"] == 1


def test_falla_transitoria_y_luego_exito_cuenta_dos_intentos(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso(guion=[TimeoutError("lento"), json_ok("Sistemas", 0.8)]))
    correr(casos_de("I001"), cliente, clasif, ruta)
    reg = lineas(ruta)[1]
    assert reg["intentos"] == 2 and len(reg["latencias_intento_ms"]) == 2
    assert reg["sector_predicho"] == "Sistemas" and reg["etapa"] == "gemini" and reg["error"] is None


def test_agotados_los_intentos_se_registra_sin_sector_y_sigue_con_el_proximo(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso(guion=[TimeoutError("x")] * 3))
    resultado = correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    registros = [r for r in lineas(ruta) if r["tipo"] == "caso"]
    assert registros[0]["sector_predicho"] is None and registros[0]["etapa"] == "fallback"
    assert registros[0]["error"] == "GeminiTimeoutError" and registros[0]["intentos"] == 3
    assert registros[1]["etapa"] == "gemini"
    assert resultado.registrados == 2


def test_reanudacion_solo_llama_a_los_casos_no_registrados(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2)
    resultado = correr(casos_de("I001", "I002", "I003", "I004"), cliente2, clasif2, ruta)
    assert (resultado.registrados, resultado.omitidos, resultado.pendientes) == (2, 2, 0)
    assert len(base2.llamadas) == 2
    ids = [r["caso_id"] for r in lineas(ruta) if r["tipo"] == "caso"]
    assert ids == ["I001", "I002", "I003", "I004"]
    assert resultado.llamadas_totales == 4


def test_reanudacion_con_todo_registrado_no_llama(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001"), cliente, clasif, ruta)
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2)
    resultado = correr(casos_de("I001"), cliente2, clasif2, ruta)
    assert base2.llamadas == [] and resultado.omitidos == 1 and resultado.registrados == 0


def test_cache_con_metadatos_incompatibles_aborta_sin_llamar_ni_modificar(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001"), cliente, clasif, ruta)
    antes = ruta.read_bytes()
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2)
    otra = dict(META, modelo="otro-modelo")
    with pytest.raises(bgs.CacheIncompatibleError) as exc:
        correr(casos_de("I001", "I002"), cliente2, clasif2, ruta, meta=otra)
    assert "modelo" in str(exc.value)
    assert base2.llamadas == [] and ruta.read_bytes() == antes


@pytest.mark.parametrize("clave,valor", [("prompt_sha256", "d" * 64), ("corpus_hash_fuera", "e" * 64)])
def test_cache_incompatible_por_prompt_o_corpus(tmp_path, clave, valor):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001"), cliente, clasif, ruta)
    cliente2, clasif2 = armar(ClienteFalso())
    with pytest.raises(bgs.CacheIncompatibleError) as exc:
        correr(casos_de("I002"), cliente2, clasif2, ruta, meta=dict(META, **{clave: valor}))
    assert clave in str(exc.value)


def test_metadatos_que_no_afectan_la_compatibilidad_se_ignoran(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001"), cliente, clasif, ruta)
    cliente2, clasif2 = armar(ClienteFalso())
    resultado = correr(casos_de("I001", "I002"), cliente2, clasif2, ruta, meta=dict(META, commit="otro999"))
    assert resultado.registrados == 1


def test_tope_alcanzado_conserva_lo_hecho_y_reporta_pendientes(tmp_path):
    ruta = tmp_path / "c.jsonl"
    base = ClienteFalso()
    cliente, clasif = armar(base, tope=2)
    resultado = correr(casos_de("I001", "I002", "I003", "I004"), cliente, clasif, ruta)
    assert resultado.tope_alcanzado is True
    assert (resultado.registrados, resultado.pendientes) == (2, 2)
    assert len(base.llamadas) == 2
    assert [r["caso_id"] for r in lineas(ruta) if r["tipo"] == "caso"] == ["I001", "I002"]


def test_tope_alcanzado_en_pleno_reintento_descarta_el_caso_pero_cuenta_la_llamada(tmp_path):
    ruta = tmp_path / "c.jsonl"
    base = ClienteFalso(guion=[TimeoutError("x")])
    cliente, clasif = armar(base, tope=1)
    resultado = correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    assert resultado.tope_alcanzado and resultado.registrados == 0 and resultado.pendientes == 2
    assert len(base.llamadas) == 1
    assert lineas(ruta)[-1] == {"tipo": "descarte", "caso_id": "I001", "intentos": 1}
    # Al reanudar con el mismo tope, el descarte cuenta: no queda margen para llamar.
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2, tope=1)
    resultado2 = correr(casos_de("I001", "I002"), cliente2, clasif2, ruta)
    assert base2.llamadas == [] and resultado2.tope_alcanzado and resultado2.llamadas_totales == 1


def test_el_tope_es_acumulado_entre_reanudaciones(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso(), tope=3)
    correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2, tope=3)
    resultado = correr(casos_de("I001", "I002", "I003", "I004"), cliente2, clasif2, ruta)
    assert len(base2.llamadas) == 1 and resultado.registrados == 1
    assert resultado.tope_alcanzado and resultado.pendientes == 1


def test_cola_truncada_por_un_corte_se_repara_y_el_caso_se_repite(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001", "I002"), cliente, clasif, ruta)
    texto = ruta.read_text(encoding="utf-8")
    corte = texto[: texto.rstrip("\n").rfind("\n") + 1] + '{"tipo": "caso", "caso_id": "I00'
    ruta.write_text(corte, encoding="utf-8")
    base2 = ClienteFalso()
    cliente2, clasif2 = armar(base2)
    correr(casos_de("I001", "I002"), cliente2, clasif2, ruta)
    assert len(base2.llamadas) == 1
    assert [r["caso_id"] for r in lineas(ruta) if r["tipo"] == "caso"] == ["I001", "I002"]


def test_latencia_total_del_caso_usa_el_reloj_inyectado(tmp_path):
    ruta = tmp_path / "c.jsonl"
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("I001"), cliente, clasif, ruta, reloj=reloj_falso([10.0, 10.75]))
    reg = lineas(ruta)[1]
    assert reg["latencia_ms"] == pytest.approx(750.0)
    assert len(reg["latencias_intento_ms"]) == 1


# ---------------------------------------------------------------------------
# 1.4 / 1.5 Dry-run, guardas y CLI
# ---------------------------------------------------------------------------
def escribir_corpus(ruta: pathlib.Path, prefijo: str, n: int) -> pathlib.Path:
    casos = [
        {
            "id": f"{prefijo}{i:03d}",
            "descripcion": f"descripcion del caso {prefijo}{i:03d}",
            "canal_origen": "email",
            "sector_asignado": SECTOR_OK,
            "sectores_adicionales": [],
        }
        for i in range(1, n + 1)
    ]
    ruta.write_text(
        json.dumps({"schema_version": 1, "metadata": {"descripcion": "t", "total_casos": n}, "casos": casos}),
        encoding="utf-8",
    )
    return ruta


@pytest.fixture
def corpora(tmp_path):
    dentro = escribir_corpus(tmp_path / "dentro.json", "R", 3)
    fuera = escribir_corpus(tmp_path / "fuera.json", "I", 2)
    return ["--corpus-dentro", str(dentro), "--corpus-fuera", str(fuera), "--cache", str(tmp_path / "cache.jsonl")]


def ejecutar(argv, capsys, **kwargs):
    codigo = bgs.main(argv, **kwargs)
    salida = capsys.readouterr()
    return codigo, salida.out + salida.err


def test_plan_dry_run_cuenta_llamadas_minimas_maximas_y_costos():
    plan = bgs.plan_dry_run(pendientes=303, max_reintentos=2, ya_hechas=0, tope=400)
    assert plan["llamadas_minimas"] == 303
    assert plan["llamadas_maximas"] == 400  # 909 teoricas, acotadas por el tope
    assert plan["costo_usd"]["introductorio"]["minimo"] == pytest.approx(303 * 0.0007125)
    assert plan["costo_usd"]["estandar"]["minimo"] == pytest.approx(303 * 0.001425)
    assert plan["costo_usd"]["introductorio"]["maximo"] == pytest.approx(400 * 0.0007125)


def test_plan_dry_run_descuenta_lo_ya_hecho_del_tope():
    plan = bgs.plan_dry_run(pendientes=10, max_reintentos=2, ya_hechas=395, tope=400)
    assert plan["llamadas_minimas"] == 10
    assert plan["llamadas_maximas"] == 5
    assert plan["alcanza_el_tope"] is True
    assert bgs.plan_dry_run(pendientes=10, max_reintentos=2, ya_hechas=0, tope=400)["alcanza_el_tope"] is False


def test_dry_run_imprime_el_plan_sin_llamar_ni_escribir_el_cache(corpora, tmp_path, capsys):
    def prohibida():
        raise AssertionError("el dry-run no puede construir el cliente de la API")

    codigo, texto = ejecutar(
        ["--dry-run", *corpora], capsys, fabrica_cliente=prohibida, entorno={}, version_sdk=lambda: "2.8.0"
    )
    assert codigo == 0
    assert "pendientes: 5" in texto and "introductorio" in texto and "estandar" in texto
    assert "llamadas minimas: 5" in texto
    assert not (tmp_path / "cache.jsonl").exists()


def test_dry_run_no_imprime_la_credencial_aunque_este_en_el_entorno(corpora, capsys):
    codigo, texto = ejecutar(
        ["--dry-run", *corpora],
        capsys,
        fabrica_cliente=lambda: None,
        entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.34.0",
    )
    assert codigo == 0 and CLAVE_FALSA not in texto


def test_dry_run_informa_la_version_del_sdk_y_si_incumple_el_pin(corpora, capsys):
    _, incumple = ejecutar(["--dry-run", *corpora], capsys, entorno={}, version_sdk=lambda: "2.8.0")
    _, cumple = ejecutar(["--dry-run", *corpora], capsys, entorno={}, version_sdk=lambda: "2.34.0")
    assert "2.8.0" in incumple and "NO cumple" in incumple
    assert "2.34.0" in cumple and "NO cumple" not in cumple


def test_dry_run_sobre_los_corpus_reales_cuenta_303_casos(tmp_path, capsys):
    codigo, texto = ejecutar(
        ["--dry-run", "--cache", str(tmp_path / "c.jsonl")], capsys, entorno={}, version_sdk=lambda: "2.34.0"
    )
    assert codigo == 0
    assert "pendientes: 303" in texto and "dentro_muestra: 200" in texto and "fuera_muestra: 103" in texto


def test_dry_run_descuenta_los_casos_ya_registrados(corpora, tmp_path, capsys):
    cliente, clasif = armar(ClienteFalso())
    correr(casos_de("R001", "R002"), cliente, clasif, tmp_path / "cache.jsonl")
    _, texto = ejecutar(["--dry-run", *corpora], capsys, entorno={}, version_sdk=lambda: "2.34.0")
    assert "pendientes: 3" in texto and "ya registrados: 2" in texto


def test_sin_confirmar_costo_aborta_con_codigo_2_sin_llamar(corpora, tmp_path, capsys):
    def prohibida():
        raise AssertionError("sin confirmacion no se construye el cliente")

    codigo, texto = ejecutar(
        [*corpora], capsys, fabrica_cliente=prohibida, entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.34.0",
    )
    assert codigo == 2 and "--confirmar-costo" in texto
    assert not (tmp_path / "cache.jsonl").exists()


def test_la_confirmacion_se_exige_antes_que_cualquier_otra_guarda(corpora, capsys):
    codigo, texto = ejecutar([*corpora], capsys, entorno={}, version_sdk=lambda: "2.8.0")
    assert codigo == 2 and "--confirmar-costo" in texto and "2.8.0" not in texto


def test_sdk_fuera_del_pin_aborta_con_codigo_2_citando_version_y_rango(corpora, capsys):
    codigo, texto = ejecutar(
        ["--confirmar-costo", *corpora], capsys, entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.8.0", fabrica_cliente=lambda: pytest.fail("no debe construir cliente"),
    )
    assert codigo == 2 and "2.8.0" in texto and ">=2.33,<3" in texto


@pytest.mark.parametrize("entorno", [{}, {"GEMINI_API_KEY": ""}, {"GEMINI_API_KEY": bgs.ENTORNO_INERTE["GEMINI_API_KEY"]}])
def test_sin_credencial_real_en_el_entorno_aborta_sin_imprimir_nada_secreto(corpora, capsys, entorno):
    codigo, texto = ejecutar(
        ["--confirmar-costo", *corpora], capsys, entorno=entorno, version_sdk=lambda: "2.34.0",
        fabrica_cliente=lambda: pytest.fail("no debe construir cliente"),
    )
    assert codigo == 2 and "GEMINI_API_KEY" in texto


def test_prompt_no_congelado_aborta_con_codigo_2(corpora, tmp_path, capsys, monkeypatch):
    otro = tmp_path / "prompt_otro.txt"
    otro.write_text("un prompt distinto", encoding="utf-8")
    monkeypatch.setattr(bgs, "PROMPT_CONGELADO_PATH", otro)
    codigo, texto = ejecutar(
        ["--confirmar-costo", *corpora], capsys, entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.34.0", fabrica_cliente=lambda: pytest.fail("no debe construir cliente"),
    )
    assert codigo == 2 and "prompt" in texto.lower()


def test_tope_superior_al_prerregistrado_aborta_antes_de_llamar(corpora, capsys):
    codigo, texto = ejecutar(
        ["--confirmar-costo", "--tope-llamadas", "500", *corpora], capsys,
        entorno={"GEMINI_API_KEY": CLAVE_FALSA}, version_sdk=lambda: "2.34.0",
        fabrica_cliente=lambda: pytest.fail("no debe construir cliente"),
    )
    assert codigo == 2 and "400" in texto


def test_corrida_completa_con_cliente_simulado_escribe_el_cache_y_no_imprime_la_clave(corpora, tmp_path, capsys):
    base = ClienteFalso()
    codigo, texto = ejecutar(
        ["--confirmar-costo", *corpora], capsys, entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.34.0", fabrica_cliente=lambda: base, sleep=sin_espera,
    )
    assert codigo == 0 and CLAVE_FALSA not in texto
    registros = lineas(tmp_path / "cache.jsonl")
    assert [r["tipo"] for r in registros] == ["meta"] + ["caso"] * 5
    assert {r["bloque"] for r in registros[1:]} == {bgs.BLOQUE_DENTRO, bgs.BLOQUE_FUERA}
    meta = registros[0]
    assert meta["sdk_version"] == "2.34.0" and meta["modelo"] == "gemini-3.6-flash"
    assert meta["tope_llamadas"] == 400 and CLAVE_FALSA not in json.dumps(meta)
    assert len(base.llamadas) == 5


def test_corrida_que_alcanza_el_tope_sale_con_codigo_3_y_conserva_el_cache(corpora, tmp_path, capsys):
    base = ClienteFalso()
    codigo, texto = ejecutar(
        ["--confirmar-costo", "--tope-llamadas", "2", *corpora], capsys,
        entorno={"GEMINI_API_KEY": CLAVE_FALSA}, version_sdk=lambda: "2.34.0",
        fabrica_cliente=lambda: base, sleep=sin_espera,
    )
    assert codigo == 3 and "pendientes: 3" in texto
    assert len([r for r in lineas(tmp_path / "cache.jsonl") if r["tipo"] == "caso"]) == 2


def test_la_clave_no_se_filtra_en_un_error_del_proveedor(corpora, tmp_path, capsys):
    base = ClienteFalso(guion=[RuntimeError(f"fallo con {CLAVE_FALSA}")] * 5)
    codigo, texto = ejecutar(
        ["--confirmar-costo", *corpora], capsys, entorno={"GEMINI_API_KEY": CLAVE_FALSA},
        version_sdk=lambda: "2.34.0", fabrica_cliente=lambda: base, sleep=sin_espera,
    )
    assert codigo == 0
    assert CLAVE_FALSA not in texto
    assert CLAVE_FALSA not in (tmp_path / "cache.jsonl").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 2.1 Desviacion declarada: reintento de fallos tecnicos (2026-11-13)
# ---------------------------------------------------------------------------
def reg_caso(caso_id="R001", **cambios) -> dict:
    base = {
        "tipo": "caso", "bloque": bgs.BLOQUE_DENTRO, "caso_id": caso_id, "sector_predicho": SECTOR_OK,
        "confianza": 0.9, "etapa": "gemini", "intentos": 1, "latencia_ms": 100.0,
        "latencias_intento_ms": [100.0], "tokens_entrada": 800, "tokens_salida": 20, "tokens_total": 820,
        "tokens_origen": "api", "error": None, "t_inicio_utc": "2026-11-13T16:55:34+00:00",
    }
    base.update(cambios)
    return base


FALLO_TECNICO = dict(
    sector_predicho=None, confianza=0.0, etapa="fallback", error="GeminiUnavailableError",
    tokens_entrada=0, tokens_salida=0, tokens_total=0,
)


def test_fallo_de_indisponibilidad_sin_tokens_es_reintentable():
    assert bgs.es_fallo_tecnico(reg_caso(**FALLO_TECNICO)) is True


def test_fallo_de_timeout_sin_tokens_es_reintentable():
    assert bgs.es_fallo_tecnico(reg_caso(**{**FALLO_TECNICO, "error": "GeminiTimeoutError", "intentos": 3})) is True


def test_respuesta_invalida_con_tokens_no_es_reintentable():
    invalido = reg_caso(
        sector_predicho=None, confianza=0.0, etapa="fallback", error="respuesta_invalida"
    )
    assert bgs.es_fallo_tecnico(invalido) is False


def test_fallo_de_indisponibilidad_con_tokens_no_es_reintentable():
    # Hubo respuesta del modelo: es conducta del sistema, no un fallo de transporte.
    assert bgs.es_fallo_tecnico(reg_caso(**{**FALLO_TECNICO, "tokens_total": 820})) is False


def test_registro_exitoso_o_sin_error_no_es_reintentable():
    assert bgs.es_fallo_tecnico(reg_caso()) is False
    assert bgs.es_fallo_tecnico(reg_caso(**{**FALLO_TECNICO, "error": None})) is False
    assert bgs.es_fallo_tecnico(reg_caso(**{**FALLO_TECNICO, "error": ""})) is False
