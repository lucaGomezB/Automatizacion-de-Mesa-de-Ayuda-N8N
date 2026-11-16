## ADDED Requirements

### Requirement: Registro aditivo de la procedencia del corpus unico y de la validez externa

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una seccion **aditiva** (el siguiente numero libre de la Seccion 3 al aplicar; el esperado es `3.44` mientras `3.39`-`3.42` sigan reservadas a `c-230`/`c-229`/`c-228`/`c-232`) que registre, con procedencia y estado, el **mapeo de procedencia del corpus unico congelado** (cada familia de cifras con su corrida y su configuracion) y la **declaracion de validez externa** (muestra no probabilistica por conveniencia, organizacion unica, universo proyectado `2.646 = 42 x 63`, remedio empirico `c-229`). Cada fila SHALL declarar el archivo y la linea de origen o el artefacto versionado, y un estado en `{vigente, retirado, condicional}`. La seccion MUST NOT modificar el valor ni el estado de ningun valor de las secciones previas y MUST NOT renumerarlas. La incorporacion SHALL dejar la numeracion de la Seccion 3 consecutiva y sin duplicados.

#### Scenario: Mapeo de procedencia registrado

- **WHEN** se recorre la seccion nueva del memo
- **THEN** cada familia de cifras declara su corrida, su configuracion y su procedencia
- **AND** el corpus congelado figura como unico, con su huella canonica

#### Scenario: Validez externa registrada

- **WHEN** se lee la entrada de validez externa
- **THEN** figuran la muestra no probabilistica por conveniencia, la organizacion unica y el universo proyectado `2.646 = 42 x 63`
- **AND** el remedio empirico `c-229` figura con estado `condicional` y su condicion de reversibilidad

#### Scenario: Numeracion consecutiva y valores previos intactos

- **WHEN** se comparan los encabezados de la Seccion 3 antes y despues del change
- **THEN** la seccion nueva ocupa el siguiente numero libre y la secuencia `3.N` sigue consecutiva y sin duplicados
- **AND** ningun valor ni estado de las secciones previas cambia

#### Scenario: Lineas de origen vigentes

- **WHEN** se verifica cada referencia `archivo:linea` de la seccion nueva contra el `.tex` en la fecha de consolidacion
- **THEN** la linea citada contiene el pasaje que el memo le atribuye
- **AND** no queda ninguna referencia desplazada por las ediciones de este change
