## Context

Ver `proposal.md` (Why). Este change cierra la integracion que la release `v1.2.1` (PR #43, merge `13e9281e3f41ec990584e0c6b62e7034c13e422f`) dejo pendiente: los changes `c-146-completar-metricas-trabajos-previos` (22/23) y `c-140-endurecimiento-tecnico-tls-reintentos-e2e` (70/73) estan aplicados en esta rama y todavia no fusionados a `main`, y la tesis necesita la compactacion de paginas que los vuelve defendibles frente al tope de la catedra. Es un change de integracion de release, hermano de c-141 (integracion de la familia del dictamen y publicacion de `v1.2.0`) y de c-145 (correccion factual y publicacion de `v1.2.1`). Gobernanza: **MEDIUM** en las ediciones editoriales; **HIGH** en dos puntos: el dominio "eliminacion de contenido" de la compactacion (Parte A, ya aplicada en `8c0cf6d`) y la publicacion del tag, el push y el PR (Parte D, acciones publicas).

Estado verificado (solo lectura, en esta rama `change/c-147-compactacion-y-release-v1-2-2`, cortada de `change/c-140-endurecimiento-tecnico` que ya incluye `c-146`):

- **Compactacion aplicada.** El commit `8c0cf6d` ("docs(tesis): compactar el documento de 111 a 104 paginas (c-147)") toca `paper/main.tex`, `paper/preambles/preamble.tex`, `paper/sections/06-implementacion.tex` y los artefactos de compilacion de `paper/` (incluido `main.pdf`). El borrador medido era 111 total / 102 cuerpo / 9 anexos; la compactacion deja 104 total / 96 cuerpo / 8 anexos. El exceso es +4 sobre el tope de 100 sobre el total, sostenido y defendido por los autores.
- **Regla de tope mal registrada.** `docs/Tesis/Correcciones/dictamen-correcciones.md` G0.1 registra la "rama (b)" (`cuerpo sin anexos <= 100, anexos sin limite`, fuente "Decision del equipo") como confirmada por el usuario el 2026-10-26. La regla real es del otro lado: **total <= 100**, y la fuente es la **catedra**. El libro mayor de paginas de esa seccion termina en la fila "release v1.2.0 (C2)" (109 / 100 / 9) y no tiene fila de `v1.2.1`, de `c-146`/`c-140` ni de la compactacion.
- **Spec abierto divergente.** `openspec/specs/tesis-document/spec.md` `Presupuesto de páginas preservado` declara "total <= 100 medido con `pdfinfo`". El delta de c-141 (aun sin archivar) lo reescribe como "101 sobre el total" con margen de renegociacion. Ninguna de las dos versiones refleja la regla real.
- **c-140 pendiente.** `openspec/changes/c-140-endurecimiento-tecnico-tls-reintentos-e2e/tasks.md` tiene 70/73: pendientes 3.8 (regresion completa de backend), 3.9 (seccion "Politica de reintento del tramo de alta (c-140)" en `docs/n8n-workflow-guide.md`, requisito `N8N-DOC-007`) y 3.10 (CP5, reimportacion del workflow en la instancia operativa, que ejecuta el equipo). El requisito `N8N-DOC-007` ya esta declarado en el delta de c-140 y se sincroniza cuando c-140 se archive.
- **c-146 aplicado.** Modifica `tesis-document` (`Completitud de las metricas de la tabla de trabajos academicos`) y agrega `Registro de procedencia de la extraccion de c-146`. Su delta se sincroniza al archivar.
- **Tags.** Publicados y anotados en `origin`: `v1.0.0` = `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` = `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0`, `v1.1.0` = `7103b649d8c4f51737ad6ad4095dad22c9406400`, `v1.1.1` = `4160d84286623b073d2904353e6f9163ae211de7`, `v1.2.0` = `a49d035c67b32ae17e633ec04b09ecdd2781aac6`, `v1.2.1` = `509ffff105c21fed0c07cbf9a46245ba6c53e0e1`. No existe `v1.2.2`. El patron C1/C2 se observa en c-141 (`a49d035` + `3bd0a53`) y c-145 (`509ffff` + `fc579d8`).
- **Anexo B y `.bib` hoy.** `12-anexos.tex:27` declara el tag `v1.2.1` sobre el commit definitivo; `Bibliography_base.bib:810` (`Gomez2026_repositorio`) consigna la version de la release.
- **Entorno de compilacion de registro.** Imagen Docker `texlive-thesis` (XeLaTeX + biber + fuentes Microsoft core), adoptada por la familia y usada por c-145. Comando: `MSYS_NO_PATHCONV=1 docker run --rm -v "<repo>/docs/Tesis/v10 (IA):/work" -w /work/paper texlive-thesis latexmk main.tex`.

## Goals / Non-Goals

**Goals:**

- Una sola version integrada, compilada, verificada y etiquetada (`v1.2.2`) que incorpora `c-146`, `c-140` y la compactacion, sin perder contenido cientifico.
- Una regla unica y correcta de tope de paginas (total <= 100, fuente catedra) registrada en un solo lugar, con el exceso honrado y defendido.
- Cerrar las tareas pendientes de c-140 y archivar los changes integrados.
- Trazabilidad de la release (`tag`, hash, merge commit) y de la regla de paginas.

**Non-Goals:**

- No reabrir el contenido de c-146 ni de c-140: el texto de la tesis ya esta aplicado; solo se cierran tareas de verificacion y documentacion.
- No rehacer la compactacion: `8c0cf6d` ya la aplico; este change la documenta y la reconcilia con la regla.
- No realizar mediciones nuevas ni re-ejecutar el clasificador, N8N o Gemini.
- No tocar el codigo de aplicacion, `n8n/workflow.json`, `data/` ni los numeros canonicos `vigente`.
- No mover, recrear ni borrar los tags `v1.0.0` a `v1.2.1`.

## Decisions

### D1 - Reparto de partes y propiedad

| Parte | Contenido | Estado en propose | Gobernanza |
|---|---|---|---|
| A | Compactacion 111 -> 104 y no-remocion/dangling refs | YA APLICADA (`8c0cf6d`); se documenta | HIGH (dominio "eliminacion de contenido"), mitigada |
| B | Reconciliacion de la regla de tope en G0.1 y en el spec | PENDIENTE | MEDIO |
| C | Cierre de 3.8 y 3.9 de c-140; 3.10 como tarea del equipo | PENDIENTE | MEDIO |
| D | Release `v1.2.2` (C1/C2, tag, push, PR) | PENDIENTE | HIGH |
| E | Archivo de c-146 y c-140 y cierre de c-141 2.9 | PENDIENTE | BAJO |

La Parte A no se vuelve a ejecutar: su commit ya existe. Las tareas de la Parte A en `tasks.md` son de verificacion y de registro, no de edicion.

### D2 - Regla de tope de paginas reconciliada

La regla real es: metrica = **total del PDF**; valor = **100**; fuente = **exigencia de la catedra**; fecha de registro; y un **exceso de +4 honrado y defendido** (104 total; cuerpo 96; anexos 8). Se registra en la seccion de presupuesto de paginas de `dictamen-correcciones.md` (G0.1), sin reescribir la entrada provisional previa: se agrega una entrada de actualizacion fechada, como ya se hizo con la "rama (b)". El requisito `Presupuesto de páginas preservado` del spec se reescribe a esta regla y agrega la prohibicion de quitar contenido o dejar referencias colgadas.

**Alternativas consideradas:** (a) dejar la regla como "cuerpo <= 100" (la mal registrada): contradice la consigna real y no explica el exceso; (b) declarar total <= 104 sin fuente: oculta que el limite real es 100 y que hay un exceso defendido. Se adopta la regla con exceso declarado.

### D3 - Tope defendido: documentar el exceso, no esconderlo

El techo practico de los autores es del orden de 110-115 paginas totales, y la decision de sostener 104 es deliberada. El registro SHALL declarar la magnitud del exceso (+4), su fecha y la decision de defenderlo ante la catedra. Esto evita dos errores: presentar 104 como si cumpliera 100 sin exceso, o compactar mas alla de lo que la catedra tolera sacrificando contenido.

### D4 - Cierre de c-140 (Parte C)

- **3.8 (regresion):** correr la red de seguridad completa del backend (`pytest` con el subconjunto SQLite y el de integracion PostgreSQL contra la base desechable, `ruff check`, `pytest scripts/preflight`, `pytest scripts/dry_run`, y la suite de `evaluation/`) y registrar el conteo. Es la red de seguridad declarada por c-140; su evidencia se anexa a la seccion c-140 de `dictamen-correcciones.md`.
- **3.9 (documentacion):** agregar la seccion "Politica de reintento del tramo de alta (c-140)" a `docs/n8n-workflow-guide.md` con nodos, valores (`maxTries`, `waitBetweenTries`, `timeout`), presupuesto de peor caso frente a `EXECUTIONS_TIMEOUT`, comportamiento tras agotar intentos, clave de idempotencia, efecto de reintentar un 401 del login sobre el bloqueo por cuenta y como desbloquear, espera fija (no exponencial) y procedimiento de reimportacion. Es el requisito `N8N-DOC-007` de c-140.
- **3.10 (CP5):** la reimportacion del workflow en la instancia N8N operativa la ejecuta el equipo. El agente la registra como tal y NO toca la instancia. La tarea se marca cerrada en el sentido de "registrada como accion del equipo".

### D5 - Release `v1.2.2` (Parte D)

- **Nombre:** `v1.2.2`. Incremento de parche: integra changes ya aplicados y una compactacion, sobre la misma estructura documental de `v1.2.1`.
- **C1:** en `sec:anexo-repositorio` el tag `v1.2.1` pasa a `v1.2.2` y se retira la linea del hash de `v1.2.1`; el titulo de `Gomez2026_repositorio` pasa a la version `1.2.2`, conservando la etiqueta de version; se recompila en `texlive-thesis` y se verifica el conteo y los invariantes de compilacion.
- **Tag:** `git tag -a v1.2.2 -m "..." <C1>`; `git cat-file -t v1.2.2` = `tag`. Push del tag y de la rama con confirmacion del usuario (checkpoint HIGH).
- **C2:** linea con el hash completo de 40 caracteres en el Anexo B y nota "Trazabilidad `v1.2.2`" en "## Notas" del registro; recompilacion y verificacion.
- **Integracion:** PR a `main` con **merge commit** (nunca squash ni rebase), de modo que el commit etiquetado quede en la historia de `main`; despues del merge, `git merge-base --is-ancestor v1.2.2 origin/main` verdadero.

**Alternativa considerada:** etiquetar en `main` despues del merge. Se descarta: el commit de merge lo crea quien mergea, puede incluir trabajo posterior a la verificacion y rompe la continuidad con `v1.0.0`..`v1.2.1`, etiquetados sobre el commit verificado.

### D6 - Archivo (Parte E)

Se cierra la tarea 2.9 de c-141 archivando los changes de familia que sigan pendientes, entre ellos `c-146` y `c-140`; al archivar, sus delta specs se sincronizan en `openspec/specs/`. `c-135` permanece abierto si su tarea 5.2 (fechas de los autores) sigue sin fuente primaria, y se deja constancia. El archivo va en un commit propio (`chore(openspec): archivar c-146 y c-140 (c-147)`), posterior a la publicacion del tag y del PR.

### D7 - No reejecutar la compactacion

El commit `8c0cf6d` ya aplico la compactacion. Las verificaciones de la Parte A consisten en confirmar el conteo (104 / 96 / 8) y en comprobar que no se removio contenido cientifico ni quedo una referencia colgada (en particular, que el `lstlisting` del Anexo H esta presente y su referencia resuelve). No se altera `8c0cf6d`.

## Risks / Trade-offs

- [La regla reconciliada no coincide con una exigencia formal de la catedra] -> Se registra lo que el equipo declara como fuente catedra con fecha; si la catedra entrega un valor distinto, se corrige la fila en la misma seccion con una entrada de actualizacion, sin reescribir la historia.
- [El exceso de +4 no es aceptado en el reexamen] -> El registro lo declara y lo defiende; si se exigiera el cumplimiento estricto de 100, se activa la rama de compactacion adicional (palancas de formato ya catalogadas en c-141 D5, con checkpoint HIGH) o se documenta la imposibilidad con la catedra.
- [La compactacion deja una referencia colgada por el `lstlisting` del Anexo H] -> Verificacion de la Parte A: el listado esta presente y su referencia resuelve (`grep` del entorno `lstlisting` y compilacion con cero indefinidas).
- [c-140 no cierra limpio (3.8 en rojo)] -> Ninguna falla bloqueante se marca cerrada; si aparece una falla preexistente del entorno, se registra como tal y se decide con el usuario si bloquea la release.
- [El tag queda fuera de `main`] -> Merge commit obligatorio y verificacion posterior con `git merge-base --is-ancestor`.
- [Se duplican ediciones con c-141 (aun sin archivar)] -> c-141 se archiva en la Parte E antes o junto con la release; el requisito de tope de paginas queda a cargo de c-147, que supersede la redaccion de c-141.

## Migration Plan

1. **Parte A (verificacion):** confirmar `8c0cf6d`, medir 104 / 96 / 8 y verificar ausencia de contenido removido y de referencias colgadas.
2. **Parte B:** reconciliar la regla en G0.1 y actualizar el libro mayor; reescribir el requisito de tope en el delta de `tesis-document`.
3. **Parte C:** correr 3.8, escribir 3.9 y registrar 3.10 en c-140; marcar las tareas.
4. **Parte D:** C1 (integrar y subir a `v1.2.2`), recompilar y verificar, tag anotado y push con confirmacion, C2 (hash), PR con merge commit.
5. **Parte E:** archivar `c-146` y `c-140` (sincronizar specs), cerrar c-141 2.9 y registrar en `CHANGES.md`.
6. **Rollback:** antes del tag, `git revert` y recompilar; despues del tag y antes de la entrega, borrar `v1.2.2` solo con confirmacion; despues de la entrega, publicar `v1.2.3`.

## Open Questions

- **OQ1:** confirmar con el usuario el valor exacto y la fecha de la exigencia de la catedra (100 sobre el total) y la procedencia textual de esa consigna, para citarla en G0.1.
- **OQ2:** confirmar si el exceso de +4 se sostiene tal cual en la entrega final o si, antes del tag, se aplica una compactacion adicional.
- **OQ3:** el nombre de la release (`v1.2.2`) o `v1.2.2-fix` si el jurado o la catedra piden una denominacion distinta.
