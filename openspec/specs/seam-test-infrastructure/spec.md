# seam-test-infrastructure Specification

## Purpose
Define la infraestructura de pruebas que hace observables las costuras transversales del sistema: un único event loop compartido entre fixtures async y tests, fallo ruidoso ante prerrequisitos obligatorios ausentes, y enforcement de claves foráneas en el engine SQLite de tests.

## Requirements

### Requirement: Un único event loop para fixtures async y tests

La configuración de pytest SHALL declarar explícitamente el scope del event loop de los fixtures async (`asyncio_default_fixture_loop_scope`) en lugar de depender del default de pytest-asyncio, de modo que los fixtures async de scope session y los tests que los consumen compartan el mismo loop. El valor declarado SHALL ser compatible con `pytest-asyncio==0.24.0`. Ninguna conexión async (por ejemplo asyncpg) SHALL crearse en un loop distinto al que usan los tests.

#### Scenario: La configuración declara el loop scope explícitamente

- **WHEN** se inspecciona `App/Backend/pytest.ini`
- **THEN** declara `asyncio_default_fixture_loop_scope` con un valor explícito no vacío
- **AND** el valor es compatible con la versión pinneada de `pytest-asyncio`

#### Scenario: Fixtures de scope session y tests comparten loop

- **WHEN** se ejecuta un test async que consume un fixture async de scope session
- **THEN** el fixture y el test operan sobre el mismo event loop
- **AND** no se levanta `RuntimeError: ... got Future ... attached to a different loop`

### Requirement: Ningún prerrequisito obligatorio de suite se saltea en silencio

Cuando un prerrequisito declarado como obligatorio para una suite de tests está ausente, la suite SHALL fallar con un mensaje accionable y exit code distinto de cero, y NO SHALL marcar los tests como skipped. La salida SHALL nombrar el prerrequisito, su destino o ubicación, y la acción concreta de remediación.

#### Scenario: Prerrequisito ausente falla ruidosamente

- **WHEN** una suite requiere un prerrequisito obligatorio y este no está disponible
- **THEN** la ejecución falla con exit code distinto de cero
- **AND** ningún test de esa suite queda marcado como skipped
- **AND** el mensaje de error nombra el prerrequisito y una acción de remediación concreta

### Requirement: Claves foráneas habilitadas en el engine SQLite de tests

El engine SQLite in-memory usado por la suite de tests SHALL habilitar `PRAGMA foreign_keys=ON` en cada conexión, de modo que las violaciones de integridad referencial se manifiesten durante los tests en lugar de quedar ocultas. El enforcement SHALL aplicar tanto a las conexiones del engine compartido como a las que abre el cliente ASGI por request.

#### Scenario: Una violación de FK falla en lugar de pasar

- **WHEN** una operación de escritura referencia una clave foránea inexistente a través del engine SQLite de tests
- **THEN** la operación falla por violación de integridad referencial
- **AND** el test que la ejercita observa el fallo, no un éxito silencioso

#### Scenario: El PRAGMA está activo en todas las conexiones

- **WHEN** se consulta `PRAGMA foreign_keys` sobre cualquier conexión abierta por el engine SQLite de tests
- **THEN** el valor devuelto es `1` (habilitado)

### Requirement: Línea base de tests registrada como red de seguridad

Quien implementa el change SHALL registrar la línea base de conteos de tests de backend y frontend antes de modificar `conftest.py` o `pytest.ini`, y SHALL volver a registrar los conteos después de los cambios. La comparación SHALL ser explícita y SHALL demostrar que ningún test previamente en verde pasó a rojo por causa de la infraestructura modificada.

#### Scenario: La línea base se captura antes y después

- **WHEN** se inicia la modificación de la infraestructura de tests
- **THEN** se registra el conteo de passed/skipped de backend y de frontend previo
- **AND** se registra el conteo posterior a los cambios
- **AND** la comparación no muestra regresiones atribuibles a los cambios de infraestructura

#### Scenario: Un fallo nuevo se reporta como hallazgo, no como regresión

- **WHEN** un test que antes pasaba ahora falla por una costura recién expuesta
- **THEN** el fallo se reporta como hallazgo del change (RED intencional), no como regresión silenciada
- **AND** ningún test se desmarca, se saltea ni se debilita para forzar el verde
