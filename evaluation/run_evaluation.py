"""
Runner de evaluación del clasificador híbrido.

Orquesta la carga del corpus, la invocación del clasificador caso por caso,
el cálculo de métricas y la escritura del reporte.

Uso (corpus real):
    python -m evaluation.run_evaluation

    Requiere:
    - data/corpus_evaluacion_pseudonimizado.csv (no trackeado en git)
    - GEMINI_API_KEY en el entorno
    - PYTHONPATH configurado para incluir Gestion_Incidentes/

Diseño (D1): el clasificador se inyecta por parámetro, lo que permite
    testear con FakeClassifier sin llamadas a Gemini.
    El main() real usa HybridClassifier; los tests usan FakeClassifier.
"""

from __future__ import annotations

import asyncio
import json
import pathlib
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional, Protocol

from evaluation.corpus import CasoEvaluacion, cargar_corpus
from evaluation.metrics import (
    CLASES,
    exactitud_global,
    f1_macro,
    f1_por_clase,
    intervalo_wilson,
    matriz_confusion,
    precision_por_clase,
    sensibilidad_por_clase,
)

# ---------------------------------------------------------------------------
# Rutas por defecto
# ---------------------------------------------------------------------------
_REPO_ROOT = pathlib.Path(__file__).parent.parent
CORPUS_REAL_PATH = _REPO_ROOT / "data" / "corpus_evaluacion_pseudonimizado.csv"
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
    categoria_real: str
    categoria_predicha: str
    confianza: float
    etapa: str  # "deterministic" | "gemini" | "fallback"


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
        corpus: Lista de casos cargados del CSV.
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
            categoria_real=caso.categoria_real,
            categoria_predicha=resultado.categoria,
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
    Genera el reporte de métricas en Markdown y lo escribe en `output_path`.

    Reutiliza las funciones puras de evaluation.metrics (grupos 2-4).

    Args:
        predicciones: Lista de predicciones del runner.
        corpus: Lista de casos originales del corpus.
        output_path: Ruta donde escribir el reporte (default: evaluation/report.md).

    Returns:
        Contenido del reporte como string.
    """
    reales = [p.categoria_real for p in predicciones]
    predichas = [p.categoria_predicha for p in predicciones]

    mc = matriz_confusion(reales, predichas)
    exactitud = exactitud_global(reales, predichas)
    aciertos = sum(r == p for r, p in zip(reales, predichas))
    lower_ic, upper_ic = intervalo_wilson(aciertos, len(reales))
    precisiones = precision_por_clase(mc)
    sensibilidades = sensibilidad_por_clase(mc)
    f1s = f1_por_clase(mc)
    f1_m = f1_macro(f1s)

    # Contar etapas
    etapas: Dict[str, int] = {"deterministic": 0, "gemini": 0, "fallback": 0}
    for pred in predicciones:
        etapa = pred.etapa if pred.etapa in etapas else "fallback"
        etapas[etapa] += 1

    lineas = [
        "# Reporte de Evaluación del Clasificador",
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
        "## Exactitud Global",
        "",
        f"- **Exactitud:** {exactitud:.4f} ({exactitud*100:.1f}%)",
        f"- **Aciertos:** {aciertos} / {len(reales)}",
        f"- **IC Wilson 95%:** [{lower_ic:.4f}, {upper_ic:.4f}]",
        "",
        "## Matriz de Confusión",
        "",
        "Filas = categoría real | Columnas = categoría predicha",
        "",
    ]

    # Encabezado de la tabla
    header = "| Real \\ Predicho | " + " | ".join(CLASES) + " |"
    separator = "|" + "---|" * (len(CLASES) + 1)
    lineas.append(header)
    lineas.append(separator)
    for clase_real in CLASES:
        fila = f"| **{clase_real}** | "
        celdas = " | ".join(str(mc[clase_real][clase_pred]) for clase_pred in CLASES)
        lineas.append(fila + celdas + " |")

    lineas += [
        "",
        "## Métricas por Clase",
        "",
        "| Clase | Precisión | Sensibilidad | F1 |",
        "|-------|-----------|--------------|-----|",
    ]
    for clase in CLASES:
        lineas.append(
            f"| {clase} | {precisiones[clase]:.4f} | {sensibilidades[clase]:.4f} | {f1s[clase]:.4f} |"
        )
    lineas += [
        "",
        f"**F1 Macro:** {f1_m:.4f}",
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
        corpus_path: Ruta al corpus CSV (default: data/corpus_evaluacion_pseudonimizado.csv).
        classifier: Clasificador a inyectar (None = usar HybridClassifier real).
        report_path: Dónde escribir el reporte.
        predicciones_path: Dónde persistir las predicciones.
    """
    corpus_path = pathlib.Path(corpus_path)

    # Validar presencia del corpus real antes de hacer nada
    if not corpus_path.exists():
        raise FileNotFoundError(
            f"El corpus de evaluación no está en: {corpus_path}\n"
            f"Colocá el archivo 'corpus_evaluacion_pseudonimizado.csv' en la carpeta 'data/' "
            f"antes de ejecutar la evaluación. Ver evaluation/README.md para instrucciones."
        )

    corpus = cargar_corpus(corpus_path)

    if classifier is None:
        # Import diferido: solo necesario para la corrida real
        try:
            import sys
            import os
            # El clasificador vive en Gestion_Incidentes/app/
            gestion_path = str(_REPO_ROOT / "Gestion_Incidentes")
            if gestion_path not in sys.path:
                sys.path.insert(0, gestion_path)
            from app.classifiers.hybrid import HybridClassifier  # type: ignore[import]

            classifier = HybridClassifier()
        except ImportError as exc:
            raise ImportError(
                "No se pudo importar HybridClassifier. "
                "Asegurate de correr con PYTHONPATH que incluya Gestion_Incidentes/. "
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
