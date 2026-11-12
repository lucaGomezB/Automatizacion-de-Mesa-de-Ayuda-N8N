## MODIFIED Requirements

### Requirement: AI writing pattern removal

The thesis prose across all 11 section files SHALL be revised to eliminate AI-generated writing patterns and to recover concision (devolucion de segunda instancia del tribunal del 11-11-2026, N-07). The revision SHALL NOT alter technical claims, numerical data, or factual content. Ademas, el texto SHALL reducir la longitud de las oraciones y las formulas de relleno, medido contra una linea base registrada con una regla de conteo unica: las oraciones de mas de 60 palabras SHALL bajar de su valor de partida y las de mas de 40 palabras SHALL bajar su porcentaje de partida; las ocurrencias de "de modo que" SHALL reducirse respecto de su valor de partida. El texto SHALL retirar las valoraciones sin respaldo (por ejemplo, "una via practicamente util") y SHALL evitar reiterar cifras ya reportadas en el capitulo de resultados. La revision MUST NOT introducir oraciones nuevas de mas de 60 palabras, MUST NOT cambiar ninguna cifra canonica ni el contenido sustantivo, y MUST NOT tocar la recitacion de las llamadas del canal telefonico, que esta verificada como correcta.

#### Scenario: Mechanical enumeration removed from conclusions
- **WHEN** reading Chapter 9 (conclusiones)
- **THEN** the text does NOT contain sequential phrases like "En relacion con el primer objetivo especifico... En relacion con el segundo..."
- **AND** the relationship between objectives and findings is expressed through flowing narrative rather than numbered enumeration

#### Scenario: Repetitive rhetorical formulas eliminated
- **WHEN** reading any chapter
- **THEN** phrases like "conviene reconocer explicitamente", "resulta pertinente destacar", and "es dable senalar" do NOT appear more than once in the entire thesis
- **AND** opening phrases across paragraphs exhibit variety in structure and vocabulary

#### Scenario: Sentence rhythm varies
- **WHEN** analyzing sentence length distribution across a chapter
- **THEN** the text contains a mix of short declarative sentences (under 20 words), medium analytical sentences (20-35 words), and longer subordinated sentences (35+ words)
- **AND** no paragraph consists exclusively of long subordinated sentences

#### Scenario: Analytical depth beyond description
- **WHEN** reading any results or discussion section
- **THEN** the text goes beyond describing what happened
- **AND** includes interpretation of WHY results occurred, what constraints emerged, what tradeoffs were encountered, and what surprised the author

#### Scenario: Technical claims preserved
- **WHEN** comparing the revised text against the original source
- **THEN** all numerical values (F1 scores, node counts, iteration numbers, percentages) are identical
- **AND** all technical claims about the software system remain factually accurate

#### Scenario: Objetivos de concision medibles

- **WHEN** se mide la longitud de las oraciones de `sections/0*.tex` a `sections/12-*.tex` con la regla de conteo registrada (una oracion por signo de cierre; comandos LaTeX, matematicas, pies de tabla y listados excluidos) antes y despues del pase
- **THEN** el numero de oraciones de mas de 60 palabras es menor que el de la linea base (de partida cercano a 24) y no queda ninguna oracion de mas de 60 palabras introducida por el pase
- **AND** el porcentaje de oraciones de mas de 40 palabras es menor que el de la linea base (de partida cercano a 8,8 %)
- **AND** la linea base y el resultado se consignan con el comando y su salida en `docs/Tesis/Correcciones/dictamen-correcciones.md`

#### Scenario: Formula "de modo que" acotada

- **WHEN** se cuentan las ocurrencias de "de modo que" en las secciones de la tesis antes y despues del pase
- **THEN** el conteo final es menor que el de la linea base (de partida cercano a 29)
- **AND** ninguna ocurrencia sustituida altera un conector que aporte una relacion causal necesaria para el argumento

#### Scenario: Valoraciones residuales sin respaldo retiradas

- **WHEN** se leen los capitulos con valoraciones (en particular las conclusiones)
- **THEN** no quedan expresiones valorativas sin respaldo empirico (por ejemplo "una via practicamente util" referida al tiempo telefonico, que es cota inferior y se midio con llamadas recitadas)
- **AND** las cifras repetidas del capitulo de resultados se remiten con `\autoref` en lugar de reiterarse

### Requirement: Nota de versiones y trazabilidad de la auditoria del tribunal en el Anexo I

El Anexo I (`sec:anexo-trazabilidad`, `12-anexos.tex`) SHALL comenzar con una subseccion breve
"Nota de versiones" con `\label{subsec:nota-versiones}`, de media pagina como maximo, que declare
que la version del 3 de julio de 2026 informo una reduccion del tiempo medio de 165,3 s a 18,2 s
(89,0 %), exactitud de 92 %, W = 0 y kappa = 0,87; que los tiempos, la exactitud y el estadistico
provenian de un corpus sintetico de 200 casos generado durante el desarrollo, descartado y
eliminado del repositorio; que la version actual los reemplaza por los del corpus real
pseudonimizado (61,6 s a 17,76 s, 71,2 %; 73,5 %; W = 363); y que el kappa = 0,87 figuraba en esa
version, sus planillas no se conservan y ya no se presenta como evidencia. La nota MUST NOT
afirmar que el 0,87 provenia del corpus sintetico. La trazabilidad SHALL tener como primera fila de
su tabla la auditoria integral del tribunal del 4 de agosto de 2026 (105 hallazgos, 28 criticos,
3,9/10; archivo en `auditorias/`), que origino la reformulacion con datos reales: esa auditoria
SHALL figurar como una fila de la tabla (y no solo como prosa), con los datos que el texto ya
declara y sin inventar cifras. La serie SHALL
distinguir (a) esa auditoria, (b) las nueve autoevaluaciones internas generadas con un modelo de
lenguaje y (c) la devolucion de segunda instancia del tribunal del 11 de noviembre de 2026. El
Anexo I SHALL cerrar con la tabla `tab:trazabilidad-devolucion-segunda-instancia` con una fila por
observacion N-01 a N-16 (observacion en 4 a 8 palabras, seccion corregida con `\autoref`, estado
"Atendida", "Atendida en parte; resta dato de los autores" o "Pendiente"), sin numeros de linea.
La confirmacion escrita del consentimiento (A1) SHALL figurar como atendida el 10 de noviembre de
2026, segun `docs/campana-medicion/confirmacion-posterior-consentimiento.md`.

#### Scenario: Nota de versiones presente

- **WHEN** se buscan "sintétic", "subsec:nota-versiones" y "165,3" en `12-anexos.tex`
- **THEN** cada busqueda devuelve al menos una coincidencia
- **AND** la nota no atribuye el 0,87 al corpus sintetico

#### Scenario: Auditoria del 4 de agosto como primera fila

- **WHEN** se compila y se lee la trazabilidad del Anexo I
- **THEN** la primera fila de su tabla es la auditoria del tribunal del 4 de agosto de 2026 con sus datos declarados (105 hallazgos, 28 criticos, 3,9/10) y su archivo en `auditorias/`
- **AND** esa auditoria figura como fila de tabla, no unicamente como prosa
- **AND** la serie distingue la auditoria, las autoevaluaciones con modelo de lenguaje y la devolucion del 11-11

#### Scenario: Tabla de la devolucion

- **WHEN** se compila y se lee el Anexo I
- **THEN** figura `tab:trazabilidad-devolucion-segunda-instancia` con N-01 a N-16 y sus `\autoref` resueltos
- **AND** N-16 figura "Pendiente"; N-01, N-02, N-04, N-05 y N-13 "Atendida en parte; resta dato de los autores"; el resto "Atendida"

#### Scenario: Consentimiento actualizado

- **WHEN** se busca "diferida" referido a A1 en `12-anexos.tex`
- **THEN** no hay coincidencias
- **AND** A1 figura atendida el 10 de noviembre de 2026

## ADDED Requirements

### Requirement: Afinado de escritura por capitulo segun las calificaciones de la devolucion

La revision de escritura SHALL atender, capitulo por capitulo, el "Motivo principal" que la seccion 6 de la devolucion de segunda instancia del 11-11-2026 registra para cada capitulo evaluado, sin cambiar cifras canonicas ni el contenido sustantivo. La correspondencia entre el capitulo evaluado y el archivo es: Introduccion = `01-introduccion.tex`; Marco teorico = `02-marco-teorico.tex` y `03-estado-del-arte.tex`; Marco metodologico = `04-marco-metodologico.tex`; Desarrollo = `06-implementacion.tex` y `07-resultados.tex`; Resultados = `07-resultados.tex`; Arquitectura = `05-arquitectura.tex`; Discusion = `08-discusion.tex`; Conclusiones = `09-conclusiones.tex` y `10-recomendaciones.tex`; Referencias = `Bibliography_base.bib` y la lista de referencias; Anexos = `12-anexos.tex`. El afinado MUST NOT reintroducir observaciones ya cerradas por `c-196` (por ejemplo, el kappa de 0,87 como evidencia, los identificadores de cambio en el cuerpo, la procedencia de los tiempos o la seleccion de los casos) y MUST NOT tocar las secciones `4.5`, `4.8` ni `9.1` por la recitacion de las llamadas (N-06, verificada como correcta). Cada pasaje editado SHALL conservarse registrado en `docs/Tesis/Correcciones/dictamen-correcciones.md` con su ubicacion previa.

#### Scenario: Afinado guiado por el Motivo principal de cada capitulo

- **WHEN** se revisa el diff de escritura de `c-197` contra el "Motivo principal" de la seccion 6 de la devolucion
- **THEN** cada capitulo evaluado (Introduccion, Marco teorico, Marco metodologico, Desarrollo, Resultados, Arquitectura, Discusion, Conclusiones, Referencias y Anexos) registra al menos un ajuste de escritura, claridad o concision coherente con su "Motivo principal"
- **AND** el registro del change enumera, por capitulo, el pasaje ajustado y el motivo atendido

#### Scenario: Sin regresion de las correcciones de c-196

- **WHEN** se buscan en `sections/*.tex`, tras el pase de `c-197`, el kappa de 0,87 como evidencia, los identificadores de cambio (`c-NNN`/`C-NN`) fuera del Anexo I y las declaraciones de procedencia de tiempos y de seleccion de casos introducidas por `c-196`
- **THEN** el kappa de 0,87 sigue sin presentarse como evidencia; los identificadores siguen fuera del cuerpo; y las declaraciones de procedencia se conservan sin cambios de sentido

#### Scenario: Secciones protegidas intactas

- **WHEN** se compara el diff de `c-197` en `04-marco-metodologico.tex` y `08-discusion.tex` con las secciones `4.5`, `4.8` y `9.1`
- **THEN** no hay cambios motivados por la recitacion de las llamadas telefonicas
- **AND** esas secciones conservan el texto vigente de `c-196` sobre la procedencia de los tiempos y la recitacion
