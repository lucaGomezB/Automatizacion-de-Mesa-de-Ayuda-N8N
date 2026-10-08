# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: Notificacion al operador designado

Cuando el backend marca un incidente con `requiere_revision_humana = true`, el workflow SHALL notificar a los operadores designados mediante correos electronicos enviados por el nodo `Notificar operador designado` (`n8n-nodes-base.emailSend` sobre SMTP). La lista de destinatarios SHALL resolverse desde el campo `destinatarios_revision` del payload de alta, que contiene los operadores activos del sector del incidente resueltos por el backend. Cuando la lista este vacia o ausente, el workflow SHALL usar la direccion configurada en la variable de entorno `OPERATOR_EMAIL` como unico destinatario de respaldo, preservando el camino de un solo destinatario. La notificacion SHALL ocurrir en la rama verdadera del gate post-POST `Requiere revision humana`, como hermana (no antecesora) del registro de auditoria, y NO SHALL emitirse cuando el flag es falso. El workflow SHALL enviar una copia por destinatario y MUST NOT exponer la lista completa de destinatarios en un campo compartido `To`, `Cc` ni `Bcc`.
(Previously: el nodo enviaba a la unica direccion fija de `$env.OPERATOR_EMAIL`.)

#### Scenario: Se notifica al operador cuando el backend pide revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = true`
- **THEN** el nodo `Notificar operador designado` envia un correo por cada operador resuelto en `destinatarios_revision`; la auditoria se registra en paralelo desde el mismo gate

#### Scenario: Fallback cuando no hay destinatarios resueltos

- **WHEN** el response tiene `requiere_revision_humana = true` y `destinatarios_revision` esta vacio o ausente
- **THEN** el nodo `Notificar operador designado` envia un correo a la direccion de `$env.OPERATOR_EMAIL`

#### Scenario: No se notifica cuando no hace falta revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = false`
- **THEN** el flujo no envia la notificacion al operador y continua con las confirmaciones por canal

#### Scenario: Un correo por destinatario sin exponer la lista

- **WHEN** hay mas de un destinatario resuelto
- **THEN** cada envio direcciona a un unico destinatario y ninguno incluye la lista completa en `To`, `Cc` ni `Bcc`

#### Scenario: La rama de revisión marca el correo como leído

- **WHEN** un incidente del canal correo requiere revision humana
- **THEN** el mensaje ya quedo marcado como leido por el disparador IMAP, de modo que el trigger no lo reprocesa

#### Scenario: La notificación no antecede a la auditoría

- **WHEN** la suite estructural inspecciona la rama verdadera del gate post-POST
- **THEN** `Notificar operador designado` y `Registro de auditoria` cuelgan ambos del gate y el registro de auditoría no es alcanzable a través del nodo de notificación

#### Scenario: La notificación no depende de Entra OAuth2

- **WHEN** la suite estructural inspecciona el nodo `Notificar operador designado`
- **THEN** el nodo es de tipo `n8n-nodes-base.emailSend` y no declara credenciales `microsoftOutlook*`

### Requirement: URLs del backend configurables por entorno

Los nodos HTTP que invocan el backend SHALL resolver la URL base con la variable de entorno `$env.BACKEND_URL` y MUST NOT hardcodear el host del backend en el JSON del workflow. La variable `BACKEND_URL` SHALL exponerse al servicio N8N desde `docker-compose.yml`. La variable `OPERATOR_EMAIL` SHALL exponerse de la misma forma como el destinatario de RESPALDO de la notificacion de revision, usado unicamente cuando el payload de alta no provea destinatarios resueltos, de modo que el mismo workflow exportado funcione en distintos entornos sin editar el JSON.
(Previously: `OPERATOR_EMAIL` era el destinatario fijo de toda notificacion de revision.)

#### Scenario: Los nodos HTTP usan la variable de entorno

- **WHEN** la suite estructural inspecciona los nodos `httpRequest` que apuntan a rutas `/api/v1/`
- **THEN** cada uno resuelve el host con `$env.BACKEND_URL` y la URL termina en el prefijo `/api/v1/` correcto

#### Scenario: No hay host hardcodeado

- **WHEN** la suite estructural busca el literal del host del backend en las URLs de los nodos `httpRequest`
- **THEN** ningun nodo contiene el host hardcodeado

#### Scenario: Las variables se exponen desde el compose

- **WHEN** se inspecciona `docker-compose.yml`
- **THEN** el servicio N8N define `BACKEND_URL` y `OPERATOR_EMAIL` como variables de entorno disponibles para los nodos del workflow

#### Scenario: OPERATOR_EMAIL es el respaldo, no la fuente principal

- **WHEN** el payload de alta provee destinatarios resueltos
- **THEN** el workflow usa esos destinatarios y no `$env.OPERATOR_EMAIL`