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
