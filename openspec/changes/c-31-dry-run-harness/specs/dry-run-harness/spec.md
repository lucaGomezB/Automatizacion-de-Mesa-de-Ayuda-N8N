## Purpose

Validar de forma local, reproducible y de costo cero el tramo compartido de registro de incidentes (normalización, validación, login dinámico, `POST /api/v1/incidentes/`, persistencia y clasificación) antes de configurar o consumir cualquier servicio pago, con preflight de contratos, guardarraíles de costo y fallo ruidoso y accionable ante quiebres de cableado.

## ADDED Requirements

### Requirement: Preflight de contratos locales

Antes de enviar cualquier incidente simulado, el arnés SHALL verificar de forma automatizada los contratos locales de los que depende el tramo compartido: que `POST /api/v1/auth/login` acepte JSON `{"username","password"}` y devuelva `{"access_token","token_type"}`; que una creación válida contra `POST /api/v1/incidentes/` con header `Authorization: Bearer <access_token>` responda 201; que una `descripcion` de menos de 10 caracteres responda 422; que una llamada sin la barra final sea detectada como redirección 307 (pérdida de `Authorization` y body); y que el webhook de N8N esté alcanzable. Cuando cualquiera de estas verificaciones falla, el arnés MUST abortar antes del recorrido end-to-end, MUST terminar con exit code distinto de cero y MUST identificar el contrato incumplido.

#### Scenario: Contrato de login válido

- **WHEN** el arnés invoca `POST /api/v1/auth/login` con credenciales locales válidas
- **THEN** la respuesta contiene `access_token` y `token_type`, y el token se usa como `Authorization: Bearer <access_token>` en las llamadas posteriores

#### Scenario: Alta válida responde 201

- **WHEN** el arnés envía una descripción válida con canal de formulario web y el token de login
- **THEN** el backend responde 201 y la respuesta incluye el identificador del incidente creado

#### Scenario: Descripción por debajo del mínimo responde 422

- **WHEN** el arnés envía una `descripcion` de menos de 10 caracteres
- **THEN** el backend responde 422 y el arnés registra el contrato de longitud mínima como verificado

#### Scenario: Falta de barra final se detecta como 307

- **WHEN** el arnés invoca la ruta de creación de incidentes sin la barra final
- **THEN** el arnés detecta la redirección 307 y la reporta como un quiebre de contrato que pierde `Authorization` y body

#### Scenario: Webhook de N8N alcanzable

- **WHEN** el arnés comprueba el webhook de N8N configurado para el formulario web
- **THEN** el webhook responde y el arnés registra el contrato de alcanzabilidad como verificado

#### Scenario: Aborto por contrato incumplido

- **WHEN** cualquiera de las verificaciones de preflight falla
- **THEN** el arnés no ejecuta el recorrido end-to-end, termina con exit code distinto de cero e indica qué contrato falló

### Requirement: Verificación end-to-end del canal web

El arnés SHALL enviar un incidente simulado del formulario web a través del webhook de N8N, esperar de forma acotada a que el workflow lo procese, y verificar contra el backend que el incidente quedó PERSISTIDO y que su `canal_origen_id` corresponde al formulario web (valor entero 2). El arnés MUST usar descripciones de prueba que activen al clasificador determinístico para evitar escaladas. Si el incidente no queda persistido dentro del tiempo acotado, o si queda persistido con un canal distinto del esperado, el arnés MUST fallar de forma ruidosa.

#### Scenario: Recorrido web completo persistido

- **WHEN** el arnés envía un incidente simulado del formulario web por el webhook de N8N y el tramo compartido está correctamente cableado
- **THEN** el backend devuelve ese incidente al consultarlo y el incidente queda persistido con `canal_origen_id` igual a 2

#### Scenario: Resolución determinística sin escalada

- **WHEN** el arnés envía una descripción de prueba elegida para pegar en las palabras clave determinísticas
- **THEN** el incidente se clasifica sin escalar al modelo pago y el resultado registra la etapa determinística

#### Scenario: Incidente no persistido

- **WHEN** el incidente simulado no queda persistido dentro del tiempo acotado
- **THEN** el arnés termina con exit code distinto de cero e informa que el webhook no completó el registro

#### Scenario: Canal persistido incorrecto

- **WHEN** el incidente simulado queda persistido con un `canal_origen_id` distinto de 2
- **THEN** el arnés termina con exit code distinto de cero e informa el canal observado y el esperado

### Requirement: Guardarraíl de costo cero

El arnés MUST operar sin invocar servicios pagos: MUST NOT realizar llamadas reales a Gemini ni a Twilio. Para lograrlo, el backend SHALL ejecutarse con una `GEMINI_API_KEY` ficticia, de modo que el clasificador determinístico resuelva los casos de alta confianza y cualquier escalada falle a un fallback seguro con `confianza=0.0` en lugar de llamar (y pagar) al modelo. Antes de ejecutar, el arnés MUST afirmar que una clave ficticia está en efecto y MUST abortar si detecta una clave real configurada.

#### Scenario: Clave ficticia afirmada antes de ejecutar

- **WHEN** el arnés inicia su recorrido
- **THEN** verifica que la `GEMINI_API_KEY` efectiva es ficticia y solo continúa si la afirmación se cumple

#### Scenario: Aborto ante clave real

- **WHEN** el arnés detecta que la `GEMINI_API_KEY` efectiva no es ficticia
- **THEN** termina con exit code distinto de cero sin enviar incidentes ni consumir el servicio pago

#### Scenario: Escalada fallida no genera costo

- **WHEN** un incidente de prueba obtiene del clasificador determinístico una confianza menor al umbral de escalada
- **THEN** la escalada falla de forma segura con `confianza=0.0` y no se completa ninguna llamada paga a Gemini

#### Scenario: Twilio nunca se invoca

- **WHEN** el arnés ejecuta su camino de costo cero
- **THEN** no se crea ninguna llamada, transcripción ni recurso de Twilio

### Requirement: Fallo ruidoso y accionable

El arnés SHALL reportar cada verificación con su resultado y MUST terminar con exit code distinto de cero ante cualquier quiebre de cableado. Todo fallo MUST emitir un mensaje accionable que nombre el componente o contrato afectado y el siguiente paso concreto para corregirlo. El arnés MUST NOT reportar éxito si alguna verificación quedó incompleta o fallida, y MUST imprimir un resumen final de verificaciones ejecutadas.

#### Scenario: Quiebre de cableado reportado

- **WHEN** cualquier verificación del preflight o del recorrido end-to-end falla
- **THEN** el arnés termina con exit code distinto de cero y su salida nombra el componente afectado y el siguiente paso para corregirlo

#### Scenario: Éxito solo con todas las verificaciones en verde

- **WHEN** todas las verificaciones pasan
- **THEN** el arnés imprime un resumen de verificaciones exitosas y termina con exit code cero

#### Scenario: Resultado parcial no se reporta como éxito

- **WHEN** una verificación queda incompleta o fue omitida
- **THEN** el arnés no reporta éxito y declara explícitamente la verificación pendiente

### Requirement: Canal correo documentado y opcionalmente automatizado

El arnés SHALL documentar el paso de ejecución en seco del canal correo (Outlook), que es gratuito porque el trigger hace polling, indicando cómo inducir un mensaje, cómo verificar la persistencia del incidente con `canal_origen_id` igual a 1 y qué credenciales se requieren. La automatización de este paso SHALL ser opcional y MUST quedar fuera del camino mínimo obligatorio, de modo que el arnés funcione sin credenciales de correo.

#### Scenario: Procedimiento de correo documentado

- **WHEN** un operador consulta la documentación del arnés
- **THEN** encuentra el procedimiento del canal correo con los pasos de inducción, verificación de persistencia (canal igual a 1) y credenciales requeridas

#### Scenario: Paso de correo opcional

- **WHEN** el arnés se ejecuta sin credenciales de correo configuradas
- **THEN** el camino de costo cero del canal web completa sin requerir el paso de correo

### Requirement: Canal teléfono fuera del camino de costo cero

El canal telefónico (Twilio) MUST quedar explícitamente fuera del camino de costo cero del arnés. El arnés MUST limitarse a documentar un procedimiento manual acotado a una o dos llamadas para cuando el usuario disponga de credenciales, y MUST NOT marcar, crear ni disparar recursos o llamadas de Twilio en ninguna ejecución.

#### Scenario: Procedimiento telefónico manual documentado

- **WHEN** un operador consulta la documentación del arnés
- **THEN** encuentra un procedimiento manual y acotado para validar el canal telefónico con credenciales reales, marcado como pago y fuera del camino de costo cero

#### Scenario: El arnés no toca Twilio

- **WHEN** el arnés ejecuta cualquier variante soportada
- **THEN** no realiza ninguna llamada ni crea ningún recurso de Twilio

### Requirement: Uso no destructivo del stack local

El arnés SHALL operar sobre el stack de Compose con nombre de proyecto fijo `mesa_local` y MUST NOT pasar el flag `-p`. El arnés SHALL reutilizar el stack ya en ejecución cuando exista o levantarlo cuando no exista, y MUST NOT modificar `docker-compose.yml`, `n8n/workflow.json` ni código de producto bajo `App/**`.

#### Scenario: Proyecto de Compose fijado

- **WHEN** el arnés invoca `docker compose`
- **THEN** no incluye `-p` y opera sobre el proyecto `mesa_local`

#### Scenario: Reutilización del stack en ejecución

- **WHEN** el stack `mesa_local` ya está en ejecución y sano
- **THEN** el arnés lo reutiliza sin recrearlo ni detenerlo

#### Scenario: Sin cambios en artefactos del repositorio

- **WHEN** el arnés completa su recorrido
- **THEN** no deja modificados `docker-compose.yml`, `n8n/workflow.json` ni archivos de producto bajo `App/**`
