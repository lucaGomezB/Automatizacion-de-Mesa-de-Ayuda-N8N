## 0. Safety net y scaffolding

- [x] 0.1 Correr la suite existente de `Gestion_Incidentes/` y capturar baseline (esperado: 142 passed / 1 skipped / 1 xfailed). Si algo falla → reportar como falla preexistente, no arreglar.
- [x] 0.2 Crear el paquete `evaluation/` con `__init__.py`, `evaluation/requirements.txt` (scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter) y `evaluation/tests/` con su `conftest.py`.
- [x] 0.3 Crear el corpus fixture sintético versionado en `evaluation/tests/fixtures/corpus_fixture.csv` (pocos casos, 3-6 por clase, marcado como SINTÉTICO en un comentario/README del fixture; NO es el corpus de tesis). Incluir al menos un caso por cada una de las tres clases y, opcionalmente, columnas `tiempo_manual_s`/`tiempo_automatizado_s`.
- [x] 0.4 Definir el `FakeClassifier` de tests (cumple el contrato `async classify(descripcion) -> ClasificacionResult`, devuelve predicciones predeterminadas por caso) en `evaluation/tests/conftest.py`. Nunca pega a Gemini.

## 1. Carga y contrato del corpus (spec: Contrato y carga del corpus de evaluación)

- [x] 1.1 RED: test `test_cargar_corpus_valido_devuelve_todos_los_casos` en `evaluation/tests/test_corpus.py` que carga `corpus_fixture.csv` y afirma cantidad de filas e id/descripcion/categoria_real del primer caso. Falla (no existe `evaluation/corpus.py`).
- [x] 1.2 GREEN: implementar `cargar_corpus(path) -> list[CasoEvaluacion]` en `evaluation/corpus.py` (lectura con pandas, mapeo a dataclass simple). Test pasa.
- [x] 1.3 TRIANGULATE: `test_cargar_corpus_inexistente_lanza_error` (ruta inexistente → error que nombra la ruta) y `test_cargar_corpus_columna_faltante_lanza_error` (CSV sin `categoria_real` → error que identifica la columna). Usar CSVs temporales en el test.
- [x] 1.4 TRIANGULATE: `test_cargar_corpus_categoria_invalida_lanza_error` (categoría `"sistemas"` minúscula o `"Redes"` → error que identifica el valor y el caso). Validar contra el set exacto `{"Sistemas","Operaciones","Soporte Técnico"}`.
- [x] 1.5 REFACTOR: extraer la constante `CATEGORIAS_VALIDAS` y la lista de columnas requeridas; suite de `evaluation/` → verde.

## 2. Matriz de confusión (spec: Matriz de confusión)

- [x] 2.1 RED: test `test_matriz_confusion_clasificacion_perfecta_es_diagonal` en `evaluation/tests/test_metrics.py`. Falla (no existe `evaluation/metrics.py`).
- [x] 2.2 GREEN: implementar `matriz_confusion(reales, predichos) -> dict/estructura` como función pura sobre las 3 clases en orden fijo. Test pasa.
- [x] 2.3 TRIANGULATE: `test_matriz_confusion_error_va_fuera_de_la_diagonal` (real Sistemas, predicho Operaciones → celda (Sistemas,Operaciones)=1, diagonal no cuenta) y un caso mixto con conteos por fila/columna.
- [x] 2.4 REFACTOR: nombrar claramente el orden de clases (filas=real, columnas=predicho); suite → verde.

## 3. Métricas por clase y macro (spec: Métricas por clase y promedio macro)

- [x] 3.1 RED: test `test_f1_por_clase_es_media_armonica` (precisión y recall conocidos → F1 = 2PR/(P+R)). Falla.
- [x] 3.2 GREEN: implementar `precision_por_clase`, `sensibilidad_por_clase`, `f1_por_clase` (funciones puras derivadas de la matriz). Test pasa.
- [x] 3.3 TRIANGULATE: `test_f1_macro_pondera_clases_por_igual` (F1 macro = media aritmética de los 3 F1, independiente de tamaños de clase) usando una matriz con clases desbalanceadas.
- [x] 3.4 TRIANGULATE: `test_precision_clase_sin_predicciones_es_cero` (denominador cero → 0.0, sin excepción) — cubre el caso límite de la spec.
- [x] 3.5 REFACTOR: factorizar el manejo de denominador-cero en un helper; suite → verde.

## 4. Exactitud global e IC de Wilson (spec: Exactitud global e intervalo de confianza de Wilson)

- [x] 4.1 RED: test `test_exactitud_global_es_proporcion_de_aciertos` (K aciertos / N casos). Falla.
- [x] 4.2 GREEN: implementar `exactitud_global(reales, predichos) -> float`. Test pasa.
- [x] 4.3 RED: test `test_wilson_contiene_la_proporcion_puntual` (IC en [0,1]; lower ≤ p̂ ≤ upper). Falla.
- [x] 4.4 GREEN: implementar `intervalo_wilson(aciertos, total, confianza=0.95) -> (lower, upper)`. Test pasa.
- [x] 4.5 TRIANGULATE: caso de referencia con valor conocido (p. ej. 184/200 → IC ≈ [0.872, 0.952] según §7.2, con tolerancia) verificando consistencia con la tesis.
- [x] 4.6 REFACTOR: cross-check opcional de exactitud/F1 contra `sklearn.metrics` sobre el fixture en un test marcado; suite → verde.

## 5. Análisis estadístico de tiempos (spec: Análisis estadístico de tiempos)

- [x] 5.1 RED: test `test_wilcoxon_diferencia_sistematica_es_significativa` en `evaluation/tests/test_stats.py` (automatizado siempre menor → p<0.05, efecto alto). Falla (no existe `evaluation/stats.py`).
- [x] 5.2 GREEN: implementar `wilcoxon_tiempos(manual, automatizado) -> (W, p, r)` envolviendo `scipy.stats.wilcoxon` y calculando el rank-biserial r. Test pasa.
- [x] 5.3 TRIANGULATE: `test_wilcoxon_series_de_distinta_longitud_lanza_error` (longitudes distintas → error, no resultado inválido).
- [x] 5.4 REFACTOR: documentar la fórmula del tamaño del efecto en docstring (consistente con §7.1); suite → verde.

## 6. Runner de evaluación (spec: Runner de evaluación sobre el corpus)

- [x] 6.1 RED: test `test_runner_recolecta_una_prediccion_por_caso` en `evaluation/tests/test_run_evaluation.py` que corre el runner con `FakeClassifier` sobre el fixture y afirma una predicción (categoria, confianza, etapa) por caso. Falla (no existe `evaluation/run_evaluation.py`).
- [x] 6.2 GREEN: implementar `evaluar_corpus(corpus, classifier) -> list[Prediccion]` (orquesta carga + invocación async caso por caso, clasificador inyectado). Test pasa.
- [x] 6.3 RED: test `test_runner_genera_report_md_con_metricas` que afirma que tras correr se escribe `report.md` (a path temporal) con matriz de confusión, exactitud y métricas por clase/macro. Falla.
- [x] 6.4 GREEN: implementar `generar_reporte(predicciones, corpus) -> str` y el wiring que escribe `evaluation/report.md` reusando las funciones puras de los grupos 2-4. Test pasa.
- [x] 6.5 TRIANGULATE: `test_runner_corpus_real_ausente_falla_claro` (path `data/corpus_evaluacion_pseudonimizado.csv` inexistente → error claro pidiendo colocar el corpus; NO inventa datos ni produce reporte ficticio).
- [x] 6.6 REFACTOR: separar el `main()`/CLI (entrada por defecto = corpus real) de la lógica testeable; persistir las predicciones a un artefacto intermedio (CSV/JSON) para no re-invocar Gemini al regenerar reporte/notebook; suite → verde.

## 7. Notebook, documentación y requirements (no-TDD: generación y verificación manual)

- [x] 7.1 Crear `evaluation/analysis.ipynb` con celdas que carguen las predicciones (artefacto intermedio o corpus) y generen: heatmap de la matriz de confusión (seaborn), histograma de confianzas por etapa (deterministic/gemini/fallback) y curva de calibración (confianza vs. tasa de acierto). Verificar que ejecuta de punta a punta contra el fixture/artefacto sintético.
- [x] 7.2 Escribir `evaluation/README.md`: esquema del CSV (columnas requeridas/opcionales), dónde colocar el corpus real, comando único de corrida, setup del entorno (PYTHONPATH/import del clasificador, `GEMINI_API_KEY`), interpretación del reporte, la decisión D1 (import directo vs HTTP, con tradeoffs) y la **advertencia metodológica** de no ajustar reglas/prompt sobre el corpus de evaluación (anti data leakage, §8.1).
- [x] 7.3 Verificar `evaluation/requirements.txt` (scikit-learn, scipy, pandas, matplotlib, seaborn, jupyter) e instalar en un venv limpio para confirmar que la suite de `evaluation/` corre.
- [x] 7.4 Correr toda la suite (`Gestion_Incidentes/` + `evaluation/`) y confirmar que el baseline del backend sigue intacto (142 passed / 1 skipped / 1 xfailed) y que los tests de `evaluation/` pasan.

## 8. Corrida real (solo cuando el usuario coloque el corpus verdadero — fuera del alcance de código)

- [ ] 8.1 (Manual, post-merge) Con `data/corpus_evaluacion_pseudonimizado.csv` presente y `GEMINI_API_KEY` operativa: ejecutar `python -m evaluation.run_evaluation`, generar `report.md` real y abrir el notebook. Cotejar las métricas contra las tablas del Capítulo 7 de la tesis. Este paso NO se incluye en el repo con datos reales; queda documentado como procedimiento en el README.
