## Purpose

Define el congelado reproducible del modelo supervisado seleccionado por el benchmark de
`c-228` y su integracion en la configuracion entregada detras del mismo contrato del
clasificador, de forma seleccionable por configuracion y sin romper el hibrido ni las cinco
cadenas canonicas.

## ADDED Requirements

### Requirement: SCI-001 — Congelado versionado y reproducible del modelo seleccionado

El change SHALL consumir el mejor modelo del benchmark de
`c-228-clasificador-supervisado-sobre-el-corpus-acumulado` conforme a los criterios fijados
de antemano y SHALL seleccionar exactamente un modelo. El modelo seleccionado SHALL
publicarse como un artefacto versionado e **inmutable** que registre, como minimo: los pesos
o un puntero con su hash SHA-256, el tokenizer y su version, la version del codebook de
entrada, el hash del split de entrenamiento y la version de preprocesamiento, con un comando
de evaluacion reproducible. El artefacto SHALL declarar que los criterios del benchmark no se
rediscuten ni se modifican y que el modelo MUST NOT re-entrenarse ni ajustarse despues de
observar el contraste. Si `c-228` no entrego un modelo o un benchmark, la seleccion SHALL
quedar bloqueada y registrada, y MUST NOT sustituirse por un modelo elegido a mano.

#### Scenario: Modelo congelado con procedencia

- **WHEN** se selecciona el mejor modelo del benchmark de `c-228`
- **THEN** se emite un artefacto versionado con pesos o puntero y hash, tokenizer, version del codebook, hash del split y preprocesamiento
- **AND** el artefacto incluye un comando de evaluacion reproducible

#### Scenario: Insumo ausente

- **WHEN** `c-228` no entrego un modelo o un benchmark disponible
- **THEN** la seleccion queda bloqueada y se registra como dependencia no satisfecha
- **AND** no se sustituye por un modelo elegido a mano

### Requirement: SCI-002 — Integracion detras del mismo contrato del clasificador

El modelo congelado SHALL integrarse en la configuracion entregada detras del **mismo
contrato del clasificador** que la abstraccion de
`inference-provider-abstraction` (`c-227`), como una etapa o proveedor **seleccionable por
configuracion** que respecta el contrato canonico: los cinco sectores canonicos con su casing
exacto y sin tildes, el esquema del resultado, el gate de revision humana y el fallback. La
integracion MUST NOT romper el clasificador hibrido vigente ni alterar el prompt, los
parametros de inferencia o las cadenas canonicas. El modelo supervisado SHALL ejecutarse de
forma **local y offline**, y MUST NOT provocar llamadas pagas fuera del gate de confirmacion.

#### Scenario: Modelo seleccionable sin romper el hibrido

- **WHEN** se habilita el modelo supervisado por configuracion
- **THEN** el sistema lo resuelve a traves del mismo contrato del clasificador y lo ofrece como proveedor o etapa seleccionable
- **AND** el clasificador hibrido vigente queda intacto

#### Scenario: Contrato canonico preservado

- **WHEN** se inspeccionan los sectores validos, el prompt, los parametros de inferencia y el esquema del resultado tras integrar el modelo
- **THEN** son identicos a los vigentes
- **AND** las cinco cadenas canonicas permanecen exactas, sensibles a mayusculas y sin tildes

#### Scenario: Ejecucion local sin llamadas pagas

- **WHEN** se clasifica con el modelo supervisado integrado
- **THEN** la inferencia ocurre localmente sobre los pesos congelados
- **AND** no se realizan llamadas pagas fuera del gate de confirmacion

### Requirement: SCI-003 — Neutralidad por defecto y no regresion

Con la configuracion entregada por defecto, la integracion SHALL ser **neutral**: el
clasificador MUST reproducir caso por caso las predicciones del clasificador hibrido vigente
y MUST NOT alterar ningun numero canonico ni la evidencia congelada. La integracion SHALL ser
**reproducible** (semilla fija, versiones pinneadas) y una verificacion SHALL demostrar que
el modelo offline es determinista y que el camino del hibrido no cambia. El default entregado
MUST NOT dejar de resolver al hibrido salvo que la regla de decision pre-registrada de
`delivered-classifier-decision` determine **reemplazar** la etapa semantica.

#### Scenario: Default neutral

- **WHEN** se clasifica el corpus con la configuracion entregada por defecto
- **THEN** las predicciones coinciden caso por caso con las del clasificador hibrido vigente
- **AND** ningun numero canonico cambia

#### Scenario: Default conservado salvo reemplazo

- **WHEN** el veredicto de la regla pre-registrada no es reemplazar
- **THEN** el default entregado sigue resolviendo al hibrido
- **AND** el modelo supervisado queda seleccionable pero no predeterminado
