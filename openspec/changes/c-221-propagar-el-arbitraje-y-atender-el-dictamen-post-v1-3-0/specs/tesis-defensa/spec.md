## MODIFIED Requirements

### Requirement: El documento precede a su incorporacion como anexo

El documento `docs/defensa/respuestas-tribunal.md` SHALL ser el artefacto fuente de las respuestas
y SHALL conservarse como material de preparacion de la defensa, fuera del cuerpo y de los anexos
de la tesis. `12-anexos.tex` MUST NOT incluir las respuestas a las preguntas del tribunal, y
ninguna seccion de la tesis SHALL remitir a ese anexo.

#### Scenario: El documento fuente se conserva fuera de la tesis

- **WHEN** se verifica el estado de los entregables del change
- **THEN** `docs/defensa/respuestas-tribunal.md` existe con sus 16 respuestas
- **AND** `12-anexos.tex` no contiene la etiqueta `sec:anexo-respuestas-tribunal`
- **AND** la compilacion no informa referencias indefinidas
