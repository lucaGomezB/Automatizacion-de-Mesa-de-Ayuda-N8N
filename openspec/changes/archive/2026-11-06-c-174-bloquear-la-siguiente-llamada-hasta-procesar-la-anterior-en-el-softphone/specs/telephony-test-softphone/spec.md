# Delta for telephony-test-softphone

## MODIFIED Requirements

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

## ADDED Requirements

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
