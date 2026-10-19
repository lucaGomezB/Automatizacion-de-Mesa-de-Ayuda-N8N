# backup-scripts Specification

## Purpose

Define el respaldo de PostgreSQL mediante `pg_dump` desde el contenedor Docker, su cifrado en reposo (AES-256) con una passphrase de despliegue, su rotacion a 7 archivos y su verificacion de restauracion reproducible, con paridad funcional entre los scripts Bash y PowerShell.

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

### Requirement: BACKUP-005 — Cifrado del dump en reposo

Los scripts de backup (`scripts/backup.sh` y `scripts/backup.ps1`) SHALL producir el dump de PostgreSQL CIFRADO en reposo con el algoritmo AES-256 (modo CBC, derivacion de clave `pbkdf2` con sal). La passphrase SHALL obtenerse de un secreto de configuracion de despliegue (variable de entorno) y MUST NOT residir en el repositorio ni dentro de `backups/`. El script MUST abortar con codigo de salida distinto de cero y un mensaje claro cuando la passphrase no este disponible o el cifrado falle. Tras un cifrado exitoso, el dump en texto plano MUST NOT quedar persistido en `backups/`. La rotacion definida en BACKUP-002 SHALL aplicarse sobre los archivos cifrados.

#### Scenario: Backup exitoso produce un dump cifrado en reposo

- **WHEN** se ejecuta el script de backup con la passphrase disponible y el contenedor postgres corriendo
- **THEN** se genera un archivo de backup cifrado que NO es legible como SQL en texto plano
- **AND** el dump en texto plano no permanece en `backups/`

#### Scenario: Falta la passphrase produce error claro y no persiste un dump en claro

- **WHEN** se ejecuta el script de backup sin la passphrase configurada
- **THEN** el script termina con exit code distinto de cero y un mensaje que indica que falta la passphrase
- **AND** no queda ningun dump en texto plano en `backups/`

#### Scenario: La rotacion opera sobre archivos cifrados

- **WHEN** el directorio `backups/` contiene mas de 7 backups cifrados
- **THEN** despues de ejecutar el script solo quedan los 7 mas recientes
- **AND** los backups mas antiguos son eliminados

#### Scenario: Equivalencia funcional Bash y PowerShell con el cifrado

- **WHEN** se ejecuta `backup.sh` en Linux y `backup.ps1` en Windows contra la misma base de datos
- **THEN** ambos producen un dump cifrado valido con el mismo formato y la misma rotacion
- **AND** ambos fallan de forma equivalente cuando falta la passphrase

### Requirement: BACKUP-006 — Automatizacion mediante programador versionado

El proyecto SHALL incluir un archivo de programacion VERSIONADO en el repositorio (entrada de `cron` o unidad `systemd` timer) que dispare el backup diario de forma automatica y registre su salida en un archivo de log. El archivo de programacion SHALL quedar bajo `scripts/` y MUST NOT incorporar secretos (passphrase ni credenciales) en su contenido. Con el programador instalado, la cadencia diaria del backup MUST NOT depender de la ejecucion manual del script.

#### Scenario: El archivo de programacion versionado existe

- **WHEN** se inspecciona `scripts/`
- **THEN** existe un archivo de programacion (cron o systemd timer) que invoca el backup diario y registra su salida en un log

#### Scenario: El programador dispara el backup diario sin intervencion manual

- **WHEN** el programador esta instalado en el host
- **THEN** el backup se ejecuta segun la cadencia diaria sin requerir que un operador lo dispare a mano

#### Scenario: El archivo versionado no contiene secretos

- **WHEN** se revisa el contenido del archivo de programacion
- **THEN** no contiene la passphrase de cifrado ni credenciales

### Requirement: BACKUP-007 — Prueba de restauracion reproducible

El proyecto SHALL incluir un script VERSIONADO de prueba de restauracion (`scripts/backup-restore-test.sh`) que descifre un dump de backup reciente, lo restaure en una base de datos DESCARTABLE y verifique que las tablas y el conteo de filas esperados existen. El script MUST NOT restaurar sobre la base de datos de la aplicacion: SHALL comparar el nombre de la base destino contra el de la base de la aplicacion y abortar con exit code distinto de cero si coinciden. La prueba SHALL ser reproducible y su procedimiento SHALL quedar documentado.

#### Scenario: Restauracion exitosa en una base descartable

- **WHEN** se ejecuta el script de prueba de restauracion sobre un dump de backup valido
- **THEN** el dump se descifra y se restaura en una base descartable
- **AND** el script confirma que existen las tablas esperadas y que el conteo de filas es el esperado

#### Scenario: La guarda impide restaurar sobre la base de la aplicacion

- **WHEN** el script de prueba de restauracion apunta a un nombre de base igual al de la base de la aplicacion
- **THEN** el script aborta con exit code distinto de cero antes de cualquier operacion destructiva

#### Scenario: Un dump no usable falla de forma ruidosa

- **WHEN** el script de prueba de restauracion recibe un dump inexistente, ilegible o que no puede descifrarse
- **THEN** el script termina con exit code distinto de cero y un mensaje que identifica la causa

### Requirement: BACKUP-008 — Snapshot de volumenes Docker documentado

El proyecto SHALL documentar el procedimiento de snapshot de los volumenes Docker (`postgres` y `n8n`) como una accion de la organizacion adoptante y SHALL dejar explicito que NO incorpora un generador versionado de esos snapshots. El respaldo canonico y restaurable SHALL ser el dump logico de `pg_dump` cubierto por BACKUP-001, BACKUP-005 y BACKUP-007; el snapshot de volumenes es un complemento opcional del adoptante.

#### Scenario: El procedimiento de snapshot queda documentado

- **WHEN** se revisa la documentacion de respaldo
- **THEN** describe el procedimiento de snapshot de los volumenes Docker `postgres` y `n8n`

#### Scenario: Se declara explicitamente la ausencia de generador versionado

- **WHEN** se revisa la documentacion de respaldo
- **THEN** declara que los snapshots de volumenes no cuentan con un generador versionado y que su generacion es manual o del adoptante

#### Scenario: El respaldo canonico es el dump logico

- **WHEN** se revisa la documentacion de respaldo
- **THEN** establece que el respaldo restaurable de referencia es el dump logico de `pg_dump`

