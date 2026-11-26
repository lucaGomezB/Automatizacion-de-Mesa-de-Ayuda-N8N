## ADDED Requirements

### Requirement: Trazabilidad de la release v1.6.6 (versión de defensa) y registro de la sexta instancia

La release `v1.6.6` es la **versión de defensa** que incorpora D-01 a D-03. El bump de versión SHALL
aplicarse a `00-portada.tex`, al Anexo B (`sec:anexo-repositorio`), a la Nota de versiones (Anexo I.1), a
`Bibliography_base.bib` (`Gomez2026_repositorio`), a `README.md`, a `knowledge-base/` y a
`docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`. El párrafo del Anexo B SHALL coincidir con el
estado real del tag (qué commit apunta y qué hash imprime, regla de c-249 OQ-05). La Nota de versiones
(Anexo I.1) SHALL registrar (a) el cambio de fechas de la campaña manual (junio–agosto → octubre 2026) y
(b) el cambio de la definición del tiempo manual (componente de carga), con el mismo criterio que los
retiros anteriores. El Anexo I.2 (`sec:anexo-trazabilidad`, `12-anexos.tex`) SHALL sumar la devolución de
quinta instancia (25/11/2026) y la de sexta instancia (26/11/2026). El Resumen y el Abstract
(`00-resumen.tex`) y la Tabla 10 SHALL decir que el brazo manual midió solo la clasificación (no el
registro) e informar también el 63,3 % sin telefonía (`07-resultados.tex:60`, `08-discusion.tex:8`). La
devolución de sexta instancia SHALL versionarse como
`auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`. La release SHALL quedar BLOQUEADA hasta
que D-01 a D-03 estén aplicados y el director haya dado su visto bueno escrito; el tag `v1.6.6` MUST NOT
publicarse antes de ese visto bueno. Los tags anteriores MUST NOT moverse, borrarse ni recrearse.

#### Scenario: Versión v1.6.6 propagada

- **WHEN** se ejecuta `rg -n "1\.6\.5" "docs/Tesis/v10 (IA)/paper/sections/00-portada.tex" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex" "docs/Tesis/v10 (IA)/Bibliography_base.bib" "README.md"`
- **THEN** las referencias de versión de la release apuntan a `v1.6.6`, salvo menciones históricas de la Nota de versiones y del registro de correcciones

#### Scenario: Anexo I.1 registra cambio de fechas y de definición del tiempo manual

- **WHEN** se lee la Nota de versiones (Anexo I.1, `12-anexos.tex:239-247`)
- **THEN** registra el cambio de fechas (junio–agosto → octubre 2026) y el cambio de la definición del tiempo manual (componente de carga) como corrección de veracidad, con el mismo criterio que los retiros anteriores

#### Scenario: Anexo I.2 con quinta y sexta instancia

- **WHEN** se ejecuta `rg -n "quinta instancia|sexta instancia|25/11/2026|26/11/2026|2026-11-25|2026-11-26" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** el Anexo I.2 lista la devolución de quinta instancia (25/11/2026) y la de sexta instancia (26/11/2026) además de la cuarta (19/11/2026) y las anteriores

#### Scenario: Resumen, Abstract y Tabla 10 con solo clasificación y 63,3 % sin telefonía

- **WHEN** se ejecuta `rg -n "63,3|clasificaci.n" "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex"` y se lee la Tabla 10
- **THEN** el Resumen, el Abstract y la Tabla 10 declaran que el brazo manual midió solo la clasificación (no el registro) e informan el 63,3 % sin telefonía

#### Scenario: Devolución de sexta instancia versionada en .md

- **WHEN** se lee `auditorias/Devolucion_Sexta_Instancia_TFI_v1.6.5_2026-11-26.md`
- **THEN** contiene la transcripción completa de la devolución de sexta instancia con el bloque de metadatos (versión auditada, emisión, calificación, condición) en el formato de las devoluciones anteriores

#### Scenario: Release bloqueada sin el visto bueno del director

- **WHEN** se comprueba `git rev-parse v1.6.6^{commit}` antes de que el director dé su visto bueno escrito
- **THEN** el tag no existe todavía, y D-01 a D-03 están aplicados en el árbol antes de que el tag se publique