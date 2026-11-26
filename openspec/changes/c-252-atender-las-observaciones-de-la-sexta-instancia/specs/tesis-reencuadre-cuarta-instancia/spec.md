## ADDED Requirements

### Requirement: Cronología día por día de la campaña manual con evidencia fechada (D-01 de c-252)

El documento SHALL declarar la cronología **día por día** de la campaña manual del corpus real, referida
al régimen (a) (119 casos de correo y formulario): recolección, redacción disociada, doble etiquetado con
consenso supervisado, cronometraje manual por pares (cada mitad y cada operador) y corridas automatizadas,
con la evidencia de cada fecha. La fecha del cronometraje manual SHALL declararse en §4.2
(`04-marco-metodologico.tex:14`), §4.4 (`:46`), la Tabla 4 (`tab:procedencia-numeros`, `:71`) y la Figura
11 (`fig:cronograma`, `12-anexos.tex:53`) como **declaración de los autores acotada por el commit del
09/10/2026** (`ea62576`), y MUST NOT extenderse a todo octubre en la Figura 11 (el 09/10 es su cota
superior). La evidencia fechada SHALL citarse explícitamente: commit `68d06ec` (2026-06-11, corpus
sintético) y commit `ea62576` (2026-10-09, corpus real versionado con `tiempo_manual_s`). El documento
SHALL declarar que los 165,3 s de la versión del 3 de julio de 2026 provienen del corpus sintético (simulado)
y no constituyen una medición real del corpus vigente, y SHALL consignarlo en la Nota de versiones (no hay un
operador real que nombrar). El orden real fue **automatizado primero (02/10) y manual después (09/10, posterior
al doble etiquetado)**: §4.2, §4.8 (`04-marco-metodologico.tex:117-131`, primera amenaza y explicaciones
rivales) y §9.1 (`08-discusion.tex:22`) SHALL corregirse para reflejar ese orden, declarando que el cronometraje
manual posterior al etiquetado sub-estima el tiempo manual y deja la reducción como cota inferior. El contenido
MUST NOT inventarse.

#### Scenario: Cronología día por día presente con evidencia por fecha

- **WHEN** se leen §4.2 y §4.4 (`04-marco-metodologico.tex:14`, `:46`) y la Tabla 4 (`tab:procedencia-numeros`)
- **THEN** figura una cronología día por día (recolección, redacción, doble etiquetado, cronometraje por pares, corrida automatizada) con la evidencia de cada fecha, y la fecha del cronometraje manual se declara como declaración de los autores acotada por el commit `ea62576` (09/10/2026)

#### Scenario: Commits de evidencia citados

- **WHEN** se ejecuta `rg -n "68d06ec|ea62576" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** aparecen ambos commits como evidencia fechada, asociados respectivamente al corpus sintético y al corpus real versionado

#### Scenario: Procedencia sintética de los 165,3 s declarada

- **WHEN** se ejecuta `rg -n "165,3" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** el pasaje de la Nota de versiones declara que los 165,3 s provienen del corpus sintético (simulado), no de una medición real del corpus vigente, y no los presenta como atribuibles a un operador real

#### Scenario: Figura 11 no extiende la barra manual a todo octubre

- **WHEN** se lee la Figura 11 (`fig:cronograma`, `12-anexos.tex:52-53`) y su nota de fuente
- **THEN** la barra de la campaña manual no se extiende más allá del 09/10, y el texto declara que esa es su cota superior

### Requirement: Definición del tiempo manual registrada sin sugerir cambio de valores (D-02 de c-252)

El documento SHALL declarar cuál de las dos descripciones del tiempo manual es la correcta —(a) lectura
cronometrada más carga "estimada… en el orden de 10 s" (v1.6.4) o (b) clasificación pura sin componente
de carga (v1.6.5)— y SHALL registrar en la Nota de versiones (Anexo I.1, `12-anexos.tex:239-247`) por qué
la otra figuró en una versión entregada al tribunal, con el mismo criterio que los retiros anteriores. Las
cifras son idénticas en ambas versiones (media 61,6 s, telefonía 87,2 s, mínimo 10 s, 199/200 múltiplos de
5 s); el documento MUST NOT presentar una corrección de datos que no ocurrió. La redacción "retirado el
componente de carga" (`04-marco-metodologico.tex:127`) y "componente que la presente versión ya no
contempla" (`12-anexos.tex:354`) SHALL reemplazarse por una forma que no sugiera un cambio en los valores.
La Tabla 3 (`tab:variables`, `04-marco-metodologico.tex:31`), la octava amenaza (`:131`), §8.1
(`07-resultados.tex:38`) y `:285` SHALL ser coherentes con la descripción elegida. OQ-2 RESUELTA: el componente
nunca se sumó, por lo que la cifra primaria de la sub-hipótesis 1 SHALL mantenerse en 71,2 % (no 65,6 %) y la
v1.6.4 SHALL declararse inexacta.

#### Scenario: Descripción correcta elegida y registrada

- **WHEN** se lee la Nota de versiones (Anexo I.1, `12-anexos.tex:239-247`)
- **THEN** registra cuál descripción (con carga vs sin carga) es la correcta y por qué la otra figuró en una versión entregada, con el mismo criterio de los retiros anteriores

#### Scenario: Sin redacción que sugiera corrección de datos

- **WHEN** se ejecuta `rg -n "retirado el componente de carga|ya no contempla|componente de carga" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** no queda una redacción que sugiera que el componente de carga fue sustraído de los valores; el tiempo manual se describe de forma consistente en Tabla 3, octava amenaza, §8.1 y `:285`

#### Scenario: Cifra primaria coherente con la decisión

- **WHEN** se lee el informe de la sub-hipótesis 1 y la discusión de la cifra primaria
- **THEN** OQ-2 resolvió "nunca se sumó": se conserva 71,2 % y la v1.6.4 se declara inexacta; la cifra primaria no baja a 65,6 %

### Requirement: Origen del régimen (a) sin léxico de organización y con deber de confidencialidad (D-03 de c-252)

El documento SHALL declarar que los incidentes del régimen (a) provienen del ámbito laboral de los reportantes
del círculo, disociados de forma irreversible desde la recolección. SHALL mencionar el deber de
confidencialidad del art. 10 de la Ley 25.326 y SHALL explicar el léxico corporativo presente (§4.4, §7.2
`11-aspectos-legales.tex:18`, caso R015 `07-resultados.tex:277`). La caracterización "del sector servicios y con sede en la provincia de Mendoza"
SHALL retirarse de §1.2 (`01-introduccion.tex:16`), las conclusiones (`09-conclusiones.tex:52`) y la
limitación (`01-introduccion.tex:76`) o SHALL explicarse a qué se refiere. El cambio de origen respecto de
la v1.6.4 SHALL registrarse en el Anexo I.1 con el mismo criterio que los retiros anteriores. La
procedencia declarada SHALL incorporar el visto bueno escrito del director antes de fijar fecha. El
contenido MUST NOT inventarse y MUST NOT contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Ámbito laboral del régimen (a) declarado

- **WHEN** se lee §4.4 (`04-marco-metodologico.tex:46`) y los pasajes de procedencia
- **THEN** el texto declara explícitamente que los incidentes del régimen (a) provienen del ámbito laboral de los reportantes, disociados desde la recolección, en una única formulación coherente

#### Scenario: Frase "del sector servicios y con sede en la provincia de Mendoza" resuelta

- **WHEN** se ejecuta `rg -n "del sector servicios y con sede en la provincia de Mendoza" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no quedan coincidencias sin aclaración: la frase se retiró o se explica a qué se refiere, de forma coherente con el origen declarado

#### Scenario: Deber de confidencialidad citado (ámbito laboral)

- **WHEN** se ejecuta `rg -n "art.*10|art.culo 10|confidencialidad" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** el art. 10 y el deber de confidencialidad se citan entre los principios generales del capítulo legal

#### Scenario: Cambio de origen registrado en el Anexo I.1

- **WHEN** se lee la Nota de versiones (Anexo I.1, `12-anexos.tex:239-247`)
- **THEN** registra el cambio de origen del régimen (a) respecto de la v1.6.4 como corrección de veracidad

### Requirement: Coherencia y redacción de la sexta instancia (D-06 de c-252)

El documento SHALL aclarar cómo A1 y T1 se cronometraron "por pares" (`04-marco-metodologico.tex:16`)
cuando cada uno trabajó en su domicilio, de modo que no quede una contradicción interna. La atribución de
autoría de las 81 reconstrucciones SHALL unificarse entre "redactadas por los autores" (Anexo F,
`12-anexos.tex:149`) y "por uno de los autores" (`04:129`, `09:54`, `06:54`, `12:241`) conforme a la
decisión de autoría. En §8.1 (`07-resultados.tex:38`) la fórmula "respaldados por" SHALL reemplazarse por
la fórmula de §4.5. En §7.5 (`11-aspectos-legales.tex:46`) la afirmación "titulares… distintos de los
autores" SHALL corregirse porque los autores también son reportantes. La forma "registro histórico/retirado"
(`12-anexos.tex:247`) SHALL reemplazarse por una forma sin barra que no yuxtaponga dos calificaciones.

#### Scenario: Cronometraje "por pares" sin contradicción con el domicilio

- **WHEN** se lee `04-marco-metodologico.tex:16` y el pasaje del domicilio
- **THEN** el texto explica cómo se cronometraron mutuamente A1 y T1 trabajando cada uno en su domicilio, sin contradicción

#### Scenario: Atribución de autoría unificada

- **WHEN** se ejecuta `rg -n "redactadas por (los autores|uno de los autores)|por ese autor" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** todas las menciones atribuyen la redacción de las 81 reconstrucciones de la misma manera, conforme a la decisión de autoría registrada

#### Scenario: "Respaldados por" reemplazado por la fórmula de §4.5

- **WHEN** se ejecuta `rg -n "respaldados por" "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex"`
- **THEN** §8.1 usa la misma fórmula que §4.5 (`04-marco-metodologico.tex:66`, `:79`) para el estado del registro primario

#### Scenario: "Titulares… distintos de los autores" corregido y barra retirada

- **WHEN** se ejecuta `rg -n "distintos de los autores|hist.rico/retirado" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** §7.5 no afirma que los autores no son titulares/reportantes, y no queda la forma "histórico/retirado" con barra