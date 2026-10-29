## ADDED Requirements

### Requirement: Figuras de componentes y de secuencia coherentes con el gate de revision vigente

Las figuras `fig:componentes` y `fig:secuencia` de `docs/Tesis/v10 (IA)/paper/sections/05-arquitectura.tex` SHALL generarse desde sus fuentes Mermaid versionadas (`docs/diagrams/componentes.md` y `docs/diagrams/secuencia.md`) y SHALL representar el gate de revision humana de la configuracion entregada tal como lo implementan `App/Backend/app/classifiers/hybrid.py`, `App/Backend/app/services/incidente_service.py` y `openspec/config.yaml` (`conventions.thresholds`): (a) la etapa deterministica cortocircuita cuando la senal es dominante y el puntaje `score_correctitud` alcanza 0,5166, y no deriva a revision por su confianza; (b) la regla de confianza menor que 0,70 se aplica solo a la salida de Gemini; (c) la etapa de reserva fija la confianza en 0,0 y deriva siempre a revision; y (d) el reportante no identificado en el directorio de empleados deriva a revision, combinado con las condiciones anteriores, rotulado con su origen (c-82) y su fecha (13-10-2026) como posterior a la campana de medicion. Las fuentes y los PNG MUST NOT contener un umbral de 0,90 sobre la confianza ni aplicar la regla de 0,70 a la etapa deterministica. Las leyendas SHALL declarar que ambas figuras describen la configuracion entregada (release `v1.2.5`) y SHALL remitir, mediante referencia cruzada, a la tabla de configuracion evaluada frente a entregada de la tesis. Los rotulos de los PNG MUST leerse completos, sin truncamientos causados por caracteres especiales de Mermaid, y el participante N8N de la fuente de secuencia SHALL citar la version de imagen que declara `docker-compose.yml`.

#### Scenario: Fuentes sin el umbral retirado

- **WHEN** se buscan "0.90", "0,90" y la condicion de confianza mayor o igual que 0,90 en `docs/diagrams/componentes.md` y `docs/diagrams/secuencia.md`
- **THEN** no aparecen
- **AND** la regla de 0,70 aparece asociada unicamente a la salida de Gemini

#### Scenario: Las cuatro condiciones del gate representadas

- **WHEN** se inspeccionan los PNG `componentes.png` y `secuencia.png` regenerados
- **THEN** figuran el cortocircuito por `score_correctitud` mayor o igual que 0,5166 con senal dominante, la regla de confianza menor que 0,70 sobre Gemini, la etapa de reserva con confianza 0,0 y revision, y el reportante no identificado en el directorio
- **AND** ninguna rama aplica la regla de 0,70 a la etapa deterministica

#### Scenario: Disparador por directorio rotulado con su fecha

- **WHEN** se lee el rotulo del disparador por reportante no identificado en ambas figuras
- **THEN** cita c-82 y la fecha 13-10-2026
- **AND** lo declara posterior a la campana de medicion

#### Scenario: Leyendas de la configuracion entregada

- **WHEN** se leen las leyendas de `fig:componentes` y `fig:secuencia` en el PDF compilado
- **THEN** declaran que describen la configuracion entregada (release `v1.2.5`)
- **AND** remiten a la tabla de configuracion evaluada frente a entregada con una referencia cruzada resuelta, sin "??"

#### Scenario: Rotulos completos y version de N8N

- **WHEN** se inspecciona el PNG de la secuencia y su fuente
- **THEN** los mensajes de confirmacion y de aviso al usuario se leen completos
- **AND** el participante N8N de `docs/diagrams/secuencia.md` cita la version de imagen de `docker-compose.yml`

### Requirement: Figura de arquitectura del sistema de cinco capas y tres canales desde fuente versionada

La figura `fig:arquitectura` SHALL representar la arquitectura de cinco capas de la Tabla `tab:capas` (canales de entrada, orquestacion, procesamiento, inferencia y persistencia) con sus tres canales de entrada (correo electronico, formulario web y telefonia) y SHALL generarse desde la fuente Mermaid versionada `docs/diagrams/arquitectura_sistema.md`. La figura MUST NOT representar un flujo de un solo canal como arquitectura del sistema ni contener erratas ortograficas. Su leyenda MUST NOT remitir a un detalle del Anexo A que el anexo no contenga, y el Anexo A (`sec:anexo-diagrama-arquitectura`) SHALL inventariar la fuente versionada de la figura junto con las de los demas diagramas.

#### Scenario: Cinco capas y tres canales

- **WHEN** se inspecciona el PNG `arquitectura_sistema.png`
- **THEN** figuran las cinco capas de la Tabla `tab:capas` y los tres canales de entrada
- **AND** el canal telefonico se representa como Twilio con transcripcion en el backend y entrega a N8N, coherente con `n8n/workflow.json`

#### Scenario: Fuente versionada y reproducible

- **WHEN** se renderiza el bloque Mermaid de `docs/diagrams/arquitectura_sistema.md`
- **THEN** el resultado coincide en contenido con el PNG embebido en la tesis
- **AND** la version de `mmdc` usada queda registrada en el registro del dictamen

#### Scenario: Sin remision colgada ni erratas

- **WHEN** se lee la leyenda de `fig:arquitectura` y se inspecciona la figura
- **THEN** la leyenda no remite a un detalle del Anexo A
- **AND** la figura no contiene "responsablle" ni "SI" sin tilde

#### Scenario: Fuente inventariada en el Anexo A

- **WHEN** se lee el Anexo A en el PDF compilado
- **THEN** lista la figura de arquitectura con su fuente `docs/diagrams/arquitectura_sistema.md`

### Requirement: Tabla de entidades y diagrama entidad-relacion coherentes con el modelo ORM entregado

La Tabla `tab:entidades` SHALL enumerar, para cada una de las siete entidades principales, atributos clave cuyos nombres coincidan exactamente con columnas del ORM de `App/Backend/app/models/` en la release entregada, sin tildes en los identificadores. SHALL describir el correo y el telefono de `directorio_empleado` como cifrados en reposo con Fernet y localizados mediante un indice ciego (c-153) y MUST NOT describirlos como almacenados en texto plano. Los valores del campo `rol` declarados en la tabla y en la prosa de la subseccion de modelo de datos SHALL coincidir con el vocabulario del modelo. La figura `fig:er_modelo_datos` y su fuente `docs/diagrams/er_modelo_datos.md` SHALL ser coherentes con la tabla y con el ORM. La tabla MUST compilarse sin texto superpuesto, y su leyenda o la de la figura SHALL declarar que describen el modelo de la configuracion entregada.

#### Scenario: Atributos con nombres del ORM

- **WHEN** se busca cada atributo listado en la Tabla `tab:entidades` entre las columnas definidas en `App/Backend/app/models/`
- **THEN** cada atributo existe en el modelo de su entidad
- **AND** ningun identificador contiene tildes ni nombres inexistentes como `id_incidente`, `categoría_predicha` o `categoría_validada`

#### Scenario: Contacto del directorio cifrado

- **WHEN** se lee la fila de `directorio_empleado` en la tabla
- **THEN** declara el correo y el telefono cifrados en reposo con Fernet y el indice ciego
- **AND** no contiene la expresion "texto plano"

#### Scenario: Roles del modelo

- **WHEN** se comparan los roles enunciados en la tabla y en la prosa de la subseccion de modelo de datos con `RolEmpleado` de `App/Backend/app/models/empleado.py`
- **THEN** coinciden en cantidad y en significado

#### Scenario: Diagrama entidad-relacion coherente

- **WHEN** se inspeccionan `docs/diagrams/er_modelo_datos.md` y `er_modelo_datos.png`
- **THEN** `DIRECTORIO_EMPLEADO` incluye `nombre`, el cifrado del contacto y el indice ciego, e `INCIDENTE` incluye `requiere_revision_humana`
- **AND** la fuente no remite a un numero de tabla distinto del de `tab:entidades` en el PDF

#### Scenario: Tabla legible y siete entidades

- **WHEN** se extrae con `pdftotext -layout` la pagina de la Tabla `tab:entidades`
- **THEN** los nombres `clasificacion_log` y `directorio_empleado` aparecen completos y sin texto superpuesto
- **AND** la tabla conserva siete filas de entidades

### Requirement: Perfil NIST CSF coherente con el estado de controles de la seccion de cumplimiento

La Tabla `tab:cumplimiento-nist` SHALL declarar, para cada una de las seis funciones, la madurez y la brecha principal del estado reconciliado del gap assessment versionado (`docs/cumplimiento/gap-assessment-iso27001-27002-nist-csf2.md`, seccion 4 y registro de estado vigente de la seccion 2.4) en la release entregada, y SHALL ser coherente con la Tabla `tab:cumplimiento-iso` y con la subseccion de brechas y hoja de ruta (`subsec:cumplimiento-brechas`): ninguna fila MUST declarar ausente un control que esas secciones declaran cerrado. Su linea de fuente SHALL fechar el estado que describe. La lista de controles atribuidos a C-61 en `subsec:cumplimiento-brechas` SHALL coincidir con la de `docs/cumplimiento/plan-cambios-cumplimiento.md`. La tabla SHALL conservar el vocabulario de alineacion y MUST NOT declarar certificacion ni conformidad.

#### Scenario: Madurez igual al gap assessment

- **WHEN** se compara la columna de madurez de `tab:cumplimiento-nist` con la seccion 4 del gap assessment de la release entregada
- **THEN** los valores coinciden funcion por funcion (GV 2, ID 2, PR 3, DE 1, RS 2, RC 2)

#### Scenario: Sin ausencias contradichas

- **WHEN** se leen las brechas de las funciones Gobernar, Identificar y Responder
- **THEN** no declaran ausentes la politica de seguridad (5.1), el inventario y la clasificacion (5.9, 5.12) ni el plan de respuesta a incidentes (5.24 a 5.27)
- **AND** las brechas residuales coinciden con las del gap assessment

#### Scenario: Lista de C-61 completa

- **WHEN** se lee la lista de controles de C-61 en `subsec:cumplimiento-brechas`
- **THEN** incluye 5.1, 5.2, 5.9, 5.12, 5.13, 5.24 a 5.27, 5.31 y 8.26

#### Scenario: Fuente fechada y lenguaje de alineacion

- **WHEN** se lee la linea de fuente de `tab:cumplimiento-nist`
- **THEN** fecha el estado reconciliado y remite al gap assessment
- **AND** la tabla no contiene "certificado", "certificacion", "conforme" ni "cumple"

### Requirement: Lectura de los errores estrictos por frontera con sus aciertos laxos

La subseccion de analisis de errores y casos limite (`subsec:analisis-errores`) SHALL presentar, por frontera de confusion, cuantos de los errores estrictos son aciertos laxos segun las definiciones de la subseccion de analisis estadistico (`subsec:analisis-estadistico`), con los valores registrados en el memo canonico: 32 de 53 en total, 10 de 12 en Sistemas-Soporte Tecnico Software, 8 de 11 en Seguridad Informatica-Soporte Tecnico Software, 5 de 14 en Soporte Tecnico Hardware-Soporte Tecnico Software y 9 de 16 en las demas fronteras. SHALL acompanarlos de una lectura operativa presentada como interpretacion, coherente con la exactitud laxa canonica (179 de 200) y con la cota superior de la tasa operativa de derivacion erronea ya declarada en la discusion, sin modificar el balance neto ni ningun valor canonico vigente. El texto SHALL decir "sobre qué aspecto" donde hoy dice "sobre que aspecto".

#### Scenario: Valores por frontera presentes y canonicos

- **WHEN** se lee la Tabla `tab:errores` y su texto en el PDF compilado
- **THEN** figuran los aciertos laxos por frontera (5, 10, 8 y 9) y el total (32 de 53)
- **AND** cada valor coincide con la seccion correspondiente de `docs/Tesis/Correcciones/numeros-canonicos.md`

#### Scenario: Consistencia con la exactitud laxa

- **WHEN** se suman los aciertos estrictos (147) y los aciertos laxos entre los errores estrictos (32)
- **THEN** el resultado es la cantidad de aciertos laxos canonica (179)
- **AND** los errores fuera del conjunto de verdad que cita el texto, si los cita, son 21

#### Scenario: Lectura operativa como interpretacion

- **WHEN** se lee el parrafo que acompana la tabla
- **THEN** presenta la lectura operativa como interpretacion
- **AND** no modifica la Tabla `tab:balance-neto` ni ningun valor canonico

#### Scenario: Errata corregida

- **WHEN** se busca "sobre que aspecto" en `07-resultados.tex`
- **THEN** no aparece
- **AND** aparece "sobre qué aspecto"

### Requirement: Trazabilidad de las observaciones A3 y A4 del dictamen del 2026-10-28

El registro `docs/Tesis/Correcciones/dictamen-correcciones.md` SHALL contener una seccion del dictamen del 2026-10-28 sobre la tesis v10 / `v1.2.5` atribuida a c-159, con una matriz `| Rec | Sintesis | Change | Archivo:linea | Ancla | Fragmento verificable | Estado |` de una fila por parte de las observaciones A3 y A4 y por cada correccion puntual del inventario del dictamen que este change atiende, con archivo y linea validos tras la aplicacion, el `\label` ancla mas cercano y un fragmento verificable. La seccion SHALL registrar las discrepancias halladas frente al dictamen, que el change cierra el residual de la observacion A1 del dictamen del 2026-10-22 en las Figuras 1 y 4, y la evidencia de cierre (salida del recomputo, resultado de la compilacion y conteo de paginas). El Anexo I (`sec:anexo-trazabilidad`) SHALL identificar el dictamen del 2026-10-28 y presentar el mapeo de A3 y A4 a c-159 y a las secciones de la tesis mediante referencias cruzadas, en una tabla distinta de `tab:anexo-trazabilidad` (o en la que se haya creado para el mismo dictamen), sin numeros de linea de las fuentes.

#### Scenario: Matriz verificable

- **WHEN** para cada fila de la matriz se lee la linea citada del archivo citado
- **THEN** la linea contiene el fragmento verificable registrado
- **AND** el `\label` ancla existe en ese archivo

#### Scenario: Anexo I con el dictamen del 2026-10-28

- **WHEN** se lee el Anexo I en el PDF compilado
- **THEN** identifica el dictamen del 28 de octubre de 2026 sobre la release `v1.2.5`
- **AND** mapea A3 y A4 a c-159 y a sus secciones sin numeros de linea
- **AND** no mezcla esas filas con las del dictamen del 22 de octubre de 2026

#### Scenario: Residual de A1 y discrepancias registrados

- **WHEN** se lee la seccion de c-159 del registro
- **THEN** consigna que las Figuras 1 y 4 cierran el residual de A1 del dictamen del 2026-10-22
- **AND** enumera las discrepancias halladas frente al dictamen

### Requirement: Impacto de paginas de la reconciliacion de figuras, tablas y evidencia cualitativa

La aplicacion de este change SHALL ser neutral en paginas: el total del PDF compilado despues del change MUST ser menor o igual que el total medido inmediatamente antes de aplicarlo, con la misma cadena de compilacion. Para lograrlo SHALL usar palancas de forma (relaciones de aspecto equivalentes en las figuras regeneradas, leyendas cortas en la lista de figuras, una columna en una tabla existente en lugar de prosa adicional) y MUST NOT eliminar contenido cientifico, numeros canonicos, figuras ni tablas, ni editar el preambulo. Si la neutralidad no puede lograrse sin eliminar contenido, el exceso SHALL registrarse con ambos conteos y su causa en el registro del dictamen como residual para los autores.

#### Scenario: Conteo antes y despues registrado

- **WHEN** se compila `main.tex` con la imagen `texlive-thesis` antes y despues del change
- **THEN** ambos totales, tomados de `main.log`, quedan registrados
- **AND** el total posterior es menor o igual que el anterior, o el exceso figura con su causa como residual

#### Scenario: Compilacion limpia

- **WHEN** se revisa `main.log` tras la compilacion final
- **THEN** no hay lineas que empiecen con "!" ni advertencias "undefined" o "multiply defined"
- **AND** `pdftotext main.pdf -` no contiene "??"

## MODIFIED Requirements

### Requirement: Evidencia textual anonimizada de errores

La subseccion de analisis de errores y casos limite (`subsec:analisis-errores`, seccion de resultados) SHALL incluir evidencia textual de los errores de clasificacion, no solo su tipificacion agregada. MUST presentar entre dos y tres ejemplos de incidentes con error estricto, cada uno con su identificador de caso del corpus, la descripcion pseudonimizada, el sector asignado, el sector predicho, la confianza reportada y la etapa del pipeline que la emitio. La descripcion SHALL reproducirse literalmente desde `data/corpus_evaluacion_pseudonimizado.json` o, si se la parafrasea, SHALL rotularse explicitamente como parafrasis; MUST NOT presentarse como reproducida una descripcion que no es literal. Los ejemplos MUST provenir de la evidencia versionada `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json` (copia de la cache `evaluation/predicciones.json`, excluida del repositorio) y MUST ser consistentes con la matriz de confusion y la tipologia de errores. Toda afirmacion de conjunto sobre la confianza de los ejemplos MUST ser verdadera para cada uno de ellos y SHALL distinguir la confianza de la etapa deterministica (indice de fuerza de senal, no utilizable como criterio de derivacion) de la confianza autodeclarada por Gemini. Cuando un ejemplo sea un acierto laxo (sector predicho dentro del conjunto de verdad del caso), el texto SHALL declararlo con la definicion de la subseccion de analisis estadistico. La anonimizacion MUST preservar la utilidad analitica del ejemplo sin exponer datos personales.

#### Scenario: Ejemplos textuales presentes

- **WHEN** se lee la subseccion de analisis de errores y casos limite
- **THEN** aparecen entre dos y tres ejemplos de descripciones de incidentes con error estricto
- **AND** cada ejemplo indica su identificador de caso, el sector asignado, el sector predicho, la confianza y la etapa

#### Scenario: Reproduccion literal o parafrasis rotulada

- **WHEN** se compara cada descripcion citada con el campo `descripcion` del caso en `data/corpus_evaluacion_pseudonimizado.json`
- **THEN** la cita es identica a la del corpus
- **AND** si no lo es, el texto la rotula expresamente como parafrasis

#### Scenario: Consistencia con las predicciones

- **WHEN** se compara cada ejemplo con su registro en `evaluation/evidence/predicciones_hybrid-v3_2026-10-07.json`
- **THEN** el par asignado/predicho, la confianza y la etapa coinciden con el registro
- **AND** el ejemplo pertenece a uno de los patrones de error descritos en la tipologia

#### Scenario: Afirmacion sobre la confianza verdadera para cada caso

- **WHEN** se lee la afirmacion de conjunto sobre la confianza de los ejemplos
- **THEN** es verdadera para cada uno de ellos
- **AND** la confianza de un caso resuelto por la etapa deterministica no se presenta como confianza alta del modelo

#### Scenario: Aciertos laxos declarados

- **WHEN** un ejemplo tiene su sector predicho entre los sectores adicionales del caso
- **THEN** el texto lo declara acierto laxo con la definicion de la subseccion de analisis estadistico

#### Scenario: Anonimización suficiente

- **WHEN** se revisan los textos citados
- **THEN** no contienen nombres de personas, direcciones, correos, telefonos ni identificadores internos que permitan reidentificacion
- **AND** la descripcion conserva el rasgo que explica el error
