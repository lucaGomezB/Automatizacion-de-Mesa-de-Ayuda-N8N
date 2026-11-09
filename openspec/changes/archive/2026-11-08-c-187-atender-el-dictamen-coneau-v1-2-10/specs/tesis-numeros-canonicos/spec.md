## ADDED Requirements

### Requirement: Unidad del denominador de la exactitud agregada del brazo manual

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar la exactitud
agregada del brazo manual de la campaña complementaria con su unidad real: estricta
`0,8278` = 125 de 151 derivaciones de operador (80 de `O1` y 71 de `O2`) sobre 138 casos
unicos, 13 de ellos con doble cobertura, y laxa `0,8609` = 130 de 151. El memo MUST NOT
rotularlas como "125/138" ni "130/138". El memo SHALL anotar que
`evaluation/data/campana/analisis/resultados.json` arrastra el rotulo "138" sin editar ese
artefacto (salida del analisis regenerable). Los valores numericos, sus intervalos
bootstrap por caso, `e_man = 0,1722` y los `a*` derivados MUST NOT cambiar, porque la
definicion por derivacion se conserva.

#### Scenario: Denominador por derivacion en el memo

- **WHEN** se lee la fila de la exactitud agregada del brazo manual en la seccion (a) del memo
- **THEN** figura 125/151 derivaciones sobre 138 casos unicos y 130/151 para la laxa
- **AND** no figura "125/138" ni "130/138"

#### Scenario: Valores numericos intactos

- **WHEN** se comparan los valores de la fila antes y despues del change
- **THEN** `0,8278`, `0,8609`, sus intervalos bootstrap, `e_man = 0,1722` y los `a*` coinciden
- **AND** solo cambia el rotulo del denominador y la nota sobre `resultados.json`

### Requirement: Registro de la proporcion de intervenciones con cambio de derivacion

El memo SHALL registrar como entrada nueva de la campaña complementaria la proporcion de
intervenciones que cambiaron la derivacion (25 de 200 = 0,125) con su intervalo de Wilson
al 95 % ([0,086; 0,178], recomputado con la misma funcion de Wilson del analisis), su
procedencia (`evaluation/data/campana/intervenciones.csv`, `cambio_sector = true`) y su
veredicto frente a la cota de 0,15 ("no concluyente"), y SHALL registrar el desglose de
las 147 intervenciones por canal (66 de 66 correo, 81 de 81 telefonia, 0 de 53
formulario web) con su fuente (sidecars de la corrida). La entrada MUST NOT reemplazar la
tasa bruta (147/200) ni ningun valor canonico vigente.

#### Scenario: Entrada nueva registrada

- **WHEN** se lee la seccion de la campaña complementaria del memo
- **THEN** figura 25/200 = 0,125 con IC de Wilson [0,086; 0,178], su procedencia y el veredicto "no concluyente"
- **AND** figura el desglose por canal de las 147 intervenciones con su fuente

#### Scenario: Tasa bruta conservada

- **WHEN** se compara la entrada de la tasa bruta de intervencion antes y despues del change
- **THEN** 147/200 y su IC [0,6698; 0,7913] se conservan
- **AND** la entrada nueva no figura como reemplazo
