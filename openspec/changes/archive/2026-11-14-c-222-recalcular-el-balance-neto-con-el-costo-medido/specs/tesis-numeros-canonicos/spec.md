## ADDED Requirements

### Requirement: Registro aditivo del balance neto recalculado con el costo medido

El memo canónico `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL incorporar una sección nueva y aditiva, posterior a la última sección vigente, sin renumerar ni alterar las anteriores. La sección SHALL registrar, como mínimo: los insumos del balance (`N = 2.646`, `dt = 43,82 s`, `e_aut` y `e_man` medidas contra la referencia común de la sección 3.21 y `c = 69,51 s` con IC 95 % `[33,42; 106,56] s` de la sección 3.31); las fórmulas de `B` y de `a*`; `B` y `a*` recalculados con el `c` medido; el método de propagación de la incertidumbre y el intervalo resultante; y el estado de cada valor. Cada valor SHALL llevar su archivo y ruta de origen, o el comando que lo reproduce, y un estado en `{vigente, condicional, retirado}`. La sección SHALL declarar de forma explícita que el supuesto «10 a 15 minutos» se reemplaza como insumo central y que la grilla de 5, 10 y 15 minutos se conserva solo como sensibilidad del supuesto superado. La sección SHALL remitir desde la sección 3.21 mediante líneas agregadas, sin reescribirla. MUST NOT modificar ningún valor ni estado de las secciones 3.1 a 3.32.

#### Scenario: Sección aditiva con el primer número libre

- **WHEN** se aplica el change y se relee el índice del memo
- **THEN** la sección nueva ocupa el primer número libre posterior a la última sección vigente
- **AND** ninguna sección previa se renumera ni se reescribe

#### Scenario: Recomputo con el costo medido y su incertidumbre

- **WHEN** se lee el balance recalculado
- **THEN** `B` y `a*` figuran con el `c` medido `69,51 s`, su intervalo `[33,42; 106,56] s` y el método de propagación declarado
- **AND** el intervalo de `B` se informa junto con el intervalo condicional con `c` fijo

#### Scenario: Reemplazo explícito del supuesto previo

- **WHEN** se busca «10 a 15 minutos» como insumo del balance
- **THEN** la sección declara que el supuesto fue reemplazado por el `c` medido
- **AND** la grilla de 5, 10 y 15 minutos queda rotulada como sensibilidad superada, con sus cifras conservadas

#### Scenario: Valores previos intactos

- **WHEN** se comparan las secciones 3.1 a 3.32 antes y después del change
- **THEN** cada valor conserva su cifra y su estado
- **AND** solo se agrega la sección nueva y la remisión desde la sección 3.21