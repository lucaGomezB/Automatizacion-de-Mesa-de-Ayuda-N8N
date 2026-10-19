## ADDED Requirements

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
