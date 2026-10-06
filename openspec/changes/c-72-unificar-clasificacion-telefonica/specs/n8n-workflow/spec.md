# Delta for n8n-workflow

## MODIFIED Requirements

### Requirement: Validación de la respuesta de clasificación según Anexo H §H.3

La clasificacion persistida del incidente SHALL provenir del backend, que valida su propia cascada conforme al contrato de resultado. Si el workflow conserva una validacion de una salida reducida de un modelo para un sub-caso (OQ1), esa validacion SHALL aplicar, en orden, los pasos del Anexo H §H.3: (1) parseo JSON válido; (2) presencia de los campos `sector_predicho` y `confianza`; (3) `sector_predicho` exactamente en `{"Seguridad Informatica", "Soporte Tecnico Hardware", "Soporte Tecnico Software", "Bases de Datos", "Sistemas"}` (case-sensitive, sin tildes); (4) `confianza` numérica en el rango `[0.0, 1.0]`; (5) si el campo `sectores_adicionales` está presente, cada uno de sus valores MUST pertenecer al mismo conjunto canónico. Ante el fallo de cualquier paso, SHALL registrar el error, fijar `confianza = 0.0` y marcar el incidente para revisión humana, sin propagar estados inconsistentes. La salida validada de un modelo reducido MUST NOT determinar el sector persistido del incidente.

#### Scenario: Respuesta válida aceptada

- **WHEN** la validación recibe `{"sector_predicho": "Soporte Tecnico Software", "confianza": 0.95, "sectores_adicionales": ["Bases de Datos"]}`
- **THEN** la marca como válida y conserva el sector predicho, los sectores adicionales y la confianza para el ruteo por umbral, sin que esa salida determine el sector persistido

#### Scenario: Categoría fuera del conjunto permitido

- **WHEN** la validación recibe una respuesta con `sector_predicho` igual a `"operaciones"` (minúscula), `"Operaciones"` o cualquier valor fuera del conjunto exacto
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Sector adicional inválido

- **WHEN** la validación recibe un `sectores_adicionales` con un valor fuera del conjunto canónico
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: JSON malformado

- **WHEN** la validación recibe un texto que no parsea como JSON
- **THEN** registra el error, fija `confianza = 0.0` y marca el incidente para revisión humana

#### Scenario: Confianza fuera de rango

- **WHEN** la validación recibe una `confianza` igual a `1.5` o no numérica
- **THEN** la rechaza, fija `confianza = 0.0` y marca el incidente para revisión humana

### Requirement: Ruteo por umbral de confianza

El gate de revision humana del workflow SHALL ser de dos capas y NO SHALL evaluar la confianza del modelo antes de persistir el incidente.

La primera capa es el nodo `if` pre-POST `Entrada valida`, que es una validación de ENTRADA y no una compuerta de confianza: para los TRES canales (correo, web y telefonía) SHALL verificar la validez y longitud del texto de la descripción pseudonimizada. Para el canal telefonía el nodo MUST NOT evaluar una clasificación producida por un modelo de n8n, porque la clasificación la resuelve el backend. Su condición SHALL ser `confianza >= 0.70 OR revision_forzada == true`, de modo que una entrada con revisión forzada se persista aunque su confianza sea `0.0`. Cuando la condición es verdadera el flujo SHALL continuar hacia la persistencia; cuando es falsa SHALL derivar a revisión humana.

La segunda capa es el nodo `if` post-POST `Requiere revision humana`, que SHALL evaluar el flag `requiere_revision_humana` devuelto por el backend en la respuesta de `POST /api/v1/incidentes/`. El backend SHALL fijar `requiere_revision_humana = confianza < 0.70` y la respuesta del POST NO SHALL incluir el campo `confianza`; por eso el gate post-POST SHALL leer el flag y NO SHALL intentar leer `confianza` del response. Cuando el flag es verdadero el flujo SHALL notificar al operador designado y registrar auditoría; cuando es falso SHALL continuar con las confirmaciones por canal. Las condiciones de los nodos `if` NO SHALL quedar vacías.

#### Scenario: Confianza por encima del umbral crea el incidente

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.85`
- **THEN** la condición `confianza >= 0.70 OR revision_forzada == true` es verdadera y el flujo rutea hacia la persistencia del incidente

#### Scenario: Confianza por debajo del umbral deriva a revisión humana

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.60` y `revision_forzada = false`
- **THEN** la condición es falsa y el flujo deriva a revisión humana

#### Scenario: Entrada valida acepta revisión forzada aun con confianza baja

- **WHEN** el nodo `if` pre-POST `Entrada valida` evalúa una entrada con `confianza = 0.0` y `revision_forzada = true`
- **THEN** la condición es verdadera por la rama `revision_forzada == true` y el flujo rutea hacia la persistencia

#### Scenario: Telefono valida su entrada como los demas canales

- **WHEN** el nodo `if` pre-POST `Entrada valida` procesa una entrada del canal telefonía
- **THEN** verifica la validez y longitud de la descripción pseudonimizada y NO evalúa una clasificación producida por un modelo de n8n

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

### Requirement: Normalización de canales a estructura unificada

El workflow N8N SHALL incluir un nodo de normalización que homogenice la entrada de cualquiera de los tres canales (correo electrónico, formulario web, telefonía con transcripción) en una estructura unificada con exactamente los campos `id`, `timestamp` (precisión al milisegundo), `canal_origen` (uno de `correo`, `web`, `telefonia`) y `descripcion`. Los nodos posteriores SHALL operar exclusivamente sobre esta estructura y no sobre la forma cruda de cada canal. Para el canal de correo, la normalización SHALL consumir los campos genéricos del mensaje IMAP (remitente, asunto, cuerpo de texto y fecha de recepción) y NO SHALL depender de campos propios de un proveedor. Para el canal de telefonía, la normalización SHALL consumir el ingreso pseudonimizado sellado por el backend a través del cableado `Sellar -> Normalizar` y MUST NOT depender de un nodo de clasificacion en n8n.

#### Scenario: Correo electrónico normalizado

- **WHEN** el disparador IMAP recibe un correo y su carga pasa por el nodo de normalización
- **THEN** la salida contiene `id`, `timestamp` con precisión al milisegundo, `canal_origen = "correo"` y `descripcion` con el cuerpo del incidente

#### Scenario: Transcripción telefónica normalizada

- **WHEN** la transcripción pseudonimizada de una llamada Twilio sellada por el backend atraviesa el cableado `Sellar -> Normalizar` hasta el nodo de normalización
- **THEN** la salida contiene los mismos cuatro campos con `canal_origen = "telefonia"`, sin un nodo de clasificacion en n8n en la ruta

#### Scenario: Canal de origen inválido rechazado

- **WHEN** la normalización recibe una entrada cuyo canal no es `correo`, `web` ni `telefonia`
- **THEN** el flujo no produce una estructura unificada válida y deriva la entrada a revisión humana

### Requirement: Trigger Webhook para la transcripción de Twilio

El workflow N8N SHALL incluir un disparador `webhook` (método `POST`, con una ruta dedicada) que reciba del backend el ingreso telefónico YA pseudonimizado, como canal de telefonía. El disparador MUST NOT ser un `twilioTrigger` de resumen post-llamada y el workflow MUST NOT parsear CloudEvents de Twilio ni depender del evento `call-summary.complete`. La salida del webhook SHALL fluir hacia la admisión (intake) del backend y, a través del cableado `Sellar -> Normalizar`, hacia el nodo de normalización con `canal_raw = "telefonia"`, de modo que el normalizador asigne `canal_origen = "telefonia"`. El webhook SHALL estar autenticado con el secreto compartido del handoff.

#### Scenario: El disparador telefónico existe y alimenta el flujo

- **WHEN** se inspecciona el workflow exportado
- **THEN** existe un nodo `webhook` con método `POST` y ruta no vacía cuya salida fluye hacia la admisión/normalización del backend, y no existe un nodo `twilioTrigger` de resumen post-llamada

#### Scenario: No hay parsing de CloudEvent

- **WHEN** se inspecciona el workflow exportado en busca de parsing del evento de resumen de Twilio
- **THEN** ningún nodo parsea el evento `call-summary.complete` ni una carga CloudEvent

#### Scenario: El canal telefónico queda identificado como "telefonia"

- **WHEN** un ingreso telefónico pseudonimizado atraviesa el flujo hasta la normalización
- **THEN** el `canal_raw` propagado es `"telefonia"` y la estructura unificada resultante tiene `canal_origen = "telefonia"`

### Requirement: Credenciales declaradas en nodos que las requieren

Todo nodo del workflow que requiera credenciales para operar (por ejemplo los nodos de Outlook y el trigger de Twilio) SHALL declarar la credencial correspondiente en su configuración, de modo que el workflow exportado no dependa de credenciales implícitas o ausentes.
(Previously: la enumeración de ejemplos incluía un nodo de modelo de lenguaje ya retirado del workflow.)

#### Scenario: Los nodos que requieren credenciales las declaran

- **WHEN** la suite de pruebas inspecciona los nodos que requieren credenciales por su tipo
- **THEN** cada uno declara una entrada de credencial no vacía en su configuración
- **AND** ningún nodo que requiera credencial queda sin declararla

## REMOVED Requirements

### Requirement: N8N-INTAKE-001 — El POST al backend envia Message-ID, clasificacion precalculada y origen

**Reason**: La clasificacion precalculada de telefonia se elimina; el backend clasifica todos los canales y el POST deja de transportar una clasificacion que pudiera omitir la cascada.
**Migration**: El POST sigue enviando la descripcion, el canal, el `Message-ID` de correo y el marcador de origen bajo un contrato nuevo. La clasificacion la resuelve el backend. Ver N8N-INTAKE-002 y N8N-UNIFY-001.

### Requirement: Acoplamiento del AI Agent a su modelo de lenguaje y al payload del trigger

**Reason**: El nodo `AI Agent` y su nodo de modelo de lenguaje fueron retirados de `n8n/workflow.json`; la clasificacion telefonica la resuelve la cascada del backend y no queda agente de n8n cuyo modelo o prompt haya que acoplar.
**Migration**: El contrato de clasificacion y el prompt unico viven en el backend (`docs/prompt_gemini.txt`, `HybridClassifier`). Ver N8N-UNIFY-001 y ASG-010.

### Requirement: N8N-AGENT-001 — AI Agent con Chat Model conectado

**Reason**: El nodo `AI Agent` fue retirado; ya no existe un agente de n8n que requiera un Chat Model conectado para producir una salida real.
**Migration**: Ninguna; la clasificacion de los tres canales se resuelve en el backend. Ver N8N-UNIFY-001.

### Requirement: N8N-AGENT-002 — Prompt dinamico con el payload del trigger

**Reason**: El `AI Agent` retirado era el unico consumidor de un prompt telefonico dentro de n8n; no queda prompt divergente que interpolar desde el trigger.
**Migration**: El prompt compartido del backend recibe la descripcion pseudonimizada. Ver TAX-003 y N8N-UNIFY-001.

### Requirement: N8N-AGENT-003 — Contrato JSON del agente compatible con el validador

**Reason**: No hay salida JSON de un agente de n8n que validar; el validador telefonico fue retirado junto con el agente.
**Migration**: El backend valida su propio contrato de resultado. Ver la MODIFIED "Validación de la respuesta de clasificación según Anexo H §H.3" y ASG-010.

### Requirement: N8N-MEMORY-001 — El nodo de memoria Redis declara credencial y parámetros

**Reason**: El nodo `memoryRedisChat` (memoria del `AI Agent` telefonico) fue retirado junto con el agente; no queda memoria conversacional de n8n que credencializar.
**Migration**: Ninguna; el flujo telefonico no mantiene estado conversacional en n8n.

### Requirement: N8N-TIMING-003 — Recuperación robusta del sello de ingreso de telefonía a través del AI Agent

**Reason**: El validador `Se verifica lo que trajo la IA` y el terminal `Derivar a revision humana`, unicos consumidores de `$('Sellar ingreso telefonia').first()` a traves del agente, fueron retirados. El flujo telefonico es ahora `Sellar -> Normalizar`.
**Migration**: La propagacion del sello entregado por el backend permanece en `Sellar ingreso telefonia`. Ver N8N-TIMING-001 y N8N-PHONE-004.

### Requirement: N8N-PHONE-001 — La rama falsa del telefono regresa al agente

**Reason**: El `AI Agent` ya no existe; no hay rama falsa que reingrese a el ni bucle de refinamiento que completar.
**Migration**: El canal telefonia fluye `Sellar -> Normalizar`; cualquier entrada invalida se resuelve por el ruteo por umbral vigente.

### Requirement: N8N-VALID-001 — Los fallos del validador IA conservan su causa

**Reason**: El validador IA telefonico fue retirado; no hay salida de modelo dentro de n8n cuyo rechazo haya que conservar ni canal que reetiquetar.
**Migration**: El backend distingue el canal y resuelve su propia cascada. Ver ASG-010 y N8N-UNIFY-001.

### Requirement: N8N-GUARD-001 — La guarda de costo preserva el item del canal de telefonía

**Reason**: El nodo `Guard de costo` y el bucle `Guard permite? -> AI Agent` fueron retirados; la reserva `n8n_gemini` de telefonia ya no existe.
**Migration**: La clasificacion telefonica no reserva `n8n_gemini`; la escalacion del backend reserva `backend_gemini`. Ver la MODIFIED de runtime-cost-guard "Enforcement del AI Agent de n8n antes de invocarlo".

### Requirement: N8N-GUARD-002 — El caller de la guarda usa el item corriente, sin referencia frágil

**Reason**: Retirado junto con el nodo `Guard de costo`; no queda llamada de guarda en el flujo telefonico de n8n que resolver el numero de origen.
**Migration**: El enforcement del gasto vive en el backend (runtime-cost-guard). Ver ASG-010.

### Requirement: N8N-REFINE-001 — Tope de refinamiento del agente pago

**Reason**: El nodo `AI Agent` fue retirado por completo de `n8n/workflow.json` (OQ1=A) y con el su bucle de refinamiento (OQ3=A); la clasificacion telefonica la resuelve la cascada del backend, de modo que no queda agente de n8n cuyos intentos de refinamiento haya que acotar.
**Migration**: La clasificacion telefonica y el acotamiento de la superficie paga se definen en el backend (cascada `HybridClassifier`) y en la delta de `classification-resilience`. Ver N8N-UNIFY-001 y N8N-INTAKE-002.

### Requirement: N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger

**Reason**: Se reescribe el cuerpo del escenario que citaba al `AI Agent` retirado y se renombra su titulo para eliminar la referencia; MODIFIED no admite un cambio de titulo de escenario sin reportar la perdida del escenario original, por lo que el bloque se reemplaza. El ID N8N-TIMING-001 se conserva.
**Migration**: Ver el ADDED "N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger (sello del backend)".

### Requirement: N8N-PHONE-003 — La rama telefónica consume el handoff pseudonimizado del backend

**Reason**: Se reescribe el cuerpo del escenario que citaba al `AI Agent` retirado y se renombra su titulo; la clasificacion la resuelve la cascada del backend. MODIFIED no admite un cambio de titulo de escenario sin reportar la perdida del escenario original, por lo que el bloque se reemplaza. El ID N8N-PHONE-003 se conserva.
**Migration**: Ver el ADDED "N8N-PHONE-003 — La rama telefónica consume el handoff pseudonimizado del backend (cascada del backend)".

## ADDED Requirements

### Requirement: N8N-INTAKE-002 — El POST al backend envia origen y no una clasificacion precalculada de telefonia

El nodo HTTP de persistencia SHALL enviar al backend la descripción pseudonimizada, el canal, el `Message-ID` del mensaje IMAP cuando el canal sea correo, y un marcador explícito de origen/evento. Para el canal telefonía el nodo MUST NOT enviar una `clasificacion` precalculada, porque la clasificación la resuelve el backend con su cascada. El workflow MUST NOT descartar el `Message-ID` ni el marcador de origen.

#### Scenario: El POST telefonico NO incluye clasificacion precalculada

- **WHEN** un incidente telefonico llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend NO incluye el sector predicho ni la confianza producidos fuera del backend

#### Scenario: El POST de correo incluye el Message-ID de origen

- **WHEN** un incidente del canal correo llega al nodo HTTP de persistencia
- **THEN** el cuerpo enviado al backend incluye el `origen_message_id` tomado del mensaje IMAP

#### Scenario: El marcador de origen es explicito

- **WHEN** se inspecciona el cuerpo que el nodo HTTP envia al backend
- **THEN** contiene un marcador explicito de origen/evento que identifica al canal emisor

### Requirement: N8N-UNIFY-001 — La clasificacion del incidente pertenece al backend

El workflow de n8n MUST NOT ser el camino de clasificacion del incidente en ningun canal. La clasificacion persistida de los tres canales SHALL provenir de la cascada del backend sobre la descripcion pseudonimizada. Cualquier clasificacion producida dentro de n8n MUST NOT persistirse como la clasificacion del incidente ni omitir la cascada del backend. El canal telefonico MUST NOT enviar una clasificacion precalculada que el backend pueda usar para saltear su cascada.

#### Scenario: Los tres canales clasifican en el backend

- **WHEN** un incidente de cualquier canal (correo, web o telefonia) se persiste
- **THEN** su sector proviene de la cascada del backend, no de n8n

#### Scenario: n8n no saltea la cascada

- **WHEN** se inspecciona el cuerpo que n8n envia al backend para un incidente telefonico
- **THEN** no contiene una clasificacion precalculada que el backend pudiera usar para omitir la cascada

### Requirement: N8N-TIMING-001 — Captura del instante de ingreso en el borde del trigger (sello del backend)

Cada trigger del workflow SHALL propagar el instante de ingreso antes de cualquier procesamiento del canal. En el canal de telefonía el instante de ingreso SHALL ser el sellado por el BACKEND en la recepción del callback de grabación y SHALL propagarse SIN ser re-sellado por n8n, de modo que la latencia incluya la descarga, la transcripción, la pseudonimización y el handoff del backend. En el canal de correo la captura SHALL ocurrir al INICIO del flujo del trigger de Outlook, en el instante en que el poller recoge el mensaje, y MUST NOT usar el `receivedDateTime` del mensaje. En el canal web la captura SHALL usar el instante de recepción del webhook. El valor SHALL propagarse al normalizador y SHALL estar disponible para el nodo HTTP de persistencia.

#### Scenario: Telefonia captura antes de la cascada del backend

- **WHEN** la suite estructural inspecciona el workflow
- **THEN** el `ingresado_en` propagado para telefonía se sella en el backend y está aguas arriba del nodo de normalización (`Sellar -> Normalizar`), sin depender de un clasificador en n8n

#### Scenario: Telefonía propaga el sello del backend

- **WHEN** el webhook de telefonía recibe el handoff del backend
- **THEN** el `ingresado_en` propagado es el valor sellado por el backend y no un instante calculado en n8n

#### Scenario: Correo sella al recoger el mensaje

- **WHEN** el trigger de Outlook recoge un mensaje
- **THEN** el ingreso capturado para ese mensaje es el instante de inicio del flujo del trigger (recogida del poller), no su `receivedDateTime`

#### Scenario: Web usa el instante de recepcion

- **WHEN** el webhook del formulario web recibe un envio
- **THEN** el ingreso capturado es el instante de recepción del webhook

#### Scenario: Propagacion al normalizador

- **WHEN** una entrada atraviesa el nodo de normalizacion
- **THEN** la estructura normalizada contiene el campo `ingresado_en`

### Requirement: N8N-PHONE-003 — La rama telefónica consume el handoff pseudonimizado del backend (cascada del backend)

El webhook del canal de telefonía SHALL aceptar exactamente el payload del handoff del backend con la descripción pseudonimizada, el `CallSid`, el número llamante y el `ingresado_en` sellado. La cascada del backend (`HybridClassifier`) SHALL recibir como entrada la descripción pseudonimizada y MUST NOT recibir el transcript crudo. El nodo HTTP de persistencia SHALL enviar el `CallSid` como `origen_message_id`, de modo que reutilice el índice único existente para la idempotencia del alta. El workflow MUST NOT recalcular ni re-sellar el instante de ingreso.

#### Scenario: El webhook recibe el payload del handoff

- **WHEN** el backend invoca el webhook de telefonía
- **THEN** el payload contiene la descripción pseudonimizada, el `CallSid`, el llamante y el `ingresado_en`

#### Scenario: La cascada del backend consume la descripción pseudonimizada

- **WHEN** el backend recibe el handoff de telefonía con la descripción pseudonimizada
- **THEN** la cascada del backend (`HybridClassifier`) clasifica esa descripción pseudonimizada y no un transcript crudo, sin un clasificador de n8n

#### Scenario: El CallSid se envía como identificador de origen

- **WHEN** el nodo HTTP de persistencia envía el alta de un incidente telefónico
- **THEN** el cuerpo incluye `origen_message_id` con el `CallSid` del handoff
