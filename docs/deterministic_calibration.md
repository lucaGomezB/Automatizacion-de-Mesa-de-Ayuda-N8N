# Calibracion offline del clasificador deterministico (c-71 y c-74)

> **c-74 (OQ3 revisado):** el punto de operacion del cortocircuito es
> **COMPARATIVO** contra la etapa semantica (Gemini), no un piso ABSOLUTO de
> precision. La calibracion corre **offline** y reutiliza las predicciones de
> Gemini **cacheadas**; no invoca al proveedor. La fuente de la calibracion es la
> cache **FORCE-ESCALATE** (`evaluation/predicciones_calibracion.json`), porque la
> cache **OFICIAL** (`evaluation/predicciones.json`, hybrid-v3) NO contiene
> predicciones de Gemini sobre el conjunto cortocircuitable (ver "Convencion de
> dos caches"). La senal de seleccion es el `score_correctitud` (ASG-010), que
> **ordena** la correctitud esperada y **NO es una probabilidad calibrada**; no la
> `confianza` (fuerza de senal, ASG-009). El tau congelado en `Settings` se
> **deriva out-of-fold** (no in-sample).

## Corpus y cobertura del vocabulario

- Casos: 200
- Casos sin match (`sin_prediccion`): 57
- Cobertura global del vocabulario: 0.7150
- Conjunto cortocircuitable (senal no ambigua): 131

## Metricas del determinista sobre el corpus (None = error)

- Exactitud estricta: 0.4850
- Exactitud de pertenencia: 0.5350
- F1 macro estricto: 0.4196
- F1 macro de pertenencia: 0.4272

## Punto de operacion COMPARATIVO (OQ3 revisado)

Criterio: **maximizar la cobertura** del subconjunto cortocircuitable `S`
sujeta al **piso comparativo** `precision_det(S) >= precision_gem(S)`, con las
predicciones de Gemini cacheadas y el umbral ajustado **out-of-fold**.

- tau OOF exacto (agregado de los 5 folds): **0.5166666666666666**
- tau fijado en Settings (`deterministic_score_threshold`): **0.5166**
  (derivado OUT-OF-FOLD y truncado hacia abajo a 4 decimales para incluir el
  conjunto no ambiguo completo)
- Cobertura del punto: **0.6550** (131/200)
- `precision_det(S)`: **0.7405** (97/131)
- `precision_gem(S)`: **0.6769** (88/130) — 1 caso cortocircuitable no tiene
  prediccion de Gemini en la cache FORCE-ESCALATE (fue el unico caso que aun
  cortocircuito en la corrida forzada, con `score = 1.0`) y se excluye del
  denominador de Gemini

> Como el piso comparativo se cumple en **todo** el conjunto cortocircuitable
> (det 0.7405 >= gem 0.6769), el punto de operacion equivale a cortocircuitar
> todo el conjunto con senal no ambigua. El valor NO se elige in-sample sobre el
> corpus de test reportado: se **deriva out-of-fold** agregando
> `ResultadoComparativoOOF.umbrales_por_fold` (regla implementada en
> `evaluation/deterministic_measurement.py::umbral_de_settings_oof`) y se replica
> en `Settings`. Los cinco folds coinciden en `0.51666...`, que truncado hacia
> abajo a 4 decimales da `0.5166`.

### Calibracion comparativa out-of-fold (anti-fuga)

Procedencia: `cross-fitting out-of-fold`. El umbral de cada fold se ajusta SOLO
con los folds de entrenamiento (excluye el fold evaluado); el corpus de
evaluacion es el test reportado y no participa del ajuste de un caso evaluado.

- Folds: 5
- Umbrales por fold: `(0.5166666666666666, 0.5166666666666666, 0.5166666666666666, 0.5166666666666666, 0.5166666666666666)`
- Regla del tau congelado: los folds coinciden; el agregado OOF (coincidencia, o
  `min` ante discrepancia) es `0.516666...`, truncado a 4 decimales = **0.5166**.
  El tau de `Settings` se **deriva** de estos umbrales por fold, no in-sample.
- Cobertura OOF: **0.6550** (131/200)
- `precision_det` OOF: **0.7405** (97/131)
- `precision_gem` OOF: **0.6769** (88/130)

### Curva comparativa (det vs gem por umbral)

| Umbral | Cortocircuitados | Cobertura | precision_det | precision_gem | Cumple piso |
|--------|------------------|-----------|---------------|---------------|-------------|
| 0.000000 | 131 | 0.6550 | 0.7405 | 0.6769 | si |
| 0.516667 | 131 | 0.6550 | 0.7405 | 0.6769 | si |
| 0.800000 | 123 | 0.6150 | 0.7236 | 0.6721 | si |
| 0.850000 | 33 | 0.1650 | 0.6667 | 0.6250 | si |
| 0.880000 | 7 | 0.0350 | 0.4286 | 0.3333 | si |
| 0.900000 | 1 | 0.0050 | 1.0000 | 0.0000 | si |

## Re-medicion hibrida OFFLINE con la cache de Gemini (task 4.4)

Simulacion del pipeline con el punto de operacion vigente, usando la cache
FORCE-ESCALATE de Gemini (`evaluation/predicciones_calibracion.json`; sin invocar
al proveedor). Mezcla: **determinista 131 / Gemini 69**.

| Metrica | Valor |
|---------|-------|
| Exactitud estricta | 0.7300 |
| F1 macro estricto | 0.5165 |
| Micro-F1 (conjunto) | 0.6654 |
| Subset accuracy | 0.4300 |
| Hamming loss | 0.3586 |
| Jaccard promedio | 0.6414 |

F1 por sector (hibrido, one-vs-rest): Seguridad Informatica 0.6122,
Soporte Tecnico Hardware 0.8800, Soporte Tecnico Software 0.7015,
Bases de Datos 0.0000 (soporte 1), Sistemas 0.3889.

### Delta contra la linea base y vs policy-B

| Comparacion | Baseline | c-74 | Delta |
|-------------|----------|------|-------|
| Cobertura del cortocircuito (piso absoluto c-71, Fase A) | 0.0050 (1/200) | 0.6550 (131/200) | **+0.6500** |
| Macro-F1 hibrido (policy-B) | 0.5165 | 0.5165 | +0.0000 |
| Micro-F1 (policy-B) | 0.6654 | 0.6654 | +0.0000 |
| Exactitud estricta (cache hybrid-v2, 199 Gemini + 1 det) | 0.6900 | 0.7300 | +0.0400 |
| Macro-F1 (cache hybrid-v2) | 0.4605 | 0.5165 | +0.0560 |

**Lectura:** el punto comparativo **reproduce la cifra policy-B** (macro-F1
0.5165 a cobertura 0.655) pero ahora **justificado** por un criterio
anti-fuga explicito (piso comparativo OOF), en lugar de un piso absoluto
inalcanzable (0.90 -> cobertura 0.005). El salto de cobertura 0.005 -> 0.6550
es el efecto directo de retirar el piso absoluto y adoptar el comparativo.

## Convencion de dos caches de predicciones

La calibracion comparativa y la corrida oficial consumen caches distintas por una
razon metodologica:

- `evaluation/predicciones.json` — **cache OFICIAL**, escrita por
  `evaluation/run_evaluation.py`. Es la corrida real del pipeline hibrido
  (`hybrid-v3`) y es la que se reporta. En esa corrida los 131 casos
  cortocircuitables **NO llaman a Gemini** (el determinista los resuelve), por lo
  que esta cache **no** contiene predicciones semanticas sobre el conjunto
  cortocircuitable.
- `evaluation/predicciones_calibracion.json` — **cache FORCE-ESCALATE**, fuente de
  la calibracion. Contiene predicciones de Gemini sobre el conjunto
  cortocircuitable (199 Gemini + 1 determinista en la copia preservada), porque la
  calibracion comparativa **necesita** `precision_gem(S)` sobre ese conjunto. Sin
  ella la re-corrida degenera a `precision_gem(S) = 0/0`.

Resolucion en codigo: `evaluation/deterministic_measurement.py::resolver_cache_calibracion(repo_root)`
prefiere la cache de calibracion (`CALIBRACION_CACHE_PATH`) cuando existe y cae a
la cache oficial (`PREDICCIONES_OFICIALES_PATH`) en caso contrario. La re-medicion
offline y el reporte usan esa resolucion.

**Regenerar la cache FORCE-ESCALATE:** correr el pipeline con el cortocircuito
determinista deshabilitado, es decir con el umbral de score por encima del maximo
observado (`DETERMINISTIC_SCORE_THRESHOLD=1.01`, o su equivalente en `Settings`),
de modo que TODOS los casos pasen por Gemini; usar `run_evaluation.py --force
--confirm-paid` con el mismo corpus y persistir el resultado como
`evaluation/predicciones_calibracion.json`. Esto invoca al proveedor (corrida
paga); no se ejecuta en la suite de tests.

## Corrida OFICIAL paga (task 4.6, COMPLETADA el 2026-10-07)

La corrida paga de `evaluation/run_evaluation.py` sobre el corpus **se ejecuto**
(hybrid-v3, tau `0.5166`). Resultados oficiales frescos:

| Metrica | Valor |
|---------|-------|
| Exactitud estricta | **0.7350** (147/200; Wilson 95% [0.6698, 0.7913]) |
| Exactitud de pertenencia | **0.7350** |
| F1 macro estricto | **0.5207** |
| Micro-F1 (conjunto) | **0.6654** |
| Subset accuracy | **0.4300** |
| Hamming loss | **0.3586** |
| Jaccard promedio | **0.6414** |

- Distribucion de etapas: **determinista 131 / Gemini 69 / fallback 0**.
- Llamadas a Gemini: **69**, errores: **0**.
- Fecha de corrida: **2026-10-07**.

### Offline (reuso de cache) vs oficial (fresco)

La re-medicion offline (seccion anterior) reutiliza la cache FORCE-ESCALATE sin
invocar al proveedor; la corrida oficial hace llamadas frescas a Gemini para los 69
casos escalados. La diferencia es minima y consistente:

| Metrica | Offline (reuso cache) | Oficial (fresco) | Delta |
|---------|-----------------------|------------------|-------|
| Exactitud estricta | 0.7300 | 0.7350 | +0.0050 |
| F1 macro estricto | 0.5165 | 0.5207 | +0.0042 |

La cifra reportada en la tesis es la **oficial fresca** (0.7350 / 0.5207); la
offline se conserva como verificacion reproducible sin costo de proveedor.

## Curva ABSOLUTA heredada (retirada como criterio de operacion)

Se conserva solo como referencia historica de c-71. El piso absoluto de 0.90
dejaba cobertura 0.005 (1/200) y ya no gobierna el cortocircuito.

| Umbral | Cortocircuitados | Aciertos | Precision | Cobertura |
|--------|------------------|----------|-----------|-----------|
| 0.0000 | 131 | 97 | 0.7405 | 0.6550 |
| 0.1667 | 33 | 22 | 0.6667 | 0.1650 |
| 0.5000 | 33 | 22 | 0.6667 | 0.1650 |
| 0.7500 | 7 | 3 | 0.4286 | 0.0350 |
| 1.0000 | 1 | 1 | 1.0000 | 0.0050 |

## Cobertura por sector (real)

- Seguridad Informatica: cobertura 0.7097 (9 sin match)
- Soporte Tecnico Hardware: cobertura 0.8353 (14 sin match)
- Soporte Tecnico Software: cobertura 0.5672 (29 sin match)
- Bases de Datos: cobertura 1.0000 (0 sin match)
- Sistemas: cobertura 0.6875 (5 sin match)

---

## Contexto y reglas

- El cortocircuito se gobierna por `score_correctitud >= deterministic_score_threshold`
  y solo con senal dominante (`sin_prediccion`/`ambiguo` escalan siempre, OQ5).
- `deterministic_min_matches` es **feature** del score (denominador de la
  evidencia), NO un gate de seleccion (OQ4/ASG-011).
- La `confianza` (ASG-009) se conserva como medida de fuerza de senal; ya NO es
  criterio de seleccion.
- El test reportado (el corpus) nunca se usa para ajustar el punto de operacion
  (procedencia cross-fitting OOF; `evaluation-framework`). El tau congelado en
  `Settings` se deriva de `ResultadoComparativoOOF.umbrales_por_fold`
  (`umbral_de_settings_oof`), de modo que su procedencia es verificable y una
  regresion a la eleccion in-sample se detecta por test.
- Restricciones intactas: cinco strings canonicos, `KEYWORD_MAP`, prompt de
  Gemini y `evaluation/corpus.py::_a_float`.

### Reproduccion

```bash
cd App/Backend
# Verificacion OFFLINE (no invoca a Gemini): imprime el reporte completo.
# Resuelve la cache FORCE-ESCALATE y debe reportar precision_gem(S) 0.6769 (88/130)
# y tau 0.5166.
PYTHONPATH=../.. python3 -m evaluation.deterministic_measurement --umbral-actual 1.0
```

El comando es **offline**: no invoca a Gemini y reutiliza la cache FORCE-ESCALATE
(`evaluation/predicciones_calibracion.json`) para la rama semantica del criterio
comparativo. NO sobrescribe este documento: la seccion de la corrida oficial paga
(0.7350 / 0.5207) se transcribe de la corrida registrada el 2026-10-07, no la
genera el comando offline.
