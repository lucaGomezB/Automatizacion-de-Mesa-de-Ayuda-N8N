## Purpose

Define los objetivos de recuperacion (RTO/RPO) y el plan de continuidad de la informacion del sistema, y establece la reconciliacion de las afirmaciones de respaldo del gap assessment de cumplimiento. Encuadra la copia fuera del host y la redundancia como responsabilidad de la organizacion adoptante, dejando explicito que el repositorio no garantiza disponibilidad ni almacenamiento offsite.

## ADDED Requirements

### Requirement: CONT-001 — Objetivos de recuperacion (RTO/RPO) documentados

El proyecto SHALL incluir `docs/seguridad/plan-continuidad.md` con los objetivos de recuperacion del sistema: un objetivo de tiempo de recuperacion (RTO) y un objetivo de punto de recuperacion (RPO) expresados en horas y alineados con la cadencia diaria del backup. El documento MUST explicitar que los objetivos corresponden al sistema evaluado y MUST NOT declarar garantias de disponibilidad.

#### Scenario: El documento define RTO y RPO

- **WHEN** se lee `docs/seguridad/plan-continuidad.md`
- **THEN** figuran un RTO y un RPO expresados en horas para el sistema evaluado

#### Scenario: Los objetivos son consistentes con la cadencia diaria

- **WHEN** se comparan el RTO/RPO con la frecuencia del backup
- **THEN** el RPO es coherente con una cadencia de backup diaria y el documento no promete una recuperacion mas rapida que la que la cadencia permite

### Requirement: CONT-002 — Plan de continuidad con restauracion y encuadre del adoptante

El documento `docs/seguridad/plan-continuidad.md` SHALL describir el procedimiento de restauracion desde el dump cifrado y SHALL documentar la copia fuera del host y la redundancia basica del PostgreSQL unico como acciones de la organizacion adoptante, NO como infraestructura provista por el repositorio. El documento MUST declarar que el repositorio no puede garantizar la disponibilidad del servicio ni la copia fuera del host. El documento SHALL estar indexado desde `docs/seguridad/README.md`.

#### Scenario: El procedimiento de restauracion queda descrito

- **WHEN** se lee el plan de continuidad
- **THEN** describe los pasos para restaurar el sistema desde un dump de backup cifrado

#### Scenario: La copia offsite y la redundancia se encuadran como accion del adoptante

- **WHEN** se lee el plan de continuidad
- **THEN** la copia fuera del host y la redundancia figuran como responsabilidad de la organizacion adoptante y no como capacidades entregadas por el repositorio

#### Scenario: El documento declara que no garantiza disponibilidad

- **WHEN** se lee el encuadre del plan de continuidad
- **THEN** declara que el repositorio no puede garantizar la disponibilidad ni el almacenamiento fuera del host

#### Scenario: El indice referencia el plan de continuidad

- **WHEN** se revisa `docs/seguridad/README.md`
- **THEN** el plan de continuidad aparece listado y su referencia resuelve a un archivo existente

### Requirement: CONT-003 — Reconciliacion de las afirmaciones de respaldo y regla de lenguaje

El gap assessment (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`) SHALL corregirse para eliminar la afirmacion obsoleta de que `backups/` esta vacio y SHALL describir su estado real (existen dumps de fecha conocida, excluidos de git). El assessment MUST reconciliar su descripcion del respaldo con los requisitos BACKUP-001 a BACKUP-008 y las brechas 5.29, 5.30, 5.33, 8.13 y 8.14. Los documentos nuevos y modificados por este change MUST usar el lenguaje de alineacion y MUST NOT afirmar certificacion ni conformidad ("compliant", "cumple", "certificado").

#### Scenario: El assessment ya no afirma que backups esta vacio

- **WHEN** se lee el gap assessment
- **THEN** no afirma que `backups/` esta vacio y describe su contenido real como excluido de git

#### Scenario: La descripcion del respaldo queda reconciliada

- **WHEN** se lee la seccion de respaldo y continuidad del assessment
- **THEN** describe el respaldo automatizado, cifrado y con prueba de restauracion segun los requisitos BACKUP-005 a BACKUP-007 y las brechas 5.29/5.30/5.33/8.13/8.14

#### Scenario: Se usa el lenguaje de alineacion

- **WHEN** se revisan los documentos nuevos y modificados por el change
- **THEN** usan "alineado con" o "controles mapeados a" y no contienen "compliant", "cumple" ni "certificado" al describir el sistema
