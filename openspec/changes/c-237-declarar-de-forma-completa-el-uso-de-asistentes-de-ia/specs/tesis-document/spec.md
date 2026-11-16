## ADDED Requirements

### Requirement: Declaracion completa del uso de asistentes de inteligencia artificial

El Anexo I (`sec:anexo-trazabilidad` en `docs/Tesis/v10 (IA)/paper/sections/12-anexos.tex`) SHALL contener una declaracion del uso de asistentes de inteligencia artificial, en una subseccion propia etiquetada `subsec:declaracion-uso-ia` (o reescrita en el lugar del Anexo I.2 si los autores lo deciden), que reemplace la declaracion acotada a "la correccion de estilo y la edicion del texto" y a "la generacion de diagramas de flujo". La declaracion SHALL cubrir cinco ambitos: (a) codigo del sistema, (b) scripts de analisis y evaluacion, (c) texto de la tesis, (d) diagramas y (e) autoevaluaciones estilo CONEAU; para cada ambito SHALL indicar la herramienta y el modelo, que produjo el asistente y el procedimiento con que los autores verificaron cifras y afirmaciones. La declaracion SHALL ser coherente con el inventario versionado del uso de asistentes y MUST NOT subdeclarar: todo ambito en el que el inventario registre asistencia SHALL figurar, y la asistencia sobre el texto MUST NOT limitarse a estilo y edicion cuando el inventario registre redaccion de prosa encargada a un agente. La declaracion MUST NOT sobredeclarar: un procedimiento de verificacion SHALL figurar solo si los autores confirmaron por escrito haberlo aplicado, y una verificacion no exhaustiva SHALL declararse como tal. SHALL declarar la normativa de la facultad aplicable o, si no existe una norma especifica, declarar su ausencia. SHALL remitir al inventario versionado, presentar el conteo de commits con marca de co-autoria de un asistente como cota inferior y no como proporcion de autoria, identificar a los autores solo por su condicion de autores (sin datos personales adicionales), ocupar como maximo una pagina del PDF y MUST NOT adoptar formato de bitacora (fechas de sesion o enumeracion de changes). El texto de la declaracion MUST NOT escribirse en el `.tex` antes de que las respuestas de los autores esten registradas en el inventario.

#### Scenario: Declaracion vieja reemplazada

- **WHEN** se busca en `12-anexos.tex` el pasaje "para la correccion de estilo y la edicion del texto, y para la generacion de diagramas de flujo"
- **THEN** el pasaje ya no figura como declaracion de uso de IA
- **AND** existe una unica etiqueta `subsec:declaracion-uso-ia` (o la reescritura en el lugar de I.2 decidida por los autores)

#### Scenario: Cinco ambitos con herramienta, producto y verificacion

- **WHEN** se lee la declaracion
- **THEN** figuran el codigo del sistema, los scripts de analisis y evaluacion, el texto de la tesis, los diagramas y las autoevaluaciones estilo CONEAU
- **AND** cada ambito indica herramienta y modelo, que produjo el asistente y el procedimiento de verificacion de los autores

#### Scenario: Sin subdeclaracion frente al inventario

- **WHEN** se contrasta la declaracion con el inventario versionado
- **THEN** cada ambito con asistencia registrada en el inventario figura en la declaracion
- **AND** el ambito del texto declara la redaccion de prosa asistida, no solo correccion de estilo

#### Scenario: Sin sobredeclaracion de la verificacion

- **WHEN** la declaracion enuncia un procedimiento de verificacion
- **THEN** ese procedimiento consta como confirmado por los autores en la seccion de respuestas del inventario
- **AND** una verificacion por muestreo o no exhaustiva se declara como tal

#### Scenario: Conteo como cota inferior

- **WHEN** la declaracion cita el numero de commits con marca de co-autoria de un asistente
- **THEN** lo presenta como cota inferior, con la ref de conteo y la remision al inventario
- **AND** no lo traduce a un porcentaje de autoria del texto o del codigo

#### Scenario: Normativa declarada

- **WHEN** se lee el cierre de la declaracion
- **THEN** cita la norma de la facultad aplicable o declara que no existe una norma especifica

#### Scenario: Extension y registro

- **WHEN** se compila el PDF
- **THEN** la declaracion ocupa como maximo una pagina
- **AND** no contiene fechas de sesion ni enumeracion de changes

#### Scenario: Compuerta de autores

- **WHEN** se edita el `.tex` con la declaracion nueva
- **THEN** el inventario ya registra, por alias y con fecha, las respuestas de los autores sobre herramientas, verificacion, distribucion del trabajo y normativa

### Requirement: Inventario reproducible del uso de asistentes de inteligencia artificial

El repositorio SHALL contener un inventario versionado del uso de asistentes de IA en `docs/Tesis/Correcciones/inventario-uso-asistentes-ia.md`, derivado del propio repositorio y regenerable. El inventario SHALL incluir: los conteos de commits con y sin marca `Co-Authored-By` de un asistente, por periodo (al menos el historial completo y el rango de la version evaluada) y por modelo, con la ref de conteo y el comando exacto; la lista de artefactos de orquestacion de agentes con su funcion; el mapa de changes archivados por ambito (codigo del sistema, scripts de analisis y evaluacion, prosa de la tesis, flujo N8N) con ejemplos verificables; las respuestas de los autores a la compuerta; y el texto fuente de la declaracion. Los conteos SHALL producirse con `docs/Tesis/Correcciones/contar_uso_asistentes.py`, cubierto por `docs/Tesis/Correcciones/test_contar_uso_asistentes.py`. Ni el script ni el inventario MUST emitir nombres reales ni correos de personas; los autores SHALL identificarse solo por alias (T1, T2, T3). Un co-autor que no sea un asistente MUST NOT contarse como asistencia.

#### Scenario: Conteos reproducibles en una ref fija

- **WHEN** se ejecuta `contar_uso_asistentes.py` sobre el rango `v1.2.18..v1.5.2`
- **THEN** informa 253 commits, de los cuales 41 llevan marca de co-autoria de un asistente
- **AND** el inventario registra la ref y el comando usados

#### Scenario: Desglose por modelo

- **WHEN** se ejecuta el conteo sobre el historial completo
- **THEN** el inventario informa el total con marca y su desglose por modelo de asistente
- **AND** el total coincide con la suma del desglose

#### Scenario: Co-autor humano excluido

- **WHEN** un commit lleva un `Co-Authored-By` que no corresponde a un asistente
- **THEN** el script no lo cuenta como commit asistido

#### Scenario: Mapa de changes por ambito

- **WHEN** se lee el mapa de changes del inventario
- **THEN** cada ambito informa cuantos changes archivados lo nombran en sus tareas
- **AND** incluye al menos un ejemplo verificable por ambito, como el bloque "Prosa de la tesis" de c-222

#### Scenario: Sin datos personales

- **WHEN** se inspeccionan la salida del script y el inventario
- **THEN** no contienen nombres reales ni correos de personas
- **AND** los autores figuran solo como T1, T2 y T3

#### Scenario: Prueba del script

- **WHEN** se ejecuta `python -m unittest test_contar_uso_asistentes -v` desde `docs/Tesis/Correcciones/`
- **THEN** todas las pruebas pasan
