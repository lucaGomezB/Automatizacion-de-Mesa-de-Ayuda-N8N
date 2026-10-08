# notification-routing Specification

## Purpose
Definir como el backend resuelve los destinatarios de las notificaciones de incidente a partir del directorio de empleados (c-54), por rol y sector, con precedencia del directorio sobre un destinatario de respaldo, un envio por destinatario y las garantias de privacidad y no-bloqueo del alta.

## Requirements

### Requirement: NR-001 — El directorio es la fuente de verdad de los destinatarios

El sistema SHALL resolver los destinatarios de la notificacion de revision humana desde el directorio `directorio_empleado` (c-54) y MUST NOT obtenerlos de una lista fija en el backend ni de una variable de entorno de N8N. El directorio SHALL ser la unica fuente de verdad de roles y direcciones de contacto para el enrutamiento de notificaciones.

#### Scenario: Los destinatarios provienen del directorio

- **WHEN** un incidente requiere revision humana y existe un operador activo del sector en el directorio
- **THEN** el destinatario de la notificacion es el email de ese operador tomado del directorio

#### Scenario: Sin directorio no hay lista embebida

- **WHEN** se inspecciona la configuracion del backend
- **THEN** no existe una lista fija de destinatarios de notificacion ni una direccion de operador embebida

### Requirement: NR-002 — Resolucion por rol y sector

Para la notificacion de revision humana, el sistema SHALL seleccionar como destinatarios a los empleados ACTIVOS con rol `operador` cuyo sector coincida con el sector predicho principal del incidente. El sistema MUST NOT seleccionar empleados con rol `usuario_final` ni `administrador_directorio`, ni empleados inactivos. Si el incidente no tiene sector resuelto o ningun operador activo coincide, el resultado SHALL ser una lista vacia, sin error.

#### Scenario: Operador del sector resuelto

- **WHEN** un incidente del sector X requiere revision y existe un operador activo del sector X
- **THEN** ese operador es un destinatario de la notificacion

#### Scenario: Varios operadores del sector

- **WHEN** un incidente del sector X requiere revision y hay N operadores activos del sector X
- **THEN** la resolucion devuelve los N destinatarios, sin duplicados

#### Scenario: Empleados de otros roles excluidos

- **WHEN** el directorio contiene `usuario_final` y `administrador_directorio` del sector X
- **THEN** ninguno de los dos es destinatario de la notificacion de revision

#### Scenario: Operador inactivo excluido

- **WHEN** el unico operador del sector esta inactivo
- **THEN** no es destinatario y la lista resuelta queda vacia

#### Scenario: Sin sector no es fatal

- **WHEN** el incidente no tiene sector resuelto o ningun operador coincide
- **THEN** la resolucion devuelve una lista vacia sin lanzar excepcion ni bloquear el alta

### Requirement: NR-003 — Precedencia del directorio y destinatario de respaldo

Cuando el directorio resuelva al menos un destinatario, el sistema SHALL usar esos destinatarios y MUST NOT usar el de respaldo. Cuando no resuelva ninguno, el sistema SHALL preservar el camino de un solo destinatario usando la direccion configurada en el entorno (`OPERATOR_EMAIL`) como unico destinatario de respaldo. Esta precedencia SHALL permitir el arranque gradual: con el directorio vacio se conserva el destinatario unico actual; una vez poblado, el directorio toma precedencia.

#### Scenario: El directorio toma precedencia

- **WHEN** existe al menos un operador activo del sector
- **THEN** la notificacion se dirige a los operadores resueltos y NO al destinatario de respaldo

#### Scenario: Fallback al destinatario unico

- **WHEN** el directorio no resuelve ningun operador del sector (vacio o sin coincidencia)
- **THEN** la notificacion se dirige al unico destinatario configurado en el entorno

#### Scenario: Compatibilidad con un backend previo

- **WHEN** el payload de alta no provee destinatarios resueltos
- **THEN** el workflow usa el destinatario de respaldo del entorno sin fallar

### Requirement: NR-004 — Contrato de destinatarios backend -> N8N

El backend SHALL exponer los destinatarios resueltos a N8N en el payload que impulsa la notificacion de revision, como una lista de direcciones, vacia cuando no haya coincidencia. La lista SHALL acompanar a la marca `requiere_revision_humana` y al numero de incidente, de modo que el workflow no requiera resolver destinatarios por su cuenta. El contrato MUST NOT exigir que N8N consulte al backend por un endpoint de resolucion de contactos.

#### Scenario: La lista llega con la marca de revision

- **WHEN** el backend responde un alta con `requiere_revision_humana = true`
- **THEN** el payload incluye los destinatarios resueltos como una lista

#### Scenario: Lista vacia representable

- **WHEN** no se resuelve ningun destinatario
- **THEN** el payload presenta una lista vacia (no ausencia de campo ni error) y el workflow aplica el respaldo

#### Scenario: Sin round-trip adicional

- **WHEN** el workflow necesita los destinatarios
- **THEN** los obtiene del payload recibido y no de una llamada adicional al backend

### Requirement: NR-005 — Un envio por destinatario

El workflow SHALL enviar una copia de la notificacion por cada destinatario resuelto y MUST NOT exponer la lista completa de destinatarios en un campo compartido `To`, `Cc` ni `Bcc`. Cuando solo haya un destinatario (resuelto o de respaldo), el comportamiento SHALL ser un unico envio.

#### Scenario: Un correo por operador

- **WHEN** se resuelven N destinatarios
- **THEN** el workflow realiza N envios, uno por destinatario

#### Scenario: La lista no se expone entre destinatarios

- **WHEN** se inspecciona el campo de destinatario de los envios
- **THEN** cada envio direcciona a un unico destinatario y no a la lista completa

### Requirement: NR-006 — Privacidad y minimizacion

Los emails de destinatario son datos personales. El sistema MUST NOT registrar emails en claro en logs estructurados, auditoria ni respuestas de error. El backend SHALL reutilizar el directorio y su contrato de resolucion (c-54) para obtener los contactos y MUST NOT duplicar la logica de resolucion de identidad. La exposicion de los emails SHALL limitarse al payload autenticado que los necesita para direccionar la notificacion.

#### Scenario: Sin emails en la trazabilidad

- **WHEN** se completa una resolucion de destinatarios, con o sin coincidencia
- **THEN** el log y la auditoria indican el resultado y el sector, sin emails en claro

#### Scenario: Reutilizacion del directorio

- **WHEN** un servicio del backend resuelve destinatarios por rol y sector
- **THEN** lo hace sobre el directorio existente, sin una segunda fuente ni resolucion paralela

#### Scenario: El payload acotado a la notificacion

- **WHEN** se expone la lista de destinatarios
- **THEN** se limita al payload que impulsa la notificacion y no se agrega a las respuestas de consulta de incidentes

### Requirement: NR-007 — No-bloqueo del alta

La resolucion de destinatarios y el envio de la notificacion MUST NOT bloquear, demorar de forma observable ni alterar la respuesta de creacion del incidente. Un directorio vacio, ausente o con error NO SHALL propagarse al alta: el sistema SHALL continuar y aplicar el respaldo. El fallo del envio de la notificacion SHALL ser observable y MUST NOT impedir la auditoria.

#### Scenario: El alta no depende de la notificacion

- **WHEN** se crea un incidente que requiere revision
- **THEN** la respuesta de creacion se completa con independencia del resultado del envio de la notificacion

#### Scenario: Directorio no dispone de contacto

- **WHEN** el directorio esta vacio o la resolucion no encuentra operadores
- **THEN** el alta concluye con normalidad y la notificacion usa el respaldo

#### Scenario: Fallo de envio auditado

- **WHEN** el envio de la notificacion falla
- **THEN** la auditoria del incidente sigue registrandose
