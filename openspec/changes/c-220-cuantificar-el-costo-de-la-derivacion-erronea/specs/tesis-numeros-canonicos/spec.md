## ADDED Requirements

### Requirement: Registro aditivo del costo de la derivación errónea

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección nueva y aditiva para el costo de la derivación errónea, posterior a la última sección vigente y sin renumerar ni alterar las anteriores. La sección SHALL registrar, como mínimo: la duración medida de las intervenciones que cambian la derivación y de las que no la cambian, con `n`, media, mediana e intervalo bootstrap al 95 %; la diferencia entre ambas; el tiempo de decisión de sector del brazo manual como proxy del rediagnóstico, con `n`, media, mediana, intervalo y desagregado por operador; la composición de `c` en un tramo activo medido y un tramo anclado, con el valor del ancla y su fuente primaria; el intervalo compuesto y el método de propagación; y la comparación explícita contra la banda canónica `[600; 900] s`. Cada valor SHALL llevar el archivo y la ruta de origen y un estado en `{vigente, condicional, retirado}`. La sección SHALL declarar qué régimen mide cada componente y qué tramo del proceso queda fuera de la medición. MUST NOT modificar ningún valor ni estado `vigente` de las secciones anteriores.

#### Scenario: Sección aditiva con procedencia

- **WHEN** se lee la sección nueva del memo
- **THEN** cada valor figura con su archivo y ruta de origen y un estado en `{vigente, condicional, retirado}`
- **AND** la sección declara que es aditiva y no reemplaza ningún valor de las secciones previas

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones previas del memo antes y después del change
- **THEN** cada valor conserva su cifra y su estado
- **AND** solo se agrega la sección nueva y, si corresponde, una remisión desde la sección que declaraba el costo sin registro

#### Scenario: Descomposición declarada por régimen

- **WHEN** se lee la definición operacional de `c` en el memo
- **THEN** consta qué régimen mide cada componente (corrección en la compuerta, rediagnóstico en el sector receptor, reanudación tras interrupción)
- **AND** consta explícitamente qué tramo no se midió y con qué cota se acota

#### Scenario: Banda canónica contrastada

- **WHEN** el intervalo compuesto de `c` se compara con la banda `[600; 900] s`
- **THEN** la sección declara si la banda queda contenida, intersectada o excluida
- **AND** si queda excluida, la sección registra el hallazgo y remite a la decisión del dueño sin recalcular el balance neto por su cuenta