## MODIFIED Requirements

### Requirement: Guardas del compose verificadas por el preflight

El preflight SHALL verificar en `docker-compose.yml`: (a) la imagen del servicio `n8n` esta pineada a una version explicita y no a `latest`, ya sea declarada en `image` o, cuando el servicio usa `build` (c-182), en el primer `FROM` del Dockerfile del build, resuelto desde el `context` y el `dockerfile` relativos al compose, con o sin flags y alias de stage; (b) `N8N_WEBHOOK_URL` apunta a la ruta dedicada de notificacion `/webhook/notificacion-clasificacion`; (c) el environment del servicio `n8n` declara `EXECUTIONS_TIMEOUT`.

#### Scenario: Imagen N8N pineada

- **WHEN** el preflight inspecciona la imagen del servicio `n8n`
- **THEN** la guarda pasa si la etiqueta es una version explicita y falla si es `latest` o si falta la etiqueta

#### Scenario: Imagen N8N pineada via build

- **WHEN** el servicio `n8n` no declara `image` sino `build` y el primer `FROM` de su Dockerfile es `n8nio/n8n:<version explicita>` (con o sin `--platform` ni `AS <alias>`)
- **THEN** la guarda pasa y su detalle nombra la imagen resuelta y la ruta del Dockerfile

#### Scenario: Build sin pin resoluble

- **WHEN** el servicio `n8n` declara `build` cuyo Dockerfile falta, no tiene `FROM`, o parte de `latest` o de una imagen sin etiqueta
- **THEN** la guarda falla de forma nombrada, sin falso PASS

#### Scenario: Webhook de notificacion dedicado en el compose

- **WHEN** el preflight inspecciona `N8N_WEBHOOK_URL`
- **THEN** la guarda pasa si apunta a `/webhook/notificacion-clasificacion` y falla si apunta a otra ruta

#### Scenario: Tope de ejecucion presente en el compose

- **WHEN** el preflight inspecciona el environment del servicio `n8n`
- **THEN** la guarda pasa si `EXECUTIONS_TIMEOUT` esta declarado y falla si esta ausente
