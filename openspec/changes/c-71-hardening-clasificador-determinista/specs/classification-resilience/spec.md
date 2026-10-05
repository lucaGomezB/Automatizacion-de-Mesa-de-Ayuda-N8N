# Delta for classification-resilience

## MODIFIED Requirements

### Requirement: Fallback tras agotar los reintentos

Agotados los intentos sin exito, el sistema SHALL aplicar el fallback vigente: un resultado con `etapa=fallback`, `confianza=0.0` y `requiere_revision_humana=true`, preservando la mejor estimacion disponible de la etapa deterministica. Cuando la etapa deterministica no produjo ninguna estimacion (ausencia de prediccion), el fallback MUST preservar esa ausencia y MUST NOT fabricar un sector canonico. El fallback MUST NOT propagar la excepcion del proveedor al llamador del clasificador hibrido.

#### Scenario: Agotar los reintentos produce el fallback con revision humana

- **WHEN** se agotan los intentos configurados sin una clasificacion valida
- **THEN** el resultado tiene `etapa=fallback`, `confianza=0.0` y `requiere_revision_humana=true`

#### Scenario: El fallback conserva la mejor estimacion deterministica

- **WHEN** el clasificador deterministico produjo una estimacion con confianza insuficiente antes de escalar a Gemini
- **THEN** el fallback conserva el sector del deterministico como mejor estimacion disponible

#### Scenario: El fallback no fabrica un sector sin estimacion

- **WHEN** se agotan los reintentos y la etapa deterministica no produjo ninguna prediccion
- **THEN** el fallback no inventa un sector canonico, conserva la ausencia de estimacion y marca revision humana

#### Scenario: El fallback no propaga la excepcion

- **WHEN** se agotan los reintentos por una falla de indisponibilidad o timeout
- **THEN** el clasificador hibrido devuelve el resultado de fallback y NO propaga la excepcion del proveedor

## ADDED Requirements

### Requirement: Decision de cortocircuito calibrada por precision y cobertura

La decision de cortocircuitar la etapa semantica SHALL basarse en un umbral de confianza calibrado contra el corpus mediante una curva de precision/cobertura, y MUST NOT depender de un valor degenerado que en la practica equivale a "un solo sector matcheo". El sistema SHALL fijar un PISO DE PRECISION aceptable para los casos cortocircuitados y SHALL maximizar la cobertura sujeta a ese piso. El umbral resultante SHALL ser explicito, documentado y verificable sobre el corpus, y SHALL poder ajustarse sin recompilar. La calibracion MUST NOT invocar al proveedor pago.

#### Scenario: El cortocircuito respeta el piso de precision

- **WHEN** se evalua sobre el corpus el subconjunto de casos cortocircuitados con el umbral elegido
- **THEN** la precision del subconjunto es mayor o igual al piso de precision definido

#### Scenario: La cobertura queda justificada

- **WHEN** se elige el umbral
- **THEN** existe una curva precision/cobertura documentada que justifica el tradeoff entre cobertura y precision, y el umbral elegido se deriva de ella

#### Scenario: La calibracion es offline

- **WHEN** se corre la calibracion del umbral
- **THEN** no se realiza ninguna llamada a Gemini y el calculo depende solo del corpus y del clasificador determinista

### Requirement: Escalamiento ante ausencia de prediccion o ambiguedad

El clasificador hibrido SHALL escalar a la etapa semantica cuando el resultado determinista senale ausencia de prediccion o ambiguedad, con independencia del umbral de cortocircuito. Una ausencia de prediccion o un empate MUST NOT cortocircuitar el pipeline ni derivar directamente a revision humana como unica via, salvo la politica resuelta por el autor para el no-match. El escalamiento SHALL quedar observable con la causa (sin senal o ambiguo).

#### Scenario: La ausencia de prediccion escala

- **WHEN** el resultado determinista senala ausencia de prediccion
- **THEN** el pipeline escala a la etapa semantica y no cortocircuita

#### Scenario: La ambiguedad escala

- **WHEN** el resultado determinista se marca como ambiguo por empate
- **THEN** el pipeline escala a la etapa semantica y no cortocircuita

#### Scenario: El escalamiento es observable

- **WHEN** el pipeline escala por ausencia de prediccion o ambiguedad
- **THEN** emite un evento estructurado con la causa del escalamiento, sin incluir el contenido crudo de la descripcion
