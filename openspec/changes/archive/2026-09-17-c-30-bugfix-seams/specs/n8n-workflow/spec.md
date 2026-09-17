## ADDED Requirements

### Requirement: N8N-AUTH-001 — Nodos HTTP autentican al backend con un JWT obtenido por login dinamico

El workflow SHALL obtener el JWT con un nodo de login que invoque `POST /api/v1/auth/login` con las credenciales del operador almacenadas como credencial de N8N (MUST NOT incluir el token ni las credenciales en `n8n/workflow.json`). El nodo que crea el incidente SHALL enviar `Authorization: Bearer <token>` con el token extraido de la respuesta del login. El token MUST NOT ser un valor estatico de larga vida, porque el JWT del backend expira (`JWT_EXPIRE_MINUTES=1440`). La ausencia de un token valido MUST NOT producir una ejecucion exitosa silenciosa; el nodo SHALL propagar el error HTTP.

#### Scenario: El alta de incidente llega autenticada al backend

- **WHEN** se ejecuta el flujo completo que invoca `POST /api/v1/incidentes`
- **THEN** el workflow obtiene el token via `POST /api/v1/auth/login` y la solicitud incluye `Authorization: Bearer <token>` y el backend responde 201, no 401

#### Scenario: El token se renueva en cada ejecucion

- **WHEN** transcurre mas de la vida util del JWT entre dos ejecuciones del workflow
- **THEN** el workflow vuelve a ejecutar el login y obtiene un token vigente en lugar de reutilizar uno expirado

#### Scenario: Sin credencial valida el nodo falla visiblemente

- **WHEN** las credenciales de login son invalidas o el token esta ausente
- **THEN** el nodo registra el error HTTP 401 y el workflow no continua como si hubiera creado el incidente

### Requirement: N8N-AGENT-001 — AI Agent con Chat Model conectado

El nodo `AI Agent` SHALL tener un Chat Model conectado y configurado, de modo que la ejecucion del agente produzca una salida real. Un nodo agente sin modelo MUST NOT considerarse configurado.

#### Scenario: El agente produce salida con el modelo conectado

- **WHEN** el workflow llega al nodo `AI Agent`
- **THEN** el agente ejecuta contra el Chat Model conectado y devuelve una respuesta no vacia

### Requirement: N8N-AGENT-002 — Prompt dinamico con el payload del trigger

El prompt del `AI Agent` SHALL interpolar la descripcion del incidente proveniente del payload del trigger, en lugar de ser un texto estatico. La descripcion SHALL llegar pseudonimizada al agente cuando corresponda.

#### Scenario: El prompt contiene la descripcion del trigger

- **WHEN** el trigger recibe una entrada con descripcion `"Servidor de correo caido"`
- **THEN** la ejecucion del agente incluye esa descripcion en el prompt, no un texto fijo

### Requirement: N8N-AGENT-003 — Contrato JSON del agente compatible con el validador

La salida del `AI Agent` SHALL solicitarse y validarse como un JSON con exactamente los campos `sector_predicho` (uno de los cinco sectores canonicos, sin tildes) y `confianza` (numero entre 0 y 1). El validador SHALL aceptar el contrato del agente y MUST NOT fallar por un formato incompatible.

#### Scenario: Salida del agente validada correctamente

- **WHEN** el agente responde con `{"sector_predicho": "Sistemas", "confianza": 0.82}`
- **THEN** el validador acepta la respuesta y el flujo continua con ese sector y confianza

#### Scenario: Salida con sector fuera del vocabulario es rechazada

- **WHEN** el agente responde con un sector que no pertenece al conjunto canonico de cinco sectores
- **THEN** el validador rechaza la respuesta y el flujo deriva a revision humana

### Requirement: N8N-ROUTE-001 — Switch de canal en modo reglas sobre el canal normalizado

El nodo `Rutear por canal de origen` SHALL operar en modo de reglas (no en modo expresion) con reglas explicitas y `fallbackOutput` definido. Las reglas SHALL evaluar el canal normalizado (`correo`, `web`, `telefonia`) y la salida SHALL ser un indice de salida valido, no el resultado de evaluar la respuesta del backend.

#### Scenario: Cada canal rutea a su rama

- **WHEN** el canal normalizado es `correo`, `web` o `telefonia`
- **THEN** el switch produce el indice de salida correspondiente a esa rama

#### Scenario: Canal desconocido usa el fallback

- **WHEN** el canal no coincide con ninguna regla
- **THEN** el switch usa el `fallbackOutput` configurado en lugar de fallar o continuar sin salida

### Requirement: N8N-WEBHOOK-001 — responseMode con respondToWebhook alcanzable

El webhook de entrada SHALL configurar su `responseMode` de modo que el nodo `respondToWebhook` sea alcanzable en todas las ramas que deben responder al cliente. MUST NOT existir un `respondToWebhook` inalcanzable ni un webhook que quede sin respuesta.

#### Scenario: El webhook responde al cliente

- **WHEN** llega una peticion al webhook con un canal valido
- **THEN** el cliente recibe la respuesta emitida por el nodo `respondToWebhook` con un cuerpo y codigo definidos

#### Scenario: Ninguna rama queda sin respuesta

- **WHEN** se recorren las ramas del flujo que atienden el webhook
- **THEN** toda rama que deba responder alcanza `respondToWebhook` y ninguna queda en espera indefinida

### Requirement: N8N-WEBHOOK-002 — El alta del formulario web pasa por el webhook N8N

El formulario web SHALL crear incidentes a traves del webhook de N8N (con middleware si hiciera falta) y MUST NOT llamar directamente a `POST /api/v1/incidentes` para el alta. El webhook de N8N MUST NOT eliminarse como parte de este change.

#### Scenario: El formulario usa el webhook y no la API directa

- **WHEN** un usuario envia el formulario web de alta de incidente
- **THEN** la peticion llega al webhook de N8N y no directamente al endpoint de incidentes del backend

#### Scenario: El webhook permanece como punto de entrada del canal web

- **WHEN** se inspecciona el workflow y el cliente del formulario
- **THEN** el webhook de N8N sigue existiendo y es el punto de entrada del alta web

### Requirement: N8N-EMAIL-001 — Extraccion del cuerpo del correo en modo simple

El trigger de Outlook SHALL exponer el cuerpo del correo en el formato configurado. Cuando el modo de salida sea `simple`, el workflow SHALL extraer la descripcion desde la ubicacion de texto disponible, de modo que el validador de correo reciba una descripcion no vacia.

#### Scenario: Correo valido produce descripcion

- **WHEN** llega un correo con cuerpo de texto
- **THEN** la validacion de correo extrae la descripcion del campo disponible y la marca como valida si cumple el minimo

#### Scenario: El cuerpo no se pierde por el modo de salida

- **WHEN** el trigger opera en modo `simple` y el campo `body` no esta disponible en la raiz
- **THEN** el flujo obtiene el texto desde la ruta efectiva del payload del trigger

### Requirement: N8N-NORM-001 — El payload al backend incluye canal_origen_id

La estructura normalizada enviada al backend SHALL incluir `canal_origen_id` correspondiente al canal de origen, ademas de `id`, `timestamp`, `canal_origen` y `descripcion`. El incidente persistido MUST NOT quedar con canal `NULL`.

#### Scenario: El incidente creado tiene canal

- **WHEN** el workflow crea un incidente desde cualquiera de los tres canales
- **THEN** el body enviado al backend incluye `canal_origen_id` y el incidente persistido tiene canal de origen distinto de `NULL`

### Requirement: N8N-PHONE-001 — La rama falsa del telefono regresa al agente

En el canal telefonico, la rama que no cumple la condicion del nodo de decision SHALL regresar al agente o a un camino que complete el flujo. MUST NOT quedar como rama terminal sin salida.

#### Scenario: Condicion falsa del telefono no termina el flujo

- **WHEN** una transcripcion telefonica no cumple la condicion evaluada
- **THEN** el flujo reingresa al agente o a un camino que produce un resultado, sin terminar en un nodo sin continuacion

### Requirement: N8N-AUDIT-001 — La auditoria reporta rechazos como rechazos

El registro de auditoria SHALL distinguir creados de rechazados segun el resultado real del flujo. Un incidente rechazado por validacion o por el validador IA MUST NOT registrarse como creado.

#### Scenario: Un rechazo no se audita como alta

- **WHEN** una entrada es rechazada por validacion
- **THEN** el registro de auditoria refleja el rechazo y no un alta exitosa

### Requirement: N8N-VALID-001 — Los fallos del validador IA conservan su causa

Cuando el validador IA rechaza una salida, el flujo SHALL conservar la causa del rechazo y MUST NOT reetiquetar el incidente con un canal distinto (por ejemplo `correo`) por el mero hecho de haber fallado la validacion.

#### Scenario: Un fallo de validacion IA no cambia el canal

- **WHEN** el validador IA rechaza la salida del agente para una entrada del canal web
- **THEN** el canal registrado sigue siendo `web` y no se reetiqueta como `correo`

### Requirement: N8N-EXPR-001 — Expresiones de nodo validas y sin bucles vacios

Las expresiones de los nodos SHALL referenciar campos existentes del payload (MUST NOT usar `.id` ni otros campos inexistentes). MUST NOT existir un nodo de reenvio vacio conectado en bucle.

#### Scenario: Las expresiones referencian campos existentes

- **WHEN** se inspeccionan las expresiones de los nodos
- **THEN** cada campo referenciado existe en el payload de entrada y ninguna expresion referencia un `.id` inexistente

#### Scenario: No hay nodo vacio en bucle

- **WHEN** se inspecciona el grafo del workflow
- **THEN** no existe un nodo de reenvio vacio conectado en bucle consigo mismo

### Requirement: N8N-URL-001 — URLs del backend con la forma correcta

Las URLs del backend usadas por los nodos HTTP SHALL incluir la barra final y el prefijo de version correctos (`/api/v1/`), de modo que no se disparen redirecciones 307 ni 404 por barra faltante. La referencia a la URL base SHALL ser compatible con N8N v2 (sin depender de `$env` bloqueado).

#### Scenario: La llamada al backend no redirige

- **WHEN** un nodo HTTP invoca un endpoint del backend
- **THEN** la URL termina en el prefijo `/api/v1/` correcto y la respuesta no es un 307 por redireccion

#### Scenario: La URL base se resuelve en N8N v2

- **WHEN** el workflow se ejecuta en N8N v2
- **THEN** la URL base del backend se resuelve sin depender de una variable de entorno bloqueada
