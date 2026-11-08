# Proposal: Cerrar los residuales de la última auditoría (dictamen CONEAU v1.2.5)

## Why

El dictamen CONEAU del 2026-10-28 sobre la release `v1.2.5`
(`auditorias/Dictamen_Tesis_v10_v1.2.5_CONEAU_2026-10-28.md`) dejó residuales de
documentación, redacción y trazabilidad que las familias c-158..c-169 no cerraron: una
atribución imprecisa a Xuan et al. en 3.3, el uso de Sokolova y Lapalme como fuente que
"confirma" un resultado propio, una tensión sin resolver en la discusión (9.2), filas
desactualizadas del Anexo I (B9, B14, B16 y la fila `Lím.`) y la cronología de las
iteraciones Scrumban sin declarar como limitación. Ninguno exige mediciones nuevas: se
cierran con redacción y trazabilidad sobre información que ya está en el repositorio.

## What Changes

- **3.3 (`03-estado-del-arte.tex:56`)**: acotar la afirmación de que el rendimiento de
  CLASIFICACIÓN depende del idioma al benchmark que incluye clasificación (MEGA,
  `ahuja2023mega`); `xuan2025mmluprox` (razonamiento de opción múltiple) pasa a respaldar
  solo la brecha de desempeño multilingüe.
- **Resultados (`07-resultados.tex:153`)**: reformular para citar
  `Sokolova2009_performance_measures` por las DEFINICIONES de las métricas, sin
  "confirman" ni atribuirle la confirmación de un resultado propio.
- **Discusión 9.2 (`08-discusion.tex:32` frente a `:38`)**: calificar explícitamente como
  indirecta la comparación con el F1 macro del inglés, coherente con la declaración de no
  comparabilidad de `:32`.
- **Anexo I (`12-anexos.tex`)**: actualizar B14 y B16 (hoy "pendientes" aunque c-159 y
  c-163 los cerraron) y B9 (declarar la no recuperabilidad de las fechas de iteración como
  limitación); reformular la fila `Lím.` para declarar (d) validación fuera de muestra como
  NEGATIVO, no como límite cerrado.
- **Cronología de iteraciones (B9, `06-implementacion.tex:68` y `12-anexos.tex:224`)**:
  declarar de forma explícita y consistente que las fechas de las iteraciones Scrumban no
  son recuperables (sin fuente primaria), límite ya documentado en
  `docs/diagrams/cronograma.md` (OQ-1). No se inventan fechas.

## Out of Scope

- **(d) validación fuera de muestra**: es un NEGATIVO declarado que exige un corpus
  independiente inexistente. Este change NO fabrica su cierre; a lo sumo garantiza que el
  negativo quede declarado con honestidad y consistencia. Medirlo sería un change futuro
  separado.
- Nuevas mediciones, cambios de código (`App/`, `n8n/`, `evaluation/`), valores canónicos,
  `openspec/config.yaml` o `CHANGES.md`.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `tesis-document`: cuatro requisitos modificados (atribuciones del eje de modelos de
  lenguaje; punteros y residuos del Anexo I del 22 de octubre; cierre de los ítems (a)-(e)
  y fila `Lím.`; síntesis del estado del arte y comparabilidad en 9.2) y un requisito
  agregado (atribución no confirmatoria de Sokolova y Lapalme).

## Impact

- `docs/Tesis/v10 (IA)/paper/sections/{03-estado-del-arte,06-implementacion,07-resultados,08-discusion,12-anexos}.tex`
  y `docs/Tesis/Correcciones/dictamen-correcciones.md`; recompilación del PDF al aplicar.
- Gobernanza: LOW/MEDIUM (docs-only). Sin cambios de código, configuración, corpus ni
  valores canónicos.
