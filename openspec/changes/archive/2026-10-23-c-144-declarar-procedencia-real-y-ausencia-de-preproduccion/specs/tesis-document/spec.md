## ADDED Requirements

### Requirement: Procedencia declarada de los ajustes realizados sobre el corpus de validacion

La tesis SHALL declarar en la discusion (`subsec:interpretacion-resultados`) que el vocabulario del filtro deterministico (c-71), las reglas de frontera del prompt (c-72) y el punto de operacion del cortocircuito (c-74) se derivaron de casos y errores observados en el corpus de validacion de 200 casos; SHALL acotar que la mitigacion fuera de muestra de c-74 (validacion cruzada de cinco pliegues para el punto de operacion) NO cubre la ampliacion del vocabulario ni las reglas del prompt; SHALL declarar que no se dispuso de un corpus independiente de preproduccion; y SHALL calificar las metricas de clasificacion como estimaciones dentro de la muestra cuya confirmacion exige un corpus independiente. Las demas secciones que afirman la ausencia de exposicion al corpus (`05-arquitectura.tex`, `06-implementacion.tex`, Anexo H) SHALL alinearse con esa declaracion o remitir a ella. La tesis MUST NOT afirmar separacion estricta entre datos de construccion y de validacion, ausencia de exposicion al corpus ni desempeno sobre datos no vistos; MUST NOT afirmar la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion ni remitir a `docs/prompt_gemini_history/`; y MUST NOT alterar ningun valor numerico por esta declaracion.

#### Scenario: Procedencia de los tres ajustes declarada

- **WHEN** se lee `subsec:interpretacion-resultados` en el PDF compilado
- **THEN** se declaran los ajustes del vocabulario del filtro deterministico, de las reglas de frontera del prompt y del punto de operacion realizados sobre el corpus de validacion
- **AND** las metricas de clasificacion se califican como estimaciones dentro de la muestra

#### Scenario: Mitigacion fuera de muestra acotada

- **WHEN** se lee la declaracion de procedencia
- **THEN** la mitigacion fuera de muestra de c-74 se acota al punto de operacion
- **AND** se declara expresamente que esa mitigacion no cubre el vocabulario ni las reglas del prompt

#### Scenario: Sin corpus independiente de preproduccion

- **WHEN** se busca en `sections/*.tex` una afirmacion sobre un corpus independiente de incidentes de preproduccion
- **THEN** se declara que no se dispuso de un corpus de esas caracteristicas
- **AND** no se afirma la existencia de un conjunto de aproximadamente 100 incidentes de preproduccion

#### Scenario: Sin afirmacion de no exposicion

- **WHEN** se buscan en `sections/*.tex` las afirmaciones "sin exposicion a" (el corpus o los 200 casos de validacion), "sin acceso al corpus", "datos no vistos" y "separacion estricta"
- **THEN** ninguna aparece como afirmacion vigente sobre la version evaluada

#### Scenario: Numeros intactos

- **WHEN** se comparan las metricas de clasificacion del PDF antes y despues de la declaracion
- **THEN** no cambia ningun valor numerico

### Requirement: Ubicacion veraz de las versiones historicas del prompt en el Anexo H

El Anexo H (`12-anexos.tex`) y su documento fuente `docs/anexo_h_prompt_gemini.md` SHALL ubicar las versiones historicas del prompt en el historial de versiones del repositorio para `docs/prompt_gemini.txt` y MUST NOT remitir a `docs/prompt_gemini_history/`, que no existe en el repositorio. `docs/anexo_h_prompt_gemini.md` MUST NOT afirmar que el prompt se ajusto sin exposicion al corpus de validacion ni sobre aproximadamente 100 incidentes de preproduccion, y SHALL declarar que las reglas de frontera de la version evaluada se incorporaron a partir de errores observados en ese corpus.

#### Scenario: Sin remision a un directorio inexistente

- **WHEN** se busca `docs/prompt_gemini_history` en `sections/*.tex` y en `docs/anexo_h_prompt_gemini.md`
- **THEN** no aparece ninguna coincidencia

#### Scenario: Ubicacion correcta en el historial de versiones

- **WHEN** se lee la seccion de iteracion del prompt del Anexo H (`12-anexos.tex`) y de `docs/anexo_h_prompt_gemini.md`
- **THEN** ambas remiten al historial de versiones de `docs/prompt_gemini.txt`
- **AND** existe `git log -- docs/prompt_gemini.txt` con las versiones historicas

#### Scenario: Documento fuente alineado con la tesis

- **WHEN** se lee la seccion de iteracion del prompt de `docs/anexo_h_prompt_gemini.md`
- **THEN** no afirma ausencia de exposicion al corpus de validacion ni la existencia de un conjunto de incidentes de preproduccion
- **AND** declara el origen de las reglas de frontera y la ubicacion de las versiones historicas del prompt
