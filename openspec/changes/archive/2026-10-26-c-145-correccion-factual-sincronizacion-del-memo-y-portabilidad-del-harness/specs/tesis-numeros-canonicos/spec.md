## MODIFIED Requirements

### Requirement: Registro canónico con procedencia por valor

El proyecto SHALL mantener el memo `docs/Tesis/Correcciones/numeros-canonicos.md`
como fuente única de verdad numérica de la tesis. Cada valor citable SHALL
registrarse con su procedencia (archivo y línea de origen) y su estado, que SHALL
ser uno de `vigente`, `retirado` o `condicional`. El memo MUST NOT contener ningún
valor sin fuente verificable y MUST distinguir el valor vigente del valor retirado
cuando una corrección reemplace una cifra previa.

Todo margen de error que la tesis publique SHALL registrarse en el memo con su valor,
los insumos de la fórmula que lo producen (incluido el tamaño del universo `N`, el
nivel de confianza, la proporción esperada y el tamaño muestral), su procedencia y su
estado. Cuando el universo cambie, el memo SHALL marcar el margen anterior y su `N`
como `retirado` en la misma operación de upsert que registra el nuevo valor como
`vigente`. Toda referencia `archivo:línea` del memo a un `.tex` SHALL resolverse, en la
fecha de consolidación, a la línea que contiene el valor citado; el memo MUST NOT
conservar referencias desplazadas por ediciones posteriores.

#### Scenario: Todo valor tiene fuente y estado

- **WHEN** se recorre la tabla canónica del memo
- **THEN** cada fila declara el valor, el archivo y la línea de origen, y un estado en `{vigente, retirado, condicional}`
- **AND** la línea indicada existe en el archivo referenciado

#### Scenario: Valor retirado no se cita como vigente

- **WHEN** una cifra fue desmentida por la evidencia disponible
- **THEN** el memo la marca como `retirado` y el valor de reemplazo queda como `vigente`
- **AND** las ramas consumidoras no citan el valor retirado como resultado

#### Scenario: Margen de error registrado con su N

- **WHEN** la tesis publica un margen de error absoluto y su tamaño muestral
- **THEN** el memo registra el margen como `vigente` con el valor de `N`, los demas insumos de la fórmula y su procedencia
- **AND** el margen anterior y su `N` quedan marcados como `retirado`, sin borrarse

#### Scenario: Referencias de línea sin desplazamiento

- **WHEN** se verifica cada referencia `archivo:línea` del memo contra el `.tex` en la fecha de consolidación
- **THEN** la línea citada contiene el valor o el pasaje que el memo le atribuye
- **AND** no queda ninguna referencia desplazada por ediciones posteriores, incluidas las de `07-resultados.tex`
