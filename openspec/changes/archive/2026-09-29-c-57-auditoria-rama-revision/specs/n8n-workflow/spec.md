# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: N8N-AUDIT-001 — La auditoria reporta rechazos como rechazos

El registro de auditoria SHALL distinguir creados de rechazados segun el resultado real del flujo. Un incidente rechazado por validacion o por el validador IA MUST NOT registrarse como creado. El camino exitoso de la rama de revisión humana (incidente creado con `requiere_revision_humana = true`) SHALL registrarse como `creado` con el `incidente_id` numérico devuelto por el backend, porque el incidente existe y la revisión es un estado posterior al alta, no un rechazo. En la rama de rechazo por validación el resultado SHALL ser `rechazado_datos_incompletos`, y en la salida de error del POST SHALL ser `error_backend`.

#### Scenario: Un rechazo no se audita como alta

- **WHEN** una entrada es rechazada por validacion
- **THEN** el registro de auditoria refleja el rechazo (`rechazado_datos_incompletos`) y no un alta exitosa

#### Scenario: El alta con revisión humana se audita como creada

- **WHEN** el backend responde con un incidente creado y `requiere_revision_humana = true`
- **THEN** el registro de auditoría tiene `resultado = "creado"` y `incidente_id` igual al `id` numérico devuelto por el backend

#### Scenario: El alta sin revisión se audita como creada

- **WHEN** el backend responde con un incidente creado y `requiere_revision_humana = false`
- **THEN** el registro de auditoría tiene `resultado = "creado"` y `incidente_id` igual al `id` numérico devuelto por el backend

#### Scenario: El error del backend se audita como error

- **WHEN** la ejecución llega a la auditoría por la salida de error del POST de persistencia
- **THEN** el registro de auditoría tiene `resultado = "error_backend"` y no `creado`

### Requirement: Notificacion al operador designado

Cuando el backend marca un incidente con `requiere_revision_humana = true`, el workflow SHALL notificar a un operador designado mediante un correo electrónico enviado por el nodo `Notificar operador designado` (`n8n-nodes-base.emailSend` sobre SMTP), dirigido a la dirección configurada en la variable de entorno `OPERATOR_EMAIL`. La notificación SHALL conservar el asunto, el cuerpo y el destinatario vigentes, SHALL ocurrir en la rama verdadera del gate post-POST `Requiere revision humana`, y NO SHALL emitirse cuando el flag es falso. La notificación SHALL ser hermana (no antecesora) del registro de auditoría en esa rama, de modo que la auditoría no dependa del éxito ni de la salida del envío.
(Previously: la notificación no sólo precedía al registro de auditoría, sino que era su única vía de acceso en la rama verdadera; el envío usaba el nodo `microsoftOutlook` sobre Microsoft Entra OAuth2.)

#### Scenario: Se notifica al operador cuando el backend pide revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = true`
- **THEN** el nodo `Notificar operador designado` envía un correo por SMTP a la dirección de `$env.OPERATOR_EMAIL`

#### Scenario: No se notifica cuando no hace falta revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = false`
- **THEN** el flujo no envía la notificación al operador y continúa con las confirmaciones por canal

#### Scenario: La notificación no antecede a la auditoría

- **WHEN** la suite estructural inspecciona la rama verdadera del gate post-POST
- **THEN** `Notificar operador designado` y `Registro de auditoria` cuelgan ambos del gate y el registro de auditoría no es alcanzable a través del nodo de notificación

#### Scenario: La rama de revisión marca el correo como leído

- **WHEN** un incidente del canal correo requiere revisión humana
- **THEN** el mensaje ya quedó marcado como leído por el disparador IMAP, de modo que el trigger no lo reprocesa

#### Scenario: La notificación no depende de Entra OAuth2

- **WHEN** la suite estructural inspecciona el nodo `Notificar operador designado`
- **THEN** el nodo es de tipo `n8n-nodes-base.emailSend` y no declara credenciales `microsoftOutlook*`

### Requirement: N8N-AUDIT-003 — El fallo de notificación no omite la auditoría

El nodo `Notificar operador designado` SHALL declarar manejo de error (`onError: continueRegularOutput` o `continueErrorOutput`) de modo que un fallo en el envío de la notificación no aborte la ejecución. La auditoría de la rama de revisión humana SHALL colgar directamente de la rama verdadera del gate post-POST `Requiere revision humana`, en paralelo con la notificación y no aguas abajo de ella, de modo que sea alcanzable con independencia del resultado del envío.

#### Scenario: El nodo de notificación declara manejo de error

- **WHEN** la suite estructural inspecciona el nodo `Notificar operador designado`
- **THEN** el nodo declara un `onError` de continuación distinto del default de detención

#### Scenario: La auditoría es paralela y no descendiente de la notificación

- **WHEN** la suite estructural inspecciona los sucesores directos de la rama verdadera del gate post-POST
- **THEN** `Registro de auditoria` es un sucesor directo de esa rama y no es sucesor de `Notificar operador designado`

#### Scenario: La auditoría sigue siendo alcanzable tras un fallo de notificación

- **WHEN** el envío de la notificación al operador falla
- **THEN** la ejecución continúa y alcanza `Registro de auditoria` por su arista directa desde el gate

#### Scenario: La rama de revisión conserva la notificación

- **WHEN** el backend marca un incidente con `requiere_revision_humana = true`
- **THEN** el flujo sigue notificando al operador designado (sin regresión)

## ADDED Requirements

### Requirement: N8N-AUDIT-004 — La auditoría no consume la salida de la notificación

En el camino exitoso, la entrada del nodo `Registro de auditoria` SHALL ser el item de la respuesta de `POST /api/v1/incidentes` (que expone `id` numérico, `sector.nombre` y `requiere_revision_humana`), tanto por la rama de revisión humana como por la rama sin revisión. La auditoría MUST NOT tomar como entrada la salida del nodo `Notificar operador designado` (resultado SMTP sin `id`), porque eso la haría registrar `incidente_id = null` y `resultado` incorrecto. La suite estructural SHALL verificar el cableado sin requerir un runtime N8N.

#### Scenario: La auditoría recibe la respuesta del POST en la rama de revisión

- **WHEN** la suite estructural inspecciona los sucesores directos de la rama verdadera del gate post-POST
- **THEN** `Registro de auditoria` es sucesor directo de `Requiere revision humana[main#0]` y por esa arista recibe el item de la respuesta del POST

#### Scenario: La auditoría no depende del item SMTP

- **WHEN** la suite estructural inspecciona el `jsCode` del nodo `Registro de auditoria`
- **THEN** el código no referencia el nodo `Notificar operador designado` y deriva `resultado` e `incidente_id` de la respuesta del backend (`item.id`, `item.error`, `item.es_valido`)

#### Scenario: No hay doble ejecución de la auditoría en la rama de revisión

- **WHEN** la suite estructural traza las entradas de `Registro de auditoria`
- **THEN** `Notificar operador designado` no figura como origen de la auditoría, de modo que la rama de revisión registra el evento una sola vez
