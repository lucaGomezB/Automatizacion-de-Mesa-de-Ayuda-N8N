## ADDED Requirements

### Requirement: Version de trabajo v10 y punteros activos consistentes

La version de trabajo vigente de la tesis SHALL ser `docs/Tesis/v10 (IA)/`, materializada como copia fiel de la version previamente publicada. Los punteros activos del proyecto —el campo `thesis:` de `openspec/config.yaml`, el estado actual declarado en `CHANGES.md`, las rutas activas de `openspec/specs/tesis-document/spec.md` y las rutas de trabajo de los changes dependientes de esta migracion— SHALL resolver a `docs/Tesis/v10 (IA)/`. La version previamente publicada `docs/Tesis/v9 (IA)/` SHALL conservarse intacta. Los registros historicos (entradas fechadas de `CHANGES.md`, dictamenes en `auditorias/`, bitacoras en `docs/Tesis/Correcciones/` y changes en `openspec/changes/archive/`) MUST NOT reescribirse para aparentar que apuntaban a v10.

#### Scenario: Existe la copia de trabajo v10 como espejo de v9

- **WHEN** se inspecciona el arbol de trabajo tras aplicar la migracion
- **THEN** existe el directorio `docs/Tesis/v10 (IA)/`
- **AND** contiene la fuente LaTeX `docs/Tesis/v10 (IA)/paper/main.tex`, la bibliografia `docs/Tesis/v10 (IA)/Bibliography_base.bib` y los textos extraidos `docs/Tesis/v10 (IA)/tesis_completa_extraida.txt` y `docs/Tesis/v10 (IA)/tesis_para_evaluacion.txt`
- **AND** la cantidad de archivos versionados de `docs/Tesis/v10 (IA)/` es igual a la de `docs/Tesis/v9 (IA)/`

#### Scenario: Los punteros activos resuelven a v10

- **WHEN** se inspeccionan los punteros activos del proyecto tras aplicar la migracion
- **THEN** el campo `thesis:` de `openspec/config.yaml` apunta a una ruta dentro de `docs/Tesis/v10 (IA)/`
- **AND** las entradas de estado actual de `CHANGES.md` designan `docs/Tesis/v10 (IA)/` como version de trabajo vigente
- **AND** las rutas activas de `docs/Tesis/v9 (IA)` en `openspec/specs/tesis-document/spec.md` fueron repuntadas a `docs/Tesis/v10 (IA)`, de modo que `grep -c "docs/Tesis/v9 (IA)" openspec/specs/tesis-document/spec.md` es 0

#### Scenario: La version publicada v9 permanece intacta

- **WHEN** se compara el arbol de `docs/Tesis/v9 (IA)/` con su estado previo a la migracion
- **THEN** no hay archivos agregados, modificados ni borrados bajo `docs/Tesis/v9 (IA)/`
- **AND** `git status` no reporta cambios para esa ruta

#### Scenario: Los registros historicos no se reescriben

- **WHEN** se inspeccionan los registros historicos que referencian v9 (entradas fechadas de `CHANGES.md`, archivos de `auditorias/`, archivos de `docs/Tesis/Correcciones/` y directorios de `openspec/changes/archive/`)
- **THEN** conservan sus referencias a `docs/Tesis/v9 (IA)` tal como estaban
- **AND** ninguna entrada fechada previa a la migracion fue reescrita para designar v10
