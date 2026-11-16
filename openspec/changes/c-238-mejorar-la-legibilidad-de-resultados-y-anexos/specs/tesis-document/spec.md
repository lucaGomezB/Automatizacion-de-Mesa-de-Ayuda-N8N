## ADDED Requirements

### Requirement: Tabla de sintesis de cifras primarias al abrir el capitulo de resultados

El capitulo de resultados (`07-resultados.tex`) SHALL abrir, despues de su parrafo introductorio y del parrafo de recordatorio de la procedencia y antes de su primera `\subsection`, con un parrafo breve que declare que se concluye frente a cada sub-hipotesis y a la hipotesis de integracion, y con una tabla unica de cifras primarias etiquetada `tab:sintesis-resultados` (devolucion de tercera instancia del 16-11-2026, M-03). Cada fila SHALL consignar la medida, la cifra primaria, su `n`, su intervalo de confianza al 95 % cuando exista, el veredicto frente a la hipotesis u objetivo con el mismo calificador que el resumen y la discusion, y una remision (`\autoref`) a la seccion que la desarrolla. La tabla SHALL incluir solo cifras primarias dentro de la muestra que el capitulo conserva y MUST NOT incluir cifras retiradas del ejemplar. Dentro de `07-resultados.tex`, cada cifra primaria de la tabla SHALL aparecer en prosa solo en su seccion de desarrollo; las demas menciones en prosa del capitulo SHALL reemplazarse por una remision a la tabla o a esa seccion (las tablas propias de cada seccion quedan exentas). El parrafo y la tabla MUST NOT introducir cifras, intervalos ni veredictos que no figuren ya en el capitulo y en `docs/Tesis/Correcciones/numeros-canonicos.md`.

#### Scenario: Sintesis presente al abrir el capitulo

- **WHEN** se lee el comienzo de `07-resultados.tex`
- **THEN** antes de la primera `\subsection` hay un parrafo de conclusion y la tabla `tab:sintesis-resultados`
- **AND** el parrafo introductorio que enumera los apartados y el recordatorio de la procedencia se conservan en ese orden antes de la sintesis

#### Scenario: Fila completa y trazable

- **WHEN** se recorre cada fila de `tab:sintesis-resultados`
- **THEN** cada una tiene medida, cifra, `n`, intervalo (o "---" si no corresponde), veredicto y una remision que resuelve a una seccion existente
- **AND** cada cifra coincide con la de su seccion de desarrollo y con `numeros-canonicos.md`

#### Scenario: Sin repeticion en prosa dentro del capitulo

- **WHEN** se cuentan las apariciones en prosa de cada cifra primaria de la tabla en `07-resultados.tex`, excluidas las tablas
- **THEN** cada cifra aparece en prosa solo en su seccion de desarrollo
- **AND** el conteo antes y despues queda registrado en `docs/Tesis/Correcciones/dictamen-correcciones.md`

### Requirement: Anexo de lecturas de sensibilidad y robustez con vocabulario minimo de rotulos

`12-anexos.tex` SHALL incorporar, como ultima `\section` dentro de `appendices` (de modo que no renumere los anexos existentes), un anexo de lecturas de sensibilidad y robustez etiquetado `sec:anexo-sensibilidad`, que reciba las tablas y lecturas del capitulo de resultados que releen valores ya calculados bajo un supuesto o un ambito alternativo y no deciden una hipotesis ni un objetivo: al menos el detalle de los descuentos de redondeo y el rango de robustez de los tiempos con `tab:rango-robustez-tiempos`, y las relecturas de la campana complementaria con otro brazo automatizado (devolucion de tercera instancia, M-03). En el cuerpo SHALL quedar la cifra primaria y una remision a `\autoref{sec:anexo-sensibilidad}`. Las etiquetas trasladadas SHALL conservar su nombre. El capitulo de resultados SHALL definir una sola vez el vocabulario de rotulos de cifras ---primaria, secundaria y sensibilidad--- y SHALL usar solo esos rotulos para calificar cifras; MUST NOT usar "cota de alcance", "vigente" ni "superada" como rotulo de cifra. "Campaña complementaria" se conserva como nombre de la campana, y "cota superior" o "cota inferior" solo cuando describan la direccion de un sesgo de medicion. El traslado MUST NOT cambiar ningun valor, intervalo ni lectura.

#### Scenario: Anexo nuevo sin renumerar

- **WHEN** se compila el documento
- **THEN** el anexo `sec:anexo-sensibilidad` aparece despues del anexo de numeros canonicos con la letra siguiente
- **AND** los anexos previos conservan su letra

#### Scenario: Tablas de robustez fuera del cuerpo

- **WHEN** se busca `tab:rango-robustez-tiempos` y el parrafo del rango de robustez en `sections/*.tex`
- **THEN** su definicion esta en `sec:anexo-sensibilidad`
- **AND** la seccion de tiempos del capitulo de resultados conserva la reduccion primaria con su intervalo y remite al anexo

#### Scenario: Vocabulario minimo de rotulos

- **WHEN** se ejecuta `rg -n -i "cotas? de alcance" "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex"`
- **THEN** no hay coincidencias
- **AND** el capitulo contiene una unica definicion de primaria, secundaria y sensibilidad

#### Scenario: Valores intactos tras el traslado

- **WHEN** se coteja el multiconjunto de cifras de `sections/*.tex` antes y despues del traslado
- **THEN** no falta ni cambia ningun valor

### Requirement: Reduccion medible de la extension del cuerpo

Las correcciones de legibilidad SHALL reducir de forma medible la extension del cuerpo (capitulos 1 a 11, `01-introduccion.tex` a `11-aspectos-legales.tex`) con un metodo de conteo unico aplicado igual a la linea base `v1.5.2` y al cierre: palabras de prosa con la limpieza de `docs/Tesis/Correcciones/sent_c197.py` (metodo principal), `wc -w` crudo de los mismos fuentes y paginas del PDF de una compilacion de verificacion (devolucion de tercera instancia, M-03). El conteo de prosa al cierre SHALL ser al menos 4 % menor que el medido al comenzar el change. La linea base, el conteo al comenzar, el resultado y la meta conjunta con el retiro de lo fuera de muestra SHALL registrarse en `docs/Tesis/Correcciones/dictamen-correcciones.md`; si la meta conjunta no se alcanza, SHALL registrarse su causa. La reduccion MUST NOT lograrse borrando contenido sustantivo, cifras ni salvedades: solo por traslado a anexos, remision en lugar de repeticion y partido de oraciones.

#### Scenario: Reduccion registrada con el mismo metodo

- **WHEN** se ejecuta el metodo de conteo sobre `v1.5.2` y sobre el estado final
- **THEN** ambos conteos usan el mismo comando y los mismos archivos
- **AND** el conteo de prosa final es al menos 4 % menor que el del comienzo del change

#### Scenario: Sin perdida de contenido sustantivo

- **WHEN** se revisa el diff de los capitulos 1 a 11
- **THEN** cada pasaje retirado del cuerpo figura trasladado a un anexo o reemplazado por una remision que resuelve

### Requirement: Cifras y conclusiones intactas en las correcciones de legibilidad

Las correcciones de legibilidad de la devolucion de tercera instancia (M-03, B-01, B-03) MUST NOT cambiar ninguna cifra, intervalo, veredicto, cita ni conclusion. La verificacion SHALL comparar una foto de cifras tomada antes de editar con la del estado final por multiconjunto de valores, admitiendo solo las apariciones agregadas por `tab:sintesis-resultados` y las retiradas por remision. `verify_citations.py` SHALL seguir en `STATUS: PASS`, una compilacion de verificacion SHALL cerrar con 0 referencias y citas indefinidas y 0 etiquetas duplicadas, y ninguna `\ref` ni `\autoref` SHALL quedar sin destino.

#### Scenario: Foto de cifras sin diferencias de valor

- **WHEN** se comparan las fotos de cifras antes y despues
- **THEN** ningun valor desaparece ni cambia
- **AND** las diferencias de cantidad de apariciones se explican por la tabla de sintesis o por remisiones registradas

#### Scenario: Citas y referencias resueltas

- **WHEN** se ejecuta `python verify_citations.py` desde `docs/Tesis/v10 (IA)/` y se compila en un directorio temporal
- **THEN** el verificador informa `STATUS: PASS`
- **AND** el registro de compilacion no tiene referencias ni citas indefinidas

## MODIFIED Requirements

### Requirement: Coherencia de los nombres de sector con su definicion canonica

En la prosa, los nombres de sector SHALL escribirse en la fuente del cuerpo y con tilde ("Seguridad Informática", "Soporte Técnico Hardware", "Soporte Técnico Software", "Bases de Datos", "Sistemas"); donde la tesis cita la cadena exacta del sistema (tablas de datos, matriz de confusion, metricas por clase, fronteras de error, prompt, definicion de la taxonomia del clasificador y toda enumeracion presentada como "los cinco sectores canonicos") SHALL escribirse en monoespaciado y sin tilde, coincidiendo byte a byte con `App/Backend/app/constants.py` (devoluciones del 11-11-2026, N-15, y del 16-11-2026, B-01). Ambas formas SHALL producirse con un par de macros definidas en `preambles/preamble.tex`: `\sectorcad{<clave>}` para la cadena del sistema y `\sectorprosa{<clave>}` para el nombre en prosa, con las claves `si`, `hw`, `sw`, `bd` y `sis`; una clave desconocida SHALL producir un error de compilacion. Fuera de los entornos literales (`lstlisting`, `verbatim`) y de `\path{}`, ninguna mencion de sector en `sections/*.tex` SHALL escribirse sin una de las dos macros. Un mismo pasaje MUST NOT mezclar ambas formas para el mismo sector salvo que distinga explicitamente el nombre de la cadena. La convencion y el inventario de pasajes SHALL constar en el registro de la revision. Las cinco cadenas canonicas en codigo, prompt y datos MUST NOT alterarse, y ningun reemplazo SHALL hacerse a ciegas.

#### Scenario: Convencion canonica aplicada

- **WHEN** se revisan las menciones de los cinco sectores segun la convencion vigente (prosa con tilde en la fuente del cuerpo; cadena exacta del clasificador en monoespaciado y sin tilde)
- **THEN** cada mencion usa la macro que le corresponde
- **AND** la convencion y el inventario por archivo constan en el registro de la revision

#### Scenario: Excepcion documentada

- **WHEN** un pasaje cita la cadena exacta del clasificador dentro de un entorno literal o de `\path{}`
- **THEN** conserva la forma canonica literal
- **AND** el registro de la revision lo consigna como excepcion

#### Scenario: Prosa con tilde

- **WHEN** se buscan "Seguridad Informatica", "Soporte Tecnico Hardware" y "Soporte Tecnico Software" escritas literalmente en `paper/sections/*.tex`
- **THEN** solo quedan ocurrencias dentro de entornos literales o de `\path{}`
- **AND** los pasajes de `01-introduccion.tex`, `07-resultados.tex` y `08-discusion.tex` que en `v1.5.2` las escribian sin tilde en prosa usan `\sectorprosa` o, si citan la taxonomia del sistema, `\sectorcad`

#### Scenario: Cadena del sistema en monoespaciado

- **WHEN** se lee un pasaje que cita la cadena exacta del clasificador
- **THEN** la cadena se produce con `\sectorcad` y el PDF la muestra en monoespaciado, byte a byte igual a una de las cinco cadenas de `constants.py`
- **AND** `rg -n "\\\\texttt\{(Seguridad|Soporte|Bases de Datos|Sistemas)" "docs/Tesis/v10 (IA)/paper/sections"` no devuelve coincidencias

### Requirement: Anexo de números canónicos citados y cuerpo sin referencias internas al memo

`docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex` SHALL incorporar un anexo (rotulado «Anexo» en español, con etiqueta `sec:anexo-numeros-canonicos`) que reúna los números canónicos que el cuerpo cita, y solo ellos, ubicado de modo que no renumere los anexos A a I existentes. Cada valor SHALL llevar su cifra y su procedencia verificable: el artefacto versionado que lo contiene, su clave y el comando que lo reproduce, o la remisión a la tabla de la tesis que lo muestra. El anexo MUST NOT incluir una columna ni un rótulo de estado (por ejemplo «vigente», «vigente (nuevo)», «condicional»), MUST NOT mencionar el memo de números canónicos ni sus secciones, y MUST NOT usar un archivo fuente de la tesis como procedencia (devolución de tercera instancia del 16-11-2026, M-03); cuando un valor sea una lectura de sensibilidad, esa calificación SHALL figurar en el texto del valor con el vocabulario de rótulos del capítulo de resultados. El anexo MUST NOT introducir valores ausentes de `docs/Tesis/Correcciones/numeros-canonicos.md` y MUST NOT modificar ningún valor canónico; el memo SHALL conservarse como fuente interna de verdad del proyecto. Las referencias del cuerpo al memo por número de sección (`Sección 3.xx`) SHALL reemplazarse por una remisión al anexo (`\autoref{sec:anexo-numeros-canonicos}`); ningún capítulo del cuerpo SHALL citar el memo por número de sección. Cada tabla del anexo SHALL tener `\caption` y `\label`, columnas `>{\raggedright\arraybackslash}p{}` y claves y rutas partibles con `\path{}` (no `\texttt{}` con guiones bajos escapados ni rutas elididas con puntos suspensivos), con la ruta completa del artefacto y del comando una sola vez en el párrafo que precede a la tabla (devolución de tercera instancia, B-03). Una compilación de verificación SHALL registrar 0 `Overfull \hbox` originados en el anexo. El crecimiento de páginas del anexo SHALL registrarse en el libro mayor de `dictamen-correcciones.md`.

#### Scenario: Anexo con los números citados

- **WHEN** se compila y se lee el Anexo de números canónicos
- **THEN** figuran los valores que el cuerpo cita
- **AND** ningún otro valor del memo se reproduce

#### Scenario: Procedencia sin estado ni memo

- **WHEN** se recorre el anexo
- **THEN** cada valor declara un artefacto versionado con su clave y su comando, o una remisión a una tabla de la tesis
- **AND** `rg -n -i "memo|\(nuevo\)|\(sin cambio\)"` sobre el rango de `sec:anexo-numeros-canonicos` no devuelve coincidencias
- **AND** ninguna tabla del anexo tiene una columna «Estado» ni una celda cuyo unico contenido sea un estado

#### Scenario: Cuerpo sin referencias internas por sección

- **WHEN** se busca `Sección[~ ]3\.[0-9]{2}` en `docs/Tesis/v10 (IA)/paper/sections/*.tex`
- **THEN** no quedan coincidencias en los capítulos del cuerpo
- **AND** cada oración que citaba el memo por sección remite a `\autoref{sec:anexo-numeros-canonicos}`

#### Scenario: Formato sin desbordes

- **WHEN** se compila el documento en un directorio temporal y se inspecciona `main.log`
- **THEN** no hay `Overfull \hbox` cuyo rango de líneas de entrada caiga en `sec:anexo-numeros-canonicos`
- **AND** el total de `Overfull \hbox` del documento es menor que 25 y queda registrado
- **AND** en el PDF ninguna clave se superpone con la columna vecina ni hay rutas con letras separadas por espacios

#### Scenario: Sin cifras nuevas ni valores cambiados

- **WHEN** se comparan los valores del anexo con el memo
- **THEN** cada cifra del anexo existe en el memo con el mismo valor
- **AND** ningún valor canónico cambia

### Requirement: Cuerpo sin identificadores de cambio y con oraciones acotadas

El cuerpo SHALL quedar sin identificadores de cambio y con oraciones acotadas. Las fuentes `.tex` del cuerpo, sus tablas y sus epigrafes, fuera del Anexo I (`sec:anexo-trazabilidad`), MUST NOT contener identificadores internos de cambio (`c-NNN`, `C-NN`, `C-63a` y similares) ni la palabra "changes"; SHALL reemplazarlos por la descripcion de lo que el cambio hizo o por una remision unica a `\autoref{sec:anexo-trazabilidad}` (devolucion del 11-11-2026, N-07). Los comentarios LaTeX (`%`) no cuentan. El contenido rasterizado de las figuras queda fuera de este requisito, salvo en las figuras que el change regenera. Este requisito prevalece sobre los requisitos anteriores que pedian nombrar un change en el cuerpo, una tabla o un epigrafe fuera del Anexo I. Ningun archivo de `paper/sections/*.tex` SHALL contener oraciones de mas de 60 palabras segun `docs/Tesis/Correcciones/sent_c197.py`, con la unica excepcion declarada de `00-portada.tex` (bloque de titulo, no prosa) (devolucion del 16-11-2026, M-03). Ademas, la revision manual con `docs/Tesis/Correcciones/list_long_c197.py <sections> 60`, que incluye pies de tabla, notas, epigrafes, vinetas y notas al pie, SHALL dejar solo filas de datos de tabla (lineas con `&`); toda nota, epigrafe, `\item` o `\footnote` de mas de 60 palabras SHALL partirse. La diferencia entre este metodo y el conteo del tribunal SHALL quedar documentada en el registro. Partir una oracion MUST NOT cambiar cifras, citas ni remisiones y MUST NOT borrar contenido sustantivo.

#### Scenario: Sin identificadores fuera del Anexo I

- **WHEN** se ejecuta `rg -n -E "\b[cC]-[0-9]{2,3}[ab]?\b"` sobre `paper/sections/*.tex`, excluyendo comentarios y el rango del Anexo I
- **THEN** no hay coincidencias

#### Scenario: Oraciones acotadas en todo el documento

- **WHEN** se ejecuta `python sent_c197.py "docs/Tesis/v10 (IA)/paper/sections"` con `PYTHONDONTWRITEBYTECODE=1`
- **THEN** informa 0 oraciones de mas de 60 palabras en todos los archivos salvo `00-portada.tex`

#### Scenario: Pies, notas y vinetas revisados

- **WHEN** se ejecuta `python list_long_c197.py "docs/Tesis/v10 (IA)/paper/sections" 60`
- **THEN** cada linea listada es una fila de datos de tabla o el bloque de la portada
- **AND** el registro consigna la linea base de ambos scripts, el resultado y la diferencia de metodo con el conteo del tribunal

### Requirement: Analisis de sensibilidad frente al ajuste del clasificador con el corpus en resultados

El documento SHALL incluir la subseccion `subsec:sensibilidad-ajustes`, ubicada en el anexo de lecturas de sensibilidad y robustez (`sec:anexo-sensibilidad`, en `12-anexos.tex`) con remision desde el capitulo de resultados (`07-resultados.tex`), que: enuncia el metodo (re-medicion de la etapa deterministica sin invocar al modelo con el vocabulario previo a su ampliacion con el corpus, conservando la logica de decision y el punto de operacion evaluados, y referencia con la logica de entonces junto con el resultado de su control de fidelidad); declara no factible la reconstruccion del vocabulario por pliegues y su motivo; presenta una tabla compacta `tab:sensibilidad-ajustes` con la configuracion evaluada y las variantes (casos resueltos por la etapa y exactitud con su IC de Wilson al 95 %, y la exactitud global con Gemini fijo solo si es computable); informa el efecto de las reglas de frontera del prompt con el mayor nivel de evidencia disponible o declara que no se cuantifico; y lee los resultados segun las reglas pre-registradas en el diseno del change. Las etiquetas `subsec:sensibilidad-ajustes` y `tab:sensibilidad-ajustes` SHALL conservarse para que las remisiones existentes resuelvan. El capitulo de resultados SHALL conservar la salvedad de estimacion dentro de la muestra con remision a `subsec:sensibilidad-ajustes`. Todo valor citado SHALL coincidir con el memo de numeros canonicos. La subseccion MUST NOT afirmar la ausencia de sesgo, MUST NOT presentar metricas obtenidas sobre el corpus como estimaciones fuera de la muestra y MUST NOT modificar ningun valor canonico.

#### Scenario: Subseccion y tabla presentes

- **WHEN** se compila el documento y se lee el anexo de lecturas de sensibilidad y robustez
- **THEN** existe `subsec:sensibilidad-ajustes` con la tabla `tab:sensibilidad-ajustes`, que incluye la configuracion evaluada (131 casos, 0,7405 con su IC) y las variantes con casos, exactitud e IC
- **AND** las referencias a ambos rotulos resuelven sin advertencias
- **AND** el capitulo de resultados remite a `subsec:sensibilidad-ajustes`

#### Scenario: Valores trazables al memo

- **WHEN** se coteja cada valor de la subseccion con `docs/Tesis/Correcciones/numeros-canonicos.md`
- **THEN** cada valor figura en la seccion de sensibilidad del memo con su procedencia

#### Scenario: Lectura de una exactitud menor como cota pesimista

- **WHEN** la exactitud de la variante principal es menor que 0,7405
- **THEN** la diferencia se presenta como cota pesimista del sesgo atribuible al vocabulario, con la razon por la que lo es
- **AND** no se la presenta como estimacion puntual del sesgo

#### Scenario: Lectura de una exactitud no menor

- **WHEN** la exactitud de la variante principal no es menor que 0,7405
- **THEN** se declara que el analisis no detecta un sesgo atribuible al vocabulario, sin descartarlo, por la diferencia entre los conjuntos de casos comparados

#### Scenario: Efecto del prompt informado o declarado

- **WHEN** se lee la subseccion
- **THEN** el efecto de las reglas de frontera sobre los 69 casos de la etapa Gemini figura con su nivel de evidencia y su contraste pareado, o se declara no cuantificado

### Requirement: Remisiones internas exactas de la vision general, del analisis de sensibilidad y del anexo de documentacion operativa

La vision general de la arquitectura (`05-arquitectura.tex`, `subsec:vision-general`) SHALL remitir a los resultados mediante `\autoref{sec:resultados}` y MUST NOT citar un numero de capitulo fijo; su remision a la prueba de humo SHALL apuntar a la seccion que la describe (`subsec:pruebas-automatizadas`), al anexo de documentacion operativa (`sec:anexo-documentacion-operativa`) y al anexo del despliegue (`sec:anexo-diagrama-arquitectura`), y MUST NOT remitir al anexo del repositorio (`sec:anexo-repositorio`), que no la documenta. El anexo de documentacion operativa SHALL nombrar el runbook de la prueba de humo y de la verificacion del borde TLS (`docs/runbook-smoke-stack-referencia.md`). La subseccion de sensibilidad (`subsec:sensibilidad-ajustes`, ubicada en el anexo de lecturas de sensibilidad y robustez de `12-anexos.tex`) SHALL citar para el nivel a (48 de 66) la linea de `evaluation/report_sensibilidad_ajustes.md` que lo contiene.

#### Scenario: Vision general sin numero de capitulo ni anexo equivocado

- **WHEN** se lee `subsec:vision-general` en las fuentes
- **THEN** no aparecen "Capítulo 7" ni la remision de la prueba de humo al Anexo B
- **AND** la remision usa `\autoref{sec:resultados}`, `subsec:pruebas-automatizadas` y los Anexos A y G

#### Scenario: Runbook de humo nombrado en el Anexo G

- **WHEN** se lee `sec:anexo-documentacion-operativa`
- **THEN** nombra `docs/runbook-smoke-stack-referencia.md`
- **AND** ese archivo existe en el repositorio

#### Scenario: Linea del reporte verificable

- **WHEN** se lee la linea citada para el nivel a en `subsec:sensibilidad-ajustes` y se ejecuta `sed -n '<linea>p' evaluation/report_sensibilidad_ajustes.md`
- **THEN** la linea obtenida contiene "sin los motivadores 48/66"

## REMOVED Requirements

### Requirement: Nomenclatura canonica de los sectores en la prosa del documento

**Reason**: Contradice el requisito "Coherencia de los nombres de sector con su definicion canonica" y origino la observacion B-01 de la devolucion de tercera instancia (16-11-2026): mandaba escribir sin tilde y en la fuente del cuerpo los pasajes de prosa que "citan el sistema", lo que dejo nombres sin tilde en la prosa mezclados con formas acentuadas. El tribunal exige monoespaciado para la cadena del sistema y forma con tilde en la prosa.

**Migration**: La regla unica vive en "Coherencia de los nombres de sector con su definicion canonica" (modificado por este change): `\sectorcad{<clave>}` para la cadena del sistema y `\sectorprosa{<clave>}` para la prosa. Los pasajes `01-introduccion.tex:48`, `01-introduccion.tex:72`, `07-resultados.tex:347` y `08-discusion.tex:26` (lineas de `v1.5.2`) se migran a la macro que corresponda.
