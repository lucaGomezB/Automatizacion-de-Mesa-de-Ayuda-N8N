## ADDED Requirements

### Requirement: Versionado e integridad de los sidecars de resultados sin PII

Los sidecars de trazabilidad de las corridas de ingesta que son libres de PII por construccion y corresponden a corridas COMPLETAS ---`data/corpus_resultados.json` (200 filas) y `data/corpus_resultados_telefonia.json` (81 filas)--- SHALL versionarse en el repositorio como evidencia agregada de transparencia. La regla de `.gitignore` que hoy los excluye (`data/corpus_resultados*.json`) SHALL reemplazarse por una que versiona esos dos sidecars completos y sigue excluyendo por defecto a cualquier otro sidecar del patron, sin habilitar el versionado de ningun sidecar con descripciones. `data/corpus_resultados_n8n.json`, cuya discrepancia de conteo (4 filas locales frente a 119 de la corrida completa del 2-10-2026) no esta resuelta, MUST NOT commitearse mientras la discrepancia siga abierta. `data/README.md` SHALL declarar versionados los sidecars completos y explicar el motivo (contienen solo identificador de caso, canal, identificador de incidente, sector, marcas temporales y latencias), y las referencias que hoy los describen como no versionados (`docs/como_cargar_datos_corpus.md`, `scripts/corpus_ingest/README.md`, `knowledge-base/09_decisiones_y_supuestos.md`) SHALL coherentizarse. Cada sidecar versionado MUST NOT contener descripciones de caso ni dato personal alguno.

#### Scenario: Sidecars trackeados y sin PII

- **WHEN** se ejecuta `git check-ignore` sobre los sidecars y se inspecciona el contenido de los versionados
- **THEN** los sidecars COMPLETOS (`corpus_resultados.json` y `corpus_resultados_telefonia.json`) no quedan ignorados y estan bajo control de versiones
- **AND** `data/corpus_resultados_n8n.json` permanece excluido a la espera de resolver su discrepancia de conteo
- **AND** ninguno de los versionados contiene una descripcion de caso ni dato personal

#### Scenario: README coherente con el versionado

- **WHEN** se lee `data/README.md` y las referencias a `corpus_resultados*.json`
- **THEN** declaran que los sidecars completos se versionan y por que
- **AND** ninguna referencia vigente los presenta como no versionados

#### Scenario: Discrepancia de conteo registrada

- **WHEN** se compara el numero de filas de `data/corpus_resultados_n8n.json` con los 119 casos de la corrida del 2-10-2026
- **THEN** la diferencia se registra como pregunta abierta sobre que artefacto es el autoritativo y el archivo no se commitea mientras la pregunta siga abierta
- **AND** la decision no se toma de forma implicita
