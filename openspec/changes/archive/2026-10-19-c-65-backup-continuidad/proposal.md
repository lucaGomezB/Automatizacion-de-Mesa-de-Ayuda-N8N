## Why

La tesis afirma en tiempo presente un esquema de respaldo que el repositorio no entrega: "respaldos diarios automaticos con retencion escalonada" (`docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex:24`) y "respaldos diarios" (`05-arquitectura.tex:25,81`). La realidad es un backup MANUAL: no hay cron ni systemd timer ni scheduler que lo dispare (`docs/por_implementar.md:4.4`, "Sin Job de Backup Automatico"), `scripts/backup.sh` produce un dump SQL EN CLARO con rotacion de 7 dias pero sin cifrado, sin copia offsite y sin prueba de restauracion, y no existe RTO/RPO ni plan de continuidad. El gap assessment lo confirma como brecha Alta (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md:64,101,104,145,146,192`). C-65 cierra la brecha entre lo que la tesis declara y lo que el sistema hace —en el mismo espiritu que C-66: hace verificable una afirmacion de la tesis— y ademas corrige afirmaciones obsoletas del propio assessment. Es el ultimo change pendiente del workstream de cumplimiento (`docs/cumplimiento/plan-cambios-cumplimiento.md`, fase 21, fila C-65).

## What Changes

- **Cifrado del dump (T)**: `scripts/backup.sh` (y su par `backup.ps1`) produce el dump cifrado en reposo con `openssl` AES-256 (modo CBC, `pbkdf2`, con sal), a partir de una passphrase obtenida de un secreto de configuracion. Se documenta el comando de generacion de la passphrase y su custodia. El archivo deja de quedar en texto plano con datos de directorio.
- **Automatizacion con programador versionado (T)**: se agrega al repositorio el archivo de programacion (entrada de `cron` y/o unidad `systemd` timer, versionados en `scripts/`), de modo que el backup deje de ser manual. El programador invoca el backup diario y registra su salida en un log.
- **Prueba de restauracion periodica reproducible (T+D)**: se agrega un script versionado de verificacion de restauracion que restaura el dump mas reciente en una base de datos DESCARtable y verifica que las tablas y el conteo de filas esperados existen, ademas de su procedimiento documentado. La prueba es de solo verificacion: no toca la base de la aplicacion.
- **Copia offsite, redundancia, RTO/RPO y plan de continuidad (D)**: se DOCUMENTAN como accion del adoptante (no infraestructura real): copia fuera del host, redundancia basica del PostgreSQL unico, objetivos de recuperacion (RTO/RPO) y plan de continuidad con procedimiento de restauracion. El repositorio no puede garantizar disponibilidad ni offsite; se declara explicitamente.
- **Correccion de afirmaciones obsoletas (D)**: el gap assessment afirma que `backups/` esta vacio (`...:64,145`); en realidad `backups/` contiene dumps reales del 2026-10-09 (gitignored). Se corrige esa afirmacion y se reconcilia con el resto del documento.
- **Snapshot de volumenes Docker (D)**: los `.tgz` de `backups/` se generan hoy de forma manual, sin generador versionado. Este change DOCUMENTA el procedimiento del adoptante para el snapshot de volumenes y deja explicito que no agrega un generador versionado (decision registrada; ver OQ1).
- **Purpose real en la spec principal (D)**: el `## Purpose` de `openspec/specs/backup-scripts/spec.md` conserva el marcador `TBD - created by archiving change c-26... Update Purpose after archive.` Se reemplaza por un proposito real de una sola frase. Es parte de C-65 porque el change ya MODIFICA la capability `backup-scripts`, y el archive NO reescribe el `## Purpose`; la spec principal es la fuente de verdad y debe dejar de exhibir el residuo de c-26.

### Out of scope (no-goals)

- NO se implementa almacenamiento offsite real ni redundancia real (replica/HA): se documentan como accion de la organizacion adoptante; el repositorio no puede garantizar disponibilidad.
- NO se persigue certificacion ISO/NIST ni se usa lenguaje de "compliant"/"cumple"/"certificado" (regla de lenguaje del proyecto).
- NO se firman contratos ni acuerdos con proveedores de nube.
- NO se toca el alcance de SMS / C-67 (archivado como NO REALIZADO, no se reintroduce).
- NO se agrega un generador versionado de snapshot de volumenes Docker (se documenta; ver OQ1).

## Capabilities

### New Capabilities

- `continuity-planning`: objetivos de recuperacion (RTO/RPO) y plan de continuidad de la informacion del sistema, con la copia offsite y la redundancia documentadas como responsabilidad de la organizacion adoptante; incluye la reconciliacion de las afirmaciones de respaldo del gap assessment.

### Modified Capabilities

- `backup-scripts`: se agregan requisitos de cifrado del dump en reposo (BACKUP-005), automatizacion mediante programador versionado (BACKUP-006), prueba de restauracion reproducible (BACKUP-007) y el encuadre del snapshot de volumenes Docker como procedimiento documentado sin generador versionado (BACKUP-008). Los requisitos BACKUP-001..004 se preservan.

## Impact

| Area | Impacto | Descripcion |
|------|---------|-------------|
| `scripts/backup.sh` | Modified | Cifra el dump en reposo con `openssl` AES-256 y toma la passphrase de un secreto de configuracion; la rotacion de 7 dias y el resto del comportamiento se preservan. |
| `scripts/backup.ps1` | Modified | Paridad funcional con `backup.sh` (BACKUP-004): mismo cifrado y mismo contrato de errores. |
| `scripts/backup-restore-test.sh` | New | Script versionado de prueba de restauracion (restaura el dump mas reciente en una base descartable y verifica tablas/filas). |
| `scripts/backup-schedule.cron` (o `.service`/`.timer`) | New | Programador versionado que dispara el backup diario y registra su salida. |
| `App/Backend/.env.example` | Modified | Documenta la passphrase de cifrado de backups y su comando de generacion. |
| `docs/operational-guide.md` | Modified | Documenta restauracion cifrada, prueba de restauracion, programador y snapshot de volumenes. |
| `docs/seguridad/plan-continuidad.md` | New | RTO/RPO, plan de continuidad, copia offsite y redundancia (accion del adoptante). |
| `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` | Modified | Corrige la afirmacion obsoleta de `backups/` vacio y reconcilia las brechas 8.13/8.14/5.29/5.30/5.33. |
| `openspec/specs/backup-scripts/spec.md` | Modified | Reemplaza el `## Purpose` con `TBD - created by archiving change c-26...` por un proposito real de una sola frase. |
| `openspec/changes/c-65-backup-continuidad/**` | New | Artefactos OPSX (proposal, specs, design, tasks). |

Sin cambios de esquema de datos, API REST ni dependencias de runtime. La passphrase de cifrado es un secreto de despliegue (no se versiona su valor).

## Governance

**ALTO (HIGH)**. El cambio toca datos de directorio (PII en el dump) y la disponibilidad del sistema. Bajo la gobernanza por dominio: la decision de cifrado y de gestion de la passphrase, la correccion del gap assessment y el plan de continuidad requieren revision del autor antes de cerrar el change. No se escribe logica de produccion en la fase de propose.

## Decisiones resueltas y preguntas abiertas

- **Cifrado (DECIDIDO)**: `openssl enc -aes-256-cbc -pbkdf2 -salt` con passphrase de un secreto de configuracion; se documenta la generacion de la passphrase. Se descarta PGP/GPG (mayor friccion de custodia de claves) y el cifrado por el propio PostgreSQL.
- **OQ1 — Snapshot de volumenes (ACEPTADO por el autor)**: se DOCUMENTA el procedimiento del adoptante y NO se agrega generador versionado. Razon: el respaldo canonico restaurable es el dump logico de `pg_dump`; el `.tgz` de volumenes es de nivel host y sumaria superficie (y paridad bash/PowerShell) sin aportar garantia de restauracion adicional (el `n8n/workflow.json` ya esta versionado). Si el autor prefiere un generador versionado, se reabre.
- **OQ2 — Fuente de la passphrase (ACEPTADO por el autor)**: variable de entorno/secreto de despliegue (`BACKUP_ENCRYPTION_PASSPHRASE`), documentada en `App/Backend/.env.example`, alineada con `docs/seguridad/gestion-secretos-y-rotacion.md`. Se descarta un archivo de clave en el repositorio.
- **OQ3 — Valores de RTO/RPO (CONFIRMADO por el autor: 24 h / 24 h)**: el autor confirmo RTO 24 h y RPO 24 h, alineados con la cadencia diaria del backup. Quedan cerrados.
- **OQ4 — Programador (DECIDIDO, revisable)**: archivo de `cron` versionado como mecanismo principal, con unidad `systemd` timer documentada como alternativa. La eleccion concreta depende del host del adoptante.

## Risks

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Perdida de la passphrase inhabilita la restauracion | Med | Custodia documentada como secreto de despliegue; la passphrase se conserva FUERA de `backups/`; runbook de custodia. |
| El cifrado rompe la rotacion o la paridad bash/PowerShell | Med | Tests de rotacion y de equivalencia (BACKUP-002/004) ampliados al archivo cifrado. |
| El dump cifrado no es restaurable por error de formato | Med | La prueba de restauracion (BACKUP-007) descifra y restaura en una base descartable; falla ruidosamente si el dump no es usable. |
| La prueba de restauracion toca la base de la aplicacion | Baja | Guarda de seguridad por nombre de base (misma logica de la suite de integracion: aborta si el destino es la base de la aplicacion). |
| Documentar offsite/redundancia como si existieran | Med | Encuadre explicito: son accion del adoptante; el repositorio no las garantiza; test de contenido. |
| Corregir el assessment introduce nuevas inconsistencias | Baja | Tarea de reconciliacion y validacion de consistencia del documento completo. |

## Rollback Plan

Revertir el commit restaura el backup en claro y elimina el programador, la prueba de restauracion y los documentos nuevos. No hay migraciones ni cambios de API. Consideracion de governance: revertir reintroduce el hallazgo de dump en claro con PII de directorio (5.33/8.13), por lo que un rollback debe quedar justificado.

## Dependencies

- Insumos de alcance y normativos (Leer antes): `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4 (fila C-65), `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 8.13, 8.14, 5.29, 5.30, 5.33), `docs/cumplimiento/marco-legal-ar-2026.md`, `docs/seguridad/gestion-secretos-y-rotacion.md`, `docs/operational-guide.md` (restauracion).
- Base de codigo y spec: `scripts/backup.sh`, `scripts/backup.ps1`, `openspec/specs/backup-scripts/spec.md` (BACKUP-001..004).
- Sin dependencias de otros changes.

## Success Criteria

- [ ] `scripts/backup.sh` y `scripts/backup.ps1` producen un dump CIFRADO en reposo (AES-256) y fallan ruidosamente si falta la passphrase; la rotacion de 7 backups sigue operando.
- [ ] Existe un programador versionado (cron/timer) que dispara el backup diario y registra su salida; el backup deja de requerir ejecucion manual.
- [ ] Existe `scripts/backup-restore-test.sh` que descifra y restaura el dump mas reciente en una base descartable y verifica tablas/filas, con guarda que impide tocar la base de la aplicacion.
- [ ] Existe `docs/seguridad/plan-continuidad.md` con RTO/RPO, procedimiento de restauracion, copia offsite y redundancia encuadradas como accion del adoptante.
- [ ] El gap assessment ya no afirma que `backups/` esta vacio y reconcilia las brechas 5.29/5.30/5.33/8.13/8.14.
- [ ] El snapshot de volumenes Docker queda documentado, dejando explicito que no se agrega generador versionado.
- [ ] `docs/seguridad/README.md` indexa el plan de continuidad con su mapa de trazabilidad.
- [ ] `openspec/specs/backup-scripts/spec.md` tiene un `## Purpose` real de una sola frase; no queda ningun `TBD - created by archiving change c-26...`.
- [ ] `openspec validate --strict c-65-backup-continuidad` y `openspec validate --strict --changes` pasan.
