## ADDED Requirements

### Requirement: Etiqueta de la version evaluada

El repositorio SHALL identificar la version evaluada de la tesis mediante un tag
anotado `v1.0.0` que apunte al commit cuya fuente compila el PDF evaluado. El tag
SHALL crearse SOLO despues de que los changes de contenido c-104, c-105, c-106,
c-107, c-108, c-109 y c-110 esten aplicados y el manuscrito recompilado, de modo
que la etiqueta refleje la fuente final corregida y no una intermedia. El tag
SHALL publicarse en el remoto `origin`.

#### Scenario: Tag existente y anotado

- **WHEN** se ejecuta `git tag -l` y `git cat-file -t v1.0.0` en el repositorio
- **THEN** el tag `v1.0.0` existe
- **AND** `git cat-file -t v1.0.0` devuelve `tag` (tag anotado, no lightweight)

#### Scenario: Tag sobre la fuente final

- **WHEN** se verifica el commit al que apunta `v1.0.0` (`git rev-parse v1.0.0^{commit}`)
- **THEN** ese commit es posterior a la aplicacion de c-104..c-110
- **AND** su fuente compila el PDF evaluado
- **AND** el tag esta publicado en `origin` (`git ls-remote --tags origin v1.0.0` lo devuelve)

#### Scenario: Sin tag sobre fuente intermedia

- **WHEN** se intenta cerrar el change antes de archivar algunos de c-104..c-110
- **THEN** la tarea de creacion del tag no se marca completa
- **AND** no se crea el tag sobre una fuente intermedia

### Requirement: Trazabilidad del hash del commit evaluado

El manuscrito SHALL consignar el hash completo de 40 caracteres del commit al que
apunta el tag `v1.0.0`, de modo que el documento bajo revision sea trazable a una
revision concreta del repositorio. El Anexo B (`sections/12-anexos.tex`,
`sec:anexo-repositorio`) SHALL reemplazar el lenguaje de "accion pendiente" por la
referencia al tag y su hash, y ese mismo hash SHALL registrarse en el registro de
trazabilidad `docs/Tesis/Correcciones/dictamen-correcciones.md`. El hash consignado
MUST coincidir con el del commit etiquetado.

#### Scenario: Hash consignado en el manuscrito

- **WHEN** se lee el Anexo B del PDF compilado (o `sections/12-anexos.tex`)
- **THEN** figura el tag `v1.0.0` y el hash completo de 40 caracteres del commit evaluado
- **AND** no permanece la frase que declara la creacion del tag como "accion pendiente"

#### Scenario: Hash coherente con el tag

- **WHEN** se compara el hash consignado en el manuscrito con `git rev-parse v1.0.0^{commit}`
- **THEN** coinciden en los 40 caracteres
- **AND** el hash tambien figura en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Nota de version legible en el PDF

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` y se inspecciona el PDF
- **THEN** la nota de version y trazabilidad aparece renderizada sin errores fatales
- **AND** el conteo de paginas no aumenta respecto de la version corregida de partida
