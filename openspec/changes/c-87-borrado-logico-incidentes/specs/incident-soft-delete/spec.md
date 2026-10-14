## Purpose

Define el borrado logico de un incidente: conserva la fila con un marcador de borrado y la atribucion del actor, la retira de toda superficie de lectura y restringe la operacion al rol administrador del directorio.

## ADDED Requirements

### Requirement: SD-001 — Borrado logico preserva la fila y registra la atribucion

El sistema SHALL soportar el borrado LOGICO de un incidente marcando la fila con un instante de borrado (`deleted_at`, datetime) y la referencia nullable al empleado que lo ejecuto (`deleted_by`, FK a `directorio_empleado.id`). El borrado logico MUST NOT eliminar fisicamente la fila ni sus relaciones (clasificaciones, sectores adicionales). Un incidente nunca borrado SHALL conservar `deleted_at` y `deleted_by` en NULL. La referencia `deleted_by` SHALL usar `ON DELETE SET NULL`, de modo que el borrado ARCO del empleado actor NO elimine el incidente. El vinculo `deleted_by` SHALL ser nullable: una cuenta sin empleado vinculado NO SHALL poder ejecutar el borrado (ver SD-002).

#### Scenario: El borrado logico conserva la fila

- **WHEN** un incidente existente se borra logicamente
- **THEN** la fila del incidente y sus relaciones persisten; solo se setean `deleted_at` y `deleted_by`

#### Scenario: Incidente no borrado conserva el marcador nulo

- **WHEN** se inspecciona un incidente que nunca fue borrado
- **THEN** `deleted_at` y `deleted_by` son NULL

#### Scenario: La atribucion registra al actor

- **WHEN** un administrador con empleado vinculado borra logicamente un incidente
- **THEN** `deleted_by` referencia el empleado del actor y `deleted_at` queda con un instante UTC

#### Scenario: El borrado ARCO del actor no elimina el incidente

- **WHEN** el empleado referenciado por `deleted_by` se elimina por una operacion ARCO
- **THEN** el incidente persiste y `deleted_by` pasa a NULL sin borrar la fila

#### Scenario: Cuenta sin empleado vinculado no puede borrar

- **WHEN** una cuenta autenticada sin empleado vinculado intenta borrar logicamente un incidente
- **THEN** el sistema responde con error de autorizacion (HTTP 403) y no modifica ninguna fila

### Requirement: SD-002 — Endpoint de borrado logico exclusivo del administrador del directorio

El sistema SHALL exponer `DELETE /api/v1/incidentes/{incidente_id}` que ejecuta el borrado LOGICO (nunca fisico) y responde HTTP 204 No Content sin cuerpo. La autorizacion SHALL enforcarse server-side mediante el registro canonico de politica de rol (`role_policy`), sin listas de rol duplicadas en la ruta: unicamente un usuario cuyo rol declare el permiso de borrado de incidentes SHALL poder ejecutarlo. Un rol no autorizado SHALL recibir HTTP 403 sin modificar ninguna fila. Un incidente fuera del alcance de visibilidad del llamante, un incidente inexistente o un incidente ya borrado SHALL comportarse como NO ENCONTRADO (HTTP 404), sin revelar su existencia. La operacion SHALL registrar la atribucion del actor conforme a SD-001. El endpoint SHALL reutilizar el camino nuevo de borrado logico y NO SHALL invocar el borrado fisico existente.

#### Scenario: El administrador borra logicamente un incidente

- **WHEN** un usuario con rol `administrador_directorio` invoca `DELETE /api/v1/incidentes/{id}` sobre un incidente visible
- **THEN** el sistema marca la fila como borrada y responde HTTP 204 sin cuerpo

#### Scenario: Un rol no administrador es rechazado

- **WHEN** un usuario con rol `mesa_de_ayuda` o `usuario_final` invoca el endpoint de borrado logico
- **THEN** el sistema responde HTTP 403 y NO modifica ninguna fila

#### Scenario: Incidente fuera de alcance no se encuentra

- **WHEN** un administrador invoca el endpoint sobre un incidente que no existe o que esta fuera de su alcance
- **THEN** el sistema responde HTTP 404 sin revelar su existencia y sin modificar ninguna fila

#### Scenario: El borrado es idempotente por olvido del recurso

- **WHEN** se invoca el endpoint sobre un incidente ya borrado logicamente
- **THEN** el sistema responde HTTP 404 y no altera el marcador existente

#### Scenario: La operacion no borra fisicamente

- **WHEN** el endpoint de borrado logico concluye con exito
- **THEN** la fila del incidente sigue existiendo en la base de datos con `deleted_at` no nulo

#### Scenario: Acceso anonimo rechazado

- **WHEN** una solicitud sin autenticacion invoca el endpoint de borrado logico
- **THEN** el sistema responde HTTP 401
