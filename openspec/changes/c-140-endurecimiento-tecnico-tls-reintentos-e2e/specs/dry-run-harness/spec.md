## MODIFIED Requirements

### Requirement: Guardarraíl de costo cero

El arnes MUST operar sin invocar servicios pagos: MUST NOT realizar llamadas reales a Gemini ni a Twilio. Para lograrlo SHALL combinar dos capas independientes sobre el backend del stack del arnes: (1) una `GEMINI_API_KEY` ficticia y (2) un presupuesto nulo de la guarda de costo en runtime (`COST_GUARD_BUDGET_USD=0`), de modo que el clasificador deterministico resuelva los casos de prueba y que cualquier escalada sea denegada por la guarda y degradada sin peticion alguna al proveedor. Antes de ejecutar, el arnes MUST afirmar dentro del contenedor del backend que ambas capas estan en efecto y MUST abortar si detecta una clave real o un presupuesto distinto de cero. Las descripciones de prueba SHALL elegirse para resolverse en la etapa deterministica, y el recorrido SHALL verificarlo (ver "Asercion de etapa deterministica y clasificacion unica").

#### Scenario: Clave ficticia afirmada antes de ejecutar

- **WHEN** el arnes inicia su recorrido
- **THEN** verifica que la `GEMINI_API_KEY` efectiva es ficticia y solo continua si la afirmacion se cumple

#### Scenario: Aborto ante clave real

- **WHEN** el arnes detecta que la `GEMINI_API_KEY` efectiva no es ficticia
- **THEN** termina con exit code distinto de cero sin enviar incidentes ni consumir el servicio pago

#### Scenario: Presupuesto nulo afirmado antes de ejecutar

- **WHEN** el arnes inicia su recorrido
- **THEN** verifica que el presupuesto efectivo de la guarda de costo del backend es cero y aborta con exit code distinto de cero si no lo es

#### Scenario: Escalada fallida no genera costo

- **WHEN** un incidente de prueba no se resuelve en la etapa deterministica y el clasificador intenta escalar
- **THEN** la guarda de costo deniega la llamada paga, el backend aplica la degradacion configurada con revision humana y no se emite ninguna peticion al proveedor de Gemini

#### Scenario: Twilio nunca se invoca

- **WHEN** el arnes ejecuta su camino de costo cero
- **THEN** no se crea ninguna llamada, transcripcion ni recurso de Twilio

## ADDED Requirements

### Requirement: Asercion de etapa deterministica y clasificacion unica

En el recorrido web, el arnes SHALL consultar el registro de clasificacion del incidente creado (`GET /api/v1/clasificaciones/incidente/{id}`) y SHALL verificar que existe exactamente un registro y que su etapa es la deterministica. Si la etapa es otra o hay mas de un registro, el arnes MUST fallar de forma ruidosa nombrando la etapa observada.

#### Scenario: Incidente resuelto por la etapa deterministica

- **WHEN** el recorrido web crea el incidente de prueba
- **THEN** el registro de clasificacion del incidente es unico y su etapa es `deterministic`, y el check `e2e:etapa` pasa

#### Scenario: Escalada detectada como fallo

- **WHEN** el registro de clasificacion del incidente de prueba muestra una etapa distinta de la deterministica
- **THEN** el arnes termina con exit code distinto de cero e informa la etapa observada y la descripcion de prueba a revisar

### Requirement: Idempotencia del alta verificada a traves del webhook

El arnes SHALL enviar dos veces al webhook web el mismo incidente de prueba con un `origen_message_id` explicito y unico por corrida, y SHALL verificar que ambas respuestas devuelven el mismo `incidente_id` y que el listado filtrado por ese `origen_message_id` devuelve exactamente un incidente.

#### Scenario: Reenvio por el webhook sin duplicado

- **WHEN** el arnes envia dos veces el mismo cuerpo con `origen_message_id = smoke-<id de corrida>` al webhook `incidente-web`
- **THEN** ambas respuestas contienen el mismo `incidente_id` y `GET /api/v1/incidentes/?origen_message_id=smoke-<id de corrida>` devuelve un unico incidente

#### Scenario: Duplicado detectado como fallo

- **WHEN** el listado filtrado devuelve mas de un incidente para el identificador de la corrida
- **THEN** el check `e2e:idempotencia` falla e informa la cantidad observada

### Requirement: Recuperacion ante indisponibilidad transitoria del backend

El arnes SHALL ofrecer, solo bajo un flag explicito, una verificacion de recuperacion: desconecta el backend de la red de automatizacion, envia un incidente por el webhook web, reconecta el backend antes de que venza la primera espera entre intentos de N8N y verifica que la respuesta incluye un incidente y que existe exactamente una fila para su `origen_message_id`. La verificacion MUST restaurar la conectividad del backend aunque falle o se interrumpa, y MUST NOT ejecutarse sin el flag. Requiere que el workflow declare la politica de reintento del tramo de alta.

#### Scenario: Indisponibilidad breve recuperada sin duplicado

- **WHEN** se ejecuta el arnes con el flag de recuperacion y el backend queda desconectado unos segundos al inicio de la ejecucion del webhook
- **THEN** el webhook responde con un incidente creado y existe una sola fila para su `origen_message_id`

#### Scenario: Conectividad restaurada ante fallo

- **WHEN** la verificacion de recuperacion falla o se interrumpe
- **THEN** el backend queda reconectado a la red de automatizacion antes de que el arnes termine

#### Scenario: Verificacion ausente sin flag

- **WHEN** el arnes se ejecuta sin el flag de recuperacion
- **THEN** no desconecta ningun servicio y no agrega el check de recuperacion

### Requirement: Grupo de verificacion del borde TLS

El arnes SHALL ofrecer, bajo un flag explicito, el grupo de checks `tls:*` que implementa la verificacion automatizada del borde TLS del despliegue de referencia definida en `tls-docker-compose`, reutilizando el levantado del stack, el modelo de checks y el contrato de exit code del arnes. Las llamadas del grupo MUST verificar la identidad del servidor contra el certificado generado para la corrida (como ancla de confianza o por huella SHA-256) y MUST NOT desactivar la verificacion. Una comprobacion que el cliente local no pueda ejecutar SHALL quedar pendiente y MUST NOT contarse como exito.

#### Scenario: Grupo TLS completo en verde

- **WHEN** se ejecuta el arnes con el flag TLS sobre el stack de referencia levantado con certificados efimeros
- **THEN** todos los checks `tls:*` pasan y el resumen final es verde

#### Scenario: Comprobacion no ejecutable reportada como pendiente

- **WHEN** el cliente local no puede ofrecer TLS 1.1 para probar el rechazo
- **THEN** el check correspondiente queda pendiente y el arnes termina con exit code distinto de cero

### Requirement: La transformacion de costo cero conserva el tramo de alta

La copia de costo cero del workflow que importa el arnes SHALL conservar los nodos del tramo de alta del canal web (normalizacion, validacion, `Login operador`, `HTTP POST a MESA-AYUDAS`, gate de revision y respuestas del webhook) con sus ajustes de nivel de nodo (`retryOnFail`, `maxTries`, `waitBetweenTries`, `onError`) y sus `parameters.options`. Al inyectar las credenciales locales en `Login operador`, la transformacion MUST fusionar sus parametros en lugar de reemplazarlos, de modo que el `timeout` declarado sobreviva.

#### Scenario: Los ajustes de reintento sobreviven a la transformacion

- **WHEN** se aplica la transformacion de costo cero a `n8n/workflow.json`
- **THEN** `Login operador` y `HTTP POST a MESA-AYUDAS` conservan `retryOnFail`, `maxTries`, `waitBetweenTries`, `onError` y `parameters.options.timeout` con los mismos valores que el workflow versionado

#### Scenario: El tramo web sigue completo

- **WHEN** se inspecciona el workflow transformado
- **THEN** el camino desde `Webhook formulario web` hasta las respuestas del webhook sigue conectado sin referencias a nodos eliminados

### Requirement: Reporte de evidencia del recorrido

El arnes SHALL poder escribir, bajo una opcion explicita, un reporte JSON con el commit del arbol verificado, la fecha y hora en UTC, la version de N8N del stack, los grupos ejecutados y el resultado y detalle de cada check. El reporte MUST NOT contener contrasenas, tokens, claves ni certificados.

#### Scenario: Reporte generado con trazabilidad

- **WHEN** el arnes se ejecuta con la opcion de reporte
- **THEN** el archivo JSON resultante incluye commit, fecha UTC, version de N8N y el resultado de cada check ejecutado

#### Scenario: Reporte sin secretos

- **WHEN** se inspecciona el reporte generado
- **THEN** no contiene la contrasena del operador, el token de acceso, claves de API ni material criptografico
