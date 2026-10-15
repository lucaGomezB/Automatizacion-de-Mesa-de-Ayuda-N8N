## MODIFIED Requirements

### Requirement: DIR-003 — Modelo de roles canonico de tres valores

El sistema SHALL modelar el rol del empleado con un vocabulario minimo de EXACTAMENTE CUATRO valores: `usuario_final`, `mesa_de_ayuda`, `administrador_directorio` y `gestion_incidentes`. El rol `operador` NO SHALL existir. El rol SHALL gobernar la autorizacion sobre el directorio, el alcance de visibilidad de incidentes, las acciones de ciclo de cierre y la elegibilidad como destino de enrutamiento de notificaciones, y MUST NOT alterar el resultado de clasificacion del incidente.

- `usuario_final` es el reportante: alcance PROPIO (solo los incidentes que reporto), NO privilegiado y MUST NOT gestionar el directorio.
- `mesa_de_ayuda` es el rol transversal de mesa de ayuda: alcance GLOBAL (ve todos los incidentes), privilegiado, elegible como destinatario de la notificacion de revision y MUST NOT gestionar el directorio. Absorbe al antiguo `operador`.
- `administrador_directorio` tiene alcance GLOBAL, es privilegiado y MAY gestionar el directorio.
- `gestion_incidentes` es el rol operativo por sector: alcance `SECTOR` (solo los incidentes de su sector no cerrados para su sector), NO privilegiado, MUST NOT gestionar ni leer el directorio, cierra y edita el estado de los incidentes de su sector y es destinatario del aviso post-revision de los sectores del incidente.

El conocimiento de rol SHALL provenir de un unico registro de politica de rol, sin duplicarse entre el enum, el CHECK de la base y los servicios.

#### Scenario: Rol valido aceptado

- **WHEN** se registra un empleado con rol `usuario_final`, `mesa_de_ayuda`, `administrador_directorio` o `gestion_incidentes`
- **THEN** el sistema acepta el rol

#### Scenario: Rol invalido rechazado

- **WHEN** se intenta registrar un empleado con un rol fuera del vocabulario de cuatro valores
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Rol operador ya no existe

- **WHEN** se intenta registrar un empleado con rol `operador`
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Filas legacy con rol operador migradas

- **WHEN** se aplica la migracion sobre datos existentes con filas de rol `operador`
- **THEN** esas filas quedan con rol `mesa_de_ayuda` (backfill ANTES de crearse el CHECK de cuatro valores), de forma append-only

#### Scenario: El downgrade no re-marca filas

- **WHEN** se revierte la migracion que introdujo `gestion_incidentes`
- **THEN** las filas con rol `gestion_incidentes` se reasignan a `usuario_final` ANTES de restaurar el CHECK de tres valores, y las filas `operador` migradas NO se re-marcan

#### Scenario: El rol no afecta la clasificacion

- **WHEN** se clasifica un incidente
- **THEN** el sector y la confianza resultantes son independientes del rol del empleado reportante o vinculado

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores y sector opcional

El directorio SHALL referenciar el sector del empleado mediante una clave foranea nullable al catalogo `sector` existente, cuyo vocabulario canonico es exactamente los cinco strings vigentes. El directorio MUST NOT introducir un vocabulario paralelo de sectores ni reutilizar un conjunto reducido de tres sectores.

El `sector_id` SHALL ser OPCIONAL para `usuario_final`, `mesa_de_ayuda` y `administrador_directorio`. El rol `gestion_incidentes` SHALL requerir un sector: un empleado `gestion_incidentes` sin sector NO SHALL ver ningun incidente (alcance VACIO) y el sistema SHALL exigir el sector al operar la autorizacion por sector de ese rol. Para el resto de los roles el sector MUST NOT condicionar la autorizacion, la visibilidad ni la elegibilidad como destinatario de la notificacion de revision. El sistema MUST NOT aplicar una regla de coherencia entre rol y sector para roles distintos de `gestion_incidentes`.

#### Scenario: Sector tomado del catalogo existente

- **WHEN** se asigna sector a un empleado
- **THEN** el valor referenciado pertenece al catalogo `sector` canonico y no a una lista propia del directorio

#### Scenario: Sector opcional para cualquier rol

- **WHEN** se registra un empleado `usuario_final`, `mesa_de_ayuda` o `administrador_directorio`, con o sin sector
- **THEN** el sistema lo persiste; ninguno de esos roles exige un sector

#### Scenario: Gestion sin sector no ve incidentes

- **WHEN** un empleado `gestion_incidentes` no tiene sector asignado
- **THEN** su alcance de incidentes es VACIO y no ve ningun incidente

#### Scenario: El sector no cambia la autorizacion

- **WHEN** dos empleados con el mismo rol distinto de `gestion_incidentes` y distinto sector (o sin sector) operan el sistema
- **THEN** su alcance de incidentes y su autorizacion sobre el directorio son identicos

#### Scenario: Sector inexistente rechazado

- **WHEN** se intenta asignar un sector que no existe en el catalogo canonico
- **THEN** el sistema rechaza la asignacion
