# Tareas — c-147 compactacion-y-release-v1-2-2

## 1. Verificacion de la compactacion aplicada (Parte A)

- [ ] 1.1 Confirmar el commit `8c0cf6d` y su contenido con `git show --stat 8c0cf6d`; verificar que toca `paper/main.tex`, `paper/preambles/preamble.tex`, `paper/sections/06-implementacion.tex` y los artefactos de compilacion versionados de `paper/` (incluido `main.pdf`), y nada mas. Verificacion: el conjunto de archivos coincide
- [ ] 1.2 Medir el PDF de la rama: `pdfinfo "docs/Tesis/v10 (IA)/paper/main.pdf" | grep Pages` y `grep -n "contentsline {section}{Anexos}" main.toc`; verificar 104 totales, 96 de cuerpo y 8 de anexos. Verificacion: 104 / 96 / 8
- [ ] 1.3 Verificar que no se removio contenido ni quedo referencia colgada: `grep -c "begin{lstlisting}" sections/12-anexos.tex` y `grep -n "lst:validar-gemini" sections/12-anexos.tex` (el listado del Anexo H presente y su referencia resuelta); `grep -ci "undefined" main.log` = 0 y `grep -c "^!" main.log` = 0. Verificacion: sin contenido removido y sin referencias colgadas
- [ ] 1.4 Registrar la fila de la compactacion (111 -> 104) en el libro mayor de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`. Verificacion: la fila figura con total, cuerpo y anexos

## 2. Reconciliacion de la regla de tope de paginas (Parte B)

- [ ] 2.1 Agregar en `docs/Tesis/Correcciones/dictamen-correcciones.md` (G0.1) una entrada de actualizacion fechada con la regla real: metrica = **total del PDF**, valor = **100**, fuente = **exigencia de la catedra**, fecha de registro y el **exceso de +4 honrado y defendido**; sin reescribir la entrada provisional previa. Verificacion: los cuatro campos y el exceso figuran en la seccion
- [ ] 2.2 Agregar al libro mayor la fila de la compactacion y la fila de la release `v1.2.2`. Verificacion: ambas filas figuran con total, cuerpo y anexos
- [ ] 2.3 Reescribir en el delta de `tesis-document` (ya redactado) el requisito `Presupuesto de páginas preservado` con la regla reconciliada, la prohibicion de quitar contenido y la de dejar referencias colgadas; verificar `openspec validate c-147-compactacion-y-release-v1-2-2 --strict`. Verificacion: el change valida estricto
- [ ] 2.4 Al archivar, sincronizar el delta a `openspec/specs/tesis-document/spec.md` y verificar `openspec validate --specs --strict --no-interactive`. Verificacion: los specs validan estrictos

## 3. Cierre de las tareas pendientes de c-140 (Parte C)

- [ ] 3.1 Tarea 3.8 de c-140: correr la red de seguridad completa del backend (subconjunto SQLite, subconjunto de integracion PostgreSQL contra la base desechable, `ruff check`, los preflights de costo y la suite de `evaluation/`) y registrar el conteo. Verificacion: todo en verde, sin fallas bloqueantes; el conteo se registra en la seccion c-140 del registro
- [ ] 3.2 Tarea 3.9 de c-140: agregar la seccion "Politica de reintento del tramo de alta (c-140)" a `docs/n8n-workflow-guide.md` con nodos, valores (`maxTries`, `waitBetweenTries`, `timeout`), presupuesto de peor caso frente a `EXECUTIONS_TIMEOUT`, comportamiento tras agotar intentos, clave de idempotencia, efecto de reintentar un 401 del login sobre el bloqueo por cuenta y como desbloquear, espera fija (no exponencial) y procedimiento de reimportacion (requisito `N8N-DOC-007`). Verificacion: `grep -n "c-140" docs/n8n-workflow-guide.md` encuentra la seccion; los valores coinciden con `n8n/workflow.json`; `test_c33_cost_guard_wiring.py` en verde
- [ ] 3.3 Tarea 3.10 de c-140 (CP5): registrar la reimportacion del workflow en la instancia N8N operativa como **ejecutada por el equipo**, no por el agente. Verificacion: la tarea 3.10 queda marcada con esa justificacion y la instancia no se toco
- [ ] 3.4 Marcar 3.8, 3.9 y 3.10 en `openspec/changes/c-140-endurecimiento-tecnico-tls-reintentos-e2e/tasks.md`; verificar con `grep -c "^- \[x\]"`. Verificacion: 73/73 tareas de c-140

## 4. Release `v1.2.2` (Parte D, patron C1/C2 de c-141 y c-145)

- [ ] 4.1 C1 (fuente): en `sec:anexo-repositorio` (`12-anexos.tex`) el tag `v1.2.1` pasa a `v1.2.2` y se retira la linea del hash de `v1.2.1`; `Gomez2026_repositorio` (`Bibliography_base.bib`) pasa a la version `1.2.2`. Verificacion: `grep -n "v1.2.2" 12-anexos.tex` y `grep -n "1.2.2" Bibliography_base.bib`; ningun hash de `v1.2.1` restante en el Anexo B
- [ ] 4.2 Recompilar en `texlive-thesis` (`latexmk main.tex`) y verificar: 0 errores fatales, 0 referencias o citas indefinidas, 0 etiquetas duplicadas, `verify_citations.py` PASS, tope (total 104, exceso +4 honrado) y portada de una pagina. Verificacion: invariantes verdes y ledger 104 / 96 / 8
- [ ] 4.3 Crear el commit C1 (`docs(tesis): integrar c-146 y c-140 y publicar v1.2.2 (c-147)`) con las ediciones de 4.1 y los artefactos recompilados. Verificacion: `git status --short` limpio y `git show --stat HEAD`
- [ ] 4.4 Crear el tag anotado `v1.2.2` sobre C1 (checkpoint **HIGH**: requiere confirmacion explicita del usuario): `git tag -a v1.2.2 -m "..."`; verificar `git cat-file -t v1.2.2` = `tag` y `git rev-parse v1.2.2^{commit}` = C1. Verificacion: tag anotado sobre C1
- [ ] 4.5 C2: agregar en el Anexo B el hash completo de 40 caracteres de `git rev-parse v1.2.2^{commit}` y la nota "Trazabilidad `v1.2.2`" en el registro; recompilar; commit C2. Verificacion: el hash de 40 caracteres figura una vez en `12-anexos.tex` y una vez en la nota
- [ ] 4.6 Push de la rama y del tag (checkpoint **HIGH**: con confirmacion explicita del usuario) y abrir el PR a `main`, integrando con **merge commit** (nunca squash ni rebase). Verificacion: `git ls-remote --tags origin v1.2.2` devuelve el tag; el PR existe
- [ ] 4.7 Verificar, tras el merge, `git merge-base --is-ancestor v1.2.2 origin/main` (verdadero) y que los tags `v1.0.0`..`v1.2.1` siguen en sus hashes. Verificacion: tag alcanzable y tags previos inmutables

## 5. Archivo y cierre documental (Parte E)

- [ ] 5.1 Archivar `c-146-completar-metricas-trabajos-previos` y `c-140-endurecimiento-tecnico-tls-reintentos-e2e` (`openspec archive <change> -y`), sincronizando sus delta specs. Verificacion: `openspec list --json` ya no los reporta activos y `openspec validate --specs --strict --no-interactive` sigue pasando
- [ ] 5.2 Cerrar la tarea 2.9 de c-141 (archivo de los changes de familia pendientes). Verificacion: 2.9 marcada o justificada
- [ ] 5.3 Actualizar `CHANGES.md` con la FASE 40 (compactacion y release `v1.2.2`) y la release vigente. Verificacion: `grep -n "v1.2.2" CHANGES.md` con coincidencias y sin changes activos de la familia integrada
- [ ] 5.4 Verificacion final: `openspec validate c-147-compactacion-y-release-v1-2-2 --strict` (o su fase archive). Verificacion: sin errores
