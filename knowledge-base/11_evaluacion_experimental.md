# Evaluación Experimental (extra — alimenta C-08)

Síntesis del marco metodológico (tesis §4) y de los resultados vigentes (§7) para reproducir la evaluación.

> **Nota C-27:** el corpus sintético de 200 casos (82 Sistemas / 64 Operaciones / 54 Soporte Técnico) y sus resultados (exactitud 92 %, F1 macro 0,919, Tabla 7, 3×3) fueron **descartados por los revisores y eliminados del repositorio**. Quedan declarados **superados** y se conservan solo como historia; la evaluación se realiza sobre el corpus real JSON multietiqueta y sus resultados vigentes figuran en el bloque «Resultados vigentes (release v1.2.0)» de más abajo.

## Resultados vigentes (release v1.2.0)

**Fuente única:** `docs/Tesis/Correcciones/numeros-canonicos.md` (memo de números canónicos, versión de trabajo v10, release `v1.2.0`). Si este bloque y el memo difieren, vale el memo; ningún valor de aquí se define por separado. Corpus: `n = 200` casos, SHA-256 `1fd17d7ea90d418bb060b57bc3a645faa4a753c7c0c26424c06c58d884dac5cb` (Sección 3.5). Corrida oficial de predicciones: `hybrid-v3` (Sección 3.9). Kappa de Cohen del doble etiquetado: `0,87` (contexto de validez, no es una métrica del clasificador).

**Tiempos de registro** (Secciones 3.1 y 3.8; contraste Wilcoxon **bilateral**, conservador frente a `H1` direccional):

| Valor | Resultado |
|---|---|
| Tiempo manual medio / automatizado medio | `61,6 s` / `17,76 s` (mediana automatizada `17,47 s`) |
| Reducción relativa de tiempo | `71,2 %` (cota superior: el tiempo manual se redondeó al alza) |
| Reducción media por incidente | `43,82 s`; pares a favor `188/200` (`94,0 %`), `12` no más rápidos (todos de correo electrónico) |
| Wilcoxon | `W = 363`, `T+ = 19.737`, `T− = 363`, `p = 3,08e-32` bilateral (`1,54e-32` unilateral) |
| Tamaño del efecto | `r = 0,9639`; `d_z = 1,0004` |
| Por canal (manual → automatizado, reducción de la media) | llamada telefónica `87,2 → 20,09 s` (`77,0 %`); correo electrónico `56,5 → 27,65 s` (`51,1 %`); formulario web `28,7 → 1,88 s` (`93,4 %`) |
| Sensibilidad del redondeo manual | descuento de `5 s`: reducción `68,61 %`; de `10 s`: `65,57 %` (la planilla tiene resolución efectiva de `5 s`: `199/200` valores son múltiplos de `5 s`) |

**Clasificación** (Secciones 3.2, 3.3 y 3.9):

| Valor | Resultado |
|---|---|
| Exactitud estricta | `0,7350` (`147/200`), IC de Wilson 95 % `[0,6698; 0,7913]` |
| Exactitud laxa (secundaria) | `0,8950` (`179/200`), IC `[0,8448; 0,9303]`; no cambia el estado de ningún objetivo |
| Macro-F1 | `0,6508` sobre las cuatro clases estimables (primaria de umbral); `0,5207` sobre cinco clases (informativa, incluye `Bases de Datos` con `n = 1`); ambas por debajo de `0,85` |
| Micro-F1 / subset accuracy / Hamming | `0,6654` / `0,43` / `0,3586` (contra la referencia multietiqueta) |
| F1 por clase | Hardware `0,8800`; Software `0,7111`; Seguridad `0,6122`; Sistemas `0,4000`; Bases de Datos `0,0000` (no estimable) |
| Por etapa | determinística `131` casos (`65,5 %`), `97/131` = `0,7405`; Gemini `69` casos (`34,5 %`), `50/69` = `0,7246`; fallback `0` |
| Por canal | llamada telefónica `53/81` = `0,6543`; correo electrónico `51/66` = `0,7727`; formulario web `43/53` = `0,8113` |
| Confianza | bandas `98 / 26 / 6 / 31 / 39`; tramo `≥ 0,90`: `46` casos, `13` errores; `124/200` (`62,0 %`) con confianza `< 0,70`, todos de la etapa determinística; punto de operación del cortocircuito `0,5166` sobre el `score_correctitud` |
| Determinística frente a Gemini sobre `S` | `97/131` frente a `88/130` (`0,6769`); McNemar `b = 16`, `c = 8`, `p` exacto `0,1516` (no significativo) |

**Intervención humana, universo y proyección** (Sección 3.4): la tasa de intervención humana **no se midió** sobre el corpus real; el valor heredado del corpus sintético está retirado en el memo y no es citable. Universo trimestral `≈ 2.646 = 42 × 63` incidentes (días hábiles); ahorro bruto proyectado `≈ 32,2` horas-persona por trimestre.

**Sensibilidad frente al ajuste del clasificador con el corpus** (Sección 3.10; tesis `subsec:sensibilidad-ajustes`). Son mediciones de sensibilidad, no reemplazan los valores de arriba:

| Variante | Resultado |
|---|---|
| E1: vocabulario previo a c-71 con la lógica vigente | `74` casos cortocircuitados (`74/200`), `39` aciertos = `0,5270` `[0,4148; 0,6366]`; diferencia descriptiva de `21,3` puntos frente a `0,7405` (cota pesimista) |
| E3: predicciones de Gemini fijas | vocabulario vigente `146/200` (`0,7300`) frente a previo `128/200` (`0,6400`); solo el vigente acierta `18`, ninguno solo el previo; `p < 0,001` |
| E4: con el vocabulario previo, sobre los casos que resuelve la etapa de reglas | reglas `38/73` = `0,5205` frente a Gemini `48/73` = `0,6575`; `p` exacto `0,0213` |
| Prompt, nivel a | etapa Gemini `50/69` = `0,7246` con todos los casos y `48/66` = `0,7273` sin los tres casos motivadores de c-72 |
| Prompt, nivel b / nivel c | nivel b: la comparación pareada no aplica; nivel c (ablación paga): no computado, sin autorización |

**Balance neto de las derivaciones erróneas** (Sección 3.11; `condicional`, son supuestos y no mediciones): con `e_man = 15 %` y un costo de `10` a `15 min` por derivación errónea, el balance es `−18,5 h` y `−43,9 h` por trimestre y la exactitud mínima de equilibrio `77,7 %` y `80,1 %`; con la exactitud laxa como cota favorable el balance es positivo (`+52,1 h` y `+62,0 h`). El balance es **indeterminado** con el diseño actual: la viabilidad técnica y económica se confirma y la operativa queda **condicional**.

**Lectura retirada:** la «calibración invertida» del clasificador en su conjunto es un efecto de composición entre etapas (Sección 3.9); dentro de Gemini la confianza autodeclarada no discrimina aciertos de errores en el rango observado (`0,85` a `1,00`).

## Diseño

- Cuasi experimental, muestras pareadas, mediciones repetidas; cada incidente procesado por flujo manual y automatizado.
- Contrabalanceo: corpus dividido en mitades; una procesada primero manual, la otra primero automatizada (mitiga efecto de aprendizaje).
- Observación naturalista (sin efecto Hawthorne): operadores no informados del cronometraje.
- **Procedencia de los ajustes del clasificador**: el vocabulario del filtro determinístico (c-71), las reglas de frontera del prompt de Gemini (c-72) y el punto de operación del cortocircuito (c-74) se ajustaron con el propio corpus de evaluación. Por eso las métricas de clasificación son estimaciones al menos parcialmente dentro de la muestra y no una evaluación fuera de muestra; el efecto de ese ajuste se analiza en la sensibilidad de la tesis (`subsec:sensibilidad-ajustes`) y en la Sección 3.10 del memo `docs/Tesis/Correcciones/numeros-canonicos.md`.

## Corpus (Anexo F — JSON pseudonimizado, versionado)

El corpus es un documento JSON con `schema_version`, `metadata` (`descripcion`, `total_casos`) y `casos`. Cada caso expone `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales` (requerido; `[]` cuando no hay), `tiempo_manual_s` y `tiempo_automatizado_s`. La verdad es multietiqueta: `{sector_asignado} ∪ sectores_adicionales`.

- Ruta canónica: `data/corpus_evaluacion_pseudonimizado.json` (versionado en su forma pseudonimizada; los originales pre-pseudonimizacion quedan fuera, Ley 25.326).
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

> Valores esperados previos (92 % de exactitud; F1 macro 0,919; Sistemas 0,933 · Operaciones 0,906 · Soporte Técnico 0,917) pertenecen al corpus sintético y quedan **superados**; los valores vigentes sobre el corpus real están en «Resultados vigentes (release v1.2.0)».

## Matriz de confusión primaria (5×5)

La matriz de referencia es **5×5** sobre las cinco clases canónicas. La Tabla 7 de la tesis (3×3, corpus sintético) queda **superada** por el rediseño multietiqueta.

## Métricas multietiqueta de conjunto

- **Subset accuracy**: proporción de casos cuyo conjunto predicho iguala el de verdad.
- **Pérdida de Hamming**: proporción de etiquetas erróneas sobre el universo del caso, en `[0, 1]`.
- **F1 micro / macro**: agregado global y balance entre clases.
- **Wilson sobre dos definiciones de acierto**: (a) igualdad estricta y (b) pertenencia (`sector_asignado` contenido en el conjunto predicho).

## Tipología de errores (análisis cualitativo)

> El conteo previo (7 / 6 / 3 casos) correspondía al corpus sintético eliminado y queda **superado**. El estado vigente es el análisis de errores de la tesis (`subsec:analisis-errores`) sobre los `53` casos con sector principal errado de la corrida oficial: patrones de descripción corta y de frontera entre sectores (Soporte Técnico Hardware y Software; Sistemas y Soporte Técnico Software). Sus conteos por patrón son de la tesis y no están en el memo de números canónicos.

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

> El baseline previo (TF-IDF + SVM, 40 casos, exactitud 78 %, F1 macro 0,764) se calculó sobre el corpus sintético eliminado y queda **superado**. El estado vigente que declara la tesis (`08-discusion.tex`, limitaciones) es que la comparación se hizo solo contra el flujo manual: no hay comparación válida contra clasificadores alternativos, y un chequeo exploratorio temprano con TF-IDF + SVM sobre un subconjunto no preservado no se reporta como tal.
