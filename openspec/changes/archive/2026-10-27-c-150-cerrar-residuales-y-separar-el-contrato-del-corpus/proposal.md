# Proposal: c-150-cerrar-residuales-y-separar-el-contrato-del-corpus

## Why

Cinco residuales documentales y un defecto de contrato del corpus quedaron sin cerrar tras la FASE 42. El registro del proyecto arrastra una referencia stale, 14 emojis prohibidos, anotaciones de rollback obsoletas y aprobaciones del autor sin registrar; y `evaluation/corpus.py` mantiene un contrato rigido (tiempos obligatorios) que obligo a un loader tolerante duplicado para los 56 casos del corpus real con `tiempo_automatizado_s: null`. Cerrarlos deja el registro auditable y el corpus con un unico contrato.

## What Changes

- **W1 (BAJO, doc).** En `CHANGES.md:2398`, reemplazar la nota stale sobre la deuda residual de C-80 por el cierre real (C-80 archivado 45/45 el 2026-10-21, ya registrado en `CHANGES.md:2329`). Hecho vigente vs registro historico: se corrige la afirmacion de estado actual, sin reescribir entradas fechadas.
- **W2 (ALTO, doc, artefactos archivados).** Anotar con fecha las tareas de rollback obsoletas de `c-148` (9.1, 9.2) y `c-149` (7.1), sin borrar el texto original (los archivos son evidencia historica).
- **W3 (MEDIO, codigo, TDD estricto).** Separar en `evaluation/corpus.py` el contrato de CLASIFICACION (id, descripcion, canal_origen, sector_asignado, sectores_adicionales) del de TIEMPOS (opcionales, pero estrictos cuando estan presentes); colapsar `cargar_corpus_tolerante` en el unico `cargar_corpus()` y actualizar los call sites.
- **W4 (ALTO, doc, ledger de gobernanza).** Registrar con precision el estado de C-60 (33/33; la 7.4 ya esta `[x]` porque su contenido es registrar la revision HIGH como PENDIENTE) y dejar la aprobacion HIGH del autor para pasar de datos sinteticos a reales explicitamente pendiente.
- **W5 (BAJO, doc).** Eliminar los 14 emojis (checkmark, U+2713) de `CHANGES.md` (lineas 197-359).
- **Confirmaciones (BAJO, doc).** Registrar en el ledger el OK del autor a la redaccion final de `00-resumen.tex` y `09-conclusiones.tex` (item 9) y ratificar las decisiones provisionales del item 8 (2026-10-27), EXCEPTO G0.7a/OQ7a y OQ6, que quedan explicitamente abiertas.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `evaluation-corpus`: `CORPUS-012` pasa a exigir dos contratos separados (clasificacion obligatoria; tiempos opcionales pero estrictos cuando presentes) y un unico loader sin duplicado tolerante.
- `project-documentation`: se agregan requisitos de higiene del registro (sin emojis) y anotacion fechada de registros historicos sin reescritura.
- `employee-directory`: se agrega el requisito de fidelidad del estado en los registros de gobernanza (una aprobacion humana PENDIENTE del autor no se registra como concedida), reasignado desde `project-documentation` porque `docs/directorio-evidencia-cumplimiento.md` esta gobernado por `openspec/specs/employee-directory/spec.md` (DIR-009).
- `tesis-document`: se agrega el registro de confirmaciones del autor sobre las decisiones provisionales en `docs/Tesis/Correcciones/dictamen-correcciones.md`, con las pendientes marcadas.

## Impact

- **Edita:** `CHANGES.md`; `docs/Tesis/Correcciones/dictamen-correcciones.md`; `docs/directorio-evidencia-cumplimiento.md`; `evaluation/corpus.py`; `evaluation/deterministic_measurement.py`; `evaluation/run_evaluation.py`; tests bajo `evaluation/tests/`. **Anota:** `openspec/changes/archive/2026-10-27-c-148-.../tasks.md` y `.../c-149-.../tasks.md`.
- **No toca:** `App/`, `n8n/`, `docker-compose.yml`, las cinco cadenas de categoria, ni la estrictez de `_a_float` en los campos que valida.
- **Gobernanza:** W2 y W4 ALTO (artefactos archivados y ledger de gobernanza): el autor revisa esos diffs antes del merge. W3 MEDIO. W1, W5 y las confirmaciones BAJO.
- **Riesgo principal:** que la relajacion del contrato de tiempos deje pasar un tiempo malformado; se conserva la estrictez de `_a_float` para los campos presentes y se cubre con tests.

## Rollback

`git revert` de los commits del change: `CHANGES.md`, el ledger y el directorio vuelven a su texto previo; `evaluation/corpus.py` restauraria el contrato con tiempos obligatorios y `cargar_corpus_tolerante`; los call sites vuelven a la carga tolerante. No hay tag ni release.

## Success Criteria

- [ ] `cd evaluation; pytest` en verde.
- [ ] No queda ningun emoji en `CHANGES.md` ni se reescribio texto historico.
- [ ] `openspec validate c-150-cerrar-residuales-y-separar-el-contrato-del-corpus --strict` pasa.
- [ ] Los diffs de W2 y W4 fueron revisados por el autor antes del merge.
