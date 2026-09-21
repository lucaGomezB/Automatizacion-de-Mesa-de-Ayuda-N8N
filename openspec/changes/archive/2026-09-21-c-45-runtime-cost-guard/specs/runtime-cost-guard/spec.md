## Purpose

Acotar en tiempo de ejecución el gasto de las TRES superficies pagas (Gemini del backend, Gemini del `AI Agent` de n8n y transcripción de Twilio) mediante un presupuesto global compartido configurable, costos unitarios por superficie y un límite de tasa por número de origen, de modo que activar credenciales reales no produzca costos descontrolados, con bloqueo real del gasto de Twilio, degradación segura, observabilidad, fail-closed ante almacén no disponible y defaults explícitos.

## ADDED Requirements

### Requirement: Presupuesto global compartido entre las tres superficies pagas

El sistema SHALL aplicar un único presupuesto global de gasto pago, expresado en una unidad monetaria común (USD) y una ventana temporal, compartido por las tres superficies pagas: Gemini del backend, Gemini del `AI Agent` de n8n y transcripción de Twilio. El sistema SHALL acumular el gasto de todas las superficies en la misma bolsa. El monto, la ventana y la unidad MUST ser configurables sin modificar el código. Cuando el gasto acumulado de la bolsa global en la ventana alcanza o supera el presupuesto configurado, el sistema SHALL considerar el presupuesto agotado y la guarda SHALL dispararse para cualquier superficie. Al iniciar una ventana nueva, el gasto acumulado SHALL reiniciarse a cero.

#### Scenario: Gasto global por debajo del presupuesto permite la llamada paga

- **WHEN** el gasto acumulado de la bolsa global en la ventana vigente es inferior al presupuesto configurado
- **THEN** la guarda permite la llamada paga en la superficie evaluada

#### Scenario: El gasto de una superficie consume la bolsa compartida

- **WHEN** una superficie paga acumula gasto y otra superficie inicia una llamada paga
- **THEN** la segunda evaluación considera el gasto acumulado por la primera, porque ambas comparten la misma bolsa

#### Scenario: Presupuesto global agotado dispara la guarda en cualquier superficie

- **WHEN** el gasto acumulado de la bolsa global alcanza o supera el presupuesto configurado
- **THEN** la guarda se dispara e impide la llamada paga en cualquiera de las tres superficies

#### Scenario: La ventana nueva reinicia el gasto acumulado

- **WHEN** transcurre la ventana configurada y comienza una ventana nueva
- **THEN** el gasto acumulado se reinicia a cero y la guarda vuelve a permitir llamadas pagas dentro del nuevo presupuesto

### Requirement: Costo unitario por superficie paga

El sistema SHALL convertir el gasto de cada superficie paga a la unidad monetaria común mediante un costo unitario configurable por superficie. Cada llamada paga concedida SHALL reservar exactamente el costo unitario de su superficie en la bolsa global. Los costos unitarios MUST ser configurables sin modificar el código y SHALL quedar documentados como estimaciones, no como contabilidad exacta.

#### Scenario: La reserva usa el costo unitario de la superficie evaluada

- **WHEN** la guarda concede una llamada paga de una superficie
- **THEN** descuenta de la bolsa global el costo unitario configurado para esa superficie

#### Scenario: Superficies distintas usan costos unitarios distintos

- **WHEN** se conceden llamadas pagas de dos superficies con costos unitarios diferentes
- **THEN** cada una descuenta su propio costo unitario de la misma bolsa global

### Requirement: Límite de tasa de llamadas pagas

El sistema SHALL aplicar un límite de tasa configurable sobre la cantidad total de llamadas pagas dentro de una ventana temporal, independientemente del presupuesto de gasto. Cuando la cantidad de llamadas pagas en la ventana alcanza o supera el límite configurado, la guarda SHALL dispararse e impedir llamadas pagas adicionales hasta que la ventana se reinicie. El límite y su ventana MUST ser configurables sin modificar el código.

#### Scenario: Tasa por debajo del límite permite la llamada paga

- **WHEN** la cantidad de llamadas pagas en la ventana vigente es inferior al límite configurado
- **THEN** la guarda permite la llamada paga

#### Scenario: Límite de tasa alcanzado dispara la guarda

- **WHEN** la cantidad de llamadas pagas en la ventana vigente alcanza o supera el límite configurado
- **THEN** la guarda se dispara e impide llamadas pagas adicionales

#### Scenario: El reinicio de la ventana de tasa rehabilita llamadas

- **WHEN** transcurre la ventana del límite de tasa y comienza una ventana nueva
- **THEN** el contador de llamadas se reinicia y la guarda vuelve a permitir llamadas pagas

### Requirement: Límite de tasa por número de origen

El sistema SHALL aplicar, además del presupuesto global, un límite de tasa configurable sobre la cantidad de llamadas pagas atribuibles a un mismo número de origen (el número del llamador). La identificación del origen SHALL usar el número provisto por el proveedor de telefonía. Cuando un número de origen alcanza o supera el límite configurado dentro de la ventana, la guarda SHALL dispararse para ese origen hasta que la ventana se reinicie. El límite y su ventana MUST ser configurables sin modificar el código.

#### Scenario: Origen por debajo del límite permite la llamada

- **WHEN** la cantidad de llamadas pagas atribuidas a un número de origen en la ventana vigente es inferior al límite configurado
- **THEN** la guarda permite la llamada de ese origen

#### Scenario: Origen excedido dispara la guarda solo para ese origen

- **WHEN** un número de origen alcanza o supera el límite configurado en la ventana vigente
- **THEN** la guarda se dispara e impide llamadas pagas adicionales de ese origen, sin impedir por sí sola las de otros orígenes por debajo de su límite

#### Scenario: El reinicio de la ventana del origen rehabilita sus llamadas

- **WHEN** transcurre la ventana del límite por origen y comienza una ventana nueva
- **THEN** el contador de ese origen se reinicia y la guarda vuelve a permitir sus llamadas pagas

### Requirement: Evaluación de la guarda antes de la llamada paga

La guarda SHALL evaluarse antes de invocar cualquier proveedor pago dentro de su alcance (Gemini del backend, Gemini del `AI Agent` de n8n y transcripción de Twilio), de modo que una decisión denegada impida efectivamente la invocación. El camino que no invoca al proveedor pago (clasificación determinística de alta confianza y clasificación precalculada provista por el emisor) MUST NOT consumir presupuesto ni quedar sujeto a la guarda. El alcance de los puntos de llamada paga cubiertos SHALL ser explícito.

#### Scenario: La llamada paga solo ocurre con la guarda permitiendo

- **WHEN** el flujo de clasificación requiere invocar al proveedor pago
- **THEN** la guarda se evalúa primero y el proveedor se invoca únicamente si la guarda lo permite

#### Scenario: La clasificación precalculada no consume presupuesto

- **WHEN** un incidente llega con clasificación precalculada válida y el clasificador pago se omite
- **THEN** la guarda no se consulta ni se descuenta gasto ni conteo de tasa

#### Scenario: El cortocircuito determinístico no consume presupuesto

- **WHEN** el clasificador determinístico alcanza la confianza suficiente y omite al proveedor pago
- **THEN** la guarda no se consulta ni se descuenta gasto ni conteo de tasa

### Requirement: Enforcement del AI Agent de n8n antes de invocarlo

Antes de invocar al `AI Agent` de n8n, el flujo de telefonía SHALL consultar la guarda mediante un endpoint del backend. Si la guarda deniega, el flujo MUST NOT invocar al `AI Agent` y SHALL derivar el incidente a revisión humana con confianza cero. Si la guarda permite, el flujo SHALL continuar con la invocación normal. La reserva de la superficie `n8n_gemini` SHALL cubrir el número acotado de invocaciones del agente por ejecución.

#### Scenario: La guarda permite y el AI Agent se invoca

- **WHEN** el flujo de telefonía consulta la guarda antes del `AI Agent` y la guarda permite
- **THEN** el `AI Agent` se invoca normalmente

#### Scenario: La guarda deniega y el AI Agent no se invoca

- **WHEN** el flujo de telefonía consulta la guarda antes del `AI Agent` y la guarda deniega
- **THEN** el `AI Agent` NO se invoca y el incidente se deriva a revisión humana con confianza cero

### Requirement: Enforcement pre-llamada de Twilio mediante webhook de voz

El sistema SHALL exponer un webhook de voz que Twilio consulta ANTES de grabar y transcribir. El webhook SHALL recibir los parámetros estándar del webhook de voz (incluido el número de origen) y SHALL consultar la guarda (bolsa global y límite por origen). Si la guarda permite, SHALL responder TwiML que ejecuta la grabación con transcripción habilitada. Si la guarda deniega, SHALL responder TwiML que rechaza la grabación con un mensaje y cuelga la llamada, de modo que NO se grabe ni se transcriba. Dado que la duración es desconocida al inicio de la llamada, la reserva SHALL ser de una unidad del costo unitario de transcripción por llamada concedida, consistente con el modelo de cantidad de llamadas por costo unitario.

#### Scenario: Guarda permite y Twilio graba con transcripción

- **WHEN** llega una llamada y la guarda permite su transcripción
- **THEN** el webhook responde TwiML que graba la llamada con transcripción habilitada

#### Scenario: Guarda deniega y Twilio no graba ni transcribe

- **WHEN** llega una llamada y la guarda la deniega por presupuesto o por límite de origen
- **THEN** el webhook responde TwiML que rechaza la grabación con un mensaje y cuelga la llamada, sin grabar ni transcribir

#### Scenario: La reserva no depende de la duración desconocida

- **WHEN** la guarda concede una llamada de transcripción al inicio, antes de conocer su duración
- **THEN** reserva exactamente una unidad del costo unitario de transcripción por esa llamada

### Requirement: Captura y registro del número de origen crudo con exclusión del corpus

El sistema SHALL capturar el número de origen provisto por el proveedor de telefonía y SHALL registrarlo de forma CRUDA en los eventos estructurados de la guarda y usarlo como clave del contador de tasa por origen. El número crudo MUST NOT incorporarse a las tablas de negocio del incidente ni al corpus de evaluación de la tesis. Su retención SHALL quedar acotada a la ventana del contador de origen.

#### Scenario: El número de origen se registra crudo en la guarda

- **WHEN** la guarda evalúa una llamada de telefonía con un número de origen disponible
- **THEN** el número crudo queda disponible para la atribución en los eventos de la guarda y como clave del contador por origen

#### Scenario: El número de origen no entra al corpus de evaluación

- **WHEN** se genera o actualiza el corpus de evaluación de la tesis
- **THEN** el corpus NO incluye el número de origen registrado por la guarda

### Requirement: Degradación segura al excederse el presupuesto o la tasa

Cuando la guarda se dispara, el sistema SHALL aplicar una política de degradación configurable y MUST NOT invocar al proveedor pago. La política por defecto SHALL ser degradar al clasificador determinístico marcando revisión humana. La degradación SHALL conservar la mejor estimación determinística disponible cuando exista y MUST NOT propagar un estado inconsistente.

#### Scenario: Degradación por fallback a determinístico con revisión humana

- **WHEN** la guarda se dispara y la política configurada es degradar al clasificador determinístico
- **THEN** el sistema devuelve el resultado determinístico marcado para revisión humana y no invoca al proveedor pago

#### Scenario: Degradación por bloqueo duro

- **WHEN** la guarda se dispara y la política configurada es bloquear
- **THEN** el sistema rechaza o difiere la operación con una señal explícita y no invoca al proveedor pago

#### Scenario: Ninguna política dispara la llamada paga

- **WHEN** la guarda se dispara bajo cualquier política configurada
- **THEN** el proveedor pago no se invoca en ningún caso

### Requirement: Fail-closed ante almacén no disponible con notificación

Cuando el almacén que persiste los contadores de la guarda no está disponible, el sistema SHALL aplicar fail-closed: SHALL denegar la llamada paga y SHALL degradar el flujo de forma segura. La indisponibilidad SHALL quedar registrada de forma observable mediante un evento estructurado de notificación. La política SHALL ser explícita y configurable, y MUST NOT resolverse de manera silenciosa ni ambigua.

#### Scenario: Almacén no disponible deniega la llamada paga

- **WHEN** el almacén de contadores no responde durante una evaluación de la guarda
- **THEN** el sistema deniega la llamada paga y degrada a determinístico con revisión humana, sin invocar al proveedor pago

#### Scenario: La indisponibilidad emite una notificación estructurada

- **WHEN** el almacén de contadores no responde durante una evaluación de la guarda
- **THEN** el sistema emite un evento estructurado de indisponibilidad que identifica la causa, la superficie y la ventana, sin secretos

#### Scenario: La política no queda implícita

- **WHEN** el almacén de contadores no responde y no hay política configurada explícitamente
- **THEN** el sistema aplica el default documentado (fail-closed) y lo registra, sin decidir de forma silenciosa

### Requirement: Estado por defecto habilitado conservador con override

El sistema SHALL declarar un comportamiento por defecto explícito y determinista para el estado sin configuración de la guarda: HABILITADA con presupuesto conservador, fail-closed. Ese default MUST quedar documentado en un único lugar canónico y MUST aplicarse de forma idéntica en cada arranque. El default SHALL poder sobrescribirse explícitamente por configuración de entorno. La ausencia de configuración MUST NOT producir un comportamiento ambiguo ni silencioso.

#### Scenario: Sin configuración la guarda arranca habilitada y conservadora

- **WHEN** el sistema arranca sin configuración explícita de la guarda
- **THEN** la guarda queda habilitada con el presupuesto conservador documentado y la política fail-closed, y registra el estado efectivo

#### Scenario: La configuración de entorno sobrescribe el default

- **WHEN** se define explícitamente el presupuesto o la habilitación por configuración de entorno
- **THEN** la guarda usa el valor configurado en lugar del default documentado

#### Scenario: El default es estable entre arranques

- **WHEN** el sistema arranca más de una vez sin configuración de la guarda
- **THEN** el comportamiento por defecto es el mismo en todos los arranques

### Requirement: Observabilidad del disparo y de la indisponibilidad

Cuando la guarda se dispara, el sistema SHALL emitir un evento de log estructurado que identifique la causa del disparo (presupuesto, tasa global o tasa por origen), la superficie paga, la ventana vigente y el límite configurado. Cuando el almacén no está disponible, el sistema SHALL emitir un evento estructurado de indisponibilidad. Los eventos MUST NOT contener secretos. Cuando la guarda permite una llamada, NO SHALL emitir un evento de disparo. El sistema MAY emitir una alerta además del log.

#### Scenario: El disparo emite un evento estructurado

- **WHEN** la guarda se dispara por presupuesto agotado o por tasa excedida
- **THEN** se emite un evento de log estructurado que nombra la causa, la superficie, la ventana y el límite, sin secretos

#### Scenario: Una llamada permitida no emite evento de disparo

- **WHEN** la guarda permite una llamada paga
- **THEN** no se emite un evento de disparo de la guarda

### Requirement: Postura efectiva de la guarda al arranque

Al arrancar, el sistema SHALL determinar y registrar la postura efectiva de la guarda (habilitada o deshabilitada, presupuesto, ventana, costo unitario por superficie, límite de tasa global, límite por origen y política de degradación) de modo que un operador pueda verificar la configuración sin inspeccionar el código. Cuando la configuración falte o sea inválida, el sistema SHALL fallar de forma explícita o aplicar el default documentado, según corresponda, y MUST NOT arrancar en un estado de gasto no acotado sin advertirlo.

#### Scenario: El arranque registra la postura efectiva

- **WHEN** el sistema arranca con configuración válida de la guarda
- **THEN** registra la postura efectiva incluyendo presupuesto, ventana, costos unitarios, tasas y política de degradación

#### Scenario: Configuración inválida no arranca en estado ambiguo

- **WHEN** la configuración de la guarda es inválida (por ejemplo un monto o límite no numérico)
- **THEN** el sistema falla de forma explícita o aplica el default documentado, y no arranca con un estado de gasto no acotado sin advertirlo

### Requirement: Evaluabilidad offline con dependencias inyectadas

La guarda SHALL poder evaluarse sin acceso a red, sin PostgreSQL y sin proveedores pagos reales, inyectando el almacén de contadores y la fuente de tiempo como dependencias. Las pruebas unitarias de la guarda MUST NOT abrir conexiones de red ni requerir servicios externos.

#### Scenario: Evaluación con almacén y reloj inyectados

- **WHEN** una prueba instancia la guarda con un almacén de contadores falso y un reloj controlado
- **THEN** la guarda decide de forma determinista sin abrir conexiones de red ni requerir servicios externos

#### Scenario: Reinicio de ventana verificable sin servicios reales

- **WHEN** una prueba avanza el reloj inyectado más allá de la ventana configurada
- **THEN** la guarda reinicia los contadores y permite la llamada, sin depender de un servicio de tiempo real
