## ADDED Requirements

### Requirement: Registro de los valores citados por el documento de respuestas del tribunal

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, con archivo y linea de origen y estado, todo valor de resultado que el documento `docs/defensa/respuestas-tribunal.md` y su incorporacion como Anexo J citen y que no figure ya en el memo. Cada valor SHALL ser recalculable desde un artefacto versionado o SHALL declararse en "Decisiones no resolubles" con su condicion de reversibilidad. La incorporacion de las respuestas MUST NOT cambiar el valor ni el estado de ningun valor canonico vigente.

#### Scenario: Valores nuevos registrados

- **WHEN** se recorre el documento de respuestas y su incorporacion como Anexo J
- **THEN** cada cifra de resultado que no figure ya en el memo tiene una fila con archivo y linea de origen y un estado en `{vigente, retirado, condicional}`
- **AND** la linea indicada existe en el archivo referenciado

#### Scenario: Valores canonicos vigentes intactos

- **WHEN** se compara el memo antes y despues del change
- **THEN** ningun valor vigente previo cambia de valor ni de estado
- **AND** los valores nuevos se agregan como entradas propias
