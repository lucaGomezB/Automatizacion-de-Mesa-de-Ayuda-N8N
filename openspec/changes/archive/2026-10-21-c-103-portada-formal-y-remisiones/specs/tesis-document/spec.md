## ADDED Requirements

### Requirement: Identidad institucional de la portada

La portada de la tesis (`sections/00-portada.tex`) SHALL acreditar la identidad
institucional del trabajo: el logo de la UTN Facultad Regional Mendoza, el rótulo
"Trabajo Final de Carrera", los tres autores (Luca Gomez, Carla Bustos, Gonzalo
Sevilla) y los dos directores ("Prof. Alberto Cortez y Prof. Ariel Enferrel", en
ese orden, ambos con el tratamiento "Prof."). La portada SHALL tomar la fecha de
compilación mediante `\today` y MUST NOT hardcodear el año.

#### Scenario: Portada con logo y directores

- **WHEN** se inspecciona la primera página del PDF compilado
- **THEN** aparece el logo UTN-FRM y el rótulo "Trabajo Final de Carrera"
- **AND** figuran los autores Luca Gomez, Carla Bustos y Gonzalo Sevilla
- **AND** figuran los directores "Prof. Alberto Cortez y Prof. Ariel Enferrel"

#### Scenario: Fecha de compilación no hardcodeada

- **WHEN** se compila el documento con babel spanish
- **THEN** la fecha de la portada se genera con `\today` (p. ej. "20 de octubre de 2026")
- **AND** el archivo fuente no contiene un año fijo en la portada

### Requirement: Presupuesto de páginas preservado

La inserción del logo y los ajustes de portada MUST NOT alterar el total de
páginas del PDF: el documento SHALL seguir compilando en 103 páginas (±0).

#### Scenario: Conteo de páginas sin cambios

- **WHEN** se compila `main.tex` tras el change y se cuentan las páginas del PDF
- **THEN** el total es 103 páginas
- **AND** la portada sigue ocupando exactamente una página

### Requirement: Coherencia de metadatos PDF

Los metadatos del PDF (`preambles/preamble.tex`) SHALL ser coherentes con la
denominación "Trabajo Final". `pdfsubject` SHALL declarar "Trabajo Final —
Tecnicatura Universitaria en Programación" y `pdftitle`, `pdfauthor` y
`pdfkeywords` SHALL ser consistentes con esa denominación y con la autoría real.

#### Scenario: Metadatos coherentes

- **WHEN** se leen las propiedades del PDF compilado o el `\hypersetup` del preamble
- **THEN** `pdfsubject` es "Trabajo Final — Tecnicatura Universitaria en Programación"
- **AND** `pdfauthor` lista Luca Gomez, Carla Bustos y Gonzalo Sevilla
- **AND** no queda "Tesis de Grado" en los metadatos

### Requirement: Nomenclatura "Trabajo Final" en el documento

El documento SHALL usar la denominación "Trabajo Final" en lugar de "Tesis de
Grado" en el cuerpo del manuscrito y el preámbulo. La ruta real
`docs/Tesis/Correcciones/` MUST NOT alterarse, porque es una ruta de repositorio
válida.

#### Scenario: Sin "Tesis de Grado" en el manuscrito

- **WHEN** se buscan las ocurrencias de "Tesis de Grado" en `main.tex`, `preambles/preamble.tex` y `sections/*.tex`
- **THEN** no queda ninguna ocurrencia de "Tesis de Grado"
- **AND** la ruta `docs/Tesis/Correcciones/dictamen-correcciones.md` permanece intacta

### Requirement: Integridad de referencias cruzadas

Toda `\section` y `\subsection` de `sections/*.tex` SHALL tener un `\label`. Las
remisiones a capítulos y secciones SHALL resolverse con `\ref`/`\autoref` (o
`\cref` si el paquete ya está disponible) y MUST NOT escribirse a mano con números
fijos. La compilación SHALL producir cero referencias indefinidas y la prosa SHALL
denominar "Sección" (no "Capítulo"). El documento MUST conservar
`\documentclass{article}`.

#### Scenario: Cero remisiones duras

- **WHEN** se busca en `sections/*.tex` el patrón "Capítulo N" o "Sección N.N" en prosa
- **THEN** no queda ninguna remisión dura
- **AND** cada remisión se resuelve mediante una etiqueta `\label`

#### Scenario: Cero referencias indefinidas

- **WHEN** se compila el documento con XeLaTeX
- **THEN** el log no contiene advertencias de "undefined reference" ni "multiply defined label"
- **AND** toda `\ref`/`\autoref` apunta a una etiqueta existente

#### Scenario: Remisión de la cota de 45 s corregida

- **WHEN** se lee la remisión de la cota de 45 s en `07-resultados.tex`
- **THEN** apunta a la sección de métricas e instrumentos (4.6), donde la cota se enuncia
- **AND** no apunta a la sección 4.4 (población, muestra y corpus)

#### Scenario: Reubicación del capítulo 11 segura

- **WHEN** el capítulo 11 se mueve de posición (c-105)
- **THEN** ninguna referencia cruzada queda indefinida, porque todas usan etiquetas
- **AND** la numeración se recalcula automáticamente
