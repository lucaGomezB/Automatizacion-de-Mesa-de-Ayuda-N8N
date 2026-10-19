## MODIFIED Requirements

### Requirement: SGD-010 — Registro de actividades de tratamiento (ROPA)

El proyecto SHALL incluir `docs/seguridad/registro-actividades-tratamiento.md` como registro de actividades de tratamiento (ROPA) segun la Ley 25.326. El registro MUST describir, por cada actividad de tratamiento (al menos: gestion de incidentes, directorio de empleados y clasificacion automatica), la finalidad, las categorias de datos y de titulares, los destinatarios o encargados (Gemini, Twilio, Microsoft, N8N), las transferencias internacionales y el plazo de conservacion. El registro MUST senalar las transferencias a Estados Unidos como pais NO adecuado y el instrumento requerido, y MUST mencionar la inscripcion de bases de datos (arts. 21 y 24) como evaluacion pendiente de la organizacion adoptante. Los plazos de conservacion del registro MUST ser consistentes con el capitulo 11 de la tesis: los incidentes se conservan 12 meses rodantes desde su creacion y luego se someten a anonimizacion irreversible; los registros de ejecucion del sistema se conservan 30 dias; los datos del directorio se conservan mientras la relacion laboral este activa mas 1 ano. El registro MUST NOT declarar "conservacion indefinida" para los incidentes.

#### Scenario: El ROPA describe las actividades de tratamiento

- **WHEN** se lee `docs/seguridad/registro-actividades-tratamiento.md`
- **THEN** cada actividad de tratamiento del sistema describe finalidad, categorias de datos/titulares, destinatarios y conservacion

#### Scenario: Las transferencias internacionales quedan registradas

- **WHEN** se lee el ROPA
- **THEN** las transferencias a Estados Unidos aparecen como pais no adecuado con el instrumento requerido (clausulas modelo o consentimiento)

#### Scenario: La conservacion de incidentes es consistente con la tesis

- **WHEN** se lee el plazo de conservacion de los incidentes en el ROPA
- **THEN** figura 12 meses rodantes con anonimizacion irreversible posterior, alineado con el capitulo 11, y NO figura "conservacion indefinida"

### Requirement: SGD-011 — Regla de lenguaje y encuadre de alineacion (transversal)

Todos los documentos de `docs/seguridad/` SHALL usar el lenguaje de **"alineado con"** y **"controles mapeados a"** al referirse a ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701, NIST CSF 2.0 y la Ley 25.326. Los documentos MUST NOT afirmar que el sistema esta "certificado", es "compliant" ni "cumple" los marcos. Los documentos MUST presentar los controles de tipo organizacional (O) y fisico como responsabilidad de la organizacion adoptante, no como controles implementados por el repositorio, y MUST indicar que la documentacion no constituye una certificacion ni una auditoria formal. La misma regla de lenguaje SHALL aplicarse a `knowledge-base/`: sus documentos MUST NOT describir el sistema como "compliant", como que "cumple" la Ley 25.326, ISO o NIST, ni como certificado; MUST usar el lenguaje de alineacion.

#### Scenario: El lenguaje de alineacion se usa consistentemente

- **WHEN** se revisan los documentos de `docs/seguridad/`
- **THEN** usan "alineado con" o "controles mapeados a" y no afirman certificacion ni conformidad

#### Scenario: Los controles organizacionales se encuadran como externos

- **WHEN** se lee un documento que menciona controles organizacionales o fisicos
- **THEN** los presenta como responsabilidad de la organizacion adoptante, no como implementados por el repositorio

#### Scenario: La documentacion aclara que no es certificacion

- **WHEN** se lee el indice o cualquier documento de la carpeta
- **THEN** se declara que la documentacion es de alineacion y no constituye certificacion ni auditoria formal

#### Scenario: La base de conocimiento no afirma conformidad

- **WHEN** se revisan los documentos de `knowledge-base/`
- **THEN** no contienen los terminos "compliant", "cumple la Ley 25.326", "cumple ISO" ni "certificado" al describir el sistema, y usan el lenguaje de alineacion

## ADDED Requirements

### Requirement: SGD-013 — Procedimiento ARCO documentado con plazos

El proyecto SHALL incluir `docs/seguridad/procedimiento-arco.md` como procedimiento operativo para el ejercicio de los derechos del titular. El documento MUST describir el canal por el que el titular presenta una solicitud, la funcion responsable de recibirla y resolverla (el responsable de proteccion de datos de la organizacion adoptante, sin nombrar personas), las acciones a ejecutar por derecho (acceso; rectificacion, actualizacion y supresion) y los plazos legales aplicables: acceso en 10 dias corridos (art. 14) y rectificacion/actualizacion/supresion en 5 dias habiles (art. 16). El canal es INFORMADO: el documento MUST NOT exigir ni introducir un endpoint backend de solicitudes ARCO. El documento MUST NOT atribuir a la Ley 25.326 vigente un derecho autonomo de oposicion. El documento MUST indicar que la solicitud y su resolucion dejan constancia auditable y MUST referenciar el canal informado en la superficie de privacidad en runtime. El documento MUST usar el lenguaje de alineacion y MUST NOT declarar certificacion.

#### Scenario: El procedimiento define canal y responsable

- **WHEN** se lee `docs/seguridad/procedimiento-arco.md`
- **THEN** describe el canal de presentacion de la solicitud y la funcion responsable de resolverla

#### Scenario: Los plazos son los legales correctos

- **WHEN** se leen los plazos del procedimiento
- **THEN** el acceso figura a 10 dias corridos (art. 14) y la rectificacion/actualizacion/supresion a 5 dias habiles (art. 16)

#### Scenario: No se atribuye un derecho autonomo de oposicion

- **WHEN** se lee la seccion de derechos del procedimiento
- **THEN** no se atribuye a la ley vigente un derecho autonomo de oposicion; el acronimo ARCO se encuadra como de practica comparada

#### Scenario: La resolucion deja constancia auditable

- **WHEN** se lee el procedimiento
- **THEN** indica que la solicitud, su tramite y su resolucion quedan registrados de forma auditable

#### Scenario: El canal es informado y no exige endpoint backend

- **WHEN** se lee la forma de presentar una solicitud
- **THEN** se describe un canal informado (la funcion responsable de proteccion de datos) con constancia auditable, y no se introduce ni se exige un endpoint backend de solicitudes ARCO

### Requirement: SGD-014 — Instrumento de transferencia internacional documentado

El proyecto SHALL incluir `docs/seguridad/instrumento-transferencia-internacional.md` que documente el mecanismo de transferencia internacional de datos hacia los proveedores con sede en Estados Unidos. El documento MUST cubrir la transferencia a Gemini, incluyendo de forma explicita la transcripcion de audio CRUDO que ocurre ANTES de la pseudonimizacion (el audio y los identificadores que contiene cruzan a Estados Unidos antes de cualquier pseudonimizacion, que opera solo sobre el texto), y la transferencia a Twilio (audio crudo y numero telefonico del llamante). El documento MUST declarar que Estados Unidos NO es pais adecuado (art. 12 de la Ley 25.326) y MUST describir los mecanismos habilitantes: consentimiento expreso del titular o clausulas contractuales modelo (Disposicion DNPDP 60/2016; Resolucion AAIP 198/2023), o normas corporativas vinculantes. El documento MUST dejar explicito que la pseudonimizacion previa mitiga el riesgo pero NO sustituye el instrumento. El documento MUST aclarar que documenta el mecanismo y NO implica la firma de contratos ni de clausulas modelo: la suscripcion es una accion organizacional de la organizacion adoptante. El documento MUST NOT declarar el instrumento como suscrito.

#### Scenario: El documento cubre ambas transferencias

- **WHEN** se lee `docs/seguridad/instrumento-transferencia-internacional.md`
- **THEN** describe la transferencia a Gemini (incluida la transcripcion de audio crudo previa a la pseudonimizacion) y la transferencia a Twilio (audio crudo y numero del llamante)

#### Scenario: Estados Unidos queda declarado como pais no adecuado

- **WHEN** se lee el documento
- **THEN** declara que Estados Unidos no integra la lista de paises adecuados (art. 12) y enumera los mecanismos (clausulas modelo o consentimiento expreso)

#### Scenario: La pseudonimizacion no sustituye el instrumento

- **WHEN** se lee el documento
- **THEN** declara que la pseudonimizacion mitiga pero no reemplaza el instrumento de transferencia

#### Scenario: El documento no declara el instrumento como suscrito

- **WHEN** se lee el encuadre del documento
- **THEN** aclara que documenta el mecanismo y que la firma de contratos o clausulas modelo es una accion organizacional, y no afirma que el instrumento este suscrito

### Requirement: SGD-015 — Politica de retencion de logs

El proyecto SHALL incluir `docs/seguridad/politica-retencion-logs.md` que defina la retencion de los registros del sistema por clase de registro, con al menos: los registros de ejecucion del sistema (por ejemplo, N8N) conservados 30 dias; los contadores de tasa por origen del guarda de costo conservados solo durante la ventana del contador. El documento MUST declarar que el numero de origen NO se registra CRUDO en los logs (se emite un identificador derivado no reversible, obtenido con HMAC-SHA-256 y una clave DEDICADA independiente de la clave de pseudonimizacion) y que los datos personales del correo ni el telefono del directorio NO aparecen en claro en los logs. El documento MUST senalar que la centralizacion de logs, el SIEM y la deteccion de anomalias quedan fuera de su alcance (brechas 8.15/8.16 mapeadas a changes separados). El documento MUST usar el lenguaje de alineacion.

#### Scenario: La politica define la retencion por clase de registro

- **WHEN** se lee `docs/seguridad/politica-retencion-logs.md`
- **THEN** cada clase de registro (al menos ejecucion del sistema y contadores de origen) tiene un plazo de retencion definido

#### Scenario: Los registros de ejecucion se conservan 30 dias

- **WHEN** se lee el plazo de retencion de los registros de ejecucion del sistema
- **THEN** figura 30 dias, consistente con el capitulo 11

#### Scenario: El numero de origen no se registra crudo

- **WHEN** se lee la seccion sobre datos personales en logs
- **THEN** declara que el numero de origen no se registra crudo (se usa un identificador derivado) y que su retencion queda acotada a la ventana del contador

#### Scenario: El alcance excluye centralizacion y deteccion

- **WHEN** se lee el encuadre del documento
- **THEN** declara que la centralizacion de logs, el SIEM y la deteccion de anomalias quedan fuera de su alcance
