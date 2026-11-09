## Purpose

Define el protocolo y los artefactos de la validación fuera de muestra del clasificador
CONGELADO sobre un corpus independiente de 150 casos: el alcance (solo clasificación), los
etiquetadores, la referencia por consenso, el muestreo estratificado con sobremuestreo y
ponderación, el n efectivo con su sesgo de exclusión y el versionado de los resultados, de
modo que la validación sea producible, registrada y verificable sin recalibrar el clasificador
ni tocar los artefactos congelados de la v9.

## ADDED Requirements

### Requirement: OOS-001 — Alcance: solo la validación de clasificación del clasificador congelado

La validación fuera de muestra SHALL medir únicamente la clasificación del clasificador
congelado sobre el corpus independiente. MUST NOT medir el brazo manual ni involucrar a los
operadores `O1`/`O2`, ni al efecto de orden, ni al cronometraje de las reasignaciones. El
resultado SHALL reportarse como el bloque out-of-sample de `evaluar_fuera_de_muestra`, sin
sustituir ni reemplazar las métricas in-sample.

#### Scenario: Alcance acotado a la clasificación

- **WHEN** se prepara la campaña de validación fuera de muestra
- **THEN** el protocolo y los artefactos declaran que la medición es solo de la clasificación del clasificador congelado
- **AND** no se registra ninguna etiqueta de brazo manual ni de operadores `O*` para el corpus independiente

#### Scenario: Bloque out-of-sample sin sustitución

- **WHEN** se ejecuta el análisis
- **THEN** el resultado fuera de muestra se reporta como un bloque rotulado `out-of-sample` con su n efectivo
- **AND** las métricas in-sample no se reemplazan ni se presentan como fuera de muestra

### Requirement: OOS-002 — Corpus independiente de 150 casos sin solape y pseudonimizado

El corpus independiente SHALL tener 150 casos nuevos con ids `I001..I150`, disjuntos de los
200 del corpus de ajuste, y SHALL pseudonimizarse con el mismo protocolo que el corpus de
ajuste mediante `scripts/corpus_ingest/pseudonymize_corpus.py`. El corpus final SHALL ser un
JSON con el esquema de `data/corpus_evaluacion_pseudonimizado.json` (las cinco cadenas de
sector canónicas, exactas y sin tildes) y SHALL pasar `verificar_no_solape` contra el corpus de
ajuste como paso previo obligatorio antes de clasificar.

#### Scenario: Sin solape de ids ni de descripciones

- **WHEN** se contrasta el corpus independiente con el de ajuste
- **THEN** `verificar_no_solape` no lanza `SolapeError`, todos los ids del candidato llevan el prefijo `I` y ninguna descripción normalizada coincide con una del corpus de ajuste

#### Scenario: Misma pseudonimización

- **WHEN** se pseudonimiza el corpus crudo
- **THEN** se usa `scripts/corpus_ingest/pseudonymize_corpus.py` con el mismo protocolo del corpus de ajuste y el pseudonimizador sale con exit code `0`

### Requirement: OOS-003 — Doble etiquetado con dos etiquetadores nuevos `E3` y `E4`

El corpus independiente SHALL doble-etiquetarse con la plantilla y el validador de la campaña
(`evaluation/data/plantilla_etiquetado.csv`, `evaluation/doble_etiquetado.py`), con exactamente
dos etiquetadores nuevos, alias `E3` y `E4`, distintos entre sí y de los analistas `A1`, de los
autores `T1`-`T3` y de los operadores `O1`/`O2`. El registro `evaluation/data/campana/registro_sujetos.csv`
SHALL registrar `E3` y `E4` con `rol = etiquetador` y un código `P<n>`, sin nombres, correos ni
legajos; la correspondencia alias-identidad SHALL custodiarse FUERA del repositorio. El
validador SHALL salir con exit code `0` o la limitación SHALL declararse.

#### Scenario: Dos etiquetadores nuevos e independientes

- **WHEN** se registran `E3` y `E4` en `registro_sujetos.csv`
- **THEN** cada uno tiene `rol = etiquetador` y una `persona` `P<n>` que no figura con ningún otro rol, distinta de las `persona` de `A1`, `T1`-`T3` y `O1`/`O2`
- **AND** ninguna fila contiene nombre, correo ni legajo

#### Scenario: Planilla válida con la plantilla y el validador existentes

- **WHEN** se valida la planilla unida de `E3` y `E4` contra el corpus independiente
- **THEN** `python -m evaluation.doble_etiquetado --tarea doble_etiquetado` sale con exit code `0`
- **AND** no se define un esquema ni un validador propios

### Requirement: OOS-004 — Referencia por consenso y conjunto de verdad laxo

La referencia SHALL ser el consenso de `E3` y `E4` sobre `sector_etiquetado` para el mismo
`id_caso` (`consenso_doble_etiquetado`). El conjunto de verdad laxo SHALL ser el sector
consensuado más la INTERSECCIÓN de los sectores adicionales que ambos etiquetadores marcaron.
Los casos discordantes SHALL EXCLUIRSE de la referencia y SHALL informarse con la advertencia
de sesgo hacia casos fáciles.

#### Scenario: Consenso como referencia

- **WHEN** `E3` y `E4` asignan el mismo `sector_etiquetado` a un caso
- **THEN** ese sector es la referencia estricta y el conjunto laxo suma la intersección de los adicionales de ambos
- **AND** el conjunto laxo nunca incluye un adicional marcado por un solo etiquetador

#### Scenario: Discordantes excluidos y reportados

- **WHEN** `E3` y `E4` asignan distinto `sector_etiquetado` a un caso
- **THEN** el caso queda fuera de la referencia
- **AND** el resultado informa cuántos casos se excluyeron y la advertencia de sesgo hacia casos fáciles

### Requirement: OOS-005 — Clasificador congelado y runner reutilizado

La clasificación SHALL ejecutarse con el clasificador CONGELADO: `classifier_version` idéntica
a la del in-sample (`hybrid-v3`) y commit `d6bb474`, sin recalibrar tau, el prompt, el
`KEYWORD_MAP` ni el vocabulario de sectores después de ver el corpus. La corrida SHALL
reutilizar `evaluar_fuera_de_muestra` y el guard `--confirm-paid` de
`evaluation/run_evaluation.py`, con `--corpus`, `--predicciones` y `--reporte` propios del
corpus independiente, sin escribir sobre los artefactos congelados de la v9.

#### Scenario: Congelamiento verificado

- **WHEN** se registra el control de clasificador congelado
- **THEN** `git diff d6bb474 HEAD` sobre el clasificador, el prompt y las constantes solo admite diferencias ajenas a la clasificación
- **AND** el resultado del control y el commit se registran en `evaluation/data/campana/README.md`

#### Scenario: Sin recalibración posterior

- **WHEN** aparece un defecto después de ver el corpus o sus predicciones
- **THEN** el protocolo prohíbe corregirlo y volver a medir sobre los mismos casos
- **AND** el defecto se informa como hallazgo y, de corregirse, se reúne un corpus independiente nuevo

#### Scenario: Rutas propias y guard de costo

- **WHEN** se clasifica el corpus independiente
- **THEN** `evaluar_fuera_de_muestra` y `--confirm-paid` se reutilizan y las predicciones quedan en `evaluation/data/campana/predicciones_independiente.json`
- **AND** `evaluation/predicciones.json` y `evaluation/report.md` no cambian

### Requirement: OOS-006 — Muestreo estratificado con sobremuestreo y ponderación

La selección de los 150 casos SHALL ser estratificada por canal de origen (correo, formulario
web, telefonía) y por sector, con sobremuestreo de la clase minoritaria (`Bases de Datos`, n=1
en el corpus de 200) y ponderación de las estimaciones globales por la distribución del
universo. Los estratos exactos SHALL fijarse y registrarse ANTES de reunir el corpus.

#### Scenario: Estratos definidos antes de reunir

- **WHEN** se inicia la recolección del corpus independiente
- **THEN** la asignación por estrato de canal y sector está decidida y registrada con su justificación
- **AND** la clase minoritaria está sobremuestreada respecto de su proporción en el corpus de 200

#### Scenario: Estimaciones globales ponderadas

- **WHEN** se calculan las métricas globales del corpus independiente
- **THEN** se informan con la ponderación por la distribución del universo, además del valor sin ponderar

### Requirement: OOS-007 — n efectivo y sesgo de exclusión declarados

El resultado SHALL declarar el n efectivo (casos con consenso) y el número de casos excluidos
por discordancia, junto con el IC de Wilson de la exactitud estricta. La exactitud estricta
del corpus independiente SHALL reportarse como estimación sobre el n efectivo, con la
advertencia de que la exclusión de los discordantes sesga la referencia hacia los casos más
fáciles.

#### Scenario: n efectivo explícito

- **WHEN** se lee el resultado fuera de muestra
- **THEN** figura el n efectivo y el conteo de casos excluidos por discordancia
- **AND** la exactitud estricta se reporta con su IC de Wilson sobre el n efectivo

#### Scenario: Advertencia de sesgo presente

- **WHEN** se reporta la exactitud fuera de muestra
- **THEN** el texto declara que excluir los discordantes sesga la referencia hacia los casos más fáciles

### Requirement: OOS-008 — Artefactos versionados con SHA-256

Los artefactos de la validación fuera de muestra SHALL versionarse en
`evaluation/data/campana/` con su SHA-256 en `evaluation/data/campana/README.md`: el corpus
independiente (`corpus_independiente.json`), las predicciones
(`predicciones_independiente.json`), la tabla del doble etiquetado independiente
(`doble_etiquetado_independiente.csv`), el registro de sujetos (`registro_sujetos.csv`), las
salidas de análisis y el resultado del control de clasificador congelado con su commit. Los
artefactos de la v9 SHALL quedar sin cambios.

#### Scenario: Hash y procedencia registrados

- **WHEN** se versionan los artefactos
- **THEN** el README registra el SHA-256 de cada archivo y el commit con que se generó el cache
- **AND** `git status` no muestra modificados `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados*.json` ni `evaluation/report.md`

#### Scenario: Cache con procedencia completa

- **WHEN** se inspecciona `predicciones_independiente.json`
- **THEN** su `cache_meta` trae `corpus_hash`, `corpus_count`, `classifier_version`, `generated_at`, `commit` y `pines`

### Requirement: OOS-009 — Protocolo y registro de decisiones versionados

El proyecto SHALL versionar el protocolo actualizado de la campaña independiente en
`docs/campana-medicion/runbook-corpus-independiente.md` y `runbook-doble-etiquetado.md`, que
SHALL nombrar a los etiquetadores `E3` y `E4`, el muestreo estratificado con sobremuestreo y
ponderación, la referencia por consenso con su sesgo de exclusión y el criterio de aceptación.
El protocolo SHALL ser ejecutable por los autores sin conocimiento tácito.

#### Scenario: Protocolo ejecutable y sin tácito

- **WHEN** un autor sigue los runbooks para la campaña independiente
- **THEN** los runbooks indican `E3` y `E4` como etiquetadores, la estratificación y ponderación, la referencia por consenso y el criterio de aceptación
- **AND** cada paso tiene su comando o su artefacto verificable

#### Scenario: Decisión de estratos registrada

- **WHEN** se consulta la decisión de muestreo
- **THEN** figura registrada la asignación por estrato decidida por los autores antes de reunir el corpus
