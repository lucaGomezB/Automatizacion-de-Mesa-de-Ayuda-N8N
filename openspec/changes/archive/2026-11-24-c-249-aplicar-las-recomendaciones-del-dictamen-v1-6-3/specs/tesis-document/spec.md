## ADDED Requirements

### Requirement: Regla escrita de movimiento de tags de release (OQ-05 de c-249)

Antes de crear el tag de la release siguiente a `v1.6.3`, el proyecto SHALL registrar en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (seccion c-249) la regla de tags aprobada por
autores y director, elegida entre: (A) tag inmutable sobre C3, cuyo PDF no imprime hash, con el hash
consignado en C4; (B) tag creado una sola vez sobre C4, despues de consignar el hash de C3 y
recompilar, y nunca movido; (C) un tag publicado puede moverse una sola vez, solo antes de difundir
el ejemplar y con registro fechado; (D) sin PDF versionado en el arbol del tag. La release `v1.6.4`
SHALL aplicar la regla elegida. Si la regla es incompatible con "Publicacion de una release de
correccion sin mover tags publicados", el change SHALL agregar un MODIFIED de ese requisito antes de
archivarse. Los tags `v1.6.2` y `v1.6.3` MUST NOT moverse, borrarse ni recrearse.

#### Scenario: Regla registrada antes del tag

- **WHEN** se compara la fecha de la fila OQ-05 de la seccion c-249 con la del tag `v1.6.4`
- **THEN** la regla figura con responsables (autores y director) y es anterior a la creacion del tag

#### Scenario: Tags anteriores intactos

- **WHEN** se ejecutan `git rev-parse v1.6.2^{commit}` y `git rev-parse v1.6.3^{commit}` antes y despues del apply
- **THEN** devuelven `e7013127...` y `f8618bdd...` respectivamente, sin cambios

### Requirement: Trazabilidad de la release en el texto del ejemplar

El parrafo del Anexo B que describe el hash (`12-anexos.tex`, hoy `:60`) SHALL coincidir con el
estado real del tag de la release que lo contiene: que commit apunta el tag y que commit imprime el
hash. La Nota de versiones (Anexo I.1) SHALL registrar `v1.6.2`, `v1.6.3` y el erratum del PDF del
tag `v1.6.2` si asi lo decide OQ-05 de c-249; si no, el registro SHALL declarar la decision.
`docs/Tesis/v10 (IA)/paper/compilacion.md` SHALL nombrar en "Fuente compilada" el hash del commit
compilado. El `tasks.md` archivado de c-248 SHALL llevar una nota aditiva fechada que enmiende la
tarea 6.3 con el estado final del tag `v1.6.3` (C4, `f8618bdd`). La cifra del inventario de uso de
asistentes de IA (Anexo I.3) SHALL coincidir con `git rev-list --count` sobre la referencia que el
texto describe.

#### Scenario: Anexo B coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en el PDF del tag `v1.6.4` y se compara con `git rev-parse v1.6.4^{commit}`
- **THEN** el texto describe correctamente que commit apunta el tag y que hash imprime
- **AND** `rg -n "el PDF compilado en el propio tag no lo imprime" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"` no devuelve coincidencias, salvo que la regla elegida haga verdadera esa frase

#### Scenario: Commit compilado nombrado

- **WHEN** se lee `docs/Tesis/v10 (IA)/paper/compilacion.md`
- **THEN** la fila "Fuente compilada" contiene un hash de commit y no solo "arbol de trabajo"

#### Scenario: Enmienda de c-248 sin reescribir historia

- **WHEN** se lee `openspec/changes/archive/2026-11-22-c-248-publicar-la-release-y-la-nota-de-erratum-de-v1-6-2/tasks.md`
- **THEN** la tarea 6.3 conserva su texto y una nota fechada de c-249 declara que el tag se movio a C4

#### Scenario: Conteo del inventario reproducible

- **WHEN** se ejecuta `git rev-list --count` sobre la referencia descrita en el Anexo I.3
- **THEN** el resultado coincide con la cifra impresa

## MODIFIED Requirements

### Requirement: Presupuesto de páginas preservado

El total de paginas del PDF de la tesis SHALL tender al tope vigente de paginas, que SHALL declararse en un unico lugar: la seccion de presupuesto de paginas de `docs/Tesis/Correcciones/dictamen-correcciones.md`, con su regla de medicion, su valor, su fuente (exigencia de la catedra o decision del equipo) y su fecha. La regla vigente SHALL ser: metrica = **total del PDF**, medido con `pdfinfo main.pdf | grep Pages` o un conteo equivalente de saltos de pagina del PDF; valor = **100 paginas**; fuente = **exigencia de la catedra**, declarada por el autor el 2026-10-27 (G0.1); fecha = 2026-10-27. La metrica superada **cuerpo sin anexos <= 100** (rama (b) del 2026-10-26) MUST NOT usarse para declarar cumplimiento ni presentarse como la regla vigente; el conteo de cuerpo sin anexos SHALL conservarse solo como informacion complementaria del libro mayor. Para cada release, el total medido SHALL consignarse en el libro mayor con la regla, el valor, la fuente y la fecha; cuando el total supere el tope, ademas con la magnitud del exceso, su fecha y la decision registrada de los autores de sostenerlo. Cuando el total supere el valor del tope, el exceso SHALL estar declarado y honrado por decision registrada de los autores, con su magnitud y fecha, y SHALL defenderse ante la catedra; un exceso no declarado MUST NOT presentarse como cumplimiento, y una reduccion que no alcance el tope no constituye incumplimiento mientras el exceso quede declarado y honrado. La portada SHALL seguir ocupando exactamente una pagina. Una reduccion para acercarse al tope MUST NOT eliminar contenido cientifico, numeros canonicos, figuras o tablas requeridas, referencias ni correcciones previas, y MUST NOT dejar referencias colgadas (`\ref` o `\autoref` sin destino) ni listados de codigo removidos con referencias en la prosa.

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

- **WHEN** se consigna el resultado de paginas de cualquier release en el libro mayor o en `CHANGES.md`
- **THEN** el numero reportado usa la metrica del total del PDF
- **AND** la cuenta por cuerpo sin anexos de la rama (b) no se usa como base del cumplimiento ni se presenta como la regla vigente

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
