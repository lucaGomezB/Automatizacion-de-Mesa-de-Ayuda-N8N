## Purpose

Cura el corpus de decisiones validadas por la organizacion en `clasificacion_log`
para entrenar un clasificador supervisado del dominio, a partir de un export crudo
de procedencia acreditada, con autorizacion institucional, pseudonimizacion, no
solape con el corpus de ajuste ni con el conjunto retenido, y procedencia versionada.

## ADDED Requirements

### Requirement: SCC-001 — Extraccion solo de decisiones validadas, autorizadas y de operacion real

El pipeline de curacion SHALL exportar exclusivamente registros de
`clasificacion_log` con decision humana validada (`sector_id_validado` no nulo y,
cuando exista, `sectores_validados`), y SHALL asociar a cada caso el texto del
`incidente` correspondiente. El pipeline MUST NOT exportar registros en etapa
`fallback` ni con `confianza = 0.0`, MUST NOT exportar filas producidas por
corridas de evaluacion o de demostracion, y MUST NOT exportar filas cuyo texto
coincida con un texto ya versionado en el repositorio (corpus de 200 casos,
material retirado por `c-235` o fixtures). La extraccion de datos reales SHALL
estar precedida por la compuerta etica y legal: autorizacion institucional escrita
(original en custodia del director), base de licitud bajo la Ley 25.326 e
informacion o consentimiento de los empleados cuyos textos y decisiones se usan.
Si la compuerta no consta cerrada, el pipeline MUST NOT emitir casos reales y SHALL
abortar con un mensaje accionable.

#### Scenario: Solo decisiones validadas de operacion real

- **WHEN** el pipeline procesa el export de `clasificacion_log`
- **THEN** solo emite casos con `sector_id_validado` no nulo que no provienen de corridas de evaluacion o demostracion
- **AND** descarta los registros en etapa `fallback`, con `confianza` igual a `0.0` o con texto ya versionado en el repositorio

#### Scenario: Bloqueo sin compuerta etica y legal

- **WHEN** el pipeline intenta exportar datos reales sin autorizacion institucional ni base de licitud registradas
- **THEN** aborta sin escribir casos reales
- **AND** el mensaje identifica la compuerta abierta como causa

### Requirement: SCC-002 — Pseudonimizacion, no solape y corpus inmutable versionado

Cada caso exportado SHALL pseudonimizarse con el protocolo del corpus de ajuste
(`scripts/corpus_ingest/pseudonymize_corpus.py`) antes de escribirse. El corpus
curado SHALL versionarse como un unico documento JSON con `schema_version` y
`metadata`, en UTF-8 sin BOM y con terminacion LF, y SHALL registrar la procedencia
de cada caso (identificador de origen, etapa, origen de la intervencion y marcas de
tiempo tal como las registro el sistema, pseudonimizadas). Como paso previo
obligatorio, el corpus SHALL verificarse con `evaluation.no_solape.verificar_no_solape`
contra el corpus de 200 casos (`data/corpus_evaluacion_pseudonimizado.json`) y
contra el conjunto de prueba retenido que exista; si hay solape con cualquiera de
ellos, el pipeline MUST NOT escribir el corpus final.

#### Scenario: Corpus versionado y pseudonimizado

- **WHEN** se escribe el corpus curado
- **THEN** el documento tiene `schema_version` y `metadata` y cada caso esta pseudonimizado
- **AND** el archivo es UTF-8 sin BOM con terminacion LF

#### Scenario: Solape con el corpus de 200 aborta la escritura

- **WHEN** el corpus candidato comparte casos con el corpus de 200 casos
- **THEN** `verificar_no_solape` lo detecta
- **AND** no se escribe el corpus final

#### Scenario: Solape con el conjunto retenido aborta la escritura

- **WHEN** existe un conjunto de prueba retenido y el corpus candidato comparte casos con el
- **THEN** `verificar_no_solape` lo detecta
- **AND** no se escribe el corpus final

### Requirement: SCC-003 — Curacion y control de calidad del corpus

El pipeline SHALL aplicar control de calidad: descartar duplicados internos por
texto normalizado, conservar la distribucion por sector y por canal del corpus
acumulado y emitir un resumen con el conteo por sector, por canal y por etapa. El
resumen SHALL declarar el volumen alcanzado frente al volumen indicativo y, cuando
no lo alcance, SHALL registrar que el entrenamiento queda condicionado. La curacion
MUST NOT alterar las cinco cadenas canonicas ni recodificar etiquetas; los valores
fuera del conjunto canonico SHALL descartarse o reportarse, nunca mapearse
silenciosamente.

#### Scenario: Resumen de control de calidad

- **WHEN** termina la curacion
- **THEN** se emite un resumen con conteo por sector, canal y etapa
- **AND** declara el volumen alcanzado frente al indicativo

#### Scenario: Etiquetas fuera del conjunto canonico

- **WHEN** un caso trae una etiqueta que no es una de las cinco cadenas canonicas
- **THEN** se descarta o se reporta
- **AND** no se mapea a otra categoria de forma silenciosa

### Requirement: SCC-004 — Compuerta de procedencia del export crudo

Ningun dato nuevo SHALL entrar al analisis sin la compuerta de procedencia cerrada:
el registro crudo exportado del sistema con las marcas temporales que el sistema
registra (nunca reconstruidas ni completadas a mano); una constancia de la
organizacion sobre la extraccion, con el original en custodia del director; el hash
SHA-256 del export crudo versionado en el repositorio; y la verificacion del
director contra la evidencia primaria, registrada con fecha, antes de habilitar el
analisis. El pipeline SHALL verificar el SHA-256 del export antes de procesarlo y
MUST abortar si no coincide. Ningun texto redactado por los autores ni generado o
asistido por IA MUST entrar como dato de entrenamiento o de prueba presentado como
real. Los fixtures sinteticos SHALL usarse solo en pruebas y SHALL rotularse como
sinteticos en el nombre del archivo, en la cabecera y en cualquier salida derivada.

#### Scenario: Export sin verificacion del director

- **WHEN** el export crudo no tiene registrada la verificacion del director o la constancia de la organizacion
- **THEN** el pipeline no habilita el analisis
- **AND** registra la compuerta de procedencia como abierta

#### Scenario: Hash del export no coincide

- **WHEN** el SHA-256 del export procesado difiere del versionado
- **THEN** el pipeline aborta sin escribir

#### Scenario: Fixture sintetico rotulado

- **WHEN** una prueba usa un fixture sintetico
- **THEN** el nombre del archivo, su cabecera y toda salida derivada lo rotulan como sintetico
- **AND** ningun artefacto de resultados lo presenta como dato real
