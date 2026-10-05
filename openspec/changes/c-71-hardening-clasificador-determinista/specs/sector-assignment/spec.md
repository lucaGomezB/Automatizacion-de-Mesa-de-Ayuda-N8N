# Delta for sector-assignment

## ADDED Requirements

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

La confianza de un resultado determinista SHALL dejar de ser una funcion que vale 1.0 ante un unico match y cae por debajo de 0.5 ante un segundo match. La confianza SHALL combinar un conteo MINIMO de matches del ganador con un MARGEN sobre el segundo candidato, de modo que un solo match, o un empate, no produzca una confianza alta. Una confianza alta SHALL ser evidencia de una senal dominante y no un artefacto del conteo de sectores que matchearon. La confianza MUST seguir acotada a [0.0, 1.0].

#### Scenario: Un unico match no produce confianza alta

- **WHEN** solo un termino del vocabulario matchea en la descripcion
- **THEN** la confianza resultante no alcanza el umbral de cortocircuito

#### Scenario: Senal dominante produce confianza alta

- **WHEN** el ganador supera el conteo minimo y mantiene un margen suficiente sobre el segundo
- **THEN** la confianza resultante refleja esa dominancia y puede alcanzar el umbral de cortocircuito

#### Scenario: La confianza permanece acotada

- **WHEN** se calcula la confianza de cualquier resultado determinista
- **THEN** su valor pertenece al intervalo [0.0, 1.0]
