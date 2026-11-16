## ADDED Requirements

### Requirement: Parrafo de licitud y alcance en §7.5 para los datos del corpus retirado

La subseccion `subsec:consentimiento-derechos` de §7.5 (`11-aspectos-legales.tex`) SHALL contener un parrafo con la base de licitud y el alcance de la autorizacion de los datos del corpus independiente retirado (los textos que en las versiones 1.3.0 a 1.5.2 se presentaron como de una tercera organizacion). El parrafo SHALL declarar de forma explicita: (i) los textos del corpus retirado no contenian datos de una tercera organizacion ni datos personales — eran descripciones genericas de incidentes construidas por los autores — y fueron retirados del repositorio publico y de la tesis; (ii) por lo tanto no corresponde autorizacion ni base de licitud de terceros; (iii) la transferencia de esos textos a la Gemini API se registra en §7.3 (`subsec:transferencia-internacional`); y (iv) la base de licitud de los datos que SI se conservan (corpus de 200 pseudonimizado y campana complementaria) sigue siendo la declarada conforme a la Ley 25.326 (con cita del articulo). El contenido factual SHALL quedar respaldado por la respuesta registrada de los autores (compuertas P4 y P8 de c-235, reabiertas por este change); sin esa respuesta, la tarea que escribe el parrafo queda bloqueada. El parrafo MUST NOT resolverse por omision y MUST NOT contener nombres reales ni la correspondencia alias-identidad.

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

### Requirement: Retiro decidido de los textos del corpus independiente del repositorio publico

La disposicion de los textos del corpus independiente publicados en el repositorio publico (`evaluation/data/campana/corpus_independiente.json` y `corpus_independiente_arbitrado.json`) SHALL ser el RETIRO, decision de los autores registrada en `docs/Tesis/Correcciones/dictamen-correcciones.md` con fecha y responsable, alineada con «Si la autorizacion no existe, retirar los textos del repositorio publico y de la tesis». Los textos SHALL eliminarse del repositorio publico (en un commit propio separado, con el ajuste de las tres pruebas y las sumas SHA-256 segun OOS-027) y de la tesis (por c-235). Los bytes MAY conservarse en un archivo PRIVADO fuera del repositorio, con sus SHA-256 citados en la tesis como trazabilidad; el repositorio publico MUST NOT volver a alojarlos como evidencia vigente. La tesis (por §7.5) y el repositorio SHALL ser coherentes: ningun archivo de la tesis ni del repositorio SHALL seguir alojando esos textos como evidencia vigente.

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
