## Purpose

Define la particion sin fuga, el entrenamiento de un clasificador supervisado tipo
BERT y el benchmark de modelos abiertos contra el clasificador hibrido, con la
referencia de `206` casos retenida y metricas por clase comparables.

## ADDED Requirements

### Requirement: SCB-001 — Particion disjunta sin fuga con los 206 retenidos

El arnes SHALL construir una particion `train`/`dev`/`test` disjunta sobre el
corpus curado, agrupando por texto casi duplicado (un mismo incidente MUST NOT
caer en dos particiones) y estratificando por sector y por canal. Los `206` casos
de la referencia arbitrada y el corpus de prueba SHALL quedar retenidos: MUST NOT
participar del entrenamiento, del ajuste de hiperparametros ni de la seleccion del
modelo. El conjunto `dev` SHALL usarse solo para parada temprana y seleccion, y
`test` SHALL evaluarse una unica vez. La particion SHALL derivarse de una funcion
pura con prueba sintetica previa a la implementacion.

#### Scenario: Particiones disjuntas

- **WHEN** se construye la particion
- **THEN** la interseccion de textos entre `train`, `dev` y `test` es vacia
- **AND** ningun identificador de los `206` aparece en `train` ni en `dev`

#### Scenario: Sin fuga del conjunto de prueba

- **WHEN** se inspecciona el entrenamiento
- **THEN** ninguna descripcion, etiqueta ni metrica de `test` ni de los `206` participa del ajuste
- **AND** el artefacto reporta el `n` de entrenamiento y el `n` de prueba por separado

### Requirement: SCB-002 — Entrenamiento tipo BERT y benchmark de modelos abiertos

El arnes SHALL entrenar un modelo de clasificacion de secuencia de la familia BERT
(encoder de dominio espanol o multilingue) sobre la particion `train`, con `dev`
para parada temprana. SHALL ademas evaluar modelos abiertos (`Llama 3`, `Mistral`,
`Qwen`) como alternativa, y SHALL comparar cada resultado contra el clasificador
hibrido congelado como base. El arnes SHALL ser reproducible (semilla fija) y MUST
NOT modificar el clasificador de produccion ni el prompt vigente. El entrenamiento
SHALL quedar condicionado a que el corpus alcance el volumen declarado; si no lo
alcanza, el arnes SHALL registrar el bloqueo en lugar de emitir un modelo.

#### Scenario: Entrenamiento reproducible

- **WHEN** se ejecuta el arnes con la misma semilla y el mismo corpus
- **THEN** la particion y las metricas son identicas entre corridas
- **AND** el clasificador de produccion y el prompt vigente no cambian

#### Scenario: Modelos abiertos comparados con el hibrido

- **WHEN** se ejecuta el benchmark
- **THEN** cada modelo abierto se evalua sobre las mismas particiones
- **AND** el resultado se compara contra el hibrido congelado

#### Scenario: Volumen insuficiente

- **WHEN** el corpus no alcanza el volumen declarado
- **THEN** el arnes registra el bloqueo
- **AND** no emite un modelo como si estuviera entrenado

### Requirement: SCB-003 — Metricas por clase, comparacion con el hibrido y no alcanzabilidad sobre los 206

El arnes SHALL reportar exactitud estricta y laxa, macro-F1 y precision,
sensibilidad y F1 por clase con su soporte, reutilizando las funciones puras de
`evaluation/metrics.py`, para que las cifras sean comparables con las del hibrido.
La lectura sobre los `206` casos SHALL presentarse como contraste descriptivo y
SHALL declarar de forma explicita que sobre esa referencia el umbral `0,85` no es
alcanzable. El artefacto MUST NOT presentar el resultado sobre los `206` como una
validacion del clasificador supervisado ni cambiar `0,6893`, el macro-F1 `0,7024`
ni el veredicto del umbral.

#### Scenario: Metricas por clase comparables

- **WHEN** se reporta el resultado del modelo supervisado
- **THEN** figuran exactitud estricta y laxa, macro-F1 y P/R/F1 por clase con soporte
- **AND** las metricas se derivan de las funciones de `evaluation/metrics.py`

#### Scenario: No alcanzabilidad declarada

- **WHEN** se lee el contraste sobre los `206`
- **THEN** se declara que el umbral `0,85` no es alcanzable sobre esa referencia
- **AND** no se presenta como validacion del clasificador supervisado
