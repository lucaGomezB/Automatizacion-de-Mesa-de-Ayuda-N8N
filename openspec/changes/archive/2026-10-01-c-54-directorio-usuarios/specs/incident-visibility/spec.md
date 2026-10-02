## Purpose

Define la visibilidad de incidentes por rol a nivel de API: que porciones del universo de incidentes puede leer/listar cada usuario autenticado segun el rol de su empleado en el directorio. La interfaz de usuario que refleje esta visibilidad queda fuera de este change (diferida).

## ADDED Requirements

### Requirement: VIS-001 — Visibilidad de incidentes y clasificaciones por rol (API)

El sistema SHALL restringir la lectura y el listado de incidentes segun el rol del empleado asociado al usuario autenticado. Un usuario con rol `administrador_directorio` SHALL ver TODOS los incidentes, sin importar el sector. Un usuario con rol `usuario_final` o `operador` SHALL ver unicamente los incidentes de SU sector (`directorio_empleado.sector_id`). El filtrado SHALL aplicarse en la capa de API/servicio de incidentes, de modo que los endpoints de lectura/listado nunca devuelvan incidentes fuera del alcance del usuario. Si la cuenta autenticada no tiene un empleado vinculado en el directorio, su alcance SHALL ser vacio (no ve incidentes por esta via). Este change implementa solo el filtrado a nivel API; la representacion en el frontend se difiere a un change posterior.

La MISMA regla de alcance SHALL aplicarse a los endpoints de clasificaciones atados a un incidente, reutilizando el servicio de visibilidad (`AlcanceIncidentes`) sin duplicar la logica:
- `GET /api/v1/clasificaciones/incidente/{incidente_id}` SHALL devolver el historial solo si el incidente esta dentro del alcance del usuario.
- `PATCH /api/v1/clasificaciones/{log_id}/validar` SHALL validar el alcance del incidente del log ANTES de cualquier mutacion.

En ambos casos, un incidente fuera del alcance SHALL comportarse como NO ENCONTRADO (HTTP 404), sin revelar la existencia ni el contenido, y el `PATCH` NO SHALL modificar el registro de clasificacion ni el incidente. Una cuenta sin empleado/sector mantiene alcance vacio; el acceso anonimo permanece 401.

#### Scenario: Administrador ve todos los incidentes

- **WHEN** un usuario con rol `administrador_directorio` lista incidentes
- **THEN** el sistema devuelve incidentes de todos los sectores

#### Scenario: No administrador ve solo su sector

- **WHEN** un usuario con rol `usuario_final` u `operador` con sector S lista incidentes
- **THEN** el sistema devuelve unicamente incidentes del sector S

#### Scenario: Sin sector no ve incidentes

- **WHEN** una cuenta autenticada no tiene empleado vinculado con sector asignado
- **THEN** el alcance de incidentes visibles es vacio

#### Scenario: Alcance aplicado en el acceso puntual

- **WHEN** un usuario no administrador solicita un incidente fuera de su sector
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Administrador lee clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` consulta el historial de clasificaciones de un incidente de cualquier sector
- **THEN** el sistema devuelve el historial completo (HTTP 200)

#### Scenario: No administrador lee clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` u `operador` con sector S consulta el historial de clasificaciones de un incidente del sector S
- **THEN** el sistema devuelve el historial (HTTP 200)

#### Scenario: Lectura de clasificaciones fuera de alcance es no encontrada

- **WHEN** un usuario no administrador (o una cuenta con alcance vacio) consulta el historial de clasificaciones de un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404), sin revelar su existencia ni su historial

#### Scenario: Administrador valida clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` valida una clasificacion de un incidente de cualquier sector
- **THEN** el sistema registra la validacion (HTTP 200)

#### Scenario: No administrador valida clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` u `operador` con sector S valida una clasificacion de un incidente del sector S
- **THEN** el sistema registra la validacion y propaga el veredicto al incidente (HTTP 200)

#### Scenario: Validacion fuera de alcance es no encontrada y no muta

- **WHEN** un usuario no administrador (o una cuenta con alcance vacio) valida una clasificacion cuyo incidente esta fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404) y NO modifica el registro de clasificacion ni el incidente

#### Scenario: Acceso anonimo a clasificaciones es no autorizado

- **WHEN** una solicitud sin autenticacion llega a los endpoints de clasificaciones por incidente o de validacion
- **THEN** el sistema responde HTTP 401, sin cambios respecto del comportamiento previo