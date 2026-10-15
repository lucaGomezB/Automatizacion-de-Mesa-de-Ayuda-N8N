## MODIFIED Requirements

### Requirement: VIS-001 — Alcance de visibilidad de incidentes y clasificaciones (PROPIO/GLOBAL)

El sistema SHALL restringir la lectura y el listado de incidentes segun el rol del empleado asociado al usuario autenticado, con exactamente tres alcances mas el vacio:

- Un usuario con rol `administrador_directorio` SHALL ver TODOS los incidentes.
- Un usuario con rol `mesa_de_ayuda` SHALL ver TODOS los incidentes (rol transversal que absorbe al antiguo `operador`).
- Un usuario con rol `usuario_final` SHALL ver UNICAMENTE los incidentes cuyo reportante vinculado sea su propio empleado (alcance PROPIO).
- Un usuario con rol `gestion_incidentes` SHALL ver UNICAMENTE los incidentes cuyo CONJUNTO de sectores incluya su propio sector y que NO esten cerrados para su sector (alcance SECTOR, ver VIS-007).
- Una cuenta autenticada sin empleado vinculado, o un `gestion_incidentes` sin sector asignado, SHALL tener alcance vacio.

Para los alcances PROPIO y GLOBAL el sector NO es frontera de acceso: el sistema MUST NOT acotar su visibilidad por `sector_id` ni por el sector del empleado. El alcance SECTOR es la excepcion: para `gestion_incidentes` el sector SI acota la visibilidad, de forma server-side. La misma regla SHALL aplicarse a los endpoints de clasificaciones atados a un incidente, reutilizando el servicio de visibilidad sin duplicar la logica:
- `GET /api/v1/clasificaciones/incidente/{incidente_id}` SHALL devolver el historial solo si el incidente esta dentro del alcance.
- `PATCH /api/v1/clasificaciones/{log_id}/validar` SHALL validar el alcance ANTES de cualquier mutacion.

Un incidente fuera del alcance SHALL comportarse como NO ENCONTRADO (HTTP 404), sin revelar su existencia ni su contenido, y el `PATCH` NO SHALL mutar nada. El acceso anonimo permanece 401.

#### Scenario: Administrador ve todos los incidentes

- **WHEN** un usuario con rol `administrador_directorio` lista incidentes
- **THEN** el sistema devuelve incidentes de todos los sectores y reportantes

#### Scenario: Mesa de ayuda ve todos los incidentes

- **WHEN** un usuario con rol `mesa_de_ayuda` lista incidentes
- **THEN** el sistema devuelve incidentes de todos los sectores y reportantes

#### Scenario: Usuario final ve solo los incidentes que reporto

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E lista incidentes
- **THEN** el sistema devuelve unicamente los incidentes cuyo reportante vinculado es E

#### Scenario: Usuario final no ve incidentes de otros

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E solicita un incidente cuyo reportante es otro empleado
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Gestion ve solo los incidentes de su sector

- **WHEN** un usuario con rol `gestion_incidentes` del sector S lista incidentes
- **THEN** el sistema devuelve unicamente los incidentes cuyo conjunto de sectores incluye S y que no estan cerrados para S

#### Scenario: Gestion no ve incidentes de otro sector

- **WHEN** un usuario con rol `gestion_incidentes` del sector S solicita un incidente cuyo conjunto de sectores no incluye S
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Gestion sin sector no ve incidentes

- **WHEN** un usuario con rol `gestion_incidentes` sin sector asignado lista incidentes
- **THEN** el alcance de incidentes visibles es vacio

#### Scenario: Cuenta sin empleado no ve incidentes

- **WHEN** una cuenta autenticada no tiene empleado vinculado
- **THEN** el alcance de incidentes visibles es vacio

#### Scenario: La cuenta admin sembrada ve todos los incidentes

- **WHEN** la cuenta `admin` sembrada por la migracion lista incidentes (esta vinculada a un empleado `administrador_directorio` sintetico)
- **THEN** el sistema los devuelve todos: su alcance efectivo es GLOBAL, no vacio

#### Scenario: El sector no acota la visibilidad

- **WHEN** un usuario con rol `mesa_de_ayuda` o `administrador_directorio` lista incidentes de cualquier sector
- **THEN** el sistema los devuelve; ningun filtro por sector reduce el alcance del rol

#### Scenario: Alcance aplicado en el acceso puntual

- **WHEN** un usuario solicita un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado, sin revelar su existencia ni su contenido

#### Scenario: Administrador lee clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` consulta el historial de clasificaciones de un incidente de cualquier sector
- **THEN** el sistema devuelve el historial completo (HTTP 200)

#### Scenario: Mesa de ayuda lee clasificaciones de un incidente en revision

- **WHEN** un usuario con rol `mesa_de_ayuda` consulta el historial de clasificaciones de un incidente
- **THEN** el sistema devuelve el historial (HTTP 200)

#### Scenario: No administrador lee clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` consulta el historial de clasificaciones de un incidente que reporto
- **THEN** el sistema devuelve el historial (HTTP 200)

#### Scenario: Lectura de clasificaciones fuera de alcance es no encontrada

- **WHEN** un usuario consulta el historial de clasificaciones de un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404), sin revelar su existencia ni su historial

#### Scenario: Administrador valida clasificaciones de cualquier sector

- **WHEN** un usuario con rol `administrador_directorio` valida una clasificacion de un incidente de cualquier sector
- **THEN** el sistema registra la validacion (HTTP 200)

#### Scenario: No administrador valida clasificaciones de su sector

- **WHEN** un usuario con rol `usuario_final` valida una clasificacion de un incidente que reporto
- **THEN** el sistema registra la validacion y propaga el veredicto al incidente (HTTP 200)

#### Scenario: Validacion fuera de alcance es no encontrada y no muta

- **WHEN** un usuario valida una clasificacion cuyo incidente esta fuera de su alcance
- **THEN** el sistema responde como no encontrado (HTTP 404) y NO modifica el registro de clasificacion ni el incidente

#### Scenario: Acceso anonimo a clasificaciones es no autorizado

- **WHEN** una solicitud sin autenticacion llega a los endpoints de clasificaciones por incidente o de validacion
- **THEN** el sistema responde HTTP 401

## ADDED Requirements

### Requirement: VIS-007 — Filtrado server-side del alcance SECTOR

El sistema SHALL acotar en el servidor el conjunto de incidentes visibles para un `gestion_incidentes` a los incidentes cuyo CONJUNTO de sectores (`{sector principal} U sectores adicionales`) incluye su propio sector y que NO estan cerrados para su sector. El filtro SHALL aplicarse tanto al listado como a la verificacion puntual de acceso y MUST NOT delegarse al cliente. Un incidente SHALL dejar de estar activo para un sector cuando existe un cierre por sector para ese par (incidente, sector) o cuando el incidente esta globalmente en estado `cerrado`.

#### Scenario: Pertenece por sector principal

- **WHEN** un `gestion_incidentes` del sector S lista incidentes y un incidente tiene S como sector principal
- **THEN** el incidente es visible para S si no esta cerrado para S

#### Scenario: Pertenece por sector adicional

- **WHEN** un `gestion_incidentes` del sector S lista incidentes y un incidente tiene S solo entre sus sectores adicionales
- **THEN** el incidente es visible para S si no esta cerrado para S

#### Scenario: El cierre por sector lo retira de la vista activa

- **WHEN** existe un cierre por sector para el par (incidente, S)
- **THEN** el incidente deja de estar activo para S, con independencia de otros sectores

#### Scenario: El cierre global lo retira de la vista activa

- **WHEN** el incidente esta en estado `cerrado`
- **THEN** no aparece en la vista activa de ningun sector

#### Scenario: El filtro no es delegable al cliente

- **WHEN** se inspecciona el comportamiento del listado para `gestion_incidentes`
- **THEN** el conjunto devuelto ya viene acotado por el servidor y la UI no puede ampliarlo

### Requirement: VIS-008 — Visibilidad del historial de incidentes cerrados

El sistema SHALL exponer el historial de incidentes cerrados acotado por el alcance del usuario. Los roles de alcance GLOBAL (`mesa_de_ayuda`, `administrador_directorio`) SHALL ver los incidentes GLOBALMENTE cerrados (estado `cerrado`); un `gestion_incidentes` SHALL ver los incidentes con un cierre por sector para SU sector, incluidos los cerrados solo por su sector y aun no globalmente cerrados; un `usuario_final` SHALL ver UNICAMENTE sus propios incidentes cerrados (alcance PROPIO). El historial MUST NOT incluir incidentes eliminados. Un incidente cerrado solo por un sector NO SHALL ser considerado cerrado globalmente y SHALL aparecer en el historial de ese sector de inmediato.

#### Scenario: Historial global

- **WHEN** un `mesa_de_ayuda` o `administrador_directorio` consulta el historial
- **THEN** el sistema devuelve los incidentes en estado global `cerrado`

#### Scenario: Historial por sector inmediato

- **WHEN** un sector cierra su parte de un incidente aun no globalmente cerrado
- **THEN** el incidente aparece en el historial de ese sector

#### Scenario: Historial propio

- **WHEN** un `usuario_final` consulta el historial
- **THEN** el sistema devuelve unicamente sus propios incidentes cerrados

#### Scenario: El historial excluye incidentes eliminados

- **WHEN** un incidente fue eliminado
- **THEN** el sistema no lo incluye en el historial de ningun rol

#### Scenario: Acceso anonimo al historial rechazado

- **WHEN** una solicitud sin autenticacion consulta el historial de incidentes cerrados
- **THEN** el sistema responde HTTP 401
