## Purpose

Define el protocolo de evaluacion del clasificador supervisado sobre un corpus
fresco de prevalencia natural, con cuotas prefijadas, etiquetado limpio e
independiente y sin exclusiones, para estimar el desempeno de composicion natural.

## ADDED Requirements

### Requirement: NPE-001 — Composicion de prevalencia natural con cuotas prefijadas

El corpus de evaluacion SHALL ser fresco, disjunto del corpus de ajuste y del
corpus curado, y SHALL tener composicion de prevalencia natural con cuotas
prefijadas por canal y por sector antes de observar los datos. El muestreo SHALL
consumirse del diseno de
`c-229-muestreo-probabilistico-del-universo-de-incidentes`; si ese corpus no esta
disponible, la tarea SHALL quedar bloqueada y registrada, sin sustituirlo por un
muestreo de conveniencia. Las cuotas SHALL documentarse con su procedencia.

#### Scenario: Cuotas prefijadas

- **WHEN** se construye el corpus de evaluacion
- **THEN** las cuotas por canal y por sector estan prefijadas antes de observar los datos
- **AND** su procedencia queda documentada

#### Scenario: Dependencia de c-229

- **WHEN** el corpus de `c-229` no esta disponible
- **THEN** la tarea queda bloqueada y registrada
- **AND** no se sustituye por un muestreo de conveniencia

### Requirement: NPE-002 — Etiquetado limpio e independiente y evaluacion sin exclusiones

El etiquetado del corpus de prevalencia natural SHALL realizarse con etiquetadores
independientes del corpus de ajuste, con la referencia derivada por consenso o
regla declarada, y SHALL registrarse su fiabilidad inter-etiquetador. La
evaluacion SHALL incluir todos los casos, sin excluir por discordancia ni por
canal, y MUST NOT usar el conjunto de evaluacion para entrenar ni ajustar el
modelo.

#### Scenario: Etiquetado independiente con fiabilidad

- **WHEN** se etiqueta el corpus de evaluacion
- **THEN** los etiquetadores son independientes del corpus de ajuste
- **AND** se registra la fiabilidad inter-etiquetador y la regla de referencia

#### Scenario: Evaluacion sin exclusiones

- **WHEN** se evalua el clasificador sobre el corpus de prevalencia natural
- **THEN** todos los casos se incluyen, sin exclusion por discordancia ni por canal
- **AND** el conjunto de evaluacion no participa del entrenamiento

### Requirement: NPE-003 — Intervalos sobre el universo y reporte por clase

La evaluacion SHALL reportar la exactitud estricta y laxa, el macro-F1 y las
metricas por clase con soporte, e intervalos de confianza estimados sobre el
universo del estudio sin excluir casos, reutilizando las funciones puras de
`evaluation/stats.py` y `evaluation/metrics.py`. El reporte SHALL distinguir la
lectura del clasificador supervisado de la del hibrido congelado sobre el mismo
corpus y SHALL rotular cada comparacion. La composicion del corpus SHALL
declararse explicitamente como de prevalencia natural.

#### Scenario: Intervalos sobre el universo

- **WHEN** se reporta el desempeno sobre el corpus de prevalencia natural
- **THEN** los intervalos se estiman sobre el universo sin excluir casos
- **AND** figuran exactitud estricta y laxa, macro-F1 y metricas por clase con soporte

#### Scenario: Comparacion rotulada con el hibrido

- **WHEN** se compara el clasificador supervisado con el hibrido
- **THEN** cada lectura se rotula con su clasificador y su corpus
- **AND** la composicion de prevalencia natural se declara explicitamente
