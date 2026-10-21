## Why

El dictamen CONEAU 2026-10-20 deja abiertas dos observaciones de contenido metodológico. La
dimensión 6 (rec. 9) señala que el margen muestral del `6,66 %` se presenta como el valor
elegido para reproducir el corpus de 200 casos, lo que invierte la lógica del muestreo: el
margen debe fijarse a priori o declararse que el tamaño se fijó por disponibilidad operativa.
La dimensión 7 (7h / 6c) observa que las conclusiones califican el diseño como «riguroso» sin
matizar que los dos etiquetadores de la verdad de referencia son las mismas personas que
operaron el brazo manual, limitación que la tesis declara en el capítulo 4 pero no refleja en
las conclusiones. c-107 propagó los números canónicos pero dejó la rec. 9 como pregunta abierta.

## What Changes

- `04-marco-metodologico.tex`: declarar que el tamaño del corpus (200 casos) se fijó por
  disponibilidad operativa, y presentar el `6,66 %` como la precisión que ese tamaño implica
  con `N ≈ 2.646`, no como un margen elegido para reproducir el corpus. Se conservan la
  fórmula, los insumos y los valores canónicos (`N ≈ 2.646`, `e ≈ 6,66 %`, `n = 200`).
- `08-discusion.tex`: incorporar la dependencia etiquetadores/operadores entre las
  limitaciones del estudio, de forma concisa.
- `09-conclusiones.tex`: retirar el calificativo «riguroso» sin matizar y llevar la
  limitación de independencia del referente a las conclusiones.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: (1) la determinación del tamaño muestral SHALL declarar si se fijó a
  priori o por disponibilidad operativa, y MUST NOT presentar el margen como calibrado para
  reproducir el corpus; (2) la dependencia entre etiquetadores y operadores SHALL propagarse
  a la discusión y a las conclusiones, y las conclusiones MUST NOT calificar el diseño como
  riguroso sin ese matiz.

## Impact

- Archivos: `docs/Tesis/v9 (IA)/paper/sections/04-marco-metodologico.tex`,
  `08-discusion.tex`, `09-conclusiones.tex`.
- Sin cambios de código ni de valores canónicos: `N ≈ 2.646`, `e ≈ 6,66 %` y `n = 200`
  permanecen; no se reintroduce el `6,74 %` ni el universo `3.700`.
- No se edita el memo canónico ni `CHANGES.md`.
- Secuenciación: c-116 (reducción de páginas) se ejecuta después; c-115 no debe aumentar el
  conteo actual de páginas (104; tope ≤ 100 tras c-116).
