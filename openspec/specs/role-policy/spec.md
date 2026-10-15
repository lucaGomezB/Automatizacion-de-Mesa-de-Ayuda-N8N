# role-policy Specification

## Purpose

Define el registro canonico y unico que mapea cada rol del directorio a su politica de autorizacion, visibilidad, privilegio y enrutamiento, de modo que el enum, el CHECK de la base y todos los servicios deriven de una sola fuente de verdad y no dupliquen el conocimiento de rol.

## Requirements

### Requirement: RP-001 — Registro canonico de roles y politica

El sistema SHALL mantener un unico registro de politica que defina EXACTAMENTE los cuatro roles del vocabulario (`usuario_final`, `mesa_de_ayuda`, `administrador_directorio`, `gestion_incidentes`) y, para cada uno, al menos: `requires_sector`, el modo de visibilidad de incidentes (`PROPIO`, `GLOBAL` o `SECTOR`), `privileged`, `manages_directory`, `can_read_directory`, `notification_recipient` (destinatario de la notificacion de revision) y `post_review_recipient` (destinatario del aviso post-revision). El registro SHALL ser la unica definicion de esos atributos por rol. Los modos de visibilidad validos SHALL ser exactamente `PROPIO`, `GLOBAL` y `SECTOR`; el antiguo modo de revision por sector NO SHALL reexistir bajo otro nombre.

- `usuario_final`: `requires_sector` falso, visibilidad PROPIO.
- `mesa_de_ayuda`: `requires_sector` falso, visibilidad GLOBAL, privilegiado, lee el directorio, destinatario de la notificacion de revision.
- `administrador_directorio`: `requires_sector` falso, visibilidad GLOBAL, privilegiado, lee y gestiona el directorio.
- `gestion_incidentes`: `requires_sector` verdadero, visibilidad SECTOR, NO privilegiado, NO lee ni gestiona el directorio, y destinatario del aviso post-revision.

#### Scenario: Todos los roles tienen politica

- **WHEN** se inspecciona el registro de politica de rol
- **THEN** contiene exactamente los cuatro roles y cada uno declara visibilidad, privilegio, gestion de directorio, elegibilidad de la notificacion de revision y elegibilidad del aviso post-revision

#### Scenario: Sectores no requeridos

- **WHEN** se consulta `requires_sector` de cada rol
- **THEN** es falso para `usuario_final`, `mesa_de_ayuda` y `administrador_directorio`

#### Scenario: Sector requerido por gestion_incidentes

- **WHEN** se consulta `requires_sector` del rol `gestion_incidentes`
- **THEN** es verdadero

#### Scenario: Modos de visibilidad acotados

- **WHEN** se consulta el modo de visibilidad de cada rol
- **THEN** `usuario_final` es PROPIO, `mesa_de_ayuda` y `administrador_directorio` son GLOBAL, y `gestion_incidentes` es SECTOR

#### Scenario: Atributos por rol

- **WHEN** se consultan privilegio y gestion de directorio
- **THEN** `usuario_final` no es privilegiado, no gestiona el directorio ni puede leerlo; `mesa_de_ayuda` es privilegiado, puede leer el directorio, no lo gestiona y es destinatario de la notificacion de revision; `administrador_directorio` es privilegiado, puede leer el directorio y lo gestiona; `gestion_incidentes` no es privilegiado, no lee ni gestiona el directorio y es destinatario del aviso post-revision

### Requirement: RP-002 — Fuente unica de verdad del conocimiento de rol

El sistema SHALL derivar del registro de politica las decisiones de autorizacion y visibilidad: el vocabulario del enum de roles, el catalogo de roles privilegiados, la derivacion rol -> alcance de `incident_visibility`, los guards de rol de las rutas, el criterio de destinatarios de la notificacion de revision y el criterio de destinatarios del aviso post-revision. Ningun modulo SHALL repetir el mapeo rol -> atributo con listas o cadenas de rol duplicadas. El CHECK del rol en la base SHALL seguir enumerando los valores del vocabulario (la base no puede leer el registro) y SHALL ser coherente con el enum.

#### Scenario: Servicios sin duplicacion

- **WHEN** se inspeccionan el servicio de privilegio, el servicio de visibilidad, los guards de rutas y la resolucion de destinatarios
- **THEN** ninguno contiene una lista propia de roles; todos consultan el registro de politica

#### Scenario: El CHECK coincide con el enum

- **WHEN** se compara el vocabulario del CHECK de la base con el enum de roles
- **THEN** ambos contienen exactamente los mismos cuatro valores

### Requirement: RP-003 — Coherencia verificable del vocabulario

El sistema SHALL exponer una verificacion automatizada que falle si el vocabulario del CHECK de la base, el enum de roles y el registro de politica divergen, o si aparece un rol fuera de los cuatro canonicos. La verificacion SHALL tambien fallar si `requires_sector` del registro no coincide con el comportamiento de visibilidad esperado para `gestion_incidentes` (sector requerido) o si el conjunto de roles con visibilidad `SECTOR` no coincide con el registro.

#### Scenario: Divergencia detectada

- **WHEN** el CHECK de la base admite un valor que el registro de politica no define (o viceversa)
- **THEN** la verificacion falla

#### Scenario: Vocabulario coherente

- **WHEN** el CHECK, el enum y el registro definen los mismos cuatro roles
- **THEN** la verificacion pasa

#### Scenario: requires_sector coherente con la visibilidad

- **WHEN** el registro declara un rol con visibilidad SECTOR
- **THEN** la verificacion exige que ese rol tenga `requires_sector` verdadero y falla si no

### Requirement: RP-004 — Conjunto de lectura del directorio

El sistema SHALL derivar de la politica de rol el permiso de LECTURA del directorio mediante `can_read_directory`. Los roles `mesa_de_ayuda` y `administrador_directorio` MAY consultar el directorio; el rol `usuario_final` y toda cuenta sin empleado vinculado NO SHALL consultarlo. El guard de lectura de las rutas del directorio SHALL ser una LISTA BLANCA derivada de `can_read_directory` (no una lista negra ni una enumeracion de roles prohibidos), de modo que ningun rol quede habilitado por omision. La gestion del directorio (`manages_directory`) SHALL seguir siendo exclusiva de `administrador_directorio`. Los accesos SHALL auditarse y NO SHALL exponer email ni telefono en claro (DIR-006).

#### Scenario: Mesa de ayuda lee el directorio

- **WHEN** un usuario con rol `mesa_de_ayuda` consulta el directorio
- **THEN** el sistema permite la consulta (HTTP 200)

#### Scenario: Administrador lee el directorio

- **WHEN** un usuario con rol `administrador_directorio` consulta el directorio
- **THEN** el sistema permite la consulta (HTTP 200)

#### Scenario: Usuario final no lee el directorio

- **WHEN** un usuario con rol `usuario_final` consulta el directorio
- **THEN** el sistema responde con un error de autorizacion (HTTP 403)

#### Scenario: Cuenta sin empleado no lee el directorio

- **WHEN** una cuenta autenticada sin empleado vinculado consulta el directorio
- **THEN** el sistema responde con un error de autorizacion (HTTP 403)

#### Scenario: El guard de lectura es una lista blanca

- **WHEN** se inspecciona el guard de lectura del directorio
- **THEN** deriva de `can_read_directory` del registro de politica y no de una lista de roles prohibidos

### Requirement: RP-005 — Permiso de borrado logico de incidentes en el registro de politica

El registro canonico de politica de rol SHALL declarar un atributo `can_delete_incident` por rol, del que SHALL derivarse el guard del endpoint de borrado logico de incidentes (SD-002) sin listas de rol duplicadas en la ruta ni en el servicio. Unicamente el rol `administrador_directorio` SHALL declarar `can_delete_incident` verdadero; `usuario_final` y `mesa_de_ayuda` SHALL declararlo falso. El atributo SHALL convivir con los atributos ya definidos en el registro de politica (ver RP-001) y SHALL ser el unico origen de la decision de autorizacion de borrado logico.

#### Scenario: El administrador puede borrar incidentes

- **WHEN** se consulta `can_delete_incident` del rol `administrador_directorio`
- **THEN** es verdadero

#### Scenario: Los demas roles no pueden borrar incidentes

- **WHEN** se consulta `can_delete_incident` de los roles `usuario_final` y `mesa_de_ayuda`
- **THEN** ambos son falsos

#### Scenario: El guard deriva del registro de politica

- **WHEN** se inspecciona el guard del endpoint de borrado logico de incidentes
- **THEN** deriva de `can_delete_incident` del registro de politica y no de una lista de roles propia
