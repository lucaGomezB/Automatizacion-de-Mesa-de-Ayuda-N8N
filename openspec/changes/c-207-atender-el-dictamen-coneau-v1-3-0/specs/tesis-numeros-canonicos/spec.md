## ADDED Requirements

### Requirement: Registro de los valores introducidos por la atención del dictamen v1.3.0

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL agregar una sección 3.21 con cada
valor nuevo que c-207 lleve a la tesis (IC de la reducción del tiempo, acuerdo y kappa
`E3`/`E4`, verificación y recálculo del balance neto), cada uno con su procedencia
(`analisis_dictamen_c207.json` y clave), su comando y su estado (`vigente`; lo que depende de
supuestos de costo, `condicional`). La sección MUST NOT modificar valores ni estados `vigente`
de las secciones 3.1 a 3.20, salvo que la verificación del balance neto obligue a marcar como
superada una lectura previa, lo que SHALL anotarse con la remisión a la sección 3.21.

#### Scenario: Procedencia completa

- **WHEN** se lee la sección 3.21 del memo
- **THEN** cada valor tiene archivo fuente, clave, comando y estado

#### Scenario: Valores previos intactos

- **WHEN** se compara el memo antes y después del change
- **THEN** el diff se limita a la sección 3.21, al encabezado de upsert y, si corresponde, a la marca de lectura superada del balance neto
