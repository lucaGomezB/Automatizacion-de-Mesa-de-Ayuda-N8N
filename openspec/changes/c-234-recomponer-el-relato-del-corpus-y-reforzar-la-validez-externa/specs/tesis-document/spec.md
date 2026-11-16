## ADDED Requirements

### Requirement: Relato de procedencia de un unico corpus congelado

El documento SHALL declarar de forma explicita que la evidencia empirica se apoya en un **unico corpus congelado** (`data/corpus_evaluacion_pseudonimizado.json`, con su SHA-256 canonico) y que las distintas cifras provienen de **varias corridas y configuraciones** sobre ese mismo corpus, no de corpus distintos. El documento SHALL hacer explicito, sin ambiguedad, que cifra proviene de que configuracion: los tiempos manuales de la campana 2026-10; los tiempos automatizados de correo y formulario (2-10-2026) medidos con `hybrid-v1`; los tiempos telefonicos (5 y 6 de octubre de 2026, sin configuracion unica, recalculados el 19-10-2026); las metricas de clasificacion (corrida fuera de linea del 7-10-2026 con `hybrid-v3`, commit `bf5e099`, configuracion evaluada); y la campana complementaria (`hybrid-v3` sobre un backend posterior, comparable con la campana 2026-10 solo sobre la cache). Cuando un pasaje sugiera una configuracion unica donde hubo varias, SHALL distinguirlas. La correccion MUST NOT cambiar el valor de ningun numero canonico y MUST NOT introducir datos nuevos.

#### Scenario: Corpus unico declarado

- **WHEN** se lee el relato de procedencia en `04-marco-metodologico.tex`, `07-resultados.tex`, `08-discusion.tex` y el Anexo B
- **THEN** el texto declara que el corpus congelado es uno solo, con su huella canonica
- **AND** declara que la multiplicidad es de configuraciones y corridas sobre ese corpus, no de corpus distintos

#### Scenario: Que cifra proviene de que configuracion

- **WHEN** se recorre el mapeo de procedencia
- **THEN** cada familia de cifras (tiempos manuales; tiempos automatizados de correo y formulario; tiempos telefonicos; metricas de clasificacion; campana complementaria) declara su corrida y su configuracion
- **AND** se distinguen la configuracion evaluada (`bf5e099`), la entregada (`v1.3.0`) y la de la campana complementaria

#### Scenario: Configuraciones no unicas explicitadas

- **WHEN** un pasaje del documento describe la configuracion de una corrida
- **THEN** el texto distingue las configuraciones que coexistieron (por ejemplo `hybrid-v1` en los tiempos frente a `hybrid-v3` en las metricas)
- **AND** no deja una configuracion unica implicita donde hubo varias

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el `.tex` antes y despues del change
- **THEN** ningun valor canonico cambia de valor
- **AND** las unicas diferencias son palabras, rotulos y remisiones de procedencia

### Requirement: Validez externa declarada en las conclusiones con su remedio empirico

Las conclusiones SHALL declarar la amenaza a la validez externa con la fuerza que el diseno permite: la muestra es **no probabilistica por conveniencia** (los 200 casos son los incidentes cronometrados), proviene de **una sola organizacion** (servicios, provincia de Mendoza) y el universo es **proyectado, no medido** (`2.646 = 42 x 63`), de modo que las cifras valen para este corpus y no se extrapolan al universo de incidentes. La declaracion SHALL senalar que el remedio empirico es el **diseno de muestreo probabilistico del universo** (change `c-229`), SHALL presentarlo como **condicional y no ejecutado** y MUST NOT afirmar que la validez externa ya fue establecida. La correccion MUST NOT cambiar el valor de ningun numero canonico.

#### Scenario: Fuerza correcta en la conclusion

- **WHEN** se leen las conclusiones (`09-conclusiones.tex`)
- **THEN** el texto declara la muestra no probabilistica por conveniencia, la organizacion unica y el universo proyectado (`2.646 = 42 x 63`)
- **AND** las cifras se declaran validas para este corpus y no extrapolables al universo

#### Scenario: Remedio empirico declarado como condicional

- **WHEN** se lee la declaracion de validez externa
- **THEN** remite al diseno de muestreo probabilistico (change `c-229`) como remedio empirico
- **AND** lo presenta como condicional y no ejecutado, sin afirmar que la validez externa ya esta establecida

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el `.tex` antes y despues del change
- **THEN** ningun valor canonico cambia de valor
- **AND** las unicas diferencias son palabras y remisiones de procedencia
