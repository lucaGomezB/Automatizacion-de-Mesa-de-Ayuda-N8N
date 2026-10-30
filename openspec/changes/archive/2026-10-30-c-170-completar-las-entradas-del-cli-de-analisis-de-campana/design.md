## Context

El CLI de análisis de campaña de c-167 (`evaluation/analisis_campana.py`) es de solo lectura y
consume ocho nombres canónicos desde una única carpeta `--entrada`
(`evaluation/data/campana/`). Dos de las entradas no las produce ningún runbook de la campaña
(ver `proposal.md` — Why, con las citas `analisis_campana.py:55,60,152,157`). La campaña todavía
no corrió, de modo que el defecto es de completitud de la instrumentación, no un fallo en
producción.

Restricciones que moldean el enfoque:

- c-167 (CLI + spec delta `evaluation-framework` + tests) ya está archivado y verificado; no se
  toca.
- Los changes archivados c-165..c-168 y c-169 no se modifican.
- No cambia el comportamiento entregado (`App/**`, `n8n/**`). El trabajo es docs + un helper puro
  de `evaluation/` + tests.
- Los datos reales de la campaña no existen aún; el helper se prueba con fixtures sintéticos de
  `evaluation/tests/fixtures/campana/`.
- Governance BAJA/MEDIA: offline, sin red ni Gemini, TDD estricto.

## Goals / Non-Goals

**Goals:**

- Que la campaña produzca EXACTAMENTE las dos entradas que el CLI de c-167 espera, de forma
  reproducible y verificable (SHA-256), sin conocimiento tácito.
- Registrar la procedencia de las dos entradas en el README de la campaña y en los runbooks.

**Non-Goals:**

- No se modifica `evaluation/analisis_campana.py`, su spec delta ni sus tests.
- No se ejecuta la campaña ni se generan datos reales (solo el paso de ensamblado y su
  documentación).
- No se regeneran artefactos de v9 ni se escribe en `evaluation/evidence/`.
- No se edita c-169 (la actualización de su gate se documenta como recomendación, ver D5).

## Decisions

- **D1 — Enfoque: preparar las entradas, no cambiar el CLI (Opción A).** Se agrega un paso que
  produce las dos entradas que el CLI ya espera. Alternativa (Opción B): cambiar
  `evaluation/analisis_campana.py` para leer los dos archivos C1 por separado y la cache in-sample
  desde una ruta documentada. Se descarta porque toca un CLI archivado y verificado (c-167), su
  spec delta de `evaluation-framework` y su suite, reabriendo trabajo cerrado por un defecto de
  completitud de la instrumentación de la campaña; además mantiene dos contratos de entrada
  divergentes (el contrato C1 de c-167 es la hoja única, `.../c-167-.../design.md:42`).

- **D2 — Helper puro y versionado, no shell manual.** La unión se implementa en
  `evaluation/preparar_entradas_analisis.py` (stdlib + `evaluation.doble_etiquetado`), no como
  comandos `cat`/`cp` en el runbook, para que sea reproducible, testeable y no se pueda saltar en
  silencio. Se apoya en las piezas ya existentes: `COLUMNAS_C1` y `validar_doble_etiquetado` de
  `evaluation/doble_etiquetado.py:44,331` y `es_archivo_congelado` de
  `evaluation/plan_campana.py:325`.

- **D3 — Unión C1 con validación por tarea.** El helper escribe un único encabezado C1
  (`plantilla_etiquetado.csv`, `doble_etiquetado.csv` + `brazo_manual.csv`) y re-valida cada tarea
  con `validar_doble_etiquetado(..., tarea=...)` contra el corpus antes de escribir. Esto respeta
  el contrato de c-167 (fila C1: la planilla trae ambas tareas) y reutiliza el validador único de
  c-168 en vez de reimplementar reglas. LF + UTF-8 sin BOM para que el SHA-256 coincida entre
  Windows y Linux (`.gitattributes` ya fija LF para los `*.csv` de la carpeta).

- **D4 — Staging in-sample como copia byte a byte.** `predicciones_in_sample.json` se materializa
  como copia exacta de `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`
  (`evaluation/data/campana/README.md:106-108`). No se regenera v9. El helper imprime y registra el
  SHA-256 de la copia y de la fuente, y se niega a escribir en `evaluation/evidence/`.

- **D5 — Registro del gate de c-169.** El gate de c-169 (`c-169-.../tasks.md:11`, tarea 0.2)
  exige hoy `doble_etiquetado.csv`, `plan_campana.csv`, `intervenciones.csv`, `registro_sujetos.csv`
  y `analisis/`, pero NO las dos entradas nuevas. Como c-170 hace correr el análisis end-to-end,
  el gate SHOULD exigir también `plantilla_etiquetado.csv` y `predicciones_in_sample.json`. No se
  edita c-169 (fuera de alcance); se deja la recomendación y la procedencia en los runbooks y el
  README de la campaña, y se propone la enmienda al gate como seguimiento.

- **D6 — Un solo spec delta.** El delta va a `evaluation-campaign-instrumentation` (ECM-011..013),
  porque los artefactos producidos son instrumentos de la campaña y no se toca el CLI. No se agrega
  delta a `evaluation-framework` porque su comportamiento no cambia (Opción A).

## Risks / Trade-offs

- **Duplicación del contenido C1** (`plantilla_etiquetado.csv` repite las filas de
  `doble_etiquetado.csv` y `brazo_manual.csv`) → Mitigación: el helper deriva el archivo de las
  fuentes versionadas y registra el SHA-256 de las tres, de modo que una divergencia es detectable;
  los runbooks indican regenerar la planilla unificada cuando cambia una fuente.
- **Deriva entre la copia in-sample y la fuente congelada** → Mitigación: copia byte a byte con
  verificación de hash; el helper imprime y registra ambos SHA-256.
- **El gate de c-169 no exige las nuevas entradas** → Mitigación: se documenta la recomendación
  (D5) y la procedencia; el propio análisis de c-167 ya declara "no se obtuvo" si faltan, así que no
  hay fallo silencioso.

## Migration Plan

1. Implementar `evaluation/preparar_entradas_analisis.py` con TDD (RED/GREEN/triangular/REFACTOR)
   y sus tests offline.
2. Actualizar los runbooks, `evaluation/data/campana/README.md` (tabla SHA-256) y
   `evaluation/data/campana/analisis/README.md`.
3. Rollback: revertir el commit del helper y de los docs. Como no se toca `App/**`, `n8n/**` ni el
   CLI de c-167, no hay cambio de comportamiento entregado que revertir.

## Open Questions

Ninguna que afecte specs, enfoque ni tareas.
