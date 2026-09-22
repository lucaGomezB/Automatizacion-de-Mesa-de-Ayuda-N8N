## ADDED Requirements

### Requirement: N8N-GUARD-001 — La guarda de costo preserva el item del canal de telefonía

El nodo `Guard de costo` del canal de telefonía SHALL consultar la guarda SIN destruir el item sellado de la entrada. Como el nodo es un `httpRequest` y su salida es la respuesta del backend, el workflow SHALL restaurar el item recuperado de `Sellar ingreso telefonia` aguas abajo de la guarda y re-inyectarle la decisión de la guarda, de modo que (a) el `AI Agent` reciba el item sellado completo cuando la guarda permite, y (b) el nodo `Guard permite?` conserve la decisión `allowed` para rutear. La consulta a la guarda y su política de costo MUST NOT cambiar.

Alcance: este requisito cubre SOLO la propagación del item a través de la guarda. La presencia de un campo de transcripción/descripción en el payload del trigger de Twilio está FUERA de alcance: es una limitación heredada de C-45 (el evento `call-summary.complete` no expone la transcripción) y se rastrea por separado. C-47 garantiza que el `AI Agent` recibe el item sellado, no que ese item contenga una descripción no vacía.

#### Scenario: El AI Agent recibe el item sellado, no solo el cuerpo de la guarda

- **WHEN** el flujo de telefonía atraviesa el nodo `Guard de costo` y la guarda permite la invocación del `AI Agent`
- **THEN** el item que llega al `AI Agent` proviene de `Sellar ingreso telefonia` (con `allowed` re-inyectado) y NO es únicamente el cuerpo de la respuesta de la guarda

#### Scenario: La decisión de la guarda alimenta el ruteo

- **WHEN** la guarda responde con su decisión
- **THEN** el item restaurado aguas abajo expone `allowed` y el nodo `Guard permite?` rutea verdadero hacia el `AI Agent` y falso hacia `Derivar a revision humana`

#### Scenario: La rama denegada conserva el item

- **WHEN** la guarda deniega la invocación del `AI Agent`
- **THEN** el item que llega a `Derivar a revision humana` conserva el contenido de telefonía y el flujo deriva a revisión humana con confianza cero, sin invocar al agente pago

### Requirement: N8N-GUARD-002 — El caller de la guarda usa el item corriente, sin referencia frágil

El cuerpo del nodo `Guard de costo` SHALL resolver el número de origen llamante (`caller`) desde el item corriente del propio nodo (`$json.From || $json.from`) y MUST NOT usar la referencia `$('Sellar ingreso telefonia').item`, que depende de la resolución de `pairedItem` y puede devolver `null` sin señal. Como `Sellar ingreso telefonia` es la entrada directa de la guarda, el item corriente YA es el sellado, por lo que no se requiere una referencia cruzada entre nodos. La ausencia del número de origen MUST NOT impedir la evaluación de la guarda: `caller` es opcional y la reserva SHALL continuar. (La recuperación con `$('Sellar ingreso telefonia').first()` queda reservada al nodo de restauración de N8N-GUARD-001, cuyo item de entrada sí es la respuesta de la guarda.)

#### Scenario: El cuerpo de la guarda usa el item corriente y ninguna referencia cruzada

- **WHEN** la suite estructural inspecciona el body del nodo `Guard de costo`
- **THEN** el body resuelve `caller` desde `$json` (`$json.From` o `$json.from`) y NO referencia `$('Sellar ingreso telefonia')` (ni por `.item` ni por `.first()`)

#### Scenario: La ausencia del caller no impide la guarda

- **WHEN** el item sellado no expone un número de origen (`From` o `from` ausente)
- **THEN** el body resuelve `caller` a `null` y la guarda igual evalúa la reserva, sin abortar el flujo