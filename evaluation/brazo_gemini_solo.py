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

import argparse
import asyncio
import hashlib
import importlib.metadata
import json
import os
import pathlib
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple

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


#: Errores de indisponibilidad o transporte del proveedor (la llamada no produjo respuesta del
#: modelo). Una respuesta invalida del modelo (`respuesta_invalida`) NO es un fallo tecnico.
ERRORES_TECNICOS_REINTENTABLES = frozenset({"GeminiUnavailableError", "GeminiTimeoutError"})


def es_fallo_tecnico(registro: Mapping[str, Any]) -> bool:
    """
    Fallo tecnico reintentable (desviacion declarada del 2026-11-13): registro en `fallback`, con
    un error de indisponibilidad o transporte y SIN tokens, es decir, sin respuesta del modelo.
    """
    return (
        registro.get("etapa") == "fallback"
        and registro.get("error") in ERRORES_TECNICOS_REINTENTABLES
        and int(registro.get("tokens_total") or 0) == 0
    )


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


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------
def plan_dry_run(*, pendientes: int, max_reintentos: int, ya_hechas: int, tope: int) -> Dict[str, Any]:
    """Llamadas minimas y maximas y costo estimado (supuesto de la tesis) sin llamar a la API."""
    restantes = max(0, tope - ya_hechas)
    teoricas = pendientes * (max_reintentos + 1)
    maximas = min(teoricas, restantes)
    minimas = pendientes
    return {
        "pendientes": pendientes,
        "ya_hechas": ya_hechas,
        "tope": tope,
        "llamadas_minimas": minimas,
        "llamadas_maximas": maximas,
        "alcanza_el_tope": teoricas > restantes,
        "costo_usd": {
            escenario: {
                "minimo": minimas * costo_llamada_supuesta_usd(escenario),
                "maximo": maximas * costo_llamada_supuesta_usd(escenario),
            }
            for escenario in PRECIOS_USD_POR_MILLON
        },
    }


def _lineas_dry_run(
    plan: Dict[str, Any], por_bloque: Dict[str, int], registrados: int, version: Optional[str]
) -> List[str]:
    lineas = [
        "Dry-run del brazo 'Gemini solo' (sin red, sin clave y sin escribir el cache)",
        f"Casos totales: {sum(por_bloque.values())} "
        f"({BLOQUE_DENTRO}: {por_bloque[BLOQUE_DENTRO]}, {BLOQUE_FUERA}: {por_bloque[BLOQUE_FUERA]})",
        f"ya registrados: {registrados}",
        f"pendientes: {plan['pendientes']}",
        f"llamadas minimas: {plan['llamadas_minimas']} (una por caso)",
        f"llamadas maximas: {plan['llamadas_maximas']} (con reintentos, acotadas por el tope de "
        f"{plan['tope']}; ya hechas: {plan['ya_hechas']})",
        f"Costo estimado con el supuesto de la tesis ({TOKENS_SUPUESTOS_ENTRADA} tokens de entrada y "
        f"{TOKENS_SUPUESTOS_SALIDA} de salida por llamada; orientativo, no es una factura):",
    ]
    for escenario, precio in PRECIOS_USD_POR_MILLON.items():
        costo = plan["costo_usd"][escenario]
        lineas.append(
            f"- {escenario} ({precio['entrada']}/{precio['salida']} USD por millon de tokens de "
            f"entrada/salida): minimo USD {costo['minimo']:.4f}, maximo USD {costo['maximo']:.4f}"
        )
    if version is None:
        lineas.append(f"google-genai: no instalada (la corrida real exige {SDK_RANGO_TEXTO})")
    else:
        try:
            verificar_version_sdk(version)
            lineas.append(f"google-genai instalada: {version} (dentro de {SDK_RANGO_TEXTO})")
        except VersionSdkIncompatibleError:
            lineas.append(
                f"google-genai instalada: {version} (NO cumple {SDK_RANGO_TEXTO}: la corrida real abortaria)"
            )
    return lineas


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
RUTA_CORPUS_DENTRO = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
RUTA_CORPUS_FUERA = _REPO_ROOT / "evaluation" / "data" / "campana" / "corpus_independiente.json"
RUTA_CACHE_DEFECTO = (
    _REPO_ROOT / "evaluation" / "data" / "campana" / "brazo_gemini_solo" / "cache_brazo_gemini_solo.jsonl"
)

CODIGO_OK = 0
CODIGO_GUARDA = 2
CODIGO_TOPE = 3


def _version_sdk_instalada() -> Optional[str]:
    try:
        return importlib.metadata.version("google-genai")
    except importlib.metadata.PackageNotFoundError:
        return None


def cargar_casos(dentro: pathlib.Path, fuera: pathlib.Path) -> List[Tuple[str, Any]]:
    """Casos `(bloque, CasoEvaluacion)`: primero los de dentro de la muestra, luego los de fuera."""
    from evaluation.campana import cargar_corpus_solo_lectura

    casos = [(BLOQUE_DENTRO, c) for c in cargar_corpus_solo_lectura(dentro)]
    casos += [(BLOQUE_FUERA, c) for c in cargar_corpus_solo_lectura(fuera)]
    ids = [c.id for _, c in casos]
    repetidos = sorted({i for i in ids if ids.count(i) > 1})
    if repetidos:
        raise ValueError(f"caso_id repetidos entre los corpus: {repetidos[:5]}")
    return casos


def _construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="cuenta llamadas y costo sin red ni clave")
    parser.add_argument(
        "--confirmar-costo", action="store_true", help="confirma la corrida PAGA (obligatorio para llamar)"
    )
    parser.add_argument(
        "--tope-llamadas", type=int, default=TOPE_LLAMADAS_DURO,
        help=f"tope duro de llamadas, solo puede bajarse (prerregistrado: {TOPE_LLAMADAS_DURO})",
    )
    parser.add_argument("--corpus-dentro", type=pathlib.Path, default=RUTA_CORPUS_DENTRO)
    parser.add_argument("--corpus-fuera", type=pathlib.Path, default=RUTA_CORPUS_FUERA)
    parser.add_argument("--cache", type=pathlib.Path, default=RUTA_CACHE_DEFECTO)
    return parser


def _commit_o_desconocido() -> str:
    try:
        from evaluation.run_evaluation import obtener_commit_corto

        return obtener_commit_corto()
    except Exception:  # noqa: BLE001 - la procedencia no debe impedir la corrida
        return "desconocido"


def _cliente_real() -> Any:
    from app.classifiers.gemini_classifier import get_genai_client  # type: ignore

    return get_genai_client()


def main(
    argv: Optional[Sequence[str]] = None,
    *,
    entorno: Optional[Dict[str, str]] = None,
    version_sdk: Optional[Callable[[], Optional[str]]] = None,
    fabrica_cliente: Optional[Callable[[], Any]] = None,
    sleep: Optional[Callable[[float], Any]] = None,
) -> int:
    """
    Punto de entrada. Devuelve 0 (completo), 2 (una guarda impidio la corrida) o 3 (tope alcanzado).

    Los parametros por palabra clave son inyectables para las pruebas; en uso real se usan el
    entorno del proceso, la version instalada de `google-genai` y el cliente real del backend.
    """
    args = _construir_parser().parse_args(argv)
    entorno = os.environ if entorno is None else entorno
    version = (version_sdk or _version_sdk_instalada)()

    if not args.dry_run and not args.confirmar_costo:
        print(
            "ERROR: corrida paga sin confirmar. Revisa el costo con --dry-run y confirma "
            "explicitamente con --confirmar-costo.",
            file=sys.stderr,
        )
        return CODIGO_GUARDA
    try:
        tope = verificar_tope(args.tope_llamadas)
        if not args.dry_run:
            verificar_version_sdk(version or "")
            clave = entorno.get("GEMINI_API_KEY")
            if not clave or clave == ENTORNO_INERTE["GEMINI_API_KEY"]:
                raise RuntimeError(
                    "falta GEMINI_API_KEY en el entorno: exportala antes de la corrida paga "
                    "(el ejecutor no la imprime ni la guarda)"
                )
        casos = cargar_casos(args.corpus_dentro, args.corpus_fuera)
    except (TopeNoPermitidoError, VersionSdkIncompatibleError, RuntimeError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return CODIGO_GUARDA

    for nombre, valor in ENTORNO_INERTE.items():  # completa lo que falte; nunca pisa lo existente
        os.environ.setdefault(nombre, valor)
    asegurar_backend_en_path()
    from app.config.settings import get_settings  # type: ignore

    if not args.dry_run:
        get_settings.cache_clear()  # que `Settings` tome la clave real del entorno
    settings = get_settings()

    _, hechos, descartados = leer_cache(args.cache)
    ya_hechas = llamadas_acumuladas(hechos, descartados)
    pendientes = [c for _, c in casos if c.id not in hechos]
    por_bloque = {
        BLOQUE_DENTRO: sum(1 for b, _ in casos if b == BLOQUE_DENTRO),
        BLOQUE_FUERA: sum(1 for b, _ in casos if b == BLOQUE_FUERA),
    }

    if args.dry_run:
        plan = plan_dry_run(
            pendientes=len(pendientes), max_reintentos=settings.gemini_max_retries,
            ya_hechas=ya_hechas, tope=tope,
        )
        print("\n".join(_lineas_dry_run(plan, por_bloque, len(hechos), version)))
        return CODIGO_OK

    from app.classifiers import gemini_classifier  # type: ignore
    from app.classifiers.gemini_classifier import GeminiClassifier  # type: ignore
    from evaluation.run_evaluation import _compute_corpus_hash

    try:
        prompt_sha = verificar_prompt_congelado(gemini_classifier._PROMPT_TEMPLATE, PROMPT_CONGELADO_PATH)
    except PromptNoCongeladoError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return CODIGO_GUARDA

    meta = {
        "change": "c-215-brazo-gemini-solo-y-contraste-de-la-hipotesis-de-eficiencia",
        "modo": "gemini_solo",
        "corpus_hash_dentro": _compute_corpus_hash(args.corpus_dentro),
        "corpus_hash_fuera": _compute_corpus_hash(args.corpus_fuera),
        "modelo": settings.gemini_model,
        "temperatura": settings.gemini_temperature,
        "top_p": settings.gemini_top_p,
        "max_output_tokens": settings.gemini_max_output_tokens,
        "max_reintentos": settings.gemini_max_retries,
        "prompt_sha256": prompt_sha,
        "sdk_version": version,
        "precios_usd_por_millon": PRECIOS_USD_POR_MILLON,
        "tokens_supuestos": {"entrada": TOKENS_SUPUESTOS_ENTRADA, "salida": TOKENS_SUPUESTOS_SALIDA},
        "tope_llamadas": tope,
        "commit": _commit_o_desconocido(),
        "generado_en": _ahora_utc(),
    }
    base = (fabrica_cliente or _cliente_real)()
    cliente = ClienteInstrumentado(base, ContadorLlamadas(tope=tope))
    clasificador = GeminiClassifier(client=cliente, sleep=sleep)  # type: ignore[arg-type]
    print(
        f"Corrida PAGA confirmada: {len(pendientes)} casos pendientes, tope {tope} llamadas "
        f"(ya hechas: {ya_hechas})."
    )
    try:
        resultado = asyncio.run(correr_brazo(casos, clasificador, cliente, args.cache, meta))
    except CacheIncompatibleError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return CODIGO_GUARDA

    print(
        f"registrados: {resultado.registrados}, omitidos: {resultado.omitidos}, "
        f"pendientes: {resultado.pendientes}, llamadas acumuladas: {resultado.llamadas_totales}"
    )
    if resultado.tope_alcanzado:
        print(
            f"TOPE de {tope} llamadas alcanzado: el cache conserva lo hecho; pendientes: "
            f"{resultado.pendientes}. No se emitieron mas llamadas."
        )
        return CODIGO_TOPE
    return CODIGO_OK


if __name__ == "__main__":
    raise SystemExit(main())
