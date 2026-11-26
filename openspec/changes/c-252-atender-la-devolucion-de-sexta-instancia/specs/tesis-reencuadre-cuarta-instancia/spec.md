## MODIFIED Requirements

### Requirement: Cronología de la campaña manual en octubre 2026 referida al corpus vigente (C-01 de c-250)

El documento SHALL referir toda medición de la línea base manual al corpus **vigente** (200 casos) y
MUST NOT presentar el corpus sintético del 3 de julio (165,3 s) como base de medición: ese corpus
SHALL figurar únicamente como histórico, retirado, en la Nota de versiones, que SHALL decir además quién
midió o generó esos 165,3 s y sobre qué textos (D-01 de c-252). La clasificación manual del corpus **real**
SHALL fecharse dentro de **octubre 2026** (no "junio a agosto"), mediante la cronología día por día que exige
el requisito "Cronología día por día de la campaña 2026-10 (D-01)" de `tesis-sexta-instancia`: §4.2
(`04-marco-metodologico.tex:14`), §4.4 (`:46`), la Tabla 4 `tab:procedencia-numeros` (`:78`), §1.2
(`01-introduccion.tex:16`) y el pie de la Figura 11 SHALL declarar que la fecha del cronometraje manual es una
declaración de los autores acotada superiormente por el commit `ea62576` (2026-10-09), y la barra de la
campaña manual de la Figura 11 MUST NOT extenderse más allá de esa cota. La evidencia fechada es: commit
`68d06ec` (2026-06-11) versiona el corpus **sintético**; commit `ea62576` (2026-10-09) versiona el corpus
**real**; los commits de c-68 (2026-10-02) y c-70 (2026-10-05 y 06) fechan las corridas automatizadas. La
declaración honesta de cronología ("declaración de los autores sin registro fechado") SHALL conservarse. El
contenido MUST NOT inventarse: las fechas sin evidencia SHALL provenir de la respuesta registrada de OQ-01 de
c-252.

#### Scenario: Corpus sintético solo histórico

- **WHEN** se ejecuta `rg -n "165,3|corpus sint.tico" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** la única aparición como base de medición no existe: el 165,3 s figura solo como histórico, retirado, y únicamente en la Nota de versiones (Anexo I.1), con la autoría de la medición declarada

#### Scenario: Ventana junio–agosto reemplazada por octubre 2026

- **WHEN** se ejecuta `rg -n "junio a agosto|junio y agosto|entre junio y agosto" "docs/Tesis/v10 (IA)/paper/sections/"`
- **THEN** no hay coincidencias fuera de la Nota de versiones; §4.2, §4.4, la Tabla 4 y §1.2 fechan la campaña vigente en octubre 2026, y la Nota de versiones registra el cambio de fechas respecto de la v1.6.4

#### Scenario: Evidencia fechada citada

- **WHEN** se lee el pasaje que fundamenta la cronología de la campaña vigente
- **THEN** se citan los commits `68d06ec` (sintético) y `ea62576` (real) como evidencia fechada, la fecha del cronometraje manual se declara acotada por `ea62576`, y la declaración honesta sin registro fechado se conserva

#### Scenario: Figura 11 acotada a la cota del 09/10

- **WHEN** se lee la línea de la campaña manual en `docs/diagrams/cronograma.md` y la Figura 11 regenerada
- **THEN** la barra termina a más tardar el 2026-10-09 (o en la cota menor registrada por OQ-01 de c-252) y el pie de la figura lo explica

### Requirement: Componente "~10 s de carga del ticket" retirado (C-02 de c-250)

La descripción del tiempo manual SHALL ser una sola y coincidir con la decisión registrada en OQ-02 de c-252.
En la rama B (la carga nunca se sumó), el "~10 s de carga del ticket estimada" no existe en los datos y el
tiempo manual SHALL describirse como **clasificación manual (lectura + decisión de sector)**, sin componente
E2E ni de carga; la Nota de versiones (Anexo I.1) SHALL declarar inexacta la descripción de la v1.6.4 y
explicar por qué figuró en una versión entregada. En la rama A (la carga se sumó y los valores la incluyen),
el tiempo manual SHALL describirse como lectura más esa carga, la cifra primaria SHALL ser la del descuento de
10 s (65,6 %) y la Nota de versiones SHALL declarar inexacta la descripción de la v1.6.5. En ambas ramas la
fórmula "en el orden de 10 s, cuya magnitud exacta no consta" MUST NOT reaparecer como estimación sin fuente,
y el texto MUST NOT sugerir un cambio de valores que no ocurrió ("retirado el componente de carga",
"componente que la presente versión ya no contempla"). La Tabla 3 (`04:31`) SHALL dar una definición
operacional **por brazo**: manual = clasificación (lectura + decisión de sector, más la carga solo en la rama
A), automatizado = E2E (recepción → persistencia); el brazo manual MUST NOT describirse como "hasta la
persistencia confirmada del ticket". El Anexo K (`12-anexos.tex:351-367`) SHALL conservar los valores de sus
descuentos (−5 s → 56,6 s / 68,6 %; −10 s → 51,6 s / 65,6 %), con el −5 s rotulado como cota del redondeo
hacia arriba (c-251 E5) y el −10 s rotulado conforme a la rama de OQ-02.

#### Scenario: Fórmula de carga retirada

- **WHEN** se ejecuta `rg -n "en el orden de 10|carga del ticket|retirado el componente de carga|ya no contempla" "docs/Tesis/v10 (IA)/paper/sections/" "data/README.md"`
- **THEN** no hay coincidencias fuera de la Nota de versiones, y la descripción vigente del tiempo manual coincide con la rama registrada en OQ-02 de c-252

#### Scenario: Definición operacional por brazo

- **WHEN** se lee la Tabla 3 (`04:31`)
- **THEN** cada brazo (manual, automatizado) tiene su definición operacional: manual = clasificación (lectura + decisión, más la carga solo en la rama A de OQ-02); automatizado = E2E, y el brazo manual no se describe como "hasta la persistencia confirmada del ticket"

#### Scenario: Anexo K permanece como sensibilidad de redondeo

- **WHEN** se lee el Anexo K (`12-anexos.tex:351-367`)
- **THEN** los valores −5 s → 56,6 s / 68,6 % y −10 s → 51,6 s / 65,6 % se conservan, el −5 s figura como sensibilidad del redondeo hacia arriba y el −10 s se rotula según la rama de OQ-02, sin sugerir que los datos cambiaron

#### Scenario: Historia de la definición registrada en I.1

- **WHEN** se lee la Nota de versiones (Anexo I.1)
- **THEN** registra la descripción del tiempo manual de la v1.6.4, la de la versión vigente, cuál es la correcta según OQ-02 de c-252 y por qué la otra figuró en una versión entregada al tribunal
