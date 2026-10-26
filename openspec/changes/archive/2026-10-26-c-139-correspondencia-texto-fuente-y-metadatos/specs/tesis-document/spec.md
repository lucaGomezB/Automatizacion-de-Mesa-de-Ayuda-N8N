## ADDED Requirements

### Requirement: Atribuciones del eje de modelos de lenguaje conformes al contenido de las fuentes

El eje de procesamiento de lenguaje natural y modelos de lenguaje grandes del marco teorico (seccion 2.4) y el estado del arte multilingue del capitulo 3 SHALL atribuir a cada fuente solo lo que esa fuente sostiene, contrastado con su texto completo cuando es de acceso abierto o con el resumen de la pagina del editor. El documento MUST NOT citar Xuan et al. (2025) como fuente de calibracion de la confianza, MUST NOT citar Lai et al. (2023) como evidencia de sensibilidad a la redaccion del prompt, MUST NOT citar Zhang et al. (2023) como evidencia de generalizacion fuera del ingles, y MUST NOT atribuir a Mayor-Rocher et al. (2026) ni a Grandury et al. (2025) diferencias de desempeno por dialecto que esas obras no reportan. La fundamentacion bibliografica de la calibracion SHALL provenir de fuentes que estudien la calibracion (incorporadas por c-138); hasta entonces el parrafo MUST NOT conservar una cita que no la trate.

#### Scenario: Calibracion sin atribucion a un benchmark de rendimiento

- **WHEN** se lee el parrafo de la seccion 2.4 que define la calibracion de la confianza
- **THEN** el parrafo no cita `xuan2025mmluprox`
- **AND** ninguna fuente citada en ese parrafo es una obra que no trate la calibracion

#### Scenario: Xuan et al. citado por lo que sostiene

- **WHEN** se buscan todas las citas de `xuan2025mmluprox` en las secciones de la tesis
- **THEN** cada una le atribuye solo resultados de rendimiento multilingue (benchmark de 29 idiomas, caida del desempeno en los idiomas con menos recursos, resultados desagregados por idioma)
- **AND** ninguna le atribuye resultados sobre calibracion, confianza o incertidumbre

#### Scenario: Diseno del prompt respaldado por la fuente adecuada

- **WHEN** se lee el parrafo de la seccion 2.4 sobre el diseno del prompt
- **THEN** Lai et al. (2023) no se cita como evidencia de sensibilidad a la redaccion del prompt
- **AND** Ahuja et al. (2023) se cita solo por su comparacion de estrategias de prompting entre idiomas
- **AND** no se afirma un efecto del orden o de la seleccion de los ejemplos sin una fuente que lo estudie

#### Scenario: Idiomas, alternancia de codigo y variedades del espanol

- **WHEN** se leen las citas de Lai et al. (2023), Zhang et al. (2023), Grandury et al. (2025) y Mayor-Rocher et al. (2026)
- **THEN** Lai et al. se cita por el ajuste por instrucciones de modelos abiertos concentrado en el ingles y en pocos idiomas, Zhang et al. por el rendimiento ante textos con alternancia de codigo, Grandury et al. por su tabla de clasificacion de variedades del espanol y Mayor-Rocher et al. por su evaluacion con pruebas de espanol como lengua extranjera
- **AND** a ninguna se le atribuyen diferencias de desempeno atribuibles al dialecto que la obra no reporte

#### Scenario: Agrupamientos de citas coherentes

- **WHEN** se lee un comando de cita con varias claves en el estado del arte multilingue del capitulo 3
- **THEN** cada clave del agrupamiento sostiene la afirmacion a la que se adjunta
- **AND** Lai et al. y Zhang et al. no respaldan la afirmacion de que el rendimiento favorece a los idiomas con mas recursos

### Requirement: Sintesis del estado del arte y recomendaciones coherentes con la evidencia comparativa citada

Las afirmaciones de sintesis del estado del arte, de la discusion y de las recomendaciones SHALL ser coherentes con los resultados de las fuentes en que se apoyan. El documento MUST NOT afirmar que la literatura reciente confirma un desplazamiento del enfoque clasico hacia los LLM cuando sus fuentes comparativas (Paket et al., 2024; Colavito et al., 2025) encuentran que los modelos tipo BERT igualan o superan a los LLM generativos, y MUST NOT citar Touvron et al. (2023) como evidencia de que los LLM desplegados localmente son competitivos en clasificacion mediante prompts. Toda caracterizacion de una obra citada en estas secciones SHALL poder contrastarse con su resumen o con su texto completo.

#### Scenario: Sintesis del estado del arte sin desplazamiento contrario a la evidencia

- **WHEN** se lee la oracion de sintesis que precede a la tabla `tab:trabajos-academicos`
- **THEN** no afirma que la literatura confirme un desplazamiento hacia arquitecturas basadas en LLM
- **AND** refleja que en las comparaciones directas relevadas los modelos tipo BERT igualan o superan a los LLM generativos, con cita explicita a `paket2024itservice` y `colavito2025benchmarking`

#### Scenario: Llama 2 citado por la disponibilidad de pesos abiertos

- **WHEN** se lee la recomendacion sobre el clasificador supervisado y los modelos de codigo abierto en el capitulo de recomendaciones
- **THEN** `Touvron2023_llama2` se cita solo por la disponibilidad de modelos de pesos abiertos aptos para despliegue local
- **AND** la competitividad en clasificacion no se le atribuye
- **AND** se consigna que en clasificacion de tickets con muchas clases los modelos tipo BERT superaron a LLM abiertos como Llama y Mistral (`paket2024itservice`)

#### Scenario: Caracterizaciones contrastables con la fuente

- **WHEN** se contrastan las citas de Colavito et al. (2025) en el marco teorico y de Jurafsky y Martin en la seccion 2.4 con el resumen o el indice de la version citada
- **THEN** cada caracterizacion se limita a lo que esa evidencia sostiene
- **AND** las inferencias propias de los autores no se presentan como resultados de la fuente

#### Scenario: Cobertura del espanol en la discusion respaldada

- **WHEN** se lee el parrafo de la discusion sobre el desempeno en espanol rioplatense frente a idiomas de mayor cobertura
- **THEN** la afirmacion de que diversos trabajos senalan la menor cobertura de los idiomas distintos del ingles cita fuentes que la sostienen
- **AND** no se menciona un desempeno reportado para el aleman sin una fuente que lo reporte

### Requirement: Cifras de Paramesh y Shreedhara (2019) localizadas o reformuladas

Toda cifra atribuida a Paramesh y Shreedhara (2019) (tamano del corpus, idioma, representacion textual o exactitud) SHALL acompanarse de la pagina del capitulo de la que proviene, o bien SHALL dejar de atribuirse si no puede localizarse en el texto completo. En ausencia de verificacion, la descripcion de la obra SHALL limitarse a lo que sostiene su resumen (comparacion de Naive Bayes multinomial, regresion logistica, k vecinos mas cercanos y SVM sobre tickets reales de una mesa de servicio de infraestructura de TI, con SVM como el clasificador de mejor desempeno) y las celdas de la tabla de trabajos academicos SHALL declarar "no reportado en el alcance revisado". La autoria MUST corresponder a la registrada en Crossref (Paramesh, S. P., y Shreedhara, K. S.).

#### Scenario: Cifras con pagina

- **WHEN** la tesis atribuye a `Paramesh2019_it_service_desk` el tamano del corpus, el idioma, la representacion TF-IDF o una exactitud
- **THEN** cada cita que acompana esas cifras indica la pagina del capitulo
- **AND** cada cifra coincide con la que figura en esa pagina

#### Scenario: Cifras no verificables retiradas

- **WHEN** las cifras no pueden localizarse en el texto completo
- **THEN** ninguna seccion atribuye a la obra 10.000 tickets, el idioma ingles, la representacion TF-IDF ni una exactitud de 87 %
- **AND** la fila de la obra en `tab:trabajos-academicos` declara "no reportado en el alcance revisado" para el corpus y la metrica, con el resultado cualitativo que sostiene el resumen

#### Scenario: Umbral del 85 % sin cifra no localizada

- **WHEN** se lee la justificacion del umbral de exactitud del 85 % en la introduccion
- **THEN** su primer criterio no se apoya en una cifra de Paramesh y Shreedhara que no haya sido localizada con pagina
- **AND** el criterio sigue declarando su fuente

#### Scenario: Autoria y caracterizacion de la obra

- **WHEN** se inspecciona la entrada `Paramesh2019_it_service_desk` y se lee su descripcion en el estado del arte
- **THEN** la entrada conserva los autores Paramesh y Shreedhara
- **AND** el texto no presenta la obra como uno de los primeros trabajos exhaustivos del area ni la nombra "Paramesh y Ramya"

### Requirement: Entradas bibliograficas de las normas y marcos del capitulo de cumplimiento

Las normas y marcos que el capitulo 11 declara adoptados SHALL tener entrada propia en `Bibliography_base.bib` y cita en el texto: ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701 en su edicion vigente, NIST CSF 2.0 y el Decreto 1558/2001 reglamentario de la Ley 25.326. Cada entrada SHALL verificarse antes de agregarse contra la ficha oficial del organismo (ISO, NIST, InfoLEG) o su DOI, e incluir organismo autor, titulo, ano, identificador (numero de norma, numero de documento o de decreto) y `doi` o `url`, con `urldate` cuando se cita por URL. El documento MUST NOT citar como marco adoptado una edicion retirada (ISO/IEC 27701:2019, retirada el 2025-10-14) y MUST NOT incorporar datos no verificados. Las afirmaciones del capitulo que la cita formal vuelve contrastables SHALL coincidir con las normas citadas.

#### Scenario: Entradas presentes y verificadas

- **WHEN** se inspecciona `Bibliography_base.bib`
- **THEN** existen las entradas `ISO27001_2022`, `ISO27002_2022`, `ISO27701_2025`, `NIST2024_csf` y `Decreto1558_2001`, con autor institucional, titulo, ano e identificador
- **AND** `NIST2024_csf` declara el DOI `10.6028/NIST.CSWP.29` y las demas una `url` de la ficha oficial con `urldate`
- **AND** las claves contienen solo letras, digitos y guiones bajos

#### Scenario: Edicion vigente de ISO/IEC 27701

- **WHEN** se lee la enumeracion de marcos adoptados del capitulo 11 y su cita
- **THEN** ISO/IEC 27701 se identifica con su edicion vigente (2025) y se describe como norma de gestion de la privacidad
- **AND** no se cita la edicion 2019 como marco adoptado

#### Scenario: Citas en el capitulo de cumplimiento

- **WHEN** se lee el capitulo 11
- **THEN** la primera mencion de cada norma o marco adoptado lleva su cita y el decreto reglamentario de la Ley 25.326 se cita junto a su mencion
- **AND** no hay citas dentro de titulos de seccion, leyendas de tabla ni lineas de fuente de tabla

#### Scenario: Afirmaciones contrastables con las normas citadas

- **WHEN** se leen la introduccion de la tabla de alineacion ISO y la del perfil NIST
- **THEN** los controles se ubican en ISO/IEC 27002:2022 y en el Anexo A de ISO/IEC 27001:2022, no en un Anexo A de ISO/IEC 27002:2022
- **AND** la escala de madurez de 0 a 4 se declara propia del relevamiento y no se presenta como definida por NIST CSF 2.0

### Requirement: Referencias metodologicas primarias de los procedimientos estadisticos

La prueba de rangos con signo, el analisis de potencia a priori y el bootstrap percentil SHALL respaldarse en el marco metodologico con una referencia primaria verificada, ademas de la referencia de implementacion (SciPy): Wilcoxon (1945), *Biometrics Bulletin*, 1(6), 80-83, DOI 10.2307/3001968; Cohen (1988), *Statistical Power Analysis for the Behavioral Sciences*, 2.a ed.; y Efron y Tibshirani (1993), *An Introduction to the Bootstrap*. Las entradas MUST NOT declarar un DOI que corresponda a otra edicion o reedicion de la obra.

#### Scenario: Citas en el marco metodologico

- **WHEN** se lee el capitulo 4 donde se declaran la prueba de Wilcoxon, el bootstrap percentil y el analisis de potencia
- **THEN** cada procedimiento cita su referencia primaria (`Wilcoxon1945_individual_comparisons`, `Efron1993_bootstrap`, `Cohen1988_power_analysis`)
- **AND** `Virtanen2020_scipy` sigue citada como referencia de implementacion

#### Scenario: Metadatos de las referencias de metodo verificados

- **WHEN** se inspeccionan las tres entradas nuevas
- **THEN** Wilcoxon (1945) figura en la revista *Biometrics Bulletin*, volumen 1, numero 6, con su DOI resoluble
- **AND** Efron y Tibshirani (1993) declaran un DOI que resuelve a la edicion de 1993, y Cohen (1988) no declara el DOI de la reedicion de 2013

### Requirement: Metadatos bibliograficos coherentes con catalogos y editores (dictamen v1.1.0)

Las entradas senaladas por el dictamen v1.1.0 SHALL corregirse conforme a Crossref, a la ficha del editor o a un catalogo, y los anos de los libros SHALL seguir un criterio uniforme: el ano de copyright de la obra (criterio APA 7), o el de la version consultada en el caso de un borrador vivo. `Paramesh2019_it_service_desk` SHALL declarar el titulo del libro, su subtitulo, los editores y la serie; `Jurafsky2023_speech_language` SHALL declarar la URL del borrador y la fecha de la version consultada; `liu2025tickit` SHALL declarar la sede FSE Companion 2025. Toda entrada `@manual`, `@misc` u `@online` citada por URL SHALL tener `urldate`, y la fecha de consulta MUST NOT imprimirse dos veces. Ninguna `note` SHALL usar punto y coma, que el estilo suprime al imprimir. Las claves existentes MUST NOT renombrarse.

#### Scenario: Capitulo de libro con sus metadatos completos

- **WHEN** se inspecciona `Paramesh2019_it_service_desk`
- **THEN** declara el libro *Data Analytics and Learning* (*Proceedings of DAL 2018*), los editores Nagabhushan, Guru, Shekar y Sharath Kumar, la serie Lecture Notes in Networks and Systems, el volumen 43 y las paginas 331-346
- **AND** la referencia compilada ya no presenta el nombre de la serie como titulo del libro

#### Scenario: Anos con criterio uniforme

- **WHEN** se inspeccionan `Stallings2017_computer_security`, `Date2003_database` y `Russell2021_ai_modern`
- **THEN** sus anos son 2018, 2004 y 2021, respectivamente, cada uno confirmado como ano de copyright en la ficha del editor o en un catalogo
- **AND** las claves no se renombran y las citas en el texto muestran el ano corregido

#### Scenario: Borrador vivo con URL y version

- **WHEN** se inspecciona `Jurafsky2023_speech_language`
- **THEN** declara la URL `https://web.stanford.edu/~jurafsky/slp3/`, la fecha de la version del borrador consultada y su `urldate`
- **AND** conserva el tipo de borrador no publicado

#### Scenario: Fechas de consulta completas y no duplicadas

- **WHEN** se compila la bibliografia
- **THEN** las nueve entradas `@manual`/`@misc` con URL (`Apache2024_airflow`, `n8n2024_docs`, `PostgreSQL2024_docs`, `Tiangolo2024_fastapi`, `Wiggins2017_12factor`, `Ley25326_2000`, `SEPyME2026_mipyme`, `APA2017`, `Gomez2026_repositorio`) tienen `urldate`
- **AND** ninguna entrada imprime la fecha de consulta dos veces
- **AND** ninguna `note` contiene punto y coma

#### Scenario: Sede, seudonimo y enlace corregidos

- **WHEN** se inspeccionan `liu2025tickit`, `Tiangolo2024_fastapi` y `GDPR2016`
- **THEN** `liu2025tickit` identifica las actas de FSE Companion 2025
- **AND** `Tiangolo2024_fastapi` no imprime el seudonimo como apellido y `GDPR2016` declara su URL oficial con `urldate`, salvo que el usuario excluya expresamente estos dos ajustes

### Requirement: Rotulo correcto del conteo global de claves en el verificador de citas

El script `docs/Tesis/v10 (IA)/verify_citations.py` SHALL informar como "unique citation keys" el numero de claves distintas citadas en el conjunto de las secciones, y no la suma de las claves unicas de cada archivo; si conserva esa suma, SHALL rotularla de forma que no se confunda con el conteo global. El calculo SHALL estar cubierto por una prueba unitaria co-ubicada que se ejecute sin dependencias externas. El veredicto PASS/FAIL MUST NOT cambiar.

#### Scenario: Conteo global en el mensaje de verificacion

- **WHEN** se ejecuta `python verify_citations.py` sobre la tesis con todas las citas resueltas
- **THEN** la salida informa "N bibliography entries <-> N unique citation keys", con N igual al numero de claves distintas citadas
- **AND** ese N coincide con el de la linea de resumen "unique keys cited" y el estado es PASS

#### Scenario: Suma por archivo con rotulo propio

- **WHEN** una misma clave se cita en mas de un archivo
- **THEN** el conteo global la cuenta una sola vez
- **AND** la suma por archivo, si se informa, lleva un rotulo distinto del conteo global

#### Scenario: Prueba unitaria del conteo

- **WHEN** se ejecuta `python -m unittest test_verify_citations -v` desde `docs/Tesis/v10 (IA)/`
- **THEN** las pruebas pasan
- **AND** cubren claves compartidas entre archivos, claves disjuntas, la ausencia de citas y el mensaje impreso por `main()`

### Requirement: Impacto de paginas cuantificado con cuerpo neutral

Las ediciones de texto del change SHALL ser neutrales en paginas para el cuerpo: la pagina en que empieza "Referencias bibliograficas" MUST NOT cambiar respecto de la linea base tomada inmediatamente antes de aplicar el change. El crecimiento de la bibliografia por las entradas nuevas y los metadatos SHALL medirse (paginas totales y paginas de la bibliografia, antes y despues) y registrarse junto con las palancas de compensacion disponibles, para la verificacion final del presupuesto en c-141. El change MUST NOT editar el preambulo LaTeX ni eliminar contenido cientifico, numeros canonicos, figuras o tablas para compensar.

#### Scenario: Cuerpo neutral

- **WHEN** se compila la tesis antes y despues de aplicar el change
- **THEN** "Referencias bibliograficas" empieza en la misma pagina en ambas compilaciones

#### Scenario: Delta bibliografico registrado

- **WHEN** se cierra el change
- **THEN** quedan registrados el total de paginas y las paginas de inicio y fin de la bibliografia antes y despues
- **AND** quedan registradas las palancas de compensacion con su rendimiento estimado para c-141

#### Scenario: Sin compensacion destructiva

- **WHEN** se revisa el diff del change
- **THEN** el preambulo LaTeX no cambia
- **AND** no se eliminaron numeros canonicos, figuras ni tablas

### Requirement: Trazabilidad de las correcciones de correspondencia texto-fuente

Cada correccion de atribucion, alta bibliografica y ajuste de metadatos del change SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md` con su ubicacion, la fuente, la atribucion previa, lo que la fuente sostiene, la evidencia (URL y nivel: texto completo, resumen o ficha oficial) y la correccion aplicada. Las decisiones que se apartan de la letra del dictamen SHALL declararse con su fundamento.

#### Scenario: Registro por hallazgo

- **WHEN** se lee el grupo del change en `dictamen-correcciones.md`
- **THEN** cada hallazgo de A4, B15 y B16 tiene una fila con su evidencia y su correccion

#### Scenario: Desviaciones declaradas

- **WHEN** una correccion difiere de lo que propone el dictamen
- **THEN** el registro declara la diferencia y su fundamento (por ejemplo, la edicion vigente de ISO/IEC 27701, el ano de copyright de Russell y Norvig o la autoria de Paramesh y Shreedhara)

## MODIFIED Requirements

### Requirement: Atribucion correcta de Revina et al. (2020)

El capitulo de estado del arte (seccion 3.3) y el de discusion (seccion 8.2) SHALL describir el aporte de Revina, Buza & Meister (2020) conforme al contenido real del articulo "IT Ticket Classification: The Simpler, the Better" (IEEE Access, vol. 8, pp. 193380-193395, 2020). El documento MUST NOT atribuir a ese articulo el uso de arquitecturas basadas en BERT, una exactitud cercana al 91 % ni la conclusion de que los modelos preentrenados transfieren conocimiento linguistico al dominio de tickets sin ajuste fino. La posible degradacion de las representaciones preentrenadas ante el vocabulario del dominio SHALL presentarse como la razon de diseno por la que los autores excluyen los word embeddings, y MUST NOT presentarse como un hallazgo medido.

#### Scenario: Sin BERT ni 91 % atribuidos a Revina
- **WHEN** se lee la seccion 3.3 o la 8.2 en busca de las referencias a Revina et al. (2020)
- **THEN** no se le atribuye uso de BERT ni de modelos preentrenados
- **AND** no se le atribuye una exactitud cercana al 91 %
- **AND** no se le atribuye la conclusion de transferencia de modelos preentrenados al dominio

#### Scenario: Conclusion real de Revina et al. enunciada
- **WHEN** se lee la descripcion de Revina et al. (2020)
- **THEN** el texto enuncia que el articulo concluye que los metodos simples y explicables con un conjunto pequeno de rasgos linguisticos del dominio son competitivos para clasificar tickets de TI
- **AND** el texto presenta la posible degradacion de los embeddings preentrenados por el vocabulario especifico del dominio como argumento de diseno de los autores para excluirlos, no como resultado medido

#### Scenario: Ningun hallazgo medido sobre modelos preentrenados
- **WHEN** se leen las secciones 3.3, 8.1 y 8.2 en busca de afirmaciones sobre el rendimiento de los modelos preentrenados atribuidas a Revina et al. (2020)
- **THEN** ninguna las presenta como hallazgo, resultado u observacion empirica del articulo
- **AND** el argumento sobre los modelos preentrenados se enuncia una sola vez en la discusion, sin duplicarse en la comparacion con la literatura

#### Scenario: Tension incorporada en la discusion
- **WHEN** se lee la seccion 8.2 del capitulo de discusion
- **THEN** la evidencia de Revina et al. sobre la competitividad de los metodos simples y su argumento de diseno se integran como una tension explicita para el enfoque basado en LLM del presente trabajo
- **AND** la discusion explica por que esa tension fortalece (no debilita) el analisis

### Requirement: Respaldo de la afirmacion sobre idiomas del corpus

La seccion 1.7 SHALL enunciar los idiomas de los corpus de la literatura sobre clasificacion automatica de tickets solo en la medida en que los declaren las fuentes citadas o la tabla de trabajos academicos relevados (`tab:trabajos-academicos`). El documento MUST NOT atribuir a una fuente idiomas que esta no reporta, en particular corpus en aleman o portugues sin una fuente que los sostenga, y SHALL anclar la afirmacion en esa tabla o en una cita verificable que la sostenga. Las evaluaciones de LLM que incorporan el espanol SHALL describirse conforme a lo que esas obras evaluan.

#### Scenario: Afirmacion comparativa respaldada o reformulada
- **WHEN** se lee la seccion 1.7 del PDF compilado
- **THEN** la afirmacion sobre los idiomas de los corpus remite a la tabla de trabajos relevados o a una cita que la sostiene
- **AND** no queda una generalizacion sobre la literatura sin referencia

#### Scenario: Sin idiomas sin fuente
- **WHEN** se buscan menciones a corpus en aleman o en portugues en la seccion 1.7
- **THEN** no aparecen, o aparecen acompanadas de una cita que las sostiene
- **AND** `zangari2023ticket` y `colavito2025benchmarking` no se citan como respaldo de idiomas que sus resumenes no mencionan

#### Scenario: Coherencia con la tabla de trabajos relevados
- **WHEN** se compara la afirmacion de la seccion 1.7 con la columna de corpus e idioma de `tab:trabajos-academicos`
- **THEN** la afirmacion es coherente con lo que la tabla declara
- **AND** si la tabla incorpora un trabajo con corpus en espanol, la afirmacion se ajusta en consecuencia

#### Scenario: Sin duplicacion del trabajo bibliografico
- **WHEN** se revisa el diff del change
- **THEN** no se agregan ni modifican entradas de `Bibliography_base.bib`
- **AND** las referencias usadas ya existen por c-78

### Requirement: Atribucion editorial de ITIL Service Operation 2011

La seccion 2.2 SHALL atribuir la edicion de 2011 de ITIL Service Operation a The Stationery Office (TSO) por encargo del Cabinet Office, sin presentarla como una publicacion directa del Office of Government Commerce. La entrada `OGC2011_itil` de `Bibliography_base.bib` SHALL ser coherente con esa atribucion: autor corporativo Cabinet Office (o el que consigne el catalogo consultado, declarado en el registro de correcciones), editorial The Stationery Office y ninguna nota que atribuya el encargo al Office of Government Commerce. La clave `OGC2011_itil` MUST NOT renombrarse.

#### Scenario: Atribucion editorial correcta en el cuerpo
- **WHEN** se lee la seccion 2.2 del PDF compilado
- **THEN** la edicion de 2011 se atribuye a TSO/Cabinet Office
- **AND** no se afirma que el Office of Government Commerce sea el editor de la edicion de 2011

#### Scenario: Correccion bibliografica delegada
- **WHEN** se inspecciona la entrada `OGC2011_itil` y su referencia compilada
- **THEN** el autor corporativo, la editorial y la nota (si existe) son coherentes con la atribucion de la seccion 2.2
- **AND** ninguna nota atribuye el encargo de la edicion de 2011 al Office of Government Commerce

#### Scenario: Cita en el texto coherente con el autor
- **WHEN** se lee la cita de la seccion 2.2 en el PDF compilado
- **THEN** la cita muestra el autor corporativo de la entrada corregida
- **AND** la prosa conserva la mencion del Office of Government Commerce solo como titular historico

### Requirement: Cobertura bibliografica formal de las plataformas comerciales

Toda mencion a las plataformas comerciales Zendesk, Freshdesk y ServiceNow en `01-introduccion.tex` SHALL acompanarse de una entrada bibliografica formal en `Bibliography_base.bib` y de su cita en el texto. Cada entrada nueva SHALL tiparse como `@online` e incluir entidad autora, titulo, ano, `url` y `urldate`, siguiendo el patron de las entradas `DigitalOcean2026_pricing` y `Google2026_vertex_pricing`. La fecha de consulta SHALL declararse una sola vez, en `urldate`; la `note`, cuando exista, SHALL declarar la pagina de documentacion de la plataforma y MUST NOT repetir la fecha. El documento MUST NOT introducir cifras de precio no verificables: cuando no exista una figura comprobable, la `note` SHALL declarar la pagina de documentacion de la plataforma y la prosa SHALL mantenerse como observacion de relevamiento.

#### Scenario: Entradas y citas incorporadas
- **WHEN** se inspecciona `Bibliography_base.bib` y `01-introduccion.tex`
- **THEN** existen entradas `@online` para Zendesk, Freshdesk y ServiceNow con `url`, `urldate = {2026-10-19}` y una `note` que declara la pagina de documentacion sin repetir la fecha
- **AND** la mencion a las tres plataformas en la introduccion se acompana de `\parencite` a esas entradas

#### Scenario: Fecha de consulta impresa una sola vez
- **WHEN** se lee la bibliografia compilada
- **THEN** cada una de las cinco entradas `@online` (DigitalOcean, Google Cloud, Zendesk, Freshdesk y ServiceNow) imprime la fecha de consulta una sola vez
- **AND** ninguna `note` de esas entradas contiene la fecha de consulta

#### Scenario: Sin cifras de precio fabricadas
- **WHEN** se revisa la prosa y la `note` de las entradas nuevas
- **THEN** no se afirma ninguna cifra de precio o de capacidad que no pueda verificarse contra la pagina de documentacion citada
- **AND** la formulacion se mantiene como observacion de relevamiento propio declarado

#### Scenario: Correspondencia citas-bibliografia preservada
- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib` tras agregar las entradas
- **THEN** no se introduce ninguna cita huerfana
- **AND** no queda ninguna entrada nueva sin usar
