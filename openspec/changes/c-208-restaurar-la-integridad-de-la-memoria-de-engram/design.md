# Design: Restaurar la integridad de la memoria de Engram (change c-208)

## Context

Ver `proposal.md` — Why. Estado de partida verificado al proponer (2026-11-13):

- `.engram/manifest.json` es version 1 con 158 entradas de chunk; `.engram/chunks/` contiene 158 archivos `.jsonl.gz`. Cada chunk es UN objeto JSON (claves `sessions`, `observations`, `prompts` y, cuando corresponde, `mutations`). Las mutaciones de relacion tienen la forma `{"entity":"relation","entity_key":"rel-...","op":"upsert","payload":"<json>"}` y el payload lleva `sync_id`, `source_id`, `target_id` y `relation`.
- Medido sobre la memoria real: 1232 observaciones en la union de chunks, 40 mutaciones de relacion, 0 referencias colgantes. El defecto original (chunk `1a793a9f`, mutacion 11, relacion `rel-4ba9039520e6d90a`, extremo `obs-32328fae59f52558` ausente) quedo reparado por el commit `04f7cd5` (chunk `6a6bd2fb`).
- El filtro del export incremental de `engram` 1.20.0 usa un watermark GLOBAL `lastChunkTime` (max `created_at` de los chunks de todas las maquinas). Datos locales mas viejos que el watermark de otra maquina no se re-exportan. La base local tiene 36 observaciones y 106 prompts del proyecto ausentes en todos los chunks.
- El defecto vive en el binario `engram` (1.20.0, instalado por el desarrollador), NO en codigo del repositorio. El repo no lo puede parchear; solo puede detectarlo y recuperarse.
- El repositorio ya posee `scripts/security/scan_engram_secrets.py` (gzip-aware) cableado al job `secret-scan` de `.github/workflows/ci.yml`, y `scripts/security/scrub_engram_prompts.py` cableado al hook `.githooks/pre-commit`. Es el mismo dominio tecnico (guardas sobre la memoria versionada).

## Goals / Non-Goals

**Goals:**

- Garantizar que un clon limpio pueda restaurar la memoria (import sin error).
- Fijar la invariante "toda relacion referencia observaciones presentes en la union de chunks" como una guarda ejecutable en CI, offline y sin secretos.
- Dejar un procedimiento de recuperacion reproducible y append-only para los datos que el watermark omitio.
- Corregir la nota tecnica sobre la version de Engram con una afirmacion exacta.

**Non-Goals:**

- No actualizar Engram ni migrar el manifest (el repo sigue en 1.20.0 / manifest v1).
- No editar, borrar ni recomputar chunks existentes; no reescribir el historial de git.
- No parchear el CLI `engram` (fuera del repositorio).
- No tocar el clasificador, la tesis, la base operativa ni los guards de secretos/prompts existentes.

## Decisions

### D1. La guarda reproduce la precondicion FK con una base TEMPORAL y solo biblioteca estandar

La precondicion del import es exactamente "la observacion referenciada debe existir en el store construido a partir de los chunks". Se materializa asi: un script `scripts/security/check_engram_chunk_integrity.py` que (1) descomprime cada `.jsonl.gz`, (2) recolecta los `sync_id` de todas las observaciones, (3) crea una base SQLite temporal (`tempfile`, `sqlite3`, `PRAGMA foreign_keys=ON`) con una tabla de observaciones y una tabla de relaciones con claves foraneas a ella, y (4) aplica las mutaciones de relacion `upsert`; una referencia ausente viola la FK y produce el fallo.

- Alternativa considerada: ejecutar `engram sync --import` contra un `ENGRAM_HOME`/base descartable en CI. Se descarta para la guarda BLOQUEANTE porque acopla el pipeline al binario pinnado (canal de instalacion, version, escritura de estado) y no es hermetico. La base SQLite temporal reproduce la MISMA condicion, es determinista y no depende de red ni del binario.
- La guarda bloqueante NO sustituye el oraculo: el motor de import de Engram 1.20.0 sigue siendo la referencia; un end-to-end con el binario MAY agregarse como verificacion NO bloqueante, pero no es necesaria para fijar el contrato.

### D2. Ubicacion en el job `secret-scan` (paso nuevo), no un job dedicado

Se agrega la guarda como un paso nuevo del job `secret-scan`, que ya hace checkout con `fetch-depth: 0`, ya existe por cada corrida y ya es dueno de la salud de `.engram/`. Evita un runner adicional.

- Alternativa considerada: un job dedicado (`engram-integrity`). Se descarta por costo (un runner mas por corrida) sin ganancia: la guarda es puramente estatica y no comparte estado con los otros jobs. Si el paso crece, se puede promover a job dedicado sin cambiar los specs.

### D3. El arreglo sistemico del repo es deteccion + recuperacion, no parche del binario

El defecto (`lastChunkTime` global) esta en `engram` 1.20.0 y no es parcheable desde el repositorio. El arreglo sistemico del lado del repo es: (a) la guarda de D1, que impide PUBLICAR memoria con una referencia colgante, y (b) el procedimiento de recuperacion de D4, que re-exporta lo omitido. Se explicita que el parche del filtro queda pendiente de una futura actualizacion de Engram.

- Alternativa considerada: borrar el watermark o forzar un export total. Se descarta: `engram sync --all` esta PROHIBIDO (exportaria otros proyectos) y editar el estado del sync no es reproducible ni auditable.

### D4. Recuperacion append-only por bump de `updated_at` de las filas estrictamente faltantes

El procedimiento documentado (script `scripts/security/reexport_missing_engram_data.py` o pasos equivalentes) detecta el conjunto local-ausente-en-chunks (observaciones y prompts del proyecto) y, para las filas estrictamente faltantes, adelanta su `updated_at` para que el filtro incremental las vuelva a considerar; luego re-ejecuta `engram sync --project`. El resultado es un chunk NUEVO; ningun chunk existente se toca. Es el mismo mecanismo que uso el arreglo puntual `04f7cd5`, generalizado y verificable.

- Restricciones: la deteccion es de SOLO LECTURA salvo el bump de timestamp de las filas faltantes; el script NUNCA imprime nombres reales ni valores de secretos; la verificacion posterior exige 0 referencias colgantes y el import exitoso.
- Alternativa considerada: exportar todo el proyecto sin watermark. Se descarta por lo mismo que D3 (prohibicion de `--all` y de manipular el estado).

### D5. Invariante append-only explicita

Los chunks estan direccionados por contenido (su nombre resume su contenido): editar o borrar un chunk rompe la evidencia de auditoria. Por eso toda correccion AGREGA un chunk. La guarda (D1) es de solo lectura y la recuperacion (D4) nunca toca chunks previos. El manifest solo agrega entradas.

### D6. Correccion de la nota tecnica (exactitud de la justificacion)

La nota canonica de la memoria (nueva, por ejemplo `docs/engram-memory.md`, enlazada desde `README.md` y `AGENTS.md`) declara: version en uso Engram 1.20.0 / manifest v1; decision de no actualizar a 3.x por ahora; y la afirmacion EXACTA de que v3.7.1 acepta el manifest v1 y lo MIGRA a v2 al exportar cuando hay sesiones propias del proyecto, y rechaza ciertas DEGRADACIONES (no el v1 como un todo). Se elimina de la documentacion cualquier afirmacion de que "v3.x rechaza el manifest v1" como bloque.

- Alternativa considerada: dejar la justificacion vaga. Se descarta: la evidencia de auditoria exige una justificacion verificable y sin errores tecnicos.

### D7. TDD y orden de trabajo

La guarda se construye con TDD: primero un fixture sintetico con una referencia colgante (RED), despues la implementacion minima (GREEN), y triangulacion con casos: chunk sin mutaciones, relacion con `op != upsert` (no exige observacion), varias relaciones, y el repositorio real en verde. La recuperacion se prueba con una base/chunks sinteticos. El orden es: guarda → cableado CI → recuperacion → documentacion.

## Risks / Trade-offs

- **La guarda solo detecta; el defecto de export sigue vivo** → Mitigacion: el procedimiento de recuperacion (D4) re-exporta lo omitido y el parche queda registrado como pendiente de actualizar Engram. Se documenta como limitacion conocida.
- **Bump de `updated_at` altera metadatos de filas faltantes** → Mitigacion: se limita a las filas estrictamente ausentes en los chunks; no cambia el contenido ni las observaciones; es append-only sobre los chunks. El `created_at` se conserva.
- **Falsos positivos en mutaciones que no son `upsert`** → Mitigacion: la guarda solo exige la observacion para `op == "upsert"`; una retraccion/borrado de relacion no requiere el extremo.
- **Chunk sin `mutations` o con `mutations` nulo** → Mitigacion: la guarda trata la ausencia como lista vacia (verificado: los chunks actuales tienen siempre `observations`; varios no tienen `mutations`).
- **Acoplamiento al formato interno de los chunks** → Mitigacion: el formato esta pinnado por Engram 1.20.0 / manifest v1 y la nota tecnica lo declara; cualquier upgrade debera revisar la guarda. La suite de la guarda fija el contrato.
- **Filtracion de datos por la recuperacion** → Mitigacion: la deteccion y el re-export no imprimen contenido; los guards existentes (`scan_engram_secrets.py` + `scrub_engram_prompts.py`) siguen corriendo en el hook antes del commit.

## Migration Plan

No hay migracion de datos del sistema ni backfill sobre la base operativa. Pasos: (1) agregar la guarda y su suite; (2) cablearla al job `secret-scan`; (3) agregar/documentar la recuperacion; (4) publicar un chunk nuevo con los datos localmente omitidos; (5) corregir la nota tecnica. Rollback: revertir el paso de CI, los scripts y la nota; el chunk nuevo de recuperacion es evidencia append-only y NO se borra (borrarlo romperia la inmutabilidad). Si el owner rechaza el change antes de aplicarlo, se elimina el directorio del change con `openspec` (ver el reporte final).

## Open Questions

- Si conviene agregar, como verificacion NO bloqueante, un end-to-end con `engram sync --import` contra un `ENGRAM_HOME` descartable. No cambia los specs ni el enfoque (la guarda bloqueante ya fija el contrato).
- Cuando se decida actualizar Engram a 3.x, revisar la guarda contra el manifest v2 (fuera del alcance de este change).
