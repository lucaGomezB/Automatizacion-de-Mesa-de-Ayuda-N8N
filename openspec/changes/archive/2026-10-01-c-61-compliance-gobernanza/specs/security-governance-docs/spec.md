## Purpose

Define los documentos de gobernanza de seguridad y privacidad del proyecto bajo `docs/seguridad/`: politica de seguridad, clasificacion y etiquetado de la informacion, roles y responsabilidades, gestion de incidentes, inventario de activos, requisitos legales, seguridad en el ciclo de desarrollo, privacidad en runtime y registro de actividades de tratamiento. Fija las reglas de lenguaje de alineacion y la trazabilidad a los controles de ISO/IEC 27002:2022, NIST CSF 2.0 y la Ley 25.326, dejando explicito que el stack es de desarrollo local y que los controles organizacionales competen a la organizacion adoptante.

## ADDED Requirements

### Requirement: SGD-001 — Ubicacion, indice y trazabilidad de la documentacion

El proyecto SHALL mantener la documentacion de gobernanza de seguridad en `docs/seguridad/`, con un indice `docs/seguridad/README.md`. El indice MUST listar cada documento con su proposito y MUST incluir un mapa de trazabilidad que asocie cada control objetivo (ISO/IEC 27002 5.1, 5.2, 5.9, 5.12, 5.13, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26 y NIST CSF Govern/Identify) con el documento que lo cubre. El indice MUST declarar que los documentos son **alineados con** los marcos citados y MUST NOT presentarlos como prueba de certificacion. Cada documento de la carpeta MUST ser referenciable desde el indice y las referencias cruzadas entre documentos MUST resolverse a archivos existentes.

#### Scenario: La carpeta y el indice existen

- **WHEN** se inspecciona `docs/seguridad/`
- **THEN** existe `README.md` y los documentos de gobernanza listados por el indice

#### Scenario: El mapa de trazabilidad cubre los controles objetivo

- **WHEN** se lee el mapa de trazabilidad de `docs/seguridad/README.md`
- **THEN** cada control objetivo (5.1, 5.2, 5.9, 5.12, 5.13, 5.24, 5.25, 5.26, 5.27, 5.31, 8.26) apunta a un documento existente que lo cubre

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

El proyecto SHALL incluir `docs/seguridad/registro-actividades-tratamiento.md` como registro de actividades de tratamiento (ROPA) segun la Ley 25.326. El registro MUST describir, por cada actividad de tratamiento (al menos: gestion de incidentes, directorio de empleados y clasificacion automatica), la finalidad, las categorias de datos y de titulares, los destinatarios o encargados (Gemini, Twilio, Microsoft, N8N), las transferencias internacionales y el plazo de conservacion. El registro MUST senalar las transferencias a Estados Unidos como pais NO adecuado y el instrumento requerido, y MUST mencionar la inscripcion de bases de datos (arts. 21 y 24) como evaluacion pendiente de la organizacion adoptante.

#### Scenario: El ROPA describe las actividades de tratamiento

- **WHEN** se lee `docs/seguridad/registro-actividades-tratamiento.md`
- **THEN** cada actividad de tratamiento del sistema describe finalidad, categorias de datos/titulares, destinatarios y conservacion

#### Scenario: Las transferencias internacionales quedan registradas

- **WHEN** se lee el ROPA
- **THEN** las transferencias a Estados Unidos aparecen como pais no adecuado con el instrumento requerido (clausulas modelo o consentimiento)

### Requirement: SGD-011 — Regla de lenguaje y encuadre de alineacion (transversal)

Todos los documentos de `docs/seguridad/` SHALL usar el lenguaje de **"alineado con"** y **"controles mapeados a"** al referirse a ISO/IEC 27001:2022, ISO/IEC 27002:2022, ISO/IEC 27701, NIST CSF 2.0 y la Ley 25.326. Los documentos MUST NOT afirmar que el sistema esta "certificado", es "compliant" ni "cumple" los marcos. Los documentos MUST presentar los controles de tipo organizacional (O) y fisico como responsabilidad de la organizacion adoptante, no como controles implementados por el repositorio, y MUST indicar que la documentacion no constituye una certificacion ni una auditoria formal.

#### Scenario: El lenguaje de alineacion se usa consistentemente

- **WHEN** se revisan los documentos de `docs/seguridad/`
- **THEN** usan "alineado con" o "controles mapeados a" y no afirman certificacion ni conformidad

#### Scenario: Los controles organizacionales se encuadran como externos

- **WHEN** se lee un documento que menciona controles organizacionales o fisicos
- **THEN** los presenta como responsabilidad de la organizacion adoptante, no como implementados por el repositorio

#### Scenario: La documentacion aclara que no es certificacion

- **WHEN** se lee el indice o cualquier documento de la carpeta
- **THEN** se declara que la documentacion es de alineacion y no constituye certificacion ni auditoria formal

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
