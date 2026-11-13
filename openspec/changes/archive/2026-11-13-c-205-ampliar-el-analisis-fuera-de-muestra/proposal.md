## Why

La validación fuera de muestra de c-191 publicó la exactitud estricta (`0,8447`, IC de Wilson `[0,7625; 0,9021]`), la laxa (`0,8738`) y la ponderada por sector (`0,8146`) sobre el n efectivo `103`, pero dejó sin medir la macro-F1, las métricas por clase, la *balanced accuracy*, el kappa del clasificador contra la referencia, el análisis de potencia del n observado y el efecto de la exclusión de los `47` discordantes. El tribunal reestimó la tesis en ~8,3/10 y señaló `Resultados` y `Marco metodológico` como los criterios a subir hacia ≥9. Completar el análisis con los artefactos YA versionados es la palanca barata: sin campo, sin corrida paga, sin tocar el clasificador ni el corpus (impacto estimado +0,3 a +0,5 en esas dos rúbricas).

## What Changes

- **Script de solo lectura** `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.py` que reproduce, desde los artefactos versionados, cada cifra nueva; reutiliza `evaluation/metrics.py` y no reimplementa el clasificador ni las métricas.
- **Métricas ampliadas fuera de muestra**: macro-F1 (cinco clases) y por clase (precisión, sensibilidad/recall, F1 y soporte); *balanced accuracy*; kappa de Cohen del clasificador contra la referencia; matriz de confusión out-of-sample `5x5`.
- **Potencia y precisión**: semi-ancho del IC de Wilson observado con `n` efectivo `103` frente al objetivo de diseño (design D1 de c-191, ~8,4 pts) y la potencia/MDE declarada.
- **Sesgo de exclusión**: análisis de sensibilidad de los `47` casos excluidos (peor/mejor caso y una cota) con una **regla de decisión explícita** que lo ata a la exactitud reportada.
- **Balance neto/costo**: extensión del balance in-sample a la tasa de error fuera de muestra donde los artefactos lo permiten (o declaración de no computable).
- **Registro canónico**: cada cifra nueva se registra en `docs/Tesis/Correcciones/numeros-canonicos.md` (sección nueva posterior a 3.19) con fuente y comando.
- **Prosa de tesis**: `07-resultados.tex` y `08-discusion.tex` reportan las métricas nuevas y el tratamiento explícito del sesgo de exclusión.

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `evaluation-out-of-sample-validation`: se extiende el análisis fuera de muestra con macro-F1, métricas por clase con soporte, *balanced accuracy*, kappa del clasificador, matriz de confusión, análisis de potencia del n observado, sensibilidad al sesgo de exclusión y extensión del balance neto.
- `tesis-numeros-canonicos`: se agrega una sección nueva (posterior a 3.19) con las cifras ampliadas fuera de muestra, cada una con procedencia y comando, sin alterar ningún valor `vigente`.
- `tesis-document`: se agrega el reporte de las métricas ampliadas fuera de muestra y el tratamiento explícito del sesgo de exclusión en `07-resultados.tex` y `08-discusion.tex`.

## Impact

- Nuevo: `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.py` y sus salidas (`.json`, `.md`) en el mismo directorio.
- `docs/Tesis/Correcciones/numeros-canonicos.md` (sección nueva tras 3.19; encabezado con el upsert de c-205).
- `docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex` y `08-discusion.tex`; `main.pdf` y `compilacion.md` recompilados.
- Lectura sin edición de `evaluation/metrics.py`, `evaluation/kappa.py`, `evaluation/stats.py`, `evaluation/campana.py`, `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c191.py` y de todos los artefactos de la campaña (`corpus_independiente.json`, `predicciones_independiente.json`, `doble_etiquetado_independiente.csv`).
- Gobernanza: MEDIUM/HIGH (cambia hechos de la tesis). Non-goals: sin campo, sin corrida paga, sin cambio de clasificador ni de corpus.

## Risks

| Riesgo | Probabilidad | Mitigación |
|--------|--------------|------------|
| El análisis contradice el resultado de c-191 | Baja | Se reporta como hallazgo; no se recalibra ni se re-mide el clasificador |
| Sobreinterpretar el resultado como confirmación | Media | Se reportan IC, n efectivo y sesgo de exclusión; no se extrapola |
| Deriva de los números vs c-191 | Baja | El script reutiliza `evaluar_fuera_de_muestra` y `resumen_exactitud` |
| Cifras sin fuente en la tesis | Media | Gate 0: toda cifra se registra en `numeros-canonicos.md` con comando |

## Rollback Plan

El change no modifica `App/`, `n8n/` ni datos canónicos. Revertir las fuentes `.tex`, la sección nueva del memo y el script/salidas nuevos de `analisis/` al commit previo deja el repositorio en el estado de `v1.3.0`. No hay migraciones ni datos productivos que revertir.

## Dependencies

- Artefactos versionados de c-191 (corpus independiente, predicciones, tabla primaria del doble etiquetado) presentes en `evaluation/data/campana/`.
- `evaluation/metrics.py`, `evaluation/kappa.py` y `evaluation/stats.py` (solo lectura).

## Success Criteria

- [ ] El script produce cada cifra nueva y es determinístico (dos corridas idénticas) y de solo lectura (`git status` limpio).
- [ ] Macro-F1, métricas por clase con soporte, *balanced accuracy*, kappa del clasificador y matriz de confusión quedan reproducidos.
- [ ] El análisis de potencia y la sensibilidad de los `47` excluidos figuran con la regla de decisión explícita.
- [ ] Cada cifra se registra en `numeros-canonicos.md` con fuente y comando.
- [ ] `07-resultados.tex` y `08-discusion.tex` reportan las métricas nuevas y el sesgo de exclusión.
- [ ] `openspec validate c-205-ampliar-el-analisis-fuera-de-muestra --strict` pasa.
