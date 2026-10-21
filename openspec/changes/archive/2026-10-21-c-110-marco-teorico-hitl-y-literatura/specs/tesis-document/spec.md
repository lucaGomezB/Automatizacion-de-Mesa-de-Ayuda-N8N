## ADDED Requirements

### Requirement: Protocolo de revisión de literatura declarado y trazable

El capítulo de estado del arte (`03-estado-del-arte.tex`) SHALL declarar el
protocolo con el que se construyó la revisión: bases de datos o repositorios
consultados, cadenas de búsqueda, criterios de inclusión y de exclusión, período
cubierto y fecha de corte. El protocolo SHALL registrarse además en una bitácora
de búsqueda versionada bajo `docs/Tesis/Correcciones/`, con una entrada por
consulta (base, cadena, fecha y resultado). El protocolo descrito en el texto MUST
ser consistente con la bitácora: no puede declararse una base, cadena o criterio
que la bitácora no registre, y la bitácora MUST NOT contener entradas que el texto
no mencione.

#### Scenario: Protocolo presente en el capítulo

- **WHEN** se lee la revisión de literatura en `03-estado-del-arte.tex`
- **THEN** el texto enuncia las bases o repositorios consultados, las cadenas de búsqueda, los criterios de inclusión y exclusión, el período y la fecha de corte
- **AND** la formulación permite a un lector reproducir la búsqueda

#### Scenario: Bitácora de búsqueda reproducible

- **WHEN** se lee la bitácora de búsqueda bajo `docs/Tesis/Correcciones/`
- **THEN** cada consulta registra base, cadena, fecha y resultado
- **AND** el conjunto de bases, cadenas y criterios coincide con los declarados en el capítulo

### Requirement: Afirmación de vacancia acotada al alcance revisado

Toda afirmación de vacancia o inexistencia en el estado del arte (en particular
"no existe artículo arbitrado 2023-2026 que evalúe Google Gemini sobre tickets de
soporte en español") SHALL formularse de manera relativa al alcance efectivamente
revisado: SHALL declarar las fuentes o bases consultadas, las cadenas empleadas y
la fecha de corte, y SHALL enmarcarse como "en las fuentes consultadas hasta la
fecha de corte". El documento MUST NOT presentar la vacancia como una inexistencia
absoluta ni global. Cuando la vacancia se reutilice como motivación en otra
sección, esa mención SHALL remitir al alcance declarado en el estado del arte.

#### Scenario: Vacancia relativa y con alcance declarado

- **WHEN** se lee la afirmación de vacancia en `03-estado-del-arte.tex`
- **THEN** declara las bases consultadas, las cadenas de búsqueda y la fecha de corte
- **AND** la formula como relativa al alcance revisado, no como inexistencia absoluta

#### Scenario: Reutilización de la vacancia acotada

- **WHEN** la vacancia se usa como motivación en otra sección del documento
- **THEN** la mención remite al alcance declarado en el estado del arte
- **AND** no repite la vacancia como una afirmación de inexistencia sin acotar

### Requirement: Subsección teórica de human-in-the-loop con fuentes

El marco teórico (`02-marco-teorico.tex`) SHALL incluir una subsección sobre
human-in-the-loop que defina el concepto, distinga grados de autonomía (desde la
supervisión total hasta la operación autónoma con revisión selectiva) y fundamente
cada aserción con al menos una fuente citada. Al menos una fuente SHALL abordar la
interacción humano-IA o el aprendizaje con intervención humana. El texto MUST NOT
introducir el término sin definición ni sostener los grados de autonomía como
aseveración propia sin respaldo.

#### Scenario: Definición y grados de autonomía

- **WHEN** se lee la subsección de human-in-the-loop en `02-marco-teorico.tex`
- **THEN** el texto define el concepto
- **AND** distingue al menos dos grados de autonomía de forma explícita

#### Scenario: Aserciones respaldadas por fuentes

- **WHEN** se lee la subsección de human-in-the-loop
- **THEN** la definición y los grados de autonomía se apoyan en al menos una cita por aserción principal
- **AND** cada clave citada existe como entrada en `Bibliography_base.bib` y resuelve por DOI o página de aterrizaje

#### Scenario: Recuento de ejes consistente

- **WHEN** se lee el párrafo introductorio del marco teórico
- **THEN** el número de ejes temáticos declarado coincide con el número de subsecciones presentes
- **AND** la subsección de human-in-the-loop queda incluida en ese recuento
