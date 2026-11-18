## Purpose

Definir el muestreo probabilistico estratificado del universo de incidentes del entorno operativo
del propio equipo (marco, estratos, cuotas prefijadas por canal y sector, denominadores y reglas de
decision), las compuertas de procedencia y etica/legal que deben cerrarse antes de cualquier computo
sobre datos nuevos, y la estimacion ponderada referida al universo (Horvitz-Thompson /
post-estratificacion) con su efecto de diseno, sin cambiar ningun valor canonico y sin usar evidencia
retirada del ejemplar.

## ADDED Requirements

### Requirement: PS-001 — Universo y marco muestral definidos

El diseno SHALL verificar o construir, como primer paso sustantivo, un marco poblacional real a partir
de los registros de incidentes del **entorno operativo del propio equipo** (sistema de tickets / base
de datos) en un periodo declarado. El marco SHALL ser enumerable por identificador, con probabilidad
de inclusion conocida y mayor que cero, y SHALL documentarse con su completitud, sus campos
disponibles y sus exclusiones. El universo SHALL definirse como la poblacion de incidentes del
entorno operativo del propio equipo en ese periodo, con su tamano `N` confirmado contra el marco: el
valor proyectado `N ≈ 2.646` del memo es solo punto de partida y, si difiere, se informan ambos, y no
constituye un marco medido. Si no existe un marco completo (identificador y contenido clasificable
para todo el periodo y los campos necesarios), la campana SHALL detenerse y el diseno SHALL declarar
que el muestreo probabilistico no es posible; MUST NOT sustituirse por una muestra por conveniencia
ni inventarse un universo. El universo SHALL declararse con sus estratos: sector responsable, canal de
origen y complejidad, cada uno con su definicion operacional, y con la regla de colapso de estratos
escasos. Marco, universo y regla de colapso SHALL registrarse ANTES de reunir la muestra en
`docs/campana-medicion/protocolo-muestreo-probabilistico.md`. El diseno MUST NOT usar la composicion
del corpus de 200 casos como la del universo ni como peso. El protocolo SHALL declarar que, para el
canal telefonico, el insumo del clasificador es el texto registrado y no una transcripcion de audio.

#### Scenario: Marco, universo y estratos declarados

- **WHEN** se lee el protocolo de muestreo probabilistico
- **THEN** figuran el marco con su procedimiento de inclusion y su completitud, el universo con su periodo y su `N` confirmado contra el marco, los estratos con su definicion operacional y la regla de colapso
- **AND** estan fijados antes de reunir la muestra

#### Scenario: Marco incompleto: la campana se detiene

- **WHEN** se verifica que no existe un marco completo para el periodo
- **THEN** la campana se detiene y el diseno declara que el muestreo probabilistico no es posible
- **AND** no se sustituye por una muestra por conveniencia ni se inventa un universo

#### Scenario: Composicion del corpus no tomada como la del universo

- **WHEN** se define la distribucion de los estratos del universo
- **THEN** no se usa la composicion del corpus de 200 casos como sustituto ni como peso
- **AND** si la distribucion del universo no esta disponible, se declara y se fija el metodo para obtenerla

### Requirement: PS-002 — Diseno estratificado con cuotas prefijadas, minimos por sector y clases no estimables

La seleccion SHALL ser probabilistica y estratificada, con cuotas prefijadas por canal y por sector y
probabilidades de inclusion conocidas y mayores que cero. El protocolo SHALL fijar ANTES de reunir la
muestra: el tamano objetivo, una cuota minima por sector, el sobremuestreo de los sectores raros, la
regla de censo (`pi = 1`) para los estratos del universo con menos casos que la cuota minima, la
lista de clases cuyas metricas por clase se declararan no estimables si quedan por debajo del
minimo, los denominadores y las reglas de decision de tres vias (objetivo alcanzado, no alcanzado,
no concluyente) cuando la estimacion se contraste contra un umbral. Nada de esto MUST reajustarse
despues de observar los datos. La composicion del corpus de 200 casos MAY usarse solo como senal de
planificacion de la rareza de una clase, rotulada como tal.

#### Scenario: Cuotas, minimos y reglas fijados antes de la recoleccion

- **WHEN** se inicia la seleccion de la muestra
- **THEN** la asignacion por estrato, el tamano objetivo, la cuota minima por sector, la regla de censo, las clases candidatas a no estimables y la regla de decision estan registrados con fecha y justificacion
- **AND** no se modifican despues de ver los resultados

#### Scenario: Clase rara no estimable declarada de antemano

- **WHEN** el universo del periodo tiene menos casos de un sector que la cuota minima
- **THEN** ese estrato se toma completo con `pi = 1`
- **AND** si aun queda por debajo del minimo, sus metricas por clase se informan como no estimables, tal como se declaro antes de reunir la muestra

### Requirement: PS-003 — Compuerta de procedencia previa a todo computo

Ningun computo sobre datos de la muestra SHALL ejecutarse sin un acta con fecha, firmada por el
director de la tesis (o por un tercero que los autores designen y el director acepte), que verifique
contra la evidencia primaria: (a) una planilla cruda por etiquetador, exportada de la herramienta de
etiquetado declarada en el protocolo, con las marcas temporales que la herramienta registra, nunca
reconstruidas ni completadas a mano; (b) una constancia firmada por cada etiquetador y una constancia
del equipo sobre la exportacion del marco desde su propio registro (fecha, periodo, sistema de origen
y cantidad), con los originales en custodia del director fuera del repositorio y el SHA-256 de cada
planilla cruda y de la exportacion del marco versionado en el repositorio; (c) que los etiquetadores
no son autores ni operadores medidos, con su vinculo con los autores declarado; y (d) que cada texto
es un incidente real del registro del entorno operativo del propio equipo, cubierto por la constancia
de exportacion del marco. Ningun texto
redactado por los autores, ni generado o asistido por IA, MUST entrar como dato; la pseudonimizacion
SHALL limitarse a reemplazar identificadores con un procedimiento declarado y su registro de cambios.
Ninguna comprobacion estadistica de forma (duraciones, pausas, longitudes) MUST sustituir la
verificacion contra la evidencia primaria.

#### Scenario: Acta previa al computo

- **WHEN** se intenta ejecutar la estimacion sobre datos reales de la muestra
- **THEN** existe un acta firmada y fechada que cubre (a) a (d)
- **AND** sin el acta, la estimacion no se ejecuta y el bloqueo se registra

#### Scenario: Planilla cruda con marcas de la herramienta

- **WHEN** se coteja una planilla de etiquetado con su exportacion original
- **THEN** su SHA-256 coincide con el versionado y sus marcas temporales son las que registro la herramienta
- **AND** ninguna marca fue reconstruida ni completada a mano

#### Scenario: Ningun texto redactado o generado

- **WHEN** se coteja la muestra con la constancia de exportacion del marco
- **THEN** cada texto corresponde a un incidente del registro del entorno operativo del propio equipo
- **AND** ningun texto fue redactado por los autores ni generado o asistido por IA, y los cambios de pseudonimizacion constan en su registro

#### Scenario: Forma estadistica no sustituye la evidencia

- **WHEN** se presenta un analisis de la forma de las marcas temporales como prueba de procedencia
- **THEN** no reemplaza el acta del director contra la evidencia primaria

### Requirement: PS-004 — Compuerta etica y legal previa a la extraccion y al envio a terceros

Antes de extraer incidentes, el protocolo SHALL declarar la base de licitud por regimen conforme a la
Ley 25.326: el **regimen (a)** (incidentes reales del entorno operativo del propio equipo,
pseudonimizados) se funda en el **consentimiento informado del grupo** (acta T2, articulo 5 inciso 1)
y en la pseudonimizacion; el **regimen (b)** (reconstrucciones de tipos de incidente reales, sin datos
personales) no requiere base de licitud. El consentimiento escrito previo de cada etiquetador SHALL
obtenerse antes de etiquetar. No hay organizacion adoptante ni autorizacion institucional de terceros:
el tratamiento se realiza en el entorno operativo del propio equipo y su marco. Antes de clasificar la
muestra con el hibrido, los autores SHALL decidir por escrito si los textos se envian a la Gemini API
u otro tercero, con que pseudonimizacion y con que instrumento de transferencia y base de licitud; sin
esa decision, ningun texto MUST enviarse. Si se decide no enviarlos, la estimacion del hibrido sobre
la muestra SHALL declararse no realizada. El repositorio publico SHALL contener solo material
pseudonimizado y consentido; el resto queda en custodia del director con su hash publicado.

#### Scenario: Consentimiento del grupo antes de extraer

- **WHEN** se solicita la exportacion del marco del periodo
- **THEN** existe el acta T2 con el consentimiento informado del grupo y la base de licitud por regimen declarada
- **AND** cada etiquetador firmo su consentimiento antes de etiquetar

#### Scenario: Envio a la Gemini API decidido antes de clasificar

- **WHEN** se va a clasificar la muestra con el hibrido
- **THEN** existe la decision escrita sobre el envio a la Gemini API con su pseudonimizacion, instrumento y base de licitud
- **AND** sin esa decision no se envia ningun texto

#### Scenario: Publicacion limitada

- **WHEN** se versiona material de la muestra
- **THEN** solo entra material pseudonimizado y consentido
- **AND** el resto queda fuera del repositorio con su SHA-256 publicado

### Requirement: PS-005 — Referencia de la muestra por el protocolo de mayoria

La referencia de la muestra probabilistica SHALL construirse con el protocolo de referencia por
mayoria de `evaluation-majority-reference` (change `c-230`): al menos tres etiquetadores
independientes, ciegos a las predicciones, con la regla de mayoria y el tratamiento de los casos
`sin_mayoria` declarados antes de etiquetar, sin arbitro unico de respaldo. Los etiquetadores SHALL
registrarse con alias nuevos (a partir de `E6`), sin reutilizar alias previos del registro de sujetos,
y el registro MUST NOT contener nombres, correos ni legajos.

#### Scenario: Referencia por mayoria

- **WHEN** se construye la referencia de la muestra
- **THEN** proviene del protocolo de mayoria con su regla declarada antes de etiquetar
- **AND** ningun caso se resuelve por la decision de un unico etiquetador

#### Scenario: Alias nuevos

- **WHEN** se registran los etiquetadores de la muestra
- **THEN** sus alias empiezan en `E6` y no reutilizan alias previos
- **AND** ninguna fila contiene datos personales

### Requirement: PS-009 — Corpus probabilistico acreditado

Se SHALL denominar **corpus probabilistico acreditado** al conjunto de casos de la muestra
probabilistica que cumple a la vez: seleccion conforme a PS-001 y PS-002; compuerta de procedencia
(PS-003) cerrada con acta; compuerta etica y legal (PS-004) cerrada; y referencia construida por el
protocolo de mayoria (PS-005, `evaluation-majority-reference`). El corpus SHALL versionarse (o, si el
consentimiento del grupo no permite publicarlo, custodiarse con su SHA-256 publicado) con un manifiesto que
declare, por caso, su estrato, su probabilidad de inclusion, su referencia y su `origen`, y la fecha
del acta. Solo ese corpus MAY usarse como conjunto retenido de evaluacion por este change y por los
changes que lo consumen; un conjunto al que le falte alguna condicion MUST NOT llamarse ni usarse
como corpus probabilistico acreditado.

#### Scenario: Las cuatro condiciones se cumplen

- **WHEN** se publica el manifiesto del corpus probabilistico acreditado
- **THEN** declara la seleccion, el acta de procedencia, la documentacion etica y legal y la referencia por mayoria, con fechas
- **AND** cada caso lleva estrato, probabilidad de inclusion, referencia y `origen`

#### Scenario: Falta una condicion

- **WHEN** alguna compuerta esta abierta o falta la referencia por mayoria
- **THEN** el conjunto no se denomina corpus probabilistico acreditado
- **AND** no se usa como conjunto retenido de evaluacion

### Requirement: PS-006 — Estimacion ponderada referida al universo

La estimacion de las metricas de clasificacion sobre el corpus probabilistico acreditado (PS-009) SHALL ponderarse por el inverso de la probabilidad de
inclusion (Horvitz-Thompson) y, cuando se disponga de los totales del universo, por
post-estratificacion a ellos. Las metricas ponderadas SHALL referirse al universo del periodo del
entorno operativo del propio equipo e informarse con un IC bootstrap estratificado sobre el universo
completo, sin excluir casos (los `sin_mayoria` entran con su tratamiento declarado). La lectura sin ponderar SHALL
informarse junto a la ponderada, rotulada, y MUST NOT presentarse como estimacion poblacional. La
ponderacion SHALL declarar la procedencia de sus pesos.

#### Scenario: Pesos y referencia al universo

- **WHEN** se calcula la exactitud estricta ponderada
- **THEN** los pesos provienen de la probabilidad de inclusion o de la post-estratificacion a los totales del universo
- **AND** la metrica se rotula como referida al universo del periodo

#### Scenario: Intervalo sobre el universo completo

- **WHEN** se estima el IC de la metrica ponderada
- **THEN** se calcula sobre todos los casos de la muestra, sin exclusiones
- **AND** se declaran el metodo, el nivel y la semilla

### Requirement: PS-007 — Efecto de diseno reportado

La estimacion SHALL reportar el DEFF de Kish del estimador ponderado junto con la exactitud
ponderada. Mientras la muestra probabilistica no exista, el DEFF del diseno SHALL declararse no
computable, con su motivo y estado `condicional`, sin consignar un valor estimado. El DEFF de un
control sobre una muestra por conveniencia MUST NOT presentarse como DEFF del diseno.

#### Scenario: DEFF con su procedencia

- **WHEN** se lee el resultado de la estimacion ponderada sobre la muestra
- **THEN** figura el DEFF con su metodo y la procedencia de los pesos

#### Scenario: DEFF no computable declarado

- **WHEN** la muestra probabilistica no existe
- **THEN** el DEFF del diseno se declara no computable y `condicional`
- **AND** no se consigna ningun valor estimado en su lugar

### Requirement: PS-008 — Herramienta offline verificada sin datos retirados

Las funciones de ponderacion, DEFF e IC SHALL producirse por un script de solo lectura bajo
`evaluation/data/campana/analisis/`, con pruebas de sus funciones puras escritas ANTES de la
implementacion. El script MUST NOT invocar a Gemini, a la red ni a un servicio externo, MUST NOT
modificar el corpus, las predicciones ni ningun valor canonico, y SHALL producir salidas identicas
byte a byte en dos corridas. Antes de escribir, SHALL superar dos verificaciones: (1) un oraculo
sintetico, rotulado `sintetico` en su fixture y en sus salidas, con valores esperados calculados a
mano; y (2) un control de sanidad sobre el corpus de 200 casos, en el que post-estratificar con su
propia composicion por sector reproduce la exactitud cruda `147/200 = 0,7350` y un DEFF igual a `1`,
leyendo `data/corpus_evaluacion_pseudonimizado.json` y `evaluation/data/campana/predicciones_in_sample.json`.
Si alguna falla, SHALL terminar con codigo distinto de cero sin escribir salidas. El script MUST NOT
leer ningun artefacto retirado del ejemplar por `c-235`, y el control de sanidad MUST NOT presentarse
como estimacion poblacional ni como DEFF del diseno.

#### Scenario: Oraculo sintetico reproducido

- **WHEN** el script corre sobre el fixture sintetico
- **THEN** reproduce los pesos, la exactitud ponderada y el DEFF calculados a mano
- **AND** las salidas rotulan el fixture como sintetico

#### Scenario: Control de sanidad sobre el corpus de 200

- **WHEN** el script post-estratifica el corpus de 200 con su propia composicion
- **THEN** obtiene `0,7350` (`147/200`) y DEFF `1`
- **AND** si no lo obtiene, termina con codigo distinto de cero sin escribir

#### Scenario: Solo lectura, determinismo y sin red

- **WHEN** el script se ejecuta dos veces
- **THEN** las salidas son identicas byte a byte
- **AND** no hay llamadas de red ni a Gemini, y `git status` no muestra archivos modificados fuera de las salidas declaradas

#### Scenario: Funciones puras probadas antes de implementar

- **WHEN** se revisa el desarrollo del script
- **THEN** las pruebas existieron antes que el modulo
- **AND** cubren pesos iguales y desiguales, cuotas proporcionales y no proporcionales, un estrato censado y DEFF mayor que 1
