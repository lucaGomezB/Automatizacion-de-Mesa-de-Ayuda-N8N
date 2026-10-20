# Delta for tesis-document

## ADDED Requirements

### Requirement: Alineacion de la tesis con el corpus real de evaluacion

La tesis SHALL reportar los resultados experimentales sobre el corpus real de 200
casos pseudonimizados (`data/corpus_evaluacion_pseudonimizado.json`), no sobre el
corpus sintetico descartado en C-27. El Capitulo 7 SHALL reportar: la distribucion
por sector del corpus real (Sistemas 16, Soporte Tecnico Hardware 85, Soporte
Tecnico Software 67, Seguridad Informatica 31, Bases de Datos 1), los canales de
origen (correo 66, formulario web 53, llamada telefonica 81), la exactitud estricta
73,5 % (147/200), macro-F1 0,5207, micro-F1 0,6654, subset accuracy 0,43, Hamming
loss 0,3586, las etapas deterministic 131 / Gemini 69, y la matriz de confusion 5x5
completa. El vocabulario de sectores reportado SHALL ser el conjunto canonico de
cinco categorias, SIN la categoria retirada "Operaciones". La tesis SHALL NOT
reportar como vigentes los valores del corpus sintetico (3 clases, distribucion
82/64/54, exactitud 92 %, F1 macro 0,919).

#### Scenario: Capitulo 7 reporta las metricas reales

- **WHEN** se lee el Capitulo 7 (Resultados) del PDF compilado
- **THEN** la exactitud reportada es 73,5 % (147/200) y el macro-F1 es 0,5207
- **AND** la matriz de confusion reportada es 5x5 sobre las cinco categorias canonicas

#### Scenario: Categoria retirada ausente

- **WHEN** se busca "Operaciones" como sector en cualquier archivo `.tex` y en el PDF compilado
- **THEN** no aparece como categoria responsable, ni en la distribucion, ni en la matriz de confusion

#### Scenario: Distribucion por sector coincide con el reporte de evaluacion

- **WHEN** se compara la distribucion por sector reportada en la tesis con `evaluation/report.md`
- **THEN** coinciden en las cinco categorias (16/85/67/31/1)
- **AND** los canales de origen reportados coinciden (66/53/81)

### Requirement: Divulgacion del procedimiento de medicion de tiempos y analisis de sensibilidad

La tesis SHALL declarar que `tiempo_manual_s` es una medicion real en vivo,
registrada durante la atencion de usuarios con redondeo hacia arriba (sesgo
sistematico de medicion), y SHALL reportar el tiempo manual como cota superior
junto con una cota inferior conservadora de sensibilidad. El claim primario de
reduccion SHALL apoyarse en la mediana y en estadisticos de rango, no solo en la
media. La prueba de Wilcoxon SHALL reportar el valor real con correccion por
empates (W=335, p=2,05e-32, r=0,983) y SHALL declarar el numero real de pares en
que el flujo automatizado no fue mas rapido (12 de 200), sin afirmar "W=0" ni
"sin excepcion".

#### Scenario: Redondeo declarado y sensibilidad reportada

- **WHEN** se leen el Capitulo 4 (metodologia) y el Capitulo 7 (resultados)
- **THEN** se declara el redondeo al alza de la medicion manual
- **AND** se reporta la reduccion como cota superior (75,9 %) junto a su cota conservadora (>= 71,3 % bajo un ajuste de -10 s)

#### Scenario: Estadistico de Wilcoxon real

- **WHEN** se lee la comparacion de tiempos de registro
- **THEN** el estadistico reportado es W=335 con p=2,05e-32 y r=0,983
- **AND** el texto no afirma W=0 ni "sin una sola excepcion"

#### Scenario: Pares invertidos declarados

- **WHEN** se leen los resultados de tiempos
- **THEN** se declara que en 12 de 200 pares el flujo automatizado no fue mas rapido que el manual

### Requirement: Consistencia de anexos, documentacion de soporte y PDF

La documentacion de soporte SHALL ser consistente con el corpus real:
`docs/anexo_f_corpus.md` SHALL declarar que la evaluacion se realiza sobre el
corpus real pseudonimizado y versionado; `evaluation/README.md` y
`evaluation/data/README.md` SHALL indicar que el corpus esta versionado en su
forma pseudonimizada; el `README.md` raiz SHALL referenciar
`docs/anexo_h_prompt_gemini.md`; y `docs/anexo_h_prompt_gemini.md` SHALL usar la
misma version de modelo que el codigo (`gemini-3.6-flash`). La tesis SHALL
recompilar `docs/Tesis/v9 (IA)/paper/main.pdf` de modo que refleje las
correcciones.

#### Scenario: Anexo H alineado con el codigo

- **WHEN** se leen el titulo y el cuerpo de `docs/anexo_h_prompt_gemini.md`
- **THEN** la version del modelo declarada coincide con `settings.gemini_model` (`gemini-3.6-flash`)
- **AND** no se menciona "Gemini 2.5 Flash"

#### Scenario: Anexo F y READMEs declaran el corpus real versionado

- **WHEN** se leen `docs/anexo_f_corpus.md`, `evaluation/README.md` y `evaluation/data/README.md`
- **THEN** declaran la evaluacion sobre el corpus real pseudonimizado
- **AND** indican que la version pseudonimizada esta versionada en el repositorio

#### Scenario: PDF recompilado

- **WHEN** se compila el proyecto LaTeX con XeLaTeX (`latexmk -xelatex main.tex`)
- **THEN** se produce `main.pdf` sin errores fatales de compilacion
- **AND** el PDF refleja las correcciones (sin la categoria "Operaciones" ni los valores sinteticos)

### Requirement: Trazabilidad del corpus real en el anexo de validacion

El anexo "Corpus de validacion" de la tesis SHALL remitir al corpus real
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y SHALL NOT declarar que el corpus se conserva como un CSV de siete columnas en
`evaluation/data/`. El anexo SHALL aclarar que la categoria predicha y la
confianza por caso viven en `evaluation/predicciones.json`, no dentro del corpus.
La tesis SHALL NOT afirmar la existencia de un corpus en `evaluation/data/`.

#### Scenario: El anexo apunta al JSON real

- **WHEN** se lee la seccion "Corpus de validacion" del Anexo de la tesis
- **THEN** referencia `data/corpus_evaluacion_pseudonimizado.json` como corpus real
- **AND** no describe un archivo CSV ni un corpus de siete columnas en `evaluation/data/`

#### Scenario: Sin corpus inexistente

- **WHEN** se busca "evaluation/data" o "CSV" como ubicacion del corpus en los `.tex` y en el PDF
- **THEN** no se afirma que el corpus resida alli

### Requirement: Divulgacion de las etapas del pipeline incluida la etapa fallback

La tesis SHALL describir el pipeline de clasificacion como tres etapas en el orden
deterministic -> Gemini -> fallback, y SHALL reportar la distribucion real de casos
por etapa: deterministic 131/200 (65,5 %), Gemini 69/200 (34,5 %) y fallback 0/200.
La tesis SHALL NOT reportar el reparto stale "~62 % / 38 %" ni "seis de cada diez"
como distribucion vigente.

#### Scenario: Distribucion de etapas real

- **WHEN** se leen los capitulos 5.5, 8.1 y 9.1 del PDF compilado
- **THEN** la primera etapa se reporta como 65,5 % y la segunda como 34,5 %
- **AND** no aparece "62 %", "38 %" ni "seis de cada diez" como reparto de etapas

#### Scenario: Etapa fallback documentada

- **WHEN** se describe el pipeline de clasificacion en la tesis
- **THEN** se documenta la etapa fallback (0 casos) y el orden deterministic -> Gemini -> fallback

### Requirement: Consistencia de la ventana temporal y reconciliacion anti-Hawthorne

La tesis SHALL declarar una unica ventana temporal para la recoleccion de datos de
la campana experimental, coherente entre los capitulos 4.2, 4.4, 4.5 y 11.5, y
SHALL NOT presentar simultaneamente un trimestre completo y una corrida de "tres
dias habiles consecutivos" como si fueran la misma ventana sin explicar su
relacion. La afirmacion anti-Hawthorne SHALL reconciliarse con el procedimiento
efectivo (medicion en vivo con conocimiento diferido del operador y `debriefing`),
sin afirmar que el operador ignoraba ser cronometrado durante toda la ventana.

#### Scenario: Ventana temporal unica

- **WHEN** se comparan los capitulos 4.2, 4.4, 4.5 y 11.5
- **THEN** la ventana temporal declarada es una sola y consistente
- **AND** el trimestre y la corrida automatizada se relacionan de forma explicita

#### Scenario: Anti-Hawthorne reconciliado

- **WHEN** se lee la afirmacion sobre el efecto Hawthorne
- **THEN** describe el procedimiento efectivo de medicion y su conocimiento diferido por parte del operador
- **AND** no sostiene que el operador desconocia el cronometraje durante toda la campana

### Requirement: Instrumento unico de medicion manual del tiempo

La tesis SHALL describir el instrumento de medicion manual (`planilla de
cronometraje`) de forma unica y consistente en los capitulos 4.2, 4.6 y 7.3: una
medicion en vivo durante la atencion, cronometrada por el companero de par, con
redondeo hacia arriba. La tesis SHALL NOT describirlo simultaneamente como
"estimados" y "cronometrados", ni como "con exactitud al segundo" y "sin
fracciones". La seccion de reduccion de intervencion humana (7.3) SHALL NOT
derivar la intervencion del flujo automatizado de la planilla del flujo manual.

#### Scenario: Relato unico del instrumento

- **WHEN** se comparan las descripciones de la planilla en 4.2, 4.6 y 7.3
- **THEN** describen el mismo procedimiento de cronometraje en vivo con redondeo al alza
- **AND** no coexisten "estimados" con "cronometrados" ni "exactitud al segundo" con "sin fracciones"

#### Scenario: Intervencion automatizada no derivada del instrumento manual

- **WHEN** se lee la seccion de reduccion de intervencion humana (7.3)
- **THEN** la intervencion del flujo automatizado se sustenta en registros del propio flujo automatizado
- **AND** no se deriva de la planilla de cronometraje del flujo manual

### Requirement: Campana experimental presentada como realizada

La tesis SHALL presentar la campana experimental como ejecutada sobre datos reales
a lo largo del Capitulo 7 y del Anexo de corpus, y SHALL NOT presentarla como
trabajo futuro, pendiente o propuesta.

#### Scenario: Sin lenguaje de trabajo futuro

- **WHEN** se lee el Capitulo 7 y el Anexo de corpus en el PDF compilado
- **THEN** la campana se reporta como realizada con datos reales
- **AND** ningun pasaje la describe como pendiente o futura

### Requirement: Coherencia de los datos en los capitulos 7.2 y 1.6

La tesis SHALL reportar en el Capitulo 7.2 las metricas reales (exactitud 73,5 %,
macro-F1 0,5207, cinco clases) y SHALL corregir en el Capitulo 1.6 la mencion a
"tres sectores (Sistemas, Operaciones y Soporte Tecnico)" por las cinco categorias
canonicas, "Gemini 2.5 Flash" por `gemini-3.6-flash` y revisar la fecha "junio de
2026".

#### Scenario: 7.2 usa metricas reales

- **WHEN** se lee el Capitulo 7.2
- **THEN** reporta exactitud 73,5 %, macro-F1 0,5207 y cinco clases
- **AND** no reporta 92 %, 0,919 ni tres clases

#### Scenario: 1.6 sin tres sectores ni modelo stale

- **WHEN** se lee el Capitulo 1.6 (alcance y delimitaciones)
- **THEN** menciona las cinco categorias canonicas y no "tres sectores" con "Operaciones"
- **AND** el modelo declarado es `gemini-3.6-flash`, no "Gemini 2.5 Flash"
