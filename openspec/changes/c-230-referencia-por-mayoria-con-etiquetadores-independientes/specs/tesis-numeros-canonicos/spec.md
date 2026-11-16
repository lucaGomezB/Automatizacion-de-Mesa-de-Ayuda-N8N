## ADDED Requirements

### Requirement: Registro aditivo de la referencia por mayoria y del acuerdo multievaluador

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva y
aditiva, posterior a la ultima seccion vigente, sin renumerar ni alterar las anteriores. La seccion
SHALL registrar, como minimo: la composicion de la referencia por mayoria (los cinco etiquetadores
`E3`, `E4`, `E6`, `E7`, `E8` y el umbral `>= 3` de `5`); el conteo de casos con mayoria y el conteo y
los identificadores de los casos `sin_mayoria`, con la regla de respaldo aplicada; el kappa de Fleiss
entre los cinco etiquetadores y la matriz de kappa de Cohen por pares, con su IC; la exactitud estricta
y la macro-F1 bajo la referencia por mayoria y bajo la referencia vigente de arbitro unico, con sus
intervalos de Wilson y el delta entre ambas; y el veredicto del umbral de `0,85` por lectura. Cada
valor SHALL llevar su archivo fuente y la clave del JSON que lo produce, o el comando que lo
reproduce, y un estado en `{vigente, sensibilidad, reinterpretacion, condicional, retirado}`. La
seccion SHALL declarar de forma explicita que la referencia por mayoria reemplaza, como referencia
primaria, a la de arbitro unico en el `31 %` de los casos, que ambas lecturas se conservan y que la
cifra primaria previa no se retira silenciosamente. La seccion SHALL declarar que no modifica ningun
valor ni estado de las secciones anteriores del memo.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera ni se reescribe

#### Scenario: Cada valor con procedencia y estado

- **WHEN** se lee la seccion nueva del memo
- **THEN** cada valor tiene archivo fuente o comando, ambito y estado
- **AND** la comparacion de las dos referencias y el kappa de Fleiss figuran con su procedencia

#### Scenario: Cifra primaria previa conservada y rotulada

- **WHEN** se comparan las dos lecturas de la exactitud estricta
- **THEN** ambas figuran con su valor, su intervalo y su rotulo de referencia
- **AND** la cifra primaria previa no se retira silenciosamente ni se borra

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones anteriores del memo antes y despues del change
- **THEN** cada valor conserva su cifra y su estado
- **AND** solo se agrega la seccion nueva
