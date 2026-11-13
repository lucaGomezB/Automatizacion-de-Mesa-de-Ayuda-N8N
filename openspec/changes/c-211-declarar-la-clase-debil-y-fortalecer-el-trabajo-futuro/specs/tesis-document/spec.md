## ADDED Requirements

### Requirement: Declaracion explicita de la clase medida mas debil

La tesis SHALL declarar de forma explicita que `Sistemas` es la clase de peor desempeno medido del clasificador en la validacion fuera de muestra: F1 0,2222 sobre un soporte de 5 casos, con 3 de sus 5 casos predichos como `Soporte Tecnico Software`. La declaracion SHALL presentarse sin atenuar el valor medido y MUST NOT afirmar ni sugerir que el clasificador vaya a mejorar. La tesis SHALL caracterizar la frontera entre `Sistemas` y `Soporte Tecnico Software` como un problema de taxonomia o de criterio de etiquetado, SHALL senalar que el soporte pequeno vuelve imprecisa la estimacion, y SHALL proponer como proximo paso de medicion el sobremuestreo de las dos clases adyacentes con doble etiquetado y arbitraje de los casos discordantes. Los valores SHALL tomarse verbatim del artefacto versionado `evaluation/data/campana/analisis/analisis_fuera_de_muestra_c205.json` y MUST NOT fijarse por separado.

#### Scenario: La clase debil se declara con su cifra

- **WHEN** se lee la discusion de la tesis (`08-discusion.tex`) o las conclusiones (`09-conclusiones.tex`)
- **THEN** `Sistemas` se identifica como la clase medida mas debil con F1 0,2222 sobre 5 casos
- **AND** se declara que 3 de esos 5 casos se predijeron como `Soporte Tecnico Software`

#### Scenario: No se sobreafirma una mejora

- **WHEN** se lee el pasaje que declara la clase `Sistemas`
- **THEN** no se afirma ni se sugiere que el clasificador vaya a mejorar esa clase
- **AND** la debilidad se declara sin atenuarla en vaguedades

#### Scenario: La frontera se caracteriza y tiene proximo paso

- **WHEN** se busca en la tesis el tratamiento de la frontera `Sistemas`--`Soporte Tecnico Software`
- **THEN** se la caracteriza como un problema de taxonomia o de criterio de etiquetado
- **AND** se propone como proximo paso de medicion el sobremuestreo de ambas clases con doble etiquetado y arbitraje

### Requirement: Trabajos futuros ordenados por prioridad y fundamentados

La seccion de trabajos futuros (`10-recomendaciones.tex`) SHALL ordenar sus subsecciones de acuerdo con la prioridad declarada en su introduccion. Cada item SHALL estar fundamentado en una limitacion medida (con su cifra) o SHALL traer un criterio de exito explicito y/o un tamano de muestra. La seccion MUST NOT incluir items que no deriven de una limitacion medida sin rotularlos explicitamente como ampliaciones de producto no derivadas de una limitacion medida. La tesis MUST NOT cambiar ninguna cifra canonica al reordenar o fundamentar los items.

#### Scenario: El orden sigue la prioridad declarada

- **WHEN** se leen las subsecciones de `10-recomendaciones.tex` en orden
- **THEN** primero figuran los items que atacan defectos medidos, luego los que fortalecen la evidencia o el clasificador, y al final las extensiones funcionales
- **AND** el orden coincide con la prioridad declarada en el parrafo introductorio

#### Scenario: Cada item esta fundamentado

- **WHEN** se revisa cada subseccion de trabajos futuros
- **THEN** cada item se ata a una limitacion medida con su cifra, o trae un criterio de exito explicito y/o un tamano de muestra

#### Scenario: Las ampliaciones de producto se rotulan

- **WHEN** se leen los items de expansion de producto (canales de mensajeria, panel de monitoreo, inventario/CMDB, base de conocimientos, automatizacion de la resolucion y agente conversacional telefonico)
- **THEN** no aparecen como subsecciones prioritarias fundamentadas
- **AND** se rotulan de forma explicita como ampliaciones de producto no derivadas de una limitacion medida

### Requirement: La validacion fuera de muestra no se informa como trabajo futuro

La tesis SHALL informar los resultados de la validacion fuera de muestra (exactitud estricta 0,8447, macro-F1 0,7447, n efectivo de 103 con 47 discordantes excluidos) en el capitulo de resultados, que es el lugar que les corresponde. La seccion de trabajos futuros MUST NOT re-informar esos resultados: SHALL limitarse al trabajo futuro derivado (repetir la validacion sobre otros corpus, con muestras mayores y sin el sesgo de exclusion) y remitir a resultados para las cifras.

#### Scenario: Los resultados quedan en resultados

- **WHEN** se lee la seccion de trabajos futuros (`10-recomendaciones.tex`)
- **THEN** no figuran alli las cifras de exactitud, macro-F1 ni del n efectivo de la validacion fuera de muestra
- **AND** la subseccion de validacion independiente remite a resultados para las cifras

#### Scenario: El trabajo futuro derivado se conserva

- **WHEN** se lee la subseccion de validacion sobre un corpus independiente
- **THEN** se conserva la propuesta de repetir la validacion sobre otros corpus, con muestras mayores y sin el sesgo de exclusion
