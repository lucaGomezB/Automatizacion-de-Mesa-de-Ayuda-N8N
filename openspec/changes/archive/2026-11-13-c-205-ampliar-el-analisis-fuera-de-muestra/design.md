## Context

Ver `proposal.md` — Why. Artefactos de partida (todos versionados por c-191, ver
`evaluation/data/campana/README.md` y la Sección 3.19 de `numeros-canonicos.md`):

- `evaluation/data/campana/corpus_independiente.json` — referencia de los `103` casos con
  consenso `E3`/`E4` (design D6); los `47` discordantes quedaron FUERA de la referencia.
- `evaluation/data/campana/predicciones_independiente.json` — `103` predicciones del
  clasificador congelado `hybrid-v3` (commit `561b3c4`).
- `evaluation/data/campana/doble_etiquetado_independiente.csv` — tabla primaria del doble
  etiquetado (150 casos, `E3`/`E4`).
- `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c191.py` — análisis de c-191
  (estricta/laxa con Wilson, por etapa, sin/con ponderación). Se LEE, no se edita.

Funciones puras ya disponibles (no reimplementar):

- `evaluation/metrics.py`: `matriz_confusion`, `precision_por_clase`, `sensibilidad_por_clase`,
  `f1_por_clase`, `soporte_por_clase`, `f1_macro`, `intervalo_wilson`, `resumen_exactitud`.
- `evaluation/kappa.py`: `kappa_cohen(pares)` (reutilizable para clasificador vs referencia).
- `evaluation/stats.py`: `efecto_minimo_detectable(n, alfa, potencia, bilateral, eficiencia_relativa)`.
- `evaluation/campana.py`: `cargar_corpus_solo_lectura`.

## Goals / Non-Goals

**Goals:**

- Completar el bloque fuera de muestra con macro-F1, métricas por clase con soporte,
  *balanced accuracy*, kappa del clasificador contra la referencia y matriz de confusión,
  reutilizando `evaluation/metrics.py`.
- Declarar la precisión/potencia del n efectivo `103` frente al objetivo de diseño D1 de c-191.
- Cuantificar el sesgo de exclusión de los `47` discordantes con una regla de decisión explícita.
- Extender el balance neto a la tasa de error fuera de muestra donde los artefactos lo permitan.
- Registrar cada cifra en el memo canónico y reportarla en la prosa de la tesis.

**Non-Goals:**

- Trabajo de campo, nueva corrida paga, gemini, ni reclutamiento (eso es c-206).
- Cambiar el clasificador, el corpus, el umbral o recalibrar nada.
- Reimplementar métricas: el script compone funciones de `evaluation/`.

## Decisions

### D1 — Reutilización estricta de las métricas

El script importa `matriz_confusion`, `precision_por_clase`, `sensibilidad_por_clase`,
`f1_por_clase`, `soporte_por_clase`, `f1_macro` e `intervalo_wilson` de `evaluation/metrics.py`;
`kappa_cohen` de `evaluation/kappa.py`; `efecto_minimo_detectable` de `evaluation/stats.py`.
No reimplementa el clasificador ni ninguna métrica. Alternativa descartada: cálculo ad-hoc,
que duplicaría la lógica y arriesgaría divergencia con los valores canónicos.

### D2 — Macro-F1 y métricas por clase, incluidas las de soporte cero

La macro-F1 es la media aritmética de las cinco F1 por clase (`f1_macro`), incluidas las de
soporte cero (`0.0`). Por clase se reportan precisión, sensibilidad/`recall`, F1 y soporte
desde la matriz `5x5` del n efectivo. La *balanced accuracy* es la media de las
sensibilidades por clase (`sensibilidad_por_clase`), y se declara su diferencia con la
exactitud estricta por desbalance.

### D3 — Kappa del clasificador contra la referencia

Se arma la lista de pares `(sector_asignado, sector_predicho)` del n efectivo y se pasa a
`kappa_cohen`; se reportan kappa, `p_o`, `p_e`, PABAK, `n` y su IC con las declaraciones de
alcance de `evaluation/kappa.py`. Se rotula como concordancia clasificador-referencia, no
como fiabilidad inter-etiquetador (esa es de `E1`/`E2`, Sección 3.14).

### D4 — Matriz de confusión fuera de muestra

`matriz_confusion(reales, predichos)` del n efectivo; filas = referencia, columnas =
predicción. Es la base de D2 y explica la frontera dominante de `Sistemas`.

### D5 — Potencia y precisión del n observado

Semi-ancho de Wilson observado = `(upper − lower) / 2` de `intervalo_wilson(87, 103)`; se
compara contra el objetivo de diseño D1 de c-191 (~8,4 pts) y se declara si lo cumple. La
potencia/MDE declarada se obtiene con `efecto_minimo_detectable(n=103)` (supuestos: `alfa=0,05`,
`potencia=0,80`, bilateral). La comparación se reporta como precisión alcanzada, no como
tamaño muestral elegido.

### D6 — Sensibilidad al sesgo de exclusión y regla de decisión

Escenarios: **peor caso** = los `47` excluidos fallan → `87/150 = 0,5800`; **mejor caso** =
los `47` aciertan → `134/150 = 0,8933`; **cota** = intervalo factible de la exactitud sobre
el universo de `150` bajo las etiquetas ausentes. Regla de decisión explícita: el umbral
`0,85` se sostiene solo si el peor caso lo alcanza; dado que el peor caso (`0,58`) queda
muy por debajo, el resultado sobre el n efectivo NO puede presentarse como superación del
umbral sin el arbitraje (c-206). Alternativa descartada: resolver los discordantes por
consenso a posteriori; el protocolo lo prohíbe (sesgaría kappa y referencia).

### D7 — Extensión del balance neto

Se recalcula el balance de derivaciones erróneas (Sección 3.11) sustituyendo `e_aut` por la
tasa de error estricta fuera de muestra; los insumos de costo y ahorro bruto siguen
`condicional`. Si un insumo no es derivable de los artefactos fuera de muestra, se declara
no computable con su motivo, sin valor.

### D8 — Script, salidas y solo lectura

`evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.py` (biblioteca estándar +
`evaluation/`), salidas `analisis_fuera_de_muestra_c205.{json,md}` en el mismo directorio, LF
y UTF-8 sin BOM. Determinístico; no escribe fuera de su directorio; imprime el SHA-256 de
cada salida. Consume los artefactos de c-191 vía `cargar_corpus_solo_lectura`.

### D9 — Registro canónico y prosa

Las cifras se registran en una sección nueva del memo posterior a 3.19 (Sección 3.20), con
procedencia y comando; la prosa de `07-resultados.tex` y `08-discusion.tex` las cita del
memo. Ningún valor `vigente` de las Secciones 3.1 a 3.19 cambia.

## Risks / Trade-offs

- [Contradicción con el resultado de c-191] → se reporta como hallazgo; no se recalibra ni se re-mide.
- [Sobreinterpretar como confirmación] → IC, n efectivo y regla de decisión de D6 bien visibles.
- [Un sector con soporte cero fuera de muestra] → se reporta `0.0` con su soporte; no se omite de la macro-F1.
- [Cifra sin fuente en la tesis] → Gate 0: toda cifra pasa por el memo con comando.
- [Gitleaks marca prosa con nombres de archivo] → referencias "sección N (`archivo.tex`)".

## Migration Plan

Apply en el orden de `tasks.md`: script + salidas (grupo 1), registro en el memo (grupo 2),
prosa + recompilación (grupo 3), validación (grupo 4). Rollback: revertir el script/salidas
nuevos, la sección nueva del memo y las fuentes `.tex`; el PDF se regenera. No hay datos ni
código productivo que revertir.

## Open Questions

- **Lista exacta de escenarios del sesgo de exclusión**: peor/mejor caso fijos; la "cota"
  admite más de una definición razonable (p. ej. por intervalo de Wilson del universo o por
  la tasa de discordancia). Se resuelve en el apply eligiendo una, declarada y reproducible.
