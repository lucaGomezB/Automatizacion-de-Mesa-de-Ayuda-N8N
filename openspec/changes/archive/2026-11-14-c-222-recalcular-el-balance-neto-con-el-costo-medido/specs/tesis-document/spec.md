## MODIFIED Requirements

### Requirement: Balance neto entre el ahorro de registro y el costo de las derivaciones erroneas

El capitulo de discusion (`08-discusion.tex`) SHALL incluir una subseccion con rotulo `subsec:balance-neto` que compute el balance neto trimestral entre el ahorro de tiempo de registro y el costo de las derivaciones erroneas adicionales del clasificador respecto del flujo manual. La subseccion SHALL enunciar de forma explicita las formulas del balance neto, `B = (N / 3.600) x [Delta t - (e_aut - e_man) x c]`, y de la exactitud minima de equilibrio, `a* = 1 - e_man - Delta t / c`, junto con la procedencia de cada insumo: universo trimestral `N ~ 2.646`, ahorro medio por incidente `Delta t = 43,82 s` (43,8 s en el texto), tasas de error del clasificador y del brazo manual medidas contra la referencia comun de la seccion 3.21 del memo (`e_aut = 28/138 = 0,2029`; `e_man = 26/151 = 0,1722`) y costo por derivacion erronea `c = 69,51 s`, IC 95 % `[33,42; 106,56] s`, de la seccion 3.31 (c-220). La subseccion SHALL incluir una tabla con rotulo `tab:balance-neto` que, para el `c` medido y para la rejilla historica de 5, 10 y 15 minutos, reporte la exactitud minima de equilibrio y el balance neto, y SHALL contrastar la exactitud minima de equilibrio con la exactitud estricta observada y su intervalo de Wilson. La fila o columna del `c` medido SHALL identificarse como lectura central; la rejilla de 5, 10 y 15 minutos SHALL rotularse como sensibilidad del supuesto superado y MUST NOT presentarse como insumo vigente. La subseccion SHALL informar el intervalo de `B` con el metodo de propagacion declarado y MUST NOT enunciar el signo si el intervalo no lo fija. La sensibilidad mixta de c-221 SHALL conservarse rotulada como sensibilidad y MUST NOT reemplazar el balance con referencia comun. Todo valor de la subseccion y de la tabla MUST coincidir con el registrado en `docs/Tesis/Correcciones/numeros-canonicos.md`. La misma lectura del balance SHALL aparecer en `00-resumen.tex`, `09-conclusiones.tex` y `12-anexos.tex`, tablas incluidas.

#### Scenario: Formulas e insumos explicitos

- **WHEN** se lee la subseccion `subsec:balance-neto`
- **THEN** figuran las formulas del balance neto y de la exactitud minima de equilibrio con la definicion de `N`, `Delta t`, `e_aut`, `e_man` y `c`
- **AND** cada insumo remite a su origen en el documento o a la seccion del memo canonico que lo mide

#### Scenario: Lectura central con el costo medido

- **WHEN** se leen el texto y `tab:balance-neto`
- **THEN** el escenario con `c = 69,51 s` y su intervalo `[33,42; 106,56] s` figura como lectura central
- **AND** el balance y la exactitud minima de equilibrio se informan con su intervalo

#### Scenario: Grilla previa rotulada como superada

- **WHEN** se busca «10 a 15 minutos» como insumo del balance
- **THEN** la subseccion declara que ese supuesto fue reemplazado por el `c` medido
- **AND** la rejilla de 5, 10 y 15 minutos figura rotulada como sensibilidad del supuesto superado, con sus cifras conservadas

#### Scenario: Calculo con los supuestos del propio documento

- **WHEN** se aplican las formulas con la grilla superada de 15 % manual y 10 y 15 minutos
- **THEN** el texto informa del orden de 304 derivaciones erroneas adicionales por trimestre, un costo de 50,7 y 76,1 horas-persona y un balance neto de -18,5 y -43,9 horas-persona
- **AND** rotula esos valores como sensibilidad del supuesto superado y no como lectura vigente

#### Scenario: Tabla de escenarios con el punto de equilibrio

- **WHEN** se lee la tabla `tab:balance-neto`
- **THEN** contiene el escenario con el `c` medido como lectura central y, como sensibilidad superada, una fila por tasa manual (10 %, 15 %, 20 % y 26,5 %) y costos de 5, 10 y 15 minutos
- **AND** cada celda coincide con el valor del memo canonico bajo la convencion de redondeo declarada en la nota de la tabla

#### Scenario: Incertidumbre muestral considerada

- **WHEN** se contrasta la exactitud minima de equilibrio con la exactitud estricta observada
- **THEN** el texto compara la exactitud minima de equilibrio del escenario medido con el intervalo de Wilson observado y declara el signo solo si el intervalo de `B` lo fija
- **AND** para la grilla superada declara que, con una tasa manual del 15 % y 10 minutos por reasignacion, el signo del balance no queda determinado por la muestra

#### Scenario: Exactitud laxa sin cifras inventadas

- **WHEN** la exactitud laxa esta registrada en el memo canonico al momento de aplicar el cambio
- **THEN** la subseccion la compara con la exactitud minima de equilibrio e informa los escenarios en que el balance resulta positivo bajo esa lectura
- **AND** si no esta registrada, la subseccion no presenta ningun valor de exactitud laxa y declara que el 26,5 % es una cota superior de la tasa operativa de derivacion erronea atribuible al clasificador

#### Scenario: Incertidumbre y signo

- **WHEN** se contrasta el intervalo de `B` con cero
- **THEN** el texto enuncia el signo solo si el intervalo lo fija
- **AND** declara el metodo de propagacion y el limite que no se iguala

#### Scenario: Sensibilidad mixta no promovida

- **WHEN** se lee la sensibilidad de c-221 sobre la tasa fuera de muestra
- **THEN** figura rotulada como sensibilidad que mezcla corpus y referencias
- **AND** no reemplaza el balance con referencia comun

#### Scenario: Lectura unica del balance

- **WHEN** se compara la calificacion del balance en `00-resumen.tex`, `08-discusion.tex`, `09-conclusiones.tex` y `12-anexos.tex`
- **THEN** los cuatro usan la misma lectura y el mismo signo
- **AND** el conteo de palabras del resumen y del abstract no aumenta

#### Scenario: Remisiones resueltas

- **WHEN** se compila el documento con XeLaTeX tras incorporar la subseccion y la tabla
- **THEN** las remisiones a `subsec:balance-neto` y `tab:balance-neto` resuelven sin referencias indefinidas
- **AND** ambos rotulos son unicos en el documento

### Requirement: Registro canonico del balance neto y sus supuestos

El memo `docs/Tesis/Correcciones/numeros-canonicos.md` SHALL registrar, en la seccion del balance neto y en la seccion aditiva que la sucede, los insumos, las formulas y los valores de la tabla del balance neto, cada uno con su procedencia (archivo y linea de origen, o recalculo con formula explicita) y su estado. Los valores calculados con el costo medido y la tasa manual medida SHALL registrarse con estado `vigente` y con sus limites declarados. La rejilla historica de 5, 10 y 15 minutos SHALL registrarse como sensibilidad con estado `condicional` y con su condicion de reversibilidad, rotulada como superada por el costo medido. Las secciones SHALL incluir un comando de recalculo reproducible y declarar la convencion de redondeo. El registro MUST NOT modificar ningun valor canonico existente.

#### Scenario: Insumos con procedencia y estado

- **WHEN** se lee la seccion del balance neto en el memo canonico
- **THEN** cada insumo declara valor, procedencia y estado: `vigente` para el universo, el ahorro medio por incidente, las tasas medidas y el costo medido; `condicional` para la rejilla de sensibilidad superada
- **AND** cada linea de origen citada existe en el archivo referenciado

#### Scenario: Valores reproducibles

- **WHEN** se ejecuta el comando de recalculo de la seccion
- **THEN** reproduce la exactitud minima de equilibrio y el balance neto del escenario medido y de cada celda de la rejilla
- **AND** la convencion de redondeo y el metodo de propagacion quedan declarados

#### Scenario: Valores canonicos existentes intactos

- **WHEN** se comparan las secciones previas del memo antes y despues del cambio
- **THEN** ningun valor existente cambia de cifra ni de estado
- **AND** la cabecera del memo registra el agregado de la seccion nueva

### Requirement: Linea futura de medicion de la exactitud manual y del costo de reasignacion

El capitulo de recomendaciones SHALL incluir, en `subsec:estudios-replicacion`, la recomendacion de que toda replicacion registre por caso la derivacion efectuada en el brazo manual, con etiquetadores distintos de los operadores, y cronometre cada reasignacion. La medicion de la exactitud manual SHALL presentarse como ya aplicada en la campana de medicion, con remision a resultados. El cronometraje directo de las reasignaciones SHALL conservarse como refinamiento del tramo largo de `c` y MUST NOT presentarse como condicion para cerrar el balance neto, porque el balance ya usa el `c` compuesto medido de la seccion 3.31. La subseccion `subsec:balance-neto` SHALL remitir a esa recomendacion, y el capitulo MUST NOT duplicarla en otra subseccion.

#### Scenario: Recomendacion presente y conectada

- **WHEN** se lee `subsec:estudios-replicacion`
- **THEN** recomienda registrar por caso la derivacion del brazo manual con etiquetadores distintos de los operadores y cronometrar las reasignaciones
- **AND** declara aplicada la medicion de la exactitud manual y remite a `subsec:balance-neto`, que a su vez remite a esta subseccion

#### Scenario: Balance no declarado bloqueado

- **WHEN** se lee la recomendacion sobre el cronometraje de reasignaciones
- **THEN** se presenta como refinamiento del tramo largo y no como requisito para cerrar el balance
- **AND** el balance vigente no se declara pendiente de esa medicion

#### Scenario: Sin duplicacion en recomendaciones

- **WHEN** se recorre el capitulo de recomendaciones
- **THEN** la medicion de la exactitud del flujo manual se recomienda una sola vez
- **AND** no existe una subseccion adicional que repita esa recomendacion

### Requirement: Viabilidad operativa presentada como condicional

El resumen (en espanol y en ingles), la justificacion de la introduccion, la discusion y las conclusiones SHALL presentar la viabilidad tecnica y la economica como sostenidas por la evidencia y la viabilidad operativa como condicional a que la exactitud efectiva supere la exactitud minima de equilibrio, sea por mejora del clasificador o porque la revision humana del sector responsable reduzca la tasa o el costo efectivos de las derivaciones erroneas. Cuando la campana de medicion haya medido la exactitud manual y el costo por derivacion erronea, la condicion SHALL expresarse con la exactitud minima de equilibrio recalculada con ambos valores medidos y el balance neto SHALL informarse con su intervalo; la viabilidad operativa SHALL declararse con el signo y el rango que el intervalo sostenga y solo SHALL presentarse como condicional al costo si el intervalo incluye cero. El documento MUST NOT afirmar que los hallazgos confirman la viabilidad "tecnica, economica y operativa" (ni la "technical, economic, and operational feasibility") como bloque incondicional. El ahorro de 32,2 horas-persona por trimestre SHALL presentarse como ahorro bruto de registro, sin cambiar su valor. El parrafo de conclusion del resumen en espanol y del abstract MUST NOT aumentar su conteo de palabras respecto de la version previa.

#### Scenario: Resumen y abstract con viabilidad operativa condicional

- **WHEN** se leen los parrafos de conclusion del resumen y del abstract en `00-resumen.tex`
- **THEN** la viabilidad tecnica y economica se presentan como confirmadas y la operativa con el signo que el intervalo del balance sostenga, o como condicional si el intervalo incluye cero
- **AND** el parrafo en espanol tiene a lo sumo 34 palabras y el parrafo en ingles a lo sumo 31

#### Scenario: Conclusiones con los tres planos de viabilidad

- **WHEN** se lee el parrafo inicial de `09-conclusiones.tex`
- **THEN** el sistema se declara tecnicamente viable y economicamente accesible, y su viabilidad operativa se declara segun el intervalo del balance, con remision a `subsec:balance-neto`
- **AND** no queda una afirmacion de viabilidad incondicional del sistema en su conjunto

#### Scenario: Justificacion sin mejora neta cuantificada

- **WHEN** se lee la dimension organizacional de la justificacion en `01-introduccion.tex`
- **THEN** la evidencia del trabajo se presenta como cuantificacion del ahorro bruto de registro y del punto de equilibrio frente al costo de las derivaciones erroneas
- **AND** no se afirma como cuantificada una mejora neta ni una reduccion del tiempo de respuesta percibido por los usuarios

#### Scenario: Ahorro de 32,2 horas-persona calificado como bruto

- **WHEN** se lee cualquier mencion de las 32,2 horas-persona por trimestre en la introduccion, la discusion o las conclusiones
- **THEN** la mencion la califica como ahorro bruto o remite al balance neto de `subsec:balance-neto`
- **AND** el valor 32,2 y su calculo (`43,8 s x 2.646 / 3.600`) se conservan sin cambios

#### Scenario: Composicion del costo economico coherente con la discusion

- **WHEN** se lee en las conclusiones la descripcion del costo monetario de operacion del sistema
- **THEN** la descripcion es coherente con las cifras de la discusion (infraestructura de 24 a 32 USD por mes frente a inferencia del orden de 1 USD por trimestre)
- **AND** no se afirma que el costo de operacion este dominado por el consumo de la API de inferencia