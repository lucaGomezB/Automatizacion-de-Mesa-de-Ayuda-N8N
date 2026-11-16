## ADDED Requirements

### Requirement: Declaracion del diseno de muestreo probabilistico del universo y su estado condicional

La tesis SHALL declarar, en el capitulo metodologico (subseccion de poblacion, muestra y corpus,
`subsec:poblacion-muestra-corpus`) y en el trabajo futuro (capitulo de recomendaciones,
`subsec:corpus-independiente`), que la validacion reportada se apoya en una muestra no probabilistica
por conveniencia de una sola organizacion y que existe un diseno de muestreo probabilistico
estratificado del universo, con cuotas prefijadas por canal y por sector, denominadores y reglas de
decision prefijados, cuyo estado es `condicional` porque depende de datos que aun no existen y de la
cooperacion de la organizacion. La tesis SHALL declarar de forma explicita que ese diseno NO eleva la
exactitud del clasificador, sino que hace valida la estimacion (permite referir las metricas al
universo con su efecto de diseno). La tesis SHALL reportar la lectura ponderada de la exactitud
estricta (`0,7489`) y el efecto de diseno como lecturas complementarias rotuladas, y MUST NOT
presentar la ponderada como la cifra primaria (`0,6893`) ni cambiar ningun valor canonico. La tesis
MUST NOT afirmar que la muestra de 200 casos es probabilistica ni que su intervalo de confianza se
estima sobre el universo.

#### Scenario: Metodologia declara el diseno y su estado condicional

- **WHEN** se lee la subseccion de poblacion, muestra y corpus
- **THEN** figura la declaracion de que la muestra es no probabilistica por conveniencia y que existe un diseno probabilistico estratificado cuyo estado es `condicional`
- **AND** se declara que el diseno no eleva la exactitud del clasificador, sino que hace valida la estimacion

#### Scenario: Lectura ponderada y efecto de diseno rotulados

- **WHEN** se leen los resultados de la validacion fuera de muestra
- **THEN** la lectura ponderada `0,7489` y el efecto de diseno figuran rotulados como complementarios
- **AND** la cifra primaria `0,6893` y su intervalo no cambian

#### Scenario: Recomendaciones remiten al diseno

- **WHEN** se lee la subseccion de validacion sobre un corpus independiente
- **THEN** remite al diseno probabilistico del universo con cuotas prefijadas por canal y sector
- **AND** declara que su ejecucion depende de datos nuevos y de la cooperacion de la organizacion

#### Scenario: Sin afirmacion de muestreo probabilistico

- **WHEN** se busca en la tesis una afirmacion de que la muestra de 200 casos es probabilistica o que su intervalo se estima sobre el universo
- **THEN** no aparece ninguna
- **AND** el muestreo se declara no probabilistico por conveniencia de forma coherente en el cuerpo y el resumen
