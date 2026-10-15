## ADDED Requirements

### Requirement: VIS-006 — Conteo de la cola de revisión pendiente acotado por alcance

El sistema SHALL exponer un recurso de conteo de la cola de revisión pendiente que devuelva el TOTAL de clasificaciones pendientes dentro del alcance del usuario, coherente con el listado `GET /api/v1/clasificaciones/revision-pendiente`. El conteo SHALL reutilizar la misma derivación de alcance que VIS-002 (sin duplicar la lógica rol -> alcance) y SHALL aplicar exactamente la misma definición de "pendiente" (`requiere_revision_humana` verdadero y sin validación). `administrador_directorio` y `mesa_de_ayuda` SHALL contar la cola completa; un `usuario_final` SHALL contar únicamente los pendientes cuyo incidente reportó; una cuenta con alcance vacío SHALL contar cero. El conteo MUST NOT acotarse por sector y su resultado MUST coincidir con la cantidad de elementos del listado equivalente sin paginar.

#### Scenario: El conteo coincide con el listado completo

- **WHEN** un usuario consulta el conteo y el listado sin paginar de la cola de revisión pendiente
- **THEN** el conteo coincide exactamente con la cantidad de elementos del listado

#### Scenario: Conteo de la cola completa para alcance global

- **WHEN** un usuario con rol `administrador_directorio` o `mesa_de_ayuda` consulta el conteo
- **THEN** el sistema devuelve el total de pendientes de todos los sectores

#### Scenario: Conteo acotado al alcance propio

- **WHEN** un usuario con rol `usuario_final` vinculado al empleado E consulta el conteo
- **THEN** el sistema devuelve únicamente la cantidad de pendientes cuyo incidente reportó E

#### Scenario: Alcance vacío cuenta cero

- **WHEN** una cuenta autenticada sin empleado vinculado consulta el conteo
- **THEN** el sistema devuelve cero

#### Scenario: Acceso anónimo al conteo rechazado

- **WHEN** una solicitud sin autenticación consulta el conteo de la cola de revisión pendiente
- **THEN** el sistema responde HTTP 401
