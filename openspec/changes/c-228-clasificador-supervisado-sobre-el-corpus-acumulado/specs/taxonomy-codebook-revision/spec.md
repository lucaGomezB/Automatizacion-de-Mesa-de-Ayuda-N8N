## Purpose

Revisa las definiciones y el criterio de frontera entre los sectores `Sistemas` y
`Soporte Tecnico Software`, y mide la ambiguedad de etiquetado de esa frontera con
una linea base del doble etiquetado E1/E2 y una medicion posterior bajo compuertas,
sin alterar las cinco cadenas canonicas.

## ADDED Requirements

### Requirement: TCR-001 — Revision del codebook de la frontera Sistemas-Software

La revision SHALL actualizar las definiciones de `Sistemas` y `Soporte Tecnico
Software` y el criterio de frontera en
`evaluation/data/campana/codebook_doble_etiquetado.md`, con ejemplos de casos
limitrofes tomados solo de textos versionados de procedencia acreditada (el corpus
de 200 casos o un export acreditado). Ningun ejemplo MUST ser redactado por los
autores ni generado o asistido por IA. La revision MUST NOT alterar las cinco
cadenas canonicas ni introducir sectores fuera del conjunto canonico, SHALL
documentar la definicion anterior y la nueva con su procedencia, y MUST NOT afirmar
que el clasificador mejorara esa clase.

#### Scenario: Codebook revisado sin cambiar las cadenas canonicas

- **WHEN** se lee el codebook revisado
- **THEN** las definiciones de `Sistemas` y `Soporte Tecnico Software` y el criterio de frontera estan actualizados
- **AND** las cinco cadenas canonicas permanecen exactas, sensibles a mayusculas y sin tildes

#### Scenario: Ejemplos con procedencia

- **WHEN** se revisan los ejemplos limitrofes del codebook
- **THEN** cada uno remite a un texto versionado de procedencia acreditada
- **AND** ninguno fue redactado por los autores ni generado por IA

### Requirement: TCR-002 — Medicion de la ambiguedad de la frontera con linea base E1/E2

La revision SHALL medir la ambiguedad de la frontera como la proporcion de casos
limitrofes que los etiquetadores asignan a una sola clase frente a los que reparten
su asignacion entre `Sistemas` y `Soporte Tecnico Software`. La medicion «antes»
SHALL derivarse del doble etiquetado E1/E2 sobre el corpus de 200 casos
(`evaluation/data/campana/doble_etiquetado.csv`), reproducida por comando, con el
`n` declarado. La medicion «despues» SHALL exigir etiquetado nuevo con el codebook
revisado, por etiquetadores registrados en `registro_sujetos.csv` con
consentimiento, con planillas originales y marcas temporales registradas por la
herramienta, bajo las compuertas de procedencia y etica; sin ese etiquetado, el
artefacto SHALL declarar que no hay medicion posterior. Si la revision no reduce la
ambiguedad, el resultado SHALL reportarse igualmente, sin presentarlo como mejora.

#### Scenario: Linea base reproducida desde E1/E2

- **WHEN** se mide la ambiguedad antes de la revision
- **THEN** el valor se reproduce por comando desde `doble_etiquetado.csv` con el `n` declarado

#### Scenario: Sin etiquetado nuevo no hay medicion posterior

- **WHEN** no existe etiquetado nuevo bajo compuertas
- **THEN** el artefacto declara que no hay medicion posterior
- **AND** no presenta ninguna mejora

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
