## ADDED Requirements

### Requirement: Integridad referencial y restaurabilidad de la memoria exportada

La memoria del proyecto versionada en `.engram/` (chunks `.jsonl.gz` direccionados por contenido) SHALL ser autocontenida y restaurable: un clon limpio SHALL poder ejecutar `engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"` y aplicar TODOS los chunks sin error. En particular, todo extremo (`source_id` o `target_id`) de una mutacion de relacion (`entity == "relation"`, `op == "upsert"`) registrada en cualquier chunk SHALL existir como observacion (`sync_id`) en la union de TODOS los chunks. El repositorio SHALL mantener esta invariante de forma APPEND-ONLY: los chunks existentes MUST NOT editarse ni borrarse (su identidad depende de su contenido), y las correcciones SHALL expresarse agregando chunks nuevos. El repositorio MUST NOT alterar esta invariante por las siguientes vias prohibidas: gitignorear o destrackear `.engram/`, reescribir el historial de git, o ejecutar `engram sync --all` (que exportaria memoria de otros proyectos). El repositorio SHALL proveer, ademas, un procedimiento de recuperacion reproducible y documentado que detecte los datos locales (observaciones y prompts del proyecto) ausentes en todos los chunks y los re-exporte hacia un chunk NUEVO, sin editar chunks existentes, sin exponer secretos y sin incluir el nombre real de ningun colaborador.

#### Scenario: Un clon limpio restaura la memoria sin error

- **WHEN** un colaborador clona el repositorio y ejecuta `git config core.hooksPath .githooks` y `engram sync --import --project "Automatizacion-de-Mesa-de-Ayuda-N8N"`
- **THEN** el import aplica todos los chunks y termina sin el error `relation FK precondition not met: referenced observation missing`
- **AND** la memoria del proyecto queda disponible en la base local de Engram

#### Scenario: Toda relacion referencia observaciones presentes en la union de chunks

- **WHEN** se recorre cada chunk de `.engram/chunks/` y se recolecta el conjunto de `sync_id` de sus observaciones
- **THEN** cada mutacion de relacion con `op == "upsert"` tiene su `source_id` y su `target_id` dentro de ese conjunto
- **AND** el numero de referencias colgantes es cero

#### Scenario: La correccion es append-only

- **WHEN** se re-exporta un dato local que el watermark omitio
- **THEN** la correccion se materializa como un chunk NUEVO bajo `.engram/chunks/`
- **AND** ningun chunk preexistente se edita ni se borra
- **AND** la entrada correspondiente se agrega a `.engram/manifest.json` sin remover entradas previas

#### Scenario: Vias de correccion prohibidas

- **WHEN** se inspecciona la configuracion y el historial del repositorio
- **THEN** `.engram/` no figura en `.gitignore` ni fue destrackeado
- **AND** no se ejecuto `engram sync --all` para reparar la memoria
- **AND** no se reescribio el historial de git

#### Scenario: Recuperacion reproducible de los datos omitidos por el watermark

- **WHEN** se ejecuta el procedimiento de recuperacion documentado sobre una base local con datos del proyecto ausentes en los chunks
- **THEN** los datos omitidos quedan exportados en un chunk nuevo
- **AND** el procedimiento no imprime secretos ni nombres reales de colaboradores
- **AND** al re-ejecutar la deteccion no quedan datos del proyecto ausentes en los chunks

### Requirement: Nota tecnica exacta de la version de Engram y la decision de actualizacion

El repositorio SHALL documentar de forma exacta, en una nota canonica de la memoria de Engram, la version efectivamente usada (Engram 1.20.0 con manifest version 1) y la decision del equipo de NO actualizar a Engram 3.x por ahora, con su justificacion. La justificacion escrita MUST NOT afirmar que Engram 3.x rechaza el manifest v1 del repositorio como un todo. La nota SHALL declarar que Engram v3.7.1 ACEPTA el manifest v1 y lo MIGRA a manifest v2 al exportar cuando hay sesiones propias del proyecto, y que lo que Engram rechaza son ciertas DEGRADACIONES (bajadas de version), no el manifest v1 en si. La nota SHALL registrar ademas el mecanismo de defecto conocido y su mitigacion vigente: el watermark global `lastChunkTime` del export incremental puede omitir datos locales mas viejos que el ultimo chunk de otra maquina, y el repositorio se protege con la guarda de integridad de CI y el procedimiento de recuperacion append-only; el parche del CLI queda pendiente para una futura actualizacion.

#### Scenario: La nota declara la version usada y la decision

- **WHEN** se lee la nota canonica de la memoria de Engram
- **THEN** declara Engram 1.20.0 con manifest version 1 como la version en uso
- **AND** declara la decision de no actualizar a Engram 3.x por ahora, con su motivo

#### Scenario: La justificacion no afirma que el v3 rechaza el manifest v1

- **WHEN** se busca en la documentacion del repositorio la afirmacion de que Engram 3.x rechaza el manifest v1 como un todo
- **THEN** no aparece
- **AND** la nota declara que v3.7.1 acepta el manifest v1 y lo migra a v2 al exportar cuando hay sesiones propias del proyecto, y que rechaza ciertas degradaciones, no el v1 en si

#### Scenario: El defecto del watermark y su mitigacion quedan registrados

- **WHEN** se lee la nota canonica de la memoria de Engram
- **THEN** describe el watermark global `lastChunkTime` como causa del dato omitido
- **AND** remite a la guarda de integridad de CI y al procedimiento de recuperacion append-only como mitigacion vigente
