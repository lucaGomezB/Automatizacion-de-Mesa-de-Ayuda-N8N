## Context

Ver `proposal.md` — Why. Artefactos de partida versionados:

- `evaluation/data/campana/corpus_campana.json` — `200` casos in-sample con
  `sector_asignado` (verdad de entrenamiento).
- `evaluation/data/campana/corpus_independiente.json` — `103` casos fuera de muestra con
  referencia por consenso `E3`/`E4`; los `47` discordantes quedaron FUERA de la referencia.
- `evaluation/data/campana/predicciones_independiente.json` — `103` predicciones congeladas
  de `hybrid-v3` (solo para la comparacion de c-210).
- `evaluation/metrics.py` — funciones puras de matriz de confusion y metricas por clase.
- `evaluation/corpus.py` — `CasoEvaluacion` y `cargar_corpus`.

El entorno tiene `scikit-learn 1.9.1` y `numpy 2.5.3`; `evaluation/requirements.txt` ya declara
`scikit-learn>=1.4`. No se agrega ninguna dependencia.

## Goals / Non-Goals

**Goals:**

- Entregar un clasificador supervisado clasico de texto, reproducible y offline, entrenado con
  los `200` casos in-sample y evaluado con los `103` casos fuera de muestra con referencia.
- Producir metricas comparables con las de c-205: exactitud estricta, exactitud laxa, macro-F1,
  *balanced accuracy* y F1 por clase con soporte.
- Garantizar determinismo byte a byte y registrar SHA-256 de entradas y salidas.
- Cubrir el modulo con pruebas TDD en `evaluation/tests/`, que es el `testpaths` de la suite.

**Non-Goals:**

- Ejecutar la medicion y publicar la comparacion contra el hibrido: eso es c-210.
- Arbitrar los `47` discordantes: eso es c-206.
- Cambiar el clasificador de produccion, el corpus, los numeros canonicos o la tesis.
- Optimizar hiperparametros con el conjunto de prueba. La linea de base es deliberadamente
  simple y honesta, no un modelo tuneado para ganar la comparacion.

## Decisions

### D1 — scikit-learn en lugar de una implementacion pura de la biblioteca estandar

El entorno ya tiene `scikit-learn 1.9.1` y la dependencia ya esta declarada en
`evaluation/requirements.txt` (`scikit-learn>=1.4`). Se usa un `Pipeline` de
`TfidfVectorizer` + `LogisticRegression` regularizada. La linea de base clasica es una
eleccion metodologica conocida y reproducible; reimplementar TF-IDF y regresion logistica a
mano agregaria superficie de error y haria menos defendible la comparacion. El resto del
modulo usa solo biblioteca estandar y funciones de `evaluation/`; scikit-learn se concentra en
el ajuste y la prediccion. Alternativa descartada: TF-IDF + regresion logistica en numpy puro,
que no aporta reproducibilidad y duplica codigo ya resuelto.

### D2 — El conjunto de prueba es el de `103` casos con referencia, no el de `150`

La muestra primaria fuera de muestra es de `150` casos: `103` con consenso `E3`/`E4` y `47`
discordantes sin referencia. El clasificador se evalua sobre los `103` porque (a) son los que
tienen verdad de referencia, (b) son el mismo conjunto efectivo de c-191/c-205 y (c) los `47`
discordantes no tienen descripcion ni etiqueta en los artefactos versionados. El documento
declara explicitamente que el `n` de prueba es `103` y que los `47` no se usan. No se
reinterpreta el `150` ni se le asigna una etiqueta a los discordantes. Alternativa descartada:
evaluar sobre `150` usando `E3` o `E4` como verdad, que sesgaria la comparacion y violaria la
regla de no reinterpretar numeros canonicos.

### D3 — Modelo, semilla y dos variantes de re-ponderacion

El modelo primario es TF-IDF de palabras (`ngram_range=(1,2)`, `sublinear_tf=True`) mas
`LogisticRegression(max_iter=2000, solver="lbfgs", random_state=42, class_weight="balanced")`.
Se corre ademas una variante sin re-ponderacion (`class_weight=None`) como sensibilidad. La
variante primaria usa re-ponderacion de clases porque el corpus de ajuste tiene una sola clase
`Bases de Datos` (`1` caso de `200`) y el conjunto de prueba sobrerrepresenta las clases chicas;
sin re-ponderacion el modelo puede colapsar a las clases mayoritarias. El documento reporta
AMBAS variantes. Alternativa descartada: una sola variante sin re-ponderacion, que ocultaria
el efecto del desbalance.

### D4 — Metricas: funciones puras del repositorio y lectura muestral/ponderada

Las metricas se calculan con `evaluation/metrics.py`, no con `sklearn.metrics`, para que sean
comparables con las de c-205. La exactitud estricta es `aciertos_estrictos(reales, predichos)`
sobre `103`; la laxa es `aciertos_laxos(predichos, conjuntos_verdad)`; la matriz `5x5` se arma
con `matriz_confusion`; la macro-F1 con `f1_macro`; la *balanced accuracy* con la media de
`sensibilidad_por_clase`; el soporte con `soporte_por_clase`. Se reportan dos lecturas:

- **Muestral**: las metricas sobre los `103` casos tal como estan.
- **Prevalencia natural**: las mismas metricas por clase re-ponderadas por la distribucion de
  los `200` casos in-sample (`85` hardware, `67` software, `31` seguridad, `16` sistemas,
  `1` base de datos). La re-ponderacion es una post-estratificacion declarada, no un cambio de
  la verdad ni del modelo.

Ninguna cifra unica se presenta como definitiva. La lectura muestral no se corrige; la
ponderada se rotula como estimacion a la prevalencia natural. Alternativa descartada: reportar
solo la exactitud muestral, que sobrestima las clases sobrerrepresentadas.

### D5 — Determinismo y formato de salida

Semilla fija `42`. `TfidfVectorizer` y `LogisticRegression` con `solver="lbfgs"` son
deterministas en este entorno. El JSON se serializa con `sort_keys=True`, `indent=2`,
`ensure_ascii=False`, LF y UTF-8 sin BOM. El Markdown se genera por plantilla fija. Dos
corridas producen los mismos bytes; el script imprime el SHA-256 de cada salida. Alternativa
descartada: serializar con el orden de insercion de Python, que es estable pero menos
auditable entre versiones.

### D6 — Solo lectura sobre los artefactos congelados

La carga usa `evaluation.campana.cargar_corpus_solo_lectura`, que copia el corpus a un
temporal antes de validarlo y nunca reescribe el original. El script no importa el
clasificador de produccion ni `App/`. No escribe fuera de su directorio de salida. Alternativa
descartada: `cargar_corpus` directo, que puede reescribir `metadata.total_casos` si esta
desincronizado.

### D7 — TDD y ubicacion de las pruebas

Las pruebas viven en `evaluation/tests/test_linea_de_base.py` porque `evaluation/pytest.ini`
declara `testpaths = tests`; asi `cd evaluation && pytest -q` las recoge. Ciclo: (1) prueba de
estructura que importa el modulo inexistente y falla (RED); (2) implementacion minima que la
hace pasar (GREEN); (3) triangulacion con entradas sinteticas distintas (dos o mas casos),
prueba de determinismo byte a byte y prueba de ausencia de red/Gemini/API paga. Alternativa
descartada: poner las pruebas junto al modulo en `evaluation/data/`, que no las recoge la
suite por defecto.

### D8 — La comparacion y el veredicto son de c-210

c-209 no ejecuta la comparacion final ni escribe el borrador de tesis. Entrega el modulo y las
pruebas; c-210 corre la medicion, produce los artefactos versionados y redacta el borrador. La
separacion evita que el desarrollo y la ejecucion se confundan en el mismo commit y permite
revisar el script antes de publicar cifras.

## Risks / Trade-offs

- [El modelo clasico rinde peor que el hibrido y la comparacion es desfavorable a la tesis] →
  se reporta exactamente como se mide; la honestidad es el activo evaluado. No se tunea con el
  conjunto de prueba ni se oculta la variante desfavorable.
- [El corpus de ajuste tiene una sola clase `Bases de Datos`] → se corre con y sin
  re-ponderacion y se reportan ambas; el soporte de `Bases de Datos` en prueba (`13`) se
  declara junto con la F1.
- [El conjunto de prueba es de `103`, no de `150`] → se declara que los `47` discordantes no
  tienen referencia y no se usan; no se extrapola al `150`.
- [La lectura ponderada se confunde con la muestral] → se rotulan ambas y se declara que la
  ponderada es una post-estratificacion a la prevalencia natural de los `200`.
- [El resultado se lee como numero canonico nuevo] → el documento declara que las cifras son
  aditivas y que no reemplazan ningun valor canonico de la tesis.

## Migration Plan

No hay migraciones ni datos productivos. Rollback: eliminar
`evaluation/linea_de_base.py` y `evaluation/tests/test_linea_de_base.py`; el repositorio vuelve
al estado previo. No se toca `App/`, `n8n/`, el corpus ni los numeros canonicos.
