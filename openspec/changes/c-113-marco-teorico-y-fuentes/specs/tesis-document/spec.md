## ADDED Requirements

### Requirement: Fundamentación de los conceptos de BPA e iPaaS

El capítulo de marco teórico (`02-marco-teorico.tex`, sección 2.3) SHALL fundamentar
con una cita verificable, o reformular de forma explícita como glosa propia, las
definiciones de "automatización de procesos empresariales" (BPA) y de "plataformas de
integración como servicio" (iPaaS). El texto MUST NOT presentar esas definiciones como
aserciones sin fuente. Toda cita nueva SHALL existir como entrada en
`Bibliography_base.bib` y resolver por DOI o página de aterrizaje del editor.

#### Scenario: Definiciones fundamentadas o reformuladas como glosa propia

- **WHEN** se lee la sección 2.3 del PDF compilado
- **THEN** la definición de BPA y la de iPaaS están respaldadas por una cita verificable o rotuladas explícitamente como glosa propia
- **AND** ninguna de las dos queda enunciada como afirmación sin fuente ni como atribución a un tercero sin cita

#### Scenario: Citas nuevas verificables

- **WHEN** se inspeccionan las citas incorporadas en la sección 2.3
- **THEN** cada clave citada existe como entrada en `Bibliography_base.bib`
- **AND** cada entrada nueva incluye `author`, `title`, `year` y el campo de publicación más `doi` o `url`, y resuelve por DOI o página de aterrizaje

### Requirement: Formulación jurídica exacta de la soberanía sobre los datos

La sección 1.7 (`01-introduccion.tex`) SHALL sustituir la atribución del "principio de
soberanía digital" a la Ley 25.326 por la formulación jurídica que la ley efectivamente
enuncia (control sobre los datos personales y su tratamiento conforme a la normativa de
protección de datos). El texto MUST NOT afirmar que la Ley 25.326 promueve la "soberanía
digital", por ser un principio que una ley de protección de datos no enuncia.

#### Scenario: Atribución imprecisa eliminada

- **WHEN** se busca la expresión "soberanía digital" en `01-introduccion.tex` y en el PDF compilado
- **THEN** no aparece atribuida a la Ley 25.326 como principio promovido por esa norma
- **AND** el pasaje enuncia el control sobre los datos personales y su tratamiento conforme a la normativa de protección de datos

#### Scenario: Formulación coherente con la fuente legal citada

- **WHEN** se lee el pasaje corregido de la sección 1.7
- **THEN** la formulación jurídica exacta se apoya en la entrada vigente `Ley25326_2000`
- **AND** no se atribuye a la ley un principio que su texto no contiene

### Requirement: Cita canónica de la definición de alucinación

La sección 2.4 (`02-marco-teorico.tex`) SHALL respaldar la definición de "alucinación"
con una cita canónica verificable sobre el fenómeno en modelos generativos de lenguaje.
La cita SHALL existir como entrada en `Bibliography_base.bib` y resolver por DOI. El
texto MUST NOT presentar la definición como aserción sin fuente.

#### Scenario: Definición con cita canónica

- **WHEN** se lee la definición de "alucinación" en la sección 2.4 del PDF compilado
- **THEN** la definición cita una referencia canónica sobre el fenómeno
- **AND** la afirmación no queda sostenida como aserción sin fuente

#### Scenario: Entrada verificable por DOI

- **WHEN** se inspecciona la entrada incorporada para la definición de alucinación
- **THEN** la entrada existe en `Bibliography_base.bib` con metadatos completos
- **AND** su DOI resuelve a la publicación real

### Requirement: Alcance acotado y justificado del eje de reconocimiento automático del habla

La sección 2.5 (`02-marco-teorico.tex`) SHALL recortarse al mínimo conceptual necesario
o SHALL justificar explícitamente por qué se conserva el eje de reconocimiento
automático del habla (ASR) pese a que la transcripción efectiva la provee un servicio
externo. Si el eje se conserva, el texto SHALL declarar su función como marco conceptual
del canal telefónico y SHALL NOT desarrollarlo como si fuera un componente integrado a
la implementación. El texto MUST NOT presentar el ASR como un eje que el sistema
efectivamente integra.

#### Scenario: Eje recortado o justificado

- **WHEN** se lee la sección 2.5 del PDF compilado
- **THEN** el eje se recorta al mínimo conceptual o el texto justifica explícitamente su permanencia como marco del canal telefónico
- **AND** se declara que la transcripción efectiva la provee un servicio externo y no el sistema desarrollado

#### Scenario: Sin desarrollo desproporcionado respecto de su uso

- **WHEN** se compara la extensión del eje de ASR con la de los ejes efectivamente usados en la implementación
- **THEN** el eje no se desarrolla como un componente del sistema propuesto
- **AND** no se afirma que el ASR permita automatizar la captura del canal telefónico del sistema

### Requirement: Terminología correcta de la trazabilidad

El documento SHALL emplear el término "trazabilidad auditable". Ningún archivo de sección
de `paper/sections/` MUST contener la expresión "trazabilidad auditiva".

#### Scenario: Término corregido en todo el cuerpo

- **WHEN** se busca la expresión "trazabilidad auditiva" en `paper/sections/*.tex` y en el PDF compilado
- **THEN** no hay coincidencias
- **AND** donde correspondía se emplea "trazabilidad auditable"
