## MODIFIED Requirements

### Requirement: Capitulo 7 reescrito sin base de empleador (R-05)

El capitulo 7 (`11-aspectos-legales.tex`) SHALL reescribirse para declarar el tratamiento que
realmente ocurrio. SHALL RETIRARSE: la base de empleador (articulo 5, inciso 2, apartado d)
como base del estudio; el responsable de proteccion de datos "designado por la organizacion";
la politica de privacidad dirigida a "los usuarios de la organizacion"; la notificacion a 120
empleados; y la carta de autorizacion. El documento SHALL explicar la base legal real de los
incidentes reales del regimen (a): la disociacion del contenido conservado y transferido
(articulos 2 y 28 de la Ley 25.326), segun la devolucion de quinta instancia (C-05, c-250). El
consentimiento informado (articulo 5, inciso 1) SHALL presentarse solo como el de los
colaboradores del estudio (los autores y `A1`) y MUST NOT presentarse como base de licitud del
contenido del corpus ni como consentimiento de los titulares de los incidentes; el documento MUST
NOT afirmar que todos los titulares del regimen (a) son integrantes del grupo cuando los
reportantes incluyen personas del circulo de los autores. El acta de consentimiento SHALL
llevar su **fecha real de firma**, sin fecha inventada. La redaccion exacta de la base legal y
la fecha real del acta SHALL provenir de la respuesta registrada de los autores; sin esa
respuesta, la tarea queda bloqueada.

#### Scenario: Base de empleador retirada

- **WHEN** se busca en `11-aspectos-legales.tex` la base de empleador (articulo 5, inciso 2, apartado d) como base del estudio
- **THEN** ya no funda el tratamiento del estudio
- **AND** si se cita la base de empleador, se presenta solo como la que corresponderia a una organizacion adoptante real (T3), de forma condicional

#### Scenario: Responsable, politica y notificacion retirados

- **WHEN** se buscan en `11-aspectos-legales.tex` "responsable de proteccion de datos designado por la organizacion", la politica de privacidad "para los usuarios de la organizacion" y la notificacion a 120 empleados
- **THEN** ya no aparecen como hechos del estudio
- **AND** no se sustituyen por una afirmacion equivalente sobre una organizacion adoptante real

#### Scenario: Base real del regimen (a) explicada

- **WHEN** se lee la explicacion de la base de licitud de los incidentes reales del regimen (a)
- **THEN** se funda en la disociacion del contenido (articulos 2 y 28 de la Ley 25.326)
- **AND** el consentimiento del 2026-10-02 figura como consentimiento de los colaboradores (autores y `A1`), separado de la situacion de los titulares de los incidentes

#### Scenario: Fecha real del acta de consentimiento

- **WHEN** se lee la fecha del acta de consentimiento (actualmente "2026-10-02" en `11-aspectos-legales.tex`)
- **THEN** la fecha consignada es la fecha real de firma confirmada por los autores
- **AND** no se inventa ni se conserva una fecha no confirmada

### Requirement: Titularidad unica del regimen (a) y tensiones del repositorio explicadas (OQ-02 de c-249)

El documento SHALL usar una sola formula para los reportantes de los 119 incidentes del regimen
(a) en `04-marco-metodologico.tex` y en `11-aspectos-legales.tex` (hoy `04:46`, `11:16`, `11:40`,
`11:48`), la que confirmen los autores en OQ-02 de c-249. Como esa formula incluye a las
personas del circulo de los autores, §7.5 MUST NOT afirmar que titulares y responsables del
tratamiento del regimen (a) son las mismas personas (devolucion de quinta instancia, C-05, c-250).
El documento y `data/README.md` SHALL
explicar que datos personales contenian los originales no versionados y de quien eran, de modo
coherente con `11:24` y `12:151`. La contradiccion entre "se redactaron" (`04:46`) y "coinciden con
el texto de origen" (`12:153`) SHALL resolverse; si las descripciones del regimen (a) fueron
reescritas por los autores, la septima amenaza (`04:129`) SHALL extenderse a los 200 casos. El
capitulo legal SHALL incluir un parrafo sobre la informacion de los empleadores reales
(confidencialidad, autorizacion o su innecesariedad) segun la respuesta. "El corpus no proviene de
una organizacion real" (`01:72`) SHALL retirarse o acotarse. El contenido MUST NOT inventarse y
MUST NOT contener nombres reales ni la correspondencia alias-identidad.

#### Scenario: Una sola formula de reportantes

- **WHEN** se ejecuta `rg -n "reportados por los integrantes del entorno operativo|propio grupo de desarrollo" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** todas las coincidencias usan la misma formula, coincidente con OQ-02 de c-249

#### Scenario: Sin identidad de titulares y responsables

- **WHEN** se ejecuta `rg -n "mismas personas" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias que afirmen que titulares y responsables del tratamiento del regimen (a) son las mismas personas

#### Scenario: Texto de origen o redaccion, sin contradiccion

- **WHEN** se leen `04:46` y `12:153` (o sus sucesores)
- **THEN** ambos describen de la misma manera la relacion entre las descripciones del regimen (a) y el texto de origen
- **AND** si fueron reescritas, la septima amenaza cubre los 200 casos

#### Scenario: Originales con PII explicados

- **WHEN** se lee `data/README.md` en el parrafo de los originales no versionados
- **THEN** dice que datos personales contenian y de quien eran, sin contradecir `11:24` ni `12:151`

#### Scenario: Sin respuesta de autores

- **WHEN** la tabla de compuertas de c-249 no contiene la respuesta OQ-02
- **THEN** las tareas gated por OQ-02 permanecen sin marcar

