# Calibracion offline del clasificador deterministico (c-71)

- Casos: 200
- Casos sin match: 57
- Cobertura global del vocabulario: 0.7150
- Piso de precision exigido (OQ1): 0.90
- Umbral elegido: 1.0
- Umbral vigente en Settings: 1.0

## Metricas del determinista sobre el corpus (None = error)

- Exactitud estricta: 0.4850
- Exactitud de pertenencia: 0.5350
- F1 macro estricto: 0.4196
- F1 macro de pertenencia: 0.4272

## Cobertura por sector (real)

- Seguridad Informatica: cobertura 0.7097 (9 sin match)
- Soporte Tecnico Hardware: cobertura 0.8353 (14 sin match)
- Soporte Tecnico Software: cobertura 0.5672 (29 sin match)
- Bases de Datos: cobertura 1.0000 (0 sin match)
- Sistemas: cobertura 0.6875 (5 sin match)

## Curva precision/cobertura (cortocircuito)

| Umbral | Cortocircuitados | Aciertos | Precision | Cobertura |
|--------|------------------|----------|-----------|-----------|
| 0.0000 | 131 | 97 | 0.7405 | 0.6550 |
| 0.1667 | 33 | 22 | 0.6667 | 0.1650 |
| 0.5000 | 33 | 22 | 0.6667 | 0.1650 |
| 0.7500 | 7 | 3 | 0.4286 | 0.0350 |
| 1.0000 | 1 | 1 | 1.0000 | 0.0050 |

---

## Contexto

Este documento registra la recalibracion OFFLINE del cortocircuito determinista
(c-71, design D4/D6). Se genera con:

```bash
cd App/Backend
PYTHONPATH=../.. python3 -m evaluation.deterministic_measurement \
    --umbral-actual 1.0 --output ../../docs/deterministic_calibration.md
```

No invoca a Gemini: solo corre `DeterministicClassifier` sobre
`data/corpus_evaluacion_pseudonimizado.json` y reutiliza `evaluation/metrics.py`.
El umbral queda como setting FIJO (OQ3), re-derivado offline, no en runtime.

## Linea base vs. endurecimiento

| Evidencia | Linea base | Tras c-71 |
|-----------|-----------|-----------|
| Casos sin match (vocabulario) | 126 (63%) | 57 (28.5%) |
| Cobertura global del vocabulario | 0.37 | 0.7150 |
| Sobre-prediccion de `Seguridad Informatica` | 126 vs 31 reales | 17 vs 31 reales (sin sesgo por defecto) |
| No-match: sector arbitrario | Si (primera clave) | No (`sin_prediccion=True`, `sector_predicho=None`) |
| Cortocircuitados con confianza exactamente 1.0 | 100% | Solo senal dominante (conf 1.0 = ganador >= 4, segundo 0) |
| Exactitud estricta del cortocircuito (conf >= 0.90) | ~0.51 | 1.00 @ cobertura 0.005 (umbral calibrado) |
| Pertenencia del cortocircuito | ~0.76 | no aplica al punto calibrado (1 caso) |

Distribucion de predicciones principales (200 casos): `None` 69 (57 sin senal +
12 ambiguos), `Soporte Tecnico Hardware` 67, `Soporte Tecnico Software` 28,
`Seguridad Informatica` 17, `Sistemas` 15, `Bases de Datos` 4.

## Interpretacion del tradeoff (hallazgo)

Con el piso de precision ESTRICTA de 0.90 (OQ1) y el corpus actual, la curva
precision/cobertura muestra que **no existe una region de cobertura util que
respete el piso**: el unico umbral admisible es 1.0, con 1/200 casos (cobertura
0.005). En otras palabras, el filtro determinista de keywords NO alcanza 0.90 de
exactitud estricta con cobertura no trivial sobre este corpus (canal telefonico
mayoritario, Hardware/Software semanticamente proximos).

Consecuencia: el pipeline hibrido escala practicamente TODOS los casos a Gemini.
El ahorro de costo/latencia del cortocircuito queda practicamente anulado. Esta
es la consecuencia directa de "PREFER precision over coverage" (OQ1) y se declara
explicitamente para que el autor decida si:

- (a) acepta el cortocircuito casi nulo (maxima precision, costo Gemini alto);
- (b) baja el piso de precision a un valor alcanzable (p. ej. 0.70, cobertura
  ~0.66 con precision 0.74 en el umbral 0) documentando el tradeoff;
- (c) invierte en vocabulario/señales mas ricas antes de recalibrar.

El umbral queda fijado en `Settings.deterministic_confidence_threshold = 1.0`.
La confianza ya NO es degenerada: 1.0 exige `winner_score >= min_matches +
2` (= 4) y margen maximo (segundo = 0); un unico match o un empate dan 0.0.

## Linea base hibrida (Gemini) — task 4.4

Capturada el 2026-10-05 con cuota de Gemini disponible, via
`evaluation/run_evaluation.py` sobre los 200 casos (199 escalaron a Gemini,
1 cortocircuito deterministico, 0 fallbacks):

| Metrica | Determinista solo | Hibrido (Gemini) | Delta |
|---------|-------------------|------------------|-------|
| Exactitud estricta | 0.4850 | 0.6700 | +0.1850 |
| F1 macro estricto | 0.4196 | 0.4801 | +0.0605 |
| Micro-F1 (conjunto) | n/d | 0.6318 | — |

Distribucion por etapa: deterministic 1, gemini 199, fallback 0.
Macro-F1 por sector del hibrido: Hardware 0.8519, Software 0.6667,
Seguridad 0.5769, Sistemas 0.3051, BD 0.0000 (soporte 1).

**Caveat de reproducibilidad (bloqueo pre-existente, fuera de c-71):** el corpus
real tiene 56 casos con `tiempo_automatizado_s: null`, y
`evaluation/corpus.py::cargar_corpus` los exige numericos. `_a_float` es
INTOCABLE por regla dura, por lo que la corrida oficial falla al cargar. Para
capturar la linea base se corrio el mismo runner sobre una copia con los tiempos
nulos normalizados a 0.0 (los tiempos NO participan de las metricas F1). Una
correccion definitiva del corpus o del loader queda como deuda separada.

