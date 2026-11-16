## MODIFIED Requirements

### Requirement: Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas

El capitulo de discusion (`08-discusion.tex`) SHALL incluir una subseccion con rotulo `subsec:balance-neto` que compute el balance neto trimestral entre el ahorro de tiempo de registro, el tiempo de revision humana que el flujo automatizado agrega y el costo de las derivaciones erroneas adicionales del clasificador respecto del flujo manual. La subseccion SHALL enunciar de forma explicita las formulas del balance neto, `B = (N / 3.600) x [Delta t - rho x r - (e_aut - e_man) x c]`, y de la exactitud minima de equilibrio, `a* = 1 - e_man - (Delta t - rho x r) / c`. SHALL declarar la procedencia de cada insumo: universo trimestral `N ~ 2.646`; ahorro medio por incidente `Delta t = 43,82 s` (43,8 s en el texto); proporcion de casos revisados `rho = 147/200` y tiempo medio por revision `r = 22,06 s` (seccion 3.31 (h) del memo); tasas de error del clasificador y del brazo manual medidas contra la referencia comun de la seccion 3.21 (`e_aut = 28/138 = 0,2029`; `e_man = 26/151 = 0,1722`); y costo por derivacion erronea `c = 69,51 s`, IC 95 % `[33,42; 106,56] s`, de la seccion 3.31. La subseccion SHALL declarar que `c` cubre solo el tramo activo (correccion en la compuerta y re-decision de sector como proxy del rediagnostico) y es por lo tanto una cota inferior del costo. Como la compuerta no detecta errores en la configuracion evaluada, el error llega al sector receptor y el tramo de reanudacion queda sin cota. Por eso `B` SHALL presentarse como cota superior del balance. La subseccion SHALL incluir una tabla con rotulo `tab:balance-neto` con la lectura central (cota superior con el `c` medido) y la sensibilidad al tramo no medido (rejilla de 5, 10 y 15 minutos con la referencia comun y el termino de revision), cada una con exactitud minima de equilibrio y balance neto. La subseccion SHALL informar el costo de equilibrio `c*` y el margen del tramo no medido. SHALL contrastar la exactitud minima de equilibrio con la exactitud estricta observada y su intervalo de Wilson. SHALL informar los intervalos de `B` con el metodo de propagacion declarado. MUST NOT enunciar que el signo del balance queda fijado por la muestra: el signo depende del tramo de reanudacion no medido. La rejilla de 5, 10 y 15 minutos MUST NOT rotularse como «supuesto superado». La subseccion MUST NOT incluir cifras de balance calculadas sobre el corpus fuera de muestra. Todo valor de la subseccion y de la tabla MUST coincidir con el registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`. La misma lectura del balance SHALL aparecer en `00-resumen.tex`, `01-introduccion.tex`, `04-marco-metodologico.tex`, `09-conclusiones.tex`, `10-recomendaciones.tex` y `12-anexos.tex`, tablas incluidas.

#### Scenario: Formulas e insumos explicitos

- **WHEN** se lee la subseccion `subsec:balance-neto`
- **THEN** figuran las formulas del balance neto y de la exactitud minima de equilibrio con la definicion de `N`, `Delta t`, `rho`, `r`, `e_aut`, `e_man` y `c`
- **AND** cada insumo remite a su origen en el documento o a la seccion del memo canonico que lo mide

#### Scenario: Termino de revision incluido

- **WHEN** se lee la lectura central del balance
- **THEN** el balance descuenta `rho x r` por incidente, con `rho = 147/200` y `r = 22,06 s`
- **AND** el valor central es aproximadamente `+18,7` horas-persona por trimestre y la exactitud minima de equilibrio aproximadamente `43,1 %`

#### Scenario: Costo como cota inferior y balance como cota superior

- **WHEN** se lee la definicion de `c` y la lectura del balance
- **THEN** `c = 69,51 s` se presenta como el tramo activo medido y cota inferior del costo, y el tramo de reanudacion como no medido y sin cota
- **AND** el balance central se presenta como cota superior, con la expresion «a lo sumo» o «cota superior»

#### Scenario: Sensibilidad al tramo no medido

- **WHEN** se leen el texto y `tab:balance-neto`
- **THEN** la rejilla de 5, 10 y 15 minutos con revision y referencia comun figura rotulada como sensibilidad al tramo no medido, con sus intervalos
- **AND** el texto informa el costo de equilibrio `c*` y el margen de tiempo del tramo de reanudacion que anularia el balance

#### Scenario: Signo no declarado fijado

- **WHEN** se buscan en `08-discusion.tex` las expresiones «signo queda así fijado», «queda fijado por la muestra» o «de modo que el signo queda fijado»
- **THEN** no aparecen
- **AND** el texto declara que el signo del balance depende del tramo de reanudacion no medido

#### Scenario: Incertidumbre declarada

- **WHEN** se contrasta el balance con cero
- **THEN** el texto informa el intervalo condicional y la cota combinada con su metodo, y declara que la cota combinada cubre solo el tramo activo medido
- **AND** no presenta la cota combinada como intervalo del balance real

#### Scenario: Sensibilidad mixta no promovida

- **WHEN** se busca en `subsec:balance-neto` una sensibilidad calculada con la tasa de error fuera de muestra
- **THEN** no figura
- **AND** los insumos del balance provienen del corpus de 200 casos y de la campana complementaria

#### Scenario: Lectura unica del balance

- **WHEN** se compara la calificacion del balance en `00-resumen.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `12-anexos.tex`
- **THEN** los cuatro usan la misma cifra central, la misma condicion de cota superior y la misma lectura condicional
- **AND** ninguno conserva `+30,6` como lectura central del balance

#### Scenario: Remisiones resueltas

- **WHEN** se compila el documento con XeLaTeX tras modificar la subseccion y la tabla
- **THEN** las remisiones a `subsec:balance-neto` y `tab:balance-neto` resuelven sin referencias indefinidas
- **AND** ambos rotulos son unicos en el documento

#### Scenario: Lectura central con el costo medido

- **WHEN** se leen el texto y `tab:balance-neto`
- **THEN** el escenario con `c = 69,51 s` y su intervalo `[33,42; 106,56] s` figura como lectura central
- **AND** el balance y la exactitud minima de equilibrio se informan con su intervalo

#### Scenario: Grilla previa rotulada como superada

- **WHEN** se busca «10 a 15 minutos» o «supuesto superado» como insumo o rotulo del balance
- **THEN** la subseccion no rotula la rejilla como «supuesto superado»
- **AND** la rejilla de 5, 10 y 15 minutos figura como sensibilidad al tramo no medido, con sus cifras conservadas

#### Scenario: Calculo con los supuestos del propio documento

- **WHEN** se aplican las formulas con la grilla de 5, 10 y 15 minutos y el termino de revision
- **THEN** el texto conserva las cifras de esa sensibilidad rotuladas como sensibilidad al tramo no medido
- **AND** no las rotula como «supuesto superado» ni como lectura vigente

#### Scenario: Tabla de escenarios con el punto de equilibrio

- **WHEN** se lee la tabla `tab:balance-neto`
- **THEN** contiene el escenario con el `c` medido como lectura central (cota superior) y, como sensibilidad al tramo no medido, las filas de la rejilla de 5, 10 y 15 minutos con el termino de revision
- **AND** cada celda coincide con el valor del memo canonico bajo la convencion de redondeo declarada en la nota de la tabla

#### Scenario: Incertidumbre muestral considerada

- **WHEN** se contrasta la exactitud minima de equilibrio con la exactitud estricta observada
- **THEN** el texto compara la exactitud minima de equilibrio del escenario medido con el intervalo de Wilson observado
- **AND** declara que el signo del balance depende del tramo de reanudacion no medido y no queda fijado por la muestra

#### Scenario: Exactitud laxa sin cifras inventadas

- **WHEN** la exactitud laxa esta registrada en el memo canonico al momento de aplicar el cambio
- **THEN** la subseccion la compara con la exactitud minima de equilibrio e informa los escenarios en que el balance resulta positivo bajo esa lectura
- **AND** si no esta registrada, la subseccion no presenta ningun valor de exactitud laxa y declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador

#### Scenario: Incertidumbre y signo

- **WHEN** se contrasta el intervalo de `B` con cero
- **THEN** el texto informa el intervalo con el metodo de propagacion declarado
- **AND** declara que el signo depende del tramo de reanudacion no medido

### Requirement: Viabilidad operativa presentada como condicional

El resumen (en espanol y en ingles), la justificacion de la introduccion, la discusion y las conclusiones SHALL presentar la viabilidad tecnica como sostenida por la evidencia y la economica como sostenida en el sentido del costo monetario de operacion, que es marginal. La viabilidad operativa SHALL presentarse como condicional: el balance neto, con el termino de revision incluido y con el costo de derivacion como cota inferior, es a lo sumo la cota superior registrada en el memo, y su signo depende del tramo de reanudacion no medido. El documento MUST NOT afirmar que la viabilidad operativa es positiva, ni la «viabilidad economica y operativa positiva», ni que el signo del balance queda fijado por la muestra. MUST NOT afirmar la viabilidad "tecnica, economica y operativa" (ni la "technical, economic, and operational feasibility") como bloque incondicional. La fila del objetivo general en `tab:cumplimiento-objetivos` SHALL calificar la viabilidad operativa como condicional, con remision a `subsec:balance-neto`. El ahorro de 32,2 horas-persona por trimestre SHALL presentarse como ahorro bruto de registro, sin cambiar su valor. El parrafo de conclusion del resumen en espanol SHALL tener a lo sumo 34 palabras y el del abstract a lo sumo 31; cada resumen MUST NOT superar 250 palabras.

#### Scenario: Resumen y abstract con viabilidad operativa condicional

- **WHEN** se leen los parrafos de conclusion del resumen y del abstract en `00-resumen.tex`
- **THEN** la viabilidad operativa se presenta como condicional y el balance como cota superior («a lo sumo», "at most"), con el termino de revision incluido
- **AND** el parrafo en espanol tiene a lo sumo 34 palabras, el parrafo en ingles a lo sumo 31 y ningun resumen supera 250 palabras

#### Scenario: Conclusiones con los tres planos de viabilidad

- **WHEN** se lee el parrafo inicial de `09-conclusiones.tex` y la fila del objetivo general de `tab:cumplimiento-objetivos`
- **THEN** el sistema se declara tecnicamente viable y de costo monetario marginal, y su viabilidad operativa condicional al tramo de reanudacion no medido, con remision a `subsec:balance-neto`
- **AND** no aparecen «viabilidad economica y operativa resulta positiva» ni «viabilidad operativa positiva»

#### Scenario: Justificacion sin mejora neta cuantificada

- **WHEN** se lee la dimension organizacional de la justificacion y el planteamiento del problema en `01-introduccion.tex`
- **THEN** la evidencia se presenta como cuantificacion del ahorro bruto de registro y de la cota superior del balance, y el saldo neto se declara condicional al tramo de reanudacion no medido
- **AND** no se afirma como cuantificada una mejora neta ni una reduccion del tiempo de respuesta percibido por los usuarios

#### Scenario: Ahorro de 32,2 horas-persona calificado como bruto

- **WHEN** se lee cualquier mencion de las 32,2 horas-persona por trimestre en la introduccion, la discusion o las conclusiones
- **THEN** la mencion la califica como ahorro bruto o remite al balance neto de `subsec:balance-neto`
- **AND** el valor 32,2 y su calculo (`43,8 s x 2.646 / 3.600`) se conservan sin cambios

#### Scenario: Composicion del costo economico coherente con la discusion

- **WHEN** se lee en las conclusiones la descripcion del costo monetario de operacion del sistema
- **THEN** la descripcion es coherente con las cifras de la discusion (infraestructura de 24 a 32 USD por mes frente a inferencia del orden de 1 USD por trimestre)
- **AND** no se afirma que el costo de operacion este dominado por el consumo de la API de inferencia

### Requirement: Registro canonico del balance neto y sus supuestos

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, en la seccion del balance neto y en las secciones aditivas que la suceden, los insumos, las formulas y los valores de la tabla del balance neto, cada uno con su procedencia (archivo y linea de origen, o recalculo con formula explicita) y su estado. El balance con el termino de revision y el costo medido como cota inferior SHALL registrarse con estado `vigente` como cota superior y con sus limites declarados. La rejilla de 5, 10 y 15 minutos con revision SHALL registrarse con estado `condicional`, como sensibilidad al tramo no medido. La lectura central previa sin termino de revision (`+30,6`) SHALL declararse retirada en la seccion nueva, sin editar la seccion que la registro. Las secciones SHALL incluir un comando de recalculo reproducible y declarar la convencion de redondeo. El registro MUST NOT modificar ningun valor canonico existente.

#### Scenario: Insumos con procedencia y estado

- **WHEN** se lee la seccion vigente del balance neto en el memo canonico
- **THEN** cada insumo declara valor, procedencia y estado: `vigente` para el universo, el ahorro medio, las tasas medidas, el termino de revision y el costo medido como cota inferior; `condicional` para la rejilla de sensibilidad al tramo no medido
- **AND** cada linea de origen citada existe en el archivo referenciado

#### Scenario: Valores reproducibles

- **WHEN** se ejecuta el comando de recalculo de la seccion
- **THEN** reproduce la exactitud minima de equilibrio y el balance neto de la lectura central y de cada celda de la rejilla
- **AND** la convencion de redondeo y el metodo de propagacion quedan declarados

#### Scenario: Valores canonicos existentes intactos

- **WHEN** se comparan las secciones previas del memo antes y despues del cambio
- **THEN** ningun valor existente cambia de cifra ni de estado
- **AND** solo se agregan la seccion nueva y las lineas de remision

### Requirement: Linea futura de medicion de la exactitud manual y del costo de reasignacion

El capitulo de recomendaciones SHALL incluir, en `subsec:estudios-replicacion`, la recomendacion de que toda replicacion registre por caso la derivacion efectuada en el brazo manual, con etiquetadores distintos de los operadores, y cronometre cada reasignacion. Ese cronometraje incluye el tiempo que el sector receptor tarda en advertir el error y devolver el ticket. La medicion de la exactitud manual SHALL presentarse como ya aplicada en la campana de medicion, con remision a resultados. El cronometraje del tramo de reanudacion SHALL presentarse como la medicion que falta para fijar el signo del balance neto, porque el `c` medido cubre solo el tramo activo y es una cota inferior. MUST NOT presentarse como un mero refinamiento sin efecto sobre el signo. La subseccion `subsec:balance-neto` SHALL remitir a esa recomendacion, y el capitulo MUST NOT duplicarla en otra subseccion.

#### Scenario: Recomendacion presente y conectada

- **WHEN** se lee `subsec:estudios-replicacion`
- **THEN** recomienda registrar por caso la derivacion del brazo manual con etiquetadores distintos de los operadores y cronometrar las reasignaciones, incluido el tramo de reanudacion
- **AND** declara aplicada la medicion de la exactitud manual y remite a `subsec:balance-neto`, que a su vez remite a esta subseccion

#### Scenario: Balance no declarado bloqueado

- **WHEN** se lee la recomendacion sobre el cronometraje de reasignaciones
- **THEN** se presenta como la medicion que fijaria el signo del balance neto
- **AND** no aparece la afirmacion de que esa medicion «no es condicion para cerrarlo»

#### Scenario: Sin duplicacion en recomendaciones

- **WHEN** se recorre el capitulo de recomendaciones
- **THEN** la medicion de la exactitud del flujo manual se recomienda una sola vez
- **AND** no existe una subseccion adicional que repita esa recomendacion

### Requirement: Exactitud del brazo manual y balance neto según la campaña de medición

La tesis SHALL declarar que la exactitud del brazo manual de la campaña 2026-10 no
se midió, con sus dos razones: el corpus no registra por caso la derivación del
operador, y esos operadores son los mismos analistas que fijaron la referencia. Para
la campaña de medición, la tesis SHALL reportar la exactitud estricta y laxa del
brazo manual calculada por c-167 contra la referencia del consenso del doble
etiquetado nuevo (casos con coincidencia `E1 = E2`; los discordantes se informan
aparte), por operador (`O1`, `O2`) con intervalo de Wilson y agregada con intervalo
bootstrap por caso, junto con el contraste de McNemar entre el brazo manual y el
automatizado sobre los mismos casos, siempre que `evaluation/data/campana/registro_sujetos.csv`
no muestre solape entre los operadores y quienes produjeron la referencia. Si hay
solape, la tesis SHALL declarar la exactitud manual "no medida: operadores no
independientes" y MUST NOT cuantificarla. Con la exactitud medida, la tasa de
derivación errónea manual SHALL presentarse como `1 - exactitud estricta del brazo
manual` de la campaña de medición, con su intervalo, y la exactitud mínima de
equilibrio SHALL recalcularse con esa tasa, con el término de revisión y con el costo
por derivación errónea medido (`69,51 s`) declarado como cota inferior del tramo
activo. El balance neto SHALL declararse `condicional` al tramo de reanudación no
medido. El 15 % preliminar SHALL conservarse rotulado como estimación preliminar. El
documento MUST NOT enunciar el signo del balance neto como resultado salvo que el
balance quede íntegramente de un lado de cero en todo el rango de costos declarado,
incluido el tramo no medido; en ese caso SHALL declararlo con el rango de costos que
lo sostiene.

#### Scenario: Declaracion en la discusion

- **WHEN** la exactitud manual de la campaña de medición fue medida y se leen `subsec:balance-neto` y la limitación sobre etiquetadores y operadores de `subsec:limitaciones-estudio`
- **THEN** se declara que la campaña 2026-10 no midió la exactitud manual y que la campaña de medición la midió con operadores independientes de la referencia, con su valor e intervalo
- **AND** la exactitud mínima de equilibrio se informa con la tasa manual medida y el término de revisión, y el balance neto se declara condicional al tramo de reanudación no medido

#### Scenario: Exactitud manual no medida por falta de independencia

- **WHEN** `registro_sujetos.csv` muestra solape entre los operadores y los productores de la referencia
- **THEN** la tesis declara la exactitud manual "no medida: operadores no independientes"
- **AND** el balance neto se declara indeterminado con el diseño de ambas campañas y se conserva el 15 % preliminar como único valor atribuido al flujo manual

#### Scenario: Declaracion en el planteamiento del problema

- **WHEN** se lee el planteamiento del problema en `01-introduccion.tex`
- **THEN** la tasa de derivación errónea del 15 % se califica como estimación preliminar, de la misma naturaleza que los 2 minutos 45 segundos
- **AND** el párrafo remite a `subsec:balance-neto` y declara el saldo neto condicional al tramo de reanudación no medido, no a la tasa a priori

#### Scenario: Sin tasa manual presentada como medida

- **WHEN** se recorren las secciones de la tesis en busca de una exactitud o tasa de derivación errónea del flujo manual
- **THEN** solo se presenta como medida la de la campaña de medición, rotulada con su campaña, sus operadores y su referencia
- **AND** ningún pasaje atribuye una exactitud manual medida a la campaña 2026-10 ni afirma un signo del balance neto que no quede fijado en todo el rango de costos

### Requirement: Fuente del criterio del umbral del 85 por ciento

La justificacion del umbral de exactitud del 85~\% en el segundo objetivo especifico (`01-introduccion.tex`) SHALL declarar que el umbral es un criterio fijado a priori por los autores. Solo SHALL apoyarse en argumentos disponibles antes de las mediciones: la referencia de la literatura sin piso numerico comun; la estimacion propia de los autores (10 a 15 minutos por reasignacion y tasa preliminar del 15 %), declarada como estimacion sin registro cuantitativo; y el margen para el intervalo de confianza. Cada argumento SHALL declarar su fuente. La justificacion MUST NOT apoyarse en el costo de derivacion medido, en la paridad con la exactitud manual medida (82,78 %), en el costo marginal por punto de exactitud ni en la exactitud minima de equilibrio. MUST NOT afirmar que una exactitud inferior al 85 % resultaria en tiempos de resolucion comparables a los del flujo manual. Esas mediciones SHALL presentarse en `subsec:balance-neto` rotuladas como lecturas posteriores que no fundamentan el umbral. La discusion y el anexo de numeros canonicos SHALL usar la misma lectura: la equivalencia con la paridad del 15 % es la estimacion a priori, y la paridad medida es una lectura posterior.

#### Scenario: Umbral declarado a priori

- **WHEN** se lee la justificacion del umbral del 85 % en `01-introduccion.tex`
- **THEN** el umbral se declara fijado a priori por los autores y cada argumento declara su fuente
- **AND** no aparecen `82,78`, «0,5 horas-persona», «70 s» ni «tiempos de resolución comparables» como fundamento del umbral

#### Scenario: Argumentos posteriores en la discusion

- **WHEN** se lee `subsec:balance-neto`
- **THEN** la paridad con la exactitud manual medida, el costo marginal por punto y la exactitud minima de equilibrio figuran rotulados como lecturas posteriores
- **AND** el texto declara que no fundamentan el umbral

#### Scenario: Lectura conciliada entre capitulos

- **WHEN** se comparan `01-introduccion.tex`, `08-discusion.tex` y las filas de paridad y costo marginal de `12-anexos.tex`
- **THEN** los tres presentan el 85 % como criterio a priori y la paridad medida como lectura posterior
- **AND** ninguno dice que la justificacion del umbral sea la paridad medida con la tasa manual

#### Scenario: Fuente declarada o reformulacion propia

- **WHEN** se lee la justificacion del umbral de exactitud del 85~\% en el capitulo de introduccion
- **THEN** cada uno de los criterios convergentes declara su fuente
- **AND** la estimacion propia de los autores (10 a 15 minutos por reasignacion y la tasa preliminar del 15 %) se declara como estimacion sin registro cuantitativo
- **AND** no queda ningun argumento presentado como respaldo sin fuente
