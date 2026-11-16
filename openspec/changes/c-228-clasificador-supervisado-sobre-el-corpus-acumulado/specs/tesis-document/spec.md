## ADDED Requirements

### Requirement: Ejemplar de la defensa sin cambios por el clasificador supervisado

El ejemplar que se defiende (`docs/Tesis/v10 (IA)/paper/sections/*.tex` en la version que cierra la entrega) MUST NOT modificarse por el clasificador supervisado sobre el corpus acumulado. En ese ejemplar la linea SHALL figurar solo como trabajo futuro, con el texto que fijan para `subsec:clasificador-supervisado`, `subsec:frontera-sistemas`, `subsec:corpus-independiente` y la limitacion de `Sistemas` de `08-discusion.tex` los requisitos vigentes tras archivar `c-235`; este requisito MUST NOT exigir texto adicional en esas subsecciones.

#### Scenario: Ejemplar intacto

- **WHEN** se compara `docs/Tesis/v10 (IA)/paper/sections` antes y despues de aplicar este change
- **THEN** no hay diferencias atribuibles a este change

#### Scenario: Sin contradiccion con el trabajo futuro vigente

- **WHEN** se leen `subsec:clasificador-supervisado` y `subsec:frontera-sistemas` en el ejemplar de la defensa
- **THEN** su texto es el que dejan los requisitos vigentes tras `c-235`
- **AND** no se presenta ningun entrenamiento ni medicion del clasificador supervisado como realizado

### Requirement: Informe del clasificador supervisado solo con compuertas cerradas en una version posterior

Una version de la tesis posterior a la defensa SHALL informar resultados del clasificador supervisado, de la revision del codebook de la frontera o de su evaluacion solo si la compuerta de procedencia y la compuerta etica y legal constan cerradas y verificadas por el director para cada dato usado. Cuando los informe, el texto SHALL rotular el conjunto de prueba (corpus probabilistico acreditado o particion retenida interna), SHALL declarar que el hibrido se ajusto, en parte, con el corpus de 200 casos y que ninguna lectura sobre ese corpus evalua el clasificador supervisado, SHALL declarar donde corrio cada modelo y si se envio texto a terceros, y MUST NOT usar cifras ni artefactos retirados por `c-235`. El texto MUST NOT introducir identificadores internos `c-NNN` en el cuerpo.

#### Scenario: Sin compuertas cerradas no hay informe

- **WHEN** alguna compuerta de un dato usado no consta cerrada y verificada
- **THEN** la tesis no informa resultados del clasificador supervisado
- **AND** la linea sigue figurando solo como trabajo futuro

#### Scenario: Informe rotulado

- **WHEN** una version posterior informa resultados con compuertas cerradas
- **THEN** cada cifra rotula su conjunto de prueba y el lugar de ejecucion del modelo
- **AND** ninguna lectura sobre el corpus de 200 casos se presenta como evaluacion del clasificador supervisado
