## ADDED Requirements

### Requirement: Tabla comparativa de trabajos académicos de clasificación de tickets

La subsección "Trabajos académicos previos sobre clasificación de tickets"
(`\label{subsec:trabajos-academicos}`) de `03-estado-del-arte.tex` SHALL presentar
una tabla comparativa de trabajos académicos con las columnas `trabajo | enfoque |
corpus/idioma | métrica reportada | condición`. La tabla SHALL reemplazar la
oración que agrupa varios trabajos en `03:32` (Paket et al., Liu et al., Zangari et
al., Colavito et al.) o complementarla, de modo que la información de corpus,
métrica y condición de cada trabajo quede expuesta en la grilla. La tabla MUST NOT
duplicar la tabla comercial `tab:comparativa`, que compara soluciones comerciales
(Zendesk, Freshdesk, Jira, ServiceNow, osTicket) y no trabajos académicos. Cada
fila SHALL reportar corpus, métrica y condición cuando la fuente documentada las
establezca.

#### Scenario: Tabla con las columnas requeridas

- **WHEN** se lee la subsección `subsec:trabajos-academicos` en el PDF compilado
- **THEN** existe una tabla con las columnas trabajo, enfoque, corpus/idioma, métrica reportada y condición
- **AND** la tabla tiene una fila por cada trabajo académico incluido, con al menos una fila de datos

#### Scenario: Los agrupamientos quedan expuestos

- **WHEN** se comparan los trabajos agrupados en `03:32` contra las filas de la tabla
- **THEN** cada trabajo de ese agrupamiento aparece como una fila propia con su corpus/idioma, métrica y condición
- **AND** la afirmación genérica que los agrupaba deja de ser la única fuente de su comparación

#### Scenario: Sin duplicar la tabla comercial

- **WHEN** se inspeccionan las dos tablas del Capítulo 3
- **THEN** `tab:comparativa` sigue comparando soluciones comerciales
- **AND** la tabla nueva compara trabajos académicos y no repite las filas comerciales

### Requirement: Procedencia de datos y regla de dato no reportado

Toda celda de la tabla comparativa SHALL provenir de la prosa de la tesis, de una
entrada de `Bibliography_base.bib` o de una fuente verificable accesible por DOI o
página de aterrizaje. Donde un dato (corpus, idioma, métrica o condición) no pueda
establecerse con una fuente, la celda MUST declararse explícitamente como "no
reportado en el alcance revisado", en consistencia con la regla de vacancia acotada
de c-110. El documento MUST NOT fabricar corpus, métricas ni condiciones, ni
atribuir a un trabajo un resultado que su fuente no reporte. El change MUST NOT
agregar entradas nuevas a `Bibliography_base.bib` salvo que la fuente nueva resuelva
por DOI.

#### Scenario: Dato no establecido marcado como no reportado

- **WHEN** se lee una celda de la tabla cuya fuente no explicita el dato
- **THEN** la celda dice "no reportado en el alcance revisado"
- **AND** no se completa con un valor estimado, inferido sin fuente ni supuesto

#### Scenario: Sin fabricación ni atribución indebida

- **WHEN** se contrasta cada valor de la tabla contra su fuente declarada
- **THEN** todo valor numérico coincide con el reportado por la fuente
- **AND** no se introduce ningún corpus, métrica o condición inexistente en la fuente

#### Scenario: Bibliografía sin altas indebidas

- **WHEN** se inspecciona `Bibliography_base.bib` tras el change
- **THEN** no hay entradas nuevas, salvo una fuente nueva que resuelva por DOI
- **AND** todas las claves citadas en la tabla existen como entradas del `.bib`

### Requirement: Neutralidad de páginas al incorporar la tabla

La incorporación de la tabla comparativa SHALL ser neutral en páginas: el total del
PDF MUST permanecer en 100 páginas o menos, medido con `pdfinfo main.pdf` sobre el
documento completo. El texto redundante que la tabla reemplaza (en particular la
oración agrupada de `03:32` y la repetición de corpus/métrica en la prosa de la
misma subsección) SHALL retirarse o condensarse en el mismo capítulo para compensar
el espacio de la tabla. El change MUST NOT exceder el tope de páginas vigente.

#### Scenario: Total de páginas dentro del tope

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se ejecuta `pdfinfo main.pdf | grep Pages`
- **THEN** el total es 100 páginas o menos
- **AND** la portada sigue ocupando exactamente una página

#### Scenario: Compensación en el mismo capítulo

- **WHEN** se compara la prosa de la subsección antes y después del change
- **THEN** la redundancia que la tabla reemplaza fue retirada o condensada en el Capítulo 3
- **AND** no se trasladó contenido científico requerido a otra sección ni se eliminó una afirmación sustantiva

#### Scenario: Compilación sin errores fatales

- **WHEN** se compila `main.tex` con `latexmk -xelatex`
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene "undefined reference" ni "multiply defined label"

### Requirement: Alcance del archivo y secuencia respecto de c-111

El change SHALL limitarse a `docs/Tesis/v9 (IA)/paper/sections/03-estado-del-arte.tex`.
El change MUST NOT editar `preambles/`, `main.tex`, el memo canónico, `CHANGES.md`
ni `dictamen-correcciones.md`. La tabla SHALL preexistir al change de versionado y
etiquetado: este change MUST aprobarse y aplicarse antes de `c-111`.

#### Scenario: Un solo archivo fuente editado

- **WHEN** se inspecciona el diff del change
- **THEN** el único archivo `.tex` modificado es `03-estado-del-arte.tex`
- **AND** no se modifican el preámbulo, `main.tex` ni los documentos de gobierno

#### Scenario: Secuencia respecto del tag

- **WHEN** se planifica el orden de aplicación
- **THEN** este change figura antes de `c-111`
- **AND** el tag de `c-111` no se crea hasta que la tabla esté aplicada y verificada
