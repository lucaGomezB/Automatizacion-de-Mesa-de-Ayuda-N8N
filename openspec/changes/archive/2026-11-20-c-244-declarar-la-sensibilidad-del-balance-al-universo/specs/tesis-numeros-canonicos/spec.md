<!--
  Delta de c-244 sobre la capacidad `tesis-numeros-canonicos`.

  Requisito ADDED (no MODIFIED): la seccion aditiva que registra la sensibilidad del
  balance al universo N es una preocupacion nueva. No reescribe el requisito
  "Registro aditivo del balance neto acotado con el termino de revision"
  (openspec/specs/tesis-numeros-canonicos/spec.md, L1146), que gobierna la seccion de
  c-236 (memo 3.46); este delta solo agrega una seccion propia con el primer numero
  libre al aplicar.

  El requisito ADDED es de documento (no hay implementacion de codigo). El cambio de
  comportamiento es a nivel de spec, por lo que no aplica `skip_specs`.
-->

## ADDED Requirements

### Requirement: Registro aditivo de la sensibilidad del balance al universo N

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección
nueva y aditiva con el primer número libre de la Sección 3 al aplicar, sin renumerar ni alterar
las secciones previas, que registre los valores de referencia del balance `B_r` para los universos
`N` que el cuerpo cite (al menos `N = 1.000`, `5.000` y `10.000`, con `+7,1`, `+35,4` y `+70,7`
horas-persona por trimestre respectivamente). Cada valor SHALL registrarse con su procedencia (el
corchete constante `25,4688` s de la fórmula `B_r = (N/3.600)[Δt − ρr − (e_aut − e_man)c]`,
derivado por el generador de solo lectura
`evaluation/data/campana/analisis/analisis_balance_neto_c236.py`), su comando reproducible y el
estado `condicional`, rotulado como derivado de un universo asumido. La sección SHALL declarar
que `B_r` escala de forma lineal con `N` y que `a*_r` y `c*` no dependen de `N`, y que `N` es una
premisa del escenario narrativo, no un universo medido. La sección MUST NOT registrar estos
valores como canónicos, MUST NOT cambiar el valor ni el estado del balance central `+18,7` de la
sección de c-236 ni de ningún valor `vigente` previo, y SHALL dejar la numeración de la Sección 3
consecutiva y sin duplicados.

#### Scenario: Sección aditiva con el primer número libre

- **WHEN** se aplica el change y se relee el índice del memo
- **THEN** la sección nueva ocupa el primer número libre posterior a la última sección vigente
- **AND** ninguna sección previa se renumera ni cambia de cifra o estado

#### Scenario: Valores registrados como derivados y condicionales

- **WHEN** se recorre la sección nueva del memo
- **THEN** `+7,1`, `+35,4` y `+70,7` figuran con estado `condicional`, con su procedencia y su comando de recálculo
- **AND** cada uno se rotula como derivado de un universo `N` asumido

#### Scenario: Balance central y valores vigentes intactos

- **WHEN** se compara el memo antes y después del change
- **THEN** el balance central `+18,7` de la sección de c-236 conserva su valor y su estado
- **AND** ningún valor `vigente` previo cambia de valor ni de estado

#### Scenario: N declarado como premisa del escenario

- **WHEN** se lee la cabecera de la sección nueva
- **THEN** declara que `B_r` escala linealmente con `N`, que `a*_r` y `c*` no dependen de `N`
- **AND** declara que `N` es una premisa del escenario narrativo, no un universo medido
