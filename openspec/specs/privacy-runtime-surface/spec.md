# privacy-runtime-surface Specification

## Purpose
Define la superficie de privacidad en runtime del sistema: el aviso de politica de privacidad accesible desde los canales de entrada, la informacion al titular (art. 6 de la Ley 25.326) y el canal para ejercer los derechos con sus plazos legales. Materializa en el sistema la afirmacion del capitulo 11 de la tesis sobre una politica de privacidad accesible desde los canales de entrada.

## Requirements

### Requirement: PRIV-001 — Superficie de politica de privacidad accesible desde los canales de entrada

El sistema SHALL exponer una superficie de politica de privacidad en el frontend, alcanzable desde el canal de entrada web mediante un enlace visible en el formulario de reporte de incidentes. La superficie SHALL exponerse como una **ruta publica estatica `/privacidad` declarada FUERA de cualquier guarda de autenticacion** (por ejemplo, fuera de `ProtectedRoute`), de modo que sea alcanzable sin sesion; SHALL enlazarse ademas desde la pagina de login. La superficie SHALL ser legible por el titular sin requerir que este complete o envie un reporte. La superficie MUST NOT recolectar datos personales adicionales a los que ya recolecta el canal. La superficie SHALL declarar su caracter de objetivo/norma vigente del sistema y MUST NOT presentar la informacion como una certificacion ni como una auditoria.

#### Scenario: El canal de entrada enlaza la politica de privacidad

- **WHEN** un usuario carga el formulario de reporte de incidentes
- **THEN** el formulario presenta un enlace visible hacia la superficie de politica de privacidad

#### Scenario: La pagina de login enlaza la politica de privacidad

- **WHEN** un usuario carga la pagina de login
- **THEN** la pagina presenta un enlace visible hacia la superficie de politica de privacidad

#### Scenario: La superficie es una ruta publica alcanzable sin sesion

- **WHEN** un usuario NO autenticado navega a la ruta `/privacidad`
- **THEN** la superficie se renderiza sin exigir sesion y sin redirigir a la ruta raiz

#### Scenario: La superficie es alcanzable sin completar un reporte

- **WHEN** un usuario accede a la superficie de politica de privacidad desde el canal de entrada
- **THEN** la superficie se renderiza sin exigir que el usuario complete ni envie un reporte

#### Scenario: La superficie no recolecta datos adicionales

- **WHEN** se inspecciona la superficie de politica de privacidad
- **THEN** no contiene campos de entrada que recolecten datos personales distintos de los del canal existente

### Requirement: PRIV-002 — Contenido: informacion al titular, bases de licitud y derechos con plazos

La superficie de privacidad SHALL presentar al titular, de forma expresa y clara: la finalidad del tratamiento y los destinatarios de los datos; la existencia e identidad del responsable del tratamiento; las bases de licitud aplicables; la transferencia internacional hacia proveedores con sede en Estados Unidos (Gemini y Twilio) y su mecanismo (consentimiento expreso o clausulas contractuales modelo); los derechos de acceso, rectificacion, actualizacion y supresion con sus plazos legales (acceso: 10 dias corridos; rectificacion/actualizacion/supresion: 5 dias habiles); y el canal para ejercerlos. La superficie SHALL advertir que algunas notificaciones generan respuestas automaticas. La superficie SHALL usar el lenguaje de **"alineado con"** y MUST NOT afirmar que el sistema esta "certificado", es "compliant" ni "cumple" los marcos.

#### Scenario: La superficie informa finalidad, responsable y destinatarios

- **WHEN** se lee la superficie de politica de privacidad
- **THEN** presenta la finalidad del tratamiento, la identidad del responsable y los destinatarios de los datos

#### Scenario: La transferencia internacional queda informada

- **WHEN** se lee la superficie de politica de privacidad
- **THEN** informa la transferencia hacia Gemini y Twilio en Estados Unidos y el mecanismo habilitante, indicando que la pseudonimizacion mitiga pero no sustituye el instrumento

#### Scenario: Los plazos de los derechos son los correctos

- **WHEN** se leen los plazos de los derechos en la superficie
- **THEN** el acceso figura a 10 dias corridos y la rectificacion/actualizacion/supresion a 5 dias habiles (art. 16), y se indica el canal para ejercerlos

#### Scenario: La superficie no afirma conformidad

- **WHEN** se revisa el texto de la superficie de politica de privacidad
- **THEN** usa "alineado con" o "controles mapeados a" y no contiene los terminos "certificado", "compliant" ni "cumple"
