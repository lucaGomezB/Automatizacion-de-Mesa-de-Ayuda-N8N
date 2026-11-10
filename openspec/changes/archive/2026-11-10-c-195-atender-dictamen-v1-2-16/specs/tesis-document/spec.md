## MODIFIED Requirements

### Requirement: Estado de la segunda sub-hipotesis coherente con la variable medida

El estado de la segunda sub-hipotesis SHALL quedar fijado como "refutada" (design D3 de c-192),
con el denominador de los casos que tuvieron oportunidad de revision humana y con el matiz de
incertidumbre que el dictamen del 2026-11-09 sobre `v1.2.13` exige. El texto SHALL declarar la
estimacion de 25 de 147 casos revisados (17,0 %; IC de Wilson [11,8 %; 23,9 %]) y que, segun la
regla de tres vias declarada, la estimacion alcanza la cota de 0,15, de modo que la
sub-hipotesis resulta refutada. El texto SHALL ademas consignar el matiz explicito: el IC de
Wilson contiene 0,15 y la prueba binomial (25 exitos sobre 147 con p = 0,15) da p = 0,28, por lo
que el intervalo no permite descartar una proporcion INFERIOR a la cota (su limite inferior es
11,8 %); el texto MUST NOT reducir ese matiz a "un valor cercano al umbral" (dictamen del
2026-11-09 sobre `v1.2.16`, A2). Se conserva el cociente 25 de 200 (12,5 %; IC [8,6 %; 17,8 %]) como
dato secundario, con la advertencia de que cuenta 53 casos web sin oportunidad de revision. El
texto SHALL declarar que la revision humana de la campaña complementaria alcanzo solo los
canales de correo (66) y telefonia (81) por la regla de derivacion por reportante no
identificado, y que los 53 casos del formulario web no tuvieron revision. Las confirmaciones
SHALL informarse con ambos denominadores explicitos: 122 de 200 (61,0 %) y 122 de 147 (83,0 %);
MUST NOT quedar un "122 (61,0 %)" adyacente al denominador de 147 que pueda leerse como
122 de 147. Ese estado y su matiz SHALL ser identicos donde el veredicto se enuncia: 8.3
(`subsec:reduccion-intervencion`) y la Tabla 18 (`tab:cumplimiento-objetivos`, filas del
objetivo general y del objetivo especifico 4); la seccion 9.1 (`08-discusion.tex`) SHALL
mencionar la segunda sub-hipotesis al resumir el estado de la hipotesis principal y SHALL llevar
el mismo matiz que 8.3. La seccion 8.3 MUST NOT contener "Medirla en condiciones validas": la
limitacion de la revision SHALL expresarse como condicion de generalizacion (extender la
conclusion al formulario web y a reportantes identificados exige una corrida en la que la
revision alcance a todos los canales), con remision a `subsec:medicion-intervencion`. El resumen (`00-resumen.tex`) y el abstract MUST NOT superar 250 palabras cada uno; si
incluyen el matiz, SHALL compensar palabras en el mismo resumen. La celda del objetivo
especifico 4 de la Tabla 18 MUST NOT contradecir el veredicto: MUST NOT declarar a la vez
"refutada" y "sin medicion valida por la regla del reportante".

#### Scenario: Veredicto unico de la sub-hipotesis 2

- **WHEN** se comparan 8.3, 9.1 y las filas del objetivo general y del objetivo especifico 4 de la Tabla 18
- **THEN** todos declaran la sub-hipotesis 2 como "refutada" con el denominador de 25 de 147
- **AND** ninguno la declara "no concluyente" con 25 de 200 como unico fundamento
- **AND** la celda del objetivo especifico 4 no declara a la vez "refutada" y "sin medicion valida"

#### Scenario: Matiz de incertidumbre declarado

- **WHEN** se leen 8.3 y 9.1
- **THEN** figuran el IC de Wilson [11,8 %; 23,9 %] que contiene 0,15 y la prueba binomial con p = 0,28
- **AND** el texto declara que el intervalo no permite descartar una proporcion inferior a la cota, sin cambiar el veredicto "refutada"
- **AND** ninguna de las dos contiene "un valor cercano al umbral"

#### Scenario: Condicion de generalizacion en 8.3

- **WHEN** se busca "Medirla en condiciones válidas" en `07-resultados.tex`
- **THEN** no hay coincidencias
- **AND** 8.3 declara que extender la conclusion al formulario web y a reportantes identificados exige una corrida con revision en todos los canales

#### Scenario: Denominadores del 122 explicitos

- **WHEN** se lee la oracion de las confirmaciones en 8.3
- **THEN** figura 122 de 200 (61,0 %) y 122 de 147 (83,0 %) con ambos denominadores explicitos
- **AND** no queda un "122 (61,0 %)" que pueda leerse como 122 de 147

#### Scenario: Estado unico de la sub-hipotesis 2

- **WHEN** se comparan el resumen, el abstract, 1.4, 4.7, 8.3, 9.1, el capitulo 10, la Tabla 18 y 11.3
- **THEN** todos declaran el mismo estado de la sub-hipotesis 2 ("refutada") con el mismo denominador (25 de 147)
- **AND** ninguno la declara "no concluyente" con 25 de 200 como unico fundamento
- **AND** ninguno la declara "refutada" por la tasa de 73,5 %

#### Scenario: Alcance de la revision declarado

- **WHEN** se lee 8.3
- **THEN** se declara que la revision humana alcanzo 66 casos de correo y 81 de telefonia y ninguno de los 53 del formulario web
- **AND** se declara que la regla del reportante determino que casos se revisaban

#### Scenario: Resumen sin ambiguedad de magnitud

- **WHEN** se lee la oracion del resumen y del abstract que enuncia los estados por sub-hipotesis
- **THEN** la cifra de intervencion nombra su magnitud y su denominador
- **AND** no queda un parentesis con 73,5 % y [67,0 %, 79,1 %] adyacente a la intervencion humana

#### Scenario: 11.3 reformulada

- **WHEN** se lee `subsec:medicion-intervencion`
- **THEN** no aparece "respecto del 73,5 %" como meta de reduccion
- **AND** se propone medir la variable con reportantes identificados en el directorio

### Requirement: Efecto minimo detectable del Spearman sin la eficiencia relativa de Wilcoxon

El efecto minimo detectable del contraste de posicion por correlacion de rangos de Spearman
SHALL calcularse con la transformacion de Fisher de la correlacion y la eficiencia relativa
asintotica de Spearman frente a Pearson bajo normalidad (`9/pi^2 ≈ 0,912`):
`rho_MDE = tanh((z_{1-alfa/2} + z_{potencia}) / sqrt((n - 3) * 9/pi^2))`, que con `n = 110`
(`n - 3 = 107`) da 0,2763 (0,276 en el texto). La tesis MUST NOT informar el MDE del Spearman con
la ARE de Wilcoxon (0,864), que corresponde a la prueba de rangos con signo. El valor SHALL
figurar en la seccion 8.7 (`07-resultados.tex`) y en `docs/Tesis/Correcciones/numeros-canonicos.md`
con su fuente. El analisis versionado SHALL producir el mismo valor que imprime la tesis:
`evaluation/stats.py` SHALL definir una constante para la eficiencia de Spearman (9/pi^2) y
`evaluation/campana.py` SHALL usarla en el MDE del Spearman, mientras los MDE de los contrastes de
Wilcoxon y Mann-Whitney SHALL conservar `ARE_WILCOXON_MINIMA`; cada comportamiento SHALL tener una
prueba escrita antes del codigo (Strict TDD). `analisis/resultados.json`, `resultados.md` y
`SHA256SUMS.txt` SHALL regenerarse con el comando de referencia del proyecto, y la regeneracion
MUST NOT cambiar ningun otro valor que el MDE del Spearman. Si la regeneracion cambia otro valor o
no es reproducible sin red, el cambio de codigo SHALL revertirse y la seccion 8.7 SHALL declarar
que 0,276 se recalculo fuera del analisis versionado, cuyo valor es 0,2834.

#### Scenario: MDE del Spearman reproducible

- **WHEN** se recalcula el MDE del Spearman con la formula y el `n` que declara el texto
- **THEN** el resultado es 0,2763 a cuatro decimales y el texto imprime 0,276
- **AND** el texto no contiene el valor 0,2834 como MDE vigente ni la ARE de Wilcoxon para el Spearman

#### Scenario: Analisis versionado alineado

- **WHEN** se lee el bloque `posicion.spearman` de cada operador en `evaluation/data/campana/analisis/resultados.json`
- **THEN** su `mde` es 0,2763 a cuatro decimales
- **AND** la comparacion con la version previa del JSON solo difiere en esos dos valores, y `SHA256SUMS.txt` solo en las filas de `resultados.json` y `resultados.md`

#### Scenario: MDE de Wilcoxon intacto

- **WHEN** se ejecutan las pruebas de `evaluation/tests/test_campana.py`
- **THEN** los MDE de los contrastes de condicion y de mitades siguen calculandose con `ARE_WILCOXON_MINIMA`
- **AND** el MDE del Spearman se calcula con la constante de la eficiencia de Spearman

#### Scenario: Camino alternativo declarado

- **WHEN** la regeneracion cambia otro valor o no se reproduce sin red y el codigo se revierte
- **THEN** 8.7 declara que 0,276 se recalculo fuera del analisis versionado, cuyo valor es 0,2834

#### Scenario: Registro del valor corregido

- **WHEN** se busca el MDE del Spearman en `numeros-canonicos.md`
- **THEN** figura 0,276 con la formula de 9/pi^2 y su procedencia (analisis regenerado o recalculo declarado)
- **AND** 0,2834 figura solo como valor superado

### Requirement: Fidelidad bibliografica y fuente de precios segun el dictamen del 9 de noviembre

La seccion 2.4 MUST NOT atribuir a Zanzotto (2019) la reserva del rol humano ante la
ambiguedad semantica y la responsabilidad sin pagina que lo respalde; la atribucion SHALL
separarse en DOS oraciones: la primera SHALL presentar como inferencia de los autores que el
diseno debe reservar a la persona un rol activo ante la ambiguedad semantica y la
responsabilidad sobre las consecuencias de la decision, y la segunda SHALL atribuir al
paradigma \emph{HitAI}, con `\textcite{Zanzotto2019_human_in_the_loop}`, que reclama retribuir
a quienes aportan el conocimiento que usan los sistemas; MUST NOT atribuirle "sostener la
supervision humana", que el resumen de la fuente no respalda (la supervision la sostienen, en el
mismo parrafo, Amershi et al. y Shneiderman). Tras el punto y coma que cierra la oracion de
Mosqueira-Rey et al., la inferencia SHALL empezar en minuscula ("; los autores de esta tesis
infieren"). Las secciones 2.5 y 9.2
MUST NOT atribuir a Xiong et al. (2024) una "baja discriminacion"; SHALL decir que predecir las
fallas sigue siendo un desafio. El punto unico de contacto (2.1) SHALL citarse con
`OGC2011_itil` y no con Galup et al. (2009). El calculo economico de 9.5 SHALL citar la pagina
de precios de la Gemini API, y la seccion 7 SHALL declarar el nivel de servicio (gratuito o
pago) en que opero el sistema y su consecuencia sobre el uso de los datos transferidos. Las URL
de Zendesk, Vertex (si se conserva) y del Decreto 1558/2001 SHALL resolver a la pagina citada.
La nota de `Zendesk2026_help_desk` SHALL describir lo que la pagina muestra (una pagina de
producto de software de servicio al cliente) y MUST NOT declarar "capacidades y precios"
ni la denominacion "Suite", que la pagina no usa; el titulo SHALL reproducir el de la pagina
verificada;
SHALL conservar autor, titulo, URL `https://www.zendesk.com/service/` y `urldate`. Ramya et al.
SHALL citarse en su version IEEE (CSITSS 2018) con DOI; Kerby (2014) con el localizador
3:11.IT.3.1; Efron y Tibshirani con año y DOI de la misma edicion; FrugalGPT en TMLR solo si se
confirma. Toda entrada nueva o modificada SHALL verificarse en la fuente y `verify_citations.py`
SHALL dar PASS.

#### Scenario: Atribuciones corregidas

- **WHEN** se leen 2.1, 2.4, 2.5 y 9.2
- **THEN** el punto unico de contacto cita ITIL, Zanzotto no sostiene una afirmacion sin respaldo y Xiong no se cita por "baja discriminacion"

#### Scenario: Zanzotto en dos oraciones

- **WHEN** se lee 2.4 (`subsec:human-in-the-loop`)
- **THEN** la inferencia de los autores y el paradigma HitAI estan en oraciones separadas
- **AND** solo la clausula de retribuir a quienes aportan el conocimiento se atribuye a `Zanzotto2019_human_in_the_loop` con `\textcite`
- **AND** la oracion de Zanzotto no contiene "sostener la supervisión humana" y en `02-marco-teorico.tex` no queda "; Los autores"

#### Scenario: Precios y nivel de servicio

- **WHEN** se leen 9.5 y 7
- **THEN** 9.5 cita la pagina de precios de la Gemini API
- **AND** 7 declara el nivel de servicio y su consecuencia sobre los datos

#### Scenario: Nota de Zendesk sin precios

- **WHEN** se lee `Zendesk2026_help_desk` en `Bibliography_base.bib`
- **THEN** la nota describe la pagina de producto y no contiene "precios" ni "Suite"
- **AND** la URL y el `urldate` se conservan

#### Scenario: Entradas corregidas

- **WHEN** se compila y se lee la lista de referencias
- **THEN** Ramya figura como IEEE CSITSS 2018 con DOI, Kerby con 3:11.IT.3.1 y Efron con año y DOI concordantes
- **AND** biber no registra advertencias y `verify_citations.py` reporta PASS

### Requirement: Linea futura de medicion de la intervencion con denominador revisable

La seccion 11.3 (`subsec:medicion-intervencion`) SHALL incluir, ademas de los reportantes
identificados, tres requisitos de una medicion valida de la segunda sub-hipotesis: que la
revision alcance a todos los canales o a una muestra aleatoria de cada uno; que cada validacion se
coteje con una referencia independiente; y que la muestra se dimensione para que el limite
superior del intervalo de Wilson pueda quedar por debajo de 0,15, porque con una proporcion
cercana a la cota una muestra del orden de 150 casos no permite declarar compatibilidad.

#### Scenario: Requisitos de la medicion futura

- **WHEN** se lee 11.3
- **THEN** figuran la revision de todos los canales (o muestra aleatoria por canal) y el cotejo con una referencia independiente
- **AND** figura el requisito de dimensionar la muestra para que el limite superior del intervalo pueda quedar por debajo de 0,15

### Requirement: Trazabilidad del dictamen del 9 de noviembre sobre v1.2.13 en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir las secciones "Dictamen v10 /
v1.2.13 (2026-11-09) - c-192", "- c-193" y "- c-194", y CADA una SHALL contener, ademas de su
tabla de correcciones, una matriz de 7 columnas (Rec | Sintesis | Change | Archivo:linea | Ancla |
Fragmento verificable | Estado) que `verificar_matriz_trazabilidad.py` verifique: c-192 con las
recomendaciones A1, A2, A3, B1, B2, B3 y los residuos de C1 y C2 que atendio; c-193 con B4 y el
item 13; c-194 con C1 (fila "Lim." y Zanzotto) y C2 (Zendesk). Las filas cuyo parrafo reescribe un
change posterior SHALL marcarse "SUPERADA por c-NNN". La fila "Lim." del Anexo I
(`tab:anexo-trazabilidad-2810`, `12-anexos.tex`) SHALL leer como SECUENCIA TEMPORAL: primero
`c-169` resolvio dos de los cinco limites estructurales (exactitud del brazo manual e intervalo
del kappa) y dejo sin concluir la sub-hipotesis de intervencion humana; despues `c-190` la
refuto sobre los casos revisados y corrigio la definicion de exactitud laxa; el efecto de orden
no se resolvio y la validacion fuera de muestra permanece como limitacion negativa declarada.
Su columna Change SHALL nombrar `\texttt{c-169}, \texttt{c-190}`. El Anexo I
(`sec:anexo-trazabilidad`) SHALL incluir una tabla de trazabilidad del dictamen del 9-11 sobre
`v1.2.13` (`tab:anexo-trazabilidad-0911-v1213`), con una fila por recomendacion (A1 a A3, B1 a B4,
C1 y C2), el change o los changes responsables (`c-192`, `c-193`, `c-194`) y las secciones
tocadas con `\autoref`, sin numeros de linea, en cuerpo `\footnotesize`. El parrafo de
presentacion del Anexo I SHALL contar los dictamenes que versiona `auditorias/` y nombrar los que
el anexo traza. `verificar_matriz_trazabilidad.py` SHALL reportar 0 fallas sobre el arbol y sobre
el tag de la release. El archivo del dictamen
(`auditorias/Dictamen_Tesis_v10_v1.2.13_CONEAU_2026-11-09.md`) SHALL estar versionado.

#### Scenario: Matrices verificables de c-192 a c-194

- **WHEN** se ejecuta `verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen informa filas para las secciones de c-192, c-193 y c-194
- **AND** la cantidad de fallas es 0

#### Scenario: Fila Lim. como secuencia temporal

- **WHEN** se compila y se lee la fila "Lim." del Anexo I
- **THEN** declara primero el aporte de `c-169` y despues el de `c-190`, en ese orden
- **AND** su columna Change nombra `c-169` y `c-190` y no contiene numeros de linea

#### Scenario: Tabla del dictamen sobre v1.2.13 en el Anexo I

- **WHEN** se compila y se lee el Anexo I
- **THEN** figura la tabla `tab:anexo-trazabilidad-0911-v1213` con las recomendaciones A1 a C2 y sus changes
- **AND** sus `\autoref` resuelven y no hay numeros de linea

#### Scenario: Conteo de la serie

- **WHEN** se cuentan los dictamenes `.md` de `auditorias/` y se lee el parrafo de presentacion del Anexo I
- **THEN** el numero declarado coincide con el de los archivos versionados

#### Scenario: Matriz completa del dictamen v1.2.13

- **WHEN** se leen las secciones de c-192, c-193 y c-194 de `dictamen-correcciones.md`
- **THEN** cada observacion, el item 12, el item 13, C1 y C2 tienen una fila con archivo, fragmento verificable y estado
- **AND** `verificar_matriz_trazabilidad.py` reporta 0 fallas

#### Scenario: Anexo I actualizado

- **WHEN** se compila y se lee el Anexo I
- **THEN** las tablas de trazabilidad del dictamen del 9-11 sobre v1.2.13 resuelven con sus `\autoref`

#### Scenario: Versionado no bloqueante del dictamen

- **WHEN** el archivo del dictamen no esta todavia en `auditorias/`
- **THEN** la tarea de versionarlo queda declarada y la release no se bloquea
- **AND** cuando el archivo se agrega, queda versionado en `auditorias/`

### Requirement: Verificador de la matriz de trazabilidad vigente

`docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` SHALL verificar todas las
matrices de 7 columnas con encabezado "Fragmento verificable" de
`dictamen-correcciones.md`, en cualquier seccion (dictamenes del 22-10, del 28-10, del
8-11 y del 9-11). Una fila SHALL pasar cuando el fragmento aparece en el archivo citado y el
ancla `\label` existe en el; si el fragmento esta en otra linea, SHALL pasar con un aviso de
desplazamiento, salvo con `--estricto`, que exige la linea exacta. Las filas cuyo estado
empieza con "PENDIENTE" o "SUPERADA" SHALL omitirse. Ademas, toda seccion `## Dictamen ...` cuyo
titulo nombre un change `c-NNN` con NNN mayor o igual que 190 SHALL contener al menos una fila de
matriz; una seccion asi sin matriz SHALL contarse como falla con un mensaje que nombre la
seccion, de modo que un ciclo de correcciones sin trazar no pase inadvertido. El script SHALL
conservar `--rev`, `--reubicar` y `--estricto`. Cada comportamiento SHALL tener una prueba en
`test_verificar_matriz_trazabilidad.py` escrita antes del codigo (Strict TDD). Tras el apply,
el script SHALL terminar con codigo 0 sobre el arbol de trabajo y con `--rev` del tag de la
release; cada fila marcada "SUPERADA" SHALL nombrar el change que reescribio el parrafo.

#### Scenario: Todas las matrices verificadas

- **WHEN** se ejecuta `python docs/Tesis/Correcciones/verificar_matriz_trazabilidad.py` desde la raiz
- **THEN** el resumen informa filas de las matrices del 22-10, del 28-10, del 8-11 y de las secciones de c-190 a c-195
- **AND** el codigo de salida es 0 y la cantidad de fallas es 0

#### Scenario: Desplazamiento de linea no es falla

- **WHEN** el fragmento de una fila aparece en el archivo en una linea distinta de la citada
- **THEN** sin `--estricto` la fila pasa con el aviso "desplazada"
- **AND** con `--estricto` la fila falla

#### Scenario: Fragmento ausente o ancla inexistente

- **WHEN** el fragmento no aparece en ninguna linea del archivo o el ancla no existe
- **THEN** la fila falla con un mensaje que nombra el fragmento o el ancla

#### Scenario: Seccion de dictamen sin matriz

- **WHEN** el registro tiene una seccion `## Dictamen ... - c-192` sin ninguna matriz de 7 columnas
- **THEN** el script informa una falla que nombra esa seccion y termina con codigo distinto de 0
- **AND** una seccion de un change anterior a c-190 sin matriz no se cuenta como falla

#### Scenario: Pruebas primero y en verde

- **WHEN** se ejecuta `python -m unittest test_verificar_matriz_trazabilidad -v` desde `docs/Tesis/Correcciones/`
- **THEN** todas las pruebas pasan, incluidas las de matrices multiples, desplazamiento, `--estricto`, filas SUPERADA y secciones sin matriz

## ADDED Requirements

### Requirement: Canal telefonico descrito por el webhook telefonia-handoff y residuales del dictamen v1.2.13

La seccion 6.3 (`06-implementacion.tex`, lista de recepcion) MUST NOT describir el disparador
telefonico como "trigger de Twilio" ni como "callback de grabación de Twilio"; SHALL describirlo
como el webhook `telefonia-handoff`, al que el backend entrega la transcripcion, coherente con
5.2, 6.4 y con el nodo "Llamada telefonica" de `n8n/workflow.json`, y SHALL hablar de "tres
disparadores de canal", porque el flujo tiene ademas el webhook `notificacion-clasificacion`
(Anexo E), que no es un canal de entrada. La descripcion MUST NOT mencionar un "webhook de
transcripción" hacia N8N. La seccion 3.1 (`03-estado-del-arte.tex`) MUST NOT atribuir a Xiong et
al. (2024) una "poca capacidad para separar aciertos de errores"; SHALL decir que predecir las
fallas sigue siendo un desafio, conservando la sobreconfianza y la concentracion en la parte alta
de la escala, como en 2.5 y 9.2. La sigla `VIS` SHALL desarrollarse en su primer uso en el cuerpo
o figurar en el glosario, y cada entrada del glosario SHALL tener uso en el cuerpo. La entrada
bibliografica de FrugalGPT SHALL conservar la URL de OpenReview (`cSimKw5p6R`) de TMLR y la nota
del preprint de arXiv (`2305.05176`); MUST NOT inventarse un venue. El exceso de paginas sobre el
tope total de 100 SHALL registrarse como residual declarado en el libro mayor, con su magnitud,
fecha y decision.

#### Scenario: Disparador telefonico en la lista de recepcion

- **WHEN** se buscan "trigger de Twilio" y "callback de grabación de Twilio" en `06-implementacion.tex`
- **THEN** no hay coincidencias
- **AND** la lista de recepcion nombra el webhook `telefonia-handoff` y "tres disparadores de canal"

#### Scenario: Atribucion de Xiong atenuada

- **WHEN** se busca "separar aciertos de errores" en `03-estado-del-arte.tex`
- **THEN** no hay coincidencias
- **AND** el texto declara que predecir las fallas sigue siendo un desafio

#### Scenario: FrugalGPT sin venue inventado

- **WHEN** se lee la entrada de FrugalGPT en la bibliografia
- **THEN** conserva la URL de OpenReview de TMLR y la nota del preprint de arXiv

### Requirement: Regla de tres vias declarada como asimetrica en su definicion

Donde se define la regla de tres vias de la segunda sub-hipotesis, en 1.4
(`01-introduccion.tex`, `subsec:hipotesis-trabajo`) y en 4.7 (`04-marco-metodologico.tex`,
parrafo "Analisis de la campana complementaria de medicion"), el texto SHALL declarar que la
regla es asimetrica: "refutada" significa que la estimacion puntual alcanza o supera la cota de
0,15, no un rechazo estadistico de la hipotesis p <= 0,15, mientras que "compatible" exige que el
limite superior del intervalo de Wilson quede por debajo de la cota. El resumen y el abstract MUST
NOT superar 250 palabras cada uno y, si no se modifican, MUST NOT cambiar.

#### Scenario: Asimetria declarada en la definicion

- **WHEN** se leen las definiciones de la regla de tres vias en 1.4 y en 4.7
- **THEN** ambas declaran que "refutada" es la estimacion puntual que alcanza la cota y no un rechazo estadistico de p <= 0,15

#### Scenario: Resumen dentro del tope

- **WHEN** se cuentan las palabras de `00-resumen.tex` con la regla registrada
- **THEN** el resumen y el abstract tienen a lo sumo 250 palabras cada uno

### Requirement: Propagacion del dictamen sobre v1.2.16 en el metodo, los resultados y el memo

La seccion 4.2 (`04-marco-metodologico.tex`, protocolo de medicion en vivo) SHALL declarar que,
por el cronometraje mutuo de los pares de la campana 2026-10, el observador de `A1` fue `T1`,
autor del trabajo, lo que debilita la atenuacion del efecto Hawthorne atribuida a `A1`. La
seccion 8.7 (`07-resultados.tex`, "Exactitud del brazo manual") SHALL declarar que
`predicciones_in_sample.json` y `predicciones_hybrid-v3_2026-10-07.json` contienen las mismas 200
predicciones, verificado antes de escribir sobre los blobs versionados (no sobre las copias de
trabajo, cuyo fin de linea puede diferir). `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL
reemplazar el estado "no concluyente" de la segunda sub-hipotesis por "refutada sobre los 147
revisados" con sus matices (Wilson [0,118; 0,239], binomial p = 0,28, el intervalo no descarta
una proporcion inferior a la cota, 25/200 como dato secundario), SHALL describir el conjunto laxo
del brazo manual por la INTERSECCION de los adicionales (130/151; la union daria 137) y SHALL
actualizar la fila del MDE del Spearman y, si el analisis se regenera, las huellas SHA-256 de
`resultados.json` y `resultados.md`.

#### Scenario: Observador de A1 declarado

- **WHEN** se lee el protocolo de medicion en vivo de 4.2
- **THEN** figura que el observador de `A1` fue el autor `T1` y que eso debilita la atenuacion del efecto Hawthorne

#### Scenario: Caches identicas declaradas

- **WHEN** se lee el parrafo "Exactitud del brazo manual" de 8.7
- **THEN** declara que las dos caches del 7-10 contienen las mismas 200 predicciones
- **AND** `git show` de ambos archivos produce el mismo SHA-256

#### Scenario: Memo sin estados superados

- **WHEN** se buscan en `numeros-canonicos.md` el estado de la segunda sub-hipotesis y la definicion del laxo manual
- **THEN** no queda "no concluyente" como estado vigente de la sub-hipotesis ni "unión" como criterio del laxo

### Requirement: Formulaciones residuales del dictamen sobre v1.2.16

La seccion 8.3 SHALL presentar `VIS-005` como requisito de la especificacion de visibilidad de
incidentes (c-82) que fija la derivacion por reportante no identificado, de modo que el lector no
dependa de un identificador interno sin explicar. La introduccion del capitulo 11
(`10-recomendaciones.tex`) SHALL decir que la campana complementaria refuto la segunda
sub-hipotesis sobre los casos revisados, y MUST NOT decir que refuto la medicion.

#### Scenario: VIS-005 presentado

- **WHEN** se lee la mencion de `VIS-005` en 8.3
- **THEN** figura como requisito de la especificacion de visibilidad de incidentes (c-82)

#### Scenario: Capitulo 11 sin refutar la medicion

- **WHEN** se lee el primer parrafo de `sec:recomendaciones`
- **THEN** lo refutado es la sub-hipotesis sobre los casos revisados y no la medicion

### Requirement: Trazabilidad del dictamen del 9 de noviembre sobre v1.2.16 en el registro y el Anexo I

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL incluir una seccion "Dictamen v10 /
v1.2.16 (2026-11-09) - c-195" con una matriz de 7 columnas (Rec | Sintesis | Change |
Archivo:linea | Ancla | Fragmento verificable | Estado) que cubra las recomendaciones A1 a A3, B1
a B3, C1 y C2 y los 18 items del inventario del dictamen, con su estado; las decisiones de los
autores del design de c-195 (consentimiento diferido a los autores, camino del MDE, crecimiento de paginas,
estado de la URL de ServiceNow, items fuera de alcance); y el libro mayor de paginas y palabras.
El Anexo I (`sec:anexo-trazabilidad`) SHALL incluir una tabla de trazabilidad del dictamen del 9-11
sobre `v1.2.16` (`tab:anexo-trazabilidad-0911-v1216`), con una fila por recomendacion, el change
`c-195` y las secciones tocadas con `\autoref`, sin numeros de linea, en cuerpo `\footnotesize`.
Los items que no se atienden SHALL figurar con su motivo (por ejemplo, la mencion de c-191 en
11.8, que el dictamen condiciona a su ejecucion antes de la defensa). La recomendacion A1
(consentimiento) y los items 1 y 2 del inventario SHALL figurar con estado "PENDIENTE (diferida: la
atienden los autores al recabar las firmas)", porque la redaccion de 7.5, la plantilla y el registro
de la campana quedan fuera de c-195. El archivo
`auditorias/Dictamen_Tesis_v10_v1.2.16_CONEAU_2026-11-09.md` SHALL estar versionado.

#### Scenario: Matriz completa del dictamen v1.2.16

- **WHEN** se lee la seccion de c-195 de `dictamen-correcciones.md`
- **THEN** cada recomendacion y cada item del inventario tiene una fila con archivo, fragmento verificable y estado
- **AND** `verificar_matriz_trazabilidad.py` reporta 0 fallas

#### Scenario: Tabla del dictamen sobre v1.2.16 en el Anexo I

- **WHEN** se compila y se lee el Anexo I
- **THEN** figura la tabla `tab:anexo-trazabilidad-0911-v1216` con sus `\autoref` resueltos

### Requirement: Consistencia de las referencias de la version entregada en v1.2.17

Las referencias a la configuracion entregada SHALL nombrar la release vigente `v1.2.17` en
`05-arquitectura.tex` (leyendas de las figuras de arquitectura, de entidades y del diagrama
entidad-relacion), `06-implementacion.tex`, `11-aspectos-legales.tex` (nota de la tabla NIST) y
`12-anexos.tex` (Anexo A, leyendas de secuencia y componentes, Anexo B, encabezado de la Tabla de
configuracion evaluada frente a entregada y su nota de fuente). El texto MUST NOT nombrar
`v1.2.16` como configuracion entregada; las menciones historicas (los dictamenes sobre `v1.2.12`,
`v1.2.13` y `v1.2.16` en el Anexo I) SHALL conservarse. Si la nota de fuente de la Tabla de
configuracion declara un `git diff --stat` contra la release, su conteo de archivos SHALL
recalcularse contra `v1.2.17`. La fecha de la portada SHALL ser la fecha de la release.

#### Scenario: Version entregada vigente

- **WHEN** se busca `v1.2.16` en los cuatro archivos
- **THEN** solo quedan menciones historicas del dictamen sobre esa version
- **AND** las referencias de configuracion entregada nombran `v1.2.17`

#### Scenario: Nota de la Tabla de configuracion verificable

- **WHEN** se ejecuta el `git diff --stat` que declara la nota contra `v1.2.17`
- **THEN** el conteo de archivos coincide con el impreso

### Requirement: Etiqueta de la release v1.2.17 y trazabilidad del hash

La release entregada SHALL ser `v1.2.17`. El Anexo B (`sec:anexo-repositorio`, `12-anexos.tex`)
SHALL nombrar el tag anotado `v1.2.17` creado sobre el commit de contenido; el commit de contenido
SHALL llevar la oracion de verificacion ("El PDF compilado en el propio tag no imprime ese hash
... `git rev-list -n1 v1.2.17` ...") en lugar del hash, y el commit inmediatamente posterior SHALL
reemplazar solo esa linea por el hash completo del commit de contenido. Los commits posteriores
MUST NOT modificar las fuentes de la tesis. El PDF compilado en el tag MUST NOT imprimir el hash de
una release previa (ni `ca3c885` de `v1.2.16` ni cualquier otro).

#### Scenario: Anexo B nombra la release vigente

- **WHEN** se compila el commit de contenido y se lee el Anexo B
- **THEN** el tag nombrado es `v1.2.17` y figura la oracion `git rev-list -n1 v1.2.17`

#### Scenario: Commit del hash posterior al tag

- **WHEN** se ejecuta `git diff --stat v1.2.17 HEAD -- "docs/Tesis/v10 (IA)/paper/sections"` tras el commit del hash
- **THEN** cambia un archivo y una linea

#### Scenario: PDF del tag sin hash ajeno

- **WHEN** se extrae el texto del PDF compilado en `v1.2.17`
- **THEN** no figura ninguna cadena hexadecimal de 40 caracteres

### Requirement: Libro mayor de paginas de las correcciones de c-195

Las correcciones de c-195 MUST NOT llevar el PDF del commit etiquetado `v1.2.17` por encima de 120
paginas, y todo crecimiento sobre las 118 paginas de `v1.2.16` SHALL deberse solo a las dos tablas
nuevas del Anexo I.
El crecimiento SHALL registrarse como decision en el libro mayor de `dictamen-correcciones.md`
(paginas antes y despues, causa y fecha). La compilacion SHALL cumplir el requisito "Thesis PDF
compilation": 0 errores, 0 referencias o citas indefinidas, `main.blg` sin advertencias,
`verify_citations.py` PASS y `compilacion.md` con el SHA-256 del PDF.

#### Scenario: Paginas dentro del margen declarado

- **WHEN** se compila `main.tex` en el commit de contenido de `v1.2.17`
- **THEN** `compilacion.md` informa a lo sumo 120 paginas
- **AND** el libro mayor registra el crecimiento respecto de 118 y su causa

## REMOVED Requirements

### Requirement: Canal telefonico descrito por el callback de grabacion y residuales del dictamen v1.2.13

**Reason**: el dictamen del 2026-11-09 sobre `v1.2.16` (B2) observa que "callback de grabacion de
Twilio" sigue siendo inexacto como disparador de N8N: el callback llega al backend, y el
disparador del flujo es el webhook `telefonia-handoff`.
**Migration**: el contenido se traslada al requisito "Canal telefonico descrito por el webhook
telefonia-handoff y residuales del dictamen v1.2.13" (ADDED en c-195), que conserva Xiong, VIS,
FrugalGPT y el exceso de paginas y reemplaza la descripcion de 6.3.

### Requirement: Consistencia de las referencias de la version entregada en v1.2.16

**Reason**: la release entregada pasa a ser `v1.2.17` (c-195); exigir `v1.2.16` contradiria la
version vigente.
**Migration**: requisito "Consistencia de las referencias de la version entregada en v1.2.17"
(ADDED en c-195).

### Requirement: Etiqueta de la release v1.2.16 y trazabilidad del hash

**Reason**: la release entregada pasa a ser `v1.2.17` (c-195).
**Migration**: requisito "Etiqueta de la release v1.2.17 y trazabilidad del hash" (ADDED en
c-195); la regla general sigue en "Regla de hash de release sin imprimir el hash de la release
previa".
