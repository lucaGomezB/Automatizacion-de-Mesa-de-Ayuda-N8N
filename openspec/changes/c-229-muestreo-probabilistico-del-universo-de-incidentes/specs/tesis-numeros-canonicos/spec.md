## ADDED Requirements

### Requirement: Registro aditivo del diseno de muestreo probabilistico y del efecto de diseno

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion nueva y
aditiva, posterior a la ultima seccion vigente (hoy `3.37`; esperado `3.40`), sin renumerar ni
alterar las anteriores. La seccion SHALL registrar, como minimo: la lectura ponderada vigente de la
exactitud estricta (`0,7489`, bootstrap `[0,6822; 0,8099]`) con su procedencia y la aclaracion de que
sus pesos son la composicion por sector del corpus de 200 y NO la del universo; el efecto de diseno de
la post-estratificacion aplicada al corpus con su metodo y su procedencia, con estado `condicional`;
la definicion del universo, el marco y los estratos del diseno probabilistico como plan, sin valores de
resultado; y la declaracion de que la ejecucion del diseno depende de datos que aun no existen y de la
cooperacion de la organizacion, con su condicion de reversibilidad. Cada valor SHALL declarar su
procedencia (archivo y linea, o el comando de solo lectura que lo reproduce) y un estado en
`{vigente, condicional}`. La seccion SHALL declarar de forma explicita que es un diseno planificado y
una lectura complementaria, que no mide de nuevo, que no cambia la cifra primaria `0,6893` ni la
lectura ponderada `0,7489`, y que no modifica ningun valor ni estado de las Secciones 3.1 a 3.37. El
efecto de diseno del diseno probabilistico SHALL declararse no computable sin la muestra probabilistica
y MUST NOT consignarse un valor estimado en su lugar.

#### Scenario: Seccion aditiva con el primer numero libre

- **WHEN** se aplica el change y se relee el indice del memo
- **THEN** la seccion nueva ocupa el primer numero libre posterior a la ultima seccion vigente
- **AND** ninguna seccion previa se renumera ni se reescribe

#### Scenario: Procedencia, estado y rotulo por valor

- **WHEN** se lee la seccion nueva del memo
- **THEN** la lectura ponderada y el efecto de diseno tienen archivo o comando de procedencia y estado en `{vigente, condicional}`
- **AND** la seccion esta rotulada como diseno planificado y lectura complementaria, no como medicion nueva

#### Scenario: Cifras canonicas intactas

- **WHEN** se comparan las Secciones 3.1 a 3.37 antes y despues del change
- **THEN** cada valor y estado previo se conserva
- **AND** solo se agrega la seccion nueva

#### Scenario: Efecto de diseno del diseno no consignado sin la muestra

- **WHEN** se busca el efecto de diseno del diseno probabilistico en el memo
- **THEN** figura como no computable con su motivo y su condicion de reversibilidad
- **AND** no aparece ningun valor estimado presentado como el del diseno probabilistico
