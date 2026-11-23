## ADDED Requirements

### Requirement: Instrumento del flujo manual descrito como realmente quedo (OQ-01 de c-249)

El capitulo de metodo SHALL describir el instrumento del cronometraje manual tal como quedo segun
la respuesta registrada de los autores a OQ-01 de c-249, y MUST NOT describir como existente un
instrumento que los autores declararon inexistente (OQ-02 (5) de c-247). La primera amenaza a la
validez (`04-marco-metodologico.tex`, parrafo de la primera amenaza) SHALL incorporar la falta o la
parcialidad del registro primario de los 61,6 s. La fila del objetivo especifico 5 en la tabla de
cumplimiento y la oracion "para que una tercera parte pueda replicarlos" (`01-introduccion.tex`)
SHALL acotarse en consecuencia. El protocolo (`04:89`) SHALL decir que se busco y que campos se
completaron en "la busqueda y la carga del ticket", y la diferencia de constructo entre esa tarea
y el tiempo de extremo a extremo del sistema SHALL figurar como amenaza. La procedencia de la
premisa de 2 min 45 s y la ventana "junio a agosto" de los 119 casos SHALL declararse segun la
misma respuesta. Sin esa respuesta, las tareas quedan bloqueadas.

#### Scenario: Planilla no descrita como existente

- **WHEN** se lee el parrafo de instrumentos de `04-marco-metodologico.tex` (hoy `:97`)
- **THEN** el texto coincide con la respuesta OQ-01 de c-249 consignada en `dictamen-correcciones.md`
- **AND** si los autores declararon que no se conservo ningun registro primario, el texto lo dice y remite al campo `tiempo_manual_s` del corpus

#### Scenario: Falta de registro primario como amenaza

- **WHEN** se lee la primera amenaza a la validez (hoy `04:117`)
- **THEN** menciona la falta (o parcialidad) del registro primario del cronometraje manual

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-249 no contiene la respuesta OQ-01
- **THEN** las tareas gated por OQ-01 permanecen sin marcar y no se escribe prosa sobre el instrumento

### Requirement: Titularidad unica del regimen (a) y tensiones del repositorio explicadas (OQ-02 de c-249)

El documento SHALL usar una sola formula para los reportantes de los 119 incidentes del regimen
(a) en `04-marco-metodologico.tex` y en `11-aspectos-legales.tex` (hoy `04:46`, `11:16`, `11:40`,
`11:48`), la que confirmen los autores en OQ-02 de c-249. Si titulares y responsables del
tratamiento son las mismas personas, §7.5 SHALL declararlo. El documento y `data/README.md` SHALL
explicar que datos personales contenian los originales no versionados y de quien eran, de modo
coherente con `11:24` y `12:151`. La contradiccion entre "se redactaron" (`04:46`) y "coinciden con
el texto de origen" (`12:153`) SHALL resolverse; si las descripciones del regimen (a) fueron
reescritas por los autores, la septima amenaza (`04:129`) SHALL extenderse a los 200 casos. El
capitulo legal SHALL incluir un parrafo sobre la informacion de los empleadores reales
(confidencialidad, autorizacion o su innecesariedad) segun la respuesta. "El corpus no proviene de
una organizacion real" (`01:72`) SHALL retirarse o acotarse. El contenido MUST NOT inventarse y
MUST NOT contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Una sola formula de reportantes

- **WHEN** se ejecuta `rg -n "reportados por los integrantes del entorno operativo|propio grupo de desarrollo" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** todas las coincidencias usan la misma formula, coincidente con OQ-02 de c-249

#### Scenario: Texto de origen o redaccion, sin contradiccion

- **WHEN** se leen `04:46` y `12:153` (o sus sucesores)
- **THEN** ambos describen de la misma manera la relacion entre las descripciones del regimen (a) y el texto de origen
- **AND** si fueron reescritas, la septima amenaza cubre los 200 casos

#### Scenario: Originales con PII explicados

- **WHEN** se lee `data/README.md` en el parrafo de los originales no versionados
- **THEN** dice que datos personales contenian y de quien eran, sin contradecir `11:24` ni `12:151`

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-249 no contiene la respuesta OQ-02
- **THEN** las tareas gated por OQ-02 permanecen sin marcar

### Requirement: Consentimiento verbal y articulo 5 analizados (OQ-03 de c-249)

`11-aspectos-legales.tex` (hoy `:30`) SHALL nombrar el consentimiento del 2-10-2026 como verbal y
su confirmacion escrita del 20-11-2026, MUST NOT llamarlo "expreso" sin esa calificacion, SHALL
reconocer que entre ambas fechas no constaba por escrito y SHALL valorar esa brecha frente al
articulo 5 de la Ley 25.326 con el texto aprobado por los autores. Las transferencias SHALL
ordenarse respecto del consentimiento y no solo de la notificacion, y la corrida de texto del 2-10
SHALL ubicarse antes o despues del consentimiento de ese dia. El texto SHALL declarar si entre el
21-09 y el 1-10-2026 se envio a Gemini texto del corpus. "Fue un desliz de redaccion" SHALL
reemplazarse por la constancia contemporanea que exista o por la declaracion de que no hay ninguna
anterior al acta del 17-11. El acta T2 §2 (`docs/seguridad/acta-consentimiento-t2.md:28-44`)
SHALL usar el mismo vocabulario que `11:30`. Todo SHALL provenir de OQ-03 de c-249.

#### Scenario: Consentimiento calificado

- **WHEN** se ejecuta `rg -n "consentimiento expreso" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias que se refieran al consentimiento del 2-10 sin calificarlo como verbal

#### Scenario: Brecha analizada y corridas ubicadas

- **WHEN** se lee §7.3
- **THEN** figura la valoracion de la brecha frente al articulo 5, la ubicacion de la corrida del 2-10 respecto del consentimiento y la declaracion sobre el periodo 21-09 a 1-10

#### Scenario: Sin "desliz" sin respaldo

- **WHEN** se ejecuta `rg -n "desliz" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias, o la oracion cita la constancia contemporanea registrada en OQ-03

### Requirement: Reglas de decision de las sub-hipotesis aplicadas como se enuncian (OQ-04 de c-249)

El veredicto escrito de la sub-hipotesis 2 (`07:184`, `09:6`) SHALL aplicar la regla enunciada en
`01:34` con su denominador prefijado, o la regla SHALL enmendarse en `01:34` y `04:109` declarando
que el denominador de 147 y el criterio binomial se fijaron despues de ver los datos, segun la
opcion que ratifiquen los autores. La variable SHALL tener un solo nombre en hipotesis, metodo y
resultados. La lectura con la referencia de consenso de la sub-hipotesis 3 (`07:153`, `08:62`) MUST
NOT contradecir la disyuncion de `01:36`. Las cifras SHALL tomarse del recomputo versionado.

#### Scenario: Veredicto conforme a la regla escrita

- **WHEN** se comparan `01:34`, `04:109`, `07:184` y `09:6`
- **THEN** el criterio que decide el veredicto es el que la hipotesis enuncia, o la enmienda post hoc esta declarada en `01:34` y `04:109`

#### Scenario: Consenso de la sub-hipotesis 3 coherente

- **WHEN** se ejecuta `rg -n "ser.a no concluyente" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias referidas a la exactitud con consenso (0,797)

### Requirement: Reencuadre completo en Resumen, Abstract y capitulos 7 a 10

El Resumen y el Abstract SHALL declarar en una oracion que la organizacion es un escenario de
referencia, que el corpus combina 119 incidentes reales y 81 reconstrucciones redactadas por un
autor, y que el flujo manual se cronometro como tarea de laboratorio, sin superar 250 palabras de
prosa cada uno. "Tarea de laboratorio" SHALL acompanar al flujo manual en `01:18`, `07:37`,
`09:6`, `09:22` y `09:41`. `07:37` MUST NOT decir que la medicion sustituye a la premisa de 2 min
45 s. "1 USD trimestral" (`00r:15`, `00r:31`, `08:118`) y "32,2 horas-persona" (`08:72`) SHALL
rotularse "sobre el volumen supuesto". `08:42`, `08:68`, `09:47` y `09:49` MUST NOT presentar el
escenario como lugar de recoleccion ni extrapolar a otras organizaciones. `01:38` MUST NOT prometer
el contraste de una hipotesis subsidiaria que no se contrasta. `04:46` MUST NOT decir que el corpus
se tomo del universo supuesto y `04:54` SHALL rotular N = 2.646 como supuesto. Ninguna cifra
canonica cambia.

#### Scenario: Resumen y Abstract reencuadrados dentro del tope

- **WHEN** se leen `00-resumen.tex` y se cuentan las palabras de prosa de cada bloque
- **THEN** cada bloque contiene escenario, composicion 119/81 y "laboratorio" (o "laboratory task")
- **AND** cada bloque tiene como maximo 250 palabras

#### Scenario: Laboratorio en los capitulos 7 a 10 y sin sustitucion

- **WHEN** se ejecuta `rg -n "laboratorio" "docs/Tesis/v10 (IA)/paper/sections/07-resultados.tex" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex"`
- **THEN** hay al menos una coincidencia en cada archivo
- **AND** `rg -n "sustituye, como lectura vigente" "docs/Tesis/v10 (IA)/paper/sections/"` no devuelve coincidencias

#### Scenario: Derivados del volumen rotulados y sin extrapolacion

- **WHEN** se ejecuta `rg -n "organizaciones medianas con vol.menes comparables|De ese universo se tom.|presentado como escenario de referencia" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias
- **AND** cada mencion de "1~USD" trimestral y de "32,2" lleva el rotulo de volumen supuesto

### Requirement: Lectura por regimen escrita con cifras recomputadas

La discusion (`08:18`) SHALL declarar que el canal telefonico coincide con las 81 reconstrucciones
del regimen (b) y SHALL informar la exactitud estricta por regimen con intervalo de Wilson. La
segunda limitacion (`08:50`) SHALL dar la proporcion 81 de 200 (40,5 %) y la clausula "declaracion
de los autores, sin registro de procedencia por caso". La autoria de las reconstrucciones SHALL
atribuirse de la misma manera en todo el documento, conforme al registro de c-246 OQ-01. `07:376`
SHALL informar el p95 de la corrida original en el nivel 5 de N8N y que el subconjunto
deterministico de la corrida ampliada ya superaba el techo. Todas estas cifras SHALL provenir de
`evaluation/data/campana/analisis/analisis_regimen_c249.json`, generado por un script con prueba
automatizada, y MUST NOT copiarse del dictamen.

#### Scenario: Cifras con generador versionado

- **WHEN** se ejecuta `pytest evaluation/data/campana/analisis/test_analisis_regimen_c249.py` y luego el script
- **THEN** la prueba pasa y el JSON contiene la exactitud por regimen, sus intervalos, las proporciones de la sub-hipotesis 2 y los p95 del nivel 5
- **AND** las cifras de `08:18`, `08:50` y `07:376` coinciden con el JSON

#### Scenario: Autoria unificada

- **WHEN** se ejecuta `rg -n "redactad[ao]s? por (los autores|un autor|ese autor|uno de)" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** todas las coincidencias atribuyen las reconstrucciones de la misma manera

### Requirement: Consistencia de los capitulos 2, 3, 6 y 10 con el reencuadre

El marco teorico SHALL fundamentar el modelo economico (costo de derivacion erronea, exactitud y
costo de equilibrio) y completar el parrafo de pruebas (`02:100`) con los metodos usados; MUST
NOT repetir con las mismas frases los pasajes de calibracion, cascadas y sesgo idiomatico del cap.
3; SHALL trasladar a los capitulos 4 o 5 los umbrales y fechas de implementacion (`02:34`, `02:46`,
`02:67`); y SHALL citar o declarar como supuesto `02:20`. El estado del arte SHALL justificar los
trabajos anteriores a 2023 o ajustar el criterio temporal (`03:8`), informar los conteos por cadena
que registra la bitacora, citar o reformular `03:22` y `03:28`, y acotar `03:24` y `03:90-92`.
`06:62`, `06:74` y `06:97` SHALL rotularse como observaciones del desarrollo sin medicion o
retirarse. El capitulo 11 SHALL tener una subseccion de primer nivel para la medicion del costo de
reasignacion con criterio de exito y tamano de muestra, y una linea sobre la medicion por regimen
o la sustitucion de las reconstrucciones; `10:6`, `10:14` y `10:38` MUST NOT presuponer una
operacion inexistente ni llamar "medida" a una propiedad del diseno.

#### Scenario: Residuos de los capitulos 6 y 10 resueltos

- **WHEN** se ejecuta `rg -n "en el campo|dependencia medida|sectores responsables|inteligencia organizacional accionable" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias que presupongan una operacion o una medicion inexistente

#### Scenario: Modelo economico con marco teorico

- **WHEN** se ejecuta `rg -n "equilibrio" "docs/Tesis/v10 (IA)/paper/sections/02-marco-teorico.tex"`
- **THEN** hay al menos una coincidencia en una subseccion con fuente

### Requirement: Forma y bibliografia conformes a las recomendaciones 13 y 14 del dictamen sobre v1.6.3

Las figuras del flujo N8N y del Anexo E MUST NOT imprimirse dentro del Anexo F. El glosario MUST NOT
tener celdas izquierdas vacias en mitad de columna. La hipotesis SHALL definir "F1 macro de
umbral" donde lo usa, y el valor p de la sub-hipotesis 1 SHALL informarse con la lateralidad de su
H1. La Decision 2003/490/CE SHALL citarse como DO L 168 de 5 de julio de 2003, pp. 19-22. Las
cuatro entradas de documentacion (n8n, PostgreSQL, Airflow, FastAPI) SHALL usar "s. f." o el ano de
la version consultada. El Anexo F SHALL referenciarse desde §4.4 y declarar historica la cadena
`metadata.descripcion` del JSON, y `data/README.md` SHALL marcar el parrafo de c-242 como superado.

#### Scenario: Fecha de la Decision corregida

- **WHEN** se ejecuta `rg -n "8 de julio de 2003" "docs/Tesis/v10 (IA)/Bibliography_base.bib"`
- **THEN** no hay coincidencias y la entrada dice 5 de julio de 2003, pp. 19-22

#### Scenario: Anexo F referenciado

- **WHEN** se ejecuta `rg -n "ref\{sec:anexo-corpus\}" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex"`
- **THEN** hay al menos una coincidencia

### Requirement: Registro de compuertas y verificacion de c-249

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL tener una seccion c-249 con la tabla de
compuertas OQ-01 a OQ-06 (pregunta, respuesta literal, fecha, responsable), la tabla ANTES/DESPUES
de cada tarea de edicion, el resultado de la coherencia y la release. El encabezado de c-248 SHALL
dejar de decir "EN CURSO".

#### Scenario: Seccion c-249 completa

- **WHEN** se lee la seccion c-249 de `dictamen-correcciones.md`
- **THEN** figuran las seis compuertas con respuesta, fecha y responsable, y una fila ANTES/DESPUES por tarea aplicada
- **AND** `rg -n "^## c-248.*EN CURSO" docs/Tesis/Correcciones/dictamen-correcciones.md` no devuelve coincidencias
