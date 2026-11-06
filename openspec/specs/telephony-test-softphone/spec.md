# telephony-test-softphone Specification

## Purpose
Herramienta de desarrollo que permite a un operador inyectar su voz en el pipeline telefónico existente mediante un softphone VoIP de navegador, con acuñado local de Access Tokens de Twilio y configuración scriptable de la cuenta, sin depender de una llamada PSTN internacional.

## Requirements

### Requirement: Acuñado local de un Access Token de Twilio con VoiceGrant

La herramienta SHALL acuñar localmente un Twilio Access Token como JWT firmado con HMAC-SHA256, a partir del API Key de la cuenta. El token SHALL incluir un `VoiceGrant` con el `outgoingApplicationSid` del TwiML App y una identidad de llamante, además de los claims de emisor, sujeto y expiración acotada. El acuñado MUST NOT requerir red ni contactar a Twilio, y MUST NOT incrustar ningún token en el código o en archivos versionados.

#### Scenario: El token contiene el grant de voz y la identidad

- **WHEN** la herramienta acuña un token con una configuración válida
- **THEN** el token es un JWT firmado con el API Key Secret cuyo `VoiceGrant` declara el `outgoingApplicationSid` del TwiML App y la identidad indicada

#### Scenario: El token está acotado en el tiempo

- **WHEN** se inspecciona el token acuñado
- **THEN** su expiración es un instante futuro acotado y no un valor indefinido

#### Scenario: El acuñado no toca la red

- **WHEN** se acuña un token sin conectividad
- **THEN** el token se genera correctamente a partir de los valores de entorno

### Requirement: El softphone de navegador coloca la llamada sin tramo PSTN

La herramienta SHALL incluir una pagina HTML estatica que use el Voice SDK de Twilio sobre WebRTC para registrar un dispositivo y colocar una llamada saliente hacia el TwiML App. La pagina SHALL mostrar un indicador de estado y controles de inicio y fin de llamada. La pagina MUST NOT requerir un paso de compilacion ni un bundler para ejecutarse. El audio de la llamada SHALL ser el del microfono del operador, de modo que el `<Record>` del flujo telefonico capture esa voz. Al finalizar la llamada, la pagina SHALL volver al reposo cuando NO haya un caso del corpus seleccionado, y SHALL entrar en el estado de procesamiento del requerimiento "Bloqueo de la siguiente llamada hasta procesar la anterior" cuando SI haya un caso seleccionado.

#### Scenario: La llamada se inicia desde el navegador

- **WHEN** el operador abre la pagina y presiona el control de inicio con un token valido
- **THEN** el dispositivo se registra y la llamada saliente hacia el TwiML App se establece

#### Scenario: La llamada se finaliza desde el navegador

- **WHEN** el operador presiona el control de fin de llamada
- **THEN** la llamada se desconecta y, sin caso seleccionado, el estado vuelve a reposo mientras que, con un caso seleccionado, entra en estado de procesamiento y el control de inicio permanece deshabilitado

#### Scenario: La página no requiere build

- **WHEN** se sirve la pagina localmente sin compilacion
- **THEN** el operador puede usarla directamente en el navegador

### Requirement: Reutilización del endpoint de voz existente como Voice URL del TwiML App

La configuración del TwiML App SHALL usar como Voice URL el endpoint de voz existente del backend (`/api/v1/cost-guard/twilio/voice`), para que la llamada iniciada por el cliente entre al mismo flujo real, incluida la admisión de la guarda de costo, sin una llamada entre números de la misma cuenta. La herramienta MUST NOT modificar el flujo de producción del backend.

#### Scenario: La llamada del cliente entra al flujo existente

- **WHEN** el dispositivo del navegador inicia la llamada hacia el TwiML App
- **THEN** Twilio invoca el endpoint de voz existente y este responde el TwiML de grabación del canal telefónico

#### Scenario: El backend de producción no se modifica

- **WHEN** se revisa el alcance de la herramienta
- **THEN** no hay cambios en rutas, servicios ni configuración del backend de producción

### Requirement: Identidad de llamante única y configurable

La herramienta SHALL permitir fijar la identidad del llamante y SHALL generar por defecto una identidad única por sesión, de modo que la clave del rate por origen de la guarda de costo no se agote al repetir pruebas. La identidad elegida SHALL reflejarse en el `VoiceGrant` del token y, por lo tanto, en el `From` (`client:<identity>`) que recibe el endpoint de voz.

#### Scenario: Identidad única por defecto

- **WHEN** la herramienta acuña un token sin identidad explícita
- **THEN** usa una identidad única por sesión que no colisiona con corridas previas

#### Scenario: Identidad explícita

- **WHEN** el operador fija una identidad explícita
- **THEN** el token acuñado declara esa identidad en su `VoiceGrant`

### Requirement: Servidor local de loopback que sirve la página y el token

La herramienta SHALL ofrecer un servidor local que sirva la página del softphone y entregue un Access Token fresco en el mismo origen, de modo que no se requiera configuración de CORS. El servidor SHALL escuchar únicamente en la interfaz de loopback y SHALL emitir tokens de vida acotada. La herramienta SHALL también ofrecer un modo sin servidor que imprima un token para inspección.

#### Scenario: La página obtiene un token fresco

- **WHEN** el operador carga la página servida por la herramienta
- **THEN** la página obtiene un Access Token fresco desde el mismo origen local

#### Scenario: El servidor solo escucha en loopback

- **WHEN** se inspecciona el binding del servidor local
- **THEN** solo acepta conexiones desde la interfaz de loopback

### Requirement: Configuración de Twilio scriptable y documentada

La herramienta SHALL documentar y automatizar, mediante el Twilio CLI, la creación del API Key y del TwiML App con su Voice URL y método de voz, mostrando los identificadores resultantes. La operación SHALL ser reproducible por un operador humano siguiendo una guía paso a paso, que SHALL cubrir la configuración de las credenciales y la ejecución del softphone. El API Key Secret SHALL tratarse como valor de un solo uso visible y MUST NOT persistirse en un archivo versionado.

#### Scenario: La configuración crea el API Key y el TwiML App

- **WHEN** el operador ejecuta el script de configuración con credenciales válidas
- **THEN** obtiene el API Key SID, el API Key Secret y el TwiML App SID, con la Voice URL apuntando al endpoint de voz existente

#### Scenario: La guía permite operar el softphone

- **WHEN** el operador sigue la guía paso a paso
- **THEN** puede configurar las credenciales, iniciar el servidor local y colocar una llamada de prueba

### Requirement: Higiene de secretos en toda la herramienta

La herramienta SHALL leer todas las credenciales exclusivamente desde variables de entorno y MUST NOT contener secretos hardcodeados ni escribir secretos en archivos versionados. Los tokens acuñados SHALL ser de vida acotada y MUST NOT exponerse en registros persistidos.

#### Scenario: Faltan credenciales

- **WHEN** la herramienta se ejecuta sin las variables de entorno requeridas
- **THEN** aborta con un mensaje claro en lugar de operar con valores vacíos o por defecto

#### Scenario: No hay secretos en el repositorio

- **WHEN** se inspecciona el contenido versionado de la herramienta
- **THEN** no contiene secretos ni tokens, solo referencias a variables de entorno

### Requirement: Seleccion del caso de corpus y listado telefonico en el softphone

El softphone SHALL presentar un control de seleccion (`<select>`) poblado UNICAMENTE con los casos de canal telefonico del corpus de evaluacion (81 casos), con valor por defecto vacio. El modo `serve` SHALL exponer por loopback el endpoint `GET /corpus-cases`, que lee la copia pseudonimizada del corpus (`data/corpus_evaluacion_pseudonimizado.json`, ruta configurable por `--corpus-json`) y devuelve `[{id, descripcion}]` tolerante a la forma exacta del rotulo de canal. Cuando el autor selecciona un caso, la llamada entrante SHALL enviar el `corpus_case_id` seleccionado como parametro custom de la llamada hacia el TwiML App; cuando la seleccion esta vacia, MUST NOT enviarse el parametro (modo de desarrollo sin correlacion). El autor SHALL RECITAR el texto del caso durante la llamada: la herramienta MUST NOT reproducir audio del caso. El endpoint y su pagina SHALL exponerse solo en loopback (por lo que el listado no requiere auth adicional) y MUST NOT loguear las descripciones de los casos.

#### Scenario: El selector se puebla solo con casos telefonicos

- **WHEN** el operador carga la pagina del softphone servida por el modo `serve`
- **THEN** el control de seleccion lista los casos del canal telefonico del corpus y no casos de otros canales

#### Scenario: Valor por defecto vacio

- **WHEN** el operador abre la pagina sin seleccionar un caso
- **THEN** el control de seleccion no tiene un caso preseleccionado y la llamada no envia `corpus_case_id`

#### Scenario: El caso seleccionado viaja con la llamada

- **WHEN** el operador selecciona un caso y coloca la llamada
- **THEN** la llamada se establece hacia el TwiML App con el `corpus_case_id` seleccionado como parametro custom

#### Scenario: Sin reproduccion de audio

- **WHEN** el operador prepara la recitacion de un caso
- **THEN** la herramienta muestra el texto del caso para recitarlo a mano y no lo reproduce por audio

#### Scenario: Solo loopback y sin logueo de descripciones

- **WHEN** se inspecciona el servidor del softphone
- **THEN** escucha solo en loopback y ninguna descripcion de caso se escribe en un registro persistido

### Requirement: Bloqueo de la siguiente llamada hasta procesar la anterior

Con un caso del corpus seleccionado, la herramienta SHALL impedir iniciar la siguiente llamada hasta que la llamada recien realizada quede completamente procesada (incidente persistido). Tras la desconexion, la pagina SHALL deshabilitar el control de inicio, SHALL mostrar un estado de procesamiento que nombra el caso seleccionado y SHALL consultar la sonda de estado en intervalos acotados (aprox. 2 s) hasta un timeout acotado (aprox. 60 s). La herramienta SHALL re-habilitar el control de inicio y mostrar un mensaje claro cuando el caso quede procesado. Si el timeout se agota sin que el caso quede procesado, la herramienta SHALL exponer el estado pendiente y SHALL permitir continuar con una advertencia visible, de modo que el operador nunca quede bloqueado. Sin un caso seleccionado, la herramienta MUST NOT aplicar este bloqueo (modo de desarrollo retrocompatible).

#### Scenario: Con caso seleccionado la llamada terminada bloquea el inicio

- **WHEN** el operador termina una llamada habiendo seleccionado un caso del corpus
- **THEN** el control de inicio queda deshabilitado y el estado indica que el caso esta en procesamiento

#### Scenario: El caso procesado rehabilita el inicio

- **WHEN** la sonda reporta que el caso seleccionado quedo procesado
- **THEN** la herramienta re-habilita el control de inicio y muestra un mensaje claro

#### Scenario: Timeout con advertencia visible

- **WHEN** el caso no queda procesado dentro del timeout acotado
- **THEN** la herramienta expone el estado pendiente y permite continuar con una advertencia visible

#### Scenario: Sin caso seleccionado no hay bloqueo

- **WHEN** el operador termina una llamada sin haber seleccionado un caso
- **THEN** el control de inicio se re-habilita como antes, sin polling ni estado de procesamiento

### Requirement: Sonda de estado del caso por loopback

El modo `serve` SHALL exponer por loopback `GET /case-status?case_id=<id>&since=<epoch_ms>` que determina si el caso fue procesado, autenticandose contra el backend con las credenciales del operador leidas exclusivamente del entorno y cacheando el JWT del lado del servidor; el JWT y las credenciales MUST NOT exponerse a la pagina ni escribirse en archivos versionados. La sonda SHALL consultar el endpoint existente `GET /api/v1/telefonia/ingresos?corpus_case_id=<id>&latest=true`, con la opcion `--insecure` (certificado autofirmado) y la URL base configurable. Un caso SHALL considerarse procesado cuando EXISTE un ingreso y su `incidente_id` NO es nulo. La sonda SHALL responder `{listo, transcripcion_estado, incidente_id, latencia_e2e_ms}`, con `listo=false` cuando no exista ingreso (404). Para desambiguar el REINTENTO del mismo `corpus_case_id`, cuando se provea `since` la sonda SHALL descartar un ingreso cuyo `ingresado_en` sea anterior a `since` y MUST NOT reportarlo como procesado; solo un ingreso con `ingresado_en` mayor o igual a `since` SHALL contar. La sonda MUST NOT loguear descripciones ni contenido de casos.

#### Scenario: Ingreso con incidente se reporta como procesado

- **WHEN** el endpoint del backend devuelve un ingreso con `incidente_id` no nulo para el caso
- **THEN** la sonda responde `listo=true` con el `incidente_id` y la `latencia_e2e_ms`

#### Scenario: Sin ingreso todavia

- **WHEN** el backend responde 404 porque el caso aun no tiene ingreso
- **THEN** la sonda responde `listo=false` con los campos de medicion nulos

#### Scenario: Reintento del mismo caso reporta el ingreso previo como no valido

- **WHEN** un mismo `corpus_case_id` se mide dos veces y la sonda encuentra el ingreso de la llamada anterior con `ingresado_en` anterior a `since`
- **THEN** la sonda NO lo reporta como procesado y `listo` permanece falso hasta que exista un ingreso con `ingresado_en` mayor o igual a `since`

#### Scenario: Estado de error terminal no se reporta como procesado

- **WHEN** el ingreso del caso queda en un estado de error terminal (por ejemplo `error_stt`) sin incidente vinculado
- **THEN** la sonda expone el `transcripcion_estado` observado y mantiene `listo=false`

#### Scenario: Sin credenciales configuradas la sonda falla de forma clara

- **WHEN** faltan las credenciales del operador en el entorno
- **THEN** la sonda responde un error claro y no expone ni las credenciales ni el JWT
