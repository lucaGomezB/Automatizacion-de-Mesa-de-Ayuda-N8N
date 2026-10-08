# foundation-environment — Delta Spec

## MODIFIED Requirements

### Requirement: ENV-001 — N8N configurado con retencion de ejecuciones

El servicio N8N en `docker-compose.yml` SHALL incluir variables de entorno que configuren la poda automatica de datos de ejecucion con antiguedad mayor a 30 dias (720 horas). La exposicion de red del servicio N8N (puertos publicados, redes y credenciales de servicios de datos) PUEDE cambiar por un change de hardening de infraestructura sin que la retencion se altere.

#### Scenario: Variables de retencion presentes en compose

- **WHEN** se inspecciona la seccion `services.n8n.environment` en `docker-compose.yml`
- **THEN** la variable `EXECUTIONS_DATA_PRUNE` tiene el valor `"true"`
- **AND** la variable `EXECUTIONS_DATA_MAX_AGE` tiene el valor `"720"`

#### Scenario: Resto de la configuracion N8N sin cambios

- **WHEN** se inspeccionan el resto de las variables de entorno del servicio N8N
- **THEN** las variables de negocio (`BACKEND_URL`, `N8N_BASIC_AUTH_ACTIVE`, `COST_GUARD_SHARED_SECRET`, etc.) permanecen sin modificacion
- **AND** los volumes del servicio N8N no se alteran

#### Scenario: La exposicion de red puede cambiar sin afectar la retencion

- **WHEN** un change de hardening de infraestructura (c-62) modifica los puertos publicados, las redes o las credenciales de servicios de datos del servicio N8N
- **THEN** la retencion de ejecuciones (`EXECUTIONS_DATA_PRUNE`, `EXECUTIONS_DATA_MAX_AGE`) permanece vigente
