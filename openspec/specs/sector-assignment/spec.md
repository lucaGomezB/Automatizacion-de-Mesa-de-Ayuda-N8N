# sector-assignment Specification

## Purpose
Define el contrato multietiqueta de asignacion de sector (sector predicho y sectores adicionales) entre el clasificador, la API y el webhook, y su persistencia normalizada en el backend.

## Requirements

### Requirement: ASG-001 — Contrato multietiqueta del resultado de clasificacion

El resultado de clasificacion SHALL exponer el sector principal como `sector_predicho` (string) y los sectores adicionales predichos como `sectores_adicionales` (lista de strings). El campo `categoria` MUST dejar de existir en el contrato. `sectores_adicionales` MUST ser una lista, posiblemente vacia, y MUST NOT repetir el valor de `sector_predicho`. Todos los valores MUST pertenecer al conjunto canonico de cinco sectores.

#### Scenario: Resultado con sector principal y adicionales

- **WHEN** el clasificador produce `sector_predicho = "Soporte Tecnico Hardware"` y detecta otro sector aplicable
- **THEN** el resultado expone `sector_predicho` y `sectores_adicionales` con el sector adicional, sin el campo `categoria`

#### Scenario: Resultado sin sectores adicionales

- **WHEN** el clasificador no detecta sectores adicionales
- **THEN** `sectores_adicionales` es una lista vacia `[]`

#### Scenario: Sector principal no repetido en adicionales

- **WHEN** el resultado se construye con un sector principal que tambien aparece entre los adicionales
- **THEN** el sistema no lo duplica dentro de `sectores_adicionales`

### Requirement: ASG-002 — Schemas de API y validacion del sector

Los schemas de respuesta y de validacion de la API SHALL usar `sector_predicho` y `sectores_adicionales` en lugar de `categoria`. La API MUST rechazar con un error de validacion cualquier sector que no pertenezca al conjunto canonico de cinco strings.

#### Scenario: Respuesta de clasificacion con el contrato nuevo

- **WHEN** un cliente consulta el resultado de una clasificacion
- **THEN** el cuerpo de respuesta contiene `sector_predicho` y `sectores_adicionales` y no contiene `categoria`

#### Scenario: Validacion de sector rechaza un valor invalido

- **WHEN** una operacion de validacion recibe un sector que no pertenece al conjunto canonico
- **THEN** la API responde con un error de validacion accionable

### Requirement: ASG-003 — Persistencia de sectores adicionales del incidente

El backend SHALL persistir el sector principal del incidente como clave foranea al catalogo de sectores y SHALL persistir los sectores adicionales en una estructura normalizada y consultable (tabla de union) con integridad referencial contra el catalogo de sectores. La desaparicion de un sector del catalogo MUST NOT corromper el incidente, y la eliminacion del incidente SHALL eliminar sus asociaciones de sectores adicionales.

#### Scenario: Creacion de incidente con sectores adicionales

- **WHEN** se crea y clasifica un incidente cuyo resultado incluye N sectores adicionales
- **THEN** persisten N asociaciones de sectores adicionales vinculadas al incidente y a filas validas del catalogo de sectores

#### Scenario: Integridad referencial de los sectores adicionales

- **WHEN** se intenta persistir una asociacion a un sector inexistente en el catalogo
- **THEN** la base de datos rechaza la operacion por violacion de clave foranea

#### Scenario: Eliminacion del incidente limpia las asociaciones

- **WHEN** se elimina un incidente con sectores adicionales
- **THEN** sus asociaciones de sectores adicionales se eliminan en cascada

### Requirement: ASG-004 — Migracion 004 sin mutar la migracion 001

El proyecto SHALL incorporar una migracion Alembic nueva (`004`) que agregue las estructuras de persistencia multietiqueta y siembre los cinco sectores canonicos. La migracion MUST NOT modificar el contenido de la migracion ya aplicada `001_seed_catalogs.py`, MUST ser idempotente al reejecutarse sobre la cabeza actual y MUST proveer un `downgrade` funcional.

#### Scenario: Upgrade siembra los cinco sectores

- **WHEN** se ejecuta `alembic upgrade head` sobre una base vacia o al dia con `001`
- **THEN** el catalogo `sector` contiene exactamente los cinco sectores canonicos y `Operaciones` no esta presente

#### Scenario: Migracion 001 intacta

- **WHEN** se inspecciona el archivo de la migracion `001_seed_catalogs.py`
- **THEN** su contenido no fue modificado por este cambio

#### Scenario: Downgrade funcional

- **WHEN** se ejecuta `alembic downgrade` desde la migracion `004`
- **THEN** las estructuras agregadas por `004` se revierten sin dejar el esquema en un estado inconsistente

### Requirement: ASG-005 — Persistencia de los conjuntos predicho y validado del log de clasificacion

El log de clasificacion SHALL soportar los conjuntos multietiqueta de sectores predichos y validados, ademas del sector principal predicho y validado. La validacion humana SHALL poder registrar el conjunto validado de sectores del caso y MUST NOT perder los sectores adicionales al confirmar o corregir una clasificacion.

#### Scenario: Log guarda el conjunto predicho

- **WHEN** se registra una clasificacion con sector principal y sectores adicionales predichos
- **THEN** el log conserva el sector principal y el conjunto completo de sectores predichos

#### Scenario: Validacion humana registra el conjunto validado

- **WHEN** un operador valida o corrige una clasificacion indicando sectores adicionales
- **THEN** el log conserva el conjunto validado de sectores y el incidente refleja la correccion

### Requirement: ASG-006 — Payload del webhook con el contrato multietiqueta

El payload de notificacion a N8N SHALL incluir `sector_predicho` y `sectores_adicionales` en lugar de `categoria`, manteniendo `incidente_id`, `confianza`, `etapa` y `requiere_revision_humana`.

#### Scenario: El payload usa el contrato nuevo

- **WHEN** se notifica a N8N la clasificacion de un incidente
- **THEN** el cuerpo JSON contiene `sector_predicho` y `sectores_adicionales` y no contiene `categoria`
