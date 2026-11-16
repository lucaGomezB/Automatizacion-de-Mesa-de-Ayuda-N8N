## ADDED Requirements

### Requirement: Parrafo de licitud y alcance de la autorizacion en §7.5 para los datos de la tercera organizacion

La subseccion `subsec:consentimiento-derechos` de §7.5 (`11-aspectos-legales.tex`) SHALL contener un parrafo con la base de licitud y el alcance de la autorizacion de los datos del corpus independiente retirado (los textos que en las versiones 1.3.0 a 1.5.2 se presentaron como de una tercera organizacion). El contenido del parrafo SHALL ramificarse por la respuesta registrada de los autores (compuertas P4 y P8 de c-235, reabiertas por este change):

- **(a) Descripciones genericas sin datos de terceros.** Si los autores registran en `dictamen-correcciones.md` que los textos del corpus retirado son descripciones genericas de incidentes que NO contienen datos de terceros ni datos personales, el parrafo SHALL declararlo de forma explicita: no existen datos de una tercera organizacion en esos textos, por lo tanto no hay autorizacion ni base de licitud que declarar, y SHALL remitir a §7.3 (`subsec:transferencia-internacional`) para la transferencia de esos textos a la Gemini API.
- **(b) Datos de terceros o personales.** Si los autores registran que los textos SI contienen datos de terceros o datos personales, el parrafo SHALL declarar la autorizacion escrita de la organizacion, su base de licitud conforme a la Ley 25.326 (con cita del articulo) y el alcance de esa autorizacion (uso, publicacion y transferencia), y SHALL remitir a §7.3 para la transferencia.

El parrafo MUST NOT resolverse por omision: SHALL existir en ambas ramas. El texto MUST NOT contener nombres reales ni la correspondencia alias-identidad. La rama elegida SHALL quedar respaldada por una respuesta de autores registrada con fecha; sin esa respuesta, la tarea que escribe el parrafo queda bloqueada.

#### Scenario: Parrafo presente en ambas ramas

- **WHEN** se lee §7.5 tras aplicar el change
- **THEN** existe un parrafo de licitud y alcance del corpus retirado
- **AND** el parrafo no depende de omitir el tema

#### Scenario: Rama de descripciones genericas

- **WHEN** los autores registraron que los textos son descripciones genericas sin datos de terceros
- **THEN** §7.5 declara que no hay datos de una tercera organizacion y que no se requiere autorizacion ni base de licitud
- **AND** remite a §7.3 para la transferencia a la Gemini API

#### Scenario: Rama de datos de terceros

- **WHEN** los autores registraron que los textos contienen datos de terceros o personales
- **THEN** §7.5 declara la autorizacion escrita, su base de licitud (Ley 25.326, articulo citado) y su alcance (uso, publicacion, transferencia)
- **AND** remite a §7.3 para la transferencia

#### Scenario: Respaldo registrado

- **WHEN** se compara cada frase factual del parrafo con la tabla de compuertas de `dictamen-correcciones.md`
- **THEN** cada afirmacion tiene una respuesta de autores registrada con fecha
- **AND** sin respuesta, el parrafo no se escribe (tarea bloqueada)

### Requirement: §1.8 veraz: una sola organizacion y validacion dentro de la muestra

La subseccion `subsec:alcance-delimitaciones` de §1.8 (`01-introduccion.tex`) SHALL quedar veraz despues del retiro de la validacion fuera de muestra (c-235): la frase que describe el corpus de la validacion SHALL retirarse o reescribirse para que la validacion experimental se presente como realizada dentro de la muestra sobre UNA sola organizacion (servicios, provincia de Mendoza), y MUST NOT afirmar que la validacion (incluida la fuera de muestra retirada) se realizo sobre un corpus de la organizacion de Mendoza ni sobre una segunda organizacion. §1.8 MUST NOT mencionar el corpus fuera de muestra ni la validacion retirada, salvo una remision unica a la nota de versiones si el texto lo requiere; en caso de remitir, SHALL ser la misma remision unica exigida para el cuerpo. La delimitacion geografica a una unica organizacion de la provincia de Mendoza SHALL conservarse como limitacion de validez externa vigente.

#### Scenario: Frase del corpus reconciliada

- **WHEN** se lee `subsec:alcance-delimitaciones` en `01-introduccion.tex`
- **THEN** la validacion experimental se presenta como dentro de la muestra sobre una sola organizacion
- **AND** no se afirma que la validacion se realizo sobre un corpus de una segunda organizacion

#### Scenario: Sin corpus fuera de muestra en §1.8

- **WHEN** se buscan en `01-introduccion.tex` las expresiones del corpus fuera de muestra retirado ("corpus independiente", "corpus arbitrado", "fuera de muestra")
- **THEN** no hay coincidencias en §1.8, salvo una remision unica a la nota de versiones

#### Scenario: Limitacion de validez externa conservada

- **WHEN** se lee la delimitacion geografica de §1.8
- **THEN** se conserva la unica organizacion de la provincia de Mendoza como limitacion de validez externa vigente
- **AND** no cambia ningun valor numerico

### Requirement: Disposicion del repositorio publico decidida y registrada con default alineado a K-02

La disposicion de los textos del corpus independiente publicados en el repositorio publico (`evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`) SHALL ser una decision OBLIGATORIA de los autores, registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` con fecha y responsable. El default alineado a K-02 SHALL ser RETIRAR los textos del repositorio publico y de la tesis (en coherencia con «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis»). Los textos MAY conservarse con el rotulado de OOS-026 UNICAMENTE si los autores registran en `dictamen-correcciones.md` la decision de que los textos son descripciones genericas de incidentes sin datos de terceros; en ese caso la conservacion SHALL documentarse explicitamente como decision de autores. La decision MUST NOT quedar sin registrar, y la tesis (por §7.5) y el repositorio SHALL ser coherentes con la rama elegida: si se retira, ningun archivo de la tesis ni del repositorio SHALL seguir alojando esos textos como evidencia vigente.

#### Scenario: Decision registrada

- **WHEN** se lee la entrada de este change en `dictamen-correcciones.md`
- **THEN** figura la decision de disposicion del repositorio publico con fecha y responsable
- **AND** figura la rama elegida (retiro o conservacion documentada)

#### Scenario: Default K-02 aplicado sin decision contraria

- **WHEN** los autores no registran que los textos son descripciones genericas sin datos de terceros
- **THEN** los textos se retiran del repositorio publico y de la tesis

#### Scenario: Conservacion solo con decision documentada

- **WHEN** los autores conservan los textos
- **THEN** la conservacion esta registrada como decision de autores y documenta que son descripciones genericas sin datos de terceros
- **AND** los archivos conservados estan rotulados segun OOS-026

#### Scenario: Coherencia entre tesis y repositorio

- **WHEN** se compara la rama elegida con §7.5 y con los archivos del repositorio
- **THEN** §7.5 y el repositorio reflejan la misma rama
- **AND** ningun archivo aloja los textos como evidencia vigente si la rama es el retiro
