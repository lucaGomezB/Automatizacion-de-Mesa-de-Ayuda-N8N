## MODIFIED Requirements

### Requirement: Presupuesto global compartido entre las tres superficies pagas

El sistema SHALL aplicar un único presupuesto global de gasto pago, expresado en una unidad monetaria común (USD) y una ventana temporal, compartido por las superficies pagas: Gemini del backend, Gemini del `AI Agent` de n8n, la admisión de voz de Twilio, la transcripción del backend y el SMS de notificación al usuario. El sistema SHALL acumular el gasto de todas las superficies en la misma bolsa. El monto, la ventana y la unidad MUST ser configurables sin modificar el código. Cuando el gasto acumulado de la bolsa global en la ventana alcanza o supera el presupuesto configurado, el sistema SHALL considerar el presupuesto agotado y la guarda SHALL dispararse para cualquier superficie. Al iniciar una ventana nueva, el gasto acumulado SHALL reiniciarse a cero.

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

### Requirement: Evaluación de la guarda antes de la llamada paga

La guarda SHALL evaluarse antes de invocar cualquier proveedor pago dentro de su alcance (Gemini del backend, Gemini del `AI Agent` de n8n, la admisión de voz de Twilio, la transcripción del backend y el envío del SMS de notificación), de modo que una decisión denegada impida efectivamente la invocación. El camino que no invoca al proveedor pago (clasificación determinística de alta confianza y clasificación precalculada provista por el emisor) MUST NOT consumir presupuesto ni quedar sujeto a la guarda. El alcance de los puntos de llamada paga cubiertos SHALL ser explícito.

#### Scenario: La llamada paga solo ocurre con la guarda permitiendo

- **WHEN** el flujo de clasificación requiere invocar al proveedor pago
- **THEN** la guarda se evalúa primero y el proveedor se invoca únicamente si la guarda lo permite

#### Scenario: El envío del SMS solo ocurre con la guarda permitiendo

- **WHEN** el sistema va a enviar el SMS de notificación al llamante
- **THEN** la guarda se evalúa y reserva primero, y el SMS se envía únicamente si la guarda lo permite

#### Scenario: La clasificación precalculada no consume presupuesto

- **WHEN** un incidente llega con clasificación precalculada válida y el clasificador pago se omite
- **THEN** la guarda no se consulta ni se descuenta gasto ni conteo de tasa

#### Scenario: El cortocircuito determinístico no consume presupuesto

- **WHEN** el clasificador determinístico alcanza la confianza suficiente y omite al proveedor pago
- **THEN** la guarda no se consulta ni se descuenta gasto ni conteo de tasa

## ADDED Requirements

### Requirement: Superficie paga de SMS de notificación

El sistema SHALL declarar el envío del SMS de notificación al llamante como una superficie paga propia (`twilio_sms`), con su propio costo unitario configurable. La guarda SHALL evaluarse y reservar esa superficie ANTES de invocar al proveedor de mensajería, de modo que una decisión denegada impida efectivamente el envío. La reserva SHALL ser de una unidad del costo unitario por SMS enviado y SHALL usar el número llamante como clave del contador de tasa por origen. Cuando la guarda deniegue el envío, el sistema SHALL omitir el SMS, SHALL registrar de forma observable la omisión y MUST NOT fallar el alta del incidente.

#### Scenario: La reserva precede al envío del SMS

- **WHEN** el sistema va a enviar un SMS de notificación
- **THEN** evalúa y reserva la superficie `twilio_sms` antes de invocar al proveedor de mensajería

#### Scenario: La guarda denegada impide el envío

- **WHEN** la guarda deniega la reserva de la superficie `twilio_sms`
- **THEN** el sistema no invoca al proveedor de mensajería y registra la omisión de forma observable

#### Scenario: La denegación no falla el alta

- **WHEN** la guarda deniega el envío del SMS
- **THEN** el incidente ya creado permanece persistido y el alta no se revierte

#### Scenario: El costo unitario del SMS es configurable

- **WHEN** se configura el costo unitario de la superficie `twilio_sms`
- **THEN** la reserva usa ese valor y el monto es ajustable sin modificar el código

#### Scenario: El origen del SMS alimenta el rate por número

- **WHEN** se reserva la superficie `twilio_sms` para un número llamante
- **THEN** el contador de tasa por origen usa ese número como clave