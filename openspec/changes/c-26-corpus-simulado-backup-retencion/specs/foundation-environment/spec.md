## MODIFIED Requirements

### Requirement: ENV-001 — N8N configurado con retencion de ejecuciones

El servicio N8N en `docker-compose.yml` SHALL incluir variables de entorno que configuren la poda automatica de datos de ejecucion con antiguedad mayor a 30 dias (720 horas).

#### Scenario: Variables de retencion presentes en compose
- **WHEN** se inspecciona la seccion `services.n8n.environment` en `docker-compose.yml`
- **THEN** la variable `EXECUTIONS_DATA_PRUNE` tiene el valor `"true"`
- **AND** la variable `EXECUTIONS_DATA_MAX_AGE` tiene el valor `"720"`

#### Scenario: Resto de la configuracion N8N sin cambios
- **WHEN** se inspeccionan el resto de las variables de entorno del servicio N8N
- **THEN** las variables existentes (`N8N_BASIC_AUTH_ACTIVE`, `BACKEND_URL`, `QUEUE_BULL_REDIS_HOST`, etc.) permanecen sin modificacion
- **AND** los volumes, puertos y dependencias del servicio N8N no se alteran
