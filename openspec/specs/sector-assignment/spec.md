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

### Requirement: ASG-007 — Ausencia explicita de prediccion ante senal nula

Cuando el clasificador determinista no encuentra ningun termino del vocabulario en la descripcion, el resultado SHALL senalar de forma EXPLICITA la ausencia de prediccion en lugar de emitir un sector arbitrario. El clasificador MUST NOT devolver un sector canonico por el solo hecho de ser la primera clave del mapa, ni presentar una confianza mayor que cero. El estado de ausencia de prediccion SHALL ser transitorio: el pipeline de clasificacion SHALL escalarlo a la etapa siguiente y MUST NOT persistirlo como un sector canonico. El contrato final del resultado persistido (ASG-001) no cambia: el resultado final expone un sector canonico o un estado de revision humana.

#### Scenario: Sin senal no se inventa un sector

- **WHEN** la descripcion no contiene ningun termino del vocabulario determinista
- **THEN** el resultado determinista senala ausencia de prediccion, no devuelve "Seguridad Informatica" ni otro sector canonico, y su confianza es 0.0

#### Scenario: El estado de ausencia escala el pipeline

- **WHEN** el clasificador hibrido recibe un resultado determinista con ausencia de prediccion
- **THEN** escala a la etapa siguiente en lugar de cortocircuitar con un sector fabricado

#### Scenario: La ausencia no se persiste como sector

- **WHEN** se persiste el resultado final de un caso que atraveso una ausencia de prediccion determinista
- **THEN** no se registra un sector canonico inventado por el no-match; el sector proviene de la etapa siguiente o el caso queda en revision humana

### Requirement: ASG-008 — Ambiguedad por empate de puntajes

Cuando dos o mas sectores alcanzan el MISMO puntaje maximo de matches, el resultado determinista SHALL marcarse como ambiguo y MUST NOT elegir un ganador por el orden arbitrario del mapa. Un resultado ambiguo MUST NOT cortocircuitar el pipeline; SHALL escalar a la etapa siguiente con la incertidumbre reflejada en su confianza. El empate SHALL poder distinguirse de un caso con senal dominante unica.

#### Scenario: Empate marca ambiguedad y escala

- **WHEN** dos sectores obtienen el mismo puntaje maximo de matches
- **THEN** el resultado se marca como ambiguo, no cortocircuita y escala a la etapa siguiente

#### Scenario: El orden del mapa no decide el ganador

- **WHEN** el empate ocurre entre sectores que aparecen en distinta posicion del mapa
- **THEN** el sector elegido no depende del orden de las claves y el resultado se reporta como ambiguo

#### Scenario: Un ganador dominante no se marca ambiguo

- **WHEN** un sector supera estrictamente a todos los demas en puntaje
- **THEN** el resultado no se marca ambiguo

### Requirement: ASG-009 — Confianza determinista con conteo minimo y margen

La `confianza` de un resultado determinista SHALL interpretarse como una medida de FUERZA DE SENAL (cuanta evidencia y cuanto margen tiene el ganador) y MUST NOT presentarse como un predictor de correctitud ni usarse como criterio de seleccion del cortocircuito. La confianza SHALL seguir combinando un conteo de matches del ganador con un MARGEN sobre el segundo candidato y SHALL permanecer acotada a [0.0, 1.0]. El sistema MUST NOT asumir que una confianza alta implica una prediccion correcta: la seleccion del cortocircuito SHALL gobernarse por el score de correctitud (ASG-010). El gate de conteo minimo asociado a esta confianza queda sujeto a la reevaluacion de ASG-011.

#### Scenario: Un unico match no produce confianza alta

- **WHEN** solo un termino del vocabulario matchea en la descripcion
- **THEN** la `confianza` resultante es baja (fuerza de senal debil) y NO se interpreta como probabilidad de acierto

#### Scenario: Senal dominante produce confianza alta

- **WHEN** el ganador supera el conteo de matches y mantiene un margen suficiente sobre el segundo
- **THEN** la `confianza` refleja esa dominancia como fuerza de senal, sin que ello implique por si solo que la prediccion sea correcta

#### Scenario: La confianza no selecciona el cortocircuito

- **WHEN** el pipeline decide cortocircuitar
- **THEN** la decision NO se basa en comparar la `confianza` contra el umbral, sino en el score de correctitud

#### Scenario: La confianza permanece acotada

- **WHEN** se calcula la confianza de cualquier resultado determinista
- **THEN** su valor pertenece al intervalo [0.0, 1.0]

### Requirement: ASG-010 — Score de correctitud del determinista

El clasificador determinista SHALL exponer un SCORE DE CORRECTITUD que ordene la correctitud esperada de su prediccion (un valor acotado a [0.0, 1.0] donde mayor = mas evidencia de acierto), calculado a partir de features observables en runtime (score ganador, runner-up, margen, cantidad de matches, longitud del texto y senales por sector). El score SHALL ser determinista (misma entrada, misma salida) y MUST NOT requerir al proveedor pago. El score NO SHALL presentarse como una probabilidad calibrada de acierto: su rol es gobernar la seleccion del cortocircuito mediante un punto de operacion comparativo (ver `classification-resilience`). La capacidad de separacion del score SHALL reportarse sobre datos no usados para fijar el punto de operacion (por ejemplo, validacion out-of-fold), de modo que no sea un artefacto del conjunto de ajuste.

#### Scenario: El score esta acotado a [0.0, 1.0]

- **WHEN** se calcula el score para cualquier resultado determinista
- **THEN** su valor pertenece al intervalo [0.0, 1.0]

#### Scenario: El score se evalua fuera del test reportado

- **WHEN** se evalua la capacidad de separacion del score
- **THEN** los datos de evaluacion excluyen el corpus usado para fijar el punto de operacion y la separacion se reporta sobre datos no usados para ese ajuste

#### Scenario: El score no invoca al proveedor pago

- **WHEN** se calcula o calibra el score
- **THEN** no se realiza ninguna llamada a Gemini ni a otro servicio pago

### Requirement: ASG-011 — Reevaluacion del gate de conteo minimo

El sistema MUST NOT asumir que exigir un conteo minimo de matches (`deterministic_min_matches`) eleva la precision del cortocircuito. La retencion, eliminacion o redefinicion de ese gate SHALL justificarse con evidencia de calibracion, y NO por inercia. Si el gate se conserva, MUST NOT actuar como criterio de seleccion del cortocircuito ni como sustituto del score de correctitud (ASG-010). El parametro SHALL seguir siendo configurable sin recompilar.

#### Scenario: El gate no se asume beneficioso

- **WHEN** se decide sobre el conteo minimo de matches
- **THEN** la decision cita evidencia de calibracion y no una suposicion de que mas matches implican mayor precision

#### Scenario: El gate no sustituye al score

- **WHEN** el gate de conteo minimo se conserva
- **THEN** la seleccion del cortocircuito sigue gobernada por el score de correctitud y no por el gate
