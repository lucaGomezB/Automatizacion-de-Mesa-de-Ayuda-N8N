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

import asyncio
import json
import pathlib
from dataclasses import asdict, dataclass, field
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
# Persistencia de predicciones (artefacto intermedio)
# ---------------------------------------------------------------------------
def guardar_predicciones(
    predicciones: List[Prediccion],
    output_path: pathlib.Path = PREDICCIONES_PATH,
) -> None:
    """
    Persiste las predicciones a JSON para no re-invocar Gemini al regenerar el reporte.

    Args:
        predicciones: Lista de predicciones a persistir.
        output_path: Ruta del JSON (default: evaluation/predicciones.json).
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    datos = [asdict(p) for p in predicciones]
    output_path.write_text(
        json.dumps(datos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def cargar_predicciones(input_path: pathlib.Path) -> List[Prediccion]:
    """
    Carga predicciones previamente persistidas desde JSON.

    Args:
        input_path: Ruta del JSON con predicciones.

    Returns:
        Lista de Prediccion.
    """
    datos = json.loads(input_path.read_text(encoding="utf-8"))
    return [Prediccion(**d) for d in datos]


# ---------------------------------------------------------------------------
# main_con_corpus_real — punto de entrada para la corrida real (testeable)
# ---------------------------------------------------------------------------
async def main_con_corpus_real(
    corpus_path: pathlib.Path = CORPUS_REAL_PATH,
    classifier: Optional[ClasificadorProtocol] = None,
    report_path: pathlib.Path = REPORT_PATH,
    predicciones_path: pathlib.Path = PREDICCIONES_PATH,
) -> None:
    """
    Carga el corpus real, evalúa y genera el reporte.

    Si el corpus no existe en `corpus_path`, lanza FileNotFoundError con
    mensaje claro indicando dónde colocar el corpus (sin inventar datos).

    Args:
        corpus_path: Ruta al corpus JSON (default: data/corpus_evaluacion_pseudonimizado.json).
        classifier: Clasificador a inyectar (None = usar HybridClassifier real).
        report_path: Dónde escribir el reporte.
        predicciones_path: Dónde persistir las predicciones.
    """
    corpus_path = pathlib.Path(corpus_path)

    if not corpus_path.exists():
        raise FileNotFoundError(
            f"El corpus de evaluación no está en: {corpus_path}\n"
            f"Colocá el archivo 'corpus_evaluacion_pseudonimizado.json' en la carpeta 'data/' "
            f"antes de ejecutar la evaluación. Ver evaluation/README.md para instrucciones."
        )

    corpus = cargar_corpus(corpus_path)

    if classifier is None:
        try:
            import sys

            backend_path = str(_REPO_ROOT / "App" / "Backend")
            if backend_path not in sys.path:
                sys.path.insert(0, backend_path)
            from app.classifiers.hybrid import HybridClassifier  # type: ignore[import]

            classifier = HybridClassifier()
        except ImportError as exc:
            raise ImportError(
                "No se pudo importar HybridClassifier. "
                "Asegurate de correr con PYTHONPATH que incluya App/Backend/. "
                "Ver evaluation/README.md para instrucciones de setup."
            ) from exc

    predicciones = await evaluar_corpus(corpus, classifier)
    guardar_predicciones(predicciones, predicciones_path)
    generar_reporte(predicciones, corpus, report_path)
    print(f"Evaluación completa. Reporte escrito en: {report_path}")


# ---------------------------------------------------------------------------
# Punto de entrada CLI
# ---------------------------------------------------------------------------
def main() -> None:
    """Punto de entrada para `python -m evaluation.run_evaluation`."""
    asyncio.run(main_con_corpus_real())


if __name__ == "__main__":
    main()
