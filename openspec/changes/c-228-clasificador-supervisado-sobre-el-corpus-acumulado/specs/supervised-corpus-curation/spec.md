## Purpose

Acumula y cura el corpus de decisiones validadas por la organizacion en
`clasificacion_log` para entrenar un clasificador supervisado del dominio, con
consentimiento, pseudonimizacion, no solape con la referencia y procedencia
versionada.

## ADDED Requirements

### Requirement: SCC-001 — Extraccion solo de decisiones validadas y consentidas

El pipeline de curacion SHALL exportar exclusivamente registros de
`clasificacion_log` con decision humana validada (`sector_id_validado` no nulo y,
cuando exista, `sectores_validados`), y SHALL asociar a cada caso el texto del
`incidente` correspondiente. El pipeline MUST NOT exportar registros en etapa
`fallback` ni con `confianza = 0.0`, porque no portan una decision util. La
exportacion de datos reales SHALL estar precedida por la verificacion del
consentimiento informado y de la base de licitud aplicable; si el consentimiento
no esta registrado, el pipeline MUST NOT emitir casos reales y SHALL abortar con
un mensaje accionable.

#### Scenario: Solo decisiones validadas

- **WHEN** el pipeline procesa `clasificacion_log`
- **THEN** solo emite casos con `sector_id_validado` no nulo
- **AND** descarta los registros en etapa `fallback` y con `confianza` igual a `0.0`

#### Scenario: Bloqueo sin consentimiento

- **WHEN** el pipeline intenta exportar datos reales sin consentimiento registrado
- **THEN** aborta sin escribir casos reales
- **AND** el mensaje identifica la ausencia de consentimiento como causa

### Requirement: SCC-002 — Pseudonimizacion, no solape con los 206 y corpus inmutable versionado

Cada caso exportado SHALL pseudonimizarse con el mismo protocolo del corpus de
ajuste (`scripts/corpus_ingest/pseudonymize_corpus.py`) antes de escribirse. El
corpus curado SHALL versionarse como un unico documento JSON con `schema_version`
y `metadata`, en UTF-8 sin BOM y con terminacion LF, y SHALL registrar la
procedencia de cada caso (identificador de origen, etapa, origen de la
intervencion y marcas de tiempo pseudonimizadas). El corpus SHALL verificarse
contra los `206` casos de referencia con `evaluation.no_solape.verificar_no_solape`
como paso previo obligatorio; si hay solape, el pipeline MUST NOT escribir el
corpus final.

#### Scenario: Corpus versionado y pseudonimizado

- **WHEN** se escribe el corpus curado
- **THEN** el documento tiene `schema_version` y `metadata` y cada caso esta pseudonimizado
- **AND** el archivo es UTF-8 sin BOM con terminacion LF

#### Scenario: Solape con la referencia aborta la escritura

- **WHEN** el corpus candidato comparte casos con los `206` de referencia
- **THEN** `verificar_no_solape` lo detecta
- **AND** no se escribe el corpus final

### Requirement: SCC-003 — Curacion y control de calidad del corpus

El pipeline SHALL aplicar control de calidad: descartar duplicados internos por
texto normalizado, conservar la distribucion por sector y por canal del corpus
acumulado y emitir un resumen con el conteo por sector, por canal y por etapa. El
resumen SHALL declarar el volumen alcanzado frente al volumen indicativo y, cuando
no lo alcance, SHALL registrar explicitamente que el entrenamiento queda
condicionado. La curacion MUST NOT alterar las cinco cadenas canonicas ni recodificar
etiquetas; los valores fuera del conjunto canonico SHALL descartarse o reportarse,
nunca mapearse silenciosamente.

#### Scenario: Resumen de control de calidad

- **WHEN** termina la curacion
- **THEN** se emite un resumen con conteo por sector, canal y etapa
- **AND** declara el volumen alcanzado frente al indicativo

#### Scenario: Etiquetas fuera del conjunto canonico

- **WHEN** un caso trae una etiqueta que no es una de las cinco cadenas canonicas
- **THEN** se descarta o se reporta
- **AND** no se mapea a otra categoria de forma silenciosa
