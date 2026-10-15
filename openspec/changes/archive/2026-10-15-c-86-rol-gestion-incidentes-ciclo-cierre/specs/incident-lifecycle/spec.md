## Purpose

Define el ciclo de vida de cierre de un incidente: el cierre por sector a cargo de `gestion_incidentes`, el cierre global a cargo de `mesa_de_ayuda`, la transicion terminal a `cerrado` cuando todos los sectores cerraron, la reapertura (`rehabilitar`) y la edicion de estado, con atribucion verificable de actor y fecha.

## ADDED Requirements

### Requirement: ILC-001 — Cierre por sector

Un empleado con rol `gestion_incidentes` SHALL poder cerrar UNICAMENTE para SU propio sector un incidente visible de su sector, registrando una fila de cierre por sector (`incidente_cierre_sector`) con el sector, el `cerrado_por` (empleado que cierra) y el instante `cerrado_en`. El cierre SHALL ser idempotente para el mismo par (incidente, sector): un segundo cierre del mismo sector NO SHALL duplicar la fila. Tras el cierre de su sector, el incidente SHALL dejar de aparecer en la vista activa de ESE sector y SHALL aparecer de inmediato en el historial de ESE sector, con independencia de que otros sectores sigan abiertos. Un `gestion_incidentes` MUST NOT cerrar para un sector distinto del suyo ni sobre un incidente fuera de su alcance.

#### Scenario: Gestion cierra para su sector

- **WHEN** un `gestion_incidentes` del sector S cierra un incidente de su alcance cuyo conjunto de sectores incluye S
- **THEN** el sistema registra el cierre del sector S con actor y fecha, y el incidente sale de la vista activa de S

#### Scenario: El cierre por sector aparece de inmediato en el historial

- **WHEN** un `gestion_incidentes` del sector S cierra un incidente con otros sectores aun abiertos
- **THEN** el incidente aparece en el historial del sector S sin esperar el cierre de los demas sectores

#### Scenario: Cierre idempotente del mismo sector

- **WHEN** el mismo sector cierra dos veces el mismo incidente
- **THEN** el sistema conserva una unica fila de cierre para ese par y no duplica el registro

#### Scenario: Gestion no cierra fuera de su alcance

- **WHEN** un `gestion_incidentes` intenta cerrar para un sector distinto del suyo o un incidente fuera de su alcance
- **THEN** el sistema responde como no encontrado o no autorizado y NO registra ningun cierre

### Requirement: ILC-002 — Cierre global por mesa de ayuda

Un empleado con rol `mesa_de_ayuda` SHALL poder cerrar GLOBALMENTE cualquier incidente. El cierre global SHALL registrar el cierre de TODOS los sectores del conjunto del incidente (`{sector principal} U sectores adicionales`) con el actor y el instante en una sola operacion y SHALL llevar el incidente al estado `cerrado`. Un incidente sin sectores asignados (sin clasificar) SHALL poder cerrarse globalmente llevandolo a `cerrado` sin filas de sector.

#### Scenario: Mesa de ayuda cierra globalmente

- **WHEN** un `mesa_de_ayuda` cierra globalmente un incidente con N sectores
- **THEN** el sistema registra el cierre de los N sectores con el mismo actor y fecha, y el incidente queda en estado `cerrado`

#### Scenario: Cierre global de un incidente sin sector

- **WHEN** un `mesa_de_ayuda` cierra globalmente un incidente sin sectores asignados
- **THEN** el incidente queda en `cerrado` sin filas de cierre por sector

#### Scenario: Cierre global idempotente

- **WHEN** un `mesa_de_ayuda` cierra globalmente un incidente ya cerrado
- **THEN** el sistema no duplica cierres y responde de forma consistente

### Requirement: ILC-003 — Transicion terminal a cerrado

El sistema SHALL llevar el incidente al estado terminal `cerrado` UNICAMENTE cuando TODOS los sectores de su conjunto hayan cerrado, o por cierre global explicito de `mesa_de_ayuda`. Mientras exista al menos un sector del conjunto sin cerrar, el incidente NO SHALL considerarse globalmente cerrado. El estado `cerrado` MUST NOT fijarse directamente por la edicion de estado. Un incidente `cerrado` SHALL ser terminal: no vuelve a estados intermedios salvo por la reapertura (ILC-004).

#### Scenario: Todos los sectores cerrados transicionan a cerrado

- **WHEN** el ultimo sector pendiente de un incidente cierra su parte
- **THEN** el sistema lleva el incidente al estado terminal `cerrado`

#### Scenario: Cierre parcial no cierra globalmente

- **WHEN** un sector cierra su parte y otro sector del mismo incidente sigue abierto
- **THEN** el incidente NO queda en estado global `cerrado`

#### Scenario: Cerrado no se fija por edicion de estado

- **WHEN** un usuario con permiso de edicion intenta fijar directamente el estado `cerrado`
- **THEN** el sistema rechaza la operacion y el estado solo cambia por el modelo de cierre

### Requirement: ILC-004 — Rehabilitar (reapertura) por mesa de ayuda

Un empleado con rol `mesa_de_ayuda` SHALL poder rehabilitar (reabrir) un incidente cerrado. La reapertura SHALL limpiar los cierres por sector del incidente, SHALL devolver el incidente a un estado no terminal `en proceso` de forma deterministica y SHALL registrar el evento de reapertura con actor, estado anterior (`cerrado`) y estado nuevo (`en proceso`). Tras la reapertura, el incidente SHALL volver a ser visible segun las reglas normales de visibilidad (activo para sus sectores). La reapertura MUST NOT estar disponible para `gestion_incidentes`, `usuario_final` ni `administrador_directorio`.

#### Scenario: Mesa de ayuda reabre un incidente cerrado

- **WHEN** un `mesa_de_ayuda` rehabilita un incidente en estado `cerrado`
- **THEN** el sistema limpia sus cierres por sector, lo devuelve a `en proceso` y registra el evento con actor y fecha

#### Scenario: Reapertura registra el estado anterior y el nuevo

- **WHEN** se reabre un incidente cerrado
- **THEN** el evento de auditoria conserva el estado anterior `cerrado` y el estado nuevo `en proceso`

#### Scenario: Solo mesa de ayuda reabre

- **WHEN** un rol distinto de `mesa_de_ayuda` intenta reabrir un incidente
- **THEN** el sistema rechaza la operacion sin mutar el estado ni los cierres

#### Scenario: El incidente reabierto vuelve a ser visible

- **WHEN** un incidente reabierto pertenece al sector de un `gestion_incidentes`
- **THEN** el incidente vuelve a aparecer en la vista activa de ese sector

### Requirement: ILC-005 — Edicion de estado del incidente

Un empleado con rol `gestion_incidentes` o `mesa_de_ayuda` SHALL poder fijar el estado del incidente entre los valores no terminales `en proceso`, `en espera` y `resuelto`. `gestion_incidentes` SHALL poder editar el estado UNICAMENTE de los incidentes de su sector dentro de su alcance; `mesa_de_ayuda` SHALL poder editar el estado de cualquier incidente. El valor `cerrado` MUST NOT aceptarse en la edicion de estado. `usuario_final` y `administrador_directorio` MUST NOT poder editar el estado.

#### Scenario: Gestion edita el estado de su sector

- **WHEN** un `gestion_incidentes` fija `en espera` en un incidente de su sector
- **THEN** el sistema actualiza el estado y registra el cambio con actor y fecha

#### Scenario: Mesa de ayuda edita cualquier estado

- **WHEN** un `mesa_de_ayuda` fija `resuelto` en cualquier incidente
- **THEN** el sistema actualiza el estado y registra el cambio

#### Scenario: Valor cerrado rechazado en edicion

- **WHEN** la edicion de estado recibe `cerrado`
- **THEN** el sistema responde con un error de validacion y NO modifica el incidente

#### Scenario: Rol no editor rechazado

- **WHEN** un `usuario_final` o un `administrador_directorio` intenta editar el estado
- **THEN** el sistema rechaza la operacion sin mutar el incidente

### Requirement: ILC-006 — Atribucion de actor en el ciclo de vida

El sistema SHALL registrar de forma durable y auditable, para cada cierre por sector, cierre global, reapertura y cambio de estado, el ACTOR (empleado que ejecuta) y el INSTANTE de la operacion. El actor MUST NOT ser anonimo en operaciones iniciadas por una cuenta con empleado vinculado. La trazabilidad MUST NOT exponer datos personales (email o telefono) en claro.

#### Scenario: Cierre con actor y fecha

- **WHEN** un empleado cierra, reabre o cambia el estado de un incidente
- **THEN** el sistema persiste el id del empleado actor y el instante de la operacion

#### Scenario: Trazabilidad sin PII

- **WHEN** se registra un evento de ciclo de vida
- **THEN** la trazabilidad usa identificadores internos y no email, telefono ni otros datos personales en claro

### Requirement: ILC-007 — Limites de autorizacion del ciclo de cierre

El rol `gestion_incidentes` SHALL poder cerrar y editar el estado de los incidentes de su sector, y MUST NOT crear incidentes, borrar incidentes ni validar clasificaciones. La validacion de clasificaciones SHALL permanecer exclusiva de los roles que hoy la poseen. Una operacion de creacion, borrado o validacion intentada por `gestion_incidentes` SHALL ser rechazada sin mutar el sistema.

#### Scenario: Gestion no crea incidentes

- **WHEN** un `gestion_incidentes` intenta crear un incidente
- **THEN** el sistema responde con un error de autorizacion y NO crea el incidente

#### Scenario: Gestion no borra incidentes

- **WHEN** un `gestion_incidentes` intenta borrar un incidente
- **THEN** el sistema responde con un error de autorizacion y NO elimina el incidente

#### Scenario: Gestion no valida clasificaciones

- **WHEN** un `gestion_incidentes` intenta validar una clasificacion
- **THEN** el sistema responde con un error de autorizacion y NO registra la validacion
