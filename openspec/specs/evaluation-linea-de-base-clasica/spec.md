# evaluation-linea-de-base-clasica Specification

## Purpose
Define un clasificador supervisado clasico de texto, reproducible y totalmente offline, como
linea de base metodologica contra la cual se compara el clasificador hibrido de la tesis. El
desarrollo entrega el modulo y sus pruebas; la ejecucion de la medicion es una change aparte.

## Requirements

### Requirement: LB-001 — Entrenamiento y evaluacion en conjuntos disjuntos

El clasificador de linea de base SHALL entrenarse EXCLUSIVAMENTE con los `200` casos in-sample
del corpus de ajuste y SHALL predecir los casos fuera de muestra con referencia por consenso
`E3`/`E4` (`103` casos). El conjunto de prueba MUST NOT usarse para entrenar, ajustar
hiperparametros ni seleccionar el modelo. La evaluacion SHALL realizarse sobre el mismo
conjunto efectivo de `103` casos que usan c-191 y c-205, y SHALL declarar que los `47` casos
discordantes de la muestra primaria de `150` quedan excluidos porque no tienen referencia de
consenso.

#### Scenario: Entrenamiento con los 200 casos y prueba con los 103 casos

- **WHEN** se construye y ejecuta la linea de base
- **THEN** el modelo se ajusta solo con los `200` casos in-sample
- **AND** las predicciones se emiten para los `103` casos fuera de muestra con referencia
- **AND** el documento declara que los `47` discordantes no se usan y que el conjunto de prueba no entrena

#### Scenario: Sin fuga del conjunto de prueba

- **WHEN** se inspecciona el flujo de entrenamiento
- **THEN** ninguna descripcion, etiqueta ni metrica de los `103` casos de prueba participa del ajuste
- **AND** el documento reporta el `n` de entrenamiento (`200`) y el `n` de prueba (`103`) por separado

### Requirement: LB-002 — Metricas comparables con el hibrido

La linea de base SHALL reportar, sobre los `103` casos de prueba, la exactitud estricta, la
exactitud laxa, la macro-F1 sobre las cinco clases canonicas, la *balanced accuracy* y la F1
por clase con su soporte. Las metricas SHALL derivarse de las funciones puras de
`evaluation/metrics.py` (`matriz_confusion`, `precision_por_clase`, `sensibilidad_por_clase`,
`f1_por_clase`, `soporte_por_clase`, `f1_macro`, `aciertos_estrictos`, `aciertos_laxos`) para
que sean comparables con las cifras de c-205. La exactitud laxa SHALL contar como acierto toda
prediccion que pertenezca al conjunto de verdad del caso (sector asignado mas sectores
adicionales). La macro-F1 SHALL incluir las cinco clases, incluidas las de soporte cero.

#### Scenario: Exactitudes estricta y laxa reportadas

- **WHEN** se leen las metricas de la linea de base
- **THEN** figuran la exactitud estricta y la exactitud laxa con sus aciertos y su `n`
- **AND** la exactitud laxa usa el conjunto de verdad del caso, no solo el sector asignado

#### Scenario: Macro-F1, balanced accuracy y F1 por clase con soporte

- **WHEN** se leen las metricas por clase
- **THEN** figuran las cinco clases con precision, sensibilidad, F1 y soporte
- **AND** figuran la macro-F1 como media de las cinco F1 y la *balanced accuracy* como media de las sensibilidades por clase
- **AND** el soporte por clase suma `103`

### Requirement: LB-003 — Reproducibilidad deterministica

El clasificador SHALL usar una semilla fija y MUST NOT depender de aleatoriedad no controlada.
Dos ejecuciones consecutivas con las mismas entradas SHALL producir artefactos identicos byte a
byte. El documento SHALL registrar el SHA-256 de cada artefacto de salida y de cada entrada
leida. La corrida SHALL imprimir el SHA-256 de cada salida.

#### Scenario: Dos corridas identicas

- **WHEN** se ejecuta la linea de base dos veces seguidas
- **THEN** los artefactos de salida son identicos byte a byte
- **AND** los SHA-256 de salida coinciden entre corridas

#### Scenario: Entradas y salidas con huella

- **WHEN** se lee el documento de resultados
- **THEN** figuran los SHA-256 de las entradas leidas y de las salidas escritas
- **AND** la corrida imprime los SHA-256 de las salidas

### Requirement: LB-004 — Ejecucion offline y de solo lectura

La linea de base MUST NOT invocar la red, Gemini, ninguna API paga ni el clasificador de
produccion. MUST NOT modificar `App/`, `n8n/`, los corpus congelados, las predicciones
versionadas ni ningun valor canonico. La lectura del corpus SHALL hacerse sin reescribir el
archivo original. El script SHALL escribir solo sus propios artefactos de salida.

#### Scenario: Sin red ni servicios pagos

- **WHEN** se inspecciona el modulo y su ejecucion
- **THEN** no importa ni invoca clientes de red, Gemini ni APIs pagas
- **AND** la corrida completa termina sin conexion externa

#### Scenario: Sin escritura sobre los artefactos congelados

- **WHEN** se ejecuta la linea de base
- **THEN** el corpus, las predicciones y el clasificador de produccion quedan intactos
- **AND** solo se escriben los artefactos propios de la linea de base

### Requirement: LB-005 — Documento de resultados autosuficiente

La linea de base SHALL producir un documento JSON con la version del modelo, la semilla, los
hiperparametros declarados, los `n` de entrenamiento y prueba, las metricas globales y por
clase, la matriz de confusion `5x5`, la distribucion de predicciones y los hashes de entradas y
salidas. El documento SHALL declarar que las cifras son ADITIVAS y que no reemplazan ningun
numero canonico de la tesis.

#### Scenario: Documento con procedencia y advertencia aditiva

- **WHEN** se lee el documento de resultados
- **THEN** figuran version, semilla, hiperparametros, `n` de entrenamiento y prueba, metricas, matriz y hashes
- **AND** se declara que las cifras son aditivas y no reemplazan numeros canonicos

### Requirement: LB-006 — Pruebas TDD del modulo

El desarrollo SHALL entregar pruebas automatizadas en `evaluation/tests/` que cubran: la
estructura del documento, las metricas sobre entradas sinteticas, el soporte por clase, el
determinismo byte a byte y la ausencia de dependencias de red, Gemini o API paga. Las pruebas
SHALL escribirse antes de la implementacion (RED) y SHALL pasar despues de la implementacion
(GREEN), con triangulacion sobre entradas distintas.

#### Scenario: Pruebas en RED y GREEN

- **WHEN** se corre la suite de pruebas del modulo
- **THEN** las pruebas fallan antes de existir la implementacion y pasan despues
- **AND** la triangulacion cubre al menos dos entradas con resultados esperados distintos

#### Scenario: Cobertura de determinismo y offline

- **WHEN** se corre la suite de pruebas
- **THEN** una prueba compara dos corridas byte a byte y verifica los SHA-256
- **AND** una prueba verifica que el modulo no importa clientes de red, Gemini ni APIs pagas
