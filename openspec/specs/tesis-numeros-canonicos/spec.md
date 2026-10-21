# tesis-numeros-canonicos Specification

## Purpose
Definir el contrato del memo canónico de números de la tesis: un registro único,
verificable y con procedencia por valor que fija los números y criterios que el
documento puede citar, declara la regla efectiva del gate de revisión humana y
resuelve —o declara explícitamente como no resolubles— las contradicciones
numéricas internas detectadas por el dictamen CONEAU. El memo actúa como Gate 0
antes de que cualquier rama reescriba el texto de la tesis.

## Requirements

### Requirement: Registro canónico con procedencia por valor

El proyecto SHALL mantener el memo `docs/Tesis/Correcciones/numeros-canonicos.md`
como fuente única de verdad numérica de la tesis. Cada valor citable SHALL
registrarse con su procedencia (archivo y línea de origen) y su estado, que SHALL
ser uno de `vigente`, `retirado` o `condicional`. El memo MUST NOT contener ningún
valor sin fuente verificable y MUST distinguir el valor vigente del valor retirado
cuando una corrección reemplace una cifra previa.

#### Scenario: Todo valor tiene fuente y estado

- **WHEN** se recorre la tabla canónica del memo
- **THEN** cada fila declara el valor, el archivo y la línea de origen, y un estado en `{vigente, retirado, condicional}`
- **AND** la línea indicada existe en el archivo referenciado

#### Scenario: Valor retirado no se cita como vigente

- **WHEN** una cifra fue desmentida por la evidencia disponible
- **THEN** el memo la marca como `retirado` y el valor de reemplazo queda como `vigente`
- **AND** las ramas consumidoras no citan el valor retirado como resultado

### Requirement: Regla del gate de intervención humana declarada y trazable

El memo SHALL declarar la regla exacta del gate de revisión humana implementada y
la tabla de contingencia `confianza × etapa × acierto` reconstruida desde
`evaluation/predicciones.json`. El memo SHALL explicar qué confianza asigna la
etapa determinística y por qué no dispara revisión. La proporción de intervención
humana SHALL registrarse como `vigente` únicamente si es derivable de una fuente
primaria permitida; en caso contrario SHALL registrarse como `retirado` y el aporte
operativo SHALL reformularse sin esa cifra.

#### Scenario: Contingencia publicada

- **WHEN** se lee la sección del gate en el memo
- **THEN** figura la tabla de contingencia de confianza contra acierto desagregada por etapa del pipeline
- **AND** se declara que los casos con confianza inferior a 0,70 corresponden a la etapa determinística

#### Scenario: Intervención no derivable se retira

- **WHEN** la proporción de intervención humana no puede derivarse de `evaluation/predicciones.json`, `evaluation/report.md` ni `data/`
- **THEN** el memo registra la cifra como `retirado`
- **AND** el memo reformula el aporte operativo sin esa cifra

#### Scenario: Tramo de alta confianza verificado

- **WHEN** el texto vigente cita un tramo de casos con confianza alta y su número de errores
- **THEN** el memo registra el valor recalculado desde `evaluation/predicciones.json`
- **AND** declara si ese tramo se deduce o no de la tabla de bandas publicada

### Requirement: Criterio único de universo y proyección horaria

El memo SHALL fijar un único criterio para el universo de incidentes (días
calendario o días hábiles), coherente con el origen de la tasa diaria declarada.
El memo SHALL registrar el universo y la proyección horaria resultantes bajo ese
criterio, y SHALL declarar la propagación obligatoria a los capítulos que citan
ambos valores. Las dos lecturas SHALL quedar documentadas, con una marcada como
`vigente` y la otra como `retirado`.

#### Scenario: Criterio único declarado

- **WHEN** se lee la sección del universo en el memo
- **THEN** se declara explícitamente si el universo se computa sobre días calendario o hábiles
- **AND** la tasa diaria usada es coherente con el criterio elegido

#### Scenario: Proyección horaria recalculada y propagada

- **WHEN** se adopta el criterio de días hábiles
- **THEN** el memo registra el universo recalculado y la proyección de horas-persona recalculada con el ahorro medio por incidente
- **AND** declara los archivos de la tesis que deben propagar el valor vigente

### Requirement: Paradigma métrico definido y reproducible

El memo SHALL definir si la tarea se evalúa como monoetiqueta o multietiqueta y
SHALL fijar el set métrico final, distinguiendo las métricas primarias de las
secundarias. El memo SHALL documentar el procedimiento de recálculo desde
`evaluation/predicciones.json` sin re-ejecutar el sistema. Las métricas
multietiqueta SHALL reportarse contra una referencia multietiqueta declarada y
MUST NOT presentarse como equivalentes de la exactitud de etiqueta única.

#### Scenario: Paradigma y set métrico declarados

- **WHEN** se lee la sección de métricas del memo
- **THEN** se declara si la referencia de verdad es monoetiqueta o multietiqueta
- **AND** se listan las métricas primarias y secundarias con su definición

#### Scenario: Recálculo reproducible sin re-ejecutar

- **WHEN** se sigue el procedimiento de recálculo documentado en el memo
- **THEN** las métricas se reproducen desde `evaluation/predicciones.json`
- **AND** no se requiere invocar el clasificador ni servicios externos

### Requirement: Tratamiento de la clase con soporte unitario

El memo SHALL declarar como no estimable toda clase cuya frecuencia en el corpus
sea de un solo caso, y SHALL reportar el efecto de su exclusión sobre la métrica
de umbral. El memo MUST NOT presentar el valor métrico de una clase con n=1 como
evidencia de desempeño del clasificador.

#### Scenario: Clase con n=1 declarada no estimable

- **WHEN** se lee la sección de métricas por clase del memo
- **THEN** la clase con soporte 1 se declara no estimable
- **AND** se reporta el valor de la métrica de umbral con y sin esa clase

### Requirement: Decisiones no resolubles declaradas con decisión editorial

El memo SHALL incluir una sección "Decisiones no resolubles" en la que cada punto
que la evidencia disponible no permita cerrar SHALL declararse de forma explícita,
junto con la decisión editorial adoptada y su condición de reversibilidad.

#### Scenario: Punto no resoluble documentado

- **WHEN** una contradicción numérica no puede reconciliarse con las fuentes permitidas
- **THEN** el memo la declara en "Decisiones no resolubles"
- **AND** registra la decisión editorial adoptada y la condición bajo la cual se revisaría

### Requirement: Gate 0 como prerrequisito de las ramas consumidoras

Este contrato SHALL actuar como Gate 0: ninguna rama que reescriba los capítulos
de la tesis SHALL fijar números nuevos sin citar el valor vigente del memo. Toda
rama consumidora MUST consumir la tabla canónica y MUST NOT redefinir sus valores
por separado.

#### Scenario: Rama consumidora cita el memo

- **WHEN** una rama de corrección reescribe un capítulo que cita números
- **THEN** los valores usados coinciden con el valor vigente del memo
- **AND** toda divergencia se resuelve actualizando el memo, no el capítulo de forma aislada
