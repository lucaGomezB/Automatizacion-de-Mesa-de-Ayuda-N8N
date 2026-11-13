"""
Ejecutor del brazo «Gemini solo» (c-215).

Manda TODOS los casos a la etapa Gemini REAL del backend (mismo modelo, prompt, parametros de
muestreo, validacion del Anexo H y reintentos que el hibrido `hybrid-v3`), sin reglas
deterministicas, inyectandole un cliente instrumentado que mide latencia, tokens e intentos y
hace cumplir un tope duro de llamadas. NO duplica el prompt ni la validacion del backend.

Es una corrida PAGA: exige `--confirmar-costo`. El modo `--dry-run` cuenta llamadas y costo sin
red, sin leer la clave y sin escribir el cache. La clave `GEMINI_API_KEY` se lee SOLO del
entorno, en tiempo de ejecucion, y jamas se imprime ni se guarda.

Prerregistro (openspec/changes/c-215-*/design.md): tope duro de 400 llamadas, una sola corrida,
SDK `google-genai` en `>=2.33,<3`, precios declarados en `PRECIOS_USD_POR_MILLON`.
"""

from __future__ import annotations

import hashlib
import json
import os
import pathlib
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Tope duro de llamadas (cada intento a la API cuenta) prerregistrado en design.md D3.
TOPE_LLAMADAS_DURO = 400

#: Rango de `google-genai` fijado por el proyecto (`openspec/config.yaml`, `stack.inference`).
SDK_RANGO_TEXTO = ">=2.33,<3"
SDK_MINIMO: Tuple[int, ...] = (2, 33)
SDK_LIMITE_EXCLUSIVO: Tuple[int, ...] = (3,)

#: Precios de lista citados por la tesis (seccion 8, consultados el 2026-10-19), en USD por millon
#: de tokens. NO estan versionados en otro lugar del repositorio: son un PARAMETRO declarado.
#: El introductorio rige hasta el 2026-12-31; el estandar desde el 2027-01-01.
PRECIOS_USD_POR_MILLON: Dict[str, Dict[str, float]] = {
    "introductorio": {"entrada": 0.75, "salida": 3.75},
    "estandar": {"entrada": 1.50, "salida": 7.50},
}

#: Supuesto de la tesis cuando la API no devuelve `usage_metadata`: tokens por invocacion.
TOKENS_SUPUESTOS_ENTRADA = 800
TOKENS_SUPUESTOS_SALIDA = 30

PROMPT_CONGELADO_PATH = _REPO_ROOT / "docs" / "prompt_gemini.txt"

#: Valores inertes para construir `Settings` del backend. NO son secretos. `GEMINI_API_KEY` se
#: incluye solo para que `Settings` pueda construirse en el dry-run; el camino pago exige la real.
ENTORNO_INERTE: Dict[str, str] = {
    "DATABASE_URL": "postgresql+asyncpg://ci:ci@localhost:5432/ci_dummy",
    "GEMINI_API_KEY": "inerte-sin-llamadas",  # gitleaks:allow (ficticio)
    "PSEUDONYMIZATION_ENCRYPTION_KEY": "MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",  # gitleaks:allow (dummy)
    "JWT_SECRET_KEY": "ci-dummy-jwt-secret-key-for-testing-only",  # gitleaks:allow (dummy)
    "COST_GUARD_CALLER_HMAC_KEY": "ci-dummy-cost-guard-caller-hmac-key",  # gitleaks:allow (dummy)
    "DIRECTORY_BLIND_INDEX_KEY": "ci-dummy-directory-blind-index-key",  # gitleaks:allow (dummy)
}


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------
class TopeDeLlamadasExcedido(Exception):
    """El contador acumulado de llamadas alcanzo el tope: no se emite la llamada."""


class VersionSdkIncompatibleError(RuntimeError):
    """La version instalada de `google-genai` esta fuera del rango fijado por el proyecto."""


class TopeNoPermitidoError(ValueError):
    """El tope pedido supera el prerregistrado o no es positivo."""


class PromptNoCongeladoError(RuntimeError):
    """El prompt cargado por el backend no es el de `docs/prompt_gemini.txt`."""


# ---------------------------------------------------------------------------
# Entorno del backend
# ---------------------------------------------------------------------------
def asegurar_backend_en_path() -> None:
    """Agrega `App/Backend` a `sys.path` (misma resolucion que el resto de `evaluation/`)."""
    ruta = str(_REPO_ROOT / "App" / "Backend")
    if ruta not in sys.path:
        sys.path.insert(0, ruta)


# ---------------------------------------------------------------------------
# Guardas puras
# ---------------------------------------------------------------------------
def _parsear_version(texto: str) -> Tuple[int, ...]:
    partes = re.match(r"^\s*(\d+(?:\.\d+)*)", texto or "")
    if not partes:
        raise VersionSdkIncompatibleError(
            f"no se pudo interpretar la version de google-genai '{texto}'; se exige {SDK_RANGO_TEXTO}"
        )
    return tuple(int(p) for p in partes.group(1).split("."))


def _completar(version: Tuple[int, ...], largo: int) -> Tuple[int, ...]:
    return version + (0,) * (largo - len(version))


def verificar_version_sdk(version: str) -> None:
    """Aborta si `google-genai` esta fuera de `>=2.33,<3` (pin de `openspec/config.yaml`)."""
    parseada = _parsear_version(version)
    largo = max(len(parseada), len(SDK_MINIMO), len(SDK_LIMITE_EXCLUSIVO))
    p = _completar(parseada, largo)
    if not (_completar(SDK_MINIMO, largo) <= p < _completar(SDK_LIMITE_EXCLUSIVO, largo)):
        raise VersionSdkIncompatibleError(
            f"google-genai {version} instalada; el proyecto exige {SDK_RANGO_TEXTO}. "
            "Instala la version del pin antes de la corrida paga (este ejecutor no instala paquetes)."
        )


def verificar_tope(tope: int) -> int:
    """El tope debe ser positivo y no superar el prerregistrado (solo puede bajarse)."""
    if tope <= 0:
        raise TopeNoPermitidoError(f"el tope de llamadas debe ser positivo (recibido {tope})")
    if tope > TOPE_LLAMADAS_DURO:
        raise TopeNoPermitidoError(
            f"tope {tope} supera el prerregistrado de {TOPE_LLAMADAS_DURO} llamadas; "
            "subirlo exige cambiar el design.md del change"
        )
    return tope


def estimar_costo_usd(tokens_entrada: float, tokens_salida: float, escenario: str) -> float:
    """Costo en USD de `tokens_entrada` + `tokens_salida` al precio del `escenario`."""
    precio = PRECIOS_USD_POR_MILLON[escenario]
    return tokens_entrada * 1e-6 * precio["entrada"] + tokens_salida * 1e-6 * precio["salida"]


def costo_llamada_supuesta_usd(escenario: str) -> float:
    """Costo de UNA llamada con el supuesto de la tesis (800 tokens de entrada, 30 de salida)."""
    return estimar_costo_usd(TOKENS_SUPUESTOS_ENTRADA, TOKENS_SUPUESTOS_SALIDA, escenario)


def verificar_prompt_congelado(
    prompt_cargado: str, ruta_congelada: pathlib.Path = PROMPT_CONGELADO_PATH
) -> str:
    """SHA-256 del prompt cargado por el backend; aborta si difiere del de `docs/prompt_gemini.txt`."""
    esperado = hashlib.sha256(
        pathlib.Path(ruta_congelada).read_text(encoding="utf-8").strip().encode("utf-8")
    ).hexdigest()
    cargado = hashlib.sha256(prompt_cargado.encode("utf-8")).hexdigest()
    if cargado != esperado:
        raise PromptNoCongeladoError(
            f"el prompt cargado (SHA-256 {cargado}) no es el congelado "
            f"({esperado}, docs/prompt_gemini.txt)"
        )
    return cargado


# ---------------------------------------------------------------------------
# Cliente instrumentado
# ---------------------------------------------------------------------------
class ContadorLlamadas:
    """Contador acumulado de llamadas (cada intento a la API cuenta) con tope duro."""

    def __init__(self, tope: int, acumuladas: int = 0) -> None:
        self.tope = tope
        self.total = acumuladas

    def reservar(self) -> None:
        if self.total >= self.tope:
            raise TopeDeLlamadasExcedido(
                f"tope de {self.tope} llamadas alcanzado ({self.total} acumuladas); no se emite otra"
            )
        self.total += 1


@dataclass
class MedicionCaso:
    """Mediciones de las llamadas de UN caso."""

    intentos: int = 0
    latencias_intento_ms: List[float] = field(default_factory=list)
    tokens_entrada: int = 0
    tokens_salida: int = 0
    tokens_total: int = 0
    tokens_origen: str = "api"


def _tokens_de(respuesta: Any) -> Optional[Tuple[int, int, int]]:
    """`(entrada, salida, total)` de `usage_metadata`, o None si la API no lo expone."""
    uso = getattr(respuesta, "usage_metadata", None)
    if uso is None:
        return None
    entrada = getattr(uso, "prompt_token_count", None)
    candidatos = getattr(uso, "candidates_token_count", None)
    if entrada is None or candidatos is None:
        return None
    salida = int(candidatos) + int(getattr(uso, "thoughts_token_count", None) or 0)
    total = getattr(uso, "total_token_count", None)
    return int(entrada), salida, int(total) if total is not None else int(entrada) + salida


class _Modelos:
    def __init__(self, padre: "ClienteInstrumentado") -> None:
        self._padre = padre

    async def generate_content(self, **kwargs: Any) -> Any:
        return await self._padre._generar(**kwargs)


class _Aio:
    def __init__(self, padre: "ClienteInstrumentado") -> None:
        self.models = _Modelos(padre)


class ClienteInstrumentado:
    """
    Envoltorio de un cliente `genai` con la misma superficie que usa `GeminiClassifier`
    (`client.aio.models.generate_content`). Mide `perf_counter` por intento, copia
    `usage_metadata`, cuenta los intentos y se niega a emitir la llamada que superaria el tope.
    """

    def __init__(
        self,
        base: Any,
        contador: ContadorLlamadas,
        reloj: Callable[[], float] = time.perf_counter,
    ) -> None:
        self._base = base
        self.contador = contador
        self._reloj = reloj
        self._medicion = MedicionCaso()
        self.aio = _Aio(self)

    def abrir_caso(self) -> None:
        self._medicion = MedicionCaso()

    def cerrar_caso(self) -> MedicionCaso:
        return self._medicion

    async def _generar(self, **kwargs: Any) -> Any:
        self.contador.reservar()
        medicion = self._medicion
        medicion.intentos += 1
        inicio = self._reloj()
        try:
            respuesta = await self._base.aio.models.generate_content(**kwargs)
        finally:
            medicion.latencias_intento_ms.append((self._reloj() - inicio) * 1000.0)
        tokens = _tokens_de(respuesta)
        if tokens is None:
            tokens = (TOKENS_SUPUESTOS_ENTRADA, TOKENS_SUPUESTOS_SALIDA, TOKENS_SUPUESTOS_ENTRADA + TOKENS_SUPUESTOS_SALIDA)
            medicion.tokens_origen = "supuesto"
        medicion.tokens_entrada += tokens[0]
        medicion.tokens_salida += tokens[1]
        medicion.tokens_total += tokens[2]
        return respuesta


# ---------------------------------------------------------------------------
# Cache JSONL reanudable
# ---------------------------------------------------------------------------
BLOQUE_DENTRO = "dentro_muestra"
BLOQUE_FUERA = "fuera_muestra"

#: Metadatos que deben coincidir al reanudar. `commit`, `generado_en` y `tope_llamadas` NO afectan
#: la comparabilidad de los registros ya escritos (el tope se hace cumplir aparte).
CLAVES_COMPATIBILIDAD = (
    "corpus_hash_dentro",
    "corpus_hash_fuera",
    "modelo",
    "temperatura",
    "top_p",
    "max_output_tokens",
    "max_reintentos",
    "prompt_sha256",
    "sdk_version",
    "precios_usd_por_millon",
)


class CacheIncompatibleError(RuntimeError):
    """El cache existente fue escrito con otra configuracion que la de la corrida actual."""


def leer_cache(ruta: pathlib.Path) -> Tuple[Optional[dict], Dict[str, dict], int]:
    """
    Lee el cache: `(meta, casos_por_id, intentos_descartados)`.

    Una ultima linea truncada (corte durante la escritura) se ignora. Un cache inexistente
    devuelve `(None, {}, 0)`.
    """
    ruta = pathlib.Path(ruta)
    if not ruta.exists():
        return None, {}, 0
    meta: Optional[dict] = None
    casos: Dict[str, dict] = {}
    descartados = 0
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        try:
            registro = json.loads(linea)
        except json.JSONDecodeError:
            continue
        tipo = registro.get("tipo")
        if tipo == "meta":
            meta = registro
        elif tipo == "caso":
            casos[registro["caso_id"]] = registro
        elif tipo == "descarte":
            descartados += int(registro.get("intentos", 0))
    return meta, casos, descartados


def llamadas_acumuladas(casos: Dict[str, dict], descartados: int) -> int:
    """Llamadas ya hechas: intentos de los casos registrados mas los de los casos descartados."""
    return sum(int(r["intentos"]) for r in casos.values()) + descartados


def _reparar_cola(ruta: pathlib.Path) -> None:
    """Elimina una ultima linea truncada para que el proximo append no la corrompa."""
    contenido = ruta.read_bytes()
    if not contenido or contenido.endswith(b"\n"):
        return
    corte = contenido.rfind(b"\n") + 1
    ruta.write_bytes(contenido[:corte])


def _verificar_compatibilidad(existente: dict, actual: Dict[str, Any]) -> None:
    diferencias = [
        f"{clave}: cache={existente.get(clave)!r} != actual={actual.get(clave)!r}"
        for clave in CLAVES_COMPATIBILIDAD
        if existente.get(clave) != actual.get(clave)
    ]
    if diferencias:
        raise CacheIncompatibleError(
            "el cache existente no es compatible con esta corrida: " + "; ".join(diferencias)
        )


def _agregar(ruta: pathlib.Path, registro: dict) -> None:
    """Agrega una linea JSON (LF) y la fuerza a disco."""
    with open(ruta, "ab") as destino:
        destino.write((json.dumps(registro, ensure_ascii=False) + "\n").encode("utf-8"))
        destino.flush()
        os.fsync(destino.fileno())


# ---------------------------------------------------------------------------
# Bucle de corrida
# ---------------------------------------------------------------------------
@dataclass
class ResultadoCorrida:
    registrados: int = 0
    omitidos: int = 0
    pendientes: int = 0
    tope_alcanzado: bool = False
    llamadas_totales: int = 0


def _ahora_utc() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _causa_es_tope(exc: BaseException) -> bool:
    actual: Optional[BaseException] = exc
    while actual is not None:
        if isinstance(actual, TopeDeLlamadasExcedido):
            return True
        actual = actual.__cause__ or actual.__context__
    return False


async def correr_brazo(
    casos: Sequence[Tuple[str, Any]],
    clasificador: Any,
    cliente: ClienteInstrumentado,
    ruta_cache: pathlib.Path,
    meta: Dict[str, Any],
    *,
    reloj: Callable[[], float] = time.perf_counter,
    ahora: Callable[[], str] = _ahora_utc,
) -> ResultadoCorrida:
    """
    Clasifica cada caso `(bloque, CasoEvaluacion)` pendiente con `clasificador` (la etapa Gemini
    real con `cliente` inyectado), persistiendo cada caso apenas termina.

    Fija el contador del cliente en las llamadas ya acumuladas del cache (el tope es global entre
    reanudaciones). Un fallo del proveedor se registra y no corta la corrida; alcanzar el tope si.

    Raises:
        CacheIncompatibleError: el cache existente no coincide con `meta` (sin llamar ni escribir).
    """
    ruta_cache = pathlib.Path(ruta_cache)
    existente, hechos, descartados = leer_cache(ruta_cache)
    if existente is not None:
        _verificar_compatibilidad(existente, meta)
        _reparar_cola(ruta_cache)
    else:
        ruta_cache.parent.mkdir(parents=True, exist_ok=True)
        _agregar(ruta_cache, {"tipo": "meta", **meta})

    cliente.contador.total = llamadas_acumuladas(hechos, descartados)
    resultado = ResultadoCorrida(omitidos=sum(1 for _, c in casos if c.id in hechos))
    pendientes = [(bloque, c) for bloque, c in casos if c.id not in hechos]

    for indice, (bloque, caso) in enumerate(pendientes):
        cliente.abrir_caso()
        inicio_utc = ahora()
        inicio = reloj()
        sector: Optional[str] = None
        confianza = 0.0
        etapa = "fallback"
        error: Optional[str] = None
        try:
            clasificado = await clasificador.classify(caso.descripcion)
            sector = clasificado.sector_predicho
            confianza = float(clasificado.confianza)
            etapa = str(clasificado.etapa)
            if etapa == "fallback":
                error = "respuesta_invalida"
        except Exception as exc:  # noqa: BLE001 - un fallo del proveedor no corta la corrida
            if _causa_es_tope(exc):
                medicion = cliente.cerrar_caso()
                if medicion.intentos:
                    _agregar(
                        ruta_cache,
                        {"tipo": "descarte", "caso_id": caso.id, "intentos": medicion.intentos},
                    )
                resultado.tope_alcanzado = True
                resultado.pendientes = len(pendientes) - indice
                resultado.llamadas_totales = cliente.contador.total
                return resultado
            error = type(exc).__name__
        latencia_ms = (reloj() - inicio) * 1000.0
        medicion = cliente.cerrar_caso()
        _agregar(
            ruta_cache,
            {
                "tipo": "caso",
                "bloque": bloque,
                "caso_id": caso.id,
                "sector_predicho": sector,
                "confianza": confianza,
                "etapa": etapa,
                "intentos": medicion.intentos,
                "latencia_ms": latencia_ms,
                "latencias_intento_ms": medicion.latencias_intento_ms,
                "tokens_entrada": medicion.tokens_entrada,
                "tokens_salida": medicion.tokens_salida,
                "tokens_total": medicion.tokens_total,
                "tokens_origen": medicion.tokens_origen,
                "error": error,
                "t_inicio_utc": inicio_utc,
            },
        )
        resultado.registrados += 1

    resultado.llamadas_totales = cliente.contador.total
    return resultado
