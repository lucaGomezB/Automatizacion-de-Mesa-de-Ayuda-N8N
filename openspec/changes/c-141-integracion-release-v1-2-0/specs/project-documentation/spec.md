## ADDED Requirements

### Requirement: Sincronia de la base de conocimiento con la release publicada de la tesis

`knowledge-base/11_evaluacion_experimental.md` SHALL presentar los resultados vigentes de la ultima release publicada de la tesis, con valores identicos a los valores `vigente` de `docs/Tesis/Correcciones/numeros-canonicos.md`, SHALL citar ese memo como fuente unica y SHALL identificar la release a la que corresponden. El archivo MUST NOT afirmar que los resultados estan pendientes de medicion; si conserva los valores del corpus sintetico descartado, SHALL presentarlos solo como antecedente historico rotulado como superado. Ningun archivo de `knowledge-base/` MUST afirmar que el vocabulario del filtro determinista o el prompt se construyeron sin acceso al corpus de evaluacion ni que la evaluacion es estrictamente fuera de muestra; cuando la base de conocimiento describa la procedencia de esos ajustes, SHALL coincidir con la que declara la tesis (vocabulario de c-71, reglas de frontera de c-72 y punto de operacion de c-74, ajustados con el corpus de evaluacion) y remitir a su analisis de sensibilidad. `knowledge-base/README.md` SHALL referenciar la ruta vigente del render de la tesis (`docs/Tesis/v10 (IA)/tesis_para_agente.md`) y la version del modelo que declara la tesis, y su resumen ejecutivo SHALL presentar los resultados vigentes sin citar valores retirados como vigentes. Ningun archivo de `knowledge-base/` MUST introducir un valor numerico de resultado que no figure en el memo.

#### Scenario: Valores iguales al memo

- **WHEN** se comparan los valores de resultado de `knowledge-base/11_evaluacion_experimental.md` con el memo canonico
- **THEN** cada valor coincide con su fila `vigente` del memo
- **AND** el archivo identifica la release `v1.2.0` y remite al memo como fuente

#### Scenario: Sin resultados pendientes de medicion

- **WHEN** se busca en `knowledge-base/11_evaluacion_experimental.md` la afirmacion de que los numeros "se re-miden" o estan pendientes
- **THEN** no aparece
- **AND** las cifras del corpus sintetico, si se conservan, figuran rotuladas como superadas

#### Scenario: Sin la afirmacion de ausencia de fuga refutada por el dictamen

- **WHEN** se busca en `knowledge-base/` la afirmacion de que keywords y prompt se construyeron sin acceso al corpus de validacion o de que la evaluacion es "estrictamente held-out"
- **THEN** no aparece
- **AND** la procedencia de los ajustes del clasificador, si se menciona, coincide con la que declara la tesis y remite a su analisis de sensibilidad

#### Scenario: Ruta y modelo vigentes en el README

- **WHEN** se lee `knowledge-base/README.md`
- **THEN** remite a `docs/Tesis/v10 (IA)/tesis_para_agente.md` como render de la tesis
- **AND** nombra el modelo con la misma version que declara la tesis (`gemini-3.6-flash`)

#### Scenario: Sin valores retirados presentados como vigentes

- **WHEN** se buscan en `knowledge-base/` los valores que el memo marca `retirado` (por ejemplo, 9,5 % de intervencion humana o el universo de 3.700 incidentes)
- **THEN** no aparecen presentados como resultados vigentes
