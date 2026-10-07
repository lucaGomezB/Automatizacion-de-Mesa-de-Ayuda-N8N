# Delta for sector-assignment

## MODIFIED Requirements

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

## ADDED Requirements

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
