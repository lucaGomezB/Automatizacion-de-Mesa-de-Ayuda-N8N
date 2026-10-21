## ADDED Requirements

### Requirement: Obligación de propagación de las ramas consumidoras

Toda rama que reescriba los capítulos de la tesis SHALL propagar los valores
`vigente` del memo canónico y MUST NOT reintroducir los valores `retirado`. La rama
SHALL registrar en su `design.md` la lista de objetivos de propagación con la
palabra textual ANTES y DESPUÉS, y SHALL declarar la condición de reversibilidad
de cada decisión editorial que aplique. La rama SHALL dejar el documento sin
ninguna ocurrencia del valor `retirado` que reemplace.

#### Scenario: Rama consumidora propaga los valores vigentes

- **WHEN** una rama reescribe un capítulo que cita un valor `retirado`
- **THEN** el capítulo pasa a citar el valor `vigente` del memo
- **AND** el valor `retirado` no queda en ningún pasaje como resultado

#### Scenario: Reversibilidad declarada

- **WHEN** la rama aplica una decisión editorial del memo (por ejemplo retirar la proporción de intervención humana)
- **THEN** la rama declara en su `design.md` la condición bajo la cual esa decisión se revisaría
- **AND** la decisión no se fija como irreversible si el memo la marca reversible
