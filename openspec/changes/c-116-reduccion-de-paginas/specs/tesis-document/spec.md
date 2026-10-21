## MODIFIED Requirements

### Requirement: Presupuesto de páginas preservado

La reducción de páginas SHALL llevar el total del PDF a un máximo de **100
páginas**, medido con `pdfinfo main.pdf` sobre el documento completo (portada,
índices, glosario, cuerpo, referencias y anexos). El conteo MUST ser de 100
páginas o menos y MUST NOT exceder el tope vigente del plan de correcciones. La
portada SHALL seguir ocupando exactamente una página.

#### Scenario: Conteo de páginas sin cambios

- **WHEN** se compila `main.tex` tras el change y se ejecuta `pdfinfo main.pdf | grep Pages`
- **THEN** el total de páginas es 100 o menos
- **AND** la portada sigue ocupando exactamente una página

#### Scenario: Tope medido sobre el total

- **WHEN** se cuenta el total de páginas del PDF
- **THEN** el conteo incluye portada, índices, glosario, referencias y anexos
- **AND** no se computa un subconjunto (solo el cuerpo) para dar por cumplido el tope

## ADDED Requirements

### Requirement: Reducción sin pérdida de contenido científico

La reducción de páginas SHALL preservar la integridad científica del documento.
El change MUST NOT eliminar ni alterar: contenido científico (afirmaciones,
argumentos, interpretaciones y análisis), las figuras y tablas requeridas por el
conjunto de changes (incluidas las ocho figuras de c-80 y las tablas con su línea
de fuente), los números canónicos (exactitud 73,5 %, macro-F1 0,5207, reducción
71,2 %, W=363, r=0,9639, κ=0,87, universo 2.646, horas-persona 32,2 h), ni las
referencias bibliográficas. Las palancas admisibles son de forma: pasajes
duplicados, leyendas sobre-extendidas, listas redundantes, tamaño del glosario,
espaciado y compactación de anexos.

#### Scenario: Cifras canónicas intactas

- **WHEN** se busca en el PDF reducido cada número canónico (73,5 %, 0,5207, 71,2 %, W=363, 0,9639, 0,87, 2.646, 32,2 h)
- **THEN** todos siguen presentes con el mismo valor
- **AND** no se introducen cifras nuevas ni se retiran las existentes

#### Scenario: Figuras y tablas requeridas preservadas

- **WHEN** se inspecciona el PDF reducido
- **THEN** las ocho figuras y las nueve tablas del change set siguen renderizando
- **AND** ninguna figura o tabla requerida fue eliminada ni recortada

#### Scenario: Correcciones previas no revertidas

- **WHEN** se compara el manuscrito reducido contra la versión de partida
- **THEN** las correcciones de c-102..c-115 (números canónicos, cifras retiradas, acentuación, orden de capítulos, glosario y marco teórico) permanecen aplicadas
- **AND** no se reintroduce ningún valor retirado (9,5 %, 3.700, "Operaciones", W=0)

### Requirement: Verificación de compilación tras la reducción

La reducción SHALL verificarse sobre el PDF compilado. La compilación con XeLaTeX
SHALL producir `main.pdf` sin errores fatales, con cero referencias indefinidas y
cero etiquetas duplicadas en el registro. El conteo de páginas y la ausencia de
referencias indefinidas SHALL registrarse como evidencia de la verificación.

#### Scenario: Compilación sin errores fatales

- **WHEN** se compila `main.tex` con `latexmk -xelatex` (imagen `texlive-thesis`)
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene "undefined reference" ni "multiply defined label"

#### Scenario: Evidencia de verificación registrada

- **WHEN** se cierra el change
- **THEN** el conteo de páginas (`pdfinfo`) y el resultado de la verificación de referencias quedan registrados en las tareas
- **AND** el conteo es 100 o menos con cero referencias indefinidas
