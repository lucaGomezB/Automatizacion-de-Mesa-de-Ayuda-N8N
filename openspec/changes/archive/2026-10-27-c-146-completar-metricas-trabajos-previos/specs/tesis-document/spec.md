## MODIFIED Requirements

### Requirement: Completitud de las metricas de la tabla de trabajos academicos

La tabla `tab:trabajos-academicos` SHALL consignar en la columna "Metrica reportada" de cada trabajo la cifra principal que su resumen o su texto completo accesible reporten textualmente (nombre de la metrica, valor y modelo o condicion), y en "Corpus/idioma" el tamano y el idioma cuando la fuente los establezca. Toda fila SHALL reportar su metrica de fuente o declarar "no reportado en el alcance revisado" con su motivo abreviado: la leyenda "no reportado en el alcance revisado" SHALL quedar solo en las celdas cuya fuente accesible no consigne el dato. Cuando exista un texto completo de acceso abierto (por ejemplo, el manuscrito aceptado alojado por los autores), sus metricas SHALL extraerse y la fuente SHALL quedar registrada en `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`; MUST NOT invocarse el acceso cerrado de la version editorial como motivo para dejar la celda sin extraer mientras exista una version de acceso abierto verificable. Las obras cuya unica version accesible sea de acceso cerrado SHALL permanecer declaradas como "no reportado en el alcance revisado" con su motivo hasta que se obtenga acceso institucional. Cuando la obra original sea de acceso cerrado pero exista un trabajo companero de acceso abierto de los mismos autores sobre el mismo problema, la celda SHALL poder apuntar a ese trabajo accesible con sus metricas, atribuyendolas explicitamente a ese trabajo companero, sin sustituir la declaracion "no reportado en el alcance revisado" de la obra original. Cada celda completada SHALL tener su procedencia (DOI o URL consultada, fecha de consulta, tipo de version y ubicacion en la fuente) registrada en `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`. El documento MUST NOT recalcular, promediar ni inferir cifras, MUST NOT agregar entradas a `Bibliography_base.bib` salvo la entrada del trabajo companero de acceso abierto (que resuelve por DOI), y MUST NOT versionar ninguna copia de los articulos.

#### Scenario: Metricas completadas desde la fuente

- **WHEN** se contrasta cada celda de metrica de `tab:trabajos-academicos` con su registro de procedencia
- **THEN** el valor consignado coincide textualmente con el de la fuente registrada
- **AND** la celda identifica la metrica, el valor y el modelo o la condicion a que corresponde

#### Scenario: Extraccion obligatoria del texto de acceso abierto

- **WHEN** una obra de la tabla tiene una version de acceso abierto verificable (manuscrito aceptado, postprint o version del editor)
- **THEN** su metrica se extrae de ese texto y la fuente queda registrada con su tipo de version, URL, fecha de consulta y ubicacion
- **AND** la celda no declara "no reportado en el alcance revisado" por el acceso cerrado de una version distinta

#### Scenario: Obras de acceso cerrado declaradas con motivo

- **WHEN** la unica version accesible de una obra es de acceso cerrado y no se dispone de acceso institucional
- **THEN** su fila declara "no reportado en el alcance revisado" con el motivo (acceso cerrado y falta de credenciales institucionales)
- **AND** la fila permanece declarada asi hasta que se obtenga el acceso institucional, con su DOI registrado como seguimiento pendiente

#### Scenario: Residuo no reportado justificado

- **WHEN** una celda conserva "no reportado en el alcance revisado"
- **THEN** el registro de procedencia documenta que el resumen no consigna el dato y que el texto completo no fue accesible o tampoco lo consigna
- **AND** la celda declara ese motivo de forma abreviada

#### Scenario: Companero accesible de una obra cerrada

- **WHEN** una obra de la tabla es de acceso cerrado pero sus autores publicaron un trabajo companero de acceso abierto sobre el mismo problema
- **THEN** la celda conserva "no reportado en el alcance revisado" para la obra original y agrega las metricas del trabajo companero, atribuidas explicitamente a ese trabajo con su clave y su identificador
- **AND** la procedencia del trabajo companero (URL, tipo de version, DOI y ubicacion) queda registrada en el registro de procedencia

#### Scenario: Obra cerrada sin alternativa accesible

- **WHEN** una obra de la tabla es de acceso cerrado y no tiene copia ni trabajo companero de acceso abierto de sus autores
- **THEN** su fila permanece cualitativa con el motivo "no reportado en el alcance revisado"
- **AND** el registro de procedencia consigna la verificacion de ausencia (OpenAlex y Semantic Scholar)

#### Scenario: Sin altas bibliograficas ni citas huerfanas

- **WHEN** se ejecuta `verify_citations.py` y se inspecciona el diff de `Bibliography_base.bib` tras completar la tabla
- **THEN** no hay citas huerfanas ni entradas sin usar
- **AND** la unica entrada agregada es la del trabajo companero de acceso abierto (exigida por la clausula del companero), esta citada en el texto y resuelve por DOI
- **AND** ninguna entrada existente de `Bibliography_base.bib` cambia

## ADDED Requirements

### Requirement: Registro de procedencia de la extraccion de c-146

El registro `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md` SHALL incorporar una seccion c-146 que documente la extraccion de la fila de Colavito, Lanubile y Novielli (2025): la URL del manuscrito aceptado, su tipo de version (postprint aceptado de acceso abierto), cada valor consignado en la tabla con su ubicacion en el manuscrito; la procedencia del trabajo companero de acceso abierto de Paramesh y Shreedhara (Ramya, Paramesh y Shreedhara, arXiv:2103.15822) con su URL, tipo de version, DOI, clave y metricas verificadas; el verdicto de Paket et al. (2024) (sin copia ni alternativa accesible, verificado en OpenAlex y Semantic Scholar); y el seguimiento pendiente de las dos obras de acceso cerrado con su DOI. El registro SHALL conservar las secciones de c-135 sin reescribir su historia. El cambio MUST NOT versionar ninguna copia de los articulos ni modificar los numeros canonicos de la tesis.

#### Scenario: Seccion c-146 con procedencia completa

- **WHEN** se revisa `docs/Tesis/Correcciones/extraccion-metricas-trabajos-c-135.md`
- **THEN** existe una seccion c-146 que indica la URL del manuscrito aceptado de Colavito, el tipo de version, los valores extraidos y su ubicacion en la fuente
- **AND** la seccion c-146 incluye la procedencia del trabajo companero accesible de Paramesh (URL, tipo de version, DOI, clave y metricas) y el verdicto de Paket 2024
- **AND** las secciones de c-135 permanecen sin reescritura

#### Scenario: Seguimiento de las obras de acceso cerrado

- **WHEN** se lee el seguimiento pendiente de la seccion c-146
- **THEN** figuran Paramesh y Shreedhara (2019) con DOI `10.1007/978-981-13-2514-4_28` y Paket et al. (2024) con DOI `10.1109/UBMK63289.2024.10773473`
- **AND** se declara el acceso institucional requerido para extraer sus metricas
- **AND** se distingue la obra original cerrada de Paramesh de su trabajo companero accesible (arXiv:2103.15822), que no requiere acceso institucional

#### Scenario: Companero accesible de Paramesh consignado

- **WHEN** se lee la fila de Paramesh y Shreedhara (2019) en el PDF compilado y la seccion c-146
- **THEN** la celda conserva "no reportado en el alcance revisado (texto cerrado)" y agrega las metricas del trabajo companero accesible (arbol de decision 90,60 % y RandomForest 91,81 %), atribuidas a Ramya, Paramesh y Shreedhara (arXiv:2103.15822)
- **AND** la prosa de la subseccion cita la clave nueva y esta aparece en `Bibliography_base.bib`

#### Scenario: Sin copias de los articulos ni cambios de numeros canonicos

- **WHEN** se inspecciona el diff del cambio
- **THEN** no se agrega ninguna copia (PDF u otro formato) de los articulos citados
- **AND** `docs/Tesis/Correcciones/numeros-canonicos.md` y los capitulos de resultados no tienen modificaciones atribuibles a este cambio
