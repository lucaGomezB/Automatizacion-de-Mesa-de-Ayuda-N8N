## ADDED Requirements

### Requirement: Capitulo de cumplimiento normativo ISO/NIST

La tesis SHALL incluir un capitulo/seccion de cumplimiento que presente el mapeo de
ISO/IEC 27001:2022 + ISO/IEC 27002:2022 y de NIST CSF 2.0, con el estado actual de
alineacion, las brechas identificadas y la hoja de ruta. El capitulo SHALL declarar
los estandares de referencia adoptados (ISO/IEC 27001:2022, ISO/IEC 27002:2022,
NIST CSF 2.0, ISO/IEC 27701 y Ley 25.326). El mapeo ISO SHALL agrupar los controles
por tema (Organizacional 5.x, Personas 6.x, Fisico 7.x, Tecnologico 8.x) y el perfil
NIST SHALL cubrir las seis funciones (GV, ID, PR, DE, RS, RC) con su nivel de
madurez. Cada tabla del capitulo SHALL declarar su linea de fuente.

#### Scenario: Capitulo de cumplimiento presente

- **WHEN** se busca en `docs/Tesis/v9 (IA)/paper/sections/` y en el PDF compilado
  contenido sobre ISO 27001/27002 y NIST CSF 2.0
- **THEN** existe una seccion de cumplimiento con el mapeo ISO y el perfil NIST
- **AND** la seccion declara los estandares adoptados y su estado actual, brechas y hoja de ruta

#### Scenario: Mapeo ISO por tema

- **WHEN** se lee la tabla de mapeo ISO/IEC 27002:2022 del capitulo
- **THEN** los controles se agrupan por tema (Organizacional, Personas, Fisico, Tecnologico)
- **AND** cada grupo declara su estado de alineacion y la evidencia o brecha principal
- **AND** la tabla no reproduce los 93 controles uno por uno

#### Scenario: Perfil NIST CSF 2.0 con las seis funciones

- **WHEN** se lee el perfil de alineacion con NIST CSF 2.0
- **THEN** figuran las seis funciones GV, ID, PR, DE, RS y RC
- **AND** cada funcion declara una subcategoria representativa y su nivel de madurez

### Requirement: Regla de lenguaje de alineacion sin certificacion

El capitulo de cumplimiento SHALL usar el vocabulario "alineado con" y "controles
mapeados a" (o "grado de alineacion" y "brecha identificada"). El documento MUST NOT
declarar "certificado", "certificacion", "compliant", "conforme" ni "cumple ISO/NIST".
El capitulo SHALL declarar de forma explicita que la evaluacion identifica alineacion y
brechas y que no constituye una certificacion ni una auditoria de conformidad.

#### Scenario: Terminos de certificacion ausentes

- **WHEN** se busca en los `.tex` del capitulo y en el PDF compilado las palabras
  "certificado", "certificacion", "compliant" y "conforme"
- **THEN** no aparecen como una declaracion de conformidad del sistema
- **AND** el capitulo usa "alineado con" y "controles mapeados a"

#### Scenario: Descargo de certificacion presente

- **WHEN** se lee la introduccion del capitulo de cumplimiento
- **THEN** el texto declara que es una evaluacion de alineacion, no una certificacion
- **AND** no afirma que exista una auditoria de certificacion

### Requirement: Neutralidad de paginas del contenido de cumplimiento

El capitulo de cumplimiento SHALL ser neutral en paginas: el total del PDF compilado
MUST NOT superar las 100 paginas. El capitulo SHALL absorber o reemplazar contenido
existente para compensar su extension, en particular la narracion de la subseccion
11.4 "Seguridad tecnica" de `11-aspectos-legales.tex`, cuya evidencia de control se
pliega al mapeo ISO. El change MUST NOT eliminar contenido cientifico, numeros
canonicos, figuras, tablas con linea de fuente ni ninguna correccion de c-102 a c-117.

#### Scenario: Tope de paginas preservado

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se ejecuta
  `pdfinfo main.pdf | grep Pages`
- **THEN** el total de paginas es 100 o menos
- **AND** el conteo no aumenta respecto del estado de partida

#### Scenario: Reemplazo de la narracion de seguridad tecnica

- **WHEN** se compara `11-aspectos-legales.tex` con el estado previo al change
- **THEN** la prosa de la subseccion 11.4 "Seguridad tecnica" fue condensada o plegada al mapeo de controles
- **AND** su evidencia tecnica permanece en la tabla de mapeo ISO

#### Scenario: Contenido canonico preservado

- **WHEN** se revisa el PDF compilado tras el change
- **THEN** el numero de figuras sigue siendo 8
- **AND** los numeros canonicos de la tesis no cambiaron
- **AND** las tablas conservan su linea de fuente

#### Scenario: Cero referencias indefinidas

- **WHEN** se revisa el log de compilacion con XeLaTeX
- **THEN** no hay advertencias de "undefined reference" ni "multiply defined label"

### Requirement: Coherencia del capitulo de cumplimiento con el marco legal

El capitulo de cumplimiento SHALL ser coherente con el Capitulo de aspectos legales
(`11-aspectos-legales.tex`). SHALL remitir a las subsecciones legales mediante
`\autoref` y MUST NOT duplicar ni contradecir su narrativa juridica (Ley 25.326,
transferencia internacional, derechos ARCO, base de licitud).

#### Scenario: Remision sin duplicacion

- **WHEN** se lee el capitulo de cumplimiento
- **THEN** remite al marco legal del Capitulo 11 mediante referencias cruzadas
- **AND** no reproduce en extenso el marco normativo ya expuesto en 11.1-11.5

#### Scenario: Coherencia de cifras y hechos legales

- **WHEN** se comparan las menciones legales del capitulo de cumplimiento con las de 11.3 y 11.5
- **THEN** las referencias a la Ley 25.326, la transferencia internacional y los plazos ARCO son consistentes
- **AND** no se introducen afirmaciones juridicas contradictorias

### Requirement: Trazabilidad de los controles a los changes archivados

El mapeo del capitulo de cumplimiento SHALL vincular cada control implementado con el
change archivado que lo cerro (C-61 a C-66) o con el artefacto versionado del
repositorio que lo evidencia. Las brechas residuales de tipo organizacional SHALL
declararse como responsabilidad de la organizacion adoptante, fuera del alcance del
repositorio.

#### Scenario: Controles trazables a los changes archivados

- **WHEN** se lee la hoja de ruta del capitulo de cumplimiento
- **THEN** los controles cerrados se asocian a los changes C-61 a C-66 o a su artefacto
- **AND** se distinguen de las brechas residuales

#### Scenario: Brechas organizacionales atribuidas al adoptante

- **WHEN** se leen las brechas residuales del capitulo
- **THEN** las de tipo organizacional (personas 6.x, fisicos 7.x, revision independiente) se declaran responsabilidad de la organizacion adoptante
- **AND** no se presentan como controles implementados en el repositorio
