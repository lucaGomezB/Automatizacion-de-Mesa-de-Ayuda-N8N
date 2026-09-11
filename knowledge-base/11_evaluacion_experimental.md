# Evaluación Experimental (extra — alimenta C-08)

Síntesis del marco metodológico (tesis §4) y resultados esperados (§7) para reproducir la evaluación.

> **Nota C-27:** el corpus sintético de 200 casos (82 Sistemas / 64 Operaciones / 54 Soporte Técnico) y sus resultados (exactitud 92 %, F1 macro 0,919, Tabla 7, 3×3) fueron **descartados por los revisores y eliminados del repositorio**. Quedan declarados **superados**; la evaluación se realiza sobre el corpus real JSON multietiqueta y los números definitivos se re-miden.

## Diseño

- Cuasi experimental, muestras pareadas, mediciones repetidas; cada incidente procesado por flujo manual y automatizado.
- Contrabalanceo: corpus dividido en mitades; una procesada primero manual, la otra primero automatizada (mitiga efecto de aprendizaje).
- Observación naturalista (sin efecto Hawthorne): operadores no informados del cronometraje.
- **Anti data-leakage**: keywords y prompt se construyeron SIN acceso al corpus de validación; la evaluación sobre el corpus real es estrictamente held-out.

## Corpus (Anexo F — JSON no versionado)

El corpus es un documento JSON con `schema_version`, `metadata` (`descripcion`, `total_casos`) y `casos`. Cada caso expone `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales` (requerido; `[]` cuando no hay), `tiempo_manual_s` y `tiempo_automatizado_s`. La verdad es multietiqueta: `{sector_asignado} ∪ sectores_adicionales`.

- Ruta canónica: `data/corpus_evaluacion_pseudonimizado.json` (gitignorada, provista externamente).
- Las cinco categorías canónicas, exactas y sin tildes: `Seguridad Informatica`, `Soporte Tecnico Hardware`, `Soporte Tecnico Software`, `Bases de Datos`, `Sistemas`.
- La distribución por sector se calcula dinámicamente a partir del corpus real; no hay proporciones fijas heredadas.
- Doble etiquetado independiente; discrepancias resueltas por consenso.

> El corpus sintético previo (CSV, 200 casos, 82/64/54, margen 6,5 %) fue eliminado junto con su andamiaje (`generate_corpus.py`, `FakeClassifier` calibrado, columna `categoria_real`).

## Métricas a calcular (C-08, rediseñado en C-27)

| Métrica | Herramienta | Definición |
|---|---|---|
| Exactitud primaria | framework | proporción de casos con `sector_predicho == sector_asignado` |
| Matriz de confusión primaria 5×5 | framework | filas = `sector_asignado`; columnas = `sector_predicho` |
| Subset accuracy | framework | conjunto predicho == conjunto de verdad |
| Pérdida de Hamming | framework | etiquetas erróneas sobre el universo del caso |
| F1 micro | framework | TP/FP/FN acumulados de todas las etiquetas |
| F1 macro | framework | media aritmética de los 5 F1 por sector |
| Precision/Recall/F1/support por sector | framework | esquema one-vs-rest |
| IC Wilson 95 % | framework | sobre igualdad estricta y sobre pertenencia |
| Jaccard / IoU | framework (opcional) | intersección / unión por caso |
| Wilcoxon rangos con signo (tiempos pareados) | scipy.stats | comparación manual vs automatizado |
| Tamaño del efecto rank-biserial | manual: r = 1 − 2W/(n(n+1)) | sobre los tiempos |

> Valores esperados previos (92 % de exactitud; F1 macro 0,919; Sistemas 0,933 · Operaciones 0,906 · Soporte Técnico 0,917) pertenecen al corpus sintético y quedan **superados**. Se reportan al re-ejecutar sobre el corpus real.

## Matriz de confusión primaria (5×5)

La matriz de referencia es **5×5** sobre las cinco clases canónicas. La Tabla 7 de la tesis (3×3, corpus sintético) queda **superada** por el rediseño multietiqueta.

## Métricas multietiqueta de conjunto

- **Subset accuracy**: proporción de casos cuyo conjunto predicho iguala el de verdad.
- **Pérdida de Hamming**: proporción de etiquetas erróneas sobre el universo del caso, en `[0, 1]`.
- **F1 micro / macro**: agregado global y balance entre clases.
- **Wilson sobre dos definiciones de acierto**: (a) igualdad estricta y (b) pertenencia (`sector_asignado` contenido en el conjunto predicho).

## Tipología de errores (análisis cualitativo)

> El conteo previo (7 / 6 / 3 casos) correspondía al corpus sintético eliminado y queda **superado**. La tipología se recalcula sobre el corpus real: descripciones breves (< 15 palabras), mezcla de categorías y jerga local / nombres internos.

## Entregables de C-08

- `evaluation/corpus.py` — loader JSON multietiqueta con validación de invariantes.
- `evaluation/metrics.py` — métricas multietiqueta y matriz primaria 5×5.
- `evaluation/run_evaluation.py` — carga el corpus, clasifica y recolecta resultados.
- `evaluation/report.md` — tablas de métricas.
- `evaluation/analysis.ipynb` — matriz de confusión, distribución de confianzas, curva de calibración.
- `evaluation/tests/fixtures/corpus_fixture.json` — fixture de pruebas con las etiquetas canónicas.
- `evaluation/requirements.txt` — scikit-learn, scipy, pandas, matplotlib, seaborn.
- `evaluation/README.md` — procedimiento reproducible.

## Baseline de referencia (§8.3)

> El baseline previo (TF-IDF + SVM, 40 casos, exactitud 78 %, F1 macro 0,764) se calculó sobre el corpus sintético eliminado y queda **superado**; se re-calcula sobre el corpus real.
