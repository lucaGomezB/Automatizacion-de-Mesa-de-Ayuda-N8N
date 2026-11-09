## MODIFIED Requirements

### Requirement: INFRA-008 — CI no se rompe

El preflight de costo que parsea `docker-compose.yml` SHALL seguir aprobando, preservando la imagen de n8n pineada, `N8N_WEBHOOK_URL` con la ruta dedicada y las variables `EXECUTIONS_TIMEOUT`. La imagen de n8n se considera pineada cuando el servicio `n8n` declara `image: n8nio/n8n:2.11.2` o cuando declara un `build` cuyo Dockerfile (resuelto desde el `context` y el `dockerfile` del build) parte con `FROM n8nio/n8n:2.11.2` como primera instruccion `FROM`, con o sin alias de stage; un `FROM` con otra version o con la etiqueta `latest` MUST NOT considerarse pineado. El subconjunto de integracion en CI MUST seguir usando su service container propio en `localhost:5432`.

#### Scenario: Preflight de costo pasa con el compose modificado

- **WHEN** CI ejecuta `python scripts/preflight/cost_readiness.py`
- **THEN** el comando termina con exit code cero

#### Scenario: CI no depende del compose

- **WHEN** CI ejecuta el subconjunto de integracion
- **THEN** usa `TEST_PG_URL` apuntando a `localhost:5432` y no el compose del repositorio

#### Scenario: Imagen literal pineada

- **WHEN** el servicio `n8n` declara `image: n8nio/n8n:2.11.2`
- **THEN** el guard de INFRA-008 considera cumplido el pin

#### Scenario: Build con FROM pineado

- **WHEN** el servicio `n8n` declara un `build` cuyo Dockerfile contiene `FROM n8nio/n8n:2.11.2` (con o sin `AS <alias>`)
- **THEN** el guard de INFRA-008 considera cumplido el pin

#### Scenario: Build con FROM distinto falla

- **WHEN** el servicio `n8n` declara un `build` cuyo Dockerfile parte de `n8nio/n8n:latest` o de otra version
- **THEN** el guard de INFRA-008 NO considera cumplido el pin
