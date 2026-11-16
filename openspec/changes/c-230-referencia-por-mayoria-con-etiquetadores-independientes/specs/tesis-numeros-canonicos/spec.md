## ADDED Requirements

### Requirement: Registro aditivo de la referencia por mayoria y del acuerdo multievaluador

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la seccion
reservada `3.39` (reserva que reconocen los registros de `c-234` y `c-235`), aditiva y sin renumerar
ni alterar ninguna otra seccion. La seccion SHALL registrar: el protocolo de referencia (numero de
etiquetadores, umbral, tratamiento de `sin_mayoria`) con la fecha de la constancia del director; la
verificacion de las funciones contra sus oraculos (sintetico y publicado), rotulada como verificacion
de implementacion; el estado de las compuertas con la fecha del acta, sin datos personales; y, solo si
la referencia de la muestra probabilistica se construyo con las compuertas cerradas, la cobertura, el
conteo de `sin_mayoria`, el kappa de Fleiss con su IC y la matriz de Cohen por pares, con archivo
fuente y clave o comando reproducible. Cada valor SHALL llevar un estado en `{vigente, condicional}`.
La seccion SHALL conservar como linea base, por remision y sin cambiar su valor ni su estado, el kappa
`0,5569` de `E1`/`E2` sobre los 200 casos. La seccion MUST NOT citar como ancla, insumo ni comparador
ninguna cifra con estado `retirado` en el memo, y MUST NOT cambiar el valor ni el estado de ninguna
otra seccion.

#### Scenario: Seccion reservada aditiva

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva es la `3.39`
- **AND** ninguna otra seccion se renumera ni se reescribe

#### Scenario: Valores con procedencia y estado

- **WHEN** se lee la seccion `3.39`
- **THEN** cada valor tiene archivo fuente o comando y estado en `{vigente, condicional}`

#### Scenario: Sin cifras retiradas

- **WHEN** se buscan en la seccion `3.39` cifras con estado `retirado` en el memo
- **THEN** no hay coincidencias
