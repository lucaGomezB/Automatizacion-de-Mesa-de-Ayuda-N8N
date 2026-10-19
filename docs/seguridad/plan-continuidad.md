# Plan de continuidad y objetivos de recuperacion

| Campo | Contenido |
|-------|-----------|
| Control mapeado | ISO/IEC 27002:2022 5.29 (seguridad de la informacion durante la disrupcion), 5.30 (preparacion de las TIC para la continuidad), 8.13 (respaldo de informacion) y 8.14 (redundancia); funcion NIST CSF 2.0 Recuperar (RC); requisitos CONT-001 y CONT-002 del change `c-65-backup-continuidad` |
| Estado | v1 — aprobada por el autor el 2026-10-19 (governance ALTO) |
| Alcance | Objetivos de recuperacion (RTO/RPO), procedimiento de restauracion desde el dump cifrado, copia fuera del host y redundancia como accion del adoptante, y custodia de la passphrase de backup. No define la infraestructura de un despliegue productivo ni sus SLA |
| Encuadre | Stack de desarrollo local (`docker-compose.yml`, `name: mesa_local`). El repositorio NO garantiza disponibilidad ni copia fuera del host; esos controles son responsabilidad de la organizacion adoptante (O) |
| Aviso de lenguaje | Alineado con ISO/IEC 27002:2022 5.29, 5.30, 8.13 y 8.14. No constituye certificacion ni auditoria |

## 1. Proposito

Dejar verificable la continuidad de la informacion del sistema: definir los
objetivos de recuperacion (RTO/RPO), describir el procedimiento de restauracion
desde el dump de backup cifrado y delimitar que parte cierra el repositorio (la
cadena de respaldo automatico, cifrado y con prueba de restauracion) y que parte
es responsabilidad de la organizacion adoptante (la copia fuera del host y la
redundancia del PostgreSQL unico).

El repositorio **no garantiza la disponibilidad del servicio** ni la
**existencia de una copia fuera del host**. Este documento describe el objetivo y
el procedimiento; su eficacia real depende de que el adoptante los opere y de la
infraestructura donde se despliegue.

## 2. Objetivos de recuperacion (RTO/RPO)

| Objetivo | Valor | Definicion | Fundamento |
|----------|-------|------------|------------|
| RTO (Recovery Time Objective) | 24 h | Tiempo objetivo para restablecer el servicio tras una disrupcion | Alineado con una operacion de recuperacion manual asistida sobre el stack local |
| RPO (Recovery Point Objective) | 24 h | Ventana maxima de perdida de datos aceptable | Alineado con la cadencia diaria del backup versionado (`scripts/backup-schedule.cron`) |

Notas:

- Los valores fueron **confirmados por el autor** (OQ3 del change) y son
  coherentes con la cadencia diaria del backup: con un respaldo por dia, una
  disrupcion puede perder hasta 24 h de datos, que es exactamente el RPO.
- El RTO depende del operador y del entorno; el repositorio aporta los
  procedimientos y los scripts, no una capacidad de recuperacion medida. Subir la
  cadencia del backup reduciria el RPO, pero esta fuera del alcance de este
  change.
- Los objetivos corresponden al sistema evaluado (stack de desarrollo local) y
  NO constituyen una garantia contractual de disponibilidad ni de tiempo de
  recuperacion.

## 3. Procedimiento de restauracion desde el dump cifrado

El respaldo canonico y restaurable es el **dump logico de `pg_dump`** producido
por `scripts/backup.sh` (BACKUP-001), cifrado en reposo con AES-256 (BACKUP-005).
Su restauracion consta de tres pasos: descifrar, restaurar y verificar.

### 3.1 Descifrar el dump mas reciente

```bash
# El backup mas reciente es backups/backup_YYYY-MM-DD.sql.enc
LATEST="$(ls -1t backups/backup_*.sql.enc | head -n 1)"

# Descifrar a un archivo temporal en texto plano (se elimina al finalizar)
BACKUP_ENCRYPTION_PASSPHRASE="<secreto-de-despliegue>" \
  openssl enc -d -aes-256-cbc -pbkdf2 \
    -pass env:BACKUP_ENCRYPTION_PASSPHRASE \
    -in "$LATEST" -out /tmp/restore.sql
```

Una passphrase incorrecta o un archivo corrupto hacen fallar `openssl` de forma
ruidosa (exit distinto de cero), sin producir un dump en claro utilizable.

### 3.2 Restaurar sobre PostgreSQL

```bash
# 1. Asegurar el contenedor de PostgreSQL
docker compose up -d postgres

# 2. Restaurar el dump (sobreescribe los datos existentes)
docker compose exec -T postgres psql -U mesa mesa_de_ayuda < /tmp/restore.sql

# 3. Eliminar el texto plano temporal
rm -f /tmp/restore.sql
```

> **Precaucion**: restaurar sobreescribe los datos del destino. Antes de
> restaurar en un entorno con datos, tomar un respaldo previo. Nunca dejar el
> dump descifrado en disco mas tiempo del necesario.

### 3.3 Verificar antes de confiar en el respaldo

Antes de una restauracion real sobre la base de la aplicacion, conviene probar la
cadena de restauracion en una base DESCARTABLE. El procedimiento de prueba esta
documentado y automatizado; ver §4.

## 4. Prueba de restauracion reproducible

La prueba de restauracion (`scripts/backup-restore-test.sh`, BACKUP-007) descifra
el dump cifrado mas reciente, lo restaura en una base DESCARTABLE y verifica que
las tablas esperadas existan con un conteo de filas plausible. Prueba que el
respaldo es **realmente restaurable**, no solo que existe.

El procedimiento completo —creacion de la base descartable, guarda por nombre y
escape hatch `TEST_PG_ALLOW_APP_DB`— esta documentado en
[`../operational-guide.md`](../operational-guide.md) §3.4. En resumen:

```bash
BACKUP_ENCRYPTION_PASSPHRASE="<secreto-de-despliegue>" \
DATABASE_URL="postgresql+asyncpg://mesa:<password>@postgres:5432/mesa_de_ayuda" \
RESTORE_DB_NAME="mesa_de_ayuda_restore_test" \
bash scripts/backup-restore-test.sh
```

Guarda de seguridad: antes de cualquier operacion destructiva el script compara
el nombre de la base destino contra el de la aplicacion (derivado de
`DATABASE_URL`) y aborta si coinciden. `TEST_PG_ALLOW_APP_DB=1` es el UNICO
escape hatch y se reserva a entornos efimeros dedicados; nunca contra una base
con datos reales.

Se recomienda ejecutar esta prueba de forma periodica (por ejemplo, tras cada
rotacion de clave o cambio de infraestructura) para evidenciar que la cadena
backup -> cifrado -> restauracion sigue funcionando.

## 5. Copia fuera del host y redundancia (accion del adoptante)

Los siguientes controles son responsabilidad de la **organizacion adoptante (O)**.
El repositorio los documenta; **no** los implementa ni los garantiza.

- **Copia fuera del host (offsite)**: el adoptante es responsable de copiar los
  dumps cifrados (`backups/*.sql.enc`) a un destino fuera del host que los
  genera, con su propia custodia y retencion. El repositorio no realiza ni
  garantiza ninguna copia offsite.
- **Redundancia basica del PostgreSQL unico**: el stack usa un unico PostgreSQL
  (`docker-compose.yml`). El adoptante es responsable de aportar la redundancia
  (segunda instancia, replica o proveedor gestionado) alineada con su criticidad
  y con los objetivos de recuperacion de §2. El repositorio no incluye replica ni
  alta disponibilidad.

Encuadre explicito: el repositorio corresponde a un **stack de desarrollo local**
y no puede garantizar la disponibilidad del servicio, la existencia de una copia
fuera del host, ni la redundancia de la base de datos. Cualquier afirmacion de
continuidad en produccion depende de que el adoptante implemente estos controles
en su entorno.

## 6. Custodia de la passphrase de backup

La passphrase de cifrado del dump (`BACKUP_ENCRYPTION_PASSPHRASE`) es un **secreto
de despliegue**, alineado con la postura de gestion de secretos de
[`gestion-secretos-y-rotacion.md`](gestion-secretos-y-rotacion.md).

Reglas de custodia:

- La passphrase se conserva **FUERA de `backups/`** y nunca se versiona en el
  repositorio. Se aporta por el entorno del host al ejecutar el backup (variable
  de entorno o `EnvironmentFile` externo, por ejemplo `/etc/mesa/backup.env`).
- Se documenta su generacion en `App/Backend/.env.example` (por ejemplo,
  `openssl rand -base64 32`).
- **La perdida de la passphrase inhabilita la restauracion** de los dumps
  cifrados con ella: la custodia segura y respaldada de la passphrase es parte
  del procedimiento de continuidad.
- La rotacion de la passphrase es un control del adoptante y debe coordinarse
  con la retencion del backup (un dump cifrado con una passphrase retirada solo
  se restaura mientras esa passphrase se conserve). Ver
  `gestion-secretos-y-rotacion.md` para el patron de rotacion con solapamiento.

## 7. Verificacion

- La verificacion de este change es **MANUAL** (governance ALTO): la lista de
  comprobacion de `openspec/changes/c-65-backup-continuidad/tasks.md`, la
  revision del autor sobre el encuadre de no-garantia y de que offsite y
  redundancia figuran como accion del adoptante, y
  `openspec validate --strict c-65-backup-continuidad`.
- La prueba de restauracion (§4) es la evidencia tecnica periodica de que la
  cadena de respaldo es restaurable.
- Revision sugerida del documento: anual, o ante cambio de infraestructura,
  cadencia de backup o criticidad del sistema.

## 8. Fuentes internas

- `docs/operational-guide.md` §3 (backup, restauracion, snapshot de volumenes y
  prueba de restauracion).
- `docs/seguridad/gestion-secretos-y-rotacion.md` — custodia y rotacion de
  secretos.
- `scripts/backup.sh`, `scripts/backup-restore-test.sh`,
  `scripts/backup-schedule.cron` — cadena de respaldo, cifrado, automatizacion y
  prueba de restauracion.
- `openspec/specs/backup-scripts/spec.md` — requisitos BACKUP-001 a BACKUP-008.
- `openspec/changes/c-65-backup-continuidad/{proposal.md,design.md,tasks.md}`.
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` — brechas 5.29,
  5.30, 8.13 y 8.14.
