## Purpose

Ingesta asíncrona del canal de telefonía propiedad del backend: recibe la notificación de grabación de Twilio, descarga y transcribe el audio con un motor dedicado de speech-to-text, pseudonimiza el texto de inmediato, lo persiste de forma cifrada y lo entrega a n8n, de modo que el canal vuelva a clasificar sin que el transcript crudo cruce el borde de la automatización.

## ADDED Requirements

### Requirement: Recepción del callback de estado de grabación con firma fail-closed

El backend SHALL exponer un endpoint que Twilio invoca cuando la grabación de la llamada está disponible. El endpoint SHALL autenticarse EXCLUSIVAMENTE con la firma `X-Twilio-Signature` (HMAC-SHA1 sobre la URL completa más los parámetros de formulario ordenados) y SHALL rechazar con HTTP 401 toda petición cuya firma falte o no sea válida. Cuando el token de autenticación de Twilio no esté configurado, el endpoint SHALL rechazar con HTTP 401 (fail-closed) y MUST NOT quedar abierto. El endpoint SHALL aceptar los parámetros de formulario del callback de grabación de Twilio (`AccountSid`, `CallSid`, `RecordingSid`, `RecordingUrl`, `RecordingStatus`, `RecordingDuration`, `RecordingChannels`, `RecordingSource`) y MUST NOT depender de un campo `From`, que ese callback no provee.

#### Scenario: Firma válida admite el callback

- **WHEN** llega una notificación de grabación con una firma `X-Twilio-Signature` válida y el token de autenticación configurado
- **THEN** el endpoint acepta la petición y continúa el procesamiento del ingreso

#### Scenario: Firma ausente o inválida se rechaza

- **WHEN** llega una notificación de grabación sin firma o con una firma que no coincide
- **THEN** el endpoint responde HTTP 401 y no procesa el ingreso

#### Scenario: Token no configurado mantiene el endpoint cerrado

- **WHEN** el token de autenticación de Twilio no está configurado
- **THEN** el endpoint responde HTTP 401 a toda petición en lugar de quedar abierto

#### Scenario: El callback no requiere el número llamante

- **WHEN** la notificación de grabación no incluye un campo `From`
- **THEN** el ingreso se procesa igualmente, porque el callback de grabación no provee ese campo

### Requirement: Sellado del instante de ingreso en la recepción del backend

El backend SHALL sellar el instante de ingreso de la telefonía al recibir el callback de estado de grabación, ANTES de descargar y transcribir el audio. Ese instante SHALL propagarse a n8n en el handoff y SHALL persistirse como `ingresado_en` del incidente, de modo que la latencia end-to-end de la telefonía incluya la descarga, la transcripción, la pseudonimización y el handoff. El sellado MUST NOT ocurrir en el borde de n8n.

#### Scenario: El ingreso se sella en la recepción del callback

- **WHEN** el backend recibe el callback de estado de grabación
- **THEN** sella el instante de ingreso antes de iniciar la descarga y la transcripción

#### Scenario: La latencia incluye el trabajo del backend

- **WHEN** se deriva la latencia end-to-end de un incidente telefónico
- **THEN** la latencia incluye la descarga de la grabación, la transcripción, la pseudonimización y el handoff

#### Scenario: El sello se propaga a n8n

- **WHEN** el backend entrega el ingreso a n8n
- **THEN** el payload del handoff incluye el `ingresado_en` sellado por el backend

### Requirement: Idempotencia del ingreso por CallSid con reintento por estado

El backend SHALL tratar `CallSid` como la clave de idempotencia del ingreso de telefonía. Ante la recepción repetida del mismo `CallSid`, el backend SHALL distinguir el estado del ingreso:

- Si el ingreso ya está `transcrito` o `pendiente`, SHALL ser un no-op: SHALL NOT descargar, SHALL NOT transcribir de nuevo, SHALL NOT reservar presupuesto pago adicional y SHALL devolver el ingreso existente.
- Si el ingreso está en un estado terminal de error (`guarda_denegada`, `error_descarga` o `error_stt`), SHALL reprocesarlo a través del pipeline normal.

El reproceso SHALL comenzar con un reclamo atómico que transicione el ingreso fuera del estado de error dentro de la MISMA transacción que el procesamiento posterior, de modo que la fila quede bloqueada y solo un reintento concurrente lo reclame. El reintento que no gane el reclamo (el UPDATE afecta cero filas) SHALL resolver como no-op devolviendo el ingreso existente. El reproceso SHALL preservar `ingresado_en` (el sello de auditoría) y reservar la superficie paga por cada intento. La idempotencia SHALL resolverse ANTES de la reserva de la superficie paga y de cualquier llamada a un proveedor externo.

#### Scenario: Callback repetido sobre un ingreso transcrito no reprocesa

- **WHEN** llega un callback de grabación con un `CallSid` cuyo ingreso ya está `transcrito`
- **THEN** el backend no descarga, no transcribe de nuevo ni reserva presupuesto adicional, y devuelve el ingreso existente

#### Scenario: Callback repetido sobre un ingreso pendiente no reprocesa

- **WHEN** llega un callback de grabación con un `CallSid` cuyo ingreso está `pendiente`
- **THEN** el backend no descarga, no transcribe de nuevo ni reserva presupuesto adicional

#### Scenario: Callback repetido sobre un ingreso en error lo reprocesa

- **WHEN** llega un callback de grabación con un `CallSid` cuyo ingreso quedó en `error_descarga`, `error_stt` o `guarda_denegada`
- **THEN** el backend reclama el ingreso atómicamente y lo reprocesa por el pipeline normal

#### Scenario: El reintento preserva el sello de ingreso

- **WHEN** el backend reprocesa un ingreso en estado terminal de error
- **THEN** el `ingresado_en` original se conserva sin sobrescribirse

#### Scenario: Solo un reintento concurrente reclama el ingreso

- **WHEN** dos callbacks repetidos del mismo `CallSid` intentan reprocesar el ingreso en error de forma concurrente
- **THEN** solo uno gana el reclamo atómico y reprocesa, y el otro resuelve como no-op devolviendo el ingreso existente

#### Scenario: CallSid nuevo inicia el procesamiento

- **WHEN** llega un callback de grabación con un `CallSid` no registrado
- **THEN** el backend inicia el flujo de ingreso para esa llamada

#### Scenario: La idempotencia precede a la reserva paga

- **WHEN** se evalúa un ingreso ya registrado
- **THEN** la verificación de idempotencia ocurre antes de la reserva de la superficie paga

### Requirement: Respuesta HTTP del callback según el estado del ingreso

El endpoint del callback de estado de grabación SHALL mapear el estado resultante del ingreso a un código HTTP. Ante un fallo transitorio de infraestructura (`error_descarga` o `error_stt`), SHALL persistir el estado de error del ingreso y SHALL responder HTTP 503 con el envelope de error estándar, de modo que el reintento nativo del callback de Twilio pueda reprocesar el ingreso. Ante `transcrito`, `pendiente` o `guarda_denegada`, SHALL responder HTTP 200 con el modelo de respuesta del callback.

#### Scenario: El fallo transitorio responde 503

- **WHEN** el ingreso resultante queda en `error_descarga` o `error_stt`
- **THEN** el endpoint responde HTTP 503 con el envelope de error estándar y el ingreso queda persistido en su estado terminal de error

#### Scenario: Los estados no transitorios responden 200

- **WHEN** el ingreso resultante queda en `transcrito`, `pendiente` o `guarda_denegada`
- **THEN** el endpoint responde HTTP 200 con el modelo de respuesta del callback

### Requirement: Descarga autenticada de la grabación

El backend SHALL descargar el audio de la grabación desde la URL provista por Twilio (`RecordingUrl`) usando autenticación HTTP Basic con las credenciales de la cuenta (`AccountSid:AuthToken`). La descarga SHALL ocurrir únicamente después de que la guarda de costo haya reservado la superficie de transcripción. El backend SHALL validar que la descarga sea exitosa antes de invocar el motor de transcripción.

#### Scenario: La grabación se descarga con credenciales

- **WHEN** la guarda concede la reserva y la grabación está disponible
- **THEN** el backend descarga el audio con autenticación Basic y obtiene su contenido binario

#### Scenario: La descarga fallida no invoca la transcripción

- **WHEN** la descarga de la grabación falla
- **THEN** el backend no invoca el motor de transcripción y registra el ingreso con su estado de error

#### Scenario: No se descarga sin reserva

- **WHEN** la guarda de costo no concede la reserva
- **THEN** el backend no descarga la grabación ni invoca el motor de transcripción

### Requirement: Transcripción con un motor dedicado de speech-to-text

El backend SHALL transcribir el audio descargado mediante un motor dedicado de speech-to-text, configurable por nombre de modelo. La transcripción SHALL solicitarse en modo verbatim con granularidad a nivel de palabra y con el idioma configurado (por defecto español rioplatense). El resultado SHALL ser el texto de la llamada, apto para el pipeline de clasificación. El motor MUST NOT ser el reconocimiento de voz embebido de la grabación de Twilio.

#### Scenario: La transcripción produce texto

- **WHEN** el audio de una llamada válida se envía al motor dedicado
- **THEN** el backend obtiene un texto de transcripción no vacío

#### Scenario: La transcripción es verbatim y con idioma configurado

- **WHEN** el backend solicita la transcripción
- **THEN** solicita el modo verbatim con granularidad de palabra y el idioma configurado

#### Scenario: El motor es independiente de Twilio

- **WHEN** se inspecciona el origen de la transcripción
- **THEN** proviene del motor dedicado del backend y no del reconocimiento de voz de Twilio

### Requirement: Pseudonimización inmediata y doble representación cifrada del transcript

El backend SHALL pseudonimizar el texto transcripto INMEDIATAMENTE después de obtenerlo y ANTES de cualquier entrega a n8n. El transcript crudo SHALL persistirse cifrado at-rest (Fernet) junto con la versión pseudonimizada en claro, en una tabla de ingreso dedicada, conforme a la doble representación del módulo de pseudonimización. La versión pseudonimizada SHALL ser la única representación que cruce el borde hacia n8n. El transcript crudo MUST NOT transitar n8n bajo ninguna ruta.

#### Scenario: El transcript se pseudonimiza antes del handoff

- **WHEN** el backend obtiene el texto transcripto
- **THEN** lo pseudonimiza antes de entregarlo a n8n y el payload del handoff no contiene PII en claro

#### Scenario: El transcript crudo se persiste cifrado

- **WHEN** se inspecciona el valor crudo almacenado en la tabla de ingreso
- **THEN** es texto cifrado ilegible y no contiene el transcript original en claro

#### Scenario: Ambas representaciones se pueblan

- **WHEN** el backend persiste un ingreso telefonico con PII en el transcript
- **THEN** el registro tiene el transcript original cifrado y la descripción pseudonimizada en claro, ambas pobladas

### Requirement: Persistencia del ingreso con trazabilidad y vínculo al incidente

El backend SHALL persistir un registro de ingreso por llamada con, al menos: el `CallSid` único, el `RecordingSid`, el número llamante cifrado, la duración en segundos, el transcript original cifrado, la descripción pseudonimizada, el `ingresado_en`, el instante de persistencia del ingreso, el estado de transcripción, el proveedor y modelo usados, un detalle de error nullable y el identificador del incidente nullable. La restricción de unicidad sobre `CallSid` SHALL imponerse a nivel de persistencia. El vínculo con el incidente creado SHALL quedar registrado cuando el alta se resuelva.

#### Scenario: El ingreso queda trazable

- **WHEN** se completa el ingreso de una llamada
- **THEN** el registro expone su estado de transcripción, proveedor, modelo e instantes para auditoría

#### Scenario: La unicidad del CallSid es efectiva

- **WHEN** dos callbacks del mismo `CallSid` intentan persistirse de forma concurrente
- **THEN** la persistencia impide registrar dos filas con el mismo `CallSid`

#### Scenario: El vínculo con el incidente se registra

- **WHEN** un incidente se crea a partir de un ingreso telefónico
- **THEN** el registro de ingreso queda asociado al identificador de ese incidente

### Requirement: Handoff autenticado hacia n8n con payload pseudonimizado

El backend SHALL entregar el ingreso a n8n mediante una invocación autenticada con un secreto compartido. El payload SHALL contener exactamente la descripción pseudonimizada, el `CallSid`, el número llamante y el `ingresado_en` sellado por el backend. El payload MUST NOT contener el transcript crudo ni datos personales en claro. El `CallSid` SHALL utilizarse aguas abajo como identificador de origen del alta para la idempotencia del incidente.

#### Scenario: El handoff lleva solo texto pseudonimizado

- **WHEN** el backend invoca a n8n con el ingreso
- **THEN** el payload contiene la descripción pseudonimizada, el `CallSid`, el llamante y el `ingresado_en`, sin transcript crudo

#### Scenario: El handoff se autentica

- **WHEN** el backend invoca a n8n
- **THEN** la invocación incluye el secreto compartido acordado

#### Scenario: El CallSid identifica el origen del alta

- **WHEN** n8n crea el incidente a partir del handoff
- **THEN** usa el `CallSid` como identificador de origen del alta

### Requirement: Recuperación ante fallo de transcripción o denegación de la guarda

Cuando la guarda de costo deniegue la reserva, o cuando la descarga o la transcripción fallen, el backend SHALL NOT abortar la ejecución ni descartar silenciosamente el ingreso. El backend SHALL persistir el ingreso con un estado de transcripción explícito y un detalle de error, de modo que el caso quede disponible para reintento o revisión humana. Un fallo transitorio de descarga o transcripción SHALL además invitar el reintento nativo del callback (HTTP 503) y un callback repetido SHALL reprocesar el ingreso automáticamente, sin intervención manual. La ejecución MUST NOT quedar en un estado ambiguo.

#### Scenario: La guarda denegada conserva el ingreso

- **WHEN** la guarda de costo deniega la reserva de transcripción
- **THEN** el backend persiste el ingreso con un estado explícito de no transcrito y no invoca al proveedor pago

#### Scenario: El fallo de transcripción queda registrado

- **WHEN** la transcripción falla
- **THEN** el backend persiste el ingreso con estado de error y detalle, sin abortar la ejecución en silencio

#### Scenario: El fallo no descarta el ingreso

- **WHEN** ocurre cualquier fallo del flujo de transcripción
- **THEN** el registro de ingreso permanece disponible para reintento o revisión

#### Scenario: El reintento es automático

- **WHEN** un ingreso queda en un estado terminal de error transitorio
- **THEN** el estado queda persistido y un callback repetido del mismo `CallSid` reprocesa el ingreso sin intervención manual

### Requirement: Grabación mono con señales de finalización y estado

El sistema SHALL generar la grabación de la llamada sin depender de la transcripción embebida del proveedor. El documento TwiML de la llamada admitida SHALL grabar en modo mono, SHALL declarar la URL de callback de estado de grabación y la acción posterior a la finalización de la grabación, y MUST NOT solicitar la transcripción embebida del proveedor. El mensaje hablado posterior a la grabación SHALL ser alcanzable por el proveedor, de modo que el llamante reciba una confirmación o un mensaje de cierre, y MUST NOT prometer la creación inmediata del ticket, que ahora es asincrónica.

#### Scenario: La grabación es mono y declara callbacks

- **WHEN** se inspecciona el TwiML de la llamada admitida
- **THEN** la grabación es mono y declara la URL de estado de grabación y la acción posterior a la finalización

#### Scenario: No se solicita la transcripción embebida

- **WHEN** se inspecciona el TwiML de la llamada admitida
- **THEN** la grabación no solicita la transcripción embebida del proveedor

#### Scenario: El mensaje posterior es alcanzable

- **WHEN** finaliza la grabación
- **THEN** el proveedor puede reproducir el mensaje hablado posterior, que no promete la creación inmediata del ticket