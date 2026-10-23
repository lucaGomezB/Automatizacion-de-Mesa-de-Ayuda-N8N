## ADDED Requirements

### Requirement: Extension del protocolo de revision para calibracion y cascadas

El parrafo de protocolo de revision de `03-estado-del-arte.tex` SHALL declarar, ademas de las cadenas A1-A4 y B1, una extension con dos cadenas de busqueda: C1 (calibracion y estimacion de la confianza en clasificadores y modelos de lenguaje) y C2 (cascadas, enrutamiento y esquemas hibridos con criterio de costo-exactitud), ejecutadas sobre las mismas seis bases, con criterios de inclusion y exclusion propios del grupo C, una regla de seleccion declarada y una fecha de corte propia posterior al 21 de octubre de 2026. La bitacora `docs/Tesis/Correcciones/bitacora-busqueda-c-110.md` SHALL registrar cada consulta de la extension (base, cadena, fecha y resultado) y MUST coincidir con el texto en bases, cadenas, criterios y fecha de corte. Las cadenas A1-A4 y B1, sus criterios y su fecha de corte MUST permanecer sin cambios.

#### Scenario: Cadenas C1 y C2 declaradas en el capitulo

- **WHEN** se lee el parrafo de protocolo de revision en `03-estado-del-arte.tex`
- **THEN** enuncia las cadenas C1 y C2 completas, las seis bases, los criterios de inclusion y exclusion del grupo C y la fecha de corte de la extension
- **AND** la formulacion permite a un lector reproducir la busqueda

#### Scenario: Bitacora consistente con la extension

- **WHEN** se compara la seccion del grupo C de la bitacora con el parrafo de protocolo
- **THEN** cada consulta registra base, cadena, fecha y resultado (claves incorporadas o ausencia de incorporaciones)
- **AND** las cadenas, bases, criterios y fecha de corte coinciden con los del capitulo, y la bitacora no registra consultas que el texto no mencione

#### Scenario: Protocolo original preservado

- **WHEN** se compara el parrafo de protocolo despues del change con la version previa
- **THEN** las cadenas A1-A4 y B1, sus criterios y la fecha de corte del 21 de octubre de 2026 permanecen identicos
- **AND** la afirmacion de vacancia sobre Google Gemini y tickets de soporte en espanol conserva su alcance original

### Requirement: Verificacion individual de las fuentes de calibracion y cascadas

Toda fuente incorporada por la extension C1-C2 SHALL verificarse antes de citarse en tres compuertas: existencia (el DOI resuelve hacia la editorial o, para sedes sin DOI, la pagina oficial de la sede responde), metadatos (titulo, autores, sede, ano y paginas coinciden con Crossref o con los metadatos oficiales de la sede) y contenido (lectura del texto completo y registro de cada afirmacion atribuida con su seccion o pagina). Las fuentes SHALL ser arbitradas y los preprints sin version arbitrada MUST excluirse. Una fuente que no supere alguna compuerta MUST NOT citarse, y ninguna oracion agregada MUST atribuir a una fuente mas de lo que esta sostiene.

#### Scenario: Existencia y metadatos registrados

- **WHEN** se inspecciona la tabla de verificacion del grupo C en la bitacora
- **THEN** cada fuente incorporada registra su DOI o URL oficial, el resultado de la resolucion y el cotejo de metadatos
- **AND** ninguna fuente incorporada carece de alguno de esos registros

#### Scenario: Correspondencia afirmacion-fuente

- **WHEN** se toma cualquier oracion agregada por el change que cite una fuente nueva
- **THEN** la bitacora registra esa afirmacion con la seccion o pagina de la fuente que la sostiene
- **AND** la oracion no atribuye a la fuente resultados que esta no reporta, como resultados sobre Gemini, sobre tickets de soporte o sobre una primera etapa de reglas

#### Scenario: Fuente no verificada o no arbitrada excluida

- **WHEN** una fuente candidata no resuelve, no coincide en metadatos, no trata lo que se le atribuiria o carece de version arbitrada
- **THEN** no aparece citada en ningun `.tex` ni como entrada de `Bibliography_base.bib`
- **AND** la bitacora la registra como excluida con su motivo

### Requirement: Fundamentacion de la calibracion de la confianza con fuentes que la tratan

La seccion del marco teorico sobre procesamiento de lenguaje natural y modelos de lenguaje grandes (`subsec:nlp-llm`) SHALL fundamentar el concepto de calibracion de la confianza con al menos dos fuentes verificadas que efectivamente lo traten, cubriendo su medicion, su correccion posterior y la confianza verbalizada por modelos de lenguaje consultados como servicio. Las oraciones agregadas MUST NOT citar `xuan2025mmluprox` como fuente de calibracion. La seccion SHALL vincular el esquema hibrido del sistema con la nocion de cascada de modelos mediante al menos una fuente verificada.

#### Scenario: Calibracion sostenida por fuentes que la tratan

- **WHEN** se leen en el PDF compilado las oraciones de `subsec:nlp-llm` sobre calibracion
- **THEN** el concepto, su medicion y la confianza verbalizada se apoyan en al menos dos fuentes verificadas de la extension C1-C2
- **AND** ninguna de esas oraciones cita a Xuan et al. (2025)

#### Scenario: Esquema hibrido vinculado con la literatura de cascadas

- **WHEN** se lee la oracion de `subsec:nlp-llm` que presenta el esquema hibrido entre clasificador supervisado y modelo de lenguaje grande
- **THEN** describe la combinacion como una cascada en la que el componente mas economico resuelve los casos para los que su senal de fiabilidad alcanza un umbral y deriva los restantes al mas costoso
- **AND** cita al menos una fuente verificada sobre cascadas de modelos

### Requirement: Estado del arte sobre calibracion de la confianza y cascadas de modelos

El capitulo de estado del arte SHALL contener una subseccion con rotulo `subsec:calibracion-cascadas` que revise la literatura sobre (a) calibracion de la confianza en clasificadores y en modelos de lenguaje grandes, incluidas la confianza verbalizada y el sesgo de etiquetas en la clasificacion por instrucciones, y (b) cascadas de modelos con criterio de costo-exactitud, citando las fuentes verificadas de la extension C1-C2. La oracion introductoria del capitulo SHALL enumerar esta area. Toda afirmacion de vacancia de la subseccion SHALL formularse relativa a las cadenas C1-C2, a las bases consultadas y a la fecha de corte de la extension, y MUST omitirse si la busqueda no la confirma.

#### Scenario: Ambos ejes cubiertos

- **WHEN** se lee la subseccion de calibracion y cascadas en el PDF compilado
- **THEN** al menos una fuente verificada sostiene cada eje (calibracion de la confianza; cascadas de modelos)
- **AND** cada fuente se describe por lo que efectivamente estudia y encuentra

#### Scenario: Vacancia acotada o ausente

- **WHEN** la subseccion enuncia que no se identifico un trabajo con determinadas caracteristicas
- **THEN** la afirmacion declara las cadenas C1-C2 y la fecha de corte de la extension y no se presenta como inexistencia absoluta
- **AND** la bitacora no registra ningun trabajo incorporado o examinado que la refute

#### Scenario: Introduccion del capitulo coherente

- **WHEN** se lee la oracion introductoria de `03-estado-del-arte.tex`
- **THEN** el numero de areas enunciadas coincide con las areas que el capitulo revisa
- **AND** la calibracion de la confianza y las cascadas de modelos figuran entre ellas

### Requirement: Lectura del hallazgo de calibracion y del esquema hibrido a la luz de la literatura

La subseccion de comparacion con la literatura de la discusion (`subsec:comparacion-literatura`) SHALL contrastar con las fuentes verificadas de calibracion y cascadas el hallazgo sobre la confianza autodeclarada, tal como lo formula por etapa del pipeline el capitulo de resultados, y el esquema hibrido de reglas y modelo. El parrafo MUST NOT introducir valores numericos ausentes de `docs/Tesis/Correcciones/numeros-canonicos.md`, salvo cifras de terceros citadas textualmente con su pagina; MUST NOT reintroducir la lectura de "calibracion invertida" del clasificador en su conjunto; y MUST NOT presentar como demostrada la eficiencia del esquema hibrido.

#### Scenario: Hallazgo contrastado con la literatura

- **WHEN** se lee la subseccion de comparacion con la literatura
- **THEN** relaciona el comportamiento de la confianza de la etapa del modelo de lenguaje con lo que la literatura documenta sobre la confianza verbalizada
- **AND** relaciona la derivacion entre etapas del esquema hibrido con el criterio de derivacion de las cascadas de modelos

#### Scenario: Coherencia con el capitulo de resultados

- **WHEN** se compara el parrafo con la subseccion de calibracion del capitulo de resultados (`subsec:calibracion`)
- **THEN** describe el hallazgo por etapa del pipeline y en los mismos terminos que ese capitulo
- **AND** no afirma "calibracion invertida" ni "anti-calibracion" del clasificador en su conjunto

#### Scenario: Sin numeros nuevos ni eficiencia afirmada

- **WHEN** se revisan los valores numericos y las conclusiones del parrafo agregado
- **THEN** todo valor figura en `numeros-canonicos.md` o es una cifra de terceros citada textualmente con su pagina
- **AND** el parrafo no afirma que la eficiencia del esquema hibrido frente a una alternativa basada solo en el modelo haya sido contrastada

### Requirement: Higiene bibliografica de las fuentes de calibracion y cascadas

Las entradas que incorpora la extension C1-C2 SHALL agregarse a `Bibliography_base.bib` en un bloque aditivo comentado, con `author`, `title`, `year`, el campo de publicacion (`booktitle` o `journal`) y `doi` o `url` oficial, con claves `ApellidoAnio_palabra_clave` y con el tipo que corresponde a la naturaleza real de la fuente (`@inproceedings` para actas, `@article` para revistas). Ninguna entrada existente MUST modificarse, ninguna clave MUST duplicarse y toda entrada nueva SHALL citarse al menos una vez en el texto.

#### Scenario: Entradas completas y bien tipadas

- **WHEN** se inspeccionan las entradas del bloque de calibracion y cascadas
- **THEN** cada una incluye autor, titulo, ano, campo de publicacion y `doi` o `url` oficial
- **AND** las actas se tipan `@inproceedings` y la revista TMLR `@article`, sin presentar un preprint como publicacion arbitrada

#### Scenario: Correspondencia citas-bibliografia preservada

- **WHEN** se ejecuta `verify_citations.py` despues del change
- **THEN** reporta cero citas huerfanas y cero entradas sin usar
- **AND** cada clave nueva aparece una sola vez como entrada en `Bibliography_base.bib`

#### Scenario: Entradas existentes intactas

- **WHEN** se inspecciona el diff de `Bibliography_base.bib`
- **THEN** solo contiene lineas agregadas en el bloque nuevo
- **AND** ninguna entrada previa cambia de clave ni de campos

### Requirement: Impacto de paginas de la cobertura de calibracion y cascadas medido y acotado

El change SHALL registrar el numero de paginas del PDF compilado antes y despues de aplicarse, medido sobre el documento completo, y el aumento atribuible a sus inserciones MUST NOT superar tres paginas. Si lo supera, SHALL aplicarse la contingencia declarada en el diseno (reduccion del parrafo de discusion y retiro de fuentes en el orden declarado) antes de cerrar el change. El conteo resultante SHALL quedar registrado para la verificacion final del tope de paginas de la release.

#### Scenario: Conteo registrado antes y despues

- **WHEN** se compila `main.tex` antes y despues de aplicar el change
- **THEN** ambos conteos, medidos sobre el PDF completo, quedan registrados en `tasks.md`
- **AND** se identifica que capitulos o secciones crecieron

#### Scenario: Aumento acotado

- **WHEN** se calcula la diferencia de paginas atribuible al change
- **THEN** es de tres paginas o menos
- **AND** si inicialmente la excedia, la contingencia del diseno se aplico y el conteo final la respeta
