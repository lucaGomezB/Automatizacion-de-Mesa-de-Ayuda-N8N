## ADDED Requirements

### Requirement: IAH-012 — Endpoint aditivo de identidad y alcance actual

El sistema SHALL exponer un endpoint autenticado y de SOLO LECTURA que devuelva la identidad efectiva de la sesion y su alcance de incidentes derivado. El endpoint SHALL recomputar el alcance por request a partir del directorio (empleado vinculado a la cuenta), reutilizando la derivacion rol -> alcance existente (VIS-001 y `role-policy`) sin duplicarla. La respuesta SHALL incluir al menos el nombre de usuario, el rol del empleado (o nulo si no hay empleado activo vinculado) y el modo de alcance con EXACTAMENTE los valores `PROPIO`, `GLOBAL` o `VACIO`. El endpoint MUST NOT exponer sector, `ver_todos` ni conceptos del modelo RBAC anterior (los modos SECTOR y REVISION NO existen). El endpoint SHALL ser ADITIVO: no modifica el contrato ni el comportamiento de los endpoints de login, refresh y logout existentes. Una solicitud sin autenticacion SHALL responder HTTP 401 con el envelope de error estandar, sin revelar datos de identidad.

#### Scenario: Usuario autenticado obtiene su identidad y alcance

- **WHEN** un usuario autenticado con empleado activo vinculado consulta el endpoint
- **THEN** el sistema devuelve su rol y el modo de alcance derivado (`PROPIO`, `GLOBAL` o `VACIO`)

#### Scenario: Cuenta sin empleado activo obtiene alcance vacio

- **WHEN** un usuario autenticado sin empleado activo vinculado consulta el endpoint
- **THEN** el sistema devuelve rol nulo y modo de alcance `VACIO`

#### Scenario: El alcance se recomputa desde el directorio

- **WHEN** el rol del empleado vinculado cambia en el directorio
- **THEN** la siguiente consulta del endpoint devuelve el modo de alcance actualizado, sin requerir re-login

#### Scenario: La respuesta no expone el modelo RBAC anterior

- **WHEN** se inspecciona la respuesta del endpoint
- **THEN** el alcance contiene unicamente el modo (`PROPIO`, `GLOBAL` o `VACIO`) y no incluye sector, `ver_todos` ni `revision`

#### Scenario: Acceso anonimo es no autorizado

- **WHEN** una solicitud sin autenticacion llega al endpoint
- **THEN** el sistema responde HTTP 401 con el envelope de error estandar y sin datos de identidad

#### Scenario: El contrato de login permanece aditivo y sin cambios

- **WHEN** un cliente existente consume login, refresh o logout
- **THEN** el contrato y el comportamiento de esos endpoints no cambian respecto de lo previo
