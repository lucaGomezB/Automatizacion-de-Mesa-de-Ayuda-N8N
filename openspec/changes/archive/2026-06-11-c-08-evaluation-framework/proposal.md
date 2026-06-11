## Why

El Capítulo 7 de la tesis reporta resultados de clasificación (exactitud global, matriz de confusión, F1 por clase, F1 macro) y de tiempos (prueba de Wilcoxon) sobre el corpus de 200 casos descrito en §4.4. Hoy no existe ningún artefacto en el repositorio que **calcule esas métricas de forma reproducible** ni que documente el procedimiento: los números de la tesis no son auditables ni regenerables. C-08 construye el framework de evaluación que produce, a partir del corpus etiquetado, exactamente las tablas del Capítulo 7, con código testeado y un procedimiento de un solo comando.

Restricción central verificada: el corpus real `data/corpus_evaluacion_pseudonimizado.csv` (200 casos, distribución 82 Sistemas / 64 Operaciones / 54 Soporte Técnico) **no está versionado ni presente en este clon** (CLAUDE.md: "not tracked in git"). Por lo tanto el framework debe ser correcto y testeado **sin** depender del corpus real, validándose contra un corpus fixture sintético pequeño, y dejar la corrida real como una operación que el usuario ejecuta cuando coloque el corpus verdadero. Los resultados de tesis salen del corpus verdadero, no de datos inventados.

## What Changes

- Nuevo paquete `evaluation/` en la raíz del repositorio, independiente de las rutas FastAPI de `Gestion_Incidentes/` pero que reusa el `HybridClassifier` ya implementado.
- **Carga de corpus** (`evaluation/corpus.py`): lectura y validación de un CSV con esquema definido (id, descripcion, categoria_real). Falla con error claro si el archivo no existe, le faltan columnas, o una categoría no pertenece al conjunto exacto `{"Sistemas", "Operaciones", "Soporte Técnico"}`.
- **Cálculo de métricas como funciones puras** (`evaluation/metrics.py`): matriz de confusión, exactitud global, precisión/sensibilidad/F1 por clase, F1 macro e intervalo de Wilson — todas funciones puras testeables sin I/O ni red.
- **Análisis estadístico de tiempos** (`evaluation/stats.py`): prueba de Wilcoxon de rangos con signo y tamaño del efecto rank-biserial sobre pares (tiempo_manual, tiempo_automatizado), según §4.7.
- **Runner de evaluación** (`evaluation/run_evaluation.py`): orquesta carga del corpus → invocación del clasificador caso por caso (recolectando categoría predicha, confianza y etapa) → cálculo de métricas → emisión de `evaluation/report.md`. Ejecutable como un solo comando cuando el corpus real esté presente.
- **Reporte** (`evaluation/report.md`): generado por el runner con las tablas de métricas (no se versiona con datos reales; se documenta su formato).
- **Notebook** (`evaluation/analysis.ipynb`): visualizaciones (matriz de confusión, distribución de confianzas por etapa, curva de calibración) sobre resultados ya calculados.
- **Corpus fixture sintético** versionado en `evaluation/tests/fixtures/` (un puñado de casos, no 200) para correr los tests sin el corpus real.
- **Documentación** (`evaluation/README.md`): esquema del CSV, cómo colocar el corpus, cómo correr la evaluación, cómo interpretar el reporte y la decisión de diseño sobre cómo se invoca al clasificador.
- **Dependencias** (`evaluation/requirements.txt`): scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter.

No hay cambios **BREAKING**: el framework es aditivo y no modifica el backend ni su API.

## Capabilities

### New Capabilities
- `evaluation-framework`: define el contrato del corpus de evaluación, el cálculo reproducible de las métricas de clasificación (exactitud, matriz de confusión, precisión/sensibilidad/F1 por clase, F1 macro, IC de Wilson), el análisis estadístico de tiempos (Wilcoxon + tamaño del efecto), la generación del reporte y el procedimiento operativo de corrida sobre el corpus real.

### Modified Capabilities
<!-- Ninguna. C-08 es aditivo: no modifica requisitos de capacidades existentes (clasificador, notificación N8N, pseudonimización). -->

## Impact

- **Código nuevo**: paquete `evaluation/` (corpus, métricas, stats, runner, notebook, tests, README, requirements). Sin cambios en `Gestion_Incidentes/app/`.
- **Reuso**: importa `HybridClassifier` (`Gestion_Incidentes/app/classifiers/hybrid.py`) y los umbrales de `Settings` (deterministic 0.90 / human_review 0.70). La decisión import-directo-vs-HTTP se documenta en design.md.
- **Dependencias nuevas** (solo para evaluación, no para el runtime del backend): scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter — aisladas en `evaluation/requirements.txt`.
- **Datos**: depende del corpus real `data/corpus_evaluacion_pseudonimizado.csv`, ausente del repo. El framework funciona y se testea sin él; la corrida real es responsabilidad del usuario al colocar el corpus.
- **Tesis**: las tablas del Capítulo 7 (§7.1 tiempos, §7.2 matriz y métricas) pasan a ser regenerables a partir del corpus mediante un comando.
- **Suite de tests**: agrega tests bajo `evaluation/tests/` (no afecta la suite actual de `Gestion_Incidentes/`: 142 passed / 1 skipped / 1 xfailed).
