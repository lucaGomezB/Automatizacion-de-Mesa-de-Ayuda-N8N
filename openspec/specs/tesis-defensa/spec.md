# tesis-defensa Specification

## Purpose
Definir el contrato del documento de respuestas del grupo a las 16 preguntas probables del tribunal de segunda instancia: que exista como documento del repositorio, que cada respuesta sea verificable contra artefactos versionados, que solo cite cifras canonicas o recalculables y que no se atribuya a un modelo de lenguaje.

## Requirements

### Requirement: Documento de respuestas a las 16 preguntas del tribunal

El proyecto SHALL mantener el documento `docs/defensa/respuestas-tribunal.md` con exactamente 16 respuestas, numeradas Q1 a Q16, una por cada pregunta de la Seccion 8 de la devolucion de segunda instancia del 11-11-2026, agrupadas en los cuatro bloques de esa seccion: procedencia de los datos (Q1 a Q4), contraste de tiempos (Q5 a Q9), clasificacion y supervision humana (Q10 a Q14) y marco legal (Q15 y Q16). Cada respuesta SHALL enunciar la pregunta y responderla de forma autonoma. El documento MUST NOT atribuirse a un modelo de lenguaje ni declarar autoria de IA.

#### Scenario: Las 16 respuestas presentes y numeradas

- **WHEN** se recorren los encabezados de `docs/defensa/respuestas-tribunal.md`
- **THEN** existen 16 respuestas identificadas Q1 a Q16, sin huecos ni duplicados
- **AND** cada respuesta reproduce la pregunta que responde

#### Scenario: Agrupacion en los cuatro bloques

- **WHEN** se leen las secciones del documento
- **THEN** las respuestas se agrupan en los cuatro bloques de la Seccion 8 (procedencia, tiempos, clasificacion y supervision humana, marco legal)
- **AND** cada bloque contiene las preguntas que le corresponden (4, 5, 5 y 2)

#### Scenario: Sin atribucion a un modelo de lenguaje

- **WHEN** se busca en el documento una atribucion de autoria a un modelo de lenguaje o a una herramienta de IA
- **THEN** no aparece ninguna
- **AND** el documento se presenta como respuesta del grupo

### Requirement: Verificabilidad de cada respuesta contra artefactos versionados

Cada respuesta SHALL apoyarse en artefactos versionados del repositorio y SHALL citar la ruta del artefacto del que proviene cada hecho, entre ellos `data/corpus_evaluacion_pseudonimizado.json`, `data/corpus_resultados_web_correo.json`, `data/corpus_resultados_telefonia.json`, `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`, `evaluation/data/campana/doble_etiquetado.csv`, `evaluation/data/campana/brazo_manual.csv`, `evaluation/data/campana/intervenciones.csv` y `evaluation/data/campana/plan_campana.csv`. Cuando un hecho solo puedan aportarlo los autores, la respuesta SHALL declararlo como tal y MUST NOT presentarlo como hecho verificado.

#### Scenario: Cada respuesta remite a un artefacto versionado

- **WHEN** se lee una respuesta
- **THEN** los hechos que afirma remiten a un artefacto versionado del repositorio
- **AND** ninguna respuesta se apoya solo en una afirmacion sin fuente

#### Scenario: Hecho no verificable declarado y no afirmado

- **WHEN** una respuesta depende de un dato que solo conocen los autores (por ejemplo el origen o la fecha exactos de un etiquetado no conservado)
- **THEN** la respuesta lo declara como pendiente o no verificable
- **AND** no lo presenta como un hecho comprobado

### Requirement: Cifras canonicas o recalculables

Toda cifra citada en una respuesta SHALL coincidir con un valor vigente del memo `docs/Tesis/Correcciones/numeros-canonicos.md` o SHALL ser recalculable desde los artefactos versionados. El documento MUST NOT introducir una cifra de resultado sin respaldo y MUST NOT reintroducir valores retirados, en particular el kappa de 0,87 como evidencia de fiabilidad.

#### Scenario: Cifra coincidente con el memo o recalculable

- **WHEN** se compara cada cifra del documento con el memo canonico
- **THEN** coincide con un valor vigente o se reproduce desde un artefacto versionado
- **AND** ninguna cifra queda sin fuente

#### Scenario: Valor retirado no reintroducido

- **WHEN** se busca el kappa de 0,87 en el documento
- **THEN** no aparece como evidencia de fiabilidad
- **AND** si se lo menciona, es para declarar que fue retirado y que sus planillas no se conservaron

### Requirement: Hechos de procedencia declarados con precision

El documento SHALL declarar, en el bloque de procedencia de los datos, los hechos que la devolucion puso en duda: (a) el kappa de 0,87 se retiro como evidencia de fiabilidad y su origen fue un oversight sin planilla conservada; (b) la version de julio (3-7-2026) informo resultados de un corpus sintetico; (c) el periodo relevado es del 16-06-2026 al 10-09-2026 con muestreo no probabilistico por conveniencia; (d) el registro primario de los 119 tiempos automatizados de correo y formulario se versiono y cubre 118 de 119 casos, con `R001` como unico caso sin registro; (e) las 81 llamadas del canal telefonico de la campana 2026-10 las recito un autor, y las llamadas del brazo telefonico de la campana complementaria las recitaron los operadores `O1` y `O2`.

#### Scenario: Kappa retirado con su origen

- **WHEN** se lee la respuesta sobre el kappa de 0,87 (Q1)
- **THEN** declara que el valor se retiro como evidencia y que su origen fue un oversight sin planilla conservada
- **AND** no lo presenta como acuerdo de los analistas originales

#### Scenario: Version de julio y corpus sintetico

- **WHEN** se lee la respuesta sobre las cifras de la version de julio (Q2)
- **THEN** declara que esas cifras (165,3 s, 92 %, W = 0, kappa = 0,87) provinieron de un corpus sintetico y fueron reemplazadas
- **AND** identifica la fecha de esa version (3-7-2026)

#### Scenario: Periodo y muestreo declarados

- **WHEN** se lee la respuesta sobre la seleccion de los 200 casos (Q3)
- **THEN** declara el periodo relevado del 16-06-2026 al 10-09-2026 y el muestreo por conveniencia
- **AND** no describe un muestreo estratificado con asignacion proporcional

#### Scenario: Registro primario declarado

- **WHEN** se lee la respuesta sobre la procedencia de los 119 tiempos (Q4)
- **THEN** declara que el registro primario pseudonimizado esta versionado y cubre 118 de los 119 casos
- **AND** identifica `R001` como el unico caso sin registro

#### Scenario: Recitacion de las llamadas declarada por campana

- **WHEN** se lee la respuesta sobre el efecto de la recitacion (Q8)
- **THEN** declara que las 81 llamadas del canal de la campana 2026-10 las recito un autor que conocia el caso
- **AND** declara que las llamadas del brazo telefonico de la campana complementaria las recitaron `O1` y `O2`
- **AND** no extrapola los tiempos telefonicos a usuarios reales

### Requirement: El documento precede a su incorporacion como anexo

El documento `docs/defensa/respuestas-tribunal.md` SHALL ser el artefacto fuente de las respuestas
y SHALL existir antes de cualquier edicion de `12-anexos.tex` que lo incorpore o lo retire. Su
inclusion como Anexo J depende de la decision de los autores registrada en
`docs/Tesis/Correcciones/dictamen-correcciones.md` (OQ3 de c-221):

- Si los autores retiran el anexo, el documento SHALL conservarse como material de preparacion de
  la defensa, fuera del cuerpo y de los anexos de la tesis; `12-anexos.tex` MUST NOT contener la
  etiqueta `sec:anexo-respuestas-tribunal` y ninguna seccion de la tesis SHALL remitir a ella.
- Si los autores conservan el anexo, el Anexo J SHALL reproducir el contenido del documento fuente
  sin alterar las respuestas ni su numeracion, y las cifras de la validacion fuera de muestra
  SHALL actualizarse al resultado arbitrado en el documento fuente y en el anexo por igual.

Mientras la decision no este registrada, el estado vigente del anexo MUST NOT cambiar.

#### Scenario: El documento fuente precede al anexo

- **WHEN** se verifica el orden de los entregables del change
- **THEN** `docs/defensa/respuestas-tribunal.md` existe con sus 16 respuestas antes de cualquier edicion de `12-anexos.tex` que incorpore o retire el Anexo J
- **AND** si el Anexo J se conserva, reproduce las mismas 16 respuestas sin cambios de fondo respecto del documento fuente

#### Scenario: Anexo J retirado por decision de los autores

- **WHEN** la decision registrada es retirar el anexo
- **THEN** `12-anexos.tex` no contiene la etiqueta `sec:anexo-respuestas-tribunal`
- **AND** `docs/defensa/respuestas-tribunal.md` se conserva con sus 16 respuestas
- **AND** la compilacion no informa referencias indefinidas

#### Scenario: Anexo J conservado por decision de los autores

- **WHEN** la decision registrada es conservar el anexo
- **THEN** `12-anexos.tex` contiene la etiqueta `sec:anexo-respuestas-tribunal` con las 16 respuestas del documento fuente
- **AND** las cifras de la validacion fuera de muestra del anexo y del documento fuente coinciden entre si y con el memo canonico
