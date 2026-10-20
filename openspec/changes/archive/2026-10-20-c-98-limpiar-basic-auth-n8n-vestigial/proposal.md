## Why

`N8N_BASIC_AUTH_*` es VESTIGIAL: n8n elimino Basic Auth en su version 1.0 y este proyecto fija `n8nio/n8n:2.11.2`, por lo que las tres variables no tienen ningun efecto. La verificacion empirica contra el stack en ejecucion confirma que `GET /rest/workflows` y `GET /rest/credentials` responden 401 incluso enviando las credenciales del `.env`; el acceso real es la cuenta owner (basada en email) creada en el primer arranque. Mantener variables inertes y una documentacion que promete un login inexistente induce a error al operador y degrada la trazabilidad de la auditoria. Este change ejecuta la remocion ya anticipada por el design de c-62 ("Reemplazar `N8N_BASIC_AUTH` por un IdP").

## What Changes

- Eliminar `N8N_BASIC_AUTH_ACTIVE`, `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` de los dos servicios N8N del compose (`n8n` y `n8n-corpus`) en `docker-compose.yml`, junto con el comentario "Autenticacion basica de N8N".
- Eliminar `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` de `.env.example` (y su comentario).
- Documentar la remocion de las dos claves del `.env` de la raiz como paso de operador; el `.env` es gitignorado y NO es un artefacto versionado.
- Reescribir la documentacion que afirma un login inexistente para que describa el mecanismo real: el acceso a la UI de N8N es la cuenta owner creada en el primer arranque, persistida hasheada en el volumen `n8n_data` (`/home/node/.n8n/database.sqlite`); su password no vive en el repo (gestor de passwords del operador).
- Realinear las specs normativas (`foundation-environment` y `local-bootstrap`) para que dejen de depender de `N8N_BASIC_AUTH_*`, preservando la intencion de seguridad de `local-bootstrap` para las credenciales restantes (`POSTGRES_PASSWORD`).
- Sin cambio de comportamiento: las variables son inertes, por lo que la remocion no altera el funcionamiento del stack.

### Non-goals (fuera de alcance)

- NO se integra un IdP (esa parte del design de c-62 queda diferida; este change ejecuta solo la remocion).
- NO se modifican las credenciales de PostgreSQL ni ningun otro secreto de desarrollo.
- NO se rediseña el modelo de autenticacion de N8N ni se toca el volumen `n8n_data`.
- NO se cambia la retencion de ejecuciones ni el workflow de N8N.

## Capabilities

### New Capabilities

- Ninguna.

### Modified Capabilities

- `foundation-environment`: el escenario "Resto de la configuracion N8N sin cambios" deja de listar `N8N_BASIC_AUTH_ACTIVE` entre las variables de negocio preservadas.
- `local-bootstrap`: el requisito de credenciales de desarrollo local parametrizadas por entorno deja de cubrir la password de basic auth de N8N y pasa a aplicar unicamente a `POSTGRES_PASSWORD`, conservando la prohibicion de credenciales hardcodeadas o trivialmente adivinables en archivos versionados.

## Impact

- **Configuracion versionada**: `docker-compose.yml` (servicios `n8n` y `n8n-corpus`), `.env.example`.
- **Documentacion**: `README.md`, `docs/operational-guide.md`, `docs/n8n-workflow-guide.md`, `docs/por_implementar.md`, `docs/security-hardening.md`.
- **Specs**: `openspec/specs/foundation-environment/spec.md`, `openspec/specs/local-bootstrap/spec.md`.
- **Accion de operador (no versionada)**: quitar `N8N_BASIC_AUTH_USER` y `N8N_BASIC_AUTH_PASSWORD` del `.env` de la raiz.
- **Sin cambios**: volumen `n8n_data`, credenciales de PostgreSQL, `COST_GUARD_SHARED_SECRET`, retencion de ejecuciones (`EXECUTIONS_DATA_PRUNE`, `EXECUTIONS_DATA_MAX_AGE`), workflow `n8n/workflow.json`.

## Governance: MEDIO

Configuracion de infraestructura y documentacion sin cambio de comportamiento observable. Se implementa con checkpoints y se reportan las decisiones; no requiere aprobacion humana previa como el nivel ALTO.
