## Purpose

Define la visibilidad de incidentes por rol a nivel de API: que porciones del universo de incidentes puede leer/listar cada usuario autenticado segun el rol de su empleado en el directorio. La interfaz de usuario que refleje esta visibilidad queda fuera de este change (diferida).

## ADDED Requirements

### Requirement: VIS-001 — Visibilidad de incidentes por rol (API)

El sistema SHALL restringir la lectura y el listado de incidentes segun el rol del empleado asociado al usuario autenticado. Un usuario con rol `administrador_directorio` SHALL ver TODOS los incidentes, sin importar el sector. Un usuario con rol `usuario_final` o `operador` SHALL ver unicamente los incidentes de SU sector (`directorio_empleado.sector_id`). El filtrado SHALL aplicarse en la capa de API/servicio de incidentes, de modo que los endpoints de lectura/listado nunca devuelvan incidentes fuera del alcance del usuario. Si la cuenta autenticada no tiene un empleado vinculado en el directorio, su alcance SHALL ser vacio (no ve incidentes por esta via). Este change implementa solo el filtrado a nivel API; la representacion en el frontend se difiere a un change posterior.

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