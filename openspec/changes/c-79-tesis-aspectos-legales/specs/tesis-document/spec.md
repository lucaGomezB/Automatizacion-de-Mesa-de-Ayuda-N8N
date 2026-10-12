## ADDED Requirements

### Requirement: Plazo de conservacion declarado y consistente

La seccion 11.2 del Capitulo 11 (`11-aspectos-legales.tex`) SHALL declarar un plazo de
conservacion unico, explicito y justificado para los incidentes, coherente con la
retencion de logs de ejecucion declarada en `05-arquitectura.tex:44`. El documento MUST
NOT declarar "conservacion indefinida" para los incidentes ni presentar el bloqueo de
escritura sobre tickets cerrados como una politica de retencion.

#### Scenario: Sin conservacion indefinida

- **WHEN** se lee la seccion 11.2 en busca de la politica de retencion de incidentes
- **THEN** el texto declara un plazo de conservacion concreto (expresado en dias, meses o anos)
- **AND** no declara "conservacion indefinida" ni "conservacion permanente" para los incidentes

#### Scenario: Consistencia con la retencion de logs

- **WHEN** se comparan la retencion de incidentes de 11.2 y la retencion de logs de ejecucion de `05-arquitectura.tex:44`
- **THEN** ambas retenciones son compatibles y no se contradicen entre si
- **AND** cualquier diferencia de plazo entre incidentes y logs queda justificada de forma explicita por la finalidad de cada conjunto de datos

#### Scenario: Bloqueo de tickets cerrados no es retencion

- **WHEN** se lee el pasaje que describe los incidentes en estado cerrado
- **THEN** el bloqueo de escritura (PATCH que devuelve 409, C-23) se presenta como control de integridad de auditoria
- **AND** no se presenta como la politica de conservacion ni como sustituto de un plazo de retencion

### Requirement: Base de licitud conforme a la Ley 25.326

La seccion 11.2 SHALL fundar la licitud del tratamiento operativo de los datos de
empleados en una base de la Ley 25.326, citando el articulo 5 inciso 2. El documento
MUST NOT invocar el "legitimo interes de la organizacion" como base autonoma de
licitud, por ser una figura del Reglamento General de Proteccion de Datos (art. 6.1.f)
que no existe como tal en la Ley 25.326.

#### Scenario: Base legal citada

- **WHEN** se lee el pasaje que enuncia el principio de licitud en 11.2
- **THEN** el texto cita la Ley 25.326 articulo 5 inciso 2 como base del tratamiento de datos de empleados
- **AND** el pasaje distingue la base de licitud operativa del consentimiento que se discute para el corpus de investigacion en 11.5

#### Scenario: Sin legitimo interes como base autonoma

- **WHEN** se busca la expresion "legitimo interes" en la seccion 11.2
- **THEN** la expresion no aparece como base de licitud del tratamiento
- **AND** el texto no atribuye a la Ley 25.326 una base de licitud que la ley no contempla

### Requirement: Alcance de la adecuacion europea

La seccion 11.1 SHALL citar el instrumento de adecuacion de la Union Europea respecto de
Argentina (Decision 2003/490/CE, de 30 de junio de 2003) y su revalidacion de enero de
2024. El documento MUST NOT describir los flujos transfronterizos como "bidireccionales"
ni sugerir que la adecuacion habilita la transferencia de Argentina hacia Estados Unidos.

#### Scenario: Instrumento de adecuacion citado

- **WHEN** se lee el pasaje de 11.1 que menciona la adecuacion europea
- **THEN** el texto nombra la Decision 2003/490/CE y su revalidacion de enero de 2024
- **AND** el texto incluye una cita o referencia verificable al instrumento

#### Scenario: Direccion de la adecuacion correcta

- **WHEN** se lee la descripcion del alcance de la adecuacion
- **THEN** el texto afirma que la adecuacion cubre el flujo UE -> Argentina
- **AND** el texto afirma que la transferencia Argentina -> Estados Unidos (Gemini, Twilio) no esta amparada por la adecuacion y requiere un instrumento propio
- **AND** el texto no describe los flujos como "bidireccionales"

### Requirement: Transferencia telefonica previa a la pseudonimizacion

La seccion 11.3 SHALL nombrar al proveedor de telefonia (Twilio) y declarar que el audio
crudo del llamante y su numero telefonico se transfieren a un proveedor con sede en
Estados Unidos antes de cualquier pseudonimizacion. El documento SHALL describir el orden
real (grabar -> transferir/transcribir -> pseudonimizar) y SHALL citar el instrumento de
transferencia internacional del articulo 12 de la Ley 25.326 (consentimiento o clausulas
contractuales modelo). El acuerdo de procesamiento de datos (DPA) MUST NOT presentarse
como sustituto de ese instrumento.

#### Scenario: Twilio y audio crudo declarados

- **WHEN** se lee la seccion 11.3 sobre transferencia internacional
- **THEN** el texto nombra a Twilio como proveedor de telefonia con sede en Estados Unidos
- **AND** el texto declara que el audio crudo del llamante y su numero telefonico se transfieren antes de la pseudonimizacion

#### Scenario: Orden del flujo correcto

- **WHEN** se lee la descripcion del tratamiento del canal telefonico
- **THEN** el orden descrito es grabar, transferir o transcribir, y luego pseudonimizar
- **AND** el texto no afirma una "pseudonimizacion previa a la transmision" para el canal telefonico

#### Scenario: Instrumento del articulo 12 citado

- **WHEN** se lee la justificacion de la transferencia internacional
- **THEN** el texto cita el articulo 12 de la Ley 25.326 y el instrumento aplicable (consentimiento o clausulas contractuales modelo)
- **AND** el DPA del proveedor se menciona como complemento, no como sustituto del instrumento de transferencia

### Requirement: Plazo de respuesta ARCO

Si el Capitulo 11 declara un plazo para el ejercicio de los derechos de rectificacion,
actualizacion o supresion, ese plazo SHALL corresponder a cinco dias habiles conforme al
articulo 16 de la Ley 25.326. El documento MUST NOT declarar el plazo como "cinco dias
corridos".

#### Scenario: Plazo ARCO correcto cuando se declara

- **WHEN** se lee el pasaje que describe los plazos de respuesta a los derechos ARCO
- **THEN** el plazo de rectificacion, actualizacion o supresion se expresa como cinco dias habiles
- **AND** no se expresa como cinco dias corridos
