#!/usr/bin/env python3
"""
Ejecuta el framework de evaluación sobre el corpus sintético provisional.
Genera evaluation/report_provisional.md y evaluation/predicciones_provisional.json.

Estrategia de rate-limit: procesa en lotes de 4 casos con pausa de 65s entre lotes,
respetando el límite de 5 RPM del tier gratuito de Gemini 2.5 Flash.

Uso:
    python scripts/run_provisional.py
"""
import asyncio
import os
import pathlib
import sys
import time

# Fix encoding for Windows console
os.environ.setdefault("PYTHONIOENCODING", "utf-8")

REPO_ROOT = pathlib.Path(__file__).parent.parent

# Cargar variables de entorno desde Gestion_Incidentes/.env antes del import de Settings
env_file = REPO_ROOT / "Gestion_Incidentes" / ".env"
if env_file.exists():
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            os.environ.setdefault(key.strip(), val.strip())

# Agregar Gestion_Incidentes al path para importar HybridClassifier
sys.path.insert(0, str(REPO_ROOT / "Gestion_Incidentes"))
sys.path.insert(0, str(REPO_ROOT))

from evaluation.corpus import cargar_corpus, CasoEvaluacion
from evaluation.run_evaluation import (
    Prediccion,
    generar_reporte,
    guardar_predicciones,
)

CORPUS_PATH = REPO_ROOT / "data" / "corpus_sintetico_provisional.csv"
REPORT_PATH = REPO_ROOT / "evaluation" / "report_provisional.md"
PREDICCIONES_PATH = REPO_ROOT / "evaluation" / "predicciones_provisional.json"

# Gemini free tier: 5 RPM. Process in batches of 4 with 65s pause.
BATCH_SIZE = 4
BATCH_PAUSE_S = 65

ADVERTENCIA_HEADER = """\
> **ADVERTENCIA: CORPUS SINTETICO PROVISIONAL**
>
> Este reporte fue generado con el corpus sintetico `corpus_sintetico_provisional.csv`
> (200 casos generados por Claude para validar el pipeline de evaluacion).
> Los numeros aqui reportados **NO son validos para el Capitulo 7** de la tesis.
> El Capitulo 7 requiere el corpus real pseudonimizado (`corpus_evaluacion_pseudonimizado.csv`).
>
> Proposito de esta corrida: validacion y calibracion del pipeline de evaluacion.

"""


async def evaluar_corpus_con_throttle(corpus, classifier):
    """
    Evalua el corpus en lotes para respetar el rate limit de Gemini (5 RPM free tier).
    Lotes de BATCH_SIZE casos con pausa de BATCH_PAUSE_S segundos entre lotes.
    """
    predicciones = []
    total = len(corpus)
    gemini_calls_in_batch = 0

    for i, caso in enumerate(corpus):
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

        if resultado.etapa == "gemini":
            gemini_calls_in_batch += 1

        # Progress
        if (i + 1) % 10 == 0:
            sys.stdout.write(f"\r  Procesado: {i+1}/{total} casos...")
            sys.stdout.flush()

        # After each batch of BATCH_SIZE, pause if we made Gemini calls
        if (i + 1) % BATCH_SIZE == 0 and gemini_calls_in_batch > 0 and (i + 1) < total:
            sys.stdout.write(f"\n  Pausa de {BATCH_PAUSE_S}s por rate limit (Gemini calls: {gemini_calls_in_batch})...\n")
            sys.stdout.flush()
            await asyncio.sleep(BATCH_PAUSE_S)
            gemini_calls_in_batch = 0
        elif (i + 1) % BATCH_SIZE == 0:
            gemini_calls_in_batch = 0

    sys.stdout.write(f"\r  Procesado: {total}/{total} casos.\n")
    sys.stdout.flush()
    return predicciones


async def run():
    print(f"Cargando corpus: {CORPUS_PATH}")
    corpus = cargar_corpus(CORPUS_PATH)
    print(f"Corpus cargado: {len(corpus)} casos")

    try:
        from app.classifiers.hybrid import HybridClassifier  # type: ignore[import]
        classifier = HybridClassifier()
        print("HybridClassifier importado OK")
    except ImportError as e:
        print(f"ERROR: no se pudo importar HybridClassifier: {e}")
        sys.exit(1)

    print("Evaluando corpus (con throttle para respetar el rate limit de Gemini)...")
    print(f"  Lotes de {BATCH_SIZE} casos, pausa de {BATCH_PAUSE_S}s entre lotes si hay llamadas a Gemini")
    t_inicio = time.time()

    predicciones = await evaluar_corpus_con_throttle(corpus, classifier)

    t_fin = time.time()
    duracion = t_fin - t_inicio
    print(f"Evaluacion completada en {duracion:.0f}s ({duracion/60:.1f} min)")

    guardar_predicciones(predicciones, PREDICCIONES_PATH)
    print(f"Predicciones guardadas: {PREDICCIONES_PATH}")

    # Generar reporte base
    contenido_base = generar_reporte(predicciones, corpus, REPORT_PATH)

    # Prepend la advertencia al archivo
    texto_final = ADVERTENCIA_HEADER + contenido_base
    REPORT_PATH.write_text(texto_final, encoding="utf-8")
    print(f"Reporte escrito: {REPORT_PATH}")

    # Resumen en consola
    reales = [p.categoria_real for p in predicciones]
    predichas = [p.categoria_predicha for p in predicciones]
    aciertos = sum(r == p for r, p in zip(reales, predichas))
    exactitud = aciertos / len(reales)

    etapas = {}
    for pred in predicciones:
        etapas[pred.etapa] = etapas.get(pred.etapa, 0) + 1

    from evaluation.metrics import (
        matriz_confusion, f1_por_clase, f1_macro, CLASES,
        precision_por_clase, sensibilidad_por_clase, intervalo_wilson
    )
    mc = matriz_confusion(reales, predichas)
    f1s = f1_por_clase(mc)
    f1_m = f1_macro(f1s)
    lower_ic, upper_ic = intervalo_wilson(aciertos, len(reales))

    print()
    print("=" * 55)
    print("RESUMEN PROVISIONAL (corpus sintetico)")
    print("=" * 55)
    print(f"Total casos: {len(predicciones)}")
    print(f"Aciertos: {aciertos}/{len(reales)}")
    print(f"Exactitud: {exactitud:.4f} ({exactitud*100:.1f}%)")
    print(f"IC Wilson 95%: [{lower_ic:.4f}, {upper_ic:.4f}]")
    print(f"F1 Macro: {f1_m:.4f}")
    print()
    print("F1 por clase:")
    for c in CLASES:
        print(f"  {c}: {f1s[c]:.4f}")
    print()
    print("Matriz de confusion (filas=real, cols=predicho):")
    header = "               | " + " | ".join(f"{c[:8]:>8}" for c in CLASES) + " |"
    print(header)
    print("-" * len(header))
    for cr in CLASES:
        row = f"  {cr[:13]:<13}| "
        row += " | ".join(f"{mc[cr][cp]:>8}" for cp in CLASES) + " |"
        print(row)
    print()
    print("Etapas del pipeline:")
    for etapa, n in sorted(etapas.items()):
        print(f"  {etapa}: {n} ({n/len(predicciones)*100:.1f}%)")
    print("=" * 55)
    print()
    print("ADVERTENCIA: estos numeros son del corpus sintetico provisional.")
    print("NO son validos para el Capitulo 7 de la tesis.")


if __name__ == "__main__":
    asyncio.run(run())
