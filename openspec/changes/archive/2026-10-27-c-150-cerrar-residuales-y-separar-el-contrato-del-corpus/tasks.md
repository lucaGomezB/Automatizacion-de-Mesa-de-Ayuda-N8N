> Ejecucion en orden estricto. Rutas relativas a la raiz del repositorio. `CH` = `CHANGES.md`; `LEDGER` = `docs/Tesis/Correcciones/dictamen-correcciones.md`; `DIRDOC` = `docs/directorio-evidencia-cumplimiento.md`; `CORPUS` = `evaluation/corpus.py`; `DET` = `evaluation/deterministic_measurement.py`; `RUN` = `evaluation/run_evaluation.py`; `TCORPUS` = `evaluation/tests/test_corpus.py`. Ninguna tarea se marca `[x]` en la fase propose. W2 y W4 son ALTO: el autor revisa esos diffs antes del merge.

## 1. Red de seguridad y linea base

- [x] 1.1 Ejecutar `cd evaluation; pytest` y registrar la linea base (conteo passed). Registrar tambien `python3 -m pytest evaluation/tests/test_corpus.py -q` como suite focal de W3.
- [x] 1.2 Registrar el uso actual del loader: `rg -n "cargar_corpus_tolerante|cargar_corpus\(" evaluation/` y consignar los call sites (`RUN` lineas 36, 1418 y 1511; `DET` lineas 1014 y 1066).
- [x] 1.3 Registrar la linea base de emojis: barrido de U+2713 en `CH` y consignar las lineas afectadas (esperado: 197, 203, 208, 211, 214 y 351-359).
- [x] 1.4 Registrar la nota stale objetivo: `sed -n '2398p' CH` y la entrada que ya documenta el cierre de C-80 (`CH:2329`), como evidencia de que el texto de 2398 quedo desmentido.

## 2. W1 — corregir la nota stale de CHANGES.md (BAJO)

- [x] 2.1 En `CH`, linea 2398, corregir la afirmacion sobre la deuda residual de C-80 para que declare el cierre real (C-80 archivado 45/45 el 2026-10-21). Verificacion: `sed -n '2398p' CH` no afirma que la evidencia visual de C-80 siga pendiente.
- [x] 2.2 Conservar sin reescribir la entrada fechada que registra el cierre (`CH:2329`) y cualquier otra entrada historica sobre C-80. Verificacion: `git diff CH` no toca las entradas fechadas de archivo.

## 3. W5 — eliminar los emojis de CHANGES.md (BAJO)

- [x] 3.1 Marcas de verificacion en encabezados de gate/estado (lineas 197, 203, 208, 211 y 214, incluidas las apariciones inline junto a un id): REEMPLAZAR la marca por texto explicito (por ejemplo `COMPLETADO` en el encabezado y `(completado)` junto al id). No cambiar el sentido de la linea.
- [x] 3.2 Marcas de verificacion en items de scope ya completados (lineas 351-359): ELIMINAR la marca; la completitud ya la declara el encabezado "Estado: `[x]` completado" de la seccion.
- [x] 3.3 Verificacion: un barrido de U+2713 sobre `CH` no devuelve ninguna coincidencia; `git diff CH` no altera el texto mas alla del retiro/reemplazo de las marcas.

## 4. W2 — anotar tareas de rollback obsoletas en changes archivados (ALTO)

- [x] 4.1 En `openspec/changes/archive/2026-10-27-c-148-sincronizar-knowledge-base-y-docs-con-el-stack-vigente/tasks.md`, agregar tras el texto original de 9.1 la anotacion: ` — ANOTACION (2026-10-27, c-150 W2): la justificacion "no hay commits del change" quedo OBSOLETA. c-148 se commiteo en 3392012 y se fusiono en PR #53 (merge 6516f5f); la verificacion de rollback es MOOT. El texto original se conserva como evidencia historica.` No borrar el texto original ni cambiar el estado `[ ]`.
- [x] 4.2 En el mismo archivo, agregar tras el texto original de 9.2 la anotacion: ` — ANOTACION (2026-10-27, c-150 W2): depende de 9.1, que quedo MOOT por el merge de c-148 (commit 3392012, PR #53, merge 6516f5f). El texto original se conserva.` No borrar el texto original ni cambiar el estado.
- [x] 4.3 En `openspec/changes/archive/2026-10-27-c-149-actualizar-dependencias-y-endurecer-la-barrera/tasks.md`, agregar tras el texto original de 7.1 la anotacion: ` — ANOTACION (2026-10-27, c-150 W2): la justificacion "no hay commits del change" quedo OBSOLETA. c-149 se commiteo en f666316 y se fusiono en PR #55 (merge 4d9e072); la verificacion de rollback es MOOT. El texto original se conserva.` No borrar el texto original ni cambiar el estado.
- [x] 4.4 Verificacion: `git diff` de ambos `tasks.md` muestra solo texto agregado (lineas `+`), sin remociones ni cambios de casilla; el conteo de tareas de cada change no cambia.

## 5. W3 — separar el contrato del corpus (MEDIO, TDD estricto)

- [x] 5.1 RED: en `TCORPUS`, escribir pruebas que (a) cargan via `cargar_corpus()` un corpus con `tiempo_automatizado_s: null` y con el campo ausente y esperan exito con tiempos en `None`; (b) esperan que un `tiempo_manual_s: "n/a"` presente sea rechazado con `CorpusError`; (c) esperan que un campo de clasificacion ausente (`descripcion`) siga siendo rechazado. Ejecutar `python3 -m pytest evaluation/tests/test_corpus.py -q` y registrar los fallos (el loader estricto aun exige los tiempos).
- [x] 5.2 GREEN: en `CORPUS`, separar `CAMPOS_CASO_REQUERIDOS` (contrato de clasificacion: `id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales`) de los campos de tiempo; hacer que `_parsear_caso` lea los tiempos como opcionales (`None` si ausentes o `null`) conservando `_a_float` estricto para los PRESENTES. `cargar_corpus()` valida ambos contratos. Verificar `python3 -m pytest evaluation/tests/test_corpus.py -q` en verde.
- [x] 5.3 Colapsar el loader tolerante: eliminar `cargar_corpus_tolerante` de `DET` (lineas 1014-1058) y hacer que `_cargar_corpus_real` (lineas 1061-1066) use `cargar_corpus`. Actualizar los call sites en `RUN` (lineas 36, 1418, 1511) para que importen y usen `cargar_corpus`. Verificacion: `rg -n "cargar_corpus_tolerante" evaluation/` sin coincidencias.
- [x] 5.4 TRIANGULATE: agregar casos con el corpus real (`data/corpus_evaluacion_pseudonimizado.json`, 56 casos con `tiempo_automatizado_s` nulo), un corpus mixto y el borde `tiempo_manual_s: 0` (valido). Ejecutar `python3 -m pytest evaluation/tests/test_corpus.py -q` en verde.
- [x] 5.5 REFACTOR: extraer el parseo de tiempos a un helper puro si la duplicacion lo justifica; ejecutar la suite focal tras cada paso. Verificacion final: `cd evaluation; pytest` completo en verde, sin regresiones respecto de 1.1.

## 6. W4 y confirmaciones del autor (ALTO)

- [x] 6.1 En `DIRDOC` (seccion 4, lineas ~70-83), registrar con precision el estado de C-60: 33/33; la tarea 7.4 esta `[x]` porque su contenido es registrar la revision HIGH como PENDIENTE; el item genuinamente pendiente es la aprobacion HIGH del autor para pasar de datos sinteticos a reales. Verificacion: el documento declara la aprobacion como PENDIENTE y no como concedida.
- [x] 6.2 En `LEDGER`, registrar (item 9, BAJO) la aprobacion del autor a la redaccion final de `docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex` (T1/T2) y `09-conclusiones.tex` (T10-T13 + parrafo de apertura), con fecha 2026-10-27, sin editar los `.tex`.
- [x] 6.3 En `LEDGER`, ratificar las decisiones provisionales del item 8 (fecha 2026-10-27) agregando una entrada/tabla fechada sin reescribir las entradas provisionales: G0.2/OQ3 (`:724`), G0.3/OQ4 (`:759`, `:772`), G0.4/OQ2 (`:774`, notando que quedo moot porque v1.2.1/v1.2.2 ya se publicaron despues de v1.2.0), OQ5 (`:1086`, `:1089`, notando que el valor FORCE-ESCALATE puede faltar y se registra como confirmado-a-proveer), c-131 Q1-Q3 (`:1223-1225`) y c-142 bloque-2 OQ3/OQ4 (`:1356-1357`). Verificacion: cada item remite a su linea original y el texto provisional previo se conserva.
- [x] 6.4 En `LEDGER`, marcar EXPLICITAMENTE como PENDIENTES, sin registrar autorizacion: G0.7a/OQ7a (ablacion paga del prompt, 138 invocaciones) como "pendiente de resolucion del orquestador/autor"; y OQ6 (`usuario_final` valida su propio incidente, dominio CRITICAL) como "pendiente de resolucion". Verificacion: `rg -n "G0.7a|OQ7a" LEDGER` y `rg -n "OQ6" LEDGER` no devuelven una autorizacion.

## 7. Cierre documental y validacion

- [x] 7.1 Agregar en `CH` la entrada C-150 con alcance (W1-W5 y confirmaciones), governance (W2/W4 ALTO; W3 MEDIO; W1/W5/confirmaciones BAJO) y el estado de verificacion. Verificacion: `rg -n "C-150" CH`.
- [x] 7.2 Ejecutar `openspec validate c-150-cerrar-residuales-y-separar-el-contrato-del-corpus --strict` y verificar que pasa.
- [x] 7.3 Barrido final: ningun U+2713 en `CH`; ningun texto historico reescrito; `cd evaluation; pytest` en verde.
- [x] 7.4 Confirmar que no se marco ninguna tarea `[x]` durante la fase propose.

## 8. Rollback documentado

- [ ] 8.1 `git revert` de los commits del change restaura `CH`, el ledger, `DIRDOC` y el contrato previo del corpus (tiempos obligatorios y `cargar_corpus_tolerante`); los call sites vuelven a la carga tolerante. No hay tag ni release que deshacer. (NO EJECUTADA todavia; se documenta como plan.)
- [ ] 8.2 Verificacion pendiente para el apply: al revertir, `cd evaluation; pytest` debe volver a la linea base de 1.1.
