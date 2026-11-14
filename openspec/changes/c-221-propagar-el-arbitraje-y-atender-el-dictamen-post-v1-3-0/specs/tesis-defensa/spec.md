## MODIFIED Requirements

### Requirement: El documento precede a su incorporacion como anexo

El documento `docs/defensa/respuestas-tribunal.md` SHALL ser el artefacto fuente de las respuestas
y SHALL existir antes de cualquier edicion de `12-anexos.tex` que lo incorpore o lo retire. Su
inclusion como Anexo J depende de la decision de los autores registrada en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (OQ3 de c-221):

- Si los autores retiran el anexo, el documento SHALL conservarse como material de preparacion de
  la defensa, fuera del cuerpo y de los anexos de la tesis; `12-anexos.tex` MUST NOT contener la
  etiqueta `sec:anexo-respuestas-tribunal` y ninguna seccion de la tesis SHALL remitir a ella.
- Si los autores conservan el anexo, el Anexo J SHALL reproducir el contenido del documento fuente
  sin alterar las respuestas ni su numeracion, y las cifras de la validacion fuera de muestra
  SHALL actualizarse al resultado arbitrado en el documento fuente y en el anexo por igual.

Mientras la decision no este registrada, el estado vigente del anexo MUST NOT cambiar.

#### Scenario: El documento fuente precede al anexo

- **WHEN** se verifica el orden de los entregables del change
- **THEN** `docs/defensa/respuestas-tribunal.md` existe con sus 16 respuestas antes de cualquier edicion de `12-anexos.tex` que incorpore o retire el Anexo J
- **AND** si el Anexo J se conserva, reproduce las mismas 16 respuestas sin cambios de fondo respecto del documento fuente

#### Scenario: Anexo J retirado por decision de los autores

- **WHEN** la decision registrada es retirar el anexo
- **THEN** `12-anexos.tex` no contiene la etiqueta `sec:anexo-respuestas-tribunal`
- **AND** `docs/defensa/respuestas-tribunal.md` se conserva con sus 16 respuestas
- **AND** la compilacion no informa referencias indefinidas

#### Scenario: Anexo J conservado por decision de los autores

- **WHEN** la decision registrada es conservar el anexo
- **THEN** `12-anexos.tex` contiene la etiqueta `sec:anexo-respuestas-tribunal` con las 16 respuestas del documento fuente
- **AND** las cifras de la validacion fuera de muestra del anexo y del documento fuente coinciden entre si y con el memo canonico
