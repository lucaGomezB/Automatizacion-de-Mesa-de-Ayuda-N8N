## Purpose

Herramienta de desarrollo que permite a un operador inyectar su voz en el pipeline telefónico existente mediante un softphone VoIP de navegador, con acuñado local de Access Tokens de Twilio y configuración scriptable de la cuenta, sin depender de una llamada PSTN internacional.

## ADDED Requirements

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

La herramienta SHALL incluir una página HTML estática que use el Voice SDK de Twilio sobre WebRTC para registrar un dispositivo y colocar una llamada saliente hacia el TwiML App. La página SHALL mostrar un indicador de estado y controles de inicio y fin de llamada. La página MUST NOT requerir un paso de compilación ni un bundler para ejecutarse. El audio de la llamada SHALL ser el del micrófono del operador, de modo que el `<Record>` del flujo telefónico capture esa voz.

#### Scenario: La llamada se inicia desde el navegador

- **WHEN** el operador abre la página y presiona el control de inicio con un token válido
- **THEN** el dispositivo se registra y la llamada saliente hacia el TwiML App se establece

#### Scenario: La llamada se finaliza desde el navegador

- **WHEN** el operador presiona el control de fin de llamada
- **THEN** la llamada se desconecta y el estado vuelve a reposo

#### Scenario: La página no requiere build

- **WHEN** se sirve la página localmente sin compilación
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
