## ADDED Requirements

### Requirement: Registro aditivo de las cifras de cobertura y pruebas ancladas a la configuracion evaluada

El memo canonico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion
nueva y aditiva con el **primer numero libre** al aplicar (hoy la ultima seccion es la `3.38`;
se espera la `3.43`), sin renumerar ni alterar las secciones anteriores. La seccion SHALL
registrar, con su procedencia (comando reproducible, revision y entorno) y su estado en
`{vigente, retirado, condicional}`: la cobertura de sentencias (porcentaje, sentencias totales
y sin cubrir) y el numero de pruebas unitarias medidos sobre la **configuracion evaluada**
(`bf5e099`, 7-10-2026) y, si difiere, sobre la **configuracion entregada** (`v1.3.0`,
`1b17e55`). Cada valor de la medicion anterior anclada a `v1.2.18` que deje de ser el vigente
SHALL marcarse como `retirado` en la misma operacion de upsert que registra el nuevo valor como
`vigente`, sin borrarse. La seccion SHALL declarar de forma explicita que no modifica ningun
valor ni estado de las secciones `3.1` a `3.42`, salvo la procedencia de las cifras de cobertura
y pruebas que aqui se re-anclan.

#### Scenario: Seccion aditiva con las cifras re-ancladas

- **WHEN** se lee la seccion nueva del memo
- **THEN** figuran la cobertura y el numero de pruebas de `bf5e099` con su comando y su entorno
- **AND** cada valor declara un estado en `{vigente, retirado, condicional}`

#### Scenario: Contraparte entregada registrada

- **WHEN** las cifras de `v1.3.0` difieren de las de `bf5e099`
- **THEN** el memo registra ambas lecturas rotuladas por revision
- **AND** si coinciden, lo declara sin duplicar la fila

#### Scenario: Anclaje previo retirado sin borrarse

- **WHEN** se compara el memo antes y despues del change
- **THEN** el anclaje a `v1.2.18` que deje de ser vigente figura como `retirado`
- **AND** ningun valor ni estado de las secciones `3.1` a `3.42` cambia, salvo esa marca de procedencia

#### Scenario: Numeracion consecutiva

- **WHEN** se listan los encabezados de la Seccion 3 del memo despues del apply
- **THEN** la seccion nueva ocupa el siguiente numero libre y la secuencia `3.N` sigue consecutiva y sin duplicados
- **AND** no se renumera ninguna seccion previa

### Requirement: Trazabilidad de la correccion de consistencia interna y bibliografia

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incorporar, siguiendo el patron de la
entrada de c-231, las filas de trazabilidad que mapean cada correccion de este change (A1 a A3,
B1 a B10, C1 a C7) a su archivo y linea y a un fragmento verificable, con su estado. La entrada
SHALL declarar que el change es de redaccion, etiquetas, procedencia y bibliografia, que no
introduce datos ni mediciones nuevas (salvo las cifras de cobertura de B4, canalizadas por el
memo) y que los checkpoints humanos de gobernanza ALTA quedaron registrados. El registro MUST
NOT alterar la trazabilidad de changes previos.

#### Scenario: Filas de trazabilidad registradas

- **WHEN** se recorre la entrada de c-233 del registro
- **THEN** cada correccion A1..A3 y B1..B10 tiene archivo, linea y fragmento verificable
- **AND** cada fila declara su estado

#### Scenario: Trazabilidad previa intacta

- **WHEN** se compara el registro antes y despues del change
- **THEN** las entradas de changes previos no cambian
- **AND** la entrada nueva es aditiva
