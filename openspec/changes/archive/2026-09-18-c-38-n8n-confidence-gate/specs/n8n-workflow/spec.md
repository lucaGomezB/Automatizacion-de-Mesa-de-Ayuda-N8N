## MODIFIED Requirements

### Requirement: Ruteo por umbral de confianza

El gate de revisión humana del workflow SHALL ser de dos capas y NO SHALL evaluar la confianza del modelo antes de persistir el incidente.

La primera capa es el nodo `if` pre-POST `Entrada valida`, que es una validación de ENTRADA y no una compuerta de confianza: para los canales correo y web SHALL verificar la validez y longitud del texto de la descripción, y para el canal telefonía SHALL verificar la validez de la respuesta de clasificación del agente. Su condición SHALL ser `confianza >= 0.70 OR revision_forzada == true`, de modo que una entrada con revisión forzada por el tope de refinamiento del agente se persista aunque su confianza sea `0.0`. Cuando la condición es verdadera el flujo SHALL continuar hacia la persistencia; cuando es falsa SHALL derivar a revisión humana.

La segunda capa es el nodo `if` post-POST `Requiere revision humana`, que SHALL evaluar el flag `requiere_revision_humana` devuelto por el backend en la respuesta de `POST /api/v1/incidentes/`. El backend SHALL fijar `requiere_revision_humana = confianza < 0.70` y la respuesta del POST NO SHALL incluir el campo `confianza`; por eso el gate post-POST SHALL leer el flag y NO SHALL intentar leer `confianza` del response. Cuando el flag es verdadero el flujo SHALL notificar al operador designado y registrar auditoría; cuando es falso SHALL continuar con las confirmaciones por canal. Las condiciones de los nodos `if` NO SHALL quedar vacías.

#### Scenario: Confianza por encima del umbral crea el incidente

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.85`
- **THEN** la condición `confianza >= 0.70 OR revision_forzada == true` es verdadera y el flujo rutea hacia la persistencia del incidente

#### Scenario: Confianza por debajo del umbral deriva a revisión humana

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.60` y `revision_forzada = false`
- **THEN** la condición es falsa y el flujo deriva a revisión humana

#### Scenario: Entrada valida acepta revisión forzada aun con confianza baja

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.0` y `revision_forzada = true` (por ejemplo, el tope de refinamiento del agente)
- **THEN** la condición es verdadera por la rama `revision_forzada == true` y el flujo rutea hacia la persistencia

#### Scenario: Confianza en el límite exacto

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.70` y `revision_forzada = false`
- **THEN** la condición `confianza >= 0.70` es verdadera y el flujo rutea hacia la persistencia (el umbral es inclusivo)

#### Scenario: El gate post-POST lee el flag del backend

- **WHEN** el nodo `if` post-POST `Requiere revision humana` evalúa la respuesta de `POST /api/v1/incidentes/`
- **THEN** su condición evalúa el campo `requiere_revision_humana` del response y NO referencia el campo `confianza`, que el response no incluye

#### Scenario: Flag verdadero deriva a notificación y auditoría

- **WHEN** la respuesta del backend tiene `requiere_revision_humana = true` (confianza por debajo de `0.70`)
- **THEN** el flujo notifica al operador designado y registra la ejecución en auditoría

#### Scenario: Flag falso continúa con las confirmaciones

- **WHEN** la respuesta del backend tiene `requiere_revision_humana = false` (confianza en o por encima de `0.70`)
- **THEN** el flujo rutea por canal de origen y continúa con las confirmaciones sin notificar al operador

## ADDED Requirements

### Requirement: Notificacion al operador designado

Cuando el backend marca un incidente con `requiere_revision_humana = true`, el workflow SHALL notificar a un operador designado mediante un correo electrónico enviado por el nodo `Notificar operador designado` (`microsoftOutlook`), dirigido a la dirección configurada en la variable de entorno `OPERATOR_EMAIL`. La notificación SHALL ocurrir en la rama verdadera del gate post-POST `Requiere revision humana`, antes del registro de auditoría, y NO SHALL emitirse cuando el flag es falso. Para el canal correo, la rama de revisión SHALL marcar además el mensaje como leído.

#### Scenario: Se notifica al operador cuando el backend pide revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = true`
- **THEN** el nodo `Notificar operador designado` envía un correo a la dirección de `$env.OPERATOR_EMAIL` y luego se registra la auditoría

#### Scenario: No se notifica cuando no hace falta revisión

- **WHEN** el response del backend tiene `requiere_revision_humana = false`
- **THEN** el flujo no envía la notificación al operador y continúa con las confirmaciones por canal

#### Scenario: La rama de revisión marca el correo como leído

- **WHEN** un incidente del canal correo requiere revisión humana
- **THEN** el flujo alcanza el marcado del mensaje como leído, de modo que el trigger no lo reprocesa

### Requirement: URLs del backend configurables por entorno

Los nodos HTTP que invocan el backend SHALL resolver la URL base con la variable de entorno `$env.BACKEND_URL` y MUST NOT hardcodear el host del backend en el JSON del workflow. La variable `BACKEND_URL` SHALL exponerse al servicio N8N desde `docker-compose.yml`, y el destinatario de la notificación de revisión SHALL exponerse como `OPERATOR_EMAIL`, de modo que el mismo workflow exportado funcione en distintos entornos sin editar el JSON.

#### Scenario: Los nodos HTTP usan la variable de entorno

- **WHEN** la suite estructural inspecciona los nodos `httpRequest` que apuntan a rutas `/api/v1/`
- **THEN** cada uno resuelve el host con `$env.BACKEND_URL` y la URL termina en el prefijo `/api/v1/` correcto

#### Scenario: No hay host hardcodeado

- **WHEN** la suite estructural busca el literal del host del backend en las URLs de los nodos `httpRequest`
- **THEN** ningún nodo contiene el host hardcodeado

#### Scenario: Las variables se exponen desde el compose

- **WHEN** se inspecciona `docker-compose.yml`
- **THEN** el servicio N8N define `BACKEND_URL` y `OPERATOR_EMAIL` como variables de entorno disponibles para los nodos del workflow
