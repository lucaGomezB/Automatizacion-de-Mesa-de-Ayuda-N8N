## ADDED Requirements

### Requirement: Kappa de Fleiss y matriz de acuerdo por pares para cinco etiquetadores

El framework SHALL calcular, en `evaluation/kappa.py`, un kappa de Fleiss no ponderado sobre la
etiqueta primaria `sector_etiquetado` de las filas con `tarea = doble_etiquetado` de cinco
etiquetadores, con las 5 clases de `SECTORES_CANONICOS`, para estimar el acuerdo multi-evaluador de
la referencia por mayoria (ARB-009 de `discordant-arbitration`). El calculo SHALL aceptar tres o mas
etiquetadores y SHALL soportar cantidad variable de etiquetadores por caso cuando la cobertura no sea
completa, informando por caso la cantidad de etiquetadores. El resultado MUST incluir `P_bar`, `P_e`,
kappa, el numero de casos y de etiquetadores por caso, el rotulo de Landis y Koch del valor puntual y
su IC (asintotico declarado o bootstrap percentil por casos con `SEMILLA_BOOTSTRAP` y
`REMUESTREOS_BOOTSTRAP` de `evaluation/metrics.py`). El framework SHALL ofrecer ademas una matriz de
acuerdo por pares que calcule el kappa de Cohen de cada par de etiquetadores reutilizando
`kappa_cohen`, sin reimplementarlo. Sin varianza entre etiquetadores en todos los casos (`P_e = 1`),
el kappa MUST declararse no estimable. El resultado MUST declarar que este kappa estima la fiabilidad
entre los cinco etiquetadores y no el acuerdo del clasificador contra la referencia. La reutilizacion
SHALL respetar los helpers de bootstrap de `evaluation/metrics.py`, sin reimplementarlos.

#### Scenario: Oraculo de kappa de Fleiss

- **WHEN** se calcula el kappa de Fleiss sobre una matriz de conteos conocida con varios etiquetadores por caso
- **THEN** devuelve `P_bar`, `P_e` y kappa con tolerancia de 1e-6 respecto del valor del oraculo
- **AND** la salida incluye el rotulo de Landis y Koch y su IC

#### Scenario: Cobertura variable por caso

- **WHEN** algunos casos tienen cinco etiquetadores y otros tienen menos
- **THEN** el kappa se calcula con la cantidad efectiva por caso y la cantidad por caso se informa
- **AND** no se exige cobertura completa ni se imputan etiquetas faltantes

#### Scenario: Matriz de acuerdo por pares

- **WHEN** se solicita la matriz del kappa de Cohen por par de etiquetadores
- **THEN** cada par figura con su kappa de Cohen calculado por `kappa_cohen`
- **AND** `kappa_cohen` no se reimplementa

#### Scenario: Sin varianza se declara no estimable

- **WHEN** todos los etiquetadores coinciden en todos los casos de modo que `P_e = 1`
- **THEN** el kappa se declara no estimable y no se devuelve valor numerico

#### Scenario: Alcance declarado

- **WHEN** se lee la salida del kappa de Fleiss
- **THEN** declara que estima la fiabilidad entre los cinco etiquetadores
- **AND** no se presenta como acuerdo del clasificador contra la referencia

## MODIFIED Requirements

### Requirement: Kappa de Cohen entre los etiquetadores nuevos con intervalos asintótico y bootstrap

El framework SHALL calcular, en `evaluation/kappa.py`, el coeficiente kappa de Cohen no
ponderado sobre la etiqueta primaria `sector_etiquetado` de las filas con
`tarea = doble_etiquetado` de la planilla de etiquetado, con las 5 clases de
`SECTORES_CANONICOS`. El cálculo MUST exigir exactamente dos `id_etiquetador` distintos, cada
uno con una etiqueta por caso, y MUST fallar con un error accionable que nombre los alias
encontrados en cualquier otro caso; el kappa de Fleiss para tres o más etiquetadores se ofrece en
su propio requisito y la salida de este cálculo MUST declarar que exige exactamente dos
etiquetadores y remitir al requisito de Fleiss. El resultado MUST incluir κ, p_o, p_e,
PABAK = (5·p_o − 1)/4, n, el IC asintótico calculado con la varianza bajo H1 de Fleiss, Cohen
y Everitt (1969), Var(κ) = [Σ_i p_ii (1 − (p_i. + p_.i)(1 − κ))² + (1 − κ)² Σ_{i≠j} p_ij
(p_.i + p_j.)² − (κ − p_e (1 − κ))²] / (n (1 − p_e)²), con límites recortados a [−1, 1], y el
IC bootstrap percentil 2,5 y 97,5 por casos con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP`
de `evaluation/metrics.py`. Las remuestras con p_e = 1 MUST descartarse y contarse; si superan
el 5 % de los remuestreos, el IC bootstrap MUST declararse no computable con el conteo. La
salida MUST incluir el rótulo de Landis y Koch derivado del valor puntual y la nota de que el
rótulo del IC puede abarcar dos categorías, y MUST declarar que el kappa es de los
etiquetadores nuevos y no un intervalo del kappa 0,87 original.

#### Scenario: Oráculo de kappa y error estándar asintótico

- **WHEN** se calcula el kappa sobre la matriz de acuerdo [[20, 5, 0], [3, 15, 2], [0, 4, 11]] (n = 60) inmersa en las 5 clases canónicas
- **THEN** κ = 0,642553 y el error estándar asintótico es 0,083594 con tolerancia de 1e-6
- **AND** p_o = 0,766667, p_e = 0,347222, PABAK = 0,708333 y el IC asintótico del 95 % es [0,478711; 0,806395]
- **AND** el rótulo de Landis y Koch es "sustancial" y la salida señala que el IC abarca "moderado" y "sustancial"

#### Scenario: Diagonal perfecta

- **WHEN** ambos etiquetadores coinciden en todos los casos y usan más de un sector
- **THEN** κ = 1 y el IC asintótico es [1, 1]

#### Scenario: Acuerdo esperado igual a uno declara no estimable

- **WHEN** ambos etiquetadores asignan el mismo único sector a todos los casos, de modo que p_e = 1
- **THEN** el resultado declara el kappa no estimable y no devuelve valor numérico ni intervalo

#### Scenario: Límites recortados al rango válido

- **WHEN** κ ± z·SE excede 1 o queda por debajo de −1
- **THEN** el límite correspondiente del IC asintótico se recorta a 1 o a −1

#### Scenario: Bootstrap reproducible

- **WHEN** se recalcula el IC bootstrap con los mismos datos
- **THEN** el intervalo es idéntico y se obtuvo con `SEMILLA_BOOTSTRAP` y `REMUESTREOS_BOOTSTRAP` importados de `evaluation/metrics.py`

#### Scenario: Remuestras degeneradas por encima del 5 %

- **WHEN** más del 5 % de las remuestras bootstrap tienen p_e = 1
- **THEN** el resultado declara "IC bootstrap no computable" con el conteo de remuestras degeneradas y no emite intervalo bootstrap

#### Scenario: Cantidad de etiquetadores distinta de dos

- **WHEN** las filas de `tarea = doble_etiquetado` tienen uno o más de dos `id_etiquetador` distintos
- **THEN** el cálculo falla con un error que nombra los alias encontrados y no reporta kappa
- **AND** la salida remite al requisito de kappa de Fleiss
