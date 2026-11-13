## Why

El script de linea de base de c-209 existe, pero el dictamen CONEAU v1.3.0 pide EVIDENCIA
NUEVA, no un script sin ejecutar. Falta correr la linea de base sobre el conjunto fuera de
muestra, producir artefactos versionados con las cifras y compararla, en el MISMO conjunto
de prueba, contra el hibrido congelado `hybrid-v3` de c-191/c-205. Esta change ejecuta la
medicion y deja la comparacion lista para que el dueno de la tesis la integre. Es ADITIVA:
no cambia ningun numero canonico y no edita los `.tex`.

## What Changes

- **Ejecucion reproducible** de `evaluation/linea_de_base.py` sobre los `200` casos
  in-sample y los `103` casos fuera de muestra con referencia por consenso. Dos corridas
  producen artefactos identicos byte a byte; se registra el SHA-256 de cada salida.
- **Artefactos versionados** en el directorio de la change: `linea_de_base_clasica_c210.json`
  (fuente unica de las cifras, con hashes de entrada y de salida), `linea_de_base_clasica_c210.md`
  (resumen legible) y `SHA256SUMS.txt`.
- **Tabla de comparacion** linea de base contra hibrido en el mismo conjunto de `103` casos:
  exactitud estricta, exactitud laxa, macro-F1, *balanced accuracy* y F1 por clase con
  soporte. El hibrido se cita de `analisis_fuera_de_muestra_c205.json`; sus cifras no se
  tocan.
- **Doble lectura metodologica**: metricas sobre la muestra y, cuando la linea de base usa
  re-ponderacion de clases, metricas ponderadas a la prevalencia natural del corpus de
  ajuste. Se reportan ambas; ninguna cifra unica se presenta como definitiva.
- **Borrador de seccion de tesis** en el directorio de la change, en estilo de
  `07-resultados.tex`, con la tabla comparativa. No se edita ningun `.tex`: el borrador
  queda para que el dueno de la tesis lo integre.

## Capabilities

### New Capabilities

- `evaluation-baseline-medicion`: ejecucion, artefactos deterministas y comparacion de la
  linea de base clasica contra el hibrido en el mismo conjunto de prueba, con lectura
  muestral y ponderada a la prevalencia natural.
- `tesis-baseline-comparison`: borrador de la seccion de resultados con la tabla comparativa
  lista para integrar, sin editar los archivos de la tesis.

### Modified Capabilities

(none)

## Impact

- Nuevos artefactos en `openspec/changes/c-210-medicion-de-la-linea-de-base/` (JSON, Markdown,
  `SHA256SUMS.txt` y borrador de tesis). La ejecucion escribe solo en el directorio de la
  change.
- Sin cambios en `App/`, `n8n/`, el clasificador de produccion, los corpus congelados, los
  numeros canonicos, `CHANGES.md` ni los `.tex`.
- Sin red, sin Gemini y sin API paga. Sin cambios de dependencias.
- Gobernanza: LOW (medicion de solo lectura sobre artefactos ya versionados); no se toca
  ningun numero canonico. El registro en `CHANGES.md` se omite porque el archivo pertenece a
  otro flujo de trabajo y esta prohibido editarlo.
