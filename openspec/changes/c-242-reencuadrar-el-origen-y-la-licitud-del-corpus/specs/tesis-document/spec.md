<!--
  Delta de c-242 sobre la capacidad `tesis-document`.

  CRITICO (fusion/archivado): cada bloque `## MODIFIED Requirements` reproduce el
  texto COMPLETO del requisito vigente en `openspec/specs/tesis-document/spec.md` y
  TODOS sus escenarios actuales; el archivado rechaza un MODIFIED que omita un
  escenario presente. Los headers `### Requirement:` se copian IDENTICOS (la fusion
  busca por texto). Los requisitos MODIFIED existen en main: fueron agregados por
  c-240 (ya archivado el 2026-11-17) salvo "Base de licitud conforme a la Ley 25.326"
  y "Consistencia..."/"Validez externa...", que son anteriores.

  El requisito ADDED es de documento (no hay implementacion de codigo). El cambio de
  comportamiento es a nivel de spec, por lo que no aplica `skip_specs`.
-->

## ADDED Requirements

### Requirement: Encuadre honesto del origen del corpus y del entorno de estudio

El documento SHALL declarar de forma explicita que la organizacion mediana del sector
servicios con sede en la provincia de Mendoza, de aproximadamente 120 usuarios internos
distribuidos en cinco areas funcionales, es un **escenario de referencia narrativo** y MUST
NOT presentarla como una organizacion real que haya adoptado el sistema. En consecuencia, el
documento MUST NOT afirmar como hecho: (i) la existencia de una organizacion adoptante real;
(ii) la existencia o el aval de una carta de autorizacion emitida por una organizacion
adoptante; (iii) la notificacion de los 120 empleados mediante comunicacion interna formal;
ni (iv) que los incidentes del corpus hayan sido reportados a la mesa de ayuda de una
organizacion real distinta del entorno operativo del propio equipo. El documento SHALL
declarar que el corpus de 200 casos es una mezcla de dos regimenes: el **regimen (a)**,
incidentes reales del entorno operativo del propio equipo, pseudonimizados; y el **regimen
(b)**, reconstrucciones de tipos de incidente reales construidas a partir de la practica,
sin datos de terceros. La declaracion SHALL preservar como vigentes y verdaderos el sistema
implementado, las campanas de medicion, los participantes identificados por alias (E1, E2,
O1, O2 y el operador con debriefing), su consentimiento documentado y la pseudonimizacion.
La reformulacion exacta de la descripcion del escenario y el tratamiento de las cifras
asociadas (aproximadamente 120 usuarios, 42 incidentes diarios, universo proyectado 2.646) en
§1.1, §1.2, §1.8, §4.1, §8.2 y §9.1 SHALL quedar ratificados por los autores y por el
director (compuertas del change) antes de escribir el texto. El texto MUST NOT contener
nombres reales ni la correspondencia alias-identidad.

#### Scenario: Escenario declarado como no real

- **WHEN** se lee cualquier pasaje que describe la organizacion del estudio (en particular §1.1, §1.2 y §1.8 de `01-introduccion.tex`)
- **THEN** el escenario se presenta como un escenario de referencia narrativo
- **AND** no se afirma que sea una organizacion real ni una organizacion adoptante real

#### Scenario: Sin organizacion adoptante real ni aval inexistente

- **WHEN** se busca en los `.tex` una "organizacion adoptante" real, una "carta de autorizacion" emitida por ella o la notificacion de 120 empleados
- **THEN** el documento no afirma la existencia de esos hechos
- **AND** si el texto menciona la organizacion adoptante, la presenta como un rol funcional generico futuro

#### Scenario: Corpus declarado como mezcla de dos regimenes

- **WHEN** se lee la descripcion del corpus en la introduccion y en el marco metodologico
- **THEN** el texto declara que el corpus mezcla el regimen (a) (incidentes reales del entorno operativo del propio equipo, pseudonimizados) y el regimen (b) (reconstrucciones de tipos de incidente reales, sin datos de terceros)
- **AND** distingue el caracter de cada regimen respecto de los datos personales

#### Scenario: Lo verdadero preservado

- **WHEN** se compara el reencuadre con la version previa del documento
- **THEN** siguen declarados como reales el sistema implementado, las campanas de medicion, los participantes (E1, E2, O1, O2 y el operador con debriefing), su consentimiento documentado y la pseudonimizacion
- **AND** ningun valor canonico del sistema o de las campanas cambia

#### Scenario: Validez externa y escenario representativo reencuadrados

- **WHEN** se leen §8.2 (`08-discusion.tex`) y §9.1 (`09-conclusiones.tex`)
- **THEN** la amenaza a la validez externa se declara sobre un unico entorno operativo presentado como escenario de referencia narrativo
- **AND** no se sostiene que los datos provengan de una organizacion real

#### Scenario: Ratificacion de autores y director registrada

- **WHEN** se compara la redaccion del encuadre con la tabla de compuertas de `dictamen-correcciones.md`
- **THEN** figuran la ratificacion de los autores y el visto bueno del director, con fecha y responsable
- **AND** sin esa ratificacion, las tareas que escriben esos pasajes quedan bloqueadas

## MODIFIED Requirements

### Requirement: Base de licitud conforme a la Ley 25.326

La seccion 11.2 SHALL fundar la licitud del tratamiento de los datos que la tesis
efectivamente trata en una base de la Ley 25.326, y MUST NOT invocarla como si existiera una
relacion de empleo inexistente. Como el escenario de referencia NO es una organizacion real y
el estudio NO tiene organizacion empleadora, la subseccion SHALL dejar de fundar el
tratamiento en el articulo 5, inciso 2, apartado d) de la Ley 25.326 para los datos del
estudio: los datos del regimen (a) del corpus SHALL fundarse en el consentimiento informado
del grupo (articulo 5, inciso 1) y en la pseudonimizacion; los datos del regimen (b)
(reconstrucciones sin datos personales) no requieren base de licitud. El articulo 5, inciso
2, apartado d) MAY seguir citandose solo como la base que corresponderia a una organizacion
adoptante real en su tratamiento operativo de datos de empleados (tratamiento T3), presentada
de forma condicional, y MUST NOT presentarse como la base vigente del trabajo. El documento
MUST NOT invocar el "legitimo interes de la organizacion" como base autonoma de licitud, por
ser una figura del Reglamento General de Proteccion de Datos (art. 6.1.f) que no existe como
tal en la Ley 25.326. La asignacion exacta de la base por regimen SHALL quedar ratificada por
los autores antes de escribirla (compuertas del change).

#### Scenario: Base legal citada

- **WHEN** se lee el pasaje que enuncia el principio de licitud en 11.2
- **THEN** el texto declara la base de licitud por regimen (consentimiento informado del grupo, articulo 5, inciso 1, para el regimen (a); sin datos personales para el regimen (b))
- **AND** no presenta el articulo 5, inciso 2, apartado d) como la base vigente del estudio
- **AND** si cita esa base de empleador, la presenta como la que corresponderia a una organizacion adoptante real (T3), de forma condicional

#### Scenario: Sin legitimo interes como base autonoma

- **WHEN** se busca la expresion "legitimo interes" en la seccion 11.2
- **THEN** la expresion no aparece como base de licitud del tratamiento
- **AND** el texto no atribuye a la Ley 25.326 una base de licitud que la ley no contempla

#### Scenario: Sin empleador ficticio

- **WHEN** se lee el pasaje de licitud operativa de 11.2
- **THEN** el texto no afirma que exista una organizacion empleadora ni una relacion de empleo
- **AND** no atribuye al estudio el tratamiento operativo de datos de empleados de una organizacion real

### Requirement: Parrafo de licitud y alcance en §7.5 para los datos del corpus retirado

La subseccion `subsec:consentimiento-derechos` de §7.5 (`11-aspectos-legales.tex`) SHALL
contener un parrafo con la base de licitud y el alcance de la autorizacion de los datos del
corpus independiente retirado (los textos que en las versiones 1.3.0 a 1.5.2 se presentaron
como de una tercera organizacion). El parrafo SHALL declarar de forma explicita: (i) los
textos del corpus retirado no contenian datos de una tercera organizacion ni datos personales
— eran reconstrucciones de tipos de incidente reales construidas por los autores — y fueron
retirados del repositorio publico y de la tesis; (ii) por lo tanto no corresponde autorizacion
ni base de licitud de terceros; (iii) la transferencia de esos textos a la Gemini API se
registra en §7.3 (`subsec:transferencia-internacional`); y (iv) la base de licitud de los
datos que SI se conservan (corpus de 200 pseudonimizado y campana complementaria). La clausula
(iv) SHALL declarar la base de licitud por regimen del corpus conservado y distinguirla: el
regimen (a) (incidentes reales del entorno operativo del propio equipo, pseudonimizados) se
funda en el consentimiento informado del grupo (articulo 5, inciso 1 de la Ley 25.326) y en la
pseudonimizacion; el regimen (b) (reconstrucciones de tipos de incidente reales, sin datos
personales) no requiere base de licitud. La clausula (iv) MUST NOT colapsar ambos regimenes en
una unica invocacion generica del articulo 5 con el consentimiento informado, MUST NOT fundar
en el consentimiento un regimen que no lo requiera y MUST NOT reproducir la base de empleador
(articulo 5, inciso 2, apartado d) como base del corpus conservado. La base que la subseccion
atribuya al regimen (a) y el tratamiento del regimen (b) SHALL ser consistentes con §7.2
(`subsec:principios-datos`). La asignacion exacta de la base por regimen y la redaccion final
de (iv) SHALL quedar ratificada por los autores antes de escribirla (compuertas del change).
El contenido factual SHALL quedar respaldado por la respuesta registrada de los autores
(compuertas P4 y P8 de c-235, reabiertas por este change); sin esa respuesta, la tarea que
escribe el parrafo queda bloqueada. El parrafo MUST NOT resolverse por omision y MUST NOT
contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Parrafo presente

- **WHEN** se lee §7.5 tras aplicar el change
- **THEN** existe un parrafo de licitud y alcance del corpus retirado
- **AND** declara el retiro del repositorio publico y la ausencia de datos de terceros

#### Scenario: Sin datos de terceros y retiro declarados

- **WHEN** se lee el parrafo de licitud
- **THEN** declara que los textos retirados no contenian datos de terceros ni personales
- **AND** que fueron retirados del repositorio publico y de la tesis
- **AND** que no corresponde autorizacion ni base de licitud de terceros

#### Scenario: Transferencia y licitud de lo conservado

- **WHEN** se lee el parrafo de licitud
- **THEN** remite a §7.3 para la transferencia de los textos a la Gemini API
- **AND** declara la base de licitud de los datos que se conservan (Ley 25.326, articulo citado)

#### Scenario: Bases de licitud distinguidas por regimen

- **WHEN** se lee la clausula (iv) de licitud de los datos conservados en §7.5
- **THEN** la base de licitud se declara por regimen: el regimen (a) en el consentimiento informado del grupo (articulo 5, inciso 1) y la pseudonimizacion; el regimen (b) sin base de licitud por no contener datos personales
- **AND** no se colapsan ambos regimenes en una unica invocacion generica del articulo 5 con consentimiento
- **AND** no se funda en el consentimiento un regimen que no lo requiera
- **AND** no se reproduce la base de empleador (articulo 5, inciso 2, apartado d) como base del corpus conservado

#### Scenario: Coherencia con §7.2

- **WHEN** se comparan §7.2 (`subsec:principios-datos`) y §7.5 (`subsec:consentimiento-derechos`)
- **THEN** la base declarada para el regimen (a) y el tratamiento del regimen (b) son los mismos en ambas subsecciones
- **AND** §7.5 no atribuye al corpus conservado una base distinta de la que §7.2 declara

#### Scenario: Respaldo registrado

- **WHEN** se compara cada frase factual del parrafo con la tabla de compuertas de `dictamen-correcciones.md`
- **THEN** cada afirmacion tiene una respuesta de autores registrada con fecha
- **AND** sin respuesta, el parrafo no se escribe (tarea bloqueada)

### Requirement: §1.8 veraz: una sola organizacion y validacion dentro de la muestra

La subseccion `subsec:alcance-delimitaciones` de §1.8 (`01-introduccion.tex`) SHALL quedar
veraz despues del retiro de la validacion fuera de muestra (c-235): la frase que describe el
corpus de la validacion SHALL retirarse o reescribirse para que la validacion experimental se
presente como realizada dentro de la muestra sobre el entorno operativo del propio equipo,
presentado como escenario de referencia narrativo (sector servicios, provincia de Mendoza), y
MUST NOT afirmar que la validacion (incluida la fuera de muestra retirada) se realizo sobre un
corpus de una organizacion real de Mendoza ni sobre una segunda organizacion. §1.8 MUST NOT
mencionar el corpus fuera de muestra ni la validacion retirada, salvo una remision unica a la
nota de versiones si el texto lo requiere; en caso de remitir, SHALL ser la misma remision
unica exigida para el cuerpo. La delimitacion geografica a un unico entorno de la provincia de
Mendoza SHALL conservarse como limitacion de validez externa vigente, sin presentarla como una
organizacion real. El tratamiento de las cifras del escenario (aproximadamente 120 usuarios,
cinco areas, 42 incidentes diarios) SHALL quedar ratificado por los autores antes de escribir
el texto (compuertas del change).

#### Scenario: Frase del corpus reconciliada

- **WHEN** se lee `subsec:alcance-delimitaciones` en `01-introduccion.tex`
- **THEN** la validacion experimental se presenta como dentro de la muestra sobre un unico entorno, declarado como escenario de referencia narrativo
- **AND** no se afirma que la validacion se realizo sobre un corpus de una segunda organizacion
- **AND** no se presenta el entorno como una organizacion real

#### Scenario: Sin corpus fuera de muestra en §1.8

- **WHEN** se buscan en `01-introduccion.tex` las expresiones del corpus fuera de muestra retirado ("corpus independiente", "corpus arbitrado", "fuera de muestra")
- **THEN** no hay coincidencias en §1.8, salvo una remision unica a la nota de versiones

#### Scenario: Limitacion de validez externa conservada

- **WHEN** se lee la delimitacion geografica de §1.8
- **THEN** se conserva el unico entorno de la provincia de Mendoza como limitacion de validez externa vigente
- **AND** no cambia ningun valor numerico

### Requirement: Consistencia de la descripcion de la organizacion adoptante

El escenario organizacional SHALL describirse de forma consistente a lo largo del documento
—la misma denominacion y los mismos atributos (un unico escenario de caracter narrativo, del
sector servicios, de aproximadamente 120 usuarios internos, cinco areas funcionales, con sede
en la provincia de Mendoza)— en todos los pasajes que lo mencionan, y SHALL presentarse como
un escenario de referencia narrativo y NO como una organizacion adoptante real. Si los
autores ratifican otro tratamiento del escenario (por ejemplo, retirar o ajustar las cifras
del escenario), el texto SHALL aplicarlo de forma consistente en todos esos pasajes.

#### Scenario: Denominacion unificada
- **WHEN** se leen las secciones 1.2 y 1.8 (`01-introduccion.tex`)
- **THEN** ambos pasajes describen el escenario organizacional con la misma denominacion
- **AND** no alternan entre "una organizacion mediana" y "una unica organizacion" como si fueran caracterizaciones distintas

#### Scenario: Atributos consistentes
- **WHEN** se compara la caracterizacion del escenario en 1.2 y 1.8
- **THEN** los atributos coinciden (sector servicios, aproximadamente 120 usuarios, cinco areas, Mendoza) o el tratamiento ratificado por los autores se aplica de forma consistente
- **AND** no se introduce un nombre propio no autorizado ni atributos contradictorios

#### Scenario: Escenario no presentado como organizacion real

- **WHEN** se lee cualquier pasaje que describe el escenario organizacional
- **THEN** se presenta como un escenario de referencia narrativo
- **AND** no se afirma que sea una organizacion adoptante real

### Requirement: Validez externa declarada en las conclusiones con su remedio empirico

Las conclusiones SHALL declarar la amenaza a la validez externa con la fuerza que el diseno
permite: la muestra es **no probabilistica por conveniencia** (los 200 casos son los
incidentes cronometrados), proviene de **un unico entorno operativo** (sector servicios,
provincia de Mendoza; presentado como escenario de referencia narrativo, NO como una
organizacion real) y el universo es **proyectado, no medido** (`2.646 = 42 x 63`), de modo que
las cifras valen para este corpus y no se extrapolan al universo de incidentes. La declaracion
SHALL senalar que el remedio empirico es el **diseno de muestreo probabilistico del universo**
(change `c-229`), SHALL presentarlo como **condicional y no ejecutado** y MUST NOT afirmar que
la validez externa ya fue establecida. La correccion MUST NOT cambiar el valor de ningun
numero canonico, salvo lo que los autores ratifiquen sobre la proyeccion del universo
(compuertas del change).

#### Scenario: Fuerza correcta en la conclusion

- **WHEN** se leen las conclusiones (`09-conclusiones.tex`)
- **THEN** el texto declara la muestra no probabilistica por conveniencia, el unico entorno operativo (escenario de referencia narrativo) y el universo proyectado (`2.646 = 42 x 63`)
- **AND** las cifras se declaran validas para este corpus y no extrapolables al universo

#### Scenario: Remedio empirico declarado como condicional

- **WHEN** se lee la declaracion de validez externa
- **THEN** remite al diseno de muestreo probabilistico (change `c-229`) como remedio empirico
- **AND** lo presenta como condicional y no ejecutado, sin afirmar que la validez externa ya esta establecida

#### Scenario: Valores canonicos intactos

- **WHEN** se compara el `.tex` antes y despues del change
- **THEN** ningun valor canonico cambia de valor
- **AND** las unicas diferencias son palabras y remisiones de procedencia

#### Scenario: Sin organizacion real en la conclusion

- **WHEN** se lee la declaracion de validez externa de las conclusiones
- **THEN** no se presenta el entorno como una organizacion real ni como una organizacion adoptante
- **AND** la limitacion se declara sobre el escenario de referencia narrativo

### Requirement: Retiro decidido de los textos del corpus independiente del repositorio publico

La disposicion de los textos del corpus independiente publicados en el repositorio publico
(`evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`)
SHALL ser el RETIRO, decision de los autores registrada en
`docs/Tesis/Correcciones/dictamen-correcciones.md` con fecha y responsable, alineada con «Si
la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». Los
textos SHALL eliminarse del repositorio publico (en un commit propio separado, con el ajuste
de las tres pruebas y las sumas SHA-256 segun OOS-027) y de la tesis (por c-235). Los bytes
MAY conservarse en un archivo PRIVADO fuera del repositorio, con sus SHA-256 citados en la
tesis como trazabilidad; el repositorio publico MUST NOT volver a alojarlos como evidencia
vigente. La tesis (por §7.5) y el repositorio SHALL ser coherentes: ningun archivo de la tesis
ni del repositorio SHALL seguir alojando esos textos como evidencia vigente. El retiro SHALL
mantenerse y MUST NOT interpretarse como una reintroduccion de la validacion fuera de muestra
retirada: el reencuadre del origen del corpus NO reincorpora esos textos ni esa validacion
como evidencia vigente. Los textos retirados SHALL describirse como reconstrucciones de tipos
de incidente reales (el mismo caracter que el regimen (b) del corpus conservado), sin alterar
la decision de retiro.

#### Scenario: Decision registrada

- **WHEN** se lee la entrada de este change en `dictamen-correcciones.md`
- **THEN** figura la decision de retirar los textos del repositorio publico con fecha y responsable

#### Scenario: Retiro del repositorio y de la tesis

- **WHEN** se aplica el retiro
- **THEN** los archivos del corpus independiente se eliminan del repositorio publico
- **AND** ningun archivo de la tesis los aloja como evidencia vigente

#### Scenario: Trazabilidad sin publicacion

- **WHEN** los autores conservan los bytes en un archivo privado
- **THEN** el archivo privado queda fuera del repositorio
- **AND** la tesis cita los SHA-256 como trazabilidad sin publicar el contenido

#### Scenario: Coherencia entre tesis y repositorio

- **WHEN** se compara §7.5 con los archivos del repositorio
- **THEN** §7.5 declara el retiro y el repositorio ya no aloja los textos

#### Scenario: Retiro no revertido por el reencuadre

- **WHEN** se compara el reencuadre del origen del corpus con la decision de retiro
- **THEN** la validacion fuera de muestra retirada no reaparece como evidencia vigente en la tesis ni en el repositorio
- **AND** los textos retirados se describen como reconstrucciones de tipos de incidente reales, coherentes con el tratamiento del regimen (b) del corpus conservado
