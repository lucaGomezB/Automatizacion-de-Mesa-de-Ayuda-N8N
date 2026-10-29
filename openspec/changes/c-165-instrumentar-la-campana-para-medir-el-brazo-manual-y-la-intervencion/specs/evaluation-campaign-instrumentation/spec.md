## Purpose

Define el instrumento y el protocolo para medir el brazo manual (exactitud de la clasificacion humana contra la verdad de consenso) y la tasa de intervencion humana real, de modo que la campana de campo sea registrada, ejecutable y verificable.

## ADDED Requirements

### Requirement: ECM-001 — Instrumento de captura del brazo manual

El proyecto SHALL proveer un instrumento que permita registrar, por caso del corpus, la clasificacion emitida por etiquetadores humanos del BRAZO MANUAL, de forma separable por etiquetador y comparable contra la verdad de consenso (`sector_asignado`). El instrumento SHALL identificar cada caso por su id de corpus y cada etiqueta por su etiquetador, MUST permitir mas de un etiquetador por caso (etiquetado independiente) y MUST NOT exponer PII en claro. El instrumento MUST ser operable sin acoplar la captura a la base de datos de produccion.

#### Scenario: Captura por caso y etiquetador

- **WHEN** un etiquetador registra la clasificacion de un caso del corpus
- **THEN** la captura queda asociada al id del caso y al identificador del etiquetador

#### Scenario: Etiquetado independiente

- **WHEN** dos o mas etiquetadores clasifican el mismo caso
- **THEN** sus etiquetas coexisten de forma separada y no se sobrescriben entre si

#### Scenario: Sin PII en la captura

- **WHEN** se registra una etiqueta del brazo manual
- **THEN** el instrumento no almacena email, telefono ni otros datos personales en claro

### Requirement: ECM-002 — Protocolo de campana registrado en el repositorio

El proyecto SHALL incluir un runbook versionado que defina la campana de campo: quienes etiquetan, cuantos casos como minimo, la exigencia de independencia, el instrumento a usar y el criterio de aceptacion/verificacion de cada dataset. El protocolo SHALL describir como se produce el dataset del brazo manual y el de intervencion, y MUST ser ejecutable por los autores sin depender de conocimiento tacito.

#### Scenario: El protocolo define sujetos casos e independencia

- **WHEN** se lee el runbook de campana
- **THEN** especifica quienes etiquetan, el minimo de casos y la exigencia de independencia

#### Scenario: El protocolo define aceptacion y verificacion

- **WHEN** se completa la campana
- **THEN** el runbook provee un criterio explicito de aceptacion/verificacion para cada dataset producido

### Requirement: ECM-003 — Medicion de la tasa de intervencion humana real

El sistema SHALL permitir calcular la TASA DE INTERVENCION HUMANA REAL a partir de las intervenciones efectivamente registradas (actor, origen e instante), distinta del marco `requiere_revision_humana` que solo senala casos elegibles para revision. La metrica SHALL ser reproducible sobre un rango temporal y MUST NOT confundir un caso elegible no intervenido con uno intervenido.

#### Scenario: La tasa cuenta solo intervenciones efectivas

- **WHEN** se calcula la tasa de intervencion para un rango temporal
- **THEN** solo cuentan los casos con una intervencion registrada, no todos los marcados `requiere_revision_humana`

#### Scenario: La metrica es reproducible

- **WHEN** se recalcula la tasa sobre el mismo rango y los mismos datos
- **THEN** el valor resultante es identico
