## MODIFIED Requirements

### Requirement: Higiene de metadatos bibliograficos

Las entradas de `Bibliography_base.bib` SHALL reflejar la autoria, editorial y estado de publicacion reales de cada fuente. Las citas en el texto SHALL seguir el estilo APA 7 para el separador entre autor y ano en las citas con "et al.". El tipo de cada entrada (`@article`, `@book`, `@inproceedings`, `@misc`, `@online`, ...) SHALL corresponder a la naturaleza real de la fuente: una fuente preprint de arXiv MUST NOT tiparse como `@article` con un campo `journal` que la presente como publicacion periodica, y un borrador no publicado MUST NOT tiparse como `@book` con una editorial comercial como si fuera una obra publicada.

#### Scenario: Co-autoria y editorial corregidas

- **WHEN** se inspeccionan las entradas `Stallings2017_computer_security`, `OGC2011_itil` y `Jurafsky2023_speech_language`
- **THEN** `Stallings2017_computer_security` incluye a Lawrie Brown como co-autor
- **AND** `OGC2011_itil` refleja la autoria/editorial real de ITIL Service Operation (2011)
- **AND** `Jurafsky2023_speech_language` indica la editorial/estado correctos (Stanford University o borrador autopublicado), no Pearson

#### Scenario: Coma antes del ano en citas "et al."

- **WHEN** se inspecciona una cita con tres o mas autores en la tesis compilada
- **THEN** el separador entre el autor y el ano es la coma segun APA ("Revina et al., 2020")
- **AND** no aparece la forma sin coma ("Revina et al. 2020") en ninguna cita parentetica

#### Scenario: Nuevas entradas con metadatos completos

- **WHEN** se agregan las referencias de B2 y la entrada de Landis & Koch
- **THEN** cada entrada nueva incluye `author`, `title`, `year` y el campo de publicacion (`journal`, `booktitle` o `publisher`) mas `doi` o `url`
- **AND** las claves siguen la convencion `ApellidoAnio_palabra_clave` del archivo

#### Scenario: Tipado de la fuente preprint de arXiv

- **WHEN** se inspecciona la entrada `Touvron2023_llama2` en `Bibliography_base.bib`
- **THEN** la entrada NO es de tipo `@article` y NO declara `journal = {arXiv preprint}`
- **AND** se tipa como recurso preprint (`@misc`/`@online`) con `eprint`, `archivePrefix = {arXiv}` y `primaryClass` (o `howpublished`)
- **AND** el identificador `arXiv:2307.09288` y su DOI `10.48550/arXiv.2307.09288` se conservan
- **AND** la referencia compilada no presenta "arXiv preprint" como una publicacion periodica

#### Scenario: Tipado del borrador no publicado

- **WHEN** se inspecciona la entrada `Jurafsky2023_speech_language` en `Bibliography_base.bib`
- **THEN** la entrada NO es de tipo `@book` con una editorial comercial
- **AND** se tipa como manuscrito/borrador no publicado (`@misc`/`@unpublished`)
- **AND** el estado (Stanford University, borrador de la 3ra edicion) queda declarado en el campo de publicacion o en `note`

## ADDED Requirements

### Requirement: Verificacion de integridad y atribucion bibliografica (B1-B3)

La tesis SHALL sostener, tras las ramas posteriores que editan los sitios de cita, las correcciones bibliograficas B1-B3 aplicadas por c-78: la atribucion correcta de Revina, Buza & Meister (2020) sin BERT ni una exactitud cercana al 91 %; la cobertura de al menos 12 articulos arbitrados publicados entre 2023 y 2026; la atribucion de los rangos interpretativos de Kappa a Landis & Koch (1977); y la higiene de citas (cero citas huerfanas, cero entradas sin usar y toda entrada resoluble por DOI o landing de editorial). El documento MUST NOT reintroducir las citas fabricadas Karchhud et al. (2024) ni Mehdi et al. (2023).

#### Scenario: Atribucion de Revina sin BERT ni 91 %

- **WHEN** se buscan "BERT" y "91" junto a las menciones de Revina et al. (2020) en `03-estado-del-arte.tex` y `08-discusion.tex`
- **THEN** no se atribuye a ese articulo el uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** la entrada citada conserva la clave correcta (`Revina2020_it_tickets`)

#### Scenario: Cobertura 2023-2026 sostenida

- **WHEN** se cuentan las entradas arbitradas del `.bib` con ano entre 2023 y 2026
- **THEN** son al menos 12 y siguen presentes las claves incorporadas por B2
- **AND** cada una es verificable por DOI o URL de editorial/ACL Anthology

#### Scenario: Kappa atribuido a Landis & Koch

- **WHEN** se leen los pasajes que interpretan el coeficiente Kappa en `04-marco-metodologico.tex`
- **THEN** los rangos interpretativos se atribuyen a Landis & Koch (1977)
- **AND** el valor `κ = 0,87` se rotula "casi perfecto", no "sustancial"

#### Scenario: Cero citas huerfanas y cero entradas sin usar

- **WHEN** se cruzan todas las claves citadas contra `Bibliography_base.bib`
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** toda entrada resuelve por DOI o landing de editorial

#### Scenario: Sin citas fabricadas

- **WHEN** se buscan las claves `Karchhud2024` y `Mehdi2023` en el arbol de la tesis
- **THEN** no aparecen ni en `Bibliography_base.bib` ni en ningun `.tex`
