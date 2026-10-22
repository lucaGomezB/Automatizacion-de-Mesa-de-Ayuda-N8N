## Why

El dictamen CONEAU 2026-10-22 (`auditorias/Dictamen_Tesis_v1.0.1_CONEAU_2026-10-22.md`) aprueba la tesis v1.0.1 **sin condiciones** y deja **tres observaciones residuales no bloqueantes**, todas de caracter editorial: (1) el parrafo introductorio de la tabla comparativa del estado del arte declara "cuatro dimensiones" e incluye "soberania sobre los datos", que no es una columna real; (2) el hallazgo de que Gemini nunca devolvio una confianza inferior a 0,85 en los 200 casos se lee solo como justificacion de una sub-hipotesis no contrastada, no como resultado empirico con valor propio; y (3) la mencion a Zendesk, Freshdesk y ServiceNow en la introduccion se formula como relevamiento propio con fecha pero sin entrada bibliografica formal. Cerrar estas tres observaciones antes de la defensa es de bajo costo y elimina los ultimos puntos observables por el evaluador. No hay cambios de codigo de aplicacion. Los cambios se aplican sobre la version de trabajo `docs/Tesis/v10 (IA)/` (creada por el change prerrequisito `c-122-migrar-tesis-a-v10`) y se publican como la release `v1.1.0` (D2).

## What Changes

- **REC 1 - Tabla comparativa del estado del arte:** alinear el parrafo introductorio de `sections/03-estado-del-arte.tex` (linea ~60) con las cuatro columnas reales de `\label{tab:comparativa}` (Solucion, Despliegue, Clasificacion automatica, Modelo de costo). Se prefiere la edicion minima (ajustar la prosa) frente a agregar la columna; la decision queda registrada en `design.md`.
- **REC 2 - Hallazgo del gate como resultado propio:** agregar una frase o parrafo en `sections/08-discusion.tex` (y/o la subseccion de intervencion humana de `sections/07-resultados.tex`, label `subsec:reduccion-intervencion`) que presente la conducta observada del gate (confianza de Gemini siempre >= 0,85 en el corpus) como hallazgo empirico positivo sobre el comportamiento del clasificador en el dominio evaluado. No introduce numeros nuevos.
- **REC 3 - Cobertura bibliografica de plataformas comerciales:** agregar entradas `@online` para Zendesk, Freshdesk y ServiceNow en `Bibliography_base.bib`, siguiendo el patron exacto del bloque c-120 (`DigitalOcean2026_pricing`, `Google2026_vertex_pricing`: `url`, `urldate = {2026-10-19}`, `note` de consulta), y citarlas con `\parencite` en `sections/01-introduccion.tex` linea ~68. **No se inventan cifras de precio**: si no hay figura verificable, la `note` declara la pagina de documentacion (capacidades/precios) y la prosa se mantiene como observacion de relevamiento.
- **RELEASE v1.1.0 - Version y trazabilidad (D2):** actualizar en `sections/12-anexos.tex` (`sec:anexo-repositorio`) el tag `v1.0.1` por `v1.1.0`, crear el tag anotado `v1.1.0` sobre el commit de cierre de v10 (patron C1/C2 de c-111) y consignar el hash completo del commit etiquetado en el manuscrito y en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

> **Nota de alcance (REC 4 retirada):** una REC 4 original proponia una nota de trazabilidad sobre una supuesta discrepancia de conteo bibliografico (54 vs 39). La verificacion directa del arbol de trabajo (`grep -c "^@"` = 56; historia git: 54 entradas antes de c-120, 56 despues, delta +2 explicado por las dos entradas `@online` de c-120) demuestra que **no existe discrepancia**. La REC 4 queda retirada y el dictamen fue corregido con fe de errata (seccion 9). Este change cierra tres observaciones, no cuatro.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `tesis-document`: se agregan tres requisitos que cierran las observaciones residuales del dictamen v1.0.1 (consistencia del parrafo introductorio con las columnas de la tabla comparativa, hallazgo del gate presentado como resultado propio, y cobertura bibliografica formal de las plataformas comerciales). Se preservan los numeros canonicos y el presupuesto de paginas (<= 101).

## Impact

- Edita: `docs/Tesis/v10 (IA)/paper/sections/{03-estado-del-arte,08-discusion,07-resultados,01-introduccion,12-anexos}.tex`, `docs/Tesis/v10 (IA)/Bibliography_base.bib` y `docs/Tesis/Correcciones/dictamen-correcciones.md` (trazabilidad del hash).
- No toca: codigo de aplicacion (`App/Backend`, `App/Frontend`, `n8n/`), numeros canonicos (`docs/Tesis/Correcciones/numeros-canonicos.md`), las cinco cadenas de categoria, figuras, `evaluation/`, `CHANGES.md`.
- Presupuesto de paginas: criterio duro. La tesis MUST permanecer en <= 101 paginas. REC 2 agrega prosa; REC 1 es neutral/minima; REC 3 agrega entradas `.bib` y un `\parencite`. El conteo neto de paginas no debe superar 101.
- Los tags `v1.0.0`/`v1.0.1` NO se mueven; se crea un tag anotado NUEVO `v1.1.0` (ver design D5).
- Dependencia: este change REQUIERE que `c-122-migrar-tesis-a-v10` este aplicado (crea `docs/Tesis/v10 (IA)/`).

## Rollback

Revertir los archivos `.tex` y `.bib` afectados con `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/..."` y recompilar el PDF. Si el tag `v1.1.0` ya se publico, eliminarlo tambien (`git tag -d v1.1.0` y `git push origin :refs/tags/v1.1.0`) para no dejar una etiqueta sobre una fuente revertida. Los tags `v1.0.0`/`v1.0.1` no se tocan.

## Success Criteria

- [ ] Las tres observaciones residuales del dictamen quedan cerradas en el PDF compilado.
- [ ] El PDF compila sin errores fatales y su total es <= 101 paginas.
- [ ] `verify_citations` reporta cero citas huerfanas y cero entradas sin usar tras agregar las tres entradas `@online`.
- [ ] No se altera ningun numero canonico, las cinco cadenas de categoria, las figuras ni `evaluation/`, y los tags `v1.0.0`/`v1.0.1` permanecen en sus commits.
- [ ] El tag anotado `v1.1.0` existe, apunta al commit de cierre y esta publicado en `origin`.
