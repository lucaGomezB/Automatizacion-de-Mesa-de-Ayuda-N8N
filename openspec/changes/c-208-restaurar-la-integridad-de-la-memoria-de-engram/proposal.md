## Why

El repositorio versiona `.engram/` como evidencia de auditoria de la tesis en un repositorio PUBLICO, pero hoy un clon limpio NO puede restaurar la memoria: `engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` falla de forma dura tras dos pasadas con `chunk 1a793a9f: apply chunk mutation 11: relation FK precondition not met: referenced observation missing`. El chunk `1a793a9f` contiene la mutacion de relacion `rel-4ba9039520e6d90a` (relacion `not_conflict`) cuyo extremo `obs-32328fae59f52558` NO fue exportado en NINGUN chunk. Evidencia verificada en la auditoria de hoy:

- El filtro del export incremental usa un watermark GLOBAL (`lastChunkTime` = max `created_at` de los chunks de TODAS las maquinas). Cuando otra maquina publica un chunk con fecha posterior, los datos locales mas viejos que ese watermark se omiten y nunca se re-exportan. Medido contra la base local: 36 observaciones de proyecto y 106 prompts de proyecto existen localmente y NO estan en ningun chunk.
- El arreglo puntual de hoy (commit `04f7cd5` en `main`) forzo `UPDATE observations SET updated_at=datetime('now')` sobre la unica observacion faltante y re-ejecuto `engram sync --project`, produciendo el chunk `6a6bd2fb`. Verificado hoy sobre los 158 archivos `.jsonl.gz` de `.engram/chunks/` (1232 observaciones en la union, 40 mutaciones de relacion): 0 referencias colgantes. Eso es un arreglo de SINTOMA, no el arreglo SISTEMICO.
- El defecto de export vive en el CLI `engram` 1.20.0 (pinnado), que el repositorio no puede parchear. Por lo tanto la mitigacion sistemica del lado del repositorio es doble: DETECTAR el defecto antes de publicar (guarda de CI) y proveer un procedimiento de recuperacion REPRODUCIBLE y APPEND-ONLY que re-exporte lo que el watermark omitio.
- Nota tecnica a corregir: la afirmacion "Engram 3.x rechaza el manifest v1 del repositorio" es inexacta. Engram v3.7.1 ACEPTA el manifest v1 y lo MIGRA a v2 al exportar cuando hay sesiones propias del proyecto; rechaza ciertas DEGRADACIONES (bajadas de version), no el v1 como un todo. La decision conservadora de no actualizar puede mantenerse, pero su justificacion escrita debe ser exacta.

## What Changes

- **Contrato de integridad y restaurabilidad de la memoria exportada**: la memoria versionada en `.engram/` SHALL ser autocontenida; todo extremo (`source_id`/`target_id`) de una mutacion de relacion SHALL existir como observacion en la union de TODOS los chunks; un clon limpio SHALL importar sin error.
- **Guarda de integridad en CI** (nuevo paso en el job `secret-scan`, o job nuevo si se prefiere): carga TODOS los chunks en una base de datos TEMPORAL y FALLA si alguna mutacion de relacion referencia una observacion ausente en todos los chunks. Sin esa guarda el defecto reincide.
- **Procedimiento de recuperacion append-only**: script reproducible que detecta el conjunto local-ausente-en-chunks y re-exporta esos datos hacia un chunk NUEVO, sin editar ni borrar chunks existentes y sin imprimir secretos ni nombres reales.
- **Correccion de la nota tecnica** sobre la version de Engram y la decision de actualizacion, escrita de forma exacta.
- **Invariantes duras reafirmados**: chunks direccionados por contenido, NUNCA editar ni borrar (arreglo append-only); `.engram/` NUNCA se gitignorea ni se destrackea; secretos saneados por `scripts/security/scan_engram_secrets.py`; prompts redactados por `scripts/security/scrub_engram_prompts.py` via `.githooks/pre-commit`; NUNCA el nombre real de un colaborador; `engram sync --all` PROHIBIDO.

**Fuera de alcance:** actualizar Engram a 3.x o cambiar el manifest (el repo sigue en Engram 1.20.0 / manifest v1); editar o borrar chunks existentes; reescribir el historial de git; tocar el clasificador, la tesis, la base operativa o cualquier corrida paga. El bug de export del CLI 1.20.0 no se parchea aqui (no es codigo del repositorio); se mitiga con deteccion y recuperacion.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `foundation-environment`: se AGREGA el contrato de integridad referencial y restaurabilidad de la memoria exportada, la invariante append-only de los chunks y la exigencia de una nota tecnica exacta sobre la version de Engram y la decision de no actualizar. No cambia el requisito existente de versionado de la memoria.
- `ci-pipeline`: se AGREGA una guarda de integridad referencial de la memoria de Engram que corre en CI, en modo offline y sin secretos, y falla ante cualquier referencia colgante.

## Impact

- Nuevo script de guarda: `scripts/security/check_engram_chunk_integrity.py` (solo biblioteca estandar: `gzip`, `json`, `sqlite3`, `tempfile`).
- Nuevo script de recuperacion: `scripts/security/reexport_missing_engram_data.py` (o equivalente documentado), append-only.
- CI: `.github/workflows/ci.yml`, job `secret-scan` (paso nuevo) o job dedicado.
- Documentacion: una nota canonica de la memoria de Engram (por ejemplo `docs/engram-memory.md`) y sus punteros desde `README.md` y `AGENTS.md`.
- Tests: `scripts/security/test_check_engram_chunk_integrity.py` (fixtures sinteticas sano vs. colgante) y la suite de la guarda.
- Gobernanza: ALTO (integridad de la evidencia de auditoria y guardas de seguridad; no toca PII ni autenticacion). Restriccion dura: NO se edita ni borra ningun chunk; el arreglo es ampliamente append-only.
- Memoria: se publica un chunk nuevo con los datos locales omitidos por el watermark (observaciones/prompts), preservando el contenido y sin secretos ni nombres reales.
