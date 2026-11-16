## ADDED Requirements

### Requirement: Registro del anexo de números canónicos citados y de sus referencias

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección nueva y aditiva, posterior a la última sección vigente (hoy `3.37`), sin renumerar ni alterar las anteriores, que registre el anexo de números canónicos de la tesis: el rótulo del anexo (`sec:anexo-numeros-canonicos`), las secciones del memo cuyos valores el cuerpo cita (`3.31`, `3.33`, `3.35` y `3.36`) y cada valor transcripto al anexo con su procedencia y su estado. La sección SHALL declarar de forma explícita que el anexo es una transcripción condensada del memo, que el memo sigue siendo la fuente interna de verdad y que el anexo no introduce valores ausentes del memo ni modifica ningún valor ni estado previo. La sección SHALL registrar el reemplazo de las referencias del cuerpo al memo por número de sección (`Sección 3.xx`) por la remisión al anexo, y SHALL declarar cuántas ocurrencias se repuntaron. El memo SHALL conservar la trazabilidad del anexo hacia los valores citados, de modo que cada cifra del anexo se resuelva a una fila vigente del memo.

#### Scenario: Sección aditiva con el primer número libre

- **WHEN** se aplica el change y se relee el índice del memo
- **THEN** la sección nueva ocupa el primer número libre posterior a la última sección vigente
- **AND** ninguna sección previa se renumera ni se reescribe

#### Scenario: Trazabilidad anexo-memo por valor

- **WHEN** se lee la sección nueva del memo
- **THEN** figuran el rótulo del anexo, las secciones del memo citadas por el cuerpo y cada valor transcripto con su procedencia y su estado
- **AND** cada valor transcripto existe en el memo con el mismo valor y estado

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones anteriores del memo antes y después del change
- **THEN** cada valor conserva su cifra y su estado
- **AND** solo se agrega la sección nueva

#### Scenario: Referencias internas repuntadas

- **WHEN** se recorre el cuerpo de los capítulos tras el change
- **THEN** no queda ninguna cita del memo por número de sección (`Sección 3.xx`)
- **AND** la sección nueva del memo declara cuántas ocurrencias se repuntaron al anexo
