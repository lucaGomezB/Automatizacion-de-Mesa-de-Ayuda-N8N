## MODIFIED Requirements

### Requirement: Declaración del estado de la hipótesis principal

El resumen, la discusión y las conclusiones SHALL declarar el estado de la
hipótesis principal como parcialmente confirmada y parcialmente refutada: se
confirma en la reducción del tiempo de registro y se refuta en el umbral de
clasificación (`73,5 %` de exactitud y macro-F1 `0,5207`, por debajo de `85 %` y
`0,85`). El resumen MUST NOT permitir inferir una confirmación plena de la
hipótesis. La declaración SHALL distinguir las sub-hipótesis de tiempo,
intervención humana y exactitud o F1. La sub-hipótesis de intervención humana
SHALL declararse **no medida** con la evidencia disponible, de forma coherente con
la retirada del `9,5 %` (c-107); el documento MUST NOT reintroducir esa cifra ni
presentarla como resultado. Las conclusiones SHALL declarar el estado por
sub-hipótesis: confirmada en tiempo, refutada en clasificación e intervención
humana no medida.

#### Scenario: Estado parcial declarado en el resumen

- **WHEN** se lee el resumen en español y el abstract
- **THEN** se declara que la hipótesis principal se confirma en tiempo y se refuta en clasificación
- **AND** no se presenta el umbral de clasificación como alcanzado

#### Scenario: Estado parcial declarado en discusión y conclusiones

- **WHEN** se leen la discusión y las conclusiones
- **THEN** el estado de la hipótesis principal se declara parcialmente confirmado y parcialmente refutado
- **AND** la refutación se ancla en las métricas de clasificación reportadas

#### Scenario: Sub-hipótesis de intervención humana declarada no medida

- **WHEN** se lee el estado de la hipótesis principal en el resumen y las conclusiones
- **THEN** la sub-hipótesis de intervención humana se declara no medida con la evidencia disponible
- **AND** no se reporta el `9,5 %` de intervención humana como resultado vigente

#### Scenario: Estado por sub-hipótesis en las conclusiones

- **WHEN** se leen las conclusiones
- **THEN** se distingue explícitamente la sub-hipótesis confirmada (tiempo), la refutada (exactitud/F1) y la no medida (intervención humana)
- **AND** no se declara la hipótesis principal confirmada o refutada como bloque

## ADDED Requirements

### Requirement: Desdoblamiento de la hipótesis principal en sub-hipótesis contrastables

La introducción (`01-introduccion.tex`, §Hipótesis de trabajo) SHALL formular la
hipótesis principal desdoblada en tres sub-hipótesis contrastables: (a) tiempo de
registro, (b) proporción de intervención humana y (c) exactitud o F1 macro. Cada
sub-hipótesis SHALL enunciar su propio contraste y su criterio de falsación
explícito. El contraste de la sub-hipótesis temporal SHALL ser el contraste no
paramétrico `H0`/`H1` sobre las medianas del tiempo de registro. El de exactitud o
F1 SHALL formularse como umbral de desempeño verificado contra la exactitud
observada y su intervalo de confianza de Wilson, sin invocar la zona de rechazo
del contraste de tiempos. El documento MUST NOT presentar la hipótesis principal
como una conjunción indivisible que se confirme o refute como bloque.

#### Scenario: Tres sub-hipótesis con contraste propio

- **WHEN** se lee la subsección de hipótesis de trabajo en `01-introduccion.tex`
- **THEN** se distinguen tres sub-hipótesis: tiempo, intervención humana y exactitud/F1
- **AND** cada una enuncia su propio contraste

#### Scenario: Criterio de falsación explícito por sub-hipótesis

- **WHEN** se lee cada sub-hipótesis
- **THEN** declara la condición que la falsaría
- **AND** la sub-hipótesis de exactitud/F1 usa el umbral `85 %`/`0,85` como criterio de desempeño verificado contra el intervalo de confianza, no como zona de rechazo

#### Scenario: Sin conjunción indivisible

- **WHEN** se lee la formulación de la hipótesis principal
- **THEN** no se enuncia como una única conjunción de mecanismo y umbral de desempeño
- **AND** no se declara confirmada o refutada en bloque

### Requirement: Reformulación del objetivo general como evaluación de viabilidad y desempeño

El objetivo general (`01-introduccion.tex`, §Objetivo general) SHALL formularse en
términos de evaluar la viabilidad y el desempeño de la automatización del registro
inicial de incidentes, y SHALL presentar el desarrollo e implementación del sistema
como el medio para esa evaluación, no como el objetivo. El documento MUST NOT
formular el objetivo general en clave exclusiva de desarrollo ("desarrollar e
implementar").

#### Scenario: Objetivo general en clave de evaluación

- **WHEN** se lee el objetivo general en `01-introduccion.tex`
- **THEN** se enuncia en términos de evaluar viabilidad y desempeño
- **AND** no se enuncia como "desarrollar e implementar"

#### Scenario: Desarrollo como medio

- **WHEN** se lee la relación entre el objetivo y la construcción del sistema
- **THEN** el desarrollo y la implementación se presentan como medio para la evaluación
- **AND** no como el objetivo declarado

### Requirement: Separación entre la implementación y el umbral de desempeño del segundo objetivo

El segundo objetivo específico (`01-introduccion.tex`, §Objetivos específicos)
SHALL separar la acción de implementar el clasificador automático del umbral de
desempeño (`exactitud ≥ 85 %`, `F1 macro ≥ 0,85`), que SHALL presentarse como
criterio de éxito contingente verificable contra el resultado observado y su
intervalo de confianza, no como parte constitutiva del objetivo. El documento
MUST NOT enunciar el umbral como una meta que el objetivo incluya por definición.

#### Scenario: Acción de implementación separada del umbral

- **WHEN** se lee el segundo objetivo específico
- **THEN** la acción de implementar el clasificador se enuncia separada del umbral de desempeño
- **AND** el umbral no figura como parte definitoria del objetivo

#### Scenario: Umbral como criterio de éxito contingente

- **WHEN** se lee el tratamiento del umbral `85 %`/`0,85`
- **THEN** se presenta como criterio de éxito verificable contra la exactitud observada y su intervalo de confianza
- **AND** su estado no alcanzado se declara en las conclusiones

### Requirement: Quinto objetivo verificable y reproducible

El quinto objetivo específico (`01-introduccion.tex`, §Objetivos específicos)
SHALL reescribirse en clave verificable y reproducible: documentar la arquitectura,
los procedimientos de despliegue y los resultados de modo que una tercera parte
pueda replicarlos. El documento MUST NOT conservar el calificador "exhaustivamente"
ni formulaciones cuyo cumplimiento no admita verificación.

#### Scenario: Sin "exhaustivamente"

- **WHEN** se lee el quinto objetivo específico
- **THEN** no contiene el término "exhaustivamente" ni otro calificador no contrastable
- **AND** su cumplimiento es verificable

#### Scenario: En clave reproducible

- **WHEN** se lee el quinto objetivo específico
- **THEN** se enuncia en términos de reproducibilidad de los artefactos y procedimientos
- **AND** es coherente con el aporte documental descrito en las conclusiones

### Requirement: Objetivo específico de análisis de errores y calibración de la confianza

La introducción SHALL agregar un objetivo específico referido al análisis de los
errores de clasificación y a la calibración de la confianza de las predicciones,
alineado con los aportes del Capítulo de resultados (tipología de errores y bandas
de confianza). El objetivo SHALL ser verificable contra los artefactos del
repositorio.

#### Scenario: Objetivo agregado

- **WHEN** se leen los objetivos específicos
- **THEN** existe uno referido al análisis de errores y a la calibración de la confianza
- **AND** es verificable contra los artefactos del repositorio

#### Scenario: Alineado con el Capítulo de resultados

- **WHEN** se compara el objetivo con los aportes del Capítulo de resultados
- **THEN** se corresponde con la tipología de errores y las bandas de confianza
- **AND** no introduce una línea de trabajo ajena a la evidencia presentada

### Requirement: Tabla de objetivos, cumplimiento y evidencia en las conclusiones

Las conclusiones (`09-conclusiones.tex`) SHALL incluir una tabla que enumere cada
objetivo (general y específicos), su grado de cumplimiento y la evidencia que lo
respalda (sección o métrica). La tabla SHALL declarar el segundo objetivo como no
alcanzado y SHALL ser coherente con el estado declarado de la hipótesis principal.

#### Scenario: Tabla presente

- **WHEN** se leen las conclusiones
- **THEN** se incluye una tabla de objetivos, cumplimiento y evidencia
- **AND** abarca el objetivo general y todos los específicos

#### Scenario: Cumplimiento y evidencia por objetivo

- **WHEN** se lee cada fila de la tabla
- **THEN** declara el grado de cumplimiento y la evidencia (sección o métrica) que lo respalda
- **AND** el segundo objetivo figura como no alcanzado

#### Scenario: Coherencia con el estado de la hipótesis

- **WHEN** se compara la tabla con la declaración del estado de la hipótesis principal
- **THEN** ambos son coherentes (tiempo confirmado, clasificación refutada)
- **AND** no se declara alcanzado el umbral de clasificación
