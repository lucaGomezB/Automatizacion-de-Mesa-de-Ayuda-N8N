## ADDED Requirements

### Requirement: URL explicita del repositorio en el anexo de codigo fuente

El Anexo B de la tesis (`sec:anexo-repositorio` en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`) SHALL mostrar de forma explicita la URL del repositorio publico del proyecto, ademas de la cita bibliografica existente, de modo que el lector no deba reconstruir la direccion desde la seccion de Referencias. La URL SHALL ser `https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N` y SHALL presentarse como enlace visible (no solo como destino de hipervinculo). El anexo SHALL conservar la prosa introductoria y la cita `\parencite{Gomez2026_repositorio}`.

#### Scenario: La URL aparece en el cuerpo del anexo

- **GIVEN** el PDF compilado de la tesis
- **WHEN** se lee el Anexo B, seccion "Repositorio de codigo fuente" (`sec:anexo-repositorio`)
- **THEN** la URL `https://github.com/lucaGomezB/Automatizacion-de-Mesa-de-Ayuda-N8N` figura de forma explicita en el cuerpo del anexo
- **AND** la URL se renderiza como texto visible y clicable, sin depender de la seccion de Referencias

#### Scenario: Cita y prosa existentes preservadas

- **WHEN** se comparan el Anexo B modificado y su version previa al change
- **THEN** la cita `\parencite{Gomez2026_repositorio}` permanece en el anexo
- **AND** la prosa introductoria del repositorio se conserva sin eliminar ninguna oracion sustantiva

### Requirement: Coherencia de la version bibliografica con la release publicada

La entrada `Gomez2026_repositorio` de `docs/Tesis/v10 (IA)/Bibliography_base.bib` SHALL declarar en su titulo la misma version que la release publicada en el manuscrito. El titulo SHALL enunciar `(Version 1.1.1)` y SHALL NOT conservar la version obsoleta `(Version 1.0.0)`. Los demas campos de la entrada (autoria, ano, `url` y `note`) SHALL conservarse y la referencia SHALL seguir imprimiendose en la seccion de Referencias.

#### Scenario: Version bibliografica alineada con la release

- **WHEN** se inspecciona la entrada `Gomez2026_repositorio` en `Bibliography_base.bib`
- **THEN** el campo `title` enuncia `(Version 1.1.1)`
- **AND** no conserva la cadena `(Version 1.0.0)`

#### Scenario: Integridad de la entrada preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib`
- **THEN** la entrada sigue existiendo y sigue siendo referenciada por la cita del anexo
- **AND** sus campos `author`, `year`, `url` y `note` se mantienen, sin introducir citas huerfanas ni entradas sin usar

### Requirement: Etiqueta de la release v1.1.1 y trazabilidad del hash

La version de trabajo de la tesis `docs/Tesis/v10 (IA)/` SHALL publicarse mediante un tag anotado `v1.1.1` creado sobre el commit que cierra las ediciones de este change. El manuscrito (`sections/12-anexos.tex`, `sec:anexo-repositorio`) SHALL identificar la version entregada con el tag `v1.1.1` y consignar el hash completo de 40 caracteres del commit etiquetado, coincidente con `git rev-parse v1.1.1^{commit}`; ese mismo hash SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El tag SHALL crearse SOLO despues de aplicar las ediciones de contenido y recompilar el PDF. Los tags previos `v1.0.0`, `v1.0.1` y `v1.1.0` MUST NOT moverse.

#### Scenario: Tag anotado v1.1.1 sobre el commit de cierre

- **WHEN** se ejecuta `git cat-file -t v1.1.1` y `git rev-parse v1.1.1^{commit}`
- **THEN** el tag existe, es anotado (devuelve `tag`, no `commit`) y apunta a un commit posterior a la aplicacion de este change
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.1.1` lo devuelve)

#### Scenario: Hash consignado y coherente con el tag

- **WHEN** se lee `sec:anexo-repositorio` en `12-anexos.tex` y se compara con `git rev-parse v1.1.1^{commit}`
- **THEN** figura el tag `v1.1.1` y el hash completo de 40 caracteres del commit etiquetado
- **AND** el hash coincide en los 40 caracteres y tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Tags previos inmutables

- **WHEN** se comparan `git rev-parse v1.0.0^{commit}`, `git rev-parse v1.0.1^{commit}` y `git rev-parse v1.1.0^{commit}` con sus valores previos
- **THEN** `v1.0.0` sigue en `61a6b117dd1321fbee25f9792d9f29b884e5ac8d`, `v1.0.1` sigue en `bac4c5f6f85c889b48a90d4396bbdaccc7a35ad0` y `v1.1.0` sigue en `7103b649d8c4f51737ad6ad4095dad22c9406400`
- **AND** ningun tag existente fue reescrito o re-creado
