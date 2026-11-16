## ADDED Requirements

### Requirement: Registro aditivo del diseno de muestreo probabilistico y del efecto de diseno

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar la seccion
reservada `3.40` (reserva que reconocen los registros de `c-234` y `c-235`), aditiva y sin renumerar
ni alterar ninguna otra seccion. La seccion SHALL registrar: el universo, el marco, los estratos, las
cuotas con minimos por sector y las clases declaradas no estimables, como plan; el control de sanidad
de la herramienta (post-estratificacion del corpus de 200 con su propia composicion: `147/200 =
0,7350`, DEFF `1`), rotulado como verificacion de implementacion y no como estimacion poblacional; el
estado de las compuertas de procedencia y etica/legal con la fecha del acta, sin datos personales; y,
solo si la campana se ejecuto con las compuertas cerradas, la exactitud ponderada y la cruda, el DEFF
y el IC sobre el universo con su comando reproducible. Mientras la muestra no exista, el DEFF del
diseno SHALL figurar como no computable con estado `condicional`, sin valor estimado. Cada valor
SHALL declarar su procedencia (archivo y clave, o comando de solo lectura) y un estado en
`{vigente, condicional}`. La seccion MUST NOT citar como ancla, insumo ni comparador ninguna cifra con
estado `retirado` en el memo, y MUST NOT cambiar el valor ni el estado de ninguna otra seccion.

#### Scenario: Seccion reservada aditiva

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva es la `3.40`
- **AND** ninguna otra seccion se renumera ni se reescribe

#### Scenario: Control de sanidad rotulado

- **WHEN** se lee el registro del control de sanidad
- **THEN** figura `147/200 = 0,7350` con DEFF `1`, con su comando
- **AND** se rotula como verificacion de implementacion, no como estimacion poblacional

#### Scenario: Sin cifras retiradas

- **WHEN** se buscan en la seccion `3.40` cifras con estado `retirado` en el memo
- **THEN** no hay coincidencias

#### Scenario: DEFF del diseno no consignado sin la muestra

- **WHEN** la campana no se ejecuto
- **THEN** el DEFF del diseno figura como no computable y `condicional`
- **AND** no aparece ningun valor estimado en su lugar
