# Proposal: c-80 — Forma y evidencia visual

## Why

La auditoria de la tesis (Bloque 4 — Forma y evidencia visual, items 26-32) detecto
un conjunto de defectos de forma y de respaldo visual que degradan la calidad
academica del documento: 50 errores ortograficos (formas `diseñó`, `desarrolló`,
`completó` y `aquéllos`, mas tildes faltantes en portada y titulos de seccion), una
sola figura en toda la tesis frente a las 8 que el documento requiere, siete anexos
(A-G) meramente descriptivos sin contenido embebido, composicion de tablas
inconsistente, aproximadamente 900 palabras duplicadas entre capitulos, una
acotacion obsoleta sobre N8N~1.62 en dos lugares, y afirmaciones valorativas sin
respaldo en la discusion y las conclusiones. Corregir esto es un requisito de
calidad editorial (governance BAJO) que no altera la arquitectura ni el codigo del
sistema; opera exclusivamente sobre el arbol LaTeX `docs/Tesis/v9 (IA)/paper/`.

## What Changes

### Grupo Forma y evidencia visual (F1-F7) — plan de auditoria items 26-32

| Id | Item del plan | Correccion |
|----|---------------|-----------|
| F1 | 26 | Correcta sustitucion contextual de las 50 apariciones erroneas de `diseñó`->`diseño`, `desarrolló`->`desarrollo` (excluyendo los 2 verbos legitimos), `completó`->`completo` y `aquéllos`->`aquellos`; tildes faltantes en portada y titulos de seccion. |
| F2 | 27 | Producir e incrustar las 8 figuras faltantes (despliegue, secuencia, ER, flujo N8N, panel admin, dashboard, boxplot de tiempos, matriz de confusion) en sus ubicaciones naturales. |
| F3 | 28 | Convertir los 7 anexos (A-G) de descriptivos a anexos con contenido real embebido e incorporar el Anexo H (prompt de Gemini) hoy ausente. |
| F4 | 29 | Unificar la composicion de las 9 tablas: fuente (`\small`) consistente y columnas de prosa en `\raggedright`. |
| F5 | 30 | Eliminar/reescribir las duplicaciones de ~900 palabras (pares 1.1/2.1, 5.3/6.3 y 8.1/9.1). |
| F6 | 31 | Retirar la acotacion obsoleta "version 1.62 no disponible en Docker Hub" y reconciliar la version de N8N con la version real (2.11.2). |
| F7 | 32 | Retirar o rebajar las afirmaciones valorativas sin respaldo de 8.1 y 9.1 a formulaciones sostenidas por la evidencia de 7 (resultados). |

Detalle de cada item:

- **F1 — Ortografia**: la sustitucion MUST ser **contextual**, no un reemplazo ciego
  global. `desarrolló` tiene 11 apariciones, pero 2 son **verbos legitimos** que NO
  deben tocarse (`00-resumen.tex:11` "el estudio se desarrolló", `06-implementacion.tex:87`
  "el frontend se desarrolló"). Las formas sustantivas (`el desarrolló`, `del desarrolló`,
  `de desarrolló`) pasan a `desarrollo`. La portada (`00-portada.tex`) y los titulos
  de seccion carecen de tildes ("TECNOLOGICA", "Programacion", "Automatizacion",
  "Republica", `\section{Introduccion}`, etc.).
- **F2 — Figuras**: la unica figura existente es `05-arquitectura.tex:31-36`
  (`figures/arquitectura_sistema.png`); `figures/` solo contiene ese PNG y `tables/`
  esta vacio. Las 8 figuras se ubican en: 1->cap5/Anexo A, 2->cap5/Anexo A,
  3->5.6/Anexo C, 4->6.3/Anexo E, 5-6->6.8, 7->7.1, 8->7.2. Existen fuentes Mermaid
  sin embeber (`docs/diagrams/despliegue.md`, `secuencia.md`, `componentes.md`).
- **F3 — Anexos**: cada anexo A-G debe incorporar contenido real (figura, tabla,
  listado o bloque de codigo) en lugar de describirlo; el Anexo H
  (`docs/anexo_h_prompt_gemini.md`, H.1-H.7) MUST incorporarse como seccion.
- **F4 — Tablas**: 4 tablas usan `\small` (`tab:comparativa`, `tab:variables`,
  `tab:entidades`, `tab:errores`) y 5 no (`tab:capas`, `tab:api`, `tab:tiempos`,
  `tab:matriz`, `tab:metricas`). Ademas, la Tabla~1 (`03-estado-del-arte.tex:36`)
  usa columnas `p{}` planas y la Tabla~3 (`05-arquitectura.tex:12`) no tiene su
  primera columna en `raggedright`.
- **F5 — Duplicaciones**: par 1.1/2.1 (`01-introduccion.tex:8,10` vs
  `02-marco-teorico.tex:10,12`, material Galup2009 casi verbatim); par 5.3/6.3
  (`05-arquitectura.tex:44` vs `06-implementacion.tex:39,41`, mas "camino de
  clasificacion unico" repetido en `05:60` y `06:44`); par 8.1/9.1
  (`08-discusion.tex:8,10,14` vs `09-conclusiones.tex:12,24`).
- **F6 — N8N 1.62**: `05-arquitectura.tex:21` y `06-implementacion.tex:10` afirman
  que "la version 1.62 no se encuentra disponible en Docker Hub", lo que contradice
  `12-anexos.tex:37` y `docs/diagrams/despliegue.md` ("N8N 2.11.2").
- **F7 — Afirmaciones valorativas**: en `08-discusion.tex:8-16` ("superan
  ampliamente", "valida la hipotesis subsidiaria", "consecuencia deseable",
  "materializa el esquema human in the loop buscado", "garantia metodologica que no
  todos los trabajos... documentan") y en `09-conclusiones.tex:6-18` ("cumplido
  satisfactoriamente", "supero con holgura", "no deja espacio para la duda
  razonable", "resultado poco frecuente", "trasciende lo meramente estadistico",
  "activo que excede").

### Orden de aplicacion (dependencia dura)

Este change comparte archivos con c-76 (numeros en 08/09 y ventana en 11), c-77
(estadistica) y c-78 (03/08 y bibliografia). MUST aplicarse **despues** de
c-76/c-77/c-78 para no pisar sus reescrituras. Ver `design.md` para el detalle.

## Capabilities

### New Capabilities

- None

### Modified Capabilities

- `tesis-document`: se modifican los requisitos de formateo de tablas (fuente y
  composicion uniformes) y de eliminacion de patrones de escritura; se agregan
  requisitos de correccion ortografica y de portada, evidencia visual (figuras
  embebidas), anexos con contenido real, ausencia de duplicaciones sustantivas,
  consistencia de la version de N8N y respaldo evidenciario de las afirmaciones.
  No se modifica `evaluation-framework`.

## Impact

- `docs/Tesis/v9 (IA)/paper/sections/00-portada.tex`, `00-resumen.tex`,
  `01-introduccion.tex`, `02-marco-teorico.tex`, `03-estado-del-arte.tex`,
  `04-marco-metodologico.tex`, `05-arquitectura.tex`, `06-implementacion.tex`,
  `07-resultados.tex`, `08-discusion.tex`, `09-conclusiones.tex`, `12-anexos.tex`
- `docs/Tesis/v9 (IA)/paper/figures/` (8 figuras nuevas)
- `docs/diagrams/` (fuentes Mermaid: despliegue, secuencia, componentes nuevos ER)
- `docs/anexo_c_esquema_bd.md`, `docs/anexo_f_corpus.md`, `docs/anexo_h_prompt_gemini.md`,
  `docs/openapi.json`, `n8n/workflow.json` (fuentes de contenido de anexos)
- `main.pdf` (se recompila despues en Overleaf, no en este repo)
- `openspec/specs/tesis-document/spec.md` (delta aplicado al archivar)

No se toca `App/**`. No se editan artefactos de c-76/c-77/c-78 ni `CHANGES.md`. No
se modifica `docs/Tesis/Correcciones/dictamen-correcciones.md`.

## Rollback Plan

`git checkout --` sobre los `.tex` y las figuras afectadas, o `git revert` del
commit del change. Los artefactos OPSX se descartan con el directorio del change.
Las figuras nuevas se eliminan de `paper/figures/`.

## Success Criteria

- [ ] Las 50 apariciones erroneas de las 4 formas quedan corregidas (los 2 verbos
      legitimos de `desarrolló` preservados); `rg` de control sin residuos.
- [ ] La portada y todos los titulos de seccion tienen las tildes correctas.
- [ ] Las 8 figuras existen en `paper/figures/` y estan embebidas via
      `\includegraphics`/`figure` en sus ubicaciones naturales.
- [ ] Los 7 anexos (A-G) contienen contenido real embebido (figura, tabla, codigo o
      listado) y el Anexo H esta incorporado como seccion.
- [ ] Las 9 tablas usan composicion uniforme (`\small` consistente y primera columna
      de prosa en `\raggedright`).
- [ ] No quedan parrafos duplicados entre 1.1/2.1, 5.3/6.3 ni 8.1/9.1.
- [ ] La acotacion de N8N~1.62 fue retirada y la version citada es consistente
      (2.11.2) en 5, 6 y el Anexo~E.
- [ ] Las afirmaciones valorativas sin respaldo de 8.1 y 9.1 fueron retiradas o
      rebajadas a formulaciones sostenidas por la evidencia de 7.
- [ ] `openspec validate c-80-tesis-forma-evidencia-visual --strict` pasa.
- [ ] `pdf` recompilado en Overleaf sin errores fatales (tarea posterior; no hay
      toolchain LaTeX local).
