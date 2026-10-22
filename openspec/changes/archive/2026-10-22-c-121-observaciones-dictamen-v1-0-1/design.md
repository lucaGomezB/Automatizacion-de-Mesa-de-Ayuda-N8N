## Context

El change cierra tres observaciones residuales del dictamen CONEAU 2026-10-22 sobre la tesis (ver `proposal.md` - Why) y publica la release `v1.1.0`. Es documental: edita unicamente LaTeX y el archivo bibliografico bajo `docs/Tesis/v10 (IA)/`, la version de trabajo creada por el change prerrequisito `c-122-migrar-tesis-a-v10`. Restricciones que condicionan el diseno:

- **Presupuesto de paginas <= 101** (criterio duro). REC 2 agrega prosa; REC 1 es neutral; REC 3 agrega entradas `.bib` (biblatex solo imprime las citadas) y un `\parencite`.
- **Numeros canonicos congelados** en `docs/Tesis/Correcciones/numeros-canonicos.md`; el texto nuevo no puede introducir valores fuera de esa tabla.
- **Sin fabricacion**: no se inventan cifras de precio (REC 3).
- **Tags existentes inmutables**: `v1.0.0` y `v1.0.1` no se mueven ni se recrean; la release de v10 se publica con un tag anotado NUEVO `v1.1.0` (ver D5).

Estado verificado de las fuentes (solo lectura):
- `03-estado-del-arte.tex:60` declara "cuatro dimensiones relevantes: tipo de despliegue, capacidad de clasificacion automatica, soberania sobre los datos y modelo de costos"; la tabla `tab:comparativa` (lineas 62-80) tiene exactamente cuatro columnas: Solucion, Despliegue, Clasificacion automatica, Modelo de costo. "Soberania sobre los datos" no es columna.
- `07-resultados.tex:136` (`subsec:reduccion-intervencion`) ya declara que "la etapa Gemini nunca devolvio una confianza inferior a 0,85", pero lo usa solo para justificar la no contraste.
- `01-introduccion.tex:68` menciona Zendesk Suite, Freshdesk y ServiceNow ITSM como "relevamiento propio ... consultada el 19-10-2026" sin `\parencite`.
- `Bibliography_base.bib` contiene el bloque c-120 con `DigitalOcean2026_pricing` y `Google2026_vertex_pricing` (lineas 525-541), ambos `@online` con `url`, `urldate = {2026-10-19}` y `note` de consulta.

## Goals / Non-Goals

**Goals:**

- Cerrar las tres observaciones residuales del dictamen v1.0.1 con el minimo cambio de prosa y `.bib` posible.
- Preservar el presupuesto de paginas (<= 101) y la neutralidad numerica.

**Non-Goals:**

- No se reabre ninguna de las siete recomendaciones del dictamen anterior (ya cerradas en c-120).
- No se agrega ninguna columna nueva a `tab:comparativa` (ver D1).
- No se agrega ninguna cifra de precio ni afirmacion comercial nueva (ver D3).
- No se agrega ninguna nota de trazabilidad de conteo bibliografico: la REC 4 original queda retirada por verificacion (ver D4).
- No se mueve ni se recrea ningun tag existente (`v1.0.0`, `v1.0.1`); solo se crea el tag nuevo `v1.1.0` (ver D5).
- No se toca codigo de aplicacion, numeros canonicos, las cinco cadenas de categoria, figuras ni `evaluation/`.
- No se ejecuta la migracion a v10 (es del change c-122, prerrequisito de este).

## Decisions

### D1 - REC 1: alinear la prosa a las columnas, no agregar una columna

Se ajusta el parrafo introductorio (`03-estado-del-arte.tex:60`) para que declare exactamente las cuatro dimensiones que la tabla tiene (Solucion, Despliegue, Clasificacion automatica, Modelo de costo), retirando "soberania sobre los datos" de la enumeracion de dimensiones. La soberania sobre los datos se conserva en la prosa circundante: ya aparece en la sintesis posterior a la tabla (`03-estado-del-arte.tex:82`, "despliegue autoalojado para resguardo de datos sensibles") y en `01-introduccion.tex:64`.

**Alternativa considerada:** agregar una quinta columna "Soberania sobre los datos". Se descarta porque obliga a poblar una celda por cada una de las cinco soluciones, introduce afirmaciones comerciales nuevas no citadas, ensancha la tabla (riesgo de desborde y de paginas netas) y contradice el objetivo de edicion minima que el propio dictamen sugiere ("una linea de texto").

### D2 - REC 2: hallazgo del gate ubicado en la discusion, con eco en resultados

El hallazgo se enuncia como resultado propio en `08-discusion.tex` (interpretacion), que es donde el dictamen pide la prominencia ("presentarlo explicitamente como hallazgo en la discusion"). Se agrega ademas una frase en `07-resultados.tex` (`subsec:reduccion-intervencion`) que reencuadre el dato ya presente como hallazgo positivo, sin duplicar el argumento. No se introducen numeros: se reutiliza el 0,85 (umbral de la etapa Gemini) y el 0,70 (umbral del gate), ambos ya en el documento y en `numeros-canonicos.md`.

**Alternativa considerada:** ubicarlo solo en resultados o solo en conclusiones. Se descarta: resultados ya declara el hecho pero sin valorizarlo, y las conclusiones son un cierre; la discusion es el lugar natural para interpretar el comportamiento del clasificador.

### D3 - REC 3: entradas `@online` con nota de documentacion, sin precios fabricados

Se agregan tres entradas `@online` (`Zendesk2026_help_desk`, `Freshdesk2026_platform`, `ServiceNow2026_itsm`) siguiendo el patron c-120 (`author` como entidad, `title`, `year = {2026}`, `url`, `urldate = {2026-10-19}`, `note`). Como no hay una figura de precio verificable y citable para las tres plataformas, la `note` declara la pagina de documentacion (capacidades/precios) y la prosa de `01-introduccion.tex:68` se mantiene como observacion de relevamiento propio, con el `\parencite` agregado al final de la mencion. El objetivo es formalizar la referencia, no afirmar cifras.

**Alternativa considerada:** reformular la mencion como observacion propia sin entradas (opcion que c-120 dejo abierta y que el dictamen califico de aceptable). Se descarta porque el dictamen v1.0.1 recomienda explicitamente completar la cobertura "de forma analoga a lo ya hecho para DigitalOcean y Google Cloud".

### D4 - REC 4 retirada: no existe discrepancia de conteo bibliografico

La REC 4 original proponia una nota de trazabilidad sobre una supuesta discrepancia de conteo (54 frente a 39). La verificacion directa del arbol de trabajo la desmiente:

- `grep -c "^@"` sobre `docs/Tesis/v10 (IA)/Bibliography_base.bib` = **56 entradas**.
- Historia git: 54 entradas antes de c-120 (`HEAD~5..HEAD~10`), 56 en HEAD; el delta de +2 corresponde exactamente a `DigitalOcean2026_pricing` y `Google2026_vertex_pricing` agregadas por c-120.
- El dictamen previo (54) era correcto; el "39" del dictamen v1.0.1 fue un error de conteo, ya rectificado con fe de errata en la seccion 9 del dictamen.

En consecuencia, **no hay discrepancia que trazar y la REC 4 queda retirada**: no se agrega ninguna nota al Anexo I ni se modifica `12-anexos.tex` por este motivo. El change cierra tres observaciones, no cuatro.

### D5 - Release v1.1.0: tag anotado sobre el commit de cierre de v10

La migracion a v10 (c-122) y el cierre de las tres observaciones (este change) constituyen la proxima version publicada de la tesis. Se publica con un tag anotado `v1.1.0` (secuencia previa: `v1.0.0` -> `v1.0.1`). Se sigue el patron C1/C2 de c-111:

- **C1:** `sections/12-anexos.tex` (`sec:anexo-repositorio`) reemplaza el tag `v1.0.1` por `v1.1.0`; el tag anotado `v1.1.0` se crea sobre el commit de cierre (que incluye las ediciones de REC 1-3 y el cambio de referencia).
- **C2:** un parrafo nuevo consigna el hash completo de 40 caracteres del commit etiquetado, y ese mismo hash se registra en `docs/Tesis/Correcciones/dictamen-correcciones.md`.

**Alternativa considerada:** un change dedicado de version/trazabilidad (patron c-111). Se descarta porque la release `v1.0.1` tambien se cerro dentro del ultimo change de contenido (c-120), y porque el tag debe apuntar al commit que cierra la migracion y las observaciones: separarlo obligaria a un commit adicional. El tag NO se crea hasta que c-122 y c-121 esten aplicados y el PDF recompilado.

## Risks / Trade-offs

- **[REC 2 agrega paginas]** -> Mitigacion: prosa acotada (una frase en resultados, un parrafo breve en discusion); REC 1 neutral; verificar el conteo de paginas tras compilar y, si supera 101, recortar el eco de resultados (mantener solo discusion).
- **[REC 3 agrega entradas .bib y podria imprimir referencias nuevas]** -> Mitigacion: las tres entradas se citan en `01-introduccion.tex` (dejan de ser "sin usar"); biblatex imprime solo las citadas; verificar con `verify_citations` y el conteo de paginas.
- **[Fabricacion de cifras de precio]** -> Mitigacion: D3 usa `note` de documentacion sin precios.

## Migration Plan

1. Verificar que el prerrequisito c-122 este aplicado (existe `docs/Tesis/v10 (IA)/` y los punteros activos resuelven a v10).
2. Aplicar las ediciones por archivo en el orden REC 1 -> REC 2 -> REC 3 (ver `tasks.md`).
3. Actualizar `12-anexos.tex` con el tag `v1.1.0` (C1) y recompilar el PDF con XeLaTeX (`latexmk -xelatex main.tex`); verificar ausencia de errores fatales, referencias indefinidas y el conteo de paginas (<= 101).
4. Ejecutar `verify_citations` (cero huerfanas, cero sin usar).
5. Crear y publicar el tag anotado `v1.1.0` (C1) y consignar el hash del commit etiquetado (C2) en `12-anexos.tex` y `docs/Tesis/Correcciones/dictamen-correcciones.md`.
6. Rollback: `git checkout <commit-previo> -- "docs/Tesis/v10 (IA)/..."` y recompilar. Los tags `v1.0.0`/`v1.0.1` no se tocan en ningun caso.

## Open Questions

Ninguna. La unica pregunta abierta previa (el conteo bibliografico de la REC 4) quedo resuelta: no existe discrepancia y la REC 4 se retiro (ver D4).
