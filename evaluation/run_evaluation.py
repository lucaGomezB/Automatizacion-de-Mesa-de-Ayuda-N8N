"""
Runner de evaluación del clasificador híbrido (multietiqueta, C-27).

Orquesta la carga del corpus JSON, la invocación del clasificador caso por caso,
el cálculo de métricas multietiqueta y la escritura del reporte.

Uso (corpus real):
    python -m evaluation.run_evaluation

    Requiere:
    - data/corpus_evaluacion_pseudonimizado.json (no trackeado en git)
    - GEMINI_API_KEY en el entorno
    - PYTHONPATH configurado para incluir App/Backend/

Diseño (D1): el clasificador se inyecta por parámetro, lo que permite
    testear con FakeClassifier sin llamadas a Gemini.
    El main() real usa HybridClassifier; los tests usan FakeClassifier.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import pathlib
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Protocol

from evaluation.corpus import CasoEvaluacion, cargar_corpus
from evaluation.metrics import (
    CLASES,
    aciertos_estrictos,
    aciertos_pertenencia,
    exactitud_global,
    exactitud_subconjunto,
    f1_macro,
    f1_micro,
    f1_por_clase,
    intervalo_wilson,
    jaccard_promedio,
    matriz_confusion,
    perdida_hamming,
    precision_por_clase,
    sensibilidad_por_clase,
    soporte_por_clase,
)

# ---------------------------------------------------------------------------
# Rutas por defecto
# ---------------------------------------------------------------------------
_REPO_ROOT = pathlib.Path(__file__).parent.parent
CORPUS_REAL_PATH = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.json"
REPORT_PATH = pathlib.Path(__file__).parent / "report.md"
PREDICCIONES_PATH = pathlib.Path(__file__).parent / "predicciones.json"


# ---------------------------------------------------------------------------
# Gate de corrida paga y estimacion de costo (C-36)
# ---------------------------------------------------------------------------
class PaidRunNotConfirmedError(RuntimeError):
    """La corrida paga fue rechazada por falta de confirmacion explicita."""


# Orden de magnitud orientativo para Gemini 2.5 Flash con un perfil de
# ~1.500 tokens de entrada y ~200 de salida. No es una tarifa de facturacion.
ESTIMATED_COST_PER_CALL_USD = 0.0002

CONFIRM_PAID_ENV_VAR = "EVALUATION_CONFIRM_PAID"
_TRUTHY_VALUES = {"1", "true", "yes"}


def estimated_cost_usd(corpus_count: int) -> float:
    """Costo total estimado de clasificar ``corpus_count`` casos."""
    return corpus_count * ESTIMATED_COST_PER_CALL_USD


def format_cost_estimation(
    corpus_count: int,
    cost_per_call: Optional[float] = None,
) -> str:
    """Renderiza la estimacion orientativa previa a una corrida paga."""
    if cost_per_call is None:
        cost_per_call = ESTIMATED_COST_PER_CALL_USD
    total = corpus_count * cost_per_call
    return "\n".join(
        [
            "Estimacion de costo (orientativa, no es una factura):",
            f"- Casos del corpus: {corpus_count}",
            f"- Costo asumido por llamada: USD {cost_per_call:.6f}",
            f"- Costo total estimado: USD {total:.6f}",
        ]
    )


def _env_confirm_paid() -> bool:
    """True si EVALUATION_CONFIRM_PAID tiene un valor verdadero (1/true/yes)."""
    value = os.environ.get(CONFIRM_PAID_ENV_VAR, "")
    return value.strip().lower() in _TRUTHY_VALUES


# ---------------------------------------------------------------------------
# Tipos
# ---------------------------------------------------------------------------
@dataclass
class Prediccion:
    """Resultado de clasificar un caso del corpus."""

    caso_id: str
    descripcion: str
    sector_asignado: str
    sector_predicho: str
    confianza: float
    etapa: str  # "deterministic" | "gemini" | "fallback"
    sectores_adicionales: List[str] = field(default_factory=list)


class ClasificadorProtocol(Protocol):
    """Protocolo mínimo que debe cumplir el clasificador inyectado."""

    async def classify(self, descripcion: str) -> Any:
        ...


# ---------------------------------------------------------------------------
# Core: recolección de predicciones
# ---------------------------------------------------------------------------
async def evaluar_corpus(
    corpus: List[CasoEvaluacion],
    classifier: ClasificadorProtocol,
) -> List[Prediccion]:
    """
    Ejecuta el clasificador sobre cada caso del corpus y recolecta predicciones.

    Args:
        corpus: Lista de casos cargados del JSON.
        classifier: Clasificador con método `async classify(descripcion)`.

    Returns:
        Lista de Prediccion en el mismo orden que el corpus.
    """
    predicciones: List[Prediccion] = []
    for caso in corpus:
        resultado = await classifier.classify(caso.descripcion)
        pred = Prediccion(
            caso_id=caso.id,
            descripcion=caso.descripcion,
            sector_asignado=caso.sector_asignado,
            sector_predicho=resultado.sector_predicho,
            sectores_adicionales=list(resultado.sectores_adicionales),
            confianza=float(resultado.confianza),
            etapa=str(resultado.etapa),
        )
        predicciones.append(pred)
    return predicciones


# ---------------------------------------------------------------------------
# Core: generación de reporte
# ---------------------------------------------------------------------------
def generar_reporte(
    predicciones: List[Prediccion],
    corpus: List[CasoEvaluacion],
    output_path: pathlib.Path = REPORT_PATH,
) -> str:
    """
    Genera el reporte de métricas multietiqueta en Markdown.

    Reutiliza las funciones puras de evaluation.metrics (design D5).

    Args:
        predicciones: Lista de predicciones del runner.
        corpus: Lista de casos originales del corpus (mismo orden).
        output_path: Ruta donde escribir el reporte (default: evaluation/report.md).

    Returns:
        Contenido del reporte como string.
    """
    reales = [p.sector_asignado for p in predicciones]
    predichas = [p.sector_predicho for p in predicciones]
    adicionales_predichos = [p.sectores_adicionales for p in predicciones]

    conjuntos_verdad = [caso.conjunto_verdad for caso in corpus]
    conjuntos_predichos = [
        frozenset({p.sector_predicho, *p.sectores_adicionales}) for p in predicciones
    ]

    mc = matriz_confusion(reales, predichas)
    exactitud = exactitud_global(reales, predichos=predichas)
    aciertos = aciertos_estrictos(reales, predichas)
    lower_ic, upper_ic = intervalo_wilson(aciertos, len(reales))

    aciertos_pert = aciertos_pertenencia(reales, predichas, adicionales_predichos)
    lower_pert, upper_pert = intervalo_wilson(aciertos_pert, len(reales))
    exactitud_pert = aciertos_pert / len(reales) if reales else 0.0

    subset = exactitud_subconjunto(conjuntos_verdad, conjuntos_predichos)
    hamming = perdida_hamming(conjuntos_verdad, conjuntos_predichos)
    micro_f1 = f1_micro(conjuntos_verdad, conjuntos_predichos)
    jaccard = jaccard_promedio(conjuntos_verdad, conjuntos_predichos)

    precisiones = precision_por_clase(mc)
    sensibilidades = sensibilidad_por_clase(mc)
    f1s = f1_por_clase(mc)
    f1_m = f1_macro(f1s)
    soportes = soporte_por_clase(mc)

    etapas: Dict[str, int] = {"deterministic": 0, "gemini": 0, "fallback": 0}
    for pred in predicciones:
        etapa = pred.etapa if pred.etapa in etapas else "fallback"
        etapas[etapa] += 1

    lineas = [
        "# Reporte de Evaluación del Clasificador (multietiqueta)",
        "",
        f"**Total de casos evaluados:** {len(predicciones)}",
        "",
        "## Etapas del pipeline",
        "",
        "| Etapa | Casos |",
        "|-------|-------|",
        f"| Deterministic | {etapas['deterministic']} |",
        f"| Gemini | {etapas['gemini']} |",
        f"| Fallback | {etapas['fallback']} |",
        "",
        "## Exactitud",
        "",
        "Definiciones (design D5): igualdad estricta del sector principal y",
        "pertenencia del sector asignado al conjunto predicho.",
        "",
        f"- **Exactitud (estricta):** {exactitud:.4f} ({exactitud * 100:.1f}%)",
        f"- **Aciertos (estrictos):** {aciertos} / {len(reales)}",
        f"- **IC Wilson 95% (estricto):** [{lower_ic:.4f}, {upper_ic:.4f}]",
        f"- **Exactitud (pertenencia):** {exactitud_pert:.4f} ({exactitud_pert * 100:.1f}%)",
        f"- **Aciertos (pertenencia):** {aciertos_pert} / {len(reales)}",
        f"- **IC Wilson 95% (pertenencia):** [{lower_pert:.4f}, {upper_pert:.4f}]",
        "",
        "## Matriz de Confusión (primaria 5x5)",
        "",
        "Filas = sector asignado | Columnas = sector predicho principal",
        "",
    ]

    header = "| Asignado \\ Predicho | " + " | ".join(CLASES) + " |"
    separator = "|" + "---|" * (len(CLASES) + 1)
    lineas.append(header)
    lineas.append(separator)
    for sector_asignado in CLASES:
        fila = f"| **{sector_asignado}** | "
        celdas = " | ".join(str(mc[sector_asignado][p]) for p in CLASES)
        lineas.append(fila + celdas + " |")

    lineas += [
        "",
        "## Métricas por sector (one-vs-rest)",
        "",
        "| Sector | Precisión | Sensibilidad | F1 | Soporte |",
        "|--------|-----------|--------------|-----|---------|",
    ]
    for sector in CLASES:
        lineas.append(
            f"| {sector} | {precisiones[sector]:.4f} | {sensibilidades[sector]:.4f} "
            f"| {f1s[sector]:.4f} | {soportes[sector]} |"
        )

    lineas += [
        "",
        "## Métricas de conjunto",
        "",
        f"- **Subset accuracy:** {subset:.4f}",
        f"- **Hamming loss:** {hamming:.4f}",
        f"- **Micro-F1:** {micro_f1:.4f}",
        f"- **Macro-F1:** {f1_m:.4f}",
        f"- **Jaccard (IoU) promedio:** {jaccard:.4f}",
        "",
        "---",
        "_Generado automáticamente por `evaluation/run_evaluation.py`_",
    ]

    contenido = "\n".join(lineas)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(contenido, encoding="utf-8")
    return contenido


# ---------------------------------------------------------------------------
# Helpers de cache (D1, D2, D3)
# ---------------------------------------------------------------------------
def _compute_corpus_hash(corpus_path: pathlib.Path) -> str:
    """
    Calcula el hash SHA-256 del contenido binario del archivo de corpus.

    Args:
        corpus_path: Ruta al archivo de corpus JSON.

    Returns:
        Hex digest SHA-256 (64 caracteres).
    """
    return hashlib.sha256(corpus_path.read_bytes()).hexdigest()


def _get_classifier_version(classifier: Any) -> str:
    """
    Obtiene la clave de version del clasificador.

    Devuelve `classifier.CACHE_VERSION` si el atributo existe;
    en caso contrario, devuelve `type(classifier).__name__`.

    Args:
        classifier: Instancia del clasificador.

    Returns:
        String identificador de version del clasificador.
    """
    return getattr(classifier, "CACHE_VERSION", type(classifier).__name__)


def _is_cache_valid(
    predicciones_path: pathlib.Path,
    corpus_hash: str,
    corpus_count: int,
    classifier_version: str,
) -> bool:
    """
    Verifica si el archivo de predicciones existente es un cache valido.

    Un cache es valido si y solo si:
    - El archivo existe.
    - Contiene el campo `cache_meta` de nivel superior.
    - `cache_meta.corpus_hash` coincide con `corpus_hash`.
    - `cache_meta.corpus_count` coincide con `corpus_count`.
    - `cache_meta.classifier_version` coincide con `classifier_version`.

    Args:
        predicciones_path: Ruta al archivo predicciones.json.
        corpus_hash: Hash SHA-256 del archivo de corpus actual.
        corpus_count: Cantidad de casos en el corpus actual.
        classifier_version: Clave de version del clasificador actual.

    Returns:
        True si el cache es valido, False en cualquier otro caso.
    """
    if not predicciones_path.exists():
        return False
    try:
        data = json.loads(predicciones_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False

    if not isinstance(data, dict) or "cache_meta" not in data:
        return False

    meta = data["cache_meta"]
    return (
        meta.get("corpus_hash") == corpus_hash
        and meta.get("corpus_count") == corpus_count
        and meta.get("classifier_version") == classifier_version
    )


# ---------------------------------------------------------------------------
# Persistencia de predicciones (artefacto intermedio)
# ---------------------------------------------------------------------------
def guardar_predicciones(
    predicciones: List[Prediccion],
    output_path: pathlib.Path = PREDICCIONES_PATH,
    cache_meta: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Persiste las predicciones a JSON para no re-invocar Gemini al regenerar el reporte.

    El archivo escrito usa el nuevo formato con `cache_meta` de nivel superior:

        {
            "cache_meta": { ... },
            "predictions": [ ... ]
        }

    Si `cache_meta` es None, se escribe el campo como objeto vacio ({}). Los callers
    que generan el cache completo deben pasar el dict de metadata; esta firma permite
    compatibilidad con usos directos que no necesitan cache.

    Args:
        predicciones: Lista de predicciones a persistir.
        output_path: Ruta del JSON (default: evaluation/predicciones.json).
        cache_meta: Metadata de cache a incluir en el archivo. Si es None, se usa {}.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    datos = {
        "cache_meta": cache_meta if cache_meta is not None else {},
        "predictions": [asdict(p) for p in predicciones],
    }
    output_path.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cargar_predicciones(input_path: pathlib.Path) -> List[Prediccion]:
    """
    Carga predicciones previamente persistidas desde JSON.

    Compatible con ambos formatos:
    - Nuevo formato: `{"cache_meta": {...}, "predictions": [...]}` — lee desde `predictions`.
    - Formato antiguo (arreglo plano): lee directamente el arreglo.

    Args:
        input_path: Ruta del JSON con predicciones.

    Returns:
        Lista de Prediccion.
    """
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if isinstance(data, dict) and "predictions" in data:
        datos = data["predictions"]
    else:
        datos = data
    return [Prediccion(**d) for d in datos]


# ---------------------------------------------------------------------------
# main_con_corpus_real — punto de entrada para la corrida real (testeable)
# ---------------------------------------------------------------------------
def _ensure_backend_on_path() -> None:
    """Agrega App/Backend/ a sys.path para importar los clasificadores reales."""
    backend_path = str(_REPO_ROOT / "App" / "Backend")
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)


def _version_clasificador_real() -> str:
    """Devuelve el CACHE_VERSION del HybridClassifier real sin construirlo (W-3).

    Construir el clasificador real exige credenciales (GeminiClassifier ->
    get_settings). Un cache hit no debe pagar ese costo: la version vive en
    ``app.constants`` (modulo liviano) y se lee sin importar ``app.classifiers``,
    que arrastra ``app.core.database`` -> ``get_settings()``.
    """
    try:
        _ensure_backend_on_path()
        from app.constants import HYBRID_CACHE_VERSION  # type: ignore[import]

        return HYBRID_CACHE_VERSION
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar HYBRID_CACHE_VERSION. "
            "Asegurate de correr con PYTHONPATH que incluya App/Backend/. "
            "Ver evaluation/README.md para instrucciones de setup."
        ) from exc


def _resolver_clasificador_real() -> ClasificadorProtocol:
    """Importa y construye el HybridClassifier real (camino pago).

    Se aísla en una funcion para que los tests puedan sustituirla sin tocar
    el backend ni disparar una llamada paga.
    """
    try:
        _ensure_backend_on_path()
        from app.classifiers.hybrid import HybridClassifier  # type: ignore[import]

        return HybridClassifier()
    except ImportError as exc:
        raise ImportError(
            "No se pudo importar HybridClassifier. "
            "Asegurate de correr con PYTHONPATH que incluya App/Backend/. "
            "Ver evaluation/README.md para instrucciones de setup."
        ) from exc


async def main_con_corpus_real(
    corpus_path: pathlib.Path = CORPUS_REAL_PATH,
    classifier: Optional[ClasificadorProtocol] = None,
    report_path: pathlib.Path = REPORT_PATH,
    predicciones_path: pathlib.Path = PREDICCIONES_PATH,
    force: bool = False,
    confirm_paid: bool = False,
    estimated_cost_per_call: Optional[float] = None,
) -> None:
    """
    Carga el corpus real, evalua y genera el reporte.

    Si el corpus no existe en `corpus_path`, lanza FileNotFoundError con
    mensaje claro indicando donde colocar el corpus (sin inventar datos).

    Logica de cache (D4):
    - Si `force=False` y `predicciones_path` contiene un cache valido (mismo hash
      SHA-256 del corpus, mismo corpus_count y misma version del clasificador),
      las predicciones se cargan del archivo y se omite la invocacion al clasificador.
    - En cualquier otro caso (cache ausente, invalido o `force=True`), se ejecuta
      `evaluar_corpus` y se persiste el resultado con metadata de cache.

    Args:
        corpus_path: Ruta al corpus JSON (default: data/corpus_evaluacion_pseudonimizado.json).
        classifier: Clasificador a inyectar (None = usar HybridClassifier real).
        report_path: Donde escribir el reporte.
        predicciones_path: Donde persistir las predicciones.
        force: Si True, bypasea el cache y re-ejecuta la clasificacion completa.
        confirm_paid: Si True, autoriza la corrida que invoca al clasificador real
            cuando no hay cache valido. Un cache hit o un clasificador inyectado
            no requieren confirmacion.
        estimated_cost_per_call: Override del costo estimado por llamada (USD).
    """
    corpus_path = pathlib.Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"El corpus de evaluacion no esta en: {corpus_path}\n"
            f"Coloca el archivo 'corpus_evaluacion_pseudonimizado.json' en la carpeta 'data/' "
            f"antes de ejecutar la evaluacion. Ver evaluation/README.md para instrucciones."
        )

    corpus = cargar_corpus(corpus_path)

    corpus_hash = _compute_corpus_hash(corpus_path)
    corpus_count = len(corpus)
    usa_clasificador_real = classifier is None

    cache_hit = False
    if not force:
        # W-3: la version del clasificador real se lee sin construirlo, de modo
        # que un cache hit no exija credenciales ni invoque Gemini.
        classifier_version = (
            _version_clasificador_real()
            if classifier is None
            else _get_classifier_version(classifier)
        )
        cache_hit = _is_cache_valid(
            predicciones_path, corpus_hash, corpus_count, classifier_version
        )

    if cache_hit:
        predicciones = cargar_predicciones(predicciones_path)
        print(
            f"Cache valido encontrado. Predicciones cargadas desde: {predicciones_path}"
        )
    else:
        if usa_clasificador_real:
            # El gate de costo se evalua ANTES de construir el clasificador real.
            if not confirm_paid:
                raise PaidRunNotConfirmedError(
                    "Corrida paga sin confirmar: la evaluacion invocaria el "
                    "HybridClassifier real. Confirma explicitamente con "
                    "--confirm-paid o "
                    f"{CONFIRM_PAID_ENV_VAR}=1."
                )
            classifier = _resolver_clasificador_real()
            print(
                format_cost_estimation(corpus_count, estimated_cost_per_call)
            )
        classifier_version = _get_classifier_version(classifier)
        predicciones = await evaluar_corpus(corpus, classifier)
        cache_meta: Dict[str, Any] = {
            "corpus_hash": corpus_hash,
            "corpus_count": corpus_count,
            "classifier_version": classifier_version,
            "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        }
        guardar_predicciones(predicciones, predicciones_path, cache_meta=cache_meta)

    generar_reporte(predicciones, corpus, report_path)
    print(f"Evaluacion completa. Reporte escrito en: {report_path}")


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------
def main() -> None:
    """Punto de entrada para `python -m evaluation.run_evaluation`."""
    parser = argparse.ArgumentParser(
        description="Runner de evaluacion del clasificador de mesa de ayuda."
    )
    parser.add_argument(
        "--force",
        "--no-cache",
        dest="force",
        action="store_true",
        default=False,
        help=(
            "Bypasea el cache de predicciones y re-ejecuta la clasificacion completa, "
            "aunque predicciones.json exista y sea valido."
        ),
    )
    parser.add_argument(
        "--confirm-paid",
        dest="confirm_paid",
        action="store_true",
        default=False,
        help=(
            "Autoriza explicitamente una corrida que invoque al clasificador pago "
            "real cuando no haya cache valido. Tambien puede habilitarse con "
            f"{CONFIRM_PAID_ENV_VAR}=1."
        ),
    )
    parser.add_argument(
        "--estimated-cost-per-call",
        dest="estimated_cost_per_call",
        type=float,
        default=None,
        help="Override del costo estimado por llamada (USD), solo para la estimacion.",
    )
    args = parser.parse_args()
    confirm_paid = args.confirm_paid or _env_confirm_paid()
    try:
        asyncio.run(
            main_con_corpus_real(
                force=args.force,
                confirm_paid=confirm_paid,
                estimated_cost_per_call=args.estimated_cost_per_call,
            )
        )
    except PaidRunNotConfirmedError as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
