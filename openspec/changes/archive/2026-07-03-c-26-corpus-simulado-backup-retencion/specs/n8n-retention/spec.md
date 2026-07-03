## ADDED Requirements

### Requirement: RETENTION-001 — Poda automatica de datos de ejecucion

El sistema SHALL configurar N8N para eliminar automaticamente los datos de ejecucion con una antiguedad mayor a 30 dias (720 horas), mediante variables de entorno en el archivo `docker-compose.yml`.

#### Scenario: Configuracion aplicada al iniciar N8N
- **WHEN** se ejecuta `docker compose up -d n8n`
- **THEN** el contenedor N8N inicia con las variables `EXECUTIONS_DATA_PRUNE=true` y `EXECUTIONS_DATA_MAX_AGE=720`
- **AND** N8N programa la poda periodica de ejecuciones antiguas

#### Scenario: Datos de ejecucion preservados dentro del periodo
- **WHEN** una ejecucion de workflow ocurre hoy
- **THEN** sus datos de ejecucion se conservan durante al menos 30 dias calendario
- **AND** no son eliminados por el proceso de poda antes de ese plazo

### Requirement: RETENTION-002 — Configuracion declarativa en docker-compose

La configuracion de retencion MUST estar declarada en el archivo `docker-compose.yml` bajo la seccion `services.n8n.environment`, sin scripts externos ni cron jobs.

#### Scenario: Variables presentes en el compose
- **WHEN** se inspecciona `docker-compose.yml`
- **THEN** la seccion `services.n8n.environment` contiene las variables `EXECUTIONS_DATA_PRUNE` y `EXECUTIONS_DATA_MAX_AGE`
- **AND** los valores son cadenas segun el formato esperado por N8N

#### Scenario: Sin dependencia de scripts externos
- **WHEN** se levanta el stack con `docker compose up -d`
- **THEN** la retencion de 30 dias funciona sin requerir un script de limpieza ni una tarea cron
