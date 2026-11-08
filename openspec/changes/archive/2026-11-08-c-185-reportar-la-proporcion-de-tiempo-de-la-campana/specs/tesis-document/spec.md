## MODIFIED Requirements

### Requirement: Reporte de la tasa de intervencion humana de la campaña de medicion

La tesis SHALL reportar en el marco metodologico (4.6 y 4.7) y en
`subsec:reduccion-intervencion` la `tasa_intervencion_humana` de la campaña de
medicion (c-167): proporcion de casos con `n` e intervalo de Wilson al 95 %, desglose
por origen (`gate`, `muestreo`, `rederivacion`, `completado_manual`) y por cambio de
sector, contraste con la cota `0,15` con la estimacion y ambos limites que entregue
c-167 (limite superior menor que `0,15`: compatible; estimacion mayor o igual que
`0,15`: refutada; estimacion menor que `0,15` con limite superior mayor o igual:
no concluyente) y la segunda dimension rotulada de la variable, la proporcion del
tiempo dedicado a tareas manuales sobre el tiempo del proceso. Cuando la cobertura de
las consignas de inicio y fin sea mayor o igual que el 80 %, la tesis SHALL reportar la
proporcion del tiempo con su estimacion puntual, su intervalo bootstrap del cociente
(`B = 2000`, semilla `20261021`), la cobertura observada y los tamanos que la
sostienen, y SHALL declarar la limitacion del denominador (tiempo de registro
automatizado mas duracion de la intervencion, no el tiempo total de atencion); cuando
la cobertura sea inferior al 80 %, SHALL declararla "no estimable" con la cobertura
observada. El titulo de `subsec:reduccion-intervencion` SHALL ser coherente con el estado
de la sub-hipotesis. Si el export no cubre la corrida, SHALL declarar "no contrastada:
registro incompleto".

#### Scenario: Tasa de intervencion reportada

- **WHEN** el export cubre la corrida y se lee `subsec:reduccion-intervencion`
- **THEN** se reporta la proporcion de casos con su `n`, su estimacion, ambos limites de Wilson, su desglose por origen y por cambio de sector y el veredicto frente a `0,15` (compatible, refutada o no concluyente)
- **AND** la proporcion del tiempo figura con su intervalo bootstrap o como "no estimable" con la cobertura observada

#### Scenario: Proporcion de tiempo reportada con su valor

- **WHEN** la cobertura de las consignas de inicio y fin es mayor o igual que el 80 % y se lee `subsec:reduccion-intervencion`
- **THEN** la proporcion del tiempo dedicado a tareas manuales se reporta con su estimacion puntual `0,5307`, su intervalo bootstrap del cociente `[0,4407; 0,6111]` (`B = 2000`, semilla `20261021`) y la cobertura observada `0,9388`
- **AND** se declaran los tamanos que la sostienen (147 casos con intervencion y 138 con duracion completa) y la limitacion del denominador (tiempo de registro automatizado mas duracion de la intervencion, no el tiempo total de atencion)
- **AND** el valor figura en `docs/Tesis/Correcciones/numeros-canonicos.md` (Seccion 3.14) con estado vigente, no reemplaza ningun valor canonico y aparece en `07-resultados.tex` una sola vez

#### Scenario: Anuncio metodologico alineado con el denominador medido

- **WHEN** se lee el parrafo de metricas del marco metodologico (`04-marco-metodologico.tex`)
- **THEN** la proporcion del tiempo se anuncia con el denominador efectivamente medido (tiempo de registro automatizado mas duracion de la intervencion) y remite con `\autoref` a `subsec:reduccion-intervencion`
- **AND** no se afirma ningun valor de la proporcion del tiempo en el marco metodologico

#### Scenario: Titulo coherente con el estado

- **WHEN** se inspecciona el titulo de `subsec:reduccion-intervencion` y su entrada en el indice
- **THEN** el titulo no promete una reduccion salvo en el estado "contrastada: compatible"
- **AND** el rotulo `subsec:reduccion-intervencion` se conserva

#### Scenario: Registro incompleto

- **WHEN** el export no cubre la corrida de la campaña de medicion
- **THEN** la subseccion declara "no contrastada: registro incompleto" y no cuantifica la proporcion
- **AND** el estado se propaga identico al resumen, la introduccion, las conclusiones y el memo
