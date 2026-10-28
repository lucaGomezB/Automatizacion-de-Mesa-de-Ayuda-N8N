## ADDED Requirements

### Requirement: Fidelidad del estado en los registros de gobernanza

Un registro de gobernanza del proyecto (al menos `docs/directorio-evidencia-cumplimiento.md` y las secciones de estado de los changes archivados) SHALL declarar el estado real de cada control y su conteo de tareas de forma verificable. Una aprobacion humana PENDIENTE del autor MUST quedar registrada como PENDIENTE y MUST NOT registrarse como concedida hasta que exista de forma verificable. Cuando el contenido de una tarea cerrada sea precisamente registrar que otra aprobacion queda pendiente, la tarea MAY figurar completada y la aprobacion pendiente SHALL permanecer visible como tal, sin que el cierre de la tarea se confunda con la aprobacion concedida.

#### Scenario: La aprobacion pendiente no se confunde con la tarea cerrada

- **WHEN** se revisa el registro de un control cuya aprobacion humana esta pendiente
- **THEN** el estado declara la aprobacion como PENDIENTE, esperando al autor
- **AND** no se presenta como concedida

#### Scenario: El conteo de tareas refleja el contenido de las tareas

- **WHEN** se revisa el registro de un change cuyo conteo se declara cerrado
- **THEN** una tarea marcada completada cuyo contenido era registrar una aprobacion pendiente no se lee como aprobacion otorgada
- **AND** el estado real de la aprobacion se declara a continuacion

#### Scenario: Dato de estado stale corregido sin reescribir la historia

- **WHEN** una afirmacion de estado actual quedo obsoleta por un cierre posterior
- **THEN** se corrige al estado real
- **AND** las entradas fechadas que documentan el hecho previo se conservan
