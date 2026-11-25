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

### Requirement: Cronología de la campaña manual en octubre 2026 referida al corpus vigente (C-01 de c-250)

El documento SHALL referir toda medición de la línea base manual al corpus **vigente** (200 casos) y
MUST NOT presentar el corpus sintético del 3 de julio (165,3 s) como base de medición: ese corpus
SHALL figurar únicamente como histórico/retirado en la Nota de versiones. La clasificación manual del
corpus **real** SHALL fecharse en **octubre 2026** (no "junio a agosto"): la ventana "junio a agosto"
de §4.2 (`04-marco-metodologico.tex:14`), §4.4 (`:46`), la Tabla 4 `tab:procedencia-numeros`
(`:78`) y §1.2 (`01-introduccion.tex:16`) SHALL reemplazarse por **octubre 2026**, referido a la
clasificación manual del corpus real. La evidencia fechada es: commit `68d06ec` (2026-06-11) versiona
el corpus **sintético**; commit `ea62576` (2026-10-09) versiona el corpus **real**. La declaración
honesta de cronología ("declaración de los autores sin registro fechado") SHALL conservarse. El
contenido MUST NOT inventarse.

#### Scenario: Corpus sintético solo histórico

- **WHEN** se ejecuta `rg -n "165,3|corpus sint.tico" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** la única aparición como base de medición no existe: el 165,3 s figura solo como histórico/retirado, y únicamente en la Nota de versiones (Anexo I.1)

#### Scenario: Ventana junio–agosto reemplazada por octubre 2026

- **WHEN** se ejecuta `rg -n "junio a agosto|junio y agosto|entre junio y agosto" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias fuera de la Nota de versiones; §4.2, §4.4, la Tabla 4 y §1.2 fechan la campaña vigente en octubre 2026

#### Scenario: Evidencia fechada citada

- **WHEN** se lee el pasaje que fundamenta la cronología de la campaña vigente
- **THEN** se citan los commits `68d06ec` (sintético) y `ea62576` (real) como evidencia fechada, y la declaración honesta sin registro fechado se conserva

### Requirement: Componente "~10 s de carga del ticket" retirado (C-02 de c-250)

El documento SHALL retirar el "~10 s de carga del ticket estimada": ese componente NO existe en los
datos. El tiempo manual SHALL describirse como **clasificación manual (lectura + decisión de
sector)**, sin componente E2E ni de carga. La fórmula "en el orden de 10 s, cuya magnitud exacta no
consta" SHALL retirarse de §4.4 (`04:89`), §4.8 octava amenaza (`04:131`), `12-anexos.tex:153`,
`07-resultados.tex:285`, `01-introduccion.tex:18`, el Resumen (`00-resumen.tex:13`), el Abstract
(`:29`), la Tabla 10 (`07:42`), la Tabla 23 (`09:14`) y `data/README.md`. La Tabla 3 (`04:31`) SHALL
dar una definición operacional **por brazo**: manual = clasificación (lectura + decisión de sector),
automatizado = E2E (recepción → persistencia); el brazo manual MUST NOT describirse como "hasta la
persistencia confirmada del ticket". El Anexo K (`12-anexos.tex:351,353,367`) SHALL CONSERVAR su
computo de −10 s → 51,6 s / 65,6 % como **sensibilidad de redondeo** (los valores se redondearon
ARRIBA a múltiplos de 5 s): MUST NOT re-relatarse como "remoción de un componente de carga".

#### Scenario: Fórmula de carga retirada

- **WHEN** se ejecuta `rg -n "en el orden de 10|carga del ticket" "docs/Tesis/v10 (IA)/paper/sections/" "data/README.md"`
- **THEN** no hay coincidencias de un componente de carga sumado al tiempo manual

#### Scenario: Definición operacional por brazo

- **WHEN** se lee la Tabla 3 (`04:31`)
- **THEN** cada brazo (manual, automatizado) tiene su definición operacional: manual = clasificación (lectura + decisión); automatizado = E2E, y el brazo manual no se describe como "hasta la persistencia confirmada del ticket"

#### Scenario: Anexo K permanece como sensibilidad de redondeo

- **WHEN** se lee el Anexo K (`12-anexos.tex:351-367`)
- **THEN** el −10 s → 51,6 s / 65,6 % figura como sensibilidad de redondeo (valores redondeados hacia arriba), y NO como remoción de un componente de carga

### Requirement: Asimetría telefónica por brazo y sub-hipótesis 1 sin telefonía (C-03 de c-250)

El documento SHALL informar la mediana y la media de duración de las 81 grabaciones frente a la
lectura manual completa, distinguiendo explícitamente la grabación cruda `duracion_segundos` (mediana
7,0 s; media 7,26 s) del `t_e2e_s` automatizado de grabación+procesamiento (mediana 18,698 s), para
no confundir ambos constructos. La sexta amenaza (`04:127`) SHALL ampliarse con esta asimetría: en el
brazo automatizado de telefonía un autor recitó una paráfrasis con tope de 45 s, mientras el brazo
manual leyó en voz alta la descripción completa, de modo que las medias 87,2 s / 20,09 s comparan dos
textos de distinta extensión; y con el componente de carga retirado, la asimetría SHALL declararse aún
más fundamental (el 87,2 s manual es clasificación pura y el 20,09 s automatizado es E2E: distinto
alcance Y distinta entrada). La sub-hipótesis 1 SHALL informarse también **sin** telefonía: sobre
correo y formulario las medias pasan de ≈44,1 s a ≈16,2 s (≈63,3 % de reducción), recomputada por
pares con su intervalo. Todas las cifras SHALL provenir de `data/corpus_resultados_telefonia.json`,
`data/corpus_evaluacion_pseudonimizado.json` y la sección 3.8 del memo canónico, a través del script
de análisis con prueba automatizada, y MUST NOT copiarse del dictamen.

#### Scenario: Grabación vs. t_e2e distinguidos

- **WHEN** se lee el pasaje que informa la duración de las 81 grabaciones
- **THEN** la mediana de grabación+procesamiento (18,7 s) no se presenta como la duración de grabación; la duración cruda (mediana 7,0 s / media 7,26 s) se distingue explícitamente del `t_e2e_s`

#### Scenario: Sexta amenaza ampliada

- **WHEN** se lee la sexta amenaza (`04:127`)
- **THEN** contrasta el brazo manual (descripción completa leída en voz alta) contra el automatizado (paráfrasis recitada, tope 45 s), declarando la distinta extensión de entrada y la asimetría de alcance tras el retiro de la carga

#### Scenario: Sub-hipótesis 1 sin telefonía

- **WHEN** se lee el informe de la sub-hipótesis 1 (`07:10`, `08:8` o su sucesor) y la salida del script de análisis
- **THEN** figura la reducción sin telefonía (correo+formulario ≈44,1 s → ≈16,2 s, ≈63,3 %) con su intervalo por pares, y las cifras coinciden con el JSON versionado

#### Scenario: Cifras con generador versionado

- **WHEN** se ejecuta `pytest evaluation/data/campana/analisis/test_analisis_quinta_instancia_c250.py` y luego el script
- **THEN** la prueba pasa y el JSON contiene la desagregación sin telefonía, la reducción sin telefonía y sus intervalos

### Requirement: Estado del registro primario unificado (C-04 de c-250)

La redacción SHALL unificar el estado del registro primario: §8.1 (`07:38`) SHALL dejar de decir que
los 119 de correo y formulario están "sin registro primario conservado" mientras atribuye "con
registro" solo a los 81 telefónicos. El texto final SHALL decir que los 81 telefónicos están
respaldados por `corpus_resultados_telefonia.json` y que los 119 de correo/formulario están
respaldados por `corpus_resultados_web_correo.json` con 118 de 119 con registro versionado, siendo
R001 el único caso sin registro, coherente con §4.5 (`04:66`, `:79`), `12-anexos.tex:149` y
`data/README.md:40-47`. No cambia ningún dato ni ningún número canónico.

#### Scenario: Redacción coherente en §8.1

- **WHEN** se lee §8.1 (`07:38`) y se contrasta con §4.5 (`04:66`, `:79`), `12:149` y `data/README.md:40-47`
- **THEN** todos los pasajes describen el mismo estado: 81 telefónicos y 118/119 correo/formulario con registro versionado, R001 como único caso sin registro

#### Scenario: Sin cambio de datos

- **WHEN** se ejecuta `sha256sum data/corpus_resultados_web_correo.json data/corpus_resultados_telefonia.json data/corpus_evaluacion_pseudonimizado.json`
- **THEN** los hashes coinciden con los registrados en la línea base (el corpus no se editó)

### Requirement: Consentimiento separado, sin originales con identificadores y licitud por disociación (C-05 de c-250)

En el capítulo legal (`11-aspectos-legales.tex`, rendido Cap. 7), el documento SHALL retirar la
afirmación de que "los originales no versionados contenían los nombres reales de sus sistemas + ID
USUARIO" (`:18` y `data/README.md:55-63`): el corpus fue SIEMPRE genérico ("sistema principal" /
"sistema secundario") y no hay originales con identificadores ni custodio ni fecha de destrucción que
declarar. El documento SHALL separar el consentimiento de los colaboradores (autores + A1) del de los
TITULARES (los reportantes del círculo), y MUST NOT sostener en `:46` que "los titulares de los datos
y los responsables del tratamiento son las mismas personas". La licitud SHALL fundarse en la
disociación citando los artículos **2 y 28** de la Ley 25.326 (el art. 28 es una adición neta; hoy
solo se cita el art. 2 en `:12`). La "notificación a los integrantes del grupo" SHALL definirse como
**verbal el 2026-09-30** (corrige el 01/10 anterior): se les comunicó que se utilizarían sus
incidentes en forma pseudonimizada y disociada, construidos a partir de sus descripciones. El
contenido MUST NOT inventarse y MUST NOT contener nombres reales ni la correspondencia
alias-identidad.

#### Scenario: Sin originales con identificadores

- **WHEN** se ejecuta `rg -n "nombres reales|ID USUARIO|SISTEMA PRINCIPAL|custodi|destrucci.n" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex" "data/README.md"`
- **THEN** no hay coincidencias que sostengan la existencia de originales con identificadores ni de custodia o destrucción que declarar

#### Scenario: Consentimiento y titularidad separados

- **WHEN** se ejecuta `rg -n "titulares.*responsables.*mismas personas" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias; el consentimiento de colaboradores (autores + A1) y el de los titulares (reportantes del círculo) se tratan por separado

#### Scenario: Licitud fundada en disociación (arts. 2 y 28)

- **WHEN** se ejecuta `rg -n "art.*28|art.culo 28|disociaci.n" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** el art. 28 y el art. 2 se citan juntos como fundamento de la licitud por disociación

#### Scenario: Notificación verbal del 30/09 definida

- **WHEN** se lee `:32` del capítulo legal
- **THEN** la notificación a los integrantes del grupo figura como verbal el 2026-09-30, y especifica que se usarían sus incidentes en forma pseudonimizada y disociada, construidos a partir de sus descripciones

### Requirement: Empleadores disueltos, reencuadre de procedencia y deber de confidencialidad (C-06 de c-250)

El documento SHALL retirar la afirmación de `11-aspectos-legales.tex:18` ("los empleadores reales de
los autores" y "no se requirió autorización de esas organizaciones"): el origen real es **familiares y
amigos (el círculo)**. Con la disolución de los "empleadores reales", MUST NOT existir una tarea de
"obtener el aval escrito del director" (la afirmación que respaldaba desapareció). El documento SHALL
agregar el deber de confidencialidad del **art. 10** de la Ley 25.326 a los principios generales del
capítulo legal (junto a la tríada CIA, hoy en `:40`). El reencuadre de procedencia SHALL retirar
"integrantes del entorno operativo del propio equipo" de toda mención de procedencia
(`01:16,48,72`, `04:46`, `08:22,42,50`, `09:52`, `11:16,46,54`, Resumen) y dejar la procedencia como
"los autores y las personas de su círculo (familiares y amigos)", CONSERVANDO el escenario ficticio
("organización mediana del sector servicios / 120 usuarios / 42 diarios", dispositivo de
dimensionamiento explícitamente no-real por R-01) y la "organización adoptante" (despliegue futuro).
El reencuadre SHALL registrarse en la Nota de versiones como corrección de veracidad (estilo R-01 a
R-07). El contenido MUST NOT inventarse.

#### Scenario: Empleadores reales retirados, sin aval del director

- **WHEN** se ejecuta `rg -n "empleadores reales|no se requiri. autorizaci.n de esas organizaciones|aval escrito del director" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias que sostengan la existencia de empleadores reales ni la necesidad de un aval del director por C-06

#### Scenario: Deber de confidencialidad citado

- **WHEN** se ejecuta `rg -n "art.*10|art.culo 10|confidencialidad" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** el art. 10 y el deber de confidencialidad se mencionan entre los principios generales del capítulo, junto a la tríada CIA

#### Scenario: Procedencia del círculo, sin "entorno operativo"

- **WHEN** se ejecuta `rg -n "integrantes del entorno operativo del propio equipo|entorno operativo" "docs/Tesis/v10 (IA)/paper/sections/00-resumen.tex" "docs/Tesis/v10 (IA)/paper/sections/01-introduccion.tex" "docs/Tesis/v10 (IA)/paper/sections/04-marco-metodologico.tex" "docs/Tesis/v10 (IA)/paper/sections/08-discusion.tex" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias en mención de procedencia; la procedencia dice "los autores y las personas de su círculo (familiares y amigos)"

#### Scenario: Escenario ficticio y organización adoptante conservados

- **WHEN** se ejecuta `rg -n "120 usuarios|42 diarios|organizaci.n adoptante" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** el escenario ficticio sigue presente como dispositivo de dimensionamiento (no-real, por R-01) y la "organización adoptante" sigue presente como despliegue futuro

### Requirement: Coherencia y redacción de la quinta instancia (C-07 de c-250)

La Tabla 26 (`tab:declaracion-uso-ia`, `12-anexos.tex:257-277`) SHALL agregar una fila sobre la
redacción del corpus que diga **"sin IA"** (no se usó un asistente de IA para reescribir las 119
descripciones del régimen (a)). La declaración I.3 (`12:279`) SHALL corregir que el etiquetado "es de
los autores": lo hicieron A1, T1, E1 y E2. La atribución de autoría de las reconstrucciones SHALL
unificarse entre "por los autores" (I.1 `12:241`), "por ese autor" (§4.4 `04:46`) y "uno de ellos"
(`09:25`), conforme a la decisión de autoría registrada en c-250. §7.5 (`11:54`) SHALL mencionar
"Gemini 3.1" para la validación retirada, como en I.1 (`12:243`). La frase "dispositivo de
dimensionamiento y no el lugar de recolección" SHALL aparecer exactamente una vez (hoy 8×). "Corpus
propio de la organización" (`09:48`) SHALL retirarse. "En su domicilio" (`04:46`) SHALL aclararse
indicando de quién es el domicilio.

#### Scenario: Fila "sin IA" en Tabla 26

- **WHEN** se lee la Tabla 26 (`tab:declaracion-uso-ia`)
- **THEN** figura una fila sobre la redacción del corpus que declara "sin IA" (no se usó IA en las 119 descripciones)

#### Scenario: Etiquetado corregido en I.3

- **WHEN** se ejecuta `rg -n "etiquetado.*de los autores" "docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex"`
- **THEN** no hay coincidencias; el texto atribuye el etiquetado a A1, T1, E1 y E2

#### Scenario: Atribución de autoría unificada

- **WHEN** se ejecuta `rg -n "por (los autores|ese autor)|uno de ellos" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** las reconstrucciones se atribuyen de la misma manera en todo el documento, conforme a la decisión registrada

#### Scenario: Frase de "dispositivo de dimensionamiento" una sola vez

- **WHEN** se ejecuta `rg -c "dispositivo de dimensionamiento y no el lugar de recolecci.n" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** el conteo total es exactamente 1

#### Scenario: "corpus propio de la organización" retirado y domicilio aclarado

- **WHEN** se ejecuta `rg -n "corpus propio de la organizaci.n" "docs/Tesis/v10 (IA)/paper/sections/09-conclusiones.tex"` y se lee `04:46`
- **THEN** no hay coincidencias de "corpus propio de la organización", y "en su domicilio" indica de quién es el domicilio

#### Scenario: Gemini 3.1 en §7.5

- **WHEN** se ejecuta `rg -n "Gemini 3\.1" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** hay al menos una coincidencia referida a la validación retirada

### Requirement: Registro de decisiones y verificación de c-250

`docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL tener una sección c-250 con la tabla de
decisiones OQ-01 a OQ-05 (decisión literal, fecha, responsable), las tablas ANTES/DESPUES de cada
tarea de edición, el resultado de la coherencia y la release. Las cinco compuertas SHALL figurar como
CERRADAS (ninguna "EN CURSO" ni pendiente de autores). El encabezado de c-249 SHALL dejar de decir
"EN CURSO" si sigue en curso.

#### Scenario: Sección c-250 completa

- **WHEN** se lee la sección c-250 de `dictamen-correcciones.md`
- **THEN** figuran las cinco decisiones con respuesta, fecha y responsable, y una fila ANTES/DESPUES por tarea aplicada
- **AND** `rg -n "^## c-249.*EN CURSO" docs/Tesis/Correcciones/dictamen-correcciones.md` no devuelve coincidencias
- **AND** `rg -n "OQ-0[1-5].*(EN CURSO|pendiente|compuerta)" docs/Tesis/Correcciones/dictamen-correcciones.md` no devuelve coincidencias de una compuerta abierta
