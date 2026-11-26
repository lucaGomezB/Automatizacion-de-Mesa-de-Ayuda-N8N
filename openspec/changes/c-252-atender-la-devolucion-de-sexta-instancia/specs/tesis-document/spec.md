## ADDED Requirements

### Requirement: Trazabilidad de la release v1.6.6 (versión de defensa tras la sexta instancia) en el texto del ejemplar

La release `v1.6.6` es la versión de defensa que incorpora D-01 a D-03 de la devolución de sexta instancia
(y D-04 a D-06 en la medida en que se resuelvan). El bump de versión SHALL aplicarse a `00-portada.tex` (hoy
`Versión 1.6.5`), al Anexo B (`sec:anexo-repositorio`), a la Nota de versiones (Anexo I.1), a
`Bibliography_base.bib` (`Gomez2026_repositorio`), a `README.md`, a `knowledge-base/` y a
`docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`. El tag anotado `v1.6.6` SHALL ubicarse sobre el
commit de contenido (C3) y el hash impreso en el Anexo B SHALL corresponder a C3, consignado en un commit
posterior (C4), según la regla de tags registrada por c-249 OQ-05. La Nota de versiones SHALL registrar
`v1.6.6` con los cambios de la sexta instancia (cronología acotada, definición del tiempo manual, origen del
régimen (a)), y el Anexo I.2 SHALL listar las devoluciones de quinta (25/11/2026) y sexta (26/11/2026)
instancia. `docs/Tesis/v10 (IA)/paper/compilacion.md` SHALL nombrar en "Fuente compilada" el hash del commit
compilado. La cifra del inventario (Anexo I.3) SHALL coincidir con `git rev-list --count` sobre la referencia
descrita. La release SHALL exigir como precondición el visto bueno escrito del director a esta versión. Los
tags `v1.6.0` a `v1.6.5` MUST NOT moverse, borrarse ni recrearse.

#### Scenario: Versión v1.6.6 propagada

- **WHEN** se ejecuta `rg -n "1\.6\.5" "docs/Tesis/v10 (IA)/paper/sections/00-portada.tex" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "README.md"`
- **THEN** las referencias de versión de la release apuntan a `v1.6.6`, salvo las menciones históricas de la Nota de versiones y del registro de correcciones

#### Scenario: Anexo B coherente con el tag v1.6.6

- **WHEN** se compara el hash impreso en `sec:anexo-repositorio` del PDF de la release con `git rev-parse v1.6.6^{commit}`
- **THEN** coinciden conforme a la regla de tags registrada, y `git cat-file -t v1.6.6` devuelve `tag`

#### Scenario: Devoluciones quinta y sexta registradas

- **WHEN** se leen el Anexo I.1 y el Anexo I.2 del PDF de la release
- **THEN** I.1 registra `v1.6.6` y los cambios de la sexta instancia, e I.2 lista las devoluciones del 25 y del 26 de noviembre de 2026

#### Scenario: Precondición del director

- **WHEN** se va a crear el tag `v1.6.6`
- **THEN** la sección c-252 de `dictamen-correcciones.md` cita la constancia fechada del visto bueno escrito del director a esta versión

#### Scenario: Tags anteriores intactos en v1.6.6

- **WHEN** se ejecuta `git rev-parse v1.6.5^{commit}` antes y después del apply
- **THEN** devuelve el mismo hash
