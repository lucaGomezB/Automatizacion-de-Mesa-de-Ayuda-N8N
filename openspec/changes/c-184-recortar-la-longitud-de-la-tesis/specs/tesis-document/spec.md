## MODIFIED Requirements

### Requirement: Presupuesto de páginas preservado

El total de paginas del PDF de la tesis SHALL tender al tope vigente de paginas, que SHALL declararse en un unico lugar: la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`, con su regla de medicion, su valor, su fuente (exigencia de la catedra o decision del equipo) y su fecha. La regla vigente SHALL ser: metrica = **total del PDF**, medido con `pdfinfo main.pdf | grep Pages` o un conteo equivalente de saltos de pagina del PDF; valor = **100 paginas**; fuente = **exigencia de la catedra**, declarada por el autor el 2026-10-27 (G0.1); fecha = 2026-10-27. La metrica superada **cuerpo sin anexos <= 100** (rama (b) del 2026-10-26) MUST NOT usarse para declarar cumplimiento ni presentarse como la regla vigente; el conteo de cuerpo sin anexos SHALL conservarse solo como informacion complementaria del libro mayor. Para la release vigente `v1.2.8` el total medido SHALL consignarse como **118 paginas** (cuerpo 107, anexos 11), con un exceso de **+18 sobre el tope de 100** del total. Cuando el total supere el valor del tope, el exceso SHALL estar declarado y honrado por decision registrada de los autores, con su magnitud y fecha, y SHALL defenderse ante la catedra; un exceso no declarado MUST NOT presentarse como cumplimiento, y una reduccion que no alcance el tope no constituye incumplimiento mientras el exceso quede declarado y honrado. La portada SHALL seguir ocupando exactamente una pagina. Una reduccion para acercarse al tope MUST NOT eliminar contenido cientifico, numeros canonicos, figuras o tablas requeridas, referencias ni correcciones previas, y MUST NOT dejar referencias colgadas (`\ref` o `\autoref` sin destino) ni listados de codigo removidos con referencias en la prosa.

#### Scenario: Conteo de páginas sin cambios

- **WHEN** se compila `main.tex` en el entorno de registro y se ejecuta `pdfinfo main.pdf | grep Pages` (o el conteo equivalente de saltos de pagina del PDF) sobre el PDF de la release
- **THEN** el total de paginas se mide sobre el PDF completo y queda registrado en el libro mayor con su regla, su valor, su fuente y su fecha
- **AND** la portada sigue ocupando exactamente una pagina
- **AND** cuando el total supera las 100 paginas, la magnitud del exceso, su fecha y la decision de sostenerlo quedan registradas, y el requisito no se reescribe para dar el tope por cumplido

#### Scenario: Tope medido sobre el total

- **WHEN** se cuenta el total de paginas del PDF
- **THEN** el conteo incluye portada, indices, glosario, cuerpo, referencias y anexos
- **AND** no se computa un subconjunto (por ejemplo, solo el cuerpo o el cuerpo sin anexos) para dar por cumplido el tope

#### Scenario: Tope total declarado en un unico lugar

- **WHEN** se lee la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`
- **THEN** figuran la metrica (total del PDF), el valor (100 paginas), la fuente (exigencia de la catedra) y la fecha
- **AND** ninguna otra regla de tope de paginas se presenta como vigente

#### Scenario: Exceso honrado y defendido

- **WHEN** el total del PDF de la release supera las 100 paginas
- **THEN** el registro declara la magnitud del exceso, su fecha y la decision de los autores de sostenerlo y defenderlo
- **AND** el PDF no se presenta como si cumpliera el tope sin exceso

#### Scenario: Contabilidad de una release sobre el total

- **WHEN** se consigna el resultado de paginas de una release (por ejemplo `v1.2.8`) en el libro mayor o en `CHANGES.md`
- **THEN** el numero reportado como exceso usa la metrica del total del PDF (118 total, +18 sobre 100)
- **AND** la cuenta por cuerpo sin anexos de la rama (b) no se usa como base del cumplimiento ni se presenta como la regla vigente
- **AND** la fila de c-169 del libro mayor queda corregida a la metrica del total

#### Scenario: Reduccion sin perdida de contenido ni referencias colgadas

- **WHEN** se compacta el documento para acercarlo al tope
- **THEN** los numeros canonicos, las figuras y tablas requeridas, las referencias y las correcciones previas permanecen
- **AND** no queda ninguna referencia colgada ni un listado de codigo removido con una referencia en la prosa
- **AND** las palancas aplicadas son de forma (indices, listas, tamano de anexos, ancho de figuras, espaciado)

#### Scenario: Portada de una sola pagina

- **WHEN** se mide el PDF compilado
- **THEN** la portada ocupa exactamente una pagina

#### Scenario: Tope renegociado documentado

- **WHEN** se registra un tope distinto de 100 paginas sobre el total (una renegociacion con la catedra)
- **THEN** el registro declara su regla de medicion, su valor, su fuente y su fecha
- **AND** el PDF de la release cumple esa regla, con el exceso, si lo hubiera, honrado y declarado

#### Scenario: Cuerpo sin anexos

- **WHEN** se consigna el conteo complementario del cuerpo sin anexos (pagina del encabezado "Anexos" de `main.toc` menos 1)
- **THEN** ese conteo se registra como informacion complementaria del libro mayor
- **AND** no se usa para dar por cumplido el tope, cuya metrica es el total del PDF

#### Scenario: Reduccion sin perdida de contenido

- **WHEN** se compacta el documento para acercarlo al tope
- **THEN** los numeros canonicos, las figuras y tablas requeridas, las referencias y las correcciones previas permanecen
- **AND** las palancas aplicadas son de forma (indices, listas, tamano de anexos, ancho de figuras y espaciado)

### Requirement: Reducción sin pérdida de contenido científico

La reducción de páginas SHALL preservar la integridad científica del documento.
El change MUST NOT eliminar ni alterar: contenido científico (afirmaciones,
argumentos, interpretaciones y análisis), las figuras y tablas requeridas por el
conjunto de changes (incluidas las ocho figuras de c-80 y las tablas con su línea
de fuente), los números canónicos (exactitud 73,5 %, macro-F1 0,5207, reducción
71,2 %, W=363, r=0,9639, κ=0,87, universo 2.646, horas-persona 32,2 h), ni las
referencias bibliográficas. Las palancas admisibles son de forma: pasajes
duplicados, leyendas sobre-extendidas, listas redundantes, tamaño del glosario,
espaciado y compactación de anexos. La reduccion SHALL organizarse en tres fases: **Fase A** (forma), que puede reubicar figuras del cuerpo en el Anexo A con precedente documentado (c-139), reemplazar un flotante `[p]` por `[htbp]` cuando la tabla quepa en el texto, y compactar los `Overfull \hbox` mayores a 10pt; **Fase B** (de-duplicacion), que reemplaza pasajes repetidos por una remision `\autoref` a su seccion primaria sin perder la afirmacion original; y **Fase C** (condensacion de los capitulos 4 y 6), que SHALL aplicarse solo con decision explicita del autor. Una reubicacion a un anexo MUST conservar la figura, su pie y su fuente, y actualizar el inventario del anexo y el indice de figuras. Las siguientes palancas estan PROHIBIDAS: alterar el interlineado o los margenes del preambulo (APA 7 y 2,54~cm estan congelados; la palanca P8 no se aplica), reducir la fuente de la bibliografia (ya esta en `\footnotesize`) y retirar los `\newpage` de capitulo.

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

#### Scenario: Reubicacion a anexo preserva figura y remision

- **WHEN** una figura del cuerpo se mueve al Anexo A (por ejemplo `fig:componentes` o `fig:secuencia`)
- **THEN** la figura, su pie y su fuente siguen presentes en el Anexo A
- **AND** el inventario del Anexo A, el indice de figuras y toda remision del cuerpo a la figura quedan actualizados y resueltos
- **AND** la `\autoref` que la referenciaba sigue dando un destino valido

#### Scenario: De-duplicacion conserva la afirmacion primaria

- **WHEN** un pasaje repetido en otro capitulo se reemplaza por `\autoref` a su seccion primaria
- **THEN** la afirmacion, el numero canonico y la cita siguen presentes en la seccion primaria
- **AND** ningun pasaje queda huerfano sin su remision ni se pierde informacion no repetida en la seccion primaria

#### Scenario: Palancas prohibidas no aplicadas

- **WHEN** se revisa el diff del change
- **THEN** el preambulo no cambia su interlineado (sigue `\doublespacing`) ni sus margenes (siguen 2,54~cm)
- **AND** la fuente de la bibliografia no baja de su valor vigente (`\footnotesize`)
- **AND** ningun `\newpage` de capitulo fue retirado

#### Scenario: Fase C solo con decision del autor

- **WHEN** se revisa el diff del change respecto de los capitulos 4 y 6
- **THEN** cualquier condensacion de esos capitulos esta respaldada por una decision explicita y registrada del autor
- **AND** sin esa decision, los capitulos 4 y 6 permanecen sin cambios

### Requirement: Verificación de compilación tras la reducción

La reducción SHALL verificarse sobre el PDF compilado. La compilación con XeLaTeX
SHALL producir `main.pdf` sin errores fatales, con cero referencias indefinidas y
cero etiquetas duplicadas en el registro. El conteo de páginas y la ausencia de
referencias indefinidas SHALL registrarse como evidencia de la verificación. La
meta `total <= 100` es el objetivo (punto dulce) del change: alcanzarla no es un
criterio obligatorio de aceptacion, pero el conteo alcanzado SHALL registrar su delta respecto de la linea base `v1.2.8` (118 total) y la reduccion no puede lograrse a costa del contenido cientifico.

#### Scenario: Compilación sin errores fatales

- **WHEN** se compila `main.tex` con `latexmk -xelatex` (imagen `texlive-thesis`)
- **THEN** se produce `main.pdf` sin errores fatales
- **AND** el registro no contiene "undefined reference" ni "multiply defined label"

#### Scenario: Evidencia de verificación registrada

- **WHEN** se cierra el change
- **THEN** el conteo de páginas (`pdfinfo`) y el resultado de la verificación de referencias quedan registrados en las tareas
- **AND** el conteo alcanzado se consigna con su delta respecto de la linea base `v1.2.8`
- **AND** la meta <= 100 se declara como objetivo del change y no alcanzarla no invalida la reduccion, siempre que el conteo haya disminuido o permanecido igual sin perdida de contenido
