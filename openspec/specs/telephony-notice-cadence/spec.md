# telephony-notice-cadence Specification

## Purpose
Controlar de forma acotada y segura la tasa de locución del aviso de privacidad del
canal telefónico, de modo que el mismo texto pueda entregarse más rápido sin exponer
el documento TwiML a inyección ni alterar el aviso que reciben los titulares.

## Requirements

### Requirement: Tasa de locución acotada del aviso telefónico

El sistema SHALL permitir ajustar la tasa de locución del aviso de privacidad del canal
telefónico mediante un valor porcentual opcional, sin modificar el TEXTO del aviso.
Cuando no se solicite una tasa, el TwiML del aviso SHALL servirse a la tasa normal
(comportamiento vigente, sin envoltura `<prosody>`), de modo que el aviso de producción
que reciben los titulares no cambie. Cuando se solicite una tasa, el contenido del
`<Say>` SHALL envolverse en un elemento `<prosody>` con el atributo `rate`. El valor
aceptado SHALL estar acotado al rango 20–200%: un valor con formato válido pero fuera
del rango SHALL acotarse (clamp) al límite más cercano, y un valor con formato inválido
SHALL ignorarse, sirviéndose la tasa normal. La validación MUST impedir la inyección de
XML o de valores no acotados. El texto, los atributos y los callbacks del `<Record>`
MUST conservarse intactos.

#### Scenario: Sin tasa solicitada el aviso se sirve a tasa normal

- **WHEN** se solicita el TwiML de una llamada admitida sin una tasa de locución
- **THEN** el `<Say>` del aviso se sirve a la tasa normal, sin envoltura `<prosody>`, con el texto idéntico al vigente

#### Scenario: Una tasa válida envuelve el aviso en prosody

- **WHEN** se solicita el TwiML de una llamada admitida con una tasa válida (por ejemplo 125%)
- **THEN** el contenido del `<Say>` se envuelve en `<prosody rate="125%">` y el texto del aviso no cambia

#### Scenario: Una tasa fuera de rango se acota

- **WHEN** se solicita el aviso con una tasa de formato válido pero fuera del rango 20–200% (por ejemplo 500%)
- **THEN** la tasa efectiva se acota al límite más cercano (200%) y el XML sigue siendo válido

#### Scenario: Una tasa inválida no altera el aviso ni inyecta XML

- **WHEN** se solicita el aviso con una tasa de formato inválido (por ejemplo `"); <Hangup/>`)
- **THEN** el valor se ignora, el aviso se sirve a tasa normal y el XML no contiene elementos inyectados

### Requirement: El aviso acelerado conserva el texto y las obligaciones de PRIV-003

El ajuste de tasa SHALL ser una propiedad de la locución y MUST NOT alterar el contenido
del aviso de privacidad. El texto del `<Say>` SHALL permanecer idéntico en todos los
casos (con tasa o sin tasa) y MUST seguir declarando grabación, finalidad, responsable,
transferencia internacional, derechos y alineación con la Ley 25.326. El sistema MUST
NOT afirmar certificación ni conformidad como consecuencia de este ajuste.

#### Scenario: El texto del aviso es idéntico con y sin tasa

- **WHEN** se comparan los textos del `<Say>` del documento admitido con y sin tasa solicitada
- **THEN** ambos textos son idénticos y el aviso mantiene grabación, finalidad, responsable, transferencia, derechos y alineación con la Ley 25.326

#### Scenario: El ajuste no relaja las garantías del documento

- **WHEN** se valida el TwiML generado con y sin tasa
- **THEN** el `<Record>` conserva sus atributos y callbacks, el XML es válido y el texto del aviso sigue siendo estático
