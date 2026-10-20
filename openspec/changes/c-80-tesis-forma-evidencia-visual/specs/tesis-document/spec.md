## MODIFIED Requirements

### Requirement: Table formatting

All tables defined in the LaTeX source SHALL render in the PDF with professional booktabs styling. Every table SHALL contain the correct number of rows and columns matching the source definition. Table composition SHALL be uniform across the document: every table SHALL declare its font size consistently and SHALL set prose columns to ragged-right so that text wraps without excessive inter-word spacing.

#### Scenario: Tables render with booktabs styling
- **WHEN** any page containing a `\begin{table}` environment in the source is inspected in the PDF
- **THEN** the table uses horizontal rules with proper booktabs spacing (`\toprule`, `\midrule`, `\bottomrule`)
- **AND** no ASCII grid characters or raw LaTeX table commands are visible

#### Scenario: Table structural integrity
- **WHEN** the row count of each rendered table is compared to its source definition
- **THEN** every table has at least one data row (no zero-row tables)
- **AND** column alignment matches the source declaration

#### Scenario: Uniform font size across tables
- **WHEN** the font declaration of all 9 tables in the thesis source is compared
- **THEN** every table either declares `\small` or explicitly declares its size following the same convention
- **AND** no table is left without a font-size declaration while its peers declare `\small`

#### Scenario: Prose columns are ragged-right
- **WHEN** the column specification of a table whose cells contain full sentences is inspected
- **THEN** the prose column uses `>{\raggedright\arraybackslash}p{...}` (or equivalent)
- **AND** no fixed-width prose column is left fully justified

## ADDED Requirements

### Requirement: Correccion ortografica y de portada

El documento SHALL estar libre de las cuatro formas ortograficas erroneas detectadas por la auditoria. La correccion MUST ser contextual y MUST NOT alterar verbos legitimos. La portada y los titulos de seccion SHALL contener las tildes correctas del espanol.

#### Scenario: Formas sustantivas corregidas
- **WHEN** se busca en los archivos `.tex` de `paper/sections/` las formas `diseñó`, `completó` y `aquéllos`
- **THEN** cero apariciones de esas formas permanecen
- **AND** las apariciones sustantivas de `desarrolló` (por ejemplo "el desarrolló del modulo") fueron reemplazadas por `desarrollo`

#### Scenario: Verbos legitimos preservados
- **WHEN** se inspeccionan `00-resumen.tex:11` ("el estudio se desarrolló") y `06-implementacion.tex:87` ("el frontend se desarrolló")
- **THEN** ambos usos verbales de `desarrolló` permanecen intactos
- **AND** no se sustituyo el verbo conjugado por el sustantivo

#### Scenario: Portada y titulos con tildes
- **WHEN** se lee la portada (`00-portada.tex`) y los titulos de seccion del documento
- **THEN** las palabras que requieren tilde ("TECNOLOGICA", "Programacion", "Automatizacion", "Republica", "Introduccion", "Conclusiones", entre otras) aparecen con su tilde correcta
- **AND** no queda ninguna ocurrencia de esas palabras sin tilde

#### Scenario: Conteo de errores resuelto
- **WHEN** se cuenta el total de ocurrencias de las cuatro formas en las secciones activas (excluyendo archivos `.bak`)
- **THEN** las 52 apariciones reportadas por la auditoria se resuelven en 50 correcciones (dos verbos legitimos preservados)
- **AND** el barrido de control no devuelve residuos incorrectos

### Requirement: Evidencia visual del sistema y de los resultados

La tesis SHALL incluir las 8 figuras requeridas, embebidas mediante `\includegraphics` dentro de un entorno `figure` con `\caption` y `\label`, en sus ubicaciones naturales. Cada figura SHALL provenir de una fuente reproducible (diagrama Mermaid versionado, script de generacion o captura manual identificada).

#### Scenario: Las ocho figuras existen y estan embebidas
- **WHEN** se listan los archivos de `paper/figures/` y se buscan los comandos `\includegraphics` en `paper/sections/`
- **THEN** existen los archivos de las 8 figuras: diagrama de despliegue, diagrama de secuencia, diagrama entidad-relacion, captura del flujo N8N, captura del panel de administracion, captura del dashboard, boxplot de tiempos y matriz de confusion
- **AND** cada figura esta referenciada por un `\includegraphics` dentro de un `figure`

#### Scenario: Ubicacion natural de cada figura
- **WHEN** se revisa el capitulo donde se discute el artefacto correspondiente
- **THEN** el diagrama de despliegue y el de secuencia aparecen en el Capitulo 5 o el Anexo A
- **AND** el diagrama entidad-relacion aparece en la seccion 5.6 o el Anexo C
- **AND** la captura del flujo N8N aparece en la seccion 6.3 o el Anexo E
- **AND** las capturas del panel de administracion y del dashboard aparecen en la seccion 6.8
- **AND** el boxplot de tiempos aparece en la seccion 7.1 y la matriz de confusion en la seccion 7.2

#### Scenario: Figuras con fuente reproducible
- **WHEN** se inspecciona una figura generada a partir de un diagrama
- **THEN** existe la fuente Mermaid correspondiente en `docs/diagrams/` o en el repositorio
- **AND** las figuras de resultados (boxplot y matriz) fueron generadas por un script reproducible a partir de los datos del corpus o de la matriz reportada
- **AND** las capturas de interfaz se identifican como tales en el texto

#### Scenario: Boxplot de latencias reportado por canal
- **WHEN** se inspecciona la figura del boxplot de tiempos (seccion 7.1)
- **THEN** la figura reporta las latencias POR CANAL (formulario web, correo y telefonia) en paneles separados o en un layout agrupado por canal, en lugar de un unico boxplot que mezcle los tres puntos de ingreso
- **AND** cada canal compara `tiempo_manual_s` contra `tiempo_automatizado_s` dentro del mismo canal
- **AND** la separacion por canal es consistente con la regla de comparabilidad de `docs/medicion-latencia-e2e.md` (los puntos de ingreso no son homogeneos)

#### Scenario: Panel de telefonia con metrica corregida
- **WHEN** se inspecciona el panel de telefonia del boxplot
- **THEN** el valor automatizado usa la metrica corregida de `tiempo_automatizado_s` que incluye la duracion de la llamada/grabacion (correccion de c-77 "Opcion A")
- **AND** si la correccion de c-77 no esta aplicada, el panel se rotula "automatizado = solo post-procesamiento de la llamada (cota inferior)"

### Requirement: Anexos con contenido real

Los anexos A a G SHALL contener contenido real embebido (figura, tabla, listado de codigo o bloque de datos) en lugar de unicamente describirlo en prosa. El Anexo H (especificacion del prompt de Gemini) SHALL incorporarse al documento como una seccion de anexo.

#### Scenario: Cada anexo A-G embebe su artefacto
- **WHEN** se lee cada una de las secciones de `12-anexos.tex`
- **THEN** el Anexo A embebe el diagrama de arquitectura (figura), el Anexo C embebe el esquema de base de datos (tabla o diagrama ER), el Anexo D embebe la especificacion OpenAPI (bloque de codigo o listado), el Anexo E embebe la configuracion del flujo N8N y el Anexo F embebe la estructura o declaracion del corpus
- **AND** cada anexo deja de ser exclusivamente un parrafo descriptivo sin contenido embebido

#### Scenario: Anexo H incorporado
- **WHEN** se busca el Anexo H en los archivos `.tex`
- **THEN** existe una seccion que incorpora el contenido de `docs/anexo_h_prompt_gemini.md` (estructura del prompt y parametros de configuracion)
- **AND** el Anexo H esta referenciado desde el texto principal del documento

#### Scenario: Contenido real y no meramente descriptivo
- **WHEN** se inspecciona un anexo convertido
- **THEN** contiene al menos un entorno `figure`, `table`, `lstlisting` o `verbatim` con contenido
- **AND** el anexo mantiene la prosa introductoria que lo contextualiza

### Requirement: Ausencia de duplicaciones sustantivas

El documento SHALL NOT repetir de forma casi verbatim parrafos equivalentes entre capitulos. El material compartido SHALL aparecer una sola vez en el capitulo que le corresponde, con referencias cruzadas donde sea necesario.

#### Scenario: Par introduccion / marco teorico
- **WHEN** se comparan `01-introduccion.tex:8,10` con `02-marco-teorico.tex:10,12`
- **THEN** la descripcion de Galup2009 no se repite casi verbatim en ambos capitulos
- **AND** cada afirmacion sobre ITSM aparece una sola vez o remite por referencia cruzada

#### Scenario: Par arquitectura / implementacion
- **WHEN** se comparan `05-arquitectura.tex:44` con `06-implementacion.tex:39,41` y se buscan las ocurrencias de "camino de clasificacion unico" (`05:60` y `06:44`)
- **THEN** la descripcion del flujo de orquestacion no se repite en ambos capitulos
- **AND** la afirmacion del camino de clasificacion unico aparece una sola vez, con remision a la otra seccion

#### Scenario: Par discusion / conclusiones
- **WHEN** se comparan `08-discusion.tex:8,10,14` con `09-conclusiones.tex:12,24`
- **THEN** la discusion y las conclusiones no repiten los mismos enunciados
- **AND** la discusion interpreta y las conclusiones sintetizan sin duplicar frases

### Requirement: Consistencia de la version de N8N

La version de N8N citada en el documento SHALL ser unica y consistente con la version realmente desplegada (2.11.2). El documento MUST NOT contener acotaciones obsoletas sobre indisponibilidad de imagenes en Docker Hub.

#### Scenario: Acotacion obsoleta retirada
- **WHEN** se busca en las secciones `.tex` la cadena "1.62" o "no se encuentra disponible en Docker Hub"
- **THEN** cero apariciones permanecen en `05-arquitectura.tex` y `06-implementacion.tex`
- **AND** la version de N8N alli citada es consistente con la del Anexo E

#### Scenario: Version reconciliada
- **WHEN** se comparan las menciones de la version de N8N en 5, 6 y el Anexo E
- **THEN** todas refieren la misma version (2.11.2)
- **AND** no queda ninguna contradiccion interna sobre la version desplegada

### Requirement: Afirmaciones respaldadas por la evidencia

Las afirmaciones de la discusion (8.1) y de las conclusiones (9.1) SHALL estar sostenidas por la evidencia empirica reportada en el Capitulo 7 (resultados) o por la literatura citada. Los juicios de valor no respaldados SHALL ser retirados o reformulados en terminos de la evidencia disponible.

#### Scenario: Juicios de valor sin respaldo retirados de la discusion
- **WHEN** se lee la seccion 8.1 de `08-discusion.tex`
- **THEN** expresiones como "superan ampliamente", "valida la hipotesis subsidiaria", "consecuencia deseable" y "materializa el esquema human in the loop buscado" no se presentan como hechos no medidos
- **AND** toda magnitud afirmada remite a los valores corregidos del Capitulo 7 (reduccion de tiempo 71,2~% con cota conservadora 65,6~% con -10~s y 68,6~% con -5~s, y exactitud 73,5~%)

#### Scenario: Juicios de valor sin respaldo retirados de las conclusiones
- **WHEN** se lee la seccion 9.1 de `09-conclusiones.tex`
- **THEN** expresiones como "cumplido satisfactoriamente", "supero con holgura", "no deja espacio para la duda razonable", "resultado poco frecuente", "trasciende lo meramente estadistico" y "activo que excede" fueron retiradas o reformuladas
- **AND** las conclusiones se sustentan en los resultados de la prueba de Wilcoxon (\(W = 363\), \(p = 3{,}08 \times 10^{-32}\), \(r = 0{,}9639\), cifras corregidas por c-76) y en las metricas de clasificacion reportadas (exactitud 73,5~%, macro-F1 0,5207)

#### Scenario: La afirmacion de garantia metodologica queda acotada
- **WHEN** se lee el parrafo de rigor metodologico en `08-discusion.tex:16`
- **THEN** la afirmacion de que la separacion de datos constituye una garantia que "no todos los trabajos del area documentan con el mismo nivel de explicitacion" se reformula sin la comparacion no verificada contra la literatura
- **AND** se describe la practica propia (aislamiento del corpus de validacion) sin adjudicar a terceros una carencia no medida
