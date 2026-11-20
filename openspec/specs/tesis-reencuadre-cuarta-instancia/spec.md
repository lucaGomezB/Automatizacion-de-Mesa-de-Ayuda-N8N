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
