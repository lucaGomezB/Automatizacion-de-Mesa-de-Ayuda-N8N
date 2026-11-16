## Purpose

Define el consumo del corpus probabilistico acreditado de `c-229`, con la
referencia por mayoria de `c-230`, como unico conjunto de prueba retenido admisible
para evaluar el clasificador supervisado, sin exclusiones y con intervalos sobre el
universo.

## ADDED Requirements

### Requirement: NPE-001 — Corpus probabilistico acreditado como conjunto de prueba

El conjunto de evaluacion del clasificador supervisado SHALL ser el corpus
probabilistico acreditado que entrega
`c-229-muestreo-probabilistico-del-universo-de-incidentes`, con cuotas prefijadas
por canal y por sector antes de observar los datos, disjunto del corpus de 200
casos y del corpus curado. Antes de usarlo, el change SHALL verificar que constan
cerradas sus compuertas de procedencia y etica y legal. Si ese corpus no esta
disponible o sus compuertas estan abiertas, la tarea SHALL quedar bloqueada y
registrada, y MUST NOT sustituirse por un muestreo de conveniencia ni por material
retirado por `c-235`.

#### Scenario: Compuertas verificadas antes de usar el corpus

- **WHEN** se consume el corpus de `c-229`
- **THEN** constan cerradas su compuerta de procedencia y su compuerta etica y legal
- **AND** las cuotas por canal y por sector estan prefijadas y documentadas

#### Scenario: Dependencia de c-229

- **WHEN** el corpus de `c-229` no esta disponible o tiene compuertas abiertas
- **THEN** la tarea queda bloqueada y registrada
- **AND** no se sustituye por un muestreo de conveniencia ni por material retirado

### Requirement: NPE-002 — Referencia por mayoria y evaluacion sin exclusiones

La referencia del corpus de evaluacion SHALL derivarse con el protocolo de mayoria
y las funciones de mayoria y kappa de Fleiss que entrega
`c-230-referencia-por-mayoria-con-etiquetadores-independientes`, con la fiabilidad
multi-evaluador registrada. La evaluacion SHALL incluir todos los casos, sin
excluir por discordancia ni por canal, y MUST NOT usar el conjunto de evaluacion
para entrenar ni ajustar el modelo.

#### Scenario: Referencia por mayoria con fiabilidad

- **WHEN** se fija la referencia del corpus de evaluacion
- **THEN** proviene del protocolo de mayoria de `c-230`
- **AND** se registra la fiabilidad multi-evaluador

#### Scenario: Evaluacion sin exclusiones

- **WHEN** se evalua el clasificador sobre el corpus acreditado
- **THEN** todos los casos se incluyen, sin exclusion por discordancia ni por canal
- **AND** el conjunto de evaluacion no participa del entrenamiento

### Requirement: NPE-003 — Intervalos sobre el universo y reporte por clase

La evaluacion SHALL reportar la exactitud estricta y laxa, el macro-F1 y las
metricas por clase con soporte, e intervalos de confianza referidos al universo
con el estimador de `c-229`, reutilizando `evaluation/metrics.py` y
`evaluation/stats.py`. El reporte SHALL distinguir la lectura del clasificador
supervisado de la del hibrido sobre el mismo corpus y SHALL rotular cada
comparacion con su clasificador y su corpus.

#### Scenario: Intervalos sobre el universo

- **WHEN** se reporta el desempeno sobre el corpus acreditado
- **THEN** los intervalos se estiman sobre el universo sin excluir casos
- **AND** figuran exactitud estricta y laxa, macro-F1 y metricas por clase con soporte

#### Scenario: Comparacion rotulada con el hibrido

- **WHEN** se compara el clasificador supervisado con el hibrido
- **THEN** cada lectura se rotula con su clasificador y su corpus
