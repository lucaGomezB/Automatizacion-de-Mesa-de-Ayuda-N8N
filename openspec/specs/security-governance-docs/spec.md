# security-governance-docs Specification

## Purpose
Define los documentos de gobernanza de seguridad y privacidad del proyecto bajo `docs/seguridad/`: politica de seguridad, clasificacion y etiquetado de la informacion, roles y responsabilidades, gestion de incidentes, inventario de activos, requisitos legales, seguridad en el ciclo de desarrollo, privacidad en runtime y registro de actividades de tratamiento. Fija las reglas de lenguaje de alineacion y la trazabilidad a los controles de ISO/IEC 27002:2022, NIST CSF 2.0 y la Ley 25.326, dejando explicito que el stack es de desarrollo local y que los controles organizacionales competen a la organizacion adoptante.

## Requirements

### Requirement: SGD-001 — Ubicacion, indice y trazabilidad de la documentacion

El proyecto SHALL mantener la documentacion de gobernanza de seguridad en `docs/seguridad/`, con un indice `docs/seguridad/README.md`. El indice MUST listar cada documento con su proposito y MUST incluir un mapa de trazabilidad que asocie cada control objetivo (ISO/IEC 27002 5.1, 5.2, 5.9, 5.12, 5.13, 5.19, 5.20, 5.21, 5.22, 5.23, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26 y NIST CSF Govern/Identify) con el documento que lo cubre. El indice MUST declarar que los documentos son **alineados con** los marcos citados y MUST NOT presentarlos como prueba de certificacion. Cada documento de la carpeta MUST ser referenciable desde el indice y las referencias cruzadas entre documentos MUST resolverse a archivos existentes.

#### Scenario: La carpeta y el indice existen

- **WHEN** se inspecciona `docs/seguridad/`
- **THEN** existe `README.md` y los documentos de gobernanza listados por el indice

#### Scenario: El mapa de trazabilidad cubre los controles objetivo

- **WHEN** se lee el mapa de trazabilidad de `docs/seguridad/README.md`
- **THEN** cada control objetivo (5.1, 5.2, 5.9, 5.12, 5.13, 5.19, 5.20, 5.21, 5.22, 5.23, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26) apunta a un documento existente que lo cubre

#### Scenario: Los controles de proveedores quedan mapeados

- **WHEN** se lee el mapa de trazabilidad de `docs/seguridad/README.md`
- **THEN** los controles 5.19 a 5.23 apuntan a `docs/seguridad/evaluacion-seguridad-proveedores.md`

#### Scenario: Las referencias cruzadas resuelven

- **WHEN** un documento de `docs/seguridad/` referencia a otro
- **THEN** el archivo referenciado existe en la carpeta

### Requirement: SGD-002 — Politica de seguridad de la informacion

El proyecto SHALL incluir `docs/seguridad/politica-seguridad-informacion.md`, alineado con ISO/IEC 27002 5.1. La politica MUST declarar su proposito, su alcance (sistema de mesa de ayuda y sus activos de informacion), los principios de seguridad adoptados, y los roles responsables de su aprobacion, comunicacion y revision periodica. La politica MUST reconocer que el repositorio corresponde a un stack de desarrollo local y que los controles organizacionales y fisicos (temas 6.x y 7.x) son responsabilidad de la organizacion adoptante. La politica MUST declarar que el sistema esta **alineado con** el marco y MUST NOT afirmar certificacion ni conformidad.

#### Scenario: La politica declara proposito, alcance y principios

- **WHEN** se lee `docs/seguridad/politica-seguridad-informacion.md`
- **THEN** el documento contiene proposito, alcance, principios de seguridad y ciclo de aprobacion/comunicacion/revision

#### Scenario: La politica encuadra el stack y los controles organizacionales

- **WHEN** se lee la politica
- **THEN** declara que el repositorio es un stack de desarrollo local y que los controles organizacionales/fisicos competen a la organizacion adoptante

### Requirement: SGD-003 — Clasificacion y etiquetado de la informacion

El proyecto SHALL incluir `docs/seguridad/clasificacion-etiquetado-informacion.md`, alineado con ISO/IEC 27002 5.12 y 5.13. El documento MUST definir un esquema de niveles de clasificacion con criterios objetivos, las reglas de etiquetado por nivel y el tratamiento requerido por nivel. El esquema MUST clasificar explicitamente los **datos personales (PII)** tratados por el sistema y los **datos del directorio de empleados**, y MUST vincular el nivel asignado con las medidas ya existentes (pseudonimizacion, cifrado at-rest, minimizacion). El documento MUST NOT exponer PII real: los ejemplos MUST ser sinteticos o estructurales.

#### Scenario: El esquema define niveles y criterios

- **WHEN** se lee `docs/seguridad/clasificacion-etiquetado-informacion.md`
- **THEN** el documento define niveles de clasificacion, sus criterios y el tratamiento/etiquetado por nivel

#### Scenario: PII y directorio quedan clasificados

- **WHEN** se lee la clasificacion
- **THEN** los datos personales y los datos del directorio de empleados aparecen clasificados con el tratamiento requerido y su vinculo con las medidas existentes

#### Scenario: Los ejemplos no contienen PII real

- **WHEN** se revisan los ejemplos del documento
- **THEN** no hay PII real; los ejemplos son sinteticos o estructurales

### Requirement: SGD-004 — Roles y responsabilidades de seguridad

El proyecto SHALL incluir `docs/seguridad/roles-responsabilidades-seguridad.md`, alineado con ISO/IEC 27002 5.2. El documento MUST definir los roles de seguridad, incluyendo al menos el responsable de seguridad de la informacion y el **responsable de proteccion de datos (DPO)**, con sus responsabilidades. El documento MUST incluir una matriz de asignacion de responsabilidades (RACI o equivalente) para las actividades de seguridad y privacidad documentadas por este change. El documento MUST distinguir los roles ejercidos por la organizacion adoptante de los roles tecnicos observables en el repositorio.

#### Scenario: Los roles de seguridad estan definidos

- **WHEN** se lee `docs/seguridad/roles-responsabilidades-seguridad.md`
- **THEN** aparecen el responsable de seguridad y el responsable de proteccion de datos (DPO) con sus responsabilidades

#### Scenario: Existe una matriz de responsabilidades

- **WHEN** se lee el documento de roles
- **THEN** contiene una matriz (RACI o equivalente) que asigna responsables a las actividades de seguridad y privacidad

#### Scenario: Se distinguen roles organizacionales de roles tecnicos

- **WHEN** se lee el documento de roles
- **THEN** se distingue que roles competen a la organizacion adoptante y cuales son observables en el repositorio

### Requirement: SGD-005 — Plan de respuesta a incidentes y procedimiento de reporte

El proyecto SHALL incluir `docs/seguridad/plan-respuesta-incidentes-seguridad.md` y `docs/seguridad/procedimiento-reporte-eventos.md`, alineados con ISO/IEC 27002 5.24, 5.25, 5.26 y 5.27. El plan MUST definir las fases de gestion de incidentes (preparacion, deteccion/triaje, contencion, erradicacion, recuperacion, lecciones aprendidas), los criterios de severidad y el canal de notificacion. El procedimiento de reporte MUST definir como cualquier persona reporta un evento de seguridad y quien lo evalua. El plan MUST aclarar que la Ley 25.326 vigente NO impone una obligacion general de notificacion de brechas a la autoridad y que se adopta el estandar de **72 horas** de los proyectos de reforma **por prudencia**. El plan MUST registrar como leccion aprendida el caso historico de filtracion de clave documentado en `docs/security-hardening.md`.

#### Scenario: El plan cubre el ciclo de gestion de incidentes

- **WHEN** se lee `docs/seguridad/plan-respuesta-incidentes-seguridad.md`
- **THEN** define las fases de gestion, los criterios de severidad/triaje y el canal de notificacion

#### Scenario: El procedimiento de reporte define canal y evaluacion

- **WHEN** se lee `docs/seguridad/procedimiento-reporte-eventos.md`
- **THEN** describe el canal de reporte de eventos y el rol que los evalua

#### Scenario: La notificacion se encuadra segun la ley vigente

- **WHEN** se lee la seccion de notificacion del plan
- **THEN** declara que la Ley 25.326 no impone obligacion general de notificacion y que se adopta el estandar de 72 horas por prudencia

### Requirement: SGD-006 — Inventario de activos de informacion

El proyecto SHALL incluir `docs/seguridad/inventario-activos-informacion.md`, alineado con ISO/IEC 27002 5.9. El inventario MUST listar los activos de informacion del sistema, cubriendo al menos datos (incidentes, directorio, catalogo), software y servicios (contexto de PostgreSQL, Redis, backend FastAPI, N8N, frontend, proveedores Gemini/Twilio/Microsoft) y MUST asignar a cada activo un propietario o responsable y su clasificacion. El inventario MUST NOT contener credenciales ni secretos.

#### Scenario: El inventario lista activos con responsable y clasificacion

- **WHEN** se lee `docs/seguridad/inventario-activos-informacion.md`
- **THEN** cada activo listado tiene responsable y clasificacion, cubriendo datos, software y servicios del sistema

#### Scenario: El inventario no contiene secretos

- **WHEN** se inspecciona el inventario
- **THEN** no incluye credenciales, claves ni valores de secretos

### Requirement: SGD-007 — Registro de requisitos legales

El proyecto SHALL incluir `docs/seguridad/registro-requisitos-legales.md`, alineado con ISO/IEC 27002 5.31. El registro MUST enumerar los requisitos legales y regulatorios aplicables al sistema, incluyendo la Ley 25.326 y las resoluciones de la AAIP relevantes citadas en `docs/cumplimiento/marco-legal-ar-2026.md`. El registro MUST distinguir los requisitos vigentes de los proyectos no sancionados, y MUST vincular cada requisito con el documento o control del sistema que lo atiende, senalando los que quedan como responsabilidad de la organizacion adoptante.

#### Scenario: El registro enumera requisitos vigentes

- **WHEN** se lee `docs/seguridad/registro-requisitos-legales.md`
- **THEN** enumera la Ley 25.326 y las normas AAIP aplicables, cada una vinculada a un documento o control que la atiende

#### Scenario: Se distinguen normas vigentes de proyectos

- **WHEN** se lee el registro
- **THEN** distingue explicitamente los requisitos vigentes de los proyectos de reforma no sancionados

### Requirement: SGD-008 — Modelado de amenazas y seguridad en el SDLC

El proyecto SHALL incluir `docs/seguridad/modelado-amenazas-sdlc.md`, alineado con ISO/IEC 27002 8.26. El documento MUST describir el modelado de amenazas adoptado (por ejemplo, STRIDE o equivalente) y MUST definir los requisitos de seguridad que cada change debe considerar en el ciclo de desarrollo OPSX, incluyendo un criterio de verificacion de seguridad previo al cierre del change. El documento MUST mapear las amenazas identificadas a los controles que las mitigan o a los changes tecnicos que las abordan (C-62 a C-67), sin declararlos implementados.

#### Scenario: El documento define modelado de amenazas y gate de seguridad

- **WHEN** se lee `docs/seguridad/modelado-amenazas-sdlc.md`
- **THEN** describe el metodo de modelado de amenazas y los requisitos de seguridad aplicables a cada change del SDLC

#### Scenario: Las amenazas se mapean a controles o changes

- **WHEN** se lee el modelado
- **THEN** cada amenaza identificada se asocia a un control o a un change tecnico que la aborda, sin declararlo implementado

### Requirement: SGD-009 — Politica de privacidad en runtime de cara al usuario

El proyecto SHALL incluir `docs/seguridad/politica-privacidad-runtime.md`, alineado con ISO/IEC 27002 5.34 y con el deber de informacion de la Ley 25.326. El documento MUST describir la informacion que se presenta al titular (finalidad, destinatarios, identidad del responsable, caracter de las respuestas y derechos), la base de licitud de cada tratamiento y los derechos de acceso, rectificacion y supresion con sus plazos legales (**acceso: 10 dias corridos; rectificacion/actualizacion/supresion: 5 dias habiles**). El documento MUST explicar la distincion entre pseudonimizacion y disociacion (art. 2) y MUST NOT atribuir a la ley vigente un derecho autonomo de oposicion.

#### Scenario: La politica de privacidad cubre informacion y derechos

- **WHEN** se lee `docs/seguridad/politica-privacidad-runtime.md`
- **THEN** describe la informacion al titular, la base de licitud y los derechos con sus plazos legales

#### Scenario: Los plazos legales son los correctos

- **WHEN** se leen los plazos de los derechos
- **THEN** el acceso figura a 10 dias corridos y la rectificacion/actualizacion/supresion a 5 dias habiles (art. 16)

#### Scenario: Se distingue pseudonimizacion de disociacion

- **WHEN** se lee la seccion sobre tratamiento de datos
- **THEN** explica la pseudonimizacion implementada frente a la disociacion de datos del art. 2 y no atribuye a la ley un derecho autonomo de oposicion

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

### Requirement: SGD-012 — Responsable del tratamiento y los tres tratamientos

El proyecto SHALL documentar, en `docs/seguridad/registro-actividades-tratamiento.md` (ROPA) y/o `docs/seguridad/registro-requisitos-legales.md`, el **responsable del tratamiento** y los **tres tratamientos** del sistema. Durante la tesis el responsable del tratamiento MUST ser el propio grupo de desarrollo del proyecto, como responsable directo (NO la UTN-FRM), y el **consentimiento informado del propio grupo** MUST quedar documentado como base de licitud del tratamiento T1. Los tres tratamientos MUST describirse por separado: **T1** piloto/desarrollo con datos REALES del grupo (cuentas del grupo y usuarios de prueba cuyos correos/celulares apuntan a contactos del grupo), base de licitud consentimiento informado; **T2** corpus de investigacion con incidentes reales pseudonimizados, responsable el grupo, salvaguarda pseudonimizacion, aclarando que pseudonimizacion no equivale a disociacion (art. 2) porque el original existe y es reidentificable; **T3** datos de produccion de una empresa que despliegue el sistema, responsable la organizacion adoptante como rol funcional generico. El documento MUST dejar explicito que el sistema no usa datos ficticios: es un piloto con datos reales del equipo. La inscripcion de bases de datos (arts. 21/24) MUST quedar como responsabilidad de la organizacion adoptante, con un template/checklist documental, y MUST NOT afirmar que la tesis inscribe bases.

#### Scenario: El responsable del tratamiento queda documentado

- **WHEN** se lee el ROPA o el registro de requisitos legales
- **THEN** identifica al grupo de desarrollo como responsable del tratamiento durante la tesis (responsable directo, no la UTN-FRM) y a la organizacion adoptante como responsable funcional de T3

#### Scenario: Los tres tratamientos se describen por separado

- **WHEN** se lee la seccion de tratamientos
- **THEN** T1 (piloto/desarrollo), T2 (corpus de investigacion) y T3 (adoptante futuro) aparecen descritos por separado con su finalidad, datos, responsable y base de licitud/salvaguarda

#### Scenario: El consentimiento del grupo respalda T1

- **WHEN** se revisa la base de licitud de T1
- **THEN** figura el consentimiento informado del propio grupo, documentado como acta breve

#### Scenario: Se distingue pseudonimizacion de disociacion en T2

- **WHEN** se lee la descripcion de T2
- **THEN** declara que los incidentes son reales y pseudonimizados y aclara que la pseudonimizacion no es disociacion (art. 2) porque el original existe y es reidentificable

#### Scenario: No se usan datos ficticios

- **WHEN** se lee la descripcion del piloto
- **THEN** declara que el sistema no usa datos ficticios y que es un piloto con datos reales del equipo

#### Scenario: La inscripcion de bases es responsabilidad del adoptante

- **WHEN** se lee la seccion de inscripcion de bases (arts. 21/24)
- **THEN** la asigna a la organizacion adoptante, entrega un template/checklist y no afirma que la tesis inscribe bases

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

### Requirement: SGD-016 — Evaluacion de seguridad de proveedores

El proyecto SHALL incluir `docs/seguridad/evaluacion-seguridad-proveedores.md`, alineado con ISO/IEC 27002 5.19, 5.20, 5.21, 5.22 y 5.23. El documento MUST cubrir los proveedores de servicios del sistema (Twilio, Gemini/Google, Microsoft y N8N), y por cada uno MUST describir la postura de seguridad observable publicamente (por ejemplo: cifrado en transito, gestion de identidades, certificaciones declaradas por el proveedor, canales de reporte de vulnerabilidades) y las clausulas o garantias contractuales a evaluar por la organizacion adoptante. El documento MUST distinguir lo evaluable publicamente de lo que requiere una accion contractual de la organizacion adoptante y MUST registrar como pendientes las garantias que no esten suscritas. El documento MUST usar el lenguaje de alineacion ("alineado con" / "controles mapeados a") y MUST NOT afirmar que el sistema, el repositorio o los proveedores estan "certificados" o son "compliant" con ISO, NIST o la Ley 25.326. El documento MUST ser referenciable desde `docs/seguridad/README.md`.

#### Scenario: El documento cubre los cuatro proveedores

- **WHEN** se lee `docs/seguridad/evaluacion-seguridad-proveedores.md`
- **THEN** contiene una seccion por cada proveedor del sistema (Twilio, Gemini/Google, Microsoft y N8N)

#### Scenario: Cada proveedor declara postura y clausulas

- **WHEN** se lee la seccion de un proveedor
- **THEN** describe su postura de seguridad observable y las clausulas o garantias contractuales a evaluar, distinguiendo lo evaluable publicamente de lo que requiere accion contractual

#### Scenario: Se registran las garantias no suscritas

- **WHEN** se lee el encuadre del documento
- **THEN** declara que las garantias y clausulas no suscritas quedan como accion pendiente de la organizacion adoptante

#### Scenario: El lenguaje de alineacion se respeta

- **WHEN** se revisa `docs/seguridad/evaluacion-seguridad-proveedores.md`
- **THEN** usa "alineado con" o "controles mapeados a" y no afirma que el sistema o los proveedores esten certificados ni sean "compliant"

#### Scenario: El documento se referencia desde el indice

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** el documento de evaluacion de proveedores aparece listado y su referencia resuelve a un archivo existente

### Requirement: SGD-017 — Reconciliacion del estado vigente y referencias cruzadas

La documentacion de cumplimiento SHALL reflejar el estado vigente del repositorio y de los changes archivados. `docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md` MUST incluir un registro de estado vigente que, por cada control reconciliado, indique el estado actual, la evidencia en codigo o documentacion, el residual abierto y el change archivado que lo cerro. El registro MUST marcar como cerrados los controles ya implementados (entre ellos MFA y rotacion de claves de C-63, el retiro de Redis de C-62, la politica, clasificacion, inventario, plan de IR y evaluacion de proveedores de C-61/C-64, el SAST y la auditoria de dependencias de C-64, y la retencion de logs de C-66). El documento MUST NOT declarar ausente un control que ya existe en el repositorio. Los residuales que dependen de la organizacion adoptante (revision independiente 5.35, redundancia 8.14, copia offsite y contratos con proveedores) MUST permanecer explicitamente abiertos.

Las referencias cruzadas de `docs/seguridad/` SHALL resolver a archivos existentes y al estado real de los changes. En particular, el inventario de activos MUST NOT listar Redis como activo activo, MUST marcar Microsoft Outlook como inactivo desde C-55 y MUST referenciar `gestion-secretos-y-rotacion.md` en lugar de un change C-63 inexistente como change unico. El `README.md` de `docs/seguridad/` MUST presentar C-62 a C-67 como archivados (no pendientes), MUST mapear 5.34/8.12 a `adr-001-reversion-minimizacion-directorio.md` y `clasificacion-etiquetado-informacion.md` en lugar de la justificacion superada, y MUST NOT conservar la nota de "pendiente para el orquestador" sobre `CHANGES.md` una vez cumplida. El ROPA MUST indicar que Microsoft Outlook figura como procesador historico inactivo.

#### Scenario: El gap assessment no declara ausente un control implementado

- **WHEN** se lee el registro de estado vigente del gap assessment
- **THEN** MFA, rotacion de claves, retiro de Redis, politica, clasificacion, inventario, plan de IR, evaluacion de proveedores, SAST/auditoria de dependencias y retencion de logs figuran como cerrados con su evidencia y su change archivado

#### Scenario: Los residuales del adoptante permanecen abiertos

- **WHEN** se lee el gap assessment reconciliado
- **THEN** 5.35, 8.14, la copia offsite y los contratos con proveedores siguen declarados como residuales o acciones de la organizacion adoptante

#### Scenario: Las referencias a Redis y a Microsoft son correctas

- **WHEN** se lee `inventario-activos-informacion.md`
- **THEN** Redis no aparece como activo activo y Microsoft Outlook figura como inactivo desde C-55

#### Scenario: El indice refleja los changes archivados

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** C-62 a C-67 figuran como archivados, la justificacion del directorio apunta al ADR y a la clasificacion vigente, y no queda la nota pendiente sobre `CHANGES.md`

### Requirement: SGD-018 — Lint documental de cumplimiento

El proyecto SHALL incluir una prueba automatizada y hermética que valide la integridad de `docs/seguridad/` sin depender de servicios externos ni de red. La prueba MUST verificar que: (a) cada documento listado en el indice existe; (b) cada archivo `.md` de la carpeta de gobernanza esta listado en el indice; (c) cada documento de gobernanza abre con los encabezados requeridos (control mapeado, estado, alcance y encuadre); y (d) ningun documento afirma certificacion o conformidad con ISO, NIST o la Ley 25.326 mediante terminos afirmativos prohibidos. La prueba MUST tolerar las negaciones y encuadres de alineacion ("no constituye certificacion", "alineado con") y MUST fallar ante una afirmacion positiva de certificacion. La prueba SHALL ejecutarse como parte de la suite de backend, de modo que el job de integracion continua existente la ejecute sin modificar el workflow.

#### Scenario: Un documento faltante rompe el lint

- **WHEN** el indice lista un documento que no existe en `docs/seguridad/`
- **THEN** la prueba falla indicando el documento y la referencia faltante

#### Scenario: Un documento no listado rompe el lint

- **WHEN** existe un documento de gobernanza en `docs/seguridad/` que el indice no lista
- **THEN** la prueba falla indicando el documento omitido

#### Scenario: Una afirmacion de certificacion rompe el lint

- **WHEN** un documento afirma que el sistema esta certificado, es compliant o cumple ISO/NIST de forma positiva
- **THEN** la prueba falla indicando el archivo y la frase prohibida

#### Scenario: El encuadre de alineacion no rompe el lint

- **WHEN** un documento declara que esta alineado con los marcos y que no constituye certificacion ni auditoria
- **THEN** la prueba pasa para ese documento

#### Scenario: El lint corre en la suite de backend

- **WHEN** se ejecuta `pytest` en `App/Backend/`
- **THEN** el lint documental se ejecuta y no requiere PostgreSQL, Gemini, N8N ni red

### Requirement: SGD-019 — Manejo de evidencia y cadena de custodia

El plan de respuesta a incidentes de seguridad y la politica de retencion de logs SHALL documentar el manejo de evidencia de un incidente (control ISO/IEC 27002 5.28). La documentacion MUST cubrir la identificacion de la evidencia, su recoleccion y preservacion, la integridad verificable (por ejemplo, hash del artefacto), el registro de custodios y transferencias, y la retencion aplicable segun la clase de registro. MUST aclarar que la cadena de custodia formal y la preservacion forense completa son responsabilidad de la organizacion adoptante cuando el incidente exceda el alcance del repositorio.

#### Scenario: La evidencia tiene identificacion y preservacion

- **WHEN** se lee la seccion de evidencia del plan de respuesta a incidentes
- **THEN** describe que evidencia se recolecta, como se preserva y donde se registra

#### Scenario: La integridad es verificable

- **WHEN** se lee el procedimiento de evidencia
- **THEN** exige un mecanismo de verificacion de integridad (hash o equivalente) y el registro de custodios y transferencias

#### Scenario: La custodia formal queda encuadrada en el adoptante

- **WHEN** se lee el encuadre de la seccion de evidencia
- **THEN** declara que la cadena de custodia formal y la preservacion forense completa competen a la organizacion adoptante

### Requirement: SGD-020 — Inventario de licencias de dependencias

El proyecto SHALL incluir `docs/seguridad/inventario-licencias.md`, alineado con ISO/IEC 27002 5.32 (Propiedad intelectual). El inventario MUST listar las dependencias principales de backend y frontend con su licencia declarada, MUST identificar las licencias que imponen obligaciones de atribucion o copyleft y MUST NOT contener credenciales ni secretos. El documento MUST declarar que es un inventario de referencia y que la verificacion legal definitiva compete a la organizacion adoptante.

#### Scenario: El inventario cubre backend y frontend

- **WHEN** se lee `docs/seguridad/inventario-licencias.md`
- **THEN** lista dependencias principales de backend y frontend con su licencia declarada

#### Scenario: Las obligaciones de licencia quedan identificadas

- **WHEN** se revisan las dependencias con licencias copyleft o de atribucion
- **THEN** el documento identifica la obligacion aplicable

#### Scenario: El inventario se referencia desde el indice

- **WHEN** se lee `docs/seguridad/README.md`
- **THEN** `inventario-licencias.md` aparece listado y su referencia resuelve a un archivo existente
