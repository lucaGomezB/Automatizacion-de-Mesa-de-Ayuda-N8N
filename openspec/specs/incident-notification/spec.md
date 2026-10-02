# incident-notification Specification

## Purpose
Definir el contrato de notificación del número de incidente al usuario final en los canales de correo y formulario web, incluyendo la garantía de entrega aun cuando el incidente se derive a revisión humana y el comportamiento ante un contacto faltante. La notificación al llamante por telefonía (SMS) se movió a `c-67-notificacion-sms-llamante`.

## Requirements

### Requirement: Número de incidente canónico y legible

El sistema SHALL exponer un número de incidente único, estable y legible para el usuario final, derivado del identificador persistido del incidente. El número SHALL ser el mismo que el backend retorna en el alta y que el workflow de orquestación propaga en sus notificaciones. El sistema MUST NOT presentar identificadores distintos por canal para un mismo incidente. La personalización por prefijo configurable queda fuera de este contrato.

#### Scenario: El número es el identificador persistido

- **WHEN** un incidente se crea por cualquiera de los tres canales
- **THEN** el número notificado al usuario es el identificador persistido del incidente

#### Scenario: El mismo número en todos los canales

- **WHEN** un incidente se crea por un canal y se notifica al usuario
- **THEN** el número notificado coincide con el que el backend expone para ese incidente

### Requirement: Notificación de confirmación al usuario en el canal correo

El sistema SHALL enviar al remitente original un correo de confirmación que incluya el número de incidente, SIEMPRE que el incidente se haya creado, con independencia de que el incidente haya sido derivado a revisión humana. El destinatario SHALL resolverse a una dirección de correo válida a partir del remitente del mensaje entrante, admitiendo que el remitente llegue tanto como cadena como como objeto estructurado del proveedor de correo. La ausencia de un destinatario válido MUST NOT abortar el flujo de alta.

#### Scenario: Confirmación de correo en el alta normal

- **WHEN** un incidente del canal correo se crea sin requerir revisión humana
- **THEN** el workflow envía un correo de confirmación al remitente original con el número de incidente

#### Scenario: Confirmación de correo en revisión humana

- **WHEN** un incidente del canal correo se crea y requiere revisión humana
- **THEN** el workflow igualmente envía el correo de confirmación al remitente original con el número de incidente

#### Scenario: Remitente estructurado produce destinatario válido

- **WHEN** el remitente entrante es un objeto estructurado que anida la dirección de correo
- **THEN** el destinatario de la confirmación resuelve a la dirección de correo efectiva y no a una representación inválida

### Requirement: Notificación de confirmación al usuario en el canal web

El sistema SHALL responder al envío del formulario web con el número de incidente, SIEMPRE que el incidente se haya creado, con independencia de que el incidente haya sido derivado a revisión humana. La respuesta SHALL ser síncrona con la petición del formulario. Cuando no exista un incidente creado, la respuesta SHALL indicar de forma explícita que no hubo alta, sin presentar un número inexistente.

#### Scenario: Respuesta web con número en el alta normal

- **WHEN** un incidente del canal web se crea sin requerir revisión humana
- **THEN** la respuesta al formulario incluye el número de incidente creado

#### Scenario: Respuesta web con número en revisión humana

- **WHEN** un incidente del canal web se crea y requiere revisión humana
- **THEN** la respuesta al formulario incluye el número de incidente creado y no un valor nulo

#### Scenario: Respuesta web sin alta

- **WHEN** una petición del canal web no produce la creación de un incidente
- **THEN** la respuesta indica que no hubo alta y no presenta un número de incidente
