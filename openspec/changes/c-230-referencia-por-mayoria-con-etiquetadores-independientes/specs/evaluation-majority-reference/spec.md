## Purpose

Construir una referencia de verdad por mayoria de varios etiquetadores independientes, sin arbitro
unico, con funciones puras probadas sin datos del estudio, un protocolo declarado y constatado antes
de etiquetar y compuertas de procedencia y etica/legal previas a cualquier computo sobre etiquetas
reales. Su primer destino es la muestra probabilistica de `evaluation-probabilistic-sampling`.

## ADDED Requirements

### Requirement: MR-001 — Funciones puras de la referencia por mayoria

El modulo `evaluation/mayoria.py` SHALL exponer funciones puras, sin E/S ni red, que dado el conjunto
de etiquetas de un caso y un umbral declarado devuelvan: el sector con al menos `umbral` votos o la
marca `sin_mayoria` con el recuento por sector; el conjunto laxo de sectores adicionales con al menos
`umbral` votos, sin repetir el principal; y la referencia de un conjunto de casos con su `origen`
(`mayoria` o `sin_mayoria`) y sus conteos. Las funciones SHALL admitir cantidad variable de
etiquetadores por caso y MUST NOT imputar etiquetas faltantes, promediar etiquetas ni elegir una
etiqueta para un caso sin mayoria. Las pruebas SHALL escribirse antes que el modulo, con casos
sinteticos, y el modulo MUST NOT modificar los contratos de `evaluation/doble_etiquetado.py` ni de
`evaluation/arbitraje.py`.

#### Scenario: Mayoria absoluta

- **WHEN** tres de cinco etiquetas sinteticas asignan el mismo sector con umbral `3`
- **THEN** la funcion devuelve ese sector con origen `mayoria`

#### Scenario: Empate sin mayoria

- **WHEN** las etiquetas sinteticas forman `2-2-1` o `2-1-1-1` con umbral `3`
- **THEN** la funcion devuelve `sin_mayoria` con el recuento por sector
- **AND** no elige ninguna etiqueta

#### Scenario: Cobertura variable

- **WHEN** un caso sintetico tiene menos etiquetadores que el resto
- **THEN** la funcion opera con las etiquetas presentes y no imputa las faltantes

#### Scenario: Pruebas antes del modulo

- **WHEN** se revisa el desarrollo
- **THEN** las pruebas de `evaluation/tests/test_mayoria.py` existieron antes que el modulo y fallaron por su ausencia

### Requirement: MR-002 — Protocolo declarado y constatado antes de etiquetar

El protocolo `docs/campana-medicion/protocolo-referencia-mayoria.md` SHALL fijar, antes de entregar
cualquier paquete de etiquetado: el numero de etiquetadores por caso (por defecto cinco, minimo tres),
el umbral de mayoria, el tratamiento de los casos `sin_mayoria` sin recurrir a la decision de un
unico etiquetador ni a un arbitro, la regla del conjunto laxo, el cegado, el codebook congelado y la
herramienta de etiquetado con su formato de exportacion y sus marcas temporales propias. Antes de
entregar el paquete ciego, el director de la tesis SHALL firmar una constancia fechada del documento
(o de su SHA-256), cuyo original queda en su custodia y cuyo hash se versiona. La fecha de commit MUST
NOT usarse como unica prueba de anterioridad. Cambiar la regla despues de ver etiquetas MUST
invalidar la referencia.

#### Scenario: Regla constatada antes de etiquetar

- **WHEN** se entrega el primer paquete ciego
- **THEN** existe la constancia del director con fecha anterior y el hash versionado coincide con el protocolo vigente
- **AND** el protocolo fija numero de etiquetadores, umbral, `sin_mayoria`, conjunto laxo, cegado y herramienta

#### Scenario: Sin arbitro unico

- **WHEN** se lee el tratamiento de los casos `sin_mayoria`
- **THEN** ninguno se resuelve por la decision de una sola persona
- **AND** el conteo y el tratamiento se informan

### Requirement: MR-003 — Compuerta de procedencia previa a todo computo sobre etiquetas reales

Ningun computo sobre etiquetas reales SHALL ejecutarse sin un acta con fecha, firmada por el director
(o por un tercero que los autores designen y el director acepte), que verifique contra la evidencia
primaria: (a) una planilla cruda por etiquetador, exportada de la herramienta declarada, con las
marcas temporales que la herramienta registra, nunca reconstruidas ni completadas a mano; (b) una
constancia firmada por cada etiquetador y la constancia de extraccion de la organizacion, con los
originales en custodia del director y el SHA-256 de cada planilla cruda versionado; (c) que los
etiquetadores no son autores ni operadores medidos, con su vinculo con los autores declarado; y (d)
que los textos etiquetados son incidentes reales del registro de la organizacion, ninguno redactado
por los autores ni generado o asistido por IA. Ninguna comprobacion estadistica de forma MUST
sustituir esa verificacion.

#### Scenario: Acta previa

- **WHEN** se intenta construir la referencia con etiquetas reales
- **THEN** existe el acta que cubre (a) a (d)
- **AND** sin acta, la referencia no se construye y el bloqueo se registra

#### Scenario: Planilla cruda intacta

- **WHEN** se coteja una planilla con su exportacion original
- **THEN** su SHA-256 coincide y sus marcas temporales son las de la herramienta

### Requirement: MR-004 — Compuerta etica y legal de los etiquetadores y los textos

Antes de entregar textos a los etiquetadores, SHALL existir la autorizacion institucional y la base
de licitud de la muestra (`evaluation-probabilistic-sampling`, PS-004), y cada etiquetador SHALL haber
firmado un consentimiento escrito previo con una plantilla versionada sin nombres, cuyos originales
custodia el director. Los etiquetadores SHALL recibir solo textos pseudonimizados y cubiertos por la
autorizacion. Este change MUST NOT enviar textos a terceros. El repositorio publico SHALL contener
solo material pseudonimizado y autorizado; las etiquetas de un sujeto sin consentimiento registrado
MUST NOT usarse.

#### Scenario: Consentimiento previo

- **WHEN** se entrega el paquete a un etiquetador
- **THEN** su consentimiento escrito previo esta registrado con fecha y alias
- **AND** la plantilla no contiene nombres ni la correspondencia alias-identidad

#### Scenario: Sujeto sin consentimiento excluido

- **WHEN** un etiquetador no tiene consentimiento registrado
- **THEN** sus etiquetas no entran en la referencia y la limitacion se declara

### Requirement: MR-005 — Registro de etiquetadores independientes con alias nuevos

`evaluation/data/campana/registro_sujetos.csv` SHALL registrar a los etiquetadores de la referencia
por mayoria con alias nuevos a partir de `E6` y codigos de persona libres a partir de `P12`, sin
reutilizar alias previos y sin nombres, correos ni legajos. Por defecto, cada uno SHALL ser una
persona distinta de todas las ya registradas; el solape SHALL verificarse con
`validar_registro_sujetos`. El protocolo SHALL declarar el vinculo de cada etiquetador con los
autores. La correspondencia alias-identidad SHALL custodiarse fuera del repositorio.

#### Scenario: Registro sin solape

- **WHEN** se agregan los etiquetadores nuevos
- **THEN** sus alias empiezan en `E6`, sus codigos en `P12` y `validar_registro_sujetos` no reporta solape
- **AND** ninguna fila contiene datos personales

### Requirement: MR-006 — Referencia de la muestra probabilistica

Con las compuertas cerradas, la referencia de la muestra de `evaluation-probabilistic-sampling` SHALL
construirse con las funciones de MR-001 y la regla constatada de MR-002, a partir del etiquetado
ciego: los etiquetadores MUST NOT ver etiquetas ajenas, la referencia ni las predicciones. SHALL
versionarse, con su SHA-256, la referencia, un sidecar con el `origen` de cada caso y el conteo de
`sin_mayoria`, y el resultado del kappa de Fleiss con la matriz por pares. Esta referencia es la que
completa el **corpus probabilistico acreditado** (`evaluation-probabilistic-sampling`, PS-009); sin
ella, o con alguna compuerta abierta, el conjunto MUST NOT recibir ese nombre. La referencia SHALL
rotularse como propia de esa muestra y MUST NOT presentarse como sustituto de la referencia del
corpus de 200 casos. Ningun artefacto retirado del ejemplar por `c-235` MUST usarse como insumo,
ancla ni comparador.

#### Scenario: Etiquetado ciego

- **WHEN** se entrega el paquete a un etiquetador
- **THEN** recibe solo `id_caso`, texto pseudonimizado, una plantilla vacia y el codebook congelado

#### Scenario: Artefactos versionados

- **WHEN** se construye la referencia
- **THEN** la referencia, el sidecar y el Fleiss quedan versionados con su SHA-256
- **AND** el sidecar declara el conteo de `sin_mayoria`

#### Scenario: Sin insumos retirados

- **WHEN** se revisan las entradas del ensamblado de la referencia
- **THEN** ninguna es un artefacto retirado del ejemplar
