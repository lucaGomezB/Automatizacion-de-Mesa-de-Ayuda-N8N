# Proposal: c-102 — Congelar números canónicos de la tesis (Gate 0)

## Why

La tesis v9, dictaminada por CONEAU el 2026-10-20, tiene contradicciones
numéricas internas que condicionan la defensa. El propio dictamen fija como
observación obligatoria número 1 reconciliar la Tabla 7.5 con la intervención
humana del 9,5 % antes de cualquier otra corrección. Hoy:
la Tabla 7.5 reporta 124 casos con confianza < 0,70 mientras el texto declara
19 casos (9,5 %) de intervención; los 131 determinísticos + 69 Gemini no cierran
con los 46 casos ≥ 0,90; el universo `3.700 = 42 × 88 días calendario` contradice
la tasa de 42/día tomada de una semana laboral; y el micro-F1 0,6654 convive con
exactitud 0,7325 y subset accuracy 0,43 sin definir si la tarea es mono o
multietiqueta. Si cada rama de corrección reescribe su capítulo con su propio
criterio, el drift numérico se propaga y la defensa no puede verificar el
resultado operativo central. Este change es el **Gate 0**: produce la fuente
única de verdad numérica ANTES de que cualquier rama toque el texto.

## What Changes

- Crear el memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md`: tabla
  canónica final con todos los números que la tesis puede citar, cada uno con
  fuente (archivo y línea) y estado (`vigente` / `retirado` / `condicional`).
- Resolver o declarar explícitamente como no resoluble las siete contradicciones
  obligatorias: (1) gate de intervención humana, (2) etapas 131/69 vs bandas de
  confianza, (3) tramo "46 casos ≥ 0,90 con 13 errores", (4) universo y
  proyección horaria, (5) paradigma métrico, (6) clase "Bases de Datos" con n=1,
  (7) tabla canónica final.
- Declarar la regla exacta del gate de revisión implementada y qué confianza
  asigna la etapa determinística y por qué no dispara revisión.
- Fijar el criterio calendario vs días hábiles con su proyección resultante
  (45,0 h o ~32,2 h) y la decisión de propagación.
- Definir el set métrico final y su procedimiento de recálculo desde
  `evaluation/predicciones.json`, sin re-ejecutar el sistema.
- Incluir una sección "decisiones no resolubles" con la decisión editorial
  adoptada por cada punto que la evidencia disponible no permita cerrar.

## Capabilities

### New Capabilities

- `tesis-numeros-canonicos`: registro canónico y verificable de los números y
  criterios que la tesis cita, con procedencia por valor (archivo y línea),
  regla del gate de revisión y decisión editorial por punto en conflicto.

### Modified Capabilities

(none)

## Impact

- Nuevo artefacto: `docs/Tesis/Correcciones/numeros-canonicos.md`. NO se edita
  ningún `.tex` en este change.
- Fuentes de solo lectura: `evaluation/report.md`, `evaluation/predicciones.json`,
  `data/`, y los `.tex` citados en el alcance.
- Consumidores: cualquier rama que reescriba `04-marco-metodologico.tex`,
  `07-resultados.tex`, `08-discusion.tex` o `09-conclusiones.tex` —incluida la
  futura c-104— debe citar solo valores de la tabla canónica.
- Governance: MEDIO. Cero cambios de runtime, código, API o dependencias; cero
  experimentos nuevos, cero recolección de datos, cero llamadas a APIs.