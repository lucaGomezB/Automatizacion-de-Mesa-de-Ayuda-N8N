# Spec delta: Publicar la release siguiente a v1.6.2 y la nota de erratum

## ADDED Requirements

### Requirement: Nota de erratum de una release con PDF de tag de hash ajeno

Cuando el PDF compilado en el arbol de un tag publicado imprima un hash que no corresponde a su commit de contenido, la tesis SHALL registrar una **nota de erratum** en `docs/Tesis/Correcciones/dictamen-correcciones.md` que identifique el tag, el hash impreso y el hash del commit de contenido, y declare que el tag no se mueve ni se borra. La release siguiente SHALL compilar el PDF de modo que su Anexo B no imprima ningun hash (remita al tag y a `compilacion.md`) y el commit siguiente SHALL consignar el hash del commit de contenido y recompilar; `compilacion.md` SHALL nombrar el commit compilado en cada caso.

#### Scenario: Release posterior a un tag con PDF de hash ajeno

- **WHEN** se compila una release cuyo tag anterior tenia un PDF que imprimia un hash ajeno
- **THEN** el PDF del commit de contenido (C3) no imprime ningun hash en el Anexo B
- **AND** el commit C4 consigna el hash del commit de contenido y recompila
- **AND** `compilacion.md` nombra el commit compilado

#### Scenario: La nota de erratum no mueve el tag

- **WHEN** se registra la nota de erratum del tag con PDF de hash ajeno
- **THEN** el tag no se borra, recrea ni reapunta
- **AND** la nota identifica el hash impreso (`17aa6d21`) y el hash del commit de contenido (`e7013127`)

### Requirement: Verificacion de flotantes en la release

La compilacion de una release SHALL verificar que cada figura y tabla flotante quede dentro de su seccion o anexo y que ninguna desborde el margen, y SHALL registrar el resultado.

#### Scenario: Flotantes contenidos

- **WHEN** se verifica la posicion de los flotantes en el PDF compilado
- **THEN** cada figura y tabla queda dentro de su seccion o anexo
- **AND** el resultado se registra en `docs/Tesis/Correcciones/dictamen-correcciones.md`
