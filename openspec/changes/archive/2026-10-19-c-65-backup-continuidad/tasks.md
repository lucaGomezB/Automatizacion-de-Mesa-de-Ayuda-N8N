## 1. Leer antes y red de seguridad

- [x] 1.1 Confirmar estado del change y activar el hook (`git config core.hooksPath .githooks`; `openspec status --change c-65-backup-continuidad --json`). Verificacion: el status lista proposal/specs/design como `done`.
- [x] 1.2 Leer los insumos obligatorios antes de escribir: `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4 (fila C-65), `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 8.13, 8.14, 5.29, 5.30, 5.33), `docs/cumplimiento/marco-legal-ar-2026.md`, `docs/seguridad/gestion-secretos-y-rotacion.md`, `docs/operational-guide.md:340-389`, `openspec/specs/backup-scripts/spec.md`. Verificacion: notas de lectura registradas con las decisiones de encuadre de lenguaje y alcance.
- [x] 1.3 Correr la red de seguridad de los scripts antes de tocar nada (`bash scripts/tests/test_up_preflight.sh`) y registrar el baseline (N assertions, M fallos). Nota: hoy NO existen tests para `backup.sh`/`backup.ps1`; el harness nuevo es aditivo. Verificacion: baseline capturado; si hay fallos, detener y reportarlos como preexistentes.

## 2. Cifrado del dump en reposo (T) — BACKUP-005

- [x] 2.1 RED: crear `scripts/tests/test_backup.sh` (harness bash con aserciones, patron `test_up_preflight.sh`) con un `docker` falso en `PATH` que emita un dump SQL de prueba, y casos que fallan porque hoy el dump NO se cifra: (a) el archivo resultante no es legible como SQL plano; (b) falta la passphrase → exit distinto de cero y sin dump en claro. Verificacion: `bash scripts/tests/test_backup.sh` falla en los casos nuevos.
- [x] 2.2 GREEN: cifrar el dump en `scripts/backup.sh` con `openssl enc -aes-256-cbc -pbkdf2 -salt` usando `BACKUP_ENCRYPTION_PASSPHRASE`; abortar antes de persistir si falta la passphrase; extension del archivo cifrado; rotacion sobre archivos cifrados. Verificacion: los casos nuevos pasan.
- [x] 2.3 TRIANGULATE: agregar casos con entradas distintas: (a) con passphrase correcta el archivo se descifra y coincide con el dump original; (b) con passphrase incorrecta el `openssl` falla ruidosamente; (c) la rotacion mantiene exactamente 7 archivos cifrados y elimina los mas antiguos; (d) `backup.ps1` declara el mismo cifrado y la misma variable (verificacion estructural, patron de paridad de `test_up_preflight.sh`). Verificacion: todos los casos pasan.
- [x] 2.4 REFACTOR: extraer la logica de cifrado/rotacion en funciones legibles de `backup.sh` sin cambiar comportamiento; re-correr el harness. Verificacion: `bash scripts/tests/test_backup.sh` verde tras cada paso.
- [x] 2.5 Documentar en `App/Backend/.env.example` la variable `BACKUP_ENCRYPTION_PASSPHRASE` con su comando de generacion (por ejemplo `openssl rand -base64 32`) y el encuadre de custodia. Verificacion: `grep -n "BACKUP_ENCRYPTION_PASSPHRASE" App/Backend/.env.example` arroja la variable y el comando.

## 3. Automatizacion con programador versionado (T) — BACKUP-006

- [x] 3.1 RED: agregar a `scripts/tests/test_backup.sh` aserciones que fallan porque no existe archivo de programacion versionado: (a) existe un archivo de programacion en `scripts/`; (b) invoca `backup.sh`; (c) registra salida en un log; (d) NO contiene la passphrase ni credenciales. Verificacion: `bash scripts/tests/test_backup.sh` falla en los casos nuevos.
- [x] 3.2 GREEN: crear el archivo de programacion versionado (entrada de `cron` en `scripts/backup-schedule.cron` y unidad `systemd` `service`+`timer` documentada como alternativa equivalente), sin secretos. Verificacion: los casos nuevos pasan.
- [x] 3.3 TRIANGULATE: caso que verifica que el programador NO referencia ningun valor de secreto (grep negativo de `BACKUP_ENCRYPTION_PASSPHRASE=` con valor y de credenciales) y que la invocacion usa la ruta relativa al repo. Verificacion: el caso pasa.
- [x] 3.4 Documentar la instalacion del programador (cron y systemd) en `docs/operational-guide.md` como paso del adoptante, reemplazando la receta solo-documentada por una referencia al archivo versionado. Verificacion: el documento referencia el archivo versionado y describe la instalacion.

## 4. Prueba de restauracion reproducible (T) — BACKUP-007

- [x] 4.1 RED: crear `scripts/tests/test_backup_restore.sh` (harness bash) con casos que fallan porque no existe `scripts/backup-restore-test.sh`: (a) el script existe y es ejecutable; (b) resta un dump usable en una base descartable y verifica tablas; (c) aborta si el nombre de base coincide con el de la aplicacion; (d) un dump inexistente/ilegible falla con exit distinto de cero. Verificacion: `bash scripts/tests/test_backup_restore.sh` falla en los casos nuevos.
- [x] 4.2 GREEN: crear `scripts/backup-restore-test.sh` que descifre el dump mas reciente, lo restaure en una base DESCARTABLE y verifique tablas y conteo de filas esperados; incluir la guarda por nombre (aborta si coincide con la base de la aplicacion derivada de `DATABASE_URL`). Verificacion: los casos nuevos pasan en un entorno con PostgreSQL descartable.
- [x] 4.3 TRIANGULATE: casos con entradas distintas: (a) `TEST_PG_ALLOW_APP_DB` es el unico escape hatch y su ausencia deja la guarda activa; (b) un dump correctamente descifrado pero invalido como SQL falla con mensaje claro; (c) la verificacion de conteo de filas detecta un dump truncado. Verificacion: todos los casos pasan.
- [x] 4.4 REFACTOR: extraer la verificacion de tablas/filas y la guarda por nombre a funciones legibles; re-correr el harness. Verificacion: `bash scripts/tests/test_backup_restore.sh` verde tras cada paso.
- [x] 4.5 Documentar el procedimiento de prueba de restauracion (incluida la creacion de la base descartable y el escape hatch) en `docs/operational-guide.md` y referenciarlo desde el plan de continuidad. Verificacion: el documento describe el procedimiento y la referencia resuelve. NOTA: la documentacion en `docs/operational-guide.md` §3.4 quedo hecha; la referencia desde `docs/seguridad/plan-continuidad.md` §4 quedo completada en el grupo 7 y resuelve.

## 5. Snapshot de volumenes Docker documentado (D) — BACKUP-008

- [x] 5.1 Documentar en `docs/operational-guide.md` el procedimiento de snapshot de los volumenes `postgres` y `n8n` como accion del adoptante, dejando explicito que NO existe un generador versionado y que el respaldo canonico restaurable es el dump logico de `pg_dump`. Verificacion: `grep -n "generador versionado\|dump logico" docs/operational-guide.md` arroja ambas afirmaciones.
- [x] 5.2 Verificar que NO se agrega generador versionado de volumenes. Verificacion: `ls scripts/` no lista un `backup-volumes.sh` nuevo; la afirmacion queda documentada.

## 6. Purpose real de la spec principal (D) — backup-scripts

- [x] 6.1 Reemplazar el `## Purpose` de `openspec/specs/backup-scripts/spec.md` (hoy `TBD - created by archiving change c-26-corpus-simulado-backup-retencion. Update Purpose after archive.`) por un proposito real de una sola frase que describa el respaldo de PostgreSQL, su cifrado en reposo y su rotacion. Este change ya modifica la capability `backup-scripts`, por lo que la correccion se hace aqui (ver design.md D7). Verificacion: `grep -n "TBD" openspec/specs/backup-scripts/spec.md` no devuelve nada.

## 7. Plan de continuidad: RTO/RPO, offsite y redundancia (D) — CONT-001/CONT-002

- [x] 7.1 Crear `docs/seguridad/plan-continuidad.md` con RTO y RPO en horas (OQ3 CONFIRMADO por el autor: 24 h / 24 h, alineados con la cadencia diaria), el procedimiento de restauracion desde el dump cifrado y el encuadre explicito de que el repositorio no garantiza disponibilidad ni offsite. Verificacion: el documento existe y contiene RTO, RPO, procedimiento y declaracion de no garantia.
- [x] 7.2 Documentar la copia fuera del host y la redundancia basica del PostgreSQL unico como accion de la organizacion adoptante, con lenguaje de alineacion. Verificacion: ambas figuran como responsabilidad del adoptante y no como capacidades del repositorio.
- [x] 7.3 Indexar el documento desde `docs/seguridad/README.md` (listado y mapa de trazabilidad de continuidad 5.29/5.30/8.13/8.14). Verificacion: el indice lista el documento y la referencia resuelve a un archivo existente.
- [x] 7.4 Registrar la custodia de la passphrase (fuera de `backups/`, como secreto de despliegue) en el plan de continuidad y enlazar con `docs/seguridad/gestion-secretos-y-rotacion.md`. Verificacion: el plan describe la custodia y la referencia resuelve.

## 8. Reconciliacion del gap assessment y regla de lenguaje (D) — CONT-003

- [x] 8.1 Corregir en `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` la afirmacion de que `backups/` esta vacio (`...:64,145`) y describir el estado real (dumps de fecha conocida, excluidos de git). Verificacion: `grep -n "vacio" docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` no atribuye vacio a `backups/`.
- [x] 8.2 Reconciliar la descripcion del respaldo y la continuidad con los requisitos BACKUP-005..008 y las brechas 5.29/5.30/5.33/8.13/8.14; actualizar el resumen ejecutivo y el orden de remediacion si la brecha cambia de estado. Verificacion: la seccion de respaldo del assessment menciona backup automatizado, cifrado y con prueba de restauracion.
- [x] 8.3 Verificar la regla de lenguaje en los documentos nuevos y modificados. Verificacion: `grep -rniE "compliant|certificado|cumple (ISO|la Ley|NIST)" docs/seguridad/plan-continuidad.md docs/operational-guide.md docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` no arroja afirmaciones de conformidad.

## 9. Verificacion de integracion y validacion OPSX

- [x] 9.1 Correr los harness de scripts y confirmar que no hay regresiones. Verificacion: `bash scripts/tests/test_backup.sh` (31 assertions, 0 failures), `bash scripts/tests/test_backup_restore.sh` (23 assertions, 0 failures, 0 skipped) y `bash scripts/tests/test_up_preflight.sh` (75 assertions, 0 failures) verdes.
- [x] 9.2 Correr lint backend (`cd App/Backend; ruff check .`) y confirmar que no se toco codigo Python. Verificacion: `All checks passed!` (exit 0), sin errores nuevos.
- [x] 9.3 Validar el change con `openspec validate --strict c-65-backup-continuidad` y `openspec validate --strict --changes`. Verificacion: `Change 'c-65-backup-continuidad' is valid` y `12 passed, 0 failed`.
- [x] 9.4 Revision humana (governance ALTO): confirmar la decision de cifrado y custodia de la passphrase, el encuadre de no-suscripcion offsite/redundancia, la correccion del assessment y la no reintroduccion del alcance SMS/C-67. Verificacion: checklist firmado por el autor.
