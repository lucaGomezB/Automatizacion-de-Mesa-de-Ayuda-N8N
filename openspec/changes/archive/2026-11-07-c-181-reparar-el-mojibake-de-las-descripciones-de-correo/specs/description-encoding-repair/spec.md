# description-encoding-repair Specification

## Purpose

Repara de forma idempotente y verificable las descripciones de incidentes de correo electronico
corrompidas por el mojibake introducido en el canal de ingesta (doble codificacion del charset),
restaurando el texto pseudonimizado operativo y el texto cifrado de auditoria, con deteccion
selectiva, modo dry-run por defecto y un runbook que documenta la causa, el procedimiento y la
evidencia.

## ADDED Requirements

### Requirement: Deteccion selectiva de descripciones corruptas por mojibake

El sistema SHALL exponer una funcion PURA de deteccion que determine si un texto esta corrupto por el
mojibake de doble codificacion. La deteccion SHALL considerarse positiva UNICAMENTE cuando se cumplen
las tres condiciones: (a) el texto presenta la firma del mojibake, (b) el reverso
`value.encode('latin-1').decode('utf-8')` tiene exito y (c) el texto revertido es estrictamente
distinto del original. La funcion SHALL ser deterministica y SHALL NOT tener efectos secundarios. Un
texto limpio SHALL evaluarse como no corrupto, y un texto que no sea codificable en `latin-1` o cuyo
reverso no sea `utf-8` valido SHALL evaluarse como no corrupto sin lanzar excepcion.

#### Scenario: Texto corrupto con acentos es detectado

- **WHEN** se evalua un texto que contiene `Ã±` u otra secuencia de doble codificacion tipica
- **THEN** la deteccion es positiva y el texto revertido `value.encode('latin-1').decode('utf-8')` es estrictamente distinto y mas limpio que el original

#### Scenario: Texto limpio no es detectado

- **WHEN** se evalua un texto ya limpio (por ejemplo `"La impresora no imprime y sale papel atascado"`)
- **THEN** la deteccion es negativa y el texto se considera no corrupto

#### Scenario: Texto no reversible se maneja con gracia

- **WHEN** se evalua un texto que no es codificable en `latin-1` o cuyo reverso no es `utf-8` valido
- **THEN** la deteccion es negativa sin lanzar excepcion y el texto se deja fuera de la reparacion

### Requirement: Reparacion idempotente y selectiva de las descripciones

El sistema SHALL reparar UNICAMENTE las filas cuya descripcion pseudonimizada sea detectada como
corrupta por la firma del mojibake. Las filas limpias MUST NOT ser modificadas. La reparacion SHALL
ser IDEMPOTENTE: una segunda ejecucion sobre los mismos datos MUST NOT encontrar filas pendientes de
reparar y MUST NOT alterar las ya reparadas. El texto reparado SHALL ser el reverso de doble
codificacion del valor almacenado (`value.encode('latin-1').decode('utf-8')`), verificado por el
round-trip.

#### Scenario: Una fila corrupta queda reparada

- **WHEN** la reparacion procesa una fila cuya `descripcion_pseudonimizada` esta corrupta
- **THEN** el valor almacenado pasa a ser su reverso limpio y deja de presentar la firma del mojibake

#### Scenario: Una fila limpia queda intacta

- **WHEN** la reparacion procesa una fila cuya descripcion no esta corrupta
- **THEN** su descripcion queda EXACTAMENTE igual y la fila se reporta como omitida

#### Scenario: Reparacion idempotente

- **WHEN** la reparacion se ejecuta una segunda vez sobre datos ya reparados
- **THEN** no encuentra nuevas filas corruptas, no modifica ninguna fila y reporta cero reparadas

### Requirement: Reparacion de la columna pseudonimizada y de la columna cifrada

Para cada fila detectada como corrupta, el sistema SHALL reparar `descripcion_pseudonimizada` y,
para la MISMA fila, `descripcion_original`: descifrar el ciphertext, aplicar el reverso de doble
codificacion al texto plano y volver a cifrar el resultado, usando el helper de cifrado de la
aplicacion y la clave `PSEUDONYMIZATION_ENCRYPTION_KEY`. La reparacion de la columna cifrada SHALL
ser un round-trip verificado (descifrado -> reverso -> re-cifrado) y el texto plano resultante SHALL
dejar de presentar la firma del mojibake. Las columnas cifradas de las filas limpias MUST NOT ser
re-cifradas ni alteradas. Si la reparacion de la columna cifrada se juzga no viable para una fila (por
ejemplo, un token no descifrable), esa fila SHALL reportarse como error y su descripcion
pseudonimizada MUST NOT escribirse, dejando la fila sin cambios parciales.

#### Scenario: Ambas columnas se reparan para la misma fila

- **WHEN** se repara una fila corrupta
- **THEN** la `descripcion_pseudonimizada` queda limpia y, al descifrar `descripcion_original`, su texto plano tambien queda limpio

#### Scenario: La columna cifrada de una fila limpia no se toca

- **WHEN** se procesa una fila no corrupta
- **THEN** su `descripcion_original` no se re-cifra ni se modifica

### Requirement: Modo dry-run por defecto, escritura explicita y reporte de conteos

El script de reparacion SHALL operar en modo DRY-RUN por defecto: MUST NOT escribir ningun cambio en
la base salvo que se solicite explicitamente con `--apply`. El script SHALL imprimir un resumen con
los conteos de candidatos (filas corruptas detectadas), reparados, omitidos y errores. Cada fila SHALL
escribirse en su propia transaccion, de modo que el fallo de una fila MUST NOT producir escrituras
parciales ni impedir el procesamiento del resto; el script SHALL reportar cada error con su
identificador de fila.

#### Scenario: Dry-run no escribe

- **WHEN** se ejecuta el script sin `--apply`
- **THEN** ninguna fila se modifica en la base y el resumen reporta los candidatos y reparables detectados

#### Scenario: Apply escribe y reporta conteos

- **WHEN** se ejecuta el script con `--apply`
- **THEN** las filas corruptas se reparan y el resumen reporta candidatos, reparados, omitidos y errores

#### Scenario: El fallo de una fila no deja escrituras parciales

- **WHEN** una fila falla durante la reparacion (por ejemplo, un token no descifrable)
- **THEN** esa fila se reporta como error sin cambios parciales y el resto de las filas se procesa normalmente

### Requirement: Documentacion operativa de la reparacion

El proyecto SHALL incluir un runbook versionado de la reparacion que documente: la causa raiz (el
descarte del charset del paquete `@n8n/imap` en la decodificacion de partes `quoted-printable` y su
doble codificacion, con el mecanismo), el volumen afectado por cada base de datos, el reverso exacto
aplicado, el procedimiento (dry-run, revision de candidatos y `--apply`), la verificacion posterior
(ausencia de la firma del mojibake y round-trip) y la evidencia a registrar (conteos antes/despues por
base). El runbook SHALL declarar que el script NO es una migracion de base de datos y que se ejecuta
de forma manual y controlada.

#### Scenario: El runbook documenta causa, reverso y procedimiento

- **WHEN** un operador consulta el runbook de la reparacion
- **THEN** encuentra la causa raiz del mojibake con su mecanismo, el reverso exacto, el volumen afectado por base, el procedimiento de dry-run/apply y la evidencia a registrar

#### Scenario: El runbook declara la ejecucion manual

- **WHEN** un operador consulta el runbook
- **THEN** el documento declara que la reparacion es manual y controlada, no una migracion automatica, y que la aplicacion sobre la base de la campana requiere aprobacion explicita
