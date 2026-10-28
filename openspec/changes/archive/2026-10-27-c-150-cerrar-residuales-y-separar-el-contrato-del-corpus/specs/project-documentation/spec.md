## ADDED Requirements

### Requirement: Registro documental libre de emojis

Los artefactos documentales del proyecto (al menos `CHANGES.md`, `docs/Tesis/Correcciones/dictamen-correcciones.md` y `docs/directorio-evidencia-cumplimiento.md`) SHALL NOT contener emojis ni pictogramas, conforme a la regla dura del proyecto. En particular, `CHANGES.md` MUST NOT contener la marca de verificacion U+2713 (CHECK MARK) ni ninguna otra variante de marca de verificacion. La finalidad de completitud o de estado SHALL expresarse con texto explicito (por ejemplo `COMPLETADO` o `(completado)`) o con la casilla markdown `[x]`, nunca con un pictograma.

#### Scenario: Sin marcas de verificacion en el registro

- **WHEN** se busca en `CHANGES.md` el caracter U+2713 (o cualquier pictograma de estado)
- **THEN** no aparece ninguna coincidencia

#### Scenario: El estado se expresa con texto

- **WHEN** se lee un encabezado de gate o de fase de `CHANGES.md` que antes llevaba una marca de verificacion
- **THEN** su estado se declara con texto explicito
- **AND** el sentido de la linea no cambia

### Requirement: Anotacion fechada de los registros historicos sin reescritura

Un registro historico del proyecto (entradas fechadas de `CHANGES.md`, tareas de un change archivado bajo `openspec/changes/archive/`) MUST NOT reescribirse en su texto original. Cuando un hecho posterior vuelva obsoleta una afirmacion de ese registro, la correccion SHALL agregarse como una ANOTACION FECHADA junto al texto original, conservandolo integro como evidencia. La anotacion MUST declarar la fecha, el hecho que la motiva y la fuente verificable (por ejemplo el commit y el merge), y MUST explicitar que el texto original se conserva como historia.

#### Scenario: Nota de estado stale corregida sin falsificar la historia

- **WHEN** una afirmacion de estado actual de `CHANGES.md` quedo desmentida por un cierre posterior ya registrado
- **THEN** la afirmacion se corrige al estado real
- **AND** las entradas fechadas que documentan los hechos previos se conservan sin reescribirse

#### Scenario: Tarea de rollback obsoleta anotada y no borrada

- **WHEN** una tarea no ejecutada de un change archivado justifica su omision con un hecho que despues dejo de ser cierto (el change fue commiteado y fusionado)
- **THEN** la tarea conserva su texto original
- **AND** recibe una anotacion fechada que cita el commit y el merge, declara la justificacion obsoleta y el rollback moot
