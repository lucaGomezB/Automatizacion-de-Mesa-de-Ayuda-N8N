# tesis-reencuadre-cuarta-instancia Specification

## Purpose
Define el comportamiento observable de la prosa de la tesis tras aplicar el reencuadre
autorizado de cuarta instancia (R-01 a R-07 + B-01): declarar la organizacion como escenario
ficticio, la composicion del corpus, el flujo manual como tarea controlada, el volumen como
supuesto, la base legal real por regimen, las limitaciones reformuladas, la nota de versiones
y los nombres de sector unificados.

## Requirements

### Requirement: Escenario declarado como parametro ficticio (R-01)

El documento SHALL declarar que la organizacion del estudio es un **escenario de referencia
ficticio construido por los autores** y MUST NOT presentarla como una organizacion real. Las
cifras de la "semana laboral representativa" (42 incidentes diarios, 2 min 45 s por registro,
15 % de derivacion erronea, alrededor de 120 usuarios, cinco areas) SHALL presentarse como
**parametros del escenario**, no como mediciones de una operacion real. El documento MUST NOT
afirmar como hecho la antiguedad del personal en una mesa de ayuda real ni derivar las cifras
de "una semana completa de operacion" real. Cualquier mencion de "la organizacion" como hecho
SHALL reencuadrarse como parametro del escenario de referencia. El texto MUST NOT contener
nombres reales ni la correspondencia alias-identidad.

#### Scenario: Cifras de la semana representativa como parametros

- **WHEN** se leen las cifras de la semana laboral representativa (42 incidentes diarios, 2 min 45 s, 15 %, ~120 usuarios, cinco areas) en §1.1 (`01-introduccion.tex`) y donde aparezcan
- **THEN** se presentan como parametros del escenario de referencia
- **AND** no se presentan como mediciones de una organizacion real

#### Scenario: Sin semana de operacion como fuente de la estimacion

- **WHEN** se busca en `01-introduccion.tex` la expresion "semana completa de operacion" (linea 18)
- **THEN** la estimacion de 2 min 45 s ya no se deriva de una semana completa de operacion real
- **AND** se presenta como un parametro a priori del escenario

#### Scenario: Sin antiguedad del personal en una mesa real

- **WHEN** se lee `04-marco-metodologico.tex` la frase "mas de tres anos de antiguedad en la mesa de ayuda" (linea 64)
- **THEN** los operadores del flujo manual se describen sin apelar a una antiguedad en una mesa de ayuda real
- **AND** no se afirma su pertenencia a una organizacion adoptante real

#### Scenario: Sin "la organizacion" como hecho

- **WHEN** se busca en `docs/Tesis/v10 (IA)/paper/sections/*.tex` la expresion "la organizacion" en afirmaciones de hecho
- **THEN** no se presenta la organizacion como una entidad real
- **AND** las menciones residuales se reencuadran al escenario de referencia o al rol generico futuro del adoptante

### Requirement: Composicion del corpus declarada (R-02)

El documento SHALL declarar la composicion de los 200 casos del corpus: cuantos son incidentes
reales del entorno operativo del propio grupo (regimen (a)) y cuantos reconstrucciones de tipos
de incidente reales (regimen (b)); quien escribio las reconstrucciones; con que metodo; y si se
uso o no un asistente de IA. La frase "corpus real pseudonimizado" de `12-anexos.tex` (linea
235) SHALL corregirse para no afirmar que el corpus completo es "real". El documento SHALL
agregar a §4.8 una amenaza a la validez: los autores escribieron parte de los casos, fijaron el
sector y ajustaron el vocabulario de reglas sobre el mismo corpus. El desglose exacto (cuantos
reales vs cuantas reconstrucciones) SHALL provenir de la respuesta registrada de los autores y
MUST NOT ser inventado por el agente; sin esa respuesta, la tarea queda bloqueada. El texto
MUST NOT contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Desglose de la composicion presente

- **WHEN** se lee la descripcion del corpus en §4.4 y en el Anexo I.1
- **THEN** se declaran cuantos casos son incidentes reales del entorno del grupo y cuantos reconstrucciones
- **AND** el desglose coincide con la respuesta consignada de los autores en la tabla de compuertas

#### Scenario: Autor, metodo y asistente declarados

- **WHEN** se lee la declaracion de composicion
- **THEN** se indica quien escribio las reconstrucciones, con que metodo y si se uso un asistente de IA
- **AND** no se atribuye la redaccion a una fuente no confirmada por los autores

#### Scenario: Frase "corpus real pseudonimizado" corregida

- **WHEN** se busca en `12-anexos.tex` la expresion "corpus real pseudonimizado" (linea 235)
- **THEN** ya no presenta el corpus completo como "real"
- **AND** distingue el caracter del regimen (a) (real pseudonimizado) del regimen (b) (reconstruccion)

#### Scenario: Amenaza de redaccion por los autores en §4.8

- **WHEN** se lee la subseccion de amenazas a la validez de §4.8
- **THEN** figura la amenaza de que los autores escribieron parte de los casos, fijaron su sector y ajustaron el vocabulario de reglas sobre ese mismo corpus
- **AND** se declara en los mismos terminos que las demas amenazas, sin minimizarla

### Requirement: Flujo manual declarado como medicion controlada (R-03)

El documento SHALL describir lo que realmente se midio en el flujo manual de la campana
2026-10: donde, sobre que textos, quienes (`A1` y `T1`) y en que fechas. La subseccion
`04-marco-metodologico.tex` (linea 46) SHALL RETIRAR las frases "sobre la operacion normal de
la mesa" y el "periodo relevado del 16 de junio al 10 de septiembre de 2026". El flujo manual
SHALL declararse como una **medicion controlada / tarea de laboratorio**, y los "61,6 s" SHALL
leerse como medicion de una tarea controlada, no de la operacion normal de una mesa de ayuda
real. El universo de 2.646 incidentes proyectado desde el periodo "del 16 de junio al 10 de
septiembre" SHALL reencuadrarse como supuesto del escenario (coordinado con R-04), sin perder
la formula `42 x 63 ~ 2.646`.

#### Scenario: Medicion real descrita

- **WHEN** se lee la descripcion del flujo manual en §4.2 y §4.4
- **THEN** se declara donde, sobre que textos, quienes (A1 y T1) y en que fechas se cronometro
- **AND** la descripcion coincide con lo consignado por los autores en la tabla de compuertas

#### Scenario: Retirada la operacion normal

- **WHEN** se busca en `04-marco-metodologico.tex` la expresion "sobre la operacion normal de la mesa" (linea 46)
- **THEN** ya no aparece
- **AND** en su lugar se declara que fue una tarea de laboratorio / medicion controlada

#### Scenario: Periodo relevado retirado

- **WHEN** se busca en `04-marco-metodologico.tex` la expresion "del 16 de junio al 10 de septiembre" presentada como periodo relevado real (linea 46)
- **THEN** ya no se presenta ese periodo como el horizonte real de relevamiento
- **AND** la formula `42 x 63 ~ 2.646` se conserva reencuadrada como supuesto del escenario

#### Scenario: Los 61,6 s leidos como tarea controlada

- **WHEN** se lee la presentacion de la media de 61,6 s del flujo manual
- **THEN** se declara como medicion de una tarea controlada / de laboratorio
- **AND** no se presenta como el tiempo de la operacion normal de una mesa de ayuda real

### Requirement: Volumen trimestral como supuesto (R-04)

El documento SHALL presentar los 2.646 incidentes por trimestre como un **supuesto del
escenario**, y el balance neto como un ejercicio con volumenes supuestos. Las menciones sin
calificar de "2.646" (en `08-discusion.tex` y `12-anexos.tex`, entre otros) SHALL quedar
rotuladas como supuesto del escenario, para que ninguna cifra derivada se lea como medicion de
un volumen real. La formula `42 x 63` SHALL conservarse como la proyeccion que define el
supuesto. MUST NOT cambiar el valor de ningun numero canonico del sistema ni de la campana.

#### Scenario: Volumen rotulado como supuesto

- **WHEN** se busca "2.646" (o `2.646`) en `08-discusion.tex`, `12-anexos.tex` y el resto de `sections/*.tex`
- **THEN** cada ocurrencia se presenta como supuesto del escenario (proyeccion `42 x 63`)
- **AND** ninguna se lee como un volumen medido de incidentes reales

#### Scenario: Balance como ejercicio con volumenes supuestos

- **WHEN** se lee la presentacion del balance neto trimestral
- **THEN** se declara como un ejercicio con el volumen supuesto de 2.646
- **AND** se mantiene como cota superior, sin afirmar ahorro real verificado

### Requirement: Capitulo 7 reescrito sin base de empleador (R-05)

El capitulo 7 (`11-aspectos-legales.tex`) SHALL reescribirse para declarar el tratamiento que
realmente ocurrio. SHALL RETIRARSE: la base de empleador (articulo 5, inciso 2, apartado d)
como base del estudio; el responsable de proteccion de datos "designado por la organizacion";
la politica de privacidad dirigida a "los usuarios de la organizacion"; la notificacion a 120
empleados; y la carta de autorizacion. El documento SHALL explicar la base legal real de los
incidentes reales del regimen (a): consentimiento informado del grupo (articulo 5, inciso 1),
reconciliando la caracterizacion del tribunal de "incidentes reales de terceros" con el hecho
de que los titulares son los propios integrantes del grupo. El acta de consentimiento SHALL
llevar su **fecha real de firma**, sin fecha inventada. La redaccion exacta de la base legal y
la fecha real del acta SHALL provenir de la respuesta registrada de los autores; sin esa
respuesta, la tarea queda bloqueada.

#### Scenario: Base de empleador retirada

- **WHEN** se busca en `11-aspectos-legales.tex` la base de empleador (articulo 5, inciso 2, apartado d) como base del estudio
- **THEN** ya no funda el tratamiento del estudio
- **AND** si se cita la base de empleador, se presenta solo como la que corresponderia a una organizacion adoptante real (T3), de forma condicional

#### Scenario: Responsable, politica y notificacion retirados

- **WHEN** se buscan en `11-aspectos-legales.tex` "responsable de proteccion de datos designado por la organizacion", la politica de privacidad "para los usuarios de la organizacion" y la notificacion a 120 empleados
- **THEN** ya no aparecen como hechos del estudio
- **AND** no se sustituyen por una afirmacion equivalente sobre una organizacion adoptante real

#### Scenario: Base real del regimen (a) explicada

- **WHEN** se lee la explicacion de la base de licitud de los incidentes reales del regimen (a)
- **THEN** se funda en el consentimiento informado del grupo (articulo 5, inciso 1)
- **AND** se aclara que los titulares son los propios integrantes del grupo (no terceros ajenos), reconciliando la caracterizacion del tribunal

#### Scenario: Fecha real del acta de consentimiento

- **WHEN** se lee la fecha del acta de consentimiento (actualmente "2026-10-02" en `11-aspectos-legales.tex`)
- **THEN** la fecha consignada es la fecha real de firma confirmada por los autores
- **AND** no se inventa ni se conserva una fecha no confirmada

### Requirement: Limitaciones reformuladas (R-06)

Las limitaciones SHALL reformularse: "una sola organizacion" y "el unico contexto en que se
evaluo" (`09-conclusiones.tex`, `08-discusion.tex` §9.3) pasan a ser "un corpus curado por los
autores sobre un escenario de referencia". El documento MUST NOT presentar la validez externa
como acotada a una unica organizacion real, sino al corpus curado sobre el escenario de
referencia. La limitacion geografica (provincia de Mendoza) SHALL conservarse como atributo del
escenario, no como sede de una organizacion real.

#### Scenario: "Una sola organizacion" reemplazada

- **WHEN** se busca en `09-conclusiones.tex` y `08-discusion.tex` la expresion "una sola organizacion" o "unico contexto en que se evaluo"
- **THEN** la limitacion se formula como "un corpus curado por los autores sobre un escenario de referencia"
- **AND** no se presenta como la limitacion de una organizacion real unica

#### Scenario: Limite geografico como atributo del escenario

- **WHEN** se lee la limitacion geografica (provincia de Mendoza)
- **THEN** se conserva como atributo del escenario de referencia
- **AND** no se presenta como la sede de una organizacion adoptante real

### Requirement: Nota de versiones del reencuadre (R-07)

El Anexo I.1 (`subsec:nota-versiones`, `12-anexos.tex` lineas 233-238) SHALL agregar una nota
de versiones: hasta la v1.6.0 el escenario se presento como una organizacion real; desde la
version siguiente se declara ficticio, con autorizacion del tribunal. La nota SHALL seguir el
mismo criterio que ya se aplico al corpus sintetico de julio y a la validacion retirada. La
nota MUST NOT afirmar hechos de procedencia no confirmados por los autores.

#### Scenario: Nota presente

- **WHEN** se lee `subsec:nota-versiones`
- **THEN** figura la declaracion de que hasta la v1.6.0 el escenario se presento como una organizacion real y desde la version siguiente se declara ficticio, con autorizacion del tribunal
- **AND** la nota sigue el patron de las declaraciones previas (corpus sintetico de julio, validacion retirada)

#### Scenario: Solo lo confirmado

- **WHEN** se lee la nota de versiones del reencuadre
- **THEN** no afirma hechos de procedencia no confirmados por los autores
- **AND** atribuye el cambio a la autorizacion del tribunal, no a otra causa

### Requirement: Nombres de sector unificados (B-01)

Los nombres de sector SHALL unificarse: la cadena del sistema en monoespaciado (`\sectorcad`)
y la mencion en prosa con tilde (`\sectorprosa`). El cambio SHALL aplicarse donde
`\sectorcad{si}` (monoespaciado, sin tilde) se usa EN PROSA, en particular `01-introduccion.tex`
lineas 48 y 72, que SHALL pasar a `\sectorprosa{si}`. Las cinco cadenas canonicas del sistema
("Seguridad Informatica", etc.) MUST NOT cambiar de valor ni de acentuacion; solo cambia la
instruccion LaTeX usada en prosa.

#### Scenario: Tilde en prosa para el sector SI

- **WHEN** se busca `\sectorcad{si}` en `01-introduccion.tex` (lineas 48 y 72)
- **THEN** esas menciones pasan a `\sectorprosa{si}` (tilde en prosa)
- **AND** el resto de los cinco sectores en la misma enumeracion usan consistentemente `\sectorprosa`

#### Scenario: Cadena del sistema intacta

- **WHEN** se lee la cadena canonica del sistema "Seguridad Informatica" y los otros cuatro sectores
- **THEN** su valor y acentuacion no cambian
- **AND** las menciones en el sistema (monoespaciado) conservan `\sectorcad`

### Requirement: Reportantes y titulares del regimen (a) declarados (OQ-01)

El documento SHALL declarar en §4.4 y §7.5 quien reporto los 119 incidentes del regimen (a)
(los propios autores, u otras personas de los lugares de trabajo de uno o mas autores), en que
tipo de lugares de trabajo y en que periodo se recogieron, y por lo tanto quienes son los
titulares de esos datos. Si los reportantes fueron terceros, el documento SHALL identificarlos
como tales, SHALL fundar el tratamiento de los originales con datos personales (art. 5 o
disociacion del art. 2 de la Ley 25.326) y SHALL retirar "el corpus no proviene de una
organizacion real" (`01-introduccion.tex:72`). Si fueron los autores, SHALL explicar por que las
descripciones estan en tercera persona y usan lexico de clientes y sucursales. El documento
SHALL distinguir, para el regimen (b), el origen (llamadas de terceros al puesto de trabajo de
un autor) del contenido (descripciones redactadas por el autor sin dato personal). El contenido
SHALL provenir de la respuesta registrada de los autores a OQ-01 y MUST NOT ser inventado; sin
esa respuesta, las tareas quedan bloqueadas. El texto MUST NOT contener nombres reales de
reportantes ni la correspondencia alias-identidad.

#### Scenario: Reportantes declarados

- **WHEN** se leen §4.4 (`04-marco-metodologico.tex`, `subsec:poblacion-muestra-corpus`) y §7.5 (`11-aspectos-legales.tex`, `subsec:consentimiento-derechos`)
- **THEN** una oracion declara quien reporto los 119 incidentes del regimen (a) y quienes son sus titulares
- **AND** coincide con la respuesta OQ-01 consignada en la seccion c-247 de `dictamen-correcciones.md`

#### Scenario: Terceros con base de tratamiento

- **WHEN** la respuesta OQ-01 declara que los reportantes fueron terceros
- **THEN** §7.2 y §7.5 fundan el tratamiento de los originales con datos personales en una base de la Ley 25.326 declarada por los autores
- **AND** `rg -n "no proviene de una organizaci.n real" S/01-introduccion.tex` no devuelve coincidencias

#### Scenario: Origen y contenido del regimen (b) distinguidos

- **WHEN** se leen las menciones del regimen (b) como "sin datos de terceros" en §4.4, §7.2 y §7.5
- **THEN** el texto distingue el origen de las llamadas del contenido de las descripciones
- **AND** explica por que la ausencia de datos personales en el contenido hace innecesaria una base de licitud para el origen

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-247 no contiene la respuesta OQ-01
- **THEN** las tareas gated por OQ-01 permanecen sin marcar
- **AND** no se escribe prosa sobre reportantes ni titulares

### Requirement: Base declarada de la composicion del corpus (OQ-01)

El documento SHALL declarar en que se apoya la composicion 119/81 del corpus: o bien que es una
declaracion de los autores sin registro de procedencia por caso, o bien SHALL retirar el
desglose por canal y volver a la descripcion cualitativa, segun decidan los autores. La
descripcion del corpus en `data/README.md` y en el Anexo F SHALL dejar de afirmar "200 casos
reales" y "clasificacion manual" como descripcion vigente. El metadato del JSON congelado
(`data/corpus_evaluacion_pseudonimizado.json`, SHA-256 `1fd17d7e...`) MUST NOT editarse salvo
decision expresa de los autores registrada en OQ-01; si se edita, el nuevo hash SHALL
propagarse a todas sus menciones en un change propio. Ningun caso del corpus SHALL cambiar.

#### Scenario: Base de la composicion declarada

- **WHEN** se lee la composicion del corpus en `04-marco-metodologico.tex:46`
- **THEN** figura la base declarada (declaracion de los autores sin registro por caso) o el desglose fue retirado
- **AND** la opcion coincide con la respuesta OQ-01

#### Scenario: Descripcion del corpus corregida sin romper el hash

- **WHEN** se ejecuta `rg -n "200 casos reales" data/README.md "S/12-anexos.tex"`
- **THEN** no hay coincidencias presentadas como descripcion vigente
- **AND** `sha256sum data/corpus_evaluacion_pseudonimizado.json` sigue dando `1fd17d7e...` salvo que OQ-01 haya elegido editar el JSON

### Requirement: Flujo manual con lugar, sistema, escucha y definicion unica (OQ-02)

El documento SHALL declarar en §4.2 o §4.4 donde y en que sistema `A1` y `T1` cargaron los 200
incidentes, que escucharon en los 81 casos telefonicos durante junio a agosto de 2026 (cuando el
audio se grabo el 5 y 6-10-2026) y cual es la experiencia real de `A1` y `T1` sin apelar al
escenario de referencia (`04-marco-metodologico.tex:58`, `:64`). El tiempo manual
(`tiempo_manual_s`) SHALL tener una sola definicion en todo el documento (`04:16`, `04:46`,
`07:284`, `08:118` y Anexo F `12:147`). La afirmacion de que se incluyen "planillas de
cronometraje" (`12:145`) SHALL retirarse o las planillas SHALL versionarse. La ventana del flujo
automatizado ("septiembre a octubre", `04:14`, `04:64`, `06:79`) SHALL coincidir con la
evidencia fechada o declarar la corrida de septiembre y su ubicacion respecto de la notificacion.
Todo el contenido SHALL provenir de la respuesta registrada a OQ-02.

#### Scenario: Lugar y sistema declarados

- **WHEN** se lee la descripcion del flujo manual de la campana 2026-10
- **THEN** figura el lugar y el sistema de carga declarados por los autores
- **AND** la oracion coincide con la respuesta OQ-02

#### Scenario: Escucha telefonica coherente con la cronologia

- **WHEN** se leen `04-marco-metodologico.tex:66` y `:89`
- **THEN** se declara que escucharon o leyeron `A1` y `T1` en los 81 casos telefonicos
- **AND** el recalculo del 19-10-2026 queda justificado con esa descripcion o reformulado

#### Scenario: Definicion unica del tiempo manual

- **WHEN** se ejecuta `rg -n "carga completa|clasificaci.n manual" S/`
- **THEN** todas las coincidencias que definen el tiempo manual usan la misma definicion

#### Scenario: Planillas y ventana coherentes con el repositorio

- **WHEN** se ejecutan `rg -n "planillas de cronometraje" S/12-anexos.tex` y `rg -n "septiembre a octubre" S/`
- **THEN** la frase de las planillas no aparece o las planillas estan versionadas en `data/`
- **AND** la ventana del flujo automatizado coincide con la respuesta OQ-02

### Requirement: Cronologia unica del consentimiento y de las transferencias (OQ-03)

La tesis (`11-aspectos-legales.tex:30`, §7.5), el acta T2 (`docs/seguridad/acta-consentimiento-t2.md`),
las respuestas al tribunal (`docs/defensa/respuestas-tribunal.md:129` y
`docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md`, respuesta 7) SHALL usar una
sola cronologia y un solo vocabulario para el 1-10-2026 y el 2-10-2026 (informacion,
consentimiento o notificacion), la redaccion del acta (2026-11-17) y su firma (2026-11-20). El
acta T2 SHALL consignar su fecha de firma y de redaccion. El acta T1 SHALL llevar una nota de
revision por las lineas agregadas el 2026-11-18 (`b01da04d`). §7.5 SHALL consignar el
consentimiento escrito de `A1` con su fecha. La lista de transferencias de §7.3 SHALL incluir la
corrida de texto del 2-10-2026 (con su ubicacion respecto de la notificacion), la de
clasificacion del 7-10-2026, la campana complementaria del 5 y 6-11-2026 y las sondas pagas del
17 y 18-11-2026. `11:24` SHALL reconciliarse con los dos CSV de facturacion versionados que cita
`07-resultados.tex:371`. §7.5 SHALL explicar en una oracion por que `v1.6.0` afirmaba que no se
habia recabado el consentimiento. Las fechas SHALL provenir de la respuesta registrada a OQ-03.

#### Scenario: Una sola cronologia en tres documentos

- **WHEN** se ejecuta `rg -n "2026-10-01|2026-10-02|2026-11-20|1 de octubre|2 de octubre" S/11-aspectos-legales.tex docs/seguridad/acta-consentimiento-t2.md docs/defensa/respuestas-tribunal.md docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md`
- **THEN** cada fecha tiene el mismo significado en los cuatro archivos
- **AND** `rg -n "sin fecha de firma consignada" docs/seguridad/acta-consentimiento-t2.md` no devuelve coincidencias

#### Scenario: Nota de revision del acta T1

- **WHEN** se lee `docs/seguridad/acta-consentimiento-t1.md`
- **THEN** una nota de revision declara la edicion del 2026-11-18 y su alcance

#### Scenario: Transferencias completas y comprobantes reconciliados

- **WHEN** se lee `subsec:transferencia-internacional` de `11-aspectos-legales.tex`
- **THEN** figuran las corridas del 2-10 y 7-10, la campana del 5 y 6-11 y las sondas del 17 y 18-11
- **AND** `11:24` no afirma que ningun comprobante se versiona mientras `07:371` cita CSV versionados

### Requirement: Resumen y Abstract reencuadrados

El Resumen y el Abstract (`00-resumen.tex`) SHALL declarar en una oracion el escenario narrativo
y la composicion del corpus, SHALL expresar el balance como ahorro neto por incidente (unos
25,5 s-persona, cota superior) con la proyeccion trimestral rotulada como tal, SHALL acotar
"viabilidad economica" a lo medido (costo marginal de inferencia; balance condicional sobre un
volumen supuesto) y el Abstract SHALL alinear "inconclusive" con "no concluyente, con estimacion
puntual por encima de la cota". Ambos MUST NOT superar 250 palabras de prosa ni cambiar cifras
canonicas.

#### Scenario: Balance por incidente como lectura primaria

- **WHEN** se lee el ultimo parrafo del Resumen y del Abstract
- **THEN** el balance figura por incidente y las horas trimestrales como proyeccion sobre un volumen supuesto
- **AND** `rg -n "viabilidad t.cnica y econ.mica" S/00-resumen.tex` no devuelve la afirmacion sin acotar

#### Scenario: Presupuesto de palabras respetado

- **WHEN** se cuentan las palabras de prosa del Resumen y del Abstract
- **THEN** cada uno tiene a lo sumo 250

### Requirement: Entorno real separado del escenario ficticio

El documento MUST NOT usar la formula "entorno operativo del propio equipo, presentado como
escenario de referencia narrativo" ni afirmar que un corpus se "recolecto" o una evidencia se
"recogio" en un escenario. Cada pasaje del Anexo B del dictamen (`01:16`, `01:62`, `01:72`,
`01:76`, `04:46`, `08:22`, `08:50`, `09:51`) SHALL separar el entorno real de recoleccion de los
casos del escenario de 120 usuarios como dispositivo de dimensionamiento.

#### Scenario: Formula hibrida retirada

- **WHEN** se ejecuta `rg -n "presentado como (un )?escenario de referencia narrativo|entorno operativo de referencia" S/`
- **THEN** no hay coincidencias que fusionen el entorno real con el escenario

### Requirement: Mediciones no comparadas con premisas

Los 61,6 s del flujo manual MUST NOT compararse con el parametro de 2 minutos 45 segundos como
si este fuera una medicion (`01:18` "sustancialmente inferior", `07:37` "reemplaza a la
estimacion preliminar"); si la comparacion se conserva, SHALL rotularse como comparacion con una
premisa. La fila de tiempos manuales de la Tabla de procedencia (`04:78`) SHALL decir "tarea de
laboratorio".

#### Scenario: Comparacion con la premisa retirada o rotulada

- **WHEN** se ejecuta `rg -n "sustancialmente inferior|reemplaza a la estimaci" S/`
- **THEN** no hay coincidencias o la oracion rotula los 2 min 45 s como premisa del escenario
- **AND** la fila "Tiempos manuales" de `tab:procedencia-numeros` contiene "laboratorio"

### Requirement: Coautoria de los datos propagada

La coautoria de los datos (81 reconstrucciones, 40,5 % de las descripciones, escritas por un
autor) SHALL figurar en las limitaciones de §9.3, en la tabla de cumplimiento del objetivo 2
(`09:22` o la fila correspondiente), en la oracion de aportes (`09:53`), en §10, en el Anexo F y
en la Nota de versiones. "corpus real" MUST NOT describir el corpus completo (`07:99`, `09:37`).

#### Scenario: Coautoria en limitaciones y conclusiones

- **WHEN** se ejecuta `rg -n "reconstrucci" S/08-discusion.tex S/09-conclusiones.tex S/12-anexos.tex`
- **THEN** hay al menos una coincidencia en §9.3, en las conclusiones y en el Anexo F
- **AND** `rg -n "corpus real" S/07-resultados.tex S/09-conclusiones.tex` no devuelve coincidencias que describan los 200 casos

### Requirement: Residuos de R-01 y volumen supuesto resueltos

Los pasajes que presentan el escenario como operacion observada SHALL reformularse: `01:48`
("operacion habitual", "representativos"), `02:12`, `04:50-54` ("universo relevado"), `04:56`,
`04:58`, `04:125` ("del periodo"), `08:56`, `08:76` ("experiencia de campo"), `09:51`, `10:14`,
`10:34`. El origen de las estimaciones de 10 a 15 minutos y del 15 % (`01:48`) SHALL declararse
(experiencia previa, bibliografia o supuesto de diseno, segun los autores). `N = 2.646` SHALL
rotularse como supuesto en `08:80`, `08:109` y el Anexo J (`12:321`) sin cambiar su valor.

#### Scenario: Sin operacion observada

- **WHEN** se ejecuta `rg -n "operaci.n habitual|universo relevado|experiencia de campo|acumulado por la organizaci|propia organizaci|entorno empresarial analizado" S/`
- **THEN** no hay coincidencias que presenten el escenario como operacion observada

#### Scenario: N rotulado

- **WHEN** se ejecuta `rg -n "2\.646" S/08-discusion.tex S/12-anexos.tex`
- **THEN** cada ocurrencia en `08:80`, `08:109` y `12:321` lleva el rotulo de supuesto

### Requirement: Consistencia del texto con la evidencia y la bibliografia

El documento SHALL atender las recomendaciones de consistencia 7 a 11 del dictamen: la nota de
facturacion (`07:371`) SHALL atribuir el 18-11 a la corrida ampliada cuantificando la diferencia
del 1,7 % y declarar que el 17-11 incluye la corrida original y consumos no registrados por
llamada; "siete apartados" (`07:6`) SHALL coincidir con las subsecciones; la oracion de TF-IDF
(`02:54`) SHALL retirarse o reescribirse; el parrafo de hipotesis subsidiarias (`01:38`) SHALL
enunciar y remitir sin informar resultados; `09:47` y `09:49` SHALL reescribirse; las fichas de
Paket (`03:49`) y Paramesh (`03:30`, copia arXiv 2103.15822) SHALL completarse sin inventar
cifras; `03:34` SHALL citar a Colavito; la "Novena" limitacion (`08:46`, `08:64`) SHALL salir de
la lista o pasar al protocolo; 0,864 (`04:123`) SHALL rotularse como cota inferior; §11.7
(`10:14`, `10:34`) SHALL omitir "la organizacion", incorporar la condicion de reapertura de c-229
y llevar al primer nivel la medicion del costo de reasignacion; §8.8 SHALL declarar que T = 4 se
fijo para la sonda y presentar las dos corridas completas. Ninguna cifra canonica cambia.

#### Scenario: Facturacion atribuida con la evidencia

- **WHEN** se lee la nota de la tabla de la sonda en `07-resultados.tex:371`
- **THEN** el 17-11 no se atribuye por entero a la corrida original y la diferencia del 18-11 se cuantifica

#### Scenario: Residuos de consistencia retirados

- **WHEN** se ejecuta `rg -n "siete apartados|versi.n arbitrada|Novena" S/`
- **THEN** no hay coincidencias incoherentes con la estructura o la bibliografia

### Requirement: Forma conforme a las recomendaciones 12 a 14

El documento SHALL corregir: la fecha de la portada (`00-portada.tex:30`) con la de la release;
§1.9 (`01:80`) con el Anexo K; las remisiones al memo interno (`07:32`, `07:310`, `08:112`); el
fragmento de `07:8`; la repeticion de `07:343`; las cinco oraciones de mas de 60 palabras
(`04:46`, `04:91`, `07:374`, `07:376`, `09:6`); las cuatro tablas sin cita
(`tab:balance-neto`, `tab:declaracion-uso-ia`, `tab:anexo-nc-costo`, `tab:anexo-nc-balance`);
las once figuras y dos tablas sin linea de fuente; los flotantes de los Anexos A y J; el
glosario (IR, RPO, VoIP, TwiML, OAuth2, IEC) y "Recharts" (`06:97`); las entradas de
Mayor-Rocher, Ramon Ferrer (editorial SAGE), Xiong y Chen; la fecha de la Decision 2003/490/CE.

#### Scenario: Tablas citadas

- **WHEN** se ejecuta `rg -n "ref\{tab:(balance-neto|declaracion-uso-ia|anexo-nc-costo|anexo-nc-balance)\}" S/`
- **THEN** cada una de las cuatro etiquetas tiene al menos una referencia

#### Scenario: Glosario y Recharts

- **WHEN** se ejecutan `rg -n "ReCharts" S/` y `rg -n "RPO|TwiML|OAuth2|VoIP" S/00-glosario.tex`
- **THEN** la primera no devuelve coincidencias y la segunda devuelve las entradas nuevas

### Requirement: Respuestas al tribunal alineadas con la version

Las nueve respuestas de `docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md` SHALL
corregirse: la 1 con el "por que" que consta en el registro de correcciones; la 3 sin atribuir
las etiquetas a un solo autor y sin comparar exactitudes de conjuntos distintos; la 4 sin "no
habia una mesa en operacion"; la 5 con la firma de `A1`; la 7 con el vocabulario de OQ-03; la 9
con "Tabla 26" y "1235". `docs/defensa/respuestas-tribunal.md:129` SHALL alinearse con OQ-03. El
aviso de que la Tabla 25 del tribunal es ahora la 26 SHALL figurar en las respuestas.

#### Scenario: Respuestas coherentes

- **WHEN** se ejecuta `rg -n "Tabla 25|1221|no hab.a una mesa|firma solicitada" docs/Tesis/Correcciones/respuestas-tribunal-cuarta-instancia.md`
- **THEN** no hay coincidencias fuera del aviso de renumeracion

### Requirement: Registro de compuertas y verificacion de c-247

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL contener la seccion c-247 con la tabla
de compuertas OQ-01 a OQ-04 (pregunta, respuesta literal, fecha, responsable), las salidas
ANTES/DESPUES de cada tarea, el resultado de la verificacion de cifras canonicas y la
instruccion OQ-04 para el change de release. Las secciones previas MUST NOT modificarse.

#### Scenario: Seccion c-247 completa

- **WHEN** se lee la seccion c-247 de `dictamen-correcciones.md`
- **THEN** figuran las cuatro compuertas, la tabla ANTES/DESPUES y la instruccion de release
- **AND** `git diff` del archivo es solo aditivo
