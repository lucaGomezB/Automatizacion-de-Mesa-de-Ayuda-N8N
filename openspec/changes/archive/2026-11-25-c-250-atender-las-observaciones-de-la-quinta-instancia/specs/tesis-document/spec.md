## ADDED Requirements

### Requirement: Trazabilidad de la release v1.6.5 (versión de defensa) en el texto del ejemplar

La release `v1.6.5` es la **versión de defensa**. El bump de versión SHALL aplicarse a
`00-portada.tex` (hoy `Versión 1.6.4`), al Anexo B (`sec:anexo-repositorio`), a la Nota de versiones
(Anexo I.1), a `Bibliography_base.bib` (`Gomez2026_repositorio`), a `README.md`, a `knowledge-base/`
y a `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`. El párrafo del Anexo B que describe el
hash SHALL coincidir con el estado real del tag de la release: qué commit apunta el tag y qué commit
imprime el hash (siguiendo la regla de tags registrada por c-249 OQ-05). La Nota de versiones SHALL
registrar `v1.6.5` y su relación con las anteriores, incluyendo que el corpus sintético del 3 de
julio (165,3 s) queda como histórico/retirado Y el reencuadre de procedencia (de "integrantes del
entorno operativo del propio equipo" a "los autores y las personas de su círculo (familiares y
amigos)") como corrección de veracidad. `docs/Tesis/v10 (IA)/paper/compilacion.md` SHALL nombrar en
"Fuente compilada" el hash del commit compilado. La cifra del inventario de uso de asistentes de IA
(Anexo I.3) SHALL coincidir con `git rev-list --count` sobre la referencia que el texto describe. El
tag `v1.6.4` y los anteriores MUST NOT moverse, borrarse ni recrearse.

#### Scenario: Versión v1.6.5 propagada

- **WHEN** se ejecuta `rg -n "1\.6\.4" "docs/Tesis/v10 (IA)/paper/sections/00-portada.tex" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "README.md"`
- **THEN** las referencias de versión de la release apuntan a `v1.6.5`, salvo las menciones históricas de la Nota de versiones y del registro de correcciones

#### Scenario: Anexo B coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en el PDF del tag `v1.6.5` y se compara con `git rev-parse v1.6.5^{commit}`
- **THEN** el texto describe correctamente qué commit apunta el tag y qué hash imprime, conforme a la regla de tags registrada

#### Scenario: Nota de versiones con reencuadre de procedencia y corpus sintético retirado

- **WHEN** se lee la Nota de versiones (Anexo I.1)
- **THEN** registra `v1.6.5`, declara que el corpus sintético del 3 de julio (165,3 s) queda como histórico/retirado, y registra el reencuadre de procedencia como corrección de veracidad

#### Scenario: Commit compilado nombrado

- **WHEN** se lee `docs/Tesis/v10 (IA)/paper/compilacion.md`
- **THEN** la fila "Fuente compilada" contiene un hash de commit y no solo "árbol de trabajo"

#### Scenario: Tag anterior intacto

- **WHEN** se ejecuta `git rev-parse v1.6.4^{commit}` antes y después del apply
- **THEN** devuelve el mismo hash, sin cambios

#### Scenario: Conteo del inventario reproducible

- **WHEN** se ejecuta `git rev-list --count` sobre la referencia descrita en el Anexo I.3
- **THEN** el resultado coincide con la cifra impresa