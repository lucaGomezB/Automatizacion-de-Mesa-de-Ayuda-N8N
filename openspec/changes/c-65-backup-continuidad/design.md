## Context

Ver `proposal.md` (Why y What Changes) para la motivacion. Estado y restricciones que condicionan el diseno:

- `scripts/backup.sh` y `scripts/backup.ps1` ejecutan `pg_dump` desde el contenedor `mesa_local-postgres-1`, escriben un `.sql` en texto plano en `backups/` y rotan a 7 archivos por fecha (`RETENTION_COUNT=7`), con paridad funcional bash/PowerShell (spec vigente `openspec/specs/backup-scripts/spec.md`, BACKUP-001..004). El nombre del dump es `backup_YYYY-MM-DD.sql` (un archivo por dia; repetir el mismo dia sobreescribe).
- No hay cron, systemd timer ni scheduler: el backup es manual (`docs/por_implementar.md` §4.4). `docs/operational-guide.md:340-353` YA documenta un cron y un Task Scheduler como receta, pero NO versiona el archivo; `:362-389` documenta restauracion (SQL y volumen) sin prueba periodica.
- `backups/` contiene dumps reales del 2026-10-09 (`backup_2026-10-09.sql`, `mesa_de_ayuda_20261009T141330.sql`) y cuatro `.tgz` de volumenes generados de forma manual; esta gitignored salvo `.gitkeep`. El gap assessment afirma que `backups/` esta vacio (`...:64,145`): afirmacion obsoleta a corregir.
- El proposito de los scripts (spec vigente) quedó como `TBD - created by archiving change c-26...`; este change lo corrige editando el `## Purpose` de la spec principal (D7), ademas del delta de requisitos BACKUP-005..008.
- Gestion de secretos vigente: `.env` + variables de entorno (`docs/seguridad/gestion-secretos-y-rotacion.md`); no hay gestor de secretos dedicado. La passphrase del cifrado de backup se alinea con esa postura (secreto de despliegue).
- El stack es de desarrollo local; el repositorio puede cerrar lo (T) tecnico y lo (D) documental, no lo (O) organizacional (offsite real, redundancia real).

### Referencias de lectura (Leer antes)

- `docs/cumplimiento/plan-cambios-cumplimiento.md` §2-§4 (fila C-65; orden y relacion con el resto del plan).
- `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` (brechas 8.13, 8.14, 5.29, 5.30, 5.33 y afirmaciones de `backups/` a corregir).
- `docs/cumplimiento/marco-legal-ar-2026.md` (encuadre de lenguaje y alcance).
- `docs/seguridad/gestion-secretos-y-rotacion.md` (postura de secretos y comando de generacion de claves).
- `docs/operational-guide.md` (restauracion SQL y de volumenes; recetas de cron y Task Scheduler).
- `openspec/specs/backup-scripts/spec.md` (BACKUP-001..004) y `scripts/backup.sh` / `scripts/backup.ps1`.
- `docs/Tesis/v9 (IA)/paper/sections/11-aspectos-legales.tex:24` y `05-arquitectura.tex:25,81` (afirmacion en presente que este change hace verificable).

## Goals / Non-Goals

**Goals:**

- Cifrar el dump en reposo con un esquema simple, reproducible y custodiado por un secreto de despliegue, preservando la rotacion y la paridad bash/PowerShell.
- Versionar el programador del backup (cron y/o systemd timer) para eliminar la ejecucion manual.
- Entregar una prueba de restauracion reproducible y segura que verifique de verdad que el dump es restaurable.
- Documentar RTO/RPO, plan de continuidad, copia offsite y redundancia como accion del adoptante.
- Corregir la afirmacion obsoleta de `backups/` vacio y reconciliar las brechas de respaldo del assessment.

**Non-Goals:**

- Infraestructura offsite real, replica o alta disponibilidad: son accion del adoptante.
- Certificacion ISO/NIST, contratos con proveedores de nube, alcance SMS / C-67.
- Generador versionado de snapshots de volumenes Docker (D5: se documenta).
- Centralizacion de logs ni monitoreo (fuera del alcance del plan C-65).

## Decisions

### D1 — Cifrado del dump con openssl AES-256 y passphrase de despliegue

`scripts/backup.sh` y `scripts/backup.ps1` producen el dump y lo cifran en reposo con `openssl enc -aes-256-cbc -pbkdf2 -salt` usando una passphrase tomada de la variable de entorno `BACKUP_ENCRYPTION_PASSPHRASE`. El archivo resultante usa la extension `.sql.enc` (o `.enc`), y la rotacion (BACKUP-002) opera sobre los archivos cifrados. Si la passphrase falta, el script aborta antes de dejar un dump en claro.

- **Alternativa A (descartada): GPG/PGP.** Mayor friccion de custodia de claves (par de claves, keyring) y peor reproducibilidad multiplataforma que una passphrase; el objetivo es simplicidad y reproducibilidad.
- **Alternativa B (descartada): cifrado por el propio PostgreSQL.** `pg_dump` no cifra la salida a un archivo plano; opciones de cifrado de transporte no aplican al artefacto en reposo.
- **Alternativa C (descartada): clave en un archivo dentro del repositorio.** Contradice la higiene de secretos y publicaria el material en el repositorio.
- **Elegida: openssl AES-256-CBC + `pbkdf2` + sal, passphrase de un secreto de despliegue.** Reproducible en Linux y Windows (OpenSSL disponible en ambos), sin material de clave en el repositorio. Se documenta el comando de generacion de la passphrase.

### D2 — Automatizacion: archivo de programacion versionado

Se agrega al repositorio un archivo de programacion bajo `scripts/` que dispara el backup diario y registra su salida en un log. Se versiona una entrada de `cron` como mecanismo principal (disponible en el host tipico) y se documenta la unidad `systemd` `service`+`timer` como alternativa equivalente. El archivo NO contiene secretos: la passphrase llega por el entorno del host al momento de ejecutar.

- **Alternativa A (descartada): solo documentar la receta del cron.** Es el estado actual (`docs/operational-guide.md:340-353`) y es justamente lo que la tesis no puede evidenciar; no cierra la brecha de automatizacion.
- **Alternativa B (descartada): workflow N8N como scheduler.** Acopla el respaldo al motor de orquestacion y a su disponibilidad; si N8N cae, el respaldo tambien.
- **Elegida: archivo de programacion versionado (cron principal, systemd timer documentado).** Versionado en el repo, reproducible y auditable; independiente de N8N.

### D3 — Prueba de restauracion en base descartable con guarda por nombre

`scripts/backup-restore-test.sh` descifra el dump mas reciente, lo restaura en una base de datos DESCARTABLE y verifica tablas y conteo de filas esperados. Reutiliza la logica de guarda de la suite de integracion: compara el nombre de la base destino contra el de la base de la aplicacion (derivado de `DATABASE_URL`) y aborta si coinciden, salvo escape hatch explicito. El procedimiento queda documentado.

- **Alternativa A (descartada): restaurar sobre la base de la aplicacion.** Destructivo; inaceptable.
- **Alternativa B (descartada): solo verificar el tamano o el encabezado del archivo.** No prueba que el dump sea restaurable; es exactamente el defecto que este change cierra (no hay prueba periodica).
- **Alternativa C (descartada): restaurar en la misma instancia compartiendo un esquema alterno.** Mayor complejidad y riesgo residual; una base descartable dedicada es mas simple y segura.
- **Elegida: base descartable dedicada + guarda por nombre + verificacion de tablas/filas.**

### D4 — Offsite, redundancia, RTO/RPO y continuidad: documentado, no implementado

`docs/seguridad/plan-continuidad.md` define RTO/RPO y describe el procedimiento de restauracion, y documenta la copia fuera del host y la redundancia del PostgreSQL unico como accion de la organizacion adoptante. El documento declara que el repositorio no garantiza disponibilidad ni offsite.

- **Alternativa A (descartada): implementar replica/HA en `docker-compose.yml`.** Cambio de infraestructura de alto esfuerzo que el stack local de tesis no justifica y que no puede validarse en este entorno.
- **Elegida: documentar con encuadre de alineacion.** Cierra las brechas 5.29/5.30/8.14 como (D) sin fingir infraestructura inexistente.

### D5 — Snapshot de volumenes Docker: documentado, sin generador versionado

El procedimiento de snapshot de los volumenes `postgres` y `n8n` (hoy manual, artefactos `.tgz` en `backups/`) se DOCUMENTA como accion del adoptante. NO se agrega un generador versionado.

- **Alternativa A (descartada): agregar `scripts/backup-volumes.sh` con paridad PowerShell.** Suma superficie y obliga a extender BACKUP-004 (paridad) sin aportar garantia de restauracion adicional: el respaldo canonico restaurable es el dump logico de `pg_dump`, y `n8n/workflow.json` ya esta versionado en el repositorio.
- **Elegida: documentar el procedimiento y declarar explicitamente la ausencia de generador versionado.** Mantiene el delta minimo y coherente.

### D6 — Correccion del gap assessment y regla de lenguaje

Se corrige la afirmacion obsoleta de que `backups/` esta vacio (`...:64,145`) y se reconcilia la descripcion del respaldo (automatizado, cifrado, con prueba de restauracion) con los requisitos BACKUP-005..007 y las brechas 5.29/5.30/5.33/8.13/8.14. Todo documento nuevo o modificado usa lenguaje de alineacion; se prohibe "compliant"/"cumple"/"certificado".

### D7 — Purpose real en la spec principal de `backup-scripts`

Se reemplaza el `## Purpose` de `openspec/specs/backup-scripts/spec.md` —hoy `TBD - created by archiving change c-26-corpus-simulado-backup-retencion. Update Purpose after archive.`— por un proposito real de una sola frase. Se hace en este change, no en un change aparte, porque C-65 ya MODIFICA la capability `backup-scripts` (BACKUP-005..008).

- **Razon**: las specs principales (`openspec/specs/`) son la fuente de verdad del comportamiento vigente, y el archivado de un change NO reescribe el `## Purpose`; nada garantiza que un change posterior vuelva a tocar esta capability, por lo que el residuo de c-26 quedaria indefinidamente. Corregirlo al modificar la spec es la unica via determinista de limpiarlo.
- **Alternativa descartada**: dejarlo como esta y esperar un change futuro de `backup-scripts` (indeterminado; el TBD es un defecto de la fuente de verdad). Tambien descartada la correccion manual fuera de todo change (rompe la trazabilidad OPSX).
- **Nota de alcance**: es una edicion de documentacion (D), sin logica de produccion ni cambio de contrato de requisitos. El delta de C-65 no re-declara el `## Purpose`; la edicion se hace directamente sobre la spec principal.

## Risks / Trade-offs

- [Perdida de la passphrase inhabilita la restauracion] → Custodia documentada como secreto de despliegue; la passphrase se conserva FUERA de `backups/`; runbook de custodia en el plan de continuidad.
- [El cifrado rompe la rotacion o la paridad bash/PowerShell] → La rotacion opera sobre archivos cifrados; tests de rotacion y equivalencia (BACKUP-002/004) se amplian al archivo cifrado.
- [Un dump cifrado que no se puede descifrar o restaurar] → La prueba de restauracion (D3/BACKUP-007) descifra y restaura en base descartable; falla ruidosamente si el dump no es usable.
- [La prueba de restauracion toca la base de la aplicacion] → Guarda por nombre de base; aborta antes de cualquier operacion destructiva.
- [Documentar offsite/redundancia como si existieran] → Encuadre explicito y scenario de spec que lo prohibe; test de contenido.
- [Corregir el assessment introduce nuevas inconsistencias] → Tarea de reconciliacion y validacion de consistencia del documento completo.
- [La cadencia diaria deja una ventana de perdida de hasta 24 h] → Se declara en el RPO (D4); subir la cadencia es posible sin cambiar el contrato, pero no es objetivo de este change.

## Migration Plan

- **Scripts (D1, D2, D3)**: cambios aditivos sobre `backup.sh`/`backup.ps1` (cifrado) mas dos archivos nuevos (programador y prueba de restauracion). Sin migracion de datos. Los dumps existentes en claro permanecen hasta su rotacion natural; se documenta la transicion. Rollback = revertir el commit (vuelve al dump en claro; justificar por governance).
- **Documentacion (D4, D5, D6)**: archivos nuevos (`plan-continuidad.md`) y ediciones puntuales (`operational-guide.md`, `.env.example`, `gap-assessment`, `docs/seguridad/README.md`). Rollback = revertir el commit.
- **Governance**: revertir D1/D6 reintroduce el hallazgo de dump en claro con PII (5.33/8.13) y la afirmacion obsoleta del assessment; cualquier rollback debe quedar justificado.

## Open Questions

- **OQ1 — Snapshot de volumenes (ACEPTADO por el autor)**: D5 confirmado; se documenta el procedimiento y no se agrega generador versionado.
- **OQ2 — Fuente de la passphrase (ACEPTADO por el autor)**: D1 confirmado; `BACKUP_ENCRYPTION_PASSPHRASE` via variable de entorno/secreto de despliegue.
- **OQ3 — Valores finales de RTO/RPO**: CONFIRMADO por el autor: RTO 24 h y RPO 24 h (alineados con la cadencia diaria). Cerrado; no cambia el enfoque ni el desglose de tareas.
- **OQ4 — Mecanismo del programador en el host objetivo**: cron como principal y systemd timer documentado. Si el host del adoptante no tiene cron, se prioriza el timer; no cambia el contrato de la spec (solo cual archivo se instala).
