## MODIFIED Requirements

### Requirement: Citation rendering

All citation commands in the 11 section files SHALL render correctly in the compiled PDF. Every `\textcite{}` and `\parencite{}` command SHALL produce a properly formatted in-text citation in APA 7th edition style. Every cited reference SHALL appear in the final bibliography section.

#### Scenario: In-text citations render
- **WHEN** the PDF is opened and any page with a citation command in the source is inspected
- **THEN** the citation displays as APA 7th formatted text (e.g., "Author (Year)" for `\textcite`, "(Author, Year)" for `\parencite`)
- **AND** no raw LaTeX citation commands are visible in the rendered text

#### Scenario: Bibliography is complete
- **WHEN** the bibliography section at the end of the PDF is inspected
- **THEN** it contains exactly the set of entries declared in `Bibliography_base.bib` (the count grows after c-78 and is not fixed at 33)
- **AND** each entry is formatted in APA 7th style

#### Scenario: Citation-bibliography cross-reference integrity
- **WHEN** a verification script cross-references all `\cite{}`, `\textcite{}`, and `\parencite{}` keys against `Bibliography_base.bib`
- **THEN** zero orphan citations are found (every citation key exists as a `@` entry in the .bib file)
- **AND** zero unused bibliography entries exist (every .bib entry is cited at least once in the text)
- **AND** all cited references are verifiable in at least one academic database (Google Scholar, Crossref, Scopus, or equivalent)

#### Scenario: Orphan-citation status documented
- **WHEN** the change is applied
- **THEN** the state of orphan citations and unused entries is documented in the tasks with the exact verification command and its output
- **AND** the two orphan citations of the audited v7 version are identified explicitly as Karchhud et al. (2024) and Mehdi et al. (2023), both VERIFIED AS FABRICATED (no matching article or author in Crossref/OpenAlex), already removed between v7 and v9
- **AND** the document MUST NOT reintroduce either fabricated reference
- **AND** the two claims those citations used to support (the "88 % a 94 %" range in `08-discusion.tex:20` and the AI-adoption claim in `03-estado-del-arte.tex:12`) are re-cited with real sources or removed/reformulated

#### Scenario: Every citation resolves by DOI or landing page
- **WHEN** each entry of `Bibliography_base.bib` is checked against DOI resolution or its publisher/ACL landing page
- **THEN** every citation resolves to a real publication
- **AND** any citation that cannot be resolved is removed or replaced (guard against the fabrication cluster identified in v7)

## ADDED Requirements

### Requirement: Atribucion correcta de Revina et al. (2020)

El capitulo de estado del arte (seccion 3.3) y el de discusion (seccion 8.2) SHALL describir el aporte de Revina, Buza & Meister (2020) conforme al contenido real del articulo "IT Ticket Classification: The Simpler, the Better" (IEEE Access, vol. 8, pp. 193380-193395, 2020). El documento MUST NOT atribuir a ese articulo el uso de arquitecturas basadas en BERT, una exactitud cercana al 91 % ni la conclusion de que los modelos preentrenados transfieren conocimiento linguistico al dominio de tickets sin ajuste fino.

#### Scenario: Sin BERT ni 91 % atribuidos a Revina
- **WHEN** se lee la seccion 3.3 o la 8.2 en busca de las referencias a Revina et al. (2020)
- **THEN** no se le atribuye uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** no se le atribuye la conclusion de transferencia de modelos preentrenados al dominio

#### Scenario: Conclusion real de Revina et al. enunciada
- **WHEN** se lee la descripcion de Revina et al. (2020)
- **THEN** el texto enuncia que el articulo concluye que los metodos simples y explicables con un conjunto pequeno de rasgos linguisticos del dominio son competitivos para clasificar tickets de TI
- **AND** el texto enuncia que los embeddings preentrenados pueden rendir peor por el vocabulario especifico del dominio

#### Scenario: Tension incorporada en la discusion
- **WHEN** se lee la seccion 8.2 del capitulo de discusion
- **THEN** la evidencia contraria de Revina et al. se integra como una tension explicita para el enfoque basado en LLM del presente trabajo
- **AND** la discusion explica por que la evidencia contraria fortalece (no debilita) el analisis

### Requirement: Estado del arte modernizado con literatura arbitrada 2023-2026

El estado del arte SHALL incorporar al menos 12 articulos arbitrados publicados entre 2023 y 2026, verificables por DOI, que cubran al menos: (a) clasificacion de tickets y enrutamiento de mesa de servicio de TI con LLM o transformers; (b) evaluacion zero-shot / few-shot de LLM multilingues; (c) desempeno de LLM en espanol o en variantes de espanol de Iberoamerica. Toda afirmacion cuantitativa comparativa del estado del arte y de la discusion SHALL estar respaldada por una cita a una referencia verificable.

#### Scenario: Referencias 2023-2026 incorporadas
- **WHEN** se inspecciona `Bibliography_base.bib`
- **THEN** contiene al menos 12 entradas nuevas arbitradas con ano de publicacion entre 2023 y 2026
- **AND** cada una es verificable por DOI o URL de editorial/ACL Anthology

#### Scenario: Cobertura de las tres lineas tematicas
- **WHEN** se revisan los articulos incorporados
- **THEN** al menos uno aborda clasificacion de tickets o enrutamiento de mesa de servicio con LLM o transformers
- **AND** al menos uno aborda evaluacion zero-shot o few-shot multilingue
- **AND** al menos uno aborda el desempeno de LLM en espanol o en espanol de Iberoamerica

#### Scenario: Afirmaciones sin cita resueltas
- **WHEN** se lee la afirmacion "88 % a 94 % de exactitud" en `08-discusion.tex:20` o la afirmacion sobre literatura few-shot en `03-estado-del-arte.tex:30`
- **THEN** cada afirmacion cita una referencia verificable que la sostiene, o ha sido retirada o reformulada sin el rango numerico
- **AND** no queda ninguna afirmacion cuantitativa comparativa sin respaldo en el estado del arte ni en la discusion

#### Scenario: Brecha de Gemini en espanol declarada
- **WHEN** se presenta la contribucion del trabajo
- **THEN** el documento declara explicitamente que no existe un articulo arbitrado 2023-2026 que evalue Google Gemini especificamente sobre tickets de soporte en espanol
- **AND** no se fabrica ni se atribuye una referencia inexistente para cubrir esa brecha

### Requirement: Fuente de la interpretacion del coeficiente Kappa

El documento SHALL atribuir los rangos interpretativos del coeficiente Kappa a Landis & Koch (1977) y no a Cohen (1960). El valor obtenido (\(\kappa = 0{,}87\)) SHALL rotularse como "casi perfecto" conforme a esos rangos, tanto en la seccion de metodologia (4.4) como en la de amenazas a la validez (4.8).

#### Scenario: Landis y Koch citados para los rangos
- **WHEN** se lee el pasaje que interpreta el valor de Kappa en 4.4 o en 4.8
- **THEN** los rangos de interpretacion se atribuyen a Landis & Koch (1977)
- **AND** existe una entrada `Landis1977_kappa` en `Bibliography_base.bib` con DOI 10.2307/2529310
- **AND** Cohen (1960) permanece citado solo por la definicion del coeficiente

#### Scenario: Rotulo "casi perfecto"
- **WHEN** se lee la interpretacion de \(\kappa = 0{,}87\)
- **THEN** el texto lo rotula como "casi perfecto"
- **AND** no lo rotula como "sustancial"

### Requirement: Higiene de metadatos bibliograficos

Las entradas de `Bibliography_base.bib` SHALL reflejar la autoria, editorial y estado de publicacion reales de cada fuente. Las citas en el texto SHALL seguir el estilo APA 7 para el separador entre autor y ano en las citas con "et al.".

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
