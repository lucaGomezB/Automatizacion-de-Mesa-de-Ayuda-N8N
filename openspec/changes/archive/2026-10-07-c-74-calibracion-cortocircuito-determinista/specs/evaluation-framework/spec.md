# Delta for evaluation-framework

## ADDED Requirements

### Requirement: Provenance de los datos de calibracion (anti data leakage)

El sistema SHALL separar estrictamente los datos usados para ajustar o calibrar el score de seleccion del cortocircuito de los datos usados para reportar metricas. El corpus de evaluacion (`data/corpus_evaluacion_pseudonimizado.json`) SHALL considerarse el conjunto de test reportado y MUST NOT usarse para derivar, ajustar o seleccionar el score ni el punto de operacion. La estrategia de procedencia SHALL adoptar una de las siguientes y documentarla con su tradeoff: (i) un conjunto held-out etiquetado nuevo, (ii) un split dev/test pre-registrado del corpus, reportando sobre la particion de test intocada, o (iii) cross-fitting/conformal, donde la calibracion se ajusta en folds que excluyen el fold evaluado y se reporta out-of-fold. El sistema SHALL hacer verificable que la entrada del ajuste no es el test reportado, de modo que las metricas reportadas no queden invalidadas por fuga.

#### Scenario: El ajuste no usa el test reportado

- **WHEN** se ajusta el score o se elige el punto de operacion
- **THEN** el corpus de evaluacion usado como test set reportado no participa del ajuste ni de la seleccion

#### Scenario: Las metricas se reportan sobre datos intocados

- **WHEN** se reportan las metricas del cortocircuito calibrado
- **THEN** se calculan sobre una particion que no fue usada para ajustar el score, o sobre predicciones out-of-fold

#### Scenario: La procedencia queda documentada

- **WHEN** se declara la estrategia de calibracion
- **THEN** queda documentada la procedencia de los datos (held-out, split pre-registrado o cross-fitting) junto con su tradeoff
