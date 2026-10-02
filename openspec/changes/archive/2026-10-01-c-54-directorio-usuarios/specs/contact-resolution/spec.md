## Purpose

Define como el sistema resuelve la identidad de un contacto (empleado) a partir de los identificadores disponibles en cada canal de ingreso, y el contrato de enganche que permite a c-53 enriquecer sus notificaciones sin cambiar su contrato de entrega.

## ADDED Requirements

### Requirement: RES-001 — Resolucion por telefono

El sistema SHALL resolver un empleado a partir de un numero telefonico normalizado a E.164, comparando por igualdad contra el telefono almacenado en texto plano. La resolucion por telefono SHALL devolver el empleado activo cuyo telefono coincide exactamente, o un resultado vacio si no hay coincidencia o si la coincidencia es ambigua. La resolucion MUST NOT fallar cuando el numero no pertenece al directorio.

#### Scenario: Telefono conocido resuelve al empleado

- **WHEN** se resuelve un telefono que corresponde a un empleado activo
- **THEN** el sistema devuelve ese empleado

#### Scenario: Telefono desconocido no es fatal

- **WHEN** se resuelve un telefono que no corresponde a ningun empleado del directorio
- **THEN** el sistema devuelve un resultado vacio sin lanzar excepcion ni bloquear al llamador

#### Scenario: Normalizacion previa a la busqueda

- **WHEN** se resuelve un telefono con formato local o con separadores
- **THEN** el sistema lo normaliza a E.164 antes de comparar por igualdad

### Requirement: RES-002 — Resolucion por email

El sistema SHALL resolver un empleado a partir de una direccion de email normalizada a minusculas, comparando por igualdad contra el email almacenado en texto plano. La resolucion por email SHALL devolver el empleado activo cuyo email coincide exactamente, o un resultado vacio si no hay coincidencia o si la coincidencia es ambigua. El sistema MUST aceptar tanto una direccion simple como la direccion efectiva extraida de una estructura de remitente del canal de correo.

#### Scenario: Email conocido resuelve al empleado

- **WHEN** se resuelve un email que corresponde a un empleado activo
- **THEN** el sistema devuelve ese empleado

#### Scenario: Email desconocido no es fatal

- **WHEN** se resuelve un email que no corresponde a ningun empleado del directorio
- **THEN** el sistema devuelve un resultado vacio sin lanzar excepcion

#### Scenario: Email con mayusculas

- **WHEN** se resuelve un email con mayusculas o espacios
- **THEN** el sistema lo normaliza a minusculas y resuelve correctamente por igualdad

### Requirement: RES-003 — Resolucion por usuario autenticado

El sistema SHALL resolver un empleado a partir de la identidad de un usuario autenticado, siguiendo el vinculo opcional entre `users` y el directorio. Si la cuenta no tiene empleado vinculado, la resolucion SHALL devolver un resultado vacio y MUST NOT impedir la operacion del canal web.

#### Scenario: Cuenta vinculada resuelve al empleado

- **WHEN** un usuario autenticado tiene una fila de directorio vinculada
- **THEN** la resolucion devuelve el empleado correspondiente

#### Scenario: Cuenta sin empleado no es fatal

- **WHEN** un usuario autenticado no tiene empleado vinculado
- **THEN** la resolucion devuelve un resultado vacio y el flujo continua

### Requirement: RES-004 — Resultado unico y comportamiento ante ambiguedad

Cada busqueda por telefono o email normalizado SHALL devolver como maximo un empleado. Cuando el identificador corresponda a mas de un empleado activo, el sistema SHALL registrar la ambiguedad y MUST NOT elegir arbitrariamente un contacto. El sistema SHALL exponer un modelo de resultado unificado que represente "encontrado" o "no encontrado".

#### Scenario: Coincidencia unica

- **WHEN** un telefono o email normalizado corresponde a exactamente un empleado activo
- **THEN** la resolucion devuelve ese empleado

#### Scenario: Coincidencia ambigua

- **WHEN** un telefono o email normalizado corresponde a mas de un empleado activo
- **THEN** el sistema registra la ambiguedad y devuelve un resultado no concluyente, sin seleccionar un contacto

#### Scenario: Resultado vacio representable

- **WHEN** la resolucion no encuentra contacto
- **THEN** el modelo de resultado representa explicitamente el estado "no encontrado", distinguible de un error

### Requirement: RES-005 — Contrato de enganche con c-53

El sistema SHALL exponer la resolucion de contactos como un servicio interno con una interfaz estable, invocable en proceso por otros servicios del backend, que devuelva el empleado o un resultado vacio. Este contrato SHALL permitir que c-53 lo consuma como estrategia de resolucion de destinatario y enriquecimiento de enrutamiento por sector/rol. Este change MUST NOT implementar el envio de notificaciones ni modificar el contrato de entrega del numero de incidente de c-53.

#### Scenario: Estrategia enchufable sin cambiar el contrato de entrega

- **WHEN** c-53 resuelve el destinatario de una notificacion
- **THEN** puede consultar el servicio de resolucion y, si no hay contacto, conservar su comportamiento actual sin romper la entrega

#### Scenario: La resolucion no envia notificaciones

- **WHEN** se invoca el servicio de resolucion
- **THEN** no se produce ninguna llamada de notificacion, SMS ni correo

#### Scenario: Independencia de c-53

- **WHEN** el directorio esta vacio o no disponible
- **THEN** c-53 sigue operando con su resolucion directa actual

### Requirement: RES-006 — Minimizacion y trazabilidad de la resolucion

La resolucion SHALL operar sobre el identificador minimo necesario y MUST NOT registrar en claro el telefono ni el email resueltos. El sistema SHALL registrar de forma estructurada el canal de origen, el resultado (encontrado / no encontrado / ambiguo) y la ausencia de contacto, sin datos personales en claro.

#### Scenario: Trazabilidad sin PII

- **WHEN** se completa una resolucion, con o sin coincidencia
- **THEN** el log estructurado indica el resultado y el canal, sin el telefono ni el email en claro

#### Scenario: Identificador minimo

- **WHEN** un servicio solicita la resolucion
- **THEN** el sistema recibe solo el identificador necesario para la busqueda y no un paquete ampliado de datos del reportante
