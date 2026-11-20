## ADDED Requirements

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
