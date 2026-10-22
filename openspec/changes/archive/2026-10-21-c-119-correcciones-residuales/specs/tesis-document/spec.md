## ADDED Requirements

### Requirement: Correccion de defectos residuales de forma y consistencia del PDF

La documentacion LaTeX de la tesis SHALL renderizar sin artefactos de forma visibles y con rotulos y referencias cruzadas consistentes. En particular: no MUST imprimirse ningun fragmento del preambulo tabular como texto; toda celda de tabla MUST estar sintacticamente completa; las remisiones a tablas MUST resolverse por `\ref{}` y no por numeros literales; los anexos MUST rotularse en espanol; el vocabulario de servicios internos MUST corresponder al despliegue real; y la entrada de las referencias bibliograficas MUST presentarse como nivel de seccion en el indice. Estas correcciones SHALL preservar el contenido y los numeros canonicos, sin alterar el presupuesto de paginas del cuerpo.

#### Scenario: Sin fragmento de preambulo tabular visible

- **WHEN** se extrae el texto del PDF compilado y se busca el literal "aggedright"
- **THEN** no aparece ninguna ocurrencia (el preambulo de columna `\raggedright\arraybackslash` esta restaurado en una sola linea)
- **AND** la tabla de tiempos conserva exactamente su contenido y sus anchos de columna

#### Scenario: Celda de la tabla de cumplimiento cerrada

- **WHEN** se lee la fila del objetivo especifico 2 en la tabla de cumplimiento del Capitulo 9
- **THEN** el intervalo de confianza se muestra como `IC [67,0 %, 79,1 %]` con el corchete cerrado
- **AND** el macro-F1 0,5207 queda fuera del intervalo, como texto separado

#### Scenario: Remision a la tabla de endpoints resuelta

- **WHEN** se lee la remision a los puntos de entrada REST en el Anexo de especificacion OpenAPI
- **THEN** el numero de tabla se resuelve mediante `\ref` al rotulo real del contrato REST (`tab:api`)
- **AND** no queda ningun `Tabla~N` literal que apunte a un numero incorrecto

#### Scenario: Anexos rotulados en espanol

- **WHEN** se inspecciona el indice general y la pagina de anexos del PDF compilado
- **THEN** el rotulo de anexos aparece en espanol, coherente con el termino usado en el cuerpo ("Anexo"/"Anexos")
- **AND** no queda el rotulo "Appendices" en ingles

#### Scenario: Redis ausente de los servicios internos

- **WHEN** se lee la descripcion de la comunicacion interna entre servicios en el Capitulo 5
- **THEN** la enumeracion de servicios internos incluye N8N, backend y PostgreSQL
- **AND** no incluye Redis, retirado en el change c-62

#### Scenario: Entrada de referencias bibliograficas en el indice

- **WHEN** se inspecciona la entrada "Referencias bibliograficas" en el indice general
- **THEN** figura como entrada de nivel de seccion y su destino hipervinculo no reutiliza el ancla de la ultima subseccion del capitulo anterior
- **AND** si la unica anomalia restante es el destino del hipervinculo, se documenta como limitacion cosmetica aceptada sin alterar el nivel visible de la entrada

### Requirement: Afirmaciones cuantitativas respaldadas por medicion

Toda afirmacion cuantitativa de la tesis SHALL estar respaldada por una medicion reproducible presente en el repositorio (por ejemplo, en `evaluation/`). Una afirmacion cuantitativa sin medicion de respaldo MUST reformularse de forma cualitativa o retirarse, y MUST NOT conservar el valor numerico.

#### Scenario: Sin puntos porcentuales de F1 sin medicion

- **WHEN** se busca en los archivos de seccion afirmaciones de puntos porcentuales de F1 atribuidas al enriquecimiento del prompt
- **THEN** no aparece el valor "4 puntos porcentuales de F1" ni otro numero inventado
- **AND** la afirmacion se expresa de forma cualitativa ("mejoro la robustez ... sobre transcripciones automaticas")
