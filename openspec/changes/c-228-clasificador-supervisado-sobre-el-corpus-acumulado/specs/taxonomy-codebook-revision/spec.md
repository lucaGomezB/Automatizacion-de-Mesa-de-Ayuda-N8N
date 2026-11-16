## Purpose

Revisa las definiciones y el criterio de frontera entre los sectores `Sistemas` y
`Soporte Tecnico Software`, y mide la ambiguedad de etiquetado de esa frontera,
sin alterar las cinco cadenas canonicas.

## ADDED Requirements

### Requirement: TCR-001 — Revision del codebook de la frontera Sistemas-Software

La revision SHALL actualizar las definiciones de `Sistemas` y `Soporte Tecnico
Software` y el criterio de frontera en
`evaluation/data/campana/codebook_doble_etiquetado.md`, con ejemplos de casos
limitrofes tomados del corpus disponible. La revision MUST NOT alterar las cinco
cadenas canonicas ni introducir sectores fuera del conjunto canonico, y SHALL
documentar la definicion anterior y la nueva con su procedencia. La revision SHALL
declarar que su objeto es reducir la ambiguedad de la frontera y MUST NOT afirmar
que el clasificador mejorara esa clase.

#### Scenario: Codebook revisado sin cambiar las cadenas canonicas

- **WHEN** se lee el codebook revisado
- **THEN** las definiciones de `Sistemas` y `Soporte Tecnico Software` y el criterio de frontera estan actualizados
- **AND** las cinco cadenas canonicas permanecen exactas, sensibles a mayusculas y sin tildes

#### Scenario: Procedencia de la revision

- **WHEN** se compara el codebook antes y despues
- **THEN** la definicion anterior y la nueva quedan documentadas con su procedencia
- **AND** no se afirma que el clasificador vaya a mejorar la clase

### Requirement: TCR-002 — Medicion de la ambiguedad de la frontera

La revision SHALL medir la ambiguedad de la frontera como la proporcion de casos
limitrofes que los etiquetadores asignan a una sola clase frente a los que dividen
su asignacion entre `Sistemas` y `Soporte Tecnico Software`, antes y despues de la
revision del codebook. La medicion SHALL usar los casos disponibles del corpus
acumulado o del corpus de etiquetado y SHALL reportar el `n`. Si la revision no
reduce la ambiguedad, el resultado SHALL reportarse igualmente, sin presentarlo
como una mejora.

#### Scenario: Proporcion de asignacion unica reportada

- **WHEN** se mide la ambiguedad de la frontera
- **THEN** se reporta la proporcion de casos asignados a una sola clase, antes y despues
- **AND** se declara el `n` de la medicion

#### Scenario: Sin mejora no se oculta

- **WHEN** la revision no reduce la ambiguedad
- **THEN** el resultado se reporta de todos modos
- **AND** no se presenta como una mejora

### Requirement: TCR-003 — Propuesta de actualizacion de las reglas de frontera del prompt

Si la revision del codebook habilita reglas de frontera nuevas, el change SHALL
proponer la actualizacion del requisito `TAX-004` de `sector-taxonomy` y del prompt
compartido (`docs/prompt_gemini.txt`) como una propuesta registrada. La propuesta
MUST NOT aplicarse de forma automatica: su aplicacion SHALL requerir aprobacion
explicita de los autores y, por defecto, se difiere a un change propio. En ningun
caso la revision SHALL cambiar las cinco cadenas canonicas.

#### Scenario: Propuesta registrada y no aplicada

- **WHEN** la revision del codebook sugiere reglas de frontera nuevas
- **THEN** la propuesta de actualizacion de `TAX-004` y del prompt queda registrada
- **AND** no se aplica sin aprobacion explicita de los autores

#### Scenario: Frontera del alcance del change

- **WHEN** se inspecciona el prompt vigente tras aplicar el change
- **THEN** el prompt no cambia salvo aprobacion explicita
- **AND** las cinco cadenas canonicas no cambian
