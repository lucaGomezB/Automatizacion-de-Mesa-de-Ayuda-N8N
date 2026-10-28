## Context

Tras la FASE 42 (c-148, c-149 archivados el 2026-10-27) quedan cinco residuales documentales y un defecto de contrato del corpus. El registro del proyecto tiene una nota de estado stale (`CHANGES.md:2398`), 14 marcas de verificacion U+2713 en `CHANGES.md` (lineas 197-359, prohibidas por la regla dura de `AGENTS.md`), dos tareas de rollback de c-148 y una de c-149 sin ejecutar con una justificacion que dejo de ser cierta, y el registro de C-60 (33/33) y las confirmaciones del autor sin consolidar. Por separado, `evaluation/corpus.py` exige los tiempos como campos obligatorios (`CAMPOS_CASO_REQUERIDOS`, lineas 55-63) y por eso existe un loader tolerante duplicado (`evaluation/deterministic_measurement.py:1014 cargar_corpus_tolerante`) creado para los 56 casos con `tiempo_automatizado_s: null`.

## Goals / Non-Goals

**Goals:**

- Corregir la nota de estado stale de `CHANGES.md` sin reescribir las entradas historicas.
- Anotar con fecha las tres tareas de rollback obsoletas, conservando su texto original.
- Separar el contrato de clasificacion del de tiempos en `evaluation/corpus.py`, colapsar el loader tolerante en uno solo y actualizar los call sites, con TDD estricto.
- Registrar con precision el estado de C-60 y las confirmaciones del autor, dejando pendientes las decisiones no autorizadas.
- Dejar `CHANGES.md` sin emojis.

**Non-Goals:**

- No se modifica el codigo de `App/`, `n8n/` ni `docker-compose.yml`.
- No se relaja la estrictez de `_a_float` para los campos que valida: un tiempo presente y no numerico sigue siendo un error.
- No se reescribe ningun texto historico (entradas fechadas de `CHANGES.md`, tareas de changes archivados, entradas provisionales del ledger).
- No se concede ninguna aprobacion pendiente del autor (ni G0.7a/OQ7a ni OQ6).

## Decisions

**D1 — Una sola fuente de estado actual frente a registros historicos.** Mismo criterio ya establecido por c-148: un HECHO VIGENTE se corrige, un REGISTRO HISTORICO se rotula o se anota y no se falsifica. W1 corrige una afirmacion de estado actual (`CHANGES.md:2398`); las entradas fechadas que ya registran el cierre de C-80 (`CHANGES.md:2329`) quedan intactas. Alternativa descartada: borrar la nota stale (perderia la trazabilidad del cambio de estado).

**D2 — Anotacion fechada aditiva para las tareas archivadas (W2).** Cada tarea obsoleta conserva su texto original y recibe un sufijo con la forma:
` — ANOTACION (2026-10-27, c-150 W2): la justificacion "no hay commits del change" quedo OBSOLETA. <change> se commiteo en <commit> y se fusiono en <PR> (merge <merge>); la verificacion de rollback es MOOT. El texto original se conserva como evidencia historica.`
Con los datos: c-148 (tasks 9.1 y 9.2), commit `3392012`, PR #53, merge `6516f5f`; c-149 (task 7.1), commit `f666316`, PR #55, merge `4d9e072`. No se toca el estado `[ ]` ni el conteo de tareas. Alternativa descartada: marcar `[x]` (falsificaria la historia: la verificacion de rollback efectivamente no se ejecuto).

**D3 — Dos contratos en el unico loader (W3).** `cargar_corpus()` separa: (a) contrato de CLASIFICACION (`id`, `descripcion`, `canal_origen`, `sector_asignado`, `sectores_adicionales`) validado de forma estricta como hoy; (b) contrato de TIEMPOS (`tiempo_manual_s`, `tiempo_automatizado_s`) opcional: ausente o `null` se acepta como `None`, presente y no numerico se rechaza via `_a_float`. `_a_float` NO se relaja: solo deja de exigirse la PRESENCIA del campo. `cargar_corpus_tolerante` desaparece; `_cargar_corpus_real` y los call sites usan `cargar_corpus()`. Alternativa descartada: mantener dos loaders (duplica el contrato y permite que diverjan).

**D4 — TDD estricto para W3.** RED primero: tests en `evaluation/tests/test_corpus.py` que (a) cargan un corpus con tiempos `null` via `cargar_corpus()` y esperan exito, (b) rechazan un tiempo no numerico presente, (c) rechazan un campo de clasificacion ausente, (d) verifican la ausencia del loader tolerante y el uso del unico loader. GREEN: mover los campos de tiempo fuera de la lista de requeridos estrictos y colapsar el loader. TRIANGULATE: corpus real (56 casos nulos) + corpus mixto + borde (tiempo `0` valido). La verificacion es `cd evaluation; pytest`.

**D5 — Higiene de emojis con dos tratamientos (W5).** Para las marcas de verificacion que cierran una linea de item completado (lineas 351-359), se ELIMINA la marca: la completitud ya la declara el encabezado "Estado: `[x]` completado" de la seccion. Para las marcas en encabezados de gate o de estado (lineas 197, 203, 208, 211, 214, incluidas las apariciones inline junto a un id de change), se REEMPLAZA por texto explicito (por ejemplo `COMPLETADO` en el encabezado y `(completado)` junto al id). Al cierre, ningun U+2713 permanece en `CHANGES.md`. Alternativa descartada: dejar las marcas (viola la regla dura del proyecto).

**D6 — Mapeo de capacidades.** `evaluation-corpus` cubre W3 (cambio de contrato real). `project-documentation` cubre la higiene y fidelidad del registro documental de `CHANGES.md` (W1, W2, W5). `employee-directory` cubre W4 (fidelidad del estado de gobernanza), porque `docs/directorio-evidencia-cumplimiento.md` esta gobernado por `openspec/specs/employee-directory/spec.md` (DIR-009); el requisito de W4 se reasigno desde `project-documentation`. `tesis-document` cubre el registro de confirmaciones en su ledger (items 8 y 9), porque `docs/Tesis/Correcciones/dictamen-correcciones.md` ya vive bajo ese dominio y su requisito de no reescritura historica ya existe alli. Alternativa considerada: mantener W4 en `project-documentation`; se descarto por fidelidad al dominio que gobierna el archivo.

## Risks / Trade-offs

- **[La relajacion de la presencia de tiempos deje pasar un valor malformado] ->** mitigado: `_a_float` sigue estricto para los campos presentes; un valor no numerico presente se rechaza y se cubre con test de triangulacion.
- **[El corpus real viole el contrato de clasificacion al unificar el loader] ->** mitigado: se corre `cd evaluation; pytest` y, si algun caso real falla por un campo de clasificacion, se documenta el hallazgo (no se relaja el contrato sin evidencia).
- **[La anotacion de la tarea archivada altere el conteo N/N del change] ->** mitigado: la anotacion no cambia el estado `[ ]` ni agrega casillas; el conteo de tareas permanece.
- **[Tocar artefactos archivados (W2) o el ledger de gobernanza (W4) en governance ALTO] ->** mitigado: el autor revisa esos diffs antes del merge; el change no commitea ni fusiona por si solo.
- **[Registrar por error una autorizacion no concedida] ->** mitigado: D6 y los escenarios exigen marcar G0.7a/OQ7a y OQ6 como PENDIENTES.

## Migration Plan

1. W1/W5: corregir la nota stale de `CHANGES.md` y eliminar los emojis; verificar con un barrido de U+2713.
2. W2: anotar las tres tareas archivadas.
3. W3 (TDD): RED -> GREEN -> TRIANGULATE -> REFACTOR en `evaluation/`; correr `cd evaluation; pytest`.
4. W4 y confirmaciones: registrar C-60 y las ratificaciones en el ledger, dejando G0.7a/OQ7a y OQ6 pendientes.
5. Cierre: `openspec validate c-150-cerrar-residuales-y-separar-el-contrato-del-corpus --strict`.

Rollback: `git revert` de los commits del change restaura el texto previo y el contrato anterior del corpus; no hay tag ni release.
