## MODIFIED Requirements

### Requirement: DOC-001 — Guia operativa referencia scripts de backup

La guia operativa (`docs/operational-guide.md`) SHALL incluir referencias a los scripts automatizados de backup (`scripts/backup.sh` y `scripts/backup.ps1`) como metodo recomendado para backups diarios, reemplazando el comando manual de cron documentado en la seccion 3.

#### Scenario: Seccion de backup referencia scripts
- **WHEN** se lee la seccion 3 (Backup y restauracion de PostgreSQL) de `docs/operational-guide.md`
- **THEN** el documento referencia los scripts `scripts/backup.sh` y `scripts/backup.ps1`
- **AND** describe como configurar la ejecucion automatica via cron (Linux/macOS) o Task Scheduler (Windows)
- **AND** incluye el comando de ejemplo para ambos entornos

#### Scenario: Comando manual permanece documentado
- **WHEN** se lee la seccion 3 de la guia operativa
- **THEN** el comando `docker compose exec postgres pg_dump` sigue documentado como alternativa manual
- **AND** la documentacion de restauracion no sufre cambios

### Requirement: DOC-002 — Tesis v8 K8s language verified

La tesis en version 8 (LaTeX) SHALL mantener el lenguaje suavizado sobre Kubernetes: "preparados para migracion" (futuro), no "mediante un cluster Kubernetes" (presente). Este requisito es de VERIFICACION unicamente.

#### Scenario: Lenguaje K8s es futuro, no presente
- **WHEN** se inspecciona `docs/Tesis/v8 (IA)/paper/sections/06-implementacion.tex` linea 8
- **THEN** el texto contiene "preparados para migracion a un cluster Kubernetes~1.30"
- **AND** NO contiene frases que afirmen que Kubernetes esta desplegado actualmente ("mediante un cluster", "se despliega en Kubernetes")

## ADDED Requirements

### Requirement: DOC-003 — Anexo G referencia scripts de backup

La documentacion operativa del Anexo G en la tesis SHALL mencionar la existencia de scripts automatizados de backup con retencion de 7 dias.

#### Scenario: Anexo G menciona backup automatizado
- **WHEN** se lee la seccion del Anexo G en la tesis v8
- **THEN** el texto menciona que existen scripts de backup automatizados (`backup.sh` y `backup.ps1`)
- **AND** describe la politica de retencion (7 backups diarios)
