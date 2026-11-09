## MODIFIED Requirements

### Requirement: Thesis PDF compilation

La tesis SHALL compilar desde la fuente LaTeX de la version de trabajo vigente (`docs/Tesis/v10 (IA)/paper/main.tex`) a `docs/Tesis/v10 (IA)/paper/main.pdf` mediante XeLaTeX y biber, sin errores fatales, con las fuentes reales que declara el preambulo (Arial y Courier New) y en el entorno de compilacion de registro consignado en `docs/Tesis/Correcciones/dictamen-correcciones.md`. El PDF SHALL incluir todos los archivos de seccion que `main.tex` incorpora con `\input`, en el orden de `main.tex`. La compilacion de una release SHALL cumplir ademas: cero referencias y citas indefinidas, cero etiquetas duplicadas, biber sin advertencias ni errores, `verify_citations.py` con estado PASS y todo `\includegraphics` resuelto a un archivo existente. Como `main.log` no se versiona, la evidencia de la compilacion de cada release SHALL versionarse junto al PDF en `docs/Tesis/v10 (IA)/paper/compilacion.md`, generado por `docs/Tesis/Correcciones/resumir_registro_compilacion.py` a partir de `main.log`, `main.blg` y `main.pdf` del mismo commit, y `dictamen-correcciones.md` SHALL remitir a ese resumen. El resumen MUST NOT editarse a mano.

#### Scenario: Successful compilation

- **WHEN** el proyecto LaTeX se compila con `latexmk -xelatex main.tex` (o con la secuencia xelatex -> biber -> xelatex -> xelatex) en el entorno de registro
- **THEN** se produce `docs/Tesis/v10 (IA)/paper/main.pdf` sin errores fatales
- **AND** el PDF contiene los archivos de seccion que `main.tex` incorpora, en el orden de `main.tex`

#### Scenario: Compilation failure recovery

- **WHEN** ocurre un error de compilacion (paquete faltante, referencia indefinida, fuente no encontrada)
- **THEN** el error se diagnostica desde el `.log`
- **AND** la correccion se aplica en el preambulo o en el `.tex` afectado
- **AND** la recompilacion es exitosa

#### Scenario: Verificaciones de una release

- **WHEN** se compila la fuente que se va a etiquetar como release
- **THEN** el `.log` no contiene referencias ni citas indefinidas ni etiquetas `multiply defined`
- **AND** `main.blg` no contiene lineas `WARN` ni `ERROR`
- **AND** `python verify_citations.py` (desde `docs/Tesis/v10 (IA)/`) reporta `STATUS: PASS`
- **AND** el texto extraido del PDF no contiene la secuencia `??`

#### Scenario: Figuras resueltas

- **WHEN** se recorren los `\includegraphics` de `sections/*.tex` contra el `\graphicspath` del preambulo
- **THEN** cada uno resuelve a un archivo existente de `figures/` o `assets/`
- **AND** ninguna figura requerida por changes previos falta en el PDF

#### Scenario: Entorno de registro validado contra la release previa

- **WHEN** se adopta un entorno de compilacion de registro para medir una release nueva
- **THEN** ese entorno reproduce sobre la fuente de la release previa su conteo de paginas publicado (101 paginas para `v1.1.1`)
- **AND** el registro consigna el entorno, sus versiones de XeLaTeX y biber y el resultado de esa reproduccion

#### Scenario: Evidencia de la compilacion versionada junto al PDF

- **WHEN** se cierra la compilacion de una release
- **THEN** `docs/Tesis/v10 (IA)/paper/compilacion.md` existe en el mismo commit que `main.pdf` y consigna la fuente compilada, el motor y la version de biber, el total de paginas, los conteos de errores fatales, referencias y citas indefinidas, etiquetas duplicadas, `Overfull \hbox` (cantidad y maximo en pt) y lineas `WARN`/`ERROR` de biber, y el SHA-256 de `main.pdf`
- **AND** el SHA-256 consignado coincide con `sha256sum main.pdf` del mismo commit
- **AND** `dictamen-correcciones.md` remite a ese resumen y consigna el estado de `verify_citations.py`

#### Scenario: Resumen reproducible

- **WHEN** se ejecuta `resumir_registro_compilacion.py` dos veces sobre los mismos `main.log`, `main.blg` y `main.pdf`
- **THEN** ambas salidas son identicas byte a byte
- **AND** la salida no contiene la fecha ni la hora del sistema

### Requirement: Evidencia visual del sistema y de los resultados

La tesis SHALL incluir las 7 figuras requeridas, embebidas mediante `\includegraphics` dentro de un entorno `figure` con `\caption` y `\label`, en sus ubicaciones naturales. Cada figura SHALL provenir de una fuente reproducible (diagrama Mermaid versionado, script de generacion o captura manual identificada). La matriz de confusion SHALL reportarse una sola vez, como la tabla `tab:matriz` de la seccion 8.2; la tesis MUST NOT embeber ademas una figura con los mismos datos. El script `scripts/figures/matriz_confusion.py` y su salida pueden conservarse en el repositorio como artefacto no embebido, declarado en `docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`.

#### Scenario: Las siete figuras existen y estan embebidas
- **WHEN** se listan los archivos de `paper/figures/` y se buscan los comandos `\includegraphics` en `paper/sections/`
- **THEN** existen y estan embebidas las 7 figuras: diagrama de despliegue, diagrama de secuencia, diagrama entidad-relacion, captura del flujo N8N, captura del panel de administracion, captura del dashboard y boxplot de tiempos
- **AND** cada figura esta referenciada por un `\includegraphics` dentro de un `figure`

#### Scenario: Matriz de confusion sin duplicacion
- **WHEN** se busca `matriz_confusion` y `fig:matriz_confusion` en `paper/sections/*.tex`
- **THEN** no hay coincidencias
- **AND** `tab:matriz` existe en `07-resultados.tex` y el texto de 8.2 la cita

#### Scenario: Ubicacion natural de cada figura
- **WHEN** se revisa el capitulo donde se discute el artefacto correspondiente
- **THEN** el diagrama de despliegue y el de secuencia aparecen en el Capitulo 5 o el Anexo A
- **AND** el diagrama entidad-relacion aparece en la seccion 5.6 o el Anexo C
- **AND** la captura del flujo N8N aparece en la seccion 6.3 o el Anexo E
- **AND** las capturas del panel de administracion y del dashboard aparecen en la seccion 6.8
- **AND** el boxplot de tiempos aparece en la seccion 8.1 y la matriz de confusion, como tabla, en la seccion 8.2

#### Scenario: Figuras con fuente reproducible
- **WHEN** se inspecciona una figura generada a partir de un diagrama
- **THEN** existe la fuente Mermaid correspondiente en `docs/diagrams/` o en el repositorio
- **AND** el boxplot fue generado por un script reproducible a partir de los datos del corpus
- **AND** las capturas de interfaz se identifican como tales en el texto o en su leyenda, con su procedencia

#### Scenario: Boxplot de latencias reportado por canal
- **WHEN** se inspecciona la figura del boxplot de tiempos (seccion 8.1)
- **THEN** la figura reporta las latencias POR CANAL (formulario web, correo y telefonia) en paneles separados o en un layout agrupado por canal, en lugar de un unico boxplot que mezcle los tres puntos de ingreso
- **AND** cada canal compara `tiempo_manual_s` contra `tiempo_automatizado_s` dentro del mismo canal
- **AND** la separacion por canal es consistente con la regla de comparabilidad de `docs/medicion-latencia-e2e.md` (los puntos de ingreso no son homogeneos)

#### Scenario: Panel de telefonia con metrica corregida
- **WHEN** se inspecciona el panel de telefonia del boxplot
- **THEN** el valor automatizado usa la metrica corregida de `tiempo_automatizado_s` que incluye la duracion de la llamada/grabacion (correccion de c-77 "Opcion A")
- **AND** si la correccion de c-77 no esta aplicada, el panel se rotula "automatizado = solo post-procesamiento de la llamada (cota inferior)"

### Requirement: Trazabilidad del dictamen del 8 de noviembre en el registro y en el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion del change
c-187 con la matriz recomendacion → ubicacion → correccion para A1-A5, B1, B2, B3 y B6, la
nota de verificacion del mecanismo de derivacion, la decision sobre el patron de release
y el conteo final de paginas y palabras, y una seccion del change c-188 con la matriz para
B4, B5, B7 y C1-C5, las decisiones del usuario (capturas, grafia del apellido, forma del
registro de compilacion), las fuentes de C2 verificadas u omitidas con su fecha de
consulta y el libro mayor de paginas. El registro SHALL incluir ademas una matriz de 7
columnas con "Fragmento verificable" para las recomendaciones del dictamen del 8 de
noviembre (filas de c-187 y de c-188), que `verificar_matriz_trazabilidad.py` verifica. El
Anexo I (`sec:anexo-trazabilidad`, `12-anexos.tex`) SHALL incluir la tabla
`tab:anexo-trazabilidad-0811` con la estructura comun de las tablas del 22 y del 28 de
octubre, con filas para A1-A5, B1, B2, B3 y B6 (`c-187`) y para B4, B5, B7, C1, C2, C3, C4
y C5 (`c-188`), cada una con las secciones o tablas donde se atendio. La tabla MUST NOT
conservar la fila que remitia B4, B5, B7 y C1-C5 a un change posterior. El parrafo
introductorio del Anexo I SHALL declarar seis dictamenes, entre el 20 de octubre y el 8 de
noviembre de 2026, y el parrafo que presenta la tabla del 8 de noviembre SHALL nombrar los
dos changes. El anexo MUST NOT contener numeros de linea de las fuentes.

#### Scenario: Tercera tabla del Anexo I completa

- **WHEN** se compila la tesis y se lee el Anexo I
- **THEN** `tab:anexo-trazabilidad-0811` tiene filas A1-A5, B1, B2, B3 y B6 atribuidas a `c-187` y filas B4, B5, B7, C1, C2, C3, C4 y C5 atribuidas a `c-188`
- **AND** cada fila remite con `\autoref` a secciones o tablas que contienen lo atendido, o nombra la bibliografia o el glosario cuando la correccion esta alli

#### Scenario: Sin fila de remision

- **WHEN** se busca "Change posterior" en `12-anexos.tex`
- **THEN** no aparece en `tab:anexo-trazabilidad-0811`

#### Scenario: Cantidad de dictamenes actualizada

- **WHEN** se lee el parrafo introductorio de `sec:anexo-trazabilidad`
- **THEN** declara seis dictamenes hasta el 8 de noviembre de 2026
- **AND** no queda "cinco dictámenes" ni "entre el 20 y el 28 de octubre"

#### Scenario: Registro de los dos changes

- **WHEN** se lee `dictamen-correcciones.md`
- **THEN** figuran la seccion de c-187 con la matriz, la nota de verificacion, la decision del patron de release y los conteos, y la seccion de c-188 con su matriz, las decisiones del usuario, las fuentes verificadas u omitidas y el libro mayor de paginas
- **AND** existe la matriz de 7 columnas del dictamen del 8 de noviembre con fragmentos verificables

## ADDED Requirements

### Requirement: Definicion declarada de las metricas multietiqueta secundarias

La tesis SHALL declarar, en el analisis estadistico (`subsec:analisis-estadistico`) y en
`subsec:matriz-metricas`, como se calculan la subset accuracy (0,43), la Hamming loss
(0,3586) y el micro-F1 (0,6654): el conjunto predicho de cada caso es la etiqueta principal
mas los sectores adicionales que emite el clasificador (8 casos, todos de la etapa
deterministica), y la Hamming loss se normaliza por la union de las etiquetas verdaderas y
predichas del caso, no por las cinco clases. La descripcion SHALL coincidir con
`evaluation/run_evaluation.py` y `evaluation/metrics.py` (`perdida_hamming`). La tesis
MUST NOT describir la salida evaluada por esas metricas como "forzada a una sola
etiqueta". Los valores canonicos MUST NOT cambiar; las cifras de verificacion alternativas
(solo etiqueta principal; Hamming por cinco clases) SHALL registrarse en
`docs/Tesis/Correcciones/numeros-canonicos.md` como verificacion, sin reemplazar valores.

#### Scenario: Conjunto predicho declarado

- **WHEN** se leen `subsec:analisis-estadistico` y `subsec:matriz-metricas`
- **THEN** se declara que el conjunto predicho incluye los sectores adicionales de 8 casos y que la Hamming loss se normaliza por la union de etiquetas del caso
- **AND** `rg -n "forzada a una sola etiqueta" "docs/Tesis/v10 (IA)/paper/sections"` no devuelve coincidencias

#### Scenario: Cifras reproducibles desde la definicion

- **WHEN** se recalculan las tres metricas desde `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` con la definicion declarada
- **THEN** se obtienen 0,43, 0,35858 y 0,66544
- **AND** `numeros-canonicos.md` registra las cifras alternativas (0,44; 0,35275; 0,182) como verificacion

### Requirement: Descripcion unica de los ejemplos del prompt

La tesis SHALL describir los ejemplos del prompt de Gemini de forma identica en
`subsec:subsistema-clasificacion`, en `subsec:implicancias-practicas` y en el Anexo H
(`subsec:anexo-estructura-prompt`): un unico ejemplo representativo por sector (cinco en
total), coherente con `docs/prompt_gemini.txt`. La tesis MUST NOT describir esos ejemplos
como "balanceados".

#### Scenario: Sin "ejemplos balanceados"

- **WHEN** se busca "balanceados" en `paper/sections/*.tex`
- **THEN** no aparece referido a los ejemplos del prompt
- **AND** las tres ubicaciones declaran un unico ejemplo por sector

### Requirement: Procedencia declarada de las capturas de interfaz

Las leyendas o el texto de `fig:panel_admin` y `fig:dashboard` (6.8) SHALL declarar la
procedencia de cada captura: instancia, fecha de captura (21-10-2026, c-80), rotulo de
version visible ("v1.0.0") y periodo de los incidentes mostrados (145 incidentes, del 2 al
13-10-2026), y SHALL explicar que la cola de revision (94 casos) y la "tasa de revision
humana" (64,8 %) reflejan el indicador `requiere_revision_humana` registrado por el backend
en esa base, distinto de la regla de confianza evaluada fuera de linea, con remision a
`subsec:reduccion-intervencion`. La tesis MUST NOT atribuir esos 94 indicadores a una regla
concreta que no pueda verificarse. Si el usuario elige reemplazar las capturas, las nuevas
SHALL provenir de la configuracion entregada y declarar igualmente su procedencia.

#### Scenario: Procedencia en las leyendas

- **WHEN** se leen las leyendas de `fig:panel_admin` y `fig:dashboard`
- **THEN** declaran fecha de captura, rotulo de version y periodo de los datos
- **AND** el texto explica la cola y la tasa de revision y remite a `subsec:reduccion-intervencion`

#### Scenario: Sin contradiccion con la seccion 8.3

- **WHEN** se compara 6.8 con `subsec:reduccion-intervencion`
- **THEN** 6.8 no sugiere que la regla de confianza derivo los casos mostrados en las capturas

### Requirement: Diagrama de despliegue coherente con la configuracion entregada

`docs/diagrams/despliegue.md` y `paper/figures/despliegue.png` SHALL representar el
frontend como el bundle compilado por Vite servido por `nginx:alpine` en el puerto 3000
(`App/Frontend/Dockerfile`), la imagen de N8N como la imagen derivada de
`docker/n8n/Dockerfile` (N8N 2.11.2 con el parche IMAP de c-182) y las redes Docker de
`docker-compose.yml`. El diagrama MUST NOT rotular el frontend como "Vite dev server". El
PNG SHALL regenerarse desde la fuente con `@mermaid-js/mermaid-cli@12.0.0` (`-b white -s 2`)
y la version, las dimensiones y la relacion alto/ancho SHALL registrarse en
`docs/Tesis/Correcciones/conteos-canonicos-tecnicos.md`.

#### Scenario: Frontend servido por nginx

- **WHEN** se busca "Vite dev server" en `docs/diagrams/despliegue.md`
- **THEN** no hay coincidencias
- **AND** el nodo del frontend menciona nginx y el puerto 3000

#### Scenario: PNG regenerado desde la fuente

- **WHEN** se compara `figures/despliegue.png` con la fuente Mermaid
- **THEN** los rotulos coinciden, sin `\n` literales
- **AND** `conteos-canonicos-tecnicos.md` registra la version de mmdc y las dimensiones nuevas

### Requirement: Verificador de la matriz de trazabilidad vigente

`docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` SHALL verificar todas las
matrices de 7 columnas con encabezado "Fragmento verificable" de
`dictamen-correcciones.md`, en cualquier seccion (dictamenes del 22-10, del 28-10 y del
8-11). Una fila SHALL pasar cuando el fragmento aparece en el archivo citado y el ancla
`\label` existe en el; si el fragmento esta en otra linea, SHALL pasar con un aviso de
desplazamiento, salvo con `--estricto`, que exige la linea exacta. Las filas cuyo estado
empieza con "PENDIENTE" o "SUPERADA" SHALL omitirse. El script SHALL conservar `--rev` y
`--reubicar`. Cada comportamiento SHALL tener una prueba en
`test_verificar_matriz_trazabilidad.py` escrita antes del codigo (Strict TDD). Tras el
apply, el script SHALL terminar con codigo 0 sobre el arbol de trabajo y con `--rev` del
tag de la release; cada fila marcada "SUPERADA" SHALL nombrar el change que reescribio el
parrafo.

#### Scenario: Todas las matrices verificadas

- **WHEN** se ejecuta `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen informa filas de las matrices del 22-10, del 28-10 y del 8-11
- **AND** el codigo de salida es 0 y la cantidad de fallas es 0

#### Scenario: Desplazamiento de linea no es falla

- **WHEN** el fragmento de una fila aparece en el archivo en una linea distinta de la citada
- **THEN** sin `--estricto` la fila pasa con el aviso "desplazada"
- **AND** con `--estricto` la fila falla

#### Scenario: Fragmento ausente o ancla inexistente

- **WHEN** el fragmento no aparece en ninguna linea del archivo o el ancla no existe
- **THEN** la fila falla con un mensaje que nombra el fragmento o el ancla

#### Scenario: Pruebas primero y en verde

- **WHEN** se ejecuta `python -m unittest test_verificar_matriz_trazabilidad -v` desde `docs/Tesis/Correcciones/`
- **THEN** todas las pruebas pasan, incluidas las de matrices multiples, desplazamiento, `--estricto` y filas SUPERADA

### Requirement: Script del resumen del registro de compilacion probado

`docs/Tesis/Correcciones/resumir_registro_compilacion.py` SHALL separar funciones puras
(extraccion de conteos desde el texto del log y del `.blg`, calculo del SHA-256 del PDF y
armado del Markdown) de la lectura y escritura de archivos, no SHALL usar red ni
subprocesos, y SHALL tener pruebas en `test_resumir_registro_compilacion.py` escritas antes
del codigo, con al menos dos casos por comportamiento (log limpio y log con errores,
referencias indefinidas, etiquetas duplicadas y `Overfull`; `.blg` limpio y con `WARN`).

#### Scenario: Conteos extraidos de un log sintetico

- **WHEN** las pruebas pasan un log con una linea `!`, una referencia indefinida, una cita indefinida, una etiqueta `multiply defined`, dos `Overfull \hbox` de 3,1 y 12,4 pt y "Output written on main.xdv (118 pages"
- **THEN** el resumen informa 1 error, 1 referencia y 1 cita indefinidas, 1 etiqueta duplicada, 2 `Overfull` con maximo 12,4 pt y 118 paginas

#### Scenario: Pruebas en verde

- **WHEN** se ejecuta `python -m unittest test_resumir_registro_compilacion -v` desde `docs/Tesis/Correcciones/`
- **THEN** todas las pruebas pasan

### Requirement: Fidelidad de las atribuciones senaladas por el dictamen del 8 de noviembre

La tesis MUST NOT atribuir a Galup et al. (2009) la degradacion de los procesos manuales con
el volumen "con un impacto desproporcionado en organizaciones medianas" ni que "advierten"
esa degradacion, salvo que se cite la pagina verificada de la fuente; en su defecto, esas
afirmaciones de `subsec:planteamiento-problema` y `subsec:mesa-ayuda-itil` SHALL
presentarse como inferencia de los autores. La afirmacion de que el espanol rioplatense "ha
recibido una atencion notablemente menor" SHALL rotularse como inferencia de los autores.
La definicion del F1 macro empleada (media aritmetica de los F1 por clase, la que
implementa `evaluation/metrics.py`) SHALL atribuirse a una fuente que la use, verificada
(Opitz y Burst, 2019, arXiv:1911.03347, u otra equivalente), y la tesis SHALL declarar que
existe otra formula (F1 de los promedios de precision y sensibilidad) cuando cite a Sokolova
y Lapalme (2009) para el promedio macro. El efecto Hawthorne SHALL citarse con una fuente
primaria o una revision verificada (DOI o catalogo), no solo con un manual general sin
pagina.

#### Scenario: Galup sin afirmaciones excedidas

- **WHEN** se busca "desproporcionado" en `paper/sections/*.tex`
- **THEN** no aparece atribuido a `Galup2009_itsm`
- **AND** cada cita restante de `Galup2009_itsm` sostiene solo la caracterizacion de ITSM o lleva pagina

#### Scenario: Variante del F1 macro con fuente

- **WHEN** se leen las definiciones del F1 macro en 2.8, `subsec:metricas-instrumentos` y `subsec:matriz-metricas`
- **THEN** la media aritmetica de los F1 por clase se atribuye a una fuente verificada que la use
- **AND** la cita de `Sokolova2009_performance_measures` no se presenta como fuente de esa formula sin la salvedad

#### Scenario: Hawthorne con fuente primaria

- **WHEN** se lee la mencion del efecto Hawthorne en `subsec:diseno-experimental`
- **THEN** cita una fuente primaria o una revision con DOI o catalogo verificado en `Bibliography_base.bib`

### Requirement: Fuentes de los proveedores y de la normativa de transferencias internacionales

`Bibliography_base.bib` SHALL incluir entradas verificadas de la Gemini API (servicio de
Google AI que usa el backend, para inferencia y transcripcion), de Twilio Programmable
Voice (grabacion de llamadas), de Docker, de Jira Service Management y de osTicket, y de la
normativa argentina complementaria del articulo 12 de la Ley 25.326 sobre transferencias
internacionales (reglamentacion y disposicion de la autoridad de aplicacion sobre paises
adecuados y clausulas modelo), y el texto SHALL citarlas donde describe esos componentes o
esa normativa (secciones 3.1 y Tabla 2, 6.1, 6.4 y 7). Cada entrada SHALL tener autor
institucional, titulo, `url` abierta durante el apply y `urldate` igual a la fecha real de
consulta. La tesis MUST NOT incorporar una fuente no verificada: la que no se verifique SHALL
omitirse y registrarse como omitida en `dictamen-correcciones.md`. La Tabla 2 SHALL citar
las cinco plataformas con `\parencite` en lugar de listar sus URL al pie. La tesis MUST NOT
atribuir a Twilio la transcripcion del audio si la realiza la Gemini API.

#### Scenario: Entradas nuevas con URL y fecha de consulta

- **WHEN** se inspeccionan las entradas nuevas de `Bibliography_base.bib`
- **THEN** cada una tiene `url` y `urldate` y figura en `dictamen-correcciones.md` con la fecha de consulta
- **AND** `verify_citations.py` reporta PASS y biber no emite advertencias

#### Scenario: Plataformas de la Tabla 2 citadas

- **WHEN** se lee la Tabla 2 (`tab:comparativa`) y su fuente
- **THEN** Jira Service Management y osTicket se citan con su entrada bibliografica como las otras tres plataformas
- **AND** la nota de fuente no lista URL de plataformas

#### Scenario: Normativa del articulo 12 citada

- **WHEN** se lee `subsec:transferencia-internacional`
- **THEN** la exigencia de un instrumento del articulo 12 cita la normativa complementaria verificada
- **AND** la transcripcion telefonica se atribuye al servicio que la realiza

### Requirement: Terminologia legal y descripcion de fuentes de la Tabla 1

La tesis SHALL usar "disociacion" (articulo 2 de la Ley 25.326) y MUST NOT usar
"pseudonimizacion" cuando atribuye a esa ley una condicion del tratamiento. En la Tabla 1
(`tab:trabajos-academicos`), la fila de Zangari et al. MUST NOT declarar el texto
"inaccesible" (es de acceso abierto) y SHALL declarar el idioma de los datos si la fuente lo
informa o "idioma no reportado"; la fila de Paramesh y Shreedhara SHALL describir a Ramya et
al. como trabajo de dos de los tres autores. La fecha de `Ley25326_2000` SHALL ser la de
sancion (4-10-2000) y ninguna parte del texto SHALL consignar otra fecha para la ley sin
rotularla como promulgacion.

#### Scenario: Disociacion en la seccion 9

- **WHEN** se busca "pseudonimizaci" en `08-discusion.tex`
- **THEN** no aparece atribuido a la Ley 25.326

#### Scenario: Tabla 1 corregida

- **WHEN** se buscan "texto inaccesible" y "de los mismos autores" en `03-estado-del-arte.tex`
- **THEN** no hay coincidencias
- **AND** la fila de Paramesh y Shreedhara dice "dos de los tres autores"

### Requirement: Forma de la lista de referencias segun el dictamen del 8 de noviembre

La lista de referencias impresa SHALL cumplir: actas de EMNLP con el anio en el nombre en
todas las entradas ("(EMNLP 2023)", "(EMNLP 2025)"); actas de PMLR impresas como
*Proceedings of Machine Learning Research* con su volumen y paginas; mayuscula tras los dos
puntos en el titulo de Mosqueira-Rey et al. ("A state of the art"); ordinal "3.ª" en
Jurafsky y Martin; URL o DOI verificado en Brown et al. (2020), Vaswani et al. (2017),
Radford et al. (2023), Pedregosa et al. (2011) y Powers (2011), o registro de su ausencia;
"Publicación anticipada en línea" en Mayor-Rocher et al.; y el apellido del primer autor de
`Gomez2026_repositorio` con la misma grafia que la portada. La verificacion SHALL hacerse
sobre el PDF compilado (salida de `biblatex-apa`), no solo sobre el `.bib`.

#### Scenario: Actas y PMLR uniformes

- **WHEN** se extrae el texto de las referencias del PDF
- **THEN** toda acta de EMNLP lleva el anio entre parentesis junto a "EMNLP"
- **AND** las entradas de PMLR imprimen "Proceedings of Machine Learning Research" seguido del volumen

#### Scenario: Correcciones puntuales visibles

- **WHEN** se extrae el texto de las referencias del PDF
- **THEN** aparecen "A state of the art", "3.ª" y "Publicación anticipada en línea" y no aparecen "a state of the art", "3.a edición" ni "Artículo en prensa"
- **AND** Brown, Vaswani, Radford, Pedregosa y Powers muestran URL o DOI, o su ausencia queda registrada

#### Scenario: Apellido consistente

- **WHEN** se compara el nombre del primer autor en `00-portada.tex` y en la entrada `Gomez2026_repositorio` impresa
- **THEN** ambos usan la misma grafia

### Requirement: Glosario conforme al uso del cuerpo tras el dictamen del 8 de noviembre

El glosario (`00-glosario.tex`) SHALL incluir CONEAU, NLBSE, PABAK, RGPD, UTC y GPT con su
expansion y MUST NOT incluir UML, FRM ni UTN mientras no se usen en el texto compilado del
cuerpo. SHALL conservar el orden alfabetico en la disposicion de dos columnas y el
comentario de cabecera SHALL declarar el total de entradas.

#### Scenario: Siglas agregadas y retiradas

- **WHEN** se buscan las entradas `\textbf{CONEAU}`, `\textbf{NLBSE}`, `\textbf{PABAK}`, `\textbf{RGPD}`, `\textbf{UTC}` y `\textbf{GPT}` en `00-glosario.tex`
- **THEN** las seis existen
- **AND** `\textbf{UML}`, `\textbf{FRM}` y `\textbf{UTN}` no existen

#### Scenario: Cobertura sin sobrantes

- **WHEN** se compara cada entrada del glosario con `rg -w` sobre `paper/sections/*.tex` excluyendo el glosario y los comentarios
- **THEN** cada entrada tiene al menos un uso

### Requirement: Fecha de las tablas primarias de la campana complementaria en el cronograma

La tabla de procedencia de `docs/diagrams/cronograma.md` SHALL fechar las tablas primarias
de la campana complementaria entre el 2026-11-04 y el 2026-11-08, coherente con
`git log -- evaluation/data/campana` (exportacion de `intervenciones.csv` el 2026-11-08).
`cronograma.png` SHALL regenerarse solo si el texto cambiado forma parte del bloque Mermaid.

#### Scenario: Fecha final corregida

- **WHEN** se busca "entre el 2026-11-04 y el 2026-11-06" en `docs/diagrams/cronograma.md`
- **THEN** no hay coincidencias
- **AND** la fila de la campana complementaria dice hasta el 2026-11-08

### Requirement: Neutralidad de paginas de las correcciones de c-188

Las correcciones de c-188 MUST NOT llevar el PDF del commit que recibe el tag de la release
por encima de 118 paginas (las del PDF del tag `v1.2.11`). El resumen y el abstract MUST NOT
cambiar ni superar 250 palabras. La compilacion SHALL cumplir el requisito "Thesis PDF
compilation" y el libro mayor de paginas (antes, despues y por cambio) SHALL registrarse en
`dictamen-correcciones.md`.

#### Scenario: Paginas dentro del tope

- **WHEN** se compila `main.tex` en el commit de contenido de la release
- **THEN** `compilacion.md` informa a lo sumo 118 paginas
- **AND** el libro mayor queda registrado en `dictamen-correcciones.md`

#### Scenario: Resumen y abstract intactos

- **WHEN** se compara `00-resumen.tex` con el de `v1.2.11`
- **THEN** no hay cambios
