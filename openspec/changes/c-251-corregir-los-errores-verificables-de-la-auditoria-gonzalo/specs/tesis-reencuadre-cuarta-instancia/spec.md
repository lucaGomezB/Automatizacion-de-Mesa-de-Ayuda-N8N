## ADDED Requirements

### Requirement: Paráfrasis fiel del art. 28 de la Ley 25.326 para la licitud por disociación (E1 de c-251)

El capítulo legal SHALL reformular la fundamentación de la licitud por disociación sin atribuir al
art. 28 la afirmación de que "los datos disociados no se consideran datos personales". El art. 2
SHALL citarse como la definición de "disociación de datos"; el art. 28 SHALL citarse como la exención
de encuestas/estadística/investigación científica en la medida en que los datos recogidos no puedan
atribuirse a una persona determinada o determinable (28.1) y el mandato de usar técnica de disociación
cuando no se pueda mantener el anonimato (28.2); el art. 11.3.e SHALL citarse como la base de cesión
sin consentimiento cuando media disociación. El texto MUST NOT presentar "disociado = no dato
personal" como texto literal de ningún artículo. La redacción final es decisión de autores+director
(OQ-2); el apply MUST NOT redactarla sin la decisión registrada.

#### Scenario: Ningún artículo citado con la frase inexacta

- **WHEN** se ejecuta `rg -n "art.culo 28 dispone que los datos disociados no se consideran datos personales|disociados no se consideran datos personales" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias del texto literal atribuido al art. 28

#### Scenario: Lectura fiel atribuida por artículo

- **WHEN** se lee `11-aspectos-legales.tex:12`
- **THEN** el art. 2 define la disociación, el art. 28 exime la investigación con datos no atribuibles y manda disociar, y el art. 11.3.e cubre la cesión, sin atribuir a ninguno la frase "disociado = no dato personal"

#### Scenario: Propagación coherente de la fundamentación

- **WHEN** se ejecuta `rg -n "disociac|sin datos personales|sin dato personal|no contiene dato personal" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"` sobre las líneas `:16`, `:18`, `:32`, `:36`, `:46` y `:54`
- **THEN** cada pasaje que funda la licitud lo hace por disociación con lectura fiel de los arts. 2/28/11.3.e, sin repetir la paráfrasis inexacta del art. 28

### Requirement: Fecha de notificación única y consistente con el acta (E2 de c-251)

El capítulo legal SHALL consignar UNA única fecha de notificación a los integrantes del grupo, y esa
fecha SHALL ser consistente con el acta firmada `docs/seguridad/acta-consentimiento-t2.md` (cabecera
y §4: notificación el 2026-10-01). La redacción actual de `11-aspectos-legales.tex:32` dice
"2026-09-30" y MUST NOT coexistir con la del acta. La fecha correcta es decisión de autores+director
(OQ-1); el apply MUST NOT elegirla sin la decisión registrada.

#### Scenario: Una sola fecha en el capítulo legal

- **WHEN** se ejecuta `rg -n "2026-09-30|2026-10-01|30 de septiembre|1 de octubre|01/10" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay dos fechas distintas para el mismo hecho; la única fecha coincide con la del acta o con la decisión OQ-1 registrada

#### Scenario: Consistencia con el acta firmada

- **WHEN** se contrasta `11-aspectos-legales.tex:32` con la cabecera y §4 de `docs/seguridad/acta-consentimiento-t2.md`
- **THEN** la fecha de notificación coincide entre ambos documentos

### Requirement: Frase sobre la v1.6.0 retirada (E3 de c-251)

El capítulo legal SHALL retirar la oración "La versión v1.6.0 afirmó que no se había recabado el
consentimiento de los titulares para la transferencia internacional; esa afirmación no se sostiene,
porque el consentimiento verbal se prestó el 2026-10-02, aunque su constancia escrita es posterior."
(actualmente al final de `11-aspectos-legales.tex:32`), que el tribunal C-05 pidió retirar
explícitamente. La cronología del consentimiento verbal (2026-10-02) MUST permanecer en el resto del
capítulo; solo la afirmación que lo opone a la v1.6.0 se retira.

#### Scenario: Oración de la v1.6.0 retirada

- **WHEN** se ejecuta `rg -n "La versi.n v1.6.0 afirm|v1.6.0" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** no hay coincidencias de una oración que afirme que el consentimiento del 02/10 refuta lo dicho en la v1.6.0 sobre los titulares

#### Scenario: Cronología del consentimiento verbal intacta

- **WHEN** se ejecuta `rg -n "2026-10-02" "docs/Tesis/v10 (IA)/paper/sections/11-aspectos-legales.tex"`
- **THEN** la fecha del consentimiento verbal 2026-10-02 sigue presente en los pasajes que la describen, solo que sin la oposición a la v1.6.0
