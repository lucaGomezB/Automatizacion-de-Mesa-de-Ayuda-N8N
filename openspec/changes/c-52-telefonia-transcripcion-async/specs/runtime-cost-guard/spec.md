## MODIFIED Requirements

### Requirement: Presupuesto global compartido entre las tres superficies pagas

El sistema SHALL aplicar un único presupuesto global de gasto pago, expresado en una unidad monetaria común (USD) y una ventana temporal, compartido por las superficies pagas: Gemini del backend, Gemini del `AI Agent` de n8n, la transcripción del backend y la admisión de voz de Twilio. El sistema SHALL acumular el gasto de todas las superficies en la misma bolsa. El monto, la ventana y la unidad MUST ser configurables sin modificar el código. Cuando el gasto acumulado de la bolsa global en la ventana alcanza o supera el presupuesto configurado, el sistema SHALL considerar el presupuesto agotado y la guarda SHALL dispararse para cualquier superficie. Al iniciar una ventana nueva, el gasto acumulado SHALL reiniciarse a cero.

#### Scenario: Gasto global por debajo del presupuesto permite la llamada paga

- **WHEN** el gasto acumulado de la bolsa global en la ventana vigente es inferior al presupuesto configurado
- **THEN** la guarda permite la llamada paga en la superficie evaluada

#### Scenario: El gasto de una superficie consume la bolsa compartida

- **WHEN** una superficie paga acumula gasto y otra superficie inicia una llamada paga
- **THEN** la segunda evaluación considera el gasto acumulado por la primera, porque ambas comparten la misma bolsa

#### Scenario: Presupuesto global agotado dispara la guarda en cualquier superficie

- **WHEN** el gasto acumulado de la bolsa global alcanza o supera el presupuesto configurado
- **THEN** la guarda se dispara e impide la llamada paga en cualquiera de las superficies

#### Scenario: La ventana nueva reinicia el gasto acumulado

- **WHEN** transcurre la ventana configurada y comienza una ventana nueva
- **THEN** el gasto acumulado se reinicia a cero y la guarda vuelve a permitir llamadas pagas dentro del nuevo presupuesto

### Requirement: Enforcement pre-llamada de Twilio mediante webhook de voz

El sistema SHALL exponer un webhook de voz que Twilio consulta ANTES de grabar. El webhook SHALL recibir los parámetros estándar del webhook de voz (incluido el número de origen) y SHALL consultar la guarda (bolsa global y límite por origen). Si la guarda permite, SHALL responder TwiML que ejecuta la grabación en modo mono con las señales de estado y fin de grabación, SIN transcripción embebida. Si la guarda deniega, SHALL responder TwiML que rechaza la grabación con un mensaje y cuelga la llamada, de modo que NO se grabe. Dado que la duración es desconocida al inicio de la llamada, la reserva SHALL ser de una unidad del costo unitario de admisión de voz por llamada concedida, consistente con el modelo de cantidad de llamadas por costo unitario. La transcripción SHALL reservarse por separado al recibir el callback de grabación, no en este webhook.

#### Scenario: Guarda permite y Twilio graba con transcripción

- **WHEN** llega una llamada y la guarda permite su grabación
- **THEN** el webhook responde TwiML que graba la llamada en modo mono con señales de estado y fin de grabación; la transcripción embebida de Twilio no se usa y la transcripción se reserva por separado al recibir el callback del backend

#### Scenario: Guarda deniega y Twilio no graba ni transcribe

- **WHEN** llega una llamada y la guarda la deniega por presupuesto o por límite de origen
- **THEN** el webhook responde TwiML que rechaza la grabación con un mensaje y cuelga la llamada, sin grabar y por lo tanto sin transcripción posterior

#### Scenario: La reserva no depende de la duración desconocida

- **WHEN** la guarda concede una llamada de admisión al inicio, antes de conocer su duración
- **THEN** reserva exactamente una unidad del costo unitario de admisión de voz por esa llamada

#### Scenario: La transcripción no se reserva en el webhook de voz

- **WHEN** la guarda concede una llamada en el webhook de voz
- **THEN** la superficie de transcripción del backend no se reserva todavía, sino al recibir el callback de grabación

## ADDED Requirements

### Requirement: Superficie paga de transcripción del backend

El sistema SHALL declarar la transcripción del backend como una superficie paga propia, con su propio costo unitario configurable. La guarda SHALL evaluarse y reservar esa superficie ANTES de descargar y transcribir la grabación, de modo que una decisión denegada impida efectivamente la descarga y la invocación del proveedor de speech-to-text. La reserva SHALL estimarse a partir de la duración conocida de la grabación, acotada por un tope configurable. El costo unitario de la superficie de admisión de voz de Twilio SHALL re-estimarse, porque ya no representa una transcripción de Twilio.

#### Scenario: La reserva precede a la descarga y transcripción

- **WHEN** el backend recibe el callback de grabación de una llamada
- **THEN** evalúa y reserva la superficie de transcripción antes de descargar el audio y de invocar al proveedor de speech-to-text

#### Scenario: La guarda denegada impide la transcripción

- **WHEN** la guarda deniega la reserva de la superficie de transcripción
- **THEN** el backend no descarga la grabación ni invoca al proveedor de speech-to-text

#### Scenario: La reserva se estima por duración acotada

- **WHEN** el callback informa la duración de la grabación
- **THEN** la reserva se estima a partir de esa duración, acotada por el tope configurado (hasta 45 s)

#### Scenario: El costo de admisión de voz se re-estima

- **WHEN** se configura el costo unitario de la superficie de admisión de voz de Twilio
- **THEN** ese costo ya no representa una transcripción de Twilio, que dejó de usarse