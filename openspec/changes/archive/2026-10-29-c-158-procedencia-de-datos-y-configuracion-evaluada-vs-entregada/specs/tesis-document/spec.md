## ADDED Requirements

### Requirement: Procedencia de los datos del brazo automatizado declarada en el protocolo de pruebas

La subseccion "Protocolo de pruebas" (`subsec:protocolo-pruebas`, `docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex`) SHALL incluir un apartado titulado "Procedencia de los datos del brazo automatizado" que declare, con la precision de su evidencia en el repositorio: (a) la corrida de tiempos de correo electronico y formulario web del 2-10-2026 (119 casos), su procedimiento de inyeccion por el arnes de ingesta a traves de los canales reales del flujo N8N, el texto inyectado, la metrica (desde el envio hasta la persistencia, con la espera de recogida del disparador IMAP en el correo y su configuracion declarada) y la configuracion del clasificador vigente ese dia (`hybrid-v1`: vocabulario de 89 patrones, prompt sin reglas de frontera y cortocircuito por confianza determinista >= 0,90); (b) la corrida telefonica concluida el 6-10-2026 (81 casos), su procedimiento (softphone de navegador, lectura en voz alta de la descripcion pseudonimizada, grabacion acotada a 45 s, entorno de medicion aislado) y la imposibilidad de asignarle una configuracion unica del clasificador, anterior en todo caso a c-74; (c) la corrida de clasificacion `hybrid-v3` del 7-10-2026 (22:22 UTC) como ejecucion fuera de linea del framework de evaluacion sobre el corpus JSON, con su archivo de evidencia versionado y el hash del corpus; y (d) el recalculo del tiempo telefonico del 19-10-2026 y su motivo. El apartado MUST NOT afirmar hechos que el repositorio no documenta (identidad nominal de quien llamo, intervalo efectivo de sondeo, version desplegada en el entorno de medicion, fuente de texto distinta de la documentada); cada dato faltante SHALL quedar marcado con un comentario LaTeX `% PENDIENTE AUTORES:` y listado como consulta en `docs/Tesis/Correcciones/dictamen-correcciones.md`. Si el apartado afirma la direccion del sesgo de los tiempos respecto de la configuracion evaluada, SHALL presentarla como inferencia y no como medicion.

#### Scenario: Corridas fechadas y separadas

- **WHEN** se lee el apartado de procedencia de la Seccion 4.5 del PDF compilado
- **THEN** figuran la corrida del 2-10-2026 (correo y formulario, 119 casos), la corrida telefonica concluida el 6-10-2026 (81 casos), la clasificacion fuera de linea `hybrid-v3` del 7-10-2026 y el recalculo telefonico del 19-10-2026
- **AND** el texto ya no describe un unico procesamiento "sobre la misma infraestructura" ni un "monitoreo continuo" sin respaldo

#### Scenario: Procedimiento de inyeccion documentado

- **WHEN** se busca en el apartado quien o que introdujo los casos por cada canal y con que texto
- **THEN** declara que el arnes de ingesta envio los 119 casos de correo y formulario por los canales reales del flujo y que en telefonia una persona leyo la descripcion pseudonimizada desde un softphone de navegador
- **AND** el intervalo del disparador IMAP se presenta como configuracion declarada del flujo, no como medicion

#### Scenario: Configuracion del clasificador por corrida segun el historial

- **WHEN** se compara la configuracion declarada para cada corrida con `git log` y con los changes archivados c-68, c-70, c-71, c-72 y c-74
- **THEN** la corrida del 2-10 se describe con la configuracion `hybrid-v1` del commit `24ab238`
- **AND** la corrida telefonica no se describe como anterior a c-71 ni se le asigna una revision unica, y se la declara anterior a c-74

#### Scenario: Corrida de clasificacion fuera de linea

- **WHEN** se lee la descripcion de la corrida de clasificacion
- **THEN** remite a `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, consigna el hash del corpus que registra la evidencia y la presenta como ejecucion del framework de evaluacion sin pasar por los canales
- **AND** la asocia a la version `hybrid-v3` que versiona el commit `d6bb474`, sin afirmar que se ejecuto sobre ese commit

#### Scenario: Datos faltantes marcados y no inventados

- **WHEN** se inspecciona la fuente `04-marco-metodologico.tex`
- **THEN** cada dato que el repositorio no documenta figura en un comentario `% PENDIENTE AUTORES:` y no en el texto compilado
- **AND** la misma consulta figura como PENDIENTE en la seccion de c-158 de `dictamen-correcciones.md`

### Requirement: Recordatorio de la procedencia al abrir la seccion de resultados

La Seccion 8 (`07-resultados.tex`) SHALL incluir, inmediatamente despues de su parrafo introductorio, un parrafo breve que recuerde que los tiempos y las metricas de clasificacion provienen de corridas y configuraciones distintas y remita al apartado de procedencia de la Seccion 4.5. El parrafo introductorio y su enumeracion de subsecciones MUST NOT modificarse por este motivo.

#### Scenario: Recordatorio presente sin alterar la enumeracion

- **WHEN** se lee el comienzo de la Seccion 8 del PDF compilado
- **THEN** el segundo parrafo distingue los tiempos (corridas del 2-10 y el 6-10, recalculo del 19-10) de las metricas (clasificacion fuera de linea del 7-10) y remite a la Seccion 4.5
- **AND** el primer parrafo sigue enumerando las seis subsecciones en su orden

### Requirement: Delimitacion temporal de la introduccion fechada con las corridas reales

La delimitacion temporal de la Seccion 1.8 (`01-introduccion.tex`, `subsec:alcance-delimitaciones`) SHALL fechar los resultados con las corridas reales del brazo automatizado (2 y 6 de octubre de 2026) y la clasificacion fuera de linea (7 de octubre) y MAY conservar el 24-09-2026 solo como fecha de integracion de `gemini-3.6-flash`. La seccion MUST NOT presentar el 24-09-2026 como inicio de una corrida.

#### Scenario: Fechas de las corridas en la Seccion 1.8

- **WHEN** se lee la ultima delimitacion de la Seccion 1.8
- **THEN** el 24-09-2026 aparece, si aparece, como fecha de integracion del modelo
- **AND** las corridas se fechan el 2 y el 6 de octubre de 2026 y la clasificacion el 7 de octubre, coherentes con `docs/diagrams/cronograma.md`

### Requirement: Interpretacion de la reduccion de tiempo sin la proporcion de cortocircuito de la configuracion posterior

La Seccion 9.1 (`08-discusion.tex`, `subsec:interpretacion-resultados`) MUST NOT apoyar la reduccion del tiempo de registro en la proporcion de casos que resuelve la etapa determinista de la configuracion evaluada en la clasificacion (65,5 %), porque esa configuracion no regia en las corridas de tiempos. La seccion SHALL declarar que la reduccion se midio con la inferencia externa incluida y con configuraciones que invocaban al modelo con mayor frecuencia, y MAY conservar la cifra del 65,5 % como dato de la configuracion evaluada.

#### Scenario: Sin apoyo causal en el 65,5 %

- **WHEN** se lee el parrafo de la Seccion 9.1 sobre la inferencia externa
- **THEN** no afirma que la reduccion de tiempo se sostiene porque la etapa determinista resuelve el 65,5 % de los casos
- **AND** remite a la Seccion 4.5 para la configuracion vigente en las corridas de tiempos

### Requirement: Descripcion exacta del tiempo telefonico y de la fuente del cronograma

La Seccion 6.4 (`06-implementacion.tex`, `subsec:integracion-canal-telefonico`) SHALL describir el tiempo automatizado telefonico como la suma de la duracion de la grabacion y la latencia desde el cuelgue hasta la persistencia del incidente, y MUST NOT describirlo como medido desde el inicio de la llamada hasta la confirmacion del numero de incidente. La leyenda de la figura del cronograma (`fig:cronograma`, `12-anexos.tex`) SHALL distinguir la fuente de los hitos (historial del repositorio, incluido el recalculo del tiempo telefonico del 19-10-2026) de la confirmacion de los autores del 9-10-2026 sobre las ventanas de las campanas, y SHALL usar un titulo corto para el indice de figuras.

#### Scenario: Tiempo telefonico descrito como se midio

- **WHEN** se lee la Seccion 6.4
- **THEN** el tiempo telefonico se describe como duracion de la grabacion mas latencia hasta la persistencia, con la grabacion acotada a 45 s
- **AND** no aparece "desde el inicio de la llamada hasta la confirmacion del numero de incidente"

#### Scenario: Leyenda coherente con el hito del 19-10

- **WHEN** se lee la leyenda de la figura del cronograma
- **THEN** atribuye los hitos, incluido el del 19-10-2026, al historial del repositorio y la confirmacion del 9-10-2026 a las ventanas de las campanas
- **AND** la entrada del indice de figuras usa el titulo corto

### Requirement: Tabla de configuracion evaluada frente a entregada

El Anexo B (`sec:anexo-repositorio`, `12-anexos.tex`) SHALL incluir una tabla con etiqueta `tab:configuracion-evaluada-entregada` y dos columnas de configuracion: "Configuracion evaluada" (commit `d6bb474`, 7-10-2026) y "Configuracion entregada" (el tag que identifica el Anexo B, hoy `v1.2.5`, 28-10-2026). La tabla SHALL consignar solo valores verificados con `git show <revision>:<archivo>` o con los changes archivados: versiones de FastAPI, Uvicorn, SQLAlchemy, google-genai, pytest, pytest-cov y React; el flujo N8N versionado; los reintentos del tramo de alta (c-140); el disparador de revision por reportante no identificado en el directorio (c-82); la prueba de humo de extremo a extremo y la verificacion automatizada de TLS (c-140); y los componentes sin cambios. Cada valor SHALL registrarse en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md` con su comando de verificacion. La tabla MUST NOT incluir valores no verificados.

#### Scenario: Valores verificados contra ambas revisiones

- **WHEN** se compara cada celda de la tabla con `git show d6bb474:App/Backend/requirements.txt`, `git show v1.2.5:App/Backend/requirements.txt`, los `package.json`/`package-lock.json` y `n8n/workflow.json` de ambas revisiones
- **THEN** cada version coincide (FastAPI 0.115.0 / 0.162.0, Uvicorn 0.30.6 / 0.54.0, SQLAlchemy 2.0.36 / 2.1.6, google-genai >=2.20.0 / >=2.33.0,<3, pytest 8.3.3 / 9.1.1, pytest-cov 5.0.0 / 7.1.0, React 18.3.1 / 19.3.1)
- **AND** las capacidades posteriores figuran como ausentes en la columna evaluada y presentes en la entregada con su change

#### Scenario: Etiqueta estable para otros changes

- **WHEN** otro change (c-159) remite a la tabla desde las leyendas de las Figuras 1 y 4
- **THEN** la referencia `\ref{tab:configuracion-evaluada-entregada}` resuelve sin advertencias de referencia indefinida

#### Scenario: Registro en el memo de conteos tecnicos

- **WHEN** se lee `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`
- **THEN** figura una seccion con cada valor de la tabla, su revision y su comando de verificacion

### Requirement: Remisiones uniformes a la configuracion evaluada o entregada

Todo pasaje de las Secciones 5.4, 6.1, 6.2, 6.3, 6.5, 6.7 y 7.4 (`subsec:seguridad-tecnica`) y del Anexo H que cite una version de dependencia o una capacidad incorporada despues de las corridas (reintentos del alta, disparador de revision por directorio, prueba de humo de extremo a extremo, verificacion de TLS, React 19) SHALL declarar a que configuracion pertenece y remitir a `tab:configuracion-evaluada-entregada`. Ningun pasaje MUST presentar esas capacidades como rasgos de la version evaluada.

#### Scenario: Versiones rotuladas

- **WHEN** se buscan en las Secciones 5.4, 6.1, 6.2 y 6.7 y en el Anexo H las versiones de FastAPI, Uvicorn, google-genai, pytest, pytest-cov y React
- **THEN** cada mencion esta rotulada como de la configuracion evaluada o de la entregada, o se reemplaza por la remision a la tabla

#### Scenario: Capacidades posteriores fechadas

- **WHEN** se leen los pasajes de 6.3 (disparador por directorio), 6.5 (reintentos), 6.7 (prueba de humo) y 7.4 (TLS)
- **THEN** cada uno declara que la capacidad pertenece a la configuracion entregada y remite a la tabla
- **AND** ninguno la atribuye al sistema que produjo los resultados de la Seccion 8

### Requirement: Precision del commit de referencia en el Anexo B

El Anexo B SHALL describir el commit al que apunta el tag de la version entregada sin llamarlo "commit definitivo": SHALL declarar que el tag fija el contenido de la version entregada y que un commit posterior de la rama principal consigna su hash, sin modificar las fuentes de la tesis.

#### Scenario: Patron de dos commits declarado

- **WHEN** se lee el primer parrafo del Anexo B
- **THEN** no aparece "commit definitivo"
- **AND** se explica que el hash se consigna en un commit posterior, verificable con `git diff --stat <tag> HEAD -- "docs/Tesis/v10 (IA)/paper/sections"`

### Requirement: Trazabilidad de las observaciones A1 y A2 del dictamen del 28-10-2026

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 / v1.2.5 (2026-10-28) - c-158" con la trazabilidad observacion -> cambio -> archivo:linea de A1 y A2, la lista de consultas a los autores con estado PENDIENTE, las discrepancias halladas con el dictamen y la fila del libro mayor de paginas. El Anexo I SHALL mencionar el dictamen del 28-10-2026 y las secciones donde se atendieron A1 y A2. Ningun artefacto MUST contener emojis.

#### Scenario: Registro completo y sin emojis

- **WHEN** se lee la seccion de c-158 del registro de correcciones
- **THEN** cada parte de A1 y A2 tiene su archivo y linea, y cada consulta a los autores figura como PENDIENTE
- **AND** el archivo no contiene emojis ni pictogramas

#### Scenario: Anexo I actualizado

- **WHEN** se lee el Anexo I del PDF compilado
- **THEN** menciona el dictamen del 28-10-2026 sobre `v1.2.5` y las secciones donde c-158 atendio A1 y A2

## MODIFIED Requirements

### Requirement: Trazabilidad del corpus real en el anexo de validacion

El anexo "Corpus de validacion" de la tesis SHALL remitir al corpus real
`data/corpus_evaluacion_pseudonimizado.json` (JSON, pseudonimizado y versionado)
y SHALL NOT declarar que el corpus se conserva como un CSV de siete columnas en
`evaluation/data/`. El anexo SHALL aclarar que la categoria predicha y la
confianza por caso no forman parte del corpus y se conservan en la evidencia versionada
`evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (copia de la cache del
framework de evaluacion, que no se versiona), y MUST NOT remitirlas a
`evaluation/predicciones.json` ni a otro archivo excluido por `.gitignore`. El anexo
SHALL declarar que los tiempos del flujo automatizado se conservan por caso en el corpus
JSON y que sus registros primarios no estan versionados en el repositorio; solo SHALL
afirmar que no se conservaron si los autores lo confirman de forma registrada. Las rutas
del anexo SHALL componerse de modo que ninguna linea exceda el margen.
La tesis SHALL NOT afirmar la existencia de un corpus en `evaluation/data/`.

#### Scenario: El anexo apunta al JSON real

- **WHEN** se lee la seccion "Corpus de validacion" del Anexo de la tesis
- **THEN** referencia `data/corpus_evaluacion_pseudonimizado.json` como corpus real
- **AND** no describe un archivo CSV ni un corpus de siete columnas en `evaluation/data/`

#### Scenario: Sin corpus inexistente

- **WHEN** se busca "evaluation/data" o "CSV" como ubicacion del corpus en los `.tex` y en el PDF
- **THEN** no se afirma que el corpus resida alli

#### Scenario: Predicciones remitidas a la evidencia versionada

- **WHEN** se busca en el Anexo F la ubicacion de las predicciones por caso
- **THEN** remite a `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`
- **AND** no remite a `evaluation/predicciones.json`

#### Scenario: Registros primarios declarados con exactitud

- **WHEN** se lee en el Anexo F la descripcion de los registros del flujo automatizado
- **THEN** declara que no estan versionados en el repositorio y que los tiempos por caso se conservan en el corpus JSON
- **AND** no afirma que el repositorio incluye "registros automaticos generados por el flujo automatizado" ni que no se conservaron sin confirmacion registrada de los autores

#### Scenario: Sin lineas fuera de margen en el anexo

- **WHEN** se compila `main.tex` y se buscan advertencias `Overfull \hbox` con origen en las lineas del Anexo F de `12-anexos.tex`
- **THEN** no aparece ninguna

### Requirement: Coherencia de la version bibliografica con la release publicada

La entrada `Gomez2026_repositorio` de `docs/Tesis/v10 (IA)/Bibliography_base.bib` SHALL declarar en su titulo la misma version que el tag de release que identifica el Anexo B (`sec:anexo-repositorio`), y su `urldate` SHALL ser la fecha de esa release. Para la release `v1.2.5`, el titulo SHALL enunciar la version `1.2.5`, con la etiqueta "Version" o con su forma acentuada si la revision ortotipografica la acentuo por decision registrada, con `urldate` `2026-10-28`, y SHALL NOT conservar numeros de version anteriores como `1.2.4`, `1.2.3`, `1.2.2`, `1.2.1`, `1.2.0`, `1.1.1` o `1.0.0`. El numero de version SHALL actualizarlo el change que publica la release, en el mismo commit que cambia el tag del Anexo B; cuando una release haya omitido esa actualizacion, el primer change documental que detecte el desfase SHALL realinear la entrada con la release del Anexo B y registrar la omision en `docs/Tesis/Correcciones/dictamen-correcciones.md`. Ningun otro change MUST modificar ese numero. Los demas campos de la entrada (autoria, ano, `url` y `note`) SHALL conservarse y la referencia SHALL seguir imprimiendose en la seccion de Referencias.

#### Scenario: Version bibliografica alineada con la release

- **WHEN** se compara el titulo de `Gomez2026_repositorio` con el tag que consigna el Anexo B
- **THEN** el titulo enuncia la version `1.2.5`, el Anexo B enuncia `v1.2.5` y `urldate` es `2026-10-28`
- **AND** el titulo de `Gomez2026_repositorio` no conserva los numeros de version `1.2.4`, `1.2.3`, `1.2.2`, `1.2.1`, `1.2.0`, `1.1.1` ni `1.0.0`

#### Scenario: Desfase heredado realineado y registrado

- **WHEN** una release publicada dejo la entrada con una version anterior a la del Anexo B
- **THEN** el change documental que lo detecta la realinea
- **AND** el registro de correcciones consigna la omision y la release que la produjo

#### Scenario: Integridad de la entrada preservada

- **WHEN** se ejecuta la verificacion de citas contra `Bibliography_base.bib`
- **THEN** la entrada sigue existiendo y sigue siendo referenciada por las citas del anexo
- **AND** sus campos `author`, `year`, `url` y `note` se mantienen, sin introducir citas huerfanas ni entradas sin usar
