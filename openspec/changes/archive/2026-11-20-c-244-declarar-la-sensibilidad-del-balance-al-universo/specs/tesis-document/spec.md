<!--
  Delta de c-244 sobre la capacidad `tesis-document`.

  Requisito ADDED (no MODIFIED): la sensibilidad del balance al universo asumido
  es una preocupacion nueva. No colisiona con "Aritmetica metodologica verificable"
  (openspec/specs/tesis-document/spec.md, L735), que exige el calculo explicito de
  las proyecciones pero no la declaracion de dependencia con N. El texto del body
  vive en `subsec:balance-neto` de `08-discusion.tex`.

  El requisito ADDED es de documento (no hay implementacion de codigo). El cambio de
  comportamiento es a nivel de spec, por lo que no aplica `skip_specs`.
-->

## ADDED Requirements

### Requirement: Declaración de la sensibilidad del balance neto al universo asumido

La subsección `subsec:balance-neto` de `08-discusion.tex` SHALL declarar que el balance neto
trimestral `B_r` escala de forma lineal con el universo `N` y que la exactitud mínima de
equilibrio `a*_r` y el costo de equilibrio `c*` NO dependen de `N`. El documento SHALL presentar
`N = 2.646` como premisa del escenario narrativo y MUST NOT presentarlo como un universo medido.
La declaración SHALL exponer, en una sola oración del cuerpo, como valores de referencia derivados
y rotulados explícitamente como condicionales, el balance resultante para `N = 1.000`, `5.000` y
`10.000` (con `+7,1`, `+35,4` y `+70,7` horas-persona por trimestre respectivamente), obtenidos por
multiplicación del corchete constante de la fórmula por `N/3.600`. La declaración SHALL ser una
sola oración del cuerpo y MUST NOT introducir una tabla en el cuerpo; una tabla en un anexo es
opcional y en ningún caso sustituye a la oración del cuerpo. MUST NOT modificar la cifra canónica
del balance central (`+18,7` horas-persona por trimestre) ni ningún otro número canónico.
Las referencias de `N` que la oración cite SHALL quedar registradas en el memo canónico
`docs/Tesis/Correcciones/numeros-canonicos.md` como valores derivados/`condicional`, no canónicos.

#### Scenario: Declaración de linealidad presente

- **WHEN** se lee `subsec:balance-neto` de `08-discusion.tex` tras aplicar el change
- **THEN** el texto declara que `B_r` escala de forma lineal con `N`
- **AND** la declaración ocupa una sola oración del cuerpo (no una nota al pie)

#### Scenario: Cantidades independientes de N declaradas

- **WHEN** se lee la oración de sensibilidad
- **THEN** declara que `a*_r` y `c*` no dependen de `N`
- **AND** no atribuye a `a*_r` ni a `c*` una dependencia de `N`

#### Scenario: N rotulado como premisa y no como medición

- **WHEN** se busca `N` en `subsec:balance-neto`
- **THEN** `N = 2.646` figura como premisa/proyección del escenario narrativo
- **AND** ningún pasaje presenta `N` como un universo medido

#### Scenario: Valores de referencia derivados y rotulados

- **WHEN** se leen los tres valores de referencia de `N`
- **THEN** figuran en la oración del cuerpo (no solo en un anexo) como derivados y condicionales, con `N` como premisa del escenario
- **AND** `B_r` para `N = 1.000`, `5.000` y `10.000` es `+7,1`, `+35,4` y `+70,7` horas-persona por trimestre (una decimal)

#### Scenario: Cifra central y cuerpo sin tabla inalterados

- **WHEN** se compara el `08-discusion.tex` antes y después del change
- **THEN** `+18,7` horas-persona por trimestre y todos los números canónicos quedan idénticos
- **AND** no se introduce ninguna tabla nueva en el cuerpo de `subsec:balance-neto`
