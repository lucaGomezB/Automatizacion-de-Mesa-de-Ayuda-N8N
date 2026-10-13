## REMOVED Requirements

### Requirement: DIR-003 — Modelo de roles minimo

**Reason**: El vocabulario cambia de cuatro a tres roles (`operador` se elimina y `mesa_de_ayuda` pasa a ser un rol de primera clase que absorbe al operador). El texto actual ademas tiene un drift: enumera tres valores omitiendo `mesa_de_ayuda`.

**Migration**: Reemplazada por "DIR-003 — Modelo de roles canonico de tres valores" en este mismo delta.

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores y sector por rol

**Reason**: El sector deja de ser obligatorio para ningun rol y se elimina la coherencia rol/sector; pasa a ser dato organizacional opcional sin efecto en la autorizacion.

**Migration**: Reemplazada por "DIR-004 — Vinculo al catalogo canonico de sectores y sector opcional" en este mismo delta.

## ADDED Requirements

### Requirement: DIR-003 — Modelo de roles canonico de tres valores

El sistema SHALL modelar el rol del empleado con un vocabulario minimo de EXACTAMENTE TRES valores: `usuario_final`, `mesa_de_ayuda` y `administrador_directorio`. El rol `operador` NO SHALL existir. El rol SHALL gobernar la autorizacion sobre el directorio, el alcance de visibilidad de incidentes y la elegibilidad como destino de enrutamiento de notificaciones, y MUST NOT alterar el resultado de clasificacion del incidente.

- `usuario_final` es el reportante: alcance PROPIO (solo los incidentes que reporto), NO privilegiado y MUST NOT gestionar el directorio.
- `mesa_de_ayuda` es el rol transversal de mesa de ayuda: alcance GLOBAL (ve todos los incidentes), privilegiado, elegible como destinatario de la notificacion de revision y MUST NOT gestionar el directorio. Absorbe al antiguo `operador`.
- `administrador_directorio` tiene alcance GLOBAL, es privilegiado y MAY gestionar el directorio.

El conocimiento de rol SHALL provenir de un unico registro de politica de rol, sin duplicarse entre el enum, el CHECK de la base y los servicios.

#### Scenario: Rol valido aceptado

- **WHEN** se registra un empleado con rol `usuario_final`, `mesa_de_ayuda` o `administrador_directorio`
- **THEN** el sistema acepta el rol

#### Scenario: Rol invalido rechazado

- **WHEN** se intenta registrar un empleado con un rol fuera del vocabulario de tres valores
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Rol operador ya no existe

- **WHEN** se intenta registrar un empleado con rol `operador`
- **THEN** el sistema rechaza el registro con un error de validacion

#### Scenario: Filas legacy con rol operador migradas

- **WHEN** se aplica la migracion sobre datos existentes con filas de rol `operador`
- **THEN** esas filas quedan con rol `mesa_de_ayuda` (backfill ANTES de crearse el CHECK de tres valores), de forma append-only

#### Scenario: El downgrade no re-marca filas

- **WHEN** se revierte la migracion
- **THEN** el vocabulario restaura los cuatro valores, pero las filas migradas NO se re-marcan como `operador`

#### Scenario: El rol no afecta la clasificacion

- **WHEN** se clasifica un incidente
- **THEN** el sector y la confianza resultantes son independientes del rol del empleado reportante o vinculado

### Requirement: DIR-004 — Vinculo al catalogo canonico de sectores y sector opcional

El directorio SHALL referenciar el sector del empleado mediante una clave foranea nullable al catalogo `sector` existente, cuyo vocabulario canonico es exactamente los cinco strings vigentes. El directorio MUST NOT introducir un vocabulario paralelo de sectores ni reutilizar un conjunto reducido de tres sectores.

El `sector_id` SHALL ser OPCIONAL para TODOS los roles y MUST NOT condicionar la autorizacion, la visibilidad ni la elegibilidad como destinatario de notificacion. Ningun rol SHALL requerir sector. El sistema MUST NOT aplicar una regla de coherencia entre rol y sector (por ejemplo, exigir sector a un rol o prohibirlo a otro). El sector queda como dato organizacional de RR.HH., sin efecto en el control de acceso.

#### Scenario: Sector tomado del catalogo existente

- **WHEN** se asigna sector a un empleado
- **THEN** el valor referenciado pertenece al catalogo `sector` canonico y no a una lista propia del directorio

#### Scenario: Sector opcional para cualquier rol

- **WHEN** se registra un empleado de cualquier rol, con o sin sector
- **THEN** el sistema lo persiste; ningun rol exige un sector

#### Scenario: El sector no cambia la autorizacion

- **WHEN** dos empleados con el mismo rol y distinto sector (o sin sector) operan el sistema
- **THEN** su alcance de incidentes y su autorizacion sobre el directorio son identicos

#### Scenario: Sector inexistente rechazado

- **WHEN** se intenta asignar un sector que no existe en el catalogo canonico
- **THEN** el sistema rechaza la asignacion
