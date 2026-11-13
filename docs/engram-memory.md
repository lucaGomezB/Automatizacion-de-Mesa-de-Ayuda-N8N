# Memoria de Engram: version, defecto conocido, guarda y recuperacion

Nota canonica de la memoria versionada en `.engram/` (change `c-208-restaurar-la-integridad-de-la-memoria-de-engram`). La memoria se publica en un repositorio PUBLICO y es evidencia para la auditoria de la tesis.

## 1. Version en uso y decision de no actualizar

- **Version en uso:** Engram 1.20.0, con `.engram/manifest.json` en **version 1** (lista de chunks con `id`, `created_by`, `created_at` y contadores).
- **Decision:** NO se actualiza a Engram 3.x por ahora. Motivo: el repositorio, los hooks, la guarda de integridad y los procedimientos de este documento estan validados contra 1.20.0 y manifest v1; una actualizacion cambia el formato del manifest y obliga a revisar la guarda y los scripts de seguridad. Es una decision de prudencia, no una incompatibilidad.
- **Afirmacion exacta sobre Engram v3.7.1:** v3.7.1 ACEPTA el manifest v1 y lo MIGRA a manifest v2 al exportar cuando hay sesiones propias del proyecto. Lo que Engram rechaza son ciertas DEGRADACIONES (bajadas de version del manifest), no el manifest v1 como un todo. Por eso esta nota no sostiene que 3.x rechace el v1 del repositorio.
- Cuando se decida actualizar, hay que revisar `scripts/security/check_engram_chunk_integrity.py` contra el manifest v2 (la guarda lee los chunks, no el manifest, pero el formato de los chunks esta pinneado por 1.20.0).

## 2. Defecto conocido: el watermark global del export incremental

El export incremental de Engram 1.20.0 filtra con un watermark GLOBAL, `lastChunkTime`: el maximo `created_at` de los chunks de TODAS las maquinas. Si otra maquina publica un chunk con fecha posterior, los datos locales mas viejos que ese watermark se omiten y nunca se vuelven a exportar. Una relacion (`not_conflict`, etc.) puede entonces quedar exportada sin una de sus observaciones, y el import de un clon limpio falla con `relation FK precondition not met: referenced observation missing`.

El defecto vive en el binario `engram`, no en codigo del repositorio, y no se parchea aqui. La mitigacion vigente es doble: la **guarda de CI** (detecta) y el **procedimiento de recuperacion append-only** (re-exporta). El parche del filtro queda pendiente de una futura actualizacion de Engram.

## 3. Invariantes duras

- **Append-only.** Los chunks `.engram/chunks/*.jsonl.gz` estan direccionados por contenido: NUNCA se editan ni se borran. Toda correccion agrega un chunk nuevo y una entrada nueva al manifest.
- `.engram/` NUNCA se agrega a `.gitignore` ni se destrackea.
- `engram sync --all` esta PROHIBIDO (exporta la memoria de todos los proyectos de la maquina). Siempre `--project "Automatizacion-de-Mesa-de-Ayuda-N8N"`.
- No se reescribe el historial de git.
- Secretos: `scripts/security/scan_engram_secrets.py`. Prompts: `scripts/security/scrub_engram_prompts.py`. Ambos corren en `.githooks/pre-commit`. NUNCA el nombre real de un colaborador en la memoria.
- Contrato de integridad: todo extremo (`source_id`, `target_id`) de una mutacion de relacion `upsert` existe como observacion (`sync_id`) en la union de TODOS los chunks.

## 4. Guarda de integridad (CI)

```bash
python3 scripts/security/check_engram_chunk_integrity.py .engram
```

Carga todos los chunks, junta los `sync_id` de observaciones, crea una base SQLite temporal con claves foraneas de las relaciones hacia las observaciones y aplica las mutaciones de relacion. Solo biblioteca estandar, sin red ni secretos; no modifica nada. Salida: una linea por referencia colgante (relacion y extremo faltante) y un resumen con el conteo. Exit 0 integra, 1 con colgantes, 2 error de uso o de I/O. Corre como un paso del job `secret-scan` de `.github/workflows/ci.yml` y es bloqueante.

Tests: `python3 -m pytest scripts/security/test_check_engram_chunk_integrity.py -q`.

## 5. Recuperacion append-only de datos omitidos por el watermark

### Deteccion (solo lectura, es la invocacion por defecto)

```bash
python3 scripts/security/reexport_missing_engram_data.py --engram-dir .engram
```

Abre la base local (`$ENGRAM_DATA_DIR/engram.db`, por defecto `~/.engram/engram.db`) con `mode=ro` e imprime SOLO CONTEOS de las observaciones y los prompts del proyecto ausentes en la union de chunks. El nombre del proyecto se compara sin distinguir mayusculas (Engram lo guarda en minusculas). Exit 0 si no falta nada, 1 si hay ausentes.

**Precondicion de la deteccion.** El conteo compara la base local contra los chunks del arbol de trabajo. Un chunk exportado en una rama todavia no integrada a `main` NO esta en ese arbol, asi que sus observaciones figuran como ausentes aunque ya esten exportadas. Antes de leer el conteo (y siempre antes de reparar) hay que estar sobre `main` actualizado, con todas las ramas propias que traen chunks ya integradas; de lo contrario la reparacion re-exportaria en un chunk nuevo datos que ya viajan en otro.

### Reparacion (opt-in; PUBLICA memoria)

> **Advertencia:** la reparacion adelanta `updated_at` en la base local y ejecuta `engram sync --project`, que produce un chunk NUEVO con la memoria omitida. Una vez commiteado en el repositorio publico, ese chunk es inmutable (append-only): no se edita ni se borra. Revisar el conteo de la deteccion y confirmar con las autoras y los autores antes de correrla.

```bash
python3 scripts/security/reexport_missing_engram_data.py --engram-dir .engram \
  --repair --confirm-publish
```

- Sin `--confirm-publish` el script se niega a reparar (exit 2).
- Antes de modificar la base hace una copia (`<db>.pre-c208.bak`, o la ruta de `--backup`).
- Adelanta `updated_at` SOLO de las observaciones estrictamente faltantes (el contenido y `created_at` no cambian) y ejecuta `engram sync --project <proyecto>`; nunca `--all`.
- Los prompts solo se detectan: la tabla `user_prompts` no tiene `updated_at`, de modo que este mecanismo no los re-exporta.
- Despues: volver a correr la deteccion (debe dar 0 observaciones) y la guarda (0 colgantes), luego el commit habitual (`engram sync` ya corrio; el hook sanea y escanea) por una rama nueva y PR.

El script nunca imprime titulos, contenido, prompts ni ids de la memoria.

Tests: `python3 -m pytest scripts/security/test_reexport_missing_engram_data.py -q` (base y chunks temporales; `engram` inyectado).
