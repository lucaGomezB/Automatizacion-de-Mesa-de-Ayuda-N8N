# backup-scripts Specification

## Purpose
TBD - created by archiving change c-26-corpus-simulado-backup-retencion. Update Purpose after archive.
## Requirements
### Requirement: BACKUP-001 — PostgreSQL backup desde contenedor Docker

El script de backup SHALL ejecutar `pg_dump` desde el contenedor `postgres` definido en `docker-compose.yml`, utilizando el usuario `mesa` y la base de datos `mesa_de_ayuda`.

#### Scenario: Backup exitoso genera archivo SQL
- **WHEN** se ejecuta `scripts/backup.sh` o `scripts/backup.ps1` con los contenedores Docker corriendo
- **THEN** se genera un archivo `backups/backup_YYYY-MM-DD.sql` que contiene un dump completo de la base de datos
- **AND** el comando `docker compose exec -T postgres pg_dump -U mesa mesa_de_ayuda` es invocado exactamente una vez

#### Scenario: Contenedor postgres detenido produce error claro
- **WHEN** se ejecuta el script de backup con el contenedor postgres detenido
- **THEN** el script termina con un mensaje de error indicando que el contenedor no esta corriendo
- **AND** el exit code es distinto de cero

### Requirement: BACKUP-002 — Rotacion de 7 backups diarios

El script SHALL retener exactamente los 7 backups mas recientes y eliminar los anteriores.

#### Scenario: Rotacion con mas de 7 backups existentes
- **WHEN** el directorio `backups/` contiene 10 archivos de backup
- **THEN** despues de ejecutar el script, solo quedan los 7 archivos mas recientes
- **AND** los 3 archivos mas antiguos son eliminados

#### Scenario: Menos de 7 backups, sin eliminacion
- **WHEN** el directorio `backups/` contiene 3 archivos de backup
- **THEN** despues de ejecutar el script, los 3 archivos permanecen y un nuevo backup es agregado
- **AND** no se elimina ningun archivo

### Requirement: BACKUP-003 — Idempotencia y seguridad

El script SHALL ser idempotente: ejecuciones repetidas en el mismo dia no deben producir archivos duplicados ni corromper backups existentes.

#### Scenario: Ejecucion repetida el mismo dia
- **WHEN** se ejecuta el script dos veces el mismo dia calendario
- **THEN** el segundo backup sobreescribe el archivo del mismo dia si existe
- **AND** el contador de archivos en `backups/` no aumenta por encima del numero de dias con backup

#### Scenario: Directorio backups no existe
- **WHEN** el directorio `backups/` no existe
- **THEN** el script lo crea automaticamente antes de ejecutar el dump
- **AND** el backup se completa exitosamente

### Requirement: BACKUP-004 — Equivalencia funcional Bash y PowerShell

Ambos scripts (Bash y PowerShell) MUST producir resultados equivalentes: mismo formato de archivo, misma rotacion, mismo comportamiento ante errores.

#### Scenario: Mismo dump SQL en ambos SO
- **WHEN** se ejecuta `backup.sh` en Linux y `backup.ps1` en Windows contra la misma base de datos
- **THEN** ambos scripts generan un dump SQL valido
- **AND** la estructura SQL de ambos dumps es equivalente (mismas tablas, mismos datos)

